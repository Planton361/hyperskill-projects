# MyAtlas V6.6

[Open MyAtlas](https://planton361.github.io/hyperskill-projects/knowledge-map/)

MyAtlas is my learning atlas and owner-attested Hyperskill project portfolio. Its two views connect a complete **Global Atlas** with **My Skill Tree**. Explore 849 Categories and 3,106 Topics, or select an independent Course, Project, or Stage pyramid. Search, the shared Inspector, exact-ID navigation, and browser history work across the views.

The current portfolio records **31 learned Topics**, **12 independently verified Topics**, and **1 completed Project**: Simple Chat Bot with Java (Project113). Course8 has 31 / 89 learned Topics and 1 / 11 associated Projects completed. Catalog inventories—52 Courses, 391 Projects, and 1,967 Stages—describe the atlas, not my enrolled plan or official overall completion.

Learning is the exact-ID union of directly observed personal learning and explicit Topic requirements of owner-attested completed Projects. Project completion provides owner-attested learning evidence; it is **not independent Hyperskill verification**. It does not establish Course or Stage completion. Missing completion records are omitted from the compact UI; provenance and evidence dates remain available in collapsed Data details.

## Exported Hyperskill Projects

Each export remains a standalone application with its source and build wrapper.

| Project | Language | Source |
| --- | --- | --- |
| Simple Chat Bot with Java · Project113 | Java | [Export and instructions](java/Simple%20Chat%20Bot%20with%20Java/) |

[All Java exports](java/). Importing and publishing a new completed export activates the same validated completion scanner and Topic union—no Hyperskill API, scraping, or synthetic achievements. The **MyAtlas Pages** workflow validates committed evidence, rebuilds public progress, and deploys the static artifact from `main`; it never commits generated files back to Git.

## Local development

Python3 and Node22 build the static application without npm runtime dependencies:

```sh
python3 -B scripts/build-myatlas.py
python3 -B scripts/check-myatlas-production.py --site build/pages/knowledge-map --current-head
mkdir -p build/preview
ln -s ../pages build/preview/hyperskill-projects
python3 -B -m http.server 8807 --bind 127.0.0.1 --directory build/preview
```

Open `http://127.0.0.1:8807/hyperskill-projects/knowledge-map/`. Use a fresh preview directory, or retain its existing symlink when rebuilding.

Canonical accepted sources are in `src/myatlas/`; public completion records are in `data/myatlas/`; historical Knowledge observations and State remain intact. `docs/knowledge-map/` is the reviewed committed production snapshot; Actions builds the current projection into an artifact, so source updates need no generated-data commit loop.

[Build, validation and evidence contract](docs/MYATLAS-DEVELOPMENT.md) · [Release and rollback](docs/V66-PRODUCTION-RELEASE.md) · [Rollback procedure](docs/MYATLAS-ROLLBACK.md)

Earlier experimental applications and generated comparison imagery have been removed. The small frozen compatibility fixtures that remain support historical State reconstruction; they are not public deployment sources. [Current release](https://github.com/Planton361/hyperskill-projects/tree/v6.6.0) · [Cleanup inventory](docs/releases/v66-cleanup-inventory.json).
