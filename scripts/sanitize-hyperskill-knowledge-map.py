#!/usr/bin/env python3
"""Sanitize a local browser HAR without network access or raw-data logging."""
import argparse
import json
import os
import tempfile
from pathlib import Path
from knowledge_atlas.catalog_observation import sanitize
from knowledge_atlas.snapshot import encode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--write-observation', action='store_true')
    args = parser.parse_args()
    try:
        observation = sanitize(json.loads(args.input.read_text()))
        payload = encode(observation)
        if args.write_observation:
            directory = Path(__file__).resolve().parents[1] / 'data/knowledge/observations'
            destination = directory / ('global-knowledge-map-' + observation['captured_at_start'][:10] + '.json')
            if destination.exists():
                if destination.read_bytes() != payload:
                    raise ValueError('Existing observation differs; preserve history with a separately reviewed snapshot')
            else:
                directory.mkdir(parents=True, exist_ok=True)
                descriptor, temporary = tempfile.mkstemp(dir=directory, prefix='.catalog-', suffix='.tmp')
                try:
                    with os.fdopen(descriptor, 'wb') as f:
                        f.write(payload)
                    os.replace(temporary, destination)
                finally:
                    if Path(temporary).exists():
                        Path(temporary).unlink()
        summary = {**observation['validation'], 'snapshot_status': observation['snapshot_status'],
                   'described_topics': len(observation['topics']),
                   'resolved_topics': sum(t['resolution'] == 'RESOLVED_TOPIC' for t in observation['topics']),
                   'partial_topics': sum(t['resolution'] == 'PARTIAL_TOPIC' for t in observation['topics']),
                   'unresolved_references': len(observation['unresolved_references']),
                   'source_pages': sum(s['path'] == '/api/topic-relations' for s in observation['source_pages']),
                   'reported_total': None, 'written': bool(args.write_observation)}
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        # Even a JSON parsing exception can contain raw body fragments. Never print it.
        print('Sanitization failed: invalid, incomplete, conflicting or unsafe input. No observation written.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
