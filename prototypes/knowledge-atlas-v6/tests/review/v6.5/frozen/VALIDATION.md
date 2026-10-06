# Knowledge Atlas V6.5 — Validation

Geometry and functional checks pass. The preferred 1920 Fit-All readability target is **not met**. This is not full visual/readability acceptance.

## Content and behavior

Source integrity confirms all eight model tables and hashes unchanged: **89 / 46 / 31 / 12**. All 89 Topics and 46 Categories, with complete labels, are rendered and fit at all nine widths in both themes. Project 113 highlights exactly 26 Topics; Stage 4 exactly 12. Mode/project changes have zero coordinate, checkpoint, layout-timing or expansion-state change. The functional browser suite passes 43 checks, including search, disclosures, accessibility targets, camera stability, mobile pan/pinch and project controls. Exhaustive selections: all 89 Topics / 137 Knowledge Relations, zero failures.

## Spatial measurements

Natural content bounds including fit padding: **8916.00 × 1867.14 px**.

| Measurement | Baseline |
| --- | ---: |
| Semantic block overlaps | 0 |
| Hierarchy crossings | 0 |
| Connector/card/tray interior intersections | 0 |
| Foreign safe-area violations | 0 |
| Minimum horizontal card gap (overlapping Y intervals) | 128.50 px |
| Minimum horizontal tray gap (overlapping Y intervals) | 104.00 px |
| Minimum foreign connector/block clearance | 48.00 px |
| Boundary ports / region gutters / vertical spacing | Pass |

Tests include full Topic Row bounds against foreign trays/categories. Source/target safe-area exceptions are restricted to their incident segments; interior intersection tests still include every block. Region-gutter checks use allocated subtree bounds, not approximate topic counts. All trays have verified top-center ports. Shared intervals are rendered once.

## Desktop and mobile

| Width | Dark / Light fit scale | Effective Topic font |
| --- | ---: | ---: |
| 1920 | 0.183939 | 2.5751 CSS px |
| 1440 | 0.130103 | 1.8214 CSS px |
| 1280 | 0.112158 | 1.5702 CSS px |
| 1200 | 0.131225 | 1.8371 CSS px |
| 1024 | 0.111485 | 1.5608 CSS px |
| 768 | 0.082773 | 1.1588 CSS px |
| 430 | 0.044863 | 0.6281 CSS px |
| 390 | 0.040377 | 0.5653 CSS px |
| 320 | 0.032526 | 0.4554 CSS px |

Height is 1080 at 1920, 900 for other desktop widths, 844 on mobile. Dark/light geometry and metrics are identical. The natural 14 px Topic font remains unchanged. At 1920, the 10 px preference is missed substantially; it must not be described as a slight reduction. Fit All is an orientation view. The wide disjoint regions and aligned sibling rows have a substantial readability cost. Exterior fit padding is only 8 natural px; removing it cannot recover the target. No required gaps were reduced to force a fit.

Baseline Depth Bands and sibling Tray Baselines align. Growth retains existing bands, allowing local exceptions for new taller content. Negative space above and below the overview is visible because width limits fit. The desktop Java/Basics zoom is legible; the mobile zoom focuses one Java/Basics child region with readable rows. Neither zoom screenshot claims all Java descendants are simultaneously readable.

## Growth

| Fixture | Added Topics | Overlaps / crossings / safe violations | Existing nodes moved | Natural bounds |
| --- | ---: | --- | ---: | --- |
| basics-growth | 20 | 0 / 0 / 0 | 63 | 9256.00 × 1867.14 |
| advanced-oop | 5 | 0 / 0 / 0 | 5 | 9256.00 × 1867.14 |
| databases | 20 | 0 / 0 / 0 | 0 | 9988.00 × 1867.14 |

All growth checkpoints rebuild identically. Databases adds a local region without moving existing nodes. Advanced OOP and Basics move successors to make room; the right-hand DevOps branch moves because the neighboring Programming languages region expands. Foundations remains fixed. Movements are explicitly listed in `tests/spatial-results.json`; zero major displacement is not claimed.

## Screenshot review

Inspected all six images below: no floating connector fragments, premature card endpoints, unintended crossings, touching cards or merging trays. Shared bus attachment at natural reading zoom is clean. Fit-All labels are fully present but too small for comfortable reading.

- [1920-dark-fit-all.png](tests/review/v6.5/1920-dark-fit-all.png)
- [1920-dark-project-113.png](tests/review/v6.5/1920-dark-project-113.png)
- [1920-dark-java-zoom.png](tests/review/v6.5/1920-dark-java-zoom.png)
- [1440-light-fit-all.png](tests/review/v6.5/1440-light-fit-all.png)
- [390-dark-fit-all.png](tests/review/v6.5/390-dark-fit-all.png)
- [390-dark-java-zoom.png](tests/review/v6.5/390-dark-java-zoom.png)

Machine results: `tests/spatial-results.json`, `tests/results.json`, `tests/relation-results.json`, and the intentionally failing strict preference report `tests/readability-results.json`. No commit, push or deployment. Changes are confined to this prototype.
