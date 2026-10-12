#!/usr/bin/env python3
"""Read-only rollout evidence: no store creation, push, pointer staging or deployment."""
import argparse
import json
from pathlib import Path
import subprocess
from project_index import generate, validate_index, git, sha, blob, tree
from project_data import validate_data


def preflight(root,atlas,revision):
    first=generate(root,revision);second=generate(root,revision)
    if first!=second:raise ValueError('Index is not reproducible')
    validate_index(root,first,revision)
    value=json.loads(first)
    baseline=json.loads((atlas/'docs/contracts/hyperskill-baseline-v1.json').read_bytes())
    entries=tree(root,revision)
    hashes={name:sha(blob(root,entries[name][2])) for name in baseline['archive_sha256']}
    if hashes!=baseline['archive_sha256'] or len(hashes)!=22:raise ValueError('Baseline archive hashes changed')
    ids=[p['project_id'] for p in value['projects']]
    if ids!=[113,229,380]:raise ValueError('Bootstrap must contain exactly the three real completions')
    for name,digest in baseline['trusted_input_sha256'].items():
        if sha(git(atlas,'show','HEAD:'+name))!=digest:raise ValueError('Trusted baseline input changed: '+name)
    data=validate_data(root,atlas,revision)
    if data['global']!=baseline['global_progress'] or data['verified_topic_ids']!=baseline['verified_topic_ids'] or data['course_completion']!=baseline['course_completion']:raise ValueError('Baseline progress changed')
    return dict(status='TESTED',source_revision=revision,application_revision=git(atlas,'rev-parse','HEAD').decode().strip(),
                validator=value['validator'],index_sha256=sha(first),index_bytes=len(first),reproducible=True,
                projects=value['projects'],archive_sha256=hashes,data_acceptance=data,
                geometry=baseline['geometry'],course_completion=baseline['course_completion'],
                store_revision=None,pointer='NOT_CREATED',production='BLOCKED_PENDING_SEPARATE_OWNER_APPROVAL',
                next_step='Refresh canonical main revision after reviewed infrastructure merges, then repeat preflight before owner-approved bootstrap')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--myatlas-root',type=Path,required=True)
    p.add_argument('--revision',required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();report=preflight(args.repository.resolve(),args.myatlas_root.resolve(),args.revision)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report,sort_keys=True,indent=2))
