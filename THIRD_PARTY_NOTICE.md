# Third-party materials in this replication package

`LICENSE` grants MIT for the author's own code and CC BY 4.0 for the author's own data and figures.
**Neither grant reaches the third-party material enumerated on this page.** Each item below states
what it is, where it sits, who holds the rights, on what basis it is included, and what a re-user
must do. Where a file mixes the author's work with third-party material, the item says which part is
which.

This notice describes the files in this repository; `ARTIFACT_MANIFEST.json` lists every one of them
with its SHA-256. The repository is a subset of the replication package that the study's exporter
(`scripts/export_public_artifact.py`, not included here) produced; items that the exporter published
but this repository leaves out are marked "not included" below. Section 9 records how the list below
was checked against the tree, and section 10 records what is still unresolved. Where something could
not be verified from this repository's own records, this notice says so instead of guessing.

---

## 1. Measurements about 32 third-party repositories — no source code

**What.** Per-function Cognitive Complexity and cyclomatic values, plus the syntactic facts needed to
interpret them: repository name, pinned commit SHA, repository-relative file path, function name and
qualified name, declaration/body/end line numbers, nesting depth, construct counts, and each tool's
number for that function. Also SonarQube's per-issue increment lists.

**Where.**

* `results/raw/<lang>/<owner>__<repo>/sonar.scanner.log` — the SonarScanner log of each of the 32
  repositories. The other raw outputs per repository (`units.json`, `run_meta.json`, `sonar.json`,
  `sonar_files.json` and one JSON per metric tool) are not included in this release; see `README.md`.
* `results/processed/functions/<lang>__<owner>__<repo>.csv` — 32 per-repository function tables.
* `results/processed/*.csv` — aggregates: `agreement_*`, `flips_*`, `attribution_*`, `coverage_*`,
  `container_*`, `cyclomatic_*`, `audit_<lang>.csv`, `audit_verdicts.csv`, `audit_vs_classifier.csv`.
* `data/repos/manifest.csv`, `data/repos/LICENSES.md`, `data/repos/selection_<lang>.json`.

**Rights.** Each subject repository's own copyright holders. Function names and file paths are theirs;
the measurements are this study's.

**Basis for inclusion.** These are facts *about* the code, not the code. No source line, statement or
expression body from any subject repository is reproduced anywhere in the package. The four files
that did contain verbatim source — `results/processed/audit_<lang>_snippets.txt`, which the
pre-publication review found to hold 2,988 lines from 27 of the 32 repositories — are not
included. The audit remains reproducible from the published
`audit_<lang>.csv` rows (repo, file, `decl_line`, function) plus the pinned SHAs in
`data/repos/manifest.csv`.

**What a re-user must do.** Nothing to reuse the measurements under CC BY 4.0. To re-obtain the code
the measurements describe, clone each repository at its pinned SHA and comply with *that repository's*
licence. `data/repos/LICENSES.md` and the `license_spdx` / `license_file` / `license_note` columns of
`data/repos/manifest.csv` record the licence read out of each clone at its pinned commit on
2026-09-18 — not the GitHub API `license` field, which reports `NOASSERTION` for five of the 32.
Terms that materially restrict reuse, as recorded there:

| Repository | Recorded SPDX id | Consequence recorded in `LICENSES.md` |
| --- | --- | --- |
| `krahets/hello-algo` | `CC-BY-NC-SA-4.0` | Commercial use prohibited; share-alike |
| `open-webui/open-webui` | `LicenseRef-OpenWebUI` | Bespoke source-available licence, not OSI-approved; branding clause |
| `JuliusBrussee/caveman` | `MIT AND BUSL-1.1` | Engine-linked directories are Business Source License 1.1, not open source, until 2030-06-21 |
| `termux/termux-app` | `GPL-3.0-only` | Copyleft; documented Apache-2.0 / MIT / GPL-2.0-with-classpath-exception carve-outs |
| `AUTOMATIC1111/stable-diffusion-webui`, `firecrawl/firecrawl`, `immich-app/immich` | `AGPL-3.0-only` | Network copyleft |
| `syncthing/syncthing` | `MPL-2.0` | File-level copyleft |
| `gohugoio/hugo` | `Apache-2.0` | Code Apache-2.0, but the `docs/` theme carries no open-source licence and is not redistributable |

The remaining 23 repositories are recorded as MIT, Apache-2.0, BSD-3-Clause or Unlicense. Those
columns are informational; the repository's own licence file at the pinned SHA governs.

## 2. Analyzer output strings emitted by SonarSource software

**What.** Short strings produced by SonarQube Community Build 26.9.0.129388 and its bundled analyzers
during the author's own scans: issue messages of the form `Refactor this method to reduce its
Cognitive Complexity from N to the 0 allowed.`, secondary-location labels such as `+1` and
`+2 (incl 1 for nesting)`, and SonarScanner CLI progress logs.

**Where.** The `message` and `increments` fields of `results/raw/microcorpus/sonar_*.json`; the
scanner logs `results/raw/<lang>/<owner>__<repo>/sonar.scanner.log` and
`results/raw/microcorpus/sonar_*.scanner.log`.

**Rights.** SonarSource S.A.

**Basis for inclusion.** They are the machine-readable measurement this study set out to record, and
they are functional strings of a few words. No rule documentation is included: the scraped RSPEC-3776
descriptions (`references/spec/s3776_rule_descriptions_from_server.json`, 27 KB of rule prose with
SonarSource's own worked examples) are **not** included.

**What a re-user must do.** Nothing, beyond not presenting the strings as their own. Re-generating
them needs a locally run SonarQube; see `reproduction/README.md`, `scripts/sonar_setup.py` and
`scripts/sonar_scan.py`.

## 3. Short quotations from the SonarSource Cognitive Complexity white paper and RSPEC-3776

**What.** `references/spec/cognitive_complexity_spec_rules.md` is the study's rule digest: a
paraphrase of the specification in the author's own words, with a page or section citation for every
claim, plus the author's own consolidated `R1`–`R15` table, rule-code index, implementation-behaviour
tables (sections 6), ambiguity catalogue (section 7) and counts (section 8). A small number of short
quoted phrases remain where the exact wording is what fixes an expected value in
`experiments/microcorpus/expected.csv`. Section 5.2 does the same for the RSPEC-3776 rule description
bundled in the sonar-java and sonar-python plugins: paraphrase, metadata field values, and the
*stated totals* of the rule pages' worked examples with their short increment labels
(`+1 (if)`, `+2 (nested if)`, …).

**Extent, measured on the file as shipped** (568 lines, 51,835 bytes, SHA-256
`62165459e3cd45cc53d95b84e796a89d5f1775e0c973a8664937ce1e4132f696`): no blockquoted lines and no
fenced code blocks at all; 24 quoted spans of two words or more, 122 words in total out of the file's
8,456, the longest being 10 words ("each method in a recursion cycle, whether direct or indirect").
No appendix, no change-log entry and no worked-example source listing is reproduced. The file says so
itself in its opening paragraphs and states that it "is **not** the specification and is not a
substitute for it".

**Rights.** SonarSource S.A. for the quoted phrases and for the specification they come from. The
file records the source's terms in its section 0: `Copyright SonarSource S.A., 2023, Switzerland. All
content is copyright protected`, together with the source URL and the PDF's SHA-256.

**Basis for inclusion.** Short quotation for research and criticism. The study's method is to
adjudicate tool behaviour against the wording of particular clauses, so those clauses have to be
quotable and citable. **The quoted phrases are outside the MIT and CC BY 4.0 grants in `LICENSE`;**
the surrounding paraphrase, tables and findings are the author's own and are CC BY 4.0.

**What a re-user must do.** Treat every quoted phrase as SonarSource's and keep its attribution.
Obtain the authoritative document from <https://www.sonarsource.com/docs/CognitiveComplexity.pdf> and
check it against the SHA-256 in section 0 of the digest; the PDF itself is not redistributed. Anyone
who wants to *apply* the metric must read the white paper, not this digest.

## 4. Micro-corpus cases derived from the white paper's worked examples

**What.** Eight cases re-implement examples printed in the white paper, and three more port its
Appendix A.3 decorator illustrations. They keep the published identifiers so that the published
expected totals apply.

**Where.** `experiments/microcorpus/java/Micro.java:544–727` (`class AppendixC`, holding C.1, C.2,
C.3 and the four body examples), `experiments/microcorpus/javascript/micro.ts:551–588` (C.4),
and `experiments/microcorpus/python/micro.py:302–326` (Appendix A.3). The duplicate of the C.4 block
in the probe input `experiments/ccts_probe/a1.ts` is not included.

**Rights.** SonarSource S.A. for the examples as printed; for Appendix C, also the copyright holders
of the projects the white paper names — SonarJava, `com.persistit.TimelyResource` ("sonar-persistit"),
SonarQube and YUI.

**Basis for inclusion.** Quotation of a specification's worked examples in order to test conformance
against the totals the specification itself asserts. Each case is a few dozen lines, surrounded by
stubs written for this study, and reproduces no usable part of any upstream program.

**What a re-user must do.** Read `experiments/microcorpus/ATTRIBUTION.md`, which maps every case id to
its upstream example and records exactly what is and is not known about the upstream licences. These
cases are **not** covered by the MIT or CC BY 4.0 grants.

## 5. Dependency metadata for third-party tools — no tool code

**What.** Package names, versions, registry URLs, SRI `integrity` hashes and the `license` field as
published on npm, plus pinned PyPI requirement lists and a Docker image digest. No package payload,
binary, wheel or image layer is included.

**Where.** `reproduction/tools_node_package.json` and `reproduction/tools_node_package-lock.json`
(lockfile v3, 216 package entries, all carrying a `license` field: 168 MIT, 18 ISC, 14 Apache-2.0,
6 BSD-2-Clause, 5 BlueOak-1.0.0, 2 LGPL-3.0-only, 2 BSD-3-Clause, 1 GPL-3.0);
`reproduction/requirements-analysis.txt`, `reproduction/requirements-tools_venv.txt`,
`reproduction/requirements-freeze.txt`; `reproduction/sonarqube_image_digest.txt`
(`sonarqube@sha256:58b068af30bd…`); the `TOOL_VERSIONS` dictionary in `src/ccstudy/tools.py`.

**Rights.** The respective package authors and SonarSource S.A.; the metadata itself is factual.

**Basis for inclusion.** Reproducibility: the lock file is what makes the Node tool set restorable at
the exact versions used. `tools/`, `tools_venv/` and `node_modules/` are not included at any depth,
so no third-party executable code ships. Editable, local and VCS lines were dropped from
`requirements-freeze.txt` by the exporter.

**What a re-user must do.** Install the tools from their own sources (`npm ci`, `pip install -r`,
`docker pull`) and comply with each project's licence at that point.

## 6. Documentation and observed behaviour of third-party tools

**Not included.** The study's three author-written research notes on third-party tools
(`references/tools/tool_landscape.md`, `references/tools/test_example_inventory.md` and
`references/tools/sonar_extraction_notes.md`), which quote briefly from those tools' documentation,
are not part of this repository. `experiments/microcorpus/ATTRIBUTION.md` still cites the first two.
The observed behaviour of the SonarSource analyzers recorded in sections 6–8 of
`references/spec/cognitive_complexity_spec_rules.md` is covered by section 3 above.

## 7. Bibliographic metadata retrieved from third-party services

**What.** Titles, authors, venues, years, DOIs and URLs for 20 bibliography entries, retrieved from
Crossref, the arXiv export API, OpenAlex, a DSpace REST API, the GitHub API and a Discourse JSON
endpoint. The per-entry verification records (`references/citation_verification.json`,
`citation_audit.md`) are not included.

**Where.** `references/references.json`.

**Rights.** Factual bibliographic data; the cited works remain their authors' and publishers'.

**Basis for inclusion.** Facts about publications. No abstract or body text of any cited work is
reproduced; the full texts used for claim checking (`references/sources/`) are not included.

**What a re-user must do.** Nothing.

## 8. Venue files and their digests — not included

The organiser's IEEE paper template, the venue's announcement pages and the 2017 proceedings volume
are not part of this repository, and neither are the digests and retrieval timestamp of them
(`references/SHA256SUMS.txt`, `references/official/RETRIEVAL_TIMESTAMP_UTC.txt`) that the exporter
published. They served only the preparation of the manuscript; no number in the paper depends on
them.

## 9. How this notice was verified

* The exported file list was produced by importing `scripts/export_public_artifact.py` (not included
  here) and applying its own `selected()` predicate to every file in the tree, rather than by reading
  the policy by eye. This repository is a subset of that list. It adds `CITATION.cff`, `.gitignore`
  and `scripts/reproduce_analysis.sh`; it replaces `README.md` and `ARTIFACT_MANIFEST.json`; and it
  edits `LICENSE`, this notice, `reproduction/requirements-analysis.txt` (Windows-only and
  manuscript-only packages removed) and `reproduction/README.md` (a note at the top).
* Every selected text file was scanned for `copyright`, `SPDX-License`, `Licensed under`,
  `All rights reserved` and `(c) 20`. Sixteen files matched. Every match in `results/` resolves to a
  third-party *path or identifier* — for example `script/copyrights.go`, `parseCopyrightNotices`,
  `meta/copyright_test.go` — and not to a copyright header, because no source body is present. The
  remaining matches were this repository's own `LICENSE`, the exporter's comment about the white-paper
  PDF (the exporter is not included here), and the digest file described in section 3.
* The record schema of each raw output family was inspected (`units.json`, `sonar.json`,
  `codemetrics.json`, `lizard.json`, `gocognit.json`, `rca.json`, `ccts.json`, `pmd.json`,
  `cognitive_java.json`, `python_tools.json`, `js_*.json`, `sonar_files.json`, `run_meta.json`):
  every record is keyed by path, line and name and carries numbers, never source text.
* The exclusion of the audit snippets, the white-paper PDF, the scraped rule descriptions,
  `references/official`, `references/sources`, `references/proceedings_2017`, `tools/`, `tools_venv/`,
  `data/raw_repos/` and `node_modules` was confirmed by their absence from that selected-file list.
* Subject-repository licences were spot-checked by reading the licence files out of the local clones
  in `data/raw_repos/` — `krahets/hello-algo` ("Attribution-NonCommercial-ShareAlike 4.0
  International"), `open-webui/open-webui` ("Open WebUI License … All rights reserved"),
  `termux/termux-app` ("released under GPLv3 only"), `JuliusBrussee/caveman` (MIT with a scope note
  routing engine-linked directories to `LICENSE.BSL`), `iluwatar/java-design-patterns` ("The MIT
  License (MIT)") and `syncthing/syncthing` ("Mozilla Public License Version 2.0") — and they match
  `data/repos/LICENSES.md`.
* The quotation volume in section 3 was measured programmatically on the shipped file, not estimated:
  blockquote lines, fenced-code lines, quoted spans, their word counts and the file's SHA-256.
* The npm licence tally in section 5 was computed from the `license` field of all 216 entries in the
  lock file.

## 10. Known residual risk

The study's pre-publication review of the package (reviewer `licensing`; its record,
`logs/artifact_review.json`, is not included here) raised nine findings. Eight are resolved in the
export policy, in the source files or by leaving files out of this repository: the audit snippets, the
scraped rule descriptions, `references/official/`, the nested `.scannerwork` directories, the
`NOASSERTION` licence column, the single-MIT licence, the extent of quotation in the rule digest
(section 3 above measures the rewritten file), and `experiments/ccts_probe/a1.ts`, the probe input
holding a second copy of the Appendix C.4 block, which is not included. One is stated here rather than
resolved:

* **No upstream licence was established for the code behind Appendix C.1–C.4.** This repository holds
  no record of the terms under which those files were published when the white paper quoted them, and
  none was looked up for this package. `experiments/microcorpus/ATTRIBUTION.md` states this
  explicitly rather than naming a licence that was never read here. A re-user who needs a licence
  answer for that upstream code must get it from SonarSource, the Persistit project and YUI.

A further limitation applies to the whole of section 1: the licence identifications in
`data/repos/LICENSES.md` are the author's reading of each repository's licence files on 2026-09-18.
They are informational. Each repository's own licence at its pinned SHA governs, and a re-user should
read it rather than rely on this package's summary.

---

*If a third-party item is found in this package that is not described above, treat this notice as
wrong on that point and the item as not licensed by `LICENSE`. Please report it so that the
repository and this file can be corrected together.*
