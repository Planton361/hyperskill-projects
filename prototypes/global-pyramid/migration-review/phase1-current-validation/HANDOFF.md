# Real migration review handoff — Phase 1

Validation PASS: real --check/--dry-run; 15 migration-review and 9 durable-authority tests; recovery/reveal/token checks; three-viewport review QA and exact HTTP byte serving.

Package: `/home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-current`
Manifest: `/home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-current/migration-manifest.json`

## Migration manifest fingerprint

f4350c3f9e455091c01481517a50286899699a813f014ca222a35bac793784d3

Target geometry fingerprint: `0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194`
Source Production inventory fingerprint (ordered canonical JSON of relative file SHA map): `cc708761487a92b6f5851284af67854778784608c54509e3dc206fbcd8fa3056`
Source accepted geometry fingerprint: `c8467c81b88d8e01351791cee448dc3509b95153bf3eb50bcf2d2f3412a07ec7`

## Fresh displacement (left/top world units; nearest-rank percentiles)

| Positions | Moved | Unchanged | Median | p95 | p99 | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| category | 46 | 0 | 113445.52817278268 | 227743.30430631764 | 231056.8557864527 | 231056.8557864527 |
| topic | 89 | 0 | 112704.84453190821 | 125956.6987530302 | 227989.64245295356 | 227989.64245295356 |
| all | 135 | 0 | 112704.84453190821 | 128792.22361617956 | 227989.64245295356 | 231056.8557864527 |

All 135/135 map uniquely: 46 Categories, 89 Topics; 0 missing/duplicate slots; every Topic uses leaf:<id>. Semantic tables/ACTIVE_HISTORY unchanged: 31 learned, 12 verified, Project 113 = 26, Stage 617 = 12. Target authority schema/coordinates/routes validated.

Accepted extent: 8892.0 × 1843.1399999999999 (aspect 4.8243757934828615) → 167748 × 44183 (aspect 3.7966638752461352).
Complete target world: 262860 × 44551 (aspect 5.900204260285965).

## Local review

```sh
python -B -m http.server 8765 --bind 127.0.0.1 --directory /home/anton/IdeaProjects/hyperskill-projects/prototypes/global-pyramid/migration-review/real-current
```

Open http://127.0.0.1:8765/view/ . The temporary QA server was stopped; this exact command/path was verified. Scroll the inspector to copy the fingerprint.

Current/Target/Split/Difference Overlay, Java, My Atlas, Project 113, Stage 617, largest movements and selected coordinates passed review QA. Ten 1440px scenes were visually inspected; screenshots at 1920 and 1024 also captured. No UI geometry generation.

Protected inventory: all 30 files and directory inventories byte-identical. Canonical master 3,295,568 bytes, unchanged. Real authority LEGACY, Generation 0, activation history 0. No approval seal created. No real approval/apply command, commit, push or deployment. The existing real apply gate remains closed. No implementation was changed for Phase 1.

**REAL MIGRATION NOT APPLIED**

Visually review Current / Target / Split / Difference Overlay. If you approve this exact candidate, provide the copied migration manifest fingerprint for Phase 2.

Old packages/tokens remain invalid. This candidate is unapproved. Implementation or input changes require another fresh package/review; the copied fingerprint alone does not enable a real apply gate.
