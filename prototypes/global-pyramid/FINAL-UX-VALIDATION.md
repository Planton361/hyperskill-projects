# Global Pyramid — final strict-projection UX validation

Recommendation: **C. READY FOR A SEPARATELY REVIEWED PRODUCTION SPATIAL MIGRATION.**

The desktop navigation blockers found in the previous iteration are addressed. All
work stays in this read-only prototype. No Production migration, commit, push,
deploy, activation, acquisition, metadata resolution or persisted learning change
was performed. The master layout algorithm and generated artifacts are untouched.

## 1. Files changed

Modified existing files, relative to `prototypes/global-pyramid/`:

- `README.md`: final report, commands and keyboard instructions.
- `app.js`: screen labels, relevant-region cameras, summary metrics, breadcrumb
  menu, search result semantics, focus history, keyboard behavior and instrumentation.
- `index.html`: region controls, semantic legend, accessible navigation labels.
- `style.css`: desktop wrapping, focus indicators, breadcrumb/menu layout and scope accents.
- `ux.js`: pure region enumeration and observed scope metrics; no layout changes.
- `tests/browser-ux.cjs`: optional output directory for preserving historical evidence.

Added implementation/tests: `labels.js`, `tests/final-labels.cjs`,
`tests/test_final_ux.py`, `tests/browser-final.cjs`, `tests/final-ux-baseline.json`,
this report, and the evidence files in `tests/final-ux/`.
[Exact file inventory and hashes](tests/final-ux/files.json) includes all added
screenshots, console logs and rerun harness outputs. Previous reports and QA images
remain unchanged. No files outside this prototype were edited.

## 2–3. Frozen geometry hash, bytes and fingerprint

| Measurement | Before | After |
|---|---|---|
| SHA-256 | `9671e7ca5517c1f35e5ee3affac066362a2470d04ef6251cbe2faa6024572c44` | identical |
| Embedded geometry fingerprint | `0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194` | identical |
| File bytes | 3,295,568 | 3,295,568 |

Byte identity PASS. Task-start hashes are locked in
[final-ux-baseline.json](tests/final-ux-baseline.json); end comparison is in
[integrity.json](tests/final-ux/integrity.json). `build.py --check` regenerates only
in memory and verifies deterministic artifact equality. It passed without writing
any artifact. All 5 roots, 849 Categories, 3,106 structural leaf slots, 3,955
positions and 3,952 hierarchy pairs remain unchanged.

## 4. Label changes

Text wraps by measured width, in deterministic word/character order. Selected
labels get up to five lines, roots two, other labels three; ellipsis is a final
fallback. Labels use fixed priority, depth, x and numeric ID ordering. Rectangle
collision suppression and a 90-label budget avoid stacking text over neighboring
labels or unrelated large cards. Label placement is screen-space presentation only.
Full titles remain available through hover, keyboard search, breadcrumbs and the
inspector. No font/layout timing or randomness determines the order.

Overview prioritizes roots and major Categories. Medium zoom exposes relevant
branch summaries; close zoom exposes Topics/references. The real 52-character
Category title “Fundamentals of data analysis and business analytics” wraps into
exactly two complete lines at all three sizes. The longer Topic “Basic literals:
numbers, strings and characters” is also tested through global search and focus.
No severe label collisions were found in the inspected screenshots. The automated
browser guard also asserts that rendered label rectangles never overlap at every
named interaction checkpoint.

## 5. Deep breadcrumbs and Back

Deep paths show `Root > … > Parent > Current`. The middle button opens a scrollable
ancestor menu with native keyboard buttons; no taxonomy segments are discarded.
Current entity has `aria-current`, emphasis and a full accessible name. Ancestor
names have full title text when the visible button is shortened. All tested paths
fit within the desktop map width. Back restores both camera and selection.
Inspector parent/child/path buttons share the same focus handler; an inspector
parent jump and Back are explicitly browser-tested.

## 6. Relevant-region navigation

Previous / Next, a native region selector, summary buttons and Alt+Left / Right
jump to relevant branches in global horizontal order. Navigation wraps; its index
shows the current region. Regions contain explicit scope leaves and keep their
original master positions. Global offers all five real roots; other views offer
only regions containing evidence, never invented memberships. UNKNOWN Project
requirements disable region navigation and scope fitting.

## 7. My Atlas overview

Computer science is the single revealed root and its control explicitly reports
89 scope Topics. The overview identifies software development foundations,
programming languages and system administration / DevOps. The five region
summaries partition the 89 Topics: JVM 3, Dev tools 9, Computer science fundamentals
6, Java 69, Command line 2. Java has **69 scope Topics, 26 learned, 11 verified**;
the entire Atlas has **89 Topics, 31 learned, 12 verified**, plus 46 Categories.
These are counts of accepted geography and recorded observations, not inferred
coverage/progress percentages. The region sums do not double-count leaves.

The 3,820 dormant positions still retain their slots; active Topic horizontal
spread remains approximately 62.43% of the global width. Large gaps remain visible
and meaningful through corridors, faint siblings and the full-world minimap.
Fit Scope provides an overview, while a single region jump makes local reading
practical. At 1024×768 Java's overview label can be suppressed for collision,
but the Java summary/selector is immediately available and Java focus is readable.
The active nodes remain visible marks at far zoom rather than disappearing.

## 8. Course assessment

Course 8's 46 explicit Categories and 89 explicit Topics use purple scope color.
Subordinate context and the legend distinguish ancestors from explicit membership.
Green learned dots and white verified rings stay independent of Course color.
The same five region jumps and Topic-group selector make the broad spread usable.
No membership was inferred from taxonomy. Scope changes reset inspector scrolling
so the Course summary and semantics are visible even in the smallest viewport.

## 9. Project assessment

Project 113 uses amber for its 26 explicit required Topics; structural Categories
remain subordinate context. Three relevant regions summarize Dev tools 3,
Computer science fundamentals 2 and Java 21. Stage 617 has exactly 12 explicit
requirements (3 + 2 + 7), with a visibly emphasized Stage selector and named Stage
in the summary. Learning markers remain independent of requirements. Topic-group
focus gives readable local requirements without moving Topics. The other ten
Projects continue to say requirements UNKNOWN; the browser checks Project 380,
which disables Fit Scope and region navigation instead of suggesting zero.

## 10. Ghost context

Local sibling ghosts remain the default. They preserve neighboring reserved slots
at very low opacity; ancestor corridors retain orientation. Ghosts never enter
explicit scope sets or learning counts. Active-only and ancestor variants remain
available and passed the earlier UX harness again. Distant branches stay hidden
on the main scoped canvas but present on the global minimap.

## 11. Search

Search still queries the complete registry, including dormant slots. Results
separate full titles from Category / Topic / unresolved-reference identity,
active/dormant status and Course/Project relevance. Search ArrowDown reaches the
first native result button; Enter selects it. Dormant reference 333 is focused at
its existing `leaf:333` slot, outside My Atlas membership, with inspection-only
styling and explicit no-activation text. No title or Topic metadata was invented.

## 12. Minimap and fitting

The minimap always draws the persisted five-root world and hierarchy routes.
Colored scope extent, white viewport and mint focus extent share those exact world
coordinates. The legend and accessible name explain the layers. The narrow Stage
Topic-group screenshots show where the selected local branch sits in the broader
Project and complete world. Clicking pans; Enter fits the scope and arrows pan.
Fit Scope clears local selection and fits evidenced cards plus immediate parent
context; it does not attempt to remove broad spread. Fit Global remains available.

## 13. Keyboard and accessibility

Native Tab/Enter scope controls, search ArrowDown/Enter, Previous/Next and
Alt+arrows, ancestor menu/jump, inspector parent, Back and Escape were exercised at
all three sizes. Escape closes the ancestor menu first, then exits local focus.
Controls have visible amber focus outlines. Breadcrumbs/regions have navigation
group names, current breadcrumb semantics, menu expansion state, typed search
results, and canvas/minimap descriptions. At 1024×768 controls wrap without page
overflow; the inspector scrolls normally. This is basic desktop keyboard QA, not
a complete screen-reader or WCAG conformance audit.

## 14. Exact coordinate invariance

The final browser harness verifies **355,950 entity comparisons per viewport**, or
**1,067,850 total**, against the immutable master. Each comparison checks exact
x/y/width/height equality: **4,271,400 exact scalar comparisons**, maximum world
coordinate displacement **0 px**. Full master JSON and node slot, parent and
sibling-order snapshots are also compared. Each viewport runs 90 full-node checks,
including 60 repeated interaction cycles.

Checks cover Global/My Atlas/Course/Project switching, camera fitting, ghost
variants, global search, dormant/active focus, breadcrumbs, inspector parent/back,
region navigation, Stage selection, learned/verified toggle and viewport resize.
The rerun prior UX suite adds 197,127 exact coordinate comparisons; combined
final plus prior UX evidence totals **1,264,977 entity comparisons**, all 0 px.
Existing deterministic geometry, stable leaf promotion and synthetic future reveal
contracts pass unchanged. No placement search or geometry write was added.

## 15. Performance

Offline headless Chrome, device scale 1. Initialization includes static file load,
hydration and initial rendering. Each median/p95 uses 60 repeated samples per
viewport. Times below are milliseconds; heap is the practical Chrome estimate,
not a retained-allocation measurement. CPU method durations exclude the subsequent
animation-frame wait; draw includes minimap rendering.

| Viewport | Init | Draw median/p95 | Scope median/p95 | Fit median/p95 | Search median/p95 | Region median/p95 | Labels median/p95 | Heap MB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1440×900 | 69.60 | 1.40/3.60 | 0.90/1.70 | 0.00/0.10 | 0.20/0.40 | 0.40/1.80 | 0.10/0.20 | 21.66 |
| 1920×1080 | 63.80 | 1.40/3.70 | 0.90/1.70 | 0.00/0.10 | 0.20/0.40 | 0.40/1.80 | 0.10/0.20 | 12.54 |
| 1024×768 | 66.20 | 1.40/3.60 | 0.90/1.90 | 0.00/0.10 | 0.20/0.40 | 0.40/1.90 | 0.10/0.20 | 12.54 |

Global overview draws all 3,955 marks, with 12 / 16 / 8 labels at 1440 / 1920 /
1024 respectively. My Atlas overview draws 258 / 257 / 259 viewport marks:
134 explicit marks plus 124 / 123 / 125 context marks, with 4 / 4 / 3 labels.
The explicit My Atlas projection still contains all 135 entities; one ancestor
card is outside the fitted reading area. Counts measure drawn marks, not stored
Knowledge. Old recorded draw median was 1.3–1.4 ms and p95 4.9–5.0 ms; current
draw remains in that range or better. Scope calculation median rises from about
0.2 to 0.9 ms because it constructs meaningful summaries and native navigation
controls. This sub-millisecond increase is justified by the navigation gain.
No large dependencies were added.

## 16. Screenshot inventory and visual inspection

All **36** final images below were individually viewed, including the final
scope-scroll fix. The breadcrumb image intentionally repeats the deep Topic
camera to document the collapsed path. No severe text overlap or page overflow
was found. Wider views show more Category labels; smaller views suppress extra
labels but retain selected text, summaries and keyboard navigation.

| Case | 1440×900 | 1920×1080 | 1024×768 |
|---|---|---|---|
| global | [1440](tests/final-ux/1440-global.png) | [1920](tests/final-ux/1920-global.png) | [1024](tests/final-ux/1024-global.png) |
| my-overview | [1440](tests/final-ux/1440-my-overview.png) | [1920](tests/final-ux/1920-my-overview.png) | [1024](tests/final-ux/1024-my-overview.png) |
| my-java | [1440](tests/final-ux/1440-my-java.png) | [1920](tests/final-ux/1920-my-java.png) | [1024](tests/final-ux/1024-my-java.png) |
| my-region-navigation | [1440](tests/final-ux/1440-my-region-navigation.png) | [1920](tests/final-ux/1920-my-region-navigation.png) | [1024](tests/final-ux/1024-my-region-navigation.png) |
| my-deep-topic | [1440](tests/final-ux/1440-my-deep-topic.png) | [1920](tests/final-ux/1920-my-deep-topic.png) | [1024](tests/final-ux/1024-my-deep-topic.png) |
| deep-breadcrumb | [1440](tests/final-ux/1440-deep-breadcrumb.png) | [1920](tests/final-ux/1920-deep-breadcrumb.png) | [1024](tests/final-ux/1024-deep-breadcrumb.png) |
| course-8 | [1440](tests/final-ux/1440-course-8.png) | [1920](tests/final-ux/1920-course-8.png) | [1024](tests/final-ux/1024-course-8.png) |
| project-113 | [1440](tests/final-ux/1440-project-113.png) | [1920](tests/final-ux/1920-project-113.png) | [1024](tests/final-ux/1024-project-113.png) |
| stage-617 | [1440](tests/final-ux/1440-stage-617.png) | [1920](tests/final-ux/1920-stage-617.png) | [1024](tests/final-ux/1024-stage-617.png) |
| minimap-narrow | [1440](tests/final-ux/1440-minimap-narrow.png) | [1920](tests/final-ux/1920-minimap-narrow.png) | [1024](tests/final-ux/1024-minimap-narrow.png) |
| dormant-reference | [1440](tests/final-ux/1440-dormant-reference.png) | [1920](tests/final-ux/1920-dormant-reference.png) | [1024](tests/final-ux/1024-dormant-reference.png) |
| long-label | [1440](tests/final-ux/1440-long-label.png) | [1920](tests/final-ux/1920-long-label.png) | [1024](tests/final-ux/1024-long-label.png) |

## 17. Tests

- All global-pyramid Python contracts: **11 passed**; includes exact counts,
  deterministic repeated generation, promotion/reveal invariance, pure UX/label
  checks, frozen artifact guard and full protected-directory hash guard.
- Final browser QA: **all three viewports passed**, zero script errors, external
  requests or browser storage writes; native keyboard interactions and collision
  guards pass. [Raw measurements](tests/final-ux/browser-results.json).
- Original browser smoke: **PASS**. [Results](tests/final-ux/legacy-smoke/browser-results.json).
- Previous UX harness: **all three viewports PASS**.
  [Results](tests/final-ux/prior-ux/browser-results.json).
- Deterministic artifact check: **PASS**, byte identity retained.
- Global Catalog regression: **27 passed, 1 skipped** (optional HAR fixture absent).
- Production Knowledge Map regression: **9 passed**. Broader regression was run
  once after implementation; it does not perform real activation.

Console evidence: [prototype](tests/final-ux/test-console.txt),
[Catalog](tests/final-ux/catalog-regression.txt),
[Production](tests/final-ux/production-regression.txt),
[final browser](tests/final-ux/browser-console.txt).

## 18. Protected Production / State / Knowledge hashes

Every protected file hash and directory inventory match the task-start record:
**29/29 unchanged, no additions or deletions**. Below, group hashes are SHA-256 of
compact sorted JSON mapping relative filenames to SHA-256 bytes; the full per-file
before/after mappings are in [integrity.json](tests/final-ux/integrity.json).

| Protected directory | Files | Before = after |
|---|---:|---|
| `data/knowledge` | 11 | `29a3d477c5aed81e53c2bf551abcb6f41fbbf3b42d71e56a0bc7c813489d35f9` |
| `docs/knowledge-map` | 14 | `0b1b1f413c13f36689119c7b7115ae4bd963ff67352edfabcc72600ae037ee00` |
| `state/knowledge-atlas` | 4 | `7b69371cb87d3dcb880803b9698b90bf09f322152ae8f1867424557a14b22137` |

ACTIVE_HISTORY remains 46 Categories + 89 Topics, Generation 0. No activation
state, presentation_generation, Production checkpoint, accepted fact or progress
observation was changed. Geometry in generated artifacts is also unchanged.

## 19. Remaining problems

Strict spread is intentional: an overview cannot display every Topic title. At
1024×768 collision suppression hides more local labels and the side inspector
needs scrolling; selecting/searching a Topic always provides its full title.
Tiny roots at global scale have vertically separated label callouts. Manual zoom
can put parts of cards behind the toolbar, while selected labels remain in the
reading area. These are presentation tradeoffs, not navigation or world-coordinate
blockers. Font metrics can differ across platforms, so the deterministic rule is
for identical fonts and viewport. Mobile, a full screen-reader audit and evidence
for unknown Projects remain outside this desktop prototype's validation.

## 20. Final recommendation

**C. READY FOR A SEPARATELY REVIEWED PRODUCTION SPATIAL MIGRATION.**

My Atlas is understandable despite fixed global coordinates. Its root and revealed
regions are explicit; region jumps make empty-space traversal practical. Course
and Project views are readable through local focus without moving Topics. Semantic
zoom prevents label overload; dormant content can be located without activation.
The remaining desktop issues are cosmetic and density tradeoffs. This recommends
a later separately reviewed migration, and does not perform or authorize one here.
