# Phase 2 acceptance and Phase 3 boundary

Canonical prerequisites were rechecked: MyAtlas PR 7 merged as
`dc5870ebdd240f022292a8050a8600e6a661a67d`; archive PR 10 merged as
`1edde674744a2fe3118ec684a8bb2819da984d50`. Both repositories' main CI passed.
Local clean main checkouts were fast-forwarded; implementation and browser
acceptance use separate checkouts. MyAtlas code/contracts are unchanged.

## Unit and contract coverage

Run with Python 3.12:

```bash
MYATLAS_ROOT=/clean/myatlas python3.12 -B -m unittest \
  scripts.tests.test_import scripts.tests.test_publish scripts.tests.test_adapters \
  scripts.tests.test_acceptance_context scripts.tests.test_universal_validation
```

- `test_import`: byte preservation, exact full manifest, optional historical time,
  Java/Python Academy structures, Kotlin/JavaScript/mixed/unknown/no suffix,
  malformed non-runnable source, no metadata, ambiguous task roots plus successful
  explicit selection, text/binary resources, role errors, private/secret metadata,
  symlink parents and special files, NFC/case/path aliases, exact IDs, duplicates.
- `test_publish`: two personal confirmations, interactive-only enforcement,
  original dirty/stale checkout untouched, canonical-main isolation, no execution,
  exact Git diff/commit boundaries, original confirmation time, rejected and
  uncertain pushes, failed PR creation, existing identical branch/PR, resume
  without a new commit or second push, changed source/journal/archive rejection.
- `test_universal_validation`: every synthetic malformed candidate is committed
  in a disposable Git repository; inventory/file/hash/schema/role/identity/time
  tampering, duplicate JSON keys, duplicates across Schema 2/3/4, symlink/Gitlink
  rejection before blob reads. Schema-4 producer/reader validation is checked
  against the actual merged MyAtlas scanner, including register-only progress.
- Existing adapter utility regressions remain; they no longer gate new imports.
  Existing PR/main-push environment regressions remain. Fixture alias discovery
  may repeat some import cases; the exact test count is recorded in the PR/CI.

No test executes imported code. Publisher tests redirect **all** Git remote
operations to temporary local origins and mock GitHub calls. They simulate
personal input only for those synthetic local fixtures, never real publication.

## Complete cross-repository acceptance

The existing workflow now runs `committed`, `java`, `python`, `unknown`,
`unmapped`, and `growth`. It fetches current MyAtlas main, requires the reviewed
Schema-4 ancestor/contract and refuses incompatible bootstrap fallback. Reader
parity tests run against that exact checkout. Every scenario keeps SHA/ref
isolation and all full MyAtlas Pages, Chromium, WebKit, verification and geometry
gates. The committed scenario still tests only the three real old archives.

`unmapped` commits a temporary mixed Kotlin/JavaScript/unknown/extensionless
project and an explicit binary resource. Its ID is absent from the real catalog.
It appears once in `completion_register` with `UNMAPPED`, no Topic evidence and
no catalog-runtime row. `growth` commits three new synthetic Schema-4 projects
sequentially: two unused catalog-known IDs and one UNKNOWN ID. The generic
publisher/importer handles all three without new adapters or configuration.
Source-looking Topic/verification/Course claims never become trusted evidence.

The immutable baseline is
[MyAtlas baseline v1](https://github.com/Planton361/myatlas/blob/dc5870ebdd240f022292a8050a8600e6a661a67d/docs/contracts/hyperskill-baseline-v1.json).
Compare all 22 committed/archive working-tree hashes and five trusted-input
hashes; real IDs remain 113/229/380, learned 32, independently verified 12,
Course completion records empty and all five accepted geometry hashes unchanged.
Candidate tests may add synthetic completions only inside their disposable
evidence clones; no such archives are committed to this PR or either production
repository. Workflow artifacts document exact application/evidence commits.

The existing MyAtlas LeetCode UI acceptance has a possible transient WebKit
`Load failed` failure. Diagnose any failure; rerunning an unchanged failed job
does not weaken its assertions. No retry policy is changed in Phase 2.

## Phase 3 handoff

Consume the exact merged repository revision with the existing read-only archive
validator. Schema 4 supplies canonical ID/URL/title, optional languages,
confirmation and optional actual completion, complete SHA-256/role inventories.
Preserve old formats and the immutable baseline. Build the planned schema-1 index
from validated Git blobs, including manifest/README metadata, blob IDs, exact
revision-bound code URLs and stable `hyperskill:<ID>` deduplication identities.
Validate the complete revision before atomically publishing an immutable payload
and switching its digest-bound pointer. Prevent older jobs overwriting a newer
pointer; preserve last-known-good on source/validation failure. Archive metadata
never supplies Topic, verified or Course claims. MyAtlas retains its catalog-bound
projection and separate universal register; never sum duplicate evidence sources.

No index, pointer, dynamic loader, public UI change, merge or deployment is
implemented here. Follow
[planned index contract 1.0](https://github.com/Planton361/myatlas/blob/dc5870ebdd240f022292a8050a8600e6a661a67d/docs/contracts/hyperskill-project-index-v1.md)
in the next separately reviewed phase.
