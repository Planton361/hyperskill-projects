#!/usr/bin/env python3
"""Read-only deterministic project index from an explicitly pinned commit."""
import argparse
import sys
from pathlib import Path
from project_index import ROOT, generate, validate_index

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,default=ROOT)
    parser.add_argument('--revision',required=True)
    args=parser.parse_args()
    raw=generate(args.repository,args.revision)
    validate_index(args.repository,raw,args.revision)
    sys.stdout.buffer.write(raw)
