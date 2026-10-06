# Knowledge Atlas V6.2 — Compact Readability Packing

An isolated static prototype. Serve locally with `python3 -m http.server 8776 --bind 127.0.0.1` from this directory; open http://127.0.0.1:8776/. Local D3/system fonts only. Production maps, public preview, normalized knowledge data and profile README are outside the write scope.

## Semantic and rendering contract

V6.1 model/Inspector/evidence semantics remain: 89 topics, 46 categories, 31 learned, 12 verified, 137 distinct knowledge relations. All topics and labels render by default in both modes and at every zoom. Manual category collapse remains explicit. Projects are Inspector/evidence objects, never taxonomy nodes. Project 113 has 26 distinct requirements; Stage 4 has 12. No applies, descriptions, mastery or competency claims are invented. `tests/integrity.py` verifies exact equality and hashes for all eight source tables.

## Natural geometry

Typography is unchanged: root 28, major 21, category 17, topic **14**, metadata 10 layout units. SVG scene scaling affects cards and labels together; no inverse scaling or screen-space labels.

Topic cards have a configured 180-unit minimum/preferred width, can widen in 12-unit steps for three-line labels, and preserve 8-unit vertical padding. Unbroken words can widen beyond the preferred cap. Measured label width includes dedicated indicator/evidence space. Actual normal-model average width is 180.28; maximum topic line count is three. Canvas measures each actual system-font size/weight, including bold category titles.

Category widths come from measured wrapped title, disclosure/padding and coverage-caption capacity. Two/three-line category headings compete on area/width. Root/major captions retain larger header padding; deep cards reduce unused header padding. Root-to-major gap is 24, major-to-child 18, deeper category-to-child 8. Topic bands start 12 below their category, with a bus 7 above the grid. Topic column/row gaps are 10/6.

## Variable-size contour packing

Root's three major branches retain their order and one shared row. Category children below them use actual subtree rectangle contours, not uniform maximum-width slots. Each subtree includes category boxes and topic-band ownership rectangles. Topic bands remain protected regions so foreign branches do not interfere with their membership bus.

The sweep enumerates vertical alignments of actual rectangle boundaries. At each alignment it derives forbidden horizontal intervals from overlapping contours, merges them implicitly, and chooses the first free x position inside candidate region widths. Candidate widths are derived from actual subtree extents and pair sums. The objective balances area/aspect ratio. Contours can interleave in empty regions; siblings can occupy staggered shelves, always below their canonical parent. No hierarchy is added. Collision comparisons use a small geometric tolerance to avoid floating-point boundary drift on checkpoint rebuild.

## Topic candidates and global feedback

Each parent considers valid one-to-five-column configurations, measured card widths/heights, exact grid bounds, aspect ratio and unused-space penalty. Stable numeric topic IDs determine contiguous column-first order. Columns use each card's own height instead of making every row as tall as its largest neighbor; this removes phantom row whitespace. No topic coordinates are stored.

`AtlasLayout.optimize()` first builds locally scored grids, then measures the overall width/height bottleneck against a fixed **1640×861** design area. This reference is viewport-independent presentation geometry, matching the 1920×1080 acceptance viewport after Inspector/margins. Height/width weights derive from the bottleneck and reference aspect ratio. Subsequent candidate ordering follows the current bottleneck.

The bounded feedback search tests alternative grids and category-region widths. Four deterministic contour-aspect seeds retain diversity; beam width is four, maximum 18 passes. Each candidate is judged by full-layout fit scale, with whitespace as a tie breaker. Unchanged contour results are memoized. Finalists receive actual boundary routing and are ranked against true visible content bounds including hierarchy edges. No exponential exhaustive search, force layout or viewport-specific relayout.

The shipped checkpoint was generated **from the model without manually specified category/column overrides**: 7,834 evaluated candidates, about 33.5 seconds locally. This is an offline presentation-generation cost. Normal runtime loads the checkpoint and uses stable local packing, approximately 15 ms in the measured run; modes, coverage, selection and zoom never invoke global optimization.

## Visible bounds, fit and Inspector

`contentBounds()` fits current cards plus visible category/membership edge points, with an 8-unit border allowance. Allocated subtree extents and potential future capacity do not enlarge fit bounds. The test deliberately inflates every reserved width/height by 10,000 and verifies identical current content bounds.

Desktop fit allowances are now 30 horizontal and 84 vertical units of CSS viewport space, versus 44/108 before. Centering preserves space for top controls and bottom legend. Every card and hierarchy point fits initial view in all tested sizes. Right Inspector is 250 px instead of 290; headings remain 22, normal body text 12, hierarchy path 11. A/B tests select every map object and project at both widths and verify no horizontal Inspector overflow. At ≤1200 the Inspector stays below the map.

## Presentation checkpoint and stable growth

Schema **4**, algorithm **atlas-compact-2**, with the same presentation-only category record boundary. Category anchors/order/child-slot extents, category-box geometry and topic-band column widths/rows/gaps are permitted. No learned/verified state, courses, projects, evidence, relations or topic IDs/x/y are persisted. Old versions are rejected rather than silently migrated. V6.1 implementation/checkpoint/reference page and metrics are archived in `tests/v6.1-baseline/`.

V6.2 establishes an explicit compact baseline: absolute V6.1 coordinates change once during compaction. Major order and canonical membership remain. Growth then preserves all existing major anchors. Retained child slots are reused; local collisions move children downward within their region. New branches append below their parent's previous allocation. Grid columns are restored from presentation metadata; positions/heights derive again from real labels. Baseline/grown checkpoints rebuild deterministically.

Basics +20 can move adjacent Java subtrees; this is a local-space tradeoff, not a promise that every minor category is immovable. Advanced OOP +5 and Databases +20 move no existing nodes in the tested fixtures. Future arbitrary growth can still require further collision policies; fixtures are test-only and never normal runtime data.

## Interactions, accessibility and evidence

Entire cards select on single click/Enter/Space. The explicit disclosure only expands/collapses and exposes aria-expanded. No required double click. Accessible names include complete source title/path, selected/learned/verified state and active “required by selected project” evidence. Focus restoration, live-region Inspector, search, reduced motion, drag/wheel and touch pinch/pan remain.

Project selection immediately enables real coverage. Amber borders/tints/diamonds and exact ancestor paths highlight requirements; unrelated nodes remain rendered at 0.4 opacity. Mint states remain intact. Show/Hide changes no geometry, checkpoint, viewport or disclosure. Hidden requirements roll up once to nearest visible ancestors; Reveal is conditional, Fit coverage is camera-only. Empty/unknown project-stage state remains distinct.

Default has zero knowledge cross-links. Topic selection routes exact prerequisites/dependents to card boundaries, with full-card obstacles and no geometry mutation. Compact row gaps use 3-unit outward ports; rounded orthogonal routing stays outside card interiors. All 137 model connections and all 89 topic selections are checked. Edge crossings/long detours remain possible.

## Reproduction

With the server running:

```bash
python3 tests/integrity.py
node tests/browser.cjs
node tests/boxed.cjs
node tests/compaction.cjs
node tests/relations.cjs
node tests/readability.cjs
```

All commands pass. The readability test uses actual SVG screen CTM and fails without rounding if topic font is below 10.0 CSS px.

Explicit checkpoint regeneration, roughly 34 seconds locally:

```bash
node tests/optimize-checkpoint.cjs
```

This writes only the prototype checkpoint and optimization results. Normal browsing never writes files. `tests/generate-checkpoint.cjs` reproduces the loaded stable checkpoint without reoptimizing. Results/screenshots remain local under `tests/`; see `VALIDATION.md`.
