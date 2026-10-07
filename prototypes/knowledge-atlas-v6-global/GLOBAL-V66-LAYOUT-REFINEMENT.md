# V6.6 Global — one focused layout refinement

**B — ONE SPECIFIC ISSUE REMAINS**

The remaining issue is the **global aspect ratio**: compact rectangular packing
now produces a roughly 20:1 landscape. Empty corridors are substantially reduced,
trays have stronger presence, all content and focused views work correctly, but
the global and Computer-science orientation views are too flat to claim visual
acceptance. This report does not substitute automated checks for human approval.
No second design direction, further layout iteration or My Skill Tree work was
started.

## Measurement first and root cause

Measured the running, unchanged prototype at 1440×900 Dark **before changing
geometry**. The same `tests/layout-metrics.cjs` oracle collects the before/after
values. Raw records are [before.json](tests/refinement/before.json) and
[after.json](tests/refinement/after.json). They include all five root bounds,
the largest 20 parent/child-or-tray horizontal spans, the largest 20 sibling gaps,
all requested distributions, projected cards/trays and status-marker optics.
Percentiles use the lower order statistic at `floor((N−1) × percentile)`.

The wasted geometry had four concrete sources:

1. A global **22,944-unit depth gap**, calculated from the total count of deep
   Categories instead of the contents of the next band. Median parent-to-child
   center distance exceeded 23,000 units even for nearby siblings.
2. Root regions reserved **18% of Computer science's width** and root gaps used
   another **2%**. This imposed 40,422.96-unit minimum allocations and 4,491.44-unit
   gaps regardless of the smaller roots' own contents.
3. Mixed Category/Topic parents positioned their direct trays beyond the full
   rightmost card/subtree extent. Most parents were not recentered over the
   final child region. These lateral offsets propagated into ancestor envelopes
   and rails. Existing sibling padding also accumulated at every level.
4. Every reference-only tray inherited the same 220-unit row width as titled
   Topics, despite containing only real `ID nnnn` labels. Its old world width
   was 236 units. At Fit All, median tray height was only 0.41 px; existing
   status-circle strokes diminished to approximately 0.017 px.

The current catalog's **largest tray has 13 rows**, not tens or hundreds.
Its height is only 441 units. This measurement is why multi-column packing was
not introduced: it would widen a width-limited forest without addressing a tall
tray failure.

## Packing, trays and routing

The visual shell, Inspector, typography, dark/light palette, selection semantics,
search, camera arithmetic, 220 ms navigation and reduced-motion behavior remain.
`model.js`, `model.json`, `index.html` and `routing.js` are byte-identical to the
start of this refinement. Changes are confined to the global prototype.

`layout.js` now follows one bottom-up complete-envelope pass:

- Recursively measure child subtrees, including all Category cards, descendant
  cards, row hit areas inside tray surfaces and connector clearance.
- Pack Category envelopes in canonical order, with a **24-unit envelope gap**.
  Ordinary card/tray safety inset is **12 units**; root safety remains 24.
  No disclosure controls exist in this always-rendered scene.
- Include the parent's direct tray as an actual item in the child region.
  Center the parent over that region before forming the combined envelope.
  Parent centering applies at every depth. No space is allocated for missing
  descendants, previous coordinates or a future scope.
- Root siblings use the same complete envelopes, with a consistent **112-unit
  inter-root gap**. Their actual measured root cards supply the minimum region
  width. Computer science no longer determines other roots' minimum widths.
- Keep one common y-band per depth, using the measured maximum card/tray heights
  and existing V6.6 inter-level/tray clearances. Remove the catalog-count-derived
  22,944-unit blanket gap. The approved natural upper-card scales are retained.

Reference rows now measure their actual ID labels with 44 units of marker/text
allowance and a 112-unit minimum. Padding makes reference-only trays **128 units**
wide. Resolved/partial Topic rows retain their V6.6 220-unit width and wrapping;
mixed trays expand to the widest actual row. All 725 current trays stay in one
canonical-order column. Every row remains independently rendered and focusable.

The V6.6 orthogonal router already supported short parent stems and shared local
rails. It is reused unchanged, with the newly packed/centered child ports as
input. Each parent's stem is 28 units; its rail spans its actual immediate child
ports and direct-tray port, not a separately allocated global lane. Child drops
end at real top ports. Shared pieces are still unioned once. Large real fan-outs
still require long rails: the presentation Atlas-to-root routes and Computer
science's broad child set cannot have tiny spans while retaining non-overlapping
rectangular envelopes and canonical order. There are no decorative curves.

For overview optics, the existing **one status circle per real leaf** is reused
as the slot cue (`.core.slot-cue`), with a non-scaling stroke floor of **0.45 px**.
No second marker, density bar, aggregate entity or sampled subset is added.
The circle diameters retain the existing V6.6 bounded optical behavior. Tray
outlines use restrained 0.9 px non-scaling strokes and stronger existing-category
surface contrast in overview. At readable focus, the original marker stroke and
row appearance are unchanged. There are no per-Topic thresholds, visibility
changes, new zoom modes or layout changes during navigation.

## Bounds, connector and gap comparison

World units unless noted. A connector span is `max(x) − min(x)` for a logical
Category/context-to-child route or Category-to-tray route (1,574 routes in both
versions). Category-only statistics exclude 725 tray routes. This avoids counting
shared SVG rail fragments as if each were a complete semantic connection.
The raw JSON also reports horizontal-only physical-segment statistics.

| Metric | Before | After | Change |
| --- | ---: | ---: | ---: |
| Global width | 392,798.64 | 254,297.00 | -35.3% |
| Global height | 192,969.84 | 12,728.84 | -93.4% |
| Aspect ratio, width / height | 2.04 | 19.98 | +881.5% |
| Fit All scale (%) | 0.28 | 0.45 | +58.2% |
| Shared hierarchy segment count | 2,643.00 | 2,715.00 | +2.7% |
| Connector horizontal span — median | 170.00 | 119.00 | -30.0% |
| Connector horizontal span — p90 | 2,210.00 | 1,632.00 | -26.2% |
| Connector horizontal span — p95 | 4,760.00 | 3,382.50 | -28.9% |
| Connector horizontal span — max | 181,903.32 | 117,534.50 | -35.4% |
| Category-only horizontal span — median | 510.00 | 404.00 | -20.8% |
| Category-only horizontal span — p90 | 4,050.00 | 2,953.00 | -27.1% |
| Category-only horizontal span — p95 | 9,010.00 | 6,782.50 | -24.7% |
| Category-only horizontal span — max | 181,903.32 | 117,534.50 | -35.4% |
| Parent/child center distance — median | 23,156.95 | 837.79 | -96.4% |
| Root-region gap (each) | 4,491.44 | 112.00 | -97.5% |
| Sibling-envelope gap — median | 64.00 | 24.00 | -62.5% |
| Sibling-envelope gap — maximum | 4,491.44 | 112.00 | -97.5% |

The physical SVG hierarchy segment count increased because changed centered
ports introduce different shared-rail junction splits; the logical route count
and semantic hierarchy did not increase. This is not duplicated edge rendering.

The height and center-distance reduction removes the measured vertical waste,
but the aspect-ratio increase is a visual regression: deep structure is compressed
into a shallow strip at complete fit. A smaller bounding area is not automatically
a more useful orientation view. This is the specific remaining issue, not a reason
to hide leaves, add adaptive coordinates or reinstate giant empty bands.

Root envelopes (clearance included; these can slightly exceed rendered content
bounds) retain canonical numeric-ID order: Math, Computer science, Natural
science, Product development, Generative AI.

| Root | Before width × height | After width × height |
| --- | ---: | ---: |
| Math | 40,422.96 × 97,000.92 | 36,061.00 × 6,810.92 |
| Computer science | 224,572.00 × 165,995.28 | 160,064.00 × 8,602.28 |
| Natural science | 40,422.96 × 97,066.92 | 19,248.00 × 6,876.92 |
| Product development | 40,422.96 × 74,268.74 | 19,248.00 × 6,441.74 |
| Generative AI | 40,422.96 × 74,070.74 | 19,248.00 × 6,243.74 |

| Root envelope | x0 | x1 | y0 | y1 |
| --- | ---: | ---: | ---: | ---: |
| Before · Math | -202,114.80 | -161,691.84 | 26,978.56 | 123,979.48 |
| Before · Computer science | -157,200.40 | 67,371.60 | 26,978.56 | 192,973.84 |
| Before · Natural science | 71,863.04 | 112,286.00 | 26,978.56 | 124,045.48 |
| Before · Product development | 116,777.44 | 157,200.40 | 26,978.56 | 101,247.30 |
| Before · Generative AI | 161,691.84 | 202,114.80 | 26,978.56 | 101,049.30 |
| After · Math | -127,158.50 | -91,097.50 | 4,122.56 | 10,933.48 |
| After · Computer science | -90,985.50 | 69,078.50 | 4,122.56 | 12,724.84 |
| After · Natural science | 69,190.50 | 88,438.50 | 4,122.56 | 10,999.48 |
| After · Product development | 88,550.50 | 107,798.50 | 4,122.56 | 10,564.30 |
| After · Generative AI | 107,910.50 | 127,158.50 | 4,122.56 | 10,366.30 |

Rendered global bounds before: x = [−201287.32, 191511.32],
y = [−8, 192961.84]. After: x = [−127154.50, 127142.50], y = [−8, 12720.84].
All complete bounds fit the usable canvas. The exact same coordinates drive the
minimap. The small roots retain their own visible root cards and guide entries;
Computer science remains the largest physical region.

## Tray and projected-card measurements

Tray count remains **725**. Ordering, identity and row count are unchanged.

| Distribution | Minimum | Median | p90 | p95 | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tray width · Before | 236.00 | 236.00 | 236.00 | 236.00 | 236.00 |
| Tray width · After | 128.00 | 128.00 | 128.00 | 128.00 | 236.00 |
| Tray height · Before | 45.00 | 144.00 | 276.00 | 342.00 | 441.00 |
| Tray height · After | 45.00 | 144.00 | 276.00 | 342.00 | 441.00 |
| Tray area · Before | 10,620.00 | 33,984.00 | 65,136.00 | 80,712.00 | 104,076.00 |
| Tray area · After | 5,760.00 | 18,432.00 | 37,996.00 | 43,776.00 | 92,748.00 |
| Projected tray width (px) · Before | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 |
| Projected tray width (px) · After | 0.57 | 0.57 | 0.57 | 0.57 | 1.06 |
| Projected tray height (px) · Before | 0.13 | 0.41 | 0.78 | 0.97 | 1.25 |
| Projected tray height (px) · After | 0.20 | 0.65 | 1.24 | 1.54 | 1.98 |

Smallest by area before/after: Normal-form games (Category 1920), one row,
236×45 → 128×45. Median-area examples: Regression (1327), 236×144 before;
Airflow (3241), 128×144 after. Largest by area: Advanced features (878), 236×441
before; Classes and members (1262), 236×393 after. Advanced features remains the
largest by row count and height: **13 rows, 128×441** after. Ties select the first
item in deterministic scene order; these are size representatives, not invented
semantic groupings.

At 1440×900 Fit All, projected Category-card median sizes are:

| Presentation depth (real roots = 1) | Before width × height, px | After width × height, px |
| --- | ---: | ---: |
| 1 | 54.50 × 9.95 | 86.22 × 15.74 |
| 2 | 8.63 × 2.96 | 13.65 × 4.68 |
| 3 | 2.16 × 0.97 | 3.41 × 1.53 |
| 4 | 0.54 × 0.24 | 0.85 × 0.38 |
| 5 | 0.54 × 0.24 | 0.85 × 0.38 |
| 6 | 0.54 × 0.18 | 0.85 × 0.29 |
| 7 | 0.54 × 0.24 | 0.85 × 0.38 |
| 8 | 0.54 × 0.13 | 0.85 × 0.20 |

Fit All scale increases from **0.00283828 to 0.00449081** (about **1.58×**).
Existing status-circle diameters project to approximately **0.040 → 0.063 px**;
their non-scaling stroke is now **0.45 px** rather than **0.017 px**. Exactly
**3,106 cues** exist before/after every navigation action in the refined scene.
The old scene had the same 3,106 status circles, without the cue class/stroke floor.

This makes tray distribution and row-derived marks more visible, but adjacent
rows project closer than one physical pixel at Fit All. Individual cues can
visually merge through rasterization; the DOM retains each real circle, row and
label. They are not replaced by a density bar. Individual titles are still
micro-text, and readable focus remains the reading mechanism.

## Focused validation

**35 checks pass:** the existing 30 checks plus explicit tray/tray overlap,
complete-envelope containment, one-cue-per-row, large-tray complete fit, and
cue persistence checks. See [results.json](tests/refinement/results.json).

- **849 Categories exactly once, 3,106 leaf slots exactly once, all five roots.**
- **89 actual Topics** (1 resolved, 88 partial), **3,017 references**. No fake
  titles, URLs, theory metadata or Topic entities. Model/data bytes unchanged.
- Canonical sibling/row ordering and same-depth Category alignment preserved.
- **Zero card overlaps, zero tray/tray overlaps, zero unrelated tray/card
  overlaps, zero sibling-envelope overlaps, zero invalid hierarchy endpoints,
  zero hierarchy intersections with card/tray interiors.** Complete envelopes
  contain their descendant cards and trays, including row hit areas.
- Category selection preserves the camera. Full subtree fits remain complete;
  secondary memberships navigate to the same single physical leaf.
- Search, keyboard activation, Topic/reference focus and reduced-motion behavior
  pass. Resolved and unresolved focus retain **16 px** Topic/reference text.
- Zoom, wheel, pan, fit, selection and search preserve the same DOM rows and
  exact geometry, with **zero navigation-triggered layout calls**.
- No leaf, title or cue is removed or hidden with zoom. No browser errors.

One 1440×900 browser review; Dark is primary. Existing light-toggle smoke remains
inside the original 30 checks, but no additional light or viewport screenshots
were generated. No historical viewport matrix, migration suite or repository-wide
regression suite was run.

## Performance

Local macOS Chromium, one-run measurements in milliseconds. Startup before/after
was freshly measured by the same oracle; action ranges below come from the final
focused run. Dispatch/CPU timings exclude asynchronous camera animation.

| Startup measurement | Before | After |
| --- | ---: | ---: |
| Model / adapter | 10.00 | 10.20 |
| Layout + routing | 83.70 | 82.40 |
| Tray packing (included in layout) | 15.60 | 14.10 |
| Initial draw | 130.60 | 127.20 |
| Browser initialization | 299.50 | 293.30 |
| Initial Fit All dispatch | 47.40 | 43.40 |

Read-only Catalog projection/build: **1,654.35 ms**;
the resulting data was compared to the existing `model.json`, without writing
Knowledge or replacing the prototype snapshot. This data build is separate from
the **82.40 ms** browser layout/routing build.

Final action samples:

| Action | Measured dispatch range, ms |
| --- | ---: |
| Fit All | 19.60–43.40 |
| Fit subtree | 9.20–52.00 |
| Topic/reference focus | 8.30–55.80 |
| Search navigation | 23.90–33.80 |

The highest focus sample includes synchronous reduced-motion navigation and its
style/layout flush. Normal animated focus dispatch is approximately 8–9 ms;
the camera duration remains 220 ms. Initial draw and layout show no material
regression in these local samples. No performance optimization, virtualization
or content suppression was introduced. In-place selection updates from the
previous implementation remain intact.

## Exactly six final review states

Captured and visually inspected at 1440×900 Dark:

1. [GLOBAL-FIT-ALL.png](tests/refinement/review/GLOBAL-FIT-ALL.png)
2. [COMPUTER-SCIENCE-FIT.png](tests/refinement/review/COMPUTER-SCIENCE-FIT.png)
3. [PROGRAMMING-LANGUAGES-FIT.png](tests/refinement/review/PROGRAMMING-LANGUAGES-FIT.png)
4. [LARGE-TOPIC-TRAY-FIT.png](tests/refinement/review/LARGE-TOPIC-TRAY-FIT.png)
5. [TOPIC-FOCUS.png](tests/refinement/review/TOPIC-FOCUS.png)
6. [UNRESOLVED-REFERENCE-FOCUS.png](tests/refinement/review/UNRESOLVED-REFERENCE-FOCUS.png)

The previous five equivalent review images and original focused results are
retained under [tests/refinement/before/](tests/refinement/before/); no before
large-tray image existed, so none is fabricated. The six final images show the
same V6.6 interface. Focused rows/trays remain comfortably recognizable, with
more adjacent real context fitting on screen. The large orientation views expose
the residual flattened hierarchy; visual acceptance is not claimed.

## Protected files and local verification

The existing independent integrity check again verifies **427 protected files**,
including original V6.6, all docs/real Production, State, Knowledge and shared
runtime sources. Content **and file inventory** remain unchanged, excluding
pre-existing dependency/cache directories. Result:
[integrity-results.json](tests/refinement/integrity-results.json).
Prototype source hashes before/after are also retained in `tests/refinement/`;
the semantic adapter, data, routing and HTML are byte-identical.

Local URL remains **http://127.0.0.1:8777/**. Exact local server command:

```sh
python3 -B -m http.server 8777 --bind 127.0.0.1 --directory /Users/antonplatonov/IdeaProjects/hyperskill-projects/prototypes/knowledge-atlas-v6-global
```

From the repository root, the focused browser command used was:

```sh
PLAYWRIGHT_MODULE=/tmp/adaptive-progress-browser/node_modules/playwright \
CHROMIUM_EXECUTABLE='/Users/antonplatonov/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing' \
node prototypes/knowledge-atlas-v6-global/tests/focused.cjs
python3 -B prototypes/knowledge-atlas-v6-global/tests/integrity.py
```

These browser paths are test-only environment overrides. The prototype needs only
a static local server. All task writes stay in `prototypes/knowledge-atlas-v6-global/`.
Original V6.6 and real Production / State / Knowledge remain byte-identical.
No commit, push, deployment, new prototype family or My Skill Tree work occurred.
