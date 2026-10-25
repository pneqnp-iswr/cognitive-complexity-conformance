# EXPERIMENT_PROTOCOL

> **Note added for the public release (2026-10-25).** This document is kept unchanged as it was fixed on 2026-09-17. It was written by generative AI agents, like the rest of the study (see the AI-use statement in `README.md`). Where it says that values are derived "by hand" or that an audit is "manual", that work was in fact performed by AI agents and was not verified by a human expert. "Pre-registered" means fixed in advance in a private repository before the runs; there is no public, independently timestamped pre-registration.

Frozen: 2026-09-17, before running any tool on the real-code corpus and before authoring the micro-corpus expected values were compared with any tool output. Any later change is recorded in RESEARCH_LOG.md and, if it affects results, labelled EXPLORATORY / POST-HOC in the manuscript.

## 1. Environment (recorded in `reproduction/environment.md`)
Windows 11 Pro 10.0.26200, Intel Core Ultra 9 275HX, 32 GB RAM; Python 3.11.0 (analysis) and `tools_venv` (Python tool versions below); Node 22.16.0; JDK 17.0.17 (PMD, sonar-scanner) and 21.0.9 (cognitive-java); Go 1.27.1 (portable); Docker Desktop 29.6.2 with `sonarqube:community` image digest sha256:58b068af…7d51 = SonarQube Community Build 26.9.0.129388; sonar-scanner CLI 8.1.0.6389.

## 2. Tools and versions (pinned)
| Language | Tool | Version | Invocation | Function identity |
|---|---|---|---|---|
| all | SonarQube (reference) | 26.9.0.129388; java 8.41, python 5.31, javascript 13.8, go 1.43.0 | quality profiles `cc-study-<lang>` with S3776 threshold 0 and cyclomatic rule threshold 0; issues via Web API | issue line = function name line; per-increment secondary locations |
| Python | complexipy | 8.0.1 | Python API `file_complexity` | name, line_start/end; nested defs folded |
| Python | cognitive_complexity | 1.3.0 | API `get_cognitive_complexity(ast node)` | every FunctionDef incl. nested |
| Python, JS/TS | rust-code-analysis | 0.0.25 (prebuilt) | `-m -O json -p FILE` | spaces with start/end lines; inclusive sums |
| all | codemetrics | 0.12.7 | `--format json --include-vendored FILES` | start/end lines; nested named functions separate |
| Java | PMD | 7.27.0 | ruleset `experiments/pmd-cc.xml` (reportLevel 1) `-f json` | beginline of method; values ≥ 1 only |
| Java | cognitive-java | 0.7.1 | `--format json --threshold 1 --failures-only=false --use-default-exclusions=false FILES` | lineStart/lineEnd |
| Go | gocognit | 1.2.1 | `-over 0 -json -d .` | FuncDecl position; func literals folded |
| JS/TS | cognitive-complexity-ts | 0.8.2 | `ccts-json FILES` | line/column, nested reported and folded |
| JS/TS | cogplexity | 0.1.0 | `score()` API | loc, increments; nested folded, also reported |
| JS/TS | oxlint-plugin-complexity | 3.0.0 | `analyzeFileComplexity()` standalone API | startLine/endLine |
| JS/TS | eslint-plugin-maintainability | 3.2.10 | rule `create()` with maxComplexity 0 via fake context | node loc |
| JS/TS | eslint-plugin-sonarjs (drift probe) | 4.2.1 | ESLint Linter, threshold 0 | message line |
| cyclomatic | radon 6.0.1 (Py), lizard 1.24.0 (all), PMD, rust-code-analysis, codemetrics, oxlint-plugin-complexity, SonarQube | | | |

Excluded by design: clippy `cognitive_complexity` (self-declared non-spec lint), @genese/complexity (own metric), BruhZul calculator (no licence), IDE plugins.

## 3. Corpora
### 3.1 Micro-corpus
Per language, one file per rule family under `experiments/microcorpus/<lang>/`, each function a separate case named `c_<id>`. `experiments/microcorpus/expected.csv` columns: `case_id, lang, file, function, rules, expected, ambiguous, readings, note`. Expected values are derived by hand from Appendix B (B1.x, B2.x, B3.x), the body-text rules (sections 2.2–2.9), Appendix A exceptions and the Appendix C examples (which are included verbatim as cases C1–C4 with their published totals). Cases whose value depends on an unstated choice are `ambiguous=1` with the candidate readings listed; they are excluded from conformance rates and reported separately (RQ1 "ambiguity" table). All tools run on the micro-corpus with the same invocations as on real code.

### 3.2 Real-code corpus
Selection procedure and thresholds: `scripts/select_repos.py` (see RESEARCH_CONTRACT §DATA). Inclusion: 8 accepted repositories per language, in stars order from the snapshot. Exclusion of files: vendored/generated/minified patterns and directories listed in `src/ccstudy/functions.py::iter_source_files` and `scripts/select_repos.py::EXCLUDE_DIRS`; files that tree-sitter fails to parse without errors are kept but flagged; files any single tool fails on are recorded per tool (coverage table). Test directories are NOT excluded (the metric gates test code too), but a `is_test_path` flag (path contains `test`/`tests`/`spec`/`__tests__`) is recorded for a sensitivity split. SonarQube's own test-file heuristics are neutralised by scanning with `sonar.sources=.` and no `sonar.tests`; SonarPython still skips generated files — reported as coverage loss.

## 4. Unit of analysis and alignment
- Function-like units enumerated by tree-sitter (`src/ccstudy/functions.py`): Python `function_definition`, `lambda`; Java `method_declaration`, `constructor_declaration`, `lambda_expression`, `static_initializer`; JS/TS `function_declaration`, `function_expression`, `arrow_function`, `method_definition`, generators; Go `function_declaration`, `method_declaration`, `func_literal`.
- **Leaf root function** (primary population): depth 0 and no nested function-like unit inside. Here all tools should score the same code; disagreement is rule-level.
- **Container root function** (secondary): depth 0 with nested units; tools differ in folding policy (Sonar Java/Python fold, SonarJS excludes, codemetrics excludes named nested, oxlint charges +1 per nested function). Reported separately; not used for H1/H3.
- Alignment rule (`src/ccstudy/align.py`): a tool row at line L belongs to the unit whose declaration header span [decl_line, body_line] contains L; ties resolved by exact decl_line match, then shallowest depth; remaining ties with no name → unaligned. Duplicates (two rows for one unit) → second row dropped and counted.
- Values absent because a tool does not report zero/one-valued functions (PMD ≥ 1, cognitive-java ≥ 1) are treated as missing, not as 0; agreement rates for these tools are computed on functions where both values exist and additionally reported assuming missing = 0 as a sensitivity check.
- Java `equals`/`hashCode` are skipped by Sonar's rule (not the metric); they are excluded from all Java comparisons.

## 5. Procedure
1. Micro-corpus authoring (expected values written before running tools on it).
2. Repository selection and cloning (`scripts/select_repos.py`), manifest with SHAs.
3. For each repository: enumerate files and units; run every tool with the same explicit file list (`scripts/run_realcode.py`); SonarQube scan per repository (`scripts/sonar_scan.py`), extract issues; save raw outputs to `results/raw/<lang>/<repo>/<tool>.json` untouched.
4. Align (`scripts/build_function_table.py`) → `results/processed/functions/<lang>__<repo>.csv` (one row per unit, one column per tool/metric) plus coverage tables.
5. Analysis (`scripts/analyze.py`) → agreement, flips, attribution, cyclomatic baseline, bootstrap CIs; figures and tables generated by `scripts/make_figures.py` / `scripts/make_tables.py` from processed CSVs only.
6. Manual audit: 30 random disagreements per language inspected to confirm alignment correctness and rule attribution (`results/processed/audit_<lang>.csv`).

## 6. Endpoints
- Primary: per-tool exact-agreement rate with the reference on leaf root functions (RQ2) and gate-flip rate at 15 (RQ3), per language.
- Secondary: conformance matrix (RQ1), attribution share (RQ4), cyclomatic baseline, sensitivity to threshold, test-vs-non-test split, missing-as-zero sensitivity, container functions.

## 7. Randomness
No stochastic components except the bootstrap (seed 20260917) and the audit sample (seed 20260917).

## 8. Stopping conditions
Experiments end when all 32 repositories (or the subset that scans successfully) have been processed by every tool; tools that crash on a repository are re-run once, then the failure is recorded.

## 9. Pre-declared exploratory analyses
Anything not listed above (e.g., per-construct disagreement magnitudes, version comparisons beyond sonarjs 4.2.1) is labelled EXPLORATORY.
