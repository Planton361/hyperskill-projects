# My Skill Tree — contextual progress analytics

**Recommendation: C — MY SKILL TREE ANALYTICS READY FOR HUMAN REVIEW**

Local review, 2026-10-08. The accepted Unified Atlas application retains exactly **Atlas** and **My Skill Tree**. All analytics live inside My Skill Tree. No commit, push, deployment, Hyperskill contact or new personal observation.

Local preview: <http://127.0.0.1:8798/prototypes/knowledge-atlas-navigation/index.html?view=skill-tree>

The repository-root static server is running on loopback port 8798. Open **Progress analysis**, retain/select Course 8, select Project 113, then Stage 617. Select Java in the existing map or search to inspect its two denominators.

## Exact statistics

| Scope | Eligible distinct Topics | Evidenced learned | Explicitly not learned | Learning unknown | Verified | Verification unknown | Remaining without confirmed learning |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Global | 3,106 | 31 | 58 | 3,017 | 12 | 3,017 | 3,075 |
| Course 8 | 89 | 31 | 58 | 0 | 12 | 0 | 58 |
| Project 113 requirements | 26 | 26 | 0 | 0 | 10 | 0 | 0 |
| Stage 617 local requirements | 12 | 12 | 0 | 0 | 7 | 0 | 0 |
| Java — Global Category (`category:73`) | 297 | 26 | 43 | 228 | 11 | 228 | 271 |
| Java — Course 8 intersection | 69 | 26 | 43 | 0 | 11 | 0 | 43 |

Global covers all 3,106 catalogued Topics, not just personal graph nodes. Java uses complete structural membership closure, including valid secondary memberships. Every scope deduplicates semantic Topic IDs. Child rows may overlap and are explicitly labelled as non-additive.

## Data and aggregation

`progress-analytics.js` is a reusable pure module, available as `ProgressAnalytics.create` in the browser and through CommonJS. Inputs are the Global Catalog, scope membership/requirement index, accepted personal Topic progress and evidence/provenance. Its functions aggregate explicit Topic sets, Global Topics, Courses, Projects, Stages and Category/Course intersections. It performs no I/O, renderer calls, persistence, clock reads or input mutation.

The UI reads the existing `../knowledge-atlas-scope-pyramid/catalog.json` (849 Categories / 3,106 Topics) and `scope-index.json` (52 Courses / 391 Projects / 1,967 Stages). Neither file was regenerated or changed. It retains the existing complete explicit Course memberships, distinct Project study-plan requirements and Stage-local requirements. Prerequisites, graph visibility and positions never establish eligibility or personal learning.

Only sourced, accepted personal Topic observations supply learned/verified values. Each boolean is resolved independently from its newest observation; equal-date contradictory values remain unknown. Verification does not require learning. Missing observations never become false. An unobserved Course displays **UNKNOWN Course progress**; any shared Topic evidence is explicitly described as such. Course 8 is labelled **Tracked / Selected Course**, with no invented current-Course claim.

All 16 UNKNOWN Project requirement scopes have null/UNKNOWN denominators and null counts. Explicitly empty requirement sets display **No requirement Topics**, never 100%. A Category/Course intersection with no Topics displays **No eligible Topics**. Completeness requires a nonempty set whose every Topic has explicit learned=true; Global and Course Category completeness are separately labelled. Verification completeness is separately tested.

Project/Stage statistics are knowledge coverage. Project 113's **completed** personal status is separately shown from explicit `personal-course-8` evidence, dated 2026-10-01. Stage 617 has no recorded personal status and is labelled **Not recorded**. Coverage never establishes completion, application or readiness; no platform-issued mastery is claimed.

## Presentation and Inspector behavior

- A compact optional overlay strip shows **31 / 3,106 evidenced learned · 12 verified** and a proportional segmented bar.
- **Progress analysis** opens a closable overlay with Global/Course comparison and optional Project/Stage cards. Selectors are local context controls and do not change main routes or Atlas filters. Stage choices use exact Project containment.
- Bars distinguish learned, explicitly not learned and unknown. Unknown has a hatched fill; textual counts and accessible bar descriptions provide meaning without color alone.
- Selecting a Category inserts Global Category and selected-Course intersection cards into the existing Inspector. Immediate Global child Categories have compact horizontal bars, learned/eligible, verified and meaningful unknown counts.
- Child clicks select that exact Category in the personal graph when present; otherwise they navigate to its exact Global semantic identity through the existing shell. The explicit **Show Category in Global Atlas** action preserves the same identity.
- The existing closable overlay and optional Pin behavior remain. Category selection and Course context changes update analytics without replacing graph nodes or building layout. No additional graph, tab or permanent column was added.

## Evidence date and freshness

The displayed **Last observed (personal)** is **2026-10-01** for the reference statistics. The complete accepted Topic observation timestamp is `2026-10-01T13:57:59.083Z`, preserved in the `<time>` element's timestamp and tooltip and in the aggregate result. Personal status dates are separately retained. Later public Catalog/relation captures do not make personal knowledge evidence fresher. A scope without dated personal evidence says **No personal evidence**.

These are historical local observations, not live data. No growth chart, streak, time estimate or achievement inflation was added. Synthetic progression exists only as disposable in-memory test data.

## Focused validation

`node prototypes/knowledge-atlas-v6-skill-tree/tests/progress-analytics.cjs` — **17 checks passed**. Includes all four reference statistics and verified counts; Java's two perspectives; nested Categories; real and synthetic secondary membership overlap; independent full-catalog descendant traversal; no eligible Course Topics; unobserved Course; all 16 UNKNOWN Projects; real empty Project/Stage; disposable +1 learning; newer false overriding older true; verified=true with learned=false; missing learning; unsourced observations; conflicting evidence; separate Course/Global Category completeness; dates; pure input immutability.

`node prototypes/knowledge-atlas-v6-skill-tree/tests/progress-browser.cjs` — focused Unified Atlas checks passed. Includes displayed counts and dates; separate personal statuses; UNKNOWN/empty cases; unobserved Course; Java Course-context updates including an empty intersection; exact personal/global child navigation; close/Pin; exact Show in Global; two persistent tabs; zero layout builds and identical graph node objects during analytics interactions. External requests were blocked and none were attempted; browser errors were empty. The browser test uses the existing local Playwright installation; it accepts `PLAYWRIGHT_MODULE` and `ATLAS_BROWSER_EXECUTABLE` overrides.

`node --check` for both new JavaScript modules and `git diff --check` passed. No broad regression suite was run.

Results: [aggregation](tests/progress-results.json), [browser](tests/progress-browser-results.json), [protection](tests/progress-protection-results.json).

## Geometry and protection

All five actual world-geometry fingerprints exactly match the existing accepted contract:

| View | SHA-256 |
| --- | --- |
| My Skill Tree | `a60fc22e272079c91f39cfed9c01af5865bae29120e6d6f7801b02da96cd6348` |
| Global | `1306993ec8a1b7a80edda4f620fb96ba5d4803c0d81ded334b92efa85cdf1174` |
| Course 8 | `ab8e05971ca8fb9d077b491a766554f5b84118e068433afe4c17faa7e91fb89b` |
| Project 113 | `33dc51873bcbd33fa6ad2de854dd719e525706bdb764a50578570d1f73e89034` |
| Stage 617 | `24edf473c9e97b7ccbb287464302a4bbf6ffadff33efdc265076b5ae6b51455e` |

The pre-task SHA-256 inventory covered **759 existing files**. **758 remain byte-identical**. The sole existing-file change is Skill Tree `index.html`, adding the analytics CSS/module/UI script tags. New files are confined to that prototype: the pure module, presentation script/CSS, focused tests/results, five captures and this report.

All pre-existing `data/knowledge/`, `state/knowledge-atlas/`, `docs/knowledge-map/`, Global V6.6, V6, Scope Pyramid and Unified Atlas navigation/shell files remain byte-identical. The personal `app.js`, `model.js`, `model.json`, registry, layout, routing, renderer/vendor and original styles remain byte-identical. No world positions, packing, routing, renderer or Atlas filter behavior changed. Existing unrelated work was preserved.

## Five review captures

Only the requested five captures were created at 1440 × 1000 and visually inspected:

1. [My Skill Tree overview progress](tests/progress-review/1-overview.png)
2. [Java Category Inspector](tests/progress-review/2-java-inspector.png)
3. [Course progress](tests/progress-review/3-course-progress.png)
4. [Project / Stage progress](tests/progress-review/4-project-stage-progress.png)
5. [Global vs personal comparison](tests/progress-review/5-global-personal-comparison.png)

**HARD STOP.** Ready for human review; no commit, push or deployment.
