# Unified V6.6 development status

UNIFIED_ATLAS_V66_TECHNICALLY_READY

TWO_TAB_NAVIGATION_ACCEPTED

SCOPE_PYRAMID_LAYOUT_ACCEPTED

FULL_TITLE_GLOBAL_HUMAN_ACCEPTANCE_PENDING

MY_SKILL_TREE_FINAL_REVIEW_PENDING

PRODUCTION_INTEGRATION_NOT_STARTED

The application has two persistent tabs: Atlas and My Skill Tree. Atlas without filters displays the complete Global Atlas; the deepest valid Course, Project or Stage filter selects an independently computed Scope Pyramid. The current accepted chrome and all world geometry are frozen.

Canonical preview: <http://127.0.0.1:8813/prototypes/knowledge-atlas-navigation/index.html?view=atlas>

From a clean checkout, run `python3 -B -m http.server 8813 --bind 127.0.0.1` at the repository root. All runtime models, scripts, styles, workers and D3 assets are versioned; the static application requires no npm installation or acquisition directory. Browser tests use the optional Playwright development dependency declared in `scripts/knowledge_atlas/package.json`.

The dormant relation observation and separate Course→Project association observation are joined through the typed Catalog. They remain excluded from active Production tables and source hashes. See [DEVELOPMENT-CHECKPOINT.md](DEVELOPMENT-CHECKPOINT.md), [RELATION-DISCOVERY.md](RELATION-DISCOVERY.md) and [FINAL-UI-CHROME-REVIEW.md](FINAL-UI-CHROME-REVIEW.md).

This checkpoint grants neither final Global visual acceptance nor final My Skill Tree visual acceptance. Production integration has not started. Historical accepted reports remain unchanged.
