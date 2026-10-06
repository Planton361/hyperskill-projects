# Final real migration review

PASS — READY FOR FINAL HUMAN REVIEW

REAL MIGRATION NOT APPLIED. Authority remains LEGACY; Generation remains 0. No approval, apply, commit, push or deploy was performed.

## Exact candidate

- Package: `prototypes/global-pyramid/migration-review/real-five-root-final-v4`
- Manifest: `prototypes/global-pyramid/migration-review/real-five-root-final-v4/migration-manifest.json`
- Manifest fingerprint: `0b67e3a39fbc5c7f87de6d236dcb9e4463635765b3b0d8a8bb4b452328016c15`
- Canonical geometry fingerprint: `0946f17af8229463757cda209a1307cd86449bfb5b54258d4aa5f14189310d29`
- Geometry file SHA256: `bf79e7309129421b32899900a47f1c9f47d624f2fa16a4eb8b503f1be52aab25`
- Source Production fingerprint: `cc708761487a92b6f5851284af67854778784608c54509e3dc206fbcd8fa3056`
- Source accepted geometry fingerprint: `c8467c81b88d8e01351791cee448dc3509b95153bf3eb50bcf2d2f3412a07ec7`

135/135 uniquely mapped: 46 Categories and 89 Topics; zero missing or duplicate slots. Every Topic maps to leaf:<id>; all target x/y/w/h exactly equal the installed master artifact. Semantic hashes match before/after: 31 learned, 12 verified, Project 113: 26 requirements, Stage 617: 12 requirements.

## Fresh displacement

Native world units, visual rectangle left/top; no alignment or scaling.

| Entities | Moved | Unchanged | Median | p95 | Maximum |
|---|---:|---:|---:|---:|---:|
| Categories | 46 | 0 | 122919.19547715 | 222186.37185156 | 225136.95833204 |
| Topics | 89 | 0 | 122965.30132473 | 133524.51198069 | 222470.12773967 |
| Overall | 135 | 0 | 122947.97111739 | 133548.06765971 | 225136.95833204 |

Source accepted extent: `{"area": 16389200.879999999, "aspect_ratio": 4.8243757934828615, "h": 1843.1399999999999, "height": 1843.1399999999999, "w": 8892.0, "width": 8892.0, "x": -4444.0, "y": 0}`.
Source full V6 bounds: `{"area": 16647420.239999998, "aspect_ratio": 4.775217712651435, "h": 1867.1399999999999, "height": 1867.1399999999999, "w": 8916, "width": 8916, "x": -4460, "y": -8}`.
Target accepted extent: `{"area": 7411609884, "aspect_ratio": 3.7966638752461352, "h": 44183, "height": 44183, "w": 167748, "width": 167748, "x": 50170, "y": 43389}`.
Target full global bounds: `{"area": 38052679200, "aspect_ratio": 4.947502850627138, "h": 87700, "height": 87700, "w": 433896, "width": 433896, "x": 0, "y": 0}`.

## Lean validation

- Four focused tests passed: byte-identical complete package regeneration, exact mapping, manifest/current-source/material validation, all old tokens stale.
- All 5 previous packages reject with STALE_SPATIAL_MIGRATION_PREVIEW, including the immediately previous real-five-root-v3-final token.
- One 1440×900 browser smoke passed: exact package verification, Current/Target/Split/Difference modes, Java, largest Categories/Topics, Project 113 and Stage 617. All six top-level labels asserted and visually inspected in Target Fit Global.
- Legacy real --check: SAFE_TO_APPLY, NO_CHANGE; applied=false, Generation=0. This check is not a migration authorization.
- All 30 protected file inventories are byte-identical, including additions/deletions: Production, State, Knowledge and canonical geometry. See final-v4-validation/protected-before.json and protected-after.json. No pending transaction.

Screenshots:

- [Target global overview](migration-review/final-v4-validation/target-five-root-overview.png)
- [Split overview](migration-review/final-v4-validation/review-1440-split.png)

## Human review

```sh
python -B -m http.server 8000 --bind 127.0.0.1 --directory /home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-five-root-final-v4
```

Open http://127.0.0.1:8000/view/ . Visually review Current / Target / Split / Difference Overlay, then copy the manifest fingerprint for a separately authorized migration phase. No package refresh or geometry regeneration is performed in the browser.

READY FOR FINAL HUMAN REVIEW
