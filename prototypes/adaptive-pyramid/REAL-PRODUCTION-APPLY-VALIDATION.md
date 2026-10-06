# Real adaptive Production apply — 2026-10-06

**C — ADAPTIVE PRODUCTION APPLY SUCCESSFUL AND READY FOR FINAL COMMIT/PUSH**

Real `docs/knowledge-map/` now contains the exact human-approved adaptive package.
The approved target was not regenerated or altered. No staging, commit, push or
deployment occurred. The architecture remains GLOBAL REFERENCE + ADAPTIVE LOCAL PYRAMID.

## Approval and atomic apply

Repository: `/Users/antonplatonov/IdeaProjects/hyperskill-projects`.
Branch: `work/adaptive-pyramid-handoff`.
HEAD: `424e820f8fc98d94f71a24d5f29fa8579d23e864`, unchanged.

Approved manifest:
`/Users/antonplatonov/IdeaProjects/hyperskill-projects/prototypes/adaptive-pyramid/production-review/final-v1/apply-manifest.json`.

| Binding | Exact fingerprint |
|---|---|
| Approved manifest | `b1597b5ea86c481a855bcc6fe6c5a7f3380300b39262bb8faa0a9b729320a069` |
| Source Production | `0b1b1f413c13f36689119c7b7115ae4bd963ff67352edfabcc72600ae037ee00` |
| Resulting Production / reviewed target | `36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7` |

Pre-flight passed all manifest/source/target/State/Knowledge/implementation/reference
bindings, exact target inventory and file-plan checks. No pending transaction existed.
Before inventories and Git status were captured in
[preflight.json](real-production-apply/preflight.json).

This existing reviewed CLI was used against real Production, then repeated unchanged:

```sh
python3 -B scripts/update-knowledge-atlas.py \
  --apply-adaptive-production /Users/antonplatonov/IdeaProjects/hyperskill-projects/prototypes/adaptive-pyramid/production-review/final-v1/apply-manifest.json \
  --reviewed-fingerprint b1597b5ea86c481a855bcc6fe6c5a7f3380300b39262bb8faa0a9b729320a069 \
  --confirm-production-replacement
```

First result: **APPLIED**. The existing operator revalidated the bindings under its
exclusive lock, staged the reviewed bytes, revalidated immediately before publication,
used the proven macOS atomic directory exchange, and verified the published inventory.
No manual copy, deletion, reconstruction or rollback command was used. Publication
completed successfully and left no managed journal or candidate directory pending.

Actual file plan exactly equals the reviewed plan: **5 replacements, 10 additions,
9 removals, 24 paths total**, all under `docs/knowledge-map/`. There are no unexpected
Production changes. All 15 published files match the reviewed target inventory.
[Actual plan and immediate post-apply inventory](real-production-apply/post-apply.json).

## Protected facts and history

| Area | Before → after |
|---|---|
| State, all 4 files | `7b69371cb87d3dcb880803b9698b90bf09f322152ae8f1867424557a14b22137` → identical |
| Knowledge, all 11 files | `29a3d477c5aed81e53c2bf551abcb6f41fbbf3b42d71e56a0bc7c813489d35f9` → identical |
| `presentation_generation` | 0 → 0 |
| Activation `layout_generation` | 0 → 0 |
| `history_version` | 0 → 0 |
| ACTIVE_HISTORY / activation-state file SHA256 | `a89d0846f57425c48f77c3dc604d29659b966867567b81c078233b39cf53d1fb` → identical |

No State migration occurred. Learned and verified facts, Course membership,
Project/Stage requirements, evidence and relations remain unchanged. The operator's
semantic-invariance validation passed both before and after apply, against the frozen
source, approved target and canonical Knowledge. The global reference and approved
review package remain byte-identical. Local geometry remains derived in memory.

## Focused checks on real Production

The Node check executes the actual published UMD runtime bytes and model/reference
assets. The browser check opens **real Production**, not a prototype or review iframe.

| Check | Result |
|---|---|
| Default My Knowledge | PASS: 31 explicitly learned Topics + 21 hierarchy-context Categories = 52 cards; 12 verified |
| Accepted Landscape | PASS: separate 89 Topics / 135 cards |
| Global Reference | PASS: 3,955 immutable reference positions; five-root orientation |
| Course 8 | PASS: compact 89 Topics / 135 cards; global highlight preserves camera and makes no layout call |
| Project 113 | PASS: compact 26 Topics / 47 cards; complete Project highlight available |
| Stage 617 | PASS: 12 explicit Topics / 28 cards; Stage highlight preserves global camera/layout-call count |
| Search / Show in Global | PASS: `topic:36` resolves and navigates to its unchanged reference position without relayout |
| Learned / verified styling | PASS: separate learning marks; counts agree with explicit progress |
| Minimap / orientation | PASS: local minimap uses local bounds, global minimap uses reference bounds; minimap fit and five-root controls work |
| Same-depth Category rank | PASS: Y spread exactly **0 px** in every tested local scope |
| Card / sibling-subtree overlaps | PASS: **0 / 0**, including measured browser layouts |
| Canonical sibling order, Topic trays and routes | PASS: order/containment/route checks |
| Duplicate semantic entities | PASS: **0** duplicates across 3,955 entities |

One browser smoke at **1440×900**, device scale 1, native macOS Chromium
**149.0.7827.55**: **PASS**. Page errors, failed requests, HTTP errors, external
requests and storage writes: **0**. No target page overflow. Current My Knowledge,
Global and Stage screenshots were captured; the My Knowledge screenshot was visually
inspected. Review labels remain exactly as approved; no branding edits were made.

[Focused runtime/layout results](real-production-apply/focused-results.json) ·
[Measured browser results](real-production-apply/browser-results.json) ·
[My Knowledge](real-production-apply/my-knowledge.png) ·
[Global](real-production-apply/global.png) ·
[Stage 617](real-production-apply/stage617.png).

The existing read-only snapshot-growth mechanism was exercised in an isolated VM
using the published runtime. Known Topic 1 is marked learned only in cloned memory:
31 → 32 Topics, 52 → 54 cards, exactly one local layout call, global geometry unchanged.
Existing-card movement is 45 px average / 260 px maximum. A subsequent verified-only
change updates styling/counts with **zero structural layout calls** and retains the
same local layout object. No real learning data was written.

Second identical real apply: **ALREADY_APPLIED**, `applied: false`. Production,
State and Knowledge inventories remain identical to the first successful apply.
[Final/idempotency verification](real-production-apply/final-results.json).

Only the requested inventory/semantic validation, focused adaptive invariants,
read-only growth/style check, one viewport smoke and idempotency check were run.
No old migration/crash suite, full regression or multi-viewport matrix was run.

## Git diff and preservation

`git status --short`, `git diff --stat` and `git diff --name-status` were captured
after apply and validation in the final results artifact. Classification:

| Class | Changes |
|---|---|
| A — existing adaptive implementation | Pre-existing edits to `scripts/update-knowledge-atlas.py`, `scripts/knowledge_atlas/transaction.py`, and untracked `scripts/knowledge_atlas/adaptive_production.py`; all unchanged from task start |
| B — real Production | Exactly 5 tracked replacements, 9 tracked removals and 10 new untracked assets under `docs/knowledge-map/`, matching the approved plan |
| C — adaptive prototype/review evidence | Existing previews, frozen review package and reports preserved; new `real-production-apply/` validation evidence and this report |
| D — unrelated pre-existing files | Preserved; no unrelated pre-existing file changed |

All **1,205 pre-existing files outside real Production**, including existing tracked
and untracked implementation/review/preview files, retain their task-start hashes.
There are **no unintended changes** under `state/knowledge-atlas/` or `data/knowledge/`.
The Git index contains no staged changes. Git diff's stat omits untracked additions;
the exact inventory comparison includes all 24 Production paths.

Serve from the repository root if needed:

```sh
python3 -B -m http.server 8765 --bind 127.0.0.1 --directory .
```

Production URL: **http://127.0.0.1:8765/docs/knowledge-map/**.
The existing server on port 8765 was reused.

**HARD STOP: no git add, commit, push or deployment was performed.**
