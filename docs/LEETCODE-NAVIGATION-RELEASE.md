# Persistent LeetCode navigation

The owner approved this specific navigation fix and its release on 2026-10-09.
Previously, following Atlas or My Skill Tree from the CPU page opened the
two-link Hyperskill shell and left no visible return link to LeetCode.

The release adds `../leetcode-atlas/` to that shell, restricts the existing
two-view router to links carrying `data-view`, and lets the three links fit in
the existing mobile header. It preserves native link, keyboard, modifier-click
and browser history behavior. It adds no application mode or progress writes.

## Exact exception to the navigation freeze

The accepted V6.6 manifest, all original `src/myatlas` sources, original builder,
guard, historical evidence and committed `docs/knowledge-map` remain unchanged.
This release supersedes the earlier instruction to leave navigation unchanged
only for the three edits in `docs/releases/myatlas-leetcode-navigation.json`.
No rendering, geometry, catalog, filter, progress, extension or publisher change
is authorized by this supplement.

The workflow first performs the entire original V6.6 build and current-head
validation. A separate packaging step then applies the exact pinned edits to
`index.html`, `shell.js` and `shell.css`, updating runtime inventory/provenance.
No extra file is added inside `knowledge-map`. Its final navigation gate checks
the exact output hashes, reverses only these three pinned edits in a disposable
copy, and runs the original unmodified V6.6 guard on that copy. Every other
application byte and all existing evidence/progress checks stay protected.
The final artifact is V6.6 with this explicit navigation supplement, rather than
a claim that its header is byte-identical to the original frozen header.

## Reproduce from committed sources

```sh
python3 -B -m unittest scripts.tests.test_myatlas_release scripts.tests.test_myatlas_navigation
python3 -B scripts/build-myatlas.py
python3 -B scripts/check-myatlas-production.py --site build/pages/knowledge-map --current-head
python3 -B scripts/build-myatlas-navigation.py
python3 -B scripts/build-myatlas-navigation.py --check
python3 -B scripts/build-leetcode-progress.py
python3 -B scripts/build-leetcode-atlas.py
```

The existing locked Playwright browser tooling runs the production interactions,
all five accepted geometry fingerprints, CPU progress and top UI checks. The
focused `tests/myatlas/navigation.cjs` additionally verifies all three links,
both return paths, keyboard focus/activation, no header collisions or overflow,
and widths 2048, 1440, 1280, 1024, 768 and 390 in Chromium/Chrome and WebKit.
Its default GitHub response is disposable and mocked; `NAV_LIVE_PROGRESS=1`
selects a public read-only GET for final live verification. No browser profile,
credentials or personal progress is changed.

Release via a `release/**` branch first; publish to main only after all CI gates
pass. Never disable checks or regenerate the V6.6 accepted manifest. Rollback is
a normal revert of this release and workflow rebuild, restoring the earlier
two-link shell while keeping the existing CPU/progress sibling routes.
