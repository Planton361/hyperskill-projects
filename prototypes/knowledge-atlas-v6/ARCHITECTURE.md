# Knowledge Atlas V6.6 — Taxonomy-routed Relation Iteration

Static isolated prototype. Run `python3 -m http.server 8776 --bind 127.0.0.1` in this directory. No commit, push or deployment. See [RELATIONS-VALIDATION.md](RELATIONS-VALIDATION.md) for this iteration. [VALIDATION.md](VALIDATION.md) retains the accepted V6.6 viewport report; its former mint cross-link rendering is superseded here. The public preview is unchanged.

## Frozen V6.5 geometry

`layout.js`, `routing.js`, `model.js`, `model.json`, structural checkpoint and schema are byte-identical to V6.5. No spacing changes, repacking or persisted viewport state. The measured region tree, depth/tray bands, bottom-center/top-center ports and shared hierarchy segments remain. Natural bounds are 8916 × 1867.14 px. All 89 Topics / 46 Categories / labels are present by default. Manual disclosure remains user-controlled. Viewport navigation never triggers layout.

## Viewport state

`viewState` distinguishes overview, subtree and topic optical states. `fitIntent` is ephemeral runtime camera intent: full bounds, subtree key set, project region key set, or a single topic. Responsive map resize refits this intent; direct pan/pinch clears it. It is never written to the structural checkpoint.

`VIEW` centralizes viewport padding, desired reading fonts, maximum scale and 220 ms transition duration. The usable map rectangle reserves controls, visible overview guide and footer. Desktop subtree fits all visible descendants and tray frames. If that region is too large for 10 px Topic text, it remains a complete fit and presents an explicit orientation hint. Mobile wide-subtree focus centers a complete local Category/Tray group at 13 px while retaining every offscreen node.

Topic focus uses 16 px where bounds permit, centered in usable map area. Project fit includes visible evidence representatives plus full relevant trays and their parent cards; projection/coverage semantics remain independent. Project selection and styling toggles do not navigate.

## Navigation semantics

Category single click selects only. Topic click or keyboard activation focuses its reading row. Search and ordinary Inspector topic links reveal manually collapsed ancestors and focus the topic. Relation-list entries instead preview or pin a visual relation route, retaining the selected Topic and camera. Category Search and Inspector category links fit subtrees. The explicit Inspector Focus subtree action replaces an ambiguous category double click. Fit All returns to orientation. Mode/theme changes preserve camera and selection. No view-history stack.

Programmatic navigation interrupts a prior transition; a generation ID prevents stale completion callbacks from changing the active transition flag. Reduced Motion uses synchronous transforms. The zoom listener updates only scene transform, optical state, percentage/status and minimap.

## Optical context

Natural node fonts and bounds stay fixed. Non-scaling hierarchy/card/tray strokes and bounded circle/ring sizes improve overview silhouettes and learning patterns. Marker strokes shrink at extremely low scale to avoid exaggerated row-marker collision. Topic labels are never hidden or made transparent based on scale. No free knowledge cross-link paths are drawn. With no Topic selection, knowledge-route highlights are absent. With a selected Topic, only its direct relations can emphasize taxonomy paths, including after Fit All; zoom never creates a global relation network.

The overview guide provides readable root/major navigation and Java-child context without enlarging text outside existing cards. The native geometry still determines all card labels/ports. A passive minimap shows complete category/tray geography, clipped viewport bounds, selected-region outline and exact amber coverage. It is aria-hidden and hidden on mobile. Its generic tray silhouettes are context/density cues, not replacement learning-state data.

### Semantic Relations vs Visual Routes

The semantic relation is always **Topic A → Topic B**. Existing prerequisite/dependent records, evidence and directed endpoint-pair deduplication are untouched in `model.js` / `model.json`. For the selected Topic, incoming pairs are listed as Prerequisites and outgoing pairs as Dependents, exactly as before. Canonical categories do **not** become semantic relation endpoints or intermediate prerequisites.

`taxonomy-relations.js` is a presentation index created once after the frozen layout. It caches Topic → canonical ancestor chains and the mapping from canonical parent/child keys to existing `L.connectorSegments`. Each relation has separate semantic source/target keys and a visual route: source → canonical ancestors → lowest common ancestor → target ancestors → target. Additional taxonomy memberships never influence this route. No new edge, checkpoint record, layout coordinate or routing lane is produced.

A cross-tray route styles only the existing shared segments that carry its canonical edges, including each terminal category-to-tray connection. Topic endpoints are represented by row accents, not additional row-to-row connectors. A same-tray relation has the same logical LCA path but **zero external visual segments**: only the two rows, common category and tray get local emphasis. The real snapshot has one tray per topic-bearing category, so same-category relations are also same-tray relations.

The projection unions segment memberships across all direct relations. Each physical SVG taxonomy segment is rendered once and only restyled. Shared prerequisite/dependent portions use a quiet neutral trace with a mixed dash pattern; focusing one relation gives those shared portions that relation's violet or mint color. No duplicate overlay or parallel colored stroke is added. Non-route descendants and unrelated branches are never marked as part of a relation.

### Relation Focus and Inspector

`focusedRelation` stores the directed pair key, semantic source/target Topic keys and its type relative to the selected Topic. `previewRelation` is transient hover/keyboard-focus state. Hover or keyboard focus temporarily strengthens one route and dims the other direct routes. Leaving that preview restores the pinned relation, or the quiet all-relations state.

Click, tap, Enter or Space pins the route **without selecting the counterpart, navigating, revealing collapsed ancestors or changing geometry**. Escape or “Show all relations” clears the pinned focus. Mode and theme changes preserve the selected Topic, camera and valid pinned relation. Selecting a different Topic resets relation focus. Preview/focus updates styles and endpoint cues in place; it never redraws category/topic nodes, rebuilds the layout or writes the checkpoint.

Inspector buttons expose “Prerequisite: Title” / “Dependent: Title” labels and `aria-pressed` for pinned focus. Hollow/filled endpoint circles, dashed/solid outlines, directional Inspector cues and explicit text supplement color. A focused status and the existing live region announce the semantic **Topic → Topic** direction. Selected Topic rows use a distinct neutral/cyan outline. Normal 220 ms camera navigation and Reduced Motion remain unchanged.

### Project Evidence Priority

Project requirement projection and covered-segment classes are unchanged: Project 113 retains 26 distinct requirements; Stage 4 retains 12. Amber diamonds, paths and minimap coverage remain. When Topic relations are active, amber evidence becomes quieter, while relation routes and counterpart borders take visual priority. Amber never becomes a prerequisite/dependent type. With no Topic relation selection, the original evidence presentation returns.

Manual collapse remains independent. The complete logical route is retained in the presentation index; only hierarchy segments already visible in the folded tree can be highlighted. Relation focus never automatically expands a hidden counterpart.

## Verification

Current relation checks use a repository-root static server at port 8780 (bind to loopback). No server is needed for the deployed static runtime.

- `python3 -m http.server 8780 --bind 127.0.0.1` from the repository root.
- `node prototypes/knowledge-atlas-v6/tests/taxonomy-relations/browser.cjs`
- `node prototypes/knowledge-atlas-v6/tests/taxonomy-relations/interactions.cjs`
- `python3 tests/integrity.py` from the prototype.
- `sha256sum --check tests/v6.6-preserved-sha256.txt` from the prototype.
- `node tests/spatial.cjs` with the prototype's existing loopback server at 8776.

The independent path oracle checks all 137 directed pairs against real canonical chains and physical frozen hierarchy pieces. The browser suite covers all nine widths in both themes, all 89 Topic selections, route deduplication, Inspector hover/focus, Project Evidence, geometry, keyboard and responsive overflow. Preservation hashes cover all protected directories, the public Atlas preview, the data snapshot and six frozen geometry/model assets. Reports and screenshots are under `tests/taxonomy-relations/`.

Historical viewport/relation suites that assert free `.knowledge` paths describe the former V6.6 rendering; those assertions are superseded by the taxonomy-route suite. The old Fit-All Topic-font ≥10 px acceptance remains obsolete. Frozen V6.5 presentation files and reports remain under `tests/review/v6.5/frozen/`. Do not regenerate the structural checkpoint for this iteration.
