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
        from knowledge_atlas.activation_persistence import accepted
        cp,previous,history,geometry,loaded=accepted(root)
        planner = ActivationPlanner(Catalog(loaded), cp, geometry)
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
