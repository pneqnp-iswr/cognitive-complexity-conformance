"""Batch driver: run scripts/run_realcode.py for every accepted repository in the manifest (or a language subset),
skipping repositories whose run_meta.json already exists (unless --force). Logs to logs/run_all_repos.log."""
import csv, json, pathlib, subprocess, sys, time, datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / "logs" / "run_all_repos.log"

def main(langs, force=False):
    mpath = ROOT / "data" / "repos" / "manifest.csv"
    man = list(csv.DictReader(open(mpath, encoding="utf-8"))) if mpath.exists() else []
    todo = [r for r in man if r["lang"] in langs]
    # languages not yet in the manifest: use the per-language selection snapshot (same records)
    for lang in langs:
        if not any(r["lang"] == lang for r in todo):
            sp = ROOT / "data" / "repos" / f"selection_{lang}.json"
            if sp.exists():
                todo += [{"lang": lang, **a} for a in json.loads(sp.read_text(encoding="utf-8"))["accepted"]]
    with open(LOG, "a", encoding="utf-8") as log:
        for r in todo:
            slug = r["repo"].replace("/", "__")
            meta = ROOT / "results" / "raw" / r["lang"] / slug / "run_meta.json"
            if meta.exists() and not force:
                log.write(f"{datetime.datetime.now().isoformat()} SKIP {r['lang']} {r['repo']} (done)\n"); log.flush(); continue
            t0 = time.time()
            log.write(f"{datetime.datetime.now().isoformat()} START {r['lang']} {r['repo']} sha={r['sha'][:10]} files={r['files']} loc={r['loc']}\n"); log.flush()
            p = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_realcode.py"), r["lang"], r["repo"]], capture_output=True, text=True, encoding="utf-8", errors="replace")
            log.write(p.stdout[-4000:] + ("\nSTDERR:\n" + p.stderr[-3000:] if p.returncode != 0 else ""))
            log.write(f"{datetime.datetime.now().isoformat()} END {r['lang']} {r['repo']} rc={p.returncode} in {time.time()-t0:.0f}s\n\n"); log.flush()

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args or ["python", "java", "javascript", "go"], force="--force" in sys.argv)
