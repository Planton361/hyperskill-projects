# Real spatial migration — Phase 2 validation

**Recommendation: A — MIGRATION FAILED / RECOVERED.**

The migration was refused before publication; no rollback was necessary. The exact
human-approved candidate and current bindings are valid, but the reviewed contract
and implemented operator APIs permit publication only in external disposable roots.
No real apply API exists. The normal canonical writer also rejects real checkouts.
These are concrete implementation blockers, not stale source or missing permission.

The earlier readiness recommendation should have distinguished durable disposable
integration readiness from availability of a real publication operator. This session
does not bypass those gates or change the reviewed implementation. All real
Production/State/Knowledge/canonical-master bytes remain unchanged.

## 1. Approved manifest identity

Path: `prototypes/global-pyramid/migration-review/real-current/migration-manifest.json`.
Human-supplied exact fingerprint:
`f4350c3f9e455091c01481517a50286899699a813f014ca222a35bac793784d3`.
Manifest preimage, entire package inventory and every reviewed byte independently
validate. No target regeneration, replacement preview or manifest refresh occurred.

## 2. Source fingerprints

Production inventory (ordered canonical JSON of relative file SHA map):
`cc708761487a92b6f5851284af67854778784608c54509e3dc206fbcd8fa3056`.
Accepted V6 geometry:
`c8467c81b88d8e01351791cee448dc3509b95153bf3eb50bcf2d2f3412a07ec7`.
Both exactly match the human-approved source. All other input, implementation,
checkpoint, activation, semantic, history and runtime bindings also validate.
Root is `/home/anton/IdeaProjects/hyperskill-projects`; branch is `main`.

## 3. Target canonical fingerprint

`0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194`.
Master byte SHA remains
`9671e7ca5517c1f35e5ee3affac066362a2470d04ef6251cbe2faa6024572c44`;
size remains 3,295,568 bytes. The exact target maps all 135 entities uniquely:
46 Categories and 89 Topics, all Topics using `leaf:<id>` slots.

## 4. Exact command / operator APIs used

The established approval command was invoked, with no implementation modification:

```sh
python -B prototypes/global-pyramid/migration-review/review.py approve \
  --manifest /home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-current/migration-manifest.json \
  --reviewed-fingerprint f4350c3f9e455091c01481517a50286899699a813f014ca222a35bac793784d3 \
  --seal /home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/phase2-real-validation/exact-approval.json
```

Result: `APPROVED_FOR_APPLY`, publication policy **`disposable-only`**. This seal is
outside the exact review package and does not modify its bytes.

Read-only operator preflight `review.disposable(real_root)` returns
`REAL_SPATIAL_MIGRATION_FORBIDDEN`. Normal updater
`canonical.writer_guard(real_root)` returns `REAL_CANONICAL_PUBLICATION_FORBIDDEN`.
No `apply-test` command was misrepresented as a real operator or invoked against
real State; no direct transaction publication/manual copying/monkeypatching was used.

## 5. Transaction result

**NOT STARTED / REFUSED BEFORE PUBLICATION.** No candidate State/Production staging,
swaps or durable commit occurred. The reviewed transaction plan explicitly says
`publication_policy = marked external disposable roots only`. Existing seals require
`disposable-only`; `apply_test` begins by enforcing the real-root refusal.
[Operator guard results](migration-review/phase2-real-validation/operator-gate-results.json).

## 6. Authority before / after

**LEGACY → LEGACY.** No `state/knowledge-atlas/spatial-authority.json` installed.
The prototype master file does not establish installed authority.

## 7. Generation / history / events

Spatial Generation **0 → 0**; activation history **0 → 0**; spatial migration events
**0 → 0**. The reviewed proposed policy remains Generation 0→1 once, activation
history unchanged, separate migration event once. That proposed transition did not
occur in this session.

## 8. ACTIVE_HISTORY

Before/after exact membership remains **46 Categories + 89 Topics**. Existing
activation-state bytes are identical. No geography was activated.

## 9. Semantic invariance

Before/after: 46 Categories, 89 Topics, 31 learned, 12 verified,
Project 113 = 26 required Topics, Stage 617 = 12 required Topics. All Knowledge
files and inventories are byte-identical: memberships, Stage semantics, metadata,
evidence, relations, learned/verified/applied observations are unchanged.

## 10. Exact coordinate verification

Independent package validation proves **135 target/master matches, 0 mismatches,
0 target/master coordinate difference**, including sizes and saved routes. This is
candidate validation, not installed Production validation. Real accepted Production
still uses legacy V6 geometry; all 135 reviewed one-time moves remain unapplied.
The required Production = target = master post-migration condition is unmet.

## 11. Normal updater --check

Fresh real legacy `--check --json`: **PASS**, `SAFE_TO_APPLY`, `applied=false`,
`state_changed=false`, Generation 0. It validates unchanged legacy Production;
it is not evidence of a completed canonical migration.
[Result](migration-review/phase2-real-validation/legacy-check.json).

## 12. Normal updater --dry-run

Fresh real legacy `--dry-run --json`: **PASS**, `SAFE_TO_APPLY`, `applied=false`,
`state_changed=false`, Generation 0.
[Result](migration-review/phase2-real-validation/legacy-dry-run.json).

## 13. Production rebuild determinism

Not performed in Phase 2: real canonical authority was not installed and its writer
is blocked. Real Production was not rebuilt or changed. Disposable determinism was
proven in Phase 1's durable tests, but cannot substitute for successful real apply.

## 14. Canonical reveal dry proof

Post-migration real proof not performed because the repository remains legacy.
Phase 1's nine durable tests prove reserved-slot reveals/reference promotion, two
0-px reveals, metadata refusal, structural extension refusal and recovery in
external disposable roots. No synthetic evidence or new activation entered real
Knowledge during this session.

## 15. Browser QA

No post-migration screenshots were captured: there is no migrated real Production.
Phase 1's exact review browser QA passed three desktop viewports; that evidence
remains candidate-review evidence. No claim of real canonical visual validation is
made here.

## 16. Test-suite matrix

| Check | Phase 2 result |
|---|---|
| Exact manifest / artifact / live-source validation | PASS |
| Exact approval token | PASS; disposable-only seal |
| Real migration operator gate | REFUSED as implemented |
| Normal canonical writer gate | REFUSED as implemented |
| Real legacy updater check / dry-run | PASS / PASS |
| Protected bytes and inventories | PASS, 30/30 unchanged |
| Real canonical apply / rebuild / browser QA | NOT RUN; blocked |
| Final post-migration comprehensive regression | NOT RUN; no migration committed |

No large regression was run against a falsely assumed migrated repository. Phase 1
already reran 15 migration-review and 9 durable/reveal/recovery tests successfully;
those logs remain under `migration-review/phase1-current-validation/`.

## 17. Idempotent second migration

Not run: no first real migration exists. No second event, increment or authoritative
rewrite occurred. The exact approval receipt is valid only under its bound policy.

## 18. Transaction / recovery cleanliness

No pending `state/.knowledge-atlas-transaction.json` before or after; no staging or
swap created by Phase 2, no incomplete transaction to recover. No destructive
rollback or unnecessary writer recovery was invoked. Publication never reached the
commit point.

## 19. Git diff classification

Full pre/post status, stat and name-status are recorded under
`migration-review/phase2-real-validation/`.

A. Intended durable implementation: the same ten tracked script changes predate
Phase 2 (148 additions, 10 deletions); new durable modules/runtime also predate it.
No implementation was edited in Phase 2.

B. Migrated State: **none**; exact four-file legacy inventory unchanged.

C. Migrated Production: **none**; exact fourteen-file legacy inventory unchanged.

D. New Phase 2 artifacts: this report and isolated preflight/status/hash/approval/
guard/check/dry-run evidence under `phase2-real-validation/`. The exact reviewed
package is unchanged; no new migration package was generated.

E. Unrelated pre-existing untracked prototypes: retained; no cleaning, deleting,
resetting, staging or unnecessary edits. No commit, push or deployment occurred.

## 20. Remaining blocker

A real publication operator and a real canonical normal-writer policy still need an
explicit implementation/review phase. Altering `review.py`, the authority writer,
or the manifest's publication contract changes reviewed bindings. The present token
cannot silently authorize that different implementation or policy. A subsequent
implementation would therefore require a fresh exact package and another human
review; no such replacement was generated here.

## 21. Recommendation

**A — MIGRATION FAILED / RECOVERED**: refused before any authoritative write; the
reviewed legacy state remains coherent and unchanged. This is not
`STALE_SPATIAL_MIGRATION_PREVIEW`: all current reviewed bindings still validate.
The exact refusal is `REAL_SPATIAL_MIGRATION_FORBIDDEN`.

**REAL MIGRATION NOT APPLIED.**
