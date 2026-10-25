"""Re-run only the tree-sitter unit enumeration for already processed repositories (e.g., after adding a unit attribute),
overwrite results/raw/<lang>/<repo>/units.json, and rebuild the function table. Raw tool outputs are untouched.
Usage: py -3.11 scripts/reenumerate_units.py --all | <lang> <repo>"""
import dataclasses, json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from ccstudy.functions import enumerate_functions, iter_source_files
import build_function_table

ROOT = pathlib.Path(__file__).resolve().parents[1]

def redo(lang, repo):
    raw = ROOT / "results" / "raw" / lang / repo.replace("/", "__")
    meta = json.loads((raw / "run_meta.json").read_text(encoding="utf-8"))
    files = list(iter_source_files(meta["repo_dir"], lang))
    units = {}
    for f in files:
        try:
            units[f] = enumerate_functions(f)
        except Exception:
            units[f] = []
    (raw / "units.json").write_text(json.dumps({f: [dataclasses.asdict(u) for u in us] for f, us in units.items()}), encoding="utf-8")
    meta["n_units"] = sum(len(v) for v in units.values())
    meta.setdefault("reruns", []).append({"tool": "enumerate", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    (raw / "run_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    n, cov = build_function_table.build(lang, repo)
    return n

if __name__ == "__main__":
    if sys.argv[1] == "--all":
        for lang_dir in sorted((ROOT / "results" / "raw").iterdir()):
            if lang_dir.name not in build_function_table.TOOL_FILES: continue
            for rd in sorted(lang_dir.iterdir()):
                if (rd / "run_meta.json").exists():
                    print(lang_dir.name, rd.name, redo(lang_dir.name, rd.name.replace("__", "/", 1)), flush=True)
    else:
        print(redo(sys.argv[1], sys.argv[2]))
