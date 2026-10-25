"""Generate manuscript figures from processed CSVs only (no manual numbers).
figures/fig_conformance_heatmap.png   RQ1: per-language conformance matrix (target rule x tool): pass / fail / not applicable
figures/fig_flip_rates.png            RQ3: gate-flip rate vs threshold per tool, one panel per language
figures/fig_diff_distribution.png     RQ2: distribution of (tool - reference) per tool per language
"""
import csv, json, pathlib, sys, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import figstyle; figstyle.apply()
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC = ROOT / "results" / "processed"; FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)
LANGS = ["python", "java", "javascript", "go"]
LANG_LABEL = {"python": "Python", "java": "Java", "javascript": "JS/TS", "go": "Go"}
SHORT = {"sonarqube": "SonarQube (ref.)", "eslint-plugin-sonarjs-4.2.1": "sonarjs 4.2.1 (snapshot)", "pmd": "PMD"}  # every other tool is labelled by its full name

def conformance_heatmap():
    exp = list(csv.DictReader(open(ROOT / "experiments" / "microcorpus" / "expected.csv", encoding="utf-8")))
    mat = {r["case_id"]: r for r in csv.DictReader(open(PROC / "microcorpus_matrix.csv", encoding="utf-8"))}
    tools_all = [c for c in next(iter(mat.values())) if c not in ("case_id", "lang", "function", "rules", "expected", "ambiguous", "readings", "found_unit")]
    targets = ["B1.1", "R2", "B2.1", "B3.1", "B3.1t", "B3", "B1.2", "B1.3", "B1.3a", "B1.4", "B1.5", "R7", "B1.7and", "B1.7or", "B1.7mix", "B1.7idiom", "R15", "B1.6", "R14",
               "B1.8d", "B1.8d2", "B1.8i", "B1.8m", "B2.6", "A.2", "A.3", "R11", "R13", "ARROW", "GO-ERRNIL", "C"]
    present = {e["target"] for e in exp if e["ambiguous"] == "0"}
    missing = present - set(targets)
    assert not missing, f"heatmap target list lacks {missing}"
    conf = {(r["lang"], r["tool"]): r for r in csv.DictReader(open(PROC / "conformance_summary.csv", encoding="utf-8"))}
    fig, axes = plt.subplots(1, 4, figsize=(7.1, 4.0), gridspec_kw={"width_ratios": [5, 4, 8, 3]})
    cmap = {0: "#ffffff", 1: "#2c7bb6", 2: "#d7191c", 3: "#f4a582", 4: "#bdbdbd"}  # 0 n/a, 1 all conform, 2 all deviate, 3 some deviate, 4 not reported
    for ax, lang in zip(axes, LANGS):
        tools = [t for t in tools_all if any(mat[e["case_id"]][t] != "" for e in exp if e["lang"] == lang)]
        tools = ["sonarqube"] + [t for t in tools if t != "sonarqube"]
        grid = np.zeros((len(targets), len(tools)))
        for i, tg in enumerate(targets):
            cases = [e for e in exp if e["lang"] == lang and e["target"] == tg and e["ambiguous"] == "0"]
            for j, t in enumerate(tools):
                if not cases:
                    grid[i, j] = 0; continue
                reported = [e for e in cases if mat[e["case_id"]][t] != ""]
                # failures as attributed in Table III (a failed case is booked to the rule the tool demonstrably fails elsewhere)
                failed = dict(x.split(":") for x in conf[(lang, t)]["failed_targets"].split(";") if x) if (lang, t) in conf else {}
                fails = int(failed.get(tg, 0))
                if not reported:
                    grid[i, j] = 4; continue
                grid[i, j] = 1 if fails == 0 else (2 if fails >= len(cases) else 3)
        img = np.zeros(grid.shape + (3,))
        for k, col in cmap.items():
            img[grid == k] = [int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        ax.imshow(img, aspect="auto")
        ax.set_xticks(range(len(tools))); ax.set_xticklabels([SHORT.get(t, t) for t in tools], rotation=90, fontsize=6)
        ax.set_yticks(range(len(targets))); ax.set_yticklabels(targets if lang == "python" else [""] * len(targets), fontsize=6)
        ax.set_title(LANG_LABEL[lang], fontsize=8); ax.grid(False)
        for s in ax.spines.values(): s.set_visible(True); s.set_linewidth(0.4)
    fig.text(0.01, 0.5, "Target rule (Appendix B / body text)", rotation=90, va="center", fontsize=7)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=cmap[1], label="all cases conform"), Patch(color=cmap[3], label="some cases deviate"), Patch(color=cmap[2], label="all cases deviate"), Patch(color=cmap[4], label="cases not reported"), Patch(facecolor="white", edgecolor="gray", label="no unambiguous case")],
               loc="lower center", ncol=5, fontsize=6, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0.03, 0.06, 1, 1)); fig.savefig(FIG / "fig_conformance_heatmap.png"); plt.close(fig)

def flip_rates():
    fig, axes = plt.subplots(1, 4, figsize=(7.1, 3.0), sharey=True)
    for ax, lang in zip(axes, LANGS):
        p = PROC / f"flips_{lang}.csv"
        if not p.exists():
            ax.set_visible(False); continue
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        tools = sorted({r["tool"] for r in rows})
        for t in tools:
            xs = [int(r["threshold"]) for r in rows if r["tool"] == t]; ys = [100 * float(r["flip_rate_near"]) for r in rows if r["tool"] == t]
            ax.plot(xs, ys, marker="o", label=SHORT.get(t, t), linestyle="--" if t == "eslint-plugin-sonarjs-4.2.1" else "-")
        ax.set_title(LANG_LABEL[lang]); ax.set_xticks([10, 15, 20, 25]); ax.set_xlabel("gate threshold t")
        if lang == "python": ax.set_ylabel("flip rate, ref. in [t-5, t+5] (%)")
        ax.legend(fontsize=5, loc="best", ncol=1, handlelength=1.1, labelspacing=0.2, borderpad=0.2)
    ymax = max(max(l.get_ydata()) for ax in axes for l in ax.get_lines())
    for ax in axes:
        ax.set_ylim(0, ymax * 1.12)  # tight common scale: preserve data readability without excessive unused y-range
    fig.tight_layout(); fig.savefig(FIG / "fig_flip_rates.png"); plt.close(fig)

def diff_distribution():
    fig, axes = plt.subplots(1, 4, figsize=(7.1, 2.6))
    for ax, lang in zip(axes, LANGS):
        files = sorted((PROC / "functions").glob(f"{lang}__*.csv"))
        if not files:
            ax.set_visible(False); continue
        rows = []
        for f in files:
            rows += [r for r in csv.DictReader(open(f, encoding="utf-8")) if r["depth"] == "0" and r["has_nested"] == "0" and r.get("has_body", "1") != "0" and r["cog__sonarqube"] != ""]
        tools = sorted(set().union(*(r.keys() for r in rows)) - {"cog__sonarqube"}); tools = [c for c in tools if c.startswith("cog__")]
        data, labels = [], []
        for t in tools:
            d = [int(r[t]) - int(r["cog__sonarqube"]) for r in rows if r.get(t, "") != ""]
            if d:
                data.append(np.clip(d, -6, 6)); labels.append(SHORT.get(t.replace("cog__", ""), t.replace("cog__", "")))
        # stacked bars of the share in buckets: <-1, -1, 0, +1, >+1
        buckets = [(-99, -2, "≤−2"), (-1, -1, "−1"), (0, 0, "0"), (1, 1, "+1"), (2, 99, "≥+2")]
        cols = ["#b2182b", "#ef8a62", "#f0f0f0", "#67a9cf", "#2166ac"]
        bottom = np.zeros(len(data))
        for (lo, hi, lab), col in zip(buckets, cols):
            share = np.array([100 * np.mean((d >= lo) & (d <= hi)) for d in data])
            ax.bar(range(len(data)), share, bottom=bottom, color=col, label=lab, width=0.7, edgecolor="none")
            bottom += share
        ax.set_xticks(range(len(data))); ax.set_xticklabels(labels, rotation=90, fontsize=6); ax.set_title(LANG_LABEL[lang]); ax.set_ylim(0, 100)
        if lang == "python": ax.set_ylabel("share of functions (%)")
    handles, labels_ = axes[0].get_legend_handles_labels()
    fig.legend(handles, ["implementation − reference: " + labels_[0]] + labels_[1:], loc="lower center", ncol=5, fontsize=6, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(FIG / "fig_diff_distribution.png"); plt.close(fig)

if __name__ == "__main__":
    conformance_heatmap(); flip_rates(); diff_distribution(); print("figures written to", FIG)
