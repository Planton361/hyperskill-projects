"""Read-only semantic build into one isolated dual-view preview. Never publishes State."""
import hashlib
import json
from pathlib import Path
from . import catalog_projection, snapshot, validate
from .catalog import active_projection
from .architecture import DECISION, PRODUCTION_MIGRATION

TARGET = 'docs/knowledge-map-adaptive-preview'


def artifacts(root):
    root = Path(root)
    loaded = snapshot.load_source(root/'data/knowledge')
    validate.validate(active_projection(loaded))
    history = json.loads((root/'state/knowledge-atlas/activation-state.json').read_bytes())
    raw = catalog_projection.project(loaded, history)
    master_bytes = (root/'prototypes/global-pyramid/generated/global-geometry.json').read_bytes()
    master = json.loads(master_bytes)
    # Match the current Catalog's structural IDs and all memberships. No layout build.
    slots = {r['key']: r for r in master['positions']}
    expected = {r['key'] if r['kind']=='category' else 'leaf:'+str(r['id']): sorted(r['parents']) for r in raw['entities']}
    if expected != {k: sorted(r['parents']) for k,r in slots.items()}:
        raise ValueError('GLOBAL_REFERENCE_STRUCTURE_CHANGED: separate reference review required')
    runtime = Path(__file__).parent/'adaptive_runtime'
    out = {p.relative_to(runtime).as_posix():p.read_bytes() for p in runtime.rglob('*') if p.is_file()}
    for name, source in [('atlas.js','canonical_runtime/atlas.js'),('labels.js','canonical_runtime/labels.js'),('ux.js','canonical_runtime/ux.js'),('adaptive.cjs','presentation/adaptive.cjs'),('registry.cjs','presentation/registry.cjs'),('views.cjs','presentation/views.cjs')]:
        out[name] = (Path(__file__).parent/source).read_bytes()
    for name in ['d3-flextree-2.1.2.cjs','d3-flextree-LICENSE','d3-hierarchy-LICENSE']:
        out['vendor/'+name] = (root/'prototypes/adaptive-pyramid/vendor'/name).read_bytes()
    raw['presentation_contract'] = DECISION
    raw['source_hashes'] = {t:snapshot.digest(loaded[t]) for t in snapshot.TABLES}
    out['model.json'] = snapshot.encode(raw)
    out['global-reference.json'] = master_bytes
    out['preview-manifest.json'] = snapshot.encode(dict(contract=DECISION,target='non-production-preview',production_migration=PRODUCTION_MIGRATION,
        global_reference_sha256=hashlib.sha256(master_bytes).hexdigest(),local_geometry_storage='derived-memory-only',
        assets={n:hashlib.sha256(v).hexdigest() for n,v in sorted(out.items())}))
    return out


def run(root, check=False):
    root=Path(root).resolve();destination=root/TARGET
    outputs=artifacts(root)
    if destination.is_symlink():raise ValueError('Preview destination symlink refused')
    if destination.exists():
        manifest=destination/'preview-manifest.json'
        if not manifest.is_file():raise ValueError('Refusing unmanaged preview destination')
        previous=json.loads(manifest.read_bytes())
        actual={p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
        if actual != set(previous['assets'])|{'preview-manifest.json'}:raise ValueError('Unmanaged preview files')
        if any(hashlib.sha256((destination/n).read_bytes()).hexdigest()!=h for n,h in previous['assets'].items()):raise ValueError('Edited managed preview; preserve changes before regeneration')
    if check:
        if not destination.exists() or any(not (destination/n).is_file() or (destination/n).read_bytes()!=v for n,v in outputs.items()):raise ValueError('Adaptive preview out of date')
    else:
        destination.mkdir(exist_ok=True)
        for n,v in outputs.items():
            p=destination/n;p.parent.mkdir(parents=True,exist_ok=True)
            if not p.exists() or p.read_bytes()!=v:p.write_bytes(v)
    return dict(status='SAFE_TO_BUILD_PREVIEW',applied=False,preview_written=not check,production_migration=PRODUCTION_MIGRATION,target=TARGET,contract=DECISION,
                counts=raw_counts(outputs),global_reference_sha256=hashlib.sha256(outputs['global-reference.json']).hexdigest())


def raw_counts(outputs):
    raw=json.loads(outputs['model.json'])
    return dict(entities=len(raw['entities']),learned=sum(r['is_learned'] is True for r in raw['progress']),verified=sum(r['is_verified'] is True for r in raw['progress']))
