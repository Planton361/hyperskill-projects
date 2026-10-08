# MyAtlas V6.6 production release

Publication is pending corrected gate validation. No deployment success is claimed.

## Exact root cause and repair

The reference snapshot was generated at `4215ac2fefea0ff6084210bac8d2dc0f42c32b34`, then committed in `fb76acb9c1fcca6f43c01d7fffa6eb6a3a1fdf1c`. A later pre-push test reused that artifact after HEAD advanced. The generator's revision was accurate at build time; the artifact was stale. Requiring a tracked projection to contain its own commit SHA would be circular.

The tracked snapshot remains bound to its authentic source revision and SHA-256 in the reviewed manifest. Deployable output is generated after the final source commit into ignored `build/pages/`. The builder rejects uncommitted implementation/runtime inputs and a checkout/GITHUB_SHA mismatch. The gate requires the artifact's revision to equal current HEAD, verifies its evidence/implementation digest, reconstructs its progress from committed evidence, and validates all frozen assets and historical data. Revision checking is retained; no metadata is manually falsified.

Pending validation adjustments read current generated progress in release browser checks, while the legacy baseline test uses the reference snapshot's historical evidence revision. This lets legitimate future owner completions update the artifact without inventing baseline achievements or changing analytics.

Baseline: 849 Categories, 3,106 Topics, zero unresolved Topics, 52 Courses, 391 Projects, 1,967 Stages, 867 Course→Project associations; 31 learned, 12 verified, one completed Project113; Course8 31/89 Topics and 1/11 associated Projects; no established Course completions. All five accepted geometry fingerprints and UI semantics remain frozen.

Public URL: https://planton361.github.io/hyperskill-projects/knowledge-map/

The annotated rollback tag `knowledge-atlas-pre-v6.6` is published at the exact previously deployed `a8b79e2e6c32df990fc3305983bb5aff1d9e2500`. Its Production fingerprint is `36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`. [Rollback](MYATLAS-ROLLBACK.md), [development/provenance contract](MYATLAS-DEVELOPMENT.md), and [reviewed release manifest](releases/myatlas-v6.6.json).

Remote CI, live deployment, automatic sync, and post-live cleanup will be recorded only after they are independently verified. Original Production and all excluded local files remain untouched.
