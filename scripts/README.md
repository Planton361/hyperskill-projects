# Hyperskill source-only publisher

The existing `publish-hyperskill-project` command archives completed Academy
solutions as source. It does not create a release or claim that the code builds
or runs. The Academy workspace is read-only throughout inspection and export.

## One-command workflow

Use the current official repository checkout and quote a workspace path with
spaces:

```bash
python3.12 scripts/publish-hyperskill-project "/path/to/Academy Project"
```

The command reads the title and Java/Python language from `course-info.yaml`,
and the exact Hyperskill ID from `course-remote-info.yaml`. If identity metadata
is missing, it asks only for the precise missing title or project URL; explicit
conflicts stop. It asks for the actual UTC completion time in an interactive
terminal when one was not supplied. That time is owner-provided and is never
inferred from file dates or the current clock.

It first performs and displays a read-only archive review. For a real run, the
owner personally types `COMPLETE <ID>` before import and `PUBLISH <ID>` after
reviewing the exact staged diff. The publisher uses a clean, isolated checkout
of canonical `origin/main`, verifies no duplicate Project ID exists, commits
only the new archive to one new branch, and opens a draft PR. It never merges,
force-pushes, changes the original Academy workspace, or publishes directly to
`main`. If the branch push succeeds but PR creation fails, use the reported
comparison link rather than publishing again.

The flags `--project-url`, `--language`, and `--title` are only for missing or
ambiguous metadata. `--completed-at` is convenient when the owner already has
the actual UTC timestamp. `--dry-run` ends after the read-only review. There is
no Java version, build, wrapper, dependency, or execution option in the new
source-only flow.

## What is archived

For Java, the publisher requires one unambiguous final `<lesson>/task/src`
folder and selects its own `.java` files. For Python, it requires one final
`<lesson>/task` and selects its `.py` files from `task/src` when present, or
from `task` otherwise. Relative names, package folders, and bytes are kept
unchanged below the export's `src/` directory. No unique `main()` is required.
Files in the opposite language and other non-source files are ignored.

The adapter may add a local UTF-8 `.txt`, `.json`, or `.csv` file only when its
relative path is directly identified by a supported string literal in the
selected solution source (literal read-mode `open()` in Python, or the selected
read-only file/resource APIs in Java). It does not copy binary files, infer
dynamic resource paths, or include an unreferenced text file. Sources and
resources are hashed in the manifest.

Each new archive contains only:

- the selected solution sources and safely identified text resources;
- a short generated `README.md` with the title, language, and exact project URL;
- `.hyperskill-import.json` schema 3 with `mode: source-only`, exact project ID,
  language, owner completion attestation, UTC timestamp, and SHA-256 hashes.

Schema-2 standalone exports such as Projects 113 and 380 remain valid and
unchanged. Duplicate ID checks recognize both schemas. New project imports do
not rewrite old exports or add build files to them.

## Trust boundary and exclusions

Academy Gradle, Maven, wrapper, requirements, IDE, and other build configuration
is untrusted input. The importer never parses, copies, evaluates, or executes it.
It does not compile Java, run Python, install dependencies, look for a `main`,
verify libraries, or analyze frameworks, modules, or source sets. A harmless or
unknown Academy build instruction cannot block an otherwise identifiable source
archive. Malformed or non-runnable solution code can still be archived.

The Project 229 failure exposed the obsolete boundary: its Academy
`build.gradle:27` and `settings.gradle:3` use double-quoted `maven { url ... }`
declarations for the Hyperskill test repository, while the previous
`academy-statements.json` line allowlist recognized only a narrower spelling.
Neither file was part of the selected final solution, so build syntax is now
outside the archive trust decision instead of receiving another project-specific
allowlist entry.

The inventory excludes earlier stages, Academy tests, task statements,
`.git`, `.idea`, `.vscode`, `.gradle`, `.m2`, virtual environments,
`node_modules`, build outputs, IDE history, caches, and generated or temporary
files. It rejects symlinks, special files, unsafe cross-platform
paths, ambiguous final-task layouts, private-looking names in selected files,
and content matching the repository's common secret patterns. Secret scanning
is a safety heuristic, so the owner still reviews the exact file list and diff.
The adapter supports Java and Python source archives; other languages and files
that cannot be safely identified remain unsupported until their own adapter is
reviewed.

## MyAtlas compatibility

MyAtlas accepts legacy schema 2 and source-only schema 3. A valid owner
completion attestation counts as project completion without requiring an
independent build. Topic IDs come only from the trusted MyAtlas catalog. An
unknown project can be recorded as completed, but it contributes no invented
learned topics. MyAtlas continues to synchronize from `hyperskill-projects/main`
on its daily Pages check or its existing manual Pages action; this publisher
does not deploy MyAtlas or change its production data.

The MyAtlas compatibility change is reviewed first. The publisher's
cross-repository CI pins that exact compatibility commit until it appears on
MyAtlas `main`, then follows `main`. Merge MyAtlas compatibility before the
publisher change only after each PR's review and green checks.

## Tests and project evidence

Run local publisher tests with Python 3.12:

```bash
python3.12 -B -m unittest scripts.tests.test_import scripts.tests.test_publish scripts.tests.test_adapters
python3.12 scripts/validate-project-exports.py
```

The tests use disposable trees and local Git repositories. They cover unknown,
reformatted, and unsafe Academy builds without executing them; external
imports, invalid Java/Python, and non-runnable sources remain archivable; and
private names, possible secrets, symlinks, unsafe paths, and unsafe resources
stop. They also verify source bytes, owner confirmations, duplicate prevention,
legacy compatibility, and Python source/resource handling. The legacy export
validator checks Projects 113 and 380 without changing their directories.

The cross-repository test creates project evidence only in a disposable clone
and runs the MyAtlas Pages acceptance locally without deployment:

```bash
python3.12 -B scripts/test-cross-repository.py \
  --myatlas-root /path/to/myatlas \
  --scenario java \
  --project-id 229 \
  --academy-source "/Users/antonplatonov/IdeaProjects/Zookeeper with Java" \
  --completed-at "2026-10-10T11:45:17Z"
```

The Project 229 dry-run found one final source file, `Main.java`, under
`Zookeeper with Java/task/src`; it reported the Java archive target
`java/Zookeeper with Java`, ID 229, and the owner-supplied timestamp. Its SHA-256
is `bcbbe093891db5551df408c0f0065bd17f48f139481676139757ff05d5719d66`. The
actual Academy workspace remains unchanged, and no Project 229 export is
published by this test.

After a project PR is reviewed, marked ready, and its MyAtlas acceptance check is
green, merge it through GitHub. MyAtlas then observes the canonical `main` on
its next scheduled sync. This workflow never auto-merges a PR.
