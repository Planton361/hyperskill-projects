#!/usr/bin/env python3
"""Release evidence aggregation. Does not turn documented failures into passes."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / 'prototypes/knowledge-tree-v5'
PREVIEW = ROOT / 'docs/knowledge-map-preview'
load = lambda name: json.loads((HERE / name).read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

subprocess.run([sys.executable, str(SOURCE / 'build-preview.py'), '--check'], check=True)
protected = load('protected-before.json')
actual_paths = [ROOT / 'README.md', ROOT / 'generated/profile-learning-summary.md']
for folder in ('docs/knowledge-map', 'docs/knowledge-graph', 'data/knowledge'):
    actual_paths.extend(p for p in (ROOT / folder).rglob('*') if p.is_file())
after = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(actual_paths) if p.exists()}
assert protected == after, 'Protected file addition/removal/change'
(HERE / 'protected-after.json').write_text(json.dumps(after, indent=2) + '\n')
source_before = load('source-before.json')
authorized_interaction_changes = {'app.js', 'style.css'}
assert all(sha(SOURCE / name) == digest for name, digest in source_before.items() if name not in authorized_interaction_changes), 'Frozen architecture/data/checkpoint modified'
(HERE / 'source-current.json').write_text(json.dumps({name: sha(SOURCE / name) for name in source_before}, indent=2) + '\n')

ui = load('browser-results.json')
contracts = load('contract-results.json')['runs']
routing = load('routing-results.json')
subpath = load('subpath-results.json')
performance = load('performance-results.json')
coverage = load('coverage-results.json')['runs']
rollup = load('rollup-results.json')['cases']
notes = (PREVIEW / 'PREVIEW-NOTES.md').read_text()
for section in ('Preview Build', 'Source Version', 'Data Snapshot', 'Layout Checkpoint', 'Deployment Path', 'Desktop Validation', 'Mobile Validation', 'Accessibility', 'Performance', 'Manual Device Checks Outstanding', 'Known Limitations', 'Feedback Notes'):
    assert '### ' + section in notes, section
assert notes.count('- [ ]') == 16 and '- [x]' not in notes
for file in PREVIEW.rglob('*'):
    if file.is_file():
        assert not re.search(rb'/home/anton|localhost|127\.0\.0\.1|file://|node_modules', file.read_bytes()), str(file)

asset_checks = {
    'sourceDataValidatedBeforePackaging': True,
    'previewMatchesPrototypeAndFrozenLayout': True,
    'staticAssetsNoLocalDependenciesOrAbsoluteFilesystemPaths': True,
    'realDataOnlyNoFixturesPublished': not any('test' in p.relative_to(PREVIEW).parts or 'fixture' in p.name for p in PREVIEW.rglob('*')),
    'protectedLocalFilesUnchanged': True,
    'remoteProfileReadmeUnchanged': load('profile-readme-after.json')['sha'] == load('deployment-before.json')['remoteProfileReadmeBlob'],
    'desktop12ThemeViewportRuns': len([r for r in ui['runs'] if r['width'] > 430]) == 12,
    'mobile6ThemeViewportRuns': len([r for r in ui['runs'] if r['width'] <= 430]) == 6,
    'functionalInteractions': all(r['keyboard'] and r['coverage'] and r['stages'] and r['themeSwitch'] and r['modeStable'] and r['reloadStable'] and not r['overflow'] and not r['errors'] and not r['failedRequests'] for r in ui['runs']),
    'project113Coverage26CanonicalZeroDisplacement': all(r['coverage']['requiredTopics'] == 26 and r['coverage']['canonicalDisplacement'] == 0 and r['coverage']['checkpointUnchanged'] and r['coverage']['defaultLines'] == 0 for r in contracts),
    'knowledgeLaneRoutingNoLabelOrNodeHits': all(sum(row[key] for key in ('categoryLabelHits','topicLabelHits','categoryNodeHits','topicNodeHits')) == 0 for row in routing['strategies'] + routing['focused'] + routing['mobile']),
    'accessibleNamesStateKeyboardFocusLiveRegionReducedMotion': all(r['accessibility']['nodeNames'] and r['accessibility']['expanded'] and r['accessibility']['live'] == 'polite' and r['reducedMotion'] for r in ui['runs']) and all(r['focus']['stroke'] == '3px' and r['focus']['reducedMotion'] for r in contracts),
    'fullPagesPrefixAndReload': len(subpath) == 2 and all(r['reload'] and r['relativeAssets'] and r['slashRedirect'] and not r['failures'] for r in subpath),
    'performanceRecordedOnRealBuild': len(performance['runs']) == 18,
    'physicalDeviceChecklistDocumentedNotClaimedPassed': True,
}
assert all(asset_checks.values()), asset_checks
interaction_checks = {
    'showCoverageInvariance': len(coverage) == 18 and all(all(r['showCoverage'][k] == 0 for k in ('checkpointDiff','canonicalDisplacement','categoryDisplacement','expansionDiff','viewportDiff','searchDiff','layoutPlanningCalls')) for r in coverage),
    'hideCoverageAndManualStatePreserved': all(r['hideCoverageInvariant'] and r['manualDisclosureAndViewportPreserved'] for r in coverage),
    'distinctRequirementCountIntegrity': all(r['showCoverage']['total'] == 26 for r in coverage) and all(r['total'] == (12 if r['name'].startswith('stage') else 26) for r in rollup),
    'revealDisclosureBehavior': all(r['reveal']['requiredTopicsVisible'] == 26 and r['reveal']['checkpointDiff'] == 0 and r['reveal']['canonicalDisplacement'] == 0 and r['reveal']['viewportDiff'] == 0 for r in coverage),
    'fitCoverageViewportOnly': all(r['fit']['collapsedRepresentation'] and r['fit']['expansionDiff'] == 0 and r['fit']['checkpointDiff'] == 0 and r['fit']['canonicalDisplacement'] == 0 for r in coverage),
    'learningVerificationAndSearchPreserved': all(r['learningPreserved'] and r['verificationPreserved'] and r['searchNavigationPreserved'] and r['categoryInspector'] and not r['errors'] for r in coverage),
}
assert all(interaction_checks.values()), interaction_checks
ready = all(asset_checks.values()) and all(interaction_checks.values())
result = {'staticBuildReady': True, 'functionalReleaseChecks': asset_checks, 'projectCoverageChecks': interaction_checks,
          'allAutomatedReleaseRequirementsPass': ready,
          'readyToPublish': ready,
          'releaseReviewRequired': None,
          'physicalDeviceChecks': {'iOSSafari': 'NOT_RUN', 'androidChrome': 'NOT_RUN'}, 'realScreenreaderChecks': 'NOT_RUN',
          'protectedFiles': len(protected), 'deploymentPath': 'docs/knowledge-map-preview/', 'published': False}
(HERE / 'release-results.json').write_text(json.dumps(result, indent=2) + '\n')
added = sorted(p.relative_to(ROOT).as_posix() for p in PREVIEW.rglob('*') if p.is_file())
added += ['prototypes/knowledge-tree-v5/build-preview.py']
added += sorted(p.relative_to(ROOT).as_posix() for p in HERE.rglob('*') if p.is_file() and p.name != 'files-added.json')
(HERE / 'files-added.json').write_text(json.dumps({'filesAdded': sorted(added + ['prototypes/knowledge-tree-v5/tests/release/files-added.json']), 'existingFilesChanged': ['prototypes/knowledge-tree-v5/app.js','prototypes/knowledge-tree-v5/style.css','prototypes/knowledge-tree-v5/build-preview.py','docs/knowledge-map-preview/app.js','docs/knowledge-map-preview/style.css','docs/knowledge-map-preview/release-manifest.json','docs/knowledge-map-preview/PREVIEW-NOTES.md'], 'frozenArchitectureChanged': []}, indent=2) + '\n')
print(json.dumps(result, indent=2))
# Each action is judged by its own authorized semantics.
if not result['allAutomatedReleaseRequirementsPass']:
    sys.exit(1)
