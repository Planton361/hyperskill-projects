# Hyperskill Importer

`import-hyperskill-project` exports eligible completed Academy projects into this
repository as standalone builds. The importer reads the source tree and its build
files. It never executes an Academy build, writes to the source, deletes source
files, stages Git changes, commits, or pushes.

## Supported projects

Version 1 accepts only simple Java console projects in the legacy Academy layout
`<lesson>/task/src/<package>`, with one of the exact reviewed build profiles in
`templates/academy-profile.json`. It copies Java source from the final `task/src`
into `src/main/java`, then creates a small Gradle application build without
Hyperskill plugins or `hs-test` dependencies.

The title is read from the unique top-level `title` field in `course-info.yaml`.
Use `--title` only when that metadata is missing, ambiguous, or needs an explicit
override. The original title is also the default directory name. Spaces and
Unicode are retained. `/` and `\\` are replaced with the visibly distinct full
width characters `／` and `＼`; control characters are replaced with `�`. The
importer warns and records both `original_project_name` and `directory_name` in
`.hyperskill-import.json`. It refuses empty, dot, dot-dot, and overlong names.

Spring Boot, extra dependencies or plugins, resources, databases, multi-module
builds, custom source sets, tests, and unfamiliar source layouts are not
automatically simplified. Unknown Academy build files fail the exact SHA-256
profile check. The importer prints the detected source, examined build files,
files it would ignore, and a reason for refusal. There is no bypass option;
review and add a new known profile or a purpose-built adapter first. Kotlin,
Python, and complex Java projects are not supported by this version.

## Requirements

- Linux or macOS with Python 3.10 or newer and Git
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
hint, not treated as authoritative. If no single version is clear, provide
`--java-version N`; the selected value becomes Gradle's `options.release` and is
recorded in the project README and import manifest. A version below detected
syntax requirements is rejected.

## Safety and filtering

The source is never a copy destination. The importer does not run any file from
it, and rejects relevant symlinks and special files. A positive allowlist accepts
only `.java` files below the final task source directory. Build scripts are
compared byte-for-byte with the reviewed profile and are never copied. Hyperskill
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

MyAtlas now lives in [its own repository](https://github.com/Planton361/myatlas) and reads committed public exports from this repository. After publishing a new completed export, run its MyAtlas Pages workflow to refresh the visualization.

## Tests

Run the infrastructure tests from the repository root:

```bash
python3 -B -m unittest discover -s scripts/tests -v
```

They use disposable source trees and repositories to exercise filtering, dry
runs, title/path handling, update protection, version checks, and refusal cases.
They do not change real Hyperskill workspaces.

## Templates and profile maintenance

`templates/java-gradle/` contains the standalone Gradle templates.
`templates/wrapper/` contains the independent Gradle 9.6.1 wrapper and its
generation settings; `wrapper-sha256.json` verifies all copied wrapper files.
`templates/academy-profile.json` preserves the original reviewed Academy scaffold
and records additional reviewed scaffolds by exact build-file SHA-256. The importer
requires one complete, unambiguous profile match; it never executes or exports
Academy build files.

When Hyperskill changes its build files, review all plugins, dependency
declarations, source sets, modules, and build logic manually. Add a new profile
only after confirming it remains safe to replace with the standalone template.
Update relevant behavior tests and verify a fresh export before accepting it.

## One-command owner publication

Keep every Academy project in its original independent IntelliJ workspace. Publish
only its reviewed final Java export under this existing repository's
`java/<Project Title>/`. No separate project repository is needed.

From **main**, after the helper changes have themselves been reviewed and released,
replace every placeholder with your actual project information:

```bash
./scripts/publish-hyperskill-project "/absolute/path/to/Original Academy Project" \
  --project-url "https://hyperskill.org/projects/ACTUAL_ID" \
  --java-version 23 --attest-completed \
  --completed-at "YYYY-MM-DDTHH:MM:SSZ"
```

Use the actual Java target; omit `--java-version` only when the existing importer
can unambiguously determine it. Use your actual completion time in UTC, not today's
time unless that is when you completed the project. The helper never generates a
completion timestamp. The JDK must support that target and Gradle (JDK 25 is used
in the disposable build test).

The helper runs the **unchanged importer dry-run**, showing COPY/IGNORE and every
RESULT path. It rejects unsupported profiles/layouts, conflicting explicit Project IDs,
duplicate exports and invalid existing evidence. It asks you to type
`COMPLETE <ID>` before import. It reads the Academy workspace only and executes
only the independent export's verified Gradle wrapper. A failed build stops before
staging or publication, leaving the new candidate available for manual review.

After a successful build it shows the exact Git diff using a temporary index,
then asks for `PUBLISH <ID>`. Default publication commits only the reviewed export
on a new `publish/hyperskill-<ID>-…` branch, performs one normal non-force push,
and prints the PR comparison URL. You open/approve/merge that PR into **main**;
MyAtlas's canonical reader follows only main. `--publish push` instead makes one
normal main push; rejected rules or concurrent changes stop it and retain the
local commit. Neither path stages or commits unrelated existing work. Start on
main at the same revision as remote main; the helper refuses divergent histories.
It preserves preexisting staged, unstaged and untracked changes.

Add `--dry-run` for inspection only, or `--prepare-only` for import/build/diff
without touching the real index, committing or pushing. There is no validation
bypass or automatic update flag; collisions and unsupported layouts require manual
adapter/update review. The schema-2 `.hyperskill-import.json` remains unchanged.
Neither the helper nor Java source assigns Topic IDs: MyAtlas uses the exact
committed Project-to-explicit-Topic-ID catalog mapping.

After a merged export, MyAtlas's daily 05:23 UTC check refreshes progress through
the existing validated Pages build. A MyAtlas main push or manual workflow run also
reads the latest committed export revision. See MyAtlas's `scripts/README.md` for
skip/failure behavior. Scheduling requires the workflow update to reach MyAtlas's
default branch; these local changes alone activate nothing.

### Focused helper tests and rollback

```bash
python3 -B -m unittest scripts.tests.test_import scripts.tests.test_publish
```

Tests use disposable IDE sources/Git repositories. Publication is mocked, while
one fixture executes the real pinned standalone Gradle build. The dedicated
`owner-publish-check.yml` workflow has read-only GitHub permissions and no publish
step.

To roll back this helper release, revert its reviewed infrastructure commit through
a normal PR; keep the existing importer and all `java/` exports intact. If an owner
cancels before publication, the new export may remain untracked: inspect only that
new directory manually, and never delete or change the original Academy workspace.
If a push is rejected, inspect the retained local commit; do not force push or use
an automatic reset. This implementation has not imported or published a real project.
