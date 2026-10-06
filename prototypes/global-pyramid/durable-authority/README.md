# Durable canonical authority integration

The existing updater now dispatches on **installed State**, not prototype files.
Without `state/knowledge-atlas/spatial-authority.json`, the legacy V6 path remains
unchanged. With the complete reviewed schema-1 authority, the normal state reader,
builder and activation workflow use the installed master bytes and reserved slots.
Unknown/partial schemas, inconsistent checkpoints or noncanonical coordinates fail
closed. No canonical operation invokes an allocator or a pyramid generator.

The real repository remains legacy. Canonical writes in this development phase
require an external root with `.atlas-disposable-test` containing exactly
`spatial-migration-tests-v1\n` and no Git checkout in its ancestry. Creating a marker
inside the real checkout cannot enable canonical publication. The existing spatial
migration `apply-test` gate remains unchanged.

## Normal workflow in a marked disposable migrated root

Run that root's existing `scripts/update-knowledge-atlas.py`:

```sh
python -B scripts/update-knowledge-atlas.py --check
python -B scripts/update-knowledge-atlas.py --dry-run
python -B scripts/update-knowledge-atlas.py --production
python -B scripts/update-knowledge-atlas.py --activation-preview /tmp/exact-reveal --project 113
```

Serve `/tmp/exact-reveal` locally and review `review.html`. The iframe is the exact
proposed Production package; coordinates/routes, relevance and counters are linked.
Copy its manifest fingerprint, then use the existing approval command:

```sh
python -B scripts/update-knowledge-atlas.py --approve-activation /tmp/exact-reveal/activation-manifest.json --reviewed-fingerprint COPIED_HASH
```

Approval consumes exact reviewed candidate/Production bytes. It independently
checks inputs, metadata, counters and canonical slots, then publishes through the
existing journal/lock/recovery transaction. A repeated identical approval returns
`NO_CHANGE`. `--recover-transaction` handles interrupted publication and orphaned
staging in disposable roots.

Metadata enrichment/progress/evidence do not invalidate structural authority.
Missing normalized Topic metadata returns `METADATA_REQUIRED`. Unknown structural
IDs or changed parents/memberships return `SPATIAL_AUTHORITY_EXTENSION_REQUIRED`;
there is no fallback to V6 placement. Invalid installed bindings return
`SPATIAL_AUTHORITY_MIGRATION_REQUIRED`.

The one-time migration increments spatial Generation 0 to 1 and records a separate
spatial event. Canonical reveals increment activation history only; Generation
stays 1 because the master already contains the geometry. This follows the existing
preview's explicit counter recommendation.

A pre-migration V6 build cache is validated as a managed cache but never used for
canonical hydration. A stale cache is reported; `--build` refreshes it. Installed
State and Production remain authoritative and strictly validated.

## Verification

```sh
python -B -m unittest discover -s prototypes/global-pyramid/durable-authority/tests -p 'test_durable.py' -v
```

Tests copy the current repository into temporary external roots, generate fresh
implementation-bound migration reviews, migrate there, and exercise the **normal
CLI**. They also capture browser scenes at 1440×900, 1920×1080 and 1024×768.
`tests/baseline.json` records real protected bytes; no fixture evidence is written
to real Knowledge. Detailed results are in [../DURABLE-AUTHORITY-VALIDATION.md](../DURABLE-AUTHORITY-VALIDATION.md).

Previously generated review packages bind the earlier implementation and are now
stale. A later real migration session needs a fresh preview/review package and a
new external human token, plus a separately reviewed decision to enable the real
publication gate. No such gate was enabled here.
