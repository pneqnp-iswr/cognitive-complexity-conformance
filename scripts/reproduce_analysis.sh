#!/usr/bin/env bash
# Recompute every statistic, table and figure of the study from the shipped per-function tables
# (results/processed/functions/*.csv), the micro-corpus matrix (results/processed/microcorpus_matrix.csv),
# the expected values (experiments/microcorpus/expected.csv) and the audit verdicts
# (results/processed/audit_*.csv). No metric tool, SonarQube server, JDK, Go or Node toolchain is needed.
#
# Outputs are written in place, over the shipped files:
#   results/processed/{conformance_summary,ambiguity_readings,agreement_*,agreement_common_*,flips_*,
#                      attribution_*,attribution_predicates_*,cyclomatic_*,coverage_*,container_*,
#                      audit_vs_classifier,coverage_causes}.csv and results/processed/summary.json
#   tables/tables.json, tables/tables.md
#   figures/fig_conformance_heatmap.png, figures/fig_flip_rates.png, figures/fig_diff_distribution.png
# The last step compares the regenerated files with the SHA-256 digests in ARTIFACT_MANIFEST.json.
# In a git checkout, `git status` / `git diff` afterwards shows the same thing.
#
# Usage:  scripts/reproduce_analysis.sh          (uses python3)
#         PY=/path/to/python scripts/reproduce_analysis.sh
# Requires the packages in reproduction/requirements-analysis.txt (the study used Python 3.11).
# Runtime: about 10-15 minutes, almost all of it the cluster bootstrap in scripts/analyze.py.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-python3}
export PYTHONIOENCODING=utf-8
export PYTHONDONTWRITEBYTECODE=1

log() { echo "[$(date +%H:%M:%S)] $*"; }

for f in results/processed/microcorpus_matrix.csv experiments/microcorpus/expected.csv; do
  [ -f "$f" ] || { echo "missing input: $f" >&2; exit 1; }
done
n_tables=$(ls results/processed/functions/*.csv 2>/dev/null | wc -l)
[ "$n_tables" -gt 0 ] || { echo "missing input: results/processed/functions/*.csv" >&2; exit 1; }
log "inputs: $n_tables per-repository function tables"

log "1/4 analyze: RQ1-RQ4 statistics, cluster bootstrap (2,000 resamples, seed 20260917)"
"$PY" scripts/analyze.py
log "2/4 coverage causes: recompute the coverage numbers"
"$PY" scripts/update_coverage_causes.py
log "3/4 tables"
"$PY" scripts/make_tables.py
log "4/4 figures"
"$PY" scripts/make_figures.py

# Python's csv module writes CRLF line endings; the released files use LF. Normalise the regenerated
# text outputs so that they can be compared byte for byte (the content is not changed).
log "normalise line endings of regenerated text outputs to LF; compare with ARTIFACT_MANIFEST.json"
"$PY" - <<'EOF'
import glob, hashlib, json, pathlib
inputs = {"results/processed/microcorpus_matrix.csv", "results/processed/audit_verdicts.csv"} | {
    f"results/processed/audit_{lang}.csv" for lang in ("python", "java", "javascript", "go")}
outputs = sorted(set(glob.glob("results/processed/*.csv")) - inputs
                 | {"results/processed/summary.json", "tables/tables.json", "tables/tables.md"})
for p in map(pathlib.Path, outputs):
    b = p.read_bytes()
    if b"\r\n" in b:
        p.write_bytes(b.replace(b"\r\n", b"\n"))
outputs += sorted(glob.glob("figures/*.png"))
try:
    manifest = {e["path"]: e["sha256"] for e in json.loads(pathlib.Path("ARTIFACT_MANIFEST.json").read_text(encoding="utf-8"))["files"]}
except (OSError, ValueError, KeyError) as e:
    print(f"   ARTIFACT_MANIFEST.json not usable ({e}); skipping the comparison")
    raise SystemExit(0)
same, differ = [], []
for p in outputs:
    (same if manifest.get(p) == hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() else differ).append(p)
print(f"   {len(same)} of {len(outputs)} regenerated files are byte-identical to the release")
for p in differ:
    note = "  (PNG bytes depend on the installed fonts and matplotlib build; compare visually)" if p.endswith(".png") else ""
    print(f"   differs: {p}{note}")
EOF
log "done"
