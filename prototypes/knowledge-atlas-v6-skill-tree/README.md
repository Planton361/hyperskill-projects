# V6.6 My Skill Tree prototype

Status: **MY_SKILL_TREE_FINAL_REVIEW_PENDING**.

This preserved personal view uses the existing V6.6 renderer and its independently computed geometry. Explicit accepted personal evidence supplies 31 learned Topics, 12 verified Topics and one evidence-backed Next Topic; Categories provide context. It does not infer learning from scope membership or Project/Stage completion.

Open through the persistent application shell: <http://127.0.0.1:8813/prototypes/knowledge-atlas-navigation/index.html?view=skill-tree>. Start `python3 -B -m http.server 8813 --bind 127.0.0.1` at the repository root. The original prototype URL safely redirects into that shell.

All runtime JavaScript, CSS, identity adapters, model JSON, D3 and license are repository-contained. `build.py` is an offline projection from existing accepted Knowledge; it makes no network requests. The committed model is used directly for review, without rebuilding geometry or reacquiring data. Shared Inspector chrome provides overlay/Pin; original Inspector data, progress and layout remain unchanged.

The canonical application focused smoke test in `../knowledge-atlas-scope-pyramid/tests/final-chrome.cjs` covers this renderer, exact identities, shell navigation and its frozen world fingerprint. Browser-test tooling is optional and declared in `../../scripts/knowledge_atlas/package.json`.

Preserving this source is a reproducibility checkpoint, not a final visual acceptance of the personal layout.
