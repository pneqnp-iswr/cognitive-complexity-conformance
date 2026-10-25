"""Recompute the numbers of results/processed/coverage_causes.csv from the current function tables (after the
2026-09-17 pipeline fixes and reruns) while keeping the investigated causes; causes of the fixed pairs are replaced by
the residual cause. Also writes the per-language reference coverage. Run after scripts/analyze.py."""
import csv, pathlib, collections, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC = ROOT / "results" / "processed"
sys.path.insert(0, str(ROOT / "scripts"))
from analyze import primary_pop  # same population definition as the analysis (kinds, has_body, Java equals/hashCode)
LANGS = ["python", "java", "javascript", "go"]
RESIDUAL = {  # cause_short after the fixes (evidence in coverage_causes.md and RESEARCH_LOG.md)
    ("javascript", "codemetrics"): "codemetrics 0.12.7 reports function declarations and methods only, not arrow functions or function expressions",
    ("java", "cognitive-java"): "JavaParser (Java 21 level) rejects the Java 22 unnamed variable `_` used in 219 RxJava files",
    ("java", "lizard"): "lizard's Java reader stops after a method with an annotated type parameter (<@NonNull T>) in RxJava core files",
    ("python", "lizard"): "module-level lambdas and @overload stubs not reported",
    ("javascript", "eslint-plugin-maintainability"): "full coverage after the zero-fill fix (files without messages contain only cc = 0 functions)",
    ("javascript", "eslint-plugin-sonarjs-4.2.1"): "full coverage after the zero-fill fix (files without messages contain only cc = 0 functions)",
    ("javascript", "cognitive-complexity-ts"): "7 files fail to parse (excalidraw); computed-key arrow properties",
    ("javascript", "cogplexity"): "one-line arrays of arrows and computed-key arrow properties not aligned",
}
NOTE = "numbers recomputed after the pipeline fixes (see RESEARCH_LOG.md)"


def _with_note(evidence: str) -> str:
    """Append the provenance note once, however often this script is re-run."""
    base = " | ".join(part.strip() for part in evidence.split(" | ") if part.strip() and "numbers recomputed" not in part)
    return (base + " | " + NOTE).strip(" |")


old = {(r["lang"], r["tool"]): r for r in csv.DictReader(open(PROC / "coverage_causes.csv", encoding="utf-8"))} if (PROC / "coverage_causes.csv").exists() else {}
out = []
for lang in LANGS:
    rows = []
    for f in sorted((PROC / "functions").glob(f"{lang}__*.csv")):
        rows += list(csv.DictReader(open(f, encoding="utf-8")))
    prim = primary_pop(rows, lang)
    ref = [r for r in prim if r["cog__sonarqube"] != ""]
    tools = sorted({c for r in rows[:1] for c in r.keys() if c.startswith("cog__") or c.startswith("cyc__")})
    for col in tools:
        tool = col.split("__", 1)[1]
        if tool == "sonarqube":
            continue
        if col.startswith("cyc__") and tool not in ("lizard", "radon"):
            continue  # cyclomatic values of tools that also report cognitive are covered by their cognitive row
        have = [r for r in ref if r.get(col, "") != ""]
        repos = len({r["repo"] for r in have}); nrep = len({r["repo"] for r in ref})
        cov = 100 * len(have) / len(ref) if ref else 0
        prev = old.get((lang, tool), {})
        cause = RESIDUAL.get((lang, tool), prev.get("cause_short", ""))
        if cov >= 99.95:
            cause = "full coverage of the primary population"
        out.append({"lang": lang, "tool": tool, "n_ref": len(ref), "n_tool": len(have), "coverage_pct": f"{cov:.2f}", "repos_covered": f"{repos}/{nrep}",
                    "cause_short": cause, "evidence": _with_note(prev.get("evidence", ""))})
    out.append({"lang": lang, "tool": "sonarqube (reference)", "n_ref": len(prim), "n_tool": len(ref), "coverage_pct": f"{100 * len(ref) / len(prim):.2f}" if prim else "0",
                "repos_covered": f"{len({r['repo'] for r in ref})}/{len({r['repo'] for r in prim})}", "cause_short": "files the reference did not analyse (SonarPython skips test/generated files; Java/Go: files excluded by the scanner)", "evidence": "reference coverage = leaf root functions with a SonarQube value / all leaf root functions"})
with open(PROC / "coverage_causes.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["lang", "tool", "n_ref", "n_tool", "coverage_pct", "repos_covered", "cause_short", "evidence"]); w.writeheader(); w.writerows(out)
for r in out:
    print(f"{r['lang']:<11} {r['tool']:<32} {r['n_tool']:>6}/{r['n_ref']:<6} {r['coverage_pct']:>6}% {r['repos_covered']:<5} {r['cause_short'][:70]}")
