# V6.2 — Compact Readability Packing validation

Local Chrome/Playwright review, 2026-10-03. All edits remain inside `prototypes/knowledge-atlas-v6/`. No commit, push or deployment. All eight source tables and source hashes remain identical.

### Bottleneck Analysis

Measured **before optimization** at 1920×1080: fit bounds **2810×1517.2**, graph viewport **1630×945**, available fitted area **1586×837** after Inspector/margins. Width scale **0.5644**, height scale **0.551674**. **Height-limited, with width only about 2.3% less restrictive**. Both dimensions required compaction; optimizing only height would soon hit width.

At unchanged natural topic font 14, target scale is 10/14 = 0.714286. Original target bounds were at most 2220.4×1171.8. New Inspector/margin allowances modestly increase the design area to 1640×861, allowing at most 2296×1205.4.

### V6.1 Baseline

The accepted V6.1 implementation/checkpoint/reference page and results are archived locally under `tests/v6.1-baseline/`. Before/after measurements use the same 1920×1080 browser and actual model:

| Measurement | V6.1 | V6.2 |
|---|---:|---:|
| Natural allocated footprint | 2786.00×1485.20 | 2269.00×1170.86 |
| Visible cards + hierarchy (no border allowance) | 2806.00×1485.20 | 2262.50×1170.86 |
| Fit bounds including border allowance | 2810.00×1517.20 | 2278.50×1186.86 |
| Fit scale | 0.551674 | 0.719772 |
| Effective topic font | 7.723438 CSS px | 10.076804 CSS px |
| Average topic card width | 204.00 | 180.28 |
| Average topic-grid width / height | 2.458 | 2.842 |
| Non-card whitespace estimate | 2,768,570 units² (66.43%) | 1,487,367 units² (56.15%) |

“Natural allocated footprint” is the union of allocated contour/ownership geometry. Visible bounds measure actual cards and hierarchy points. Whitespace is the bounding rectangle minus the sum of non-overlapping card areas: an estimate including necessary hierarchy separation, not a claim that all this area can be removed. V6.1 fit used card bounds; V6.2 explicitly includes edge points.

### Compaction Strategy

Measured category widths, smaller deep-category headers/gaps, variable-height topic columns, actual-contour interleaving and bounded global feedback. Topic font remains **14**, configured minimum card width **180**. No screen-space/inverse-scale labels, semantic hiding, force layout or drilldown. All 89 topic names still render.

### Contour Packing

Actual rectangle contours can interleave in empty subtree regions. Vertical boundary alignments produce forbidden x intervals; the first free horizontal position is evaluated inside several actual-width regions. This is a deterministic variable-node contour sweep, not a formal Buchheim implementation. Grid ownership regions protect membership buses. Root major order remains Foundation → Programming languages → DevOps; descendants can occupy staggered shelves. No extra semantic parent is created.

### Topic Grid Optimization

One-to-five-column measured candidates include exact width, card height, label wrapping, aspect and unused-space scores. Contiguous stable ID order remains. Cards use their own heights within columns; short cards no longer inherit a neighbor's three-line row height. Global feedback tests narrower/wider grids according to the current bottleneck and evaluates the resulting **whole scene**, including alternative category-region packing.

The automatic model-only generation evaluated **7,834** candidates over at most 18 passes with a four-state beam and four deterministic contour seeds. It accepts no manually specified topic positions or category/column overrides. Finalists are rerouted and compared using full content bounds. Cached normal runtime does not rerun this search. The local pass began height-limited; the final scene is slightly width-limited.

### Category Card Compaction

Widths derive from actual bold title, wrapping, caption capacity, disclosure and padding. Typography stays root 28, major 21, category 17, meta 10. Long category names use two/three lines. Deeper headers reduce padding while keeping all title/caption geometry inside their cards. No competence values.

### Vertical Spacing

Root → major: **24** units; major → child: **18**; deeper category → child: **8**, versus the previous uniform 26. Topic grid begins **12** below its parent, versus 26; bus is 7 above the grid. Topic row gap **6**, column gap **10**, versus 8/12. Card padding, font and maximum three topic lines stay readable at natural scale. Full-label clipping/overlap tests pass.

### Visible Bounds vs Reserved Capacity

Current fit includes actual Category/Topic Cards and visible hierarchy/membership edge points, plus **8** natural units around content. No allocated empty slot enters fit. Inflating every checkpoint reserve width/height by 10,000 without adding content produces **exactly identical** visible fit bounds.

Desktop CSS fit allowances: **44 → 30** horizontal, **108 → 84** vertical. The actual graph stays 945 px high at 1920×1080. Inspector **290 → 250** increases graph width from 1630 to 1670. Both Inspector widths were tested by selecting every map node and project: zero horizontal overflow, heading 22 px, body 12 px, path unchanged at 11 px. With new geometry/margins but old 290-px Inspector, topic fit is 9.8310 px; 250 px reaches the accepted 10.0768 px. The width reduction is therefore a documented contributor, not the sole solution.

### Fit-All Results

All values measured from actual scene transformation, no rounded acceptance. Desktop tests use height 900 except the specified 1920×1080; mobile uses 844. Raw visible content includes cards and hierarchy, with no exterior border allowance.

| Viewport | Fit scale | Root px | Major px | Category px | Topic px | Visible bounds (units) |
|---|---:|---:|---:|---:|---:|---:|
| 1920×1080 | 0.719772 | 20.154 | 15.115 | 12.236 | 10.076804 | 2262.50×1170.86 |
| 1440×900 | 0.509107 | 14.255 | 10.691 | 8.655 | 7.127496 | 2262.50×1170.86 |
| 1280×900 | 0.438885 | 12.289 | 9.217 | 7.461 | 6.144393 | 2262.50×1170.86 |
| 1200×900 | 0.429705 | 12.032 | 9.024 | 7.305 | 6.015874 | 2262.50×1170.86 |
| 1024×900 | 0.429705 | 12.032 | 9.024 | 7.305 | 6.015874 | 2262.50×1170.86 |
| 768×900 | 0.323897 | 9.069 | 6.802 | 5.506 | 4.534563 | 2262.50×1170.86 |
| 430×844 | 0.175554 | 4.916 | 3.687 | 2.984 | 2.457757 | 2262.50×1170.86 |
| 390×844 | 0.157999 | 4.424 | 3.318 | 2.686 | 2.211982 | 2262.50×1170.86 |
| 320×844 | 0.127277 | 3.564 | 2.673 | 2.164 | 1.781874 | 2262.50×1170.86 |

All widths also pass full dark/light rendering, no page horizontal overflow and initial fitting of every card/hierarchy point.

### Effective Typography

**Primary PASS:** actual topic text **10.076804399490356 CSS px ≥ 10.0** at 1920×1080. `tests/readability.cjs` measures computed font multiplied by actual SVG screen CTM and exits 0. Natural font is still 14; scale 0.7197717797. No rounding converts a failure into success.

Root 20.154, major 15.115, category 12.236 CSS px. Topic font improves about **30.5%** over V6.1. At 1440 it improves **5.51 → 7.13 px**. Natural average cards are narrower, but their effective screen width increases from about 112.5 to 129.8 px. All six explicit long-name cases stay within three lines; every Topic/Card label and category caption stays inside its card. At 1024 the overview retains full root/major structure; fine reading still uses zoom.

### Project Evidence Regression

Project 113: exact **26** required Topic Cards and accessible requirement names. Stage 4: exact **12**. Amber cards, category ancestors and canonical paths; unrelated cards remain visible at 0.4 opacity. Mint learning indicators and 12 verification rings remain recognizable. Selection and Hide/Show coverage preserve exact card geometry, checkpoint serialization, camera and disclosure state. Roll-up totals remain 26, Reveal is conditional and Fit coverage changes only viewport. Project 380's known empty completed stages and unloaded requirements remain unchanged. Mobile touch controls also pass 26/12 checks.

### Knowledge Relations Regression

89 topic selections match exact direct prerequisites/dependents; all 137 model connections route to card boundaries with **zero card-interior intersections**. Default overview has zero knowledge cross-links. Compact gaps use 3-unit external ports. Hierarchy/membership lines also avoid card interiors. Cross-links never affect layout. Search centers the complete selected card, preserves mode, opens required ancestors and supplies about 17 px readable topic text.

### Major Anchor Stability

The **new V6.2 baseline** preserves all existing major anchors exactly in every Growth Fixture. No Foundation/DevOps displacement from unrelated Java growth. Baseline/grown checkpoint rebuilds reproduce coordinates and wrapping without floating-point drift. Canonical hierarchy, IDs and major order remain unchanged.

Absolute V6.1 coordinates change once during this explicit presentation compaction; unchanged absolute old anchors would constrain the requested smaller bounds. The V6.1 checkpoint remains archived; no public checkpoint is overwritten. Schema **4**, algorithm **atlas-compact-2**, contains presentation geometry only, never topic x/y or knowledge state.

### Growth Tests

| Fixture | Added topics | Existing nodes moved | Major anchors moved | Card overlap |
|---|---:|---:|---:|---|
| Advanced OOP | 5 | 0 | 0 | 0 |
| Basics | 20 | 52 | 0 | 0 |
| Databases | 20 | 0 | 0 | 0 |

Basics grows its band and repositions descendants plus **17 adjacent Java-region nodes outside Basics**. This preserves major geography while admitting local neighbor movement; it is more local movement than V6.1's 11 outside-Basics nodes. New Databases gets a region below the existing allocation. Every grown checkpoint rebuild is deterministic. Synthetic fixtures are test-only.

### Mobile

430/390/320: exact 89/46, all labels present, whole initial scene fits, no horizontal page overflow. Fit-all fonts are intentionally small; after For loop/Basics navigation, cards use roughly 17 px topic text. Automated touch pinch/pan, search, selection, Inspector below map and project/stage controls pass. No physical-device or screen-reader usability study was performed. Keyboard names/selection/disclosure/live region/reduced motion remain intact.

### Performance

Representative normal 1440 run: parse **3.3 ms**, stable layout **14.6 ms**, initial render **4.5 ms**, search **0.1 ms**, Fit all max about **5.2 ms**, selection max **8.2 ms**. All-topic routing stress max about **2.2 ms**. The offline global generation takes **33.5 s**; 7,834 bounded candidates are not recomputed on mode, selection, coverage, pan or zoom. A missing checkpoint would invoke the slow generation fallback, so the bundled validated checkpoint is important.

### Remaining Risks

The primary threshold has only about **0.077 px** headroom. Other system fonts/browser platforms require the same strict test; this report establishes the local Chrome/Linux result. Staggered category siblings and some long perimeter routes can make exact levels harder to read than a strict same-row tree. Minor anchors can move under local growth. Arbitrary growth beyond the tested fixtures has no universal collision-free guarantee. Smaller screens still require zoom for detailed reading. Global generation is intentionally an offline cost.

### Acceptance Result

**PASS.** Exact 89 Topic Cards / 46 Category Cards, 31 learned / 12 verified, complete labels, at most three topic lines, minimum width respected, zero card overlap/label clipping/hierarchy-card intersections. Mode coordinates identical; coverage displacement zero; Project/Stage requirements 26/12; Major Growth displacement zero. The sole failed V6.1 acceptance now passes strictly at **10.076804399490356 px**.

Functional suite **43** checks; box/routing/theme/growth suite **30**; compaction/typography/Inspector/reserve matrix **24**. Additional integrity, all-topic relation and strict readability suites pass. Machine-readable results are in `tests/results.json`, `boxed-results.json`, `compaction-results.json`, `relation-results.json`, `readability-results.json` and `optimization-results.json`.

### Recommendation

Use this compact V6.2 checkpoint for local review. Retain the strict 10.0 px test and bundled presentation checkpoint; do not trade completeness or natural typography for further density. Further work, if needed, should improve route clarity and cross-platform headroom. No publication is part of this task.

## Local review screenshots

- [1920 Dark — Fit-All](tests/review/v6.2/1920-dark-fit-all.png)
- [1920 Dark — Java/Basics subtree](tests/review/v6.2/1920-dark-java-basics.png)
- [1920 Dark — Project 113 coverage](tests/review/v6.2/1920-dark-project-113.png)
- [1440 Light — Fit-All](tests/review/v6.2/1440-light-fit-all.png)
- [390 Dark — Fit-All](tests/review/v6.2/390-dark-fit-all.png)
- [390 Dark — For loop / Basics detail](tests/review/v6.2/390-dark-java-basics.png)

Screenshots are local artifacts; nothing was committed.
