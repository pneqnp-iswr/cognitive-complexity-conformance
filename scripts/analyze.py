"""Analysis for RQ1-RQ4 (see RESEARCH_CONTRACT.md / EXPERIMENT_PROTOCOL.md).
Inputs: results/processed/functions/*.csv, results/processed/microcorpus_matrix.csv, experiments/microcorpus/expected.csv
Outputs (results/processed/):
  conformance_<summary>.csv          RQ1 per-tool conformance on unambiguous micro-corpus cases + per-rule failures
  ambiguity_readings.csv             RQ1 observed readings on ambiguous cases
  agreement_<lang>.csv               RQ2 per tool: n, exact, within1, MAD, rho, direction, bootstrap CIs
  flips_<lang>.csv                   RQ3 per tool x threshold: flip rates overall / near-window, precision, recall
  attribution_<lang>.csv             RQ4 per tool: share of disagreements attributed by construct-presence predicates
  cyclomatic_<lang>.csv              baseline: cyclomatic cross-tool agreement
  coverage_<lang>.csv                per tool: units, aligned, missing
  container_<lang>.csv               secondary: root functions with nested units
  summary.json                       everything, for result_manifest generation
Randomness: cluster bootstrap over repositories, 2000 resamples, seed 20260917.
"""
import csv, json, math, pathlib, random, re, statistics, collections
import numpy as np
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC = ROOT / "results" / "processed"
FUNC = PROC / "functions"
SEED = 20260917; B = 2000
THRESHOLDS = [10, 15, 20, 25]
LANGS = ["python", "java", "javascript", "go"]
PRIMARY_KINDS = {"python": {"function"}, "java": {"method", "constructor"}, "javascript": {"function", "function_expr", "arrow", "method"}, "go": {"function", "method"}}
REF = "cog__sonarqube"
REF_CYC = "cyc__sonarqube"
DRIFT_PROBE = {"cog__eslint-plugin-sonarjs-4.2.1"}

# target rule -> predicate over a function row (features json, logical_ops json, recursion flag)
def _pred_factory():
    def has(feat, *ks):
        return any(feat.get(k, 0) > 0 for k in ks)
    return {
        "B1.1": lambda f, ops, rec: has(f, "if", "ternary"),
        "B1.2": lambda f, ops, rec: has(f, "switch", "match", "switch_block", "select"),
        "B1.3": lambda f, ops, rec: has(f, "for"),
        "B1.4": lambda f, ops, rec: has(f, "while", "for"),
        "B1.5": lambda f, ops, rec: has(f, "catch"),
        "B1.6": lambda f, ops, rec: has(f, "label", "goto"),
        "B1.7": lambda f, ops, rec: sum(ops.values()) > 0,
        "B1.7and": lambda f, ops, rec: (ops.get("&&", 0) + ops.get("and", 0)) > 0,
        "B1.7or": lambda f, ops, rec: (ops.get("||", 0) + ops.get("or", 0)) > 0,
        "B1.7mix": lambda f, ops, rec: (ops.get("&&", 0) + ops.get("and", 0)) > 0 and (ops.get("||", 0) + ops.get("or", 0)) > 0,
        "B1.7idiom": lambda f, ops, rec: False,  # the `x = x || default` idiom is not distinguishable in the features
        "B1.7bit": lambda f, ops, rec: False,
        "B3.1t": lambda f, ops, rec: has(f, "ternary"),
        "ARROW": lambda f, ops, rec: rec.get("kind") == "arrow",
        "B1.8": lambda f, ops, rec: rec["direct"],
        "B1.8d": lambda f, ops, rec: rec["direct"] and not rec["method"],  # plain direct recursion
        "B1.8d2": lambda f, ops, rec: rec["calls"] >= 2,  # direct recursion with several call sites
        "B1.8m": lambda f, ops, rec: rec["method"],  # recursion through self/this/receiver
        "B1.8i": lambda f, ops, rec: False,  # indirect recursion is not detectable from one function
        "R2": lambda f, ops, rec: has(f, "else", "elif"),
        "B2.1": lambda f, ops, rec: has(f, "else", "elif"),
        "R7": lambda f, ops, rec: has(f, "try", "finally"),
        "R11": lambda f, ops, rec: False,
        "R13": lambda f, ops, rec: ops.get("??", 0) > 0,
        "R14": lambda f, ops, rec: has(f, "break", "continue"),
        "R15": lambda f, ops, rec: has(f, "paren_bool"),
        "B2.4": lambda f, ops, rec: has(f, "while", "for") and has(f, "ternary"),
        "B2.6": lambda f, ops, rec: has(f, "lambda", "nested_def", "nested_fn", "anon_class"),
        "A.2": lambda f, ops, rec: has(f, "nested_fn", "lambda"),
        "A.3": lambda f, ops, rec: has(f, "nested_def"),
        "B3": lambda f, ops, rec: has(f, "if", "ternary", "switch", "catch") and has(f, "for", "while", "catch"),
        "B3.1": lambda f, ops, rec: has(f, "ternary") and has(f, "if"),
        "B1.3a": lambda f, ops, rec: has(f, "async_for"),
        "COMP": lambda f, ops, rec: has(f, "comprehension", "comp_for", "comp_if"),
        "GO-ERRNIL": lambda f, ops, rec: has(f, "if_nil_check"),
        "ELSE-LOOP": lambda f, ops, rec: has(f, "else") and has(f, "for", "while", "try"),
        "C": lambda f, ops, rec: False,
    }
PRED = _pred_factory()

def load_functions():
    data = collections.defaultdict(list)
    for p in sorted(FUNC.glob("*.csv")):
        lang = p.name.split("__")[0]
        for r in csv.DictReader(open(p, encoding="utf-8")):
            data[lang].append(r)
    return data

def primary_pop(rows, lang):
    out = []
    for r in rows:
        if r["depth"] != "0" or r["has_nested"] != "0" or r["kind"] not in PRIMARY_KINDS[lang] or r.get("has_body", "1") == "0":
            continue
        if lang == "java" and r["name"] in ("equals", "hashCode"):
            continue
        out.append(r)
    return out

def cluster_bootstrap(pairs_by_repo, statfn, seed=SEED, b=B):
    rng = random.Random(seed)
    repos = sorted(pairs_by_repo)
    vals = []
    for _ in range(b):
        samp = [rng.choice(repos) for _ in repos]
        pool = [p for rp in samp for p in pairs_by_repo[rp]]
        if pool:
            v_ = statfn(pool)
            if v_ is not None and v_ == v_:
                vals.append(v_)
    if not vals:
        return (float("nan"), float("nan"))
    vals.sort()
    return (vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1])

def agreement_stats(pop, tool, ref=REF):
    by_repo = collections.defaultdict(list)
    for r in pop:
        if r.get(ref, "") != "" and r.get(tool, "") != "":
            by_repo[r["repo"]].append((int(r[ref]), int(r[tool])))
    pairs = [p for v in by_repo.values() for p in v]
    if not pairs:
        return None
    a = np.array([p[0] for p in pairs]); t = np.array([p[1] for p in pairs])
    exact = float(np.mean(a == t)); within1 = float(np.mean(np.abs(a - t) <= 1)); mad = float(np.mean(np.abs(a - t)))
    rho = float(stats.spearmanr(a, t).statistic) if len(pairs) > 2 and a.std() > 0 and t.std() > 0 else float("nan")
    lo, hi = cluster_bootstrap(by_repo, lambda pool: sum(x == y for x, y in pool) / len(pool))
    res = {"tool": tool.replace("cog__", "").replace("cyc__", ""), "n": len(pairs), "n_repos": len(by_repo), "exact": exact, "exact_ci_lo": lo, "exact_ci_hi": hi,
           "within1": within1, "mad": mad, "spearman": rho, "share_tool_higher": float(np.mean(t > a)), "share_tool_lower": float(np.mean(t < a)),
           "max_abs_diff": int(np.max(np.abs(a - t))), "mean_ref": float(a.mean()), "mean_tool": float(t.mean())}
    pos = [(x, y) for x, y in pairs if x > 0]
    res["n_pos"] = len(pos); res["exact_pos"] = (sum(x == y for x, y in pos) / len(pos)) if pos else float("nan")
    both = [(x, y) for x, y in pairs if x > 0 and y > 0]  # both values reported (above the reporting threshold)
    res["n_both_pos"] = len(both); res["exact_both_pos"] = (sum(x == y for x, y in both) / len(both)) if both else float("nan")
    both = [(x, y) for x, y in pairs if x > 0 and y > 0]  # both values reported (above the reporting threshold)
    res["n_both_pos"] = len(both); res["exact_both_pos"] = (sum(x == y for x, y in both) / len(both)) if both else float("nan")
    res["share_ref_zero"] = float(np.mean(a == 0))
    per_repo = {rp: sum(x == y for x, y in v) / len(v) for rp, v in by_repo.items()}
    res["exact_min_repo"] = min(per_repo.values()); res["exact_max_repo"] = max(per_repo.values())
    return res, pairs, by_repo

def flip_stats(pairs, by_repo, tool, thresholds=THRESHOLDS):
    out = []
    for th in thresholds:
        flips = [(x > th) != (y > th) for x, y in pairs]
        near = [(x, y) for x, y in pairs if th - 5 <= x <= th + 5]
        nflips = [(x > th) != (y > th) for x, y in near]
        ref_flag = sum(x > th for x, y in pairs); tool_flag = sum(y > th for x, y in pairs); both = sum(x > th and y > th for x, y in pairs)
        lo, hi = cluster_bootstrap(by_repo, lambda pool: sum((x > th) != (y > th) for x, y in pool) / len(pool))
        def _near_rate(pool, th=th):
            nn = [(x, y) for x, y in pool if th - 5 <= x <= th + 5]
            return (sum((x > th) != (y > th) for x, y in nn) / len(nn)) if nn else None
        nlo, nhi = cluster_bootstrap(by_repo, _near_rate)
        out.append({"tool": tool.replace("cog__", ""), "threshold": th, "n": len(pairs), "flip_rate": sum(flips) / len(pairs), "flip_ci_lo": lo, "flip_ci_hi": hi,
                    "n_near": len(near), "flip_rate_near": (sum(nflips) / len(near)) if near else float("nan"), "flip_near_ci_lo": nlo, "flip_near_ci_hi": nhi,
                    "ref_flagged": ref_flag, "tool_flagged": tool_flag, "both_flagged": both,
                    "precision": both / tool_flag if tool_flag else float("nan"), "recall": both / ref_flag if ref_flag else float("nan"),
                    "share_ref_flagged": ref_flag / len(pairs)})
    return out

def _family(code):
    """B1.7or -> B1.7, B1.8d2 -> B1.8, B3.1t -> B3.1, A.2 -> A.2, R15 -> R15, COMP -> COMP."""
    m = re.match(r"^([A-Z]+(?:\d+)?(?:\.\d+)?)", code)
    return m.group(1) if m else code

def microcorpus_deviations():
    """Per (lang, tool): targets of unambiguous mismatches (dev_conf) and targets of ambiguous cases where the tool's
    value differs from the SonarQube reference (dev_amb); plus the conformance table and ambiguity readings."""
    exp = {r["case_id"]: r for r in csv.DictReader(open(ROOT / "experiments" / "microcorpus" / "expected.csv", encoding="utf-8"))}
    mat = list(csv.DictReader(open(PROC / "microcorpus_matrix.csv", encoding="utf-8")))
    tools = [c for c in mat[0] if c not in ("case_id", "lang", "function", "rules", "expected", "ambiguous", "readings", "found_unit")]
    conf = []; dev_conf = collections.defaultdict(set); dev_amb = collections.defaultdict(set); amb_rows = []
    dev_ref = collections.defaultdict(set)  # (lang) -> targets where the reference fails an unambiguous case
    for lang in LANGS:
        for t in tools:
            rows = [r for r in mat if r["lang"] == lang and r[t] != ""]
            if not rows:
                continue
            un = [r for r in rows if r["ambiguous"] == "0"]
            ok = [r for r in un if int(r[t]) == int(r["expected"])]
            bad = [r for r in un if int(r[t]) != int(r["expected"])]
            targets_failed = collections.Counter()
            fam_failed = collections.defaultdict(collections.Counter)  # family -> Counter of failed dedicated sub-targets
            for r in bad:
                tg = exp[r["case_id"]]["target"]; fam_failed[_family(tg)][tg] += 1
            for r in bad:
                tg = exp[r["case_id"]]["target"]
                own = fam_failed[_family(tg)][tg] - 1  # other failed cases with the same dedicated target
                if own <= 0 and sum(fam_failed[_family(tg)].values()) - 1 <= 0:
                    # no other failure in the target's family: does the tool fail a dedicated case of another rule the case exercises?
                    for rule in exp[r["case_id"]]["rules"].split(";"):
                        fr = _family(rule.strip())
                        if fr != _family(tg) and fam_failed.get(fr):
                            tg = fam_failed[fr].most_common(1)[0][0]; break
                targets_failed[tg] += 1; dev_conf[(lang, t)].add(tg)
            for r in rows:
                if r["ambiguous"] == "1" and r["sonarqube"] != "" and int(r[t]) != int(r["sonarqube"]):
                    dev_amb[(lang, t)].add(exp[r["case_id"]]["target"])
            n_all = len([r for r in mat if r["lang"] == lang and r["ambiguous"] == "0"])
            conf.append({"lang": lang, "tool": t, "n_unambiguous": n_all, "n_reported": len(un), "n_conform": len(ok), "conformance": len(ok) / n_all if n_all else float("nan"),
                         "n_mismatch": len(bad), "n_missing": n_all - len(un), "failed_cases": ";".join(f"{r['case_id']}:{r[t]}/{r['expected']}" for r in bad),
                         "failed_targets": ";".join(f"{k}:{v}" for k, v in targets_failed.most_common()),
                         "ambiguous_differs_from_ref": ";".join(sorted(dev_amb[(lang, t)]))})
        dev_ref[lang] = set(dev_conf.get((lang, "sonarqube"), set()))  # the reference's failures attributed with the same rule as every tool
        dev_ref[lang] = set(dev_conf.get((lang, "sonarqube"), set()))  # the reference's failures attributed with the same rule as every tool
        for r in mat:
            if r["lang"] == lang and r["ambiguous"] == "1":
                amb_rows.append({"case_id": r["case_id"], "lang": lang, "target": exp[r["case_id"]]["target"], "readings": r["readings"],
                                 **{t: r[t] for t in tools if any(x[t] != "" for x in mat if x["lang"] == lang)}})
    return conf, (dev_conf, dev_amb, dev_ref), amb_rows, tools

def attribution(pop, tool, dev_conf, dev_amb, dev_ref, lang):
    rows = [r for r in pop if r.get(REF, "") != "" and r.get(tool, "") != ""]
    dis = [r for r in rows if int(r[REF]) != int(r[tool])]
    agree = [r for r in rows if int(r[REF]) == int(r[tool])]
    # reference deviations count only where the tool itself conforms on that target
    ref_only = {k for k in dev_ref if k not in dev_conf}
    pc = [PRED[k] for k in dev_conf if k in PRED]; pr = [PRED[k] for k in ref_only if k in PRED]; pa = [PRED[k] for k in dev_amb if k in PRED]
    def make_cls(conf_targets):
        pc_ = [(k, PRED[k]) for k in sorted(conf_targets) if k in PRED]
        ref_only_ = {k for k in dev_ref if k not in conf_targets}
        pr_ = [(k, PRED[k]) for k in sorted(ref_only_) if k in PRED]; pa_ = [(k, PRED[k]) for k in sorted(dev_amb) if k in PRED]
        def cls(r):
            f = json.loads(r["features"]); ops = json.loads(r["logical_ops"])
            rec = {"direct": r["recursion_direct"] == "1", "calls": int(r.get("recursion_calls") or 0), "method": r.get("recursion_method") == "1", "kind": r.get("kind")}
            for cat, preds in (("tool", pc_), ("reference", pr_), ("ambiguity", pa_)):
                for k, p in preds:
                    if p(f, ops, rec):
                        return cat, k
            return "unexplained", ""
        return cls
    cls = make_cls(set(dev_conf))
    labelled = [cls(r) for r in dis]
    c = collections.Counter(cat for cat, _ in labelled)
    firing = collections.Counter((cat, k) for cat, k in labelled)
    base = collections.Counter(cls(r)[0] for r in agree)
    n = len(dis)
    out = {"tool": tool.replace("cog__", ""), "tool_targets": ";".join(sorted(dev_conf)), "reference_targets": ";".join(sorted(ref_only)), "ambiguity_targets": ";".join(sorted(dev_amb)),
            "n_pairs": len(rows), "n_disagree": n, "n_tool": c["tool"], "n_reference": c["reference"], "n_ambiguity": c["ambiguity"], "n_unexplained": c["unexplained"],
            "share_tool": c["tool"] / n if n else float("nan"), "share_reference": c["reference"] / n if n else float("nan"),
            "share_ambiguity": c["ambiguity"] / n if n else float("nan"), "share_unexplained": c["unexplained"] / n if n else float("nan"),
            "base_rate_flagged_among_agreeing": (base["tool"] + base["reference"] + base["ambiguity"]) / len(agree) if agree else float("nan"),
            "first_firing": ";".join(f"{cat}:{k}:{v}" for (cat, k), v in firing.most_common())}
    if "B1.8d2" in dev_conf:  # sensitivity to the post-hoc two-call-site recursion target
        cls2 = make_cls(set(dev_conf) - {"B1.8d2"}); c2 = collections.Counter(cls2(r)[0] for r in dis)
        out["share_tool_wo_b18d2"] = c2["tool"] / n if n else float("nan"); out["share_reference_wo_b18d2"] = c2["reference"] / n if n else float("nan")
    else:
        out["share_tool_wo_b18d2"] = out["share_tool"]; out["share_reference_wo_b18d2"] = out["share_reference"]
    out["_cls"] = cls
    return out

AUDIT_VS_CLS = []

def main():
    data = load_functions()
    conf, (dev_conf, dev_amb, dev_ref), amb_rows, mc_tools = microcorpus_deviations()
    with open(PROC / "conformance_summary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(conf[0].keys())); w.writeheader(); w.writerows(conf)
    with open(PROC / "ambiguity_readings.csv", "w", newline="", encoding="utf-8") as fh:
        keys = ["case_id", "lang", "target", "readings"] + mc_tools
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(amb_rows)
    summary = {"conformance": conf, "ambiguity": amb_rows, "langs": {}}
    for lang in LANGS:
        rows = data.get(lang, [])
        if not rows:
            continue
        pop = primary_pop(rows, lang)
        allcols = set().union(*(r.keys() for r in rows))
        tools = sorted(c for c in allcols if c.startswith("cog__") and c != REF)
        cyc_tools = sorted(c for c in allcols if c.startswith("cyc__") and c != REF_CYC)
        # coverage
        cov = []
        for t in [REF] + tools + [REF_CYC] + cyc_tools:
            cov.append({"tool": t, "units_all": len(rows), "primary_pop": len(pop), "primary_with_value": sum(r.get(t, "") != "" for r in pop),
                        "primary_missing": sum(r.get(t, "") == "" for r in pop), "root_with_nested": sum(r["depth"] == "0" and r["has_nested"] == "1" for r in rows),
                        "nested_units": sum(r["depth"] != "0" for r in rows)})
        with open(PROC / f"coverage_{lang}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(cov[0].keys())); w.writeheader(); w.writerows(cov)
        agr, flips, attr, cont, cyc = [], [], [], [], []
        cls_by_tool = {}
        ref_missing_files = collections.Counter(r["file"].split("/")[0] for r in pop if r.get(REF, "") == "")
        for t in tools:
            res = agreement_stats(pop, t)
            if not res:
                continue
            a, pairs, by_repo = res
            a["is_drift_probe"] = t in DRIFT_PROBE
            # test split
            for label, sub in (("nontest", [r for r in pop if r["is_test_path"] == "0"]), ("test", [r for r in pop if r["is_test_path"] == "1"])):
                rs = agreement_stats(sub, t)
                a[f"exact_{label}"] = rs[0]["exact"] if rs else float("nan"); a[f"n_{label}"] = rs[0]["n"] if rs else 0
            agr.append(a)
            flips += flip_stats(pairs, by_repo, t)
            key = (lang, t.replace("cog__", ""))
            a_ = attribution(pop, t, dev_conf.get(key, set()), dev_amb.get(key, set()), dev_ref.get(lang, set()), lang)
            cls_by_tool[t] = a_.pop("_cls"); attr.append(a_)
            # container secondary
            cpop = [r for r in rows if r["depth"] == "0" and r["has_nested"] == "1" and r["kind"] in PRIMARY_KINDS[lang]]
            rc = agreement_stats(cpop, t)
            if rc:
                cont.append({"tool": t.replace("cog__", ""), "n": rc[0]["n"], "exact": rc[0]["exact"], "within1": rc[0]["within1"], "mad": rc[0]["mad"], "share_tool_higher": rc[0]["share_tool_higher"], "share_tool_lower": rc[0]["share_tool_lower"]})
        # sensitivity: common subset (functions valued by every independent tool, drift probe excluded)
        ind = [t for t in tools if t not in DRIFT_PROBE]
        common = [r for r in pop if all(r.get(t, "") != "" for t in ind) and r.get(REF, "") != ""]
        common_stats = []
        for t in ind:
            rs = agreement_stats(common, t)
            if rs:
                common_stats.append({"tool": t.replace("cog__", ""), "n_common": rs[0]["n"], "exact_common": rs[0]["exact"], "mad_common": rs[0]["mad"]})
        if common_stats:
            with open(PROC / f"agreement_common_{lang}.csv", "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(common_stats[0].keys())); w.writeheader(); w.writerows(common_stats)
        for t in cyc_tools:
            rs = agreement_stats(pop, t, ref=REF_CYC)
            if rs:
                d = rs[0]; d["tool"] = t.replace("cyc__", ""); cyc.append(d)
        for name, lst in (("agreement", agr), ("flips", flips), ("attribution", attr), ("container", cont), ("cyclomatic", cyc)):
            if lst:
                with open(PROC / f"{name}_{lang}.csv", "w", newline="", encoding="utf-8") as fh:
                    w = csv.DictWriter(fh, fieldnames=list(lst[0].keys())); w.writeheader(); w.writerows(lst)
        # distribution of reference values (for context)
        refvals = [int(r[REF]) for r in pop if r.get(REF, "") != ""]
        # share of the reference losses that are test paths (SonarQube's path heuristic), first-firing predicates, audit vs classifier
        ref_missing = [r for r in pop if r.get(REF, "") == ""]
        ref_missing_test_share = (sum(r["is_test_path"] == "1" for r in ref_missing) / len(ref_missing)) if ref_missing else None
        test_share_primary = sum(r["is_test_path"] == "1" for r in pop if r.get(REF, "") != "") / max(1, len(refvals))
        with open(PROC / f"attribution_predicates_{lang}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(["tool", "category", "target", "n_disagreements"])
            for a in attr:
                for item in a.get("first_firing", "").split(";"):
                    if item:
                        cat, k, v = item.split(":"); w.writerow([a["tool"], cat, k, v])
        avc = []
        vp = PROC / "audit_verdicts.csv"; ap = PROC / f"audit_{lang}.csv"
        if vp.exists() and ap.exists():
            verdicts = {r["audit_id"]: r for r in csv.DictReader(open(vp, encoding="utf-8"))}
            index = {(r["repo"], r["file"], str(r["decl_line"])): r for r in pop}
            for ar in csv.DictReader(open(ap, encoding="utf-8")):
                v = verdicts.get(ar["audit_id"]); fr = index.get((ar["repo"], ar["file"], str(ar["decl_line"])))
                t_ = "cog__" + ar["tool"]
                if v is None or fr is None or t_ not in cls_by_tool:
                    continue
                cat, k = cls_by_tool[t_](fr)
                avc.append({"audit_id": ar["audit_id"], "lang": lang, "tool": ar["tool"], "audit_category": v["mechanism_category"], "audit_targets": v.get("target_rules", ""),
                            "classifier_category": cat, "classifier_target": k, "agree": int(cat == v["mechanism_category"] or (v["mechanism_category"] == "mixed" and cat in ("tool", "reference", "ambiguity")))})
        AUDIT_VS_CLS.extend(avc)
        summary["langs"][lang] = {"n_units": len(rows), "n_primary": len(pop), "n_primary_ref": len(refvals), "n_repos": len({r["repo"] for r in rows}),
                                  "ref_missing_test_share": ref_missing_test_share, "test_share_primary": test_share_primary,
                                  "audit_vs_classifier": {"n": len(avc), "agree": sum(a["agree"] for a in avc)},
                                  "ref_mean": statistics.mean(refvals) if refvals else None, "ref_median": statistics.median(refvals) if refvals else None,
                                  "ref_share_gt15": sum(v > 15 for v in refvals) / len(refvals) if refvals else None,
                                  "ref_share_zero": sum(v == 0 for v in refvals) / len(refvals) if refvals else None,
                                  "ref_missing_by_topdir": dict(ref_missing_files.most_common(8)),
                                  "agreement": agr, "flips": flips, "attribution": attr, "container": cont, "cyclomatic": cyc, "coverage": cov, "agreement_common": common_stats}
        print(f"== {lang}: units={len(rows)} primary={len(pop)} with_ref={len(refvals)} repos={summary['langs'][lang]['n_repos']}")
        for a in agr:
            print(f"   {a['tool']:<30} n={a['n']:6d} exact={a['exact']:.3f} [{a['exact_ci_lo']:.3f},{a['exact_ci_hi']:.3f}] within1={a['within1']:.3f} MAD={a['mad']:.3f} rho={a['spearman']:.3f} hi={a['share_tool_higher']:.3f} lo={a['share_tool_lower']:.3f}")
        for f in flips:
            if f["threshold"] == 15:
                print(f"   flip15 {f['tool']:<30} rate={f['flip_rate']:.4f} [{f['flip_ci_lo']:.4f},{f['flip_ci_hi']:.4f}] near={f['flip_rate_near']:.3f} (n_near={f['n_near']}) P={f['precision']:.3f} R={f['recall']:.3f}")
        for at in attr:
            print(f"   attr   {at['tool']:<30} disagree={at['n_disagree']} tool={at['share_tool']:.3f} ref={at['share_reference']:.3f} amb={at['share_ambiguity']:.3f} unexpl={at['share_unexplained']:.3f} base={at['base_rate_flagged_among_agreeing']:.3f} T={at['tool_targets']} R={at['reference_targets']} A={at['ambiguity_targets']}")
    if AUDIT_VS_CLS:
        with open(PROC / "audit_vs_classifier.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(AUDIT_VS_CLS[0].keys())); w.writeheader(); w.writerows(AUDIT_VS_CLS)
    (PROC / "summary.json").write_text(json.dumps(summary, indent=1, default=float), encoding="utf-8")

if __name__ == "__main__":
    main()
