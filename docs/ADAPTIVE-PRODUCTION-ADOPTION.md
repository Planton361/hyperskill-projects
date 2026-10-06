# Adaptive Production adoption

Production now uses **GLOBAL REFERENCE + ADAPTIVE LOCAL PYRAMID**. The static
package under `docs/knowledge-map/` is the exact approved target, fingerprint
`36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`.
My Knowledge defaults to explicitly learned Topics plus hierarchy context.
Global reference bytes are persisted separately; local coordinates are derived.
State, Knowledge, ACTIVE_HISTORY and Generation/history remain unchanged.

Current read-only checks:

```sh
python3 -B scripts/check-adaptive-production.py
node prototypes/adaptive-pyramid/real-production-apply/focused.cjs
```

With a repository-root HTTP server on port 8765 and installed Playwright, run
`prototypes/adaptive-pyramid/real-production-apply/smoke.cjs` for the single
1440×900 Production smoke. `PLAYWRIGHT_MODULE` and `CHROMIUM_EXECUTABLE` can select
the installed browser runner. `PRODUCTION_BASE` can select a hosted origin, e.g.
`https://planton361.github.io/hyperskill-projects`.

The existing validation workflow was incompatible with the adopted runtime: its
legacy `--check` expected V6 release branding/checkpoint assets, and its browser
regression expected the old SVG API. The workflow now runs the exact read-only
adaptive release checker, focused layout/growth checks and one Production smoke,
then verifies Production, State and Knowledge remain unchanged. It runs on matching
pushes to both work branches and main. Pages uses GitHub's legacy dynamic
`pages-build-deployment` workflow, publishing main's `/docs` directory.

The normal `--adaptive-preview --check` remains a separate derived-preview check.
Do not use legacy `--production` or spatial-migration operations to publish adaptive
Production. The exact reviewed adaptive operator remains available for separately
reviewed future packages. The final-v1 manifest is historical approval evidence,
bound to the pre-adoption branch/HEAD; a subsequent commit deliberately makes that
old apply approval stale. It is not a reusable permission token.

## Included source and audit evidence

Required packaging, explicit manifest validation/operator, native macOS atomic
exchange, focused tests and the three milestone reports are included in the adoption
commit. The final-v1 manifest, inventories, file diff, semantic result and README
are preserved without modifying their reviewed bytes. Current real-Production
screenshots and bounded result summaries are retained as evidence.

The complete staging/exclusion classification is
`docs/adaptive-production-final-inventory.tsv`. No State or Knowledge paths are staged.
No credentials, sessions, HARs, browser caches, dependencies or IDE state are included.

Duplicated `production-preview/{current,target}/`, final-v1 `view/`, normal generated
adaptive preview, and redundant review screenshots remain local and are excluded
from the commit. Production already contains the exact target bytes. The old source
package is recoverable from the manifest's recorded pre-adoption commit. The review
HTML template and package construction source are retained. Historical reports'
links to excluded local outputs describe evidence from that review, rather than
additional hosted Production assets. Historical review/proof tools require those
local frozen outputs and the recorded source identity; current CI does not execute
them. The manifest's package fingerprint remains an audit binding even though its
duplicated view tree is intentionally excluded from Git.

Machine-local `real-production-apply/preflight.json` and `final-results.json` contain
full local working inventories/status and remain excluded. Their useful outcomes are
recorded in the milestone report and portable focused/protection summaries. No
excluded file is deleted. No superseded history is reactivated by this commit.
