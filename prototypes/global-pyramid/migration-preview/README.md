# Production spatial migration preview

Read-only comparison of frozen accepted V6 geometry and 135 exact canonical global
slots. No migration/apply/approval API exists. Only this isolated directory and the
migration validation report are generated. Real Knowledge, State and Production
must remain unchanged.

From the repository root:

```sh
python -B prototypes/global-pyramid/migration-preview/build.py
python -B prototypes/global-pyramid/migration-preview/build.py --check
python -B -m unittest discover -s prototypes/global-pyramid/migration-preview/tests -v
python -B -m http.server 8000 --bind 127.0.0.1 --directory prototypes/global-pyramid
```

Open `http://127.0.0.1:8000/migration-preview/view/`. Run `--check` immediately before
reviewing: it rejects stale authoritative inputs, master bytes, implementation and
artifacts. The static browser does not itself read all repository source files to
check freshness; its READY label is the bound package outcome. Preview fingerprints
are integrity/review identities, not authentication or authorization tokens.
The view uses the existing canonical artifact via a relative reference; keep this
package in the prototype subtree when serving it. It is not a standalone deploy.

Select Current, Target, Split or Overlay. Scope, type, top movements, branch and
accepted-entity filters share identity across panes. Wheel zooms; drag/arrows pan;
Tab/Enter operate controls; Escape clears entity selection. Split fits cameras
independently and shows scales. Overlay keeps world origins and left/top displacement;
it displays at most five vectors. Select one entity for its vector and exact diff.

V6 native x is horizontal center; the current artifact retains all native geometry
and explicitly adapts it to left/top rectangles. Target x/y/w/h equal the master
exactly. Primary metrics compare left/top; separate center metrics handle size
changes. No alignment, normalization or camera transform affects the diff.
Semantic tables are shared unchanged by both endpoints. New global ancestors and
secondary memberships are context, not invented Course/Project membership.

Artifacts are deterministic: current/target geometry, semantic snapshot, exact diff,
metrics, route/tray comparison and manifest. Build and browser timings live only
under `tests/`, outside deterministic identities. Manifest bindings include exact
input inventories, runtime implementation, accepted inventory, mapping and artifact
bytes. Missing/duplicate/ambiguous mappings and inconsistent inputs fail closed with
structured `MIGRATION_*` statuses. `--check` is validation, not approval.

Browser QA:

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
CHROMIUM_EXECUTABLE=/absolute/path/to/chrome \
node prototypes/global-pyramid/migration-preview/tests/browser.cjs
```

See [plan](PLAN.md), [future transaction analysis](TRANSACTION-DESIGN.md) and
[validation report](../MIGRATION-PREVIEW-VALIDATION.md). Nothing in these documents
applies or authorizes a real spatial migration.
