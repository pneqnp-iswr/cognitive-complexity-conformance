# Coverage causes: why tools lack values on the primary population

Companion to `coverage_causes.csv`. Numbers were computed with `py -3.11` scripts from
`results/processed/functions/<lang>__<repo>.csv` (regenerated 2026-09-17 13:41–13:48, after the
units.json rebuild; the older `coverage_java/javascript/go.csv` from ~05:00 differ slightly),
from the raw tool JSON files (`results/raw/<lang>/<repo>/<tool>.json`) and from `run_meta.json`.

**Population.** Primary = `depth == 0`, `nested_count == 0`, `has_body == 1`, and a SonarQube
reference (`cog__sonarqube` non-empty). `n_ref` is that count; `n_tool` is how many of those rows
have a value for the tool. Python 24,520; Java 58,532; JS/TS 26,038; Go 28,521.
The reference itself is issue-based: Sonar runs S3776 with threshold 0 (`scripts/sonar_setup.py`
lines 16–20), so it emits a row only for functions with cognitive complexity > 0; the remaining
depth-0 units in a file get 0 from the zero-fill rule in `scripts/build_function_table.py`
(lines 37 and 61) as soon as *any* Sonar row exists in that file. Because Sonar also runs the
cyclomatic rule S1541 at threshold 0 (every function has cyclomatic ≥ 1) for Python/Java/JS, every
analysed file has a row and thus a reference. Go has no S1541 rule, which is why `cyc__sonarqube`
is empty for Go and the Go reference only covers files with at least one cc > 0 function.
The same zero-fill rule applies to `pmd`, `eslint-plugin-sonarjs-4.2.1`,
`eslint-plugin-maintainability` and `gocognit` (`THRESHOLD_TOOLS`), which is what makes the
ESLint plugins' shortfall a file-level artefact (see below).

"File-level" below means the tool reported no row at all in the file; "function-level" means the
file has tool rows but this function has none.

## Pairs below 95 %

### javascript / codemetrics — 12,415 / 26,038 (47.7 %), 7/8 repos
Two causes. (1) immich-app/immich failed entirely: `run_meta.json` records
`errors.codemetrics = TypeError: 'NoneType' object is not iterable` at `src/ccstudy/tools.py:151`
(codemetrics printed `null` for one chunk and the adapter did not guard it), `codemetrics.json`
is `[]`, so all 4,032 immich reference functions are missing and the repo counts as not covered.
(2) In the other seven repos codemetrics 0.12.7 does not report arrow functions or function
expressions: 10,472 of 10,473 primary arrows and 29/29 `function_expr` units are missing, against
813/9,313 `function` declarations and 2,309/6,223 methods (covered kinds: function 8,500, method
3,914, arrow 1). The extension pattern (.tsx 88.7 % missing, .ts 47 %) is a consequence of React
components being arrow functions, not of an extension filter — codemetrics did emit .tsx rows
(822 in ant-design). No error rows or meta errors exist in any `codemetrics.json`.

### java / cognitive-java — 50,598 / 58,532 (86.5 %), 8/8 repos
All but 25 misses are in ReactiveX/RxJava (6,290 of 14,199 covered, 44.3 %). `cognitive_java.json`
for RxJava holds 11 meta rows, 8 of them errors of the form
`Failed to parse Java source: <file>:<line>: unnamed variables are a preview feature and are
disabled by default. (use --enable-preview to enable unnamed variables)`: the JavaParser bundled
in cognitive-java-cli 0.7.1 parses at Java 21 level and rejects the Java 22 `_` unnamed variables
used in RxJava 4. `run_cognitive_java` in `tools.py` passes 200 files per invocation and keeps
nothing when the tool fails, so 1,600 of 2,072 files (7,909 primary functions, 872 files with a
reference) are lost. The three successful chunks (600 files) show `excludedFiles: 0`. The 25
remaining misses are Java lambdas (36/36 missed, some in the lost chunks).

### java / lizard — 47,719 / 58,532 (81.5 %), 7/8 repos
(1) TheAlgorithms/Java was lost completely: `run_meta.json` records
`errors.lizard = FileNotFoundError [WinError 206]` ("file name or extension too long"), i.e. the
Windows 32,767-character command-line limit. The original `run_lizard` (commit f60187b) passed 200
absolute OneDrive paths per call; the length-based chunking now in `tools.py` (commit 5702b67,
20,000 chars) was only re-run for iluwatar (rerun entry at 00:13:50Z, 4,978 rows). TheAlgorithms'
`lizard.json` is `[]` (2 bytes): 8,336 misses. (2) RxJava (84.7 %): lizard 1.24's Java reader stops
emitting after the first method whose type parameter carries an annotation. In `Maybe.java` lizard
reports 2 functions and 181/183 misses all follow line 157
`public static <@NonNull T> Maybe<T> ambArray(...)`; the same holds for `Single.java` (171/173 after
line 162), `Flowable.java` (324/470 after line 6251) and `Observable.java` (289/432 after line 5584).
Plus 36 lambdas; other repos are at 95.8–100 %.

### javascript / lizard — 20,105 / 26,038 (77.2 %), 8/8 repos
Function-level (5,787 of 5,933 misses). lizard's JavaScript/TypeScript reader drops 3,286 of 6,223
class/object methods (52.8 %), 1,512/10,473 arrows and 1,131/9,313 functions. In a 1,500-row sample
of missed vs. covered methods: getters/setters 136 vs 0, TypeScript return-type annotations 1,076
vs 690, private `#methods` 44 vs 22. In 301 files every miss lies after the last line lizard
reported (parser bail-out), and `run_meta.json` shows large unaligned/duplicate counts for lizard
(e.g. ant-design 1,757 unaligned, 99 dups). Worst repos: immich 67 %, pi 69 %, gstack 77 %.

### javascript / eslint-plugin-sonarjs-4.2.1 — 21,560 / 26,038 (82.8 %), 8/8 repos
Entirely file-level (4,478 misses in 2,241 files) and not a parse problem: the adapter's meta rows
report 0 errors in all 8 repos, and every covered function with Sonar cc = 1 is reported as 1
(4,396/4,396). The rule runs with threshold 0 (`src/js_cc.mjs` line 114:
`"sonarjs/cognitive-complexity": ["error", 0]`) so it only reports functions with cc > 0. All 2,241
missed files have a maximum Sonar cognitive complexity of 0 over all their units; the plugin
therefore emits no row for the file, and the zero-fill in `build_function_table.py` (which needs at
least one tool row per file) never fires, whereas Sonar's S1541 cyclomatic rows give those files a
reference. The shortfall concentrates in .tsx demo/test code (ant-design 39.4 %, immich 64.9 %).

### javascript / eslint-plugin-maintainability — 21,950 / 26,038 (84.3 %), 8/8 repos
Same mechanism: all 4,088 misses are file-level; 2,067 of the 2,109 missed files have max Sonar
cc 0 (`js_cc.mjs` line 86 runs the rule with `maxComplexity: 0`, so cc-0 functions produce no
report). The other 42 files (max Sonar cc 1–6) are functions the plugin scores 0 where Sonar does
not. Adapter meta errors = 0 in every repo.

### python / lizard — 22,221 / 24,520 (90.6 %), 7/8 repos
Shubhamsaboo/awesome-llm-apps was lost with the same `WinError 206` as the Java repos
(`run_meta.json.errors.lizard`, timing `lizard: 0.0`, `lizard.json` = `[]`, no rerun entry): 1,932
of the 2,299 misses. The remaining 367 are the 183 module-level lambdas (missed by every tool) and
184 functions of which 147 are `@overload`/`@typing.overload` stubs (langchain
`runnables/base.py` 51).

## Pairs at or above 95 %

- **python / codemetrics 99.25 %** — all 183 misses are module-level lambdas (kind = lambda);
  no error rows.
- **python / cognitive_complexity 97.99 %** — 183 lambdas + 311 functions in 53 files that
  `ast.parse` rejects under `tools_venv` Python 3.11.0 (`python_tools.json` error rows: invalid
  syntax x22, "multiple exception types must be parenthesized" x15, "expected '('" x15, 3.12-only
  f-string syntax x4); the whole file is lost.
- **python / complexipy 98.38 %** — 183 lambdas + 213 functions, all 213 defined inside a
  module-level `try`/`if`/`with` block (decl lines indented; `youtube_dl/compat.py` 84), which
  complexipy 8.0.1 does not enumerate.
- **python / rust-code-analysis 99.12 %** — 183 lambdas + 32 functions (`rca.json` has 441
  "no output" rows, mostly empty `__init__.py`).
- **python / radon 97.84 %** — shares the `ast.parse` failures with cognitive_complexity
  (313 file-level) + 183 lambdas + 33.
- **java / codemetrics 99.94 %** — the 36 lambdas only.
- **java / pmd 97.64 %** — exactly the five RxJava core files listed in `pmd.json`
  `processingErrors` (Flowable 470, Observable 432, Maybe 183, Single 173, Completable 124 = 1,382):
  PMD 7.27 aborts them with a `SemanticException` in type resolution or a `NullPointerException` in
  `OverloadSelectionResult.isFailed`. All other repos 100 %.
- **javascript / cognitive-complexity-ts 95.73 %** — immich 569 misses, 301 of them NestJS methods
  with a decorator on the previous line (0 of 800 covered ones), which the tool reports at the
  decorator line, outside the alignment window (`run_meta` immich unaligned = 929); 7 excalidraw
  files fail with "Unreachable branch. Module has no module/namespace keyword" (`ccts.json` meta
  `n_failed_files: 7`, incl. `packages/excalidraw/components/App.tsx`, 157 misses).
- **javascript / cogplexity 96.77 %** — immich 654 of 840 misses (decorated methods, unaligned = 890
  in `run_meta`); gstack 132 one-line arrays of arrows in tests.
- **javascript / oxlint-plugin-complexity 98.42 %** — computed-key reducer arrows
  (`[actionTypes.x]: state => ...`, freeCodeCamp `redux/index.js` 55 + 35) and `#private` methods.
- **javascript / rust-code-analysis 99.07 %** — 239 of 243 misses are the same computed-key arrows;
  3 `.cjs` files "no output".
- **go / codemetrics 98.98 %** — all 290 misses are func literals assigned to struct fields
  (kind = lambda); 0 functions or methods missed.
- **go / gocognit 100 %** — no misses.
- **go / lizard 96.46 %** (extra pair, reference = cognitive population) — 887 top-level
  funcs/methods dropped mid-file (all misses after the last lizard row in 43 files) + 122/290 func
  literals.

## Cross-cutting notes
- Python lambdas (183) and Java/Go lambdas / func literals (36 / 290) are counted as leaf root
  units by the tree-sitter enumeration but reported by none of the tools except SonarQube; they
  are a population choice rather than a tool defect.
- The two lizard repo failures and the immich codemetrics failure are fixable by re-running the
  tool (`scripts/rerun_tool.py`) with the current `tools.py`; the `[]` files are the residue of the
  failed first run.
