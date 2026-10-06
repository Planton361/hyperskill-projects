#!/usr/bin/env bash
# Read-only readiness report. Installs nothing and writes no repository state.
set -u
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
printf 'System: %s / %s\n' "$(uname -s)" "$(uname -m)"
if [ "$(uname -s)" != Darwin ] || [ "$(uname -m)" != arm64 ]; then
  printf 'Expected continuation host: macOS / arm64 (report only).\n'
fi
for tool in git python3 node npm; do
  if command -v "$tool" >/dev/null 2>&1; then "$tool" --version; else printf 'Missing: %s\n' "$tool"; fi
done
for file in MAC-HANDOFF.md scripts/update-knowledge-atlas.py scripts/knowledge_atlas/presentation/adaptive.cjs prototypes/adaptive-pyramid/core.cjs prototypes/global-pyramid/generated/global-geometry.json prototypes/global-pyramid/root-layout/previous-global-geometry.json; do
  if [ -f "$repo_root/$file" ]; then printf 'OK: %s\n' "$file"; else printf 'Missing: %s\n' "$file"; fi
done
if command -v node >/dev/null 2>&1; then
  node - "$repo_root" <<'NODE'
const path = require('node:path'), fs = require('node:fs');
try {
  const {chromium} = require(process.env.PLAYWRIGHT_MODULE || path.join(process.argv[2], 'scripts/knowledge_atlas/node_modules/playwright'));
  const executable = process.env.CHROMIUM_EXECUTABLE || chromium.executablePath();
  console.log('Optional Chromium: ' + (fs.existsSync(executable) ? 'available' : 'not installed'));
} catch { console.log('Optional Playwright: not installed'); }
NODE
fi
