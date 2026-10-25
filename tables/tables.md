### T1. Implementations Under Test (Reference: SonarQube Community Build 26.9.0.129388)

| Implementation | Version | Languages used |
|---|---|---|
| complexipy | 8.0.1 | Python |
| cognitive_complexity | 1.3.0 | Python |
| rust-code-analysis | 0.0.25 | Python, JS/TS |
| codemetrics | 0.12.7 | all four |
| PMD | 7.27.0 | Java |
| cognitive-java | 0.7.1 | Java |
| gocognit | 1.2.1 | Go |
| cognitive-complexity-ts | 0.8.2 | JS/TS |
| cogplexity | 0.1.0 | JS/TS |
| oxlint-plugin-complexity | 3.0.0 | JS/TS |
| eslint-plugin-maintainability | 3.2.10 | JS/TS |
| eslint-plugin-sonarjs 4.2.1 | 4.2.1 | JS/TS (reference snapshot) |
| lizard | 1.24.0 | Python, Java, JS/TS (cyclomatic baseline only) |
| radon | 6.0.1 | Python (cyclomatic baseline only) |

### T2. Real-Code Corpus

| Lang. | Repos | Function-like units | Leaf root | With ref. | Ref. = 0 (%) | > 15 (%) |
|---|---|---|---|---|---|---|
| Python | 8 | 49,796 | 37,525 | 24,337 | 40 | 5.3 |
| Java | 8 | 90,620 | 62,511 | 58,255 | 75 | 1.0 |
| JS/TS | 8 | 124,115 | 26,039 | 26,038 | 60 | 1.8 |
| Go | 8 | 51,008 | 29,763 | 29,763 | 46 | 2.9 |

### T3. Micro-Corpus Conformance of the Reference and the Implementations on Unambiguous Cases (Failed Target Rules: Count)

| Lang. | Implementation | Conform | % | Failed target rules |
|---|---|---|---|---|
| Python | codemetrics | 46/56 | 82 | A.3:3, B1.8i:2, B2.6:2, B1.8d:1, B1.8m:1, B1.8d2:1 |
| Python | cognitive_complexity | 51/56 | 91 | B1.8i:2, B2.1:1, B1.3a:1, B1.8m:1 |
| Python | complexipy | 52/56 | 93 | B1.8i:2, B2.6:1, B1.8m:1 |
| Python | rust-code-analysis | 45/56 | 80 | R7:2, B1.8i:2, A.3:2, B1.8d:1, B3:1, B1.8m:1, B1.7and:1, B1.8d2:1 |
| Python | SonarQube (ref.) | 50/56 | 89 | B1.8i:2, B1.8d:1, B1.8m:1, B2.6:1, B1.8d2:1 |
| Java | codemetrics | 45/62 | 73 | B2.6:5, R2:2, B2.1:2, B1.8i:2, B1.6:2, B1.8d:1, B1.8m:1, C:1, B1.8d2:1 |
| Java | cognitive-java | 62/62 | 100 | — |
| Java | PMD | 58/62 | 94 | B1.8i:2, B1.7mix:1, B1.8d2:1 |
| Java | SonarQube (ref.) | 57/62 | 92 | B1.8i:2, B1.8d:1, B1.8m:1, B1.8d2:1 |
| JS/TS | codemetrics | 46/65 | 71 | B2.6:5, B2.1:3, R2:2, B1.8i:2, B1.8d:1, B1.6:1, B1.8m:1, B1.8d2:1 |
| JS/TS | cognitive-complexity-ts | 57/65 | 88 | B1.8i:2, R13:2, B2.6:1, C:1, B1.8d2:1 |
| JS/TS | cogplexity | 60/65 | 92 | B2.6:5 |
| JS/TS | eslint-plugin-maintainability | 51/65 | 78 | B2.6:5, B1.8i:2, R13:2, B3.1t:1, B1.6:1, B1.8m:1, C:1, B1.8d2:1 |
| JS/TS | eslint-plugin-sonarjs 4.2.1 (snapshot) | 43/65 | 66 | B2.6:7, B1.7or:5, B1.7mix:3, B1.8i:2, B1.7idiom:1, B1.8d:1, B1.8m:1, C:1, B1.8d2:1 |
| JS/TS | oxlint-plugin-complexity | 54/65 | 83 | B2.6:5, B1.8i:2, R13:2, B1.7idiom:1, C:1 |
| JS/TS | rust-code-analysis | 56/65 | 86 | B1.8i:2, B1.8d:1, B2.6:1, B1.6:1, B1.8m:1, ARROW:1, C:1, B1.8d2:1 |
| JS/TS | SonarQube (ref.) | 43/65 | 66 | B2.6:7, B1.7or:5, B1.7mix:3, B1.8i:2, B1.7idiom:1, B1.8d:1, B1.8m:1, C:1, B1.8d2:1 |
| Go | codemetrics | 50/53 | 94 | B1.8i:2, B1.8d2:1 |
| Go | gocognit | 48/53 | 91 | B1.8i:2, B2.1:1, B1.8m:1, B1.8d2:1 |
| Go | SonarQube (ref.) | 43/53 | 81 | GO-ERRNIL:4, B1.8i:2, B1.8d:1, B1.6:1, B1.8m:1, B1.8d2:1 |

### T4. Agreement with the SonarQube Reference on Leaf Root Functions and Gate Flips at t = 15

| Lang. | Implementation | n | Cov. (%) | Exact (%) [95% CI] | Exact ref>0 (%) | ±1 (%) | MAD | ρ | Higher (%) | Lower (%) | Flip@15 (%) | Flip near (%) [95% CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Python | codemetrics | 24,337 | 100 | 99.8 [99.7, 99.8] | 99.6 | 99.9 | 0.00 | 1.000 | 0.2 | 0.1 | 0.01 | 0.1 [0.0, 0.3] |
| Python | cognitive_complexity | 24,026 | 99 | 95.6 [94.7, 96.7] | 92.8 | 98.2 | 0.11 | 0.998 | 2.0 | 2.5 | 0.25 | 3.2 [2.1, 4.3] |
| Python | complexipy | 24,124 | 99 | 82.8 [78.2, 85.5] | 76.9 | 91.3 | 0.39 | 0.967 | 13.1 | 4.1 | 0.71 | 9.0 [6.9, 10.9] |
| Python | rust-code-analysis | 24,305 | 100 | 94.3 [90.9, 96.4] | 90.7 | 98.4 | 0.09 | 0.998 | 2.5 | 3.2 | 0.21 | 3.0 [1.6, 4.3] |
| Java | codemetrics | 58,255 | 100 | 95.6 [93.9, 97.3] | 82.3 | 99.2 | 0.06 | 0.998 | 0.1 | 4.3 | 0.11 | 6.6 [4.8, 10.2] |
| Java | cognitive-java | 55,884 | 96 | 97.8 [95.9, 99.2] | 93.1 | 100.0 | 0.02 | 0.992 | 2.1 | 0.0 | 0.02 | 1.1 [0.6, 1.6] |
| Java | PMD | 56,873 | 98 | 98.5 [96.7, 99.6] | 94.2 | 99.3 | 0.04 | 0.998 | 1.5 | 0.1 | 0.05 | 2.5 [1.4, 4.2] |
| JS/TS | codemetrics | 15,165 | 58 | 83.1 [78.2, 89.5] | 69.4 | 94.6 | 0.39 | 0.980 | 14.8 | 2.0 | 0.59 | 14.1 [9.6, 17.5] |
| JS/TS | cognitive-complexity-ts | 25,482 | 98 | 74.4 [68.4, 81.8] | 54.5 | 90.5 | 0.45 | 0.922 | 25.5 | 0.1 | 0.55 | 18.5 [16.0, 19.8] |
| JS/TS | cogplexity | 25,755 | 99 | 88.1 [85.9, 91.4] | 75.9 | 96.7 | 0.19 | 0.974 | 11.9 | 0.0 | 0.25 | 8.1 [5.5, 10.1] |
| JS/TS | eslint-plugin-maintainability | 26,038 | 100 | 82.8 [79.2, 87.9] | 66.5 | 93.9 | 0.33 | 0.936 | 15.8 | 1.4 | 0.45 | 14.3 [9.5, 18.8] |
| JS/TS | eslint-plugin-sonarjs 4.2.1 (snapshot) | 26,038 | 100 | 100.0 [100.0, 100.0] | 100.0 | 100.0 | 0.00 | 1.000 | 0.0 | 0.0 | 0.00 | 0.0 [0.0, 0.0] |
| JS/TS | oxlint-plugin-complexity | 25,627 | 98 | 84.0 [80.7, 88.5] | 70.3 | 95.0 | 0.27 | 0.950 | 16.0 | 0.0 | 0.32 | 10.2 [7.0, 13.7] |
| JS/TS | rust-code-analysis | 25,795 | 99 | 80.3 [73.8, 84.6] | 56.7 | 92.8 | 0.39 | 0.975 | 19.6 | 0.1 | 0.60 | 18.5 [9.7, 36.7] |
| Go | codemetrics | 29,763 | 100 | 81.8 [74.9, 89.3] | 74.8 | 90.3 | 0.47 | 0.954 | 18.2 | 0.0 | 0.76 | 12.3 [9.2, 15.7] |
| Go | gocognit | 28,442 | 96 | 80.6 [74.0, 88.1] | 74.1 | 89.7 | 0.50 | 0.953 | 18.8 | 0.6 | 0.80 | 12.6 [9.1, 16.4] |

### T5. Attribution of Real-Code Disagreements

| Lang. | Implementation | Disagree | Impl. (%) | Ref. (%) | Amb. (%) | Unexpl. (%) | Base (%) | Impl. targets | Ref. targets |
|---|---|---|---|---|---|---|---|---|---|
| Python | codemetrics | 60 | 13 | 0 | 68 | 18 | 26 | A.3, B1.8d, B1.8d2, B1.8i, B1.8m, B2.6 | — |
| Python | cognitive_complexity | 1,061 | 77 | 19 | 4 | 0 | 31 | B1.3a, B1.8i, B1.8m, B2.1 | B1.8d, B1.8d2, B2.6 |
| Python | complexipy | 4,150 | 0 | 22 | 66 | 12 | 23 | B1.8i, B1.8m, B2.6 | B1.8d, B1.8d2 |
| Python | rust-code-analysis | 1,381 | 88 | 0 | 2 | 10 | 42 | A.3, B1.7and, B1.8d, B1.8d2, B1.8i, B1.8m, B3, R7 | B2.6 |
| Java | codemetrics | 2,563 | 98 | 0 | 1 | 0 | 13 | B1.6, B1.8d, B1.8d2, B1.8i, B1.8m, B2.1, B2.6, C, R2 | — |
| Java | cognitive-java | 1,209 | 0 | 84 | 5 | 11 | 12 | — | B1.8d, B1.8d2, B1.8i, B1.8m |
| Java | PMD | 875 | 48 | 43 | 2 | 7 | 11 | B1.7mix, B1.8d2, B1.8i | B1.8d, B1.8m |
| JS/TS | codemetrics | 2,556 | 27 | 72 | 0 | 0 | 12 | B1.6, B1.8d, B1.8d2, B1.8i, B1.8m, B2.1, B2.6, R2 | B1.7idiom, B1.7mix, B1.7or, C |
| JS/TS | cognitive-complexity-ts | 6,526 | 26 | 39 | 0 | 36 | 4 | B1.8d2, B1.8i, B2.6, C, R13 | B1.7idiom, B1.7mix, B1.7or, B1.8d, B1.8m |
| JS/TS | cogplexity | 3,068 | 0 | 97 | 0 | 3 | 4 | B2.6 | B1.7idiom, B1.7mix, B1.7or, B1.8d, B1.8d2, B1.8i, B1.8m, C |
| JS/TS | eslint-plugin-maintainability | 4,471 | 53 | 43 | 0 | 4 | 12 | B1.6, B1.8d2, B1.8i, B1.8m, B2.6, B3.1t, C, R13 | B1.7idiom, B1.7mix, B1.7or, B1.8d |
| JS/TS | oxlint-plugin-complexity | 4,109 | 38 | 61 | 1 | 0 | 4 | B1.7idiom, B1.8i, B2.6, C, R13 | B1.7mix, B1.7or, B1.8d, B1.8d2, B1.8m |
| JS/TS | rust-code-analysis | 5,083 | 57 | 42 | 0 | 1 | 43 | ARROW, B1.6, B1.8d, B1.8d2, B1.8i, B1.8m, B2.6, C | B1.7idiom, B1.7mix, B1.7or |
| Go | codemetrics | 5,414 | 1 | 96 | 2 | 0 | 21 | B1.8d2, B1.8i | B1.6, B1.8d, B1.8m, GO-ERRNIL |
| Go | gocognit | 5,515 | 13 | 85 | 2 | 0 | 24 | B1.8d2, B1.8i, B1.8m, B2.1 | B1.6, B1.8d, GO-ERRNIL |

### T6. Baseline: Cyclomatic Complexity Agreement with SonarQube on the Same Functions

| Lang. | Tool | n | Exact (%) | ±1 (%) | MAD |
|---|---|---|---|---|---|
| Python | codemetrics | 24,337 | 81.7 | 94.6 | 0.29 |
| Python | lizard | 24,148 | 73.0 | 90.0 | 0.48 |
| Python | radon | 23,991 | 72.2 | 89.6 | 0.51 |
| Python | rust-code-analysis | 24,305 | 70.1 | 87.6 | 0.58 |
| Java | codemetrics | 58,255 | 96.3 | 99.5 | 0.04 |
| Java | lizard | 55,237 | 96.7 | 99.6 | 0.04 |
| Java | PMD | 56,872 | 92.8 | 98.4 | 0.10 |
| JS/TS | codemetrics | 15,165 | 84.5 | 95.9 | 0.24 |
| JS/TS | lizard | 20,105 | 83.2 | 93.5 | 0.43 |
| JS/TS | oxlint-plugin-complexity | 25,627 | 82.2 | 94.1 | 0.30 |
| JS/TS | rust-code-analysis | 25,795 | 88.8 | 97.2 | 0.17 |
