# V6.6 Global — final vertical composition

## Result and scope

The final composition keeps the accepted compact X geometry exactly and gives the forest visibly separated depth levels. At 1440×900 Dark, the world occupies 222.65 vertical screen pixels instead of 57.16, with the same Fit All scale. The five roots remain aligned; their real subtrees finish at different depths. Topic trays retain their V6.6 surfaces and every individual slot.

Only `layout.js` changed among the eight runtime/data files recorded before this pass. `app.js`, `style.css`, `index.html`, `model.js`, `model.json`, `routing.js` and `taxonomy-relations.js` are byte-identical to the compact-X baseline. No new UI, visualization family, alternate page, zoom state or data semantics were introduced.

## Why it appeared flat

The previous band spacing added only 72–88 world units of clearance around measured cards and trays. Once X packing improved, the complete map was still 254,297 units wide but only 12,728.84 high: a 19.98:1 strip. Large upper-depth cards consumed most of that height; deeper levels were separated by only about 613–889 units. Fit All projected the entire hierarchy into 57 pixels. The accepted horizontal packing was not the cause of missing vertical hierarchy and has been retained.

## Final deterministic policy

All measurements below are world units unless explicitly marked as screen pixels. Depth 0 is the presentation-only Global Atlas context; depth 1 contains the five real root Categories. This does not add a Knowledge entity or alter taxonomy depth.

For each depth, measure maximum Category-card height `H` and maximum owned tray height `T`. Use half the measured presentation-card height as the optical rhythm reference, `R = H₀ / 2 = 2,017.28`.

```text
trayGap = T > 0 ? 68 + clamp(0.35 × sqrt(H × T), 60, 92) : 68
factor(d) = d < 2 ? 1.3 + 0.25d : 2.2 + 0.16 × min(d − 2, 4)
nextClearance = max(30, R × factor(d))
ownedRequirement = max(28, T > 0 ? trayGap + T : 0)
Y[d + 1] = Y[d] + H + ownedRequirement + nextClearance
```

The modest depth-factor progression is capped. It reserves measured owned content before the next band, then supplies a consistent optical separation relative to the existing large upper-level cards. It is independent of viewport, camera scale, progress and search. Absolute band assignment ensures exact same-depth Y equality rather than accumulating rounding differences down different ancestry paths.

Three deeper-band starting factors (1.6, 2.2 and 2.8) were evaluated numerically in memory. The middle value produced a 223-pixel hierarchy without consuming the larger candidate's 255 pixels. Only this final policy was implemented. See `tests/vertical-composition/numeric-policy-evaluation.json`.

Tray offsets increase from 68 to 128–160 below the owner card. Their minimum/median/maximum are 128 / 133.25 / 160. Their X positions, widths, heights, columns, rows and canonical order are unchanged. The small local owner-to-tray stems remain identifiable. Each tray is terminal within its actual branch; no artificial global leaf baseline or bottom alignment is imposed.

## Before / after geometry

| Metric | Before | After |
|---|---:|---:|
| Global width | 254,297.00 | 254,297.00 |
| Global height | 12,728.84 | 49,580.01 |
| Width / height | 19.98 | 5.13 |
| Fit All scale | 0.0044908119246393 | 0.0044908119246393 |
| Projected world height, pixels | 57.16 | 222.65 |

Width and Fit All scale are exactly unchanged. Height increases 3.90×. Fit All remains width-limited, so this pass spends available vertical screen space without making any Topic or root card smaller. Every node and tray retains its original X coordinate and dimensions. Sibling-envelope gaps remain 24; inter-root gaps remain 112. No horizontal corridor returns.

### Depth bands

`Gap` means next baseline minus current baseline, including card, owned tray and clearance. Values are rounded here; exact values and one distinct Y per depth are recorded in the JSON evidence.

| Depth | Before Y | After Y | Before gap | After gap | After tray offset |
|---|---:|---:|---:|---:|---:|
| 0 | 0.00 | 0.00 | 4,122.56 | 6,685.02 | — |
| 1 | 4,122.56 | 6,685.02 | 3,587.92 | 6,660.70 | — |
| 2 | 7,710.48 | 13,345.73 | 1,424.92 | 5,882.94 | 160.00 |
| 3 | 9,135.40 | 19,228.66 | 888.72 | 5,669.50 | 160.00 |
| 4 | 10,024.12 | 24,898.16 | 666.18 | 5,745.56 | 135.84 |
| 5 | 10,690.30 | 30,643.73 | 633.18 | 6,032.74 | 133.25 |
| 6 | 11,323.48 | 36,676.46 | 613.12 | 6,330.20 | 128.00 |
| 7 | 11,936.60 | 43,006.66 | 618.18 | 6,339.29 | 132.04 |
| 8 | 12,554.78 | 49,345.95 | — | — | 128.00 |

### Root envelopes

The order below is the existing canonical catalog order. Every root has before Y₀ = 4,122.56 and after Y₀ = 6,685.024. X bounds are unchanged. Envelope bounds include the existing interaction safety margins; they extend slightly beyond the rendered-content bounds used by Fit All.

| Root | X₀ → X₁, unchanged | Width, unchanged | Before Y₁ | After Y₁ | Before height | After height |
|---|---:|---:|---:|---:|---:|---:|
| Math | -127,158.50 → -91,097.50 | 36,061.00 | 10,933.48 | 30,952.15 | 6,810.92 | 24,267.13 |
| Computer science | -90,985.50 → 69,078.50 | 160,064.00 | 12,724.84 | 49,576.01 | 8,602.28 | 42,890.99 |
| Natural science | 69,190.50 → 88,438.50 | 19,248.00 | 10,999.48 | 31,018.15 | 6,876.92 | 24,333.13 |
| Product development | 88,550.50 → 107,798.50 | 19,248.00 | 10,564.30 | 25,506.18 | 6,441.74 | 18,821.16 |
| Generative AI | 107,910.50 → 127,158.50 | 19,248.00 | 10,366.30 | 25,308.18 | 6,243.74 | 18,623.16 |

## Connectors

Routing code is unchanged: a short parent stem, a shared local orthogonal rail and child drops. Parent stems remain 28 units. Only vertical drops and the 128–160-unit tray offsets grow. The 2,715 rendered segments and 1,574 logical routes (849 context/Category routes plus 725 tray routes) are unchanged. Horizontal spans match individually, not just statistically.

For logical routes, span is `max(coordinate) − min(coordinate)` over the complete routed path; shared rails are physically drawn once. Physical-segment statistics are also retained in the JSON.

| Span metric | Before | After |
|---|---:|---:|
| Horizontal median | 119.00 | 119.00 |
| Horizontal p90 | 1,632.00 | 1,632.00 |
| Horizontal p95 | 3,382.50 | 3,382.50 |
| Horizontal max | 117,534.50 | 117,534.50 |
| Vertical, all routes median | 383.00 | 4,841.02 |
| Vertical, all routes p90 | 581.00 | 5,660.38 |
| Vertical, all routes p95 | 581.00 | 5,947.56 |
| Vertical, all routes max | 581.00 | 6,265.08 |
| Vertical, Category routes median | 548.00 | 5,328.78 |
| Vertical, Category routes p90 | 581.00 | 5,947.56 |
| Vertical, Category routes p95 | 581.00 | 5,947.56 |
| Vertical, Category routes max | 581.00 | 6,265.08 |

The greater vertical span is intentional hierarchy separation. Horizontal median/p90/p95/maximum are exactly preserved. Connector collision and endpoint checks still pass across the complete scene.

## Focused validation

**39 / 39 checks pass**: the existing 35 focused checks plus four vertical-only preservation checks. Evidence: [results.json](tests/vertical-composition/results.json), [before.json](tests/vertical-composition/before.json), [after.json](tests/vertical-composition/after.json).

- All 849 Category identities and 3,106 leaf identities render exactly once; all five real roots exist under the presentation-only context.
- All 3,106 individual slot cues persist. There are 725 trays and 31,566 SVG elements.
- Canonical sibling and leaf ordering is preserved. Every same-depth Category Y is exactly equal, without rounding.
- Zero card overlaps, tray/card collisions, tray/tray overlaps, sibling-envelope overlaps or incomplete envelopes.
- Every hierarchy endpoint is valid; no route passes through an unrelated card or tray.
- Resolution remains 1 resolved Topic, 88 partial Topics and 3,017 unresolved references. References retain numeric identity and known memberships; no titles, URLs, theory or Topic metadata are invented.
- All node/tray X coordinates, dimensions, row identities and labels are exactly equal to before. Every logical route's horizontal span matches before.
- Fit All and complete subtree fits contain their target geometry. Selection does not move the camera. Search, Topic Focus, keyboard and reduced-motion behavior pass.
- Zoom, pan, search and navigation cause zero layout calls and zero geometry mutations. The same DOM nodes, labels, rows and cues remain present; no zoom visibility thresholds were introduced.
- Navigation remains 220 ms, with synchronous reduced-motion behavior. No browser errors occurred.

The single browser review used 1440×900 Dark only. No historical matrix, migration suite, full repository regression or additional theme/viewport review was run.

## Performance

One local run, not a benchmark: model parse 9.5 ms; layout 82.5 ms (including 13.8 ms tray packing); initial SVG render 123.7 ms; application initialization 287.1 ms. Browser navigation-to-ready measurement was 392.2 ms. Fit All CPU samples were 46.2 and 22.1 ms; Fit subtree 10.4–54.7 ms; Topic Focus 9.1–42.5 ms. These operation timings are separate from the existing 220 ms camera animation and include a synchronous reduced-motion sample. No virtualization or performance-specific rendering change was introduced.

## Visual review and screenshots

The before/after comparison shows a layered forest instead of a narrow horizontal strip. The five aligned root cards retain their existing silhouettes; Computer science extends deeper than the smaller real domains. Terminal trays remain small at orientation scale, but their individual cues and local ownership remain visible. Computer science and Programming languages retain complete-subtree orientation behavior; Formatted output focuses its real row at a readable 16-pixel effective font. The Inspector and V6.6 surfaces are unchanged.

Exactly these five review captures were produced:

1. [GLOBAL-FIT-ALL-BEFORE.png](tests/vertical-composition/review/GLOBAL-FIT-ALL-BEFORE.png)
2. [GLOBAL-FIT-ALL-AFTER.png](tests/vertical-composition/review/GLOBAL-FIT-ALL-AFTER.png)
3. [COMPUTER-SCIENCE-FIT-AFTER.png](tests/vertical-composition/review/COMPUTER-SCIENCE-FIT-AFTER.png)
4. [PROGRAMMING-LANGUAGES-FIT-AFTER.png](tests/vertical-composition/review/PROGRAMMING-LANGUAGES-FIT-AFTER.png)
5. [TOPIC-FOCUS-AFTER.png](tests/vertical-composition/review/TOPIC-FOCUS-AFTER.png)

Limitations remain the accepted orientation contract: most deep Category text and Topic titles are micro-text at Fit All. Strict depth alignment intentionally leaves space under shallower subtrees, and longer vertical drops are visible in branch fits. Reading happens through child-subtree fit or Topic Focus. Relation overlays remain disabled as before. This recommendation reflects this implementation review, not a claim of separate human sign-off.

## Protected files and reproduction

The complete protected inventory and all **427 SHA-256 hashes** match the pre-prototype baseline. Original V6.6 is byte-identical. Production documentation/runtime, State, Knowledge and shared runtime sources remain unchanged. The read-only catalog projection check passes. Evidence: [integrity-results.json](tests/vertical-composition/integrity-results.json) and `tests/protected-before.json` / `tests/protected-after.json`.

The runtime before/after manifests confirm that only `layout.js` changed in this pass. All writes are confined to `prototypes/knowledge-atlas-v6-global/`. No commit, push or deployment was performed.

From the repository root, start locally:

```sh
python3 -m http.server 8777 --bind 127.0.0.1 --directory prototypes/knowledge-atlas-v6-global
```

Local URL: <http://127.0.0.1:8777/>

Focused check command used in this environment:

```sh
PLAYWRIGHT_MODULE=/tmp/adaptive-progress-browser/node_modules/playwright CHROMIUM_EXECUTABLE='/Users/antonplatonov/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing' node prototypes/knowledge-atlas-v6-global/tests/focused.cjs
python3 -B prototypes/knowledge-atlas-v6-global/tests/integrity.py
```

## Recommendation

**C — V6.6 GLOBAL COMPOSITION ACCEPTED**

Stop at this prototype. No My Skill Tree, Course or Project work is included.
