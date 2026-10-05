# Experimental Global Atlas

Read-only, non-authoritative projection of the captured Global Catalog. This is
neither Production, ACTIVE_HISTORY, nor an activation preview. The accepted
personal Atlas remains authoritative. No activation, acquisition, crawling,
deployment or Knowledge mutation API is present here.

From the repository root:

```bash
python -B prototypes/global-atlas/build.py
python -B prototypes/global-atlas/build.py --check
python -B -m http.server 8000 --bind 127.0.0.1 --directory prototypes/global-atlas
```

Open <http://127.0.0.1:8000/>. Static HTTP is required for JSON loading. No runtime
dependency, CDN, authenticated request, browser storage or backend is used.

```bash
python -B -m unittest discover -s prototypes/global-atlas/tests -v
# Optional external test dependencies, already installed outside this repository:
PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
CHROMIUM_EXECUTABLE=/absolute/path/to/chrome \
node prototypes/global-atlas/tests/browser.cjs
```

The browser test serves files through an offline Playwright route, creates an
isolated non-persistent context, and writes only this prototype's screenshots
and `tests/browser-results.json`. Measurements are machine-dependent. See
[DESIGN-VALIDATION.md](DESIGN-VALIDATION.md) for architecture, findings and gaps.

Files added only under this directory:

- Projection/runtime: `build.py`, `atlas.js`, `app.js`, `index.html`, `style.css`,
  `generated/catalog.json`.
- Documentation: `README.md`, `DESIGN-VALIDATION.md`.
- Tests: `tests/test_model.py`, `tests/core.cjs`, `tests/browser.cjs`.
- Validation artifacts: `tests/browser-results.json`, `tests/validation.json`,
  `tests/global-overview.png`, `tests/my-atlas.png`, `tests/project-stage.png`,
  `tests/deep-focus.png`.
