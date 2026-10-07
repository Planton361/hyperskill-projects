# Generic V6.6 Scope Pyramid — prototype

This report records the prototype run before the development checkpoint. See
[SCOPE-PYRAMID-ACCEPTED.md](SCOPE-PYRAMID-ACCEPTED.md) and
[checkpoint validation](tests/checkpoint-validation.json) for current checkpoint status.

**C — GENERIC SCOPE PYRAMID PROVEN**

One projection/layout engine renders Course 8, Project 113 and Stage 617 from their existing explicit evidence. All eight required real/synthetic cases pass the focused invariants. This verdict applies to the bounded prototype and the measured desktop viewport, not to arbitrary-scale optimality or production readiness.

Local preview: [Course 8](http://127.0.0.1:8810/prototypes/knowledge-atlas-scope-pyramid/?scope=course), [Project 113](http://127.0.0.1:8810/prototypes/knowledge-atlas-scope-pyramid/?scope=project), [Stage 617](http://127.0.0.1:8810/prototypes/knowledge-atlas-scope-pyramid/?scope=stage).

## Scope projection model

`ScopePyramid(scope_type, scope_id, explicit_topic_ids, explicit_category_ids, global_catalog, measure)` returns `{projection, m, L}`. `measure` is the browser text-measurement dependency. The first five arguments are semantic input; `L` is disposable local geometry.

`projection.js` deduplicates/sorts explicit numeric IDs, verifies they exist, then walks every structural Category membership upward. Its pure output contains explicit Topic IDs, explicit Category IDs, context Category IDs, used roots, the complete induced membership hierarchy and an identity-to-identical-identity map. It contains no positions, sizes, routing, camera, checkpoint or layout score. The checked semantic JSON files in `tests/` demonstrate this separation.

Closure is minimal for the supplied memberships: only ancestors of explicit Topics/Categories are admitted. An explicit Category never causes descendant Topics to become members. Categories carry `explicit` or `context` roles in the render model. The 46 explicit Course Categories already contain their entire required ancestor closure, so Course 8 needs zero additional context Categories. Project and Stage have no explicit Category membership; all their Categories are context.

The presentation root is `presentation:<scope_type>:<scope_id>`, has type `context`, and is absent from the semantic identity map and taxonomy hierarchy. Only used Global roots are attached beneath it. All three real scopes use one root; disposable cross-root tests use five.

Canonical physical ownership uses the same rule as Global: use the accepted canonical parent if it is an actual membership; otherwise the first canonical numeric membership. Every semantic Topic renders once. Secondary memberships remain in `projection.hierarchy` and Inspector navigation, and Category coverage counts distinct Topics over all memberships. For example, Topic 36 is physically under Operations on primitive types while also retaining its Data types and variables membership. That secondary context Category remains visible and navigable without duplicating the Topic or inventing scope membership. Physical connectors form the canonical ownership tree, as in the Global foundation; they do not draw a second row for secondary memberships.

## Foundation and evidence

`build.py` reads the current full-title Global model without rebuilding or modifying it. `tests/source.json` records its SHA-256 and observation identifiers. The isolated `catalog.json` is a read-only input snapshot: **849 Categories, 3,106 titled Topics, zero unresolved references, 31 learned and 12 verified**.

`scopes.json` contains only these accepted seeds:

- Course 8: `data/knowledge/courses.json`, 89 explicit Topic IDs and 46 explicit Category IDs.
- Project 113: dedicated `project_requires` edges from `data/knowledge/edges.json`, 26 distinct requirements.
- Stage 617: `required_topic_ids` from `data/knowledge/stages.json`, 12 requirements. The cumulative stage list is not used as stage membership.

No API requests, bulk acquisition, completion-based membership inference, or progress inference occurred.

## Algorithm and packing/scoring model

`layout.js` is the one layout implementation. It derives V6.6 Category measurement, complete column-major Topic trays, occupied contours, separate `cardBounds`/`subtreeBounds`, local sibling alignment and short orthogonal buses from the current Global implementation. `routing.js` is copied unchanged from that foundation; `style.css` retains its V6.6 visual language. The prototype uses SVG at this scope size rather than the Global tiled renderer.

The bottom-up planner retains several useful shapes for each subtree instead of forcing every subtree to its own preferred aspect ratio. This prevents an individually compact child choice from imposing a poor shape on the parent.

1. Measure full titles with browser Canvas `system-ui`: 14 px Topics, 17 px Categories, 21 px used roots, 28 px presentation root. Category line spacing is 1.3× font size so SVG font bounds do not overlap. Topic line spacing remains 17 px. Cards expand for unbreakable text; nothing is truncated.
2. For each complete tray evaluate 1/2/3/4 columns where possible and preferred row widths 160/200/240. Existing width expansion handles long titles. Column-major flattening always preserves numeric Topic order.
3. Build occupied contours from Category cards, complete tray rectangles and reserved routing corridors. Pack sibling anchors left-to-right only as far apart as those contours require. There is no global same-depth row.
4. For broad sets (at least three child modules), evaluate one row plus deterministic contiguous partitions targeting two, three and four rows. Numeric Category order is preserved left-to-right, then top-to-bottom. Each module is a complete subtree; no hierarchy is dropped or hidden.
5. Keep at most two best shapes per aspect profile (0.6, 1, 1.6, 2, 2.5, 4, 7), deduplicated by bounds. A bounded beam combines child shapes as siblings are added. Parents can choose different child orientations. The final presentation-root score uses aspect 2, near the useful desktop canvas aspect; it is not scope-specific.
6. Materialize the winning nested plan once. Route from parent-card boundaries through the reserved buses/spines to child-card or complete-tray boundaries. Navigation changes only the camera/selection, never geometry.

The deterministic score is:

```text
max(width / targetAspect, height)
+ 0.10 * sqrt(width * height)
+ 0.035 * sqrt(max(0, width * height - occupiedArea))
+ 0.012 * estimatedConnectorLength
+ 0.5 * extraLocalTopicLines
+ 0.01 * rowHeightImbalance
```

Occupied area includes complete tray/card surfaces. The score balances fit, bounding area, whitespace, connector span, wrapping and row imbalance. Stable candidate enumeration resolves ties. Complete trays, nonintersecting occupied contours, reserved routing space, full measured text and canonical order are construction constraints, not violations that a better numeric score may purchase. The independent validation rejects any final candidate violating them.

Spacing is compact and shared by every scope: parent-to-bus 10, bus-to-child 10, sibling clearance 12, tray-column gap 16, row gap 24 and used-root gap 32. No geometry, spacing, score or branch arrangement is selected by Course/Project/Stage identity or name. No Global coordinates are read.

## Real scope measurements

Chrome, Dark, **1440×900 CSS pixels**, DPR 2. The 104 px header leaves a 1440×796 map; Fit All reserves controls/footer/padding and fits into 1392×684. World dimensions include 8 units of outer padding on each side. Topic font is `14 × Fit All scale`. Timings are single warm browser runs including projection and layout, not a cross-browser performance benchmark.

| Scope | Explicit Topics | Explicit Categories | Context Categories | Roots | World W × H | Aspect | Fit All | Topic px | Trays | Columns → tray count | Layout ms | Overlaps |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|---:|---:|
| course:8 | 89 | 46 | 0 | 1 | 2,727.87 × 1,386.40 | 1.968 | 0.493364 | 6.91 | 26 | 1 col: 24, 2 col: 2 | 426.9 | 0 |
| project:113 | 26 | 0 | 21 | 1 | 1,816.50 × 939.80 | 1.933 | 0.727814 | 10.19 | 11 | 1 col: 9, 2 col: 2 | 55.7 | 0 |
| stage:617 | 12 | 0 | 16 | 1 | 1,271.50 × 698.60 | 1.820 | 0.979101 | 13.71 | 6 | 1 col: 6 | 12.5 | 0 |

### Course 8

[Fit All capture](tests/course-fit-all.png). The view exposes all 89 Topics and 46 explicit Categories, with 31 learned and 12 verified overlays. The root and branches are structurally traceable; small Topic text is not intended for full-title reading at Fit All. Fit subtree and Topic Focus provide reading views without changing or hiding geometry. This meets the structural-overview goal, with the readability limitation stated below.

### Project 113

[Fit All capture](tests/project-fit-all.png). All 26 requirements and 21 context Categories fit with approximately 10.2 px Topic text. The text is directly readable in the reviewed desktop capture, though compact. Project requirement accents coexist with 26 learned and 10 verified overlays; these are independent facts.

### Stage 617

[Fit All capture](tests/stage-fit-all.png). All 12 requirements and 16 context Categories fit with approximately 13.7 px Topic text. This is a comfortable reading view. The Stage accent coexists with 12 learned and seven verified overlays. [Topic Focus and overlay Inspector](tests/stage-topic-focus-inspector.png) demonstrates requirement, learned and verified together on exact `topic:36`.

## Connector span distribution

World units; min / median / p90 / p95 / max. Span measures the full horizontal extent of each Category or tray connection, including a row spine when used. `results.json` additionally records individual painted segment-length distributions; shared buses are deduplicated by the inherited router.

| Scope | Min | Median | p90 | p95 | Max |
|---|---:|---:|---:|---:|---:|
| course:8 | 0.00 | 85.00 | 499.00 | 732.00 | 1,671.12 |
| project:113 | 0.00 | 0.00 | 489.00 | 539.50 | 698.00 |
| stage:617 | 0.00 | 0.00 | 175.25 | 267.00 | 357.50 |
| synthetic:one | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| synthetic:five-one-branch | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| synthetic:twenty-several-branches | 0.00 | 0.00 | 206.00 | 303.50 | 961.50 |
| synthetic:hundred-multiple-roots | 0.00 | 74.00 | 528.00 | 667.00 | 2,501.00 |
| synthetic:three-hundred | 0.00 | 94.00 | 881.00 | 1,054.00 | 4,752.75 |

## Synthetic scale results

These disposable scopes sample known Global IDs only to exercise the generic algorithm. They are explicitly typed `synthetic`; they are not real Hyperskill scope evidence and do not enter any accepted data or State. The one-Topic case deliberately uses the longest full title. The five-Topic case uses one branch. The 20/100/300 cases round-robin across the five roots, covering several branches and very different Category titles.

| Scope | Explicit Topics | Explicit Categories | Context Categories | Roots | World W × H | Aspect | Fit All | Topic px | Trays | Columns → tray count | Layout ms | Overlaps |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|---:|---:|
| synthetic:one | 1 | 0 | 5 | 1 | 239.00 × 664.90 | 0.359 | 1.028726 | 14.40 | 1 | 1 col: 1 | 1.0 | 0 |
| synthetic:five-one-branch | 5 | 0 | 5 | 1 | 664.00 × 651.00 | 1.020 | 1.050691 | 14.71 | 1 | 3 col: 1 | 4.4 | 0 |
| synthetic:twenty-several-branches | 20 | 0 | 29 | 5 | 2,155.00 × 757.30 | 2.846 | 0.645940 | 9.04 | 13 | 1 col: 12, 2 col: 1 | 38.1 | 0 |
| synthetic:hundred-multiple-roots | 100 | 0 | 73 | 5 | 3,488.00 × 1,751.80 | 1.991 | 0.390456 | 5.47 | 47 | 1 col: 44, 2 col: 3 | 929.5 | 0 |
| synthetic:three-hundred | 300 | 0 | 133 | 5 | 5,912.00 × 2,942.00 | 2.010 | 0.232495 | 3.25 | 92 | 1 col: 83, 2 col: 9 | 2675.0 | 0 |

The 300-Topic fixture exercises four-column trays; the five-Topic fixture exercises three-column trays. The 100/300 cases preserve all five roots. All fixtures have zero overlaps, zero route/card collisions, zero clipped titles and preserved canonical order. Large fixtures are orientation views and require focus for reading.

## Validation and generality

[Focused results](tests/results.json), [generality audit](tests/generality.json), [protected-surface audit](tests/protected-check.json).

- Exact foundation and known scope counts; explicit/context classification; no descendant membership inferred from Categories.
- Closure independently recomputed by queue traversal and compared with the engine's recursive closure. Reversed seed inputs produce byte-identical semantic projections and geometry, including routing and tray packing.
- Exact semantic inventory, no duplicate Topic/Category nodes, only used roots, all supplied structural memberships retained, presentation roots excluded from semantic mappings.
- Pairwise card/row overlap, unrelated card/tray overlap, tray/tray overlap, complete row containment, route orthogonality, route/card/tray avoidance and exact Category endpoints.
- Numeric sibling and column-major Topic order; local sibling alignment; complete normalized title reconstruction and measured text widths. Actual SVG `getBBox()` checks on all three rendered scenes find no text outside its card and no overlapping text bounds.
- Exact `Show in Global` identity mappings checked for every projected Topic/Category. The isolated `global.html` bridge opens the unchanged Global view in a same-origin iframe and calls its existing selection API with the exact key. Browser navigation verifies actual Global selection for both `topic:36` and `category:3`. There is no title matching or coordinate conversion.
- Search, Topic Focus, Fit subtree, Fit All, Inspector, learned/verified/requirement co-display, pan/zoom and minimap clicks pass. Camera/selection interactions leave the geometry and layout-build count unchanged. Browser errors: zero.
- `layout.js` has no scope type, real scope ID or branch-name conditions. A metamorphic check adds 100,000 to every semantic ID and parent/membership/progress reference used by the engine: all three real scope layouts retain exactly the same positions, sizes and text. Scope datasets and UI accents are the only type-specific inputs; there is one engine entry point and one layout implementation.

## Limitations

The finite beam is deterministic, not a proof of globally optimal packing. It deliberately trades exhaustive search for bounded shape diversity. The 300-Topic fixture takes about 2.7 seconds on the measured machine; the planner runs synchronously and is a prototype, not a large-catalog renderer. No claim is made that 300 full titles are readable at Fit All.

Course 8's Fit All Topic text is about 6.9 px, with lower Category headings about 8.4 px. Its complete structure is useful for orientation, but lower-level reading needs Fit subtree or the 16 px Topic Focus view. Project's approximately 10.2 px Fit All text is compact; Stage is more comfortable. An accessibility-scale fit requirement for every scope would need an additional product decision, not hidden content or changed membership.

Measurements and snapshots use desktop Chrome and the local system font. Font/platform changes can legitimately change measured geometry; determinism is guaranteed for identical inputs and measurements. No Safari/mobile sweep or repository-wide regression was run. The checked identity bridge depends on serving this directory alongside the existing Global prototype. Secondary taxonomy memberships are preserved and navigable in the Inspector rather than drawn as duplicate physical Topic rows.

## Reproduce locally

From the repository root:

```sh
python3 -B prototypes/knowledge-atlas-scope-pyramid/build.py --baseline # once on a fresh checkout
python3 -B prototypes/knowledge-atlas-scope-pyramid/build.py
python3 -m http.server 8810 --bind 127.0.0.1
```

In another terminal, use the existing Playwright dependency (or provide `PLAYWRIGHT_MODULE`) and an installed browser (optionally `ATLAS_BROWSER_EXECUTABLE`):

```sh
node prototypes/knowledge-atlas-scope-pyramid/tests/validate.cjs
node prototypes/knowledge-atlas-scope-pyramid/tests/generality.cjs
python3 -B prototypes/knowledge-atlas-scope-pyramid/build.py --verify
```

This session used the preexisting `/tmp/adaptive-progress-browser/node_modules/playwright` module and `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`. These paths are environment overrides, not required runtime dependencies. `SCOPE_URL` can override the test URL. The initial protected baseline refuses accidental overwrite.

## Protection and stop

The audit confirms **all 662 protected files and their path inventory are byte-identical to the start of this task**. The baseline includes the user's preexisting uncommitted changes. All repository writes for this milestone are under `prototypes/knowledge-atlas-scope-pyramid/`. Production, State, accepted Knowledge, the original V6, Global V6 and Skill Tree prototypes remain unchanged.

**One reusable engine genuinely serves all three required scopes. C — GENERIC SCOPE PYRAMID PROVEN. HARD STOP.** No additional Courses/Projects acquired; no commit, push or deployment. The next milestone is **COURSE / PROJECT / STAGE RELATION DISCOVERY + ACQUISITION**, and has not been started.
