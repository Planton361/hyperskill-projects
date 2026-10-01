# Knowledge Map V3 build contract

This directory contains display configuration, not Hyperskill facts.
display-map.json supplies ancestry-based domains/subdomains for the bounded
profile summary. clusters.json defines six layout groups by category ancestor
IDs and display titles. Remaining roadmap topics use the existing subdomain
projection. Invalid or ambiguous cluster membership fails closed.

Learned/verified, prerequisite/dependent, requirements and progress are never
duplicated here. The existing Control Flow capability remains topic evidence
IDs 25, 89, 87, 88: 4/4 learned and 3/4 verified, not proficiency.

## Rebuild / verify

From repository root, Python 3.10+:

~~~bash
python3 scripts/build-knowledge-map.py
python3 scripts/build-knowledge-map.py --check
python3 -m unittest discover -s scripts/tests -p 'test_*.py'
~~~

Normalized data/knowledge and observations pass the existing source validator.
Outputs: docs/knowledge-map/model.json and the unchanged bounded
generated/profile-learning-summary.md. --check compares deterministic artifacts
without writes; --root supports isolated test roots. No API/session access.
The model is never source-of-truth or an input to its own rebuild.

## Runtime reference

V3 app/style come from accepted preview commit
3c1539db481159e2cf45eb2f69d5410f15dc0bd0; index branding is production-specific.
Local D3 7.9.0 and its license are retained. Source generation reproduces the
accepted preview model byte-for-byte without reading that artifact.
docs/knowledge-graph remains unchanged as the historical/fallback route.

## Global graph contract

Default My Knowledge shows only is_learned === true topics plus completed/active
project diamonds. Every learned name is permanent and word-wrapped, not truncated.
Verified is a separate ring. Failed/evaluation assessment does not reverse
explicit learning. Roadmap includes all 89 course topics, with weaker hollow
not-learned nodes. Applied IDs are unknown; only the aggregate is reported.

There are no visible category nodes or hierarchy edges. Real ancestry drives
cluster forces and quiet captions. Ordered seeded starts, fixed simulation
ticks, rectangle collisions and settling produce repeatable positions.
Manual drag positions persist only within the page. Fit includes label bounds.
Drag can reintroduce overlaps; no idle animation runs, including Reduced Motion.

Prerequisite/dependent records with identical directed endpoints draw one arrow;
all source records/provenance stay in Advanced / Evidence. Selection emphasizes
direct neighbors and incident edges. Projects add no requirements by default.
Explicit Show project connections reveals project_requires, never project_applies.
Search centers/selects/opens the inspector; unlearned results switch to Roadmap.
Clear removes selection/requirements; Fit separately restores the viewport.

Zoom changes label density, not scene membership. Learned/project/selected/hover
labels remain visible. Additional roadmap labels: degree >=7 below 0.65;
in-view degree >=3 at 0.65–1.15; all in-view topics at >=1.15. Degree is a
display priority, not proficiency. Mobile Fit is overview-only; zoom/search
provides readable neighborhoods.

Above 1200 px inspector/graph are side by side; at <=1200 inspector is below.
ResizeObserver automatically recalculates Fit. Keyboard Tab/Enter/Space,
search ArrowDown/Enter, Escape, dedicated focus ring and shapes/status text
supplement pointer input and colors. Touch pinch/pan is supported.

## Navigation compatibility

The route remains unchanged, so existing profile CTA links open the map.
As in the accepted preview, previous V2 domain/subdomain/topic/project query
parameters and browser history do not restore drilldown/focus state.
No new URL-state contract or profile changes are bundled into V3.

## Local browser regression

~~~bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
node scripts/tests/knowledge_map_browser.cjs http://127.0.0.1:8000/knowledge-map/
ENGINE=firefox node scripts/tests/knowledge_map_browser.cjs http://127.0.0.1:8000/knowledge-map/
node scripts/tests/knowledge_graph_browser.cjs http://127.0.0.1:8000/knowledge-graph/
~~~

Supply Playwright externally through PLAYWRIGHT_MODULE, optionally
CHROMIUM_EXECUTABLE/FIREFOX_EXECUTABLE. No saved account/session state.
V3 tests widths 1440/1280/1200/1024/768/430/390/320 in both themes:
exact counts, every learned name, four topic selections, search centering,
project opt-in, roadmap density, keyboard, reload stability, breakpoint resizing,
pan/zoom/touch, request failures and overflow. Optional SCREENSHOT_DIR and
RESULTS_PATH write only to caller-supplied paths; no fixtures/screenshots publish.

## Limits / release isolation

Real-device/Safari and large dense graph testing remain separate. Layout is
synchronous and may later need a worker. Resize restores Fit. The V2 drilldown
browser contract is replaced by V3 global-scene assertions; all source-data
contracts remain active.

Pages publishes main/docs. Release-branch push alone does not deploy production.
Do not merge, change Pages settings, or modify the profile automatically.
Normalized sources, prototypes and the old graph route are outside this release.
