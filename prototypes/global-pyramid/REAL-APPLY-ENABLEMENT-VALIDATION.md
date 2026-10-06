# Real apply enablement validation

## 1. Implementation change

One shared `_apply_exact` in `migration-review/review.py` now serves both the existing
marked disposable API and the explicit real operator. Transaction publication,
staging, journal, swaps, verification and recovery code are unchanged. Exact reviewed
candidate bytes are used; no preview/layout/candidate generation occurs during apply.

Files changed for this iteration:
- `scripts/update-knowledge-atlas.py`: explicit apply/confirmation CLI and structured outcomes.
- `scripts/knowledge_atlas/spatial_authorization.py`: new repository identity/policy helper.
- `scripts/knowledge_atlas/canonical.py`: normal real writer requires strictly restored installed non-fixture receipt; marked non-Git copies retain their prior path.
- `prototypes/global-pyramid/migration-review/review.py`: shared writer, strict real gate, closed seal/publication policy, runtime binding of updater CLI and authorization helpers.
- `prototypes/global-pyramid/migration-review/tests/test_real_authorization.py`: nine focused authorization tests.
- `prototypes/global-pyramid/migration-review/README.md`: current operator/review instructions.
- This report; isolated evidence under `migration-review/real-apply-enablement/`; the new review package below.

The first selected test run also refreshed existing durable test `e2e-results.json`
and `performance.json`; the final focused run suppresses that historical-output hook.
No unrelated prototype files were cleaned, reset, staged or deleted.

## 2. Real authorization requirements

Only `--apply-spatial-migration ABSOLUTE_MANIFEST --reviewed-fingerprint TOKEN
--confirm-real-spatial-migration` enters the real operator. Confirmation must be
explicit; missing/wrong tokens fail closed. Root must equal the operator repository,
be an absolute resolved non-disposable Git checkout on `main`, and pass top-level
and destination-symlink checks. No environment bypass or debug root switch exists.

Manifest must be non-fixture and pass exact package inventory/token/runtime validation.
Source must still be the reviewed LEGACY state, with exact Production, geometry,
State, Knowledge, counters and canonical-master bindings. Pending transactions refuse.
All bindings and real authorization are checked again under exclusive lock immediately
before transaction journal/swaps. Already-installed exact same candidate is verified
and returns `ALREADY_APPLIED`, without another event/increment/write. Plain real
`approve` and `apply-test` refuse. The normal real canonical writer requires a valid
installed, non-fixture migration receipt under this publication policy; prototype
presence alone never permits canonical publication.

## 3. Focused tests

Final pass: **16/16 PASS**, 49.464 seconds: 9 real authorization tests, 4 selected
migration approval tests, 3 selected durable authority tests. Exact apply/replay,
deterministic/non-overwriting packages, missing/wrong and consistently rehashed tokens,
metadata promotion, no allocation/rebuild during exact approval, and real guards pass.
[Final log](migration-review/real-apply-enablement/focused-tests-final.log).
Only one authorized injected failure was run, after State swap: the existing rollback
restored old coherent State/Production and removed the journal. No full crash matrix
or repository-wide regression was rerun; transaction code was not changed.

Real legacy `--check` / `--dry-run`: **SAFE_TO_APPLY**, applied=false, state_changed=false.
An initial launch lacked Playwright configuration and refused read-only; rerunning
with the existing installed browser environment passed. The initial focused pass
found a real/disposable writer dispatch issue, corrected before the final green pass.
A single 1440×900 review smoke passed: exact package verification, Current/Target/Split/
Overlay, 135 mappings, Project 113=26, Stage 617=12, no browser errors. Split screenshot
was visually inspected. No multi-viewport QA or UI redesign.

## 4. Old package stale

Old `real-current` package fails **STALE_SPATIAL_MIGRATION_PREVIEW** due to changed
bound implementation. Its former copied token cannot authorize this implementation.
A dedicated test checks both package inspection and explicit apply dispatch in the
controlled checkout. [Refusal evidence](migration-review/real-apply-enablement/old-package-stale.json).
The old package/approval bytes were retained without refresh.

## 5. Controlled authorized apply

A fresh non-fixture candidate in an isolated `main` Git checkout passed the same real
authorization gate and called the established transaction exactly once. Result:
**APPLIED_SPATIAL_MIGRATION**. All 135 positions and exact candidate bytes validate;
Knowledge is byte-identical, ACTIVE_HISTORY 46/89 unchanged, Generation 0→1,
activation history remains 0 and spatial event occurs once. Identical API and normal
CLI replay: **ALREADY_APPLIED**, with unchanged State/Production bytes. Normal real
canonical writer recognition of the installed receipt also passed in that controlled
checkout. Actual repository real apply was **never invoked**.

## 6. Real authoritative hashes

Exact root-relative filename→SHA256 inventory comparison: **30/30 files unchanged**,
including file additions/deletions. Tree digests below hash compact sorted UTF-8 JSON
of each root-relative inventory; before and after match.

| Protected tree | Files | Before / after SHA256 | Result |
|---|---:|---|---|
| `docs/knowledge-map/` | 14 | `0b1b1f413c13f36689119c7b7115ae4bd963ff67352edfabcc72600ae037ee00` | Identical |
| `state/knowledge-atlas/` | 4 | `7b69371cb87d3dcb880803b9698b90bf09f322152ae8f1867424557a14b22137` | Identical |
| `data/knowledge/` | 11 | `29a3d477c5aed81e53c2bf551abcb6f41fbbf3b42d71e56a0bc7c813489d35f9` | Identical |
| Canonical master | 1 | `9671e7ca5517c1f35e5ee3affac066362a2470d04ef6251cbe2faa6024572c44` | Identical |

[Before](migration-review/real-apply-enablement/protected-before.json) /
[after](migration-review/real-apply-enablement/protected-after.json).
No pending transaction exists; no real authority was installed.

## 7. Fresh package

`/home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-authorized-v2`

Generated once at a new, non-overwriting path from current inputs and implementation.
Status: **AWAITING_EXPLICIT_HUMAN_REVIEW**. Target/master coordinates, alias slots,
routes, source bindings, semantics and package bytes independently validate.
No approval seal was created for this real package. Build ~4118.20 ms;
diff computation ~33.42 ms.

## 8. Fresh manifest

`/home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-authorized-v2/migration-manifest.json`

## 9. NEW manifest fingerprint

`7c79c8447b61bfeebca06bc17ab0792841c8c66eb22b568de8c93a3aba1247a2`

## 10. Canonical geometry fingerprint

`0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194`

## 11. Source Production fingerprint

`cc708761487a92b6f5851284af67854778784608c54509e3dc206fbcd8fa3056`

Source accepted geometry: `c8467c81b88d8e01351791cee448dc3509b95153bf3eb50bcf2d2f3412a07ec7`.

## 12. Fresh migration metrics

135/135 unique mappings: 46 Categories, 89 Topics; all Topics use `leaf:<id>`;
0 missing, 0 duplicate slots. Semantics: 31 learned, 12 verified,
Project 113=26, Stage 617=12, identical semantic hashes before/after.
Left/top displacement in original world units; percentiles use nearest rank.

| Kind | Count | Moved | Unchanged | Min | Mean | Median | p95 | p99 | Max | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 135 | 135 | 0 | 77630.48768338378 | 113627.47179021106 | 112704.84453190821 | 128792.22361617956 | 227989.64245295356 | 231056.8557864527 | 15339708.691678492 |
| category | 46 | 46 | 0 | 77630.48768338378 | 115425.3994236917 | 113445.52817278268 | 227743.30430631764 | 231056.8557864527 | 231056.8557864527 | 5309568.373489819 |
| topic | 89 | 89 | 0 | 78008.44675614046 | 112698.20582234465 | 112704.84453190821 | 125956.6987530302 | 227989.64245295356 | 227989.64245295356 | 10030140.318188675 |

Current world: 8,916 × 1,867.14; area 16,647,420.24; aspect 4.775217712651435.
Target full world: 262,860 × 44,551; area 11,710,675,860; aspect 5.900204260285965.
Accepted scope extent: 8,892 × 1,843.14 → 167,748 × 44,183;
aspect 4.8243757934828615 → 3.7966638752461352.
[Exact metrics and critical validation](migration-review/real-apply-enablement/fresh-package-validation.json).

## 13. Local review

```sh
python -B -m http.server 8000 --bind 127.0.0.1 --directory /home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-authorized-v2
```

Open **http://127.0.0.1:8000/view/**. Visually review Current / Target / Split /
Difference Overlay, Java, largest Categories/Topics, Project 113, Stage 617 and
selected current/target coordinates. Copy this package's displayed manifest fingerprint.
[Screenshot](migration-review/real-apply-enablement/review-1440-split.png) /
[browser result](migration-review/real-apply-enablement/browser-smoke.json).

## 14. Real repository unchanged

Authority **LEGACY**, Generation **0**, activation history **0**, ACTIVE_HISTORY
**46 Categories / 89 Topics**. Production, State, Knowledge and canonical master
remain byte-identical. No fresh real approval, real apply, activation, commit, push
or deployment occurred. **REAL MIGRATION NOT APPLIED.**

## 15. Recommendation

**C — READY FOR HUMAN REVIEW.** Fresh token required; implementation enablement
is not approval of this candidate. Stop here. An actual migration requires a later
explicitly authorized human-review/apply session.
