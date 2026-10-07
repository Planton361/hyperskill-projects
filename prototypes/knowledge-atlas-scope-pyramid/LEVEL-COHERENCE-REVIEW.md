# Level coherence review

Recommendation: **C — LEVEL-COHERENT SCOPE PYRAMID ACCEPTED**.

This is the technical recommendation from the comparative review below. The new four captures are available for owner review; it does not claim a new human sign-off, and does not change Global's HUMAN_ACCEPTANCE_PENDING status.

## One engine, local bands

`ScopePyramid → ScopeProjection → AtlasLayout.build` remains the single engine for all scope types. Semantic closure, seeds, IDs, titles, canonical owners and requirement/personal layers are unchanged. Layout contains no scope names, semantic IDs or branch names. Geometry stays outside the semantic projection.

Each **used root independently** measures its Category cards and defines card-only depth spacing: maximum Category card height at that local depth + 20 units for the orthogonal bus/drop. Topic trays, subtree heights and other roots never enter that table. First-row Category tops align to these bands. Topic trays remain complete local modules below their owner. They can extend below subsequent card bands; occupied contours keep adjacent content and routing corridors apart. Card bounds remain distinct from subtree bounds.

Local deterministic multi-row arrangements remain available where broad siblings would otherwise create excessive width. These can create a second terrace for the same taxonomy depth: exact depth alignment is a preference, not a hard global constraint. Routing remains the existing short orthogonal bus/spine/drop implementation. Numeric sibling order is preserved within rows and through their ordered sequence; Topic columns retain canonical reading order.

## Packing and bounded scoring

The existing measured-width and 1–4 column tray alternatives remain. Two-module arrangements now also evaluate stacking: a single Category child plus an owning tray no longer has to be placed side by side. No scope-specific tuning or alternate layout implementation was added.

For each candidate collect Category top-Y positions per relative taxonomy depth. Compute mean absolute deviation and maximum deviation, excluding Topic rows. At the presentation root score each used root independently, then average the roots' mean penalties and take their maximum deviation; never mix unrelated roots into a shared depth-height table.

```
score = existing compactness score
      + min(0.8 × compactness, 3 × mean Y deviation + 0.75 × max Y deviation)
```

The compactness terms still account for dimensions/aspect, occupied area, whitespace, connectors, wrapping and imbalance. The bounded term cannot grow without limit. The beam retains two especially coherent alternatives in addition to its aspect-profile winners so a parent can choose a locally wider child that aligns better with neighboring branches. All constants are generic and shared across real and disposable scopes.

Exact alignment was evaluated and rejected as the default: it made Course 8 about 4,796 units wide after the additional packing alternatives, with only 3.9–4.1 projected Topic pixels. The selected compromise aligns the upper hierarchy and preserves two lower terraces. Full Topic text remains available through Topic Focus.

Measured SVG Topic line boxes in the current Chrome overlapped with 17-unit line spacing. Spacing is now 19 units; full titles and browser bounding-box checks pass. Font size remains 14 units.

## 1440 × 900 Dark comparison

Chrome, DPR 2. Same V6.6 renderer, camera region and scope seeds before/after. Before uses the unchanged engine from commit c615427e644006e5eb9b3f28aaf71d72938ffb81, saved outside the repository for comparison.

| View | World W × H | Fit All | Topic px | Mean / max depth Y deviation | Connector span mean / p95 / max | Whitespace | Overlaps after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Course before | 2727.9 × 1386.4 | 0.4934 | 6.91 | 164.48 / 380.66 | 278.5 / 965.2 / 1671.1 | 66.6% | 0 |
| Project before | 1816.5 × 939.8 | 0.7278 | 10.19 | 51.11 / 160.70 | 214.8 / 630.0 / 698.0 | 72.2% | 0 |
| Stage before | 1271.5 × 698.6 | 0.9791 | 13.71 | 13.35 / 51.57 | 105.6 / 357.5 / 357.5 | 68.6% | 0 |
| Course after | 3408.1 × 1435.7 | 0.4084 | 5.72 | 99.59 / 362.78 | 304.5 / 1068.1 / 1829.1 | 72.3% | 0 |
| Project after | 1954.0 × 956.9 | 0.7124 | 9.97 | 0.00 / 0.00 | 202.7 / 678.0 / 768.5 | 75.1% | 0 |
| Stage after | 1409.5 × 724.9 | 0.9436 | 13.21 | 0.00 / 0.00 | 118.0 / 426.5 / 426.5 | 70.2% | 0 |

Depth deviation groups Categories by used physical taxonomy root and local depth, with mean absolute distance from each group's mean top-Y. Singleton groups contribute zero. Connector span is the horizontal extent of Category-to-Category routes. Whitespace is 1 minus (Category-card area + complete tray area) / padded world area; Topic rows inside trays are not counted twice. Before and after review measurements independently recheck Category cards, Topic rows and complete tray rectangles for overlaps; all are zero. Current routing and text checks also come from the focused oracle.

Course 8 improves mean deviation **39.5%**, max deviation **4.7%**, and max same-depth range **17.4%**. The upper Category bands align through depth 3. Most deeper cards occupy one of two clear terraces. Width grows 24.9%, height 3.6%, and Fit All scale falls 17.2%. Whitespace grows about 5.7 percentage points. This is a deliberate overview/order tradeoff, not an area-minimization claim. Fit All is for structural reading; Topic Focus retains readable full-title detail.

Project 113 has 26 requirements / 21 context Categories; Stage 617 has 12 requirements / 16 context Categories. Both use one root and have zero meaningful same-depth Y deviation. Project Fit All Topic text is about 10 px and Stage about 13.2 px. The same engine achieves the stronger structure without a large sparse-scope expansion.

## Exactly four new captures

- [Course 8 before](tests/level-course-before.png)
- [Course 8 after](tests/level-course-after.png)
- [Project 113 after](tests/level-project-after.png)
- [Stage 617 after](tests/level-stage-after.png)

No other new screenshots were captured. Existing historical captures were left unchanged. Camera, search, overlay Inspector, Fit subtree, Topic Focus, progress overlays, exact-ID Show in Global and minimap remain functional. The minimap now occupies the empty upper-right graph area; a projected DOM-bounds check confirms it covers no card or tray in any of the three Fit All views.

## Focused validation

`tests/validate.cjs` passes for real scopes and 1 / 5 / 20 / 100 / 300 Topic disposable fixtures: deterministic geometry and closure, complete titles, no overlap, valid orthogonal routes/endpoints, canonical order, exact semantic identity, preserved progress, browser text bounds and interactions. Screenshot generation in this oracle is now opt-in (`CAPTURE=1`) so validation does not overwrite historical review captures. `tests/generality.cjs` passes after remapping all semantic IDs. `tests/locality.cjs` proves tall trays cannot enter card depth spacing and a tall independent root cannot change another root's Category baselines. Parent scoring may choose a different tray width from retained candidates; that is a local packing choice, not a cross-root band constraint.

| Disposable Topics | Used roots | World W × H | Layout ms | Overlaps | Route collisions |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 239.0 × 670.9 | 1.0 | 0 | 0 |
| 5 | 1 | 664.0 × 657.0 | 1.5 | 0 | 0 |
| 20 | 5 | 2176.5 × 835.4 | 65.2 | 0 | 0 |
| 100 | 5 | 3590.0 × 1950.7 | 590.2 | 0 | 0 |
| 300 | 5 | 6249.0 × 2968.8 | 1628.0 | 0 | 0 |

Run with the existing Playwright installation and Chrome executable via `PLAYWRIGHT_MODULE`, `ATLAS_BROWSER_EXECUTABLE`, and `SCOPE_URL`. `tests/levels.cjs before` additionally requires `BASELINE_LAYOUT` pointing to the frozen old script outside Git, plus `BASELINE_SCOPE_CSS` for its unchanged minimap placement. `CAPTURE=1` on the level review captures only Course before and the three after views. Timings are observations, not deterministic assertions.

## Limits and protection

The beam is a bounded heuristic, not a proof of globally minimal score. Course still needs lower repeated terraces and focused zoom for Topic reading; 100/300 Topic fixtures are structural stress tests, not human readability promises. Same-depth spacing can be influenced by a long **Category card within its own root**, but never by an unrelated tray or another root.

Production, State/history/generation, accepted Knowledge, Global V6.6, V6 and the skill-tree surfaces are byte-inventory checked against the pre-task baseline. No commit, push, deployment or bulk acquisition is part of this milestone.
