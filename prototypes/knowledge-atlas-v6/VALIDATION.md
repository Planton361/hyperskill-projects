# Knowledge Atlas V6.6 — Viewport / Focus + Context

Viewport and interaction validation passes with documented full-subtree reading limits. The former **Fit-All Topic font ≥10 CSS px** acceptance is **obsolete**. **Fit-All is an orientation view.** All 89 Topics and 46 Categories remain rendered with every label; zoom never hides knowledge.

## Geometry Preservation

V6.5 geometry is frozen. SHA-256 checks confirm byte identity of `layout.js`, `routing.js`, `model.js`, `model.json`, `layout-checkpoint.json` and its schema. A browser comparison against the frozen V6.5 app confirms all 135 node positions and dimensions are identical. Navigation does not repack, recompute layout or write checkpoints. Natural content bounds remain **8916 × 1867.14 px**. The spatial suite retains 0 semantic overlaps, 0 hierarchy crossings, 0 safe-area violations and exact card/tray ports, including all three growth fixtures. Source integrity still confirms **89 / 46 / 31 / 12**, 26 Project 113 requirements, 12 Stage 4 requirements, and no project_applies.

## Overview View

Fit All keeps the entire taxonomy and connected structure visible. Stronger non-scaling hierarchy/card/tray strokes and bounded topic status markers make group silhouettes and state patterns easier to distinguish. Topic text retains the natural 14 px font and becomes micro-text through zoom. Native complete-title tooltips remain. Knowledge cross-links are hidden in Overview, including after returning from a selected Topic.

A quiet overview guide spells out Computer science, the three major branches, Java and its main subcategories. Its region buttons navigate into real category subtrees. This guide is separate navigation context; original Card labels, bounds and connector ports remain unchanged.

## Fit-All Scale

| Width | Fit-All scale | Topic font | Root Card font | Major Card font | Category Card font |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1920 | 0.181920 | 2.5469 px | 5.0938 px | 3.8203 px | 3.0926 px |
| 1440 | 0.128084 | 1.7932 px | 3.5864 px | 2.6898 px | 2.1774 px |
| 1280 | 0.110139 | 1.5419 px | 3.0839 px | 2.3129 px | 1.8724 px |
| 1200 | 0.129206 | 1.8089 px | 3.6178 px | 2.7133 px | 2.1965 px |
| 1024 | 0.109466 | 1.5325 px | 3.0651 px | 2.2988 px | 1.8609 px |
| 768 | 0.080754 | 1.1306 px | 2.2611 px | 1.6958 px | 1.3728 px |
| 430 | 0.042844 | 0.5998 px | 1.1996 px | 0.8997 px | 0.7284 px |
| 390 | 0.038358 | 0.5370 px | 1.0740 px | 0.8055 px | 0.6521 px |
| 320 | 0.030507 | 0.4271 px | 0.8542 px | 0.6406 px | 0.5186 px |

Full bounds fit at every tested width/theme. At 1920, scale is approximately 18.19%, versus V6.5 approximately 18.39%; extra viewport allowance reserves navigation/context controls. Geometry is identical.

## Major-Level Readability

Native Root/Major/Card labels remain small in the full map. They were not enlarged beyond their Card boundaries: minimum screen fonts would risk detaching text from cards or colliding with the tree. Instead the overview guide uses readable **14 px Root / 12 px Major** context text on desktop, **12 / 10 px** on mobile. Java and its main children appear in an 11 px context line. This does not claim every native Category Card label is comfortably readable in Overview.

## Subtree Reading View

Desktop Fit selected subtree captures the full visible subtree, including Tray frames, with 24 px side margins and additional control/footer clearance. Its zoom is capped at a 13 px Topic font where a complete fit allows that. When a wide subtree is below 10 px, status explicitly says “Subtree overview · choose a child to read”; the Inspector provides readable child navigation and a Focus subtree action. No auto-collapse/filter policy is added.

Mobile (≤700 px) uses the authorized local window when the full subtree cannot meet 10 px: one descendant Category/Tray group is centered at **13 px** Topic text. Its category and all rows fit without clipping. Remaining subtree content stays rendered outside the viewport and can be reached by pan. The selected Category and its full breadcrumb remain in the Inspector.

## Java Fit

A complete Java fit is physically too wide for desktop reading: **3.99 px at 1920**, decreasing at smaller widths. The desktop full-subtree contract is preserved; no cropped desktop Java fit is misreported as a readable complete subtree. Use child navigation or Topic Search for reading. Mobile Java Fit shows a readable local Java region at 13 px while retaining the full landscape.

## Basics Fit

At 1920, complete Basics Fit achieves **11.63 px** Topic text. At smaller desktop widths it falls below 10 px: the full region contains six child categories and 29 Topics. Child subtree focus and search remain readable. Mobile uses the 13 px local window.

## Topic Focus View

Topic click, keyboard Enter/Space and Topic Search center the complete Topic row in the usable map area at **16 px** for For loop at all nine widths. The Inspector stays visible on desktop and appears below the map on mobile. Only real direct prerequisite/dependent links render, using the unchanged mint lane router. Returning to Fit All hides these links.

## Search Navigation

For loop Search finds the true Topic, opens only its manually collapsed ancestor path, selects it, centers it, enters Topic Focus, updates the Inspector and shows direct Knowledge Relations. Category Search (Java, Basics, Dev tools and other real Categories) selects and fits the subtree. No mode switch. The existing live region announces reading navigation.

Category single click is selection only and preserves the viewport. Topic single click navigates to reading focus. Chevron remains the independent manual Expand/Collapse control. Category double click is not implemented; the explicit Inspector Focus subtree button provides quick focus without ambiguous gestures. Inspector child buttons navigate to their subtrees.

## Project Coverage Overview

Project selection preserves the current viewport and enables the same exact coverage semantics: **26** Required Topics for Project 113, **12** for Stage 4. Amber highlights the existing shared hierarchy paths and required rows; unrelated branches remain visible and dimmed. Show/Hide coverage changes styling only. Topic click within coverage enters Topic Focus without disabling or changing the requirement set.

## Project Coverage Fit

Fit project coverage is a separate navigation action. It fits visible evidence representatives plus the complete relevant Topic Trays and their parent Cards, with viewport margins. It does not alter the 26 required-topic set or expand nodes. A manually collapsed Category remains a representative. All target bounds fit at every tested width. Because requirements span several distant regions, coverage fit is also an orientation view; no 10 px text promise is made.

## Minimap

Small, passive, desktop-only context map in the lower right: full taxonomy/tray geography, a clipped viewport rectangle, selected topic/subtree outline, and exact amber evidence regions. The mini tray silhouette is a generic group/density cue; individual learned/verified/not-learned states remain in the main map. The minimap is aria-hidden, non-focusable and has no pointer interaction. It is hidden at ≤700 px. No structural layout calculations run during its viewport updates.

## Zoom Controls

Fit all, Fit selected subtree, −, zoom percentage and + remain compact and always available inside the map. The view status distinguishes orientation, subtree reading and topic focus. Fit All is the return-to-overview action. Inspector Focus subtree and Fit project coverage are contextual actions. No additional Back stack is added.

## Viewport Transitions

Navigation uses **220 ms** D3 viewport transitions. Reduced Motion uses synchronous transforms. A new navigation interrupts the previous transition reliably; interrupted promises are handled. User pan/pinch and +/- preserve geography and change only the viewport/optical emphasis.

## Desktop

1920×1080 and 1440/1280/1200/1024/768×900 were tested in Dark and Light for Fit All, Java Fit, Basics Fit, For loop Focus and Project Fit. Inspector is right of the map above 1200 px, below it at 1200 and less. Fit calculations use the actual map dimensions and reserved UI space. Mode/theme switching retains viewport and selection and performs no layout recomputation. Full-fit target bounds have zero clipping; surrounding unrelated map regions may naturally be outside a focused viewport.

| Width | Java Topic px | Basics Topic px | Topic Focus px | Project fit scale | Project Topic px |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1920 | 3.9895 | 11.6332 | 16.0000 | 0.199754 | 2.7966 |
| 1440 | 2.8089 | 8.1906 | 16.0000 | 0.140640 | 1.9690 |
| 1280 | 2.4153 | 7.0430 | 16.0000 | 0.120936 | 1.6931 |
| 1200 | 2.8335 | 8.2623 | 16.0000 | 0.141872 | 1.9862 |
| 1024 | 2.4006 | 7.0000 | 16.0000 | 0.120197 | 1.6828 |
| 768 | 1.7709 | 5.1639 | 16.0000 | 0.088670 | 1.2414 |
| 430 | 13.0000 | 13.0000 | 16.0000 | 0.047044 | 0.6586 |
| 390 | 13.0000 | 13.0000 | 16.0000 | 0.042118 | 0.5897 |
| 320 | 13.0000 | 13.0000 | 16.0000 | 0.033498 | 0.4690 |

Mobile Java/Basics numbers describe the local reading window, not a complete subtree fit. Full per-view Root/Major/Category/Topic fonts, zoom scales, target counts and screen bounds are in `tests/viewport-results.json` (90 entries).

## Mobile

430/390/320×844 tested in both themes. Full landscape remains rendered. Fit All is orientation only; Java/Basics focus uses a readable local Category/Tray group. For loop Search focuses the entire row at 16 px with no page horizontal overflow. Inspector is below the map. Touch pinch/pan work, and controls do not depend on hover. Manual collapse/search reveal semantics remain. Mobile local-window clipping of the rest of the subtree is intentional and is recorded separately from the complete local reading group, which has zero clipping.

## Accessibility

Viewport buttons retain accessible names. Zoom percentage is a polite, atomic status. Search uses the existing live region; Inspector retains the full canonical breadcrumb and true semantic Topic/Category IDs. Topic keyboard activation enters Reading View. Chevron keyboard behavior remains independent. Reduced Motion is verified instant. Minimap is hidden from assistive technology. Tests are automated Chromium checks, not a human screen-reader audit.

## Performance

No layout recomputation during zoom/navigation. Measured dispatch/CPU durations across the matrix:

| Action | Range, latest per-width samples |
| --- | ---: |
| Fit all | 4.30–5.80 ms |
| Fit subtree | 2.50–3.40 ms |
| Topic focus | 0.30–0.50 ms |
| Project fit | 0.70–0.90 ms |
| Search navigation | 8.60–9.80 ms |

End-to-end animated For loop Search navigation, including Playwright input/wait: **235–262 ms**, with the 220 ms transition. CPU samples exclude asynchronous animation duration. These are local-machine samples, not a device-independent frame-rate guarantee. All 89 Topic selections / 137 Knowledge Relations also pass.

## Remaining Risks

- Complete desktop Java Fit misses the reading-font target at every tested width. Complete Basics Fit misses it below 1920. Keeping frozen geometry and fitting the entire region makes these limits unavoidable; navigate into children for reading.
- Native Root/Major/Card labels remain small in Overview; the separate guide supplies readable orientation context.
- Mobile subtree focus intentionally shows a local window. The selected parent can be outside that window; Inspector breadcrumbs preserve context.
- Dense overview row borders/markers are optical distribution cues, not comfortable topic-level reading. Browser/system-font and assistive-technology differences still warrant user review.

## V6.5 vs V6.6 Recommendation

Keep V6.6 as the viewport/navigation improvement over the frozen V6.5 geometry. It makes the landscape/reading distinction explicit, adds reliable Topic/Search focus, responsive subtree navigation, context guidance, minimap and exact project-region fit. It does **not** achieve a readable complete Java desktop subtree, or complete Basics reading at every desktop width. Those limits are reported rather than resolved by squeezing geometry, hiding labels or violating desktop full-subtree fitting.

Automated checks: **339 viewport checks / 90 views**, **18 focused interaction checks**, geometry/growth, source integrity, unchanged SHA-256 manifest, updated readability acceptance, and all 89 Topic selections. No commit, push or deployment. Work is confined to this prototype.

## Review Artifacts

- [1920-dark-overview.png](tests/review/v6.6/1920-dark-overview.png)
- [1920-dark-java.png](tests/review/v6.6/1920-dark-java.png)
- [1920-dark-basics.png](tests/review/v6.6/1920-dark-basics.png)
- [1920-dark-for-loop.png](tests/review/v6.6/1920-dark-for-loop.png)
- [1920-dark-project-overview.png](tests/review/v6.6/1920-dark-project-overview.png)
- [1920-dark-project-fit.png](tests/review/v6.6/1920-dark-project-fit.png)
- [1440-light-overview.png](tests/review/v6.6/1440-light-overview.png)
- [390-dark-overview.png](tests/review/v6.6/390-dark-overview.png)
- [390-dark-java.png](tests/review/v6.6/390-dark-java.png)
- [390-dark-for-loop.png](tests/review/v6.6/390-dark-for-loop.png)
- [320-dark-for-loop.png](tests/review/v6.6/320-dark-for-loop.png)

More screenshots for each viewport/state are under `tests/review/v6.6/`. Frozen V6.5 app/styles/index and reports are under `tests/review/v6.5/frozen/`.
