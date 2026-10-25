# RESEARCH_CONTRACT

> **Note added for the public release (2026-10-25).** This document is kept unchanged as it was fixed on 2026-09-17. It was written by generative AI agents, like the rest of the study (see the AI-use statement in `README.md`). Where it says that values are derived "by hand" or that an audit is "manual", that work was in fact performed by AI agents and was not verified by a human expert. "Pre-registered" means fixed in advance in a private repository before the runs; there is no public, independently timestamped pre-registration.

Frozen: 2026-09-17 (before any metric tool was run on the real-code corpus; only the four hand-written sandbox files in `experiments/sandbox/` had been probed to verify that the tools run and to learn their output formats).

## PROBLEM

Cognitive Complexity (Campbell, SonarSource, white paper v1.7, 2023) is a prose specification of a code-understandability metric. It is enforced as a CI quality gate with a default threshold of 15 (rule S3776) and is used as a dependent variable in empirical software-engineering studies. The metric has been re-implemented independently in at least a dozen open-source tools across languages. Whether these implementations, and SonarSource's own per-language analyzers, produce the same number for the same function — and therefore whether a threshold decision or a published measurement is tool-independent — has not been measured. Prior work shows that tools disagree for cyclomatic, Halstead and object-oriented metrics (Lincke et al. 2008; Aversano et al. 2017, 2018; Zaric & Rakic 2024), but Cognitive Complexity is the first widely deployed metric with a normative written specification (Appendix B rules, Appendix C worked examples), which makes rule-level conformance testing possible rather than mere "tools differ" observations.

## RESEARCH QUESTION

RQ1 (conformance): For a construct-enumerating micro-corpus with spec-derived expected values, which Appendix B rules do (a) SonarSource's own analyzers for Java, Python, JavaScript/TypeScript and Go and (b) independent open-source implementations violate, and where is the specification itself ambiguous?

RQ2 (agreement on real code): On functions from popular open-source repositories, how often and by how much do independent implementations disagree with the SonarQube reference value, and how does this compare with cross-tool agreement for cyclomatic complexity?

RQ3 (gate flips): What fraction of functions is classified differently with respect to the default gate (>15) depending on the tool used, and how does this fraction change with the threshold (10, 15, 20, 25)?

RQ4 (attribution): What share of real-code disagreements is explained by the rule-level deviations identified in RQ1?

## HYPOTHESIS / TARGET PROPOSITION

H1: At least one independent implementation per language deviates from the SonarQube reference on more than 5 % of leaf root functions (functions that contain no nested function-like unit), and at least one such deviation is attributable to a specific Appendix B rule.
H2: The SonarQube reference itself violates at least one Appendix B rule in at least one language (candidate from the source-code reading of 2026-09-17: recursion, B1.8, and `||` sequences in JavaScript, B1.7).
H3: Gate flips at 15 are rare in absolute terms (< 2 % of all functions) but concentrated among functions near the threshold, so that among functions with reference value in [10, 20] more than 5 % flip for at least one tool.
H4: Cross-tool agreement for cyclomatic complexity is not better than for cognitive complexity (the "better-specified metric agrees better" expectation is not confirmed).

Falsification: if every independent implementation agrees exactly with the reference on ≥ 99 % of leaf root functions and gate-flip rates are < 0.5 % for all tools, H1 and H3 are refuted and the paper reports tool-independence as a positive reproducibility finding.

## CONTRIBUTION

A spec-adjudicated conformance suite and a differential study of 13 open-source Cognitive Complexity implementations against SonarQube's reference across four languages, quantifying rule-level deviations, real-code agreement, and gate-flip rates, and showing which deviations originate in the specification's own ambiguity or in the reference implementation.

## SECONDARY CONTRIBUTIONS

- A reusable, versioned micro-corpus (per language) with expected values and explicit ambiguity labels.
- A public harness (tree-sitter alignment + adapters) that other tools can be plugged into.
- A catalogue of concrete deviations suitable for bug reports to tool maintainers.

## MECHANISM

Implementations translate prose rules into AST traversals; the prose leaves nesting scope, operator-sequence boundaries, nested-function attribution, recursion detection and language-specific constructs (comprehensions, `match`, `??`, `else` on loops) underspecified or costly to implement. Each such gap is a place where independent implementers may choose differently; the micro-corpus isolates each gap so that a disagreement can be traced to one rule, and the real-code corpus measures how often those constructs occur in practice and whether they move a function across the gate.

## SCOPE

- Languages: Java, Python, JavaScript/TypeScript, Go (all analyzable by SonarQube Community Build).
- Reference: SonarQube Community Build 26.9.0.129388 (sonar-java 8.41, sonar-python 5.31, SonarJS 13.8, sonar-go 1.43.0), rule S3776 with threshold 0 so every function is reported.
- Independent implementations (versions pinned): Python — complexipy 8.0.1, cognitive_complexity 1.3.0, rust-code-analysis 0.0.25, codemetrics 0.12.7; Java — PMD 7.27.0, cognitive-java 0.7.1, codemetrics 0.12.7; JS/TS — cognitive-complexity-ts 0.8.2, cogplexity 0.1.0, oxlint-plugin-complexity 3.0.0, eslint-plugin-maintainability 3.2.10, rust-code-analysis 0.0.25, codemetrics 0.12.7; Go — gocognit 1.2.1, codemetrics 0.12.7. Additionally eslint-plugin-sonarjs 4.2.1 (an archived npm snapshot of SonarJS's own rule) as a reference-version-drift probe, not as an independent implementation.
- Cyclomatic baseline: SonarQube (S1541 / FunctionComplexity), PMD, radon, lizard, rust-code-analysis, codemetrics, oxlint-plugin-complexity.
- Unit of analysis: function-like units enumerated by tree-sitter (see EXPERIMENT_PROTOCOL.md §4).

## OUT OF SCOPE

- Whether Cognitive Complexity predicts understandability (validity); only measurement consistency is studied.
- C/C++/C#/Kotlin/PHP implementations (no free reference analyzer or not in the time budget).
- Commercial or IDE-only implementations (SciTools Understand, IntelliJ plugins).
- Whole-file or project-level aggregates; only per-function values.
- Any claim about which implementation is "correct" beyond conformance to the written specification.

## DATA

- Micro-corpus: hand-written minimal functions per language in `experiments/microcorpus/<lang>/`, with `expected.csv` (case id, rule ids, expected value, ambiguity flag, derivation note), authored from Appendix B/C and the body text before running any tool on them.
- Real code: 8 repositories per language selected by the pre-registered procedure in `scripts/select_repos.py` (GitHub search `language:L stars:>=5000 archived:false fork:false pushed:>=2026-01-01`, stars-descending order, accept when target-language LOC ∈ [20k, 400k] (Java: [20k, 600k]), shallow clone at HEAD, SHA recorded, skipped repositories logged with reasons). Manifest: `data/repos/manifest.csv`, selection snapshots `data/repos/selection_<lang>.json`.

## GROUND TRUTH

Two levels. (1) Specification: expected values derived by hand from Appendix B rules and the worked examples; every case whose value depends on an unstated choice is labelled AMBIGUOUS with the candidate readings and excluded from conformance rates (but reported). (2) Reference: SonarQube's value for the same function; the reference's own conformance to level (1) is measured, not assumed.

## BASELINES

- Strongest baseline for RQ2/RQ3: the null of practice — implementations are interchangeable (exact agreement ≈ 100 %, flip rate ≈ 0).
- Comparative baseline: cross-tool agreement for cyclomatic complexity on the same functions (the metric for which tool-dependence is already established).
- Reference-drift baseline: eslint-plugin-sonarjs 4.2.1 vs SonarJS 13.8 (same vendor, different version).

## METRICS

- RQ1: per-tool conformance rate on unambiguous micro-corpus cases; per-rule pass/fail matrix; list of ambiguous cases with observed readings.
- RQ2: exact-agreement rate with the reference; share within ±1; mean absolute deviation; Spearman ρ; distribution of signed differences; all on leaf root functions (primary) and on all root functions (secondary, with nested-unit folding noted).
- RQ3: gate-flip rate at threshold t ∈ {10, 15, 20, 25}: share of functions with (ref > t) ≠ (tool > t), over all functions and over functions with reference value in [t−5, t+5]; "flagged-by-reference" precision/recall of each tool at t = 15.
- RQ4: share of disagreeing functions containing at least one construct on which the tool deviated in the micro-corpus (feature counts from tree-sitter), reported per tool with the unexplained residual.
- Coverage: functions reported by each tool / functions enumerated; unaligned rows.

## STATISTICAL METHOD

Descriptive statistics with 95 % confidence intervals from a cluster bootstrap over repositories (2,000 resamples, seed 20260917), since functions within a repository are not independent. No null-hypothesis significance tests are planned; the pre-registered thresholds in H1–H4 are the decision rules. Spearman ρ with the same bootstrap.

## REQUIRED EVIDENCE

- Claim "tool X violates rule R": the micro-corpus case(s) for R with tool output and spec derivation (`results/processed/microcorpus_matrix.csv`).
- Claim "X disagrees with the reference on p % of functions": `results/processed/agreement_<lang>.csv` with bootstrap CI and per-repository breakdown.
- Claim "p % of functions flip at 15": `results/processed/flips_<lang>.csv`.
- Claim "deviation explained by rule R in q % of cases": `results/processed/attribution_<lang>.csv`.
- Every manuscript number: `results/result_manifest.csv`.

## THREATS

- Alignment errors between tools' function identities (mitigated by the pre-registered alignment rule, coverage reporting and manual audit of 30 random disagreements per language).
- Version drift: results are for pinned versions and dated; the reference itself may change.
- Repository selection bias toward popular projects; generalization to other code is not claimed.
- Micro-corpus authoring bias: expected values derived by one person; mitigated by deriving from quoted spec text, cross-checking with the four Appendix C examples, and labelling ambiguities rather than resolving them.
- Tool misconfiguration (e.g., thresholds, file discovery): mitigated by running every tool with a threshold of 0/1 and the same explicit file list, and reporting coverage.

## SUCCESS CRITERIA

H1–H4 as stated; the study is successful (informative) if either the deviations are quantified with attributable rules, or tool-independence is demonstrated with the pre-registered agreement levels.

## FAILURE CRITERIA

- Alignment coverage below 90 % for any tool–language pair without a documented cause (would invalidate agreement statistics for that pair).
- SonarQube scans failing for more than 2 of 8 repositories in a language (would shrink the sample; report and continue with the remainder).
- Discovery of a published study measuring the same agreement (post-result novelty audit) — would require re-positioning.
