#!/usr/bin/env python3
"""Print a deterministic public review candidate. No publication or source writes."""
import argparse
import json
from pathlib import Path
from knowledge_atlas.project_completion import scan

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
args = parser.parse_args()
scopes = json.loads((args.root / 'src/myatlas/knowledge-atlas-scope-pyramid/scope-index.json').read_text())
result = scan(args.root, scopes)
print(json.dumps(result, sort_keys=True, indent=2))
raise SystemExit(bool(result['rejected']))
