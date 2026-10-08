"""Typed dispatch; legacy progress observations keep their original representation."""
import json
import os
import tempfile
from pathlib import Path
from .catalog_observation import validate_observation

CATALOG_TYPES = ('global_knowledge_catalog', 'scope_relations_catalog',
                 'course_project_associations_catalog')


def validate_catalog_observation(row):
    kind = row.get("observation_type")
    if kind == "global_knowledge_catalog":
        return validate_observation(row)
    if kind == "scope_relations_catalog":
        from .scope_relations import validate_observation as validate_relations
        return validate_relations(row)
    if kind == "course_project_associations_catalog":
        from .course_project_associations import validate_observation as validate_associations
        return validate_associations(row)
    raise ValueError("Unsupported catalog observation type")


def load(path):
    personal, catalog = {}, {}
    for p in sorted(Path(path).glob('*.json')):
        row = json.loads(p.read_text())
        kind = row.get('observation_type', 'personal_progress')
        key = 'observations/' + p.name
        if kind in CATALOG_TYPES:
            validate_catalog_observation(row)
            catalog[key] = row
        elif kind == 'personal_progress':
            personal[key] = row
        else:
            raise ValueError('Unsupported observation type')
    return personal, catalog


def write_immutable_catalog(folder, observation, prefix):
    """Publish reviewed catalog bytes atomically; competing inventories fail closed."""
    from .snapshot import encode
    from .catalog_observation import require
    import hashlib
    validate_catalog_observation(observation)
    body = encode(observation)
    digest = hashlib.sha256(body).hexdigest()
    folder = Path(folder)
    for existing in folder.glob('*.json'):
        old = json.loads(existing.read_bytes())
        if old.get('observation_type') == observation['observation_type']:
            require(existing.read_bytes() == body, 'Conflicting immutable catalog observation')
            return existing, False
    path = folder / (prefix + '-' + observation['captured_at_end'][:10] + '-' + digest[:12] + '.json')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=folder, prefix='.catalog-write-', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(body); stream.flush(); os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            require(path.read_bytes() == body, 'Conflicting immutable observation bytes')
            return path, False
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path, True
