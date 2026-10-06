# Knowledge Atlas V6.3 — Validation

Validated locally in Chromium, 2026-10-03. Only this isolated prototype was edited. No commit, push or deployment. Source equality/hashes pass for categories, topics, edges, projects, stages, courses, progress and evidence; production maps/public preview/profile remain outside the change scope.

## Visual Result

The lower atlas reads as grouped reference lists rather than stacks of independent cards. Stronger category boxes remain the structural backbone. Faint topic-tray surfaces and compact individual rows reduce leaf-line clutter; complete labels and individual selection/evidence targets remain. Reviewed dark overview, Basics detail, project coverage, light overview and mobile screenshots. This is principally a visual-clutter improvement, not a large global scale improvement.

## Topic Tray Concept

26 presentation-only trays group 89 real topic nodes beneath their canonical parents. The model still contains exactly 135 taxonomy nodes: 46 categories plus 89 topics. Each rendered topic occurs once and is contained in its canonical tray. Trays have no semantic ID, Search result, Inspector object or extra keyboard stop. Category membership and all 45 canonical branch edges match V6.2.

## Leaf Packing Algorithm

Measured 1–4-column candidates, exact per-column widths and per-item heights; deterministic numeric-ID order. Width/height, unused space and preferred aspect 1.2–2.5 inform the score. Feasible multi-topic candidates inside 0.8–4 take precedence over extreme shapes. Global bounded feedback evaluates grid/category-region alternatives while retaining literal V6.2 major anchors. Seven current trays have five or more topics; their aspect ratios range from 0.937 to 3.034. The preferred ratio is deliberately soft. Mean tray occupancy by item-hit-area is **83.36%**; mean aspect across all trays is **2.1868**, versus V6.2 grid mean **2.8424**.

## Topic Item Design

Variant **B — List Rows** is the default. Variant **A — Mini Cards** was rendered at identical geometry in both Fit-All and Basics detail, and remains reviewable with `?items=mini`. Rows reduce nested box outlines while selection/focus/hover/evidence expose their full hit rectangles. No layout shift between variants. Natural font stays **14**; configured minimum width **172** versus 180 before; average width **172.58** versus **180.28**. Vertical padding is six versus eight. All six specified long names render completely in two or three lines; maximum is three, with zero clipping. Full-source tooltips and Inspector titles remain.

## Membership Line Reduction

| Metric | V6.2 | V6.3 |
| --- | ---: | ---: |
| Membership paths | 151 | 26 |
| Membership segments | 203 | 26 |
| Total membership length, natural units | 9900.19 | 312.00 |
| Category hierarchy segments | 303 | 281 |
| All hierarchy + membership segments | 506 | 307 |
| Average category hierarchy path length | 278.06 | 273.32 |
| Strict orthogonal segment crossings | 45 | 3 |

Membership segments decrease **87.19%**, and their total length **96.85%**. Each remaining membership path is one 12-unit shared rail. Crossings count strict perpendicular interior intersections in route polylines, excluding shared endpoints/collinear junctions; it is a geometry estimate, not a raster-pixel count. Zero hierarchy/membership segments enter category or topic card interiors. Three edge crossings remain; zero is not claimed.

## Bounding Box

| Metric | V6.2 | V6.3 |
| --- | ---: | ---: |
| Allocated root extent, natural units | 2269.00 × 1170.86 | 2242.94 × 1175.38 |
| Actual visible content extent | 2262.50 × 1170.86 | 2256.94 × 1175.38 |
| Fit bounds including allowance | 2278.50 × 1186.86 | 2272.94 × 1191.38 |
| 1920 Fit-All scale | 0.719771780 | 0.721533186 |
| Effective Topic font, actual SVG screen CTM | 10.076804399 | 10.101463675 |

Width decreases **0.244%**, height increases **0.381%**; total bounding area is slightly larger. 1920 remains width-limited: available fit area 1640×861; width ratio 0.721533 versus height ratio 0.722691. Inspector, fit margins and category typography remain unchanged. The map's overall item/card-area whitespace estimate rises from **56.15% to 60.65%**, partly because rows use smaller hit rectangles; this estimate excludes tray surfaces and is not a direct measure of visual emptiness. Trays solve clutter and local grouping more than outer bounds. Future-reserve inflation by 10,000 units leaves current visible fit bounds identical.

## Fit-All Typography

**PASS:** actual 1920×1080 Topic text **10.101463675 CSS px**, strictly ≥10 and above V6.2's **10.076804399**. No rounding-based pass, inverse scaling, font inflation, label hiding or screen-space overlays. Preferred >10.5–11 is **not achieved**; balanced trays and exact major-anchor stability were preserved instead.

| Viewport | Fit scale | Root px | Major px | Category px | Topic px |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1920×1080 | 0.721533 | 20.2029 | 15.1522 | 12.2661 | 10.1015 |
| 1440×900 | 0.510353 | 14.2899 | 10.7174 | 8.6760 | 7.1449 |
| 1280×900 | 0.439959 | 12.3189 | 9.2391 | 7.4793 | 6.1594 |
| 1200×900 | 0.428075 | 11.9861 | 8.9896 | 7.2773 | 5.9931 |
| 1024×900 | 0.428075 | 11.9861 | 8.9896 | 7.2773 | 5.9931 |
| 768×900 | 0.324690 | 9.0913 | 6.8185 | 5.5197 | 4.5457 |
| 430×844 | 0.175984 | 4.9275 | 3.6957 | 2.9917 | 2.4638 |
| 390×844 | 0.158385 | 4.4348 | 3.3261 | 2.6926 | 2.2174 |
| 320×844 | 0.127588 | 3.5725 | 2.6794 | 2.1690 | 1.7862 |

The same natural fit bounds apply at every width. My Knowledge and Course Roadmap have identical IDs, coordinates, tray geometry and hierarchy. All 89 topics and 46 categories remain rendered; no topic label is hidden by zoom or mode.

## Category / Topic Separation

Category cards keep V6.2 measured size/weight and explicit chevrons. Topic rows are lighter and enclosed by one faint outline. Within-tray row gaps are four units; between-tray contour separation is at least eight, with additional frame padding separating items across groups. Category→tray rail is 12. Root/major/deep level gaps remain 24/18/8. Trays with direct topics remain separate from child-category branches. No topic-to-topic hierarchy is drawn.

## Project Evidence

Project selection retains immediate coverage. Project 113 produces **26 exact highlighted individual topics** and 26 evidence markers; Stage 4 produces **12**. Learning/verification indicators remain 31/12. No applies or topic completion is inferred. Required accessible names include “required by selected project.” Shared tray/rail styling adds no extra evidence count. Manual-collapse roll-up still sums to 26 exactly; Reveal appears only when requirements are manually hidden.

## Project Path Highlight

Required topic border/tint/diamond, relevant tray boundary/shared rail and complete category ancestor path turn restrained amber. Unrelated nodes/trays remain present and dimmed, retaining orientation. Topic/card/tray coordinates, checkpoint, camera and expansion set have **zero displacement/diff** across project selection and Show/Hide. Fit coverage remains viewport-only. No aggregate count replaces individual evidence.

## Knowledge Relations

Default overview has zero cross-links. Each of the 89 topic selections exposes only its real direct prerequisites/dependents. All 137 routes avoid card interiors, use boundary side ports and leave geometry unchanged. Tray outlines are not routing barriers. Selected Topic and full-title Inspector remain true Topic IDs. Route detours and crossings can still occur in dense geometry.

## Major Anchor Stability

All three V6.2 major anchors are preserved **exactly** in V6.3: foundations x−887, programming languages x248.5, DevOps x887; shared y87.04. All growth fixtures have zero major-coordinate changes. Canonical category order/membership is unchanged; deeper anchors change once for V6.3 presentation packing. Schema 5 stores presentation geometry only, no topic coordinates or knowledge state.

## Growth Tests

| Fixture | Additional topics | Existing nodes moved | Major nodes moved | Card/tray/category overlaps |
| --- | ---: | ---: | ---: | ---: |
| Advanced OOP +5 | 5 | 0 | 0 | 0 |
| Basics +20 | 20 | 41 | 0 | 0 |
| Databases +20 | 20 | 0 | 0 | 0 |

Basics growth adds/expands a local tray and shifts adjoining Java subtrees down when free space runs out; six moved nodes lie outside Basics but remain within the Java region. No DevOps/foundations major displacement. Grown checkpoints rebuild deterministically. These synthetic fixtures are restricted to tests; normal runtime uses only real normalized data.

## Desktop

All six desktop widths were checked in dark/light. Full taxonomy, all complete labels, initial fit without clipping/overflow, zero target/frame overlap and project evidence pass. 1440 Topic text **7.144939065 px**, slightly above V6.2 **7.127496243**. 1024 preserves a structural overview; comfortable text reading requires zoom. Category click selects without collapse; explicit chevron changes only disclosure. Single-click entire topic targets, Enter selection, search centering and relation highlighting pass. No double-click dependency.

## Mobile

430, 390 and 320 tested in dark/light: complete taxonomy, no page horizontal overflow, Inspector below map. Tiny Fit-All text is expected; Search/zoom raises topic text to ≥16 CSS px. Actual touch topic/category taps, pinch zoom, drag pan, project coverage Show/Hide and exact Stage 4 selection pass. Labels remain present throughout. Mobile overview is for orientation rather than reading every label.

## Accessibility

Individual category/topic targets keep role/button names, aria-pressed, keyboard focus and Enter selection. Separate disclosure exposes aria-expanded. Tray surface is decorative; tray grouping is presentation-only and has no navigation stop. Native SVG title plus Inspector preserves full names. Evidence has textual accessible state and diamonds, not color alone. Reduced motion and live-region Inspector remain. Automated checks do not replace a manual screen-reader audit.

## Performance

Measured Chromium run at 1440: model parse **4.1 ms**, checkpoint layout **21.7 ms**, tray candidate packing within layout **1.6 ms**, initial render **5.2 ms**, first Fit-All **5.3 ms** (repeat ≤0.2 ms), topic selection max **7.8 ms**, coverage max **0.9 ms**, Search input **0.1 ms**. Exhaustive 89-topic selection run: max selection **6.3 ms**, max relation routing **2.6 ms**. Timing varies with browser scheduling; these are local observations. Offline checkpoint optimization: 5,158 candidates, **16.59 s**; it never runs on mode/evidence/selection/zoom. Full rendering is retained; no virtualization.

## Remaining Risks

Preferred 10.5–11 px overview text is not reached; improvement over V6.2 is only 0.02466 px. Fit has little spare width/height budget. Some trays remain below/above the soft preferred aspect ratio. Three hierarchy-route crossings remain. Basics growth requires local minor-subtree movement, although all majors stay fixed. Arbitrary future growth is not proven by three fixtures. Exact font metrics can vary across OS/system fonts. Screen-reader behavior needs human review. No claim of a substantially smaller global map is made.

## V6.2 vs V6.3 Recommendation

Recommend **V6.3 List Rows** for the prototype: substantially fewer leaf connections, stronger parent grouping and less box mass, while preserving all knowledge/evidence semantics and the strict Fit-All threshold. Mini Cards make every item boundary clearer but visually recreate nested UI-card stacks; keep them as a review variant. Continue to use zoom/search for detail. No publication or production change was made.

## Test Results and Local Review

All suites pass: 43 functional interaction checks, 30 boxed checks, 25 compaction checks, 25 tray checks, all 89-topic/137-relation routes, source integrity and strict screen-CTM readability. Machine results: `tests/results.json`, `boxed-results.json`, `compaction-results.json`, `tray-results.json`, `relation-results.json`, `readability-results.json`.

Requested local screenshots:

- [1920 Dark Fit-All](tests/review/v6.3/1920-dark-fit-all.png)
- [1920 Dark Java / Basics](tests/review/v6.3/1920-dark-java-basics.png)
- [1920 Dark Project 113 coverage](tests/review/v6.3/1920-dark-project-113.png)
- [1440 Light Fit-All](tests/review/v6.3/1440-light-fit-all.png)
- [390 Dark Fit-All](tests/review/v6.3/390-dark-fit-all.png)
- [390 Dark zoomed Java / Basics](tests/review/v6.3/390-dark-java-basics.png)

Direct before/after and A/B:

- [V6.2 overview](tests/review/v6.3/comparison-v6.2-1920-fit-all.png)
- [V6.2 Basics detail](tests/review/v6.3/comparison-v6.2-1920-basics.png)
- [Mini Cards overview](tests/review/v6.3/comparison-mini-1920-fit-all.png)
- [Mini Cards Basics](tests/review/v6.3/comparison-mini-1920-basics.png)
- [List Rows Basics](tests/review/v6.3/comparison-rows-1920-basics.png)

Screenshots are local, uncommitted review artifacts.
