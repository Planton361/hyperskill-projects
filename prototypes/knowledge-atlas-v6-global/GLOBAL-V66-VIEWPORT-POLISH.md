# Global V6.6 viewport polish

2026-10-07. One application-chrome/orientation pass on the accepted Global Atlas. Review: 1440 × 900 CSS px, Dark, DPR2. No graph-layout or optical-design iteration.

The default Inspector now collapses to an edge button. Selecting an entity opens the original Inspector as a 250-px right overlay. Close and Escape expose the map immediately; Pin restores the optional side-by-side arrangement. Inspector content is unchanged, including evidence and unresolved-reference information. Fit All closes an unpinned Inspector; a pinned Inspector remains open.

Fits use the unobstructed map rectangle, excluding controls, navigation, footer and an open overlay. When a retained fit is active, opening/closing or pinning refits the camera to that rectangle. After free navigation, opening the Inspector only translates the camera when needed to keep the selected card visible, preserving its scale. Graph geometry and scene compilation remain untouched.

| 1440 × 900 | Before, permanent Inspector | After, closed | After, overlay | After, pinned |
| --- | ---: | ---: | ---: | ---: |
| Canvas width × height | 1190 × 765 | 1440 × 787 | 1440 × 787 | 1190 × 787 |
| Unobstructed Overview fit rectangle | 1142 × 547.70 | 1392 × 611.20 | 1142 × 611.20 | 1142 × 611.20 |
| Fit All scale | 0.03719521 | 0.04533777 | 0.03719521 | 0.03719521 |
| Map screen bounds, x / y / width / height | 24 / 379.42 / 1142 / 367.46 | 24 / 329.45 / 1392 / 447.90 | 24 / 369.67 / 1142 / 367.46 | 24 / 369.67 / 1142 / 367.46 |

Closed Inspector: **250 px extra width, 22 px extra height, 24.49% more canvas area and 21.89% greater Fit All scale**. The header retains its original 113-px height and design. Controls/status share one row; the five-root guide retains its readable labels and three existing major-branch links. Reduced guide spacing releases another 41.50 px above the map. Combined usable Overview height increases by 63.50 px. The minimap shifts left of an unpinned drawer and retains its existing semantics.

Overview Category selection adds restrained V6.6 accent strokes along the canonical ancestor path, selected boundary and direct child structure. A pointer-transparent UI overlay references the exact existing connector segments and card bounds; each highlighted segment occurs once. Programming languages highlights 30 existing segments, its canonical ancestors and eight direct child Categories. Unrelated entities remain fully rendered with their accepted optics. Clearing selection removes the highlights. Subtree and Topic states never show this overlay; zoom changes only the camera. Root-region backgrounds were skipped because the existing five root labels provide orientation without extra surfaces competing with the accepted map.

Review captures (all native 1440 × 900, Dark; exported at DPR2):

1. [Global Fit All — before](tests/viewport-polish/before/global.png)
2. [Global Fit All — Inspector collapsed](tests/viewport-polish/after/global.png)
3. [Global Fit All — Computer science selected, Inspector overlay](tests/viewport-polish/after/selected-branch.png)
4. [Programming languages selected](tests/viewport-polish/after/programming-languages.png)
5. [Topic Focus — Formatted output](tests/viewport-polish/after/topic.png)

Additional comparisons: [pinned Inspector](tests/viewport-polish/after/pinned.png), [Natural science](tests/viewport-polish/after/natural.png), [Bioinformatics](tests/viewport-polish/after/bio.png). Reading-state scales remain 0.27261876, 0.53227686 and 1.14285714 respectively. Native camera centering changes by −0.5 px vertically. At an identical camera and canvas, each shared reading-map comparison checks 2,380,000 physical pixels with **zero differences**. Equal canvas dimensions isolate styling from viewport clipping and antialiasing.

One short native Safari 27.0.1 DPR2 navigation comparison: Overview and dense Programming languages subtree both retain **17 ms median / p95 frame intervals**, with zero frames above 50 ms. Overview render-JS p95 is 4 → 5 ms; dense subtree remains 3 → 3 ms. No layout rebuild, scene replacement or cache-cap overflow occurred. [Safari measurements](tests/viewport-polish/safari.json).

**38 focused checks passed.** Full geometry hash is unchanged:

`b38b9c7a692c27be27db7e4500b1a5b3abec85eac2ab0bf0c07852f0f8f1a6d9`

849 Categories, 3,106 leaf slots, labels, routing paths, tile commands/styles, 31 learned IDs, 12 verified IDs, progress anchors and collision metadata are identical. Every tile level retains the complete entity inventory. Pan/zoom preserves the same scene and layout, with no content-visibility thresholds. The tiled renderer, worker, paint code, accepted optics CSS, local geometry, original V6.6, My Skill Tree, Production, State and Knowledge remain byte-identical across the 474-file preservation manifest. Only application behavior/markup and the new chrome stylesheet changed; test evidence and this report stay inside the existing Global prototype. [Checks and measurements](tests/viewport-polish/checks.json), [preservation manifest](tests/viewport-polish/protected-before.json).

The overlay necessarily reduces unobstructed fit width while open; pinning deliberately retains the previous width reservation. Closing it restores the larger fit area. Verification is focused on the requested desktop Dark viewport and Safari DPR2; no broad regression or further graph/performance iteration was performed. No commit, push or deployment.

C — GLOBAL V6.6 COMPLETE
