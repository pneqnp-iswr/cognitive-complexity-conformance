"""Deterministic repository selection for the real-code corpus (criteria fixed in advance).

Criteria (frozen before any metric tool is run on real code):
  * GitHub search: language:<L> stars:>=5000 archived:false fork:false pushed:>=2026-01-01, sorted by stars desc,
    retrieved on the date recorded in the output (results are a snapshot; the snapshot is saved verbatim).
  * Walk the list in stars order; clone the default branch at its current HEAD (recorded SHA, shallow, depth=1);
  * Count source files/LOC of the target language (simple line counter over language extensions,
    excluding vendored/minified/test-fixture dirs per exclude list); accept a repo if
    20,000 <= LOC <= 400,000 (Python/JS-TS/Go) or 20,000 <= LOC <= 600,000 (Java);
  * Stop when N accepted repos per language (default 8). Every skipped repo is recorded with the reason.
Output: data/repos/selection_<lang>.json and data/repos/manifest.csv
"""
import csv, datetime, json, os, pathlib, subprocess, sys, time, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "repos"
CLONES = ROOT / "data" / "raw_repos"
DATA.mkdir(parents=True, exist_ok=True); CLONES.mkdir(parents=True, exist_ok=True)

LANGS = {
    "python": {"gh": "Python", "ext": {".py"}, "lo": 20000, "hi": 400000},
    "java": {"gh": "Java", "ext": {".java"}, "lo": 20000, "hi": 600000},
    "javascript": {"gh": "TypeScript", "ext": {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}, "lo": 20000, "hi": 400000},
    "go": {"gh": "Go", "ext": {".go"}, "lo": 20000, "hi": 400000},
}
EXCLUDE_DIRS = {"node_modules", "vendor", "third_party", "thirdparty", "external", "dist", "build", "out", ".git",
                "site-packages", "venv", ".venv", "fixtures", "__snapshots__", "testdata", "test-data", "generated", "gen"}
EXCLUDE_FILE_MARKERS = (".min.js", ".min.ts", ".d.ts", "_pb2.py", ".pb.go", "_generated", ".generated.")
N_PER_LANG = int(os.environ.get("N_PER_LANG", "8"))

def gh_search(lang_gh, page):
    q = f"language:{lang_gh} stars:>=5000 archived:false fork:false pushed:>=2026-01-01"
    cmd = ["gh", "api", "-X", "GET", "search/repositories", "-f", f"q={q}", "-f", "sort=stars", "-f", "order=desc",
           "-f", "per_page=50", "-f", f"page={page}"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return json.loads(r.stdout)

def count_loc(repo_dir, exts):
    files = 0; loc = 0
    for dp, dns, fns in os.walk(repo_dir):
        dns[:] = [d for d in dns if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for fn in fns:
            if pathlib.Path(fn).suffix in exts and not any(m in fn for m in EXCLUDE_FILE_MARKERS):
                p = pathlib.Path(dp) / fn
                try:
                    with open(p, "rb") as f:
                        n = sum(1 for line in f if line.strip())
                except Exception:
                    continue
                files += 1; loc += n
    return files, loc

def clone(full_name):
    dest = CLONES / full_name.replace("/", "__")
    if not dest.exists():
        subprocess.run(["git", "clone", "--depth", "1", "--quiet", f"https://github.com/{full_name}.git", str(dest)], check=True, timeout=1800)
    sha = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
    return dest, sha

def main(langs):
    manifest = []
    for lang in langs:
        cfg = LANGS[lang]
        snapshot = []; accepted = []; skipped = []
        page = 1
        while len(accepted) < N_PER_LANG and page <= 4:
            res = gh_search(cfg["gh"], page)
            items = res.get("items", [])
            if not items:
                break
            snapshot.extend([{k: it.get(k) for k in ("full_name", "stargazers_count", "size", "pushed_at", "default_branch", "license", "html_url", "language")} for it in items])
            for it in items:
                if len(accepted) >= N_PER_LANG:
                    break
                name = it["full_name"]
                lic = (it.get("license") or {}).get("spdx_id")
                if it["size"] > 1_500_000:  # > 1.5 GB repo: skip for feasibility
                    skipped.append({"repo": name, "reason": f"repo size {it['size']} KB > 1.5 GB"}); continue
                try:
                    dest, sha = clone(name)
                except Exception as e:
                    skipped.append({"repo": name, "reason": f"clone failed: {e}"}); continue
                files, loc = count_loc(dest, cfg["ext"])
                if loc < cfg["lo"] or loc > cfg["hi"]:
                    skipped.append({"repo": name, "reason": f"LOC {loc} outside [{cfg['lo']}, {cfg['hi']}]", "files": files, "loc": loc}); continue
                rec = {"repo": name, "sha": sha, "stars": it["stargazers_count"], "license": lic, "files": files, "loc": loc,
                       "default_branch": it["default_branch"], "clone_dir": str(dest.relative_to(ROOT))}
                accepted.append(rec); manifest.append({"lang": lang, **rec})
                print(lang, "ACCEPT", name, sha[:10], files, loc, flush=True)
            page += 1
        (DATA / f"selection_{lang}.json").write_text(json.dumps({"retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "query": f"language:{cfg['gh']} stars:>=5000 archived:false fork:false pushed:>=2026-01-01 sort=stars", "criteria": {k: (sorted(v) if isinstance(v, set) else v) for k, v in cfg.items()},
            "snapshot_order": snapshot, "accepted": accepted, "skipped": skipped}, indent=1), encoding="utf-8")
    # Reproduction must be idempotent: one run replaces the manifest instead of appending duplicate rows.
    # The manifest also carries licence columns added later from a hand-verified inspection of the clones
    # (data/repos/LICENSES.md); keep any column already present so a re-selection cannot silently drop them.
    base_fields = ["lang", "repo", "sha", "stars", "license", "files", "loc", "default_branch", "clone_dir"]
    manifest_path = DATA / "manifest.csv"
    existing_fields = []
    if manifest_path.exists():
        with manifest_path.open(encoding="utf-8", newline="") as fh:
            existing_fields = next(csv.reader(fh), [])
    fields = base_fields + [c for c in existing_fields if c not in base_fields]
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(manifest)

if __name__ == "__main__":
    main(sys.argv[1:] or list(LANGS))
