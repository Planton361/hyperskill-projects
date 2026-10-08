"""Read-only compatibility with the immutable, adopted adaptive release."""
import hashlib
import json
from pathlib import Path, PurePosixPath

from . import adaptive_production as A, snapshot
from .catalog import Catalog
from .observations import validate_catalog_observation


MANIFEST = 'prototypes/adaptive-pyramid/production-review/final-v1/apply-manifest.json'
REVIEWED_FINGERPRINT = 'b1597b5ea86c481a855bcc6fe6c5a7f3380300b39262bb8faa0a9b729320a069'


def verify_historical_knowledge_compatibility(historical, current, catalog_observations):
    """Pure check of inventories and the loader's typed catalog collection.

    Historical bytes remain frozen. Extra files default to rejection; only
    direct observation JSON files dispatched as catalog-only may be admitted.
    Validation is reused, never inferred from a filename or a claimed type.
    This verifies compatibility, not permission to overwrite observations.
    """
    for name, sha256 in historical.items():
        A.require(name in current, 'Missing historical Knowledge file: ' + name)
        A.require(current[name] == sha256, 'Changed historical Knowledge file: ' + name)

    additions = sorted(current.keys() - historical.keys())
    directory = PurePosixPath(A.KNOWLEDGE) / 'observations'
    for name in additions:
        path = PurePosixPath(name)
        A.require(path.parent == directory and path.suffix == '.json',
                  'Unexpected additional Knowledge file: ' + name)
        key = path.relative_to(A.KNOWLEDGE).as_posix()
        A.require(key in catalog_observations,
                  'Additional observation is not catalog-only: ' + name)
        validate_catalog_observation(catalog_observations[key])
    return additions


def verify_historic_release(root):
    """Verify the historical package and current active inputs without writes."""
    root = Path(root)
    m = json.loads((root / MANIFEST).read_bytes())
    A.require(A.digest({k: v for k, v in m.items() if k != 'manifest_fingerprint'})
              == m['manifest_fingerprint'] == REVIEWED_FINGERPRINT,
              'Reviewed manifest changed')
    A.pending(root)
    for folder, key in ((A.PRODUCTION, 'target_production'), (A.STATE, 'source_state')):
        A.require(A.bound_tree(root, folder) == m[key], 'Changed inventory: ' + folder)

    # bound_tree also rejects symlinks/non-regular files, including ignored files.
    knowledge = A.bound_tree(root, A.KNOWLEDGE)
    data = snapshot.load_source(root / A.KNOWLEDGE)
    additions = verify_historical_knowledge_compatibility(
        m['source_knowledge']['inventory'], knowledge['inventory'],
        data['catalog_observations'])
    # Validate composition with accepted active identities as well as the schema.
    Catalog(data)

    reference = (root / A.REFERENCE).read_bytes()
    A.require(hashlib.sha256(reference).hexdigest() == m['global_reference_sha256'],
              'Global reference changed')
    A.require(reference == (root / A.PRODUCTION / 'global-reference.json').read_bytes(),
              'Packaged reference changed')
    raw = json.loads((root / A.PRODUCTION / 'model.json').read_bytes())
    A.require(raw['source_hashes']
              == {t: snapshot.digest(data[t]) for t in snapshot.TABLES}
              == m['semantic_invariance']['source_hashes'], 'Semantic inputs changed')
    return {
        'status': 'PASS',
        'production_fingerprint': m['target_production']['fingerprint'],
        'production_inventory_exact': True,
        'state_inventory_exact': True,
        'historical_knowledge_inventory_exact': True,
        'validated_catalog_only_additions': additions,
        'active_semantic_hashes_unchanged': True,
        'state_history_generation_unchanged': True,
        'global_reference_unchanged': True,
    }


def verify_release(root):
    root = Path(root)
    release = root / 'docs/knowledge-map/release-manifest.json'
    if release.is_file() and json.loads(release.read_bytes()).get('edition') == 'myatlas-v6.6':
        from .myatlas_guard import verify_release as verify_v66
        return verify_v66(root)
    return verify_historic_release(root)
