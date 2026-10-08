# Universal V6.6 Scope Progress Inspector

**C — UNIVERSAL PROGRESS INSPECTOR READY FOR HUMAN REVIEW**

Local development workspace, 2026-10-08. The previously accepted My Skill Tree progress Inspector is the presentation foundation. The current local branch/worktree was retained; no reset to remote main, commit, push, deployment, Hyperskill request or new personal observation.

Canonical local preview: <http://127.0.0.1:8798/prototypes/knowledge-atlas-navigation/index.html?view=atlas&course=8>

The loopback static server remains running on port 8798. Open **Inspector** to see the active scope's coverage. Select Java or a Topic in the existing map/search. Existing Course / Project / Stage filters select the corresponding exact scope; the main views remain **Atlas** and **My Skill Tree**.

## Shared architecture

The accepted `progress-analytics.js` remains the one semantic-ID aggregation implementation. It now also exposes `categoryInScope`, `topic` and `officialCourseProgress`. Existing Global/Course/Project/Stage and Category calls still use the same aggregation routine. Official Course snapshots use that routine with their explicitly Course-bound observation set; there is no second counting algorithm.

`progress-presentation.js` extracts the accepted compact card/bar/date markup into a shared presenter. Scope Pyramid Inspectors and My Skill Tree comparison/Category views use it. The accepted `progress.css` is byte-identical and imported directly into the Scope entrypoint. No redesigned controls, new dashboard, permanent panel or main tab was added.

Scope `ux-model.js` delegates Topic states and its legacy Course Category overlay shape to the shared module. Its previous separate progress calculation was removed. Scope `app.js` changes are confined to Inspector markup and bindings; the renderer, camera, routing, selectors and initialization code remain byte-identical. The scope root Inspector shows coverage even without an entity selection, including UNKNOWN/EMPTY scopes.

All inputs are existing local files: the Global Catalog (849 Categories / 3,106 Topics), the explicit scope index (52 Courses / 391 Projects / 1,967 Stages), and accepted personal progress/evidence/provenance. No catalog or requirement relations were regenerated.

## Inventory coverage and exact fixtures

Pure validation ran over every scope:

| Inventory | Validated | Known-empty | Unknown requirements |
| --- | ---: | ---: | ---: |
| Courses | 52 | 0 | 0 |
| Projects with known requirements | 375 | 5 | — |
| Projects with UNKNOWN requirements | 16 | — | 16 |
| Stages | 1,967 | 328 | 0 |
| Global Categories | 849 | Per exact descendant set | — |

All known scopes satisfy `learned + explicitly not learned + unknown = eligible distinct Topics`. Their eligible counts equal the distinct exact input membership/requirement IDs. Verified is independently joined by Topic ID; remaining equals explicit false plus unknown and is labelled **Not yet evidenced learned**.

| Scope | Learned / eligible | Verified | Explicitly not learned | Learning unknown |
| --- | ---: | ---: | ---: | ---: |
| Global | 31 / 3,106 | 12 | 58 | 3,017 |
| Course 8 | 31 / 89 | 12 | 58 | 0 |
| Course 2 | 1 / 275 | 0 | 9 | 265 |
| Project 113 requirements | 26 / 26 | 10 | 0 | 0 |
| Project 380 requirements | 14 / 15 | 3 | 1 | 0 |
| Stage 617 local requirements | 12 / 12 | 7 | 0 | 0 |
| Java Global (`category:73`) | 26 / 297 | 11 | 43 | 228 |
| Java within Course 8 | 26 / 69 | 11 | 43 | 0 |

[Complete inventory results](tests/universal-progress-results.json) include individual scope records, verification-unknown counts, dates, official Course states, explicit statuses, all Category results and fixture summaries. Category closure was independently validated from the full reverse-membership relation, not from rendered graph nodes. All 849 Categories were also checked within representative Course 8, Course 2, Project 113, Project 380 and Stage 617 scopes.

## Personal evidence and official Course progress

Knowledge coverage uses shared Global Topic identities: personal learning observed in Course 8 may cover the same Topic in Course 2. Course 2 therefore has **1 / 275 evidenced learned** in Global knowledge coverage, while **Officially observed Course progress: UNKNOWN** is separately shown. The same distinction applies to every Course.

Only Course 8 has a complete accepted personal Course snapshot. Official progress requires an explicitly sourced Course row marked `topic_status_coverage: complete`, a complete set of learned boolean observations bound to that exact Course and snapshot date, and agreement with its explicit learned total/count. Partial, missing, wrong-Course or inconsistent snapshots remain UNKNOWN. Shared Topic knowledge cannot manufacture an official Course snapshot. No official percentage, current-Course claim or Hyperskill completion certificate is inferred.

Personal Topic evidence remains historical: **2026-10-01**, with full timestamp `2026-10-01T13:57:59.083Z` retained in aggregate results and date tooltips. Missing personal evidence is labelled as such; later public catalog captures do not refresh personal knowledge. The application describes local historical evidence, never current/live Hyperskill state.

The sourced per-field observation resolver retains unknowns, resolves newest explicit boolean observations independently and does not infer learning from membership, requirements, prerequisites, completion or taxonomy position. Disposable tests verify independent `verified=true` / `learned=false`; no synthetic observation entered any protected file.

## UNKNOWN / EMPTY and completion semantics

All 16 UNKNOWN Project requirement scopes show **Requirements not established**, **UNKNOWN denominator** and no progress denominator/count. Their aggregate counts remain null.

Known-empty Projects 405, 454, 455, 462 and 580 show **No requirement Topics**. All 328 empty Stage-local sets use the same known-empty behavior. Empty Category intersections show **No eligible Topics**. Empty sets never count as complete or 100%.

Project and Stage denominator sets come only from their exact accepted explicit relations. Stage `all_prerequisites`, cumulative unions and rendered descendant lists are never substituted.

Project 113's recorded **completed** status and Project 380's recorded **active** status are displayed separately, dated 2026-10-01. Stage 617 has no recorded personal status and is labelled **Not recorded**. All requirement Topics learned means knowledge coverage only; it establishes neither Project/Stage completion, application nor readiness.

## Category and Topic Inspectors

Selecting a Category in any local Course/Project/Stage pyramid shows:

1. **Global Category**: distinct complete structural descendant Topic IDs, including valid secondary memberships.
2. **Active Scope Category**: those descendants intersected with the active scope's complete explicit Topic ID set.

Both show learned/eligible, verified, explicit false, unknown, verification unknown, Not yet evidenced learned and personal date. Nonempty all-learned evidence is explicitly labelled within the relevant Global Category or active scope. Verification completeness is separate.

The immediate-subcategory breakdown uses the same bars, in an expandable section. Child rows use the active scope's intersection and show learned/eligible, verified and meaningful unknown counts. Overlapping child totals are labelled non-additive. Exact-ID child navigation stays in the local scope when the Category is present; otherwise it opens that precise Global Category through the existing shell.

The recorded catalog has no Category with multiple structural parents. Representative secondary-membership validation therefore uses **Category 35** and **Topic 36**, which belongs to Categories **35 and 306**; no extra Category-parent relationship was manufactured.

Topic Inspectors retain exact title/ID, the selected Course membership / Project study-plan / Stage-local requirement role, taxonomy path and **Show in Global**. Learning, verification and verification/evaluation state now come from the shared evidence resolver, with explicit false distinguished from unknown and personal date visible. Membership never changes personal state.

## Focused validation and browser behavior

Executed:

- `node prototypes/knowledge-atlas-v6-skill-tree/tests/progress-analytics.cjs`: all 17 existing focused aggregation checks passed.
- `node prototypes/knowledge-atlas-v6-skill-tree/tests/universal-progress.cjs`: complete inventory, all Category closures and representative intersections, historical fixtures, independent partition/reference checks, official-versus-shared knowledge, incomplete-snapshot guards, UNKNOWN/EMPTY, dates, independent verification and input immutability passed.
- `node prototypes/knowledge-atlas-v6-skill-tree/tests/universal-progress-browser.cjs`: Course 8, Course 2, Project 113, Project 380, Stage 617, unobserved Course 3, UNKNOWN Project 229, empty Project 405 and empty Stage 179 passed. Also checked Java in Course/Project/Stage, Category 35 secondary memberships, explicit false and unknown Topic states, Project/Stage Topic roles, subcategory navigation, exact `category:194` / `topic:36` Global navigation, and My Skill Tree comparison controls.
- Syntax checks for changed/new JavaScript and `git diff --check` passed.

Inspector open/close/Pin/clear and entity/breakdown interactions preserve the same graph node objects, world geometry and scope layout-build count. My Skill Tree analytics context changes preserve its actual Topic rendering and geometry. Existing Atlas filter changes retain their existing scope-layout behavior. Browser console/page errors were empty; external requests were blocked and none were attempted. No broad regression suite or screenshot matrix was run.

[Focused browser results](tests/universal-browser-results.json). Three representative captures were visually inspected: [Course 2 knowledge versus official progress](tests/universal-review/course2-knowledge-official.png), [Java within Course 8](tests/universal-review/java-course8.png), [Project 380 coverage and recorded status](tests/universal-review/project380-status.png).

## Geometry and protection

Actual world-geometry hashes exactly match the accepted contracts for Global, My Skill Tree, Course 8, Course 2, Project 113 and Stage 617. The other representative scopes preserve their measured geometry across Inspector interactions. Full hashes are recorded in the browser results.

The pre-task byte inventory covered **773 existing files**. **766 remain byte-identical**. Seven existing files changed: Scope entrypoint, Scope UX data adapters, Scope Inspector functions, Skill Tree entrypoint, shared aggregation module, Skill Tree presentation adapter, and one historical browser assertion updated to the new official-Course wording. New files contain the shared presenter, focused validation/results, three representative captures and this report.

Protected `data/knowledge/`, `state/knowledge-atlas/` and `docs/knowledge-map/` are unchanged. All Global sources, all layout/projection/routing/worker sources, accepted styles (including progress CSS), the Unified Atlas shell and the personal renderer/model sources are unchanged. Scope `app.js` was additionally compared as source: everything before `inspect()` and from `render()` through the end is byte-identical to its pre-task version. Existing unrelated work and historical reports/captures were retained.

[Protection results](tests/universal-protection-results.json).

**HARD STOP. No commit, push or deployment.**
