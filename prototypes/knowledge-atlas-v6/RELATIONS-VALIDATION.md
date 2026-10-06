# Knowledge Atlas — Taxonomy-routed Relations

Prototype-only iteration on the accepted V6.6 stand. **927 browser checks across 18 width/theme configurations**, seven additional interaction checks, real-data integrity, frozen-asset hashes and spatial/growth regression pass. No public preview changes, commit, push or deployment.

### Relation Routing Strategy

Knowledge relations style the existing orthogonal taxonomy segments. No new geometry, free diagonal, row-to-row connector, routing lane or parallel overlay is rendered. All direct relations are initially quiet; one hovered, keyboard-focused or pinned relation receives stronger emphasis. Existing hierarchy segments are rendered once, with deduplicated relation memberships.

### Semantic vs Visual Distinction

All **274 prerequisite/dependent evidence records** and **137 deduplicated directed endpoint pairs** remain unchanged. The semantic relation is **Topic A → Topic B**. Canonical categories are only visual routing context; they are never introduced as semantic relation endpoints. Model, source data and evidence are byte-identical. The Inspector explicitly explains this distinction. See [ARCHITECTURE.md](ARCHITECTURE.md#semantic-relations-vs-visual-routes).

### LCA Implementation

`taxonomy-relations.js` caches canonical ancestor chains and parent/child-to-segment mappings after the frozen layout is built. Each visual path is source → canonical ancestors → LCA → target ancestors → target. Additional taxonomy memberships do not participate. An independent oracle verifies all 137 pairs, their original endpoints, both ancestor chains, LCA, exact logical path and physical segment coverage. Its geometry comparison does not derive expected results from the implementation's segment-membership map.

### Same-Tray Behavior

**63 real pairs** share a tray. Their external segment set is empty. Both rows, the tray and its local category receive emphasis; no loop or connector is added inside/outside the tray. The logical source/LCA/target path remains available independently of its local visual representation.

### Same-Category Behavior

The current real snapshot has one tray per topic-bearing category. Its same-category pairs therefore use the same local treatment. They do not route through the root or higher ancestors.

### Cross-Category Behavior

**74 pairs** cross category/tray boundaries. Only the minimal canonical route through their LCA is highlighted, including the existing terminal category-to-tray ports. Endpoint rows identify the semantic Topics. No direct horizontal line joins rows.

### Cross-Branch Behavior

**10 of those 74 pairs** cross major branches. The real common ancestor is Computer science, so these routes reuse the existing root/major buses. An explicit real cross-major focus test verifies the root LCA and exact strong segment set. No relation is synthesized.

### Prerequisite Visual Language

Restrained violet-blue paths, dashed row/category outlines and hollow endpoint circles. Inspector entries use “○ ←” with an accessible “Prerequisite: Title” label. On shared sections used by both relation types, the all-relations state uses one quiet neutral trace with a mixed dash pattern; individual focus assigns the selected relation's color.

### Dependent Visual Language

Restrained mint/cyan paths, solid outlines and filled endpoint circles. Inspector entries use “● →” and “Dependent: Title”. Selected Topics keep a distinct neutral/cyan outline. Shape, directional text and accessible state supplement color.

### Relation Focus Interaction

Hover/keyboard focus previews one route. Click/tap/Enter/Space pins that route while retaining the selected Topic and camera. It **does not select the counterpart**. Escape or “Show all relations” clears the pin. Leaving a transient preview restores the pinned route or quiet all-relations state. Changing the selected Topic resets relation focus; mode/theme switches retain a valid pin.

### Inspector Sync

For loop retains its **two Prerequisites and two Dependents**. Every entry is tested for preview, pin, reset and route synchronization. “Types and variables”, “Conditional statement”, “Writing first program” and “IntelliJ IDEA” are tested additionally, and all 89 Topic selections are checked for exact, deduplicated taxonomy highlights. In the real data, **IDE is a Category**, not a Topic; its category-focus navigation is tested separately instead of inventing a Topic.

### Project Evidence Regression

Project 113 remains completed with **26 distinct requirements**; Stage 4 remains **12 explicit requirements**. No `project_applies`. Covered hierarchy segments match the accepted public-preview baseline exactly. Relation hover/focus and Topic selection retain coverage classes and counts. Amber remains weakly visible behind active relation emphasis; violet/mint card colors explicitly take priority over amber. With no Topic relation selection, the original coverage presentation returns.

### Geometry Regression

**89 Topics / 46 Categories / 31 Learned / 12 Verified** remain. All 135 node positions and dimensions, hierarchy path strings and structural checkpoint content match the accepted V6.6 baseline. Six frozen geometry/model assets remain byte-identical to the V6.5/V6.6 preservation manifest. Navigation, relation hover/focus, coverage, mode and theme cause **zero node displacement and zero layout rebuilds**.

Spatial regression, including Basics +20, Advanced OOP +5 and Databases +20, retains **0 semantic overlaps, 0 hierarchy crossings, 0 connector obstacle/safe-area violations**, exact ports and shared buses. Baseline natural bounds: **8916 × 1867.14 px**. Minimum measured card gap: 128.5 px; tray gap: 104 px; connector clearance: 48 px. Growth tests use in-memory fixtures only and do not alter the real snapshot.

Hash preservation covers 56 files, including all protected Knowledge Map / V5 Preview / Atlas Preview / Knowledge Graph assets, knowledge data, repository/profile-summary files and the six frozen prototype assets. Public preview files are untouched.

### Desktop

1920×1080 and 1440/1280/1200/1024/768×900, each in Dark and Light. States: no selection, Topic selected, relation hovered, relation pinned and Project Coverage + Topic selection. No runtime errors, free knowledge paths, duplicate highlighted segments or page overflow. Inspector stays right above 1200 px and below at 1200 and narrower. Basics reading and Topic Focus visually checked; existing viewport geometry is preserved.

### Mobile

430/390/320×844 in Dark and Light. Tap pins a relation, selection and viewport remain stable, Inspector stays below, and no horizontal page overflow occurs. For loop remains at **16 px effective Topic text**. Additional Chromium touch emulation confirms pinch/pan with a pinned relation at all three widths; geometry, checkpoint and relation focus survive those gestures. Physical iOS/Android devices have not been tested.

### Accessibility

Native relation buttons expose descriptive prerequisite/dependent labels and `aria-pressed` for pinned state. Keyboard focus previews, Enter/Space pins, Escape resets. Inspector status and the existing live region communicate semantic Topic → Topic direction. Hollow/filled markers, dash patterns and text prevent color-only distinctions. Reduced Motion and normal/interrupted camera navigation are verified. Human VoiceOver/TalkBack audits remain outstanding.

### Performance

Local Chromium dispatch/CPU measurements, excluding asynchronous animation duration:

| Action | Measured range |
| --- | ---: |
| For loop selection, latest 18 samples with coverage | 10.50–12.00 ms |
| Relation hover / keyboard preview | 0.70–1.50 ms |
| Relation pin/reset | 0.70–1.00 ms |
| Taxonomy relation projection | 0.50–1.20 ms |

The relation index is built once; routes/chains are cached. Preview/focus changes only styles and endpoint cues. Tests instrument layout builds after initialization and confirm **zero calls**, and verify the same layout object and checkpoint remain. These measurements are local-machine samples, not physical-device frame-rate guarantees.

### Removed Direct Cross-Link UX

Default Topic selection never invokes the former `AtlasRouting.route` knowledge-lane renderer. Its old implementation remains untouched inside the frozen routing asset for historical/debug tests. No `.knowledge` paths or free relation arrows are created in the normal UI. Unselected Overview has no relation highlights; selected Overview shows only the selected Topic's direct routes.

### Remaining Risks

- Complete-map and large-area views remain orientation views. Use smaller subtree or Topic Focus for reading.
- At 16 px Topic Focus, distant counterparts/LCA sections may be offscreen. Their Inspector entries and semantic direction remain available; pan/zoom reveals the route. No automatic relation-fit camera jump is added.
- Manually collapsed counterparts retain their logical routes, but only already-visible hierarchy segments can be accented. Pinning never changes expansion state.
- Shared sections of different relation types use a neutral combined trace until one relation is focused; Inspector text and endpoint shapes disambiguate them.
- Physical Safari/Android and human screen-reader testing remain outstanding.

### Recommendation

Keep this taxonomy-routed presentation for prototype review: the permanent pyramid remains clean, semantic data stays intact, and each direct relation can be traced without a cross-graph line. **Public preview migration is not performed. No commit, push or deployment.**

Test evidence: [path-results.json](tests/taxonomy-relations/path-results.json), [browser-results.json](tests/taxonomy-relations/browser-results.json), [interaction-results.json](tests/taxonomy-relations/interaction-results.json), [preserved-before.json](tests/taxonomy-relations/preserved-before.json), [preserved-after.json](tests/taxonomy-relations/preserved-after.json).

Visual review: [Basics focused prerequisite](tests/taxonomy-relations/1920-basics-focused-prerequisite.png), [Light project + Topic](tests/taxonomy-relations/1440-light-project-topic.png), [Mobile relation focus](tests/taxonomy-relations/390-topic-focused.png), [Cross-major route](tests/taxonomy-relations/1920-cross-major-overview.png).
