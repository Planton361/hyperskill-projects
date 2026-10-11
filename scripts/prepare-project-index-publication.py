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
    parser.add_argument('--recovery-pointer',type=Path)
    args=parser.parse_args()
    recovery=None
    if args.recovery_pointer:
        source=args.recovery_pointer
        if not source.is_file() or any(p.is_symlink() for p in (source,*source.parents)):
            parser.error('Regular owner-selected recovery pointer required')
        recovery=source.read_bytes()
    p=decode(prepare(ROOT,args.revision,args.output,bootstrap=args.bootstrap,
                     guard=args.output.parent/'publication-guard.json',recovery=recovery))
    print('Validated reachable immutable payload; candidate pointer staged:',p['index_url'])
