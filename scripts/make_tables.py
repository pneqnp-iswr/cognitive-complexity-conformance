"""Generate manuscript tables (as JSON blocks for the manuscript builder + markdown for inspection) from processed CSVs.
Outputs: tables/tables.json (list of table blocks), tables/tables.md
Every number here is computed from results/processed/*.csv; nothing is typed by hand."""
import csv, json, pathlib, sys, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from ccstudy.tools import TOOL_VERSIONS

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC = ROOT / "results" / "processed"; OUT = ROOT / "tables"; OUT.mkdir(exist_ok=True)
LANGS = ["python", "java", "javascript", "go"]
LL = {"python": "Python", "java": "Java", "javascript": "JS/TS", "go": "Go"}
TOOL_LANG = {"complexipy": "Python", "cognitive_complexity": "Python", "rust-code-analysis": "Python, JS/TS", "codemetrics": "all four", "pmd": "Java",
             "cognitive-java": "Java", "gocognit": "Go", "cognitive-complexity-ts": "JS/TS", "cogplexity": "JS/TS", "oxlint-plugin-complexity": "JS/TS",
             "eslint-plugin-maintainability": "JS/TS", "eslint-plugin-sonarjs-4.2.1": "JS/TS (reference snapshot)"}
NAME3 = {"sonarqube": "SonarQube (ref.)", "eslint-plugin-sonarjs-4.2.1": "eslint-plugin-sonarjs 4.2.1 (snapshot)", "pmd": "PMD"}
SHORT = {"eslint-plugin-sonarjs-4.2.1": "eslint-plugin-sonarjs 4.2.1 (snapshot)", "pmd": "PMD", "cognitive-complexity-ts": "cognitive-complexity-ts", "oxlint-plugin-complexity": "oxlint-plugin-complexity",
         "eslint-plugin-maintainability": "eslint-plugin-maintainability", "rust-code-analysis": "rust-code-analysis", "cognitive_complexity": "cognitive_complexity"}

def pct(x, d=1):
    return f"{100 * float(x):.{d}f}"

def th(x):
    return f"{int(float(x)):,}"

def read(name):
    p = PROC / name
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []

def main():
    tables = []; md = []
    summary = json.loads((PROC / "summary.json").read_text(encoding="utf-8"))
    # T1 tools
    rows = [[SHORT.get(t, t).replace(" (snapshot)", ""), TOOL_VERSIONS[t], TOOL_LANG.get(t, "")] for t in ["complexipy", "cognitive_complexity", "rust-code-analysis", "codemetrics", "pmd", "cognitive-java", "gocognit",
                                                                  "cognitive-complexity-ts", "cogplexity", "oxlint-plugin-complexity", "eslint-plugin-maintainability", "eslint-plugin-sonarjs-4.2.1"]]
    rows += [["lizard", TOOL_VERSIONS.get("lizard", ""), "Python, Java, JS/TS (cyclomatic baseline only)"], ["radon", TOOL_VERSIONS.get("radon", ""), "Python (cyclomatic baseline only)"]]
    tables.append({"id": "T1", "caption": "Implementations Under Test (Reference: SonarQube Community Build " + TOOL_VERSIONS["sonarqube"].split(" ")[0] + ")",
                   "header": ["Implementation", "Version", "Languages used"], "rows": rows, "col_widths_pt": [104, 42, 100], "keep_together": True,
                   "footnote": "eslint-plugin-sonarjs 4.2.1 is a 2024 snapshot of the reference's JavaScript rule (drift probe); lizard and radon compute only cyclomatic complexity."})
    # T2 corpus
    rows = []
    for lang in LANGS:
        s = summary["langs"].get(lang)
        if not s: continue
        rows.append([LL[lang], str(s["n_repos"]), th(s["n_units"]), th(s["n_primary"]), th(s["n_primary_ref"]), pct(s.get("ref_share_zero") or 0, 0), pct(s["ref_share_gt15"])])
    tables.append({"id": "T2", "caption": "Real-Code Corpus", "header": ["Lang.", "Repos", "Function-like units", "Leaf root", "With ref.", "Ref. = 0 (%)", "> 15 (%)"],
                   "rows": rows, "col_widths_pt": [38, 34, 44, 36, 40, 32, 28], "font_pt": 7, "keep_together": True,
                   "footnote": "Function-like units: all functions, methods, lambdas and function literals enumerated by tree-sitter; Leaf root: named functions, methods and constructors (JS/TS also arrow functions and function expressions) at depth 0 that contain no nested unit and have a body; With ref.: leaf root functions with a SonarQube value (the primary population); Ref. = 0 and > 15: share of the primary population with reference value 0 (unreported, zero-filled) and above 15."})
    # T3 conformance (micro-corpus)
    conf = read("conformance_summary.csv")
    rows = []
    for lang in LANGS:
        for r in [x for x in conf if x["lang"] == lang]:
            rows.append([LL[lang], NAME3.get(r["tool"], r["tool"]), f"{r['n_conform']}/{r['n_unambiguous']}", pct(r["conformance"], 0), r["failed_targets"].replace(";", ", ")])
    tables.append({"id": "T3", "caption": "Micro-Corpus Conformance of the Reference and the Implementations on Unambiguous Cases (Failed Target Rules: Count)", "header": ["Lang.", "Implementation", "Conform", "%", "Failed target rules"],
                   "rows": rows, "col_widths_pt": [34, 80, 40, 22, 76], "font_pt": 7, "keep_together": True,
                   "footnote": "Rule codes are defined in Section III.B. A failed case is booked to the rule the implementation demonstrably fails on a dedicated case; conform counts below the unambiguous total without a failed target are unreported cases."})
    # T4 agreement + flips (real code)
    rows = []
    for lang in LANGS:
        agr = read(f"agreement_{lang}.csv"); fl = {(r["tool"], r["threshold"]): r for r in read(f"flips_{lang}.csv")}
        for a in agr:
            f = fl.get((a["tool"], "15"))
            n_ref = summary["langs"][lang]["n_primary_ref"]
            rows.append([LL[lang], SHORT.get(a["tool"], a["tool"]), th(a["n"]), pct(int(a["n"]) / n_ref, 0), f"{pct(a['exact'])} [{pct(a['exact_ci_lo'])}, {pct(a['exact_ci_hi'])}]", pct(a.get("exact_pos", float("nan"))), pct(a["within1"]),
                         f"{float(a['mad']):.2f}", f"{float(a['spearman']):.3f}", pct(a["share_tool_higher"]), pct(a["share_tool_lower"]),
                         pct(f["flip_rate"], 2) if f else "", (f"{pct(f['flip_rate_near'])} [{pct(f.get('flip_near_ci_lo', float('nan')))}, {pct(f.get('flip_near_ci_hi', float('nan')))}]") if f else ""])
    tables.append({"id": "T4", "caption": "Agreement with the SonarQube Reference on Leaf Root Functions and Gate Flips at t = 15",
                   "header": ["Lang.", "Implementation", "n", "Cov. (%)", "Exact (%) [95% CI]", "Exact ref>0 (%)", "±1 (%)", "MAD", "ρ", "Higher (%)", "Lower (%)", "Flip@15 (%)", "Flip near (%) [95% CI]"],
                   "rows": rows, "col_widths_pt": [32, 76, 34, 26, 68, 32, 30, 30, 30, 34, 34, 40, 54], "font_pt": 7, "wide": True, "float": "top",
                   "footnote": "n: functions with both values; Cov.: n as a share of leaf root functions with a reference value; CI: cluster-bootstrap interval over repositories; Exact ref>0: exact agreement on functions whose reference value is above 0; ρ: Spearman correlation; Higher/Lower: share of functions with the implementation above/below the reference; Flip@15: share whose gate decision at 15 differs; Flip near: the same for reference values in [10, 20]."})
    # T5 attribution
    rows = []
    for lang in LANGS:
        for a in read(f"attribution_{lang}.csv"):
            if a["tool"] == "eslint-plugin-sonarjs-4.2.1" or int(a["n_disagree"]) == 0:
                continue
            rows.append([LL[lang], SHORT.get(a["tool"], a["tool"]), th(a["n_disagree"]), pct(a["share_tool"], 0), pct(a["share_reference"], 0), pct(a["share_ambiguity"], 0), pct(a["share_unexplained"], 0),
                         pct(a["base_rate_flagged_among_agreeing"], 0), a["tool_targets"].replace(";", ", "), a["reference_targets"].replace(";", ", ")])
    tables.append({"id": "T5", "caption": "Attribution of Real-Code Disagreements",
                   "header": ["Lang.", "Implementation", "Disagree", "Impl. (%)", "Ref. (%)", "Amb. (%)", "Unexpl. (%)", "Base (%)", "Impl. targets", "Ref. targets"],
                   "rows": rows, "col_widths_pt": [36, 92, 40, 30, 30, 30, 36, 30, 100, 98], "font_pt": 7, "wide": True, "float": "top",
                   "footnote": "Disagree: leaf root functions on which implementation and reference differ; Impl./Ref./Amb./Unexpl.: shares attributed, in this order, by construct presence to an implementation deviation, a reference deviation, a specification ambiguity, or none of these; Base: share of agreeing functions the same predicates flag; Impl./Ref. targets: rules on which the implementation failed, or only the reference failed, unambiguous cases; shares are rounded independently and may not sum to 100. Attribution is diagnostic, not causal."})
    # T6 cyclomatic baseline
    rows = []
    for lang in LANGS:
        for a in read(f"cyclomatic_{lang}.csv"):
            rows.append([LL[lang], SHORT.get(a["tool"], a["tool"]), th(a["n"]), pct(a["exact"]), pct(a["within1"]), f"{float(a['mad']):.2f}"])
    tables.append({"id": "T6", "caption": "Baseline: Cyclomatic Complexity Agreement with SonarQube on the Same Functions", "header": ["Lang.", "Tool", "n", "Exact (%)", "±1 (%)", "MAD"],
                   "rows": rows, "col_widths_pt": [34, 82, 38, 36, 34, 28], "font_pt": 7, "keep_together": True,
                   "footnote": "Tools that report both metrics plus lizard and radon (cyclomatic only); Go is absent because sonar-go reports no per-function cyclomatic value."})
    for _t in tables:  # empty cells are shown as an em dash
        _t["rows"] = [[("—" if str(c).strip() == "" else c) for c in r] for r in _t["rows"]]
    (OUT / "tables.json").write_text(json.dumps(tables, indent=1, ensure_ascii=False), encoding="utf-8")
    for t in tables:
        md.append(f"### {t['id']}. {t['caption']}\n\n| " + " | ".join(t["header"]) + " |\n|" + "---|" * len(t["header"]))
        for r in t["rows"]:
            md.append("| " + " | ".join(r) + " |")
        md.append("")
    (OUT / "tables.md").write_text("\n".join(md), encoding="utf-8")
    print("tables:", [t["id"] for t in tables])

if __name__ == "__main__":
    main()
