# Project-completion-driven learning — technical review

Date: 2026-10-08. Status: TECHNICALLY_VALIDATED — HARD STOP.

Owner-attested completion establishes learning of every exact, explicitly associated Project requirement Topic ID. Effective learning is the union of accepted direct learning and completed-Project learning. It is not reduced to application evidence. Verification remains exclusively explicit verification evidence.

The read-only scanner `scripts/scan-project-completion.py` discovers immediate language/project exports with schema-2 import manifests and validates every listed file hash. Completion requires an exact positive Hyperskill Project ID, owner attestation, completed status and UTC observation timestamp. Arbitrary source folders and unattested exports do not count. Invalid/tampered exports produce diagnostics and a failing exit status. UNKNOWN requirements add no Topics; known-empty requirements add none. No network or Hyperskill session is used.

The sole legacy exception is `java/Simple Chat Bot with Java`, requiring its existing exact Project 113 URL and exact completion statement, plus a valid export manifest. Its observation date is this milestone's review date, 2026-10-08, represented at UTC midnight; it does not assert the historical completion date.

The reviewed local public projection is `progress.json`. Project 113 contributes 26 distinct requirement Topics, all already directly learned: 26 Topics now have both sources, zero genuinely new learned Topics, 31 effective learned and 12 verified globally. Historical personal snapshots remain unchanged. Topic Inspectors expose source and observation date, including earlier false observations alongside completion learning. A false personal observation cannot erase project learning.

Shared analytics propagate exact IDs across all Course, Project, Stage and Category scopes, the personal tree, and Global statistics. Official Hyperskill Course progress continues to use only its complete dated personal snapshot. `newLearnedTopicIds()` reports completed-Project Topics absent from the direct learned set. Repeated scans are byte-stable; they do not accumulate duplicate evidence or counters. Personal tree membership can grow for future new learned Topics; no layout algorithm, geometry checkpoint or persistent history is changed.

For future exports, the importer accepts `--project-url https://hyperskill.org/projects/ID --completed-at UTC_TIMESTAMP`. Supplying that flag is an explicit owner completion attestation. Updating an attested export requires a fresh explicit attestation. Completion is never inferred from importing alone.

`.github/workflows/project-completion-review.yml` scans published pushed repository contents (or manual dispatch), with read-only permissions, and uploads a review candidate artifact. It neither replaces the reviewed projection nor commits, pushes or deploys. Review the candidate and its semantic effect before separately accepting a future projection. The local working-tree scanner is a review tool, not proof that an export has been published. This workflow has been authored but was not run on GitHub during this milestone.

Validation completed:

- Scanner suite: 3 tests passed, covering valid/overlapping exports, no attestation, arbitrary directory, hash tampering, invalid IDs/status/date, UNKNOWN and empty requirements, repeat scan and real legacy 113.
- Importer suite: 17 tests passed, including actual completion metadata generation and required re-attestation. The first run had one macOS temporary-path alias mismatch; all tests pass with `TMPDIR=/private/tmp`.
- `node prototypes/project-completion/test.cjs`: passed learning union and a newly learned missing Topic, overlap, earlier false observation, source/date markup, unchanged verification, all 52 Courses / 391 Projects / 1,967 Stages / 849 Categories, official snapshot isolation, UNKNOWN/empty requirements, repeat aggregation, tree membership growth, immutable inputs and exact legacy tree geometry.
- Existing `progress-analytics.cjs`: 17 checks passed. Existing `universal-progress.cjs`: full inventory and historical fixtures passed.
- Existing `progress-browser.cjs`: all seven check groups passed, no page errors or external requests. Accepted browser geometry fingerprints remain unchanged for Global, Course 8, Project 113, Stage 617 and My Skill Tree; existing Inspector/navigation behavior passed.
- `git diff --check` passed. `git diff --exit-code -- data/knowledge state/knowledge-atlas docs/knowledge-map scripts/knowledge_atlas/fixtures` passed: protected Knowledge, personal snapshots, production, persistent state and geometry fixtures remain unchanged.

Changes are limited to offline scanner/import support, review-only automation, a separate prototype completion projection, semantic integration into existing prototype views, provenance text, tests and this report. Existing unrelated working-tree changes were retained. No UI redesign, production mutation, commit, push or deployment was performed. Production adoption and future projection approval are outside this milestone.
