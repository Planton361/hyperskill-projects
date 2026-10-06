# Current Git state

- Handoff branch: `work/adaptive-pyramid-handoff` (tracks `origin` after push).
- Baseline main: `b666e28d326e25c1ac8dca03aafe149798fa2a84`.
- Date: 2026-10-06.
- Final handoff commit SHA: run `git rev-parse HEAD` after checking out this branch.
  A commit cannot embed its own SHA; the final pushed SHA is also in the handoff report.
- Main is unchanged. This branch preserves unfinished experimental work.

# Current architecture decision

**GLOBAL REFERENCE + ADAPTIVE LOCAL PYRAMID**.
Global Catalog describes the known captured Hyperskill universe; Global Pyramid
remains the complete, immutable global reference. Personal / Course / Project / Stage
views reuse semantic entities, taxonomy and canonical ordering, with separate derived
local presentation coordinates. Global and local x/y need not match.
Strict-global personal-coordinate Production adoption is paused/superseded.
See `scripts/knowledge_atlas/ARCHITECTURE-DECISION.md` for the enforceable decision.

# Current implementation status

- Global Catalog: 849 Categories, 89 Topics, 3,017 references; 3,955 structural slots.
- Global Pyramid: frozen A2 five-root composition, checked-in geometry and source input.
- Adaptive Pyramid: standalone comparison plus normal-loader dual-view integration.
- Latest layout: depth-banded rectangular contour tidy; same-depth Category ranks,
  disjoint sibling subtree envelopes, canonical Topic trays and orthogonal routes.
- My Knowledge defaults to 31 explicitly learned Topics (12 verified); Accepted
  Landscape is separate. Local geometry and independent cameras are browser memory.
- Production has **not** been migrated. Knowledge / State / Production are unchanged.
- Next task: **Production Adaptive-View Migration Preview**.

# Important directories

- `prototypes/global-pyramid/`: reference UI, build, frozen input, canonical geometry,
  tests and historical strict-global design/validation evidence.
- `prototypes/adaptive-pyramid/`: original comparison UI, licensed vendored layout,
  integration evidence and current `layout-refinement-tests/`.
- `scripts/knowledge_atlas/`: normal semantic loader/updater, adaptive preview builder,
  `adaptive_runtime/`, shared `canonical_runtime/`, `presentation/` and migration guards.
- `docs/knowledge-map-adaptive-preview/`: deterministic output, intentionally untracked;
  generate it before opening the integration preview.
- `prototypes/global-atlas/`: previously committed catalog projection/build dependency.
- `prototypes/knowledge-atlas-v6/` and `prototypes/knowledge-atlas-activation/`:
  referenced legacy source, fixtures and historical evidence.
- `data/knowledge/`, `state/knowledge-atlas/`, `docs/knowledge-map/`: protected
  authoritative inputs/state/current Production, inherited unchanged from main.
- `docs/adaptive-handoff-inventory.tsv`: every pre-handoff modified/untracked path,
  category A–F, inclusion decision and reason (including ignored local files).

# Run locally on macOS

From the repository root:

```sh
bash scripts/dev-macos-check.sh
python3 -B scripts/update-knowledge-atlas.py --adaptive-preview --json
python3 -B scripts/update-knowledge-atlas.py --adaptive-preview --check --json
python3 -B -m http.server 8765 --bind 127.0.0.1 --directory .
```

Open **http://127.0.0.1:8765/docs/knowledge-map-adaptive-preview/**.
Original comparison: http://127.0.0.1:8765/prototypes/adaptive-pyramid/.
Global reference: http://127.0.0.1:8765/prototypes/global-pyramid/.
Preview generation needs only Python's standard library and committed inputs.
Static UI assets are offline/same-origin; no runtime npm installation is needed.

# Focused validation commands

Generate the preview first, then:

```sh
node prototypes/adaptive-pyramid/layout-refinement-tests/layout.cjs
python3 -B prototypes/adaptive-pyramid/layout-refinement-tests/integrity.py
python3 -B scripts/update-knowledge-atlas.py --adaptive-preview --check --json
python3 -B prototypes/global-pyramid/build.py --check
node prototypes/global-pyramid/tests/core.cjs
```

These passed on Linux during handoff, including deterministic repeated layout/build
and unchanged inventories/hashes of all 31 protected/reference files.
The latest browser smoke also passed at 1440×900: 31 learned, 52 local cards,
12 Stage 617 Topics, 3,955 global cards, immutable reference, zero page/request errors.
Some tests write validation results/timings beside their source.
Historical `integration-tests/core.cjs` contains intentional old-layout parity checks
superseded by the latest rank invariants: do not use it as current acceptance.
Historical task-start integrity suites describe old working inventories, not this
handoff. Do not rerun the old migration/crash matrix merely to resume.

# External dependencies

Detected Linux tools: Python **3.14.7**, Node **22.22.2**, npm **10.9.7**.
Current preview uses stdlib Python; shared code uses modern Python features
(e.g. `Path.is_relative_to`, Python 3.9+). macOS itself was not tested here.
Node runs focused tests; optional pinned Playwright **1.62.1** requires Node >=20.
Chromium used for smoke: **149.0.7827.55**. The old V5 release package separately pins
Playwright 1.61.0; use the dedicated current package below.
Install Git, Python 3 and Node/npm if absent; no Java toolchain is needed for this work.

Optional browser setup (local dependency directory, no global installation):

```sh
npm ci --prefix scripts/knowledge_atlas --ignore-scripts
scripts/knowledge_atlas/node_modules/.bin/playwright install chromium
# With the HTTP server above running in another terminal:
node prototypes/adaptive-pyramid/layout-refinement-tests/smoke.cjs
# Optional current measured-layout acceptance:
PLAYWRIGHT_MODULE="$PWD/scripts/knowledge_atlas/node_modules/playwright" \
  node prototypes/adaptive-pyramid/layout-refinement-tests/browser.cjs
```

Playwright chooses its native macOS browser. `CHROMIUM_EXECUTABLE` may override it;
`PLAYWRIGHT_MODULE` may point to another installed module. Linux cache/browser paths
in historical reports are evidence only. Shared legacy Production layout uses a
font-metrics canary; macOS fonts may differ. Do not rewrite protected checkpoints or
bypass that guard. The adaptive preview does not invoke that legacy allocator.

# Local-only / intentionally excluded files

No required private input is needed for the adaptive preview: committed normalized
Knowledge, activation state and global reference are sufficient. No new acquisition
is required. Never copy raw HAR, cookies, browser profiles, sessions, credentials,
secret `.env` files or personal account IDs to GitHub.

Excluded: deterministic integration preview (regenerate above); superseded executable
strict-global review package trees (`migration-review/packages/`, `real-current/`,
`real-authorized-v2/`, `real-five-root-v3/`, `real-five-root-v3-final/`,
`real-five-root-final-v4/`); independent old V2/V3/radial/hierarchy/profile/V5
untracked experiments; ignored logs, caches, locks, IDE/build state and old outputs.
Their architectural reports/operator source remain where relevant. Old reports may
link excluded packages; those links are historical, not continuation dependencies.
All excluded Linux files remain intact. `node_modules/` is now precisely ignored.
Focused secret inspection found no credentials/session/account material in the
selected files; matching author email in a third-party license is public attribution.

# Current next task

**Production Adaptive-View Migration Preview**: prepare a new, isolated reviewable
candidate for adopting the accepted adaptive local views with the global reference.
Establish packaging, semantic invariance, protected-state boundaries, and review
criteria before any separately authorized Production migration. Begin from the
current normal-loader integration and latest layout, not an old Version-A package.

# Important warnings

- Do not revive stale strict-global migration tokens or apply old migration packages.
- Adaptive architecture supersedes that Production coordinate path.
- Knowledge / State / Production semantics remain protected; no deployment occurred.
- Preview regeneration writes only its managed derived destination; do not add
  `--production`, approval/apply, bootstrap, rebalance or migration flags.
