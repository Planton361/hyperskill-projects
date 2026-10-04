# Persistent Knowledge Atlas state

These JSON files are intentional version-controlled presentation/update history.
They must be reviewed and committed together by an operator; the pipeline never
stages, commits, pushes or deploys them. `data/knowledge/` remains knowledge truth.
`docs/` is derived output. The ignored prototype build may be deleted and rebuilt
without losing spatial memory.

`layout-checkpoint.json` uses `state_schema_version: 2`,
`layout_schema_version: 2` and `layout_algorithm_version: atlas-incremental-2`.
It records relative category slot anchors, stable sibling/topic ordering,
allocated/visible region dimensions, reserve, card dimensions, wrapped slot rows
and tray row allocations. Topic rows contain only an ordering key, width and
height; x/y coordinates are derived from their tray, row order and preceding
allocations. Removed row allocations can remain as reserved slots so surviving
rows do not move. Category parenthood comes from knowledge data; sibling keys in
state are presentation/history references and are checked against that data.

The checkpoint must never contain learned/verified state, course membership,
project status/requirements, relation/evidence records, labels or per-topic x/y.
`update-snapshot.json` contains stable IDs and hashes for parents, metadata,
progress, project/stage state, membership, requirements, relations and provenance.
It includes checkpoint/derived-geometry fingerprints to verify the state pair.
It contains no source-record duplicate and is not authority for knowledge facts.

Numbers in persisted presentation state are rounded to six decimal layout units.
Relative category/tray offsets preserve the original arithmetic: all 135 frozen
baseline bounds are reproduced exactly, including their binary floating-point
results. Derived geometry is not rounded to a different visual layout.
Dictionary IDs have stable serialization; existing presentation arrays retain
their intentional order. Review actual local diffs rather than replacing state
with a freshly optimized map.

`presentation_generation` increases once when any persisted presentation
allocation/order changes. This includes a local tray append/repack even if
category anchors and widths stay unchanged. It does not increase for progress,
project state/evidence, relation or membership changes. The snapshot may change
for those knowledge changes while the checkpoint remains byte-identical.
Blocked/failed runs only report a candidate generation; persisted generation
does not change. An explicit rebalance with identical presentation also leaves
generation unchanged.

Initialization is explicit:

```bash
python -B scripts/update-knowledge-atlas.py --bootstrap-state
```

Bootstrap requires both state JSON files absent, the accepted V6 source data,
matching font metrics, valid evidence, all frozen node bounds exactly matching
and a passing browser build. Existing/partial state is refused. There is no
force-overwrite or random fallback. This initial state was bootstrapped from the
accepted baseline with generation 0.

For a reviewed structural candidate use `--approve-review`. Major movement or
reparenting needs `--rebalance`, preferably preceded by `--dry-run --rebalance`.
Schema 2 uses order-preserving checkpoint/geometry hashes; unlike source-set
hashes, presentation array ordering is never normalized away. The only supported
legacy migration is explicit `--migrate-state` from schema 1 with layout 2. It
requires matching source, legacy hashes and reconstructed geometry, and publishes
state/build together without changing geometry or generation.

Unknown **state** schemas require a dedicated migration and return
`STATE_MIGRATION_REQUIRED`; `--rebalance` cannot bypass them. A recognized state
format with a changed layout version may be rebuilt only with explicit
`--rebalance`. Review category moves, unrelated regions, row/allocation changes,
before/after bounds and generation. Never edit hash assertions just to suppress
a validation failure.

State and build are published under an advisory repository-directory lock with
fsynced candidates and a durable transaction journal. State is exchanged as a
directory so its two files change together. Linux `renameat2(RENAME_EXCHANGE)`
avoids the missing-directory window of two ordinary renames. All targets roll
back on a caught pre-commit failure. The durable COMMITTED journal record is the
commit point; post-commit cleanup never masquerades as an aborted update.

An abrupt process/host crash can leave the two directories at different versions
until recovery. Multi-directory filesystem atomicity is unavailable; supported
pipeline readers honor the lock/journal and refuse that interrupted state.
Direct external readers do not honor this protocol. Recover explicitly:

```bash
python -B scripts/update-knowledge-atlas.py --recover-transaction
```

Read-only commands do not repair or mutate interrupted state. Recovery rolls
back an uncommitted transaction, or cleans backups after a committed one. It
refuses unknown journals and externally modified targets instead of overwriting
them. Keep the journal/backups until recovery succeeds. The supported writer
platform is Linux on a local filesystem with working rename exchange, flock and
fsync; NFS/Windows/macOS parity is not asserted.
