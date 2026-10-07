# V6.6 full-title preview validation

These checks apply to the metadata-enriched preview, not the historical accepted geometry. The historical `accepted.cjs`, `protected-source.json`, and accepted report continue to describe commit `ca5dbe97d37f3c6fe034d6338da88285d9fdb640`; they must not be rewritten to accept the new geometry.

Start the local preview from the repository root:

```sh
python3 -B -m http.server 8801 --bind 127.0.0.1 --directory prototypes/knowledge-atlas-v6-global
node prototypes/knowledge-atlas-v6-global/tests/full-title/validate.cjs
```

The existing `tests/browser.cjs` uses repository Playwright by default. An installed browser may be supplied using `ATLAS_BROWSER_EXECUTABLE`; `PLAYWRIGHT_MODULE` can select an existing Playwright installation. No authenticated profile is used. Validation checks all 3,106 title/numeric searches and Topic Inspectors, all Category focus calls, measured title bounds, occupied sibling contours, card/tray/route collisions, deterministic reload, every raster inventory, main-thread fallback, and navigation without layout calls.

Run the offline ingestion audit with the original external candidate path as the sole positional argument:

```sh
python3 -B prototypes/knowledge-atlas-v6-global/tests/full-title/audit.py '<external candidate path>'
```

It validates both candidate digests, the existing strict observation contract, source and target fingerprints, the exact persisted observation, normal Catalog composition, immutable original evidence, personal progress, and active Course/Project/Stage facts. Optional `--baseline-manifests '<local manifest directory>'` verifies protected before/after hashes and original Knowledge files. The original run checked 1,199 protected files and all 11 preexisting Knowledge files; the manifests remain outside Git.

`review.cjs` compares the current preview with a separately served, untouched accepted prototype copy (`BEFORE_URL`, default port 8802; `ATLAS_URL`, default port 8801), records actual browser measurements, and captures exactly seven 1440×900 Dark/DPR2 review images. `metrics.json` contains the accepted hash as well as the final preview hash. The baseline must be the accepted ID-based model/layout together, not the new model in the old layout.

`safari.html` is the focused native Safari DPR2 probe. A local server must accept its `/safari-result` POST and save only the safe timing result. `safari.json` records one warm navigation run: overview pan/zoom, one programming subtree focus, and Topic 3887 focus. Warm frame cadence is compared with the historical 17 ms p95 baseline. This is local-only; no remote endpoint or acquisition profile is involved.

`checks.json`, `ingestion-audit.json`, `metrics.json`, `safari.json`, and the seven `review/*.png` files are the current preview evidence. They are not a new human acceptance milestone.
