#!/usr/bin/env python3
"""Git-only completed export review; stdout artifact, no repository writes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from knowledge_atlas.git_completion import committed_inputs

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=ROOT)
parser.add_argument('--ref', default='HEAD')
parser.add_argument('--previous', type=Path, help='Explicit local accepted projection for review; default reads committed accepted-sync.json')
parser.add_argument('--summary', action='store_true', help='Render the JSON artifact on stdin as a human-readable summary')
args = parser.parse_args()
try:
    if args.summary:
        artifact = json.load(sys.stdin)
        c = artifact['changes']
        print('# Completed Project learning review\n')
        print('Source commit: ' + artifact['projection']['source']['commit'])
        print('Semantic changes: ' + str(c['semantic_change']))
        for key in ('newly_completed_project_ids', 'removed_or_revoked_project_ids', 'newly_learned_topic_ids',
                    'no_longer_effectively_learned_topic_ids', 'already_learned_topic_ids', 'updated_provenance_topic_ids'):
            print('- ' + key.replace('_', ' ') + ': ' + json.dumps(c[key]))
        print('- Global learned: ' + str(c['global']['learned']) + '; verified: ' + str(c['global']['verified']))
        portfolio = artifact['projection']['portfolio']
        print('- Confirmed completed Projects: ' + str(portfolio['completed_project_count']) + '; catalog Projects: ' + str(portfolio['project_catalog_count']))
        print('- Course completions: ' + ('Not recorded' if portfolio['completed_course_count'] is None else str(portfolio['completed_course_count']) + ' confirmed') + '; catalog Courses: ' + str(portfolio['course_catalog_count']))
        print('- Impacted scopes: ' + ', '.join(k + '=' + str(len(v)) for k,v in c['impacted_scopes'].items()))
    else:
        inputs = committed_inputs(args.root, args.ref)
        if args.previous:
            inputs['previous'] = json.loads(args.previous.read_text())
            inputs['source']['baseline_sha256'] = hashlib.sha256(args.previous.read_bytes()).hexdigest()
        if inputs['previous'] and 'projection' in inputs['previous']:
            inputs['previous'] = inputs['previous']['projection']
        engine = ROOT / 'scripts/knowledge_atlas/completion_projection.cjs'
        inputs['source']['implementation_sha256'] = {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
            'scripts/sync-project-completion.py', 'scripts/knowledge_atlas/git_completion.py',
            'scripts/knowledge_atlas/project_completion.py', 'scripts/knowledge_atlas/course_completion.py', 'scripts/knowledge_atlas/completion_projection.cjs',
            'prototypes/knowledge-atlas-v6-skill-tree/progress-analytics.js')}
        result = subprocess.run(['node', str(engine)], input=json.dumps(inputs), text=True, capture_output=True, check=True)
        print(json.dumps(json.loads(result.stdout), sort_keys=True, indent=2))
except (ValueError, KeyError, OSError, subprocess.CalledProcessError):
    # Never echo arbitrary metadata, subprocess stderr, private paths or raw blobs.
    print('Git completion validation failed; inspect committed export metadata and catalog identities.', file=sys.stderr)
    raise SystemExit(1)
