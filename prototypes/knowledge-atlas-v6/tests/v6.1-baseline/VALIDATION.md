# V6.1 — validation and review

Local Chrome/Playwright validation, 2026-10-03. Only this isolated prototype was updated. No commit, push or deployment. Source integrity verifies all eight normalized tables against `data/knowledge/`.

### Visual Result

Quiet dark/light box atlas, with a strong root, three major branches, category coverage captions and compact topic grids. Screenshots were visually reviewed: boxes make individual knowledge units recognizable and amber coverage immediately apparent. Full fit remains an overview; it does not yet provide comfortable reading of every topic name.

### Box Node System

135 complete rectangular interaction targets. Subtle surfaces, thin borders, small radii, no neon, gradients or heavy shadows. Nodes remain a taxonomy visualization rather than project/kanban cards.

### Category Cards

46 cards; root 28, major 21, category 17 natural font units. Coverage is learned / descendant topic count, never competency. Explicit disclosure belongs visually to the card but is an independent accessible control.

### Topic Cards

89 cards, minimum observed width **204** units (configured minimum 180); complete labels at natural font 14. Learned indicators: 31; verification rings: 12. Hollow unlearned indicators stay visible.

### Topic Grid Algorithm

Automatic, measured one-to-four-column candidate packing. Stable ID order; column widths and row heights derive from actual labels, count, parent width and aspect ratio. No topic x/y persistence. Common parent bus and column spines preserve direct sibling membership.

### Long Label Handling

Every topic uses at most three lines. All six explicit long-name cases pass: Basic literals and Boolean operations use three lines; Comparing values, Floating-point operations, Scanner input and IntelliJ run/debug use two. No truncation, character columns or escaped label geometry. Category titles and coverage captions fit inside their boxes with no label overlap.

### Fit-All Readability

**The 10 CSS px acceptance target is not met.** `tests/readability.cjs` measures actual computed font × SVG screen transformation at **1920×1080**: natural 14 px, scale 0.551674, effective **7.7234 px**. It exits **1**, writes `readability-results.json` and preserves this failure.

The available fitted map area after Inspector/controls is **1586×837**. At 10 px the full bounds would need to fit within **2220.4×1171.8** layout units. Current bounds are **2810×1517.2**: approximately 21% width and 23% height reduction still needed. Existing full hierarchy, minimum card widths and all 135 measured boxes constrain this implementation. This is an algorithm limitation, not a claim that 10 px is mathematically impossible. A 36-candidate investigation of card width and subtree aspect scoring retained the current best measured packing. Increasing font size or hiding nodes was not used to turn the test green.

At 1440×900 topic text is 5.51 px; 1280: 4.71; 1200: 4.48; 1024: 4.48; 768: 3.61. Root at 1920 is 15.45 px, major categories 11.59, other categories 9.38. Search gives approximately 17 px topic text. Fit selected subtree is available for detailed reading.

### Layout Bounding Box

Same 1920×1080 comparison against archived V6:

| Measurement | V6 before boxes | V6.1 |
|---|---:|---:|
| Natural bounds width | 6931.29 | 2810 |
| Natural bounds height | 4340.40 | 1517.20 |
| Natural topic font | 40 | 14 |
| Fit scale | 0.186619 | 0.551674 |
| Effective topic font | 7.4647 px | 7.7234 px |
| Maximum topic lines | 9 | 3 |

Natural units changed, so reduced bounds alone do not prove improved screen readability. Effective text improves only about **3.5%**; the larger improvement is word wrapping, structured hit targets and recognizable regions.

### My Knowledge

Default contains all 89 topics and 46 categories. Mint highlights learned knowledge within the complete landscape. Not learned remains visible and muted.

### Course Roadmap

Same full node set and hierarchy; unlearned labels receive greater visual emphasis. No filtering or automatic expansion/collapse.

### Mode Stability

Exact IDs/x/y equality across My Knowledge → Roadmap → My Knowledge. Modes do not rebuild geometry. Zoom-out also retains every label.

### Project Evidence

Project selection immediately enables real coverage; Show/Hide toggles remain available. Project 113 selects exactly **26** topic cards; Stage 4 exactly **12**. Amber card borders, tinted surfaces and diamonds preserve simultaneous mint learned/verified state. No applies or competency claims.

### Project Path Highlight

Exact canonical ancestor set and connecting hierarchy edges match requirements. Relevant membership buses/spines are amber. Unrelated cards remain present at 0.4 opacity; path opacity is subdued. Visual review confirms immediate map response.

### Project Coverage Invariance

Exact equality before/after project selection and explicit Hide/Show: all card positions/dimensions, checkpoint serialization, viewport x/y/scale, manual collapse set. Evidence is exclusively an overlay. Collapsed requirements roll up once; sum stays 26. Reveal only appears after relevant manual collapse. Fit coverage only changes viewport.

### Knowledge Relations

Zero background knowledge paths at overview. All 89 topic selections produce their exact direct relations; 137 unique model relations preserved. All 137 boundary routes avoid card interiors. Contextual routing never changes coordinates. Some route crossings/detours remain.

### Search

“For loop” opens collapsed ancestors, retains My Knowledge, selects the correct card, centers its full rectangle within 1 px, uses readable scale, shows Inspector and direct relations. Unlearned topic navigation also retains mode. Mobile search camera survives Inspector resize.

### Category Interaction

Card single-click selects without collapse. Disclosure single-click changes expansion and preserves selection. Enter/Space activate their respective controls. No necessary double-click behavior.

### Topic Interaction

Entire card selects, not just status dot/text. Keyboard Enter selection passes. No topic disclosure or hidden secondary click behavior.

### Major Anchor Stability

All existing major category anchors stay fixed in the three growth fixtures. Foundation and DevOps no longer shift under Advanced OOP +5. Baseline checkpoint rebuild reproduces exact coordinates and label breaks.

Absolute pre-box V6 coordinates are not retained: the schema-3 presentation baseline deliberately uses the new box scale and efficient packing. Canonical order, hierarchy and broad major ordering remain. Subsequent growth respects new major anchors.

### Growth Tests

| Test-only fixture | Added topics | Existing nodes moved | Major anchors moved | Card overlap |
|---|---:|---:|---:|---|
| Advanced OOP | 5 | 0 | 0 | none |
| Basics | 20 | 46 | 0 | none |
| Databases | 20 | 0 | 0 | none |

Basics increases rows/columns and locally moves descendant slots; **11 moved nodes are outside Basics but within the adjacent Java/Errorless-code region**. This preserves major geography at the cost of some local neighbor movement. Databases appends a region below the scene; growth increases total height. Grown checkpoint rebuilds are deterministic. Fixtures never enter normal runtime data.

### Desktop

1920, 1440, 1280, 1200, 1024, 768, in both dark and light: exact 89/46 rendered, every topic label present, every card inside initial viewport, no page horizontal overflow. Natural card/label geometry and edge avoidance pass. Inspector switches below at ≤1200.

### Mobile

430, 390, 320 in both themes: all 89/46 remain rendered, initial complete fit, no horizontal page overflow. Automated 390 touch pinch/pan, search, selection and below-map Inspector pass. Fit-all text is intentionally too small for detailed reading on mobile; zoom/search exposes readable cards. Mobile project coverage (26), Hide/Show and Stage 4 (12) also pass touch-control tests. A physical-device usability study was not performed.

### Accessibility

Real SVG button interaction targets with full accessible names, canonical paths, selected state, learning state and verification. Explicit disclosure exposes aria-expanded. All 26 required cards include “required by selected project” in accessible names. Diamonds supplement color. Keyboard, focus restoration, reduced motion and polite Inspector live region preserved. No screen-reader end-to-end session was performed.

### Performance

Representative local 1440 browser run: model parse ~3 ms, layout ~8 ms, initial render ~4 ms, search ~0.1 ms. All-topic stress run: maximum direct relation routing ~1.6 ms and topic selection ~5 ms. Timings vary by run/device and are not performance budgets. Full rendering remains default.

### Remaining Risks

The requested 10 px desktop fit-all text threshold fails. Fine reading still needs zoom. Category subtree shelves stagger siblings vertically; canonical edges remain correct, but a strict same-level row view is not retained everywhere. Long perimeter routes can reduce visual hierarchy clarity in dense regions. Amber dimming makes unrelated labels less legible at overview without hiding them. Arbitrary untested growth may need further collision handling. System-font metrics vary across operating systems.

### Comparison with V6

Cards and two/three-line labels replace up-to-nine-line text columns. Topic units and click targets are clearer. Coverage is an unmistakable amber taxonomy overlay. Major anchors survive tested unrelated growth. Fit-all font gains are modest, so this should not be presented as a completed 10 px readability solution.

### Recommendation

Keep immediate project coverage on selection: it gives a clear map response, while explicit Hide/Show offers control and both paths pass invariance tests. Use V6.1 for local design review of the box system and evidence overlay. Before accepting desktop Fit-all readability, continue packing work against the strict 10 px measurement; preserve the failed test as the gate. No publication is recommended as part of this task.

## Reproducible results and screenshots

Functional interaction suite: `tests/results.json` (43 checks). Box/geometry/theme/growth suite: `tests/boxed-results.json` (30 checks). All-topic routing: `tests/relation-results.json`. Strict failed readability: `tests/readability-results.json`.

- [1920 Dark — Fit-All My Knowledge](tests/review/v6.1/1920-dark-fit-all.png)
- [1920 Dark — Basics subtree](tests/review/v6.1/1920-dark-java-basics.png)
- [1920 Dark — Project 113 coverage](tests/review/v6.1/1920-dark-project-113.png)
- [1440 Light — Fit-All](tests/review/v6.1/1440-light-fit-all.png)
- [390 Dark — Fit-All](tests/review/v6.1/390-dark-fit-all.png)
- [390 Dark — For loop / Basics detail](tests/review/v6.1/390-dark-java-basics.png)

Screenshots are local review artifacts and were not committed.
