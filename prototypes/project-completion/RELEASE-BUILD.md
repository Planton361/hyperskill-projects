# Frozen V6.6 local release recipe

Build and serve only a new disposable linked Git worktree. The builder refuses the original checkout. Python 3 and Node are the build tools; every browser runtime asset is versioned in this repository. No npm dependency or Hyperskill connection is required by the build or static site.

```sh
git worktree add --detach /tmp/v66-release-review HEAD
cd /tmp/v66-release-review
python3 -B scripts/check-adaptive-production.py
python3 -B scripts/sync-project-completion.py > /tmp/v66-public-review.json
python3 -B scripts/build-v66-candidate.py
mkdir -p /tmp/v66-preview/hyperskill-projects
ln -s /tmp/v66-release-review/docs/knowledge-map /tmp/v66-preview/hyperskill-projects/knowledge-map
python3 -m http.server 8807 --bind 127.0.0.1 --directory /tmp/v66-preview
```

Preview: `http://127.0.0.1:8807/hyperskill-projects/knowledge-map/`.

For focused browser validation, install the repository's locked development dependency with `npm ci --prefix scripts/knowledge_atlas`, then run `scripts/knowledge_atlas/node_modules/.bin/playwright install chromium` if needed. In another terminal at the isolated worktree root:

```sh
ATLAS_PREVIEW=http://127.0.0.1:8807/hyperskill-projects/knowledge-map/ node prototypes/project-completion/release-test.cjs
```

Results go to ignored `test-results/v66-release.json`; no screenshots are required. `ATLAS_REVIEW_ARTIFACT` can select a different result path. `ATLAS_BROWSER_EXECUTABLE` can select an installed Chromium for local validation; it is not a site dependency.

The builder preserves the committed 15-file Production edition and historical manifest, packages the accepted three renderers inside the two-tab shell, resolves dormant personal Topic references from committed catalog identities, relocates relative assets, checks generated learning evidence at the renderer boundary, and retains legacy URL adapters. It generates a public progress projection and a full candidate/source manifest. Repeating the build at the same HEAD is byte-identical.

Only the isolated worktree's `docs/knowledge-map/` is replaced. The original checkout's Production guard continues to verify the current public edition. That historical guard intentionally does not approve the replacement package. Publishing and the new-edition migration gate require separate approval; no deployment workflow is activated by this recipe.
