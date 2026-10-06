# Adaptive dual view — current decision

**ADAPTIVE_VIEW_PRODUCTION_ADOPTED**.

Adaptive Knowledge Atlas adoption is complete on main at commit
`9db33a8960c42a86914706316d12fa81bdbf4029`. Public Production is deployed and
validated; GitHub CI passed and GitHub Pages deployment succeeded.
The Production fingerprint is
`36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`.
See [the public Atlas](https://planton361.github.io/hyperskill-projects/knowledge-map/)
and [the adoption guide](../../docs/ADAPTIVE-PRODUCTION-ADOPTION.md).

## Production contract

The architecture is **GLOBAL REFERENCE + ADAPTIVE LOCAL PYRAMID**.

- Global Reference uses canonical immutable global geometry, persisted separately
  from derived local geometry. It remains independent from personal progress.
- Global and local views share semantic identities, taxonomy and canonical sibling
  ordering. Presentation coordinates do not define entity identity.
- My Knowledge is the default: explicitly learned Topics plus necessary hierarchy
  context. Accepted Topics are not automatically learned. Accepted Landscape is
  available separately; ACTIVE_HISTORY remains the accepted semantic context.
- Compact My Knowledge, Course, Project and Stage views derive local geometry from
  their visible semantic scope. Local x/y are presentation-only; no local geometry
  checkpoint is authoritative and no authoritative local x/y persistence is needed.
- Normal progress changes can alter the visible set and adaptive local geometry.
  Verified-only styling changes do not structurally relayout. Course/Project
  highlight modes preserve the existing layout; compact modes derive local layouts.
- Derived layouts retain depth-constrained ranks, zero same-depth Category Y spread,
  no card or sibling-subtree overlaps, and canonical sibling order.

Adoption changed Production presentation/runtime only. State, Knowledge,
ACTIVE_HISTORY, `presentation_generation` and `history_version` remained unchanged.
No activation-state or layout-checkpoint migration was required for local geometry.

## Superseded path and historical evidence

Strict-global-coordinate personal Production adoption is **permanently superseded**,
unless a future explicit architecture decision replaces this one. Version-A
migration packages/tokens and old spatial-authority operators are not applicable
Production adoption instructions.

Adaptive views are now Production, not merely a preview. Historical preview,
review and apply reports preserve what was true during each phase; their earlier
pending/not-yet-applied wording does not describe current Production. The frozen
final-v1 approval is audit evidence, not authorization for future replacements.
Main is authoritative; the retained handoff branch is historical/recovery context.

## Next engineering milestone

**REAL PERSONAL-PROGRESS UPDATE FLOW VALIDATION** will verify the normal workflow:
new accepted personal progress evidence → learned/verified semantic state update
→ adaptive Production rebuild → My Knowledge expands/restyles → global reference
remains unchanged.

This decision records the next task; this documentation cleanup does not implement
or execute that workflow. Normal development starts from deployed adaptive
Production, as documented in [MAC-HANDOFF.md](../../MAC-HANDOFF.md).
