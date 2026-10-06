# Knowledge Atlas V6.4 — Visual Composition

Visual refinement of the accepted V6.3, retaining its complete model, checkpoint and all 135 node coordinates. Static, isolated prototype. Run `python3 -m http.server 8776 --bind 127.0.0.1` here and open http://127.0.0.1:8776/. Local D3 and system fonts; no CDN. Changes are confined to this directory. No commit, push or deployment.

## Semantic contract

The normalized model is unchanged: 89 topics, 46 categories, 31 learned, 12 verified and 137 knowledge relations. All topics and labels render by default at every zoom in both modes. Manual disclosure remains optional. Projects stay in the Inspector, outside taxonomy. Project 113 has 26 distinct requirements; its Stage 4 has 12. No applies, topic mastery, project descriptions or completion claims are inferred. `tests/integrity.py` verifies identity and source hashes for all eight knowledge tables.

Categories form the canonical tree; direct topic children form a **presentation-only tray**. `L.trays` contains derived rectangles and references to existing topic/category keys. It adds no model node, semantic ID, Search result, Inspector object or evidence entity. Categories with both category and topic children retain separate branches and a direct-topic tray. Each topic belongs to exactly its canonical parent's tray.

## Topic trays and individual targets

Default variant B uses list rows: transparent individual hit rectangles, complete left-aligned labels and mint/hollow/verified indicators within a faint shared surface. Variant A uses mini cards; `?items=mini` allows local comparison. Both variants use identical geometry, text and interactions. Rows receive visible card borders on selection, keyboard focus, hover or project evidence. Native SVG titles provide complete source-name tooltips.

The decorative surface layer is aria-hidden and sits behind hierarchy, knowledge relations and node targets. Topic container groups have `role=presentation`, no ID/data-key/tabindex, and no extra navigation stop. Individual topics remain accessible buttons with true topic IDs. Entire hit rectangles are clickable even when transparent. Accessible names preserve state/path and add “required by selected project” when appropriate.

One category-bottom → tray-top segment replaces per-topic ticks/spines. There are no interior Topic→Topic membership lines. The tray frame/rather close packing conveys shared parent membership, without implying prerequisite order. Existing hierarchy edges still connect real category cards at their boundaries.

## Natural geometry and packing

Typography remains root 28, major 21, category 17, topic **14**, meta 10 natural layout units. Cards/text scale together; no screen-space or inverse-scale labels. Category measurements/wrapping remain V6.2.

Topic targets use minimum/preferred width 172, measured text plus 44 units for indicators/evidence/padding, 12-unit widening steps as needed, and at most three lines for the current model. Height is `max(29, lines × 17 + 12)`: six units vertical padding. Horizontal padding is ten. Unbroken words can widen beyond the preferred cap. Labels remain complete.

Each category evaluates valid 1–4-column configurations in stable numeric-ID, contiguous column-first order. No pedagogical order is invented. Column width is the maximum measured item width in that column; each item retains its own height. Gaps are eight horizontally/four vertically, with three-unit outer tray padding. Between independent trays, contour separation is at least eight units: actual item separation across frames includes their outer padding. Category→tray separation is 12, category levels retain 24/18/8 gaps by depth.

Scores combine exact width/height, global bottleneck weights, unused space and a soft 1.2–2.5 preferred aspect ratio. For multi-topic groups, candidates outside 0.8–4 are excluded **when a feasible candidate inside that range exists**. This avoids extreme columns/ribbons without forcing every small group to have the same shape. Single-topic trays and some larger trays remain outside the preferred soft range.

## Contour packing and global feedback

V6.2 variable-size contour/shelf packing remains: actual category/tray rectangles constrain local sibling positions, not equal maximum-width slots. Tray interiors are ownership regions: unrelated category hierarchy cannot cut through a tray. Category children may occupy staggered shelves while always remaining below their canonical parent.

The bounded offline optimizer uses four contour-aspect seeds and up to 18 greedy passes. Grid and category-region alternatives are scored against a fixed viewport-independent 1640×861 reference area. It prioritizes zero rectangle collisions, then fit scale balanced with tray aspect quality. Finalists route category edges and fit actual visible content bounds. The inherited V6.3 result evaluated 5,158 candidates in about 16.6 seconds; V6.4 retains that checkpoint byte-for-byte and does not run a new packing search.

The explicit V6.3 generator seeds **only major presentation anchors** from the archived V6.2 checkpoint: x −887, 248.5, 887; y 87.04. Major order and all three anchor positions are therefore identical across V6.2/V6.3. Deeper category positions changed once in the V6.3 migration; V6.4 retains every one of them.

## Checkpoint and growth

Schema **5**, algorithm **atlas-trays-3**. Records retain category anchors/order/child-slot allocation, measured category boxes and topic-band geometry; the band now includes tray padding. No topic IDs/x/y, knowledge states, courses, projects, evidence or relations are persisted. Old schemas are rejected explicitly. Complete V6.2 implementation/reference checkpoint/metrics are archived under `tests/v6.2-baseline/`.

Normal runtime restores category slots and tray column choices, derives actual topic geometry again, and grows locally. Existing major anchors remain fixed in Advanced OOP +5, Basics +20 and Databases +20. Basics growth shifts some adjacent Java subtrees down to avoid collisions; it does not shift unrelated major regions. New branches append below their parent's existing region. Both cards and whole tray frames are tested for collision after growth; rebuilt checkpoints are deterministic. Synthetic fixtures are test-only.

## V6.4 orthogonal composition routing

Category hierarchy now has a separate composition router; contextual knowledge routing retains its mint rounded lane language. Parent ports are bottom-center, child ports top-center. Whole category/topic rectangles and tray frames block hierarchy routing; input/output corridors are reserved so another branch cannot obstruct a later connection.

For each sibling set, first try a shared vertical trunk/horizontal bus/child drops, checking every segment against node zones and already-routed foreign branches. Staggered sets may not admit that simple shape. Their fallback uses a direction-state A* planner with Manhattan length and a 40-unit bend penalty, rather than shortest length alone. This removes staircase micro-bends. Routing tries a bounded set of six deterministic group orders if a corridor is blocked; deepest groups first succeeds for the validated default. Membership rails also constrain foreign hierarchy lines.

Within each parent group, union all valid sibling routes and extract a rooted shortest-path tree. This removes loops and makes shared junctions explicit. Split shared rails where endpoint/junction/child ownership changes. Each resulting SVG segment is drawn once and carries the real child keys whose parent→child paths use it. Coverage colors a segment only when at least one of those actual children lies on a required ancestor path; irrelevant sibling drops stay subdued. No semantic nodes or relationships are added.

Default: 116 rendered category segments versus 281 in V6.3; average 1.91 bends per real connection, maximum four, zero hierarchy crossings/intersections. Eight blocked-tray routes need four bends. All growth fixtures also have zero crossings and maximum four. Knowledge lanes ignore tray frames as before but avoid all item text/cards.

## V6.4 presentation tokens and focus

`AtlasLayout.SPACE`: ROOT_MAJOR 24, MAJOR_CATEGORY 18, CATEGORY_CATEGORY 8, CATEGORY_TRAY 12, SIBLING_MAJOR 10, SIBLING_CATEGORY 8, TRAY_INTERNAL_X 8, TRAY_INTERNAL_Y 4, TRAY_PADDING 3. `AtlasLayout.TYPE`: ROOT 28, MAJOR 21, CATEGORY 17, TOPIC 14, META 10. These systematize the accepted numeric geometry; they do not move existing anchors.

`CARD` rendering tokens specify category radius 5, title X34, disclosure X15, root/major header padding 8 and deep-category padding 5, caption bottom inset 7; topic status X12, label X24, evidence right inset 10. Positions are measured relative to the appropriate box boundaries, preserving consistent alignment within each typography class.

Default deep connectors use slate opacity .32, major .42, root .55; no curves/glow. Tray outlines use .38 opacity and .65 stroke, with nearly neutral surfaces. Category borders retain stronger weight. Selected hierarchy context uses violet opacity .95 and matches an Inspector accent line. Project focus uses amber rails and outlines, keeps relevant category surfaces neutral, and dims unrelated nodes to .30. Required topic rows retain amber tint/marker plus separate mint learning/verification state. No additional tray count is introduced.

Six of eleven multi-child families retain an aligned sibling row; five remain staggered to preserve compact geometry. An explicit probe aligning all Java children at their current X anchors caused 18 card overlaps. No global depth-band migration is applied in this visual pass. Major anchors and all other node coordinates remain identical to V6.3.

## Fit, interaction and evidence

Visible fit bounds include actual category/topic targets, tray frames and relevant hierarchy edges, plus eight units of natural border allowance. Allocated future capacity is excluded. Inspector width remains 250 CSS px, below-map at ≤1200; fit allowances remain 30 horizontal/84 vertical CSS px. Modes, zoom, evidence and selection do not relayout.

Category card click/Enter selects; its separate accessible chevron only toggles disclosure. Topic click/Enter selects the true topic. Search opens manually collapsed ancestors, centers the actual topic target, zooms to readable text and shows direct relations without changing mode. Pan, wheel zoom, touch pinch/pan, reduced motion, focus restoration and live-region Inspector remain.

Project selection immediately activates coverage, retaining the accepted V6.2 response. Exact required items gain amber border/tint/diamond while mint learning/verification indicators remain. Ancestor categories/edges, the shared rail and relevant tray borders highlight. Unrelated nodes remain at 0.3 opacity. There is no aggregate tray count that could duplicate evidence. Show/Hide changes no geometry, checkpoint, camera or disclosure. Manual collapse retains nearest-visible-ancestor roll-up; conditional Reveal and camera-only Fit coverage remain.

Default has no knowledge cross-links. Topic selection displays only direct prerequisites/dependents. Boundary-side ports accommodate compact row spacing. Routing treats complete category/topic hit rectangles as obstacles, but not tray frames: trays are presentation groupings, not semantic barriers. All 137 routes and all 89 selected topics are verified against card interiors. Routes do not affect layout; crossings/detours can remain.

## Reproduction

With the local server running:

```bash
python3 tests/integrity.py
node tests/browser.cjs
node tests/boxed.cjs
node tests/compaction.cjs
node tests/trays.cjs
node tests/composition.cjs
node tests/relations.cjs
node tests/readability.cjs
```

Explicit offline regeneration using the V6.2 major-anchor seed:

```bash
node tests/optimize-checkpoint.cjs
```

`tests/generate-checkpoint.cjs` reproduces the loaded checkpoint without global optimization. Review screenshots and A/B comparisons are local under `tests/review/v6.4/`; detailed measurements and limitations are in `VALIDATION.md`.

V6.3 runtime/checkpoint and measurements are frozen under `tests/v6.3-baseline/`. Composition metrics and alignment trial: `tests/composition-results.json`; five sequential before/after startup measurements: `tests/composition-performance.json`. The route planner adds one-time startup cost (local median layout 17.4 → 75.2 ms), not interaction-time relayout.
