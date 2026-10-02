# Public Preview release validation

These tools and artifacts are private repository validation material. They are
not copied into docs/knowledge-map-preview/. Every browser release test loads
only the real preview model; no fixtures are injected.

From repository root, install the development-only browser test dependency:

```sh
npm install --prefix prototypes/knowledge-tree-v5/tests/release
npx --prefix prototypes/knowledge-tree-v5/tests/release playwright install chromium
```

Then:

```sh
python prototypes/knowledge-tree-v5/build-preview.py --check
python -m http.server 8774 --bind 127.0.0.1 --directory docs
```

With that server running, in another terminal:

```sh
node prototypes/knowledge-tree-v5/tests/release/rollup.cjs
node prototypes/knowledge-tree-v5/tests/release/coverage.cjs http://127.0.0.1:8774/knowledge-map-preview/
node prototypes/knowledge-tree-v5/tests/release/browser.cjs http://127.0.0.1:8774/knowledge-map-preview/
node prototypes/knowledge-tree-v5/tests/release/performance.cjs http://127.0.0.1:8774/knowledge-map-preview/
node prototypes/knowledge-tree-v5/tests/release/contracts.cjs http://127.0.0.1:8774/knowledge-map-preview/
node prototypes/knowledge-tree-v5/tests/release/routing.cjs http://127.0.0.1:8774/knowledge-map-preview/
```

Run performance alone, without concurrent browser checks. Timing wrappers are
installed only in that measurement context; published assets remain unchanged.
Alternatively supply an existing Playwright installation through PLAYWRIGHT_MODULE. Generated screenshots, benchmark output and reports are ignored; runtime assets are unchanged.

For the full GitHub Pages prefix, start a second static test server:

```sh
python prototypes/knowledge-tree-v5/tests/release/serve-prefix.py
```

Then:

```sh
node prototypes/knowledge-tree-v5/tests/release/subpath.cjs
gh api repos/Planton361/Planton361/contents/README.md --jq '{path,sha}' > prototypes/knowledge-tree-v5/tests/release/profile-readme-after.json
python prototypes/knowledge-tree-v5/tests/release/verify-release.py
```

The aggregate release gate checks the three actions separately:

- Show/Hide: zero canonical, category, checkpoint, disclosure, rendered-coordinate,
  search and viewport differences; no layout planning. Manual changes survive Hide.
- Reveal: all required topics rendered; no checkpoint/canonical/viewport change.
  Compact screen coordinates may change with explicit disclosure.
- Fit: current visible topic/roll-up representation; viewport changes only.

Coverage totals exactly 26 distinct real requirements, including mixed disclosure.
All 18 viewport/theme cases pass. The aggregate gate exits 0 when these contracts
and existing release regressions pass. Physical-device and real screenreader
checks remain outstanding and are not marked passed.

The original protected-file/source hashes and remote Profile README blob are
stored as evidence of this work session. Do not regenerate the before manifests
to hide unrelated source or production changes. Physical-device and real
screenreader checks have not been performed.
