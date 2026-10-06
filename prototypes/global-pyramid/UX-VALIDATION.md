# Global Pyramid UX — Strict Projection Refinement

Presentation-only refinement of the established master geography. No commit,
push, deployment, real activation, metadata resolution or acquisition occurred.
The first phase's [DESIGN-VALIDATION.md](DESIGN-VALIDATION.md) remains a historical
report; this document describes the current UX.

## Geometry and protected state

The exact master artifact was hashed before any UX edit. Before and after:

```text
SHA-256: 9671e7ca5517c1f35e5ee3affac066362a2470d04ef6251cbe2faa6024572c44
Geometry fingerprint: 0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194
Artifact bytes: 3,295,568
```

The artifact, source builder, Catalog projection and geometry index are unchanged.
No x/y/width/height, slot, ordering, primary parent, root sector or route changed.
The artifact remains deep-frozen; hydrated node coordinates remain non-writable.
The inventory remains 5 roots, 849 Categories, 3,106 structural leaf slots,
3,955 positions and 3,952 hierarchy pairs. There is no runtime layout API.

All 29 protected files under `docs/knowledge-map/`, `state/knowledge-atlas/` and
`data/knowledge/` have identical before/after hashes and match the main baseline.
ACTIVE_HISTORY stays 46 Categories / 89 Topics; generation and history stay 0.
Progress stays 31 learned / 12 verified. Project 113 stays 26 requirements / 5
loaded Stages; Stage 617 has 12 explicit requirements. The ten unloaded Projects
remain UNKNOWN. No project completion inference was added.

The pre-edit record is [tests/ux-baseline.json](tests/ux-baseline.json).
The final full-file comparison and exact change manifest are
[tests/ux/integrity.json](tests/ux/integrity.json) and
[tests/ux/files.json](tests/ux/files.json).

## Presentation changes

`ux.js` contains pure scope/context and camera helpers. It separates explicit
Course/Project membership from structural ancestor context. Ancestors never
become Course/Project members. Scope geometry is always joined from existing
slots, not calculated. A synthetic Course with reference 333 as its only member
checks that ancestor closure stays context rather than explicit membership.

The renderer gives scoped nodes normal opacity and a scope color: blue for My
Atlas, purple for Course, amber for Project. Learned Topics get green dots and
verified Topics white rings, keeping the scope color distinct. This personal
layer starts enabled and is optional. Rounded close-zoom cards and tiny far-zoom
marks are rendering styles over unchanged world rectangles.

Scope summaries expose exact counts and UNKNOWN evidence. Branch buttons and a
Topic-group selector let users jump from an overview to a readable local group.
Breadcrumbs show the real primary global path and offer parent focus. Inspector
child navigation prioritizes currently relevant children; dormant metadata can
still be inspected through search and Global navigation.

## Ghost policy and active corridors

Three variants were captured at identical cameras:

- A, active only: explicit nodes; hierarchy corridors remain because location
  context is required in every scoped view.
- B, ancestors: A plus non-explicit ancestors at 0.30 opacity.
- C, local siblings: B plus the immediate primary-tree siblings of corridor
  nodes, at 0.085 opacity; ghost connectors use 0.07 opacity. No recursive ghost
  expansion or distant subtree reveal occurs. Viewport culling further limits it.

C is the selected default. At 1440×900 it adds approximately 124 subtle context
marks to the My Atlas overview while keeping 135 accepted identities unchanged.
A and B happen to look alike for current My Atlas: its ancestors are already
accepted entities. They differ for Project and synthetic Course context. The
additional local siblings make the reserved gaps perceptible without presenting
all 3,955 positions equally strongly. Ghosts are never Knowledge state.

Bright active corridors and subdued ghost corridors exclusively paint existing
`hierarchy_routes`. No new routes are constructed. The old ad hoc secondary
membership line overlay was removed; secondary memberships remain in the
inspector. Focusing a dormant entity paints that exact slot as inspection context
with a dashed outline, without changing explicit membership or accepted history.

## Camera fitting and focus

Fit Global uses immutable world bounds. Fit My Atlas / Course / Project uses
relevant leaves and their immediate structural parents. This includes useful
local ancestor context without letting root-to-leaf distance dominate every fit.
Ancestor corridors continue to the real global roots outside the viewport, and
the complete-world minimap shows their location. It is a camera choice, not a
claim that distant ancestors disappeared from the world.

Selected active branch focus fits its relevant cards plus the selected parent,
not its entire dormant allocated region. Dormant branch focus uses its existing
region; single-entity focus uses the existing card rectangle. All relevant
positions remain within the selected global branch. No hidden-space compaction,
new coordinate, placement search or scope-specific packing occurs.

Scope switching preserves the camera synchronously; Fit is an explicit action.
Camera history, pan, wheel/button/keyboard zoom and minimap navigation remain.
Viewport resizing preserves the camera's world center. Desktop page height now
accounts for wrapping Course/Stage controls at 1024×768, keeping the minimap in
view. Fit UNKNOWN is disabled and never implies zero requirements.

Fit Scope helps orient broad scopes but cannot make all widely separated Topic
labels simultaneously readable. Direct branch/Topic-group focus is essential.

## Minimap and semantic zoom

The minimap always paints all five global sectors and the complete persisted
hierarchy. It overlays explicit scope marks, dashed scope extent, a green focused
branch/slot outline and the white viewport rectangle. Its coordinate transform
always uses global bounds. The scope extent uses the same relevant/local-parent
bounds as Fit Scope. Tiny extents receive a minimum screen-space outline for
visibility, without changing any world bounds.

Far zoom shows five root names, selected major Categories and scoped Topic-count
callouts anchored to their actual world cards. Medium zoom introduces relevant
Category names and group counts. At close zoom, Topic titles, unresolved IDs and
fine Category labels become readable. Labels have deterministic priority,
collision rejection and a hard 90-label budget. Long labels truncate; the full
text remains in search/inspectors. Callout offsets and screen-size glyphs are
presentation only. Root callouts reserve separate rows at small desktop widths.

## Search and dormant inspection

Search still scans the complete global registry, regardless of scope. Results
include active/dormant status, explicit Course-8 relevance, explicit Project-113
relevance and unresolved-reference status where applicable. Titles and semantic
IDs remain metadata; leaf slot IDs are also searchable. Search exposes at most
40 results and asks users to refine larger result sets.

Selecting reference 333 from My Atlas focuses `leaf:333` and paints it as an
inspected dormant slot. Accepted and scoped membership do not change. The
breadcrumb includes Computer science → Programming languages → Python → Basics
→ Simple programs. Deep active Topic 78 is likewise readable at its master slot.

## Explicit visual acceptance answers

1. **Does My Atlas remain understandable?** Yes as a branch overview: labels,
   counts, learning marks and navigation now identify its major revealed areas.
   Individual Topics require branch/group focus.
2. **Is its location in the full pyramid obvious?** Yes, through the permanent
   global minimap, root navigation, actual-path breadcrumbs and fixed-camera
   switching between Global and scoped views.
3. **Is the empty space acceptable?** For exploration with context, yes; for a
   dense all-Topics-at-once dashboard, no. The 62.43% global-width span is unchanged.
4. **Which ghost strategy works best?** C, ancestor plus local sibling context;
   very faint one-hop ghosts balance orientation and emphasis. A is useful when
   concentrating on a familiar group; B adds little to current My Atlas.
5. **Does Fit Scope sufficiently solve broad spread?** No by itself. It frames
   the true extent, but cannot overcome global spacing. Group focus complements it.
6. **Is Project Focus readable without moving Topics?** Yes in narrow Topic
   groups. Project and Stage overviews identify contextual branches and exact
   requirement counts, but do not show every Topic title at once.
7. **Is Course readable without moving Topics?** Yes as an overview plus branch/
   Topic-group navigation. Purple membership styling remains distinct from learning.
8. **Does semantic zoom prevent label overload?** Yes: priority, collisions and
   the 90-label cap are enforced. Sparse overview labels are intentional.
9. **Can dormant references be located without activation?** Yes; browser QA
   searches and focuses reference 333 while asserting it stays outside My Atlas.
10. **Is this enough for Production migration?** Not yet. Recommend **iterate
    once more**, preserving this exact master geometry. Focus the next review on
    label completeness, narrow-group reading and orientation for smaller roots.

## Browser QA and screenshots

The existing offline Playwright infrastructure runs at 1440×900, 1920×1080 and
1024×768, without external requests, persistent browser state or new dependencies.
Every listed scene was captured at each viewport. Representative images were
visually inspected across all three sizes; all required scenes were inspected.

| Scene | 1440×900 | 1920×1080 | 1024×768 |
| --- | --- | --- | --- |
| Global overview | [1440](tests/ux/1440-global.png) | [1920](tests/ux/1920-global.png) | [1024](tests/ux/1024-global.png) |
| My Atlas default | [1440](tests/ux/1440-my-default.png) | [1920](tests/ux/1920-my-default.png) | [1024](tests/ux/1024-my-default.png) |
| My Atlas ghost geography | [1440](tests/ux/1440-my-ghosts.png) | [1920](tests/ux/1920-my-ghosts.png) | [1024](tests/ux/1024-my-ghosts.png) |
| My Atlas Java focus | [1440](tests/ux/1440-my-java.png) | [1920](tests/ux/1920-my-java.png) | [1024](tests/ux/1024-my-java.png) |
| Course 8 | [1440](tests/ux/1440-course-8.png) | [1920](tests/ux/1920-course-8.png) | [1024](tests/ux/1024-course-8.png) |
| Project 113 | [1440](tests/ux/1440-project-113.png) | [1920](tests/ux/1920-project-113.png) | [1024](tests/ux/1024-project-113.png) |
| Stage 617 | [1440](tests/ux/1440-stage-617.png) | [1920](tests/ux/1920-stage-617.png) | [1024](tests/ux/1024-stage-617.png) |
| Dormant unresolved reference | [1440](tests/ux/1440-dormant-reference.png) | [1920](tests/ux/1920-dormant-reference.png) | [1024](tests/ux/1024-dormant-reference.png) |
| Deep active Topic | [1440](tests/ux/1440-deep-active-topic.png) | [1920](tests/ux/1920-deep-active-topic.png) | [1024](tests/ux/1024-deep-active-topic.png) |
| Narrow Project minimap | [1440](tests/ux/1440-minimap-narrow-project.png) | [1920](tests/ux/1920-minimap-narrow-project.png) | [1024](tests/ux/1024-minimap-narrow-project.png) |
| Project Topic group | [1440](tests/ux/1440-project-topic-group.png) | [1920](tests/ux/1920-project-topic-group.png) | [1024](tests/ux/1024-project-topic-group.png) |
| UNKNOWN Project | [1440](tests/ux/1440-unknown-project.png) | [1920](tests/ux/1920-unknown-project.png) | [1024](tests/ux/1024-unknown-project.png) |
| Variant A active only | [1440](tests/ux/1440-my-active-only.png) | [1920](tests/ux/1920-my-active-only.png) | [1024](tests/ux/1024-my-active-only.png) |
| Variant B ancestors | [1440](tests/ux/1440-my-ancestors.png) | [1920](tests/ux/1920-my-ancestors.png) | [1024](tests/ux/1024-my-ancestors.png) |

## Measurements and performance assessment

Local Chromium 154, offline route interception, device scale 1; 60 repeated
search/scope/fit cycles at each viewport. Draw timing includes the full Canvas
map and minimap. Scope timing includes summary and selector reconstruction;
Fit Scope includes bounds calculation and camera setup but not the next paint.
Heap is Chromium's JS estimate and excludes native Canvas/GPU memory.

| Viewport | Init ms | Draw median / p95 ms | Fit median / p95 ms | Scope median / p95 ms | Search median / p95 ms | Global marks / labels | My marks / context / labels | JS heap MB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1440 × 900 | 70.70 | 1.30 / 4.90 | 0.00 / 0.10 | 0.20 / 1.50 | 0.20 / 0.30 | 3955 / 12 | 258 / 124 / 5 | 21.36 |
| 1920 × 1080 | 64.10 | 1.40 / 5.00 | 0.00 / 0.10 | 0.20 / 1.50 | 0.20 / 0.30 | 3955 / 15 | 257 / 123 / 5 | 21.34 |
| 1024 × 768 | 63.70 | 1.30 / 5.00 | 0.00 / 0.10 | 0.20 / 1.50 | 0.20 / 0.30 | 3955 / 10 | 259 / 125 / 3 | 17.94 |

My visible counts exclude offscreen accepted ancestors and include presentation
ghosts; accepted membership remains exactly 135. At 1440, variants A/B paint
134 accepted marks and C paints 258 total marks, including 124 context marks.
At 1920 C paints 257; at 1024 C paints 259. The stronger context, label callouts,
minimap, scope summaries and local focus justify the modest draw increase from
the first phase's 2.3 ms p95 to roughly 5 ms p95. Initialization remains near
70 ms. Search and Fit remain sub-millisecond at p95; scope switching stays
within a few milliseconds. The existing smoke's measured deep-focus DOM count
is 103, under its original 200-element guard.

Exact results: [tests/ux/browser-results.json](tests/ux/browser-results.json).

## Tests, integrity and displacement

- Existing six global-pyramid contracts plus two new UX contracts: **8 passed**.
  They include existing activation simulations, valid reference promotion and
  deterministic bytes; UX helpers test cameras, ghosts, membership boundaries,
  UNKNOWN scopes and dormant inspection.
- New three-viewport browser QA: **passed**, including all screenshot scenes,
  exact Stage 617 membership, progress/ghost toggles, search, focus, back, minimap,
  keyboard pan, zoom, repeated operations, zero storage/network leakage, bounded
  labels, all five root labels, and no horizontal/vertical desktop overflow.
- **197,127** exact coordinate comparisons across the new browser suite. Complete
  master JSON and hydrated node slot/position/parent/order snapshots compare
  identically before/after every viewport's operation sequence.
- Existing browser smoke: **passed**, with **64,080** coordinate comparisons and
  its original performance, DOM, interaction and semantic guards. Its output now
  supports an isolated destination; prior phase screenshot/results artifacts
  are preserved.
- Global Catalog regression: **28 tests**, **27 passed / 1 skipped**. The skip is
  the optional real-HAR fixture; no acquisition was needed.
- Knowledge Map regression: **9 passed**, including in-memory rebuilding and
  byte-verification of the installed Production package. Broader regressions
  ran once after the presentation implementation was stable.
- `build.py --check`: **passed**, read-only deterministic artifact comparison.
- Master SHA-256 and embedded fingerprint: **identical** before/after.
- Protected Production/State/Knowledge changes: **0 of 29 files**.
- Exact world-coordinate displacement: **0 px**. Future reveal tests still pass.

Logs: [test-console.txt](tests/ux/test-console.txt),
[catalog-regression.txt](tests/ux/catalog-regression.txt),
[production-regression.txt](tests/ux/production-regression.txt),
[legacy-smoke-console.txt](tests/ux/legacy-smoke-console.txt).

## Remaining UX problems and recommendation

My Atlas is substantially more useful than the unlabeled sparse first phase,
but broad scopes still require navigation. Callout collisions can suppress
useful group labels, especially at 1024. Long names truncate. Deep breadcrumbs
can wrap into the reading area. Tiny minimap focus outlines need further clarity.
The four smaller roots still receive much less world width than Computer
science, although all five names and root buttons remain available. Context
ancestors must not be mistaken for explicit Project requirements; subdued
labels and inspector wording help, but merit further user review.

Recommendation: **iterate once more** on label prioritization, group reading and
minimap/breadcrumb clarity. Keep this exact geometry frozen. The strict projection
architecture and zero-displacement promise remain proven; no Production spatial
migration is authorized or recommended as part of this task.

## Exact changed files

All changes are below `prototypes/global-pyramid/`. Existing files modified:

- `README.md`
- `app.js`
- `index.html`
- `style.css`
- `tests/browser.cjs`

New source/tests/report files:

- `ux.js`
- `UX-VALIDATION.md`
- `tests/ux.cjs`
- `tests/test_ux.py`
- `tests/browser-ux.cjs`
- `tests/ux-baseline.json`

New screenshot, measurement, integrity and regression-log artifacts are all in
`tests/ux/`; [files.json](tests/ux/files.json) lists every exact file path added
or modified against the pre-edit prototype hashes. No existing file outside
this prototype was changed.
