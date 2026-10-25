"""Scan a directory with sonar-scanner as project <key>, wait for CE task completion, then extract all
issues of the complexity rules (per-file paging to stay under the 10,000-result cap) into a JSON file.

Usage: py -3.11 scripts/sonar_scan.py <project_key> <source_dir> <out_json> [--lang py|java|js|go] [--extra k=v ...]
"""
import argparse, json, pathlib, re, subprocess, sys, time, requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCANNER = ROOT / "tools" / "sonar-scanner-8.1.0.6389-windows-x64" / "bin" / "sonar-scanner.bat"
BASE = "http://localhost:9000"
AUTH = ("admin", "admin")
TOKEN = (ROOT / "data" / "sonar_token.txt").read_text(encoding="utf-8").strip()
CC_RULES = {"python:S3776", "java:S3776", "javascript:S3776", "typescript:S3776", "go:S3776"}
CY_RULES = {"python:FunctionComplexity", "java:S1541", "javascript:S1541", "typescript:S1541"}
JAVA17 = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"

def api(path, **params):
    r = requests.get(BASE + path, auth=AUTH, params=params, timeout=120)
    r.raise_for_status()
    return r.json()

def run_scan(key, src, lang, extra, log_path):
    src = pathlib.Path(src).resolve()
    args = [str(SCANNER), f"-Dsonar.projectKey={key}", f"-Dsonar.projectName={key}", f"-Dsonar.host.url={BASE}",
            f"-Dsonar.token={TOKEN}", f"-Dsonar.projectBaseDir={src}", "-Dsonar.sources=.", "-Dsonar.scm.disabled=true",
            "-Dsonar.sourceEncoding=UTF-8", "-Dsonar.cpd.exclusions=**/*", "-Dsonar.exclusions=**/node_modules/**,**/vendor/**,**/third_party/**,**/*.min.js"]
    if lang == "java":
        # metric is purely syntactic; binaries dir can be empty
        (src / ".sonar_empty_bin").mkdir(exist_ok=True)
        args += [f"-Dsonar.java.binaries={src / '.sonar_empty_bin'}", "-Dsonar.java.source=21", "-Dsonar.inclusions=**/*.java"]
    elif lang == "py":
        args += ["-Dsonar.python.version=3.12", "-Dsonar.inclusions=**/*.py"]
    elif lang == "js":
        args += ["-Dsonar.inclusions=**/*.js,**/*.jsx,**/*.mjs,**/*.cjs,**/*.ts,**/*.tsx", "-Dsonar.javascript.maxFileSize=4000",
                 "-Dsonar.typescript.tsconfigPaths=", "-Dsonar.javascript.node.maxspace=8192"]
    elif lang == "go":
        args += ["-Dsonar.inclusions=**/*.go", "-Dsonar.go.exclusions="]
    for e in extra:
        args.append("-D" + e)
    env = dict(**__import__("os").environ)
    env["JAVA_HOME"] = JAVA17
    t0 = time.time()
    with open(log_path, "w", encoding="utf-8", errors="replace") as log:
        p = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=str(src))
    dt = time.time() - t0
    txt = pathlib.Path(log_path).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"api/ce/task\?id=([A-Za-z0-9_-]+)", txt) or re.search(r"ceTaskId=([A-Za-z0-9_-]+)", txt)
    if p.returncode != 0 or not m:
        tail = txt[-3000:]
        raise RuntimeError(f"scanner failed rc={p.returncode}\n{tail}")
    task = m.group(1)
    while True:
        st = api("/api/ce/task", id=task)["task"]
        if st["status"] in ("SUCCESS", "FAILED", "CANCELED"):
            break
        time.sleep(3)
    if st["status"] != "SUCCESS":
        raise RuntimeError(f"CE task {task} status {st['status']}: {st.get('errorMessage')}")
    return dt, st.get("analysisId")

def list_files(key):
    files, page = [], 1
    while True:
        j = api("/api/components/tree", component=key, qualifiers="FIL", ps=500, p=page)
        files += [c["key"] for c in j["components"]]
        if page * 500 >= j["paging"]["total"]:
            break
        page += 1
    return files

def fetch_issues(key):
    out = []
    # total count first
    tot = api("/api/issues/search", componentKeys=key, ps=1, resolved="false")["total"]
    if tot < 10000:
        page = 1
        while True:
            j = api("/api/issues/search", componentKeys=key, ps=500, p=page, resolved="false", additionalFields="_all")
            out += j["issues"]
            if page * 500 >= j["total"]:
                break
            page += 1
    else:
        for fk in list_files(key):
            page = 1
            while True:
                j = api("/api/issues/search", componentKeys=fk, ps=500, p=page, resolved="false", additionalFields="_all")
                out += j["issues"]
                if page * 500 >= j["total"]:
                    break
                page += 1
    return out

def normalize(issues):
    rows = []
    for it in issues:
        rule = it["rule"]
        kind = "cognitive" if rule in CC_RULES else "cyclomatic" if rule in CY_RULES else "other"
        msg = it.get("message", "")
        m = re.search(r"from (\d+) to the (\d+) allowed", msg) or re.search(r"(\d+)[^\d]+(\d+)\s*allowed", msg) or re.search(r"complexity of (\d+)", msg, re.I)
        val = int(m.group(1)) if m else None
        flows = []
        for fl in it.get("flows", []):
            for loc in fl.get("locations", []):
                tr = loc.get("textRange", {})
                flows.append({"line": tr.get("startLine"), "col": tr.get("startOffset"), "msg": loc.get("msg")})
        tr = it.get("textRange", {})
        rows.append({"file": it["component"].split(":", 1)[1], "rule": rule, "kind": kind, "line": it.get("line"),
                     "start_line": tr.get("startLine"), "start_col": tr.get("startOffset"), "end_line": tr.get("endLine"),
                     "value": val, "message": msg, "increments": flows})
    return rows

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("key"); ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--lang", default="py"); ap.add_argument("--extra", nargs="*", default=[])
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    log = out.with_suffix(".scanner.log")
    dt, analysis = run_scan(a.key, a.src, a.lang, a.extra, log)
    issues = fetch_issues(a.key)
    rows = normalize(issues)
    meta = {"project_key": a.key, "source_dir": str(pathlib.Path(a.src).resolve()), "lang": a.lang, "scan_seconds": round(dt, 1),
            "analysis_id": analysis, "server_version": requests.get(BASE + "/api/server/version", auth=AUTH).text,
            "n_issues": len(issues), "n_cognitive": sum(r["kind"] == "cognitive" for r in rows),
            "n_cyclomatic": sum(r["kind"] == "cyclomatic" for r in rows)}
    out.write_text(json.dumps({"meta": meta, "rows": rows}, indent=1), encoding="utf-8")
    print(json.dumps(meta))
