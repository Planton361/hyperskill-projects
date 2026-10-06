# Exact spatial migration review / approval validation

**Decision: B. NEEDS ANOTHER APPROVAL ITERATION.** The exact review-token contract and disposable atomic publication proof pass. Real Production, State, Knowledge and canonical geometry remain byte-identical. No real approval seal was created; no migration was applied, committed, pushed or deployed.

The remaining blocker is durable integration: normal V6 state/pipeline readers reject the proposed canonical-authority schema, intentionally and safely. The disposable runtime and independent spatial validator work, but routine evidence/progress updates and real future activation need a canonical-authority writer before a real apply session. The future reveal tests below prove slot reuse, not that a normal post-migration activation CLI is complete.

## 1. Architecture and files

Implementation is isolated under [migration-review/](migration-review/). Existing Production, activation CLI, transaction module, preview code and layout generators were not edited.

Added source/documentation: `migration-review/review.py`, `README.md`, `PLAN.md`; runtime templates `runtime/review.js`, `review.css`, `authority-guard.js`; test harnesses `tests/test_review.py`, `crash.py`, `browser.cjs`, `browser_runner.py`; this report. Added generated evidence: `tests/baseline.json`, `integrity.json`, `final-package-check.json`, `future-reveal.json`, `recovery-results.json`, `disposable-apply-results.json`, `browser-results.json`, test/regression/browser logs and 24 PNG screenshots. The exact recursive inventory is [tests/files.json](migration-review/tests/files.json). Every file in that inventory is newly added for this phase. Unapproved development packages created during this iteration were explicitly removed; the final package was created at a new path, never silently overwritten.

Package generation adapts existing preview artifacts once, stages exact proposed State/Production files, then binds their bytes. Approval independently validates those bytes and current source bindings. Apply reads the sealed candidate bytes directly. Neither approval nor apply calls the package adapter, preview constructor or any layout algorithm.

## 2. Exact review package

Final unapproved package: [accepted-v6-to-canonical-a-r3](migration-review/packages/accepted-v6-to-canonical-a-r3/). It contains 39 files, 12,070,084 bytes. Status: `AWAITING_EXPLICIT_HUMAN_REVIEW`.

Contents include `migration-manifest.json`, its canonical preimage `manifest-core.json`, unchanged preview current/target geometry, diff, metrics, comparison, semantic snapshot, preview manifest, semantic-invariance report, transaction plan, review summary, exact canonical master/catalog, `view/`, and staged `candidate/state/` and `candidate/production/`. No unrelated Production files are copied into the review view. The candidate includes the complete assets needed for a coherent disposable release.

Final manifest fingerprint:

```text
9fa257df4fb8b73fc67ba9e83066ae5cfe74af81728e8e666cf5c113d7bed6a5
```

This fingerprint identifies a candidate, not an approval. [final-package-check.json](migration-review/tests/final-package-check.json) independently revalidated the final package against real inputs without invoking approval or publishing anything.

## 3. Bindings and fingerprints

Canonical deterministic encoding reuses the snapshot encoder: sorted object keys, preserved array order, fixed indentation, Unicode and finite-number discipline. SHA256 binds exact artifact bytes; embedded fingerprints bind canonical structured content. No timestamps enter the package or seal.

The manifest binds complete source input and Production inventories; accepted V6 geometry; checkpoint; activation state; Knowledge; ordered accepted entity inventory; ACTIVE_HISTORY identity; Generation; activation history version/events; canonical geometry SHA/fingerprint/schema/algorithm/catalog; one-to-one mapping; exact target positions, context, routes and sectors; diff; metrics; semantic report; transaction plan; review UI; proposed State/Production bytes; validation/runtime implementation fingerprints. Changed implementation requires a new review package/token.

Source accepted geometry fingerprint: `c8467c81b88d8e01351791cee448dc3509b95153bf3eb50bcf2d2f3412a07ec7`.

Source checkpoint: `64c219ed63c6ad34fd42a365f4df91d13d9dd37bbaa54a0197beabf351dc0bd9`.

Source activation state: `a89d0846f57425c48f77c3dc604d29659b966867567b81c078233b39cf53d1fb`.

Source Knowledge semantic fingerprint: `392db9773079c01173bf36d68267fe7f69611027985a7285d06c877ce47e17bb`.

A separate candidate-intent fingerprint binds the source/target contract without creating a circular self-hash. Authority/event records carry that intent identity. The externally reviewed final manifest binds all candidate bytes. Publication also copies the exact reviewed manifest into State as a detached `spatial-migration-review.json` receipt, preserving the full reviewed identity without regenerating it.

## 4. Human review token and stale rejection

The static localhost review page verifies the manifest's raw canonical preimage SHA and every packaged artifact before loading the comparison. It offers Current, Target, Split, Overlay, largest movements, Java/branch/type/entity filters, Project 113 and Stage 617, exact coordinates, counts, displacement metrics and a copyable fingerprint. Source and target, proposed Generation 0→1, dry-run status and lack of approval/apply controls are explicit.

The page verifies package integrity; live source freshness is checked by the approval CLI. Missing token returns `REVIEWED_SPATIAL_FINGERPRINT_REQUIRED`. Wrong/old token, altered artifacts, source changes or bound implementation changes return `STALE_SPATIAL_MIGRATION_PREVIEW`. Extra package files and unknown schemas/fields fail closed. A consistently edited/rehashed package cannot use the old copied token or seal; a dedicated test proves this. A new benign UI candidate is accepted only with its new explicit token and fresh validation.

`approve --reviewed-fingerprint ... --seal ...` produces a new `APPROVED_FOR_APPLY` receipt, outside the package, and refuses overwrite. It does not publish. Hashes/seals are integrity receipts, not cryptographic proof of a human identity. Explicit local operator invocation remains the authorization boundary.

Stale tests cover Production, current accepted geometry, checkpoint, activation state, Knowledge, ACTIVE_HISTORY, Generation, activation history, canonical geometry, target artifact, diff, metrics, manifest and implementation. Fixture packages cannot authorize real sources.

## 5. Exact disposable publication and authority

Disposable apply is restricted to an external root marked `.atlas-disposable-test` with exact content `spatial-migration-tests-v1\n`. The real repository and all its descendants are refused regardless of marker presence. Symlinked roots/assets/markers are rejected. No real apply command exists.

A disposable release publishes six prebuilt State files plus the exact reviewed manifest receipt, and fourteen Production files. It preserves original `model.json` bytes and all Knowledge. The runtime is explicitly branded **DISPOSABLE CANONICAL AUTHORITY**, reusing the refined global UI self-contained. Persisted target bytes equal the reviewed target bytes exactly; published master bytes equal the frozen master. Layout/preview constructors and the candidate adapter are patched to raise during apply tests: publication still succeeds.

Authority schema 1 explicitly binds kind `global-canonical-pyramid`, master schema/algorithm, geometry SHA/fingerprint, catalog fingerprint, intent fingerprint, master asset and slot contract. Checkpoint/state schema 3, activation schema 2 and spatial-history schema 1 are closed contracts. Unknown fields/version fail closed. The runtime guard requires matching State/Production authority and exact accepted coordinates, without V6 fallback. Original preview-relative master reference remains review metadata; runtime follows the explicit packaged authority asset.

Independent installed validation, the existing release byte verifier and browser checks pass. **The old V6 `state.read`/update pipeline does not pass on this new schema; it rejects with `STATE_MIGRATION_REQUIRED`.** This is an explicit integration limitation, not a claim of full post-migration Production support.

## 6. Generation, history and semantic invariance

Reconciled policy: accepted spatial authority materially changes, so disposable `presentation_generation` and accepted layout generation increment exactly once, **0→1**. Activation `history_version` remains **0** and activation events remain unchanged. A separately typed `SPATIAL_AUTHORITY_MIGRATION` event records the authority transition; spatial history version becomes 1. Replay returns `ALREADY_APPLIED`, with no bytes changed, no second event and no additional increment.

ACTIVE_HISTORY remains exactly 46 Categories and 89 Topics in original order. The migration activates nobody. Before/after semantic snapshots and original Knowledge bytes remain identical: 31 learned, 12 verified, Project 113 has 26 requirements, Stage 617 has 12. Course memberships, evidence, relations, Topic metadata and personal state are unchanged; the other ten incomplete Projects retain UNKNOWN requirements. Taxonomy ancestor context is not membership.

Disposable progress/project-only edits leave all slots and Generation unchanged. They invalidate the old migration replay source receipt, as expected. This is a geometry-policy simulation, not a completed global-authority update writer.

All 135 accepted entities map uniquely: Categories to `category:<id>`, Topics to `leaf:<id>`. All 135 move once from V6: median 112,704.84453190821, p95 128,792.22361617956, maximum 231,056.8557864527 world units. This one-time cost is distinct from future zero displacement.

## 7. Future reveal and promotion

After disposable migration, pure authority-bound reserved-slot lookup reveals reference 333, then 334. Across the two reveals, **271 existing complete geometry records compare exactly equal; displacement is 0 px**. Master bytes/records remain unchanged; no placement search occurs. No synthetic facts are written into real Knowledge.

A disposable valid Topic-evidence fixture promotes reference 333 to Topic 333 through existing pure Catalog resolution. Both identities resolve to `leaf:333`; the entire reserved slot record is identical. Simultaneous reference/topic aliases cannot duplicate a physical slot. Existing accepted coordinates and semantic facts remain unchanged. [future-reveal.json](migration-review/tests/future-reveal.json) records the proof. Actual durable activation publication remains a required follow-up.

## 8. Transaction and recovery

Existing exclusive-lock, staging, fsync, durable journal, directory-swap, rollback and recovery infrastructure is reused unchanged. Shared-lock approval verifies live source and exact package; exclusive apply repeats package/seal/source preflight. Knowledge is outside the publication unit. State and Production move together logically under a journal; two directory swaps are not a simultaneous filesystem operation. Journal-aware validators refuse to accept an intermediate state.

Installed exact bytes and unchanged nonspatial inventories are verified after swaps and before durable `COMMITTED`. Before that point, recovery restores old V6 State+Production. After it, recovery retains new canonical State+Production and cleans up. Early hard-crash orphan staging directories are removed without changing visible old inputs. Pending transactions require explicit disposable recovery before validation/replay.

Nine injected exception boundaries roll back exactly. Twelve subprocess hard-crash boundaries pass: candidate construction, approval validation, before/after State staging, after Production staging, before final rename, after State swap, before/after Production swap, before durable commit all recover old coherent bytes; after durable commit and after cleanup retain new coherent bytes. Knowledge stays unchanged at every boundary. [recovery-results.json](migration-review/tests/recovery-results.json).

## 9. Browser and test results

Final approval suite: **15 tests pass, 67.824 seconds**. Includes determinism/byte-identical regeneration, exact manifest/token attacks, stale inputs/runtime, exact apply without regeneration, semantic/counter/history policy, replay, unknown schemas, real-root blocks, future reveal/promotion, exceptions and hard crashes.

Existing Production regression: **9 tests pass**. Global-pyramid suite: **11 tests pass**. Existing preview deterministic check returns `MIGRATION_PREVIEW_READY`. Untouched real Production `update-knowledge-atlas.py --check` passes with browser infrastructure: no apply/state change, Generation 0 and 164 runtime checks.

Final browser QA passes at **1440×900, 1920×1080, 1024×768**. Review package integrity/token verification succeeds. Corrupt target bytes block rendering. No console errors, external requests or horizontal overflow. Search/focus, Stage 617, filters and keyboard Enter/Escape checks pass. 3,645 review entity comparisons plus 405 published entity comparisons give **4,050 exact x/y/width/height tuple comparisons (16,200 scalar equalities)**. No geometry mutation.

Screenshot inventory: for each width 1440, 1920, 1024, `tests/review-WIDTH-{split,java,stage-617,largest-category,largest-topic,vector,token}.png` and `tests/disposable-WIDTH-my-atlas.png`: **24 screenshots**. Representative scenes at every viewport and the 1440 scene set were visually inspected; updated final-token/overview and disposable views were inspected again. Independent split-camera scales clearly show broad canonical spread; overlay limits vectors to five, preserving readability. The exact token remains selectable/copyable. At 1024 and 1440 the sidebar needs vertical scrolling for the token and details. This is usable, but not a simultaneous all-details dashboard.

Browser evidence is [browser-results.json](migration-review/tests/browser-results.json); disposable release/replay evidence is [disposable-apply-results.json](migration-review/tests/disposable-apply-results.json). No separate performance benchmark was required for this approval iteration; prior UX/preview performance findings remain the baseline.

## 10. Protected byte identity

All **30 protected files** retain their exact initial hashes, including complete inventories (added/deleted files would fail). Group SHA256 uses sorted compact JSON of repository-relative path→file-SHA mappings:

| Protected tree | Files | Before = after |
|---|---:|---|
| Production `docs/knowledge-map/` | 14 | `0b1b1f413c13f36689119c7b7115ae4bd963ff67352edfabcc72600ae037ee00` |
| State `state/knowledge-atlas/` | 4 | `7b69371cb87d3dcb880803b9698b90bf09f322152ae8f1867424557a14b22137` |
| Knowledge `data/knowledge/` | 11 | `29a3d477c5aed81e53c2bf551abcb6f41fbbf3b42d71e56a0bc7c813489d35f9` |

Canonical geometry before/after SHA256: `9671e7ca5517c1f35e5ee3affac066362a2470d04ef6251cbe2faa6024572c44`.
Embedded fingerprint before/after: `0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194`.
Bytes before/after: **3,295,568**. Counts stay five roots, 849 Categories, 3,106 leaves, 3,955 positions. [integrity.json](migration-review/tests/integrity.json) contains every before/after file hash.

## 11. Remaining work and recommendation

The approval mechanism is useful and the disposable transaction proof is coherent. Before a real session: promote the canonical runtime/state adapter into durable supported packaging; implement explicit new-schema handling for routine updates and canonical-slot activation; test that writer's semantic/history/generation policies, stale reviews and recovery end-to-end. Keep unknown authority versions fail-closed. Any bound implementation change requires a fresh exact package, human review and new copied fingerprint.

This contract currently targets the captured 135-entity Generation-0 baseline. New taxonomies/inventories require explicit fresh contracts; seals are not identity authentication; static review alone cannot establish live freshness. Neither the fixture marker nor approval receipt enables real publication here.

**Final recommendation: B. NEEDS ANOTHER APPROVAL ITERATION.** No real migration should be performed from this implementation until the durable updater/activation integration is separately completed and reviewed.
