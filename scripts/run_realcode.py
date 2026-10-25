"""Run the full tool set on one selected repository and save raw outputs + the aligned per-function table.

Usage: py -3.11 scripts/run_realcode.py <lang> <repo_full_name>   (lang: python|java|javascript|go)
Reads data/repos/manifest.csv for the clone directory and SHA.
Outputs:
  results/raw/<lang>/<repo_slug>/units.json          tree-sitter units + features
  results/raw/<lang>/<repo_slug>/<tool>.json         raw normalized rows per tool (untouched afterwards)
  results/raw/<lang>/<repo_slug>/sonar.json          SonarQube issues (via scripts/sonar_scan.py)
  results/raw/<lang>/<repo_slug>/run_meta.json       timings, versions, file counts, errors
  results/processed/functions/<lang>__<repo_slug>.csv  one row per unit, one column per tool/metric
"""
import csv, dataclasses, datetime, json, pathlib, subprocess, sys, time, traceback
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from ccstudy import tools
from ccstudy.functions import enumerate_functions, iter_source_files
from ccstudy.align import align

ROOT = pathlib.Path(__file__).resolve().parents[1]
THRESHOLD_TOOLS = {"sonarqube", "pmd", "eslint-plugin-sonarjs-4.2.1", "eslint-plugin-maintainability", "gocognit"}
SONAR_LANG = {"python": "py", "java": "java", "javascript": "js", "go": "go"}
TOOLS_BY_LANG = {
    "python": ["python_tools", "rca", "codemetrics", "lizard"],
    "java": ["pmd", "cognitive_java", "codemetrics", "lizard"],
    "javascript": ["js_cogplexity", "js_oxlint", "js_maintainability", "js_sonarjs421", "ccts", "rca", "codemetrics", "lizard"],
    "go": ["gocognit", "codemetrics", "lizard"],
}

def slug(repo):
    return repo.replace("/", "__")

def run_tool(name, files, repo_dir):
    if name == "python_tools": return tools.run_python_tools(files)
    if name == "rca": return tools.run_rca(files)
    if name == "codemetrics": return tools.run_codemetrics(files)
    if name == "lizard": return tools.run_lizard(files)
    if name == "pmd": return tools.run_pmd(files, repo_dir)
    if name == "cognitive_java": return tools.run_cognitive_java(files, repo_dir)
    if name == "gocognit": return tools.run_gocognit(repo_dir, files)
    if name == "ccts": return tools.run_ccts(files)
    if name.startswith("js_"): return tools.run_js_tool(name[3:], files)
    raise ValueError(name)

def main(lang, repo):
    mpath = ROOT / "data" / "repos" / "manifest.csv"
    man = {r["repo"]: r for r in csv.DictReader(open(mpath, encoding="utf-8")) if r["lang"] == lang} if mpath.exists() else {}
    if repo not in man:  # fall back to the per-language selection snapshot
        sel = json.loads((ROOT / "data" / "repos" / f"selection_{lang}.json").read_text(encoding="utf-8"))
        man = {a["repo"]: a for a in sel["accepted"]}
    rec = man[repo]
    repo_dir = str((ROOT / rec["clone_dir"]).resolve())
    out_raw = ROOT / "results" / "raw" / lang / slug(repo); out_raw.mkdir(parents=True, exist_ok=True)
    out_proc = ROOT / "results" / "processed" / "functions"; out_proc.mkdir(parents=True, exist_ok=True)
    meta = {"lang": lang, "repo": repo, "sha": rec["sha"], "repo_dir": repo_dir, "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "tool_versions": tools.TOOL_VERSIONS, "timings_s": {}, "errors": {}, "n_files": 0, "n_units": 0}
    files = list(iter_source_files(repo_dir, lang))
    meta["n_files"] = len(files)
    # 1) units
    t0 = time.time(); units = {}; parse_errors = 0
    for f in files:
        try:
            units[f] = enumerate_functions(f)
        except Exception as e:
            parse_errors += 1; units[f] = []
    meta["timings_s"]["enumerate"] = round(time.time() - t0, 1); meta["parse_errors"] = parse_errors
    meta["n_units"] = sum(len(v) for v in units.values())
    (out_raw / "units.json").write_text(json.dumps({f: [dataclasses.asdict(u) for u in us] for f, us in units.items()}), encoding="utf-8")
    # 2) tools
    all_rows = []
    for name in TOOLS_BY_LANG[lang]:
        t0 = time.time()
        try:
            rows = run_tool(name, files, repo_dir)
        except Exception as e:
            meta["errors"][name] = traceback.format_exc()[-1500:]; rows = []
        meta["timings_s"][name] = round(time.time() - t0, 1)
        (out_raw / f"{name}.json").write_text(json.dumps(rows), encoding="utf-8")
        all_rows += rows
        print(f"  {name}: {len(rows)} rows in {meta['timings_s'][name]}s", flush=True)
    # 3) sonar
    t0 = time.time()
    sj = out_raw / "sonar.json"
    key = f"cc-{lang}-{slug(repo)}"[:390]
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "sonar_scan.py"), key, repo_dir, str(sj), "--lang", SONAR_LANG[lang]],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=4 * 3600)
    meta["timings_s"]["sonar"] = round(time.time() - t0, 1)
    if r.returncode != 0 or not sj.exists():
        meta["errors"]["sonar"] = (r.stdout + r.stderr)[-3000:]
        print("  sonar FAILED", flush=True)
    else:
        all_rows += tools.rows_from_sonar(sj, repo_dir)
        print(f"  sonar: ok in {meta['timings_s']['sonar']}s", flush=True)
    # 4) align and write table (shared post-processing, rebuildable from raw files)
    meta["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out_raw / "run_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    import build_function_table
    n, coverage = build_function_table.build(lang, repo)
    meta = json.loads((out_raw / "run_meta.json").read_text(encoding="utf-8"))
    meta["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out_raw / "run_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("n_files", "n_units", "timings_s", "coverage")}, indent=None)[:1500])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
