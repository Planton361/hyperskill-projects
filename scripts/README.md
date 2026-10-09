# Hyperskill Importer

`import-hyperskill-project` exports eligible completed Academy projects into this
repository as standalone builds. The importer reads the source tree and its build
files. It never executes an Academy build, writes to the source, deletes source
files, stages Git changes, commits, or pushes.

## Supported projects

Java supports the legacy and current Academy final task layout
`<lesson>/task/src/<package>` and the reviewed non-executed build vocabulary.
It copies Java source into `src/main/java` and generates the standalone Gradle
application. Python supports `<lesson>/task` and `<lesson>/task/src` through the
separate, explicitly limited adapter documented below.

The title is read from the unique top-level `title` field in `course-info.yaml`.
Use `--title` only when that metadata is missing, ambiguous, or needs an explicit
override. The original title is also the default directory name. Spaces and
Unicode are retained. `/` and `\\` are replaced with the visibly distinct full
width characters `／` and `＼`; control characters are replaced with `�`. The
importer warns and records both `original_project_name` and `directory_name` in
`.hyperskill-import.json`. It refuses empty, dot, dot-dot, and overlong names.

Spring Boot, extra dependencies, custom source sets, databases and unfamiliar
layouts require a reviewed adapter. Unknown build statements stop with a reason.
There is no automatic approval of unknown frameworks or dependencies.

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

The importer reads explicit Java settings from the reviewed build files and scans
source for a few language features such as text blocks, records, and sealed
classes. This is a heuristic, not a compiler. Course metadata is reported as a
hint, not treated as authoritative. Java 23 is the default; an explicit
`--java-version N` selects another supported target. The selected value becomes Gradle's `options.release` and is
recorded in the project README and import manifest. A version below detected
syntax requirements is rejected.

## Safety and filtering

The source is never a copy destination. The importer does not run any file from
it, and rejects relevant symlinks and special files. A positive allowlist accepts
only `.java` files below the final task source directory. Build scripts are
inspected against the reviewed statement vocabulary and are never copied. Hyperskill
tests, earlier stages, task descriptions, `*-info.yaml`, `.git`, `.idea`,
`.gradle`, `build`, `target`, `out`, IDE history, caches, generated reports,
temporary files, and resources are excluded. Unexpected files inside the final
task or non-empty utility modules stop the import.

Before staging any output, it checks generated text for platform-test markers,
common secret patterns, merge markers, unsafe target paths, and trailing
whitespace. This secret scan is heuristic; inspect changes before publishing.
The manifest records the project title, actual directory name, Java version,
and SHA-256 checksums of imported/generated files.

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

They use disposable source trees and repositories to exercise filtering, dry
runs, title/path handling, update protection, version checks, and refusal cases.
They do not change real Hyperskill workspaces.

## Validated adapters and templates

`templates/java-gradle/` and the SHA-verified Gradle wrapper are the only Java
build inputs exported or executed. Java 23 is the default target. Academy Gradle
files are read, never executed/copied. `academy-statements.json` recognizes the
reviewed legacy/current scaffold vocabulary independently of whole-file hashes;
comments, whitespace and supported target versions need no infrastructure PR.
Unknown plugins, dependencies, source sets, modules or statements stop inspection.
`academy-profile.json` remains historical documentation and is no longer a gate.
Java exports currently support JDK-only console sources with no resources or
runtime file access. The standalone compiler is the final dependency check.

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

After an owner-approved merge, the existing daily 05:23 UTC MyAtlas check and
`workflow_dispatch` consume canonical main. Failed acceptance keeps the previous
public site. Revert infrastructure through a normal PR to roll back; retain all
existing exports and completion evidence.
