"""Release gates combine magnitude and semantic locality, never pixels alone."""
import math

POLICY = {'affected_category_soft': 64, 'direct_sibling_soft': 32, 'unrelated_without_review': 0,
          'major_normal': 0, 'local_hard': 384, 'tray_growth_soft': 256, 'multi_ancestor_exhaustion': 3}


def impact(data, before, after, changes, events, repacked, checkpoint):
    categories = {f"category:{r['id']}": r for r in data['categories']}
    topics = {r['id']: r for r in data['topics']}
    old_parent = {k: parent for parent, r in checkpoint['categories'].items() for k in r['sibling_order']}
    origins = set()
    for topic in changes['topics']['added']:
        origins.add('category:' + str(topics[topic]['canonical_parent_id']))
    for category in changes['categories']['added']:
        parent = categories[f'category:{category}']['canonical_parent_id']
        if parent is not None: origins.add('category:' + str(parent))
    for category in changes['categories']['removed']:
        if f'category:{category}' in old_parent: origins.add(old_parent[f'category:{category}'])
    for topic in changes['topics']['removed']:
        for k, r in checkpoint['categories'].items():
            if f'topic:{topic}' in r['topic_order']: origins.add(k)
    for key in changes.get('label_changes', []):
        origins.add(key if key.startswith('category:') else 'category:' + str(topics[int(key.split(':')[1])]['canonical_parent_id']))
    expected, ancestors, siblings = set(), set(), set()
    def subtree(key):
        expected.add(key)
        for k, r in categories.items():
            if r['canonical_parent_id'] is not None and 'category:'+str(r['canonical_parent_id']) == key: subtree(k)
    old_nodes = {n['key']: n for n in before['nodes']}
    for origin in origins:
        subtree(origin); key = origin
        while key in categories:
            ancestors.add(key); expected.add(key)
            if old_nodes.get(key, {}).get('depth') == 1: break
            parent = categories[key]['canonical_parent_id']
            if parent is None: break
            key = 'category:' + str(parent)
        parent = categories.get(origin, {}).get('canonical_parent_id')
        siblings |= {k for k, r in categories.items() if r['canonical_parent_id'] == parent and k != origin}
    moves = []
    for n in after['nodes']:
        old = old_nodes.get(n['key'])
        if old and n['key'].startswith('category:'):
            d = math.hypot(n['x']-old['x'], n['y']-old['y'])
            if d > .000001:
                moves.append({'key': n['key'], 'title': categories[n['key']]['title'], 'displacement': round(d, 6),
                              'depth': old['depth'], 'scope': 'expected' if n['key'] in expected else 'direct_sibling' if n['key'] in siblings else 'unrelated'})
    moves.sort(key=lambda r: int(r['key'].split(':')[1]))
    unrelated = [r for r in moves if r['key'] not in expected]
    old_trays = {t['parent']: t for t in before['trays']}
    tray_growth = [{'region': t['parent'], 'height_growth': round(t['height']-old_trays.get(t['parent'], {}).get('height', 0), 6),
                   'width_growth': round(t['width']-old_trays.get(t['parent'], {}).get('width', 0), 6)}
                  for t in after['trays'] if t['parent'] in repacked]
    reasons, outcome = [], 'SAFE_TO_APPLY'
    def review(reason):
        nonlocal outcome
        reasons.append(reason)
        if outcome == 'SAFE_TO_APPLY': outcome = 'REVIEW_REQUIRED'
    def rebalance(reason):
        nonlocal outcome
        reasons.append(reason); outcome = 'REBALANCE_REQUIRED'
    if changes['categories']['added']: review('NEW_CATEGORY: new visual region requires review')
    if changes.get('label_changes'): review('LABEL_CHANGE: measured presentation requires review')
    if unrelated: review('UNEXPECTED_REGION_MOVEMENT')
    if any(r not in expected for r in repacked): review('UNEXPECTED_TRAY_REPACK')
    for r in moves:
        if r['depth'] <= 1: rebalance('MAJOR_ANCHOR_MOVEMENT: ' + r['key'])
        elif r['displacement'] > POLICY['local_hard']: rebalance('LOCAL_HARD_BUDGET: ' + r['key'])
        elif r['scope'] == 'expected' and r['displacement'] > POLICY['affected_category_soft']: review('AFFECTED_SOFT_BUDGET: ' + r['key'])
        elif r['scope'] == 'direct_sibling' and r['displacement'] > POLICY['direct_sibling_soft']: review('SIBLING_SOFT_BUDGET: ' + r['key'])
    if any(max(t['height_growth'], t['width_growth']) > POLICY['tray_growth_soft'] for t in tray_growth): review('LARGE_LOCAL_TRAY_GROWTH')
    exhausted = sorted({e['region'] for e in events if e.get('required_width', 0) > e.get('available_width', float('inf'))})
    if len(exhausted) >= POLICY['multi_ancestor_exhaustion']: rebalance('MULTI_ANCESTOR_RESERVE_EXHAUSTION')
    def path(key):
        parts=[]
        while key in categories:
            parts.append(categories[key]['title']);parent=categories[key]['canonical_parent_id']
            if parent is None:break
            key='category:'+str(parent)
        return ' > '.join(reversed(parts))
    return {'origins': sorted(origins), 'origin_titles': [path(k) for k in sorted(origins)],
            'expected_affected_ancestors': sorted(ancestors), 'expected_regions': sorted(expected),
            'moved_categories': moves, 'unrelated_moved_categories': unrelated,
            'repacked_trays': sorted(repacked), 'tray_growth': tray_growth,
            'escalation_level': max((e['level'] for e in events), default=0),
            'exhausted_regions': exhausted, 'policy': POLICY, 'outcome': outcome, 'reasons': sorted(set(reasons))}
