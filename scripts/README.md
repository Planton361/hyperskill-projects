# Hyperskill Importer

`import-hyperskill-project` exports eligible completed Academy projects into this
repository as standalone builds. The importer reads the source tree and its build
files. It never executes an Academy build, writes to the source, deletes source
files, stages Git changes, commits, or pushes.

## Supported projects

Version 1 accepts only simple Java console projects in the legacy Academy layout
`<lesson>/task/src/<package>`, with the reviewed build profile recorded in
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

- Linux with Python 3.10 or newer and Git
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
`templates/academy-profile.json` pins the one manually reviewed Academy scaffold.

When Hyperskill changes its build files, review all plugins, dependency
declarations, source sets, modules, and build logic manually. Add a new profile
only after confirming it remains safe to replace with the standalone template.
Update relevant behavior tests and verify a fresh export before accepting it.
