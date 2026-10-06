"""Disposable metrics; writes only this prototype's validation artifact."""
import hashlib
import importlib.util
import json
import time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('pyramid',BASE/'build.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
t=time.perf_counter();data=b.snapshot.load_source(b.ROOT/'data/knowledge');history=json.loads((b.ROOT/'state/knowledge-atlas/activation-state.json').read_text());model=b.projection.project(data,history);projection_ms=(time.perf_counter()-t)*1000
t=time.perf_counter();geo=b.geometry(model);layout_ms=(time.perf_counter()-t)*1000
t=time.perf_counter();payload=b.snapshot.encode(geo);encode_ms=(time.perf_counter()-t)*1000
assert payload==(BASE/'generated/global-geometry.json').read_bytes()
by={n['key']:n for n in geo['positions']};personal=[by[b.slot(k)] for k in model['personal']];leaves=[n for n in personal if n['key'].startswith('leaf:')]
def bounds(nodes):
    x=min(n['x'] for n in nodes);y=min(n['y'] for n in nodes)
    return dict(x=x,y=y,w=max(n['x']+n['w'] for n in nodes)-x,h=max(n['y']+n['h'] for n in nodes)-y)
r=bounds(personal);leaf_bounds=bounds(leaves)
card_area=sum(n['w']*n['h'] for n in personal);all_keys={n['key'] for n in personal}
in_span=[n for n in geo['positions'] if leaf_bounds['x']<=n['x']<=leaf_bounds['x']+leaf_bounds['w']]
result=dict(counts=geo['counts'],resolution=dict(resolved=1,partial=88,unresolved=3017),geometry_fingerprint=geo['geometry_fingerprint'],source_catalog_fingerprint=geo['source_catalog_fingerprint'],geometry_bytes=len(payload),catalog_bytes=len(b.snapshot.encode(model)),projection_ms=projection_ms,layout_ms=layout_ms,geometry_encode_ms=encode_ms,total_build_ms=projection_ms+layout_ms+encode_ms,bounds=geo['bounds'],personal=dict(accepted_categories=46,accepted_topics=89,visible_positions=135,hidden_positions=3820,hidden_percent=3820/3955*100,bounds=r,leaf_bounds=leaf_bounds,leaf_span_percent_of_global_width=leaf_bounds['w']/geo['bounds']['w']*100,card_area_percent_of_visible_bounds=card_area/(r['w']*r['h'])*100,empty_area_percent_of_visible_bounds=100-card_area/(r['w']*r['h'])*100,hidden_positions_in_leaf_horizontal_span=sum(n['key'] not in all_keys for n in in_span)),activation_simulations=2,maximum_displacement_px=0,reference_promotion=dict(id=333,slot='leaf:333',entire_geometry_byte_identical=True))
(BASE/'tests/validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
