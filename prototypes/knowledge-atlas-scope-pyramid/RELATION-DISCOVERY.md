# Course / Project / Stage relation API discovery

Current result: **C — PROJECT / STAGE RELATION SEMANTICS RESOLVED; FULL RELATION ACQUISITION READY**.

The acquisition contract is resolved: counters are not ID relations; Project entry prerequisites remain UNKNOWN without an explicit list; Stage-specific necessary knowledge is evidenced; complete Project study-plan knowledge requires an explicit Project-level source interpretation. The current Project UI supplies that interpretation for the two examined Projects. Unknown optional field meanings remain unknown and do not generate edges.

This semantic investigation on 2026-10-07 changes only this report. Layout acceptance remains unchanged. The earlier discovery below used Course 8 / Course 2 and Project 113 / Project 380; this follow-up inspected only the two existing Projects, their UI sections and relevant public client modules. No third control, catalog enumeration, bulk acquisition, commit, push or deployment occurred. Accepted Project 113 **26** / Stage 617 **12** facts remain unchanged.

## Course endpoints and membership

| Purpose | Observed endpoint / fields | Semantics |
| --- | --- | --- |
| Catalog/list | `/api/tracks?page_size=2&page=1` and page 2; `tracks[].id,title` | Course semantic ID is the API Track ID; both pages returned two rows and `has_next=true`. |
| Metadata | `/api/tracks/8`, `/api/tracks/2` | One identified object with explicit title, `topics_count`, public/non-beta flags. |
| Complete scoped taxonomy | `/api/topic-relations?track_id=<id>&page_size=100&page=<n>` | Returned rows explicitly evidence Category membership; their `descendants` arrays explicitly name scoped Topic IDs. |
| Topic membership | Union of all filtered rows' `descendants` | Deduplicate IDs across Categories. Checked against child IDs minus the complete returned Category ID set; the two independent constructions match for both Courses. |
| Category membership | IDs of all returned filtered relation rows | This is explicit API evidence. Do not synthesize membership from the Global ancestor closure. |

| Course | Title | Category page sizes | Explicit Categories | Distinct explicit Topics | Metadata Topics | Used Global roots |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 8 | Introduction to Java | 46, terminal | 46 | 89 | 89 | 1162 |
| 2 | Python Developer | 100 + 24, terminal | 124 | 275 | 275 | 1162, 525, 4055 |

Course 8's complete Topic and Category ID sets match the accepted seeds exactly, not merely their counts. Course 2 uses the same endpoint family and existing Global Category/Topic ID system. All 124 Category IDs and 275 Topic IDs resolve in the current Global Catalog. Its Computer science root contains 273 Topics; the other two used roots contribute one each. A single root's descendants must not be mistaken for the complete Course.

Safe primary provenance: [Course 8 metadata](https://hyperskill.org/api/tracks/8), [Course 8 scoped relations](https://hyperskill.org/api/topic-relations?track_id=8&page_size=100&page=1), [Course 2 metadata](https://hyperskill.org/api/tracks/2), [Course 2 relations page 1](https://hyperskill.org/api/topic-relations?track_id=2&page_size=100&page=1), [page 2](https://hyperskill.org/api/topic-relations?track_id=2&page_size=100&page=2).

### Pagination and UNKNOWN versus empty

Observed envelopes contain only `meta.page`, `meta.has_next`, `meta.has_previous`; **no total/count field** is provided. Array length is the page's returned row count. `topics_count` belongs to Course metadata and counts Topics, not Category pages or taxonomy edges. Continue while `has_next` is true, validate page numbers/identities, and terminate on the explicit terminal flag. A short page alone is not the general stopping rule.

Course 8 page 2 after its terminal page returns 404. Course 2 page 2 returns 24 rows and `has_next=false`. Both paged list endpoints also exhibit `has_previous=true` on page 2. Catalog totals remain UNKNOWN; discovery did not enumerate them.

A nonexistent Course ID returns **200 with an empty relation array**, while `/api/tracks/<same-invalid-id>` returns 404. Thus an empty filtered hierarchy does not prove an existing empty Course. Validate metadata existence and identity first. Missing, inaccessible, malformed, interrupted or unvalidated scope evidence is UNKNOWN, never an empty membership set. A validated existing Course with complete terminal empty evidence can be represented as explicitly empty, with metadata counts reconciled separately. No real empty Course was found in this small sample.

`/api/topics?track_id=8&page_size=100&page=1` returns 100 unrelated Topic objects with `has_next=true`; it does **not** restrict membership to the 89 Course Topics. Reject it as a Course membership source. Do not infer membership from titles or silently accept an unsupported filter.

## Project prerequisite vs Stage requirement semantics

### 1. Reconstruct Project 380 without inventing P

The premise “Project 380 has a known twelve-ID prerequisite set” is **not supported by the saved artifacts**. `GET /api/projects/380` returns `projects[0].n_last_prerequisites = 12`, a scalar. Its complete field inventory contains no Project prerequisite-ID array. The previously observed list response has the same scalar. Therefore:

- `P`, meaning an explicit **Project entry-prerequisite Topic-ID set**, is **UNKNOWN**, not empty.
- The observed scalar is `C_last = 12`; **it does not establish |P| = 12**.
- `S_s = stages[].prerequisites` is a real, explicitly returned ID array for each Stage.
- `U = union(S_s)` is a calculated set with **15** distinct IDs. The union alone initially remains a diagnostic, not automatic Project membership.

All sets below are sorted for reporting; API array order and Stage order are separate facts.

| Stage s | Explicit order | S_s: `prerequisites` | Count | Separately returned `all_prerequisites` |
| ---: | ---: | --- | ---: | --- |
| 2266 | 1 | `15, 147, 148, 193` | 4 | `15, 147, 148, 193` |
| 2267 | 2 | `14, 146` | 2 | `14, 15, 146, 147, 148, 193` |
| 2268 | 3 | `9, 27, 30, 31, 112, 113, 307, 518, 1248` | 9 | `9, 14, 15, 27, 30, 31, 112, 113, 146, 147, 148, 193, 307, 518, 1248` |

```
U = {9, 14, 15, 27, 30, 31, 112, 113, 146, 147, 148, 193, 307, 518, 1248}
|U| = 15
P = UNKNOWN
|P| = UNKNOWN       (observed counter C_last = 12)
P ∩ U = UNKNOWN
P - U = UNKNOWN
U - P = UNKNOWN
```

**Differing IDs/titles:** neither `P - U` nor `U - P` can be printed as an ID list because P has never been observed. They are UNKNOWN, not `{}`. Selecting any twelve of the fifteen Topics would manufacture evidence. The following is the complete **U inventory**, not a claimed difference set; every title comes from the existing Global Catalog by exact ID:

| Topic ID in U | Existing Global Catalog title |
| ---: | --- |
| 9 | String |
| 14 | Types and variables |
| 15 | Introduction to Java |
| 27 | Integer types and operations |
| 30 | Comments |
| 31 | Characters |
| 112 | Naming variables |
| 113 | Reading user input with Scanner |
| 146 | Arithmetic operations |
| 147 | Basic literals: numbers, strings and characters |
| 148 | Writing first program |
| 193 | Printing data |
| 307 | Increment and decrement |
| 518 | Formatted output |
| 1248 | Coding style conventions |

The expected `|P|=12` is thus corrected as a type/provenance mistake, without deciding that the two counts are inconsistent or that three Topics are missing. No separate Project prerequisite relation was established by that scalar.

### 2. Endpoint, enclosing object and terminology provenance

| Observed fact / set | Endpoint (GET unless noted) | Response field / enclosing object | Project / Stage identity | Source terminology and limits |
| --- | --- | --- | --- | --- |
| C_last=12; C_first=4 | `/api/projects/380` and prior `/api/projects?page_size=2&page=1` | `projects[].n_last_prerequisites`, `n_first_prerequisites`; Project object | Project 380; no Stage ID or Topic IDs in these fields | API names **counts of prerequisites** with first/last qualifiers. It does not say entry prerequisites, recommended Topics, or provide a membership list. |
| P | No identified endpoint/list field | None observed | Project 380 | Project entry-prerequisite ID relation remains UNKNOWN. |
| S_2266, S_2267, S_2268 | `/api/stages/2266`, `/api/stages/2267`, `/api/stages/2268`; UI also requests `/api/stages?project=380&page=1` | `stages[].prerequisites`; Stage object | `project=380`; respective `id=2266/2267/2268` | Explicitly called **prerequisites**, associated with a named Stage. The UI gives additional necessary-learning context, below. |
| Separate Stage arrays | Same Stage endpoints | `stages[].all_prerequisites`; Stage object | Same Project/Stage identities | Explicitly called **all_prerequisites**. Not automatically renamed “cumulative knowledge.” |
| U | No source field directly named U | Computation over complete S_s arrays | Project 380, all three explicitly declared Stages | Initially a derived diagnostic; qualified as Project study-plan knowledge only with the explicit UI contract below. |
| C_last=26 | `/api/projects/113` | `projects[].n_last_prerequisites`; Project object | Project 113 | Same numeric counter family as Project 380's 12, not an ID relation. |
| S_614 … S_618 | `/api/stages/<id>`; UI also requests `/api/stages?project=113&page=1` | `stages[].prerequisites`; Stage object | `project=113`; explicit Stage ID | Same ID-array family as Project 380's S_s. |
| Accepted Project 113 26 | Historical `data/knowledge/edges.json`, `stages.json`, `evidence.json` | `project_requires` edges each carrying `stage_id` and `stage-<id>` evidence; Stage's `required_topic_ids` is the local snapshot alias for API `prerequisites` | Project 113; Stage evidence 614–617 | These facts are Stage-sourced necessary knowledge, not a Project scalar converted into IDs. |
| Accepted Stage 617 12 | `/api/stages/617`, historical `stage-617` evidence | `stages[].prerequisites`; twelve stage-context edges in the accepted snapshot | Project 113 / Stage 617 | Exact local array, not its 26-ID `all_prerequisites` array. |
| Topic-to-Topic dependencies seen while UI resolves labels | `/api/topics?ids=<exact Stage IDs>&page=1` | `topics[].prerequisites`; Topic object | `topics[].id` identifies the **requiring Topic**, not a Project or Stage | Different enclosing type and different relation. Never mix these dependency arrays into Project or Stage membership. |

Individual Stage responses and the earlier declared-ID batches agree on retained safe fields. The UI's Project-filtered Stage list is terminal (`has_next=false`), has exactly the Project's declared Stage IDs, and agrees on reciprocal `project`, explicit `order`, titles and local ID arrays. The first/last counter fields never identify the members of any P set.

Primary API sources: [Project 380](https://hyperskill.org/api/projects/380), [Project 380 Stage list](https://hyperskill.org/api/stages?project=380&page=1), [Stage 2268](https://hyperskill.org/api/stages/2268), [Project 113](https://hyperskill.org/api/projects/113), [Project 113 Stage list](https://hyperskill.org/api/stages?project=113&page=1), [Stage 617](https://hyperskill.org/api/stages/617).

### 3. Repeat the decomposition for Project 113

`P_113 = UNKNOWN`: no entry-prerequisite ID list was present. `C_last_113=26` is a scalar from the same **counter family** as Project 380's 12.

| Stage s | Explicit order | S_s: `prerequisites` | Count | Separately returned `all_prerequisites` |
| ---: | ---: | --- | ---: | --- |
| 614 | 1 | `15, 147, 148, 193` | 4 | `15, 147, 148, 193` |
| 615 | 2 | `14, 30, 112, 113, 1248` | 5 | `14, 15, 30, 112, 113, 147, 148, 193, 1248` |
| 616 | 3 | `9, 27, 31, 146, 307` | 5 | `9, 14, 15, 27, 30, 31, 112, 113, 146, 147, 148, 193, 307, 1248` |
| 617 | 4 | `25, 36, 87, 88, 89, 152, 259, 260, 348, 1476, 1761, 3538` | 12 | `9, 14, 15, 25, 27, 30, 31, 36, 87, 88, 89, 112, 113, 146, 147, 148, 152, 193, 259, 260, 307, 348, 1248, 1476, 1761, 3538` |
| 618 | 5 | `` | 0 | `9, 14, 15, 25, 27, 30, 31, 36, 87, 88, 89, 112, 113, 146, 147, 148, 152, 193, 259, 260, 307, 348, 1248, 1476, 1761, 3538` |

```
U_113 = {9, 14, 15, 25, 27, 30, 31, 36, 87, 88, 89, 112, 113, 146, 147, 148, 152, 193, 259, 260, 307, 348, 1248, 1476, 1761, 3538}
|U_113| = 26
P_113 = UNKNOWN
|P_113|, P_113 ∩ U_113, P_113 - U_113, U_113 - P_113 = UNKNOWN
```

All 26 U_113 identities resolve through Global. The accepted 26 `project_requires` targets exactly equal these Stage-sourced IDs; the accepted Stage 617 subset exactly equals its twelve `prerequisites` IDs. Every accepted Project edge's stage context and evidence was checked; `data/knowledge/SCHEMA.md` explicitly documents that provenance. No accepted fact, evidence or source hash was changed.

**Answer to the field-family question:** the accepted **26 IDs** come from the same **Stage array family** as Project 380's **15 IDs**. They do **not** come from a twelve-ID Project field family, because no such list has been observed. The two Project counters (26 and 12) share their own numeric field family. Project 113's counter/set count equality does not establish a general set-construction rule.

### 4. Normal authenticated UI cross-check and source behavior

Project 380 was opened normally in the isolated authenticated Chrome profile. Only its semantic UI labels, Topic-card links and relevant API responses were inspected; no lesson, assignment description or solution prose was scraped. All three Stage sections were expanded without starting or implementing a Stage, marking learning, or changing progress.

The Project panel is headed **“What you'll learn.”** Its visible generic helper describes the plan as including **“all the necessary topics from your course to get it built.”** The three Stage sections together show **15 Topic cards** and their respective Stage implementation links: four / two / nine cards. Expanding sections requests exactly S_2266, S_2267 and S_2268 as `/api/topics?ids=...`; the returned Topic objects carry exact semantic IDs. No title matching or conversion of lesson-step IDs to Topic IDs was used. This is explicit **Project necessary-study-plan knowledge**, rather than a supposed twelve-member entry prerequisite list. [Project 380 UI](https://hyperskill.org/projects/380).

Project 113 exposes the same panel and component contract. Expanding its Stage 4 loads precisely Stage 617's twelve-ID `prerequisites` array and displays those Topic cards before its implementation link. [Project 113 UI](https://hyperskill.org/projects/113).

The versioned [Project view client](https://hs.azureedge.net/static/hyperskill.org/ProjectView-DsMtEye2.js) binds each returned Stage's `prerequisites` array to the Topic cards in that necessary-study-plan panel. The [Stage preview client](https://hs.azureedge.net/static/hyperskill.org/StagePreview-CID3vlPl.js) loads its Topic list from the same local Stage field. These behaviors establish the mapping; set inclusion alone is not the semantic evidence.

Separately, the [Stage implementation client](https://hs.azureedge.net/static/hyperskill.org/StageImplement-CugVvPEO.js) passes Project `n_last_prerequisites` as the numeric **topicsCount** prop to progress/completion modals. It does not extract prerequisite member IDs from the counter. No completion or implementation action was performed; this was a read of public client source behavior. The exact backend derivation of the counter remains unestablished. Neither a stale-cache explanation nor a second twelve-ID relation is asserted.

Read-only OPTIONS requests for the Project and Stage endpoints returned generic resource metadata without field definitions. They supplied no further temporal interpretation of `all_prerequisites`. Public client fingerprints were recorded outside Git; no whole client bundle, headers or profile data were persisted in the repository.

**Third control:** not necessary. The two known Projects plus the visible panel and its source binding establish the distinction between counters, Stage ID arrays and the Project necessary-study-plan relation. A third count match would not establish a missing P list.

### 5. Final semantic definitions and classifications

| Source relation or field | Classification requested in this investigation | Definition supported by the evidence |
| --- | --- | --- |
| `Stage.prerequisites` | **A — stage-local necessary learning knowledge**, with API terminology preserved | Explicit Topic IDs assigned to that Stage's necessary study-plan section. Preserve the source name `prerequisites`; the normalized `stage_requires` alias means this evidenced Stage knowledge relation. It is not all Topics used at runtime, proof of application, or a claim that the server enforces a pre-entry gate. |
| `Stage.all_prerequisites` | **E — precise temporal/operational semantics unestablished** | A separately observed ID array explicitly named `all_prerequisites`. In both samples it equals the prefix union of local arrays, but that is a calculated consistency fact. Without explicit field documentation or an equivalent UI binding, do not promote it to B “cumulative knowledge through this Stage,” C “before entry,” learned knowledge or membership. Retain its native field and IDs as opaque typed evidence. |
| Hyperskill Project necessary-study-plan panel | **B — complete Project necessary learning knowledge in the evidenced study-plan context** | The source explicitly identifies all necessary Topics to build the Project and renders the complete declared Stage Topic sections. This supplies the Project-level equivalence needed before aggregating local Stage lists. It does not claim runtime application or entry knowledge. |
| Project entry prerequisites P | **F — unclear / not evidenced** | No explicit Project entry-prerequisite ID source observed. UNKNOWN, even though the API has numeric first/last counters. |
| `Project.n_first_prerequisites`, `n_last_prerequisites` | Numeric metadata; **not a Topic relation** | Preserve exact source names and values. Client use of the last counter as topicsCount is evidenced. No membership, recommendation, entry condition or backend counting algorithm is inferred. |
| Topic object's own `prerequisites` | Topic dependency relation, outside this Project/Stage decomposition | IDs required by that Topic; not the Stage's local list and not a Project prerequisite list. |

The prefix-union arithmetic for `all_prerequisites` is recorded for diagnostics only. It does not determine the classifications above. Source naming, UI context and client binding determine the relations used for scopes.

### 6. Normalized relation model — keep distinct relations and UNKNOWNs

Preserve raw typed observations and their enclosing types/field paths before normalization. The following is a **future contract**, not a data/schema modification made in this task:

| Normalized relation / evidence | Status and rule |
| --- | --- |
| `project_prerequisites(project_id, topic_id)` | Only populate from an explicit **Project entry-prerequisite ID list** with matching source terminology/context. UNKNOWN for both examined Projects; never construct from a scalar or the first Stage. |
| `stage_requires(stage_id, topic_id)` | Known from the Stage's `prerequisites` array under the evidenced necessary-learning interpretation. Store original field name and Stage/Project provenance. Explicit `[]` is known empty. |
| `stage_all_prerequisites_observation(stage_id, topic_ids)` | Preserve native array separately; temporal semantics E. Do not substitute for stage_requires or label as cumulative learned knowledge. |
| `project_requires(project_id, topic_id)` | Known only where an explicit Project requirement/use list **or a source-established complete necessary-study-plan contract** exists. Store derivation plus Project-level UI/source evidence. A bare Stage union is insufficient. |
| `project_count_observation(project_id, source_field, value)` | Store first/last numeric counters separately as metadata. Do not use them to invent or trim edges, or as authoritative ID-set cardinalities. |

For the two examined Projects, define `Q` as the Project UI's complete necessary-study-plan Topic set. The explicit UI contract and Stage-to-card binding give `Q_380=U_380` (15) and `Q_113=U_113` (26). **Q is not P.** These are justified study-plan aggregates, not inferred entry-prerequisite relations. The Project 380 counter of 12 remains independently retained metadata.

This report therefore supports future `project_requires` for these **evidenced necessary-study-plan sets**, while `project_prerequisites` remains UNKNOWN. A source can later evidence entry prerequisites as another relation; keep both and compare their actual ID sets at that time. Do not retroactively name Q “entry prerequisites.” The accepted Project 113 26 / Stage 617 12 relations remain untouched.

### 7. Which relation seeds each Pyramid

**PROJECT scope:** seed the evidenced `project_requires` / necessary-study-plan relation, with its explicit source context and completeness. The investigated Project 380 can be evidenced with Q_380's **15 IDs**, because the Project panel explicitly establishes necessary-study-plan membership. It must never be seeded with twelve arbitrarily selected IDs, Project counters, entry prerequisites, Topic dependency closure or an unqualified Stage union. No Project 380 Pyramid was rendered or added during this task.

**STAGE scope:** seed `stage_requires` mapped to that Stage's explicitly evidenced local `prerequisites` IDs. Stage 617 remains twelve. Do not use its 26-ID `all_prerequisites` array as the local seed. Preserve Stage title/order/Project identity independently.

If another Project lacks a complete explicit Project list and lacks an evidenced equivalent necessary-study-plan contract, its complete Project relation is **UNKNOWN** and its view is **PROJECT_SCOPE_UNKNOWN**. Known Stage lists and known entry prerequisites may still be acquired and shown under their own accurately named relations. They never manufacture a complete Project Pyramid. Missing or interrupted evidence is UNKNOWN, not empty.

### 8. Resulting bulk-acquisition contract

1. Acquire Project identities and their explicitly declared Stage IDs. Complete pagination, reciprocal Project checks, Stage identity/order checks and global Topic ID resolution before declaring any set complete.
2. Persist native Stage `prerequisites` and `all_prerequisites` observations separately. Normalize only the local necessary-learning relation under the evidenced field/UI contract. No inferred learned, verified, applied or progress state.
3. Acquire explicit Project entry-prerequisite ID lists only if such a source is actually discovered. Otherwise retain UNKNOWN; no false empty relation.
4. Acquire Project necessary-knowledge membership only from a direct explicit list or a **documented, source-established complete Project study-plan equivalence**. The inspected standard Project component supplies the latter for the pilot contract. Preserve the component/source version, interpretation and full Stage provenance; variants without this evidence remain PROJECT_SCOPE_UNKNOWN. Do not silently generalize to a differently named API relation or template.
5. Counters are separate metadata. A counter/ID cardinality difference is recorded as a diagnostic, not treated as proof of different relations, a hard completeness failure, or permission to alter the ID set. Identity/completeness comes from actual lists and source meaning.
6. Course membership continues to use the explicit filtered taxonomy contract above. All foreign keys target existing global semantic identities; no Topic metadata duplication, title matching or extra membership inference.
7. Keep accepted historical facts and new observation provenance distinct. API/UI terminology changes, missing lists, ambiguous variants or unresolved IDs stay UNKNOWN/quarantined. A UI/client contract change requires revalidation of that interpretation before promoting new aggregates.

**Readiness:** the blocking relational mistake is resolved. A Project counter is not a twelve-ID P set, while source-evidenced necessary-study-plan Topic relations can be acquired safely with independent UNKNOWN entry prerequisites. Exact backend counter derivation and an optional opaque field's temporal meaning are not required to fabricate or reconcile membership; they remain explicitly unclaimed. This is readiness of the conservative relation-acquisition contract, not a claim that every optional relation is available.

### 9. Evidence, security, protection and hard stop

The earlier [sanitized discovery snapshot](tests/relation-discovery.json) remains unchanged as historical evidence, including its earlier B assessment. This report's updated interpretation supersedes that assessment; no discovery values were rewritten to manufacture agreement. New browser/API projections and source fingerprints remain outside Git.

Only semantic UI labels, Topic-card links, safe ID/title arrays, original field names, count values and public client source behavior were inspected. No Cookie, Authorization, CSRF secret, password, account identifier, raw authenticated header, HAR or profile data was persisted in the repository. The existing login was valid and no login was automated. No lesson/assignment prose was scraped, and no learning/completion State action was performed.

Protected inventories were compared to the start of this semantic task: accepted Knowledge, State/history/generation, Production, Global V6.6, V6, skill-tree, and **every Scope Pyramid file except this requested report** are unchanged. This includes the locally accepted level-coherence engine, CSS, seeds, catalog, reports, tests and screenshots. `git diff --check` passes. All U IDs resolve to the existing Global Catalog; accepted 26/12 exact sets were verified read-only.

**C — PROJECT / STAGE RELATION SEMANTICS RESOLVED; FULL RELATION ACQUISITION READY. HARD STOP.**

Next milestone: FULL COURSE / PROJECT / STAGE RELATION ACQUISITION. It has **not** begun. No commit, push or deployment.
