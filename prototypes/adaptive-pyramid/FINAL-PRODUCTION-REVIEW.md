# Final adaptive Production review

**PASS — READY FOR FINAL HUMAN APPROVAL**

The validated candidate is frozen in one new, non-overwriting review package.
Real Production was not applied. No commit, push or deployment occurred.

Package: `prototypes/adaptive-pyramid/production-review/final-v1/`.
Exact manifest:
`/Users/antonplatonov/IdeaProjects/hyperskill-projects/prototypes/adaptive-pyramid/production-review/final-v1/apply-manifest.json`.

Review URL:
**http://127.0.0.1:8765/prototypes/adaptive-pyramid/production-review/final-v1/view/**

## Exact approval bindings

Branch `work/adaptive-pyramid-handoff`, HEAD
`424e820f8fc98d94f71a24d5f29fa8579d23e864`.

| Binding | SHA256 fingerprint |
|---|---|
| **NEW manifest / human approval token** | `b1597b5ea86c481a855bcc6fe6c5a7f3380300b39262bb8faa0a9b729320a069` |
| Source Production | `0b1b1f413c13f36689119c7b7115ae4bd963ff67352edfabcc72600ae037ee00` |
| Target Production | `36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7` |
| Entire review package, excluding its manifest | `5d7090e693455865ee1bd661927a0e100f9cdf43b25d06a201879f34a7c636dc` |
| State | `7b69371cb87d3dcb880803b9698b90bf09f322152ae8f1867424557a14b22137` |
| Knowledge | `29a3d477c5aed81e53c2bf551abcb6f41fbbf3b42d71e56a0bc7c813489d35f9` |
| Adaptive implementation/runtime/operator | `40ab6e28820d788f1e4e09d1e31c703dd3ad16ffd9c4f9a3c4d9964f50a6f952` |
| Global reference bytes | `bf79e7309129421b32899900a47f1c9f47d624f2fa16a4eb8b503f1be52aab25` |

Canonical identity is UTF-8, sorted compact JSON, without timestamps. Inventories
map relative paths to file SHA256. Production inventories include the
`docs/knowledge-map/` prefix. The manifest fingerprint hashes all manifest fields
except `manifest_fingerprint`; the package fingerprint hashes all package files
except `apply-manifest.json`, avoiding circular identity. It includes the frozen
current/target views, review UI, README, inventory, diff and semantic result files.

The target is **byte-identical to the validated Production preview target**.
Two fresh builds through the same builder produced identical bytes. Source
Production still matches the validated baseline and HEAD; State and Knowledge do
too. There was no pending transaction. The final package was created with an
exclusive new-directory operation and has not been regenerated or overwritten.

## Exact Production file plan

Only `docs/knowledge-map/` would be replaced. There are **24 changed paths**:
5 replacements, 10 additions and 9 removals. The exact source path → reviewed
target file → SHA256 plan is [production-diff.json](production-review/final-v1/production-diff.json).
Every target byte is in `final-v1/view/target/`; publication does not rebuild it.

| Action | Paths relative to `docs/knowledge-map/` |
|---|---|
| Replace | `app.js`, `index.html`, `model.json`, `release-manifest.json`, `style.css` |
| Add | `adaptive.cjs`, `atlas.js`, `global-reference.json`, `labels.js`, `registry.cjs`, `ux.js`, `views.cjs`, `vendor/d3-flextree-2.1.2.cjs`, `vendor/d3-flextree-LICENSE`, `vendor/d3-hierarchy-LICENSE` |
| Remove | `geometry.js`, `layout-checkpoint.json`, `layout-checkpoint.schema.json`, `layout.js`, `model.js`, `routing.js`, `taxonomy-relations.js`, `vendor/D3-LICENSE`, `vendor/d3-7.9.0.min.js` |

The generated Production checkpoint copy is retired; the authoritative legacy
State checkpoint is preserved. The candidate's read-only review notices and release
manifest remain exactly as previously validated. Removing those notices would require
a newly fingerprinted review, rather than silently changing approved bytes.

## No State migration; semantic invariance

**NO STATE / KNOWLEDGE / GENERATION CHANGE.**

- `activation-state.json`, ACTIVE_HISTORY and its accepted IDs/events: unchanged.
- State `layout-checkpoint.json` and `update-snapshot.json`: unchanged.
- `presentation_generation`, activation `layout_generation` and `history_version`:
  all remain **0**, unchanged.
- Knowledge facts, Course membership, Project/Stage requirements, Topic learned and
  verified records, evidence and prerequisite/dependent relations: invariant.
- Global reference stays separately packaged; adaptive local geometry stays derived.

[Semantic invariance](production-review/final-v1/semantic-invariance.json) compares
source Production and target read models against canonical Knowledge, verifies all
eight table hashes, independently compares records/memberships/requirements/evidence,
and verifies the accepted-history projection. Full State and Knowledge inventories
are bound and revalidated by the operator. No new durable State or acceptance receipt
is introduced merely to publish presentation bytes.

## Small explicit operator and controlled publication proof

The new `--apply-adaptive-production` dispatch uses
`scripts/knowledge_atlas/adaptive_production.py`. It requires an absolute exact
manifest, its exact reviewed fingerprint and explicit confirmation. It denies mixed
operator flags and rejects missing/wrong approval, stale Production/State/Knowledge,
modified package/target, changed implementation, changed reference or branch/HEAD,
and pending publication transactions. There is no environment-variable bypass.

The existing exclusive directory lock and `transaction.publish` are reused. The
helper stages the complete package next to Production, fsyncs staged files/directories,
and exchanges the whole managed directory atomically. The narrowly scoped portability
addition uses macOS `renamex_np(RENAME_SWAP)`; Linux retains `renameat2` exchange.
There is no two-rename fallback. The native macOS man page and SDK constant were
checked, and the actual exchange passed on this filesystem.

All bindings are revalidated after staging, immediately before publication.
Post-publication verification checks the exact target inventory and unchanged State
and Knowledge. A transient journal is kept at
`docs/.adaptive-production-transaction.json`, outside State, and is cleaned by the
existing helper. No permanent generation/history writer is invoked.

The exact CLI command was executed **only inside a TemporaryDirectory mirror**.
The mirror copies the bound implementation, source inputs and review package. Its
Git identity is read from the original gitdir; no Git mutation is performed.

| Proof | Result |
|---|---|
| Missing manifest, missing fingerprint, wrong fingerprint, missing confirmation | PASS: rejected, zero writes |
| Stale Production, State, Knowledge; modified target; changed implementation | PASS: rejected, zero writes |
| One representative failure after staging, before publication | PASS: original files intact; staging cleaned |
| Exact reviewed package, actual macOS atomic exchange | **APPLIED**, only 24 paths under `docs/knowledge-map/` changed |
| Exact target inventory after apply | PASS: matches reviewed target fingerprint |
| State, Knowledge, ACTIVE_HISTORY, Generation/history in temporary copy | PASS: byte-identical |
| Second identical exact CLI apply | **ALREADY_APPLIED**, zero file changes |

[Controlled proof results](production-review/proof-results.json).
No broad crash matrix, old migration tests or repository regression were run.

## Exact target browser check and human review

One **1440×900** smoke, native macOS Chromium **149.0.7827.55**, passes against
`final-v1/view/target/`. It verifies default My Knowledge (31 learned Topics / 52
cards / 12 verified), Accepted Landscape (89 Topics), complete Global (3,955 cards),
Course 8 compact/highlight (89 Topics), Project 113 compact/highlight (26 Topics),
Stage 617 (12 Topics), complete-registry search, Show in Global and learned/verified
styling. Highlights preserve global camera/layout-call count and global geometry.
No page errors, failed/external requests, storage writes or target page overflow.

The review page reuses the existing preview UI and exposes all five requested
views, source/target/manifest fingerprints, 24 changed files and the explicit no-State
statement. Its five view buttons were exercised in the same browser smoke.

[Browser results](production-review/browser-results.json) ·
[Review screenshot](production-review/exact-review.png) ·
[Exact My Knowledge](production-review/exact-my-knowledge.png) ·
[Exact Global](production-review/exact-global.png) ·
[Exact Course](production-review/exact-course.png) ·
[Exact Project](production-review/exact-project.png).

Prior preview UX limits remain: expanded Course overviews require focus/search,
the canvas has accessibility limitations, and the package is larger than current
Production. This freeze adds no additional layout or UX changes.

## Local review and hard stop

From `/Users/antonplatonov/IdeaProjects/hyperskill-projects`:

```sh
python3 -B -m http.server 8765 --bind 127.0.0.1 --directory .
```

The existing localhost server on port 8765 was reused during validation.
Open **http://127.0.0.1:8765/prototypes/adaptive-pyramid/production-review/final-v1/view/**.

For reference only, **after separate explicit human approval**, the exact operator is:

```sh
python3 -B scripts/update-knowledge-atlas.py \
  --apply-adaptive-production /Users/antonplatonov/IdeaProjects/hyperskill-projects/prototypes/adaptive-pyramid/production-review/final-v1/apply-manifest.json \
  --reviewed-fingerprint b1597b5ea86c481a855bcc6fe6c5a7f3380300b39262bb8faa0a9b729320a069 \
  --confirm-production-replacement
```

This command was **not** run against real Production. Final real-file verification
passes: all **29 files** in Production/State/Knowledge retain their inventories and
match HEAD, and the separately bound global reference is unchanged. Package/manifest
validation still passes after the controlled proof and browser smoke.
[Final protected validation](production-review/final-validation.json).

Only the explicit operator/dispatcher, macOS atomic-exchange helper, the existing
builder's optional root parameter and new review/evidence/report files were changed.
Real Production, State and Knowledge were not written. No commit, push or deployment.

**HARD STOP: real Production remains untouched pending human approval.**
