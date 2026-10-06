# Durable canonical spatial authority validation

**Recommendation: C — READY FOR ONE EXPLICIT REAL MIGRATION REVIEW/APPLY SESSION.**

The normal updater now supports legacy and installed canonical authority. All migrated
writes in this task occurred in marked external temporary copies. The real repository
remains legacy: 46 Categories, 89 Topics, 31 learned, 12 verified, Generation 0,
activation history 0. No real migration, activation, acquisition, commit, push or
deployment occurred. Real canonical publication remains explicitly blocked.

## 1. Files changed

Normal integration modifies:

- `scripts/update-knowledge-atlas.py`
- `scripts/knowledge_atlas/activation.py`
- `scripts/knowledge_atlas/activation_persistence.py`
- `scripts/knowledge_atlas/build.py`
- `scripts/knowledge_atlas/catalog.py`
- `scripts/knowledge_atlas/layout_bridge.cjs`
- `scripts/knowledge_atlas/pipeline.py`
- `scripts/knowledge_atlas/report.py`
- `scripts/knowledge_atlas/state.py`
- `scripts/knowledge_atlas/validate.py`

New durable helpers: `canonical.py`, `canonical_activation.py`,
`catalog_projection.py` under `scripts/knowledge_atlas/`.
New durable runtime assets under `scripts/knowledge_atlas/canonical_runtime/`:
`app.js`, `atlas.js`, `ux.js`, `labels.js`, `style.css`, `index.html`,
`authority-guard.js`. They adapt the proven renderer; normal builds have no prototype
imports and ship no experimental controls or debug panels. No new dependency.

Migration-review compatibility changes: `migration-review/review.py`,
`migration-review/tests/test_review.py`, `migration-review/tests/crash.py` under
this prototype. Tests generate fresh previews after implementation changes, the
state-reader assertion now expects canonical support, and real-root refusal precedes
locking. The migration apply gate remains disposable-only.

New documentation, tests and evidence are below `durable-authority/`:
`PLAN.md`, `README.md`, `tests/test_durable.py`, `tests/crash.py`,
`tests/browser.cjs`, baseline/integrity/results/performance JSON, console logs and
25 PNG screenshots. This report is new. [Exact path/hash inventory](durable-authority/tests/changed-files.json).
Existing canonical generator and master artifact were not edited.

## 2. Updater architecture

The existing CLI, pipeline, state reader, activation persistence, builder and
transaction publisher are extended. There is no second updater. Relevance still
comes from `ActivationPlanner` and explicit Catalog evidence. Deterministic snapshot
encoding and the existing release validator remain in use.

## 3. Legacy / canonical dispatch

Installed `state/knowledge-atlas/spatial-authority.json` triggers strict canonical
validation. Prototype files never install authority. Missing authority with partial
canonical checkpoint/history/snapshot records is refused. Absent authority plus
legacy records retains the existing allocation path. Canonical mode rejects legacy
rebalance/custom-state operations and never falls back to additive allocation.

Real final `--check` and `--dry-run`: `SAFE_TO_APPLY`, `NO_CHANGE`,
`applied=false`, `state_changed=false`, spatial Generation 0. That ordinary no-change
status does not authorize spatial migration.

## 4. Persisted authority schema

Reuse the reviewed schema-1, kind `global-canonical-pyramid` authority exactly:
`kind`, `schema_version`, `geometry_schema_version`, `geometry_fingerprint`,
`geometry_sha256`, `catalog_fingerprint`, `layout_algorithm_version`,
`review_candidate_fingerprint`, `slot_contract`, `master_asset`.

Checkpoint schema 3 and activation schema 2 bind the same authority and exact visible
geometry. The snapshot schema-3 wrapper retains the normal source index. Separate
schema-1 spatial history records the migration event/version, source/target geometry,
review identity and generation transition. The archived migration receipt binds the
authority bytes and reviewed contract. No competing authority/version representation
was added. Unknown fields/versions, partial records, mismatched fingerprints,
noncanonical accepted geometry or incompatible receipts fail closed.

## 5. Canonical restore

Read the **installed** `docs/knowledge-map/generated/global-geometry.json`; verify
its exact SHA, embedded fingerprint, schema, algorithm, structural catalog, aliases,
roots and routes. Validate accepted inventory, every position/size/parent/path,
ancestor context, root sectors, extent, groups and routes against that master.
Repeated restoration returns the exact persisted canonical records. No prototype
layout generation or coordinate recomputation occurs.

## 6. Production rebuilding

The normal `--check`, `--dry-run`, `--production` succeed after disposable migration;
repeated Production publication is byte-identical/idempotent. The initial exact
migration package is recognized, and normal Production packaging replaces its
adapter with durable branded assets without changing accepted coordinates or counters.

The fixture retains the real pre-migration V6 build cache. Its managed integrity is
checked, but its old geometry is never used for hydration or treated as authority.
The report identifies a stale derived cache; `--build` refreshes it. Installed
State and Production remain strictly checked. Search, scopes, global minimap,
Fit My Atlas, branch/deep focus, saved taxonomy routes, semantic relations and
independent learned/verified styling work in the durable runtime.

## 7. Canonical reveal planning

Normal `--activation-preview DIRECTORY --project 113` produces one
`CANONICAL_REVEAL` candidate using reserved slots. It records newly active identities,
slot coordinates, parent/root, metadata state, authority fingerprint, zero existing
node displacement, zero placement evaluations and explicit counter deltas. Other
placement variants are refused. Normal builds report review required and never
activate geography themselves.

The static `review.html` shows the exact candidate Production in an iframe, links
coordinates/routes/relevance/metrics, and supplies a copyable manifest fingerprint.
Existing accepted rows are copied exactly; only accepted visibility, contextual
subset and scope extent change.

## 8. Reveal approval

Use the existing `--approve-activation MANIFEST --reviewed-fingerprint HASH` command.
The external token, closed manifest schema and complete package byte inventory are
checked. Bindings cover normalized Knowledge, personal state, Course/Project/Stage
and provenance evidence, relevance context/plan, complete ACTIVE_HISTORY, checkpoint,
installed authority/master, State/Production inventories and relevant implementation
and runtime bytes. Candidate slots/routes, semantic publication, release inventory,
metrics and expected counters are independently validated.

Approval publishes **exact reviewed geometry, checkpoint and Production bytes**.
It derives only compatible State wrappers/events from reviewed identities. Missing
or wrong tokens, altered artifacts, consistent rehash with an old token, changed
semantic inputs or changed runtime bindings refuse publication. Identical repeated
previews are byte-identical. Identical approved replays return `NO_CHANGE` without
another event; previews become stale after later reveals or semantic changes.

## 9. No placement search

Disposable tests replace legacy `activation_geometry.js`, `persistent_layout.js`
and `layout_update.js` with throwing scripts. Normal canonical checks, builds and
reveals still pass. Additional approval tests make the layout bridge and builder
raise if called: exact approval still succeeds and the published geometry bytes
match the candidate bytes. Metrics report `placement_search=false`, evaluations 0.
Only a browser-validation action is added to the existing bridge, before loading
legacy layout code.

## 10. Reference → Topic

`reference:333` and `topic:333` both resolve to reserved `leaf:333`.
Its exact slot is `(148938, 41431, 240, 32)`, primary parent `category:428`.
A separate normal-updater test enriches dormant reference 333 with explicit synthetic
Topic metadata: semantic resolution changes, accepted geometry and counters do not.
Then explicit Project relevance is added and normal preview/approval reveals Topic
333 at that same slot. Existing positions remain identical and Production validates.
No real Topic metadata was resolved or fabricated.

## 11. Structural extension / refusal

Explicit refusal tests cover unknown Topic ID, new Category, new root, changed
accepted parent, bad authority fingerprint, unsupported schema and partial authority.
They leave State/Production unchanged. Captured structural parent memberships and
inventory are compared independently of metadata. Unknown structural identities or
changed memberships return `SPATIAL_AUTHORITY_EXTENSION_REQUIRED`; inconsistent
installed authority returns `SPATIAL_AUTHORITY_MIGRATION_REQUIRED`.

Missing accepted normalized metadata, explicit evidence, Topic theory ID or URL
returns `METADATA_REQUIRED`. A reserved slot is never sufficient to invent a Topic.
Learned/verified/progress, Project completion, Course membership, requirements,
Stage evidence, provenance and metadata enrichment may change without altering
spatial authority. Authority fingerprints bind structure/geometry, not arbitrary
semantic labels or progress.

## 12. Counter / event policy

This implements the existing preview section 16 recommendation explicitly:

| Transition | Spatial Generation | Activation history | Spatial history |
|---|---:|---:|---:|
| Real legacy baseline | 0 | 0 | absent |
| Disposable migration | 1 | 0 | 1 |
| First canonical reveal | 1 | 1 | 1 |
| Second canonical reveal | 1 | 2 | 1 |
| Identical reveal again | 1 | 2 | 1 |
| Progress / Project / other semantic updates | 1 | 2 | 1 |

The migration increments spatial Generation once; known-slot reveals change
activation history/visibility only. Migration is a separate typed event, never
135 activations. Authority schema and reviewed master remain unchanged.

## 13. Transaction / recovery

Reuse the existing exclusive lock, durable staging/files, source preflight,
journal, State/Production swaps, byte verification and recovery. ACTIVE_HISTORY,
checkpoint, snapshot, reveal receipt and Production publish coherently. Knowledge
is not a transaction destination. Post-swap validation checks installed canonical
State and exact release bytes before the durable `COMMITTED` journal record.

Nine exception-injection rollbacks and eleven actual process-exit cases pass.
Pre-commit boundaries: before authority validation, after candidate validation,
before State staging, after State staging, after Production staging, before swaps,
after State swap, after Production swap, before commit record. Recovery restores
old coherent canonical State + Production. Hard exits after durable commit and
after cleanup preserve new coherent State + Production. Explicit recovery also
cleans staging orphaned before journaling. [Boundary results](durable-authority/tests/recovery-results.json).

## 14. Complete disposable end-to-end scenario

Copy current legacy source, State, Production and V6 cache into an external marked
root. Generate a fresh migration preview/review, approve its exact token and apply
with the existing disposable adapter. Verify immediate semantic identity: 46/89,
31/12, Project 113 = 26, Stage 617 = 12, unchanged ACTIVE_HISTORY membership.
Run normal check/dry-run/Production and deterministic rebuild.

Add valid disposable metadata/hierarchy and Project relevance for 333, review and
approve through the copied **normal CLI**, check exact slot and all 135 prior rows.
Repeat for 334 and check all 139 prior rows. Final fixture contains 53 Categories
and 91 Topics (144 accepted positions), reflecting seven new accepted ancestor
Categories and two Topics. Both repeated approvals are no-change.

Then update progress/learned/verified, Project metadata and completion, Topic URL,
Course membership and Stage evidence through normal Production builds. Exact visible
geometry stays unchanged; completion infers no learned/verified state. Deliberate
progress evidence makes fixture counts 32 learned/13 verified. Project 113 has 28
requirements after the two synthetic additions; Course 8 stays 89 and Stage 617
stays 12. All fixture facts remain temporary.

**274 complete prior-position records compare exactly; maximum displacement 0 px.**
[Scenario evidence](durable-authority/tests/e2e-results.json).

## 15. Browser results

Headless Chrome validates final disposable Production at 1440×900, 1920×1080 and
1024×768. Eight scenes each cover My Atlas, Course 8, Project 113, Stage 617,
revealed Topic 333 from search, deep Topic 78, semantic relations and keyboard
minimap/region navigation. All 3,955 world slots are checked in each scene:
**94,920 entity comparisons / 379,680 exact x/y/width/height comparisons**, zero
mutation; serialized master remains identical. No browser errors/external requests
or horizontal page overflow. The exact reveal-review fingerprint is also checked.

All 25 screenshots were visually inspected. Scope colors remain distinct, ancestors
and local sibling ghosts are subordinate, progress marks independent, global minimap
and keyboard focus remain visible. Search focuses the new Topic at its canonical
slot. Broad views intentionally remain sparse; region controls and semantic zoom
make local navigation readable. Focused cards become large, and at 1024 px some
Category labels are suppressed rather than overlapping. These are presentation
tradeoffs, not integration blockers. The review page needs scrolling to inspect
its full iframe and the right inspector can require scrolling.

Screenshot inventory under `durable-authority/tests/`:
`{1440,1920,1024}-{my-atlas,course-8,project-113,stage-617,revealed-333,deep-topic,relations,navigation}.png`,
plus `1440-reveal-review.png`. [Browser assertions/metrics](durable-authority/tests/browser-results.json).

## 16. Performance

Final local fixture measurements include browser validation and filesystem work;
CLI samples are not isolated CPU microbenchmarks. No large dependency was added.

| Viewport | Initialization ms | Draw median / p95 ms | Scope median / p95 ms | Search median / p95 ms | JS heap MiB |
|---|---:|---:|---:|---:|---:|
| 1440×900 | 58.4 | 1.4 / 1.7 | 0.9 / 1.0 | 0.2 / 0.3 | 22.8 |
| 1920×1080 | 60.7 | 1.5 / 1.7 | 0.9 / 1.2 | 0.3 / 0.3 | 17.4 |
| 1024×768 | 58.6 | 1.4 / 1.7 | 0.9 / 1.2 | 0.2 / 0.3 | 17.0 |

Fit median is below timer resolution (reported 0), p95 0.1 ms; recorded region
navigation 0.6–1.1 ms. Thirty repeated draw/scope/fit/search samples per viewport.
Heap is Chrome's estimate, not a memory bound. Normal CLI median check 3,195 ms
(8 samples), dry-run 3,328 ms (1), Production 3,904 ms (9), preview 3,844 ms (5),
successful/idempotent approval 2,797 ms (5). End-to-end scenario including browser
capture and semantic builds: 80.2 s. [Raw CLI measurements](durable-authority/tests/performance.json).

Tests: final integration **8 PASS** in `stable-test-console.txt`; additional
repeat-preview/missing-token/runtime-staleness test **1 PASS** in
`deterministic-reveal.txt`; existing migration approval **15 PASS**, global pyramid
model/UX **11 PASS**, normal Atlas/planner/activation/hardening regression **110 PASS**.
Total **145 distinct Python tests pass**, with browser and fault cases inside them.
The stable integration pass includes the inherited real V6 cache and final strict
migration-receipt validation. No unrelated massive suite was repeatedly run.

## 17. Real protected hashes

All 30 protected files and exact inventories match before/after, including no
added/deleted authoritative files. [Full per-file comparison](durable-authority/tests/protected-integrity.json).
Tree hashes below are SHA-256 of sorted compact UTF-8 JSON mapping root-relative
paths to each file SHA-256; `ensure_ascii=false`.

| Protected tree | Files | Identical before / after SHA-256 |
|---|---:|---|
| Production `docs/knowledge-map/` | 14 | `0b1b1f413c13f36689119c7b7115ae4bd963ff67352edfabcc72600ae037ee00` |
| State `state/knowledge-atlas/` | 4 | `7b69371cb87d3dcb880803b9698b90bf09f322152ae8f1867424557a14b22137` |
| Knowledge `data/knowledge/` | 11 | `29a3d477c5aed81e53c2bf551abcb6f41fbbf3b42d71e56a0bc7c813489d35f9` |

Canonical master SHA before/after:
`9671e7ca5517c1f35e5ee3affac066362a2470d04ef6251cbe2faa6024572c44`.
Embedded fingerprint before/after:
`0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194`.
Exact size before/after: **3,295,568 bytes**. No generator was run against it.
Real authority installed: **false**. Real Generation/history and ACTIVE_HISTORY are
unchanged; final normal legacy check/dry-run pass without publication.

## 18. Remaining risks

Previously saved preview/review packages bind old validator/runtime bytes and are
now **stale**. A later real session must generate a fresh isolated preview and review
package, visually inspect that exact candidate, copy a new fingerprint, and explicitly
review enabling the real-root publication gate. The old copied token is not reusable.

Schema-1 captured authority is deliberately closed. Structural additions/reparenting
need a separately reviewed authority extension; there is no automatic extension.
The hash contract binds reviewed bytes and does not authenticate a human by itself.
The disposable marker is a development write gate, not a cryptographic credential.
Full mobile/accessibility work and alternative relation visualization remain outside
this task. Cooperative writers must use the shared lock; direct external file edits
are checked by preflight/staleness guards. Migration/apply outside the marked test
adapter remains unavailable in this implementation phase.

## 19. Recommendation

**C — READY FOR ONE EXPLICIT REAL MIGRATION REVIEW/APPLY SESSION.**

Normal legacy and canonical runtime/updater paths are validated; exact reviewed
reveals are durable, metadata-safe and zero-displacement; recovery is proven; real
Production/State/Knowledge remain untouched. This recommendation is readiness for
a separately authorized fresh review/apply session, not approval or execution of
that migration here.
