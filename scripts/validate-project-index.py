#!/usr/bin/env python3
"""Independently check index metadata, exact Git inventories, URLs and digest."""
import argparse
from pathlib import Path
from project_index import ROOT, sha, validate_index, validate_pointer

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('index',type=Path)
    parser.add_argument('--repository',type=Path,default=ROOT)
    parser.add_argument('--revision',required=True)
    parser.add_argument('--pointer',type=Path)
    args=parser.parse_args()
    raw=args.index.read_bytes()
    data=validate_index(args.repository,raw,args.revision)
    if args.pointer: validate_pointer(args.pointer.read_bytes(),raw)
    print(f"PASS revision={data['revision']} projects={len(data['projects'])} sha256={sha(raw)}")
