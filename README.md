# Hyperskill Projects

This repository archives my final Hyperskill solution files. New projects use a
source-only format: the archive preserves selected `.java` or `.py` files and
their paths, plus a short README and a SHA-256 manifest with the exact project ID
and my completion attestation. A source archive makes no claim that a solution
builds or runs.

Projects 113 and 380 use the earlier schema-2 export format. They remain valid
and unchanged; MyAtlas reads both formats.

## Projects

| Project | Language | Export format |
| --- | --- | --- |
| [Simple Chat Bot with Java](java/Simple%20Chat%20Bot%20with%20Java/) · [Project 113](https://hyperskill.org/projects/113) | Java | legacy schema 2 |

[Browse Java archives](java/README.md). MyAtlas reads committed project evidence
from this repository and derives learned topics only from its trusted catalog.

## Archive a completed project

Use the existing publisher from a clean, current checkout:

```sh
python3.12 scripts/publish-hyperskill-project "/path/to/Academy Project"
```

The publisher reads project identity and language from Academy metadata, asks for
the actual UTC completion time if it was not supplied, and first shows a
read-only dry-run. It archives final solution files without reading Academy
build configuration. In the real interactive flow, the owner personally types
`COMPLETE <ID>` and `PUBLISH <ID>` after reviewing the evidence and diff. It then
creates one branch and a draft PR in an isolated checkout. Nothing is merged
automatically. See [publisher details and safety rules](scripts/README.md).

Old schema-2 exports remain readable and keep their historical standalone files;
new exports do not add build scripts, wrappers, or runtime claims.

## MyAtlas

[MyAtlas](https://github.com/Planton361/myatlas) consumes both legacy and
source-only completion evidence after an approved project merge. Its daily Pages
sync refreshes the site; no MyAtlas production code or deployment is part of a
project archive.
