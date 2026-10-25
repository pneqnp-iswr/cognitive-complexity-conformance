"""Re-run one tool on an already processed repository, overwrite its raw JSON, and rebuild the function table.
Usage: py -3.11 scripts/rerun_tool.py <lang> <repo_full_name> <tool_name>   (tool names as in run_realcode.TOOLS_BY_LANG)"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from ccstudy.functions import iter_source_files
import run_realcode, build_function_table

ROOT = pathlib.Path(__file__).resolve().parents[1]
lang, repo, name = sys.argv[1:4]
raw = ROOT / "results" / "raw" / lang / repo.replace("/", "__")
meta = json.loads((raw / "run_meta.json").read_text(encoding="utf-8"))
files = list(iter_source_files(meta["repo_dir"], lang))
t0 = time.time()
rows = run_realcode.run_tool(name, files, meta["repo_dir"])
(raw / f"{name}.json").write_text(json.dumps(rows), encoding="utf-8")
meta["timings_s"][name] = round(time.time() - t0, 1)
meta.setdefault("reruns", []).append({"tool": name, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rows": len(rows)})
(raw / "run_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
n, cov = build_function_table.build(lang, repo)
print(name, "rows:", len(rows), "table rows:", n, "coverage:", {k: v for k, v in cov.items() if name.split("_")[-1] in k or "lizard" in k})
