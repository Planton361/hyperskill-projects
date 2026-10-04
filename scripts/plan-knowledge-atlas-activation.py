#!/usr/bin/env python3
"""Read-only activation planning from existing local evidence and accepted geometry."""
import argparse
import json
from pathlib import Path
import sys
from knowledge_atlas import snapshot, state
from knowledge_atlas.catalog import Catalog
from knowledge_atlas.activation import ActivationPlanner, human


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    context = parser.add_mutually_exclusive_group()
    context.add_argument('--course', type=int, help='plan one explicitly tracked course')
    context.add_argument('--project', type=int, help='plan explicit requirements of one known project')
    parser.add_argument('--json', action='store_true', help='deterministic complete plan on stdout')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        cp, previous = state.read(root / 'state/knowledge-atlas')
        geometry = json.loads((root / 'docs/knowledge-map/geometry.js').read_text().split('=', 1)[1].rstrip(';\n'))
        if snapshot.ordered_digest(geometry) != previous['geometry_fingerprint']:
            raise ValueError('Accepted geometry fingerprint disagrees with persistent state')
        planner = ActivationPlanner(Catalog(snapshot.load_source(root / 'data/knowledge')), cp, geometry)
        kwargs = {'mode': 'CURRENT_COURSE', 'course_ids': [args.course]} if args.course is not None else \
                 {'mode': 'PROJECT_FOCUS', 'project_ids': [args.project]} if args.project is not None else {}
        plan = planner.plan(**kwargs)
        print(snapshot.encode(plan).decode(), end='') if args.json else print(human(plan))
        # Planning completed successfully even if the plan requires review/metadata.
        return 0
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as e:
        print(json.dumps({'status': 'VALIDATION_FAILED', 'message': str(e)}, sort_keys=True))
        return 1


if __name__ == '__main__':
    sys.exit(main())
