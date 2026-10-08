# V6.6 analytics and Git sync local checkpoint

Recommendation: **C — V6.6 ANALYTICS AND SYNC CHECKPOINT COMPLETE**.

This checkpoint preserves the accepted application and completion-learning contract. No new product features, redesign, live Hyperskill requests, Production integration, push or deployment. The only preparation edits were replacing machine-specific paths in two focused browser tests with the existing repository browser helper, and refreshing focused validation artifacts.

## Local commits and inventory

Original commits `a99777d9fc7126dc4ab5d079e9d1fc6b93940f55`, `6c1934c979c2e002f7dac2e4c7cc0b347e8e15df`, and `4c14b8a6b41f6f6d22674d90d26e6333cc2af23f` remain in order. The local `origin/main` reference was verified as `a8b79e2e6c32df990fc3305983bb5aff1d9e2500`; no fetch or remote write was used.

First checkpoint: `9082a8cc25c8d6f14c2c993632d34d186f099717` — analytics, Universal Inspector and the completion projection consumed by that runtime, 36 files. Completion aggregation and runtime loading were already coupled, so these are kept together rather than introducing a transient missing runtime dependency.

Second checkpoint: the commit containing this report — completed-export discovery/import support, Git sync, workflow and reviews, 16 files. Resolve its exact SHA using `git log -1 --format=%H -- prototypes/project-completion/CHECKPOINT-REVIEW.md`; the final checkpoint response records it. Both real commits explicitly stage reviewed paths, inspect staged differences, validate inventory and check staged contents for secrets/private paths.

First commit files:

- `prototypes/knowledge-atlas-scope-pyramid/app.js`
- `prototypes/knowledge-atlas-scope-pyramid/index.html`
- `prototypes/knowledge-atlas-scope-pyramid/ux-model.js`
- `prototypes/knowledge-atlas-v6-global/app.js`
- `prototypes/knowledge-atlas-v6-global/index.html`
- `prototypes/knowledge-atlas-v6-skill-tree/PROGRESS-ANALYTICS-REVIEW.md`
- `prototypes/knowledge-atlas-v6-skill-tree/README.md`
- `prototypes/knowledge-atlas-v6-skill-tree/UNIVERSAL-PROGRESS-INSPECTOR-REVIEW.md`
- `prototypes/knowledge-atlas-v6-skill-tree/app.js`
- `prototypes/knowledge-atlas-v6-skill-tree/index.html`
- `prototypes/knowledge-atlas-v6-skill-tree/model.js`
- `prototypes/knowledge-atlas-v6-skill-tree/progress-analytics.js`
- `prototypes/knowledge-atlas-v6-skill-tree/progress-presentation.js`
- `prototypes/knowledge-atlas-v6-skill-tree/progress-ui.js`
- `prototypes/knowledge-atlas-v6-skill-tree/progress.css`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-analytics.cjs`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-browser-results.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-browser.cjs`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-protection-results.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-results.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-review/1-overview.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-review/2-java-inspector.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-review/3-course-progress.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-review/4-project-stage-progress.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/progress-review/5-global-personal-comparison.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/universal-browser-results.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/universal-progress-browser.cjs`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/universal-progress-results.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/universal-progress.cjs`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/universal-protection-results.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/universal-review/course2-knowledge-official.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/universal-review/java-course8.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/universal-review/project380-status.png`
- `prototypes/project-completion/REVIEW.md`
- `prototypes/project-completion/progress.json`
- `prototypes/project-completion/test.cjs`

Second commit files:

- `.github/workflows/project-completion-review.yml`
- `prototypes/project-completion/CHECKPOINT-REVIEW.md`
- `prototypes/project-completion/GIT-DRIVEN-SYNC-REVIEW.md`
- `prototypes/project-completion/actions-dry-run.json`
- `prototypes/project-completion/differential-example.json`
- `prototypes/project-completion/protection-results.json`
- `prototypes/project-completion/public-sync-example.json`
- `scripts/import-hyperskill-project`
- `scripts/knowledge_atlas/completion_projection.cjs`
- `scripts/knowledge_atlas/git_completion.py`
- `scripts/knowledge_atlas/project_completion.py`
- `scripts/scan-project-completion.py`
- `scripts/sync-project-completion.py`
- `scripts/tests/test_git_project_completion.py`
- `scripts/tests/test_import.py`
- `scripts/tests/test_project_completion.py`

## Validation

- Analytics aggregation: **17 focused checks PASS**.
- Universal scope tests: all 52 Courses, 391 Projects, 1,967 Stages and 849 Category closures/intersections **PASS**, including official Course versus effective knowledge separation, UNKNOWN versus empty requirements and independent verification.
- Existing completion union tests: **PASS**, including global deduplication, old false observations, provenance, unchanged verification, all scopes and personal tree membership.
- Python scanner/completion tests: **8 PASS**, including legacy 113, exact IDs, incomplete/tampered/ambiguous exports, duplicate/conflicting/revoked evidence, removal, fresh-clone reproduction and dirty-file isolation.
- Importer regression: **17 PASS** with canonical temporary paths.
- Focused Universal Inspector browser test: all eight check groups **PASS**, including nine representative scopes and the accepted geometry fingerprints. No full historical screenshot matrix was repeated; only the existing three focused Inspector captures were refreshed. No browser errors or external requests.
- Workflow YAML parsed successfully. Triggers, read-only permissions, action inventory and run commands were inspected. Commands generate JSON/summary in runner temporary storage and upload review artifacts only; no commit/push, Hyperskill access, Production writer, Pages deploy or generated-output loop.
- Security audit: staged credential/private-path patterns checked, public projection inspected, metadata/path/symlink/identity rejection reviewed and tested, UI provenance escaping and subprocess argument boundaries reviewed. No newly added dependencies or runtime network clients. This is a focused local audit, not an external dependency vulnerability scan.
- Clean-checkout candidate: a disposable clone with precisely the reviewed files committed passed analytics, universal, completion and scanner tests. Its CLI generated byte-identical JSON on repeated runs, the readable summary matched expected totals, and the checkout remained clean. Required browser helper, package declaration, runtime data, and script imports exist in committed sources.
- The saved public JSON example was reconstructed **byte-for-byte** using its recorded source commit and the versioned legacy accepted baseline. Example provenance intentionally records that historical revision; it is not relabelled as a later commit. The scanner's default HEAD mode also reproduces current committed evidence, with source commit and implementation hashes included.
- `git diff --check`: **PASS**.

## Expected portfolio and progress

Project IDs: `[113]`; completed count **1**; exact project-based attestations **26**. Effective global learned **31**, verified **12**. Course 8 **31 / 89**, Project 113 **26 / 26**, Stage 617 **12 / 12**. Project-based learning is unioned with direct evidence by exact Topic ID, retaining direct/project/both provenance. Repeating the scan reports no semantic changes. Verification remains explicit; official Course/Stage progress is not manufactured from completion.

[Public JSON example](public-sync-example.json), [differential example](differential-example.json), [Git sync review](GIT-DRIVEN-SYNC-REVIEW.md), [workflow command dry-run](actions-dry-run.json).

## Production and geometry freeze

The current inventory was recomputed: **496 files** across the previously protected roots. All application/runtime/layout files, historical Knowledge, `docs/knowledge-map/` and `state/knowledge-atlas/` remain byte-identical to milestone entry. Six validation files changed: two browser test helper imports, one browser results JSON and three focused Inspector captures. No application or geometry change was made during checkpoint preparation.

Read-only Production guard: **PASS**; exact Production/state/historical Knowledge inventories, active semantic hashes, state/history/generation and Global reference remain unchanged. Production fingerprint:

`36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`

Accepted fingerprints compared against current browser geometry:

- Global: `1306993ec8a1b7a80edda4f620fb96ba5d4803c0d81ded334b92efa85cdf1174`
- My Skill Tree: `a60fc22e272079c91f39cfed9c01af5865bae29120e6d6f7801b02da96cd6348`
- Course 8: `ab8e05971ca8fb9d077b491a766554f5b84118e068433afe4c17faa7e91fb89b`
- Project 113: `33dc51873bcbd33fa6ad2de854dd719e525706bdb764a50578570d1f73e89034`
- Stage 617: `24edf473c9e97b7ccbb287464302a4bbf6ffadff33efdc265076b5ae6b51455e`

## Exclusions and working tree

The actual repository is intentionally **not globally clean**: unrelated older modifications and untracked preview/review material remain. All checkpoint-selected files are committed; the excluded paths below are retained locally. The original three modified Scope geometry-test harnesses are outside this analytics/sync checkpoint; their current local versions are preserved without staging them. Historical personal-tree development snapshots/tests, earlier relation/navigation review work, and adaptive Production previews are likewise excluded.

- `docs/knowledge-map-adaptive-preview/adaptive.cjs`
- `docs/knowledge-map-adaptive-preview/app.js`
- `docs/knowledge-map-adaptive-preview/atlas.js`
- `docs/knowledge-map-adaptive-preview/global-reference.json`
- `docs/knowledge-map-adaptive-preview/index.html`
- `docs/knowledge-map-adaptive-preview/labels.js`
- `docs/knowledge-map-adaptive-preview/model.json`
- `docs/knowledge-map-adaptive-preview/preview-manifest.json`
- `docs/knowledge-map-adaptive-preview/registry.cjs`
- `docs/knowledge-map-adaptive-preview/style.css`
- `docs/knowledge-map-adaptive-preview/ux.js`
- `docs/knowledge-map-adaptive-preview/vendor/d3-flextree-2.1.2.cjs`
- `docs/knowledge-map-adaptive-preview/vendor/d3-flextree-LICENSE`
- `docs/knowledge-map-adaptive-preview/vendor/d3-hierarchy-LICENSE`
- `docs/knowledge-map-adaptive-preview/views.cjs`
- `prototypes/adaptive-pyramid/production-preview/course.png`
- `prototypes/adaptive-pyramid/production-preview/current-production.png`
- `prototypes/adaptive-pyramid/production-preview/current/app.js`
- `prototypes/adaptive-pyramid/production-preview/current/geometry.js`
- `prototypes/adaptive-pyramid/production-preview/current/index.html`
- `prototypes/adaptive-pyramid/production-preview/current/layout-checkpoint.json`
- `prototypes/adaptive-pyramid/production-preview/current/layout-checkpoint.schema.json`
- `prototypes/adaptive-pyramid/production-preview/current/layout.js`
- `prototypes/adaptive-pyramid/production-preview/current/model.js`
- `prototypes/adaptive-pyramid/production-preview/current/model.json`
- `prototypes/adaptive-pyramid/production-preview/current/release-manifest.json`
- `prototypes/adaptive-pyramid/production-preview/current/routing.js`
- `prototypes/adaptive-pyramid/production-preview/current/style.css`
- `prototypes/adaptive-pyramid/production-preview/current/taxonomy-relations.js`
- `prototypes/adaptive-pyramid/production-preview/current/vendor/D3-LICENSE`
- `prototypes/adaptive-pyramid/production-preview/current/vendor/d3-7.9.0.min.js`
- `prototypes/adaptive-pyramid/production-preview/global.png`
- `prototypes/adaptive-pyramid/production-preview/learning-growth.png`
- `prototypes/adaptive-pyramid/production-preview/my-knowledge.png`
- `prototypes/adaptive-pyramid/production-preview/project.png`
- `prototypes/adaptive-pyramid/production-preview/stage.png`
- `prototypes/adaptive-pyramid/production-preview/topic-group.png`
- `prototypes/adaptive-pyramid/production-review/exact-course.png`
- `prototypes/adaptive-pyramid/production-review/exact-global.png`
- `prototypes/adaptive-pyramid/production-review/exact-my-knowledge.png`
- `prototypes/adaptive-pyramid/production-review/exact-project.png`
- `prototypes/adaptive-pyramid/production-review/exact-review.png`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/app.js`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/geometry.js`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/index.html`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/layout-checkpoint.json`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/layout-checkpoint.schema.json`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/layout.js`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/model.js`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/model.json`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/release-manifest.json`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/routing.js`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/style.css`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/taxonomy-relations.js`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/vendor/D3-LICENSE`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/current/vendor/d3-7.9.0.min.js`
- `prototypes/adaptive-pyramid/production-review/final-v1/view/index.html`
- `prototypes/adaptive-pyramid/real-production-apply/final-results.json`
- `prototypes/adaptive-pyramid/real-production-apply/preflight.json`
- `prototypes/knowledge-atlas-scope-pyramid/COMBINED-COURSE-PROJECT-UX-REVIEW.md`
- `prototypes/knowledge-atlas-scope-pyramid/COURSE-PROJECT-INTEGRATION-REVIEW.md`
- `prototypes/knowledge-atlas-scope-pyramid/CROSS-VIEW-NAVIGATION-REVIEW.md`
- `prototypes/knowledge-atlas-scope-pyramid/MULTI-SCOPE-UX-REVIEW.md`
- `prototypes/knowledge-atlas-scope-pyramid/PERSISTENT-APP-SHELL-REVIEW.md`
- `prototypes/knowledge-atlas-scope-pyramid/RELATION-INGESTION-REVIEW.md`
- `prototypes/knowledge-atlas-scope-pyramid/review/associations/course-2-selectors.png`
- `prototypes/knowledge-atlas-scope-pyramid/review/associations/course-31-selectors.png`
- `prototypes/knowledge-atlas-scope-pyramid/review/associations/course-8-selectors.png`
- `prototypes/knowledge-atlas-scope-pyramid/review/relations/course-8.png`
- `prototypes/knowledge-atlas-scope-pyramid/review/relations/project-380.png`
- `prototypes/knowledge-atlas-scope-pyramid/review/relations/stage-617.png`
- `prototypes/knowledge-atlas-scope-pyramid/review/relations/unknown-project-95.png`
- `prototypes/knowledge-atlas-scope-pyramid/review/ux/course2-unknown-association.png`
- `prototypes/knowledge-atlas-scope-pyramid/review/ux/course8-overview.png`
- `prototypes/knowledge-atlas-scope-pyramid/review/ux/course8-pinned-inspector.png`
- `prototypes/knowledge-atlas-scope-pyramid/tests/association-review.cjs`
- `prototypes/knowledge-atlas-scope-pyramid/tests/catalog-review.cjs`
- `prototypes/knowledge-atlas-scope-pyramid/tests/generality.cjs`
- `prototypes/knowledge-atlas-scope-pyramid/tests/levels.cjs`
- `prototypes/knowledge-atlas-scope-pyramid/tests/ux-review.cjs`
- `prototypes/knowledge-atlas-scope-pyramid/tests/validate.cjs`
- `prototypes/knowledge-atlas-v6-skill-tree/BASELINE.md`
- `prototypes/knowledge-atlas-v6-skill-tree/MY-SKILL-TREE-VALIDATION.md`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/focused-console.txt`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/focused.cjs`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/geometry.cjs`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/integrity-results.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/integrity.py`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/protected-after.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/protected-before.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/results.json`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/review/GLOBAL-REFERENCE-FIT-ALL.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/review/LEARNED-TOPIC-FOCUS.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/review/MY-SKILL-TREE-COMPUTER-SCIENCE.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/review/MY-SKILL-TREE-FIT-ALL.png`
- `prototypes/knowledge-atlas-v6-skill-tree/tests/review/NEXT-TOPIC-FOCUS.png`

Hosted Actions and Pages were not invoked. Any future integration/publication requires a separate request. HARD STOP after the local commits and final read-only checks.
