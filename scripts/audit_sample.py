"""Draw the audit sample (fixed in advance; inspected by an AI agent): 30 random disagreeing leaf-root functions per language
(seed 20260917), stratified over tools, with source snippets, for manual inspection of alignment and attribution.
Output: results/processed/audit_<lang>.csv (judgement columns left empty for the auditor) and audit_<lang>_snippets.txt"""
import csv, json, pathlib, random, sys, collections
ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC = ROOT / "results" / "processed"
LANGS = ["python", "java", "javascript", "go"]
PRIMARY_KINDS = {"python": {"function"}, "java": {"method", "constructor"}, "javascript": {"function", "function_expr", "arrow", "method"}, "go": {"function", "method"}}
N = 30

def main():
    mpath = ROOT / "data" / "repos" / "manifest.csv"
    man = {r["repo"]: r for r in csv.DictReader(open(mpath, encoding="utf-8"))} if mpath.exists() else {}
    for sp in (ROOT / "data" / "repos").glob("selection_*.json"):
        for a in json.loads(sp.read_text(encoding="utf-8"))["accepted"]:
            man.setdefault(a["repo"], a)
    for lang in LANGS:
        existing = PROC / f"audit_{lang}.csv"
        if existing.exists() and any(r["alignment_correct"] for r in csv.DictReader(open(existing, encoding="utf-8"))):
            print(lang, "audit already judged; not regenerated"); continue
        rows = []
        for f in sorted((PROC / "functions").glob(f"{lang}__*.csv")):
            rows += list(csv.DictReader(open(f, encoding="utf-8")))
        if not rows:
            continue
        pop = [r for r in rows if r["depth"] == "0" and r["has_nested"] == "0" and r["kind"] in PRIMARY_KINDS[lang] and r.get("has_body", "1") != "0" and r["cog__sonarqube"] != "" and not (lang == "java" and r["name"] in ("equals", "hashCode"))]
        tools = sorted(set().union(*(r.keys() for r in rows)) - {"cog__sonarqube"}); tools = [c for c in tools if c.startswith("cog__")]
        dis = []
        for r in pop:
            for t in tools:
                if r.get(t, "") != "" and int(r[t]) != int(r["cog__sonarqube"]):
                    dis.append((t, r))
        rng = random.Random(20260917)
        by_tool = collections.defaultdict(list)
        for t, r in dis:
            by_tool[t].append(r)
        sample = []
        k = 0
        while len(sample) < min(N, len(dis)):
            t = tools[k % len(tools)]; k += 1
            if by_tool[t]:
                r = by_tool[t].pop(rng.randrange(len(by_tool[t]))); sample.append((t, r))
        out = []; snippets = []
        for i, (t, r) in enumerate(sample, 1):
            repo_dir = ROOT / man[r["repo"]]["clone_dir"]
            src = (repo_dir / r["file"]).read_text(encoding="utf-8", errors="replace").splitlines()
            a, b = int(r["decl_line"]) - 1, int(r["end_line"])
            snippet = "\n".join(src[a:min(b, a + 60)])
            out.append({"audit_id": f"{lang}-{i:02d}", "tool": t.replace("cog__", ""), "repo": r["repo"], "file": r["file"], "function": r["qualified_name"], "decl_line": r["decl_line"],
                        "ref_value": r["cog__sonarqube"], "tool_value": r[t], "features": r["features"], "logical_ops": r["logical_ops"], "recursion_direct": r["recursion_direct"],
                        "alignment_correct": "", "cause": "", "note": ""})
            snippets.append(f"===== {lang}-{i:02d} tool={t} ref={r['cog__sonarqube']} tool_value={r[t]} {r['repo']} {r['file']}:{r['decl_line']} {r['qualified_name']}\n{snippet}\n")
        with open(PROC / f"audit_{lang}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
        (PROC / f"audit_{lang}_snippets.txt").write_text("\n".join(snippets), encoding="utf-8")
        print(lang, "disagreements:", len(dis), "sampled:", len(sample))

if __name__ == "__main__":
    main()
