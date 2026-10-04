"""Layout bridge, exact nonstructural guards and displacement metrics."""
import json
import math
import subprocess
from pathlib import Path
from .classify import STRUCTURAL
from .snapshot import encode


def bridge(runtime, **payload):
    try:
        result = subprocess.run(['node', str(Path(__file__).with_name('layout_bridge.cjs'))],
                                input=json.dumps({'runtime': str(runtime), **payload}), text=True,
                                capture_output=True, timeout=120)
    except subprocess.TimeoutExpired as e:
        raise ValueError('layout/browser validation timed out; no update installed') from e
    if result.returncode:
        raise ValueError('layout bridge failed: ' + result.stderr.strip())
    return json.loads(result.stdout)


def update(runtime, data, cp, geom, diff, rebalance=False, budget=None, active_keys=None):
    if not rebalance and not (set(diff['change_types']) & STRUCTURAL) and not diff.get('label_changes'):
        return {'checkpoint': cp, 'geometry': geom, 'events': [], 'repacked_trays': []}
    return bridge(runtime, action='update', data=data, checkpoint=cp, geometry=geom,
                  diff=diff, rebalance=rebalance,
                  activeKeys=active_keys, budget=budget or {'max': 1e12, 'significant': 100, 'major': 1e12})


def displacement(before, after, kind):
    old = {n['key']: n for n in before['nodes'] if n['key'].startswith(kind + ':')}
    values = sorted(math.hypot(n['x']-old[n['key']]['x'], n['y']-old[n['key']]['y'])
                    for n in after['nodes'] if n['key'] in old)
    def percentile(p):
        if not values: return 0
        at = (len(values)-1)*p
        lo, hi = math.floor(at), math.ceil(at)
        return values[lo] + (values[hi]-values[lo])*(at-lo)
    return {'median': percentile(.5), 'p90': percentile(.9), 'max': max(values, default=0),
            'significant_percentage': 100*sum(v > 1 for v in values)/max(1, len(values)),
            'changed': sum(v > .001 for v in values),
            'affected_nodes': sorted(n['key'] for n in after['nodes'] if n['key'] in old and
                 math.hypot(n['x']-old[n['key']]['x'], n['y']-old[n['key']]['y']) > .001)}


def zero_guard(diff, before_cp, after_cp, before_geom, after_geom):
    if not (set(diff['change_types']) & STRUCTURAL) and not diff.get('label_changes'):
        if encode(before_cp) != encode(after_cp) or encode(before_geom) != encode(after_geom):
            raise ValueError('nonstructural zero-displacement contract violated')
