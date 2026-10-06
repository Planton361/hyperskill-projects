> **Historical strict-global workflow — superseded for Production.**
> All packages and tokens described below are non-applicable. Follow
> [the current architecture decision](../../../scripts/knowledge_atlas/ARCHITECTURE-DECISION.md)
> and the root MAC-HANDOFF.md. Production has not been migrated.

# Exact spatial migration review and approval contract

Current A2 review candidate: **[real-five-root-final-v4/](real-five-root-final-v4/)**.
See [FINAL-MIGRATION-REVIEW.md](../FINAL-MIGRATION-REVIEW.md) for the exact
fingerprint, validation, metrics and serve instructions. Status: **AWAITING HUMAN REVIEW**.

All older packages/tokens, including `real-five-root-v3-final`, `real-authorized-v2` and the intermediate
`real-five-root-v3`, are **STALE**. Do not approve/apply them. The corrected five-root
geometry is visually approved; this fresh migration candidate still needs human review.

Exact reviewed bytes use one shared transaction writer for marked disposable roots
and explicitly confirmed real apply. Real migration remains default-deny.
No real migration has been applied. The instructions below describe the operator
contract; package generation never implies approval or apply.

From the repository root, generate a **new** package using a fresh read-only preview
from `migration-preview/build.py`'s `artifacts(root)` helper. Do not refresh historical
preview/review folders or reuse an existing output:

```sh
python -B prototypes/global-pyramid/migration-review/review.py package \
  --output prototypes/global-pyramid/migration-review/packages/NEW_PACKAGE_NAME \
  --preview /ABSOLUTE/PATH/TO/FRESH_PREVIEW
python -B -m http.server 8000 --bind 127.0.0.1 \
  --directory prototypes/global-pyramid/migration-review/packages/NEW_PACKAGE_NAME
```

Open `http://127.0.0.1:8000/view/`. The self-contained page verifies the manifest's
canonical preimage and all bound artifact bytes before rendering. It shows Current,
Target, Split and Overlay, branch/type/Project/Stage/entity filters, exact coordinates,
one-time movement metrics, target fingerprint, proposed Generation 0→1 and a copyable
manifest fingerprint. It does not scan live repository sources; approval does that.
Use localhost (a secure context for browser SHA256) rather than opening a file URL.

Only after a human reviews the exact **fresh real** package and copies its fingerprint,
a separate explicitly authorized migration session may invoke:

```sh
python -B scripts/update-knowledge-atlas.py \
  --apply-spatial-migration /ABSOLUTE/PATH/TO/migration-manifest.json \
  --reviewed-fingerprint COPIED_EXACT_MANIFEST_FINGERPRINT \
  --confirm-real-spatial-migration
```

This is an apply command, not a preview command. Do not run it during package generation.
It requires the intended `main` checkout, a non-fixture manifest, no pending transaction,
exact current source/runtime bindings and a final locked preflight. It validates and
seals the reviewed bytes in memory before the established transaction. It never
regenerates coordinates. Missing confirmation/token, stale inputs or an unrelated root
fail closed. Plain real-root `approve` and `apply-test` refuse publication.

Disposable `approve` writes an isolated seal only; package tokens still bind all exact
candidate bytes. `apply-test`, `recover-test` and `validate-test` continue to require
external marked roots. The disposable marker does not authorize a real checkout.

Disposable API/CLI examples, exclusively for temporary test copies:

```sh
python -B prototypes/global-pyramid/migration-review/review.py apply-test \
  --root /tmp/MARKED_DISPOSABLE_ROOT --manifest /tmp/FIXTURE_PACKAGE/migration-manifest.json \
  --seal /tmp/FIXTURE_APPROVAL.json
python -B prototypes/global-pyramid/migration-review/review.py recover-test \
  --root /tmp/MARKED_DISPOSABLE_ROOT
python -B prototypes/global-pyramid/migration-review/review.py validate-test \
  --root /tmp/MARKED_DISPOSABLE_ROOT --manifest /tmp/FIXTURE_PACKAGE/migration-manifest.json \
  --reviewed-fingerprint FIXTURE_REVIEW_TOKEN
```

Approval/apply only read the packaged target and candidate files. They never call
the package adapter, preview constructor or layout generator. The exact reviewed
manifest is copied as a detached State receipt, not regenerated. Candidate intent
identity avoids self-hash recursion; the human token binds the complete manifest
and its exact candidate file hashes.

The explicit disposable schemas are authority 1, checkpoint/state 3, activation 2,
spatial-history 1. Unknown fields/versions fail closed. Generation changes once to
1, activation history stays 0, ACTIVE_HISTORY stays 46 Categories/89 Topics, and a
separate spatial event records the authority change. Replay checks exact installed
bytes and unchanged nonspatial inputs before `ALREADY_APPLIED`. Pure fixture reveal
and promotion use reserved slots; they are not a new real activation writer.

The migrated test runtime reuses the refined canonical UI, packaged self-contained.
The original preview `master_reference` is retained byte-for-byte as review metadata;
published runtime reads the explicit authority `master_asset` instead. The normal updater supports both legacy and canonical authority. Real canonical
writes require a strictly validated installed non-fixture migration receipt; file
presence alone is insufficient. See [durable integration](../DURABLE-AUTHORITY-VALIDATION.md).

Tests (all writers target disposable copies):

```sh
python -B -m unittest discover -s prototypes/global-pyramid/migration-review/tests -v
PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
CHROMIUM_EXECUTABLE=/absolute/path/to/chrome \
python -B prototypes/global-pyramid/migration-review/tests/browser_runner.py
```

Future operator workflow: new package → local exact review → copy token → separately
authorized explicit confirmed apply → locked exact validation → atomic publication →
post-migration validation. Implementation changes require a new package and token. Commit, push and deployment require separate decisions.

[Validation and recommendation](../MIGRATION-APPROVAL-VALIDATION.md).
