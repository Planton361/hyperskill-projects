# Global Topic metadata ingestion — reviewed offline observation

Result: **849 Categories, 3,106 structural leaf slots, 3,018 RESOLVED_TOPIC, 88 PARTIAL_TOPIC, 0 UNRESOLVED_REFERENCE.** Every leaf has explicit Topic identity/title. No ordinary leaf displays an ID placeholder. Personal facts remain **31 learned / 12 verified**.

## Preflight and scope

`git fetch origin --prune` completed. HEAD and origin/main both equalled `ca5dbe97d37f3c6fe034d6338da88285d9fdb640`. No rebase was performed. Preexisting untracked adaptive-preview and Skill Tree artifacts were left untouched. This milestone ran offline: no Hyperskill requests, authenticated browser, HAR processing, or acquisition profile access. Only Knowledge observation ingestion and the isolated Global prototype were changed. No commit, push, or deployment.

## Exact digest distinction

The supplied whole-file SHA-256 was verified against the original candidate bytes:

`e435b577a848cc542ef2a9a2e334708958680b961a93cc3fd8ebcef6564a2d2a`

The filename digest and `content_digest` field were independently verified:

`aaf5cc3a0a363c0f629e5aae1ee3e2c5504d1aa8a5074c1b18e42e7e3a5b0b56`

This second digest is **SHA-256 of `snapshot.encode(candidate with only content_digest omitted)`**. It covers the complete remaining candidate envelope, including bookkeeping, provenance, fingerprints and the sanitized observation. It is not merely a target-set hash or a hash of Topic records. Existing `snapshot.encode` serializes UTF-8 JSON, sorted object keys, two-space indentation, preserved array order, and a trailing newline. The whole-file hash includes the `content_digest` field; the two intentionally different byte sequences explain the different digests. Neither value was guessed.

The target-set and source/catalog fingerprints were also recomputed. Removing only this new observation from normal source loading reproduces exactly the candidate's accepted-source fingerprint and its 3,017 unresolved target IDs.

## Existing immutable observation model

The candidate is a bookkeeping envelope. Its `sanitized_observation` member already satisfies the existing `global_knowledge_catalog` observation schema, without field transformations. It was validated using `catalog_observation.validate_observation` and persisted using existing `snapshot.encode` conventions as:

[global-topic-metadata-2026-10-07-89d5c1a731e5.json](../../data/knowledge/observations/global-topic-metadata-2026-10-07-89d5c1a731e5.json)

Persisted observation SHA-256: `89d5c1a731e534e180309c7648baa49be2bec7418a3ec092abdc5af48012cc9d`.

The exact embedded evidence interval is `2026-10-04T14:01:54.769Z` through `2026-10-07T16:16:35.405Z`. The start includes the reused structural taxonomy evidence; the end is the actual candidate's final metadata capture timestamp. No capture date was manufactured. The immutable filename uses the recorded end date and observation digest prefix. All 11 preexisting Knowledge files, including the previous global observation, remain byte-identical. No old evidence was edited and no parallel Topic database was introduced.

The existing observation loader and Catalog normalization compose this evidence into the existing numeric identities. The existing reference-promotion semantics are preserved: reference history remains, Topic identity resolves the same structural numeric leaf, and no second physical slot is allocated. Existing accepted Topic records retain priority when appropriate; all previous 89 Topic records compare exactly equal after composition.

## Validation and semantic preservation

| Contract | Result |
|---|---:|
| Acquired targets accounted for | 3,017 / 3,017 |
| Acquisition exceptions / conflicts | 0 / 0 |
| Categories | 849, unchanged |
| Structural leaf slots | 3,106, unchanged |
| Resolved / partial / unresolved | 3,018 / 88 / 0 |
| Structural memberships | Exact equality |
| Canonical hierarchy and structural positions | Exact equality |
| Reference history | Exact equality |
| Previous Topic records | All 89 preserved |
| Duplicate semantic Topic / physical row | 0 / 0 |
| Learned / verified | 31 / 12, exact original IDs |
| Course 8 membership | 89 Topic IDs, unchanged |
| Project 113 requirements | 26 Topic identities, unchanged |
| Stage 617 requirements | 12 direct / 26 cumulative, unchanged |
| Active Knowledge tables and personal observations | Exact equality |
| Normal Global projection | Matches normal Catalog loading |

The 88 partial Topics retain their original explicit identity/title evidence; missing fields were not fabricated. Metadata enrichment adds no learned, verified, course-membership, project-requirement, availability, or completion claim. Structural evidence is kept distinct from newly acquired Topic fields.

## Security and protected surfaces

Security scan **PASS** for the complete candidate and strict nested observation: forbidden Cookie/Authorization/CSRF/token/account/request-header fields; bearer/JWT-like values; email addresses; private filesystem paths; account/session identifiers; and URLs with query/fragment data. Only approved semantic metadata and safe provenance are retained. The original candidate stays outside Git. No raw HAR, request headers, session secrets, or authenticated response dumps were added.

Before/after SHA-256 checks passed for **1,199 protected files** plus all **11 original Knowledge files**. Protected directory inventories also match exactly: `state/knowledge-atlas/`, `docs/knowledge-map/`, `prototypes/knowledge-atlas-v6/`, and `prototypes/knowledge-atlas-v6-skill-tree/`. Production remains untouched. `GLOBAL-V66-ACCEPTED.md` is byte-identical and continues to document the historical accepted commit.

Reproducible evidence: [offline audit](tests/full-title/audit.py), [ingestion results](tests/full-title/ingestion-audit.json), and [validation instructions](tests/full-title/README.md). The separate full-title geometry review is documented in [GLOBAL-V66-FULL-TITLE-REMEASURE.md](GLOBAL-V66-FULL-TITLE-REMEASURE.md).
