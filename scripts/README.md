# Hyperskill Importer

`import-hyperskill-project` exports eligible completed Academy projects into this
repository as standalone builds. It inventories the Academy workspace but treats
its build files as untrusted input: it never parses, executes, copies, or uses them
to configure an export. It never writes to the source, deletes source files, stages
Git changes, commits, or pushes.

## Supported projects

Java supports exactly one Academy final task source root,
`<lesson>/task/src`. It copies eligible Java files from that root into
`src/main/java` and generates the standalone Gradle application. Python supports
`<lesson>/task` and `<lesson>/task/src` through the separate, explicitly limited
adapter documented below.

The title is read from the unique top-level `title` field in `course-info.yaml`.
Use `--title` only when that metadata is missing, ambiguous, or needs an explicit
override. The original title is also the default directory name. Spaces and
Unicode are retained. `/` and `\\` are replaced with the visibly distinct full
width characters `／` and `＼`; control characters are replaced with `�`. The
importer warns and records both `original_project_name` and `directory_name` in
`.hyperskill-import.json`. It refuses empty, dot, dot-dot, and overlong names.

Java exports support standalone JDK-only console code. External imports, runtime
file/resource access, additional modules or source sets, frameworks, and ambiguous
entry points stop with a reason. The independent export build is the final check
that selected Java sources compile without Academy dependencies.

## Requirements

- Linux or macOS with Python 3.12 or newer and Git
- A JDK at least as new as the selected Java target
- Gradle 9.6.1 Wrapper template (the wrapper pins and verifies its distribution)

The wrapper can download Gradle when needed. It does not install a JDK. Each
exported Java project has its own wrapper and can be opened or built alone.

## Usage

Run from the repository root. Quote source paths that contain spaces:

```bash
./scripts/import-hyperskill-project --dry-run --java-version 23 \
  --project-url https://hyperskill.org/projects/113 \
  "/home/me/IdeaProjects/Simple Chat Bot with Java" java

./scripts/import-hyperskill-project --java-version 23 \
  --project-url https://hyperskill.org/projects/113 \
  "/home/me/IdeaProjects/Simple Chat Bot with Java" java
```

The positional arguments are `<source> <language>`; no slug or project-name
argument is required. The title is auto-detected, and `--title` overrides it.
Other options are `--concepts`, `--main-class`, `--dry-run`, and `--update`.
Run `./scripts/import-hyperskill-project --help` for the current syntax.

`--dry-run` lists all inspected source entries with `COPY` or `IGNORE`, validates
the generated files, checks for a target collision, and runs `git diff --check`
and `git status`. It does not write files or run a build. An actual import creates
the destination only after validation, then displays Git status. It never commits
or pushes.

## Java version

The importer scans selected source for a few language features such as text
blocks, records, and sealed classes. This is a heuristic, not a compiler. Course
metadata may be reported as a hint but never controls the target. Java 23 is the
default; an explicit `--java-version N` selects another supported target. The
selected value becomes Gradle's `options.release` and is recorded in the project
README and import manifest. A version below detected syntax requirements is
rejected.

## Safety and filtering

The source is never a copy destination, and the importer does not run any file
from it. It rejects unsafe paths and symlinks throughout the inventory, as well
as relevant special files. It accepts only `.java` files below the unique final
task source directory. Academy build files and wrappers are ignored without
parsing or copying. Hyperskill tests, earlier stages, task descriptions,
`*-info.yaml`, `.git`, `.idea`, `.gradle`, `build`,
`target`, `out`, IDE history, caches, generated reports, temporary files, and
resources are excluded. Unexpected source sets, modules, resources, or files
inside the final task stop the import.

Generated text is checked for platform-test markers, common secret patterns,
merge markers, unsafe target paths, and trailing whitespace. Selected Java source
is preserved byte-for-byte, including trailing whitespace; the independent
standalone compiler validates it. This secret scan is heuristic; inspect changes
before publishing. The manifest records the project title, actual directory
name, Java version, and SHA-256 checksums of imported/generated files.

## Updates

A destination collision is rejected unless `--update` is explicit. Updates require
the importer manifest, reject extra or missing files, and refuse to overwrite
files changed since the prior import. They never delete destination files. The
project README is user-maintained and is preserved across updates. Build outputs
such as ignored `build/` or `.gradle/` directories in an existing target cause the
conservative update check to stop; move them aside before updating.

## Completion evidence

`--project-url` records the exact Hyperskill Project ID. To explicitly attest a completed export, supply `--completed-at` with the actual UTC completion/observation time, in `YYYY-MM-DDTHH:MM:SSZ` form. This is an owner attestation; it does not fabricate platform verification or imply Course completion. The independent `export_metadata.py` validator keeps this importer usable without MyAtlas.

MyAtlas now lives in [its own repository](https://github.com/Planton361/myatlas) and reads committed public exports from this repository. After an approved project merge, its daily Pages check refreshes the visualization; workflow_dispatch remains available.

## Tests

Run the infrastructure tests from the repository root:

```bash
python3 -B -m unittest discover -s scripts/tests -v
```

They use disposable source trees and repositories to exercise filtering, unknown
and reformatted Academy Gradle files, real standalone builds, title/path handling,
update protection, version checks, and refusal cases. They do not change real
Hyperskill workspaces. The export validator rebuilds the committed Project 113
and 380 evidence without rewriting either export.

## Validated adapters and templates

`templates/java-gradle/` and the SHA-verified Gradle wrapper are the only Java
build inputs exported or executed. Java 23 is the default target. Academy Gradle
files and wrappers are untrusted inventory entries; their syntax, plugins,
repositories, dependencies, and formatting never affect export configuration.
Project 229 exposed the previous false rejection: both `build.gradle:27` and
`settings.gradle:3` declare the Academy test Maven repository with a
double-quoted URL, while the old line allowlist contained only the single-quoted
form. Those files are not needed by the selected JDK-only `Main.java`. The
standalone compiler remains the final dependency and Java validity check.

The Project 229 dry-run now succeeds and identifies `java/Zookeeper with Java`
as its target. The selected `Main.java` is preserved byte-for-byte, including a
12-space whitespace-only line at line 74 inside the goose text block. The
read-only real workspace was then imported only in a disposable evidence clone;
its standalone Java 23 build and the full MyAtlas Pages acceptance passed with
Project 229 recorded as completed. The source inventory matched before and
after, and no export was published.

The Python 3.12+ adapter accepts a single final task, a unique `main.py`/`app.py` or
main guard, local modules and the explicit standard-library list in
`source_adapters.py`. UTF-8 `.txt`, `.json` and `.csv` resources must be referenced
by literal read-only `open` calls and remain inside `src/`. Dynamic execution,
introspection, external imports, links, unknown resources and dependency/build
metadata stop. A comment-only requirements file is harmless; nothing is installed.
Validation compiles Python sources without executing the student's program.
Run exported Python from `src/` so approved relative resource paths resolve.

## One-command owner publication

Run the existing helper with the original Academy directory (or a file within it):

```bash
python3.12 scripts/publish-hyperskill-project "/path/to/Academy Project" \
  --completed-at "YYYY-MM-DDTHH:MM:SSZ"
```

Use the **actual** UTC completion time. It is never invented. An interactive run
asks for it when omitted. Language/title come from `course-info.yaml`; project ID
comes from the typed `hyperskill_project` record in `course-remote-info.yaml`.
Missing ID/title prompts are targeted; conflicting explicit metadata stops. Flags
`--language`, `--title`, `--project-url`, `--main-class`, `--java-version` resolve
supported ambiguities. Course language version never overrides the Java 23 default.

The sequence is language detection → validated source extraction → language
adapter → standalone export → owner completion evidence → Git publication.

1. Inspect original sources and known local IDs without modifying them.
2. Clone to a retained temporary checkout and fetch canonical `origin/main`.
   This also works for stale/dirty/detached or locally read-only checkouts; it never
   changes their files, index, branches or Git administration. Canonical evidence
   and duplicates are checked again after fetching.
3. The **owner** types `COMPLETE <PROJECT_ID>`. Neither Codex nor another agent may
   enter that confirmation on the owner's behalf. `--attest-completed` is only a
   legacy compatibility flag and never substitutes for this confirmation.
4. Export/build, verify source immutability and show the exact temporary-index diff.
5. The **owner** types `PUBLISH <PROJECT_ID>`. Commit only the reviewed new export,
   push one new branch normally, and open a draft PR through the existing `gh`
   authentication. No auto-merge. PR creation failure reports the comparison URL
   and retained checkout; do not repeat publication. No new credentials are needed.

`--dry-run` performs read-only inspection. `--prepare-only` stops after export,
build and review. Unsupported projects, duplicates, build failures and rejected
pushes stop with concrete reasons. The isolated checkout is retained for review;
no resets, clean, force pushes or automatic retries are used. `--publish push`
retains the existing explicit fast-forward publication mode; the default is a PR.

## Full cross-repository acceptance

Every project PR runs `project-atlas-acceptance.yml` with read-only permissions.
It validates committed IDs, attestations, file hashes, standalone templates and
real builds before MyAtlas imports any candidate. Separate disposable Java/Python
Academy fixtures then exercise a further completion with the real catalog. Every
scenario builds **all Pages routes**, reverses the reviewed release supplements
through the existing guards, checks deduplication/independent verification, and
runs Chromium/WebKit desktop/mobile UI and geometry tests. No Pages upload or
deployment occurs in this workflow. Reports/screenshots are CI artifacts.

The current MyAtlas main is used once it contains the acceptance entrypoint.
During initial review only, `templates/myatlas-acceptance.json` pins the exact
companion PR commit; **merge the MyAtlas companion first**, then this PR. This
bootstrap never selects an arbitrary branch or downloads executable code by title.
The chosen actual commits are reported on every run. GitHub branch protection is
not configured by this change; reviewers must require the checks before merging.

Local equivalent (clean committed MyAtlas checkout required):

```bash
python3.12 -B scripts/test-cross-repository.py --myatlas-root ../myatlas --scenario committed
python3.12 -B scripts/test-cross-repository.py --myatlas-root ../myatlas --scenario java
python3.12 -B scripts/test-cross-repository.py --myatlas-root ../myatlas --scenario python
python3.12 -B -m unittest scripts.tests.test_import scripts.tests.test_publish scripts.tests.test_adapters
```

To test a specific catalog project with its real read-only Academy workspace,
pass `--project-id ID --academy-source /absolute/path --completed-at ACTUAL_UTC`
to a `java` or `python` scenario. The harness creates and commits evidence only
inside a disposable repository clone, checks the source inventory before and
after, builds the export, and runs the complete local MyAtlas Pages acceptance
without deployment. Unknown MyAtlas project requirements are recorded as unknown
and receive no inferred learned topics.

After an owner-approved merge, the existing daily 05:23 UTC MyAtlas check and
`workflow_dispatch` consume canonical main. Failed acceptance keeps the previous
public site. Revert infrastructure through a normal PR to roll back; retain all
existing exports and completion evidence.
