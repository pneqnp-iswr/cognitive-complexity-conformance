"""Adapters that run each Cognitive Complexity implementation and return normalized rows.

Row schema (dict): file (absolute path str), line (int, 1-based line the tool reports for the function),
end_line (int|None), name (str), value (int|None), metric ('cognitive'|'cyclomatic'), tool (str), extra (dict)

All adapters take a repo root and an explicit list of source files (absolute paths) so that every tool
sees exactly the same file set.
"""
from __future__ import annotations
import json, os, pathlib, re, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
VENV_PY = ROOT / "tools_venv" / "Scripts" / "python.exe"
RCA = TOOLS / "rca" / "target" / "release" / "rust-code-analysis-cli.exe"
CODEMETRICS = TOOLS / "codemetrics" / "codemetrics.exe"
PMD = TOOLS / "pmd-bin-7.27.0" / "bin" / "pmd.bat"
COGJAVA = TOOLS / "cognitive-java-cli-0.7.1.jar"
GOCOGNIT = TOOLS / "gopath" / "bin" / "gocognit.exe"
GOBIN = TOOLS / "go" / "bin"
JAVA17 = pathlib.Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot")
JAVA21 = pathlib.Path(r"C:\Program Files\Eclipse Adoptium\jdk-21.0.9.10-hotspot")
NODE_ADAPTER = ROOT / "src" / "js_cc.mjs"

TOOL_VERSIONS = {
    "sonarqube": "26.9.0.129388 (java 8.41, python 5.31, javascript 13.8, go 1.43.0)",
    "complexipy": "8.0.1", "cognitive_complexity": "1.3.0", "rust-code-analysis": "0.0.25", "codemetrics": "0.12.7",
    "pmd": "7.27.0", "cognitive-java": "0.7.1", "gocognit": "1.2.1", "cognitive-complexity-ts": "0.8.2", "cogplexity": "0.1.0",
    "oxlint-plugin-complexity": "3.0.0", "eslint-plugin-maintainability": "3.2.10", "eslint-plugin-sonarjs-4.2.1": "4.2.1",
    "radon": "6.0.1", "lizard": "1.24.0",
}

def _run(cmd, cwd=None, env=None, timeout=3600, input_text=None):
    e = dict(os.environ); e["PYTHONIOENCODING"] = "utf-8"
    if env:
        e.update(env)
    return subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, input=input_text)

def _norm(p):
    return str(pathlib.Path(p).resolve())

def _chunks_by_length(files, max_chars):
    """Split a file list into command-line-safe chunks (Windows limit ~32k chars)."""
    out, cur, n = [], [], 0
    for f in files:
        if cur and n + len(f) + 3 > max_chars:
            out.append(cur); cur, n = [], 0
        cur.append(f); n += len(f) + 3
    if cur:
        out.append(cur)
    return out

# ---------------------------------------------------------------- SonarQube (from scan JSON)
def rows_from_sonar(scan_json, repo_root):
    d = json.loads(pathlib.Path(scan_json).read_text(encoding="utf-8"))
    rows = []
    for r in d["rows"]:
        if r["kind"] not in ("cognitive", "cyclomatic"):
            continue
        val = r["value"]
        if val is None:
            m = re.search(r"is (\d+) which is greater", r["message"]) or re.search(r"complexity of (\d+)", r["message"])
            val = int(m.group(1)) if m else None
        rows.append({"file": _norm(pathlib.Path(repo_root) / r["file"]), "line": r["line"], "end_line": None, "name": "",
                     "value": val, "metric": r["kind"], "tool": "sonarqube", "extra": {"increments": r["increments"], "col": r["start_col"]}})
    return rows

# ---------------------------------------------------------------- Python tools
_PY_SCRIPT = r'''
import ast, json, sys, io
import complexipy
from cognitive_complexity.api import get_cognitive_complexity
from radon.complexity import cc_visit
out = []
for path in sys.stdin.read().splitlines():
    if not path.strip():
        continue
    try:
        fc = complexipy.file_complexity(path)
        for f in fc.functions:
            out.append({"file": path, "line": f.line_start, "end_line": f.line_end, "name": f.name, "value": f.complexity, "metric": "cognitive", "tool": "complexipy", "extra": {}})
    except Exception as e:
        out.append({"file": path, "line": None, "end_line": None, "name": "", "value": None, "metric": "cognitive", "tool": "complexipy", "extra": {"error": str(e)[:200]}})
    try:
        src = open(path, "rb").read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    v = get_cognitive_complexity(node)
                except Exception as e:
                    v = None
                out.append({"file": path, "line": node.lineno, "end_line": getattr(node, "end_lineno", None), "name": node.name, "value": v, "metric": "cognitive", "tool": "cognitive_complexity", "extra": {}})
        for b in cc_visit(src.decode("utf-8", "replace")):
            # radon: functions and methods (class blocks carry methods)
            items = [b] + list(getattr(b, "methods", []))
            for it in items:
                if it.__class__.__name__ in ("Function",):
                    out.append({"file": path, "line": it.lineno, "end_line": it.endline, "name": it.name, "value": it.complexity, "metric": "cyclomatic", "tool": "radon", "extra": {"is_method": it.is_method}})
    except Exception as e:
        out.append({"file": path, "line": None, "end_line": None, "name": "", "value": None, "metric": "cognitive", "tool": "cognitive_complexity", "extra": {"error": str(e)[:200]}})
json.dump(out, sys.stdout)
'''

def run_python_tools(files):
    r = _run([str(VENV_PY), "-c", _PY_SCRIPT], input_text="\n".join(files) + "\n", timeout=7200)
    if r.returncode != 0:
        raise RuntimeError("python tools failed: " + r.stderr[-2000:])
    rows = json.loads(r.stdout)
    for x in rows:
        x["file"] = _norm(x["file"])
    return rows

# ---------------------------------------------------------------- rust-code-analysis (per file, JSON)
def run_rca(files):
    rows = []
    for f in files:
        r = _run([str(RCA), "-m", "-O", "json", "-p", f], timeout=600)
        if r.returncode != 0 or not r.stdout.strip():
            rows.append({"file": _norm(f), "line": None, "end_line": None, "name": "", "value": None, "metric": "cognitive", "tool": "rust-code-analysis", "extra": {"error": (r.stderr or "no output")[:200]}})
            continue
        try:
            d = json.loads(r.stdout)
        except Exception as e:
            rows.append({"file": _norm(f), "line": None, "end_line": None, "name": "", "value": None, "metric": "cognitive", "tool": "rust-code-analysis", "extra": {"error": "bad json"}})
            continue
        def walk(s):
            if s["kind"] in ("function",):
                m = s["metrics"]
                rows.append({"file": _norm(f), "line": s["start_line"], "end_line": s["end_line"], "name": s["name"], "value": int(m["cognitive"]["sum"]), "metric": "cognitive", "tool": "rust-code-analysis", "extra": {}})
                rows.append({"file": _norm(f), "line": s["start_line"], "end_line": s["end_line"], "name": s["name"], "value": int(m["cyclomatic"]["sum"]), "metric": "cyclomatic", "tool": "rust-code-analysis", "extra": {}})
            for c in s.get("spaces", []):
                walk(c)
        walk(d)
    return rows

# ---------------------------------------------------------------- codemetrics (multi-language, dir walk)
def run_codemetrics(files):
    rows = []
    # pass files explicitly in chunks (Windows command-line length limit)
    def run_chunk(chunk):
        # codemetrics prints `null` (or nothing) for a whole invocation when one file makes it fail; bisect the chunk so
        # that only the offending files are recorded as errors (fix of 2026-09-17; before, the whole repository was lost).
        r = _run([str(CODEMETRICS), "--format", "json", "--include-vendored"] + chunk, timeout=1800)
        d = None
        if r.stdout.strip():
            try:
                d = json.loads(r.stdout)
            except Exception:
                d = None
        if not isinstance(d, list):
            if len(chunk) > 1:
                h = len(chunk) // 2
                run_chunk(chunk[:h]); run_chunk(chunk[h:])
            else:
                rows.append({"file": _norm(chunk[0]), "line": None, "end_line": None, "name": "", "value": None, "metric": "cognitive", "tool": "codemetrics", "extra": {"error": (r.stderr or r.stdout)[:200]}})
            return
        for it in d:
            rows.append({"file": _norm(it["file"]), "line": it["start_line"], "end_line": it["end_line"], "name": it["function"], "value": it["cognitive"], "metric": "cognitive", "tool": "codemetrics", "extra": {}})
            rows.append({"file": _norm(it["file"]), "line": it["start_line"], "end_line": it["end_line"], "name": it["function"], "value": it["cyclomatic"], "metric": "cyclomatic", "tool": "codemetrics", "extra": {}})
    for chunk in _chunks_by_length(files, 20000):
        run_chunk(chunk)
    return rows

# ---------------------------------------------------------------- PMD 7 (Java)
PMD_RULESET = ROOT / "experiments" / "pmd-cc.xml"
def run_pmd(files, repo_root):
    if not PMD_RULESET.exists():
        PMD_RULESET.write_text('''<?xml version="1.0"?>
<ruleset name="cc" xmlns="http://pmd.sourceforge.net/ruleset/2.0.0">
  <description>Cognitive and cyclomatic complexity, report every method</description>
  <rule ref="category/java/design.xml/CognitiveComplexity"><properties><property name="reportLevel" value="1"/></properties></rule>
  <rule ref="category/java/design.xml/CyclomaticComplexity"><properties><property name="methodReportLevel" value="1"/><property name="classReportLevel" value="9999"/></properties></rule>
</ruleset>
''', encoding="utf-8")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tf:
        tf.write("\n".join(files) + "\n"); listfile = tf.name
    out = tempfile.mktemp(suffix=".json")
    env = {"JAVA_HOME": str(JAVA17), "PATH": str(JAVA17 / "bin") + os.pathsep + os.environ["PATH"], "PMD_JAVA_OPTS": "-Xmx6g -Dfile.encoding=UTF-8"}
    r = _run([str(PMD), "check", "--file-list", listfile, "-R", str(PMD_RULESET), "-f", "json", "-r", out, "--no-progress", "--no-cache", "-t", "8"], env=env, timeout=7200)
    rows = []
    if not pathlib.Path(out).exists():
        raise RuntimeError("PMD produced no report: " + r.stdout[-1500:] + r.stderr[-1500:])
    d = json.loads(pathlib.Path(out).read_text(encoding="utf-8"))
    for fobj in d.get("files", []):
        for v in fobj.get("violations", []):
            m = re.search(r"has a (cognitive|cyclomatic) complexity of (\d+)", v["description"])
            if not m:
                continue
            nm = re.search(r"The (?:method|constructor) '([^']*)'", v["description"])
            rows.append({"file": _norm(fobj["filename"]), "line": v["beginline"], "end_line": None, "name": nm.group(1) if nm else "",
                         "value": int(m.group(2)), "metric": m.group(1), "tool": "pmd", "extra": {"col": v["begincolumn"]}})
    rows.append({"file": "", "line": None, "end_line": None, "name": "", "value": None, "metric": "meta", "tool": "pmd",
                 "extra": {"processingErrors": d.get("processingErrors", [])[:50], "n_processing_errors": len(d.get("processingErrors", []))}})
    os.unlink(listfile); os.unlink(out)
    return rows

# ---------------------------------------------------------------- cognitive-java (fabian-barney)
def run_cognitive_java(files, repo_root):
    rows = []
    rel = [os.path.relpath(f, repo_root) for f in files]
    env = {"JAVA_HOME": str(JAVA21), "PATH": str(JAVA21 / "bin") + os.pathsep + os.environ["PATH"]}
    def run_chunk(chunk):
        # A chunk that fails to parse (e.g. one file with Java 22 syntax that JavaParser rejects) used to be dropped
        # entirely. Since 2026-09-17 the file named in the parse error is recorded as an error row and the chunk is
        # retried without it, so that only the offending files are lost.
        chunk = list(chunk)
        while chunk:
            r = _run([str(JAVA21 / "bin" / "java.exe"), "-Xmx4g", "-jar", str(COGJAVA), "--format", "json", "--threshold", "1", "--failures-only=false",
                      "--use-default-exclusions=false"] + chunk, cwd=repo_root, env=env, timeout=3600)
            txt = r.stdout
            j = txt.find("{")
            try:
                d = json.loads(txt[j:txt.rfind("}") + 1])
                break
            except Exception:
                err = (r.stdout + r.stderr)[-800:]
                m = re.search(r"Failed to parse Java source:\s*\n?\s*(\S+?\.java):\d+", r.stdout + r.stderr)
                bad = None
                if m:
                    tail = m.group(1).replace("\\", "/").lstrip("/")
                    bad = next((c for c in chunk if c.replace("\\", "/").endswith(tail)), None)
                if bad is None:
                    if len(chunk) > 1:  # unknown failure: bisect
                        h = len(chunk) // 2
                        run_chunk(chunk[:h]); run_chunk(chunk[h:])
                    else:
                        rows.append({"file": _norm(pathlib.Path(repo_root) / chunk[0]), "line": None, "end_line": None, "name": "", "value": None, "metric": "meta", "tool": "cognitive-java", "extra": {"error": err}})
                    return
                rows.append({"file": _norm(pathlib.Path(repo_root) / bad), "line": None, "end_line": None, "name": "", "value": None, "metric": "meta", "tool": "cognitive-java", "extra": {"error": err}})
                chunk.remove(bad)
        else:
            return
        for mth in d.get("methods", []):
            rows.append({"file": _norm(pathlib.Path(repo_root) / mth["src"]), "line": mth["lineStart"], "end_line": mth.get("lineEnd"), "name": mth["method"],
                         "value": mth["cc"], "metric": "cognitive", "tool": "cognitive-java", "extra": {}})
        rows.append({"file": "", "line": None, "end_line": None, "name": "", "value": None, "metric": "meta", "tool": "cognitive-java", "extra": {"exclusions": d.get("exclusions"), "n_files": len(chunk)}})
    for i in range(0, len(rel), 200):
        run_chunk(rel[i:i + 200])
    return rows

# ---------------------------------------------------------------- gocognit (Go)
def run_gocognit(repo_root, files):
    env = {"PATH": str(GOBIN) + os.pathsep + os.environ["PATH"], "GOFLAGS": "-mod=mod", "GOPATH": str(TOOLS / "gopath"), "GOCACHE": str(TOOLS / "gocache")}
    r = _run([str(GOCOGNIT), "-over", "0", "-json", "-d", "."], cwd=repo_root, env=env, timeout=3600)
    rows = []
    try:
        d = json.loads(r.stdout) if r.stdout.strip() else []
    except Exception:
        return [{"file": "", "line": None, "end_line": None, "name": "", "value": None, "metric": "meta", "tool": "gocognit", "extra": {"error": r.stdout[:300] + r.stderr[:300]}}]
    want = set(_norm(f) for f in files)
    for it in d or []:
        fp = _norm(pathlib.Path(repo_root) / it["Pos"]["Filename"])
        if fp not in want:
            continue
        rows.append({"file": fp, "line": it["Pos"]["Line"], "end_line": None, "name": it["FuncName"], "value": it["Complexity"], "metric": "cognitive", "tool": "gocognit",
                     "extra": {"diagnostics": [(x.get("Inc"), x.get("Nesting"), x.get("Text"), x.get("Pos", {}).get("Line")) for x in it.get("Diagnostics", [])][:80]}})
    return rows

# ---------------------------------------------------------------- lizard (cyclomatic, all languages)
def run_lizard(files):
    import csv as _csv, io as _io
    rows = []
    for chunk in _chunks_by_length(files, 20000):
        r = _run([str(ROOT / "tools_venv" / "Scripts" / "lizard.exe"), "--csv"] + chunk, timeout=3600)
        for parts in _csv.reader(_io.StringIO(r.stdout)):
            # NLOC, CCN, token, PARAM, length, location, file, function, long_name, start_line, end_line
            if len(parts) < 11:
                continue
            try:
                ccn = int(parts[1]); fpath = parts[6]; name = parts[7]; start = int(parts[9]); end = int(parts[10])
            except Exception:
                continue
            rows.append({"file": _norm(fpath), "line": start, "end_line": end, "name": name, "value": ccn, "metric": "cyclomatic", "tool": "lizard", "extra": {}})
    return rows

# ---------------------------------------------------------------- JS/TS tools via node adapter
def run_js_tool(tool, files):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tf:
        tf.write("\n".join(files) + "\n"); listfile = tf.name
    r = _run(["node", "--max-old-space-size=8192", str(NODE_ADAPTER), tool, listfile], timeout=7200)
    os.unlink(listfile)
    if r.returncode != 0:
        raise RuntimeError(f"node adapter {tool} failed: {r.stderr[-2000:]}")
    d = json.loads(r.stdout)
    rows = []
    for x in d["rows"]:
        rows.append({"file": _norm(x["file"]), "line": x["line"], "end_line": x.get("endLine"), "name": x.get("name", ""), "value": x["value"], "metric": "cognitive", "tool": x["tool"], "extra": x.get("extra", {})})
        if x["tool"] == "oxlint-plugin-complexity" and x.get("extra", {}).get("cyclomatic") is not None:
            rows.append({"file": _norm(x["file"]), "line": x["line"], "end_line": x.get("endLine"), "name": x.get("name", ""), "value": x["extra"]["cyclomatic"], "metric": "cyclomatic", "tool": x["tool"], "extra": {}})
    rows.append({"file": "", "line": None, "end_line": None, "name": "", "value": None, "metric": "meta", "tool": d["tool"], "extra": {"errors": d["errors"][:100], "n_errors": len(d["errors"])}})
    return rows

# ---------------------------------------------------------------- cognitive-complexity-ts (CLI, per file)
def run_ccts(files):
    """cognitive-complexity-ts via its programmatic API (src/ccts_batch.mjs): the CLI only handles one file per call."""
    rows = []
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tf:
        tf.write(chr(10).join(files) + chr(10)); listfile = tf.name
    r = _run(["node", "--max-old-space-size=8192", str(ROOT / "src" / "ccts_batch.mjs"), listfile], timeout=7200)
    os.unlink(listfile)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return [{"file": "", "line": None, "end_line": None, "name": "", "value": None, "metric": "meta", "tool": "cognitive-complexity-ts", "extra": {"error": (r.stdout + r.stderr)[-500:]}}]
    def walk(fp, node, depth):
        for it in node.get("inner", []):
            if it.get("kind") == "function":
                rows.append({"file": _norm(fp), "line": it["line"], "end_line": None, "name": it.get("name", ""), "value": it["score"], "metric": "cognitive", "tool": "cognitive-complexity-ts", "extra": {"col": it.get("column"), "depth": depth}})
            walk(fp, it, depth + 1)
    for fp, fnode in d["results"].items():
        walk(fp, fnode, 0)
    for e in d["errors"]:
        rows.append({"file": _norm(e["file"]), "line": None, "end_line": None, "name": "", "value": None, "metric": "cognitive", "tool": "cognitive-complexity-ts", "extra": {"error": e["msg"]}})
    rows.append({"file": "", "line": None, "end_line": None, "name": "", "value": None, "metric": "meta", "tool": "cognitive-complexity-ts", "extra": {"n_failed_files": len(d["errors"]), "errors": d["errors"][:20]}})
    return rows
