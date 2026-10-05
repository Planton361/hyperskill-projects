# Activation Persistence — local validation

Baseline HEAD: `4e4a15bf4cfb7fb9abf587aebdae74033bb5624d`.
Local validation record for the activation persistence baseline. No new factual
Course activation or visible geography is included. Hosted CI must be observed
for the final committed revision before declaring the baseline ready.

## Files Added

- scripts/knowledge_atlas/activation_persistence.py
- scripts/knowledge_atlas/activation_geometry.js
- scripts/knowledge_atlas/activation_variants.js
- scripts/knowledge_atlas/activation-state.schema.json
- scripts/knowledge_atlas/ACTIVATION-PERSISTENCE.md
- scripts/knowledge_atlas/ACTIVATION-PERSISTENCE-VALIDATION.md
- scripts/tests/test_knowledge_atlas_activation_persistence.py
- scripts/tests/fixtures/activation/scenarios.json
- scripts/tests/fixtures/activation/reviewed-centering.json
- state/knowledge-atlas/activation-state.json

## Files Changed

- scripts/update-knowledge-atlas.py
- scripts/plan-knowledge-atlas-activation.py
- scripts/knowledge_atlas/pipeline.py
- scripts/knowledge_atlas/layout_bridge.cjs
- scripts/knowledge_atlas/state.py
- scripts/knowledge_atlas/transaction.py
- scripts/knowledge_atlas/report.py
- scripts/knowledge_atlas/README.md
- state/knowledge-atlas/README.md
- .github/workflows/knowledge-atlas-check.yml
- .gitignore

The reference prototype remains untouched by this persistence iteration. Its
pre-existing untracked files are not staged. All 555 other original untracked
files retain their original hashes. No raw HAR is tracked or staged.

## Activation State

Strict schema 1, separate from factual Knowledge data. Accepted geometry is
stored exactly, including Topic trays/rows and additive hierarchy segments.
Hash checks bind geometry to the update snapshot; ID/generation checks bind it
to the checkpoint. Incompatible/unknown fields require explicit migration.
No Course membership, requirements, progress or relation truth is stored here.

## Baseline ACTIVE_HISTORY

46 accepted Categories and 89 Topics; all 135 existing bounds are unchanged.
History version0; layout Generation0. No Python or other dormant branch receives
real accepted geometry. Global Catalog remains5 roots/849 Categories/3106 leaf
references, with1 resolved/88 partial/3017 unresolved.

## Bootstrap

`--bootstrap-activation-state` records the authoritative Generation-0 baseline.
It refuses overwrite and non-baseline migration. Reproducible bootstrap bytes
are tested against the real baseline activation state. The established checkpoint
and update snapshot are not rewritten.

## Preview Workflow

`--activation-preview DIRECTORY [--course ID | --project ID] --variant NAME`
creates deterministic local artifacts and, for renderable/no-change scope, a
static local review page. External directories or ignored
prototypes/activation-previews are allowed; existing packages cannot be overwritten.
The real Course-8 preview reports NO_CHANGE with zero new nodes and zero expected
Generation change. No persistent state or Production write occurs.

A local Course-8 review package was generated outside the repository. Its
view/index.html displays the exact no-change candidate. Local package paths are
not serialized into accepted presentation history.

## Activation Manifest

Binds plan, complete Knowledge/Catalog/evidence/personal inputs, history,
checkpoint, existing geometry/bounds/connectors, exact candidate, variant,
algorithm implementation/version, accepted runtime and validation report.
The manifest has its own deterministic fingerprint. Approval also requires the fingerprint copied during human review, so a consistently replaced package under the same path cannot reuse an old review. Human output shows context,
new IDs, metadata blockers, geometry metrics and expected Generation change.

## Plan Fingerprint

Canonical semantic inventory hashing is insensitive to input inventory order.
No generated clock timestamp participates. Source observation dates are meaningful
provenance inputs and changing them invalidates the input binding.

## Geometry Fingerprint

Ordered presentation serialization; no coordinate rounding before hashing.
Independent geometry, existing-bound and connector fingerprints are retained.
Subpixel changes alter the candidate fingerprint. Approval checks existing
node/tray/branch/connector prefixes byte-for-byte, not within a tolerance.

## Selected Variant Binding

CENTERING is selectable and independently bound. It is not globally preferred.
The reviewed disposable Small candidate reproduces exact reviewed node, tray and
segment geometry:3 Categories/6 fixture Topics, maximum drift919px,0 displacement,
0 overlaps,0 crossings,0 canvas growth.919px is not an acceptance threshold.
Empty/refused plans do not invoke a variant comparison that requires new geometry.

## Approval Workflow

`--approve-activation /path/activation-manifest.json --reviewed-fingerprint <HASH>` revalidates the exact artifact
and current input bindings. It never regenerates the geometry to be persisted.
Fresh semantic planning and independent geometry/build validation precede the
joint transaction. Fixture manifests are forbidden to the operator CLI.

## Stale Preview Rejection

Tests cover changed Course/project/stage/evidence/progress inputs, Catalog,
checkpoint, accepted node/connector geometry, plan/candidate/metrics/manifest,
selected variant, algorithm and runtime. Failures reject before publication.
Artifact/source/runtime fingerprints are checked again at transaction preflight.

## Metadata Blocking

METADATA_REQUIRED reports IDs, reasons and missing fields. Relevant unresolved
references cannot be silently omitted from complete activation. No automatic
partial activation or fake Topic title exists.

## Review Blocking

Canonical normal builds and Production updates return REVIEW_REQUIRED when
new renderable relevance is outside ACTIVE_HISTORY. The old approve-review flag
cannot bypass activation identity. Pure read-only previews are not approval.
Legacy isolated allocator tests without activation history retain their test API;
canonical Production and history-aware updates always enforce the new guard.

## Rebalance Blocking

Ordinary activation approval cannot override geometry refusal or a new-root plan.
No automatic/global rebalance implementation is added.

## Small-Centering Disposable Apply

Two tested paths: the internal explicit fixture adapter, and the ordinary operator
API with synthetic normalized evidence in a disposable repository copy. Both
persist exact reviewed Centering geometry. Only the temporary copy reaches49
Categories/95 Topics and Generation1. No synthetic Knowledge is written into the
real repository. Numeric fixture IDs are an isolated schema adapter, not real
Hyperskill identities.

## Large Fixture

6 requested Categories/156 fixture Topics: ACTIVATION_REBALANCE_REQUIRED.
No ordinary persistence; refusal thresholds are not weakened.

## Blocked Fixture

References333/336 remain unresolved: METADATA_REQUIRED, no placeholder geometry,
no approval. They do not become Topic entities merely from structural identity.

## New Root

ACTIVATION_REBALANCE_REQUIRED. No Math or other inactive root is attached to
Computer science or persisted by the ordinary activation path.

## Transaction Safety

Exclusive root lock; fully staged state and Production; input/artifact preflight;
durable journal; atomic directory exchanges; final release/state byte verification.
The state directory transaction includes activation history, checkpoint and update
snapshot, so there is no separately published activation-state half-update.

## Crash Recovery

Injected exceptions and real fork/os._exit tests cover candidate preparation,
state staging, before swaps, after state swap, after Production swap and before
journal completion. Recovery restores the old coherent release before COMMITTED.
The existing durable COMMITTED record remains the commit point and makes cleanup
recoverable. Pending journals block readers until explicit recovery.

## Generation Rules

Baseline and previews:0. A newly accepted geometry event:+1 exactly once.
Project/progress/relations on accepted geography: no geometry increment.
History version counts activation events separately from the layout counter.

## Idempotency

Second identical apply returns NO_CHANGE; state, Production and counters remain
byte-identical. An old artifact after other relevant input/history changes is
stale, not authorization to restore an earlier map.

## Determinism

Equivalent inputs produce byte-identical package artifacts. Reversed semantic
inventory order produces the same plan fingerprint. Exact candidate arrays and
coordinates preserve presentation order. No randomness or generated timestamps.

## Production Auto-Activation Guard

Tested with explicit synthetic new-Course membership in a disposable copy:
normal --production returns REVIEW_REQUIRED and leaves Production unchanged.
Current real --check and --dry-run both return SAFE_TO_APPLY / NO_CHANGE.

## Course History

Accepted IDs form accumulated ACTIVE_HISTORY. Course completion or a current-course
switch does not remove accepted geography. Historical Knowledge metadata must
remain available; missing facts produce an explicit error, not destructive hiding.

## Project-Only Workflow

A project evidence/status update on already accepted Topics needs no activation
preview. Disposable post-activation project completion and explicit personal
progress updates preserve exact accepted geometry and Generation1.
The real repository remains31 learned/12 verified. Project113 keeps26 explicit
requirements; Stage4 keeps12. No project_applies is introduced.

## Search / Fit / Minimap Integration Contract

Normal accepted model plus stored geometry drives search, focus, minimap and Fit
Active Atlas. Additive branch routes support the existing LCA/amber taxonomy
routing. Relations do not reveal dormant endpoints. Production contains no fixture
or preview styling/labels; no Global Catalog UI is added.

## CI

Read-only workflow now includes fixture-path triggers and the new persistence tests
through its Atlas test discovery. Applies and recovery run only in temporary roots;
real Production/state hashes remain guarded. Hosted CI is a separate required
finalization check on the committed revision; local results do not establish it.

## Current Production Regression

14/14 Production assets byte-identical to the pre-implementation hash inventory.
Real browser regression:1141 checks PASS;18 viewport/theme scene sequences match
the accepted preview exactly. Public deployment is untouched.

## Current State Regression

Both established state JSON files are byte-identical. Generation0, schema2,
algorithm atlas-incremental-2;0 Category/Topic displacement. Only baseline activation
history and its documentation are added. All11 Knowledge files are unchanged.

## Tests

| Matrix | Result |
| --- | --- |
| Activation persistence |24 tests PASS|
| Atlas + Hardening (final rerun) |53 tests PASS|
| Global Catalog, activation planner, graph, importer, Map |113 tests OK;1 optional local HAR test skipped|
| Packaging |7 tests PASS|
| Real browser/runtime |1141 checks PASS;18 identical viewport/theme scene sequences|
| Real --check / --dry-run |SAFE_TO_APPLY / NO_CHANGE; Generation0; checkpoint unchanged|
| Course8 / Project113 plans |NO_CHANGE;0 new geometry/metadata blockers|

Total 197 distinct unittest cases executed, with 196 passing and the documented optional
HAR acceptance case skipped. No known failing suite remains.

## Remaining Risks

- First real Course needs explicit normalized membership/metadata/evidence inputs;
  this iteration does not implement collection or resolve3017 references.
- Approval requires an external reviewed manifest fingerprint; this is integrity-bound operator authorization, not signed identity.
- A hard crash before the journal can leave ignored orphan staging directories; live targets remain unchanged and recovery never adopts those candidates.
- Broad/repeated activation, multi-root geography, old-label resizing and additive
  growth of an existing Topic Tray require separate design/review.
- Review thresholds remain prototype heuristics, not universal acceptance policy.
- Hosted CI must succeed on the final committed revision before readiness is declared.

## Ready For First Real Course Activation?

Infrastructure readiness requires successful hosted CI on the final committed
revision. A first real Course additionally requires explicit real evidence,
resolution of required metadata and separate review/approval of an exact candidate.
No real new Course is activated here. This does not approve future geometry in
advance, remove refusal gates or grant automatic use of Centering.
