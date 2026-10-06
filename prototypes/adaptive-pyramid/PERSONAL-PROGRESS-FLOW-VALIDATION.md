# Personal-progress flow validation

**C — REAL PERSONAL-PROGRESS UPDATE FLOW VALIDATED**

Starting main: `5823127884286d68cf4d1a49c540d42b55965f7d`.
Architecture: **ADAPTIVE_VIEW_PRODUCTION_ADOPTED — GLOBAL REFERENCE + ADAPTIVE LOCAL PYRAMID**.
All scenarios used synthetic, explicitly disposable evidence. No real Hyperskill
observation was acquired or accepted. No real Knowledge, State or Production was
written; nothing was committed, pushed or deployed.

## Actual current data path

The existing source is `data/knowledge/observations/learned-2026-10-01.json`:
a sanitized Course-8 snapshot with a timestamp, explicit Topic booleans, literal
verification statuses, complete Topic coverage, learned IDs/count and skipped count.
`evidence.json` links normalized progress rows to that snapshot through an evidence
ID, `snapshot_file`, timestamp, method and explicit confidence. Historical evidence
is retained; it is not merged into new Topic assertions.

`snapshot.load_source` reads normalized tables and dispatches observations through
`observations.load`. Personal observations previously had no importer/sanitizer;
the loader alone does not normalize a new snapshot. The adopted builder validates
`active_projection(loaded)` using `validate.validate`, including snapshot/row
agreement, evidence references, aggregates, course membership and taxonomy.
`catalog_projection.project` consumes the normalized Topic progress and accepted
history; `adaptive_preview.artifacts` binds it to the frozen global geometry.
`production-preview/build.py: candidate(root)` packages the exact adopted runtime.
Local selection/layout then derives My Knowledge from learned Topics and ancestors.

The small new `personal_progress.normalize` performs allowlist validation and pure
normalization of a complete explicit snapshot. It derives `is_verified` only from
the literal `verification_status == "verified"`, recomputes redundant indexes,
preserves Project/Applied facts and old evidence, and runs the existing validator.
It rejects incomplete coverage, unknown fields, nonboolean states, inconsistent
counts, stale timestamps, duplicate evidence and application inference. This is
not the historical V6 operator or a second model/layout pipeline.

## Future file changes and authority decision

For a genuine accepted refresh of existing Course-8 Topic statuses:

| Path | Role | Required change |
|---|---|---|
| `data/knowledge/observations/<new-evidence-id>.json` | Semantic input | Add actual sanitized snapshot; retain old observations |
| `data/knowledge/progress.json` | Semantic input | Update explicit rows, provenance/time and redundant Course indexes |
| `data/knowledge/evidence.json` | Semantic provenance | Add evidence referencing the new snapshot; retain old evidence |
| `docs/knowledge-map/model.json` | Derived Production | Rebuild after separate review/authorization |
| `docs/knowledge-map/release-manifest.json` | Derived Production | Update model asset hash after separate review/authorization |
| `state/knowledge-atlas/` | Existing presentation/accepted-history authority | No writes for these progress-only updates |
| ACTIVE_HISTORY | Accepted Landscape membership | Unchanged |
| `presentation_generation`, `layout_generation`, `history_version` | Authority counters | Unchanged: **0 → 0** |
| Canonical/global reference geometry and assets | Global presentation authority | Unchanged |

Those are the exact changed candidate Production paths in all three scenarios:
`model.json` and `release-manifest.json`. Runtime/CSS/vendor assets are identical.
Course membership, Topic/Category metadata, taxonomy, Project/Stage requirements,
relations and application evidence must not change for these status-only refreshes.
The global observation file remains unchanged. No local geometry checkpoint is
introduced or updated.

State is **still a genuine read dependency**, not entirely obsolete: the builder
reads `activation-state.json` for `active_categories` and `active_topics`, which
supply Accepted Landscape. Learned selection comes from progress, independently.
A disposable dependency probe removed every other State file temporarily and
produced byte-identical candidate output, then restored the files. Thus neither
`layout-checkpoint.json` nor `update-snapshot.json` is a progress-build dependency.
No dependency was removed from real code. ACTIVE_HISTORY and all counters remained
byte-identical in every final disposable root and in the real repository.

## Disposable fixtures and semantic results

The preview allocates a fresh resolved macOS temporary directory and copies current
accepted Knowledge, State, canonical reference and required packaging inputs.
Initial candidate bytes match deployed Production exactly. It writes normalized
updates and candidate output only inside that new root. There is no output-path,
apply or real-write flag. Invalid observations are rejected before allocating it.

Fixture envelopes use the current observation schema, with provenance
`source: validation-only`, `method: synthetic_disposable_fixture` and a clear
SYNTHETIC/DISPOSABLE warning. Normalized observations also carry `validation_only`.
These fixtures must never enter real accepted Knowledge.

| Scenario | Explicit transition | Learned | Verified | My Knowledge cards |
|---|---|---|---|---|
| A | Topic **1**, `Method "main"`: `is_learned false → true` | 31 → **32** | 12 → **12** | 52 → **54** |
| B | Topic **9**, `String`: `verification_status evaluation → verified` | 31 → **31** | 12 → **13** | 52 → **52** |
| Sequential | A, then verify already-visible Topic 9 | 32 → **32** | 12 → **13** | 54 → **54** |

IDs were selected from existing Course-8 progress, not invented. A preserves
`is_completed`, skipped, verification and Applied values. B derives only the
corresponding `is_verified false → true`; no learned inference occurs. No unrelated
Topic changes semantic state. A adds Topic 1 plus one necessary hierarchy card.
All prior evidence records, Course membership, Project state/requirements, Stage
requirements, taxonomy and relations remain unchanged. Provenance/timestamps refresh
for the complete snapshot's rows; this is distinct from a Topic state transition.

## Candidate, layout and global contract

Scenario A candidate fingerprint:
`1d5eb5d500837715e1f8c675fc87a32eb7dcbcca0fc2de3f0faf69b8df82d017`.
Scenario B:
`c90c4bc864820e5ff8d1577031f0d1ba201b3bccccbda2dd574ae15f82e4aeb0`.
Sequential:
`d4b10cc37f8675e0d0036e4354c01dae5de939a9532990d466c9e18e26bb7394`.
Each candidate rebuild is deterministic and runs the same semantic validator,
Catalog projection and packaging function as adopted Production.

Using the focused deterministic text measure, A's local bounds grow from
**4160 × 1170** to **4420 × 1170**. Of 52 existing cards, **11 move**; median
movement across existing cards is **0 px**, maximum **260 px**. Adaptive layout
measured **0.475 ms** on this Mac; timings are observations, not acceptance limits.
B and the sequential second step preserve visible IDs, positions, bounds and the
structural signature exactly: **0 moved cards**, **0 px displacement**, and
`Views.updateSnapshot` performs **no structural relayout** when fed the rebuilt
semantic model. No runtime object was edited to simulate progress.

All candidates pass: exact learned-plus-ancestor visibility, no duplicate semantic
entities, same-depth Category Y spread **0**, no card overlaps, no sibling-subtree
overlaps and canonical sibling order. All retain **3,955** global entities/slots.
Global geometry, entity inventory, coordinates, root composition and canonical
ordering are equal. Canonical and packaged global-reference bytes have SHA-256:
`bf79e7309129421b32899900a47f1c9f47d624f2fa16a4eb8b503f1be52aab25`.
Global displacement is **0 px** in all scenarios.

## Browser and focused checks

One successful isolated smoke at **1440×900**, Chromium **149.0.7827.55**:
default My Knowledge loads with **32 learned / 12 verified / 54 cards**; Topic 1
is visible with hierarchy context; browser-measured layout passes the invariants.
Global Reference opens with 3,955 slots; Show in Global selects Topic 1 at its
unchanged canonical coordinates and centers it inside the viewport. No page,
request, HTTP or console errors. [Screenshot](personal-progress-flow/learned-candidate.png).
B uses focused runtime validation only; no viewport matrix or historical suites.

Executed focused checks:

```sh
python3 -B prototypes/adaptive-pyramid/personal-progress-flow/validate.py
node prototypes/adaptive-pyramid/personal-progress-flow/layout.cjs
# Serve the learned scenario's disposable_root from pipeline-results.json:
python3 -B -m http.server 8777 --bind 127.0.0.1 --directory /ABSOLUTE/DISPOSABLE_ROOT
PLAYWRIGHT_MODULE=/PATH/TO/playwright CHROMIUM_EXECUTABLE=/PATH/TO/chromium \
  node prototypes/adaptive-pyramid/personal-progress-flow/smoke.cjs
```

The schema proof includes eight targeted rejection cases. The browser runner was
installed only under `/private/tmp`; an already installed Chromium was reused.
The initial Mac temp-path symlink refusal was corrected by resolving the newly
allocated disposable root. No existing publication helpers were weakened.

## Protected real bytes

Before and after inventories are exactly equal, including every file under each
protected directory. Canonical inventory fingerprints:

| Protected path | Before = after |
|---|---|
| `data/knowledge/` | `29a3d477c5aed81e53c2bf551abcb6f41fbbf3b42d71e56a0bc7c813489d35f9` |
| `state/knowledge-atlas/` | `7b69371cb87d3dcb880803b9698b90bf09f322152ae8f1867424557a14b22137` |
| `docs/knowledge-map/` | `36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7` |
| `prototypes/global-pyramid/generated/` | `fd9c00270c914bf4430b8bfe908daa68d11d0a74807ca2a236c0493087770f69` |

ACTIVE_HISTORY's activation file remains
`a89d0846f57425c48f77c3dc604d29659b966867567b81c078233b39cf53d1fb`.
See [before](personal-progress-flow/protected-before.json),
[after](personal-progress-flow/protected-after.json),
[pipeline results](personal-progress-flow/pipeline-results.json),
[layout results](personal-progress-flow/layout-results.json),
[State dependency](personal-progress-flow/state-dependency-results.json),
[global equality](personal-progress-flow/global-reference-results.json) and
[browser results](personal-progress-flow/browser-results.json).

## Future real operator sequence and tooling

1. Obtain **actual** sanitized explicit progress evidence supplied from the user's
   Hyperskill progress source. This tool does not authenticate or acquire evidence.
2. Supply the full Course snapshot plus explicit provenance envelope to the new
   preview-only command:

   ```sh
   python3 -B scripts/preview-adaptive-progress.py \
     --observation /ABSOLUTE/PATH/TO/ACTUAL-SANITIZED-ENVELOPE.json --json
   ```

3. Review semantic before/after and the added observation/evidence in the reported
   disposable root. Reject any unrelated status, membership or application change.
4. Review the deterministically rebuilt adaptive Production candidate fingerprint,
   confirm global-reference bytes are unchanged, and run focused layout checks and
   one appropriate candidate smoke.
5. Review exact semantic-input and derived-output file diffs. Separately authorize
   acceptance of actual evidence and a newly reviewed Production replacement.
   The historical adoption manifest cannot authorize changed Knowledge or targets.
6. Only then perform the separately authorized real update, commit and deployment.
   Do not invoke legacy V6 State writers or old strict-global migration operators.

New tooling is limited to the pure normalizer, preview-only CLI, focused scenario
proofs and this report. It supports complete snapshots of already-known Course
Topics; partial batches, new memberships/metadata and acquisition remain outside
this validated scope. No real-ingestion or publication bypass was added.
Never infer learned from Project completion, verified from learned, applied from
requirements, or Topic metadata from taxonomy. Synthetic validation fixtures are
not acceptable real evidence.
