# Hyperskill Projects

This repository contains my owner-attested final solutions for completed [Hyperskill](https://hyperskill.org/) projects. It is a **source archive**, not a claim that any archived solution has been compiled or run.

New projects are stored under `projects/<ID>/` with selected owner-reviewed source files, a per-project README, and a SHA-256 manifest. Existing legacy archives retain their original paths and formats (schemas 2 and 3). The publisher supports arbitrary safe source-file extensions; it does not require a per-language adapter.

## Published projects

| Hyperskill ID | Project | Language | Archived code |
| ---: | --- | --- | --- |
| [113](https://hyperskill.org/projects/113) | Simple Chat Bot with Java | Java | [Browse](java/Simple%20Chat%20Bot%20with%20Java/) |
| [229](https://hyperskill.org/projects/229) | Zookeeper with Java | Java | [Browse](java/Zookeeper%20with%20Java/) |
| [380](https://hyperskill.org/projects/380) | My First Project with Java | Java | [Browse](java/My%20First%20Project%20with%20Java/) |

**Documentation snapshot:** 14 October 2026. The project manifests in Git are the source of truth, and the [public validated project index](https://planton361.github.io/hyperskill-projects/portfolio/current.json) supplies the current published inventory. For the live, human-readable project list and learning progress, open [MyAtlas — My Skill Tree](https://planton361.github.io/myatlas/knowledge-map/?view=skill-tree) and choose **Meine Projekte**. The README table is updated in a separate documentation-only PR after new projects have been successfully merged; it is not an automatically refreshed view.

## Publish a completed project

From a current local checkout, use Python 3.12 and the existing universal publisher:

```sh
python3.12 scripts/publish-hyperskill-project "/absolute/path/to/Academy Project" --dry-run
```

Inspect the exact project identity, selected final solution files, file roles, excluded paths, and hashes. If the selection is ambiguous or resources are needed, review an explicit `--files-from` JSON selection. When satisfied, run the same command without `--dry-run` in an **interactive terminal**:

```sh
python3.12 scripts/publish-hyperskill-project "/absolute/path/to/Academy Project"
```

The publisher creates an isolated review checkout. I personally type `COMPLETE <ID>` to attest that I completed the project and own its code, then `PUBLISH <ID>` after inspecting the full Git diff. It creates a **Draft pull request**; merging is always a separate, manual decision. Neither the publisher nor its checks compile, execute, or install the archived solution. If a publication was interrupted, use the existing `--resume` flow rather than attempting a second import.

See [publishing instructions and the exact safety rules](docs/PUBLISHING.md).

## Validated index and MyAtlas

After a reviewed project PR is merged into `main`, GitHub Actions validates the archive and publishes a revision-bound, SHA-256-validated project index on GitHub Pages through its append-only store. Only a fully validated index is exposed by the [public pointer](https://planton361.github.io/hyperskill-projects/portfolio/current.json).

[MyAtlas](https://github.com/Planton361/myatlas) reads that public index anonymously. Its **Meine Projekte** menu and My Skill Tree update from the accepted data without a new MyAtlas source commit or manual site rebuild for each project. A failed refresh retains the last validated snapshot (or the static fallback if none is cached). Learning and independent verification follow the trusted MyAtlas catalog; an archived project never creates unsupported Topic or Course claims.

Repository README updates are deliberately **separate from project archive PRs** to preserve their focused, data-only acceptance path.
