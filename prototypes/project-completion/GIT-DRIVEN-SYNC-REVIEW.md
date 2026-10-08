# Git-driven Project completion sync review

**C — GIT-DRIVEN SYNC READY FOR INTEGRATION**

Technical validation completed 2026-10-08. HARD STOP. No commit, push, deployment, Production write, or live Hyperskill request occurred in the working repository. Git commits used by tests exist only in disposable fixture repositories.

## Preserved foundation

HEAD remains `4c14b8a6b41f6f6d22674d90d26e6333cc2af23f`. All three local commits ahead of `origin/main` were inspected and retained: `a99777d` (complete relations), `6c1934c` (unified application), and `4c14b8a` (personal tree). Existing uncommitted analytics/completion work and unrelated changes were retained.

The new serializer calls the existing `progress-analytics.js` implementation. It does not implement another learned/verified algorithm. No accepted UI, Inspector design, geometry, personal progress semantics, or historical observations were changed during this milestone.

## Recognized inventory and exact identity

| Export | Exact identity evidence | Requirements | Effective contribution |
| --- | --- | --- | --- |
| `java/Simple Chat Bot with Java` | Exact `https://hyperskill.org/projects/113` URL and reviewed completion statement in README; validated schema-2 import manifest | 26 explicit Topic IDs | 26 project-based attestations; all 26 already directly learned |

Completed portfolio IDs: `[113]`; completed count: **1**. Global effective learned: **31 / 3106**. Explicitly verified: **12**. Direct learned: **31**. Project-based learned: **26**. Both sources: **26**. Project-only learned: **0**.

Exact Project 113 requirements:

```json
[9,14,15,25,27,30,31,36,87,88,89,112,113,146,147,148,152,193,259,260,307,348,1248,1476,1761,3538]
```

The legacy observation date remains the previously reviewed `2026-10-08T00:00:00Z`; it denotes review-date precision, not the original completion time. No title matching is used.

## Completion contract and discovery

The current importer supports Java, so discovery is restricted to `java/<export>/.hyperskill-import.json`. Supporting another language requires its reviewed export validator and workflow path, rather than treating arbitrary source directories as exports.

New imports carry a stable top-level `project_id` and this explicit attestation:

```json
{
  "project_id": 113,
  "completion": {
    "project_id": 113,
    "status": "completed",
    "attested_by": "owner",
    "observed_at": "2026-10-08T12:00:00Z"
  }
}
```

The importer creates it only with `--project-url` and `--completed-at`. Previous attestation-only metadata remains supported; a top-level ID, when present, must agree. Exact README Project URLs must agree too. Positive integer IDs must exist in the committed Atlas scope catalog. Completion dates, owner identity, and status are explicit. Metadata also requires schema 2, matching language/directory, standalone Java build/wrapper/source inventory and matching SHA-256 hashes for every manifest member.

Missing attestation is ignored except for the specific reviewed legacy 113 rule. Incomplete/tampered exports, unsafe paths, symlinks, malformed metadata, conflicting IDs, absent catalog Projects, and contradictory duplicate completion statuses fail validation. Identical Project IDs are counted once; multiple completed exports select the latest observation with repository-path tie-breaking. The source ledger retains the committed export blobs used during discovery. Explicit `status: "revoked"` is supported for removal of current completion evidence; it requires the same identity/owner/date contract. An explicit revocation overrides the legacy fallback.

The Git reader resolves a commit and reads its tree/blob objects. Untracked files, staged changes, dirty source files, browser state and local workspace contents cannot establish completion. Missing committed manifest members fail even if a matching file exists locally. No checkout, reset, rebase or index update is used.

## Public projection and differential updates

Entry point:

```sh
python3 -B scripts/sync-project-completion.py
```

It writes JSON to stdout only. `--ref` selects a committed revision. By default, comparison uses committed `prototypes/project-completion/accepted-sync.json`, falling back to the committed legacy `progress.json`. With neither present, output explicitly reports a bootstrap with no accepted baseline. `--previous PATH` supports a deliberate local review against a saved accepted projection or full artifact.

The [public JSON example](public-sync-example.json) reads actual Project/catalog evidence from HEAD and compares against the existing local accepted legacy `progress.json`. That legacy baseline is still uncommitted, as it was at milestone entry. The baseline hash is recorded. The effective totals are independently reconstructible from committed export/catalog evidence; the differential also needs the indicated accepted baseline. Implementation hashes identify the currently uncommitted scanner/serializer/aggregation code for later reproducibility.

The artifact contains completed IDs/count, effective/direct/project learned IDs, verified IDs, per-Topic direct/project/both provenance and dated observations, per-Project requirement/contribution summaries, global totals, all Course/Project/Stage/Category coverage, source commit, repository-relative evidence paths, Git blob IDs and SHA-256 hashes. Only explicit public projection fields are serialized; raw source contents, credentials, machine paths and browser data are not included. My Skill Tree receives the same effective learned IDs through the accepted aggregation contract; this milestone does not modify its UI or model.

The real example reports no newly completed Projects, no newly learned Topics, no provenance changes and no impacted scopes against the accepted foundation. Repetition produces identical bytes. Sorting and serialization are deterministic; object key order in the accepted baseline does not produce false changes. Commit/evidence hash changes alone do not count as semantic progress changes.

The [disposable differential example](differential-example.json) starts with Topic 1 directly learned and verified, then adds synthetic Projects 7 and 8 with requirements `[1,2]` and `[2,3]`. It reports newly completed `[7,8]`, newly learned `[2,3]`, already learned `[1]`, effective total **3**, verified total **1**, and affected scopes. The example is prominently marked validation-only and is not real owner evidence.

On export removal or revocation, the diff explicitly reports removed/revoked Projects, changed provenance, and any Topics no longer effectively learned. A remaining direct observation or another completed Project preserves learning. Verification remains independent. UNKNOWN requirements add no Topics; known-empty requirements contribute zero. Official Hyperskill Course snapshots are neither recalculated nor rewritten.

## GitHub Actions prototype

`.github/workflows/project-completion-review.yml` responds to pushes affecting supported exports and relevant inputs, plus manual dispatch. It checks out committed evidence, uses Python and Node, runs the Git-only scanner and existing analytics, generates JSON and a readable change summary, and uploads both as review artifacts. Permissions are `contents: read`. There is no automatic commit, branch update, projection replacement, Pages action, or Production writer.

[Actions dry-run result](actions-dry-run.json): **PASS**. The workflow's exact scan and summary shell commands ran in a disposable committed checkout containing the real export/catalog and current implementation. Two executions produced identical JSON bytes and the expected 1 completed Project / 31 learned / 12 verified / no semantic changes. Hosted Actions execution and GitHub artifact upload were not performed because this milestone forbids pushing.

## Validation and protection

- **8 completion tests passed:** legacy 113, new learning, overlap, duplicate Projects, repeated scans, dirty-file isolation, incomplete/missing/tampered exports, missing/ambiguous IDs, catalog absence, symlinks, contradictory duplicates, UNKNOWN/empty requirements, revocation/removal, independent evidence preservation, and fresh-clone reproducibility.
- **17 importer tests passed**, including explicit attestation output and required re-attestation; tests used canonical macOS temporary paths.
- Existing completion propagation tests passed across all 52 Courses, 391 Projects, 1,967 Stages and 849 Categories, including unchanged verification/official progress and tree growth.
- Browser regression passed all seven existing check groups with no page errors or external requests. Test screenshots/results were redirected outside the frozen prototype directories.
- **15 Production guard tests passed.** The real read-only Production guard reports **PASS**, exact Production/state/historical Knowledge inventory, unchanged active semantics, unchanged history/generation, and unchanged Global reference.
- **496 protected files are byte-identical** to milestone entry, with no added files under the protected roots. This includes accepted Global/personal/scope prototypes and their existing analytics files, historical Knowledge, Production, and `state/knowledge-atlas/`.
- `git diff --check` passed. All three existing local commits remain intact.

[Protection results and browser fingerprints](protection-results.json):

| View | Unchanged SHA-256 geometry fingerprint |
| --- | --- |
| Global | `1306993ec8a1b7a80edda4f620fb96ba5d4803c0d81ded334b92efa85cdf1174` |
| My Skill Tree | `a60fc22e272079c91f39cfed9c01af5865bae29120e6d6f7801b02da96cd6348` |
| Course 8 | `ab8e05971ca8fb9d077b491a766554f5b84118e068433afe4c17faa7e91fb89b` |
| Project 113 | `33dc51873bcbd33fa6ad2de854dd719e525706bdb764a50578570d1f73e89034` |
| Stage 617 | `24edf473c9e97b7ccbb287464302a4bbf6ffadff33efdc265076b5ae6b51455e` |

Production fingerprint: `36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`.

## Remaining Pages integration

A later authorized integration must preserve and commit the accepted local foundation together with the new tooling, review and save a schema-2 accepted baseline, run the hosted workflow, and inspect its uploaded artifact. The consumer/packaging step must deliberately select the reviewed projection and use the existing analytics contract while retaining separate official Course progress and Production guards. A separate release decision is needed before any Pages packaging/publication. This prototype intentionally does not wire its candidate artifact into current Production or create an automated publication/commit loop.

Technical work is complete and stopped at the requested boundary.
