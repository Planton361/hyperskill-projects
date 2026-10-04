#!/usr/bin/env python3
"""Offline incremental Knowledge Atlas updates. Never commits, pushes or deploys."""
import argparse
import json
import os
from pathlib import Path
import sys
from knowledge_atlas.pipeline import run
from knowledge_atlas.report import human


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--dry-run', action='store_true')
    modes.add_argument('--check', action='store_true')
    modes.add_argument('--build', action='store_true')
    parser.add_argument('--rebalance', action='store_true', help='explicit geography migration; combine with --dry-run to review')
    parser.add_argument('--preview', action='store_true', help='package validated build into docs/knowledge-atlas-preview; no deployment')
    parser.add_argument('--production', action='store_true', help='package SAFE_TO_APPLY Atlas into docs/knowledge-map; no commit/push/deploy')
    parser.add_argument('--source', type=Path, help='normalized data directory (default data/knowledge)')
    parser.add_argument('--output', type=Path, help='isolated managed build directory below prototypes/')
    parser.add_argument('--state', type=Path, help='isolated test state below prototypes/ (default state/knowledge-atlas)')
    parser.add_argument('--bootstrap-state', action='store_true', help='initialize absent state from frozen accepted V6 baseline only')
    parser.add_argument('--approve-review', action='store_true', help='explicitly authorize a validated REVIEW_REQUIRED candidate')
    parser.add_argument('--recover-transaction', action='store_true', help='recover interrupted publication under exclusive lock')
    parser.add_argument('--migrate-state', action='store_true', help='explicit supported state-schema 1 to 2 ordered-hash migration')
    parser.add_argument('--report-json', type=Path, help='write this run JSON and sibling .txt report (explicit diagnostic output)')
    parser.add_argument('--json', action='store_true', help='print only machine-readable report to stdout')
    args = parser.parse_args()
    if args.preview and (args.check or args.dry_run): parser.error('--preview requires build mode')
    if args.production and (args.preview or args.bootstrap_state or args.recover_transaction or args.migrate_state or args.rebalance or args.approve_review or args.source or args.state or args.output):
        parser.error('--production requires canonical data/state and SAFE_TO_APPLY; use separate reviewed state migration first')
    if sum([args.bootstrap_state,args.recover_transaction,args.migrate_state])>1:parser.error('choose one bootstrap/recovery/migration operation')
    if (args.bootstrap_state or args.recover_transaction or args.migrate_state) and (args.check or args.dry_run or args.preview or args.rebalance or args.approve_review):
        parser.error('bootstrap/recovery are separate explicit writer operations')
    if args.check and (args.rebalance or args.approve_review): parser.error('--check cannot authorize changes')
    root=Path(__file__).resolve().parents[1]
    if args.report_json:
        path=args.report_json.resolve()
        if path.suffix != '.json': parser.error('--report-json requires a .json diagnostic file')
        if any(path.is_relative_to(root/p) for p in ('state','data','docs','prototypes','scripts','generated','.github')):
            parser.error('--report-json must not overwrite source, state, runtime or build trees')
    mode = 'check' if args.check else 'dry-run' if args.dry_run else 'build'
    try:
        report = run(root, args.output, args.source, mode, args.rebalance, args.preview,
                     state=args.state, approve_review=args.approve_review, bootstrap=args.bootstrap_state,
                     recover=args.recover_transaction,migrate=args.migrate_state,production=args.production)
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as e:
        marker = next((m for m in ('FONT_METRICS_MISMATCH','STATE_MIGRATION_REQUIRED','REBALANCE_REQUIRED',
                       'RECOVERY_REQUIRED') if m in str(e)), 'VALIDATION_FAILED')
        report = {'status': marker, 'message': str(e), 'safe_to_build_preview': False, 'applied':False}
    if args.report_json:
        from knowledge_atlas.transaction import durable_file, sync_dir
        path=args.report_json.resolve(); path.parent.mkdir(parents=True,exist_ok=True)
        for p,content in [(path,(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()),
                          (path.with_suffix('.txt'),(human(report)+'\n').encode())]:
            tmp=p.with_name(p.name+'.tmp'); durable_file(tmp,content); os.replace(tmp,p); sync_dir(p.parent)
    if not args.json: print(human(report) + '\n\nJSON report:')
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    if report.get('applied') or report['status']=='SAFE_TO_APPLY': return 0
    return 3 if report['status']=='REVIEW_REQUIRED' else 2 if report['status']=='REBALANCE_REQUIRED' else 1


if __name__ == '__main__': sys.exit(main())
