# Global Atlas from V6.6 — focused prototype validation

**B — V6.6 GLOBAL NEEDS ONE FOCUSED LAYOUT ITERATION**

The complete current Catalog is rendered in the V6.6 interface. Data integrity,
fixed geometry, navigation and the focused spatial invariants pass. The five
roots have distinct sibling regions, and Topic/reference focus preserves the
recognizable V6.6 card-and-tray appearance. The full and large-branch landscapes
remain visually dominated by long connector lanes and very small tray silhouettes.
This is a functional design prototype, not a claim that global composition has
passed human acceptance. A subsequent focused iteration should improve the
balance of depth spacing and card/tray silhouettes within this same V6.6 design.
That iteration has not been built here.

## Baseline and reuse

Read before editing: V6.6 `index.html`, `style.css`, `app.js`, `layout.js`,
`routing.js`, `model.js`, `taxonomy-relations.js`, `VALIDATION.md`,
`ARCHITECTURE.md` and `RELATIONS-VALIDATION.md`. Visually inspected the V6.6
1440 dark overview, Java and For loop review images.

- `index.html`: copied header/search/canvas/control/Inspector structure. Removed
  My Knowledge/Course Roadmap buttons; Global Atlas is the sole primary view.
- `style.css`: copied the complete dark/light palette, typography, cards, tray
  surfaces, selection, markers, Inspector, controls and minimap styling. Extended
  existing category selectors to presentation context, and topic-row selectors
  to reference rows. The original overview guide now has five columns.
- `app.js`: derived the SVG renderer, camera calculations, 220 ms transitions,
  reduced-motion handling, overview guide, minimap, search keyboard handling,
  Category selection and Topic focus directly from V6.6. Replaced course/project
  Inspector content with real global structural and resolution information.
- `layout.js`: retained measured title wrapping, card metrics, ordered single-column
  tray packing, bottom-up disjoint subtree composition, depth-band alignment,
  ports and bounds calculation. Added global geometry as described below.
- `routing.js`, `taxonomy-relations.js`, D3 and its license: byte-identical copies.
  Relation overlays are explicitly disabled; `taxonomy-relations.js` is not
  loaded. No semantic relation is manufactured for unresolved references.
- `model.js`: new adapter for the existing validated composed Catalog. `build.py`
  calls `Catalog(load_source(...))` read-only; it performs no data acquisition.

No Course-8 coordinate checkpoint or later strict-global geometry is read.
No Production renderer or adaptive styling is used as a visual source.
See [BASELINE.md](BASELINE.md).

## Current global content

Counts below are derived from current repository data, independently compared
against `data/knowledge/observations/global-knowledge-map-2026-10-04.json`.

| Content | Count |
| --- | ---: |
| Real roots | 5 |
| Category identities/cards | 849 |
| Distinct structural leaf slots/rows | 3,106 |
| Resolved Topics | 1 |
| Partial Topics | 88 |
| Unresolved references | 3,017 |
| Real entities/structural references | 3,955 |
| Presentation-only Atlas context | 1 |
| Total scene entries | 3,956 |
| Source hierarchy pairs | 3,952 |
| Category hierarchy pairs | 844 |
| Leaf memberships | 3,108 |
| Physical trays | 725 |
| Physical category/context branches | 849 |
| Deduplicated hierarchy SVG segments | 2,643 |
| SVG elements, main scene plus exact-geometry minimap | 31,422 |
| Accepted learned / verified overlay | 31 / 12 |

Every Category and every distinct leaf identity is present once. Leaf IDs 36
and 1425 each have two real memberships, explaining the difference between
3,108 memberships and 3,106 physical rows. All memberships remain available in
the Inspector. The accepted canonical parent owns a Topic's row; a reference
without canonical Topic metadata uses its lowest-ID real parent as an explicitly
presentation-only owner. Additional-membership Categories link to the same row.
Subtree fitting includes secondary-member rows at their existing positions,
even if that makes its complete fit geographically wider.

Unresolved records remain `reference:<id>`, with no `topic:<id>` entity, invented
title, URL, theory metadata or progress. `ID 333` is a display label, not a Topic
title. Its Inspector explicitly says **Unresolved reference** and exposes its
numeric identity, real memberships and catalog provenance. Partial Topics retain
their capture resolution alongside any accepted metadata for the same ID. The
one resolved Topic is **Formatted output**, ID 518. Personal progress only styles
matching accepted Topic identities; it does not affect ownership, order, geometry
or visibility. Existing evidence details remain in the V6.6 Inspector style.

## Global layout and five-root composition

One deterministic rectangular hierarchy is computed at startup, independent of
the viewport and progress. There is no persisted global layout checkpoint.

1. Build a presentation-only `atlas:root`, excluded from the semantic registry,
   above the five real roots. Catalog inventory order is canonical numeric ID
   order: **Math, Computer science, Natural science, Product development,
   Generative AI**. This is why Math precedes Computer science spatially.
2. Measure Category text with the V6.6 system-font measurements and Topic/reference
   rows with its 14 px row policy. Keep every row in an ordered one-column tray.
3. Measure disjoint subtrees bottom-up. Category children occupy separate lateral
   regions; direct leaf trays retain the V6.6 reserved region/port treatment.
   Sibling Categories and tray rows each follow canonical numeric ID order;
   the historical Java-specific display reorder is removed.
4. Reserve a common vertical band at every taxonomy depth, including room for
   the maximum card and tray at that depth. A global breadth-derived band gap
   replaces course-scale gaps. In this snapshot the base gap is 22,944 world
   units: 32 times the 717 Categories at unscaled depths. It is fixed at build,
   not recalculated with zoom. This conservative gap is the main remaining
   composition weakness: hierarchy levels are clear, but the long routes
   dominate the large-branch views.
5. Use fixed natural card scales of 64, 64, 16, 4 for presentation depths 0–3;
   deeper cards and all rows retain their original natural sizing. These are
   globally measured card/font dimensions, not screen-size clamps or semantic
   zoom. Upper-level silhouettes otherwise disappeared at the measured global
   scale. Fonts, surfaces and proportions remain the V6.6 language.
6. Reserve each root region at least 18% of the largest root's natural width,
   with inter-root gaps of 2% of that width (4,491.44 units here). Center the
   root cards over their allocations. Smaller roots have usable regional
   separation without receiving invented descendants or equalizing real content.
7. Reuse V6.6 bottom-center/top-center ports and shared orthogonal routing.
   The minimap uses these exact same Category, tray and connector coordinates.

| Root | Distinct physical leaves | Allocated region width |
| --- | ---: | ---: |
| Math | 213 | 40,422.96 |
| Computer science | 2,686 | 224,572.00 |
| Natural science | 94 | 40,422.96 |
| Product development | 55 | 40,422.96 |
| Generative AI | 58 | 40,422.96 |

The minimum smaller-root region spans approximately 115 screen pixels at the
review Fit All scale. Computer science remains substantially larger. Readable
root names are supplied by the retained V6.6 overview navigation guide; native
on-canvas root labels are still micro-text.

Global content bounds, including tray frames and V6.6 padding:
`x = [-201287.32, 191511.32]`, `y = [-8, 192961.84]`.
Total: **392,798.64 × 192,969.84 world units**.
Fit All at 1440×900: scale **0.0028382836** (0.284%). Individual Topic text is
about 0.04 screen pixels there; it is not presented as readable text at Fit All.

## Navigation, completeness and focused checks

All knowledge remains rendered. There is no scope filtering, manual collapse,
learned-only filter, virtualization, per-row visibility threshold or staggered
reveal. Original folding controls were omitted because they conflict with the
stronger complete-global-scene contract. Selection is not a collapse action.

Category click selects without moving the camera. Fit selected subtree includes
the entire selected global subtree, including secondary memberships. Large
subtrees remain honest orientation views. Topic/reference click or keyboard
Enter/Space centers its real row. The tested resolved, partial and unresolved
focus paths retain the same geometry. Search covers every Category, Topic title
and numeric reference ID; exact numeric matches rank first. Search creates no
nodes and never relayouts. Enter, ArrowDown and Escape search behavior is reused.

Programmatic camera navigation uses the original **220 ms** transition. Reduced
motion uses a synchronous transform. Zoom changes only the camera, status,
existing marker optics and minimap. No zoom code hides labels or rows. Selection
now restyles existing DOM nodes instead of reconstructing the scene, following
the measured performance failure described below.

**30 focused browser checks pass**, at one viewport, Dark primary. They cover:

- Five roots; exact source Category and leaf identity inventories, each once;
  separate unresolved identities with no invented metadata.
- **0 card overlaps**, **0 adjacent sibling-subtree overlaps**, **0 unrelated
  tray/card overlaps**, **0 connector/card-or-tray interior intersections**,
  **0 invalid branch/tray endpoints**, **0 canonical-order violations**.
- One coherent y-band per taxonomy depth; all global bounds fit at Fit All;
  complete Computer science and Programming languages subtree fits.
- Category selection preserves camera; resolved/partial/reference search and
  keyboard focus; multiple memberships retain one physical row.
- Every label remains rendered through zoom, search, selection and theme changes;
  the identical SVG row DOM nodes survive navigation.
- **0 layout calls after initialization**; unchanged node coordinates, dimensions,
  label lines, tray geometry and routed segment geometry throughout navigation.
- Reduced-motion synchronous focus and no browser errors.

This is not a full historical viewport, migration, light-theme or mobile matrix.
The Light toggle remains available and was only smoke-tested for stable geometry.
No physical-device or human screen-reader audit is claimed.

## Performance

Local macOS headless Chromium, 1440×900. These are one-run measurements, not a
device-independent frame-rate guarantee. CPU/dispatch values exclude asynchronous
camera animation except the explicitly marked end-to-end samples.

| Measurement | Time |
| --- | ---: |
| Offline Catalog projection/build | 1,685.2 ms |
| Browser model parse/adapter | 9.3 ms |
| Complete layout/routing | 82.1 ms |
| Tray packing, included in layout | 14.6 ms |
| Initial full SVG render | 124.8 ms |
| App initialization, fetch through initial fit | 287.8 ms |
| Browser navigation through ready test hook | 400.6 ms |
| Fit All dispatch | 25.8–43.9 ms |
| Fit subtree dispatch | 10.5–49.9 ms |
| Topic/reference focus dispatch | 9.0–45.1 ms |
| Search lookup | 0.4–0.7 ms |
| Search navigation dispatch | 26.8–34.9 ms |
| Resolved search through animation completion | 315.3 ms |
| Reference search through animation completion | 296.6 ms |

The first honest copied renderer measured **112–181 ms** synchronous selection
work, because V6.6 rebuilt all SVG nodes for each selection. This was an actual
main-thread pause at global scale. The sole rendering optimization changes
selection to update existing classes/ARIA/Inspector state. It preserves every
node, label and pixel geometry. Normal selection dispatch became 18–35 ms;
the reduced-motion case including synchronous focus measured 73.5 ms. No
knowledge is culled. Before/after measurements are retained in
`tests/performance-before-selection-reuse.json` and `tests/results.json`.

## 1440×900 Dark review screenshots

All five final screenshots were captured and visually inspected:

1. [Global Fit All](tests/review/01-global-fit-all.png)
2. [Computer science subtree](tests/review/02-computer-science.png)
3. [Programming languages subtree](tests/review/03-programming-languages.png)
4. [Resolved Topic focus — Formatted output](tests/review/04-resolved-topic.png)
5. [Unresolved reference focus — ID 333](tests/review/05-unresolved-reference.png)

Topic/reference focus unmistakably retains V6.6 cards, ordered tray rows,
selection, markers, Inspector and quiet palette. Five root regions and hierarchy
depths can be distinguished in orientation. Nevertheless, deep Category/tray
silhouettes are too small relative to connector lengths in global/large-branch
fits. Search and Inspector navigation work naturally; unaided visual scanning
across large branches remains the reason for the recommendation at the top.

## Local use and reproduction

Exact local start command, from any working directory:

```sh
python3 -B -m http.server 8777 --bind 127.0.0.1 --directory /Users/antonplatonov/IdeaProjects/hyperskill-projects/prototypes/knowledge-atlas-v6-global
```

Local URL: **http://127.0.0.1:8777/**

The generated current `model.json` is included; serving requires no build,
package installation or external network. To refresh it from the same repository
Catalog, run from the repository root:

```sh
python3 -B prototypes/knowledge-atlas-v6-global/build.py
python3 -B prototypes/knowledge-atlas-v6-global/tests/integrity.py
```

Exact browser validation command used on this Mac, with the server running:

```sh
PLAYWRIGHT_MODULE=/tmp/adaptive-progress-browser/node_modules/playwright \
CHROMIUM_EXECUTABLE='/Users/antonplatonov/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing' \
node prototypes/knowledge-atlas-v6-global/tests/focused.cjs
```

Both test dependency paths are local environment overrides; neither is required
by the prototype runtime. Browser results, counts, performance and geometry
checks are in `tests/results.json`; the independent Catalog freshness and
protected-inventory check is in `tests/integrity-results.json`.

## Preservation and scope

SHA-256 before/after manifests cover **427 files** across the complete original
`prototypes/knowledge-atlas-v6/`, all `docs/` (including real adopted
`docs/knowledge-map/` Production), `state/knowledge-atlas/`, `data/knowledge/`
and shared `scripts/knowledge_atlas/` sources. Content and file inventories are
unchanged, excluding pre-existing dependency/cache directories. The manifests
and a repeatable read-only integrity check are stored in `tests/`.

**Original V6.6 is byte-identical. Real Production, State and Knowledge are
unchanged.** Existing unrelated untracked files were left untouched. Repository
writes for this task are confined to `prototypes/knowledge-atlas-v6-global/`.
No My Skill Tree, Course/Project redesign, strict-global migration package,
commit, push or deployment was performed.
