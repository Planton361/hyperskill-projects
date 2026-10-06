# Five-root real migration review

**Validation: PASS. Recommendation: READY FOR HUMAN REVIEW.**

Fresh package: `/home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-five-root-v3-final`

Manifest: `/home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-five-root-v3-final/migration-manifest.json`

**NEW manifest fingerprint**
```
658998a4f9cf2b9d44fd308e210af9e7b6a40d26f05556d340e1b94cd2a1b993
```

Canonical geometry fingerprint:
`0946f17af8229463757cda209a1307cd86449bfb5b54258d4aa5f14189310d29`

Source Production fingerprint:
`cc708761487a92b6f5851284af67854778784608c54509e3dc206fbcd8fa3056`

Source accepted-geometry fingerprint:
`c8467c81b88d8e01351791cee448dc3509b95153bf3eb50bcf2d2f3412a07ec7`

## Mapping and fresh movement

135/135 uniquely mapped: 46 Categories, 89 Topics; 0 missing, 0 duplicate slots.
Every Topic uses `leaf:<id>`; all coordinates/sizes/routes and five root sectors
match the approved A2 master exactly. Semantics unchanged: 31 learned, 12 verified,
Project 113=26 requirements, Stage 617=12. Manifest binds current source State,
Knowledge, ACTIVE_HISTORY, counters, target, mapping, diff, metrics, semantics,
transaction plan and real-apply-capable implementation/runtime.

Recomputed left/top displacement in original world units; nearest-rank percentiles:

| Entities | Moved / unchanged | Median | p95 | Maximum |
|---|---:|---:|---:|---:|
| category | 46 / 0 | 122919.19547715 | 222186.37185156 | 225136.95833204 |
| topic | 89 / 0 | 122965.30132473 | 133524.51198069 | 222470.12773967 |
| all | 135 / 0 | 122947.97111739 | 133548.06765971 | 225136.95833204 |

Old accepted bounds `(x, y, width, height)`:
`(-4444.0, 0, 8892.0, 1843.14)`.
New accepted bounds:
`(50170, 43389, 167748, 44183)`.
Accepted aspect ratio **4.824375793483 → 3.796663875246**.
Current full V6 bounds remain `(-4460, -8, 8916, 1867.14)`;
new full world bounds are `(0, 0, 433896, 87700)`.
[Exact metrics](migration-review/real-five-root-v3-final/migration-metrics.json).

## Lean validation / safety

- Four focused tests PASS, 4.044 seconds: byte-identical full package regeneration
  in disposable temporary output, exact mappings, manifest/source/material checks,
  and stale old token rejection. [Log](migration-review/five-root-v3-validation/tests-final.log).
- Previous `real-authorized-v2` token/package returns
  **STALE_SPATIAL_MIGRATION_PREVIEW**. No old manifest/token was reused.
- One 1440×900 smoke on the final review page: Current/Target/Split/Overlay,
  Java branch, largest Category/Topic filters, Project/Stage counts; no browser errors.
  [Target overview](migration-review/five-root-v3-validation/target-five-root-overview.png) /
  [Split](migration-review/five-root-v3-validation/review-1440-split.png), both inspected.
- Real legacy `--check`: **SAFE_TO_APPLY**, applied=false, state_changed=false.
- **30/30 protected files/inventories byte-identical**, including canonical master
  SHA256 `bf79e7309129421b32899900a47f1c9f47d624f2fa16a4eb8b503f1be52aab25`.
  [Before](migration-review/five-root-v3-validation/protected-before.json) /
  [after](migration-review/five-root-v3-validation/protected-after.json).

Minimal compatibility changes: preview pins the explicitly approved A2 master SHA;
the existing strict authority reader adds the declared A2 algorithm to its allowlist
while retaining A1; review labels preserve the aligned sibling baseline/apex, and
minimap captions read the bound world width. No layout regeneration or new updater.
An intermediate `real-five-root-v3` package revealed the stale hardcoded minimap
caption during inspection; it was retained untouched and is now stale. Only
**`real-five-root-v3-final`** is the current review candidate. Historical packages
were not overwritten. No broad suite, crash matrix or multi-viewport QA.

## Local human review

```sh
python -B -m http.server 8000 --bind 127.0.0.1 --directory /home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-five-root-v3-final
```

Open **http://127.0.0.1:8000/view/**. Inspect Current / Target / Split / Difference
Overlay. Use **Fit global reference** in Target to see the aligned five-root world;
review Java, Project 113, Stage 617, largest movements and individual coordinates.
Copy the displayed fingerprint only after reviewing this exact package.

Actual authority **LEGACY**; actual Generation **0**; ACTIVE_HISTORY remains
46 Categories / 89 Topics; no pending transaction. No real approval/apply, authority
installation, Production/State/Knowledge write, commit, push or deployment.

**REAL MIGRATION NOT APPLIED.**

**READY FOR HUMAN REVIEW**
