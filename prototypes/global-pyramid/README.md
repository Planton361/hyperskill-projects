> **Current architecture: ADAPTIVE_VIEW_PRODUCTION_ADOPTED.** Production is
> deployed as **GLOBAL REFERENCE + ADAPTIVE LOCAL PYRAMID**. The strict-global
> personal-coordinate Version-A Production adoption is permanently superseded,
> unless a future explicit architecture decision replaces it. Historical migration
> packages and approval tokens are non-applicable.
> See [the current decision](../../scripts/knowledge_atlas/ARCHITECTURE-DECISION.md).
> The documentation below is retained historical/reference evidence, not a pending
> Production migration or current operator workflow.

# Global Canonical Pyramid — Version A

Current pre-migration candidate: **A2 root composition**, awaiting human visual
approval. See [ROOT-LAYOUT-VALIDATION.md](ROOT-LAYOUT-VALIDATION.md) and
[root-layout/global-overview.png](root-layout/global-overview.png). All previous
migration packages/tokens are **STALE**. No new migration package has been generated.

The frozen A1 artifact under `root-layout/previous-global-geometry.json` supplies
local subtree geometry; A2 only translates those blocks and updates the presentation
apex/sectors/routes. No internal layout or node scale changes. Focused current checks:

```sh
python -B prototypes/global-pyramid/build.py --check
python -B -m unittest discover -s prototypes/global-pyramid/root-layout -p test_root_layout.py -v
```

The older UX/baseline suites and reports below remain historical A1 evidence. Do not
refresh their frozen hashes to disguise this intentional geometry revision.

Isolated, read-only experiment. Every scope hydrates the same generated geometry.
No activation, Production migration, acquisition, persistent browser state or
runtime layout generation is involved.

From the repository root:

```sh
python -B prototypes/global-pyramid/build.py --check
python -B -m unittest discover -s prototypes/global-pyramid/tests -v
python -B prototypes/global-pyramid/tests/measure.py
python -B -m http.server 8000 --bind 127.0.0.1 --directory prototypes/global-pyramid
```

Open http://127.0.0.1:8000/. Choose a root, use inspector child/path navigation,
search a title or `category:73`, `leaf:333`, `reference:333`, then focus a branch
or slot. Wheel/buttons zoom, drag/arrows pan, Back restores the previous camera and selection.
Fit Scope changes only the camera; it never compacts hidden positions.

Browser QA uses externally installed Playwright and Chromium:

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
CHROMIUM_EXECUTABLE=/absolute/path/to/chrome \
node prototypes/global-pyramid/tests/browser.cjs
```

The UX refinement treats `generated/global-geometry.json` as immutable. Use
`--check` to validate it; UX work must never regenerate or rewrite it.
Scopes keep the camera when switching. Fit My Atlas / Course / Project fits
relevant cards and immediate parents; the minimap keeps the full world visible.
Local sibling ghosts are the default, with active-only and ancestor variants
available. Select a branch or Topic group for detail. Search includes dormant
slots and inspects them without activation.

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
CHROMIUM_EXECUTABLE=/absolute/path/to/chrome \
node prototypes/global-pyramid/tests/browser-ux.cjs
```

See [UX-VALIDATION.md](UX-VALIDATION.md) for the current UX report and three-viewport
screenshots. All outputs stay in this directory. See [DESIGN-VALIDATION.md](DESIGN-VALIDATION.md)
for the complete report, file manifest, measurements and screenshot links.


Final desktop polish adds wrapped, collision-suppressed labels, collapsed deep
breadcrumbs with an ancestor menu, and Previous / Next relevant-region jumps.
Branch summaries distinguish scope Topics from observed learned / verified counts.
Use Tab and Enter for controls; Search ArrowDown reaches results, Escape closes
the ancestor menu or leaves focus, and Alt+Left / Right jumps between regions.
The minimap supports Enter to fit scope and arrow keys to pan.

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
CHROMIUM_EXECUTABLE=/absolute/path/to/chrome \
node prototypes/global-pyramid/tests/browser-final.cjs
```

[FINAL-UX-VALIDATION.md](FINAL-UX-VALIDATION.md) is the final polish report, including
36 inspected desktop screenshots and the migration recommendation. The earlier
validation reports remain historical evidence. `tests/final-ux-baseline.json`
locks the task-start geometry and protected file hashes; do not refresh it to
accept a geometry or authoritative-state change. Final QA outputs are isolated
in `tests/final-ux/`. Use `ATLAS_TEST_OUTPUT` with the older browser harnesses to
preserve historical outputs.
