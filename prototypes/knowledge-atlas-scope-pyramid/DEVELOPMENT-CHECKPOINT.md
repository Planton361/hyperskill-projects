# Unified V6.6 development checkpoint

Local-only checkpoint of the completed dormant Catalog and accepted Unified Atlas application. No new feature, UI polish, acquisition, Production integration, push or deployment is authorized by this checkpoint.

## Status

UNIFIED_ATLAS_V66_TECHNICALLY_READY

TWO_TAB_NAVIGATION_ACCEPTED

SCOPE_PYRAMID_LAYOUT_ACCEPTED

FULL_TITLE_GLOBAL_HUMAN_ACCEPTANCE_PENDING

MY_SKILL_TREE_FINAL_REVIEW_PENDING

PRODUCTION_INTEGRATION_NOT_STARTED

## Catalog and evidence

| Inventory | Count |
|---|---:|
| Global Categories / titled Topics / unresolved | 849 / 3,106 / 0 |
| Courses / Projects / Stages | 52 / 391 / 1,967 |
| Course → Topic / Course → Category | 8,195 / 3,960 |
| Project study-plan Topics / Stage-local Topics | 28,480 / 28,865 |
| Course → Project associations / distinct Project targets | 867 / 299 |
| Complete Course association inventories | 52 |
| Nonempty / known-empty / UNKNOWN Course association inventories | 48 / 4 / 0 |
| Known / UNKNOWN Project requirement scopes | 375 / 16 |
| Explicit-empty Projects, included in known owners | 5 |
| Known Stage sets / explicit-empty Stage sets | 1,967 / 328 |
| UNKNOWN Project entry-prerequisite ID sets | 391 |
| Explicit learned / verified Topics | 31 / 12 |

Course association empty owners are 31, 41, 57 and 60. UNKNOWN remains distinct from empty. Stage.all_prerequisites remains opaque source evidence; numeric Project counters never become member-ID lists. Project study-plan unions remain qualified by the source-established UI contract, not invented entry prerequisites.

Immutable typed observations:

- `scope-relations-2026-10-07-e691c7ed0be7.json`: SHA-256 `e691c7ed0be7b8ac124a1a139ede097cc8040f1212f29ad2ff4da9129ec647f6`; reviewed candidate manifest-inventory digest `3edd24dfffb842033ba1166dd75fca38804eb65dd3cf5c96859d39e7c56be43f`.
- `course-project-associations-2026-10-07-308e07fe07bc.json`: SHA-256 `308e07fe07bc3077cab5560f84e51a451d1a1b6cfdc9a6411c1648676f7bc45a`; reviewed candidate manifest-inventory digest `9d60f781ca8762e818033bf0fb50ea8b36c3796d3afe4cc3191ec43da9cee360`. Native complete relation: `/api/tracks/<id>` → `tracks[].projects`.

Original source timestamps, safe endpoints, sanitizer/schema versions and sanitized source digests remain inside the observations. No raw responses, headers or browser material are copied. The composed `scope-index.json` is a deterministic typed-Catalog export joined to these observations; it is not a separate maintained entity database. Existing Global metadata remains the sole Topic/Category source.

Exact fixture sets are checked by the focused data tests: Course 8 has 89 Topics, 46 Categories and its original 11 Project IDs; Course 2 has 43 Projects and Course 3 has 36. Project 113 has 26 study-plan Topics; Stage 617 has 12 stage-local Topics. Project 380 has the exact 15 study-plan IDs, independent numeric counter 12 and UNKNOWN entry-prerequisite IDs.

The authoritative [RELATION-DISCOVERY.md](RELATION-DISCOVERY.md) and [RELATION-EXCEPTION-REVIEW.md](RELATION-EXCEPTION-REVIEW.md) preserve source semantics. Superseded local UX/ingestion reports and excess historical captures are retained locally, outside this focused checkpoint. Historical tracked acceptance reports are unchanged.

## Reproduction and current review

Canonical preview: <http://127.0.0.1:8813/prototypes/knowledge-atlas-navigation/index.html?view=atlas>.

Serve a clean checkout from its root with `python3 -B -m http.server 8813 --bind 127.0.0.1`. No acquisition workspace, profile, npm runtime, source regeneration or external API request is needed. All three renderers, runtime model JSON, scope index, shared shell, worker, D3 assets and license are versioned.

The accepted shell resolves Global / Course / Project / Stage through one Atlas tab; My Skill Tree is separate. The fixed filters, grouped search, default-closed overlay Inspector, explicit Pin, Reset to Global, exact Show in Global and Back/Forward behavior remain frozen. See [CURRENT-STATUS.md](CURRENT-STATUS.md), [UNIFIED-ATLAS-SCOPE-REVIEW.md](UNIFIED-ATLAS-SCOPE-REVIEW.md) and [FINAL-UI-CHROME-REVIEW.md](FINAL-UI-CHROME-REVIEW.md). Only the final six chrome comparison captures are added as review images.

Optional browser tooling is declared in `scripts/knowledge_atlas/package.json` and its lockfile; it is used for validation only. Historical standalone scripts that assumed direct ScopeApp access are not this shell's test entrypoint.

## Focused verification

**PASS** — isolated staged-tree reproduction from 58 explicitly reviewed changed/new files, exported with `git checkout-index` into a separate directory. The repository-only tree was served on an independent localhost port. Acquisition/profile directories and unrelated untracked/ignored files were absent. Playwright and Chrome were external validation tools only; the application made zero external requests and required no external runtime assets.

Verified Global with all 849 / 3,106 entities; Course 8; Course 2; Project 113; Stage 617; My Skill Tree; the Course→Project→Stage cascade; Global→My Skill Tree→Atlas with retained scope; actual Inspector Show in Global for Topic 36; Back/Forward restoring the local scope/Topic; legacy exact Category and scope routes; UNKNOWN/empty states; overlay/Pin; search/keyboard and two persistent tabs. Six actual world-geometry fingerprints match the accepted contract. Local source fingerprints for layout/projection/routing/worker/style also match the frozen fixture.

Focused data validation verified all 29 contracts: the initial run passed 28, and its one outdated Global-observation fixture was corrected to select by type and re-run successfully. This test-only fix removes an ordering assumption introduced by the two additive observation types; no verifier/application semantics changed. Positive allowlists, exact joins/provenance, normalized counts, exact fixture sets, immutable replay/conflict rejection, UNKNOWN/empty preservation and invalid-observation/active-semantic negative cases pass.

`tests/ux-model.cjs` and `tests/final-chrome.cjs` pass in the isolated checkout. `python3 -B scripts/check-adaptive-production.py` passes there and in the working repository, with exact Production/State/historical Knowledge inventories, unchanged active semantic hashes and Production fingerprint:

`36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`

Historical apply-manifest bytes match the original Git version. Preflight byte inventories for existing Knowledge, State, Production and all runtime/layout files remain exact; only checkpoint documentation and the test-fixture correction were newly written. `git diff --check` passes.

Intended/staged security audit: **PASS**. No credential values, JWTs, private email/account identifiers, authenticated URLs, raw HAR/header data or private user filesystem paths were found. Four pattern hits are explicitly reviewed rejection-regex literals and a deliberately invalid synthetic path in a negative test. Review PNGs contain only the local catalog/progress UI. The two observation schemas independently reject sensitive fields and values.

Logical local commits preserve 13 data/typed-loader/test/export files, 31 application/chrome/report/review files, and 14 personal-prototype dependency files. Before each commit, exact staged names and bytes are compared with the reviewed path inventory. Only six final chrome screenshots are added. Excluded local work remains untouched: adaptive-preview/release artifacts, superseded UX/ingestion reports and captures, old standalone audit scripts/results, personal historical screenshots/checkpoint output, all caches/dependencies and every outside-Git acquisition/browser/profile artifact.

No push or deployment. No broad historical migration/layout suite or new performance/design work. Final human acceptance for Global and My Skill Tree remains pending.
