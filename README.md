# One Specification, Many Numbers — replication package

Replication package for the paper *One Specification, Many Numbers: Conformance of Cognitive
Complexity Implementations Across Four Languages* (Rafig Huseynzade, 2026).

Cognitive Complexity is defined by a prose white paper rather than a formula, yet it gates merges in
CI at a default threshold of 15. The study checks whether independent implementations of that one
specification compute the same number for the same function: it compares 11 open-source
implementations (15 implementation–language pairs) with SonarQube's own analyzers for Python, Java,
JavaScript/TypeScript and Go, on a micro-corpus of 270 minimal functions with expected values derived
from the white paper (236 unambiguous, 34 labelled ambiguous) and on 138,393 leaf root functions from
32 popular repositories pinned to commit SHAs. It reports which written rules each implementation, and
the reference itself, violates; how often the tools disagree on real code; how often the gate decision
at 15 depends on the tool; and how much of the disagreement is associated with the rule-level
deviations found on the micro-corpus.

## How to cite

The paper (to appear):

> Rafig Huseynzade. "One Specification, Many Numbers: Conformance of Cognitive Complexity
> Implementations Across Four Languages." In *2nd Republican Conference "Actual Scientific-Practical
> Problems of Software Engineering"*, Institute of Information Technology, Ministry of Science and
> Education of Azerbaijan, Baku, 25 November 2026. To appear.

This package: Rafig Huseynzade, *Replication package: One Specification, Many Numbers*, version 1.0.0,
2026, <https://github.com/pneqnp-iswr/cognitive-complexity-conformance>. Machine-readable metadata is
in [`CITATION.cff`](CITATION.cff).

## Repository map

| Path | Contents |
| --- | --- |
| `RESEARCH_CONTRACT.md` | Study protocol fixed in advance (2026-09-17): research questions, hypotheses, metrics, decision rules |
| `EXPERIMENT_PROTOCOL.md` | Frozen experimental protocol: tools and invocations, corpora, unit of analysis, alignment rule |
| `experiments/microcorpus/` | The 270 micro-corpus cases (`python/`, `java/`, `javascript/`, `go/`), `expected.csv` (expected value, ambiguity label, readings, target rule and derivation note per case) and `ATTRIBUTION.md` (cases derived from the white paper's worked examples) |
| `experiments/` (other) | Tool configuration (`pmd-cc.xml`, `sandbox/.oxlintrc.json`) and small probe inputs |
| `data/repos/` | `manifest.csv` (the 32 repositories with pinned SHAs and licences), per-language selection snapshots, `LICENSES.md` |
| `results/processed/functions/` | 32 per-function tables, one per repository: one row per function-like unit, one column per tool and metric. **The input of the statistical analysis.** |
| `results/processed/` | Micro-corpus matrix and conformance, agreement, gate flips, attribution, cyclomatic baseline, coverage, container functions, the audit sample performed by an AI agent (`audit_<lang>.csv`, `audit_verdicts.csv`; see Limitations) and `summary.json` |
| `results/raw/` | Raw tool output on the micro-corpus (`microcorpus/`) and the SonarScanner log of each repository |
| `tables/`, `figures/` | Tables (`tables.md`, `tables.json`) and the three figures, all generated from `results/processed/` |
| `src/ccstudy/` | Measurement library: tree-sitter function enumeration (`functions.py`), alignment of tool rows to functions (`align.py`), tool adapters (`tools.py`); `src/*.mjs` are the Node adapters |
| `scripts/` | `reproduce_analysis.sh`, the analysis (`analyze.py`, `update_coverage_causes.py`, `make_tables.py`, `make_figures.py`) and the measurement harness (`select_repos.py`, `run_all_repos.py`, `run_realcode.py`, `run_microcorpus.py`, `sonar_*.py`, `build_function_table.py`, …) |
| `reproduction/` | Full re-run procedure (`README.md`), pinned Python and Node dependencies, SonarQube image digest, captured environment |
| `references/` | `spec/cognitive_complexity_spec_rules.md`, the study's rule digest of the white paper (paraphrase with short attributed quotations), and `references.json`, the bibliography |
| `ARTIFACT_MANIFEST.json` | Size and SHA-256 of every file in this release |

## Quick start: reproduce the statistics, tables and figures

No metric tool, SonarQube server, JDK, Go or Node toolchain is needed. With Python 3.11 (the version
used in the study):

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r reproduction/requirements-analysis.txt
PY=.venv/bin/python scripts/reproduce_analysis.sh
```

The script runs `analyze.py` (all RQ1–RQ4 statistics, with a cluster bootstrap over repositories,
2,000 resamples, seed 20260917), `update_coverage_causes.py`, `make_tables.py` and `make_figures.py`
on the shipped per-function tables, overwriting `results/processed/*`, `tables/` and `figures/` in
place. It takes about 10–15 minutes. At the end it compares the regenerated files with
`ARTIFACT_MANIFEST.json`; `git status` shows the same. On Windows, run it from Git Bash or WSL
(`PY=.venv/Scripts/python`), or run those four Python scripts in that order.

Expected outcome: all regenerated CSV and JSON files and both table files are byte-identical to the
release. The PNG figures show the same data, but their bytes depend on the installed fonts (the
figures use Times New Roman when it is available) and the matplotlib build. Among the numbers you
should see: 138,393 leaf root functions with a reference value; exact agreement with the reference
between 74.4% (cognitive-complexity-ts) and 99.8% (codemetrics on Python); a gate-flip rate at 15 of
up to 18.5% among functions with a reference value in [10, 20] (cognitive-complexity-ts); and
reference conformance on the unambiguous micro-corpus cases of 50/56 (Python), 57/62 (Java),
43/65 (JS/TS) and 43/53 (Go).

## Re-running the measurements from scratch

[`reproduction/README.md`](reproduction/README.md) is the full procedure as used in the study. In
short:

1. **Subject code.** Clone each of the 32 repositories at the SHA pinned in `data/repos/manifest.csv`
   into `data/raw_repos/<owner>__<repo>` (`git clone --depth 1`, then
   `git fetch --depth 1 origin <sha> && git checkout <sha>`).
2. **Reference.** Run SonarQube Community Build 26.9.0.129388 from the image pinned by digest
   (`sonarqube@sha256:58b068af30bdfdccf91222de36e310529033e853dfae221b429cba80d10d5751`, also in
   `reproduction/sonarqube_image_digest.txt`) with SonarScanner CLI 8.1.0.6389, and create the
   study's quality profiles (S3776 and the cyclomatic rule at threshold 0) with `scripts/sonar_setup.py`.
3. **Implementations.** Install the pinned versions: Python tools from
   `reproduction/requirements-tools_venv.txt`, Node tools from `reproduction/tools_node_package.json`
   and its lock file, plus PMD 7.27.0, cognitive-java 0.7.1, gocognit 1.2.1 (Go 1.27.1),
   rust-code-analysis 0.0.25 and codemetrics 0.12.7. The versions are also recorded in
   `src/ccstudy/tools.py` (`TOOL_VERSIONS`).
4. **Runs.** Micro-corpus: `scripts/sonar_scan.py` per language, then `scripts/run_microcorpus.py`.
   Real code: `scripts/run_all_repos.py`, which writes the raw outputs to `results/raw/` and the
   per-function tables to `results/processed/functions/`. Then `scripts/reproduce_analysis.sh`.

The harness was written for and run on Windows 11: tool locations in `src/ccstudy/tools.py` and
`scripts/sonar_scan.py` point to Windows executables (`.exe`, `.bat`) and JDK install paths, and the
`clone_dir` column of the manifest uses Windows separators. On other systems, adjust those paths first.

## What is not included, and why

- **Raw tool outputs for the 32 repositories** (`units.json`, `run_meta.json`, `sonar.json`,
  `sonar_files.json` and one JSON per tool, per repository). They are missing from the study's export
  that this release was built from, which holds only the SonarScanner logs. Without them the
  per-function tables cannot be rebuilt from raw output (`scripts/build_function_table.py`), but the
  tables themselves are included in `results/processed/functions/` and suffice for every statistic.
  The raw outputs will be added in a later release if they are recovered.
- **The cloned subject repositories.** They are third-party code under their own licences; re-obtain
  them at the pinned SHAs. No source code from them is included.
- **The SonarSource white paper** (*Cognitive Complexity: a new way of measuring understandability*,
  v1.7, 29 August 2023), which is copyright SonarSource. Download it from
  <https://www.sonarsource.com/docs/CognitiveComplexity.pdf>; its SHA-256 is recorded in section 0 of
  `references/spec/cognitive_complexity_spec_rules.md`.
- **Tool binaries, virtual environments and `node_modules`.** Install them from their own sources at
  the pinned versions.
- **The paper text** and the scripts that built it, until the conference proceedings appear.

`RESEARCH_CONTRACT.md` and `EXPERIMENT_PROTOCOL.md` are included unchanged; they mention a research
log, a result manifest and the manuscript, which are not part of this release.
`experiments/microcorpus/ATTRIBUTION.md` likewise cites study notes and a probe file
(`experiments/ccts_probe/a1.ts`) that are not included.

## Limitations

- **A single source of expected values.** The micro-corpus expected values and ambiguity labels were
  derived once from the white paper, by the AI agents described below, and were not verified by a
  human expert or a second independent labeller. The same holds for the audit of 120 sampled
  real-code disagreements (`results/processed/audit_*.csv`).
- **SonarQube is a comparator, not ground truth.** Real-code agreement is measured against SonarQube's
  analyzers, which themselves fail some unambiguous micro-corpus cases. A disagreement means the tools
  differ, not that the other implementation is wrong.
- **Pinned versions.** All results hold for the tool versions and repository snapshots recorded here;
  any of them may change.
- **Attribution is diagnostic.** Assigning real-code disagreements to rule-level deviations relies on
  construct-presence predicates; it shows association, not cause.

## AI-use statement

Generative AI agents based on OpenAI ChatGPT were used extensively in this study: to select the topic and design the study, to write the micro-corpus and derive its expected values, to implement and run the measurement and analysis code, to audit a sample of 120 disagreements, and to draft the paper. The micro-corpus labels and the audit were not verified by a human expert. The author initiated the work and takes responsibility for the published content.

## License

Three regimes apply, by path; [`LICENSE`](LICENSE) is authoritative and
[`THIRD_PARTY_NOTICE.md`](THIRD_PARTY_NOTICE.md) lists every third-party item.

- **MIT**: the author's code (`src/`, `scripts/`, tool configuration and probe inputs under
  `experiments/`, and the micro-corpus sources except the cases derived from the white paper's
  examples).
- **CC BY 4.0**: the author's data, results, figures, tables and documentation (`data/`, `results/`,
  `figures/`, `tables/`, `experiments/microcorpus/expected.csv`, `reproduction/`, and the documents at
  the repository root).
- **Third-party material**, covered by neither grant: the short quotations from the white paper in the
  rule digest, the micro-corpus cases derived from its worked examples, analyzer messages emitted by
  SonarSource software, dependency metadata, and anything belonging to the measured repositories
  (whose file paths and function names appear in the data). See `THIRD_PARTY_NOTICE.md`.

Contact: Rafig Huseynzade, Independent Researcher, Baku, Azerbaijan — huseynzaderafig@gmail.com
