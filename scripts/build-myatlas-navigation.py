#!/usr/bin/env python3
"""Apply/check the separately approved three-file navigation delta."""
import argparse
import json
from pathlib import Path
from knowledge_atlas.navigation_release import apply_navigation, verify_navigation

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
parser.add_argument('--site', type=Path, default=ROOT / 'build/pages/knowledge-map')
args = parser.parse_args()
action = verify_navigation if args.check else apply_navigation
print(json.dumps(action(ROOT, args.site), sort_keys=True, indent=2))
