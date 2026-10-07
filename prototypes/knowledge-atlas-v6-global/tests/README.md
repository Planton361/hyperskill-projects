# Accepted Global validation and commit scope

The accepted implementation is unchanged. Test infrastructure now uses the repository's tracked Playwright 1.62.1 dependency/lockfile rather than requiring a particular `/tmp` module or a machine-specific browser executable.

From repository root, install the existing development dependency and Chromium:

```sh
npm ci --prefix scripts/knowledge_atlas --ignore-scripts
scripts/knowledge_atlas/node_modules/.bin/playwright install chromium
python3 -B -m http.server 8791 --bind 127.0.0.1 --directory prototypes/knowledge-atlas-v6-global
```

With that local server running, run only the focused checks:

```sh
node prototypes/knowledge-atlas-v6-global/tests/focused.cjs
node prototypes/knowledge-atlas-v6-global/tests/accepted.cjs
python3 -B prototypes/knowledge-atlas-v6-global/tests/integrity.py
git diff --check
```

`ATLAS_URL`, `PLAYWRIGHT_MODULE` and `ATLAS_BROWSER_EXECUTABLE` optionally select an existing server, installed runner or browser. The accepted numeric geometry fingerprint uses macOS system-ui text measurement; other platforms can render the same source with different font metrics. The fingerprint check is intentionally strict. `focused.cjs` preserves the current local alignment, identity, completeness, text/tray/card/routing collision and indexing assertions; it does not reinstate the obsolete global same-depth Y rule. `accepted.cjs` checks the live freeze fingerprint, deterministic initialization, exact progress anchors and zero distinct progress overlap, complete tile inventories, navigation stability and accepted Inspector/orientation behavior at one 1440 × 900 DPR2 viewport. It reads the existing final Safari evidence; it does not start another benchmark.

`integrity.py` compares the current data projection without writing `model.json`, and verifies the frozen Global runtime and all tracked protected files/shared dependencies in `protected-source.json`. The freeze also checks a complete local inventory, including the existing untracked My Skill Tree work; that machine-local inventory is excluded from the commit. Generated check outputs go to ignored `tests/generated/`.

Optional final screenshots can be reproduced with `node prototypes/knowledge-atlas-v6-global/tests/capture-accepted.cjs`; they go to `tests/generated/`. Runtime needs no npm package: `index.html` loads the committed relative JS/CSS, `model.json` and vendored D3. `build.py` retains the projection source, using the tracked Catalog/snapshot modules and existing Knowledge data. Do not regenerate the accepted model as part of read-only validation.

Commit classification:

| Class | Included / excluded |
| --- | --- |
| A — required source | All prototype root JS/CSS/HTML/data/projection files and D3/license; included unchanged. |
| B — required focused tests | Current local-geometry suite, live accepted-milestone suite, integrity check, portable browser helper, final capture helper and tracked protection manifest; included. |
| C — important reports | BASELINE, all eight Global milestone reports, final acceptance document and concise accepted check records; included. Historical conclusions remain historical. |
| D — small final evidence | Three final review screenshots (Fit All, Programming languages selection, Topic Focus) and final Safari measurements; included. |
| E — reproducible output | Other screenshots, large before/after facts and geometry dumps, traces, console output, timing experiments; excluded. |
| F — local investigation/cache | Superseded capture/comparison/benchmark drivers, historical source copies, temporary inventories, browser/tile/npm/Python caches; excluded. |
| G — unrelated work | My Skill Tree, adaptive previews/reviews, unrelated docs and other existing local work; excluded and unchanged. |

Historical report links to omitted generated artifacts document the original review; their prose is preserved. The committed current suites and three final screenshots are the final reproducible checkpoint. No historical viewport matrix, broad migration suite or Production deployment is part of this freeze.
