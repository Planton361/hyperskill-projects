# Unified Atlas with optional scope filters

Recommendation: **C — UNIFIED ATLAS READY FOR HUMAN REVIEW**

Canonical local preview: http://127.0.0.1:8813/prototypes/knowledge-atlas-navigation/index.html?view=atlas

This milestone supersedes the separate Courses & Projects primary-view behavior in earlier navigation reports. Historical reports are unchanged.

## Two-tab application

The existing persistent shell now has exactly **Atlas** and **My Skill Tree**. Course, Project and Stage are optional Atlas filters. The shell owns routing/history and primary active state. Its navigation DOM remains mounted while switching between Global, local scopes and My Skill Tree.

No filters displays the complete existing full-title Global Atlas, including all **849 Categories / 3,106 titled Topics**, with **31 learned / 12 verified**. Filtered Atlas uses the existing independently computed Scope Pyramid engine. The rule is Stage → Project → Course → full Global. There is no additional semantic scope and no geometry merger.

## Stable Atlas filter bar

The filter bar is owned by the parent shell, above its map content. Course, Project and Stage selectors, searches, Reset button and context status are created once. Changing a scope updates options and values without recreating or moving those elements. Child Scope headers no longer contain duplicate selectors, Clear selection or Reset controls. Legacy local selector handlers are disabled for this shell-owned integration.

The Stage slot reserves its rectangle when no Project is selected; its controls are then invisible/inert. Course and Project controls do not expand or shift into that slot. With a Project selected, Stage choices become visible in the same location. Searches support explicit titles and exact numeric IDs, Enter selection and ArrowDown access to the native selector.

Desktop 1440×900 Dark:

| Chrome | Rectangle / behavior |
| --- | --- |
| Main header | x=0, y=0, width=1440, height=56 |
| Main navigation | x=208, y=11.5, width=250, height=32 |
| Main buttons | 122×32, fixed order Atlas / My Skill Tree |
| Atlas filter bar | x=0, y=56, width=1440, height=80 |
| Course / Project / Stage slots | fixed three-column placement; Stage space retained when conditional controls are absent |
| Reset | same fixed fourth-column position for every Atlas pyramid |
| Renderer frame | begins at y=136 |
| View search toolbar | 44px high, below filters |
| Map canvas | begins at y=180, 720px high |
| Fit All row | same baseline across Global and scoped content |

At 480×900 the navigation remains one row and the Atlas filter bar has fixed height 202px. Filters use fixed stacked slots; Global/local switches retain identical rectangles. Screenshots confirm no overlapping headers or duplicate navigation. My Skill Tree has no scope filter UI; those persistent nodes are hidden while that separate main view is active.

View-specific search, map actions and Inspector remain in their original applications. Only chrome/viewport CSS standardizes the search toolbar and map-control baseline; Topic and Category typography is unchanged. The context/status row consistently identifies the active scope and its explicit Topic count, or the complete Global inventory.

## Source semantics and Project access

The filter bar reads the existing `ScopeUXModel` from the retained Scope application. No second relation parser or catalog database is introduced. Its initial hidden Scope instance loads the accepted catalog but builds **zero local geometries** until a scope is selected.

Without Course, all **391** Project identities are selectable, including the 92 outside all Course association inventories. With Course, only its exact evidenced Project IDs appear. The existing 52 complete inventories, 867 relations, 299 distinct targets, 48 nonempty Courses, four explicitly empty Courses and zero UNKNOWN association inventories are preserved. Course 8 shows exactly 11 Projects; Course 2 exactly 43. No membership is derived from Topics, language or titles.

Stage options use only the selected Project's declared Stage identities in source order. Project requirements, Stage-local requirements, entry-prerequisite UNKNOWN states and numeric metadata remain distinct and unchanged.

## Clearing and return behavior

- Clear Stage: return to the selected Project pyramid.
- Clear Project: clear Stage and return to selected Course; with no Course, display complete Global Atlas.
- Clear Course: remove the filter while preserving the valid Project and its Stage; restore all 391 Project choices.
- Change Course: retain compatible Project/Stage selections; clear incompatible ones.
- Reset to Global: clear all filters/searches, return to the complete Global renderer and fit its camera. It does not rebuild Global geometry.
- Fit All: existing camera-only action; filters remain unchanged.

My Skill Tree remains independent of all filters. Visiting it preserves the remembered Atlas route, selector values and cached local view. Returning restores the selected scope, camera and selected entity/Inspector state without an extra layout build. The remembered route is also carried in shell history state.

Only one content renderer is visible and interactive at a time. Inactive application frames remain cached, hidden and inert. No renderer geometry is copied between frames. Loading first-time content uses a status overlay while the navigation and filters remain usable; no empty page or empty replacement frame is shown.

UNKNOWN Project 95 still displays **Requirements not established** with no layout. Empty Project 405 and Stage 618 display their distinct known-empty messages. Course 31 shows **No projects in this course** while its own Course pyramid remains available. The full 16 UNKNOWN Project / 5 empty Project / 328 empty Stage contract remains intact.

## Exact-ID Show in Global

A local Show in Global action navigates the same shell to unfiltered Atlas, clears Course/Project/Stage controls and selects/focuses the exact Global Topic or Category key using the existing Global API. No title matching or coordinate conversion occurs.

The actual Stage 617 `topic:36` link was tested. Global selected exactly `topic:36`, the URL retained `key=topic:36`, and all filter values were empty. Browser Back restored Stage 617, Topic 36 and its open local Inspector; Forward restored the exact Global identity. Legacy Category 35 identity links also resolve to the complete Global view.

## Canonical and legacy routes

Canonical routes normalize to:

- `?view=atlas`
- `?view=atlas&course=8`
- `?view=atlas&course=8&project=113`
- `?view=atlas&course=8&project=113&stage=617`
- `?view=atlas&project=113`
- `?view=atlas&key=topic%3A36`
- `?view=skill-tree`

Old `view=global`, `view=courses`, `view=projects`, `view=personal` and `scope=course|project|stage&id=<id>` normalize into these routes with their exact identities retained. The existing old prototype entrypoints and `global.html?key=...` bridges redirect once into the canonical shell. Stage → Project context comes from the existing declared relation, not inferred membership. There is one router/history owner and no redirect loop.

## Focused checks

`tests/unified-atlas.cjs` passes the requested A–L scenarios:

| Check | Result |
| --- | --- |
| A: unfiltered full Global | PASS; 849/3,106, unique semantic IDs, progress 31/12 |
| B: Course 8 | PASS; exact 89 Topics and 11 Project choices |
| C: Course 2 | PASS; local pyramid and exact 43 Project choices |
| D: Course 8 + Project 113 | PASS |
| E: direct Project 113 | PASS; no Course filter, all 391 Projects accessible |
| F: Project 113 + Stage 617 | PASS; declared Stage order/containment |
| G: deselect/cascading behavior | PASS |
| H: Reset to full Global / Fit All camera-only | PASS |
| I: My Skill Tree return | PASS; selection, camera and cached geometry/build count unchanged |
| J: exact-ID Show in Global | PASS; filters clear and Back restores local state |
| K: Back/Forward / canonical and legacy routes | PASS |
| L: explicit empty Course, UNKNOWN Project, empty Project/Stage | PASS |

The test asserts exact navigation/filter/selector/reset rectangle equality, the same DOM elements, one active map, no duplicate child controls, a consistent search/header/map-control origin, and six frozen world geometry hashes. One 480px smoke verifies the same filter rectangles across Global/local switching. Two representative desktop images and one narrow image were inspected outside Git; no broad screenshot/regression matrix was run.

Browser errors, failed resources, external requests and extra navigation tabs: **0**. `tests/ux-model.cjs` also passes existing evidence, optional Course semantics, explicit progress and multi-membership Category completion checks. Prior navigation test entrypoints delegate to the superseding unified Atlas contract.

## Geometry and protected-file result

Actual before/after geometry fingerprints cover node identities/coordinates/dimensions/full-title lines, connector segments, trays and layout checkpoint:

| View/scope | SHA-256 | Result |
| --- | --- | --- |
| global | `1306993ec8a1b7a80edda4f620fb96ba5d4803c0d81ded334b92efa85cdf1174` | identical |
| course8 | `ab8e05971ca8fb9d077b491a766554f5b84118e068433afe4c17faa7e91fb89b` | identical |
| course2 | `0dcc2984b65d27f08a46d11a9b7fa2b6afb72d127796c4016c6dc3a8299cff6b` | identical |
| project113 | `33dc51873bcbd33fa6ad2de854dd719e525706bdb764a50578570d1f73e89034` | identical |
| stage617 | `24edf473c9e97b7ccbb287464302a4bbf6ffadff33efdc265076b5ae6b51455e` | identical |
| personal | `a60fc22e272079c91f39cfed9c01af5865bae29120e6d6f7801b02da96cd6348` | identical |

All Scope layout/projection/routing/worker/graph-style/model/catalog files remain byte-identical, including `ux-model.js`. Global and Skill Tree application, model, layout, routing, renderer and styling files are unchanged. Reversing only the Scope embedded-chrome ownership guard and removed duplicate control bindings reproduces its exact pre-task `app.js`; rendering, Inspector data, camera functions and progress/completion calculations have no edits.

Byte comparison against the complete local pre-task working tree:

- `data/knowledge/`: 14 files byte-identical.
- `state/knowledge-atlas/`: 4 files byte-identical.
- `docs/knowledge-map/`: 15 files byte-identical.
- `prototypes/knowledge-atlas-v6-global/`: 323 files byte-identical.
- `prototypes/knowledge-atlas-v6-skill-tree/`: 28 files byte-identical.
- `prototypes/knowledge-atlas-v6/`: 282 files byte-identical.

Existing local and unrelated work is preserved. Focused syntax checks and `git diff --check` pass. No Hyperskill contact, acquisition, Knowledge changes, Production changes, commits, pushes or deployments occurred.

Global full-title status remains **FULL_TITLE_GLOBAL_TECHNICALLY_READY / HUMAN_ACCEPTANCE_PENDING**. This unified application is ready for owner review; no additional UX or layout work follows this milestone.
