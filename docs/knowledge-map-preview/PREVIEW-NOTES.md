# Knowledge Map · Public Preview Notes

### Preview Build

Isolated static V5.2 build. The only UI differences from the accepted source are the browser title “Knowledge Map · Preview” and the quiet header “KNOWLEDGE ATLAS / PREVIEW”. JavaScript, CSS, D3, source snapshot and checkpoint are copied byte-for-byte. No runtime dependency on Python, Node, a development server or external fonts/CDNs. D3 7.9.0 and its license are bundled. Fixtures and test tooling are not part of this public directory.

Build/check from repository root:

```sh
python prototypes/knowledge-tree-v5/build-preview.py
python prototypes/knowledge-tree-v5/build-preview.py --check
```

This command validates source data before packaging and writes only this isolated preview directory. The manifest records every asset and accepted-source SHA-256.

### Source Version

Accepted local V5.2 architecture remains frozen. Authorized Project Coverage interaction correction: Show/Hide is a pure overlay, Reveal is explicit disclosure, and Fit is explicit viewport navigation. Only prototype app.js and style.css changed for this correction; layout, routing, data and checkpoint hashes remain unchanged. The source is not represented as a newly committed release or Git tag. Publication is limited to the isolated preview through the existing Pages configuration. Production routes, knowledge data and Profile README remain unchanged.

### Data Snapshot

Literal copy of the eight normalized `data/knowledge/` tables; source SHA-256 values and table equality validated before build. Personal snapshot shown by the accepted UI: 01 Oct 2026.

- Introduction to Java: 89 distinct topics.
- Learned: 31. Verified: 12.
- Project 113: Simple Chat Bot with Java, status `completed`, 26 distinct `project_requires` topics.
- Project 113 completed-stage inventory remains `null`; completion of individual stages is not inferred.
- Project 380 remains `active`, with `completed_stage_ids: []`, exactly as source data.
- No `project_applies`; no synthetic data or topic duplicates.
- The source has no project descriptions. None were invented.

### Layout Checkpoint

`layout_schema_version: 2`, `layout_algorithm_version: persistent-geography-2`, generation 0. Exact accepted checkpoint, deterministic re-run unchanged. Category-only presentation allocation: no learned/verified state, courses, projects, evidence, knowledge relations or individual Topic x/y records.

Project selection and Show/Hide coverage preserve checkpoint bytes, canonical coordinates, category anchors, disclosure state, rendered-node coordinates, search and viewport. Hidden required topics roll up exactly once onto the nearest rendered ancestor. Reveal required topics opens only the necessary ancestors, preserving checkpoint, canonical geography and viewport; changing the compact disclosure projection is allowed for this explicit action. Fit project coverage changes only the viewport and includes currently visible roll-up categories.

### Deployment Path

`docs/knowledge-map-preview/`, isolated from `docs/knowledge-map/` and `docs/knowledge-graph/`. GitHub Pages configuration was read, not modified: `main`, `/docs`, legacy branch build.

Intended public URL after a separately authorized publication:

https://planton361.github.io/hyperskill-projects/knowledge-map-preview/

Public Preview release V5.2.1 targets this URL through the existing main/docs Pages deployment. Automated checks pass; physical-device and real screenreader checks remain outstanding. Browser tests cover `/knowledge-map-preview/` and the complete `/hyperskill-projects/knowledge-map-preview/` prefix, slash redirect, reload and all relative asset requests. No missing or external assets were observed. The production `/knowledge-map/` route is unchanged.

### Desktop Validation

Chromium 149.0.7827.55, 1920 / 1440 / 1280 / 1200 / 1024 / 768 px, each Dark and Light. All 12 functional runs passed, using only the real published snapshot. Default My Knowledge shows 31 learned topics and 12 verified rings, with taxonomy; Inspector is right of the map above 1200 px and below at 1200 px or less.

Search, topic/category/project selection, project coverage, opt-in requirement lines, expand/collapse, subtree actions, Fit all / Fit subtree, Course Roadmap / My Knowledge, course overlay, theme switching, keyboard, Reduced Motion, reload, full long labels, label clipping/overlap and page overflow passed. Show/Hide invariance, explicit Reveal and explicit Fit passed at every desktop width/theme. A default desktop-light screenshot was visually inspected. No browser errors or failed asset requests.

### Mobile Validation

Chromium mobile emulation: 430 / 390 / 320 px, each Dark and Light. All six functional runs passed. Accepted structural collapsed default: nine visible structural nodes, zero topic wall. Touch tap, pinch/pan emulation, search, expand/collapse, Inspector/Evidence and reload passed. A default mobile-dark screenshot was visually inspected.

Project 113 Show coverage retains all nine structural nodes, their coordinates and the viewport at all three widths in both themes. Exactly 26 hidden requirements are represented as restrained amber roll-ups: Software development foundations 5, Basics 17, Code organization 3, Errorless code 1. Each requirement is counted once. Selecting a category retains the overlay and shows its exact required/visible/hidden counts. Separate Reveal makes all 26 required topics visible without automatic Fit; separate Fit affects only the viewport. Show/Hide also preserves subsequent manual disclosure and navigation. Coverage screenshots at 390 Dark and 320 Light were visually inspected.

### Accessibility

Accessible node names include title, depth and hierarchy; expandable categories expose `aria-expanded`; selected nodes expose `aria-pressed`. Keyboard traversal/selection, search ArrowDown/Enter, Space expansion, Escape clearing, focus styling and the polite Inspector live-region passed automated checks. Reduced Motion was emulated and verified. System fonts and existing focus/shape/status cues remain unchanged.

No physical-device accessibility testing or real screenreader testing was performed. Full VoiceOver, TalkBack or other screenreader compatibility is not claimed.

### Performance

Measured the real isolated build over 18 cold browser contexts, one for each viewport/theme. No CPU/network throttling; local static serving on AMD Ryzen 7 9800X3D, Chromium 149.0.7827.55. Test-only function wrappers measured the existing implementation; shipped source assets were not modified. Search used the real “For loop” query and selection. These are host measurements, not phone performance guarantees.

JSON decode includes reading the response body. Layout includes initial checkpoint planning, compact projection planning and hierarchy placement. Initial DOM render includes routing work and excludes first paint; routing rows therefore overlap the render total and must not be added to it.

| Measurement | Median ms | p90 ms | Maximum ms |
|---|---:|---:|---:|
| Initial model JSON decode | 0.60 | 0.70 | 0.70 |
| Initial layout calculation | 2.50 | 2.80 | 5.60 |
| Initial DOM render, including routing | 62.60 | 64.00 | 71.60 |
| Initial route calculation | 52.00 | 52.90 | 53.90 |
| Route calculation on topic selection | 50.10 | 51.30 | 51.50 |
| Search handler / results update | 0.10 | 0.10 | 0.10 |

Mobile default calculates a much smaller initial DOM and no knowledge routes. No performance optimization or new routing strategy was introduced. Correctness tests of all 137 real directed knowledge connections, five focused selections and three mobile widths report zero label/node obstacle hits for lane routing.

### Manual Device Checks Outstanding

No physical device was used. Every item remains unchecked.

**iOS Safari** — record device, iOS/Safari version, theme and observations:

- [ ] Load the published preview URL and reload.
- [ ] Pinch to zoom.
- [ ] Pan the map.
- [ ] Tap a node and read its Inspector.
- [ ] Expand and collapse categories.
- [ ] Search a learned and an unlearned topic.
- [ ] Scroll the Inspector and Advanced Evidence.
- [ ] Select Project 113: Show coverage retains disclosure/viewport and totals 26; Reveal opens required branches; Fit navigates separately.

**Android Chrome** — record device, Android/Chrome version, theme and observations:

- [ ] Load the published preview URL and reload.
- [ ] Pinch to zoom.
- [ ] Pan the map.
- [ ] Tap a node and read its Inspector.
- [ ] Expand and collapse categories.
- [ ] Search a learned and an unlearned topic.
- [ ] Scroll the Inspector and Advanced Evidence.
- [ ] Select Project 113: Show coverage retains disclosure/viewport and totals 26; Reveal opens required branches; Fit navigates separately.

### Known Limitations

- **Explicit disclosure:** Reveal can change compact display positions as branches open; canonical geography and checkpoint remain unchanged. It preserves pan/zoom, so newly revealed topics can be outside the current viewport. Fit is a separate action. This is the authorized interaction contract, not an overlay invariance failure.
- **Physical devices and screenreaders:** emulation passed; actual iOS Safari, Android Chrome, VoiceOver and TalkBack remain untested.
- **Project descriptions:** unavailable in the current source snapshot.
- **My Knowledge relation visibility:** only edges whose topic endpoints are currently rendered are drawn. All direct relation records are listed in Inspector; selecting an unlearned related topic opens the accepted Roadmap experience. For loop has four direct relations, three visible in the tested My Knowledge view.
- **Performance scope:** local desktop-host measurements do not establish real mobile/network performance. Rendering is synchronous, as in the frozen source.

### Feedback Notes

- **visual:** Quiet Preview label only. Tested defaults have no observed clipping, label overlap or document overflow; no redesign.
- **interaction:** Show/Hide overlay, Reveal disclosure and Fit navigation have separate controls and separately verified invariants. All automated release requirements now pass. Publication scope is exclusively this Public Preview; production migration remains prohibited.
- **mobile:** Show coverage keeps the nine-node structural default and reports 26 real requirements through roll-ups. Eight physical-device checks per platform remain open.
- **accessibility:** Automated names/state/focus/keyboard/live-region checks pass. Record actual screenreader findings separately.
- **performance:** Desktop first draw calculates routes before the initial Fit hides the overview connections; measured route work is about 53 ms median. Recorded only, not optimized during this release iteration.
- **data:** Exact source snapshot preserved, including unknown stage completion and missing descriptions. No competence scores or inferred evidence.
- **possible future improvement:** Collect device and screenreader feedback after publication. No additional architecture work was started.
