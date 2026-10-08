# MyAtlas V6.6 production release

Release branch prepared from the frozen `3b110202000bf9712033211ef8b72fe62f43baee` checkpoint. Remote validation and live publication are pending; this document will be completed only after actual deployment and cleanup verification.

Rollback anchor: annotated `knowledge-atlas-pre-v6.6` at exact previously deployed `a8b79e2e6c32df990fc3305983bb5aff1d9e2500`, published before migration. [Exact rollback procedure](MYATLAS-ROLLBACK.md).

Production entry: `docs/knowledge-map/index.html`. Public URL: https://planton361.github.io/hyperskill-projects/knowledge-map/

Canonical sources: `src/myatlas/`, completion evidence: `data/myatlas/`, builder: `scripts/build-myatlas.py`, focused tests: `tests/myatlas/`. The runtime has no prototype directory dependency. Historical Knowledge and unrelated State are preserved. Accepted geometry and progress semantics remain frozen.

Baseline: 849 Categories, 3,106 Topics, zero unresolved Topics, 52 Courses, 391 Projects, 1,967 Stages, 867 Course→Project associations; 31 learned, 12 verified, Project113 completed once; Course8 31/89 Topics and 1/11 associated Projects. No established Course completion record.

[Reviewed V6.6 manifest](releases/myatlas-v6.6.json), [historic migration manifest](releases/knowledge-atlas-pre-v6.6-manifest.json), and [historic release manifest](releases/knowledge-atlas-pre-v6.6-release.json) preserve integrity evidence. The new guard validates frozen application/source inventories, historical data, and reconstruction of generated progress from exact committed evidence. The old verifier remains available through rollback history and the edition dispatcher.

Pages uses the supported artifact pipeline: read-only build and validation, separate Pages/OIDC deployment permissions, validated main only, stale-SHA refusal, no generated commits. [Development and workflow details](MYATLAS-DEVELOPMENT.md).
