# Activation Geometry Visual Refinement

## Why Current Drift Is 1291 px

The semantic attachment parent is category:1164, **Programming languages**, center x=1154.
Its accepted Java child is also centered at 1154. The current Python root is at
3736, so the direct-child center-extrema midpoint is (1154+3736)/2=2445:
2445−1154=1291px. No accepted parent moved. The complete new subtree bounding-box
center is 3944.5, offset 2790.5 from the parent; its root offset is 2582px.
The complete accepted-plus-candidate parent subtree bounding-box center is 1282,
only 128px from the parent. These are distinct metrics, not interchangeable.

The current parent-to-Python route is 2664px, including a 2582px horizontal bus.
The four candidate hierarchy routes total 3470px; newly added physical segments
sum to 3418px because 52px reuses the accepted parent stem. The nearest accepted
sibling is Java: center distance 2582px, card-edge gap 2392px.

The original cost is lexicographic: added canvas area, new physical connector
length, summed horizontal attachment distance, worst parent drift, coordinate
and stable geometry ties. The original bounded search explores 38697 placements;
its retained partial states yield 45 completed candidates. Its 28px minimum new
stem places Python's outgoing bus at or below y=405.72, exactly where Java's
accepted long bus spans x=-716..3704. A closer attachment then fails the crossing
gate. The first sampled safe right slot is x=3736, derived from an existing tray
boundary (3756) minus the 20px slot margin. This hard corridor constraint and the
bounded search explain the result; zero-growth preference alone does not.

## Current Candidate

Unchanged original result: Python/Basics/Simple programs centers 3736/3910/4130.
Compact new subtree, width607px, but its language root looks far detached from
Programming languages at overview scale. First connector is 4.34 times the
614.5px median of 34 accepted sibling connections. The long horizontal extension
is correctly attached to the accepted parent stem, with valid ports.

## Parent-Distance Candidate

Centers1539/3910/4130. The new language root is only385px from its parent;
parent drift192.5px, first connector467px (0.76× existing sibling median).
However, this shifts the separation downstream: Python→Basics has2371px drift,
and the new subtree spans2804px. At overview scale Basics can read as a separate
island. A low initial-parent metric is not sufficient for visual acceptance.

## Centering Candidate

Centers2992/3910/4130. Minimizes **worst drift across affected parents** among
retained valid candidates:919px, down28.8% from1291. First connector1920px,
down27.9%, at3.12× the accepted sibling median. New subtree width1351px.
It balances language-root attachment and downstream cohesion without centering
or moving any accepted card. All new categories still use accepted depth bands.

## Connector-Length Candidate

Centers2625/3910/4130. Total route length ties at3470px; longest-horizontal-bus
tie-breaking selects1471px. First connector1553px (2.53× median), initial drift
735.5px, but worst downstream drift1285px. Its1718px subtree is wider than
Centering. It shortens the first connection while keeping nearly the original
worst separation elsewhere.

## Balanced Candidate

Same geometry as Connector, legitimately. Score uses root-parent distance,
longest horizontal bus and worst drift with weight1 each; whitespace deviation
and width growth with0.25 each, normalized by parent card width302px. Stable
metric and coordinate ties follow. Hard validity gates always run first.
The scalar compromise is useful evidence, not the final visual recommendation.

## Candidate Comparison

Normalized drift below = initial parent drift / frozen parent subtree width5676px.
Connector column = first route / total four new routes, in px. REVIEW means
ACTIVATION_REVIEW_REQUIRED. No alternative changes the semantic ActivationPlan.

| Candidate | Existing displacement | Parent drift px | Normalized drift | Worst affected-parent drift px | Connector first / total px | Canvas width / height growth px | Overlaps | Crossings | Outcome |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| current | 0 | 1291 | 22.74% | 1291 | 2664 / 3470 | 0 / 0 | 0 | 0 | REVIEW |
| parent-distance | 0 | 192.5 | 3.39% | 2371 | 467 / 3470 | 0 / 0 | 0 | 0 | REVIEW |
| centering | 0 | 919 | 16.19% | 919 | 1920 / 3470 | 0 / 0 | 0 | 0 | REVIEW |
| connector | 0 | 735.5 | 12.96% | 1285 | 1553 / 3470 | 0 / 0 | 0 | 0 | REVIEW |
| balanced | 0 | 735.5 | 12.96% | 1285 | 1553 / 3470 | 0 / 0 | 0 | 0 | REVIEW |

The search retains316 distinct valid candidates across four objectives; these
are bounded-search minima, not a proof of exhaustive optimality. Candidate
regions come from accepted/candidate card and tray boundaries, parent offsets,
existing corridor slots, and explicit horizontal expansion probes. Complete
coordinate and rejection inventories are in small-variant-comparison.json.

Valid128/256/384px width-growth probes were found (13 retained candidates each).
Their minimum root distance remains385px and minimum worst drift919px, exactly
as in zero-growth candidates. Minimum total route length rises from3470px to
3798/3926/4054px respectively. Growth is allowed and evaluated, but buys no
better attachment for this fixture. No selected alternative grows the canvas.

## Recommended Candidate

**Centering**, scoped to this exact Small ActivationPlan. It reduces the worst
separation rather than hiding it in a downstream connection, preserves compact
branch grouping, and keeps every accepted coordinate and connector segment exact.
Do not automatically replace the ordinary Small scenario: the comparison mode
retains Current and all objective alternatives for review.

## Visual Reasoning

All five overviews use the same camera and frozen parent/Java/candidate review
region. Focused views additionally test category/tray reading. Current is compact
but remote; Parent Distance is close at its root but split internally; Balanced
and Connector improve the initial attachment at the cost of a wider internal
span. Centering makes the three-card chain easier to read as one branch while
its parent stem unambiguously originates from Programming languages.

The usable activation corridor is pre-existing empty presentation space:
Python's bottom is y=377.72; a comparison-only12px minimum stem permits its bus
at389.72,16px above Java's frozen bus405.72. The new Basics stem at3910 lies
beyond Java's bus endpoint3704. No old bus is rewritten. Existing segments remain
byte-identical and candidate segments are additive.28px remains preferred;
12px is not a universal production spacing policy.

Parallel buses still look dense at zoomed-out scale. At reading zoom the separate
buses and exact ports make parentage traceable without Inspector assistance.
This corridor supports the reviewed fixture, not arbitrary future sibling
capacity. Personal spatial memory takes precedence over canonical visual
sibling sorting; taxonomy semantics and activation history stay separate.

## Large Activation Regression

6 requested categories /156 fixture topics: ACTIVATION_REBALANCE_REQUIRED.
No refusal thresholds weakened; comparison policy applies only to Small variants.

## Blocked Regression

METADATA_REQUIRED. References333/336 remain report-only, without fake titles or
user-facing geometry. The renderable fixture preview remains distinct.

## New Root Regression

ACTIVATION_REBALANCE_REQUIRED. No Math geography appended to Computer science.
Baseline remains NO_CHANGE and ordinary Small remains ACTIVATION_REVIEW_REQUIRED.

## Production Regression

All14 docs/knowledge-map assets byte-identical; no packaging, commit, push or
deploy. The protected manifest verifies all732 pre-existing files, including555
unrelated untracked files. Global catalog, Course-8 projection and personal
progress are unchanged. The Small fixture JSON and original Small report are
byte-identical to their refinement baselines.

## State Regression

Checkpoint and update snapshot byte-identical. Generation0, layout schema2,
algorithm atlas-incremental-2. All135 accepted category/topic bounds,26 trays and
119 connector segments remain exact in every alternative. Existing-node bound
hash remains3ae5f458602cd10a819dac851e7c59c29b68d919705e6f81c961633b15ce6323.
No activation state or accepted geometry is persisted.

## Validation

95 comparison/browser checks PASS, including reversed input, repeated byte
serialization, hard geometry gates, identical camera, growth probes, no external
requests, protected hashes, and9 viewport widths×2 themes without page overflow.
102 core prototype geometry/browser checks PASS;7 integrity tests PASS.

## Screenshot Paths

All paths below are local ignored review artifacts under tests/output/:

- small-current.png and small-current-focused.png
- small-parent-distance.png and small-parent-distance-focused.png
- small-centering.png and small-centering-focused.png
- small-connector.png and small-connector-focused.png
- small-balanced.png and small-balanced-focused.png
- variants-1440-dark.png / variants-1440-light.png
- variants-390-dark.png / variants-390-light.png

Comparison entry: index.html?scenario=small-variants. Machine-readable metrics:
reports/small-variant-comparison.json; checks:reports/variants-validation.json.

## Ready For Persistence?

**YES for the reviewed Centering Small fixture only**: visually coherent enough
for the next separately approved persistence phase, with exact accepted geometry
and zero overlaps/crossings. This is not permission to persist now, nor a general
claim that Large or new-root activation is safe. Broader capacity, multiple
successive activations and acceptance policy still need future review.
