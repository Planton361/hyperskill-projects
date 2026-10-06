# Production Adaptive-View Migration Preview — 2026-10-06

**C — READY FOR FINAL HUMAN REVIEW BEFORE ADAPTIVE PRODUCTION APPLY**

The isolated candidate is ready for human comparison. My Knowledge now shows the
31 explicitly learned Topics and their hierarchy context instead of presenting all
89 accepted Topics as the personal map. Global orientation remains available through
the complete frozen reference, identity-based navigation, breadcrumbs and separate
local/global cameras. This recommendation authorizes no apply operation.

Review question: **Is the adaptive Production candidate clearly better for normal
learning while preserving global orientation?**

Open the [human review package](production-preview/index.html) through the local
server: **http://127.0.0.1:8765/prototypes/adaptive-pyramid/production-preview/**.
It contains Current Production, Target My Knowledge, Target Global, Target Course
and Target Project. The current copy is byte-identical to real Production. The target
is a complete self-contained static package at `production-preview/target/`.
Use “Open target at full viewport” to review it without the review page's header.

## Baseline, pre-flight and isolation

Branch: `work/adaptive-pyramid-handoff`.
HEAD: `424e820f8fc98d94f71a24d5f29fa8579d23e864`.
The initial working tree contained only the untracked normal adaptive preview.
The four required handoff/architecture/validation documents were read first.

`bash scripts/dev-macos-check.sh`, normal preview generation and normal preview
`--check --json` all passed on Darwin arm64, Python 3.9.6, Node 22.22.2.
npm and repo-local Playwright are absent; no runtime dependency or portability fix
was needed. Browser validation used the cached runtime Playwright and native macOS
Chromium 149.0.7827.55. Its default executable revision was absent, so the harness
used `CHROMIUM_EXECUTABLE` to select the installed browser. The initial progress
comparison assertion was corrected to compare Production's `progress.topics` against
the target's flat progress array in identity order; every Topic record then matched.

The builder imports the normal read-only `adaptive_preview.artifacts` path. It loads
canonical Knowledge, validates the active projection and projects the Catalog with
existing activation history. It never calls the legacy allocator, State transaction,
strict-global migration operator or Production writer. Reference structure/membership
must match the frozen geometry before packaging. No global layout is regenerated.

Only new review/build/test/report files and their isolated outputs were written.
No tracked source file was edited. Real Production, State, Knowledge and the generated
reference match HEAD. No commit, push or deployment occurred.

## Exact proposed Production file replacement

This is the file plan **if this exact candidate is later approved**. It is a clean
replacement of the generated static directory, not a request to run the current
legacy `--production` command. Full sizes/hashes and classifications are in
[build-results.json](production-preview/build-results.json).

| Classification | Proposed action | Paths under `docs/knowledge-map/` |
|---|---|---|
| Runtime/UI | Replace | `index.html`, `app.js`, `style.css` |
| Runtime/UI | Add | `adaptive.cjs`, `atlas.js`, `labels.js`, `ux.js`, `registry.cjs`, `views.cjs` |
| Runtime dependency/licenses | Add | `vendor/d3-flextree-2.1.2.cjs`, `vendor/d3-flextree-LICENSE`, `vendor/d3-hierarchy-LICENSE` |
| Generated model/config | Replace | `model.json`, `release-manifest.json` |
| Global reference asset | Add | `global-reference.json` |
| Retired legacy presentation | Remove from generated package | `geometry.js`, `layout.js`, `model.js`, `routing.js`, `taxonomy-relations.js`, `layout-checkpoint.json`, `layout-checkpoint.schema.json` |
| Retired legacy dependency | Remove from generated package | `vendor/d3-7.9.0.min.js`, `vendor/D3-LICENSE` |

There are 5 replacements, 10 additions and 9 removals; all 15 target files are
accounted for. Removing the **generated Production copy** of a checkpoint does not
remove or rewrite `state/knowledge-atlas/layout-checkpoint.json`.

The candidate retains the validated adaptive runtime and algorithm. Packaging changes
the title/read-only review notice, removes fixture options from the visible scope
selector and hides the historical strict-mask comparison button. Internal fixture
helpers remain for validation. No algorithm or semantic-selection change was made.
The release manifest describes a read-only candidate, lists asset hashes, states
`state_migration: false` and `authorizes_apply: false`; it has no fabricated accepted
generation or migration receipt. These review notices are intentionally part of the
exact packaged bytes; any later removal should be an explicit reviewed difference.

New implementation/evidence files for this task: `production-preview/build.py`,
`focused.cjs`, `smoke.cjs`, `index.html`, `protected-before.json`,
`protected-head-check.json`, `build-results.json`, `focused-results.json`,
`browser-results.json`, the `current/` and `target/` packages, eight PNGs, and this
report. The normal `docs/knowledge-map-adaptive-preview/` remains a separate derived
pre-flight output. No existing authoritative or runtime source was changed.

## Minimum durable change; State and history decision

Persist the global reference **separately from the semantic model** as
`global-reference.json`, byte-for-byte from the accepted frozen artifact. Local
geometry, ranks, trays, routes, collapse state, animation positions and two cameras
remain derived browser memory. Deterministic layout requires visible semantic IDs,
canonical order and current card measurement, not authoritative personal x/y.

| Authority/history | Must change for this target? | Decision |
|---|---|---|
| `activation-state.json` | No | Continue reading accepted IDs for Accepted Landscape. No activation, geometry acceptance or history event is manufactured. |
| State `layout-checkpoint.json` | No | Preserve legacy Generation 0 checkpoint as historical/rollback authority. Adaptive runtime does not hydrate it. |
| `presentation_generation` | No | Remains 0. No persisted allocation/order changes occur; derived local movement is not a legacy allocation event. |
| Generation/history | No State history change | Activation `layout_generation` remains 0 and events remain intact. Use static release asset hashes to identify this candidate; do not repurpose State generation to count local renders or releases. |
| `ACTIVE_HISTORY` | No | Retain its current accepted entity set and interpretation, exposed as Accepted Landscape. It is not learned truth. |
| Knowledge | No | All facts, evidence, progress, membership and requirements remain authoritative and unchanged. |
| `update-snapshot.json` | No | No accepted legacy State update occurred. Preserve the checkpoint/snapshot pair. |

No State/schema migration is technically necessary for these derived local views.
The generated model **does** change read-model shape: one Catalog registry plus
reference mappings replaces the V6 model/geometry hydration contract. That is a
generated runtime contract change, not an authoritative Knowledge schema change.
Future global taxonomy/reference changes require separate review. Future adaptive
publication must select this builder explicitly and retain the migration guards;
the legacy Production command is not an adaptive publisher.

## View semantics and behavior

**My Knowledge is the default**, seeded only by Topic progress records whose
`is_learned` is exactly true. Ancestors are hierarchy context, with no inferred
learning or membership. Independent expected-ID construction gives exactly 31
explicit Topics and 52 visible cards; 12 Topics are verified. Accepted Landscape
has 89 Topics / 135 cards and remains a separate selection.

**Global** uses all 3,955 immutable reference positions: 849 Categories, 89 described
Topics and 3,017 unresolved references. Semantic IDs, taxonomy, primary parents and
canonical ordering are shared with local views; local absolute coordinates differ.
Global roots, paths and reference bytes are unchanged. Global highlight and compact
views have separate cameras/minimaps. “Show in Global Atlas” resolves an inspected
Topic to its frozen position. Complete-registry search aliases `topic:36`, `leaf:36`
and `reference:36` resolve to the same described Topic; inspection does not learn it.

**Course** uses explicit Catalog membership. Course 8 has 89 Topics / 135 cards;
learned-only intersects explicit Topic membership with learned facts before rebuilding
context, yielding 31 / 52. Compact Course derives local layout. Course highlight
paints the complete global reference without a layout call or global-camera change.

**Project** uses explicit requirements. Project 113 has 26 Topics / 47 cards, with
26 learned / 10 verified. Stage 617 uses its own 12 requirements / 28 cards, with
12 learned / 7 verified; it is not inferred cumulative coverage. Stage 618 is known
empty; Project 380 is Requirements UNKNOWN. Project completion never manufactures
learned/verified facts. Project and Stage highlights preserve global geometry/camera;
Compact Project uses derived local ranks. Selector changes need a view action, so
typing/inspection does not relayout. Learned/verified marks remain independent styling.

## Measurements, growth and performance

One native Chromium run at **1440×900**, device scale 1, macOS system fonts. Bounds
below include local subtree envelopes. Values are observations, not a benchmark.

| View | Topics / cards | Width × height | Measured layout | Fit scale |
|---|---:|---:|---:|---:|
| Current Production default | 89 / 135 | 8,916 × 1,867.14 | 0 ms checkpoint hydration | 12.81% |
| Target My Knowledge | 31 / 52 | 4,096 × 1,152 | 1.9 ms | 27.97% |
| Target Course 8 | 89 / 135 | 11,168 × 1,876 | 1.5 ms | 9.93% |
| Target Project 113 | 26 / 47 | 3,877 × 1,084 | 0.4 ms | 29.63% |
| Target Stage 617 | 12 / 28 | 2,127 × 1,016 | 0.2 ms | 51.75% |

The target personal overview has about 28.3% of the current default's bounding-box
area, partly because it correctly shows fewer Topics. This is not an equal-content
layout comparison. On equal Course 8 content the conservative target envelopes are
larger than current Production; same-depth ranks and disjoint subtree envelopes cost
space. Compared with the **same personal visibility mask on the full global reference**,
the target My Knowledge envelope area is approximately 707 times smaller.

My Knowledge fit shows 10 overview labels and zero full Topic titles. Group focus
at 118.08% shows 10 full Topic titles. Course fit still needs branch focus or summary.
Visual inspection found aligned ranks, separated trays and readable focused Topics.
The candidate improves the learned-only overview and orientation options; it does
not make every Topic readable at overview zoom.

One explicitly labelled **in-memory learning simulation** changes already-known
Topic 1 from not learned to learned: 31 → 32 learned; verified stays 12. Local cards
52 → 54; bounds 4,096 × 1,152 → 4,356 × 1,152. Among the 52 existing cards, 11 move,
average displacement **45 px**, median **0 px**, maximum **260 px**. Movement is
horizontal in this scene; existing Category ranks do not move. Selected screen-anchor
displacement is **0 px**. Exactly one layout call occurs. Every global position stays
unchanged. The existing 180-ms transition runs; this focused smoke checks the settled
result after 200 ms, not a new animation collision matrix. No real learning fact is
written. Wider future growth may expand shared rank bands and move Category Y.

Package size: current **746,034 bytes / 14 files**; target **5,409,504 bytes / 15
files**, **7.25×** larger, uncompressed. The target model is 2,031,344 bytes and the
complete global reference is 3,300,297 bytes. Two deterministic target builds take
3.55 seconds total. Single-run localhost readiness: current 70.1 ms, target 55.4 ms;
these are warm local observations and do not establish a network-loading advantage.
The target eagerly loads the model/reference; cold-network cost remains a review risk.

## Screenshots and review evidence

All images are from the same 1440×900 browser smoke and were visually inspected.

- [Current Production](production-preview/current-production.png)
- [Target My Knowledge](production-preview/my-knowledge.png)
- [Target Global](production-preview/global.png)
- [Target Course](production-preview/course.png)
- [Target Project](production-preview/project.png)
- [Focused Topic group](production-preview/topic-group.png)
- [Stage 617](production-preview/stage.png)
- [Learning growth](production-preview/learning-growth.png)

## Focused validation only

| Requested check | Result / evidence |
|---|---|
| Target build | PASS isolated self-contained package and frozen current copy |
| Deterministic rebuild | PASS identical asset bytes from repeated normal-loader builds; second full package build preserves target hashes |
| My Knowledge visible IDs | PASS exact learned IDs plus independently walked primary ancestors; 31 / 52 |
| Same-depth rank | PASS maximum Category Y spread exactly **0 px** at every depth |
| No overlaps/order | PASS measured card, full sibling subtree envelope, canonical order, tray containment and route checks |
| Course behavior | PASS exact Course membership, learned-only intersection, compact and highlight |
| Project behavior | PASS exact Project/Stage requirements, UNKNOWN versus known-empty |
| Highlight does not relayout | PASS Course, Project and Stage preserve global camera/reference and layout-call count |
| One learning-growth simulation | PASS in-memory Topic 1 addition, settled layout invariants and anchor preservation |
| Global reference unchanged | PASS packaged bytes, frozen model/reference, before/after runtime geometry |
| Real Production / State / Knowledge unchanged | PASS inventories/hashes, all 31 protected/reference files match HEAD |
| One browser smoke at 1440×900 | PASS native Chromium; zero page errors, failed/external requests, non-GET requests or localStorage writes; no target page overflow; review-page navigation passes |

[Focused results](production-preview/focused-results.json),
[browser results](production-preview/browser-results.json),
[build/protected hashes](production-preview/build-results.json),
[HEAD verification](production-preview/protected-head-check.json).
No full regression, old migration suite or crash suite was run.

Protected hashes use SHA256 over sorted compact JSON mapping repo-relative filenames
to individual SHA256 values. Inventories are unchanged before and after build/smoke.

| Protected area | Aggregate SHA256 |
|---|---|
| Production — 14 files | `0b1b1f413c13f36689119c7b7115ae4bd963ff67352edfabcc72600ae037ee00` |
| State — 4 files | `7b69371cb87d3dcb880803b9698b90bf09f322152ae8f1867424557a14b22137` |
| Knowledge — 11 files | `29a3d477c5aed81e53c2bf551abcb6f41fbbf3b42d71e56a0bc7c813489d35f9` |
| Generated reference — 2 files | `fd9c00270c914bf4430b8bfe908daa68d11d0a74807ca2a236c0493087770f69` |

Global geometry individual SHA256:
`bf79e7309129421b32899900a47f1c9f47d624f2fa16a4eb8b503f1be52aab25`.

## Remaining risks and reproduction

Human acceptance is still pending. Full Course overviews remain wide; labels are
suppressed at low zoom and focus/summary/search are necessary. Canvas does not provide
the complete semantic accessibility tree. Mobile, additional browsers and cold-network
performance were outside the requested scope. This candidate changes the V6 UI:
its prerequisite/relation visualization and theme toggle are not carried over as
equivalent controls; semantic memberships/evidence remain inspectable through the
shared registry. Human review should assess that tradeoff. Local navigation/collapse
state is intentionally lost on reload. One growth scene does not establish arbitrary
bulk-growth or animation stability. A later approved apply needs its own publication
operation/rollback plan; historical strict-global receipts remain non-applicable.

From the repository root:

```sh
python3 -B prototypes/adaptive-pyramid/production-preview/build.py
node prototypes/adaptive-pyramid/production-preview/focused.cjs
python3 -B -m http.server 8765 --bind 127.0.0.1 --directory .
```

The local server was already running on port 8765 during this task and was reused.
Run the smoke with `PLAYWRIGHT_MODULE` pointing to an installed Playwright and, if
needed, `CHROMIUM_EXECUTABLE` pointing to the native installed browser:

```sh
PLAYWRIGHT_MODULE=/Users/antonplatonov/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright \
CHROMIUM_EXECUTABLE=/Users/antonplatonov/Library/Caches/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-mac-arm64/chrome-headless-shell \
node prototypes/adaptive-pyramid/production-preview/smoke.cjs
```
