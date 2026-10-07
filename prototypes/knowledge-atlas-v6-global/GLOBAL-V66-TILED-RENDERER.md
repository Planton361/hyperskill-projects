# V6.6 Global Atlas — full-fidelity tiled renderer

Measured 2026-10-07 on this Mac. Recommendation: **C — FULL-FIDELITY GLOBAL V6.6 RENDERER READY FOR HUMAN REVIEW**.

The normal Global prototype now uses a viewport Canvas with bounded raster tiles. The accepted model, layout, coordinates, card/tray dimensions, connector geometry and semantic scope remain unchanged. Human navigation acceptance is still pending.

## Architecture and completeness

`model.js`, `model.json`, `layout.js`, `routing.js` and `style.css` are byte-identical to the pre-task versions. `app.js` retains D3 camera navigation, the existing 220 ms transitions, reduced motion, fit calculations, Search and Inspector. `index.html` replaces the heavy graph/minimap SVG surfaces with Canvas. New files are `tiled-renderer.js`, `tile-paint.js`, `tile-worker.js` and a focus-border-only `renderer.css`.

The immutable scene is compiled once after the authoritative layout. A static bounding-volume index serves draw-command queries and pointer hit testing. Compilation/index construction never occurs during camera navigation. No live per-entity SVG DOM or per-entity listeners remain.

The complete scene contains:

| Item | Count |
|---|---:|
| Real Categories | 849 |
| Leaf slots | 3,106 |
| Presentation-only context root | 1 |
| Learned Topics | 31 |
| Verified Topics | 12 |
| Actual label/meta text lines | 5,013 |
| Static surface/text commands | 8,969 |
| Permanent contour/marker/connector commands | 7,408 |
| Total required command IDs | 16,377 |

Every technical level exposes the **same 3,955 Knowledge IDs**, plus the same presentation context, and the **same 16,377 command IDs**. Tests compare each level against the original full SVG registry and validate each static command's spatial-index inclusion. Text is never conditional on zoom, rank or selected branch. All 3,106 slot cores and 12 verified rings keep their exact SVG world positions. Unresolved identities remain references; Search for 333 selects `reference:333` and the Inspector says “Unresolved reference”.

There is one deliberate fidelity split: static card surfaces and every text line are raster-tiled; permanent tray surfaces, hierarchy strokes, outlines, slot cores and verified rings are composited from the immutable command index in a batched Canvas ink pass at the actual camera scale. This preserves V6.6 **non-scaling strokes** and its existing optical marker-radius formulas during tile resampling. The permanent ink pass is part of every resolution's assembled full scene. It is separate from the tiny transient selection/hover overlay. Raw static texture files alone are therefore not claimed to contain the complete assembled scene.

Viewport clipping selects spatial intersections, never semantic samples. The complete coarse fallback contains every static entity/label; the full-scene ink pass supplies their original contours/status markers. Branch/Topic Focus only changes the camera. No semantic LOD, label thresholds, scope mutation, collapsed branches, counts replacing rows or geometry reflow were introduced. Existing shared connector segments are consumed once; none were added or redrawn per child.

## Tiles, cache and invalidation

Selected tile size: **512×512 physical pixels**, with a 2-pixel bleed on each side (516×516 backing bitmap). This kept measured worker tile bursts small enough for native warm navigation; a 1024 variant was unnecessary after measurement. No variants are exposed.

Ranks −9 through 3 correspond to powers of two from **1/512 to 8 pixels per world unit**. The requested rank is `ceil(log2(cameraScale × devicePixelRatio))`, clamped to available levels. At the accepted Global Fit, DPR2 requests rank −6. Two rank −8 tiles cover the entire frozen world and stay pinned. Missing sharper tiles immediately use the nearest cached containing lower-resolution tile; the region never becomes empty. New tiles replace that fallback when ready.

Only the coarse world coverage and current viewport are prewarmed. Higher-resolution tiles are created on demand. The worker uses the same painter and immutable scene, with one job in flight. Obsolete unstarted jobs are discarded in favor of the latest camera. OffscreenCanvas/ImageBitmap is optional; the identical main-thread painter is tested as a fallback. API basis: [HTML Canvas standard](https://html.spec.whatwg.org/multipage/canvas.html#the-offscreencanvas-interface).

LRU capacity is **96 MiB of tile pixel storage**. Eviction closes ImageBitmaps or releases Canvas backing sizes. Recorded maximum: **94 tiles / 100,112,256 bytes (95.48 MiB)**, below the 100,663,296-byte cap. Diagnostic histories are bounded. The viewport's 2380×1530 backing surface adds about 13.9 MiB; minimap about 0.20 MiB; one in-flight tile about 1.02 MiB. These are pixel estimates, **not process RSS**: browser/GPU copies, fonts, command objects and BVH storage are additional.

Theme changes discard raster cache and rebuild its palette/base coverage without changing the command geometry. Future progress updates would rebuild affected status/style commands from the authoritative new progress snapshot and invalidate tiles/index entries; no real progress mutation or update UI was added. Hover/selection only redraw the transient overlay and existing taxonomy emphasis.

## Measurement method

Primary: **native Safari 27.0.1**, actual **DPR2**, 1440×900 Atlas iframe in a fully visible 1728×951 browser content window. Regression: headed **Chrome for Testing 149.0.7827.55**, actual DPR2, the same 1440×900 Atlas in a 1500×916 content window. Performance runs do not emulate DPR. The map itself occupies 1190×765 CSS pixels; the remaining width is the existing Inspector.

The repeatable driver first measures blank-page idle rAF cadence, then loads the actual prototype. It exercises actual D3 mouse-pan/wheel handlers with a time-based continuous trajectory: horizontal/vertical pans, zoom in/out and 220 ms branch/Topic navigation. Cold samples include the first real navigation/tile requests. Warm paths are prewarmed explicitly. Separate Global-orientation pans/zoom exercise the whole visible scene. No browser workloads were run simultaneously.

The table intervals are **observed rAF callback spacing**, not proof of physical monitor scanout. Chromium also has a recorded browser trace. Safari JS/tile timings come from browser-side instrumentation; no separate Safari GPU/style-layout profiler trace is claimed. Its millisecond timer quantization makes a reported 0 ms mean “below timer resolution”. Tile-composite timings measure `drawImage` submission, not GPU completion.

Primary artifacts: `tests/tiled/safari-svg-3.json`, `safari-tiled-6.json`, `chromium-svg-2.json`, `chromium-tiled-5.json`. Earlier diagnostic runs are retained but are not used for the acceptance tables. The SVG diagnostic oracle is a copy of the **current optimized pre-task Global** implementation, not historical Course V6.6 and not another product direction.

| Idle cadence | SVG median / p90 / p95 / max ms | Tiled median / p90 / p95 / max ms |
|---|---:|---:|
| Safari | 17.0 / 17.0 / 18.0 / 28.0 | 17.0 / 18.0 / 22.0 / 27.0 |
| Chromium | 8.3 / 8.8 / 9.1 / 9.3 | 8.3 / 9.2 / 9.6 / 10.3 |

## Initial render and cold cache

| Measurement, ms | Safari SVG | Safari tiled | Chromium SVG | Chromium tiled |
|---|---:|---:|---:|---:|
| First public API ready | 533.0 | 484.0 | 362.1 | 305.1 |
| Browser initialization | 326.0 | 440.0 | 240.5 | 237.4 |
| Layout, once | 167.0 | 220.0 | 80.1 | 74.6 |
| Initial draw / scene compilation and base coverage | 49.0 | 198.0 | 55.6 | 106.7 |
| Fit All synchronous call | 2.0 | 5.0 | 8.2 | 26.6 |

Scene compilation was 116.0 ms in Safari and 66.1 ms in Chromium. Coarse prewarm plus minimap was 35.0 / 15.3 ms. First API availability is not a claim that all sharper visible tiles have settled. The cold-global phase includes settling them. Safari initial draw grows because compilation/base coverage replaces deferred SVG raster work; its layout timing also varies independently although the layout file is unchanged. The first build remains a noticeable long frame.

Safari cold cache:

| Phase | SVG ms: median / p90 / p95 / max | Tiled ms: median / p90 / p95 / max | Tiled samples |
|---|---:|---:|---:|
| First Global Fit / initial build | 18.0 / 101.0 / 101.0 / 502.0 | 16.0 / 20.0 / 24.0 / 456.0 | 15 |
| First Computer science navigation | 24.0 / 140.0 / 140.0 / 151.0 | 17.0 / 18.0 / 20.0 / 24.0 | 17 |
| First dense-region navigation + pan | 114.0 / 128.0 / 136.0 / 219.0 | 17.0 / 17.0 / 17.0 / 25.0 | 131 |

Chromium cold cache:

| Phase | SVG ms: median / p90 / p95 / max | Tiled ms: median / p90 / p95 / max | Tiled samples |
|---|---:|---:|---:|
| First Global Fit / initial build | 8.4 / 16.7 / 16.7 / 291.6 | 8.3 / 9.4 / 9.7 / 225.0 | 22 |
| First Computer science navigation | 41.7 / 50.0 / 50.0 / 58.4 | 8.3 / 8.5 / 8.8 / 9.2 | 29 |
| First dense-region navigation + pan | 8.3 / 8.9 / 9.3 / 50.1 | 8.3 / 8.5 / 9.4 / 10.4 | 251 |

The first Computer science transition needed no additional tiles in this trajectory because its requested rank was covered by the preceding Global Fit tiles. The first Programming languages pan generated new tiles. “Cold” does not artificially clear useful global coverage between operations.

## Warm continuous navigation

Safari / actual DPR2:

| Phase | SVG ms: median / p90 / p95 / max | Tiled ms: median / p90 / p95 / max | Tiled samples |
|---|---:|---:|---:|
| Dense horizontal pan | 132.0 / 136.0 / 137.0 / 139.0 | 17.0 / 17.0 / 17.0 / 19.0 | 111 |
| Dense vertical pan | 132.0 / 136.0 / 139.0 / 153.0 | 17.0 / 17.0 / 17.0 / 18.0 | 111 |
| Dense continuous zoom in/out | 141.0 / 151.0 / 191.0 / 196.0 | 17.0 / 17.0 / 17.0 / 17.0 | 157 |
| Repeated branch / Topic navigation | 82.0 / 134.0 / 138.0 / 146.0 | 17.0 / 17.0 / 18.0 / 27.0 | 97 |
| Global horizontal pan | 92.0 / 94.0 / 94.0 / 96.0 | 17.0 / 17.0 / 17.0 / 26.0 | 111 |
| Global vertical pan | 87.0 / 90.0 / 90.0 / 93.0 | 17.0 / 17.0 / 17.0 / 18.0 | 111 |
| Global continuous zoom in/out | 92.0 / 99.0 / 100.0 / 115.0 | 17.0 / 17.0 / 17.0 / 18.0 | 159 |

Chromium / actual DPR2:

| Phase | SVG ms: median / p90 / p95 / max | Tiled ms: median / p90 / p95 / max | Tiled samples |
|---|---:|---:|---:|
| Dense horizontal pan | 8.3 / 8.4 / 8.8 / 17.1 | 8.3 / 9.5 / 10.0 / 10.3 | 219 |
| Dense vertical pan | 8.3 / 8.4 / 8.6 / 17.5 | 8.3 / 9.8 / 10.0 / 10.3 | 219 |
| Dense continuous zoom in/out | 50.0 / 58.3 / 58.3 / 58.6 | 8.3 / 9.5 / 10.0 / 10.3 | 312 |
| Repeated branch / Topic navigation | 41.7 / 58.3 / 58.3 / 66.6 | 8.3 / 8.7 / 9.6 / 10.3 | 150 |
| Global horizontal pan | 8.4 / 16.7 / 17.6 / 25.0 | 8.3 / 8.4 / 9.2 / 10.3 | 219 |
| Global vertical pan | 8.4 / 16.7 / 16.8 / 25.0 | 8.3 / 9.1 / 9.9 / 10.3 | 219 |
| Global continuous zoom in/out | 49.9 / 58.3 / 58.4 / 59.4 | 8.3 / 8.4 / 9.2 / 10.3 | 313 |

Safari warm p95 is 17 ms for both pan directions and zoom, matching its 17 ms median idle cadence. Repeated navigation p95 is 18 ms. Isolated 26/27 ms warm outliers remain, comparable to the 27 ms idle maximum in this run. Chromium pan was already near idle in the optimized SVG baseline; its major improvement is zoom/navigation. These continuous samples support readiness for human review, not a claim of completed human acceptance.

## JavaScript, tile costs, browser work and cache

Timings below are median / p95 milliseconds. Ink is sampled separately for each back/front pass, not their combined duration. Worker generation is elapsed worker time per produced tile; it does not block main-thread input.

| Browser / phase | Render JS | Tile draw submission | Ink pass | Worker tile generation | Desired-level cache hits |
|---|---:|---:|---:|---:|---:|
| Safari / Dense horizontal pan | 2.0 / 3.0 | 0.0 / 0.0 | 1.0 / 2.0 | 0.0 / 2.0 | 99.7% |
| Safari / Dense vertical pan | 2.0 / 3.0 | 0.0 / 0.0 | 1.0 / 2.0 | 0.0 / 0.0 | 99.8% |
| Safari / Dense continuous zoom in/out | 2.0 / 4.0 | 0.0 / 0.0 | 1.0 / 2.0 | 0.0 / 2.0 | 92.3% |
| Safari / Repeated branch / Topic navigation | 2.0 / 4.0 | 0.0 / 0.0 | 1.0 / 2.0 | 0.0 / 1.0 | 48.0% |
| Safari / Global continuous zoom in/out | 3.0 / 4.0 | 0.0 / 0.0 | 2.0 / 2.0 | 0.0 / 0.0 | 100.0% |
| Chromium / Dense horizontal pan | 1.9 / 2.1 | 0.1 / 0.2 | 0.9 / 1.0 | 0.2 / 1.0 | 99.9% |
| Chromium / Dense vertical pan | 1.7 / 1.8 | 0.1 / 0.2 | 0.7 / 0.9 | 0.0 / 0.1 | 99.9% |
| Chromium / Dense continuous zoom in/out | 1.5 / 2.6 | 0.1 / 0.2 | 0.7 / 1.2 | 0.1 / 1.3 | 98.3% |
| Chromium / Repeated branch / Topic navigation | 1.0 / 2.3 | 0.1 / 0.2 | 0.5 / 1.1 | 0.0 / 0.4 | 73.3% |
| Chromium / Global continuous zoom in/out | 2.4 / 2.6 | 0.0 / 0.1 | 1.2 / 1.4 | 0.0 / 0.0 | 100.0% |

Hit rate counts desired-level lookups: `hits / (hits + fallback lookups)`. Repeated navigation traverses many intermediate resolution ranks and the 96 MiB LRU evicts them; it therefore has a lower desired-level hit rate while retaining complete coarse fallback and near-idle frame cadence. New sharper tiles are never counted as newly revealed knowledge. Safari produced 1,318 tiles and evicted 1,224; Chromium produced 2,200 and evicted 2,106 over the whole probe. Queue misses also include requests later canceled when the camera changes.

Main-thread tile generation occurred only for two pinned coarse tiles during startup: maximum 21 ms Safari / 10.3 ms Chromium per tile. Subsequent measured tile generation ran in the worker; recorded main-thread tile-generation count was zero for every navigation phase. Cold worker maxima were 9 ms Safari / 10.2 ms Chromium. The measured minimap base is built once, then only its bitmap and two small bounds overlays are submitted. No thousands of minimap primitives survive.

Chromium trace totals for the continuous dense zoom phase (about 2.6 seconds):

| Trace work | SVG ms | Tiled ms |
|---|---:|---:|
| Main JS / native Canvas submission | 19.2 | 490.9 |
| Style / Layout | 1330.6 | 8.1 |
| Paint | 541.5 | 5.4 |
| PrePaint | 284.6 | 7.9 |
| Composite | 199.4 | 1.6 |
| Raster | 389.0 | 1.2 |

The optimized SVG bottleneck is browser style/layout/paint/raster work during scale changes, rather than graph layout or high-cost event JS. Canvas trades that browser SVG work for a measured bounded main-thread ink/composition pass plus cached text rasterization. Trace categories overlap and thread durations are not an additive wall-time budget. The main JS aggregate includes native Canvas API submission; it is not pure V8 CPU time.

Chromium compositor `DrawFrame` dense-zoom median / p95 changes from 51.7 / 56.8 ms to 8.3 / 10.0 ms. Tiled trace maxima are 25.9 ms for dense zoom and 32.9 ms for repeated branch navigation, even though rAF callback maxima are lower. These events are another browser-side observation, not confirmed display presentation. Compressed traces and all phase summaries: `tests/tiled/trace-svg-2.json.gz`, `trace-tiled-5.json.gz`, `trace-svg-2-summary.json`, `trace-tiled-5-summary.json`.

## Visual fidelity and interaction

Paired 1440×900 Dark / DPR2 captures (2880×1800 PNGs), each with exactly equal camera transforms and Inspector HTML:

| State | Optimized SVG reference | Tiled renderer |
|---|---|---|
| Global Fit All | [SVG](tests/tiled/svg-global.png) | [Tiled](tests/tiled/tiled-global.png) |
| Computer science | [SVG](tests/tiled/svg-computer-science.png) | [Tiled](tests/tiled/tiled-computer-science.png) |
| Programming languages | [SVG](tests/tiled/svg-programming-languages.png) | [Tiled](tests/tiled/tiled-programming-languages.png) |
| Topic 518 / Formatted output | [SVG](tests/tiled/svg-topic.png) | [Tiled](tests/tiled/tiled-topic.png) |

Review preserves the full hierarchy, measured card/tray silhouettes, actual text and progress distribution. No optical spacing/color redesign was made. SVG non-scaling strokes remain explicit Canvas ink at identical widths/opacity. Existing marker-radius formulas remain optical styling and never control existence. No extra shared connector segments were introduced.

Canvas/SVG font antialiasing and tile resampling differ; **the screenshots are not pixel-identical**. Map-area mean absolute RGB-channel differences (0–255, excluding the minimap) are global: 0.257, computer-science: 0.311, programming-languages: 0.310, topic: 0.380. These averages include substantial background and are supplementary, not proof of semantic or visual parity. `tests/tiled/visual.json` retains pixel counts/maxima. Exact labels, world positions and states are checked independently.

The minimap now shows one full-scene raster from the same command model; it replaces the previous abstract miniature card/tray palette. This is an explicit miniature-rendering delta. Its frozen world bounds, viewport clamp and full selected-subtree bounds overlay remain correct. Main-map V6.6 visuals, header, controls and Inspector retain their accepted styling.

Canvas hit testing returns the exact entity at every card/row center, with deterministic topmost render-order precedence. Category click selects without moving the camera. Topic/reference click and Search select/focus the existing semantic key. Hover keeps the real leaf tooltip and clears it on pointer leave; hover hit identity is recomputed through the latest camera without per-frame DOM geometry measurement.

Accessibility delta: thousands of per-SVG-node Tab stops are replaced by one Canvas Tab stop and canonical roving navigation with arrows, Home/End and Enter/Space. Selected identity/type/path is exposed in the Canvas accessible name and live announcement; the HTML Inspector retains evidence/state content. Search keyboard use and reduced motion remain. This is **not full historical per-node screen-reader parity** or a complete accessibility redesign. No hidden duplicate SVG scene was retained.

## Focused checks and protected files

**44 focused checks pass**, zero browser errors. They cover full semantic ID equality, per-level command/index completeness, all label/meta strings and exact X / 1e−6-unit Y positions, all marker positions, four identical cameras/Inspectors, Search including unresolved references, real pointer clicks/hover, keyboard/reduced motion, minimap bounds, bounded cache and actual eviction, and main-thread fallback. Navigation makes zero layout calls, zero scene/index recompilations and zero scope changes. Every performance run records exactly one initial authoritative layout call. No full repository or historical matrix was run.

Serialized accepted geometry is byte-identical before/after. SHA-256:

`4081d9e31f1f0404fac686511d4fcef176ac00901206d4317cfc6584e1f8fc89`

`tests/tiled/protected-before.json`, `protected-after.json` and `preservation.json` confirm all **455 protected files and directory inventories** unchanged: original V6.6, My Skill Tree, `docs/knowledge-map/`, `state/knowledge-atlas/`, `data/knowledge/`, and Production/shared runtime `scripts/knowledge_atlas/`. Of previously existing Global root files, only `app.js` and `index.html` change; layout/model/routing/data/style and existing reports remain unchanged. All added work and diagnostic artifacts are inside this Global prototype.

## Remaining limits and local review

The first build remains approximately 0.48 s to API availability on the final Safari run, with a 456 ms long frame dominated by initial model/layout/scene work. Theme invalidation also rebuilds coarse coverage. High-resolution intermediate levels can sharpen after navigation as cached complete lower-resolution text is replaced. Main-thread fallback is functionally verified, but its native continuous-performance profile is not asserted. Texture cap is not a total GPU/process-memory guarantee. Browser/font/DPR combinations beyond this Mac were not profiled. Human judgement of continuous navigation remains required.

From the repository root:

```sh
python3 -m http.server 8777 --bind 127.0.0.1 --directory prototypes/knowledge-atlas-v6-global
```

Local prototype: [http://127.0.0.1:8777/](http://127.0.0.1:8777/). The existing local server currently serves it.

Focused replay:

```sh
python3 prototypes/knowledge-atlas-v6-global/tests/tiled/server.py
node prototypes/knowledge-atlas-v6-global/tests/tiled/checks.cjs
node prototypes/knowledge-atlas-v6-global/tests/tiled/visual.cjs
node prototypes/knowledge-atlas-v6-global/tests/tiled/performance.cjs svg 2
node prototypes/knowledge-atlas-v6-global/tests/tiled/performance.cjs tiled 5
node prototypes/knowledge-atlas-v6-global/tests/tiled/trace-summary.cjs
```

The Chromium scripts use the installed Playwright package and cached Chrome for Testing; neither was installed or changed. For native Safari, open `http://127.0.0.1:8783/tests/tiled/run.html?browser=safari&renderer=tiled&run=6` in a window large enough to show the entire 1440×900 iframe. Use `renderer=svg` for the frozen optimized-SVG diagnostic comparison. Do not run another browser workload concurrently. JSON results are saved locally by the test server.

No personal-view, Course, Project, Production, State or Knowledge work. No commit, push or deployment.
