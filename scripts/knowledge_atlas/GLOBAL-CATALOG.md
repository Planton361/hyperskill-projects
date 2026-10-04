# Global catalog data foundation

## Global Catalog

The internal universe is a composed catalog, independent of the V6 renderer.
`catalog.Catalog(snapshot.load_source(...))` joins sanitized global observations
with accepted normalized facts by `category:<id>` and `topic:<id>`. Courses,
projects and stages retain `course:<id>`, `project:<id>`, `stage:<id>`. Titles are
never keys. There are no parallel maintained global category/topic tables.
Existing active entities join under the same identity, with their accepted
metadata/evidence retained; this is not a copy per course.

The 2026-10-04 observation establishes five roots, 849 categories, 3,106 distinct
structural leaves and 3,952 hierarchy pairs (844 category pairs, 3,108 leaf
memberships). Maximum leaf depth is eight, counting roots at zero. The roots
are Computer science, Math, Natural science, Product development and Generative
AI. Forest validation checks parent/children agreement, transitive descendants,
reachability, cycles, self-relations and unique structural IDs.

## Structural References

A structural leaf is not automatically a Topic. Unresolved references retain a
numeric Hyperskill ID, all explicit parent memberships, and source references.
They have no invented title, theory step, public URL or `topic:<id>` entity.
Leaves 36 and 1425 each have two structural memberships. A Topic's explicitly
supplied canonical parent is separate from those memberships.

## Topic Resolution States

| State | Required explicit evidence |
| --- | --- |
| RESOLVED_TOPIC | Topic API entity (`is_group: false`), ID, title, parent field, theory identifier, prerequisites, explicit prerequisites and followers fields |
| PARTIAL_TOPIC | Explicit Topic identity and title, including a learning-activity `topic_id` foreign key; detailed fields may be absent |
| UNRESOLVED_REFERENCE | Explicit structural leaf membership only |

The snapshot has one resolved Topic, 88 partial Topics and 3,017 unresolved
references. Its resolution states describe this capture, even when richer
accepted Course-8 metadata already exists for the same identity. Capture
absence does not invalidate that older evidence. An empty captured relation
array differs from an absent field. No global URL was returned and none is
synthesized. Ordered Topic hierarchy paths retain their original order;
children, descendants and relationship inventories are deterministically
sorted/deduplicated. Original descendant multiplicity is not a separate fact;
every explicit leaf membership survives.

### Category bulk-resolution pilot

The owner tested the normal global Knowledge Map path Computer science →
Programming languages → Python → Basics → Simple programs (Category 428).
Its structural leaves are 333, 336, 335, 404, 399 and 418. Merely displaying the
Category did not trigger Topic-detail requests for those six IDs or resolve
their metadata. **Category bulk resolution was unavailable for this tested
interaction.** Do not repeat this pilot or assume that category expansion
returns Topic metadata.

The 3,017 unresolved references are intentionally valid Catalog state. Keep
the captured global structure; future explicit course/project evidence can
identify which unresolved IDs matter. Only those relevant IDs are candidates
for targeted Topic metadata evidence. No mass crawling is planned. The targeted
capture/observation mechanism has not yet been implemented; the pure promotion
API and synthetic fixture establish only its evidence and provenance contract.

`Catalog.promote_reference(id, sanitized_observation, observation_id=None)` is
pure: it returns a new catalog and requires a validated observation explicitly
describing that Topic. The original reference history, structural memberships
and per-field provenance remain intact. Future full metadata can upgrade a
partial Topic via a later typed observation. Missing fields never retract
older facts. Refreshes retain missing identities for review rather than
silently deleting them; structural facts and metadata history are traceable.

## Global Taxonomy vs Course Membership

Taxonomy says where knowledge exists. Course membership is a separate explicit
many-to-many join in course metadata. It cannot be guessed from a branch title
or map filter. A Topic shared by courses 8, 42 and 57 remains one Topic. Category
context can be derived by walking every explicit structural ancestor.

## Project Evidence

Project context seeds only `project_requires` records from dedicated accepted
project/stage requirement evidence. A project-filtered Knowledge Map, stage
study plan, source code or taxonomy does not establish requirements. No
`project_map_context` relation is added in this iteration. Project 113 retains
26 distinct required Topics; its fourth stage retains 12 requirements. There
are no `project_applies` assertions.

## Personal State

Catalog facts never establish learned, verified, applied, available or locked
states. `enabled` and other platform flags are not imported. Personal progress
continues to use the original typed/legacy observation path and accepted
evidence. The current exact state remains 31 learned and 12 verified Topics.
An aggregate of 35 in another capture does not identify four additional Topics.
Project completion implies neither learning nor verification nor application.

## Dormant / Relevant Semantics

`get_relevance(entity_id, context)` independently returns `catalog_known`,
`course_relevant`, `project_relevant`, `learned`, `verified`, and a derived
`dormant` result for the selected context. Dormancy is absence from the explicit
course/project scopes. It is not persisted as a hidden/visible fact. Unknown
personal values remain null. Course/project category relevance includes
structural ancestors without claiming explicit course membership for them.

## Active Projection

Pure data APIs currently available:

```python
catalog.get_course_projection(8)
catalog.get_tracked_courses_projection([8])
catalog.get_project_context(113)
catalog.get_catalog_ancestors("topic:36")
catalog.get_resolution_status(333)
catalog.get_relevance("category:331", {"course_ids": [8]})
```

Course seeds are explicit memberships plus necessary taxonomy ancestors.
Project seeds are explicit requirements plus context. Projection output keeps
resolved entities, unresolved references and wholly unknown candidates separate;
it also preserves scoped accepted relations and personal progress. Unknown
course IDs require membership evidence. Personal scopes apply state to course
nodes; they do not remove not-learned nodes. Pure projections allocate no slots.

The production compatibility adapter `active_projection(data)` admits only
accepted normalized tables and legacy personal observations to the current
pipeline. It does not automatically activate a course or global ancestor.
Trusted active-data edits continue to go through the existing migration gates.
Course 8's query fixture remains exactly 46 categories, 89 Topics and 136
hierarchy pairs, with existing relations, projects, progress and evidence.

Future view semantics (design only): Global Atlas includes all known catalog
positions, representing unresolved references distinctly; My Courses includes
tracked memberships and ancestors; Current Course narrows those seeds to one
course; My Knowledge styles that selected course scope with personal evidence;
Project Focus uses explicit project requirements and ancestors. No UI controls
or global renderer mode are introduced here.

## Why Global Catalog Does Not Automatically Change Production

The [Activation / Reveal contract](ACTIVATION.md) now supplies pure planning of
evidenced relevance, renderability and candidate presentation impact. Planning
retains accepted history and does not activate dormant geography or acquire
Topic metadata. Existing Course/project projection APIs remain compatible.

Typed loaders dispatch `global_knowledge_catalog` separately from
`personal_progress` (missing type retains legacy semantics). Global observations
are validated but excluded from the active source fingerprint and `model.json`.
The updater reports global additions separately, using the accepted active
catalog as its explicitly named comparison basis. It does not claim a stored
previous global checkpoint. Global comparisons can report GLOBAL_NEW_CATEGORY,
GLOBAL_NEW_REFERENCE, GLOBAL_NEW_TOPIC, GLOBAL_METADATA_CHANGE, GLOBAL_REPARENT,
GLOBAL_RELATION_CHANGE, REFERENCE_RESOLVED and GLOBAL_CATALOG_ONLY. Disappearance
produces a MISSING candidate, not a deletion instruction.

Consequently this ingestion yields zero displacement, no checkpoint change,
generation zero and byte-identical production assets. All global records remain
data groundwork. No changes to layout/runtime/routing files are required.

## Sanitizer and security

```bash
python -B scripts/sanitize-hyperskill-knowledge-map.py --input /absolute/local/capture.har --dry-run
python -B scripts/sanitize-hyperskill-knowledge-map.py --input /absolute/local/capture.har --write-observation
```

The offline sanitizer constructs new objects using only these allowlists:

- Global unfiltered `/api/topic-relations`: id, title, parent_id, children,
  descendants. Scoped `track_id`/`project_id` responses are excluded.
- `/api/topics/<observed-id>`: id, title, is_group, parent_id, children,
  hierarchy, root_id, theory, prerequisites, explicit_prerequisites (kind/source
  only), followers. Only explicit `is_group: false` entities are admitted.
- Learning activities: topic_id and title only. Activity IDs are never copied.
- Provenance: method, normalized relative endpoint path, response JSON type,
  content-derived source ID, safe pagination fields and capture timestamp range.

No headers, raw request URLs, account/progress/study-plan IDs, lesson blocks,
solutions, telemetry or platform flags pass through. Unknown response fields
are not copied. A recursive output guard rejects sensitive field names, bearer
credentials, secret assignments, JWT-like values, email addresses, private URL
queries and local filesystem paths. Approved titles containing these patterns
fail closed and require review. CLI errors are generic, never raw exceptions.
Global observations are also checked against their strict field schema when
loaded. Per-field facts reference sanitized endpoint sources; each source maps
back to its observation in the composed catalog.

Capture completeness requires contiguous decoded global pages, consistent
page sizes, full intermediate pages, boundary flags, unique IDs, identical
repeated public records, and complete structural references. This capture has
pages 1–9, counts 100 × 8 + 49. The API supplies no total; `reported_total` stays
null. Duplicate captures with missing HAR bodies are harmless only if each
logical page has a valid complete body. Malformed selected bodies fail closed.
Topic/prerequisite/follower coverage remains PARTIAL independently of complete
taxonomy pagination. This implementation intentionally accepts only PARTIAL
snapshots; authoritative replacement needs a later completeness contract.

Sanitized observations contain `observation_type`, two schema versions, capture
interval, snapshot status, categories, Topics, unresolved references, separate
hierarchy/prerequisite/follower records, source pages, coverage and validation.
Per-field provenance is stored with described entities. Follower endpoints may
be Categories or unresolved references; they are numeric references here and
are not falsely promoted to Topic-dependent edges. Prerequisites and followers
retain independent evidence. Explicit-prerequisite kind/source records stay
in Topic metadata with their own fact-source field.

Output is deterministic, including reordered HAR entries and duplicate bodies.
An identical write is a no-op. A differing observation on the same capture date
is refused, preserving immutable history pending a separately named, reviewed
snapshot. Raw HARs remain outside the repository and are never imported.

## How Future Courses Activate Existing Knowledge

Collect explicit course membership. Reuse resolved/partial IDs. Relevant
unresolved references may later receive targeted explicit Topic evidence;
the acquisition mechanism remains future work. Wholly unknown IDs are new
candidates requiring evidence. Membership-only
changes must not duplicate entities. Presentation activation is a later reviewed
operation; this API deliberately does not promise usable geometry for dormant
branches.

## How Future Projects Add Evidence

Collect exact Project/Stage requirement evidence, resolve IDs against this
catalog, attach project evidence, refresh personal state separately, then
compute scope. When relevant entities and accepted geometry already exist,
expected semantic additions are NEW_TOPIC = 0 and NEW_CATEGORY = 0, with zero
displacement for evidence/state changes. Dormant branches without geometry
still require a later activation review.

## Geography, scale and next phases

Choose data-first activation: store the complete taxonomy now and allocate
geometry only on first approved scope activation. Laying out 3,955 positions
now would expand checkpoints and Fit All while making the personal map harder
to read. Two-level region reservations may help later, but no slots are reserved
or generation changed now. The actual 2.5 MB sanitized snapshot is practical for
offline data processing; it is not a global V6 performance benchmark. V6 still
loads 135 active positions. Its single-root model cannot consume a five-root
forest directly.

Next phases: design targeted resolution only when explicit course/project
evidence identifies relevant unresolved IDs; design immutable refresh naming
and conflict review; expand data-only course membership evidence. The failed
Category bulk-resolution pilot does not need repeating. Incremental activation,
region reservation and UI scope controls remain separate presentation work.
Keep Course 8 and production byte/geometry tests as regression fixtures.

## Validation baseline and legacy map contract

The older map builder produces an editorial projection with domains, clusters
and derived connections. It is still tested in disposable roots. Its output is
not the installed V6 `model.json`, which contains normalized active tables and
indexes. The Map suite's formerly stale installed-output assertion now rebuilds
the current V6 production package from accepted active data, checkpoint and
geometry in memory, and compares all production files byte-for-byte. This keeps
the meaningful installed-output regression instead of accepting a red test or
overwriting Production with a historical format.

Hosted read-only validation runs Global Catalog, Atlas/Hardening, Graph,
Importer, Map and Packaging contracts plus accepted browser/production checks.
It checks Production/State hashes and rejects repository write leakage. The
optional real-HAR reproducibility test runs locally only; raw captures are
never needed or uploaded by CI.

Tests:

```bash
python -B -m unittest discover -s scripts/tests -p test_global_catalog.py -v
# Optional real-HAR idempotency check; raw input stays local:
HYPERSKILL_GLOBAL_HAR=/absolute/local/capture.har python -B -m unittest discover -s scripts/tests -p test_global_catalog.py -v
```
