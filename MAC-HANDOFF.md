# Mac handoff — adaptive Knowledge Atlas adopted

## Current authoritative state

**ADAPTIVE_VIEW_PRODUCTION_ADOPTED** — the migration milestone is complete.
Main is authoritative. The retained `work/adaptive-pyramid-handoff` branch is
historical/recovery context, not the starting point for another migration.

- Deployed adaptive adoption commit on main:
  `9db33a8960c42a86914706316d12fa81bdbf4029`
  (`feat: adopt adaptive knowledge atlas views`). Documentation-only follow-ups
  may advance main; `git rev-parse origin/main` gives its current tip after fetch.
- Production inventory fingerprint:
  `36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`.
- GitHub CI: **PASS**. GitHub Pages: **SUCCESS**. Public Production is deployed
  and validated at [the Knowledge Atlas](https://planton361.github.io/hyperskill-projects/knowledge-map/).
- State, Knowledge, ACTIVE_HISTORY, `presentation_generation` and `history_version`
  were unchanged by adoption. No state migration was required.

## Adopted architecture

**GLOBAL REFERENCE + ADAPTIVE LOCAL PYRAMID** is now Production.
Global Reference retains canonical immutable global geometry. My Knowledge is the
default personal view: **31 explicitly learned Topics plus hierarchy context**
at the validated adoption baseline. Accepted Topics are not implicitly learned;
Accepted Landscape remains a separate view.

Compact My Knowledge, Course, Project and Stage views use derived local
presentation coordinates. Local x/y and camera state are not authoritative
semantic data; no local geometry checkpoint is authoritative. Progress can grow
or restyle local views while global reference geometry remains independent.
Course/Project highlights preserve the current layout; compact views derive their
own layout. Global search and Show in Global preserve global orientation.

Strict-global personal-coordinate Production adoption is **permanently
superseded**, unless a future explicit architecture decision replaces this one.
Historical strict-global packages and approval tokens are not applicable.
See [the architecture decision](scripts/knowledge_atlas/ARCHITECTURE-DECISION.md)
and [the Production adoption guide](docs/ADAPTIVE-PRODUCTION-ADOPTION.md).

## Normal Mac development

Begin from main and the deployed adaptive Production package, not a migration
preview. Inspect local changes before switching branches; preserve unrelated
local files. With a clean tracked working tree:

```sh
git fetch origin --prune
git switch main
git pull --ff-only origin main
bash scripts/dev-macos-check.sh
python3 -B scripts/check-adaptive-production.py
node prototypes/adaptive-pyramid/real-production-apply/focused.cjs
python3 -B -m http.server 8765 --bind 127.0.0.1
```

Open [local Production](http://127.0.0.1:8765/docs/knowledge-map/).
These checks are read-only; serving does not rebuild Production. The existing
single-viewport smoke is documented in the adoption guide and can use an installed
Playwright/browser setup. Do not use legacy `--production` or spatial-migration
commands to publish adaptive Production.

For an isolated development preview, the existing `--adaptive-preview` build
writes `docs/knowledge-map-adaptive-preview/`; it does not replace Production.
Such generated output is optional development material, not the adopted package.

## NORMAL POST-ADOPTION DEVELOPMENT

Future work starts from deployed adaptive Production on main. The next substantive
engineering milestone is **REAL PERSONAL-PROGRESS UPDATE FLOW VALIDATION**:

new accepted personal progress evidence → learned/verified semantic state update
→ adaptive Production rebuild → My Knowledge expands/restyles → global reference
remains unchanged.

This is a future validation task, not work performed by this documentation cleanup.
Any future Production replacement must follow an explicit reviewed package workflow;
the completed migration's frozen approval is not reusable authorization.

## Historical evidence and local exclusions

The Production preview, final human review and real apply reports under
`prototypes/adaptive-pyramid/` record their original phases and remain unchanged.
Strict-global reports under `prototypes/global-pyramid/` remain historical evidence.
They do not override the adopted architecture or authorize another migration.

Generated preview/view copies, redundant review screenshots and machine-local
`real-production-apply/preflight.json` / `final-results.json` may remain untracked.
Do not stage dependencies, browser caches, IDE state, credentials, sessions, logs,
temporary output or unrelated experiments. See the adoption guide and
`docs/adaptive-production-final-inventory.tsv` for the retained evidence/exclusions.
