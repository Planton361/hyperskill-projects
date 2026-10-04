# Activation / Reveal planning

The global Catalog defines the internal knowledge universe. Accepted Course,
Project and personal Topic evidence establishes relevance. Minimum metadata
determines renderability. A read-only ActivationPlan describes what a later,
separately approved presentation activation would require.

Revealed does not mean learned. Project relevance does not mean learned.
Project completion implies neither verification nor `project_applies`. Dormant
does not mean deleted. Course 8 still reveals all 89 Topics while 31 are learned
and 12 verified.

## Pure API and CLI

`ActivationPlanner(catalog, checkpoint, geometry)` takes a composed `Catalog`
and accepted presentation inputs. The constructor validates the checkpoint,
checks its Category/Topic inventory against geometry, and checks renderability
of accepted history. The CLI also validates the checkpoint/snapshot pair and
the accepted geometry fingerprint. These inputs are read, never modified.

```bash
python -B scripts/plan-knowledge-atlas-activation.py --course 8
python -B scripts/plan-knowledge-atlas-activation.py --project 113
python -B scripts/plan-knowledge-atlas-activation.py --json
```

The separate CLI has no write, apply, collection, or report-file option. Default
context is `MY_ATLAS`; `--course` selects `CURRENT_COURSE`; `--project` selects
`PROJECT_FOCUS`. JSON goes to stdout. Exit 0 means planning succeeded, including
plans requiring metadata/review; consumers must inspect `recommended_outcome`.
Validation errors exit 1. No browser or layout allocator is invoked.

Pure queries:

```python
planner.plan()  # MY_ATLAS, all tracked historical courses, projects, personal evidence
planner.plan('CURRENT_COURSE', course_ids=[8])
planner.plan('PROJECT_FOCUS', project_ids=[113])
planner.plan(course_ids=[8, 42], project_ids=[113], include_personal=True)
planner.get_entity_status('reference:333')
```

The IDs 42 and any hypothetical metadata in tests are synthetic examples, not
claims about real Hyperskill Course membership. Existing `Catalog` projection,
ancestor and resolution APIs remain compatible. Future `GLOBAL_CATALOG` search
or visualization remains separate from personal activation planning.

## Independent dimensions and reasons

Plan rows keep catalog status/resolution, Course reasons, Project reasons,
personal relevance, learning, verification, renderability and presentation
activation separate. Current explicit personal rows are reported without
changing their truth; literal verification statuses and evidence IDs are retained.
Null means no such personal evidence, not false.

Seed reasons are:

* `COURSE`: explicit `topic_ids` / `category_ids` in accepted Course metadata,
  carrying Course identity, field and evidence IDs.
* `PROJECT`: accepted explicit `project_requires`, carrying Project identity,
  edge ID, optional Stage ID and evidence IDs. Listing a Project, completing it,
  a filtered map, study plan or source code is insufficient.
* `PERSONAL`: affirmative explicit learned or verified Topic progress, carrying
  evidence IDs and its observation timestamp/context. Negative/unknown personal
  states do not independently seed reveal; they still style relevant Topics.
* `STRUCTURAL_ANCESTOR`: Category context connecting a seed to roots. Reasons
  identify the original seed, traversed child, and observation field-source or
  accepted hierarchy-edge evidence for the membership. Seed reasons remain
  independently available, so this chain explains Course/Project/Personal origins.

Seed evidence must exist and have explicit confidence. The input is the accepted
normalized evidence boundary, not arbitrary raw response data. No new acquisition
mechanism or inference is implemented.

## Structural closure and renderability

Closure includes seeded Categories/Topics/references and every evidenced
structural ancestor path. It preserves multiple memberships, including IDs 36
and 1425, and never pulls unrelated siblings into the plan. Canonical parent is
reported separately from structural memberships. Structural membership source
records remain traceable to sanitized observations or accepted evidence.

A user-facing Topic requires:

1. Stable positive Hyperskill ID and explicit typed Topic entity.
2. Nonempty title.
3. At least one valid Category membership leading to a known root.

`RESOLVED_TOPIC` and `PARTIAL_TOPIC` can satisfy this display contract. Theory,
prerequisites, followers, learning and verification are not required to display
it. Category display similarly requires identity/title and valid placement;
an explicit root needs no parent.

Unresolved leaves use `reference:<id>` in planning, never fabricated `topic:<id>`
entities or titles. Relevant references report `BLOCKED_ON_METADATA`, their
membership paths and reasons, and missing title/Topic entity type. Completely
unknown IDs also lack structural membership. A later explicit metadata promotion
uses the existing Catalog promotion model; this planner acquires no metadata.

## ActivationPlan and outcome policy

`schema_version: 1` plans include context, seed/reason rows, already-active IDs,
new Category/Topic candidates, blocked reference rows, required ancestors,
affected roots and major branches, accepted presentation fingerprints, retained
history, estimated entity counts and outcome conditions. Major branch means the
first Category below a root, not an invented domain inferred from a title.

Each placement reports the ordered ancestor chain, active/dormant ancestors,
nearest accepted ancestor and required new Category chain. Estimates are record
counts, not pixel budgets or guarantees of future displacement. Catalog counts
and context-dormant counts remain separate from the active projection.

| Condition | Final planning outcome | Existing pipeline correspondence |
| --- | --- | --- |
| Only accepted geometry | `NO_CHANGE` | `SAFE_TO_APPLY` |
| New renderable geography within an accepted root | `ACTIVATION_REVIEW_REQUIRED` | `REVIEW_REQUIRED` |
| First activation of a different global root | `ACTIVATION_REBALANCE_REQUIRED` | `REBALANCE_REQUIRED` |
| Any relevant entity lacks minimum metadata | `METADATA_REQUIRED` | Blocked before presentation mutation; no applicable pipeline permission |

Severity is deterministic: metadata, then new root, then same-root review,
then no change. Coexisting conditions remain listed. Same-root activation,
including a new major branch, conservatively requires review; actual capacity
and whether review later discovers a rebalance need are not assessed here.

Known ancestors of a blocked reference can be listed as Category candidates.
`geometry_required` describes candidate geography, not approval: the entire
plan remains blocked if metadata is missing. `newly_activated` is always empty,
`presentation_mutation_permitted` is always false, and planning displacement is
always zero. Future displacement is unknown for candidates/blocked entities;
only `NO_CHANGE` proves future displacement zero.

All set-like output arrays have deterministic ordering. Membership paths keep
their meaningful root-to-parent order. No timestamp, random identifier or local
source path is added to a plan. Equivalent input inventories yield identical
serialized JSON via `snapshot.encode(plan)`.

## Accumulated Course and Project history

`MY_ATLAS` uses the union of explicitly tracked historical Courses, accepted
Project requirements and affirmative personal Topic evidence. Completed Courses
and Projects remain provenance sources; status does not filter their evidence.
Learning and verification remain independent of those histories.

Accepted geometry retains `presentation_history: ACTIVE_HISTORY` independently
of relevance. A node can be `DORMANT` for a selected evidence context while still
`ALREADY_ACTIVE` in accepted presentation history; that does not hide or remove
it. Every plan reports the complete retained accepted inventory and no
geometry removals. Context scopes can select Course/Project rows without deleting
that presentation history. Removing/changing a Course selection is not permission
to erase revealed geography. A future approved activation would persist new
geometry and presentation history separately from Knowledge evidence and could
increase Generation only because accepted presentation geography changed.

Future default `MY_ATLAS` is this accumulated revealed personal landscape.
`CURRENT_COURSE` and `PROJECT_FOCUS` are contextual views. `GLOBAL_CATALOG` is a
separate universe query. My Knowledge keeps not-learned but relevant Topics and
uses personal styling; it does not reduce the landscape to learned Topics.

## Relations, search and viewport boundaries

Prerequisites and dependents never seed relevance. The plan reports existing
routable edges only where both endpoints already have accepted geometry;
others remain deferred and cannot route into dormant geography. No routing code
changes: existing LCA taxonomy routing and amber `project_requires` overlays
remain authoritative once endpoints have accepted geometry.

Future default search should search the revealed personal Atlas; global Catalog
search should be separate. Unresolved dormant references must not appear as fake
Topics. Future Fit All should fit active personal geometry, not all 3,955 global
structural positions. Current UI, search, minimap and viewport are unchanged.

## Regression and next presentation phase

Course 8 plans 46 existing Categories and 89 existing Topics, no new candidates,
no blocked entities and `NO_CHANGE`. Project 113 plans its 26 requirements and
existing ancestor context, likewise `NO_CHANGE`. Accepted Generation is 0,
layout schema 2 and algorithm `atlas-incremental-2`.

Tests cover synthetic overlap, dormant partial metadata, unresolved references,
all four new-root policies, multiple memberships, provenance, personal-only
relevance, relation boundaries, history, deterministic serialization and protected
source/Production/state bytes. Synthetic fixtures stay in memory only.

The next separate presentation phase must review candidate layout against
accepted capacity, frozen bounds, root-region design and visual readability.
This foundation neither approves activations nor computes future placement.
