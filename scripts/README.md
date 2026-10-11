# Universal Hyperskill code archive publisher

The existing `publish-hyperskill-project` command creates Schema-4 archives under
`projects/<EXACT_ID>/`. It preserves the owner's chosen relative paths and bytes,
without language adapters, extension admission, compilation, imports, dependency
installation, or execution of Academy builds/solution code.

The authoritative operating guide is [docs/PUBLISHING.md](../docs/PUBLISHING.md).
The [Codex/Raycast snippet](../docs/publish-snippet.txt) leaves the two actual owner
confirmations manual. The manifest follows the reviewed
[MyAtlas contract 4.0](https://github.com/Planton361/myatlas/blob/dc5870ebdd240f022292a8050a8600e6a661a67d/docs/contracts/hyperskill-code-archive-v4.md).

```bash
python3.12 scripts/publish-hyperskill-project "/path/to/Academy Project" --dry-run
python3.12 scripts/publish-hyperskill-project "/path/to/Academy Project"
```

For an ambiguous structure, mixed languages, explicit text/binary resources or a
workspace without Academy metadata, use `--files-from selection.json` with exactly
`{"schema":1,"files":{"relative/program":"solution","data/image.bin":"resource"}}`.
Supply the exact `--project-url` and public `--title` when missing. Repeatable
`--language` metadata is optional. The automatic mode proposes safe UTF-8 files
in one unambiguous final task; explicit selection determines roles and preserves
full workspace-relative paths below `solution/`. It never infers resource needs
from source imports, keywords or extensions. All omitted paths are reported.

The owner types `COMPLETE <ID>` and `PUBLISH <ID>` interactively. Confirmation time
is recorded after the first input; actual historical `--completed-at` is optional
and otherwise absent. Dry-run time is never completion evidence. Publication
uses a clean isolated canonical-main checkout, an exact reviewed Git diff,
a deterministic new branch and a Draft PR. Existing IDs across Schema 2/3/4,
unsafe paths, symlinks, secrets, non-regular files and inconsistent inventories
stop. Archives 113/229/380 are never migrated or overwritten.

Interrupted publication retains its review checkout and an untracked local
journal. `--resume /exact/review/checkout` validates and reuses the same commit
and confirmation. Existing identical branches/PRs are linked instead of creating
another publication; conflicting changes require manual review. No force-push,
automatic merge or deployment is performed.

## Regression checks

```bash
python3.12 -B -m unittest scripts.tests.test_import scripts.tests.test_publish \
  scripts.tests.test_adapters scripts.tests.test_acceptance_context \
  scripts.tests.test_universal_validation
python3.12 -B scripts/validate-project-exports.py
MYATLAS_ROOT=/path/to/myatlas python3.12 -B -m unittest scripts.tests.test_universal_validation
python3.12 -B scripts/test-portfolio-growth.py --myatlas-root /clean/myatlas
python3.12 -B scripts/test-cross-repository.py --myatlas-root /clean/myatlas --scenario unmapped
```

All archive fixtures and publisher origins are temporary/local; GitHub publication
calls are mocked in tests. The frozen Java/Python adapter utility tests remain as
legacy regressions; those adapters no longer admit new publisher/importer code.
New cases cover Kotlin, JavaScript, mixed languages, unknown/no suffixes, explicit
binary resources, generic workspaces, malformed identities/inventories and safe
resume after rejected/uncertain pushes or PR-creation failures. Cross-repository
CI uses current Schema-4 MyAtlas main, refuses incompatible fallback, and tests
committed/java/python/unknown/unmapped/growth against full Pages/browser gates.

GitHub SHA/ref variables from this repository are removed only from the isolated
MyAtlas subprocess environment. MyAtlas's own production revision guard is
unchanged. Universal completion totals remain separate from catalog-bound Topic
projection. No dynamic index, runtime, catalog or production Pages integration
is introduced by the publisher phase.

Phase 3 adds a read-only, explicitly revision-bound project index:

```bash
python3.12 -B scripts/build-project-index.py --revision "<full commit SHA>" > /tmp/index.json
python3.12 -B scripts/validate-project-index.py /tmp/index.json --revision "<full commit SHA>"
python3.12 -B -m unittest scripts.tests.test_project_index
```

See [PROJECT-INDEX.md](../docs/PROJECT-INDEX.md) for the exact index/pointer
contract, durable Git retention, the gated extension of the **existing** Pages
workflow, failure recovery, manual bootstrap and Phase 4 handoff. No live
pointer or index deployment is enabled by this PR.
