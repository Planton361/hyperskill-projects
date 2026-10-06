# Knowledge Atlas V6.4 — Visual Cleanup / Composition Validation

Validated locally in Chromium on 2026-10-03. Changes are confined to `prototypes/knowledge-atlas-v6/`; no commit, push or deployment. Eight normalized source tables remain identical with matching hashes. Public Preview, production maps and profile README were not edited.

## Visual Result

The overview is quieter: thin slate orthogonal hierarchy, shared sibling trunks instead of repeated lines, faint topic-tray outlines and lighter box mass. Root/major connectors remain more prominent than deep branches. Topic selection adds violet hierarchy context and an Inspector accent; project selection creates a clear amber focus path while unrelated regions remain visible. All 89 topics, 46 categories, 26 trays, 31 learned and 12 verified remain present. Reviewed dark/light overview, Basics detail, project coverage and mobile images.

## Connector System

Hierarchy uses exclusively axis-aligned line segments, bottom-center parent ports and top-center child ports. No hierarchy SVG Q/C curves or diagonal segments. Full category/topic cards and tray bounds are routing obstacles; reserved port corridors prevent routes from blocking later inputs/outputs. Routing does not change node coordinates or knowledge semantics.

## Shared Trunks

Each sibling set first attempts a shared vertical output, horizontal bus and child drops. Staggered/obstructed families use a low-bend obstacle route. Within each parent group, the route union becomes one rooted tree with explicit junctions. Shared rails are partitioned by real child ownership and painted once; coverage highlights only intervals actually needed by relevant children. There are 22 category-parent connection groups, representing 45 real canonical category edges. The 26 shared tray-membership segments remain unchanged. Trays remain presentation-only, with individually accessible Topic IDs.

## Hierarchy Crossings

**Zero** in default, Advanced OOP +5, Basics +20 and Databases +20. V6.3 had three strict route-polyline crossings: two between different parent groups and one within a group. V6.4 has neither foreign crossings nor same-group through-crossings; shared endpoint/T junctions are intentional sibling buses. Zero hierarchy/membership segments enter Category Cards, Topic Trays or Topic Rows; label geometry remains contained inside cards. Project paths are subsets of these same unobstructed segments, so no evidence line enters unrelated nodes.

Crossings are measured as strict perpendicular interior intersections; shared endpoints and collinear shared intervals are treated as bus structure. Full segment/card/tray-interior tests are independent of that crossing metric.

## Bend Count

| Metric | V6.3 | V6.4 |
| --- | ---: | ---: |
| Rendered category hierarchy segments | 281 | 116 |
| Membership segments | 26 | 26 |
| Total rendered hierarchy + membership segments | 307 | 142 |
| Average bends per canonical category connection | 5.2444 | 1.9111 |
| Maximum bends | 41 | 4 |
| Category hierarchy crossings | 3 | 0 |
| Hierarchy/card/tray intersections | 0 | 0 |
| Average aligned sibling-card gap, natural units | 210.7431 | 210.7431 |
| Actual card/tray overlaps | 0 | 0 |

The router uses directional A* with a 40-unit bend cost when a clean shared bus is blocked. **37/45 paths have at most two bends; eight need four**, mainly because a parent has a direct tray below its output or because staggered subtrees occupy the direct corridor. No claim that every path meets two bends. Growth maximum also remains four. Segment totals compare actual rendered geometry: V6.3 repeated complete paths, V6.4 paints shared intervals once. Average sibling gap is a card-center-derived gap for aligned pairs, not a reserved subtree gutter.

## Spacing Rhythm

Presentation tokens retain accepted V6.3 numeric geometry:

| Token | Natural units |
| --- | ---: |
| ROOT_MAJOR | 24 |
| MAJOR_CATEGORY | 18 |
| CATEGORY_CATEGORY | 8 |
| CATEGORY_TRAY | 12 |
| SIBLING_MAJOR | 10 |
| SIBLING_CATEGORY | 8 |
| TRAY_INTERNAL_X / Y | 8 / 4 |
| TRAY_PADDING | 3 |

Small internal row gaps, larger separation across ownership frames and explicit category→tray rails keep related knowledge together. No arbitrary per-topic positions or newly invented ordering. No spacing growth is forced into a layout with little remaining Fit-All budget.

## Sibling Alignment

Six of eleven multi-child category families retain exact shared Y baselines, including the three majors, Dev Tools, Computer science fundamentals and several OOP sibling sets. Five compact families remain staggered, as in V6.3. A trial shifting all four Java-child subtrees to one Y row while retaining their X anchors created **18 card overlaps**; it was not adopted. Shared connectors make those existing staggered families calmer without silently destroying persistent geography.

## Depth Bands

Preferred depth alignment was evaluated; no new global depth-band layout is applied. Exact-depth rows would require a wider structural migration or new overlaps in the current contour-packed geometry. Existing canonical depth, major row and six aligned sibling groups remain. This pass improves connector clarity rather than claiming that all equal-depth nodes now share a row.

## Category Card Cleanup

Explicit rendering tokens keep radius 5, disclosure X15 and title/coverage start X34. Root/major header inset 8; deep-category inset 5; coverage bottom inset 7. Fixed root/major/category type sizes remain 28/21/17. Hover raises borders without shifting layout. Selected border and Inspector accent both use restrained violet. Category click selects; its independent chevron only changes disclosure. No double-click dependency.

## Topic Tray Cleanup

All 26 trays remain. Fainter outlines (.65-unit stroke, .38 opacity) and almost neutral surfaces reduce container mass. List Rows remain the default, Mini Cards stay an optional review variant. Topic minimum hit height remains 29; natural font 14. Status X12, labels X24 and evidence right inset 10 are fixed relative to each row boundary. Complete labels remain at most three lines; all six specified long-title checks pass. Individual full hit rectangles, source-title tooltips and true IDs remain.

## Visual Mass Reduction

No large region backgrounds, shadows or glow. Category boxes carry stronger contrast than tray outlines or rows. Default connector opacity is .32 for deep branches, .42 from majors and .55 from root. Active selection context is .95 violet. Required rows have amber tint/diamond, while relevant categories retain their normal surface and a subtle amber outline. No replacement of learned/verified state.

## Fit-All Composition

| Metric | V6.3 | V6.4 |
| --- | ---: | ---: |
| Fit content bounds including 8-unit allowance | 2272.94 × 1191.38 | 2260.14 × 1191.38 |
| Fit-All scale at 1920×1080 | 0.721533186 | 0.722691333 |
| Topic font, actual screen CTM | 10.101463675 px | 10.117678165 px |
| Left/right fit-bound whitespace | 15.00 / 15.00 px | 18.31 / 18.31 px |
| Top/bottom fit-bound whitespace | 58.69 / 26.69 px | 58.00 / 26.00 px |
| Area-weighted natural node center of mass | −46.918 / 672.162 | −46.918 / 672.162 |

Inspector width and fit margins are unchanged. Reduced exterior detours shrink fit width by 12.8 units; the result becomes narrowly height-limited at 1920. Screen center of node-area mass is about 4.18 px left of map center and 77.05 px below it; the latter reflects the many lower topic nodes, while upper control clearance is retained. All 135 node positions and the presentation checkpoint remain **identical** to V6.3. No phantom reserve enters Fit-All bounds. No artificial font scaling/hiding.

## Project Evidence Focus

Project selection immediately enables coverage, retaining V6.3 behavior. Project 113 highlights **26** exact individual Topics; Stage 4 highlights **12**. Relevant shared hierarchy intervals, ancestor borders, membership rails and tray outlines turn amber. Irrelevant sibling drops do not. Shared paths are rendered once, not repeated per requirement. Unrelated nodes/trays dim to **0.30** and remain rendered. Required rows retain separate mint learning/verified indicators. No extra tray count or duplicate evidence entity is added. Camera, node/tray geometry, checkpoint and expansion set have zero change across coverage Show/Hide. Manual-collapse roll-up still sums to 26, and conditional Reveal remains correct.

## Knowledge Relations

Default has no knowledge cross-links. Selected Topics expose only real direct prerequisites/dependents, in mint rounded/lane routes distinct from the slate orthogonal hierarchy and amber evidence paths. All 89 Topic selections and all 137 model routes avoid card interiors/text. Tray outlines do not form semantic barriers. Knowledge routes never affect layout. Violet hierarchy context and Inspector accent accompany selection.

## Major Region Balance

Foundations, Programming languages and DevOps retain their exact high-priority V6.3 anchors: x −887 / 248.5 / 887, y87.04. Their visible regional extents are approximately **567.2×1094.1**, **1680.9×1104.3** and **216.0×370.5** natural units. Different widths reflect the actual taxonomy, not artificial equal columns. DevOps has its own clear major heading and clean vertical branch. Regional bounding rectangles may interleave in unused contour space; actual cards/trays do not overlap. No full geography replacement or global rebalance was introduced.

## Typography

Natural Root/Major/Category/Topic/Meta sizes remain **28 / 21 / 17 / 14 / 10**. Primary acceptance **passes at 10.117678165 CSS px**, strictly ≥10. All labels scale with their geometry; no inverse-scale labels or screen-space hacks.

| Viewport | Fit scale | Root px | Major px | Category px | Topic px |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1920×1080 | 0.722691 | 20.2354 | 15.1765 | 12.2858 | 10.1177 |
| 1440×900 | 0.513243 | 14.3708 | 10.7781 | 8.7251 | 7.1854 |
| 1280×900 | 0.442451 | 12.3886 | 9.2915 | 7.5217 | 6.1943 |
| 1200×900 | 0.428075 | 11.9861 | 8.9896 | 7.2773 | 5.9931 |
| 1024×900 | 0.428075 | 11.9861 | 8.9896 | 7.2773 | 5.9931 |
| 768×900 | 0.326529 | 9.1428 | 6.8571 | 5.5510 | 4.5714 |
| 430×844 | 0.176980 | 4.9555 | 3.7166 | 3.0087 | 2.4777 |
| 390×844 | 0.159282 | 4.4599 | 3.3449 | 2.7078 | 2.2300 |
| 320×844 | 0.128311 | 3.5927 | 2.6945 | 2.1813 | 1.7964 |

## Desktop

1920, 1440, 1280, 1200, 1024 and 768 tested in both dark/light. Full 89/46 rendering, visible complete labels, initial fit, no page overflow, no card/tray overlap, clean orthogonal hierarchy and exact evidence pass. 1440 Topic text is **7.1854 px**, versus V6.3 **7.1449**; smaller overviews still need zoom for detail. My Knowledge/Course Roadmap IDs, coordinates, hierarchy and tray geometry are identical. Default, Topic selection and project focus now have visibly distinct emphasis.

## Mobile

430, 390 and 320 tested dark/light with complete taxonomy and Inspector below the map. Fit-All remains an orientation view; after Search/zoom, text is ≥16 CSS px. Touch pan/pinch, actual Topic/Category taps, Search, coverage Show/Hide and Stage 4 work. No mobile-specific semantic hiding or page horizontal overflow. Clean hierarchy and subtle trays persist at natural zoom.

## Growth Regression

Advanced OOP +5, Basics +20, Databases +20: **zero hierarchy crossings, zero route/card/tray intersections, zero card/tray overlap, zero major displacement**, deterministic rebuilt checkpoints. Existing movement remains local and matches V6.3: OOP and Databases move zero existing nodes; Basics moves 41 existing nodes, including six neighboring Java-region nodes outside Basics. No Foundations or DevOps anchor shifts. Growth routes retain maximum four bends. Synthetic fixtures are used only by tests, never normal runtime.

## Accessibility Regression

89 individual accessible Topic targets and 46 Category targets remain, with complete names, selected state and keyboard focus/Enter behavior. Trays have no extra tab stop. Disclosures retain aria-expanded and independent click/keyboard operation. Active requirements include “required by selected project” plus diamonds, not color alone. Inspector live-region and reduced-motion behavior remain. Automated Chromium tests do not replace a human screen-reader audit.

## Performance

Five sequential 1920 loads per version: median checkpoint-layout time **17.4 ms V6.3 → 75.2 ms V6.4**. Obstacle/rail-aware routing and shared-tree extraction add startup cost; mode, zoom, coverage and selection do not rerun layout. In the full regression run at 1440: parse 4.8 ms, tray packing 1.8 ms, render 5.3 ms, first Fit-All 5.6 ms, coverage max1.2 ms, Topic selection max12.3 ms and Search input0.2 ms. The exhaustive 89-selection run measured max selection8.6 ms and routing3.6 ms. Concurrent-test layout timing was101.7 ms, showing scheduling variation. Full rendering remains; no virtualization or hidden topics.

## V6.3 vs V6.4

**Improved:** 281→116 category segments, 3→0 crossings, 5.24→1.91 average bends, 41→4 maximum bends, quieter tray/line styling, clear selection context and amber focus. Fit font improves slightly. **Preserved:** all data/evidence counts, entire taxonomy/labels, all existing node positions, byte-identical checkpoint, 26 membership segments, mode geography, major anchors and interactions. **Not changed:** five staggered sibling families and global depth-band placement.

## Remaining Risks

Eight routes still need four bends; the universal two-bend preference is not achieved. Five sibling families remain staggered and the composition retains the contour-packed footprint. Runtime startup routing is about58 ms slower in the sequential median; interactions remain fast. Smaller desktop/mobile Fit-All text is an overview, not comfortable detail reading. Very faint dark connectors/tray outlines may benefit from user review. Three growth fixtures do not prove arbitrary future geometry. System-font metrics and assistive-technology behavior vary across platforms.

## Recommendation

Recommend retaining V6.4 as the isolated visual refinement: a calmer orthogonal hierarchy with explicit shared trunks, stronger evidence focus and zero measured crossings, while preserving accepted semantics and persistent geography. A future all-siblings-on-one-row migration would require a separate geometry iteration; it was deliberately not forced into this pass. No publishing action was taken.

## Local Review and Reproduction

All current suites pass: 43 functional, 30 boxed, 25 compaction, 25 tray and **19 composition** checks; source integrity, strict screen-CTM readability and all 89 selections/137 relations pass. Results live under `tests/*-results.json`; sequential startup samples are `tests/composition-performance.json`. Frozen before-reference: `tests/v6.3-baseline/`.

- [1920 Dark Fit-All](tests/review/v6.4/1920-dark-fit-all.png)
- [1920 Dark Project 113 Coverage](tests/review/v6.4/1920-dark-project-113.png)
- [1920 Dark Java / Basics](tests/review/v6.4/1920-dark-java-basics.png)
- [1440 Light Fit-All](tests/review/v6.4/1440-light-fit-all.png)
- [390 Dark Fit-All](tests/review/v6.4/390-dark-fit-all.png)
- [390 Dark zoomed Java / Basics](tests/review/v6.4/390-dark-java-basics.png)
- [V6.3 reference overview](tests/review/v6.4/comparison-v6.3-1920-fit-all.png)

Run the commands in `ARCHITECTURE.md`, including `node tests/composition.cjs`, with the local server running. Screenshots remain local and uncommitted.
