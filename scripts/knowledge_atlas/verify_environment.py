#!/usr/bin/env python3
"""Validate pinned font binaries and browser metrics without writing Atlas state."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from knowledge_atlas.layout_update import bridge

HERE = Path(__file__).resolve().parent
policy = json.loads((HERE/'font-canary.json').read_text())
for name, expected in policy['font_files'].items():
    if hashlib.sha256((HERE/'fonts'/name).read_bytes()).hexdigest() != expected:
        raise SystemExit('FONT_BINARY_MISMATCH: '+name)
result = bridge(HERE.parents[1]/'prototypes/knowledge-atlas-v6', action='canary')
print(json.dumps(result,sort_keys=True,indent=2))
