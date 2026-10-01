# Knowledge snapshot contract (v1)

This directory is the renderer-independent source of truth. The 2026-10-01
snapshot contains public metadata plus explicitly whitelisted personal facts
provided by the owner. It contains no session, account ID, certificate URL,
lesson content, solutions, platform tests, or authentication data.

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

`learned_topic_ids: null` and `applied_topic_ids: null` mean the complete sets
are unavailable. An empty array would mean a known empty set; never substitute
one for the other. Topic 15 alone has explicit learned/verified evidence.
All topic-level applied values are null. Aggregate 31/89 learned and 26/85
applied do not assign status to individual topics.

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
