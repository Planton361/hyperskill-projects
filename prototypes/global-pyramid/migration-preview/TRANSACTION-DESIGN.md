# Future spatial migration design — analysis only

No transaction, apply API, approval CLI or disposable apply adapter is implemented
by this preview. The preview builder/checker uses only the existing read-only
shared lock. It refuses pending recovery journals; it never recovers them.

## Publication and file boundary

A later, separately reviewed implementation would publish the complete
`state/knowledge-atlas/` and `docs/knowledge-map/` directories in one existing
joint transaction. The candidate must use the exact reviewed canonical bytes;
it must never regenerate placement during approval or publish.

Files expected to change in that later implementation:

- State `layout-checkpoint.json`: replace V6 allocation/tray descriptors with a
  versioned canonical-master authority contract, exact master fingerprint and
  accepted entity→slot mapping. Preserve all semantic identities.
- State `activation-state.json`: migrate the strict history schema explicitly;
  record authority binding, reviewed migration event and exact accepted geometry
  projection/mapping, preserving active Categories/Topics and activation events.
- State `update-snapshot.json`: rebind geometry/layout version and counter; retain
  semantic source fingerprints and accepted inventory. README should explain the
  authority transition and distinguish later reveal from V6 allocation.
- Production `geometry.js` / a reviewed immutable `global-geometry.json` asset,
  checkpoint and schema, runtime hydration/rendering/camera assets, index and
  release manifest. The exact final package file list must be determined by the
  future runtime adapter review, rather than this prototype renderer.
- Durable schema/runtime/pipeline helpers under `scripts/knowledge_atlas/` would
  need reviewed global-authority hydration, validation and packaging support.
  They are unchanged by this task. Prototype modules must not become ambient
  Production dependencies. Production currently has one-root V6/tray assumptions.

Files/facts that should not change: normalized `data/knowledge/`, observations,
Course/Project/Stage memberships and requirements, learned/verified/applied state,
evidence/relations, Category/Topic IDs, canonical semantic parents, ACTIVE_HISTORY
membership and existing activation events. In particular, `topic:36` remains
canonically attached to Category 306 semantically; its global layout parent is
Category 35. Both structural memberships survive. The presentation super-root
must never enter Knowledge or membership tables.

## Schema migration is required

Activation schema 1 is closed and stores exact V6 nodes/trays/segments; checkpoint
schema 2 stores V6 allocation regions, Topic orders, tray/card dimensions and slot
anchors. They cannot silently hydrate a global master. Recommend activation
schema 2 and checkpoint schema 3 (exact numbering subject to later repository
review), with explicit `spatial_authority` kind/version/fingerprint, immutable
master reference and semantic ID→slot mapping. Validate primary layout parent
separately from canonical semantic parent. Retain secondary memberships.
Old readers must refuse unknown schemas; no fallback to fresh V6 layout.

Source hashes and semantic membership indexes should remain stable. Global
reference positions are valid presentation slots, not fake accepted Topics.
Activation metadata gates still apply when evidence is required; revealing an
already captured slot must not manufacture titles, theory IDs or progress.
Taxonomy changes beyond this captured master need a new explicit authority review.

## Transaction reuse and commit point

Reuse `transaction.lock(..., write=True)` only in the future approved operation,
staging, fsync, exact directory inventories, durable recovery journal and Linux
`renameat2` directory exchange. Reuse existing preflight source/artifact/state/
Production fingerprint checks, and refusal while a pending journal exists.
The two directory exchanges are individually atomic, not a simultaneous filesystem
swap; journal-aware readers must keep refusing the in-progress release.

The commit point remains the durable **COMMITTED** journal record, written only
after both swaps and exact verification. Before it, any failure/process death
must restore both pre-migration directories from the exchanged stages in reverse
order. After it, recovery completes cleanup without undoing the accepted release.
Keep backups until commit verification completes; restore old authority and old
counters together on rollback. Schema-specific validation must run before staging
and again after swapping. Existing crash/failure fixture infrastructure can be
reused in disposable repositories; old activation validators' zero-displacement
checks must not be bypassed to allow this one-time migration.

After swap verify exact complete file inventories, byte hashes and release
manifest; checkpoint/activation schema and authority binding; canonical master
bytes/fingerprint; 135 accepted entity mappings and target coordinates/routes;
new generation/event counters; all eight semantic tables, evidence/relations,
ACTIVE_HISTORY and Knowledge directory byte inventory. Run browser checks on the
staged global runtime before publication, then verify hydration after exchange.
A migration-specific approval token must bind the reviewed manifest, target bytes,
source baselines and runtime. Approval consumes reviewed bytes, not a fresh layout.

## Generation and history policy — explicit recommendation

Recommend **A: increment `presentation_generation` exactly once** in the future
real migration (0 → 1 for this baseline). It replaces sizes, routes, bounds and
positions of every accepted entity, so leaving the established spatial counter
at zero would disguise a material presentation revision. Keep the history's
layout generation and checkpoint counter in agreement. Preview changes neither.

Also record a separately versioned **spatial migration event** binding old and new
authorities, source/target fingerprints and reviewed manifest. This event is an
audit record in addition to option A, not option B's alternative of keeping the
presentation counter unchanged. It must not pretend to be an activation.
`history_version` should stay activation-only: retain 0 here, with unchanged
activation events. A separate `spatial_history_version` / authority epoch records
this one spatial event. Human review must explicitly accept this policy before
implementation; this document does not change any real counter.

After migration, an already captured dormant ID reveal changes activation history
and visibility, not the master. Keep the spatial generation/authority epoch stable
for those zero-movement reveals; increment the activation history as appropriate.
That is an explicit new schema policy, not an accidental reuse of V6's allocator
and unconditional activation generation increment. Byte-identical replay changes
no counter. Rollback restores the entire prior counter/event state atomically.
