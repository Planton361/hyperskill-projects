# Global Canonical Pyramid — Version A: validation report

Baseline main: `b666e28d326e25c1ac8dca03aafe149798fa2a84`.
Implemented only under `prototypes/global-pyramid/`. No commit, push or deployment.

## 1. Architecture

Existing `global-atlas/build.py` supplies the read-only Catalog projection;
its Course and Project APIs, accepted history join and evidence semantics are
reused unchanged. A separate taxonomy-only Python generator writes the master
geometry once. The Canvas browser hydrates it, deep-freezes the artifact and
locks node coordinates against assignment. There is no runtime layout API.
Global, My Atlas, Course and Project are visibility/style projections of the
same slots. Camera pan, zoom and focus change screen transforms only.
The existing treemap prototype and V6 Production remain unchanged.

## 2. Files

Every file added by this task is listed in the manifest at the end. No existing
repository file was changed. Existing unrelated untracked work was preserved.

## 3. Exact inventory

Five roots, 849 Categories, 3,106 structural leaves, 3,955 physical positions,
3,952 real hierarchy pairs. Leaf memberships number 3,108; Categories contribute
844 pairs. Semantic leaves are 89 Topics and 3,017 unresolved references;
resolution is 1 RESOLVED_TOPIC, 88 PARTIAL_TOPIC, 3,017 UNRESOLVED_REFERENCE.
The presentation anchor adds no Knowledge/Catalog position. There are 3,955
primary routes including five presentation-anchor routes; secondary memberships
remain separate rather than duplicating physical leaves.

## 4. Algorithm

Structural Category depth selects a primary parent: deepest structural parent,
then lowest numeric Category ID. Categories and leaves each sort by numeric ID.
For each Category, measure child Category subtrees bottom-up; reserve a 260-unit
leaf tray if needed, 64-unit horizontal gaps and at least 300 units of width.
Category cards are fixed 280 × 80; leaf cards are fixed 240 × 32, 40 units apart
in their tray. Titles and metadata never determine these measurements.
The child gap is `max(160, subtree_width // 8)`, giving broad branches additional
vertical separation. Center the parent above its allocated region; place the
leaf tray followed by child Category regions from left to right. This is a
hierarchical width-reservation algorithm, without search, randomness or force.
Orthogonal Category buses and leaf tray-side rails are generated and persisted.
Primary and secondary parents are both above their children on this capture.

The artifact stores schema/algorithm versions, taxonomy fingerprint, anchor,
root sectors, exact integer positions, regions, depths, ordering, memberships,
primary parents, secondary memberships, identity aliases, routes, bounds and a
geometry fingerprint. The taxonomy fingerprint excludes titles, Topic resolution,
accepted semantic parent metadata, Course, Project and personal data.
Geometry fingerprint: `0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194`.
Repeated generation is byte-identical, including after input entity reordering.

## 5. Stable leaf identity

`category:<id>` identifies Category geometry; `leaf:<id>` identifies structural
leaf geometry. `leaf_identity_mapping` explicitly stores both `reference:<id>`
and `topic:<id>` aliases for each slot. These aliases are geometry mappings,
not claims that unresolved Topics exist. Unresolved semantic records retain no
invented title, URL or theory. The inspector labels them as unresolved IDs.
The mandatory fixture uses Catalog's validated `promote_reference` API for ID
333. Its resolution becomes PARTIAL_TOPIC; memberships are preserved. The new
semantic Topic still joins `leaf:333`, and the entire geometry remains
byte-identical, beyond merely preserving that slot's coordinates.

## 6. Five-root arrangement

Presentation-only `presentation:hyperskill` sits above five disjoint sectors.
Numeric root ordering is Math (525), Computer science (1162), Natural science
(2148), Product development (3051), Generative AI (4055). Each sector gets its
measured subtree width, with an 800-unit gap to the next sector. Root navigation,
colored sector silhouettes, screen-space root labels and a minimap identify them.
The anchor exists only in this prototype geometry; no entity, membership or fact
is persisted to Knowledge. Overall bounds are 262,860 × 44,551 units.

## 7. Screenshots and visual findings

All images were captured and visually inspected at 1440 × 900:

| View | Screenshot | Finding |
| --- | --- | --- |
| Full Global | [global-overview.png](tests/global-overview.png) | Top-down buses and widening branch silhouettes communicate hierarchy; most cards are subpixel marks. Root labels are readable. |
| Computer science | [computer-science.png](tests/computer-science.png) | Dominant sector consumes most global width; focus exposes its branching outline, not individual labels. |
| My Atlas strict | [my-atlas.png](tests/my-atlas.png) | Active branches are visible at global positions, but gaps dominate and overview labels disappear. |
| My Atlas Java focus | [my-atlas-java-focus.png](tests/my-atlas-java-focus.png) | Branch shape improves; this broad focus still needs more zoom to read cards. |
| Course 8 | [course-8.png](tests/course-8.png) | Same 135 positions as accepted history on current evidence. |
| Project 113 | [project-113.png](tests/project-113.png) | 26 requirement Topics plus ancestor context; overview remains scattered. |
| Stage 617 | [project-stage.png](tests/project-stage.png) | 12 incremental requirements, 26 explicitly recorded cumulative Topics; still sparse. |
| Deep branch | [deep-branch.png](tests/deep-branch.png) | Category 2930 and reserved child 2931 are readable and connected. |
| Unresolved slot | [unresolved-focus.png](tests/unresolved-focus.png) | Reference 333 has a clear reserved card and explicit `leaf:333` mapping, without invented Topic metadata. |

[deep-focus.png](tests/deep-focus.png) additionally shows the depth-eight slot.
The renderer uses tiny screen-space marks at low zoom and full cards when
focused; persisted widths and heights never change. Root/child/path buttons,
search and camera history are necessary navigation, not optional polish.

## 8. Strict My Atlas findings

Accepted history is exactly 46 Categories + 89 Topics. Structural ancestor
closure currently adds no extra identities, giving 135 visible positions.
Global-to-personal orientation is mechanically exact: switching scope at a fixed
camera leaves every visible card in place. The minimap preserves world context.
Visual orientation is weaker at overview scale because labels are too small;
individual branch/slot focus and inspectors are readable. This projection is
correct but is not an attractive default personal overview.

## 9. Empty-space amount and pattern

3,820 of 3,955 positions are hidden (96.5866%). The active leaf bounding box
spans 164,108 horizontal units, or 62.4317% of global width. There are 2,379
hidden structural positions inside that horizontal span. Active cards occupy
0.023125% of the full visible-entity bounding rectangle; 99.976875% is non-card
area, including connector/structural spacing. This last metric measures area,
not simply the fraction of dormant slots. Empty space is concentrated between
separate active branches and long ancestor-to-descendant buses, rather than
being uniform padding around individual cards. No space was compacted.

## 10–11. Activation and exact displacement

Two disposable in-memory reveals begin with ACTIVE_HISTORY, first revealing
reference 333 / Category 428, then reference 2931 / Category 2930. They look up
already reserved slots; no placement search or geometry generation runs.
Every previously visible entity preserves exact x, y, width and height after
each reveal, including the first reveal's entities during the second reveal.
Maximum displacement: **0 px**, both rounds. Browser scope tests perform
64,080 exact coordinate comparisons; Node core tests perform another 4,272.
All shared Global/My Atlas/Course/Project coordinates compare exactly.
Learned/verified changes preserve geometry. Completion adds no learned,
verified or applied assertion. Current personal state remains 31 learned /
12 verified. All ten other Projects retain requirements UNKNOWN.

## 12. Performance

Local Python and headless Chromium 154 measurements; external dependencies,
no new project dependency. Browser samples use offline route interception and
60 scope/search cycles. Timings are observations, not service guarantees.

| Metric | Result |
| --- | ---: |
| Existing source load + projection | 1220.73 ms |
| Taxonomy layout + fingerprint | 28.40 ms |
| Geometry encoding | 9.85 ms |
| Total measured build | 1258.99 ms |
| Geometry bytes | 3,295,568 |
| Semantic catalog bytes | 1,976,924 |
| Browser fetch/parse | 40.10 ms |
| Browser hydration/indexing | 16.30 ms |
| Initialization before scheduled paint | 62.30 ms |
| Initial Global draw | 3.20 ms |
| Draw median / p95 | 0.60 / 2.30 ms |
| Search median / p95 | 0.20 / 0.40 ms |
| Scope computation median / p95 | 0.00 / 0.20 ms |
| Scope through two animation frames p95 | 33.20 ms |
| Estimated JS heap | 20,398,599 bytes |
| DOM elements in measured focus | 78 |

Heap excludes native Canvas/GPU memory. Scope computation timing excludes
selector reconstruction; the scope-to-paint measurement includes public scope
switching and deliberately waits two frames.

## 13. Tests

Six focused Python contracts pass, including their Node runtime suite. Browser
QA passes with no page errors, external requests or persistent browser storage.
Contracts cover baseline counts/resolution/state, roots, unique slots/aliases,
primary/secondary membership, parent above child, region containment, no card
or root-sector overlap, ordering, deterministic bytes, semantic/progress
independence, valid promotion, frozen geometry, absence of runtime layout,
all scope coordinates, two future reveals and protected file hashes.
See [test-console.txt](tests/test-console.txt),
[browser-results.json](tests/browser-results.json), and
[validation.json](tests/validation.json).

## 14. Production / State / Knowledge hash comparison

All 29 files across `docs/knowledge-map/`, `state/knowledge-atlas/` and
`data/knowledge/` match before/after SHA-256 and the specified main baseline.
Changed protected files: **0**. History version 0, layout generation 0, events
empty. Full per-file hashes are in [integrity.json](tests/integrity.json).
No activation APIs or Production builders were called.

## 15. Limitations

The captured taxonomy is complete for this experiment, not a guarantee about
future Hyperskill structure. Newly discovered IDs have no reserved location;
future structural changes would need an explicit geometry version/review policy.
Fixed cards truncate long titles; full metadata remains in the inspector.
Lowest-zoom cards are tiny marks. Computer science dominates the forest's
horizontal allocation, making the four smaller roots less legible in overview.
Large scope gaps and absence of broad-scope labels remain unresolved usability
problems. Secondary connectors are optional selected-node overlays and are not
obstacle-optimized. This is not a production package or responsive-device audit.

## 16. Recommendation

The **master-geometry architecture is proven**: every captured Category/leaf has
a deterministic existing position, all scopes reuse it, and revealing known
entities causes exactly zero displacement. Keep this as a reference prototype.
**Do not adopt this exact geometry as Production's spatial authority yet.**
The broad personal projection is too sparse and requires too much navigation.
Further taxonomy-only layout and semantic navigation experiments should be
visually reviewed before freezing a long-term authority. Such experiments must
retain stable leaf identity and scope invariance; Production migration remains
a separate explicitly reviewed task.

## Exact added-file manifest

- `DESIGN-VALIDATION.md`
- `README.md`
- `app.js`
- `atlas.js`
- `build.py`
- `generated/catalog.json`
- `generated/global-geometry.json`
- `index.html`
- `style.css`
- `tests/browser-results.json`
- `tests/browser.cjs`
- `tests/computer-science.png`
- `tests/core.cjs`
- `tests/course-8.png`
- `tests/deep-branch.png`
- `tests/deep-focus.png`
- `tests/global-overview.png`
- `tests/integrity.json`
- `tests/measure.py`
- `tests/my-atlas-java-focus.png`
- `tests/my-atlas.png`
- `tests/project-113.png`
- `tests/project-stage.png`
- `tests/test-console.txt`
- `tests/test_model.py`
- `tests/unresolved-focus.png`
- `tests/validation.json`
