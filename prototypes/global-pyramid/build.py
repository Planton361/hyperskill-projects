#!/usr/bin/env python3
"""Taxonomy-only master geometry; existing Catalog projection supplies semantics."""
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
spec = importlib.util.spec_from_file_location('global_projection', ROOT/'prototypes/global-atlas/build.py')
projection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(projection)
snapshot = projection.snapshot

def slot(key):
    return key if key.startswith('category:') else 'leaf:'+key.split(':')[1]

def legacy_geometry(model):
    # No title, resolution, accepted canonical parent, Course, Project or progress input.
    parents = {slot(n['key']): sorted(n['parents'], key=lambda k:int(k.split(':')[1])) for n in model['entities']}
    order = lambda k: (0 if k.startswith('category:') else 1, int(k.split(':')[1]))
    def category_depth(k):
        ps=parents[k]
        return 0 if not ps else 1+max(category_depth(p) for p in ps)
    primary={k:min(ps,key=lambda p:(-category_depth(p),int(p.split(':')[1]))) if ps else None for k,ps in parents.items()}
    children = {k: [] for k in parents}
    for key, ps in parents.items():
        if ps: children[primary[key]].append(key)
    for cs in children.values(): cs.sort(key=order)
    roots = sorted(model['roots'], key=order)
    plans = {}
    def measure(key):
        cats = [k for k in children[key] if k.startswith('category:')]
        leaves = [k for k in children[key] if k.startswith('leaf:')]
        for c in cats: measure(c)
        widths = ([260] if leaves else []) + [plans[c][0] for c in cats]
        w = max(300, sum(widths)+64*max(0,len(widths)-1))
        gap = max(160, w//8)
        h = max(80, gap+max([len(leaves)*40]+[plans[c][1] for c in cats]))
        plans[key] = (w,h,cats,leaves)
    for r in roots: measure(r)
    positions = {}
    def place(key,x,y,depth,root):
        w,h,cats,leaves = plans[key]
        gap=max(160,w//8)
        positions[key] = dict(key=key,x=x+(w-280)//2,y=y,w=280,h=80,depth=depth,root=root,
            parents=parents[key],primary_parent=primary[key],
            secondary_memberships=[p for p in parents[key] if p!=primary[key]],sibling_order=leaves+cats,region=dict(x=x,y=y,w=w,h=h))
        widths = ([260] if leaves else [])+[plans[c][0] for c in cats]
        cursor = x+(w-sum(widths)-64*max(0,len(widths)-1))//2
        for i,k in enumerate(leaves):
            positions[k] = dict(key=k,x=cursor+10,y=y+gap+i*40,w=240,h=32,depth=depth+1,root=root,
                parents=parents[k],primary_parent=key,secondary_memberships=[p for p in parents[k] if p!=key],sibling_order=[])
        if leaves: cursor += 324
        for c in cats:
            place(c,cursor,y+gap,depth+1,root);cursor+=plans[c][0]+64
    sectors=[];cursor=0
    for r in roots:
        w,h,*_=plans[r];place(r,cursor,240,0,r)
        sectors.append(dict(root=r,x=cursor,y=240,w=w,h=h));cursor+=w+800
    total=cursor-800
    anchor=dict(key='presentation:hyperskill',x=(total-400)//2,y=0,w=400,h=80)
    routes=[]
    for k,n in sorted(positions.items()):
        p=positions.get(n['primary_parent'],anchor)
        # Leaves use a tray-side rail so connectors cannot run through earlier rows.
        a=[p['x']+p['w']//2,p['y']+p['h']];b=[n['x']+n['w']//2,n['y']]
        points=[a,[a[0],a[1]+40],[b[0],a[1]+40],b]
        if k.startswith('leaf:'):
            rail=n['x']-8;points=[a,[a[0],a[1]+40],[rail,a[1]+40],[rail,n['y']+16],[n['x'],n['y']+16]]
        routes.append(dict(parent=n['primary_parent'] or anchor['key'],child=k,points=points))
    source=dict(roots=roots,parents=parents)
    digest=lambda v:hashlib.sha256(snapshot.encode(v)).hexdigest()
    result=dict(geometry_schema_version=1,layout_algorithm_version='canonical-pyramid-a-1',
        source_catalog_fingerprint=digest(source),presentation_super_root=anchor,root_sectors=sectors,
        positions=[positions[k] for k in sorted(positions)],hierarchy_routes=routes,
        bounds=dict(x=0,y=0,w=total,h=max(s['y']+s['h'] for s in sectors)),
        identity_strategy='category:<id>; reference:<id> and topic:<id> both map to leaf:<id>',
        leaf_identity_mapping=[dict(structural_id=int(k.split(':')[1]),slot=k,semantic_aliases=['reference:'+k.split(':')[1],'topic:'+k.split(':')[1]]) for k in sorted(positions) if k.startswith('leaf:')],
        primary_parent_rule='deepest structural Category parent, then lowest numeric Category ID; independent of semantic canonical parent',
        counts=dict(categories=sum(k.startswith('category:') for k in positions),structural_leaves=sum(k.startswith('leaf:') for k in positions),positions=len(positions),hierarchy_pairs=len(model['hierarchy'])))
    result['geometry_fingerprint']=digest(result)
    return result

# Explicit presentation order, independent of numeric IDs and semantic titles.
ROOT_ORDER = ('category:1162', 'category:525', 'category:2148', 'category:3051', 'category:4055')
MIN_SECTOR_WIDTH = 48000
SECTOR_GAP = 4000
REFERENCE_HASH = '9671e7ca5517c1f35e5ee3affac066362a2470d04ef6251cbe2faa6024572c44'

def geometry(model):
    """Compose frozen local blocks; never rerun internal subtree placement."""
    from copy import deepcopy
    raw = (BASE/'root-layout/previous-global-geometry.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REFERENCE_HASH, 'Local geometry reference changed'
    previous = json.loads(raw)
    original = {n['key']: n for n in previous['positions']}
    parents = {slot(n['key']): sorted(n['parents'], key=lambda k: int(k.split(':')[1])) for n in model['entities']}
    assert parents == {k: n['parents'] for k,n in original.items()}, 'Structural change requires a separate layout review'
    assert set(model['roots']) == set(ROOT_ORDER), 'Unexpected root inventory'
    sectors = {s['root']: s for s in previous['root_sectors']}
    total = sum(max(sectors[r]['w'], MIN_SECTOR_WIDTH) for r in ROOT_ORDER) + SECTOR_GAP * 4
    baseline = total // 10  # One tenth of world width for the presentation apex/corridor.
    positions = deepcopy(previous['positions'])
    result = deepcopy(previous)
    result.pop('geometry_fingerprint')
    result['root_sectors'] = []
    translations = {}
    cursor = 0
    for root in ROOT_ORDER:
        old = sectors[root]
        width = max(old['w'], MIN_SECTOR_WIDTH)
        dx = cursor + (width-old['w'])//2 - old['x']
        dy = baseline - original[root]['y']
        translations[root] = (dx, dy)
        local = dict(x=old['x']+dx, y=old['y']+dy, w=old['w'], h=old['h'])
        # Reserved presentation area: padded sectors are not Category regions/facts.
        result['root_sectors'].append(dict(root=root, x=cursor, y=baseline, w=width,
            h=max(old['h'], MIN_SECTOR_WIDTH//4), subtree_bounds=local))
        cursor += width + SECTOR_GAP
    for n in positions:
        dx,dy = translations[n['root']]
        n['x'] += dx; n['y'] += dy
        if 'region' in n:
            n['region']['x'] += dx; n['region']['y'] += dy
    anchor = dict(key='presentation:hyperskill', x=(total-400)//2, y=0, w=400, h=80, depth=-1)
    by = {n['key']: n for n in positions}
    routes = deepcopy(previous['hierarchy_routes'])
    for route in routes:
        n = by[route['child']]
        if route['parent'] == anchor['key']:
            a = [anchor['x']+anchor['w']//2, anchor['y']+anchor['h']]
            b = [n['x']+n['w']//2, n['y']]
            bus = baseline//4
            route['points'] = [a, [a[0],bus], [b[0],bus], b]
        else:
            dx,dy = translations[n['root']]
            route['points'] = [[x+dx,y+dy] for x,y in route['points']]
    result.update(layout_algorithm_version='canonical-pyramid-a-2-root-composition',
        positions=positions, hierarchy_routes=routes, presentation_super_root=anchor,
        bounds=dict(x=0,y=0,w=total,h=max(s['y']+s['h'] for s in result['root_sectors'])),
        root_composition=dict(version=1, root_order=list(ROOT_ORDER),
            minimum_sector_width=MIN_SECTOR_WIDTH, sector_gap=SECTOR_GAP,
            minimum_sector_height=MIN_SECTOR_WIDTH//4, root_baseline=baseline,
            reference_geometry_fingerprint=previous['geometry_fingerprint'],
            policy='Rigid subtree translation; unscaled cards; presentation padding only'))
    result['geometry_fingerprint'] = hashlib.sha256(snapshot.encode(result)).hexdigest()
    return result

def encoded():
    model=projection.project(snapshot.load_source(ROOT/'data/knowledge'),json.loads((ROOT/'state/knowledge-atlas/activation-state.json').read_text()))
    return snapshot.encode(model),snapshot.encode(geometry(model))

if __name__=='__main__':
    start=time.perf_counter();model,geo=encoded()
    for name,payload in [('catalog.json',model),('global-geometry.json',geo)]:
        target=BASE/'generated'/name
        if '--check' in sys.argv: assert target.read_bytes()==payload
        else: target.write_bytes(payload)
    print(json.dumps(dict(build_layout_ms=(time.perf_counter()-start)*1000,catalog_bytes=len(model),geometry_bytes=len(geo))))
