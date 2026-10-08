#!/usr/bin/env python3
"""Read-only exact V6.6 application, evidence and progress integrity validation."""
import argparse,json
from pathlib import Path
from knowledge_atlas.myatlas_guard import verify_release
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--site',type=Path)
p.add_argument('--current-head',action='store_true')
a=p.parse_args()
print(json.dumps(verify_release(Path(__file__).resolve().parents[1],a.site,a.current_head),sort_keys=True,indent=2))
