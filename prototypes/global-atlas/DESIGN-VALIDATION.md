# Global Atlas design and scale experiment

Baseline: `8e4bc0f4b5fb10ed1d606b34011eb39b562de881`. Experimental,
read-only, non-authoritative. No production migration or new activation.

## Architecture and source boundaries

`build.py` loads existing normalized data through `snapshot.load_source`, joins
through the existing `Catalog` and queries its Course/Project projection APIs.
It reads accepted history only to label the personal overlay. Its sole output
is `generated/catalog.json` under this prototype. No presentation allocator,
activation planner/approval API or Production builder is invoked. The generated
file is reproducible, disposable output, not a manually maintained taxonomy.

One entity registry is shared by every scope. Stable typed IDs are keys;
titles are search/display values only. Categories, Topics and structural
references remain different types. Course, Project and Stage records keep
their stable IDs separately as scope metadata rather than geography nodes.
Course membership arrays support many-to-many joins. Project requirements
retain accepted edge IDs, Stage IDs and evidence IDs. Stage records preserve
explicit incremental and cumulative arrays without inferring cumulative facts.
Personal observation rows retain literal learning/verification states.

Captured resolution is 1 RESOLVED_TOPIC, 88 PARTIAL_TOPIC and 3,017
UNRESOLVED_REFERENCE. Accepted metadata is a separate richer evidence source;
partial capture does not retract it. References have ID, parents and source
provenance, **no title, URL, theory or fabricated `topic:<id>` identity**.
“Unresolved reference #333” is an interface description, never Topic metadata.

The model retains 3,952 structural hierarchy pairs independently of canonical
Topic parentage. Leaves 36 and 1425 each have two memberships. For a single
visual position, explicit canonical parent wins where supplied; otherwise the
first stable sorted structural parent determines placement. All structural
parents remain available in the inspector and scope ancestor closure. Selecting
a shared leaf draws its additional membership connection. No second leaf copy
is allocated; the secondary parent's rectangle is not a second entity inventory.

## Renderer and navigation

Independent Canvas renderer and balanced binary nested treemap partition, with
five equal root navigation regions arranged in a 3×2 grid. Root area is a
navigation choice, **not proportional universe size**. Within each root, leaf
weights drive partitioning. Each Category encloses descendants with a header
band; a leaf has one rectangle. No force simulation, thousands of DOM elements
or all-edge drawing. Screen culling and semantic zoom suppress tiny shapes and
small labels. Screen-space collision checks and a 250-label budget prevent
label explosion. Detailed identity and provenance are in DOM inspectors.

Fit Global, Fit Scope, root buttons, entity/branch focus, parent/path buttons,
Back camera history, pointer pan, wheel/button zoom, keyboard pan/zoom and a
clickable viewport minimap supply orientation. Search scans the complete known
registry, including stable reference IDs, exposes at most 40 result buttons and
asks for query refinement when necessary. Search is independent of the selected
scope. Branch focus provides progressive detail through camera scale and
culling; there is no separate persisted expansion state or branch hiding API.

Scopes only change highlight sets; geometry and entity counts remain fixed:

| Scope | Exact source and behavior |
| --- | --- |
| Global | All 3,955 known positions, five separate roots. Blue outline identifies accepted entities. |
| My Atlas | Accepted ACTIVE_HISTORY IDs: 46 Categories + 89 Topics. This joins personal identity into global geography; it does not reuse or replace personal coordinates. |
| Course | Explicit Course 8 Category/Topic membership plus structural ancestor context; purple highlight. Ancestors are never reclassified as explicit Course membership. Selector consumes Course inventory, supporting later evidenced Courses. |
| Project | Project 113: 26 distinct requirement targets and all structural ancestors; amber highlight. Stage selector highlights exact Stage requirement edges (Stage 617: 12 Topics). All eleven known Projects are selectable; ten show requirements UNKNOWN. |

An optional personal layer adds green learned Topics and white verified rings,
without overloading the initial overview. Missing personal evidence stays unknown.
Required does not imply learned, verified or applied. Resolved/partial inactive
Topics retain Topic circles and their captured resolution in details; unresolved
references use gray rectangles and diamonds. Current real Topics happen all to
be active, so no invented inactive real Topic is added just to exercise styling.

## Real capture and initial measurements

849 Categories + 89 evidenced Topics + 3,017 references = **3,955 positions**.
There are 3,106 distinct structural leaves and 3,108 leaf memberships, 844
Category hierarchy pairs, five roots and maximum leaf depth eight. Full model
also contains one Course, eleven Projects and five loaded Stages. Learning
remains 31 learned / 12 verified.

Measurements from headless Chromium 149 on this workstation, 1440×900,
device scale 1, offline interception of real generated data; 60 repeated
search/scope samples. Browser dependencies are external and were not added.
See `tests/browser-results.json` for exact measured values and environment.

| Measurement | Initial validation run |
| --- | --- |
| Python projection/build | Approximately 1.2 seconds; 1,976,924 bytes output |
| Browser fetch + parse | 25.6 ms |
| Browser indexing + layout | 6.0 ms |
| Initialization (through setup, before scheduled paint) | 34.9 ms |
| Overview painted positions / labels | 3,947 / 21; remaining tiny shapes culled |
| DOM elements (including focused inspector) | 77 |
| Draw time, median / p95 | 1.7 / 2.2 ms |
| Search latency, median / p95 | 0.2 / 0.3 ms |
| Scope computation, median / p95 | Below 0.1 / 0.1 ms |
| Scope-to-paint harness, median / p95 | 33.2 / 33.3 ms, deliberately waits two animation frames |
| Deep Category focus | `category:2930`, 10 painted objects, two labels; 0.1 ms draw |
| Depth-eight reference focus | `reference:2931`, 10 painted objects, one label; 0.2 ms draw |
| JS heap indication | ~9.6 MB; Chromium estimate, excludes native Canvas/GPU/process memory |

These are local scale measurements, not device-wide guarantees or production
service budgets. Broad timing guards catch gross regressions (2 s initialization,
50 ms search/scope, 100 ms draw); they are intentionally looser than measurements.
Screenshots cover Global, My Atlas, Project Stage and deep reference focus.

## Concrete answers to the experiment questions

1. **3,955 positions:** useful for overview density, location and exploration;
   not individually readable simultaneously. Camera focus is necessary.
2. **Five roots:** coexist in distinct named regions and minimap; equal area
   keeps small roots navigable without implying equal record counts.
3. **Personal joins:** exact 135 accepted identities join without duplicates.
   Global coordinates are exploratory, not accepted personal geometry.
4. **Shared Courses:** yes. Twenty additional synthetic Course overlays reuse
   the same 89 Topic IDs in memory; entity count remains 3,955.
5. **Shared Projects:** yes. Twenty synthetic Projects reuse Project-113 targets
   with separate requirement records; no Topic duplication.
6. **Unresolved references:** safe separate type; metadata never invented.
   Synthetic Course relevance to reference 333 leaves it unresolved.
7. **More Projects:** add scope records and evidenced requirement edges;
   UNKNOWN remains distinct from a complete empty requirement inventory.
8. **More Courses:** add explicit membership records; scope closure operates on
   the same IDs. Membership alone does not change geography or resolve references.
9. **Search:** sub-millisecond p95 in this run, including unresolved IDs; 40
   displayed results cap DOM cost. Titles cannot search unresolved references.
10. **Focus/navigation:** root controls, minimap, breadcrumbs, parents, Back and
    Fit commands remain usable; deep branch/leaf focus is smoke-tested.
11. **Desktop usability:** visually inspected 1440×900; density overview is
    workable with search/focus. This is not a user study or physical-device test.
12. **V6 reuse:** normalized loaders, Catalog semantics, stable IDs, evidence and
    progress contracts; concepts of scoped coverage, inspector and camera fit.
13. **Keep separate:** V6 single-root model, cards/trays, persistent geometry,
    checkpoint allocation, activation/state mutation and packaging.
14. **Production renderer:** recommend a separate forest-aware overview renderer
    or renderer layer rather than feeding the full forest into current V6.
    Canvas is adequate here; WebGL and large dependencies are not justified yet.
15. **Bottlenecks:** data resolution is the main knowledge limitation (3,017
    references). Labels/edge readability dominate visualization risk; current
    layout/render/memory are inexpensive. Rendering all future relation edges
    or allowing unbounded labels would degrade clarity before node throughput.

## Precise collection gaps and minimum future evidence

Current `courses.json` has **only Course 8**, `projects.json` eleven Course-8
Projects, and `stages.json` only the five Project-113 Stages. The taxonomy itself
does not supply other Course memberships, Project requirements, or personal
progress. This prototype performs no scraping. The existing offline sanitizer
does not constitute a collector for these missing Course/Project facts.

| Entity | Minimum useful evidence contract | Current gap / handling |
| --- | --- | --- |
| Course | Positive Course ID, explicit title, explicit Topic-ID and Category-ID membership inventories with completeness, explicit Project IDs, returned public counts, capture date, source endpoint/method, evidence ID and confidence | Other Courses entirely absent. Null/incomplete inventories must not mean zero; counts do not establish individual membership. Retain explicit membership independently from derived ancestor context. |
| Project | Positive Project ID, explicit title, language, ordered Stage-ID inventory, capture date and provenance/evidence | Eleven metadata records known; no additional Course's Project inventory. Listed Stage IDs alone do not load Stage records or requirements. |
| Stage | Positive Stage ID, explicit position, Project ID, title, required Topic-ID inventory, completeness, cumulative inventory only when explicitly returned, source/date/evidence | Other ten Projects have public Stage IDs but no loaded Stage/requirement records. They cannot be rendered as zero-requirement Projects. Deduplicate targets across Stages while retaining each edge's Stage context and evidence. |
| Topic resolution | Explicit typed Topic identity/title, structural memberships and field provenance; detailed theory/relations only when explicitly evidenced | Target only unresolved IDs identified by future explicit Course/Project membership. Resolution observation must satisfy existing Catalog promotion contract; no guessed titles, URLs or mass crawl. |

Collection should retain immutable sanitized observations, validate stable IDs,
inventory completeness and source evidence, and explicitly distinguish missing
fields, unknown/incomplete sets and confirmed empty sets. Count mismatches and
metadata/parent conflicts need review rather than silent substitution. No
learning/verification/application inference follows from these records.

**Course-by-Course membership materially improves Global Atlas:** it answers
which known regions a future Course actually uses, exposes overlap, and
identifies relevant unresolved IDs. Taxonomy alone cannot answer those questions.
The existing many-to-many data model can consume this evidence without creating
new copies of Topics or activating personal geography.

**Project Stage requirements materially improve Project Focus:** they establish
the exact required IDs and Stage progression, enable precise Stage selection and
cross-Project overlap, and separate partial coverage from UNKNOWN. A Course's
Topic list, Project title or completion status cannot establish requirements.

## Tests, safety and limitations

New Python and Node tests validate real counts/roots/resolution, deterministic
repeated output, exact personal/Course/Project overlays, geometry containment,
maximum depth, scope invariance and deduplication. Synthetic cases are memory
only: twenty shared Courses, twenty shared Projects, 938 active identities
(all 849 Categories plus 89 Topics), and Course-relevant unresolved reference.
They never write synthetic normalized facts, publish membership or activate
anything. Browser smoke/performance tests use the real dataset and isolate all
outputs here. Protected tree hashes are checked around unit tests.

Validation results and pre/post protected-tree digests are recorded in
`tests/validation.json` after final checks. Production assets, state, accepted
history, checkpoint allocation, Generation 0 and Knowledge data remain
byte-identical; unrelated original untracked files are preserved. No commit,
push, publication, real activation event or new factual membership is performed.

Final local results: 190 existing tests ran (189 PASS, one optional external-HAR
test skipped), seven Production packaging tests PASS, six prototype Python tests
PASS including the Node core contracts, prototype browser/performance smoke PASS,
existing graph browser smoke PASS. Accepted Atlas browser regression: 1,141 checks
PASS, 18 viewport/theme scene sequences identical. Read-only updater check:
NO_CHANGE, Generation 0, zero displacement and no state change. All 14 Production
assets, four state files, eleven Knowledge files and 582 original untracked files
retain their pre-work bytes (611 files total). Hosted CI is not run because this
work is not committed or pushed; no workflow changes are introduced.

Limitations: exploratory treemap layout can reflow when taxonomy changes, and
does not promise future frozen global geography. Adding Course/Project overlays
to the same capture does preserve geometry. The primary placement of shared
leaves biases the region inventory; secondary memberships are shown on demand,
not duplicated. Many personal entities are spread across taxonomy, so Fit Scope
can still be broad. Canvas accessibility relies on the search, inspector and
root/path controls; a complete accessible hierarchy browser remains future work.
No prerequisite edge layer, crawler, activation integration or production theme
parity. Larger datasets, many requirement edges, low-power devices and human
navigation studies need additional testing. The 250-label policy may suppress
otherwise useful labels in very dense views.

**Recommendation: keep the prototype and iterate further.** It is a suitable
data/renderer experiment for a future Global Atlas, not a production replacement
or evidence that personal geometry can be safely expanded without review.
