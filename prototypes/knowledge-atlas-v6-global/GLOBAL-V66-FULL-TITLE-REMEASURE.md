# Global V6.6 full-title remeasure — preview for human acceptance

**C — FULL-TITLE GLOBAL V6.6 READY FOR HUMAN ACCEPTANCE**

Local review: [http://127.0.0.1:8801/](http://127.0.0.1:8801/).

The complete offline metadata observation is ingested and the authorized full-title remeasurement is complete. This is a V6.6 preview; human acceptance has not yet been recorded. The historical accepted report is unchanged.

## Geometry and retained design

Historical baseline: `atlas-v66-global-4-local-contours`, geometry SHA-256 `b38b9c7a692c27be27db7e4500b1a5b3abec85eac2ab0bf0c07852f0f8f1a6d9`.

Full-title preview: `atlas-v66-global-5-full-titles`, geometry SHA-256 `59e0bd708e1af9f62b85054358988119b9764d171718b1c19a5ea94c6dc7a383`.

The old fingerprint was reproduced from the untouched accepted model and runtime before comparison. The new fingerprint intentionally changes with real text input. Geometry is deterministic on fresh initialization; navigation never rebuilds it.

Only the obsolete reference-specific compact width was removed. All rows use the original V6.6 real-Topic baseline: 14 px system-ui, actual canvas measurement, preferred 220 px row width, 176 px text region, 17 px line spacing, and 12 px vertical padding. Existing width expansion (up to the 320 px preference ceiling, then sufficient width for an unbreakable word) is retained. No title is truncated, ellipsized, hidden, or forced into the old 68 px reference text region.

Trays with fewer than eight Topics retain one reading column. Larger trays evaluate the existing complete 1/2/3/4-column column-major packings with measured row heights and unchanged canonical numeric order. The existing local occupied-width/height cost selects the complete packing. The actual data selected **695 one-column and 30 two-column trays**; no tray needed three or four columns. Semantic groups are neither split nor paginated.

The accepted V6.6 visual language, five roots, local contour packing, sibling alignment, measured Category cards, separate card/subtree bounds, orthogonal routing, full-fidelity tiled renderer, minimap, selected-path orientation, overview optics, overlay/pinnable Inspector, and compact viewport chrome remain. No prerequisite/follower edges or new view were added. Approved dependency and hierarchy fields are retained in the Catalog/model and exposed in an optional Topic metadata Inspector section. The projection now explicitly emits zero resolution counts, preventing the former missing-zero count from breaking Global Inspector initialization.

## Before / after measurements

One identical 1440×900 Dark/DPR2 browser measurement oracle was used for both scenes. World distances are layout units; browser timings are single-run measurements, not a broad benchmark.

| Metric | Accepted ID-based Global | Full-title preview |
|---|---:|---:|
| World width | 30702.875000 | 33484.125000 |
| World height | 9879.280000 | 16597.840000 |
| Aspect ratio | 3.107805 | 2.017378 |
| Fit All scale | 0.045338 | 0.036824 |
| Browser layout build, ms | 177.200000 | 170.700000 |
| Tray packing, ms | 21.300000 | 24.200000 |
| Browser initialization, ms | 346.000000 | 351.600000 |
| Tray width: min / median / p90 / p95 / max | 128 / 128 / 264 / 264 / 264 | 236 / 236 / 236 / 236 / 480 |
| Tray height: min / median / p90 / p95 / max | 45 / 144 / 210 / 243 / 393 | 45 / 145 / 294 / 328 / 411 |
| Topic row width: min / median / p90 / p95 / max | 112 / 112 / 112 / 112 / 220 | 220 / 220 / 220 / 220 / 288.73 |
| Topic row height: min / median / p90 / p95 / max | 29 / 29 / 29 / 29 / 46 | 29 / 29 / 46 / 46 / 63 |
| Connector horizontal span: min / median / p90 / p95 / max | 0 / 82 / 1,056.25 / 1,773 / 17,222.25 | 0 / 130 / 1,407.25 / 2,194 / 14,960.25 |
| Hierarchy parent/child center distance: min / median / p90 / p95 / max | 103.06 / 316.63 / 1,469.92 / 2,063.43 / 13,827.18 | 103.06 / 408.97 / 1,759.02 / 2,424.30 / 15,859.88 |

Wrapped-line distribution: accepted **3,081 × 1 line, 25 × 2 lines**; full titles **2,273 × 1 line, 793 × 2 lines, 40 × 3 lines**. Maximum final wrapping is **3 lines / 63 px row height**. All 3,106 rows satisfy their measured line widths and complete title bounds.

| Root | Accepted bounds; width × height | Full-title bounds; width × height |
|---|---|---|
| Math | (-15346.44, 121.04)–(-12020.44, 1893.48); 3326.00 × 1772.44 | (-16737.06, 121.04)–(-11801.56, 2202.36); 4935.50 × 2081.32 |
| Computer science | (-11956.44, 121.04)–(7599.81, 9863.28); 19556.25 × 9742.24 | (-11737.56, 121.04)–(3476.69, 16581.84); 15214.25 × 16460.80 |
| Natural science | (5724.94, 121.04)–(9897.94, 826.12); 4173.00 × 705.08 | (3284.56, 121.04)–(9129.06, 873.06); 5844.50 × 752.02 |
| Product development | (9951.44, 121.04)–(12248.94, 817.90); 2297.50 × 696.86 | (9193.06, 121.04)–(12243.56, 1038.96); 3050.50 × 917.92 |
| Generative AI | (12306.94, 121.04)–(15346.44, 800.24); 3039.50 × 679.20 | (12307.56, 121.04)–(16737.06, 851.24); 4429.50 × 730.20 |

Root subtree bounding rectangles can interlock in unused space, as in the accepted contour design. Their **occupied contours, including reserved routing corridors, have zero sibling collisions**. Rectangular bounding-box interlocks are not occupied-space collisions.

Largest final tray by occupied area: **GitHub Actions, Category 2205**, 13 Topics, two columns, **480 × 328 = 157,440** layout units². Largest row width is **288.726562 px**, expanded by actual text measurement rather than an arbitrary global width.

Longest and widest title: **Topic 3887 — “Hard skills and daily responsibilities of an Ops / DevOps Engineer”**, 66 characters, **419.125 px natural width**, retained completely in three lines at 220 × 63 px. Other widest titles are Topic 2958 (402.417969 px) and Topic 4411 (389.388672 px), also fully retained. Full-catalog title character distribution, min/median/p90/p95/max: **2 / 20 / 35 / 39 / 66**; natural 14 px width distribution: **12.34 / 131.99 / 230.71 / 262.10 / 419.12 px**. These statistics use all 3,106 explicit titles, including the original 89.

## Structural and interaction checks

**34 focused checks passed**; browser errors: zero. [checks.json](tests/full-title/checks.json) records:

- Five roots; all 849 Categories and 3,106 Topics exactly once; zero unresolved leaves and zero ID-only display labels.
- Original structural memberships, canonical physical owners, numeric sibling order, hierarchy and reference history preserved. Semantic Topics remain bound to their existing numeric structural leaves.
- Zero Category/card overlaps, Topic-row overlaps, unrelated tray/card collisions, tray intersections, occupied sibling-contour collisions, invalid hierarchy endpoints, routes crossing cards/trays, duplicated routing segments, clipped or overlapping text, and ellipsis.
- Every one of 3,106 numeric-ID searches finds its Topic; every real-title query finds an exact-title Topic. Repeated titles remain valid identities and are individually addressable by numeric ID.
- All 3,106 Topic Inspectors show the real title, resolution state, numeric identity and memberships; all Topic focus calls use the final measured row. All 849 Category focus calls preserve the scene; representative complete subtrees fit the viewport.
- Full model/scene identity equality; complete semantic and command inventories at every raster level; complete spatial command index; actual main-thread fallback works with Worker disabled. No zoom-dependent semantic visibility.
- Pan, zoom, Category focus and Topic focus make **zero layout calls** and preserve layout, scene and command identities. Fresh initialization reproduces exact geometry.

Progress preserves the exact original **31 learned IDs and 12 verified IDs**. Every marker is attached to its correct final Topic row; verified rings share the learned core anchor. Fit All has **zero distinct progress-marker outer-AABB overlap**. World coordinates intentionally changed during remeasurement; semantic progress did not. [metrics.json](tests/full-title/metrics.json) records the IDs, anchors, and collision result.

The renderer source, paint code, worker and optics are unchanged. New geometry/version inputs regenerate scene, command indices and geometry-keyed tiles normally. Worker and fallback retain the complete scene and all semantic inventory at every raster resolution. Cache bytes remain below the existing 96 MiB cap. Fit All remains an orientation view; focusing Topic 3887 exposes the complete title at a 16 px projected font. No semantic zoom was introduced.

## One focused native Safari DPR2 performance check

Native Safari user agent: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/27.0.1 Safari/605.1.15`. Device pixel ratio **2**, embedded application viewport **1440 × 900**. One focused probe warmed each view, then measured pan/zoom in overview and navigation through one programming subtree and Topic 3887. [safari.json](tests/full-title/safari.json) contains the observed timing data.

| Warm view | Frame p95, ms | Renderer JS p95, ms | Max frame, ms | Frames >50 ms | Layout calls |
|---|---:|---:|---:|---:|---:|
| overview | 17 | 4 | 18 | 0 | 0 |
| subtree | 17 | 4 | 20 | 0 | 0 |
| topic | 17 | 4 | 18 | 0 | 0 |

Warm frame cadence matches the historical **17 ms p95** baseline. All views retain 3,956 scene entities, the same geometry and scene, and the bounded cache. No material warm regression was found, so no renderer optimization work was undertaken. Cold browser initialization is separately reported above; the focused Safari result measures warm navigation.

## Small visual review set

Exactly seven Dark/DPR2 captures at a 1440×900 CSS viewport were inspected. PNGs are 2880×1800 physical pixels. Large subtrees remain orientation views; reading focus exposes complete titles.

1. [Global Fit All](tests/full-title/review/01-global-fit-all.png)
2. [Computer science subtree](tests/full-title/review/02-computer-science.png)
3. [Natural science subtree](tests/full-title/review/03-natural-science.png)
4. [Dense programming branch](tests/full-title/review/04-programming-languages.png)
5. [Topic 3887 focus](tests/full-title/review/05-topic-3887.png)
6. [Derivatives: several long titles](tests/full-title/review/06-long-title-category.png)
7. [Learned/verified overview and selected path](tests/full-title/review/07-learned-verified-overview.png)

## Protected surfaces and stop

The [ingestion audit](tests/full-title/ingestion-audit.json) verifies all **1,199 protected files**, all **11 original Knowledge files**, and protected directory inventories byte-for-byte. State, Production (`docs/knowledge-map/`), original V6, My Skill Tree, and historical `GLOBAL-V66-ACCEPTED.md` remain unchanged. Changes are confined to the new immutable Knowledge observation and Global prototype/report/review evidence. Existing unrelated untracked files were preserved.

`git diff --check` passes. No commit, push or deployment was performed. No Hyperskill contact or acquisition browser was used. **Hard stop for human acceptance.**
