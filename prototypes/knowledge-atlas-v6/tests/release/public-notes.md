# Knowledge Atlas · Preview

### Preview Build

Isolated static release of the accepted V6.6 release candidate, using frozen V6.5 spatial geometry. Public path: [Knowledge Atlas Preview](https://planton361.github.io/hyperskill-projects/knowledge-atlas-preview/). Existing Knowledge Map, V5 preview and Knowledge Graph paths remain unchanged. Production migration is **NOT PERFORMED**.

The runtime is copied directly from the accepted prototype. Only the document title and quiet page heading change to “Knowledge Atlas · Preview”. All other runtime assets are byte-identical. `release-manifest.json` records SHA-256 hashes for the accepted source and published assets, including the layout implementation, model and checkpoint. Packaging verifies hashes before and after copying.

All assets use relative paths. D3 7.9.0 and its license are bundled locally. No server-side processing, development server, external runtime dependency, machine-specific paths or synthetic growth fixtures are published. This release contains 11 runtime/license files, the release manifest and these notes.

### Data Snapshot

The bundled snapshot matches all eight real knowledge-data tables and their source hashes:

| Item | Count / value |
| --- | --- |
| Topics | 89 |
| Categories | 46 |
| Learned Topics | 31 |
| Verified Topics | 12 |
| Project 113 | Simple Chat Bot with Java |
| Project status | completed |
| Distinct Project 113 `project_requires` | 26 |
| Stage 4 explicitly recorded requirements | 12 |
| `project_applies` | 0 |

No requirements, learning states or relationships are inferred. Stage requirements do not imply an independently recorded stage-completion status.

### Layout Geometry

The V6.5/V6.6 geometry and checkpoint are preserved. Natural content bounds remain approximately **8916 × 1867.14 natural pixels**. Browser checks compare all 135 node positions and dimensions against the accepted source. Semantic overlaps, hierarchy crossings, connector/obstacle intersections, spacing violations and region violations are zero. Card/tray connections retain exact ports and shared orthogonal sibling buses.

Mode switching, project coverage, theme switching and viewport navigation preserve coordinates and checkpoint content. Zoom performs no structural layout recomputation. All 89 Topics and 46 Categories, with their labels, remain rendered by default; zoom never removes knowledge. Explicit manual collapse remains available independently of zoom.

### Navigation Model

**Global Overview → Area Overview → Subtree Reading → Topic Focus** are viewport states of the same map, not different layouts or filtered datasets.

Category single click selects. “Fit selected subtree” and the Inspector's “Focus subtree” navigate into that area. Category Search selects and fits its subtree. Topic click, keyboard activation and Topic Search enter Topic Focus. Search opens a manually collapsed ancestor path when needed, without switching My Knowledge / Course Roadmap. Fit all returns to the complete landscape.

### Global Overview

Fit all includes the complete taxonomy. Topic text may be micro-text. Tray silhouettes, learning-state markers and project evidence communicate distribution. A readable overview guide supplies the root, major branches and Java context without changing node geometry. Knowledge cross-links are hidden in Overview. The previous “Fit-All Topic font >= 10 px” criterion is obsolete: **Fit-All is an orientation view**.

### Area Overview

Java and other large areas retain their full desktop subtree bounds. Complete Java Fit gives approximately 3.99 px Topic text at 1920; it is primarily an orientation view. Use Inspector child navigation, smaller subtree focus or Search to read topics. Status explicitly distinguishes an area overview from a readable subtree.

### Subtree Reading

At 1920, complete Basics Fit gives approximately 11.63 px Topic text. Smaller desktop widths cannot fit all Basics content at 10 px; navigate into its children for comfortable reading. On mobile, Java/Basics focus uses a local descendant category/tray window at 13 px while the remaining map stays rendered and accessible by pan. This mobile window is not a complete-subtree fit.

### Topic Focus

Searching “For loop” selects the real Topic, centers its complete row at 16 px effective Topic text, opens the Inspector and shows only direct prerequisite/dependent relations. The full canonical path preserves context. The Inspector is on the right above 1200 px and below the map at 1200 px and narrower. Surrounding map content can be outside the focused viewport without being removed.

### Project Evidence

Selecting Project 113 preserves the viewport and highlights its exact 26 requirements. Stage 4 highlights exactly 12. Amber emphasis reuses the existing hierarchy segments and required rows; unrelated knowledge stays visible and dimmed. Show/Hide coverage changes styling only. Fit project coverage is a separate viewport action that includes all relevant visible evidence representatives and tray bounds. Wide coverage is also an orientation view. Topic Focus does not change evidence semantics.

### Desktop Validation

The local static release passed **750 checks across 18 width/theme configurations**. Static release testing covers **1920×1080** and **1440/1280/1200/1024/768×900**, each in Dark and Light. Scenarios include initial Overview, Fit all, Java, Basics, For loop Search/Topic Focus, My Knowledge, Course Roadmap, minimap, Project 113, coverage toggle/fit, Stage 4, theme switching, keyboard activation, Reduced Motion and reload.

Tests check full overview bounds, focused target bounds, relative assets, zero page overflow, responsive Inspector placement, unchanged geometry/checkpoint, real data counts and absence of runtime errors. Final publication also requires a separate smoke test on the actual HTTPS Pages URL, including HTTP status and asset hashes.

### Mobile Validation

Automated Chromium mobile emulation covers **430/390/320×844**, each in Dark and Light, using the same release runtime and scenarios. Full landscape remains rendered. Search provides readable local Topic Focus at 16 px; local subtree windows provide 13 px Topic text. No horizontal page overflow occurs. The Inspector is below the map; the passive minimap is hidden at these widths. Touch pinch/pan and unchanged geometry also pass in all six mobile width/theme configurations. These checks are emulation, not physical-device certification.

### Accessibility

Viewport controls retain accessible names, the zoom percentage is an accessible status, Search uses the live region, and Inspector breadcrumbs retain canonical context. Topic keyboard activation enters focus. Reduced Motion produces immediate viewport transforms instead of the normal 220 ms transition. The visual minimap is `aria-hidden` and non-interactive. Automated checks do not replace a human screen-reader audit.

### Performance

Viewport actions use transforms and optical styling without recomputing the frozen layout. Automated release testing records navigation CPU samples and verifies the structural-layout counter remains unchanged across navigation. Recorded local CPU ranges: Fit all 2.70–3.30 ms, subtree fit 0.60–1.00 ms, Topic Focus 0.30–0.70 ms, project fit 0.50–0.80 ms, Search navigation 6.90–8.30 ms. These dispatch samples exclude animation duration. Normal animation duration is 220 ms; Reduced Motion is synchronous. Desktop and mobile timings are local browser measurements, not physical-device frame-rate guarantees.

### Physical Device Tests Outstanding

The following have **not been performed** for this release:

- Physical iOS Safari, including pan/pinch and reload.
- Physical Android Chrome, including pan/pinch and reload.
- VoiceOver navigation and announcements.
- TalkBack navigation and announcements.

### Known Limitations

**Full-map and large-area views are orientation views. Comfortable topic reading is provided through subtree and topic focus.**

Complete desktop Java Fit is below the comfortable reading target at every tested width. Complete Basics Fit reaches that target at 1920 but falls below it at smaller desktop widths. The overview guide supplies readable global context; native map labels are not enlarged beyond their frozen cards. Mobile subtree focus intentionally shows a local window, and the selected parent can be outside that window; Inspector breadcrumbs preserve context. Browser fonts and assistive-technology behavior still need real-world evaluation.

### Feedback Notes

Please include viewport/device, browser, theme, navigation action and selected category/topic or project stage with feedback. Useful evaluation flows are Overview → Java → Basics → For loop, and Project 113 → Show coverage → Fit coverage → a required Topic. Distinguish orientation clarity from local reading comfort. Report missing content, navigation failures or evidence mismatches separately from cosmetic preferences. This preview does not authorize or perform production migration.
