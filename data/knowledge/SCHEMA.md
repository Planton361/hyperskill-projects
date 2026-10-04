# Knowledge snapshot contract (v1 active tables, v1 typed global observations)

This directory is the renderer-independent source of truth. The 2026-10-01
snapshot contains public metadata plus explicitly whitelisted personal facts
provided by the owner. It contains no session, account ID, certificate URL,
lesson content, solutions, platform tests, or authentication data.

The active normalized tables remain the accepted Course-8 projection. Global
catalog facts are now supplied by typed sanitized observations and joined by
stable identity in one internal catalog. They are not automatically inputs to
the production renderer or its persistent geometry. See the
[global catalog contract](../../scripts/knowledge_atlas/GLOBAL-CATALOG.md) for
the strict observation schema, resolution/reference model, five-root forest
validator, per-field provenance, projection API and security allowlist.

`global_knowledge_catalog` observations carry separate completeness status for
taxonomy pagination, categories, leaf references, Topic metadata, prerequisites
and followers. The current global snapshot is PARTIAL: 849 described categories,
89 described Topics and 3,017 unresolved references. Structural leaves without
explicit Topic identity are never fake Topic entities. Legacy progress
observations remain unchanged; typed loader dispatch keeps personal state and
global facts independent. Only accepted active tables/personal observations
contribute to the presentation source fingerprint.

The normal global Category-428 display did not resolve its six Python leaf
references into Topic metadata. Unresolved references are intentional valid
state. Future targeted acquisition is not implemented and is limited to IDs
made relevant by explicit course/project evidence; no mass Topic crawling is
planned. Category display must not be assumed to provide bulk Topic metadata.

## Tables and keys

- `courses.json`: numeric course ID; explicit topic/category/project membership
  arrays; public totals. Membership arrays represent many-to-many joins.
- `categories.json`: numeric IDs, labels, canonical parent and map URL.
- `topics.json`: numeric topic IDs; separate theory step IDs and URLs.
- `projects.json`: numeric project IDs, language and public stage-ID inventory.
- `stages.json`: loaded stage records, positions, incremental and cumulative
  required-topic IDs. Only project 113 stage records are loaded. Other projects'
  public `stage_ids` are external references, not claims that their records or
  requirements have been loaded.
- `edges.json`: typed source/target keys, optional stage context, evidence IDs.
- `progress.json`: separate course aggregates, partial topic observations, and
  project observations. There is no account identifier.
- `evidence.json`: normalized provenance, observed date, relevant fields,
  method and confidence. Personal excerpts are owner-provided evidence, not
  independently re-fetched authenticated data. Only allowlisted facts survive.

Graph keys use `course:8`, `topic:15`, `category:74`, etc. Names are never keys.
Category nodes use Hyperskill's topic namespace upstream; they are deliberately
typed separately here. Topic 36 and 1425 have multiple explicit category
memberships; retain those edges as well as each canonical parent.

## Relationship semantics

- `hierarchy`: category → category/topic, from the course-filtered map children.
- `prerequisite`: prerequisite topic → requiring topic, from `prerequisites`.
- `dependent`: topic → dependent topic, independently from `followers`.
  This snapshot retains only course-internal topic endpoints, not followers
  that are categories or belong to other courses. These two relations can
  corroborate the same directed connection; the renderer draws one segment.
- `project_requires`: project → topic, with Stage ID and stage evidence.
  Project 113 has 26 distinct targets. Stage 5 adds no new requirements.
- `course_contains`: course → root category/project, from explicit course/map
  membership. It is not a learning prerequisite.
- `project_applies`: reserved. None currently exist. The validator requires
  explicit evidence with a matching `assertion` object containing `type`,
  `source`, `target`; generic requirement evidence is insufficient.

## Unknowns are data

`null` means a complete ID set is unavailable; an empty array means a known
empty set. Never substitute one for the other. The owner-supplied sanitized
snapshot `observations/learned-2026-10-01.json`, observed at
2026-10-01T13:57:59.083Z, covers all 89 course topics. It explicitly establishes
31 `is_learned: true` IDs, 58 false values, and zero skipped topics, matching
the authenticated course counter. `learned_topic_ids` contains those 31 IDs.
Every personal topic row references the snapshot evidence; validation compares
its source booleans and verification status rather than inferring from counts.

Learned and verified are separate: only 12 records have
`verification_status: "verified"`. Topic 113 (Reading user input with Scanner,
not project 113) is learned/completed but has verification status `failed`.
Other learned records can have `evaluation`; preserve the literal status.
`is_verified` is true only for the exact status `verified`. `My Knowledge`
in the accepted V6 Atlas includes the revealed Course landscape: all 89 Course-8
Topics, with 31 learned and 12 verified styled independently. The older graph
learned-only view is not the V6 visibility contract. Explicit `not_learned`
remains distinct from missing/unknown status. The read-only
[Activation / Reveal planner](../../scripts/knowledge_atlas/ACTIVATION.md)
describes future relevance and presentation candidates without changing these
personal facts or accepted geometry.

`applied_topic_ids` and every topic-level `is_applied` remain null. The earlier
aggregate 26/85 is not a new topic-level observation and is not inferred from
project requirements. The new snapshot does not refresh project or Applied
aggregate evidence. Historical Topic 15 evidence is retained but no longer
used for the current row; its old stage position is not merged into the new
snapshot. The trailing browser console source label is not observation data.

Project 113 is completed. Its full authenticated completed-stage inventory
has not been copied into this dataset and remains null. Project 380 is active
in the study plan with `completed_stage_ids: []`. A topic's observed
`stage_position` does not identify the project that applied it.

Other listed projects display `available`: this means part of the public
course catalogue, not verified personal availability, subscription entitlement,
readiness, or a completed/active status. Unloaded requirements show unknown,
never zero. Snapshots describe the observed date, not live account state.

Future true topic-level applied observations also need explicit evidence with
`assertion: {"type": "topic_applied", "topic_id": 15}` (using the actual ID).
Do not create assertions merely to satisfy validation; they require an actual
source that makes the corresponding claim.

## Offline generation and validation

From the repository root:

```bash
python3 scripts/build-knowledge-graph.py
python3 scripts/build-knowledge-graph.py --check
python3 -m unittest discover -s scripts/tests -p 'test_knowledge_graph.py' -v
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:8000/knowledge-graph/`. Opening `index.html` using a
`file://` URL is not supported because browsers restrict fetching local JSON.
GitHub Pages can serve `/docs` as its source; no backend, build service, CDN
or live Hyperskill access is needed at runtime. Pages has not been configured
or published by this change. Root/profile READMEs remain unchanged.

`graph.json` and `preview.svg` are generated, not manually edited. Input order
is normalized for nodes/edges; the fixed-step force layout uses no wall-clock
time or randomness. Repeated builds of identical inputs are byte-identical.
The static preview is a projection of the same graph, not a screenshot of live
personal progress. The browser uses the same initial positions and may relax
them with D3. Geometric proximity never constitutes an evidentiary relation.

## Browser and dependency checks

D3 7.9.0 is vendored with its ISC license. Runtime requests are same-origin
only. There are no analytics, browser storage writes or authentication calls.
The renderer supports keyboard selection/search and reduced motion.

Optional browser smoke test (Playwright is an external test dependency, not a
runtime dependency; install outside this repository if desired):

```bash
PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
CHROMIUM_EXECUTABLE=/absolute/path/to/chrome \
node scripts/tests/knowledge_graph_browser.cjs http://127.0.0.1:8000/knowledge-graph/
```

The test uses an isolated non-persistent browser context and saves no cookies,
HAR, traces, screenshots or authentication state. Dependencies must already
be installed; neither the generator nor tests download them automatically.

No Hyperskill collector is part of this phase. Future collection must be
separate, use explicit allowlists, keep sessions outside Git, validate schema
drift and provenance, and never reinterpret missing values as false.
