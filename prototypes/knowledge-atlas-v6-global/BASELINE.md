# V6.6, extended to the global Catalog

This isolated prototype derives directly from `../knowledge-atlas-v6/`.
Its visual and interaction baseline is Knowledge Atlas V6.6, including the
review images in `../knowledge-atlas-v6/tests/review/v6.6/`. Neither adopted
Production nor the later global-pyramid geometry is a design/layout source.

Copied and adapted: `index.html`, `style.css`, `app.js`, `layout.js`.
Unmodified copies: `routing.js`, `taxonomy-relations.js`, D3 and its license.
`taxonomy-relations.js` is retained for provenance but is not loaded: relation
overlays are disabled in this focused iteration. `model.js` is the new typed
Catalog adapter. `build.py` reads the repository's existing validated Catalog
and writes only this prototype's `model.json` and build timing report.

V6.6 cards, trays, palette, typography, Inspector, markers, search, minimap,
camera arithmetic, 220 ms navigation and reduced-motion behavior are retained.
Global depth spacing, upper-depth natural card scales, root-region reservations,
reference semantics and Inspector content are explicit adaptations. No old
coordinate checkpoint is imported. All leaf rows remain rendered at every zoom.

See [GLOBAL-V66-VALIDATION.md](GLOBAL-V66-VALIDATION.md) for measurements,
limitations, screenshot links and the local start command. The SHA-256 manifests
in `tests/` verify the original V6.6 and protected repository surfaces unchanged.

The accepted horizontal geometry refinement and its before/after evidence are documented in
[GLOBAL-V66-LAYOUT-REFINEMENT.md](GLOBAL-V66-LAYOUT-REFINEMENT.md).
`GLOBAL-V66-VALIDATION.md` retains the initial prototype measurement baseline.

The final vertical composition and current review are documented in
[GLOBAL-V66-VERTICAL-COMPOSITION.md](GLOBAL-V66-VERTICAL-COMPOSITION.md).
The earlier reports retain their historical measurements and recommendations.
