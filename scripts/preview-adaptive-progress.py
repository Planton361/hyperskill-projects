#!/usr/bin/env python3
"""Preview explicit progress using the adopted pipeline; writes only a new temp root."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
from knowledge_atlas import adaptive_production as A, snapshot
from knowledge_atlas.personal_progress import normalize

ROOT = Path(__file__).resolve().parents[1]


def preview(source, envelope):
    source = Path(source).resolve()
    original = snapshot.load_source(source / A.KNOWLEDGE)
    updated, semantic = normalize(original, envelope)
    # Caller cannot select a write destination. Never invoke a real Knowledge or
    # Production writer; all writes below are to this newly allocated temp root.
    temp_base = Path(tempfile.gettempdir()).resolve()
    A.require(not temp_base.is_relative_to(ROOT) and not temp_base.is_relative_to(source),
              'Temporary directory must be outside the repository and source root')
    disposable = Path(tempfile.mkdtemp(prefix='adaptive-progress-', dir=str(temp_base))).resolve()
    A.require(disposable.parent == temp_base and not disposable.is_relative_to(ROOT)
              and not disposable.is_relative_to(source), 'Real-root fixture publication refused')
    for folder in (A.KNOWLEDGE, A.STATE, 'prototypes/global-pyramid/generated',
                   'prototypes/adaptive-pyramid/vendor', 'prototypes/adaptive-pyramid/production-preview'):
        destination = disposable / folder
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Input roots supply data, never executable packaging code.
        origin = ROOT if folder.startswith('prototypes/adaptive-pyramid/') else source
        shutil.copytree(origin / folder, destination,
                        ignore=shutil.ignore_patterns('target', 'current', '*.png', '__pycache__'))
    before = A.candidate(disposable)
    for table in ('progress', 'evidence'):
        (disposable / A.KNOWLEDGE / (table + '.json')).write_bytes(snapshot.encode(updated[table]))
    observation_file = semantic['observation_file']
    (disposable / A.KNOWLEDGE / observation_file).write_bytes(snapshot.encode(updated['observations'][observation_file]))
    after = A.candidate(disposable)
    A.require(after == A.candidate(disposable), 'Nondeterministic progress candidate')
    A.require(before['global-reference.json'] == after['global-reference.json'], 'Global reference changed')
    for label, outputs in (('baseline', before), ('candidate', after)):
        folder = disposable / label
        for name, payload in outputs.items():
            p = folder / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(payload)
    def counts(outputs):
        rows = json.loads(outputs['model.json'])['progress']
        return {'learned': sum(r['is_learned'] is True for r in rows),
                'verified': sum(r['is_verified'] is True for r in rows)}
    report = {'status': 'PREVIEW_ONLY', 'disposable_root': str(disposable),
              'candidate_path': str(disposable / 'candidate'), 'semantic_diff': semantic,
              'before': counts(before), 'after': counts(after),
              'candidate_production_fingerprint': A.digest(A.inventory(after, A.PRODUCTION + '/')),
              'global_reference_equal': True, 'state_unchanged': A.bound_tree(disposable, A.STATE) == A.bound_tree(source, A.STATE),
              'production_files_changed': [n for n in sorted(after) if before[n] != after[n]],
              'real_writes': False, 'state_migration': False}
    (disposable / 'preview-report.json').write_bytes(snapshot.encode(report))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT, help='Read-only pipeline input root')
    parser.add_argument('--observation', type=Path, required=True, help='Sanitized observation/provenance JSON envelope')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        report = preview(args.source, json.loads(args.observation.read_text()))
    except (ValueError, KeyError, TypeError) as error:
        parser.exit(2, str(error) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
