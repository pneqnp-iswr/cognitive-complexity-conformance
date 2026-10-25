"""Persist, for every scanned repository, the list of main source files that SonarQube indexed (qualifier FIL), as
normalised absolute paths, into results/raw/<lang>/<repo>/sonar_files.json. Used by build_function_table.py to
zero-fill functions of analysed files that carry no S3776 issue (a file whose functions all score 0 has no issue and, in
Go, no cyclomatic row either). Usage: py -3.11 scripts/sonar_files.py"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import sonar_scan
from ccstudy.tools import _norm
ROOT = pathlib.Path(__file__).resolve().parents[1]
n_done = 0
for lang_dir in sorted((ROOT / "results" / "raw").iterdir()):
    if lang_dir.name not in ("python", "java", "javascript", "go"):
        continue
    for rd in sorted(lang_dir.iterdir()):
        sj = rd / "sonar.json"
        if not sj.exists():
            continue
        meta = json.loads(sj.read_text(encoding="utf-8"))["meta"]
        key = meta["project_key"]; src = pathlib.Path(meta["source_dir"])
        comps = sonar_scan.list_files(key)
        files = sorted({_norm(src / c.split(":", 1)[1]) for c in comps})
        (rd / "sonar_files.json").write_text(json.dumps(files), encoding="utf-8")
        n_done += 1
        print(lang_dir.name, rd.name, "indexed main files:", len(files), flush=True)
print("repositories:", n_done)
