# Final V6.6 Progress UI Copy Review

Recommendation: **C — PROGRESS UI COPY CLEANUP ACCEPTED**

Presentation-only cleanup implemented in maintained sources and rebuilt into the isolated local V6.6 candidate. Progress calculations, evidence, contracts, relations, styling, geometry, navigation, and original Production remain unchanged. No commit, push, deployment, or live Hyperskill access.

## Visible labels before and after

| View | Before | After |
| --- | --- | --- |
| My Skill Tree Topics | 31 / 3106; 12 verified Topics | Topics learned · **31 / 3,106** · **12 verified** |
| Global Project metric | 1 confirmed completed Project; 391 catalog Projects | Projects completed · **1** |
| Global Course metric | Course completions not yet recorded; 52 catalog Courses | **Omitted** when no completion evidence exists |
| Selected Course summary | — | Course Projects · **1 / 11 completed** |
| Global Topics card | 31 / 3106 evidenced learned; repeated partitions, dates and denominator text | **31 / 3,106 learned** · **12 verified** |
| Course 8 card | Selected Course 8; 31 / 89 evidenced learned; official snapshot and missing completion rows | **Introduction to Java** · **31 / 89 learned** · **12 verified** · **1 / 11 associated projects completed** |
| Project 8 card | Project 8 · knowledge coverage; 2 / 56 evidenced learned; completion Not recorded | **Minesweeper (Kotlin)** · **2 / 56 learned** · **1 verified** |
| Stage 46 card | Stage 46 · knowledge coverage; 0 / 34 evidenced learned; Personal status Not recorded | **Lay the groundwork** · **0 / 34 learned** |
| Confirmed Project 113 | Completed (evidenced), with source details alongside statistics | **Completed**, with provenance in Data details |
| Missing Course/Project/Stage completion | Prominent Not recorded row | **Omitted**; no inferred Not completed or zero Course completions |
| UNKNOWN requirements | Requirements not established; UNKNOWN denominator | **Requirements unknown** |
| Known-empty Project/Stage requirements | No requirement Topics | **No required Topics** |

Exact IDs remain in selector values, scope identity attributes, Data details, and existing navigation targets. Scope names are taken from the accepted catalog. The Course Projects summary follows the selected Course; known-empty and unknown inventories do not fabricate a 0 / 0 summary.

## Hidden versus retained information

One collapsed **Data details** section in the progress panel contains the shared bar legend, scope-specific definitions, and evidence. Scope, Category, and Topic Inspectors use the same optional details pattern. The bar still displays the accepted learned / explicitly not learned / unknown segments using the original colors.

Retained access includes:

- Learned, explicitly not learned, unknown, verified, explicitly not verified, and verification-unknown counts; Topic verification/evaluation statuses.
- Exact Topic denominator definitions and scope IDs; Course associated-Project inventory definition, evidence reference, and completed Project IDs.
- Direct observation versus owner-attested Project provenance, source references, and source-specific timestamps.
- Official Hyperskill Course snapshot coverage separately from the effective learned union.
- Explicit completion records, dates and sources; catalog totals, which remain inventories rather than enrolled plans or official overall completion.

Repeated status, denominator, remaining-count, date, and evidence paragraphs were removed from the visible cards. Their underlying data remains unchanged. Missing completion indicators are omitted, and explicit negative/conflicting observations remain accessible in details. Zero verified counts are retained in details rather than adding a visible row to an otherwise empty learned card.

There are no palette, CSS, map-renderer, layout, routing, or Inspector Pin / Close changes. Long source references allow wrapping through markup without changing styles.

## Focused screenshot comparison

| Requested view | Before | After |
| --- | --- | --- |
| My Skill Tree summary | [Summary](copy-review/before-summary.png) | [Summary](copy-review/after-summary.png) |
| Global progress card | [Global/Course panel](copy-review/before-global-course.png) | [Global/Course panel](copy-review/after-global-course.png) |
| Course 8 card | [Global/Course panel](copy-review/before-global-course.png) | [Global/Course panel](copy-review/after-global-course.png) |
| Project 8 card | [Project/Stage panel](copy-review/before-project-stage.png) | [Project/Stage panel](copy-review/after-project-stage.png) |
| Stage 46 card | [Project/Stage panel](copy-review/before-project-stage.png) | [Project/Stage panel](copy-review/after-project-stage.png) |
| Expanded evidence details | [Existing evidence](copy-review/before-details.png) | [Data details](copy-review/after-details.png) |
| UNKNOWN Project 229 | [UNKNOWN](copy-review/before-unknown.png) | [UNKNOWN](copy-review/after-unknown.png) |
| Narrow 390px viewport | [Narrow](copy-review/before-narrow.png) | [Narrow](copy-review/after-narrow.png) |

The captures were visually inspected. The expanded-details capture scrolls to the optional section so its legend, partitions, source dates and official Course snapshot can be read. Narrow collapsed and expanded details have no horizontal overflow; the existing panel scrolls vertically. No broad historical screenshot matrix was repeated.

Visible text measurement excludes native selector option inventories, which are not all shown at once, and excludes collapsed details:

| Region | Before characters | After characters | Reduction |
| --- | --- | --- | --- |
| summary | 204 | 109 | 46.6% |
| global-course | 1051 | 148 | 85.9% |
| project-stage | 1744 | 231 | 86.8% |

## Validation

| Check | Result |
| --- | --- |
| Presentation contract tests | PASS: short readable names, comma formatting, missing completion omitted, explicit completion retained, known-empty/UNKNOWN distinction, segmented bars, one collapsed details section, retained evidence, pure inputs |
| Existing analytics aggregation | 17 checks PASS |
| Universal scope/Category aggregation and presentation | Eight check groups PASS; only copy assertions updated |
| Portfolio completion tests | PASS; baseline 31 learned / 12 verified / 1 Project; no Course completion records; exact memberships, duplicate IDs, Course fixtures, revocation, new Project updates |
| Completion-learning union tests | PASS; overlap, global propagation, verification independence, historical snapshots, legacy, UNKNOWN/empty and geometry fixtures preserved |
| Focused before/after candidate browser test | PASS across all requested views; zero browser errors, failed requests, or external requests |
| Existing portfolio browser test, run only in the isolated candidate | Five check groups PASS, including synthetic Project 380 and explicit Course completion fixtures |
| Controls | Search, Category Inspector, Course selection, Pin / Close and summary controls PASS; same personal layout object and zero new layout builds |
| Baseline completion evidence | Project 113 Completed; Stage 617 missing completion omitted despite 12 / 12 learned; global Course metric hidden |
| Explicit Course fixture | Course completion metric and Completed indicator appear only with explicit evidence; no fixture was persisted |
| Narrow screen | 390 × 844, collapsed and expanded details: PASS, no horizontal overflow |
| Public progress data | Byte-identical to the accepted portfolio candidate |
| Repeated candidate builds | All 69 files byte-identical on repeated build |
| Production guard / whitespace | PASS |

Test sources: [copy-test.cjs](copy-test.cjs), [copy-review.cjs](copy-review.cjs). Results: [before labels](copy-review/before.json), [after labels and geometry](copy-review/after.json), [protection evidence](copy-protection-results.json).

## Freeze and reproducibility

All 1,482 existing files were fingerprinted at milestone entry. Only two maintained runtime presentation scripts and five related presentation-test scripts changed. All other existing files, including unrelated modified/untracked work, remain byte-identical.

The accepted `progress-analytics.js`, Git scanner, public serializer, Course evidence contract, input JSON, historical observations, relations, CSS/colors, layouts, models, shell, routing, and guard implementation are unchanged. The five accepted local commits remain intact at HEAD `a3c31daaa4ea974f8d6afe1b6ef4bf2202e69553`; `origin/main` remains `a8b79e2e6c32df990fc3305983bb5aff1d9e2500`. Nothing was staged.

Only these candidate assets differ from the previous accepted portfolio candidate:

- `views/knowledge-atlas-v6-skill-tree/progress-presentation.js`
- `views/knowledge-atlas-v6-skill-tree/progress-ui.js`
- `candidate-manifest.json`, recording their updated source hashes

The existing isolated packager rebuilt from the maintained sources. `progress.json` is byte-identical, as are all other runtime assets. No changes were made only in disposable release output.

All five geometry fingerprints remain unchanged:

| View | SHA-256 | Result |
| --- | --- | --- |
| personal | `a60fc22e272079c91f39cfed9c01af5865bae29120e6d6f7801b02da96cd6348` | PASS |
| global | `1306993ec8a1b7a80edda4f620fb96ba5d4803c0d81ded334b92efa85cdf1174` | PASS |
| course8 | `ab8e05971ca8fb9d077b491a766554f5b84118e068433afe4c17faa7e91fb89b` | PASS |
| project113 | `33dc51873bcbd33fa6ad2de854dd719e525706bdb764a50578570d1f73e89034` | PASS |
| stage617 | `24edf473c9e97b7ccbb287464302a4bbf6ffadff33efdc265076b5ae6b51455e` | PASS |

The existing Production guard passes with fingerprint:

`36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`

Original `docs/knowledge-map/`, `state/knowledge-atlas/`, and `data/knowledge/` inventories and hashes are unchanged (33 actual files across those roots). The historical release manifest and protected semantics are preserved. The original public Production edition was not modified.

## Updated preview

[My Skill Tree](http://127.0.0.1:8806/hyperskill-projects/knowledge-map/?view=skill-tree) · [Course 8](http://127.0.0.1:8806/hyperskill-projects/knowledge-map/?course=8) · [Project 8](http://127.0.0.1:8806/hyperskill-projects/knowledge-map/?project=8) · [Stage 46](http://127.0.0.1:8806/hyperskill-projects/knowledge-map/?project=8&stage=46)

Technical review complete. No commit, push, deployment, Production integration, or Hyperskill request. Hard stop.
