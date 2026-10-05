# Exact reviewed activation persistence

Knowledge evidence → relevance plan → local geometry preview → human review →
explicit manifest approval → joint state/Production transaction. Relevance is not
learning, completion is not verification, and presentation history is not Course
membership. No real future Course or synthetic Python evidence is added here.

## Presentation state and bootstrap

`state/knowledge-atlas/activation-state.json`, schema 1, is presentation-only.
It stores active global IDs, exact accepted geometry (including additive hierarchy
segments), ordered geometry/bound/connector hashes, a history version and accepted
manifest events. Unknown state versions/fields require
`ACTIVATION_STATE_MIGRATION_REQUIRED`; no silent rebuilding. The strict public
schema is `activation-state.schema.json`; Python also checks counters, identities,
event fields, hash consistency and checkpoint agreement.

```sh
python -B scripts/update-knowledge-atlas.py --bootstrap-activation-state
```

Bootstrap refuses overwrite, records existing 46 Category/89 Topic history and
Generation 0, and does not rewrite the established checkpoint, update snapshot or
Production. It uses the authoritative accepted geometry, not fresh layout.
Missing history can be read as a virtual baseline for compatibility, but only the
explicit bootstrap writes it. Pending transactions require recovery first.

`history_version` counts accepted activation events; `presentation_generation`
remains the existing layout counter. Bootstrap changes neither. New geometry
increments each exactly once; repeating the exact already-applied manifest
changes neither. Progress, project state/evidence and relations do not increment
layout Generation. Preview is never an activation event.

Accepted geography is ACTIVE_HISTORY. It survives Course completion/current-course
changes. Normal builds filter Knowledge entities by accepted history, retaining
history as a presentation boundary. Missing historical Knowledge metadata is an
explicit error, not permission to remove geography or invent facts.

## Preview and exact approval

```sh
python -B scripts/update-knowledge-atlas.py --dry-run
python -B scripts/update-knowledge-atlas.py \
  --activation-preview /tmp/atlas-course-preview --course 8 --variant current
# Serve /tmp/atlas-course-preview locally; inspect view/index.html and metrics.
python -B scripts/update-knowledge-atlas.py \
  --approve-activation /tmp/atlas-course-preview/activation-manifest.json \
  --reviewed-fingerprint SHA256_COPIED_DURING_REVIEW
python -B scripts/update-knowledge-atlas.py --check
```

Preview writes only a new external/local directory or ignored
`prototypes/activation-previews/` subtree. It refuses overwrite and cannot write
state or Production. The deterministic package contains activation-plan.json,
candidate-geometry.json, metrics.json and activation-manifest.json, plus a static
local `view/` using the exact candidate. No allocation is rerun by this page.
For current Course 8 the package reports NO_CHANGE with no new geometry. Approval
of that package is a read-only NO_CHANGE, not an activation event.

Variants are current, parent-distance, centering, connector and balanced. These
are review choices, not universal acceptance rules. Centering's 919px drift is
only a measured property of the reviewed Small fixture. The geometry mechanism
is promoted into durable modules; the isolated prototype remains reference
material and is never a runtime dependency or Production package input.

The manifest binds:

- semantic ActivationPlan fingerprint (stable set/inventory order);
- complete sanitized Knowledge input, Catalog, Course/project/evidence and
  personal progress fingerprints;
- current activation history and layout checkpoint;
- ordered frozen existing geometry, bounds and connectors;
- exact candidate nodes/trays/rows/additive segments/canvas;
- selected variant, algorithm version/implementation and validation report.

No generated preview/review timestamps participate in these deterministic identities. Source observation dates remain evidence inputs and are deliberately bound. Presentation arrays
preserve order; coordinates are not rounded for fingerprints. Even a subpixel
change invalidates the candidate binding. Semantic input changes, modified
artifacts, history, existing geometry, algorithm or selected variant cause
STALE_ACTIVATION_PREVIEW. Generate a new preview and review it again. A hash is
an integrity/review identity, not a cryptographic authentication credential;
explicit operator invocation authorizes that exact manifest.

Approval also requires the manifest fingerprint copied during human review. A consistently replaced/rehashed package at the same path invalidates that external review token. Approval does not run the placement algorithm again. It verifies bindings,
recomputes independent geometry checks, enforces exact old node/tray/connector
preservation, validates the complete semantic inventory and candidate build, and
publishes only the artifact geometry. Checkpoint allocation descriptors are
derived from reviewed coordinates; they are not allowed to replace those
coordinates/routes during future hydration.

## Gates and transaction

Normal canonical build/Production updates never allocate newly relevant nodes.
They return REVIEW_REQUIRED and request an activation preview. The older
`--approve-review` flag cannot bypass that gate. Isolated legacy allocator tests
without activation history retain their existing explicit test/migration API;
canonical Production and history-aware updates always use the new gate.

Relevant unresolved references block complete activation: METADATA_REQUIRED,
with IDs/reasons/missing fields. No automatic partial activation. New roots and
geometry refusal remain ACTIVATION_REBALANCE_REQUIRED; ordinary manifest approval
cannot override them. No rebalance workflow is introduced.

The existing exclusive lock, durable staged files, renameat2 directory exchange
and recovery journal publish the complete state directory and Production together.
Before publication, source/artifact/state/Production fingerprints are rechecked.
After swaps the release and activation state are byte-verified. Before the durable
COMMITTED journal record, recovery rolls back all swapped targets. After that
commit point cleanup is recoverable without undoing the accepted release. Readers
refuse a pending journal. No partially activated map is accepted.

```sh
python -B scripts/update-knowledge-atlas.py --recover-transaction
```

Tests inject failures and hard process exits around candidate preparation,
staging, swaps and journal completion. The reviewed 3 Category/6 fixture Topic
Centering apply runs only in a disposable repository. Fixture manifests are
rejected by the operator CLI; the internal test adapter requires an explicitly
marked temporary root and refuses the real repository. Numeric fixture IDs are
only a disposable normalized-schema adapter, never real Hyperskill claims.

## Future real operator workflow

1. Import explicit Course/Project/Progress evidence and resolve required metadata.
2. Dry-run; review relevance, metadata blockers and presentation impact.
3. Create a new preview package and select a candidate variant.
4. Serve its static view locally and visually review that exact geometry.
5. Approve its exact manifest; joint transaction applies accepted presentation.
6. Run --check and inspect git diff.
7. Commit and push manually; observe Hosted CI and verify GitHub Pages.

Future Python Course evidence reuses global IDs. Relevant unresolved IDs require
targeted explicit metadata before normalization/preview. Candidate entities must
have accepted normalized Knowledge rows/evidence before Production publication;
global leaf references are never fake Topics. No metadata collection is automated.

Project-only completion on already accepted Topics changes evidence/styles only:
no activation preview and no Generation increment. LCA taxonomy routing, amber
project requirements, search, minimap, Fit Active Atlas and focus consume the normal
accepted model and geometry. Relations do not activate dormant endpoints. No
preview dashed styling or fixture labels are added to Production.

CI performs read-only checks on real state and runs all apply/recovery fixtures in
temporary copies. It never approves real geography. Large, blocked and new-root
fixtures remain refusal cases. Multi-root geography, repeated crowded activations,
accepted-label resizing and additive growth of an existing Topic Tray still need
separate design/review; this work does not grant a general activation approval.
