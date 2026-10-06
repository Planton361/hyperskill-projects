# Production spatial migration preview — validation

Recommendation: **C — READY FOR EXPLICIT HUMAN REVIEW / APPROVAL IMPLEMENTATION.**

The read-only package reports `MIGRATION_PREVIEW_READY`. Every accepted entity maps exactly once, all semantic tables remain identical, displacement is measured, the comparison is usable, and future reserved-slot reveals move existing entities exactly 0 world px. This recommendation establishes readiness to review and implement a separate approval workflow; it is not approval to migrate. Nothing was committed, pushed, deployed, activated, acquired or applied.

## 1. Files added / changed

Only new files in `prototypes/global-pyramid/migration-preview/` and this report were written. No pre-existing prototype implementation, master artifact, Production, State, Knowledge or scripts were modified.

The isolated subtree contains:

- `PLAN.md` (written before implementation), `README.md`, `TRANSACTION-DESIGN.md`.
- `build.py`: read-only input loading, exact mapping, deterministic diff/metrics, manifest, freshness checker and structured refusal gates. It reuses snapshot encoding, accepted-state validation, release verification and the existing shared read lock. It contains no placement or apply API.
- `current-geometry.json`, `target-geometry.json`, `migration-diff.json`, `migration-metrics.json`, `geometry-comparison.json`, `semantic-snapshot.json`, `migration-manifest.json`.
- `view/index.html`, `view/style.css`, `view/app.js`: four comparison modes, identity-linked filters, independent camera fitting, global/bounds minimap and selected movement inspection.
- `tests/test_preview.py`, `tests/browser.cjs`, baseline/integrity/build/check/future-reveal/browser JSON evidence, test/regression logs, 36 comparison PNGs and three existing-Production QA PNGs.

[Exact new-file inventory and hashes](migration-preview/tests/files.json) lists individual paths. Existing global `labels.js` and master geometry are referenced read-only rather than copied. The original V6 native geometry is included because it is the source being compared; unrelated Production assets are not copied into the package.

## 2. Source / target identity

| Binding | Fingerprint / hash |
|---|---|
| Accepted Production geometry (ordered JSON fingerprint) | `c8467c81b88d8e01351791cee448dc3509b95153bf3eb50bcf2d2f3412a07ec7` |
| Checkpoint (ordered JSON fingerprint) | `64c219ed63c6ad34fd42a365f4df91d13d9dd37bbaa54a0197beabf351dc0bd9` |
| Activation state (ordered JSON fingerprint) | `a89d0846f57425c48f77c3dc604d29659b966867567b81c078233b39cf53d1fb` |
| Knowledge semantic source fingerprint | `392db9773079c01173bf36d68267fe7f69611027985a7285d06c877ce47e17bb` |
| Canonical master embedded geometry fingerprint | `0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194` |
| Canonical master file SHA256 | `9671e7ca5517c1f35e5ee3affac066362a2470d04ef6251cbe2faa6024572c44` |
| Preview runtime fingerprint | `ccb2189c9ea41bde95b8337ff31a341365435e911782c3eddf681335ec8dbf81` |

Manifest fingerprint: `37acf036cfa931906847feeaf7c182a38f0a82d0083d26008e20dbc8154cb041`. Production `geometry.js` byte hash: `0ec2c2374471be6e63e5144de284cacdf08a82a028648f064fe720fcb35d369b` (identical after). Payload fingerprints and wrapper-file hashes are deliberately distinguished.

The global master before/after is exactly **3,295,568 bytes**, SHA256 `9671e7ca5517c1f35e5ee3affac066362a2470d04ef6251cbe2faa6024572c44`, embedded fingerprint `0c5171f3ea6ccd706b4c901c36aaea674a44a46818136b7b941dc1c7ef9d4194`. The start/end file inventory proves byte identity. Its 5 roots, 849 Categories, 3,106 structural leaves, 3,955 positions and 3,952 structural pairs are unchanged.

## 3. Accepted inventory / target mapping

Exactly **46 Categories + 89 Topics = 135 accepted positions** map to 135 unique physical slots. Missing, duplicate, ambiguous or unknown accepted entities: **none**. All Categories map `category:<id>` → `category:<id>`; all Topics map `topic:<id>` → `leaf:<id>`. Target x/y/width/height exactly match the master, with no tolerance. The master explicitly aliases both `reference:<id>` and `topic:<id>` to the same stable leaf slot. No unresolved reference becomes a fabricated Topic.

All persisted target parents, root memberships, primary paths and secondary memberships are validated. For this inventory, accepted Categories already contain the required ancestor context; no extra semantic entity is added. The five sectors do not overlap. Parent-before-child geometry and saved-route validity are checked separately from semantic parents.

## 4. Displacement convention

V6 stores **x = horizontal center, y = top**, whereas the master stores **x = left, y = top**. Comparing those native x fields directly would compare different anchors. The preview retains the entire original V6 geometry and native x/y; its comparison rectangle uses `current_left = native_x − width / 2`. Primary deltas and Euclidean distances compare left/top against master left/top. Center deltas/distances are separately included to expose size-related anchor differences.

These are original world units with no origin alignment, scale normalization, packing or recomputation. At camera scale 1 they are world pixels; they are not screenshot pixel distances. Split panes fit cameras independently and display camera scales. The overlay preserves both original world origins in one coordinate system.

Each diff row includes identity/type, both native and normalized source coordinates, target coordinates, sizes and size deltas, left/top and center deltas/distances, current depth/branch/path, target depth/root/path/primary parent and stable slot.

## 5. Category / Topic / overall displacement

All values below preserve the generated JSON numeric representation. Percentiles use nearest rank. The complete per-entity result is in [migration-diff.json](migration-preview/migration-diff.json); additional center-anchor distributions are in [migration-metrics.json](migration-preview/migration-metrics.json).

| Metric | Categories | Topics | All accepted |
|---|---:|---:|---:|
| count | 46 | 89 | 135 |
| min | 77630.48768338378 | 78008.44675614046 | 77630.48768338378 |
| max | 231056.8557864527 | 227989.64245295356 | 231056.8557864527 |
| mean | 115425.3994236917 | 112698.20582234465 | 113627.47179021106 |
| median | 113445.52817278268 | 112704.84453190821 | 112704.84453190821 |
| p95 | 227743.30430631764 | 125956.6987530302 | 128792.22361617956 |
| p99 | 231056.8557864527 | 227989.64245295356 | 227989.64245295356 |
| total | 5309568.373489819 | 10030140.318188675 | 15339708.691678492 |
| unchanged | 0 | 0 | 0 |
| moved | 46 | 89 | 135 |

Largest Category: `category:2679` — System administration and DevOps, **231,056.8557864527** world units. Largest Topic: `topic:876` — Parameters and options, **227,989.64245295356** world units. All 135 entity sizes also change to the fixed canonical card/leaf dimensions; exact sizes and deltas are recorded per entity.

This is a **one-time spatial migration cost**, not the zero-displacement scope/reveal invariant. No claim is made that migration itself moves existing nodes 0 px.

## 6. Bounds, roots, hierarchy and Topic surfaces

| Geometry | x | y | Width | Height | Area | Aspect ratio |
|---|---:|---:|---:|---:|---:|---:|
| V6 native full bounds | -4460 | -8 | 8916 | 1867.1399999999999 | 16647420.239999998 | 4.775217712651435 |
| V6 actual accepted node extent | -4444.0 | 0 | 8892.0 | 1843.1399999999999 | 16389200.879999999 | 4.8243757934828615 |
| Canonical accepted 135-position extent | 65994 | 240 | 167748 | 44183 | 7411609884 | 3.7966638752461352 |
| Complete canonical global world | 0 | 0 | 262860 | 44551 | 11710675860 | 5.900204260285965 |

The accepted inventory is in Computer science. Target scope extent includes its accepted root and all 135 nodes; it must not be confused with the entire five-root world or a leaves-only camera fit. Target coordinates retain the global root/sector origin, accounting for substantial one-time translation as well as expansion. The accepted Topics remain spread across approximately 62.43% of full global width; no gap is compacted.

Current V6 has **45 Category branches, 119 shared connector segments, 26 Topic trays and 136 semantic hierarchy pairs**. Target scope uses **135 saved primary routes** including its presentation-anchor route; the full master contains 3,955 primary routes including five presentation-anchor routes. These counts are not interchangeable with 3,952 structural membership pairs: secondary memberships and presentation anchors differ from primary layout edges.

[geometry-comparison.json](migration-preview/geometry-comparison.json) pairs every saved V6 Category branch with its exact canonical route: **45/45 routes change**. It records all 26 original tray surfaces, all 89 Topic→slot mappings and comparison-only envelopes. The target has 26 accepted leaf parent groups; those groups are metadata, not re-created V6 trays. V6 shared rail/segment geometry is retained intact rather than silently reinterpreted as one route per Topic. Target connectors come only from persisted global routes.

One visual primary-parent change is explicit: `topic:36` (Floating-point types and operations) moves from layout Category 306 to canonical primary layout Category 35. Its semantic canonical parent remains Category 306; both structural memberships remain recorded. Current and target inspector paths expose the distinction. No Knowledge edge or semantic parent is rewritten.

## 7. Semantic invariance

Both geometry endpoints share one unchanged semantic snapshot; no migration-specific semantic rewriting exists. Every one of the eight tables (categories, topics, courses, projects, stages, edges, evidence, progress) has exactly equal before/after semantic hashes. Their underlying Knowledge source files are byte-identical. This preserves Course membership, Project membership/requirements, Stage requirements, learned/verified/applied semantics, evidence, relations and entity identities.

Before = after: **46 Categories, 89 Topics, 31 learned, 12 verified; Project 113 has 26 explicit requirements, Stage 617 has 12**. The other ten known Projects retain UNKNOWN requirements; absence of evidence is not converted to an empty requirement list or zero. Project completion does not imply learning, verification or application.

ACTIVE_HISTORY membership and activation events remain byte-identical; `presentation_generation = 0`, layout generation = 0 and `history_version = 0`. The preview adds no persisted Knowledge fact or presentation super-root membership.

## 8. Visual comparison findings

All 36 comparison screenshots below were captured and visually inspected at 1440×900, 1920×1080 and 1024×768. Current Production was also independently exercised by its existing browser regression.

- Full Current: the compact V6 hierarchy and trays remain recognizable. The comparison uses exact saved spatial data but shared preview colors/labels; it is not a pixel-for-pixel clone of Production styling.
- Full Target: five root labels identify the complete spatial reference. Accepted amber nodes sit in Computer science, with dormant master geography faint behind them. The target’s much greater breadth/depth is visible.
- Split / My Atlas: major regions can be compared directly; camera scale labels and the two-world minimap prevent falsely implying equal world sizes. At overview, individual Topics remain too small to read, intentionally; branch or entity selection resolves detail.
- Java: the branch filter yields 95 accepted positions (26 Categories, 69 Topics). Its expanded reserved geography and changed descendant arrangement are clear without altering coordinates.
- Deep Topic: Adding annotations (`topic:78`) is readable in both panes at close focus; original V6 tray versus reserved canonical sibling slots is visible.
- Project / Stage: 26 and 12 explicit required Topics are independently highlighted. Subordinate ancestors and global ghosts supply context; green learned dots and white verified rings remain independent of requirement color. Sparse separated requirement clusters remain apparent.
- Largest Category / Topic: both focused labels and exact source/target rectangles are accessible; all dimensions and movement values appear in the inspector.
- Overlay: at most five vectors are shown; selecting `topic:36` shows one labeled source→target vector in common world coordinates. This makes the one-time movement readable without hundreds of overlapping lines.
- Minimap: V6 versus full global bounds remain visible during narrow focus. Amber scope extent and white camera viewport are clipped to each mini-world. The minimap is hidden in overlay mode to avoid obscuring its endpoint.

No severe label overlap or horizontal overflow was observed in these scenes. At 1024×768 the inspector extends below the initial viewport and needs vertical scrolling; controls wrap in logical order, and the comparison itself remains usable. At 1440/1920 more inspector detail is visible immediately. Dropdown labels can truncate in the closed control; full labels remain available in the selected canvas label and inspector.

Native selects/buttons are keyboard reachable and labeled. Enter activates mode buttons; Escape clears entity focus; arrow keys pan a focused canvas. This is a review tool, not a full accessibility rewrite of the underlying Atlas.

## 9. Screenshot inventory

Each row was captured at all three requested sizes. Overview/split/My Atlas/bounds scenes intentionally share camera states where the question is the same. PNGs live under `migration-preview/tests/`.

| Scene | 1440×900 | 1920×1080 | 1024×768 |
|---|---|---|---|
| current-overview | [1440](migration-preview/tests/1440-current-overview.png) | [1920](migration-preview/tests/1920-current-overview.png) | [1024](migration-preview/tests/1024-current-overview.png) |
| target-overview | [1440](migration-preview/tests/1440-target-overview.png) | [1920](migration-preview/tests/1920-target-overview.png) | [1024](migration-preview/tests/1024-target-overview.png) |
| split-overview | [1440](migration-preview/tests/1440-split-overview.png) | [1920](migration-preview/tests/1920-split-overview.png) | [1024](migration-preview/tests/1024-split-overview.png) |
| my-atlas | [1440](migration-preview/tests/1440-my-atlas.png) | [1920](migration-preview/tests/1920-my-atlas.png) | [1024](migration-preview/tests/1024-my-atlas.png) |
| java | [1440](migration-preview/tests/1440-java.png) | [1920](migration-preview/tests/1920-java.png) | [1024](migration-preview/tests/1024-java.png) |
| deep-topic | [1440](migration-preview/tests/1440-deep-topic.png) | [1920](migration-preview/tests/1920-deep-topic.png) | [1024](migration-preview/tests/1024-deep-topic.png) |
| project-113 | [1440](migration-preview/tests/1440-project-113.png) | [1920](migration-preview/tests/1920-project-113.png) | [1024](migration-preview/tests/1024-project-113.png) |
| stage-617 | [1440](migration-preview/tests/1440-stage-617.png) | [1920](migration-preview/tests/1920-stage-617.png) | [1024](migration-preview/tests/1024-stage-617.png) |
| largest-category | [1440](migration-preview/tests/1440-largest-category.png) | [1920](migration-preview/tests/1920-largest-category.png) | [1024](migration-preview/tests/1024-largest-category.png) |
| largest-topic | [1440](migration-preview/tests/1440-largest-topic.png) | [1920](migration-preview/tests/1920-largest-topic.png) | [1024](migration-preview/tests/1024-largest-topic.png) |
| bounds-minimap | [1440](migration-preview/tests/1440-bounds-minimap.png) | [1920](migration-preview/tests/1920-bounds-minimap.png) | [1024](migration-preview/tests/1024-bounds-minimap.png) |
| selected-vector | [1440](migration-preview/tests/1440-selected-vector.png) | [1920](migration-preview/tests/1920-selected-vector.png) | [1024](migration-preview/tests/1024-selected-vector.png) |

Three additional actual-Production smoke screenshots are listed in the exact file inventory under `tests/production-screenshots/`.

## 10. Future authority simulation / interaction invariance

Disposable fixture-only simulation begins with 135 target slots and reveals one dormant Category plus one dormant leaf, then another Category plus another leaf. Each reveal reads its existing master record directly; no layout/placement search occurs. Existing-record comparisons: **135 + 137 = 272**, every complete record identical, maximum displacement exactly **0 px**. All four new records equal their pre-existing master slots; the master is unchanged. No fixture fact enters real Knowledge or State. Evidence: [future-reveal.json](migration-preview/tests/future-reveal.json).

Browser QA checks target/global exact coordinates and complete immutable current/target/master/semantic snapshots across modes, scopes, filters, selected entities, Stage selection, keyboard actions, camera fitting, resize and 30 repeated interaction cycles per viewport. **19,035 entity comparisons** (6,345 per viewport), equivalent to **76,140 x/y/width/height scalar comparisons**, with no tolerance and no mutation. These compare target with its canonical master; they do not equate current V6 coordinates with target coordinates. One-time migration still moves all 135 positions.

## 11. Deterministic artifact contract / staleness

Two complete generations from identical input are byte-identical, and both equal the saved seven artifacts. Timings are excluded from deterministic files. The manifest binds exact accepted inventory and one-to-one mapping, every artifact byte hash, source Production geometry, checkpoint, activation-state, Knowledge, global master, relevant repository input inventory and preview build/runtime files. A source read race fails closed. It refuses pending transaction journals and never executes recovery.

`build.py --check` rechecks input/runtime inventories, manifest integrity, artifact hashes and fresh deterministic bytes. Stale source/runtime evidence returns `MIGRATION_SOURCE_CHANGED`; modified artifacts return `MIGRATION_GEOMETRY_CONFLICT`. Synthetic missing/duplicate/unknown/ambiguous mapping, invalid target and semantic mismatch cases refuse. Successful outcome is `MIGRATION_PREVIEW_READY`; no approval/apply CLI is implemented.

The static browser’s READY label describes the bound package outcome, not a live repository freshness scan. Run `--check` immediately before review. Fingerprints are integrity identities, not authenticated approval tokens. Any later approval implementation must recheck them rather than trust a displayed status or old screenshot.

## 12. Performance

Preview build: **1327.858 ms**; diff/target/comparison/metric construction: **34.298 ms**; seven deterministic artifacts: **770,970 bytes**. Freshness/check regeneration: 1,336.477 ms in the recorded run. Artifact size excludes screenshots, tests and existing referenced master/labels assets. The full master is referenced unchanged (3,295,568 bytes), not duplicated.

| Viewport | Initialization ms | Overlay median / p95 ms | Selected vector median / p95 ms | Fit median / p95 ms | JS heap bytes |
|---|---:|---:|---:|---:|---:|
| 1440×900 | 54.500 | 0.500 / 0.800 | 0.400 / 0.500 | 0.000 / 0.100 | 15,166,544 |
| 1920×1080 | 50.000 | 0.500 / 0.600 | 0.400 / 0.500 | 0.000 / 0.100 | 12,390,784 |
| 1024×768 | 50.200 | 0.500 / 0.600 | 0.400 / 0.400 | 0.000 / 0.100 | 15,255,176 |

These are local offline headless Chrome 154.0.8037.57 measurements, not network/Production performance guarantees. Draw samples are synchronous renderer time, not total screenshot or display-presentation latency; sub-millisecond timer resolution explains zero Fit medians. The browser never contacts Hyperskill or other external sources. Heap is Chrome’s optional `performance.memory` estimate.

## 13. Tests / current Production validity

All stable final checks pass:

- Migration preview: **11 focused tests** — accepted inventory, one-to-one leaf mapping, exact coordinates/native source preservation, semantic/diff metrics, repeat-generation bytes, checked manifest, failed mapping/invalid target/semantic gates, stale source/runtime and altered-artifact refusal, preserved route/tray records, two-step fixture reveal and protected-byte identity.
- Existing global-pyramid suite: **11 tests**, including master determinism, five-root integrity, reference→Topic slot promotion and protected-state checks.
- Existing repository Knowledge map regression: **9 tests**.
- Current untouched Production `scripts/update-knowledge-atlas.py --check`: **PASS**, 164 runtime checks, zero category/topic displacement, unchanged checkpoint, Generation 0, `applied: false`, `state_changed: false`. Its ordinary `SAFE_TO_APPLY` no-change status is not authorization for this spatial migration.
- Existing current Production browser regression: **1,141 checks PASS** across nine widths (1920, 1440, 1280, 1200, 1024, 768, 430, 390, 320), dark/light themes and animated smoke. Current accepted scene hashes match and Project/Stage counts remain correct; no page/request errors.
- Preview browser: all three requested sizes, 36 scenes, mode/filter/keyboard/resize/repeated interaction checks, zero JS errors, zero external requests, zero local/session storage writes and no horizontal overflow.
- Deterministic artifact checker: `MIGRATION_PREVIEW_READY`.

Commands and browser environment configuration are in [README.md](migration-preview/README.md); raw results/logs are under `tests/`. Broader Production/repository regression was run once after implementation stabilized; targeted tests were repeated after adding route/tray and stale-runtime guards.

## 14. Protected Production / State / Knowledge bytes

| Protected inventory | Files | Before hash = after hash | Result |
|---|---:|---|---|
| `data/knowledge/` | 11 | `29a3d477c5aed81e53c2bf551abcb6f41fbbf3b42d71e56a0bc7c813489d35f9` | Byte-identical |
| `docs/knowledge-map/` | 14 | `0b1b1f413c13f36689119c7b7115ae4bd963ff67352edfabcc72600ae037ee00` | Byte-identical |
| `state/knowledge-atlas/` | 4 | `7b69371cb87d3dcb880803b9698b90bf09f322152ae8f1867424557a14b22137` | Byte-identical |

Hash method: SHA256 of UTF-8 sorted compact JSON path→file SHA256 inventory (`ensure_ascii=false`). Exact before/after per-file SHA256 values are in [integrity.json](migration-preview/tests/integrity.json), with start inventory in [baseline.json](migration-preview/tests/baseline.json). **29 authoritative files plus canonical geometry/catalog = 31 unchanged files**; no protected file was added, deleted or changed. Knowledge observations are included. These directory inventory hashes are distinct from semantic/payload fingerprints in the manifest.

## 15. Future transaction design recommendation

[TRANSACTION-DESIGN.md](migration-preview/TRANSACTION-DESIGN.md) analyzes the current packaging/activation/checkpoint/recovery infrastructure and future file boundary. A separately reviewed implementation should reuse the existing joint State/Production durable transaction, fsynced stages, exact inventories, pending-journal refusal and directory exchanges. The durable **COMMITTED** journal record remains the commit point after both swaps and byte/schema/semantic verification; failures before it restore both directories and counters, recovery after it cleans up.

The future runtime must package the exact reviewed master bytes and hydrate slots rather than recompute placement. Activation schema 1 and V6 checkpoint schema 2 cannot silently represent the new authority; explicit versioned schemas and a reviewed runtime adapter are required (recommended next versions 2 and 3 respectively, subject to implementation review). Production geometry/runtime assets, checkpoint, activation-state authority binding/event, update snapshot and release manifest would change. Knowledge files, semantic parents, memberships, requirements, evidence and existing activation events must not change.

The two directory exchanges are individually atomic, not simultaneous; journal-aware readers must refuse during the transition. A future migration-specific approval must bind this manifest, source baselines, runtime and exact target bytes, then revalidate before staging and after swap. Existing activation zero-movement guards must not be bypassed to disguise this deliberately nonzero one-time change.

## 16. Generation / history policy recommendation

Recommend **A: increment `presentation_generation` once in the future real migration (0→1)** because every accepted position and size, routes and bounds change. Keep checkpoint/history layout-generation counters consistent. Also record a separately versioned spatial migration event for audit; this supplements A rather than using B to leave the presentation counter unchanged.

Keep `history_version` activation-only (0 here), preserving activation events. A separate `spatial_history_version` / authority epoch should record the spatial transition. Human review must explicitly accept this policy before implementation. Once the immutable authority is installed, reveals of already captured IDs should change activation history/visibility while keeping spatial generation and master authority stable. No real counter/event was changed in this preview.

## 17. Remaining risks and final decision

The one-time migration is substantial: every accepted node changes location/size and 45 Category routes change. Users will need orientation support rather than an expectation that the initial migration is invisible. Topic 36’s primary visual-parent choice requires explicit acknowledgment even though its semantic relations stay unchanged.

Broad target scopes remain sparse; compact V6 trays become reserved global slots. Full Topic titles require branch/entity focus, especially in narrow split panes. The existing refined canonical UX demonstrates navigation, while this preview deliberately emphasizes comparison rather than reimplementing the full polished Atlas. Its current-side styling is a comparison renderer, not an actual Production runtime replacement.

No approval authentication, global Production adapter, schema migration or atomic apply implementation exists yet. Their correctness, crash recovery, rollout/rollback and later approval policy require separate review. A changed taxonomy or source/runtime makes this preview stale; new unknown IDs beyond the captured master would need a separately reviewed authority revision, not placement search during activation.

**Final recommendation: C — READY FOR EXPLICIT HUMAN REVIEW / APPROVAL IMPLEMENTATION.** All required preview gates pass. The measured one-time spatial change is fully reviewable, semantics and authoritative bytes are unchanged, target slots are valid, browser comparison is understandable, and subsequent fixture reveals retain exact 0 px movement. The migration itself remains unapplied.
