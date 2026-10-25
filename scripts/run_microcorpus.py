"""Run every tool on the micro-corpus (all four languages), align to tree-sitter units, and produce
results/processed/microcorpus_matrix.csv (one row per case, one column per tool) plus raw outputs in
results/raw/microcorpus/<tool>_<lang>.json. SonarQube values come from scans of the per-language dirs
(scripts/sonar_scan.py must have been run for micro-<lang> projects into results/raw/microcorpus/sonar_<lang>.json)."""
import csv, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from ccstudy import tools
from ccstudy.functions import enumerate_functions
from ccstudy.align import align

ROOT = pathlib.Path(__file__).resolve().parents[1]
MC = ROOT / "experiments" / "microcorpus"
RAW = ROOT / "results" / "raw" / "microcorpus"; RAW.mkdir(parents=True, exist_ok=True)
PROC = ROOT / "results" / "processed"; PROC.mkdir(parents=True, exist_ok=True)
FILES = {"python": MC / "python" / "micro.py", "java": MC / "java" / "Micro.java", "javascript": MC / "javascript" / "micro.ts", "go": MC / "go" / "micro.go"}

THRESHOLD_TOOLS = {"sonarqube", "pmd", "eslint-plugin-sonarjs-4.2.1", "eslint-plugin-maintainability", "gocognit"}
_analysed = {}
def analysed_ok(tool, f):
    """True if the tool produced at least one row for the file (i.e., analysed it)."""
    return (tool, f) in _analysed

def save(name, rows):
    (RAW / f"{name}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return rows

def main():
    all_rows = []
    py, jv, ts, go = [str(FILES["python"].resolve())], [str(FILES["java"].resolve())], [str(FILES["javascript"].resolve())], [str(FILES["go"].resolve())]
    all_rows += save("python_tools", tools.run_python_tools(py))
    all_rows += save("rca", tools.run_rca(py + ts))
    all_rows += save("codemetrics", tools.run_codemetrics(py + jv + ts + go))
    all_rows += save("pmd", tools.run_pmd(jv, str(FILES["java"].parent)))
    all_rows += save("cognitive_java", tools.run_cognitive_java(jv, str(FILES["java"].parent)))
    all_rows += save("gocognit", tools.run_gocognit(str(FILES["go"].parent), go))
    all_rows += save("lizard", tools.run_lizard(py + jv + ts + go))
    for t in ["cogplexity", "oxlint", "maintainability", "sonarjs421"]:
        all_rows += save(f"js_{t}", tools.run_js_tool(t, ts))
    all_rows += save("ccts", tools.run_ccts(ts))
    for lang, key in [("python", "py"), ("java", "java"), ("javascript", "js"), ("go", "go")]:
        sj = RAW / f"sonar_{key}.json"
        if sj.exists():
            all_rows += tools.rows_from_sonar(sj, str(FILES[lang].parent))
        else:
            print("WARNING: no sonar scan for", lang)
    # align
    units = {f: enumerate_functions(f) for f in py + jv + ts + go}
    tool_names = sorted({r["tool"] for r in all_rows if r["metric"] == "cognitive" and r.get("line") is not None})
    for r in all_rows:
        if r.get("line") is not None and r["metric"] in ("cognitive", "cyclomatic"):
            _analysed[(r["tool"], r["file"])] = True
    aligned = {}
    unaligned_log = {}
    for t in tool_names:
        a, un, d = align(units, all_rows, t, "cognitive")
        aligned[t] = a
        unaligned_log[t] = {"unaligned": len(un), "dups": len(d), "examples": [(pathlib.Path(u["file"]).name, u["line"], u.get("name"), u["value"]) for u in un[:10]]}
    # expected
    exp = list(csv.DictReader(open(MC / "expected.csv", encoding="utf-8")))
    out_rows = []
    for e in exp:
        f = str(FILES[e["lang"]].resolve())
        us = [u for u in units[f] if u.name == e["function"] and u.depth == 0]
        rec = {"case_id": e["case_id"], "lang": e["lang"], "function": e["function"], "rules": e["rules"], "expected": e["expected"],
               "ambiguous": e["ambiguous"], "readings": e["readings"], "found_unit": len(us)}
        for t in tool_names:
            v = None
            if us:
                r = aligned[t].get((f, us[0].idx))
                v = r["value"] if r else None
                # tools that report only functions above a threshold (0 here, PMD: >= 1): an analysed file with no
                # report for a root unit means value 0 (protocol section 4, clarified 2026-09-17 before real-code runs)
                if v is None and t in THRESHOLD_TOOLS and analysed_ok(t, f):
                    v = 0
            rec[t] = v if v is not None else ""
        out_rows.append(rec)
    cols = ["case_id", "lang", "function", "rules", "expected", "ambiguous", "readings", "found_unit"] + tool_names
    with open(PROC / "microcorpus_matrix.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(out_rows)
    (PROC / "microcorpus_alignment_log.json").write_text(json.dumps(unaligned_log, indent=1), encoding="utf-8")
    print("cases:", len(out_rows), "tools:", tool_names)
    print("units not found:", [r["case_id"] for r in out_rows if r["found_unit"] != 1])

if __name__ == "__main__":
    main()
