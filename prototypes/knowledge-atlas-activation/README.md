# Activation geometry — isolated local prototype

Baseline: `4e4a15bf4cfb7fb9abf587aebdae74033bb5624d`.
Nothing here activates a real course, imports Topic metadata, records progress,
accepts geometry, or modifies Production. Generation remains 0.

## Local review

From the repository root:

```sh
python -B prototypes/knowledge-atlas-activation/build-fixtures.py
python -B -m http.server 8766 --bind 127.0.0.1
```

Open <http://127.0.0.1:8766/prototypes/knowledge-atlas-activation/>.
The scenario selector lives in the development inspector. Switching scenarios
preserves the camera; Fit Active Atlas, Fit Existing and Focus Candidate are
explicit camera actions. Search, subtree collapse, Topic focus, dark/light,
minimap, project coverage and the accepted relation UI reuse V6 behavior.
The canvas remains pan/zoom based. It never fits the entire global catalog.

## Semantic boundary and fixture adapter

`build-fixtures.py` constructs in-memory synthetic evidence and invokes the
existing `ActivationPlanner`. It exports those plans only into this prototype.
The geometry layer consumes explained renderable candidates from that plan;
prerequisites, sibling proximity and project-filtered maps create no relevance.

The Python chain uses real global Categories 331 → 1201 → 428. All six displayed
Topic labels are neutral **fixture-only** text, not Hyperskill metadata.
The numeric-only planner/model contract requires an isolated adapter. Its
temporary numeric IDs become `fixture-topic:*` keys before scene construction.
Exported Topic identities have `hyperskill_id: null`. Adapter numbers are only
test plumbing; no real global entity, course membership, learning or verification
claim is created. There are no lesson links for fixture Topics.

References 333/336 remain real unresolved catalog references. Their missing
Topic classification/title, memberships and synthetic relevance reasons appear
only in the report. They receive no rows, search entries, minimap geometry or
placeholder titles. `METADATA_REQUIRED` remains the final blocking outcome even
when a renderable subset is shown for development review.

## Frozen geometry

All 135 accepted nodes retain **exactly** x, y, width and height. All 26 accepted
trays and 119 hierarchy segments are copied unchanged. No baseline subtree
layout is recomputed. `AtlasIncremental.update` is never called. The accepted
checkpoint is read only; there is no activation-state writer or approval action.

Category cards, measured font sizes, padding, ports and single-column Topic
packing reuse accepted V6 tokens. Existing category depth bands remain fixed.
Deeper new bands can extend downward with the V6 tray/child gaps. Frozen trays
are presentation containers, not semantic nodes.

The bounds hash covers sorted stable key/x/y/width/height tuples:
`3ae5f458602cd10a819dac851e7c59c29b68d919705e6f81c961633b15ce6323`.
Every scenario reports this hash and the hash of its retained accepted bounds.

## Placement search and activation-order presentation

**Personal spatial memory takes priority over global sibling sorting.**
Taxonomy sibling order is not a requirement to reorder accepted visual siblings.
Existing siblings stay fixed; new siblings append deterministically outside their
current center range. Candidate categories are processed by depth then stable
identity; Topic rows by fixture identity. Taxonomy parentage is unchanged.

The deterministic search generates positions from card/tray obstacle boundaries,
parent anchors and discrete outer-canvas slots. It uses a bounded beam of 64
states and retains spatially diverse 128px cells before filling remaining slots
by score. It examines up to 512 horizontal positions and 24 bus heights per
state. This is a conservative prototype search, **not an exhaustive proof that
every rejected layout is mathematically impossible**.

Hard constraints precede scoring: no semantic overlap, connector through card,
independent hierarchy crossing, invalid port or accepted-bound mutation.
Costs are lexicographic, not a weighted sum:

1. Added canvas area.
2. Added physical connector length.
3. Total horizontal distance from structural parents.
4. Maximum parent-centering drift.
5. Positive-side preference, absolute coordinate, coordinate, stable serialization.

Safe areas, sibling spacing and discrete slots encourage consistent whitespace.
No random values, timestamps or durations enter geometry/report serialization.
Font measurement uses the accepted browser canvas; the font canary is checked.
Reports contain no performance timings; timings are recorded separately.

## Additive hierarchy grammar

Connections use exact bottom/top card ports, orthogonal stems and horizontal
buses. Bus heights start with V6's preferred parent-to-bus gap and may use
obstacle-boundary alternatives within the parent/child band gap. These are tree
attachment buses, not arbitrary graph routing lanes.

Already drawn same-parent collinear pieces are subtracted from new segments;
only their uncovered extensions are appended. Same-parent bus junctions are
legitimate; intersecting independent-parent routes are rejected. Existing shared
segments are not shortened, re-centered, split or rewritten. Programming
languages initially has one vertical Java stem. Python adds a horizontal branch
off that existing stem and a new child stem; the original vertical stays exact.

Accepted prerequisites/dependents still use the existing LCA taxonomy router.
The 26 Project-113 requirements and 12 Stage-4 requirements keep their amber
taxonomy paths. Relations do not activate dormant endpoints. The fixture tests
exercise the existing same-tray LCA behavior; no real synthetic relations or
project evidence are added to Knowledge data.

## Canvas growth and refusal policy

Canvas expansion is additive left/right/down. Accepted nodes are never scaled
or moved to center a parent. Drift is reported instead. Centralized prototype
thresholds in `ActivationGeometry.TOKENS` refuse:

- Any first activation of another global root.
- No safe slot found by the bounded search.
- A new attachment longer than 5,200px or parent drift above 2,400px.
- Width growth above 75%, area growth above 150%, or branch isolation above 1,600px.
- A Topic append to an accepted tray: a separate additive-tray design is needed.

These are explicit review heuristics, not accepted Production policy. Refusal
returns `ACTIVATION_REBALANCE_REQUIRED` and keeps the visible scene at baseline.
It never starts a rebalance. No automatic geometry acceptance is implemented.

## Scenarios

| Scenario | Meaning |
| --- | --- |
| Baseline | Exact accepted 46 Categories / 89 Topics; no additions. |
| Small | Real Python chain plus 6 fixture rows; same-root visual review. |
| Large | Several real Python categories, 156 fixture rows; append or explicit refusal. |
| Blocked | Small renderable preview plus unresolved 333/336 in report only. |
| New Root | Math; no candidate geometry, explicit multi-root refusal. |
| New Major Branch | Real Algorithms and data structures Category plus 8 test rows. |

For a refused Large scenario, Focus Candidate falls back to the existing
Programming languages region in the review harness. No refused fixture branch
is drawn. Its requested counts/packing needs remain in the report.

## Validation and review artifacts

```sh
python -B prototypes/knowledge-atlas-activation/tests/test_integrity.py -v
FONTCONFIG_FILE="$PWD/scripts/knowledge_atlas/fontconfig.xml" \
  node prototypes/knowledge-atlas-activation/tests/browser.cjs
```

The browser harness serves local files via request interception and rejects all
external origins. Configure `PLAYWRIGHT_MODULE` and `CHROMIUM_EXECUTABLE` if the
default installed runtime paths differ. It needs the accepted fonts/browser for
pixel checks. Screenshots/candidate geometry live in ignored `tests/output/`;
machine-readable deterministic scenario reports live in `reports/`. The local
protected-file manifest is ignored and guards all 732 pre-existing tracked and
untracked files from this session. On a fresh checkout, create it before work with
`python -B prototypes/knowledge-atlas-activation/audit-protected.py --capture`.
That command refuses to overwrite an existing baseline. Check it with the same
script without flags. It is not Knowledge truth or an activation state file.

The review matrix covers widths 1920, 1440, 1280, 1200, 1024, 768, 430, 390, 320,
each dark/light. Baseline map pixels are compared to the accepted Production
runtime with non-map control overlays hidden; the inspector intentionally adds
development controls. No viewport or geometry tolerance excuses node movement.

## Persistence boundary and next decision

Do not promote this prototype directly into Production. An approved future
activation would record new geometry as presentation history, independently of
course/project/personal truth. Existing branch positions survive course endings.
Before persistence, review the corridor attachment visually, calibrate refusal
thresholds, design additive tray growth and define segment-level overlay routing
for future cross-branch candidate relations. Multi-root geography needs its own
design. The large-case refusal is useful evidence of limited room near Python,
not permission to rebalance Java automatically.

## Small Activation Variants

Choose **Small Activation Variants**, then Current, Parent Distance, Centering,
Connector or Balanced. Fit Comparison uses the same frozen parent/Java/candidate
review region for every variant; changing variants preserves the camera. Focus
Candidate provides a separate reading view. All variants consume the identical
Small ActivationPlan; no semantic evidence or fixture source is changed.

The comparison search retains 316 valid placements from four deterministic
objectives. These are evaluated search candidates, not exhaustive global optima.
Its centralized comparison policy uses a 192-state beam, a minimum new stem of
12px (28px remains preferred), and explicit 128/256/384px growth probes. A narrow
existing corridor above Java's bus becomes usable without changing any accepted
segment. This is optional comparison policy: ordinary scenarios retain the
original policy and outcomes.

Hard collision, crossing, exact-port and frozen-bound constraints precede costs.
Parent Distance minimizes the new root's distance from its semantic parent.
Centering minimizes the worst drift across all affected parents, preventing a
short initial attachment from merely transferring the problem downstream.
Connector minimizes total route length, then the longest horizontal bus.
Balanced weights root distance, longest bus and worst drift at 1 each, whitespace
deviation and width growth at 0.25 each, normalized by the attachment parent's
card width; deterministic metric/coordinate ties follow. Total connector length
ties in the selected zero-growth candidates, so Connector and Balanced legitimately
select identical geometry. Growth is not a dominant cost in this comparison.

The original 1,291px metric describes drift from direct-child card extrema, not
parent movement or the complete subtree bounding-box center. The latter drifts
only 128px. Normalize direct-child drift against the frozen Programming languages
subtree width (5,676px); compare first connector length with the 614.5px median
of 34 existing sibling connections. Do not impose a new arbitrary drift cutoff.

**Visual recommendation: Centering** for this Small fixture. Worst drift falls
to 919px, the first connector to 1,920px, and the new branch stays more compact
than Parent Distance or Balanced. It preserves all accepted bounds/segments,
requires no canvas growth and remains ACTIVATION_REVIEW_REQUIRED. This finding
does not establish a general activation capacity or approve persistence.

```sh
FONTCONFIG_FILE="$PWD/scripts/knowledge_atlas/fontconfig.xml" \
  node prototypes/knowledge-atlas-activation/tests/variants.cjs
```

See `reports/VISUAL-REFINEMENT.md`, `reports/small-variant-comparison.json` and
`reports/variants-validation.json`. Deterministic comparison screenshots and
candidate geometry are local ignored files under `tests/output/`.
