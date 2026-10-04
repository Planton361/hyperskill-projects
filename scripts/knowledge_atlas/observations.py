"""Typed dispatch; legacy progress observations keep their original representation."""
import json
from pathlib import Path
from .catalog_observation import validate_observation


def load(path):
    personal, catalog = {}, {}
    for p in sorted(Path(path).glob('*.json')):
        row = json.loads(p.read_text())
        kind = row.get('observation_type', 'personal_progress')
        key = 'observations/' + p.name
        if kind == 'global_knowledge_catalog':
            validate_observation(row)
            catalog[key] = row
        elif kind == 'personal_progress':
            personal[key] = row
        else:
            raise ValueError('Unsupported observation type')
    return personal, catalog
