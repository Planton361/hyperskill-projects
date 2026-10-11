#!/usr/bin/env python3
"""Gated existing-Pages-job preparation; not a separate deployment process."""
import argparse
from pathlib import Path
from project_index import ROOT, decode
from project_index_store import prepare, current_main

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision',required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--bootstrap',action='store_true')
    args=parser.parse_args()
    p=decode(prepare(ROOT,args.revision,args.output,bootstrap=args.bootstrap,
                     guard=args.output.parent/'publication-guard.json'))
    print('Validated reachable immutable payload; candidate pointer staged:',p['index_url'])
