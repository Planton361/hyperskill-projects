# Knowledge Atlas V6.1 — Boxed Knowledge Atlas

Isolated static prototype; production maps, public preview and source knowledge data are outside its write scope. No CDN or external fonts. D3 and routing dependencies are local. Serve the directory with `python3 -m http.server 8776 --bind 127.0.0.1` and open http://127.0.0.1:8776/.

## Semantic boundary and reuse

`model.js` retains V5/V6 normalization, typed IDs, canonical taxonomy, stable numeric sibling order, deduplicated prerequisite/dependent relations and nearest-visible-ancestor evidence roll-up. `model.json` is an exact copy of the eight real normalized tables, with source hashes. Runtime uses no growth fixtures. Counts: 89 topics, 46 categories, 31 learned, 12 verified, 137 knowledge relations. Projects are Inspector objects, never taxonomy nodes. Requirements do not imply application, mastery or a topic's learning state. Known empty stage completion arrays remain different from unknown completion inventories.

## Box system and topic grids

Natural system typography: root 28, major category 21, other category 17, topic 14, metadata 10 layout units. Categories have stronger surfaces/borders, coverage captions and a separate disclosure inside the visual box. Topics have restrained surfaces, left-aligned complete names, mint learned indicators, verification rings and hollow unlearned indicators. The entire box selects; the explicit disclosure only toggles expansion.

Canvas measures labels at the actual system font. Topic cards start at 204 units, widen in 12-unit steps up to 276 to obtain at most three lines, and can grow further for unbroken words. Minimum configured width is 180. No character-column wrapping or ellipsis. Padding is 12 horizontal and 8 vertical, with dedicated indicator/evidence space. Row heights follow measured line count. Grid candidates have one to four columns; the count heuristic, actual column/row extents, aspect ratio and available parent width contribute to the score. Stable numeric IDs determine column-first order. No topic coordinates are persisted.

## Hierarchy, contour packing and fit

Category branches remain canonical top-down parent/child edges. Root's three major branches share one row and retain their order. Below that, category subtree contours can occupy multiple bounded shelves, each child below its parent. This is presentation only: a lower sibling does not become a child of another sibling. All cards retain their true category depth and direct parent. Full topic-band ownership rectangles prevent another branch from occupying a grid's interior.

The packing algorithm tests content-derived widths, collides complete subtree contours and scores area/aspect ratio. It avoids the enormous horizontal fan of a strict single-row tree. The tradeoff is staggered siblings and occasional long perimeter routes; canonical edges and Inspector paths explain membership. Topic grids use a common parent bus, external column spines and short stubs. No topic-to-topic hierarchy is created.

Fit uses complete card rectangles plus 16-unit bounds margins, 44 horizontal and 108 vertical control/footer allowance. It never hides knowledge. Mode and camera transformations do not rebuild layout. Default is all-expanded, My Knowledge, Fit all. Fit intent survives resizing; search/manual camera intent is preserved. At 1920×1080, topic text is 7.72 effective CSS px; the requested 10 px threshold is explicitly **not met**. See validation and the strict readability test.

## Presentation checkpoint and growth

Schema 3, algorithm `atlas-boxed-1`; schema is in `layout-checkpoint.schema.json`. This explicit new presentation baseline changes V6 absolute scene units to box geometry; canonical hierarchy and major branch order remain. The previous V6 implementation/checkpoint is archived in `tests/v6-before-boxed/` for comparison. Older checkpoints are rejected rather than silently migrated.

Allowed checkpoint content: category-local anchors, child-slot x/y/extents and order, category-box geometry/typography, and topic-band dimensions/column widths/row counts. No topic IDs or coordinates, knowledge state, courses, projects, evidence or relations. Category labels are presentation metadata, with names still sourced from the model. Baseline and grown checkpoints rebuild deterministically.

Retained major anchors have priority. Existing local child slots remain until contour collisions require downward movement within their parent. New branches append below the parent's previous region. This prevents unrelated Foundation/DevOps displacement in the tested fixtures. Basics +20 expands locally and moves an adjacent Java subtree when necessary; new Databases grows below the existing scene. Stable anchors consume more vertical space after growth; unlimited arbitrary growth has no universal collision-free guarantee.

## Evidence overlay

Project selection immediately enables coverage if real requirements exist. Explicit Show/Hide remains available. Required cards and ancestor category cards receive amber borders/tints, connecting hierarchy and relevant membership paths become amber, and required cards receive diamonds. Learned indicators and verified rings stay visible. Unrelated cards/disclosures remain rendered at 0.4 opacity. Evidence accessible names identify “required by selected project”. Overlay painting changes styles and accessible descriptions only: no geometry, checkpoint, viewport or expansion mutation.

Project 113: 26 distinct required topics. Stage 4: 12 explicit stage requirements. Manually hidden evidence rolls up once to the nearest visible ancestor. Reveal is shown only for hidden requirements; Fit coverage changes only the camera. Project 380 has known empty completed stages and no loaded requirements. No project descriptions or applies claims are invented.

## Routing, interaction and accessibility

`routing.js` reuses the local V5 lane/grid routing implementation with rectangle obstacles and box ports. Hierarchy paths terminate bottom/top; contextual knowledge paths use boundary ports, orthogonal lanes and grid routing if necessary. Lines avoid card interiors. No force simulation. Default has zero knowledge cross-links; selection shows exact direct prerequisites/dependents. Relations never alter geometry. Edge crossings and long detours can remain.

Search opens necessary ancestors, selects and centers the complete card, uses about 17 effective px topic text, retains mode and shows contextual relations. Enter/Space select cards or activate explicit disclosures; focus is restored after redraw. Double-click has no required behavior. Accessible button names include original source names, canonical path, learning/verification state and active requirement evidence; `aria-pressed` marks selection, `aria-expanded` belongs to disclosure. Inspector is a polite live region. Drag, wheel and touch pinch/pan remain; reduced motion is respected.

Inspector is right above 1200 px and below at narrower widths. Personal projects are directly selectable, catalogue entries remain under disclosure. Single-course data needs no redundant dropdown. Minimap is not implemented.

## Validation commands

With the local server running:

```bash
python3 tests/integrity.py
node tests/browser.cjs
node tests/boxed.cjs
node tests/relations.cjs
node tests/readability.cjs
```

The final command intentionally exits 1 while the measured 10 px target remains unmet. This is a real failed acceptance criterion, not a passing regression assertion. The other suites verify semantics, geometry, evidence, interactions, growth and desktop/mobile coverage. Browser suites use existing Playwright/Chrome; no downloads. `tests/generate-checkpoint.cjs` explicitly regenerates the prototype-only checkpoint; normal browsing never writes it. Review screenshots and JSON results remain local under `tests/`.
