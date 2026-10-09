# Hyperskill Projects

My completed Hyperskill projects, exported as standalone applications. This repository is where I keep the code I write while learning, with an independent build and run instructions for each project.

## Projects

| Project | What I practised | Language / runtime |
| --- | --- | --- |
| [Simple Chat Bot with Java](java/Simple%20Chat%20Bot%20with%20Java/) · [Hyperskill Project 113](https://hyperskill.org/projects/113) | Console input/output, methods, arithmetic, loops and a small quiz | Java · JDK 23 |

[Browse the Java projects](java/README.md). There is currently one completed project export in this repository; new projects are added as I finish them.

## Run a project

Each project has its own Gradle Wrapper. For the current Java project:

```sh
cd "java/Simple Chat Bot with Java"
./gradlew run
```

Use `./gradlew build` to compile it. The first run may download the pinned Gradle distribution. See the project's README for its required JDK. The projects run independently of Hyperskill's IDE plugins and of MyAtlas.

## Repository layout

```text
java/                    Standalone Java project exports
  <project>/             README, Gradle Wrapper and src/main/java
scripts/                 Conservative export importer and its tests
  templates/             Reviewed standalone build templates
site/                    Small redirects for the earlier MyAtlas URLs
.github/workflows/       Project/importer checks and redirect-only Pages build
```

## Add a completed project

The importer supports the reviewed simple Java console-project scaffold. It copies the final Java source into a standalone application, preserves the original workspace and filters out platform tests, task descriptions, IDE files and caches.

Start with a dry run:

```sh
./scripts/import-hyperskill-project --dry-run --java-version 23 \
  --project-url https://hyperskill.org/projects/113 \
  "/path/to/Simple Chat Bot with Java" java
```

Use the actual project URL and required Java version for a new export. Review the output before running the same command without `--dry-run`. The importer does not commit or push. [Supported layouts, limitations and update instructions](scripts/README.md).

## Learning visualizations

[MyAtlas](https://github.com/Planton361/myatlas) is maintained in its own repository. It presents my Hyperskill learning and confirmed LeetCode progress; the application source, catalogs, evidence tooling and release checks live there.

- [Hyperskill Atlas](https://planton361.github.io/myatlas/knowledge-map/?view=atlas)
- [My Skill Tree](https://planton361.github.io/myatlas/knowledge-map/?view=skill-tree)
- [LeetCode CPU Atlas](https://planton361.github.io/myatlas/leetcode-atlas/)
- [LeetCode progress summary](https://planton361.github.io/myatlas/leetcode-progress/)

MyAtlas reads completed project evidence from the committed exports in this repository. Project completion, learned topics and independently verified topics remain separate measures. Earlier `/hyperskill-projects/` Atlas links redirect to their new addresses, preserving view parameters and bookmarks.
