# MyAtlas rollback

The annotated `knowledge-atlas-pre-v6.6` tag points to the exact previously deployed Pages revision `a8b79e2e6c32df990fc3305983bb5aff1d9e2500`. Its historical Production fingerprint is `36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7`. The historical manifests are retained in `docs/releases/`; Git history contains the entire previous application. No duplicate application archive is required in the current runtime.

To reconstruct and validate locally:

```sh
git worktree add --detach /tmp/myatlas-rollback knowledge-atlas-pre-v6.6
cd /tmp/myatlas-rollback
python3 -B scripts/check-adaptive-production.py
```

If the live V6.6 edition fails, stop cleanup and prevent automatic main deployments before restoring the old edition. These are rollback operations, not part of normal release validation:

```sh
gh workflow disable myatlas-pages.yml --repo Planton361/hyperskill-projects
git branch rollback/pre-v6.6 knowledge-atlas-pre-v6.6
git push origin refs/heads/rollback/pre-v6.6
printf '%s' '{"build_type":"legacy","source":{"branch":"rollback/pre-v6.6","path":"/docs"}}' > /tmp/myatlas-rollback-pages.json
gh api --method PUT repos/Planton361/hyperskill-projects/pages --input /tmp/myatlas-rollback-pages.json
```

If that rollback branch already exists, verify its exact target before using it; never force-update it. Wait for the Pages build to succeed, verify its commit against the rollback tag, and smoke-test the public site. This preserves main and all accepted development commits. Do not report rollback success from a push alone.

To resume a repaired V6.6 edition, explicitly restore Pages `build_type: workflow`, enable `myatlas-pages.yml`, dispatch it on verified `main`, and verify the actual deployment and live assets. No reset, force push, or rewriting of historical personal evidence is required.
