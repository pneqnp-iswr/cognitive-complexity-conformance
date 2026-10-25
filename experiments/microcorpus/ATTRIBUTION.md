# Attribution for micro-corpus cases derived from the Cognitive Complexity white paper

Most of the 270 cases in `expected.csv` are minimal functions written for this study from the rule
text (`origin` column = `spec-derived`, `rules` column = a `B*`/`R*` identifier). A small number of
cases instead **re-implement a worked example printed in the white paper**, so that the study can
check each tool against the totals the specification itself states. Those cases, and only those, are
recorded here.

Primary source of the examples:

> G. A. Campbell, *Cognitive Complexity: a new way of measuring understandability*, SonarSource S.A.,
> white paper, version 1.7, 29 August 2023.
> <https://www.sonarsource.com/docs/CognitiveComplexity.pdf>
> Copyright footer printed on every page: `Copyright SonarSource S.A., 2023, Switzerland. All content
> is copyright protected`.

The PDF is **not** redistributed with this package (`scripts/export_public_artifact.py` excludes
`references/spec/CognitiveComplexity.pdf`; its SHA-256 is recorded in
`references/spec/cognitive_complexity_spec_rules.md`, section 0). That digest does not reproduce the
examples' code either: its section 3 records, per example, only the method name, the project the
white paper names as its source, the stated total and the checked increment sequence. The totals
below are taken from there and from `expected.csv`.

**Do not edit the source files listed here.** The line numbers are load-bearing: every recorded value
in `results/processed/microcorpus_matrix.csv` was produced by aligning tool output to these lines.

---

## 1. Appendix C worked examples (`target` column = `C` in `expected.csv`)

The white paper names the project each Appendix C example was taken from. The names in the last
column are as recorded in the table of `references/spec/cognitive_complexity_spec_rules.md`
section 3.

| Case id | Expected | Function in this corpus | Location | White paper's example | Upstream source named by the white paper |
| --- | --- | --- | --- | --- | --- |
| `java-C1` | 19 | `overriddenSymbolFrom` | `java/Micro.java:546` (comment at 545) | Appendix C.1 | `org.sonar.java.resolve.JavaSymbol.java` — SonarJava |
| `java-C2` | 35 | `addVersion` | `java/Micro.java:575` (comment at 574) | Appendix C.2 | `com.persistit.TimelyResource.java` — recorded in the digest as "sonar-persistit" |
| `java-C3` | 20 | `toRegexp` | `java/Micro.java:621` (comment at 620) | Appendix C.3 | `org.sonar.api.utils.WildcardPattern.java` — SonarQube |
| `js-C4` | 20 | `save`, the single method of the object literal `yuiModel` | `javascript/micro.ts:553` (object at 552, block 552–588; comment at 551) | Appendix C.4 | `model.js` — YUI |

All three Java cases sit inside `class AppendixC`, which spans `java/Micro.java:544–727`; lines
707–726 of that class are compilation stubs written for this study (`TIMED_OUT`, `WWRetryException`,
`ClassJavaType`, …) so that the file parses standalone. They are marked in the file as
"never analysed as cases" and have no row in `expected.csv`.

**A second copy of the C.4 block exists** at `experiments/ccts_probe/a1.ts:552–588`. `a1.ts` is an
earlier snapshot of `javascript/micro.ts` kept as a probe input for `cognitive-complexity-ts`; a
`diff` shows the two files are identical except that `micro.ts` adds the post-hoc case
`c103_recursion_two_calls` at lines 589–596. `a1.ts` carries no case id and no row in `expected.csv`.

## 2. Annotated body examples (`rules` column = `body` in `expected.csv`)

These are the examples printed in the running text of the specification rather than in an appendix.
The white paper does **not** name an upstream project for any of them; they are illustrations written
for the paper.

| Case id | Expected | Function | Location | Where it is printed |
| --- | --- | --- | --- | --- |
| `java-sumOfPrimes` | 7 | `sumOfPrimes` | `java/Micro.java:659` (comment at 658) | page 10 (the `note` column, and the digest's section 3) |
| `java-getWords` | 1 | `getWords` | `java/Micro.java:673` (comment at 672) | page 10 (the `note` column, and the digest's section 3) |
| `java-myMethod` | 9 | `myMethod` | `java/Micro.java:687` (comment at 686) | section 2.9 (white paper pp. 8–9) |
| `java-myMethod2` | 2 | `myMethod2` | `java/Micro.java:700` (comment at 699) | section 2.9 (white paper pp. 8–9) |

Two further cases are noted in `expected.csv` as following the *shape* of a body example without
reproducing it: `java-c63` (`c63_labeled_continue`, note "sumOfPrimes pattern") and `java-c41`
(`c41_lambda_with_if`, note "section 2.9 myMethod2 pattern"). They are ordinary spec-derived cases.

## 3. Appendix A.3 compensating-usage examples (`target` column = `A.3`)

Three Python cases are ports of the decorator examples printed in Appendix A.3 (white paper
pp. 12–15). They keep the paper's function names so that a reader can match them to the text, and
they reproduce the three totals the appendix states, which the digest records in its section 2.10:
a qualifying decorator 1, `not_a_decorator` 2, a decorator generator 1. Like the body examples,
Appendix A.3 names no upstream project.

| Case id | Expected | Function | Location | White paper's example |
| --- | --- | --- | --- | --- |
| `py-c44` | 1 | `c44_decorator` | `python/micro.py:302–307` | `a_decorator`, total 1 |
| `py-c45` | 2 | `c45_not_a_decorator` | `python/micro.py:310–316` | `not_a_decorator`, total 2 |
| `py-c46` | 1 | `c46_decorator_generator` | `python/micro.py:319–326` | `decorator_generator`, total 1 |

`py-c41` and `py-c42` cite `A.3` in their `rules` column as the reading they test, but their bodies
are written for this study.

## 4. Basis on which these derived cases are included

* **Purpose.** Each case exists so that an implementation can be checked against a total the
  specification itself asserts (19, 35, 20, 20, 7, 1, 9, 2, and the three Appendix A.3 totals). That
  is the conformance question the study measures; the examples cannot be replaced by different code
  without losing the published expected value.
* **Extent.** The excerpts are short and are the specification's own illustrations, not a usable
  portion of any upstream program: the Java cases carry hand-written stubs in place of the real
  types, `micro.ts` keeps only the one `save` method, and no upstream file, module or build is
  reproduced.
* **Attribution.** The upstream projects the white paper names are listed in section 1 above; the
  specification and its copyright holder are named at the top of this file and in section 0 of
  `references/spec/cognitive_complexity_spec_rules.md`.
* **Licence status.** These excerpts are **not** covered by this package's MIT or CC BY 4.0 grants
  (see `../../LICENSE` and `../../THIRD_PARTY_NOTICE.md`). They are included as quotation for
  research and criticism. Any right they carry remains with SonarSource S.A. and, for the Appendix C
  examples, with the copyright holders of the named upstream projects.
* **What this file does not claim.** This repository holds **no record of the licence** under which
  the Appendix C source files were published at the time the white paper quoted them, and none was
  verified for this note. `references/tools/tool_landscape.md` records licences for the *current*
  SonarSource repositories it inspected on 2026-09-17 (row J2: sonar-java "SSAL v1.0 (not OSI)";
  row S6: SonarJS "Repo LICENSE.txt = SSAL v1.0 … npm `eslint-plugin-sonarjs` 4.2.1 says
  `LGPL-3.0-only`"), but those are today's terms of today's repositories, not the terms of the
  2017-era files in Appendix C. Nothing is recorded anywhere in this repository about the licences of
  Persistit or YUI. A re-user who needs a licence answer for the upstream code must obtain it from
  those projects.

## 5. Precedent recorded in this repository

`references/tools/test_example_inventory.md` (compiled 2026-09-17 from the tools' own test files at
pinned commits) records that several independent implementations already ship these same examples as
test fixtures: PMD, cognitive-java and cogplexity encode the three Java Appendix C examples,
cogplexity also the JavaScript C.4 example, gocognit encodes C.3 and four annotated body examples,
and codemetrics two body examples. That inventory is evidence about existing practice; it is not a
licence grant and is not relied on as one.

---

### How this file was verified

* Case ids, expected values, `rules`, `target` and `origin` read from `expected.csv`
  (270 data rows; `target == "C"` yields exactly `java-C1`, `java-C2`, `java-C3`, `js-C4`;
  `rules == "body"` yields exactly the four `java-*` rows in section 2).
* Line numbers read with `grep -n` from the working copies of `java/Micro.java` (727 lines),
  `javascript/micro.ts` (596 lines), `python/micro.py` (487 lines) and
  `../ccts_probe/a1.ts` (588 lines). No source file was modified.
* The duplication of the C.4 block was established with
  `diff experiments/ccts_probe/a1.ts experiments/microcorpus/javascript/micro.ts`, whose only output
  is the eight added lines of `c103_recursion_two_calls`.
* Upstream project names, example totals and page numbers were read from
  `references/spec/cognitive_complexity_spec_rules.md` sections 2.9, 2.10 and 3 (checked against that
  file at SHA-256 `65b78a35cb96a03916ef669232bb6ef859aabf77b406d3297bf2598980d58e08`), and
  cross-checked against the `note` column of `expected.csv`.
* The expected values were cross-checked against `results/processed/microcorpus_matrix.csv`, where
  the `expected` column carries the same numbers for these eight case ids.
