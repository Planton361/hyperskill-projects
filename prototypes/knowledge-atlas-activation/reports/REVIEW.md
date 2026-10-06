# Activation Geometry Prototype — Review Report

## Prototype Files

All new files are under `prototypes/knowledge-atlas-activation/`:
`activation-geometry.js`, `build-fixtures.py`, `preview.js`, local `app.js`,
`index.html`, `style.css`, `audit-protected.py`, `README.md`, fixture plans,
`tests/browser.cjs`, `tests/test_integrity.py`, and scenario/validation reports.
The accepted renderer assets are read from Production; none are rewritten.

## Frozen Baseline

Baseline commit: `4e4a15bf4cfb7fb9abf587aebdae74033bb5624d`.
135 exact accepted node bounds, 26 exact trays, 119 exact connector segments.
46 Categories, 89 Topics, 136 explicit hierarchy pairs.
Existing-bound SHA-256:
`3ae5f458602cd10a819dac851e7c59c29b68d919705e6f81c961633b15ce6323`.
Every scenario retains the same hash; all x/y/width/height comparisons are exact.

## Placement Algorithm

Pure ActivationPlan consumer with measured V6 Category/Topic sizes. Hard bounds,
port, collision, through-card and independent hierarchy crossing guards precede
lexicographic area/length/distance/drift scoring. Bounded spatially diverse beam
search: 64 states, 512 horizontal slots, 24 bus-height alternatives. See README
and centralized TOKENS for the exact deterministic policy and limitations.

## Sibling Activation Order

Accepted siblings remain fixed. New siblings append in deterministic identity
order outside accepted sibling positions. Personal spatial memory wins over
catalog sibling sorting; taxonomy semantics remain unchanged.

## Connector Extension

All original 119 segments remain exact. Shared same-parent collinear coverage
is subtracted from new strokes; only uncovered bus/stem pieces are added.
The small case adds 10 segments, including a branch off the accepted Programming
languages stem. Legitimate same-parent junctions are not independent crossings.

## Small Activation

3 real structural Categories (Python → Basics → Simple programs), 6 fixture-only
Topic rows. Placement x: 3736 / 3910 / 4130, accepted depths 2 / 3 / 4.
Outcome: `ACTIVATION_REVIEW_REQUIRED`. Zero existing displacement.

## Large Activation

Requested: 6 Categories and 156 fixture rows, maximum proposed tray height
1,596px. The bounded search fails while attaching category:1202, with frozen
cards/trays and hierarchy constraining the corridor. Outcome:
`ACTIVATION_REBALANCE_REQUIRED`. No rejected candidate geometry is drawn.
This is conservative refusal, not an exhaustive impossibility proof.
The focused review capture shows the existing attachment region and refusal.

## Blocked Metadata

Renderable subset: 3 Categories + 6 fixture Topics. References 333 and 336 stay
undrawn, absent from ordinary search and minimap. Both retain category:428
membership, fixture-only course relevance and missing Topic type/title in the
report. Final blocking outcome: `METADATA_REQUIRED`.

## New Root

Math fixture: `ACTIVATION_REBALANCE_REQUIRED`; zero candidate geometry.
A separate multi-root visual design is required. No fake attachment to Computer
science is created.

## Canvas Growth

Accepted bounds: x −4460…4456, y −8…1859.14; width 8916px, height 1867.14px.
Small/Blocked: +0px width and height. Refused Large/New Root: unchanged.
Additional same-root Algorithms and data structures fixture: 1 Category,
8 fixture Topics, 5 new segments; +288px width to the left, +0px height;
`ACTIVATION_REVIEW_REQUIRED`.

## Parent Centering Drift

Small/Blocked: maximum 1291px, chiefly Programming languages gaining Python.
Parents are not moved to restore symmetry. New-major case: 146px.
Prototype threshold: 2400px; thresholds require review before persistence.

## Overlaps

Zero new/new and new/accepted semantic overlap. Topic rows are contained in their
presentation trays. Minimum small-case clearance: 16px cards, 20px trays.
The ledger treats intentional row-in-tray containment as containment, not overlap.

## Hierarchy Crossings

Zero new/new or new/accepted independent hierarchy crossing; zero connector
through-card intersections and zero invalid ports in every scenario.

## Topic Tray Behavior

Accepted V6 one-column packing, 220px Topic width / 236px tray width for these
labels, 8px tray padding, 4px row gap, 14px text with 17px line height.
Fixture rows are 29px tall. Existing 26 tray objects remain exact.
Appending into a frozen existing tray is explicitly deferred/refused.

## Project Evidence Regression

Project 113 still has 26 distinct requirements; Stage 4 (617) has 12.
Amber paths and accepted coverage signatures match across Baseline, Small,
Blocked and new-major previews. No project_applies or real synthetic evidence.

## Relation Regression

Accepted prerequisite/dependent path/index signatures remain identical.
137 directed pairs of each type remain in source truth. Same-tray candidate
fixture routing uses the existing LCA router. No free graph lines are added;
relations do not create relevance. Future candidate cross-branch routes reusing
coarse frozen segments need additional overlay-index work before persistence.

## Minimap / Fit

Minimap includes 49 Categories / 27 trays for Small/Blocked and excludes blocked
references. Fit Active Atlas covers accepted plus preview geometry; Fit Existing
matches baseline fit. Scenario toggles preserve the viewport transform.
Search/subtree collapse/Topic focus work for accepted and fixture entities.

## Desktop

Widths 1920, 1440, 1280, 1200, 1024, 768; Dark and Light reviewed and checked.
Baseline graph pixels match accepted Production at every viewport. Development
inspector/controls are intentionally different; map control overlays are hidden
only for the pixel comparison. Baseline node geometry has no tolerance.

## Mobile

Widths 430, 390, 320; Dark and Light. No page-level horizontal overflow; controls
remain usable. The panned local reading view displays fixture rows at V6 reading
scale. The inspector follows the map, matching the accepted mobile structure.

## Determinism

All six scenarios: repeated geometry/report serialization byte-identical;
reversed candidate/display input yields identical output. Fixture regeneration
is byte-identical. Timings are separate from deterministic scenario reports.

## Performance

Final core run, seven samples per scenario: Small median 303.4 ms;
Large median 254.3 ms. This measures candidate computation only, not a
full-global layout or a frozen-node layout recalculation. Browser: 154.0.8037.57.

## Production Regression

All 14 Production assets byte-identical. All 732 pre-existing tracked/untracked
files retain their hashes. No commits, push, deployment or Production packaging.

## State Regression

Checkpoint/update snapshot byte-identical; no ActivationPlan or accepted
activation geometry is persisted. Prototype JSON and screenshots are review
artifacts only. Personal state stays 31 learned / 12 verified; no aggregate-35
update. Global catalog remains 5 roots / 849 Categories / 3106 leaves,
1 resolved / 88 partial Topics / 3017 unresolved references.

## Generation

0. Layout schema 2; algorithm `atlas-incremental-2`.

## Screenshots / Review Paths

Local viewer: <http://127.0.0.1:8766/prototypes/knowledge-atlas-activation/>.
Ignored local capture folder: `../tests/output/`:

1. `01-baseline-overview.png`
2. `02-small-overview.png`
3. `03-small-focus.png`
4. `04-large-overview.png`
5. `05-large-refusal-focus.png`
6. `06-blocked-metadata.png`
7. `07-new-root-refusal.png`
8. `08-mobile-small.png`

Additional width/theme focused captures are in the same folder. Deterministic
metrics: baseline/small/large/blocked/new-root/major JSON in this directory.
Validation: `validation.json` (154 browser checks, 18 viewport/theme combinations)
and `validation-core.json` (102 checks against final geometry/report code).
Independent Python integrity/regression suite: 7 tests passed.

## Remaining Risks

Bounded search can conservatively refuse a feasible arrangement. The 1291px
parent drift and 2664px longest small attachment need human visual review.
Thresholds are prototype heuristics. Multiple future activations, accepted-tray
expansion, new cross-branch overlay indexing and multi-root geography remain
outside this prototype's acceptance scope. Scene adapter copies the accepted
app and will need reconciliation if that runtime changes.

## Recommendation For Persistence Phase

Review Small and new-major attachments first. Preserve accepted node/segment
hashes as persistence gates. Design additive existing-tray growth, candidate
relation-overlay indexing and activation history explicitly. Persist only
reviewed presentation deltas in a separate approved phase; do not promote this
prototype automatically or rebalance existing Java geography silently.
