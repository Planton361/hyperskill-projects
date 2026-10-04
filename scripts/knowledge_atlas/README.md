# Knowledge Atlas production hardening (pipeline v2)

The accepted V6 UI and public URLs are unchanged. `/knowledge-map/` is the
production Atlas target. This offline
pipeline reads normalized knowledge and persistent presentation history. It
never collects authenticated data, infers evidence, creates `project_applies`,
commits, pushes or deploys.

Clean-checkout inputs include the accepted V6 runtime/vendor files below
`prototypes/knowledge-atlas-v6/` and the intentionally versioned frozen geometry
fixture `fixtures/accepted-v6-geometry.json`. Screenshots and historical browser
run outputs are not dependencies. Local Playwright installations are selected
with `PLAYWRIGHT_MODULE`; no personal filesystem path is embedded in the bridge.
Dry-run/check reports include the actual font measurements/browser version and
source, checkpoint, geometry, build-manifest and asset hashes for hosted parity
comparison.

## Normal operator workflow

```bash
python -B scripts/update-knowledge-atlas.py --dry-run
python -B scripts/update-knowledge-atlas.py --production
python -B scripts/update-knowledge-atlas.py --check
git diff
```

Default / `--build` publishes validated prototype artifacts and, when needed,
updates both persistent state files as one transaction. Output remains
`prototypes/knowledge-atlas-v6/build/` (ignored). The state lives in
`state/knowledge-atlas/` (intentionally version controlled). Review the state diff
and commit it yourself when appropriate. The default remains an isolated build;
only explicit `--production` packages `/knowledge-map/`. The updater never
commits, pushes or deploys.

## Production packaging and rollback

`--production` requires canonical `data/knowledge/` and `state/knowledge-atlas/`
and strictly SAFE_TO_APPLY. REVIEW_REQUIRED and REBALANCE_REQUIRED cannot be
bypassed with production flags. It builds in memory, validates source/state,
font canary, geometry and runtime, verifies the accepted runtime assets, then
runs all nine widths (1920, 1440, 1280, 1200, 1024, 768, 430, 390, 320) in both
themes. The initial generation-0 baseline additionally compares complete scene
sequences against the retained accepted public Preview: exact node/tray/path
geometry, rendered SVG text metrics, navigation, relations and Inspector data.
The binary spelling of derived line-height metadata is not a rendered metric;
SVG text bounds are compared exactly, with no added font/geometry tolerance.

Only title/header Preview wording is removed. The persistent-state hydration and
generic project index adapters were already part of the accepted pipeline.
Their hashes and every difference from the historical Preview are explained in
`release-manifest.json`. No CSS, routing, relation, model-runtime or vendor edit
is permitted. The production file set must equal the manifest plus the manifest
itself; old assets are replaced as a directory, never left alongside the Atlas.
`geometry.js` is a required runtime asset. Snapshots, fixtures, notes and reports
are not deployed.

The existing durable directory-exchange transaction publishes production and,
only if changed, persistent state together. Final file-set/hash/byte verification
occurs before the durable COMMITTED marker; any failure rolls back all targets.
The same Linux `renameat2`/crash-recovery limitations as prototype transactions
apply. Previews, the historical graph, normalized knowledge and Profile README
are never production targets. `--production --dry-run` performs the complete
candidate regression without final writes. `--check` additionally checks the
installed Atlas package against regenerated production bytes. A second unchanged
production build preserves all state and production bytes.

After a Hyperskill project completion: update normalized knowledge through the
existing import workflow, dry-run, inspect the report, build production only for
SAFE_TO_APPLY, inspect `git diff`, commit and push manually, then confirm hosted
Atlas CI, Pages deployment and public assets/behavior. Project/progress-only
updates must have zero structural displacement and no checkpoint/generation
change.

For REVIEW_REQUIRED: inspect the candidate report and an isolated candidate or
explicit Preview; obtain human review, then run `--approve-review` separately to
persist the reviewed presentation state/prototype. Re-run dry-run; only the now
SAFE_TO_APPLY production candidate may be packaged. For REBALANCE_REQUIRED:
simulate `--dry-run --rebalance`, visually review the geography, explicitly
approve and run `--rebalance`, inspect the new generation, perform full
regressions, then package production separately. Production never authorizes a
geography migration implicitly.

The pre-promotion production commit is
`044f4d1a99d840bdae6e85dafff4457d055d2b74`. Git history is the rollback archive;
no V3 copy is deployed. To roll back, `git revert <migration-commit>`, review,
run applicable validation and commit/push the revert through the normal release
process. This restores the prior production assets and packaging changes. Never
rewrite history or run rollback automatically.

`--dry-run` performs full diff, classification, semantic-region analysis,
candidate reconstruction, geometry validation and in-memory browser validation.
It never writes persistent state or final build output. `--check` also requires
knowledge to match the saved comparison fingerprint, verifies the checkpoint/
snapshot pair and geometry fingerprint, checks exact frozen V6 reconstruction,
and compares installed build bytes if a build exists. With no ignored build, it
validates a complete reproducible build in memory. Both use read-only directory
locks and never repair state implicitly.

## Review and explicit geography migration

```bash
python -B scripts/update-knowledge-atlas.py --dry-run --report-json /tmp/knowledge-atlas-update-report.json
python -B scripts/update-knowledge-atlas.py --approve-review
python -B scripts/update-knowledge-atlas.py --dry-run --rebalance
python -B scripts/update-knowledge-atlas.py --rebalance
```

Outcomes are SAFE_TO_APPLY, REVIEW_REQUIRED or REBALANCE_REQUIRED for a valid
candidate. Validation, state-migration and font failures are separate errors,
never release approvals. Normal commands apply only SAFE_TO_APPLY. Review
candidates are fully generated/validated in memory and reported; they do not
replace the final build or state. `--approve-review` explicitly authorizes that
review candidate but cannot bypass REBALANCE_REQUIRED. `--rebalance` explicitly
allows a complete layout reconstruction, subject to all validation contracts.
Outcome is retained in the report even when explicitly approved; `applied` and
`authorization` distinguish simulation, blocked release and authorized mutation.
Reports show candidate and persisted generation separately.

Exit codes: 0 safe or explicitly authorized apply, 3 REVIEW_REQUIRED without
apply, 2 REBALANCE_REQUIRED without apply, 1 validation/state/font error.
`--check` cannot be combined with approval/rebalance writer authorizations.

`--json` prints only JSON. `--report-json PATH.json` writes the current JSON report and
sibling `.txt` diagnostic report, including blocked outcomes, with atomic file
replacements. These explicitly requested diagnostics are the only report writes
in dry-run/check mode. Source/state/docs/runtime/build/generated/workflow paths are refused as report
locations. The installed build's `update-report.json` retains the last installed
report on an immediate NO_CHANGE run so no artifacts churn. Diagnostics are
post-operation output, separate from the state/build transaction.

## Bootstrap and recovery

```bash
python -B scripts/update-knowledge-atlas.py --bootstrap-state
python -B scripts/update-knowledge-atlas.py --recover-transaction
python -B scripts/update-knowledge-atlas.py --migrate-state
```

Only explicit bootstrap may create absent state. It requires the exact accepted
source baseline and all 135 frozen bounds matching before writing. Partial or
existing state is never overwritten. No normal command falls back to a new map.
State schema 2 uses order-preserving presentation hashes. `--migrate-state` is
the explicit, lossless schema-1-to-2 hash migration for the recognized layout-2
format; it validates the source and old geometry before joint state/build
publication. Unknown state schemas return STATE_MIGRATION_REQUIRED. Layout-version mismatch
requires an explicit migration/rebalance of a recognized state format.

Recovery is a separate exclusive writer operation. A pending journal blocks
read-only and normal updates. See `state/knowledge-atlas/README.md` for the
commit point, crash behavior, atomic-directory-exchange platform requirements
and rollback protocol. State/source changes between validation and publication
are detected in a final optimistic preflight. Do not edit state or the source
concurrently with an update; non-pipeline tools do not honor the advisory lock.

`--source PATH` supports normalized fixtures. A write with custom source requires
explicit `--state PATH` below `prototypes/`, preventing a fixture from replacing
real repository history. `--output PATH` also stays below `prototypes/`; existing
unmanaged/tampered output directories are refused. State/build paths must be
disjoint. Tests use disposable state, source and build directories.

## Region and movement policy

Origins are canonical parents of new/removed Topics/Categories and changed
labels. Expected geography consists of each origin's subtree and ancestor chain
up to its existing Major region (depth 1). The root and unrelated branches are
excluded. Following siblings/subtrees moved by propagation are reported
separately, never silently called local. Reports include origins, ancestors,
actual moved categories, unrelated categories, repacked trays, escalation,
capacity exhaustion, bounds, median/p90/max movement and outcome reasons.

Measured baseline units: 64 px category sibling gap, 112 px Major gap,
29–63 px topic rows, 4 px row gap, 236 px typical tray width. Defaults:

| Scope | Normal release policy |
| --- | --- |
| Changed tray rows | append/repack locally; >256 px tray growth requires review |
| Expected categories | >64 px movement requires review |
| Direct siblings | >32 px movement requires review; any movement outside expected region also requires review |
| Unrelated categories | 0 preferred; any movement requires review |
| Existing root/Major anchors | 0 allowed; any movement requires rebalance |
| Existing category >384 px | hard rebalance limit |
| Width reserve exhausted across 3+ regions | rebalance |
| New category | always review |
| Changed label | review; valid measured growth, no silent layout reset |
| Reparenting/layout-version migration | explicit rebalance |

The 256 px threshold is about six ordinary 41 px rows including gaps; it is a
review trigger rather than a claim that allocated space is free. Test both
semantic locality and magnitude; 30 px in an unrelated JVM branch is review,
1 px of a Major anchor is rebalance. Pixel budgets alone never authorize release.

Category slots append deterministically, multiple new IDs numerically ordered.
When a new horizontal slot would exceed its parent's allocation, it wraps to a
reviewed second local row inside that parent's width. Hierarchy routes derive a
boundary rail automatically from allocation; no semantic relation is changed.
The real new-Java-Category fixture is REVIEW_REQUIRED with zero existing anchors
moved. A new direct Basics tray propagates to Databases, so its real fixture is
REBALANCE_REQUIRED. Three Topics appended to existing JVM basics are SAFE_TO_APPLY
with zero existing category/topic displacement.

Persistent tray row allocations preserve source-independent positions/order.
Removed rows can reserve their former slot; reserve is excluded from visible
Fit-All bounds when no live content uses it. Generation changes once per actual
persisted presentation mutation, including row ordering/dimensions, even when
category anchors do not change. Nonstructural changes never mutate the checkpoint
or generation. Six-decimal relative offsets eliminate state floating noise while
reproducing original frozen geometry exactly.

## Browser/font environment and local CI parity

The workflow `.github/workflows/knowledge-atlas-check.yml` is read-only. Its pins:
Ubuntu runner 24.04, Python 3.12.11, Node 22.16.0, Playwright 1.62.1, Chromium
revision 1234 / **151.0.7922.34**, locale en-US / en_US.UTF-8, DPR 1, viewport
1440×900 (accepted browser navigation regression also uses 1920×1080).
Noto Sans Regular/Bold are vendored under `fonts/` with their OFL license and
SHA-256 values in `font-canary.json`. The fontconfig policy selects Noto Sans.

Every bridge call checks three representative widths plus ascent/descent with
0.001 px tolerance BEFORE any structural work or state publication. A mismatch
returns FONT_METRICS_MISMATCH. Baseline checks additionally cover all accepted
category/topic measurements. The canary is a drift detector, not a substitute
for the complete frozen geometry test.

Reproduce the browser/font environment on Linux (install outside the repo):

```bash
npm install --prefix /tmp/atlas-browser --ignore-scripts playwright@1.62.1
export PLAYWRIGHT_MODULE=/tmp/atlas-browser/node_modules/playwright
export PLAYWRIGHT_BROWSERS_PATH=/tmp/atlas-pinned-browsers
/tmp/atlas-browser/node_modules/.bin/playwright install --with-deps chromium
mkdir -p "$HOME/.local/share/fonts/knowledge-atlas"
cp scripts/knowledge_atlas/fonts/*.ttf "$HOME/.local/share/fonts/knowledge-atlas/"
fc-cache -f
export FONTCONFIG_FILE="$PWD/scripts/knowledge_atlas/fontconfig.xml"
export CHROMIUM_EXECUTABLE="$(node -e 'process.stdout.write(require(process.env.PLAYWRIGHT_MODULE).chromium.executablePath())')"
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
python -B scripts/knowledge_atlas/verify_environment.py
python -B scripts/update-knowledge-atlas.py --check
```

The pinned browser and font policy were tested locally and reproduce both the
canary and all 135 frozen bounds. The original local reference is Chrome
154.0.8037.57 with the same font files and identical measured canary widths.
Linux distro, FreeType/fontconfig and runner image packages are not fully
container-digest pinned; full OS-level parity with hosted Actions is not claimed.
The guards fail visibly on drift. The pipeline itself downloads no dependencies.

## Validation and CI

```bash
python -B -m unittest discover -s scripts/tests -p 'test_knowledge_atlas*.py' -v
node scripts/knowledge_atlas/browser-regression.cjs
PYTHONPATH=scripts python -B -m unittest knowledge_atlas.test_production -v
```

Existing knowledge schema/evidence rules, IDs, references, canonical parents,
cycles, memberships, stage/project requirements and progress remain validated.
No requirement becomes application evidence. Global Topics are never duplicated
by course membership. Nonstructural geometry/checkpoint identity is exact.
Geometry checks cover every node/tray, region containment, hierarchy endpoints,
zero semantic overlap and zero hierarchy crossings. The in-memory runtime checks
all projects and loaded stages; the separate read-only accepted browser harness
covers Project 113/Stage 4 and taxonomy-route/navigation preservation. When a
production manifest is installed, the existing read-only CI browser step also
runs the full production viewport/theme matrix and accepted Preview comparison.

CI triggers on pushes/pull requests affecting knowledge/pipeline/state and relevant V6 runtime files, plus manual dispatch. It
installs exact browser dependencies/fonts, runs canary, check, dry-run, unit
contracts, accepted browser regression, verifies production state hashes and
uploads only JSON/TXT reports. REVIEW_REQUIRED exits 3 and makes the workflow
fail visibly; REBALANCE_REQUIRED exits 2. No approval flags, bootstrap, recovery,
preview, state apply, artifact push or deployment are present in CI. Tests can
write only their disposable fixture state/build trees.

`--preview` remains an explicit optional packaging command after authorization
and validation. It participates in the same transaction, retains preview notes,
and never deploys. It was not used in this hardening iteration. Review any
release-specific numerical claims in retained notes before packaging new data.

The inherited V6 Inspector/course context still uses the first course. Global
membership indexes are prepared for future overlays/filters; no UI redesign or
course selector is part of this work. Physical-device/screen-reader certification
is not established by headless pipeline tests.
