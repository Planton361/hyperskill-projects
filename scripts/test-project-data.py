#!/usr/bin/env python3
"""Read-only data-contract acceptance for one exact archive commit."""
import argparse
import json
import os
from pathlib import Path
from project_data import validate_data
from project_index import ROOT, git

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--myatlas-root',type=Path,required=True)
parser.add_argument('--repository',type=Path,default=ROOT)
parser.add_argument('--revision',required=True)
args=parser.parse_args()
if git(args.repository,'rev-parse','HEAD').decode().strip()!=args.revision:
    raise ValueError('Selected commit differs from checkout')
report=validate_data(args.repository,args.myatlas_root,args.revision)
raw=json.dumps(report,sort_keys=True,indent=2)+'\n'
Path('project-data-report.json').write_text(raw);print(raw)
if os.environ.get('GITHUB_STEP_SUMMARY'):
    with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as output: output.write('### Archive data acceptance\n\n```json\n'+raw+'```\n')
