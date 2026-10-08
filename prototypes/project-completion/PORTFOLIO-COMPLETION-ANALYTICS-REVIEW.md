# V6.6 Portfolio Completion Analytics Review

**C — PORTFOLIO COMPLETION ANALYTICS READY**

Focused enhancement implemented in maintained development sources and rebuilt into the isolated V6.6 candidate. No commit, push, deployment, Pages configuration change, live Hyperskill access, or original Production mutation.

## Current evidence and displayed metrics

| Dimension | Current display | Meaning |
| --- | --- | --- |
| Topics learned | 31 / 3,106 | Exact-ID union of direct learning and explicit requirements of confirmed completed Projects |
| Topics verified | 12 | Independent explicit verification evidence |
| Projects completed | 1 confirmed completed Project; 391 catalog Projects | Unique scanner-confirmed Project IDs: `[113]` |
| Courses completed | Course completions not yet recorded; 52 catalog Courses | No existing Course completion evidence; JSON count is `null`, not zero |

Project 113 is **Simple Chat Bot with Java**, mapped through its exact Hyperskill Project URL in `java/Simple Chat Bot with Java/README.md` and the reviewed legacy completion evidence. Its 26 distinct requirement Topic attestations remain separate provenance; the effective learned union remains 31. No title matching, incomplete-export counting, or global duplication by Course membership was introduced. Completion evidence is displayed with its source and observation timestamp `2026-10-08T00:00:00Z`.

The 391 and 52 denominators are catalog inventories. They do not represent an enrolled plan or official overall Hyperskill completion. Knowledge coverage, portfolio completion, and officially observed Course progress remain separate.

## Per-Course associated Project completion

The numerator is the intersection of unique confirmed completed Project IDs and the Course's explicitly associated Project IDs. The denominator is the unique explicit associated Project inventory. Project 113 contributes to these nine Courses while counting once globally:

| Course ID | Course | Confirmed completed / associated Projects |
| --- | --- | --- |
| 8 | Introduction to Java | 1 / 11 |
| 9 | Java Desktop Application Developer | 1 / 42 |
| 12 | Java Backend Developer (Spring Boot) | 1 / 49 |
| 15 | Java Core | 1 / 42 |
| 17 | Java Developer | 1 / 42 |
| 35 | Advanced Java | 1 / 17 |
| 38 | Spring Security for Java Backend Developers | 1 / 31 |
| 39 | Java Full Stack Developer | 1 / 28 |
| 70 | Introduction to Spring Boot with Java | 1 / 17 |

The other 43 Courses have no confirmed completed associated Projects. Courses 31, 41, 57, and 60 have explicitly empty Project inventories and display **No associated Projects**. Unknown inventories display **Project associations not recorded** with no invented denominator. The complete 52-Course inventory, including exact membership evidence IDs, is in [portfolio-results.json](portfolio-results.json).

All Course completion indicators currently display **Not recorded**. Project 113 displays **Completed (evidenced)**. Stage 617 displays **Not recorded**, independently of its 12 / 12 Topic coverage. An active Project record does not establish an explicit negative completion observation.

## Course completion evidence contract

New source file: [course-completions.json](course-completions.json), currently `{"schema":1,"records":[]}`.

Future records must contain exactly these fields; this example is **validation-only**, not an actual completion:

```json
{
  "schema": 1,
  "records": [{
    "course_id": 8,
    "is_completed": true,
    "observed_at": "2026-10-08T14:00:00Z",
    "source": "owner",
    "evidence_id": "course-8-example"
  }]
}
```

The validator requires an integer exact catalog Course ID, a boolean, a valid full UTC timestamp, source `owner` or `hyperskill`, and a unique public-safe evidence ID. Extra fields, unknown IDs, ambiguous boolean IDs, malformed dates, inferred sources, and private-path evidence IDs are rejected. No network access is needed; `hyperskill` identifies a directly observed historical record.

The Git scanner reads this file from committed source evidence and includes its Git blob and SHA-256 references. Uncommitted attestations are not published by the Git scanner. Maintained local prototype previews read the separate source file; the release uses its validated embedded `course_completion` projection. Records serialize deterministically. A newer explicit false record can revoke completion without deleting historical evidence or independent Topic evidence. Conflicting latest observations cannot confirm completion. Project and Stage completion indicators consume only explicit completion records; Stage completion is never inferred from Project exports.

Learning all Course Topics, completing one or every associated Project, and requirement coverage cannot create a Course completion record. A fixture with all Course 8 Topics learned still reports Course completion **Not recorded**.

## New Project updates and deterministic projection

The accepted scanner and learning aggregator remain authoritative. The public projection adds `portfolio`, `course_completion`, and `course_project_completion`; it retains direct/project/both Topic provenance and independent verification. The human-readable summary now reports portfolio totals and truthful unrecorded Course state. Differential summaries also identify changes to Course Project counts and explicit Course records, including known-empty/UNKNOWN Project cases without invented learned Topics.

[Public projection example](portfolio-public-example.json) records source commit `a3c31daaa4ea974f8d6afe1b6ef4bf2202e69553` and reviewed implementation hashes. The example wraps the projection and change report; the deployed-candidate boundary is `/hyperskill-projects/knowledge-map/progress.json`, which serves the projection object itself. [Readable sync summary](portfolio-sync-summary.md) reports no semantic changes on current evidence.

[Disposable Project 380 differential example](portfolio-differential-example.json):

- Confirmed completed Projects: 1 → 2, IDs `[113,380]`.
- Effective learned Topics: 31 → 32; newly learned exact Topic ID `518`.
- Verified Topics: unchanged at 12.
- Course 8 associated Projects: 1 / 11 → 2 / 11; the other eight exact associated Course counts update too.
- Course completions remain unrecorded; no Course is automatically completed.

A browser fixture replaced only the JSON response, with no application edits, and showed these updated counters and learning coverage. An independent Course 8 attestation fixture showed one confirmed Course completion while knowledge remained 31 learned / 12 verified and Project count remained one. No fixture was written as live portfolio evidence.

## UI before and after

The existing overlay and progress panel are retained. Three compact metrics replace the single Topic-only overview; the small Topic knowledge bar remains. Course cards add an associated-Project count and small independent bar. Existing Project/Stage knowledge cards add a separate completion indicator. Completed Project names, exact IDs, source, and date are available in compact expandable evidence sections.

No new cards outside the existing progress panel, navigation, map renderer, shell, or geometry were added. Search, Category Inspector, overlay / Pin / Close, selectors, and two tabs remain usable. The narrow overview wraps and the panel scrolls.

| View | Before | After |
| --- | --- | --- |
| Compact overview | [Capture](portfolio-review/before-overview.png) | [Capture](portfolio-review/after-overview.png) |
| Progress panel | [Capture](portfolio-review/before-panel.png) | [Capture](portfolio-review/after-panel.png) |
| Narrow 390px panel | — | [Capture](portfolio-review/narrow-panel.png) |

Captures were visually inspected. No broad historical screenshot matrix was repeated.

## Focused validation

| Check | Result |
| --- | --- |
| Existing analytics aggregation | 17 focused checks PASS |
| Universal scope and Category Inspector aggregation/presentation | Eight check groups PASS across 52 Courses, 391 Projects, 1,967 Stages, and 849 Categories |
| Existing completion-learning union / overlap / provenance / UNKNOWN / empty / verification / Skill Tree growth | PASS |
| Repository discovery and committed evidence | Nine Python tests PASS, including incomplete/ambiguous exports, duplicates, revocation, legacy 113, clean disposable clone reproduction, and committed Course attestation |
| Strict Course record validation | Two Python tests PASS, including invalid identities, dates, sources, and public evidence IDs |
| Portfolio metrics and exact Course association fixtures | PASS: global uniqueness, duplicate memberships, empty inventories, independent Topic/verification, all-learned Course still unrecorded, explicit Course fixture and later false evidence |
| Focused candidate browser checks | Five groups PASS; zero errors, failed requests, or external requests |
| Search / Category Inspector / Pin / Close and completion controls | PASS; same personal layout object, zero new layout builds |
| Synthetic JSON-only new Project / explicit Course updates | PASS |
| Repeated Git scan | Byte-identical JSON; no semantic changes |
| Repeated isolated candidate rebuild | All 69 files byte-identical |
| Candidate sources | All 48 packaged source asset hashes match maintained source files; public JSON equals current reproducible scanner projection |
| Workflow | YAML parsed; `contents: read`, push / dispatch triggers, review-only steps; actual JSON and summary commands PASS locally |
| Focused security review | No credential/private-path patterns in reviewed sources/public JSON; strict records, escaped UI evidence, no new runtime external network client |
| Existing Production guard / diff whitespace | PASS |

Evidence: [browser results](portfolio-browser-results.json), [portfolio results](portfolio-results.json), [rebuild inventory](portfolio-candidate-reproduction.json), [protection results](portfolio-protection-results.json).

## Geometry and Production protection

All five accepted fingerprints remain identical at 1440 × 1000:

| View | Geometry fingerprint | Result |
| --- | --- | --- |
| personal | `a60fc22e272079c91f39cfed9c01af5865bae29120e6d6f7801b02da96cd6348` | PASS |
| global | `1306993ec8a1b7a80edda4f620fb96ba5d4803c0d81ded334b92efa85cdf1174` | PASS |
| course8 | `ab8e05971ca8fb9d077b491a766554f5b84118e068433afe4c17faa7e91fb89b` | PASS |
| project113 | `33dc51873bcbd33fa6ad2de854dd719e525706bdb764a50578570d1f73e89034` | PASS |
| stage617 | `24edf473c9e97b7ccbb287464302a4bbf6ffadff33efdc265076b5ae6b51455e` | PASS |

Original Production guard fingerprint remains:

`36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`

Actual frozen-root inventory checked this milestone: 15 files in `docs/knowledge-map/`, four in `state/knowledge-atlas/`, and 14 in `data/knowledge/` (33 total). Their inventories and SHA-256 hashes are unchanged. Historical personal snapshots, original release manifest, Production guard implementation, active Knowledge semantics, and original public edition are unchanged. This count describes these three roots; the earlier 496-file broader protected inventory is not relabelled as this narrower inventory.

Renderer/layout/model/routing source fingerprints remain unchanged. The only change to a renderer entry script is a one-line local evidence loader in scope `app.js`; no rendering or layout logic changed. The read-only validation workflow gains only the Course evidence file trigger, and publishing remains inactive.

## Maintained changes and preview

Maintained sources: shared `progress-analytics.js`, `progress-presentation.js`, `progress-ui.js`, `progress.css`; the scope data loader; Git reader, serializer and summary script; the new strict Course validator and empty source records; focused data/browser tests and documentation. The accepted knowledge aggregation algorithm was reused without alteration.

The same isolated linked worktree was rebuilt using the existing candidate-only packager. Seven candidate files change from the accepted prior candidate: the five analytics/presentation/loader assets, generated `progress.json`, and its candidate manifest. The package still contains 69 files and preserves the historical edition. All new enhancement source changes remain uncommitted as requested; future publication requires an approved checkpoint containing those maintained sources and the previously proposed packaging/migration work.

Canonical preview: [V6.6 My Skill Tree](http://127.0.0.1:8806/hyperskill-projects/knowledge-map/?view=skill-tree). Root entry: [V6.6 Atlas](http://127.0.0.1:8806/hyperskill-projects/knowledge-map/). Public JSON: [progress.json](http://127.0.0.1:8806/hyperskill-projects/knowledge-map/progress.json).

Existing excluded modified scope tests, untracked previews, and previous review material were not changed. The five accepted local commits and `origin/main` remain intact; no staging or repository commit was performed. No Production integration or publishing was activated. Technical validation ends here.
