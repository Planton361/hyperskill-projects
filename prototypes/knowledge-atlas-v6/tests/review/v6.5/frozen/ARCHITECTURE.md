# Knowledge Atlas V6.5 — Spatial Composition

Isolated static prototype. Run `python3 -m http.server 8776 --bind 127.0.0.1` in this directory. No commit, push or deployment. Figma file `fziWy5RNL9gzyRzJk1wHLO`, node `22:2`, is the visual reference; its absolute positions are not used.

## Unchanged semantics

89 Topics, 46 Categories, 31 Learned, 12 Verified, 137 Knowledge Relations. All labels and topics render at every zoom. Project 113 has 26 distinct requirements; Stage 4 has 12. No project_applies. Source model and model builder are unchanged. Modes, Inspector, Search, manual disclosures, pan/pinch and evidence interactions remain.

## Geometry

`AtlasLayout.LAYOUT` defines all external spacing/safe-area/lane tokens. Root/Major/Category/Topic fonts remain 28/21/17/14 natural px. Cards are measured with the browser's actual system-font metrics. Category heights are standardized by structural depth. Trays use one measured column, a 220 px row width (236 including tray padding), expanding locally for long labels. Complete labels wrap; font sizes never shrink to solve geometry.

Measurement is bottom-up. Each subtree owns a disjoint region containing cards, topic trays, safe areas, descendants and routing lanes. Child region widths are summed with category gutters of 64 px or major gutters of 112 px. Siblings cannot occupy each other's empty region. The viewport budget, shelf packing and offline fit optimizer are removed.

Placement is top-down through measured regions. Category centers account for the actual region anchor, including asymmetric direct-topic lanes. Baseline structural depths share Y positions. At each depth, a tray band reserves the maximum real tray height before the next structural depth: category → tray 68 px, tray → next structural band 72 px. Without trays, structural gaps are 88/82/76 px. Java's presentation sibling order is Basics, Code organization, Working with data, Errorless code, on one baseline; this does not change canonical parents or IDs.

Mixed parents reserve direct topics in a separate lateral region, connected from the same bus. Existing child regions are never routed through that tray. Leaf trays remain centered on their own category. All three major regions remain distinct in their original left/center/right semantic order.

## Hierarchy and evidence

Hierarchy routing derives one orthogonal trunk and bus per parent, followed by child drops. Source is bottom-center; cards and trays terminate at top-center. Bus is 28 px below the parent and at least 30 px above children. Singleton aligned paths simplify to a continuous vertical stem.

Category and tray paths are unioned into SVG segments, including explicit junctions. Shared intervals render once. Tray intervals carry all their topic keys for exact evidence projection. There is no second amber overlay geometry: coverage styles those same segments. Knowledge Relations retain the existing separate mint rounded obstacle routing, hidden until a topic is selected.

## Checkpoint and growth

Checkpoint schema 5, explicit algorithm `atlas-spatial-5`. The `anchor` is the measured distance from the region left boundary to its category center. Records persist category dimensions, allocated regions, sibling order and tray bounds; no topic coordinates or semantic/evidence state. A stale algorithm is rejected, not silently loaded. The generator explicitly bypasses the old checkpoint for this authorized geometry migration.

Growth preserves previous bands/anchors and expands regions only as needed. Existing earlier sibling positions stay fixed; successors shift horizontally when an expanded region would violate its gutter. Ancestors are not recentered wholesale. New branches append to the local region. Checkpoint rebuilds are deterministic. Growth may shift the right-hand major branch when Programming languages becomes wider; zero unrelated movement is not claimed.

Fit All uses actual content bounds after geometry is complete. Project/mode changes never rebuild layout, alter coordinates/checkpoints, change the camera or expand nodes.

## Reproduction

With the server running:

- `python3 tests/integrity.py`
- `node tests/spatial.cjs`
- `node tests/browser.cjs`
- `node tests/relations.cjs`
- `node tests/readability.cjs` (strict 10 px target; currently returns failure)

`tests/generate-checkpoint.cjs` explicitly generates a fresh baseline. Old boxed/compaction/tray/composition suites describe V6.1–V6.4 geometry, including coordinate-equality and 10 px assumptions; they are not V6.5 acceptance suites. Prior architecture/validation remain under `tests/review/v6.4/`.
