"""Rebuild results/processed/functions/<lang>__<repo>.csv from the raw per-tool JSON files of one repository
(results/raw/<lang>/<repo>/units.json, <tool>.json, sonar.json). Pure post-processing: raw files are never modified.
Usage: py -3.11 scripts/build_function_table.py <lang> <repo_full_name>   (or --all to rebuild every repo with run_meta.json)"""
import csv, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from ccstudy import tools
from ccstudy.functions import FunctionUnit
from ccstudy.align import align

ROOT = pathlib.Path(__file__).resolve().parents[1]
THRESHOLD_TOOLS = {"sonarqube", "pmd", "eslint-plugin-sonarjs-4.2.1", "eslint-plugin-maintainability", "gocognit"}
FULLFILE_ZERO_TOOLS = {"eslint-plugin-sonarjs-4.2.1", "eslint-plugin-maintainability"}
TOOL_FILES = {"python": ["python_tools", "rca", "codemetrics", "lizard"], "java": ["pmd", "cognitive_java", "codemetrics", "lizard"],
              "javascript": ["js_cogplexity", "js_oxlint", "js_maintainability", "js_sonarjs421", "ccts", "rca", "codemetrics", "lizard"], "go": ["gocognit", "codemetrics", "lizard"]}

def slug(repo):
    return repo.replace("/", "__")

def is_test_path(rel):
    parts = rel.lower().split("/")
    # A path is a test path if a directory component contains "test"/"spec" or the file name follows a common
    # language-specific test convention. `rel` is lower-cased above, so Java *Test.java/*Tests.java are checked in lower case.
    dirs, fname = parts[:-1], parts[-1]
    java_named_test = fname.endswith(("test.java", "tests.java"))
    return (any(("test" in d or "spec" in d) for d in dirs)
            or fname.startswith("test_")
            or fname.endswith(("_test.py", "_test.go", "_tests.py"))
            or ".test." in fname or ".spec." in fname
            or java_named_test)

def build(lang, repo):
    raw = ROOT / "results" / "raw" / lang / slug(repo)
    meta = json.loads((raw / "run_meta.json").read_text(encoding="utf-8")) if (raw / "run_meta.json").exists() else {}
    repo_dir = meta.get("repo_dir") or str((ROOT / "data" / "raw_repos" / slug(repo)).resolve())
    units_raw = json.loads((raw / "units.json").read_text(encoding="utf-8"))
    units = {f: [FunctionUnit(**u) for u in us] for f, us in units_raw.items()}
    all_rows = []
    for name in TOOL_FILES[lang]:
        p = raw / f"{name}.json"
        if p.exists():
            all_rows += json.loads(p.read_text(encoding="utf-8"))
    if (raw / "sonar.json").exists():
        all_rows += tools.rows_from_sonar(raw / "sonar.json", repo_dir)
    sonar_files = set(json.loads((raw / "sonar_files.json").read_text(encoding="utf-8"))) if (raw / "sonar_files.json").exists() else set()
    analysed = {(r["tool"], r["file"]) for r in all_rows if r.get("line") is not None and r["metric"] in ("cognitive", "cyclomatic")}
    # ESLint-based rules run at threshold 0 on the explicit file list emit no message for a file whose functions all
    # score 0; such files were analysed, so they count as analysed unless an error row names them (fix of 2026-09-17).
    if sonar_files and lang == "go":
        # Go only: sonar-go runs S3776 on every indexed file (including _test.go, verified 2026-09-17) and Go has no cyclomatic
        # rule that would mark an analysed file; a file without any issue therefore has only zero-valued functions and is
        # zero-filled. Not applied to Python/Java, whose analyzers skip files they classify as tests although the scanner indexes them.
        analysed |= {("sonarqube", f_) for f_ in units.keys() if f_ in sonar_files}
    for t_ in FULLFILE_ZERO_TOOLS:
        if any(r["tool"] == t_ for r in all_rows):
            errored = {r["file"] for r in all_rows if r["tool"] == t_ and r.get("line") is None and (r.get("extra") or {}).get("error")}
            analysed |= {(t_, f_) for f_ in units.keys() if f_ not in errored}
    cog_tools = sorted({r["tool"] for r in all_rows if r["metric"] == "cognitive" and r.get("line") is not None})
    cyc_tools = sorted({r["tool"] for r in all_rows if r["metric"] == "cyclomatic" and r.get("line") is not None})
    aligned = {}; coverage = {}
    for metric, tl in (("cognitive", cog_tools), ("cyclomatic", cyc_tools)):
        for t in tl:
            a, un, d = align(units, all_rows, t, metric); aligned[(metric, t)] = a
            coverage[f"{metric}:{t}"] = {"aligned": len(a), "unaligned": len(un), "dups": len(d)}
    out_proc = ROOT / "results" / "processed" / "functions"; out_proc.mkdir(parents=True, exist_ok=True)
    cols = ["lang", "repo", "file", "idx", "kind", "name", "qualified_name", "decl_line", "body_line", "end_line", "depth", "parent_idx", "has_nested", "nested_count",
            "is_test_path", "recursion_direct", "recursion_calls", "recursion_method", "has_body", "features", "logical_ops"] + [f"cog__{t}" for t in cog_tools] + [f"cyc__{t}" for t in cyc_tools]
    n = 0
    with open(out_proc / f"{lang}__{slug(repo)}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for f, us in units.items():
            rel = pathlib.Path(f).relative_to(repo_dir).as_posix()
            it = int(is_test_path(rel))
            for u in us:
                row = {"lang": lang, "repo": repo, "file": rel, "idx": u.idx, "kind": u.kind, "name": u.name, "qualified_name": u.qualified_name,
                       "decl_line": u.decl_line, "body_line": u.body_line, "end_line": u.end_line, "depth": u.depth, "parent_idx": u.parent_idx if u.parent_idx is not None else "",
                       "has_nested": int(u.has_nested), "nested_count": u.nested_count, "is_test_path": it, "recursion_direct": int(u.recursion_direct), "recursion_calls": int(getattr(u, "recursion_calls", 0)), "recursion_method": int(getattr(u, "recursion_method", False)), "has_body": int(getattr(u, "has_body", True)),
                       "features": json.dumps(u.features, sort_keys=True), "logical_ops": json.dumps(u.logical_ops, sort_keys=True)}
                for t in cog_tools:
                    r_ = aligned[("cognitive", t)].get((f, u.idx)); v = r_["value"] if r_ else None
                    if v is None and t in THRESHOLD_TOOLS and (t, f) in analysed and u.depth == 0:
                        v = 0
                    row[f"cog__{t}"] = "" if v is None else v
                for t in cyc_tools:
                    r_ = aligned[("cyclomatic", t)].get((f, u.idx)); v = r_["value"] if r_ else None
                    if v is None and t == "sonarqube" and (t, f) in analysed and u.depth == 0:
                        v = 0
                    row[f"cyc__{t}"] = "" if v is None else v
                w.writerow(row); n += 1
    meta["coverage"] = coverage
    if (raw / "run_meta.json").exists():
        (raw / "run_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return n, coverage

if __name__ == "__main__":
    if sys.argv[1] == "--all":
        for lang_dir in (ROOT / "results" / "raw").iterdir():
            if lang_dir.name not in TOOL_FILES: continue
            for rd in lang_dir.iterdir():
                if (rd / "run_meta.json").exists():
                    n, cov = build(lang_dir.name, rd.name.replace("__", "/", 1)); print(lang_dir.name, rd.name, n)
    else:
        n, cov = build(sys.argv[1], sys.argv[2]); print(n, json.dumps(cov))
