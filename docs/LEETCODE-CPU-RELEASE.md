# LeetCode CPU Atlas release

Public sibling route: <https://planton361.github.io/hyperskill-projects/leetcode-atlas/>.
Accepted source: foundation commit `0c980b0c2e62c15cabce998467d8e4928627936c`,
including the final responsive top UI polish. The copied six CPU source files
and four snapshot inputs retain the exact hashes in `src/leetcode-atlas/BASELINE.json`.

## Publication decision and licenses

On 2026-10-09 the owner explicitly requested publishing the built CPU Atlas.
After the earlier unresolved redistribution gate was explained, the owner
answered: “wenn es besser ist, nutze eine geegiente lizenz, ich gebe es frei”.
This is recorded as a specific public-release approval for the existing
metadata-only snapshot, superseding the prior local-only release restriction.
It is not recorded as a separate LeetCode rights-holder grant.

Original MyAtlas CPU implementation and its adapters use MIT, per the owner's
license instruction. The community publisher declares MIT for
[kaysss/leetcode-problem-set at the pinned revision](https://huggingface.co/datasets/kaysss/leetcode-problem-set/blob/81f5c9e681bbcc6d334a17fc7d8666c9a039d7a8/README.md).
Source revision: `81f5c9e681bbcc6d334a17fc7d8666c9a039d7a8`.
CSV SHA-256: `ad3828cb457962a0aa63553cdaf07240f671074ecc95542035be6fe91604dfef`.
No new source acquisition occurs. Publication relies on that publisher
declaration and the owner's explicit decision; the underlying LeetCode
redistribution rights have not been independently established. Choosing MIT
for our implementation does not relicense third-party material or establish
an upstream grant. Historical acquisition/provenance notices stay unchanged.

[LICENSE](../src/leetcode-atlas/LICENSE) covers original implementation;
[NOTICE.txt](../src/leetcode-atlas/NOTICE.txt) records source attribution and
scope. D3 retains its BSD-3-Clause notice and Noto Sans retains OFL 1.1.
The same notices are packaged alongside the published application. This
decision does not authorize statements, descriptions, solutions, scraping,
new acquisition or any private account access.

## Inventory and preserved behavior

Only the accepted CPU runtime, two integration files, four existing snapshot
inputs, and license notices are added under `src/leetcode-atlas/`. The shared
read-only loader, frozen MyAtlas CSS, D3, fonts and their license notices are
reused from existing committed sources. `scripts/build-leetcode-atlas.py`
verifies committed input bytes, accepted hashes, exactly 3,511 unique IDs and
empty packaged personal evidence before writing only `build/pages/leetcode-atlas/`.
No raw CSV, descriptions, examples, solution code, private profile, credentials,
extension or exported owner progress is packaged. The frozen Hyperskill build,
guard, accepted release manifest, source assets and navigation remain unchanged.
Generated files stay ignored under `build/`.

Build adapters only relocate relative paths, retain the reviewed public-progress
and top UI hooks, and make the CPU page's first two navigation links open the
existing `knowledge-map/` route. They do not embed or modify the Hyperskill shell.
The CPU's accepted 240 × 120 cards, Category placement, world coordinates,
filters, focus, zoom and Inspector are preserved. Geometry SHA-256 remains
`c23469da99adc627db3a52d89d316082e53514d8d7210e46c1b13cc8296504a6`.

This is the pinned 3,511-record community snapshot, not today's official
complete LeetCode catalog. Canonical IDs stay unchanged, including evaluation
IDs; no evaluation ID is inferred to be an official internal/numeric ID.
Green cards and counts read the existing public `solved.json` anonymously.
No solves are hardcoded, migrated, renamed, inferred or written. Initial
failure remains unavailable; failed refresh retains an explicitly stale
validated projection. Refresh never repacks or rebuilds the CPU world.
Owner capture/publishing and uncertain Accepted confirmation remain unchanged.

## Reproduce and test

From a committed clean checkout:

```sh
python3 -B scripts/check-myatlas-production.py
python3 -B -m unittest scripts.tests.test_leetcode_cpu scripts.tests.test_leetcode_progress
python3 -B scripts/build-myatlas.py
python3 -B scripts/check-myatlas-production.py --site build/pages/knowledge-map --current-head
python3 -B scripts/build-leetcode-progress.py
python3 -B scripts/build-leetcode-atlas.py
cp docs/.nojekyll build/pages/.nojekyll
npm ci --prefix scripts/knowledge_atlas --ignore-scripts
scripts/knowledge_atlas/node_modules/.bin/playwright install chromium webkit
mkdir -p build/preview
ln -s ../pages build/preview/hyperskill-projects
python3 -B -m http.server 8807 --bind 127.0.0.1 --directory build/preview
```

Use a fresh preview directory or retain its existing symlink. Open
`http://127.0.0.1:8807/hyperskill-projects/leetcode-atlas/`. Then run:

```sh
node tests/leetcode-atlas/progress.cjs test-results/leetcode-cpu
node tests/leetcode-atlas/top-ui.cjs test-results/leetcode-cpu after
node tests/myatlas/release.cjs
node tests/myatlas/geometry-browser.cjs
```

`CPU_SITE_PREVIEW` selects the project root URL; `CPU_PREVIEW` selects the CPU
route for toolbar tests. `CPU_CHROME=1` uses installed Google Chrome locally;
the default uses locked Chromium, plus WebKit in both cases. `PLAYWRIGHT_MODULE`
can point at an existing locked tooling installation. The toolbar suite tests
2048/1440/1280/1024/768/390 px with live progress and dynamic counts. Mocked
progress tests cover green pixels, category/difficulty counts, duplicates,
undo, offline/malformed responses, unresolved IDs, anonymous requests and
unchanged layout/index objects. Fixtures stay in disposable visitor contexts.

The existing summary tests and all Hyperskill gates remain in the workflow.
Release branches validate without deploying. Only green CI permits a reviewed,
fast-forward-safe main update; main repeats all gates before Pages deployment.
Verify both previous routes, CPU navigation and all five Hyperskill fingerprints
live afterward. Rollback uses focused revert commits through the same workflow,
never force-push, manifest regeneration or public-progress changes.
