# Cognitive Complexity: study digest of the specification, and observed Sonar implementation behaviour

**What this file is, and what it is not.** This is a working digest written for the present
study. It is **not** the specification and is not a substitute for it. The normative text is
SonarSource's white paper *Cognitive Complexity: a new way of measuring understandability*
by G. Ann Campbell, **version 1.7, 29 August 2023**, published at
<https://www.sonarsource.com/docs/CognitiveComplexity.pdf> and copyright SonarSource S.A.;
it is not reproduced here. Sections 2-5 restate each rule in the author's own words and cite
where the white paper states it (body section or appendix item, plus the page recorded during
transcription) so that every claim can be checked against the original. Anyone who wants to
*apply* the metric must read the white paper itself.

A small number of short quotations remain, each well under 25 words, in quotation marks and
attributed to the section or appendix it comes from. They are kept only where the exact
wording is what fixes an expected value in `experiments/microcorpus/expected.csv`, and they
are used for analysis and criticism. The white paper's change log, its appendix lists as
printed, and the source code of its worked examples are **not** reproduced; where a worked
example supplies an expected value, only the value and the arithmetic that produces it are
recorded.

Sections 6, 7 and 8 - the observed implementation behaviour tables, the ambiguity catalogue
and the counts - are the author's own findings, derived from the analyser sources listed in
section 0 and from their test fixtures.

Compiled 2026-09-17 from primary sources: the white-paper PDF (text layer extracted with
`pdftotext`, poppler) and the fetched analyser sources named in section 0.

## 0. Provenance

| Item | Value |
|---|---|
| White paper | *Cognitive Complexity: a new way of measuring understandability*, by G. Ann Campbell, SonarSource |
| Version / date printed on page 2 | `29 August 2023, Version 1.7` |
| Copyright footer | `Copyright SonarSource S.A., 2023, Switzerland. All content is copyright protected` |
| Source URL | https://www.sonarsource.com/docs/CognitiveComplexity.pdf |
| Local copy | `<LOCAL_PATH>/OneDrive/Documents/Conferences/research/references/spec/CognitiveComplexity.pdf` |
| SHA-256 | `d1bbd47a0c48500bfeafa5dfada42ecddfe1c3e75b7adebe11cb7a037fa4cb77` |
| Size / pages | 866,052 bytes, 22 pages, PDF 1.7 (Adobe InDesign 18.1, CreationDate 2023-08-30 22:17:46) |

The SHA-256 and the URL above are the provenance anchor: re-download the PDF from the URL,
hash it, and every page and section citation in this file can be resolved against it.

Implementation sources fetched (all `master` as of 2026-09-17):

| Language | File | Notes |
|---|---|---|
| Java (rule) | `SonarSource/sonar-java` `java-checks/src/main/java/org/sonar/java/checks/CognitiveComplexityMethodCheck.java` | S3776, default `Threshold` 15, skips `equals`/`hashCode` |
| Java (metric) | `SonarSource/sonar-java` `java-frontend/src/main/java/org/sonar/java/ast/visitors/CognitiveComplexityVisitor.java` | the actual counter |
| Java (fixtures) | `java-frontend/src/test/files/metrics/CognitiveComplexity.java`, `java-checks/src/test/files/checks/CognitiveComplexityMethodCheckMax0.java` | expected values used below |
| Java (rule text) | `sonar-java-plugin/src/main/resources/org/sonar/l10n/java/rules/java/S3776.html` and `S3776.json` | bundled copy of RSPEC-3776 |
| Python (rule) | `SonarSource/sonar-python` `python-checks/src/main/java/org/sonar/python/checks/CognitiveComplexityFunctionCheck.java` | S3776, default `threshold` 15, skips inner functions and generated files |
| Python (metric) | `python-frontend/src/main/java/org/sonar/python/metrics/CognitiveComplexityVisitor.java` | the actual counter |
| Python (fixtures) | `python-frontend/src/test/resources/metrics/cognitive-complexities.py` (file total asserted = 91), `python-checks/src/test/resources/checks/cognitiveComplexityFunction.py` | |
| Python (rule text) | `python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S3776.html` and `S3776.json` | bundled copy of RSPEC-3776 |
| JS/TS (rule + metric) | `SonarSource/SonarJS` `packages/analysis/src/jsts/rules/S3776/rule.ts` (+ `meta.ts`, `config.ts`, `unit.test.ts`, `helpers/jsx.ts`) | default threshold 15; the rule directory moved from `packages/jsts/src/rules/S3776` to `packages/analysis/src/jsts/rules/S3776` |
| JS/TS (rule metadata) | `sonar-plugin/javascript-checks/src/main/resources/org/sonar/l10n/javascript/rules/javascript/S3776.json` | no `.html` is checked in for JS; description is generated at build time |

Not reachable from this machine: `rules.sonarsource.com` (DNS `ENOTFOUND` for every
path, including `/java/RSPEC-3776/json`), `github.com/SonarSource/rspec` (HTTP 404 via
API and raw; the repository appears to be no longer public), and
`sonarsource.github.io/rspec/...` (returns a GitHub 404 shell). The RSPEC-3776 material
summarised in section 5 is therefore taken from the copies bundled in the sonar-java and
sonar-python plugins, which are generated from the same RSPEC source.

## 1. White paper version and date

Version and date, printed on page 2: `29 August 2023, Version 1.7`. Every page carries the
footer `Copyright SonarSource S.A., 2023, Switzerland. All content is copyright protected`;
the back cover reads `© 2008-2023, SonarSource S.A, Switzerland.` These three strings are
recorded because they identify the exact edition the study analysed.

## 2. Rule digest (paraphrase, with citations)

Each item below is this study's restatement of a rule, followed by where the white paper
states it. Page numbers are those of the v1.7 PDF identified in section 0.

### 2.1 Basic criteria and methodology (p. 5)

The paper frames the metric with three guiding rules: constructs that merely shorthand
several statements into one are not counted; every break in the code's linear flow costs one
point; and flow-breaking constructs nested inside one another cost extra. It then classifies
the points into four kinds - *nesting*, *structural*, *fundamental* and *hybrid* - which
differ only in whether the construct is charged for the nesting it sits in and whether it
deepens the nesting for what it contains; arithmetically every increment is worth one. The
taxonomy is presentational: the paper says explicitly that the distinction exists to make
clear where nesting increments do and do not apply, not to change the total.

Working definitions used throughout this file: *structural* = charged +1 plus the current
nesting depth, and deepens nesting for its body; *hybrid* = charged +1 with no nesting
surcharge, but still deepens nesting for its body; *fundamental* = charged +1 flat, no
nesting effect either way; *nesting* = the surcharge itself.

### 2.2 Shorthand is ignored (p. 6)

The metric is meant to reward readable code, so constructs that condense several statements
into one readable one are ignored or discounted. Two consequences are stated: a method call
costs nothing (naming a block of code is exactly such a shorthand, so methods themselves
carry no increment), and "null-coalescing operators" cost nothing either, because they
collapse a null guard into a single expression.

(Observation by the author, not by the paper: the illustration the paper gives for this rule
is the *null-conditional* / safe-navigation operator `?.`, not a null-coalescing operator
such as `??`. The paper uses the single term "null-coalescing" for both, which is why rule
R13 below covers both and why the study's cases `js-c81`/`js-c82` test them separately.)

### 2.3 Increments for breaks in the linear flow (p. 6)

Constructs that interrupt reading order cost a point. The paper assigns **structural**
increments to loops (`for`, `while`, `do while`, ...) and to conditionals (`if`, the ternary
operator, and preprocessor conditionals such as `#if`, `#ifdef`), and **hybrid** increments
to the continuation branches (`else if`, `elif`, `else`, ...). Continuation branches get no
nesting surcharge because, in the paper's reasoning, the reader already paid that cost when
reading the leading `if`.

### 2.4 Catch clauses (p. 7)

A `catch` clause is treated as a branch in the same way an `if` is, so each clause is a
structural increment - one point per clause, regardless of how many exception types the
clause names (this is what makes Java 7 multi-catch cost 1, not *n*). `try` and `finally`
blocks are, in the paper's words, "ignored altogether". (§2.4, p. 7.)

### 2.5 Switch statements (p. 7)

A `switch` together with all of its cases is charged a single structural increment, not one
per case. The stated justification is that a `switch` compares one variable against an
explicit set of literals and can be taken in at a glance, whereas an equivalent `if`/`else
if` chain may compare anything against anything and has to be read line by line. This is the
one place where Cognitive Complexity deliberately departs from Cyclomatic Complexity's
per-branch counting.

### 2.6 Sequences of binary logical operators (pp. 7-8)

Individual `&&` / `||` tokens are not counted. What is counted is each *run* of like
operators: the paper's formulation is that the metric "increments for each new sequence of
like operators" (§2.6). Lengthening a run costs nothing (`a && b` and `a && b && c && d` are
equally hard to read), but switching operator starts a new run and costs a point, because
mixed-operator expressions are harder to follow.

Two annotated illustrations in the paper fix the values the study's micro-corpus depends on:
an `if` whose condition runs `&&`, then `||`, then `&&` is charged 4 in total (one for the
`if` plus one per run), and an `if` whose condition is a single `&&` joining an operand to a
negated parenthesised `&&` is charged 3 (one for the `if`, one for each of the two runs the
negation separates). The paper also states that these increments apply wherever the operators
occur - in variable assignments, method invocations and return statements, not only in
control-flow conditions.

### 2.7 Recursion (p. 8)

Every method in a recursion cycle costs one fundamental increment, "whether direct or
indirect" (§2.7). Two reasons are offered: recursion is a kind of meta-loop and loops are
counted, and recursion is genuinely hard to follow even for experienced readers. Note the
unit of counting: per *method in the cycle*, not per recursive call site.

### 2.8 Jumps to labels (p. 8)

`goto`, a labelled `break` or `continue`, and the numeric multi-level forms of `break` and
`continue` found in some languages each cost a fundamental increment. All other jumps and
early exits cost nothing, on the ground that an early `return` frequently makes code clearer
rather than harder.

### 2.9 Nesting increments (pp. 8-9)

Five flow-breaking constructs in a row are easier to read than the same five nested inside
one another, so each construct that carries a structural or hybrid increment adds one nesting
level to whatever it contains, and each structural construct is additionally surcharged by
the nesting depth it sits at. Constructs that carry neither a structural nor a hybrid
increment - a method body, a `try` block - do not deepen nesting.

Two further points are made in the same section. First, top-level methods are ignored and
lambdas and nested methods carry no structural increment of their own, but they *do* deepen
the nesting level for anything inside them. Second, the paper's own worked examples fix the
following totals (values only; the example code is not reproduced here, and the study's
equivalents live in `experiments/microcorpus/`):

| Example (p. 9) | Total | Increment sequence as annotated |
|---|---|---|
| `myMethod`: `try` wrapping `if` > `for` > `while`, plus a `catch` containing an `if` | 9 | 1 + 2 + 3 (inside the `try`; the `try` itself is free and does not deepen nesting) + 1 (`catch`) + 2 (`if` inside the `catch`, nesting 1) |
| `myMethod2`: a method holding a lambda that holds an `if` | 2 | method +0 but nesting becomes 1; `if` inside the lambda +2 |
| the same method inside a `#if DEBUG` block | 4 | `#if` +1 and nesting becomes 1; the method is still free; the `if` inside the lambda +3 (nesting 2) |

(Transcription note, author's own: in the PDF the `+2 (nesting=1)` / `+3 (nesting=2)`
annotations sit on the lambda line, but the totals only work if they belong to the `if`
inside the lambda; the attachment above is the only consistent reading. The `#if DEBUG`
example is the only place in the paper where a preprocessor conditional nests a *method*.)

### 2.10 Appendix A: compensating usages (pp. 12-15), summarised

Appendix A's premise: the metric is meant to be language-agnostic, but languages differ, and
a strict reading would over-charge idioms that exist only because a language *lacks* a
feature other modern languages have. Exceptions are therefore granted for such deficits -
but only for deficits, not for the absence of an innovation one language happens to have
introduced first, and new exceptions are meant to be added slowly and withdrawn once the
deficit disappears. Three exceptions existed as of v1.7.

**A.1 - COBOL, missing `else if`.** COBOL has no `else if`, so an `IF` that is the sole
statement of an `ELSE` is treated as though it were an `else if`: the `ELSE` itself is not
charged, and the `IF` gets no nesting surcharge. An `IF` that is *not* the only statement in
the `ELSE` is charged normally, with nesting. (The appendix's COBOL listing stacks its four
annotations on the wrong lines in the PDF; the reading given here is the only one consistent
with the prose.)

**A.2 - JavaScript, missing class structures.** An outer function used purely as a
declarative namespace - that is, one whose top level contains only declarations - is ignored:
it is neither charged nor counted as a nesting level for the functions declared inside it. As
soon as the outer function's own top level contains anything that would carry a structural
increment, it is no longer purely declarative and is treated like any other function. The
appendix's two examples fix the study's expected values: the declarative form totals **1**
(only the inner `if`) and the non-declarative form totals **3** (outer `if` +1, inner `if`
+2 at nesting 1).

**A.3 - Python, decorators.** Decorators are written as a function wrapping a nested
function, which the general rules would charge for nesting; since the idiom is ubiquitous in
Python, an exception ignores that nesting level. The exception is deliberately narrow: to
qualify, a function may contain "only a nested function and a return statement" (Appendix
A.3). The appendix's three examples fix the expected values: a qualifying decorator totals
**1**, a function that also does other work (`not_a_decorator`) totals **2**, and a
decorator generator - decorator nested inside decorator, each qualifying - still totals
**1**.

### 2.11 Appendix B: specification (p. 16), as a citation table

Appendix B is a deliberately concise enumeration of what increments the metric, subject to
the Appendix A exceptions. Its preamble makes one point that matters for this study's
ambiguous cases: the list is comprehensive but not language-exhaustive, so a construct that a
language spells unusually (`elif` for `else if` is the paper's own example) is still covered
even though it is not named. Appendix B is printed as three bullet lists - increments
(8 items), constructs that raise the nesting level (6 items), and constructs that receive a
nesting increment (5 items). The sub-numbering `B1.1 ... B3.5` used throughout this
repository is **this study's**, assigned in printed order so that individual items can be
cited; the PDF numbers only the three lists.

The table below is the study's consolidation: one row per distinct construct, with the
increment type taken from the body text (sections 2.1-2.9) and the Appendix B items that
cover it in the last column. `R1 ... R15` are the study's own rule identifiers.

| Rule | Construct | Increment type | Deepens nesting for its body | Receives a nesting surcharge | Appendix B items |
|---|---|---|---|---|---|
| R1 | `if`, ternary `?:` (and `#if`, `#ifdef`) | structural | yes | yes | B1.1, B2.1, B3.1 |
| R2 | `else if` / `elif`, and plain `else` | hybrid | yes | no | B1.1, B2.1 |
| R3 | `switch`, charged once for the statement and all its cases | structural | yes | yes | B1.2, B2.2, B3.2 |
| R4 | `for`, `foreach` | structural | yes | yes | B1.3, B2.3, B3.3 |
| R5 | `while`, `do while` | structural | yes | yes | B1.4, B2.4, B3.4 |
| R6 | `catch`, once per clause however many types it names | structural | yes | yes | B1.5, B2.5, B3.5 |
| R7 | `try`, `finally` | none - "ignored altogether" (§2.4) | no | no | - |
| R8 | jumps naming a target: `goto LABEL`, `break`/`continue` with a label, and the numeric multi-level forms | fundamental | no | no | B1.6 |
| R9 | each run of like binary logical operators (`&&`, `\|\|`; a run ends where the operator changes) | fundamental | no | no | B1.7 |
| R10 | each method in a recursion cycle, direct or indirect | fundamental | no | no | B1.8 |
| R11 | a top-level method or function | none | no (but see R12) | no | - |
| R12 | nested methods, lambdas and other "method-like structures" | none | yes | no | B2.6 |
| R13 | null-coalescing and null-conditional operators | none (ignored) | no | no | - |
| R14 | other jumps and early exits (`return`, unlabelled `break`/`continue`, `throw`) | none | no | no | - |
| R15 | unary negation and parentheses within an operator sequence | none (the metric is "only concerned with binary boolean operators", change log 1.1) | no | no | - |

`B3` without a suffix is used in `expected.csv` and in the paper for the nesting-increment
group as a whole - cases whose expected value turns on accumulated nesting depth rather than
on one named construct.

### 2.12 Rule-code index used by the study

Besides the Appendix A/B/C codes and the consolidated `R` codes above, the micro-corpus and
the analysis scripts use finer target codes so that a failure can be booked to one construct.
They are the study's own labels, not the white paper's; the authoritative definitions live in
`experiments/microcorpus/expected.csv` (column `target`), `scripts/analyze.py` (the `PRED`
map) and Section III.B of the manuscript. They are listed here so that this file defines
every code the paper's Table III, Table VI and Fig. 1 name.

| Code | What the case isolates | Relation to the rules above |
|---|---|---|
| A.1 | the COBOL `ELSE`+`IF` exception | §2.10 A.1 (no corpus case: the study covers no COBOL) |
| A.2 | the JavaScript declarative-outer-function exception | §2.10 A.2 |
| A.3 | the Python decorator exception | §2.10 A.3 |
| B1.3a | `async for` - a `for` under an atypical spelling | B1.3 via the Appendix B preamble |
| B1.7and | a sequence built only from and-type operators | B1.7 / R9 |
| B1.7or | a sequence built only from or-type operators | B1.7 / R9 |
| B1.7mix | an expression containing both kinds, so at least one operator change | B1.7 / R9 |
| B1.7idiom | the `x = x \|\| default` value idiom, which Appendix C.4 charges +1 | B1.7 / R9 |
| B1.7bit | non-short-circuit boolean operators (`&`, `\|`): binary logical operators or not | B1.7 / R9, unresolved (item 7 below) |
| B1.8d | plain direct recursion | B1.8 / R10 |
| B1.8d2 | direct recursion with two or more call sites - one increment per method, not per call | B1.8 / R10 (§2.7) |
| B1.8i | indirect (mutual) recursion | B1.8 / R10 |
| B1.8m | recursion through a receiver (`self.`, `this.`, a Go method receiver) | B1.8 / R10 |
| B3.1t | the nesting surcharge on a nested ternary | B3.1 / R1 |
| ARROW | the nesting policy for a top-level arrow function bound to a `const` | B2.6 / R12 |
| C | the stated totals of the Appendix C examples (C.1-C.4) | section 3 below |
| COMP | comprehensions and generator expressions | not mentioned by the specification (item 13) |
| ELSE-LOOP | `else` attached to a loop or to `try` (Python) | not mentioned by the specification (item 12) |
| GO-ERRNIL | Go `if err != nil` error checks | no compensating usage exists for Go in Appendix A (unnumbered note at the end of section 7) |

## 3. Appendix C examples and their stated totals

Appendix C prints four real-world methods with per-line annotations and a stated total. The
code is the appendix's own material and is not reproduced here; what the study needs is the
total and the increment sequence that produces it, both recorded below. The arithmetic was
re-checked against the annotations during transcription. The study's executable equivalents
are in `experiments/microcorpus/` (cases `java-C1`, `java-C2`, `java-C3`, `js-C4`).

| # | Method, source | Stated total | Increment sequence (checked) |
|---|---|---|---|
| C.1 | `overriddenSymbolFrom`, `org.sonar.java.resolve.JavaSymbol` (SonarJava) | 19 | 1 + 1 + 2 + 1 + 3 + 4 + 5 + 1 + 1 = 19 |
| C.2 | `addVersion`, `com.persistit.TimelyResource` (sonar-persistit) | 35 | 1 + 2 + 3 + 3 + 4 + 5 + 5 + 1 + 2 + 3 + 1 + 3 + 2 = 35 |
| C.3 | `toRegexp`, `org.sonar.api.utils.WildcardPattern` (SonarQube) | 20 | 1 + 1 + 1 + 2 + 1 + 3 + 1 + 4 + 1 + 1 + 1 + 1 + 1 + 1 = 20 |
| C.4 | `save`, `model.js` (YUI) | 20 | 1 + 1 + 2 + 1 + 2 + 3 + 1 + 4 + 4 + 1 = 20 |

What each example settles, and where its annotations had to be reconstructed (author's
analysis):

- **C.1** - a five-deep `if`/`for`/`if`/`if`/`if` chain whose surcharges run +1, +2, +3, +4,
  +5, and an `else if` inside it charged a flat +1 at the same depth as its leading `if`.
  Confirms the reading of R2 used in item 1 below.
- **C.2** - `synchronized` and `try` add nothing and do not deepen nesting; an unlabelled
  `break` adds nothing; a `try` nested inside a `catch` keeps its contents at the `catch`'s
  depth (an `if` there is charged +3 at nesting 2). The multi-operator conditions inside the
  loop each add a flat +1 for the operator change.
- **C.3** - in the PDF the four annotations `+2 (nesting = 1)`, `+1`, `+3 (nesting = 2)`,
  `+1` are printed as a block beside the wrong lines; the attachment recorded above is the
  only one that reproduces the stated total of 20. This example also shows a top-level `||`
  and a top-level ternary each charged at nesting 0 even though the ternary contains the
  `||` - the `||` is a fundamental increment and never takes a surcharge.
- **C.4** - in the `-layout` extraction the `+2 (nesting = 1)` for the callback's `if` is
  printed on the preceding line; the raw-order extraction confirms the attachment above. Two
  things follow: the `||` used as a default-value idiom is charged +1 (the basis of code
  B1.7idiom), and a first-level nested function deepens the enclosing method's nesting,
  because `save` has a top-level structural increment and so is not exempt under A.2.

Further totals stated in the body text and in Appendix A, all used as expected values:
`sumOfPrimes` = 7 (p. 10: outer labelled `for` +1, inner `for` +2, `if` +3, `continue OUT`
+1) and `getWords` = 1 (p. 10: a single `switch`); `myMethod` = 9, `myMethod2` = 2 and the
`#if DEBUG` variant = 4 (§2.9, tabulated above); Appendix A's JavaScript declarative example
= 1 and non-declarative = 3; Appendix A's Python `a_decorator` = 1, `not_a_decorator` = 2,
`decorator_generator` = 1.

## 4. Version history relevant to this study (change log, p. 21)

The white paper carries a change log covering versions 1.1 through 1.7. It is not reproduced
here; what matters for the study is which versions changed the *metric* rather than the
prose. In summary: the hybrid increment type and the `else` / `else if` treatment, indirect
recursion, and Appendix A were introduced at 1.1 (which also states that the metric is
concerned only with binary boolean operators); Appendices B and C were added at 1.2; the
Python decorator exception at 1.3; a clarification of which nested methods deepen the nesting
level at 1.4; and an explicit statement that all multi-level `break`/`continue` forms take a
fundamental increment at 1.5. Versions 1.6 and 1.7 are cosmetic (an author-title removal, and
branding and layout changes).

Consequences recorded for the study: the normative rules have not changed since version 1.5
(5 April 2021), so the analysed edition 1.7 is rule-identical to every release the tools
under study could have been written against since 2021; and there is no version 1.0 entry -
the log was initiated at 1.1.

## 5. Language-specific notes

### 5.1 From the white paper

- COBOL: `ELSE` immediately followed by `IF` is treated as `else if` (no increment for the `ELSE`, no nesting penalty for the `IF`). (Appendix A.1)
- JavaScript: an outer function used purely declaratively (only declarations at its top level) is ignored and does not raise the nesting level of its inner functions; if it has any top-level structural increment it gets standard treatment. (Appendix A.2)
- Python: a function containing only a nested function and a `return` statement (a decorator) does not raise the nesting level of the nested function. (Appendix A.3)
- C/C++ preprocessor: `#if`, `#ifdef` are listed among conditionals that receive a structural increment (section 2.3) and can nest a method (section 2.9 example).
- Java 7 multi-catch: one increment per `catch` clause regardless of the number of types (section 2.4, Appendix A).
- `break NUMBER` / `continue NUMBER` (PHP-style multi-level jumps) receive a fundamental increment (B1.6, change log 1.5).

### 5.2 From RSPEC-3776 as bundled in the plugins

The rule description shipped with the plugins (Java and Python copies are identical in the
core text; JS ships no `.html`, but its `S3776.json` carries the same title and metadata) is
a short user-facing summary rather than a specification. Paraphrased: the rule fires when a
function's cognitive complexity exceeds a threshold; complexity is described as a measure of
how hard the control flow is to understand, with three headline ideas - each break in linear
reading flow increments (loops, conditionals, catches, switches, jumps to labels, conditions
mixing operators), each nesting level increases complexity, and ordinary method calls are
free *except* recursive ones. The description defers to the white paper for the actual
computation.

Metadata (all three plugins): type `CODE_SMELL`, impact `MAINTAINABILITY: HIGH`, attribute
`FOCUSED`, default severity `Critical`, tag `brain-overload` (JS adds
`editable-source`), remediation "Linear with offset", 5min offset + 1min "per complexity
point over the threshold", quickfix `infeasible`. Titles: Java "Cognitive Complexity of
methods should not be too high"; Python and JS "Cognitive Complexity of functions should
not be too high". Scope: Java `Main`, JS `Main`, Python `All`. Note that nothing in the
metadata gives the rule gate semantics.

Java-only exception, paraphrased from the rule's *Exceptions* paragraph: `equals` and
`hashCode` are not reported, on the ground that they are often generated and end up hard to
read in classes with many fields. This exclusion is a rule-level filter; the metric still
computes a value for those methods.

Java rule-page worked examples (stated values only): `calculateFinalPrice` noncompliant = 3
(`+1 (if)`, `+1 (more than one condition)`, `+1 (change of operator in condition)`),
compliant = 1; `calculateTotal` two `for` loops = 2, refactored = 0; `calculateDiscount`
= 6 (`+1 (if)`, `+2 (nested if)`, `+1 (else)` x3), refactored = 3.

Python rule-page worked examples (stated values only): `process_eligible_users` = 5
(`+1 (for)`, `+1 (if) +1 (nested) +1 (multiple conditions)`, `+1 (mixed operator)`),
refactored = 3 (+ `is_eligible_user` = 2); `process_user` = 8, refactored = 2 (+2 +2);
`calculate` = 6 (`+1 (if)`, `+1 (for) +1 (nested)`, `+1 (if) +2 (nested)`), refactored = 4.

Python check-level exclusions (from `CognitiveComplexityFunctionCheck.java`): inner
functions (any `FunctionDef` with a `FunctionDef` ancestor) are not reported separately
(their complexity is folded into the outermost function); files detected as generated
(`GeneratedFileUtils.isGeneratedFileForReadabilityRules`) are skipped.

JS check-level options (`meta.ts`, `config.ts`): `[threshold: integer >= 0, 'silence-issues']`;
`silence-issues` computes the file metric without reporting.

## 6. Construct -> increment -> nesting, as implemented by Sonar

Legend: `S` = structural (+1 + current nesting), `H` = hybrid (+1, no nesting), `F` =
fundamental (+1), `0` = no increment. "Raises nesting" says whether the construct's body
is visited at nesting+1. Provenance: `spec` = stated in the white paper; `impl` =
derived from the fetched implementation source and, where noted, confirmed by a
fixture; `impl (inferred)` = follows from the source but no fixture exercises it.

### 6.1 Java (`CognitiveComplexityVisitor.java`, sonar-java)

| Construct | Increment | Raises nesting | Provenance / evidence |
|---|---|---|---|
| `if` | S, at `if` keyword | then-branch yes; condition visited at outer nesting | spec; impl `visitIfStatement` |
| `else` (non-`if`) | H, at `else` keyword | else-branch yes | spec; impl |
| `else if` | H (+1): visitor lets the nested `if` add `nesting` then subtracts `nesting-1` (`ignoreNesting` flag) | its then-branch visited at the *same* nesting as the parent `if`'s then-branch | spec; impl; fixture `noNestingForIfElseIf` = 21 |
| `?:` conditional expression | S, at `?` token | yes, for condition, true and false operands alike | impl (condition nested is impl choice); fixture `ternaryOp` = 2 |
| `switch` statement | S, at `switch` keyword, once | yes (all cases) | spec; impl; fixture `toProtocolType` = 1, `switch2` = 12 |
| `switch` *expression* (Java 14) | not handled by `visitSwitchStatement`; `BaseTreeVisitor.visitSwitchExpression` is not overridden | - | impl (inferred): likely 0 and no nesting; unverified |
| `for`, foreach | S, at `for` keyword | yes, including init/condition/update expressions | spec; impl |
| `while` | S, at `while` keyword | yes, including condition | spec; impl |
| `do ... while` | S, at `do` keyword | yes, including condition | spec; impl |
| `catch` | S per clause, at `catch` keyword; multi-catch counts once | yes | spec; impl; fixture `doFilter` (two catches = 2) |
| `try` body, resources, `finally` | 0 | no (visited at outer nesting) | spec; impl; fixture `bulkActivate` = 6 |
| `synchronized` | 0 | no | spec example C.2 |
| `break LABEL`, `continue LABEL` | F, at keyword | no | spec; impl; fixture `breakWithLabel` = 2, `sumOfNonPrimes` = 9 |
| unlabeled `break`/`continue`, `return`, `throw` | 0 | no | spec; impl |
| `&&` / `\|\|` sequences (`CONDITIONAL_AND`/`CONDITIONAL_OR` only) | F, +1 at the first operator of each run of like operators; the whole tree is flattened **through parentheses** (`ExpressionUtils.skipParentheses`) | no | spec; impl; fixtures `extraConditions2` `a && (b \|\| c) \|\| d` = 2, `extraCondition11` `a \|\| (b \|\| c)` = 1, `extraConditions12` = 7 ("parentheses completely ignored") |
| `&`, `\|`, `^` on booleans, `!` | 0 | no | impl (inferred): only `CONDITIONAL_AND/OR` kinds tested |
| lambda | 0 | yes (`visitLambdaExpression` nesting++) | spec B2.6; impl; fixture `main` = 4 |
| anonymous class / local class body | 0 | yes (`visitClass` nesting++); its methods are *not* analysed separately (`memberOfAnonymousClass`, `isWithinLocalClass`) and are folded into the enclosing method | impl; fixtures `main` = 4, `localClasses` = 3 |
| method / constructor (top-level) | 0 | no; each method's count starts at `nesting = 1` internally (i.e. first structural increment = +1) | spec; impl |
| initializer / static initializer blocks | counted for file-level metric only | - | impl `compilationUnitComplexity` |
| recursion | 0 (not implemented; fixture comment `// TODO find recursion`) | - | impl; contradicts spec B1.8 |
| `equals`, `hashCode` | excluded from the S3776 rule, not from the metric | - | impl `isExcluded` |
| `?.`/null-coalescing | n/a in Java | | |

### 6.2 Python (`CognitiveComplexityVisitor.java`, sonar-python)

Nesting in Python is tracked per *statement list*: every `StatementList` whose parent is
not one of `TRY_STMT` (the `try:` body), `FINALLY_CLAUSE`, `CLASSDEF`, `FUNCDEF`,
`WITH_STMT`, or the file itself raises the nesting level by one while it is visited.

| Construct | Increment | Raises nesting | Provenance / evidence |
|---|---|---|---|
| `if` | S, at `if` keyword | body yes | spec; impl; fixture `if_nested` = 6 |
| `elif` | H (+1) | body yes, at the *same* level as the `if` body | spec; impl; fixture `elif_nesting` = 4 |
| `else` of `if` | H (+1) | body yes | spec; impl; fixture `else_nesting` = 4 |
| `else` of `for` / `while` | H (+1) | body yes | impl `visitElseClause`; fixtures `for_with_else_complexity` = 4, `while_with_else_complexity` = 4 |
| `else` of `try` | H (+1) | body yes | impl; fixture `try_else` = 4 |
| `while` | S | body yes; condition not nested | spec; impl |
| `for` / `async for` | S | body yes | spec; impl |
| `except` clause | S per clause (tuple of types counts once) | body yes | spec; impl; fixture `try_except` = 11 |
| `try:` body, `finally:` | 0 | no | spec; impl; fixture `try_finally` = 2 |
| `with` / `async with` | 0 | no | impl `WITH_STMT` in exclusion list |
| conditional expression `x if c else y` | S, at `if` keyword | yes, for the whole expression including its condition | impl; fixtures `nested_conditional_expression_false/true` = 3 each |
| `and` / `or` sequences | F, +1 per run of like operators; the tree is flattened through nested `AND`/`OR` nodes **but not through parentheses** (a `ParenthesizedExpression` node is neither `AND` nor `OR`, so a parenthesised sub-expression is visited as a separate sequence) | no | spec; impl; fixture `and_or` = 7. Parentheses behaviour: impl (inferred), e.g. `a and (b or c) or d` -> 3 (Java gives 2) |
| `not` | 0 | no | impl (inferred): unary, no handler |
| `match` / `case` (3.10) | 0 (no handler for `MATCH_STMT`) | case-block bodies **do** raise nesting (their statement list parent `CASE_BLOCK` is not in the exclusion list) | impl (inferred); unverified by fixture |
| comprehension `for` / `if`, generator expressions | 0 | no | impl (inferred): no handler |
| `lambda` | 0 | no (`LAMBDA` is not `FUNCDEF`) | impl (inferred) |
| walrus `:=` | 0 | no | impl (inferred) |
| `break` / `continue` / `return` / `raise` | 0 (Python has no labels) | no | impl; fixture `jump_statements` = 6 |
| nested `def` | 0 | yes: level = parent level + 1 when the parent is a function, **except** when the parent function is a "wrapper" (all its other statements are `return NAME`), in which case level = parent level; the nested function's increments are folded into the outermost function's total | spec A.3, B2.6; impl `NestingLevel`; fixtures `nesting_func` = 3, `decorator_func` = 1, `complex_decorator_func` = 3, `not_complex` = 0 |
| nested `class` | 0 | resets nesting level to 0 for its methods | impl; fixture `function_with_nested_class` = 4 (method inside nested class: `+1`, not `+2`) |
| module-level statements | counted in file metric only | | impl; fixture trailing `if/elif/else` |
| recursion | 0 (fixture comment `# TODO recursion +1`) | | impl; contradicts spec B1.8 |
| decorated function (`@deco def f`) | no special handling; only the *wrapper* pattern above | | impl |

### 6.3 JavaScript / TypeScript (`rule.ts`, SonarJS)

Nesting in JS is tracked per *node*: the rule registers specific child nodes
(`consequent`, `alternate`, loop `body`, each `SwitchCase`, `CatchClause.body`, ternary
`consequent`/`alternate`, and third-level-or-deeper functions) in `nestingNodes`; the
counter increments on entering and decrements on leaving each such node. Conditions and
loop headers are therefore never nested.

| Construct | Increment | Raises nesting | Provenance / evidence |
|---|---|---|---|
| `if` | S at `if` token | `consequent` yes | spec; impl |
| `else` (non-`if`) | H (+1) at `else` token | `alternate` yes | spec; impl; unit test `check_secondaries` |
| `else if` | H (+1): an `IfStatement` that is its parent's `alternate` calls `addComplexity` instead of `addStructuralComplexity` | its `consequent` yes, at the parent's level | spec; impl |
| `for`, `for...in`, `for...of`, `while`, `do...while` | S at first token | `body` yes | spec; impl |
| `switch` | S at `switch` token, once | every `SwitchCase` yes | spec; impl |
| `catch` | S at `catch` token | `body` yes | spec; impl |
| `try`, `finally` | 0 | no | spec; impl (no handler) |
| `?:` | S at `?` token | `consequent` and `alternate` yes; `test` **not** nested | impl; unit test `nested_conditional_expression` (+3, +3, +5) |
| `break LABEL`, `continue LABEL` | F at keyword | no | spec; impl; unit test |
| `&&` | F: +1 for the first `&&` of each run (`previous?.operator !== current.operator`) | no | spec; impl |
| `\|\|` | **0, never counted** (`current.operator !== '\|\|'` guard) | no | impl; unit tests: `foo(1 \|\| 2 \|\| 3 \|\| 4)` no increment, `const x = a \|\| []` valid at threshold 0, `foo(1 && 2 \|\| 3 && 4) // +2`. **Contradicts spec section 2.6 and Appendix C.4 (the `options \|\| (options = {})` line is charged +1).** |
| `??` | 0 | no | spec R13; impl guard `!== '??'`; unit test `c ?? ''` = 0 |
| `?.` optional chaining | 0 | no | spec R13; impl (no handler); unit test `obj.title?.text` = 0 |
| parentheses | transparent (ESTree has no parenthesised-expression node); `foo((1 && 2) && (3 && 4)) // +1` | | impl; unit test `and_or` |
| `!` | 0; `foo(1 && 2 && !(3 && 4)) // +2` (two `&&` sequences) | | impl; unit test |
| JSX short-circuit `{ a && b && <el/> }` inside a `JSXExpressionContainer` | 0 when the whole expression is a single-operator chain with no conditional; otherwise normal rules (`{ a && (b \|\| c) }` -> +1 for `&&`, 0 for `\|\|`; `{ a && (b ? x : y) }` -> +1 `&&`, +1 `?`) | | impl `getJsxShortCircuitNodes`; unit tests |
| function-like (declaration, expression, arrow, method, getter/setter, constructor, class method) | 0 | see below | spec; impl `:function` |
| nesting of functions, **file metric**: first-level function | no | inner ("second-level") functions get +1 nesting *only if* the enclosing top-level function has at least one structural increment (`topLevelHasStructuralComplexity`) **and** is not a React functional component (name starts with a capital letter and top-level `return` of `JSXElement`/`JSXFragment`) | spec A.2; impl; unit tests `nesting_func_*`, `Welcome` |
| nesting of functions, **file metric**: third-level and deeper functions | no | always +1 nesting | impl `onEnterFunction` |
| nesting of functions, **per-function issue** (`functionOwnComplexity` / `functionOwnControlFlowNesting`) | each function is reported with its *own* complexity: control-flow nesting counted from 0 at the function boundary, enclosing functions' nesting ignored, nested functions' increments **excluded** from the enclosing function's count | | impl; unit tests `nesting_func_with_complexity` (outer 1, inner 1), `two_level_function_nesting` (`nested2` = 1). **Diverges from spec B2.6 and from Java/Python, which fold nested lambdas/defs into the enclosing method.** |
| `class` (declaration/expression) | 0 | no effect on nesting (only functions and control flow raise it) | impl; unit test `class B {}` inside `if` |
| module-level statements | counted in file metric only (`fileComplexity`) | | impl |
| recursion | 0 (no handler) | | impl; contradicts spec B1.8 |
| labels without `break`/`continue`, `throw`, `return`, `await`, `yield` | 0 | | impl (no handler) |

### 6.4 Cross-language divergence summary (implementation-derived)

| Question | Java | Python | JS/TS | Spec |
|---|---|---|---|---|
| `a \|\| b` | +1 | +1 | 0 | +1 |
| `a && (b \|\| c) \|\| d` | 2 | 3 (inferred) | 1 (`\|\|` free) | 2 |
| ternary condition nested? | yes | yes | no | unspecified |
| loop condition nested? | yes (`for`/`while`/`do`) | no | no | unspecified |
| `if` condition nested? | no | no | no | unspecified |
| nested function raises nesting? | lambda yes, local/anonymous class yes | `def` yes (wrapper exception), `class` resets to 0, `lambda` no | second-level: conditional (A.2 + React); third-level+: yes; ignored for per-function issue | yes (B2.6) |
| nested function's increments folded into outer? | yes | yes | no (file metric: yes) | implied yes |
| recursion | no | no | no | +1 per method in cycle |
| `switch` cases raise nesting? | yes (whole switch) | n/a (`match` not handled) | yes (per case) | yes |
| labelled jump | +1 | n/a | +1 | +1 |
| `try`/`finally` | 0, no nesting | 0, no nesting | 0, no nesting | 0 |
| loop/try `else` (Python) | n/a | +1, nests | n/a | unspecified |

(No equivalent source-level table was produced for sonar-go: Go behaviour enters this study
only through the observed runs recorded in `experiments/microcorpus/expected.csv`, whose
`origin` column marks the `GO-ERRNIL` cases as real-code-derived post hoc on 2026-09-17.)

## 7. Ambiguities and open questions

Numbered for citation; the numbering is referenced from `experiments/microcorpus/expected.csv`
and must not be renumbered. "Spec" refers to the white paper v1.7.

1. **`else if` hybrid increment vs. nesting of its body.** B2.1 lists `else if` as raising the nesting level, and section 2.3 says the hybrid increment carries no nesting increment. The spec does not say whether the body of an `else if` sits at the same depth as the body of the leading `if` (all three implementations: yes) or one deeper, nor how a chain `if / else if / else if / else` of length n is charged (all three: +1 for the `if` plus +1 per `else if`/`else`, all at the `if`'s nesting). C.3 confirms this reading (its `else if (ch == '*')` is charged a flat +1 while sitting at nesting 1).
2. **Else-nested-if (non-COBOL).** `else { if ... }` is +1 for `else` and +(1+nesting+1) for the inner `if` in all three implementations (Java fixture `noNestingForIfElseIf`: `+5 (nesting=4)` under an `else` at nesting 3; Python `else_nesting` = 4). The spec only spells this out for COBOL via the exception, leaving the general case to inference.
3. **Ternary nesting scope.** B2.1/B3.1 make the ternary a nesting structure but do not say which operands are nested. Java and Python nest the whole expression (condition included); JS nests only the two result operands. `c1 ? (c2 ? a : b) : d` is +1 +2 = 3 everywhere, but `(c1 ? a : b) ? c : d` would be 3 in Java/Python and 2 in JS. C.3's top-level `... || ... ? 1 : 0` does not disambiguate, because the `||` is a fundamental increment and never nests.
4. **Ternary inside `if` condition vs. inside loop header.** Java nests the loop header (`for`/`while`/`do` call `super.visitX` after `nesting++`) but not the `if` condition (`scan(tree.condition())` before `nesting++`). A ternary in a `while` condition therefore costs +2 at top level in Java and +1 in Python/JS. Spec silent.
5. **Lambda / nested-function nesting.** Spec B2.6 and section 2.9 say nested methods and lambdas raise the nesting level, and the C.4 example charges nested callbacks accordingly. JS applies this only to the *file* metric (with the Appendix A.2 declarative exemption and a React-component exemption that is not in the spec) and reports each function with nesting reset to 0 and nested functions excluded. Java and Python fold nested bodies into the outermost method. So the same code yields different S3776 values per language, and for JS the per-function number is not the spec's number.
6. **Wrapper/decorator exception scope.** Appendix A.3 restricts the exception to a function holding "only a nested function and a return statement". sonar-python's `isWrapperFunction` requires every statement other than the nested `def` to be `return NAME` (any single bare name, not necessarily the nested function; multiple such returns permitted; a docstring statement would break it). Whether a decorator that also assigns `functools.wraps` or contains a docstring qualifies is undefined in the spec and rejected by the implementation.
7. **Sequences of logical operators and negation.** The spec's second annotated example - an `&&` joining an operand to a negated parenthesised `&&`, charged +2 for the condition - implies that negation (and the parentheses it requires) starts a new sequence; section 2.6 restricts counting to *binary* operators. But the spec does not say whether parentheses *without* negation break a sequence: `a && (b && c)`. Java and JS treat parentheses as transparent (+1); sonar-python (inferred from the `flattenOperators` kinds) would give +2. Java's fixture comment says "parentheses completely ignored"; the spec's negated example is consistent with either reading only because the `!` intervenes. The same silence covers non-short-circuit `&`/`|` on booleans (code B1.7bit).
8. **`||` in JS.** SonarJS never increments for `||` (nor `??`), presumably to spare the `x = x || default` idiom, but the exemption applies to every `||`, including `if (a || b)` and mixed `a && b || c && d` (JS: 2, spec: 3). The white paper's own JS example (C.4) charges the default-value `||` +1. Undocumented in the rule description.
9. **Mixed-operator counting rule.** The spec's "increments for each new sequence of like operators" (§2.6) is implemented as +1 at each operator whose kind differs from the previous operator in a left-to-right flattening of the tree, ignoring precedence. So `a || b && c || d` = 3 (`||`, `&&`, `||`) even though `b && c` is one sub-expression and the two `||` belong to one precedence level; a precedence-aware reading (`||` sequence + one `&&` sequence = 2) is also defensible from the prose. Java fixture `extraConditions5` `a || b && c || d && e` = 5 confirms the token-order reading.
10. **`switch` / `match`.** B1.2 gives `switch` a single structural increment; Java switch *expressions* (arrow form, Java 14) are not handled by the Java visitor (inferred), and Python `match` receives no increment at all while its case bodies raise nesting (inferred). Whether pattern-matching constructs are "switch" for the spec is unstated - the Appendix B preamble's atypical-spelling clause argues yes, the absence of any mention argues no. Also unstated: whether guard conditions in `case` labels (`case X when a && b`) count as logical sequences (they would, mechanically, in all three).
11. **Labelled `break`/`continue`.** Only jumps *to a label* count (B1.6). A label that is never jumped to, a labelled `break` that targets the immediately enclosing loop (semantically an unlabeled break), and `break` inside `switch` all cost 0. Whether a labelled `continue` to the immediately enclosing loop should count is not discussed; implementations count any labelled jump.
12. **`try`/`catch`/`finally`.** `try` and `finally` are "ignored altogether" (§2.4) and do not raise nesting; but the spec does not say whether statements inside the `try` body of a nested `try` inside a `catch` are at the `catch`'s nesting (yes, in all three: C.2 places an `if` inside a `try` inside a `catch` at `+3 (nesting = 2)`). Python-specific `try ... else:` and loop `else:` are not in the spec; sonar-python charges them as hybrid increments that raise nesting (code ELSE-LOOP).
13. **Comprehensions, generator expressions, `filter`/`map` callbacks.** Spec is silent (code COMP). Python comprehension `for`/`if` are 0 in sonar-python, although they are loops/conditionals in the spec's sense; a comprehension rewritten as a `for`+`if` costs +3 (nested). Boolean operators inside comprehensions are still charged. JS `.map(x => ...)` callbacks are arrow functions and follow the function-nesting rules of item 5.
14. **Walrus `:=`, assignment expressions, `await`, `yield`.** Not mentioned; 0 everywhere.
15. **Optional chaining and nullish coalescing.** Section 2.2 exempts "null-coalescing operators" but illustrates the rule with a null-*conditional* operator (`?.`). Implementations ignore both `?.` and `??` (JS). Whether `a ?? b ?? c` "sequences", or whether a mixed `a ?? b || c` counts as an operator change, is moot in JS because `??` and `||` are both free; in languages that do count `||` (C#, Kotlin `?:`) the interaction is unspecified.
16. **Recursion detection.** B1.8 charges one increment for "each method in a recursion cycle, whether direct or indirect" (§2.7), which needs call-graph analysis. None of the three implementations does it (Java and Python fixtures carry explicit TODOs). The spec does not define what a "cycle" is across overloads, virtual dispatch, higher-order calls, or mutual recursion across files, nor whether the increment is per method or per call site - the study reads it as per method (codes B1.8d2, B1.8i).
17. **Nesting of the `else` body, the C.4 pattern.** In C.4 an `else` at `nesting = 2` costs +1 while the `if`s inside it cost `+4 (nesting = 3)`, so the `else` raises nesting (B2.1) yet its body sits at the same level as the body of the `if` it belongs to (both +4). Consistent, but it means "increments the nesting level" in B2 must be read as "its body is one level deeper than the statement", not "one deeper than the sibling branch".
18. **Method-like structures at the top level.** Java starts each method at internal `nesting = 1` (so the first structural increment is +1); JS counts module-level control flow into a file metric with nesting from 0; Python counts module-level statements likewise. The spec says top-level methods are ignored and does not define a value for code outside any method.
19. **Anonymous/local classes.** Java raises nesting for any class body (including anonymous class methods, which are folded into the enclosing method); Python *resets* nesting for a nested class; JS ignores classes for nesting. Spec: not mentioned - B2.6 covers only "methods and method-like structures".
20. **Preprocessor conditionals.** `#if`/`#ifdef` are structural increments that can nest a whole method (the section 2.9 example totals 4 on that basis). The spec does not say how `#elif`/`#else` (hybrid?) or unbalanced conditionals across method boundaries are handled; only relevant for C/C++/C#.
21. **Secondary-location messages** differ (`+2 (incl 1 for nesting)` in Java/Python, `+2 (incl. 1 for nesting)` in JS); Python's logical-operator secondaries all point at the *root* operator token rather than each sequence start (`incrementWithoutNesting(pyBinaryExpressionTree.operator())` inside the loop). Cosmetic, but it means Python's secondary locations cannot be used to reconstruct per-operator attribution.
22. **`equals`/`hashCode` exclusion (Java)** is a rule-level exception not present in the spec; the metric still counts them.
23. **Generated files (Python)** are skipped at rule level; unspecified in the spec.

Recorded alongside the catalogue, not numbered because it emerged after the fact: Appendix A
lists no compensating usage for Go, yet sonar-go was observed to ignore `if <error> != nil`
without an `else` (code GO-ERRNIL, cases `go-c98`-`go-c102`, marked real-code-derived in
`expected.csv`). By the text of Appendix A such an exception would have to be an explicit
addition; none is published.

## 8. Counts

- White paper: version 1.7, 29 August 2023; 22 pages; change log covers 1.1-1.7 (7 entries, 20 bullet items).
- Appendix B: 3 lists (B1 increments: 8 items; B2 nesting level: 6 items; B3 nesting increments: 5 items) = 19 bullet rules; consolidated into 15 rules R1-R15 above.
- Appendix C: 4 examples (19, 35, 20, 20); plus 8 further annotated examples with stated totals in the body and Appendix A.
- Implementation tables: Java 23 rows, Python 23 rows, JS/TS 24 rows, cross-language summary 12 rows (recounted 2026-09-18 from the tables in section 6; an earlier count of 21/22/22 was wrong and is corrected here).
- Ambiguities listed: 23.
