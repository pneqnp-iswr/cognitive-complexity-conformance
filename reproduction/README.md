# Reproduction package — Cognitive Complexity conformance study

> **Note for this repository (release v1.0.0).** This file is the reproduction procedure as written
> during the study, unchanged apart from this note and the sentence on raw outputs below. Some steps
> name scripts or files that are not part of this repository: the manuscript build and checks
> (`build_manuscript_spec.py`, `build_manuscript.py`, `fix_layout.py`, `manuscript_to_markdown.py`,
> `qa_pdf.py`, `numeric_audit.py`, everything under `paper/`), the revision pipelines
> `pipeline_r1.sh`–`pipeline_r3.sh`, the citation-verification and author-document scripts, the
> exporter `export_public_artifact.py` and its checks, `results/result_manifest.csv`,
> `claim_evidence_matrix.csv` and `logs/`. The git history mentioned in section 2 is that of the
> study's working repository, which is not public. To recompute the statistics, tables and figures,
> run `../scripts/reproduce_analysis.sh` (section 4 without the manuscript steps); see `../README.md`.

This directory documents how to reproduce the manuscript analyses from scratch. All scripts live in
`../scripts` and `../src`; processed tables are in `../results/processed`, figures in `../figures`, and tables in `../tables`.
Per-repository raw outputs are written to `../results/raw/<lang>/<owner>__<repo>/`; of these, this release contains only
the SonarScanner logs (`sonar.scanner.log`). Nothing in
`results/processed`, `figures/` or `tables/` is edited by hand.

## 0. Environment

Captured host: see `environment.md` / `environment.json` (Windows 11, Python 3.11.0, Node 22.16.0, Go 1.27.1 portable,
JDK 17.0.17 for PMD and JDK 21.0.9 for cognitive-java — both recorded under `tool_runtimes` in `environment.json`; the `java`
on PATH at capture time was an unrelated JDK 8 and is not used by the study. Rebuilding `paper/FINAL_SUBMISSION.docx`/`.pdf`
additionally needs Microsoft Word (COM automation via pywin32); no number in the paper depends on it. Python packages:
`requirements-analysis.txt` (minimal, for the analysis and build scripts) and `requirements-tools_venv.txt` (metric tools);
`requirements-freeze.txt` is the full capture of the analysis interpreter,
Docker Desktop 29.6.2). Python packages of the analysis interpreter: `requirements-freeze.txt`. Tool versions are pinned in
`src/ccstudy/tools.py::TOOL_VERSIONS` and in Section 2 of `../EXPERIMENT_PROTOCOL.md`.

Required local tools (installed under `../tools/`, git-ignored; install commands):

| Tool | Version | Install |
|---|---|---|
| Python metric tools (venv `tools_venv`) | complexipy 8.0.1, cognitive_complexity 1.3.0, flake8-cognitive-complexity 0.1.0, radon 6.0.1, lizard 1.24.0 | `py -3.11 -m venv tools_venv && tools_venv\Scripts\pip install complexipy==8.0.1 cognitive_complexity==1.3.0 flake8-cognitive-complexity==0.1.0 radon==6.0.1 lizard==1.24.0` |
| PMD | 7.27.0 | unzip `pmd-dist-7.27.0-bin.zip` (GitHub releases) into `tools/pmd-bin-7.27.0` |
| cognitive-java | 0.7.1 | `tools/cognitive-java-cli-0.7.1.jar` from Maven Central `media.barney:cognitive-java-cli:0.7.1` (sha256 109f915e…) |
| gocognit | 1.2.1 | portable Go 1.27.1 in `tools/go`, `go install github.com/uudashr/gocognit/cmd/gocognit@v1.2.1` with GOPATH=`tools/gopath` |
| rust-code-analysis-cli | 0.0.25 | prebuilt `rust-code-analysis-win-cli-x86_64.zip` (GitHub release v0.0.25) into `tools/rca` |
| codemetrics | 0.12.7 | `codemetrics_0.12.7_windows_amd64.zip` (GitHub release) into `tools/codemetrics` |
| Node packages (`tools/node`) | cognitive-complexity-ts 0.8.2, cogplexity 0.1.0, oxlint-plugin-complexity 3.0.0 (+ oxc-parser), eslint-plugin-maintainability 3.2.10, eslint-plugin-sonarjs 4.2.1, eslint 10.10.0, @typescript-eslint/parser 8.70.0, typescript 6.0.3, oxlint 1.83.0 | `cd tools/node && npm install` (see `tools_node_package.json` copy here) |
| SonarQube Community Build | 26.9.0.129388 (image digest sha256:58b068af30bd…) | `docker run -d --name sonarqube -p 9000:9000 -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube@sha256:58b068af30bdfdccf91222de36e310529033e853dfae221b429cba80d10d5751` |
| sonar-scanner CLI | 8.1.0.6389 windows-x64 | unzip into `tools/sonar-scanner-8.1.0.6389-windows-x64` |

## 1. SonarQube configuration
```
py -3.11 scripts/sonar_setup.py
```
Creates quality profiles `cc-study-{py,java,js,ts,go}` that activate only S3776 (threshold 0) and the cyclomatic rule
(threshold 0), sets them as defaults, and writes an analysis token to `data/sonar_token.txt` (git-ignored).

## 2. Micro-corpus (RQ1)
```
for L in py java js go: py -3.11 scripts/sonar_scan.py micro-$L experiments/microcorpus/<lang> results/raw/microcorpus/sonar_$L.json --lang $L
py -3.11 scripts/add_targets.py          # idempotent: target-rule column in expected.csv
py -3.11 scripts/run_microcorpus.py      # -> results/processed/microcorpus_matrix.csv
```
Expected values (`experiments/microcorpus/expected.csv`) were written before any tool ran on the corpus; the file is
versioned in git, see `git log -- experiments/microcorpus/expected.csv`.

## 3. Real-code corpus (RQ2–RQ4)
```
py -3.11 scripts/select_repos.py python java javascript go     # GitHub search snapshot + shallow clones + LOC filter; writes data/repos/*
py -3.11 scripts/run_all_repos.py                               # per repo: units, all tools, SonarQube scan, raw JSON, function table
py -3.11 scripts/build_function_table.py --all                  # (optional) rebuild processed tables from raw JSON
```
The selection is a dated snapshot of GitHub search results; to reproduce with the *same* repositories use the commit SHAs
in `data/repos/manifest.csv` (`git clone --depth 1` then `git fetch --depth 1 origin <sha> && git checkout <sha>`).

## 4. Analysis, figures, tables, manuscript
```
py -3.11 scripts/analyze.py            # results/processed/{conformance_summary,ambiguity_readings,agreement_*,flips_*,attribution_*,cyclomatic_*,coverage_*,container_*}.csv, summary.json
py -3.11 scripts/audit_sample.py       # results/processed/audit_<lang>.csv (+ snippets) — the audit sample (seed 20260917)
py -3.11 scripts/make_figures.py       # figures/*.png
py -3.11 scripts/make_tables.py        # tables/tables.json, tables/tables.md
py -3.11 scripts/build_manuscript_spec.py   # paper/manuscript.json, paper/values.json, results/result_manifest.csv
py -3.11 scripts/build_manuscript.py paper/manuscript.json paper/FINAL_SUBMISSION.docx   # Word automation -> .docx + .pdf
py -3.11 scripts/qa_pdf.py paper/FINAL_SUBMISSION.pdf paper/qa_render                    # page renders + programmatic checks
```
Randomness: only the cluster bootstrap and the audit sample, both seeded with 20260917.

## 5. Result and claim provenance
`../results/result_manifest.csv` lists the generated manuscript placeholders with their processed source and producing script.
`../claim_evidence_matrix.csv` maps the scientific claims to evidence. `scripts/numeric_audit.py` is a consistency smoke test,
not a proof that every textual occurrence of a number maps uniquely to one raw row.

## 6. Public artifact export
Do **not** publish the working repository verbatim: it may contain local audit PDFs and an old tracked virtual environment.
Run `py -3.11 scripts/export_public_artifact.py`. The exporter includes locally available raw JSON outputs, excludes cloned
subject repositories, tool binaries/venvs, third-party full-text PDFs and credentials, scans for obvious secrets, writes SHA-256
hashes to `ARTIFACT_MANIFEST.json`, and creates `dist/replication-package.zip`.

## 7. Known platform notes
* Windows path-length limits made a few large Java repositories fail to check out; they are recorded as skipped in `data/repos/selection_java.json`.
* SonarPython does not report S3776 for files it classifies as tests; these functions have no reference value and are excluded (coverage tables).
* `eslint-disable` comments in analysed files silence ESLint-based tools and SonarJS; the micro-corpus contains none, real code is analysed as-is.

## 8. Revision after internal review (2026-09-17)

Pinned dependency files added at the reviewers' request: `requirements-tools_venv.txt` (pip freeze of the metric-tool venv)
and `tools_node_package-lock.json` (lock file of the Node tools). The revision pipeline is `../scripts/pipeline_r1.sh`:

1. targeted reruns after the coverage investigation (`results/processed/coverage_causes.{csv,md}`):
   `scripts/rerun_tool.py java ReactiveX/RxJava cognitive_java` (parse-failing files are now skipped one by one instead of
   dropping a 200-file chunk), `... java TheAlgorithms/Java lizard`, `... python Shubhamsaboo/awesome-llm-apps lizard`,
   `... javascript immich-app/immich codemetrics` (a chunk for which codemetrics prints `null` is bisected);
2. `scripts/reenumerate_units.py javascript <repo>` for every JS/TS repository (TypeScript decorators now belong to the
   method header span; ESLint-based threshold tools are zero-filled on every analysed file);
3. `scripts/analyze.py` with the refined attribution targets in `experiments/microcorpus/expected.csv`
   (B1.8d/d2/i/m, B1.7and/or/mix/idiom/bit, B3.1t, ARROW; labels only, expected values unchanged);
4. `scripts/make_tables.py`, `scripts/make_figures.py`, `scripts/fix_layout.py` (two-pass Word layout: builds the
   manuscript, reads `paper/layout_report.json`, moves float anchors recorded in `paper/float_anchors.json`),
   `scripts/manuscript_to_markdown.py`, `scripts/qa_pdf.py`;
5. `scripts/update_coverage_causes.py` (recomputes coverage numbers, keeps the investigated causes),
   `scripts/fill_author_explanation.py` (Russian author notes), `scripts/make_claim_matrix.py`,
   `scripts/make_citation_audit.py`.

Citation verification: `scripts/verify_citations.py` (Crossref/arXiv/OpenAlex), `scripts/verify_citations_extra.py` and
`scripts/verify_citations_extra2.py` (CEUR, DSpace, GitHub/Discourse APIs, arXiv via curl), `scripts/check_source_claims.py`
(downloads open full texts into `references/sources/`, not redistributed, and prints keyword contexts for the claim checks).

### 8.1 Second revision (round 2)
`../scripts/pipeline_r2.sh`: `scripts/sonar_files.py` (scanner file index per repository; Go zero-fill), `scripts/reenumerate_units.py --all`
(new unit features: else/elif for Java and Go, `async_for`, `paren_bool`, receiver-based method recursion), `scripts/analyze.py`
(narrowed predicates, failed-case attribution by the `rules` list, exact agreement on reference > 0, near-window bootstrap CI,
first-firing predicates, audit-vs-classifier table), then tables, figures, build, QA and the author documents.

### 8.2 Final check (round 3)
`../scripts/pipeline_r3.sh` re-runs `scripts/analyze.py` (the reference's failed micro-corpus cases attributed with the same
rule-list logic as the tools'; exact agreement where both values are above 0), the tables and figures (Fig. 1 from the attributed
failures, unreported cases in grey), the build, QA, author documents and the numeric audit.

## 10. What the published package does not contain

`scripts/export_public_artifact.py` builds the public package and deliberately leaves out: the cloned subject repositories
(`data/raw_repos`, pinned in `data/repos/manifest.csv`), tool binaries and virtualenvs (`tools`, `tools_venv`), the SonarSource
white paper and the downloaded full texts of cited works (`references/spec/CognitiveComplexity.pdf`, `references/sources`),
the organiser's template and the scraped announcement pages (`references/official`, except the retrieval timestamp), the
scraped S3776 rule descriptions, the source snippets quoted for the audit (`results/processed/audit_*_snippets.txt`),
the analysis token, the working `logs/` tree (the review and novelty logs cited by the audits are published individually) and
the generated `paper/FINAL_SUBMISSION.docx`/`.pdf` and `paper/qa_render/` (rebuild them with `scripts/fix_layout.py` and
`scripts/qa_pdf.py`). Absolute local paths are stripped from every published text file.

Two caveats for re-running steps that need the subject code: `scripts/audit_sample.py` re-draws the manual-audit sample only
when the repositories are cloned at their pinned SHAs (the shipped `results/processed/audit_<lang>.csv` already carry the
verdicts), and `scripts/rerun_tool.py` likewise needs the clone plus the tool it re-runs.
