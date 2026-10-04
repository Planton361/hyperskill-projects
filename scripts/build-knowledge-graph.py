#!/usr/bin/env python3
"""Offline validation and deterministic graph/preview generation. No network I/O."""
import argparse
import html
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from knowledge_atlas.observations import load as load_observations

TABLES = ('courses', 'categories', 'topics', 'projects', 'stages', 'edges', 'progress', 'evidence')
TYPES = {'courses': 'course', 'categories': 'category', 'topics': 'topic', 'projects': 'project', 'stages': 'stage'}
COLORS = {'course': '#c9afff', 'category': '#818da9', 'unknown': '#647087', 'not_learned': '#647087', 'learned': '#79dcb4', 'completed': '#79dcb4', 'active': '#efbb79', 'available': '#9aa8ed'}

def load(root):
    data = {name: json.loads((root / 'data/knowledge' / (name + '.json')).read_text()) for name in TABLES}
    data['observations'], data['catalog_observations'] = load_observations(root/'data/knowledge/observations')
    return data

def validate(data):
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    evidence = {e['id']: e for e in data['evidence']}
    entities = {}
    for table, kind in TYPES.items():
        rows = data[table]
        require(len({x['id'] for x in rows}) == len(rows), f'duplicate IDs: {table}')
        for row in rows:
            require(isinstance(row['id'], int), f'non-numeric Hyperskill ID: {table}')
            entities[f"{kind}:{row['id']}"] = row
    require(len(evidence) == len(data['evidence']), 'duplicate evidence IDs')
    def check_evidence(row):
        refs = row.get('evidence_ids', [])
        require(bool(refs) and all(x in evidence for x in refs), 'missing evidence')
    for row in entities.values():
        check_evidence(row)
    require(len({e['id'] for e in data['edges']}) == len(data['edges']), 'duplicate edge IDs')
    signatures = set()
    for edge in data['edges']:
        kind, source, target = edge['type'], edge['source'], edge['target']
        require(source in entities and target in entities, 'dangling edge')
        check_evidence(edge)
        require(all(evidence[e]['confidence'] == 'explicit' for e in edge['evidence_ids']), 'non-explicit edge')
        require(kind in ('hierarchy', 'prerequisite', 'dependent', 'project_requires', 'project_applies', 'course_contains'), 'unknown relation')
        signature = (kind, source, target, edge.get('stage_id'))
        require(signature not in signatures, 'duplicate relationship')
        signatures.add(signature)
        if kind in ('project_requires', 'project_applies'):
            require(source.startswith('project:') and target.startswith('topic:'), 'invalid project relation endpoints')
        if kind in ('prerequisite', 'dependent'):
            require(source.startswith('topic:') and target.startswith('topic:'), 'invalid topic relation endpoints')
        if kind == 'hierarchy':
            require(source.startswith('category:') and target.split(':')[0] in ('category','topic'), 'invalid hierarchy')
        if kind == 'project_applies':
            require(any(evidence[e].get('assertion') == {'type': kind, 'source': source, 'target': target} for e in edge['evidence_ids']), 'project_applies needs a matching explicit application assertion')
        if 'stage_id' in edge:
            stage = entities.get(f"stage:{edge['stage_id']}")
            require(stage is not None and source == f"project:{stage['project_id']}", 'invalid edge stage')
            if kind == 'project_requires':
                require(int(target.split(':')[1]) in stage['required_topic_ids'], 'stage does not require target')
    for course in data['courses']:
        for field, kind in [('topic_ids','topic'),('category_ids','category'),('project_ids','project')]:
            ids = course[field]
            require(len(ids) == len(set(ids)), f'duplicate course {field}')
            require(all(f'{kind}:{i}' in entities for i in ids), f'unknown course {field}')
        require(len(course['topic_ids']) == course['topics_count'], 'course count mismatch')
    for stage in data['stages']:
        require(f"project:{stage['project_id']}" in entities, 'missing stage project')
        for field in ('required_topic_ids','cumulative_required_topic_ids'):
            require(all(f'topic:{i}' in entities for i in stage[field]), 'missing stage topic')
    p = data['progress']
    for snapshot in data.get('observations', {}).values():
        course = entities.get(f"course:{snapshot['course_id']}")
        require(course is not None, 'unknown observation course')
        rows = snapshot['topics']
        ids = [r['topic_id'] for r in rows]
        require(len(ids) == len(set(ids)) and set(ids) == set(course['topic_ids']), 'observation coverage mismatch')
        require(all(type(r['is_learned']) is bool and type(r['is_skipped']) is bool for r in rows), 'invalid observation booleans')
        learned = sorted(r['topic_id'] for r in rows if r['is_learned'])
        require(snapshot['learned_topic_ids'] == learned and len(learned) == snapshot['learned_topics_count'], 'observation learned mismatch')
        require(sum(r['is_skipped'] for r in rows) == snapshot['skipped_topics_count'], 'observation skipped mismatch')
    for table, kind in [('courses','course'),('topics','topic'),('projects','project')]:
        require(len({x[kind+'_id'] for x in p[table]}) == len(p[table]), 'duplicate progress')
        for item in p[table]:
            require(f"{kind}:{item[kind+'_id']}" in entities, 'unknown progress entity')
            check_evidence(item)
    for item in p['topics']:
        require(type(item.get('is_learned')) is bool, 'non-boolean learned status')
        require(type(item.get('is_skipped')) is bool, 'non-boolean skipped status')
        expected_verified = None if item.get('verification_status') is None else item['verification_status'] == 'verified'
        require(item.get('is_verified') is expected_verified, 'verification status mismatch')
        for ref in item['evidence_ids']:
            filename = evidence[ref].get('snapshot_file')
            if filename:
                snapshot = data.get('observations', {}).get(filename)
                require(snapshot is not None, 'missing observation snapshot')
                matches = [t for t in snapshot['topics'] if t['topic_id'] == item['topic_id']]
                require(len(matches) == 1, 'missing or duplicate observation topic')
                require(snapshot['course_id'] == item['course_id'], 'observation course mismatch')
                require(item.get('observed_at') == snapshot['observed_at'], 'observation timestamp mismatch')
                require(all(item.get(k) == matches[0].get(k) for k in ('is_learned','is_skipped','is_completed','verification_status')), 'status disagrees with observation')
        if item.get('is_applied') is True:
            assertion = {'type':'topic_applied','topic_id':item['topic_id']}
            require(any(evidence[e].get('assertion') == assertion for e in item['evidence_ids']), 'unproven applied topic')
    for item in p['courses']:
        course = entities[f"course:{item['course_id']}"]
        for field, total in [('learned_topics_count','learned_topics_total'),('applied_topics_count','applied_topics_total')]:
            require(0 <= item[field] <= item[total], 'invalid progress counts')
        require(item['learned_topics_total'] == course['topics_count'] and item['applied_topics_total'] == course['capstone_topics_count'], 'progress denominator mismatch')
        for field, count, status in [('learned_topic_ids','learned_topics_count','is_learned'),('applied_topic_ids','applied_topics_count','is_applied')]:
            if item[field] is not None:
                require(len(set(item[field])) == len(item[field]) == item[count], 'incomplete full status set')
                explicit = {t['topic_id'] for t in p['topics'] if t.get(status) is True and t['course_id'] == item['course_id']}
                require(set(item[field]) == explicit, 'unproven full status set')
        if item.get('topic_status_coverage') == 'complete':
            rows = [t for t in p['topics'] if t['course_id'] == item['course_id']]
            require({t['topic_id'] for t in rows} == set(course['topic_ids']), 'incomplete topic coverage')
            require(sum(t['is_learned'] for t in rows) == item['learned_topics_count'], 'learned count mismatch')
            require(sum(t['is_skipped'] for t in rows) == item['skipped_topics_count'], 'skipped count mismatch')
            verified = sorted(t['topic_id'] for t in rows if t['is_verified'] is True)
            require(item.get('verified_topic_ids') == verified, 'verified IDs mismatch')
            for t in rows:
                require(any(evidence[e].get('snapshot_file') for e in t['evidence_ids']), 'complete status needs observation evidence')
    targets = {e['target'] for e in data['edges'] if e['type'] == 'project_requires' and e['source'] == 'project:113'}
    require(len(targets) == 26, 'project 113 must have 26 distinct required topics')
    active = next(x for x in p['projects'] if x['project_id'] == 380)
    require(active['completed_stage_ids'] == [], 'project 380 has no completed-stage evidence')
    return entities

def layout(nodes, links):
    """Seeded, fixed-step force layout; positions are presentation, never evidence."""
    n = len(nodes)
    points = [[math.cos(i*2.399963)*math.sqrt(i+1)*25, math.sin(i*2.399963)*math.sqrt(i+1)*25] for i in range(n)]
    index = {node['id']:i for i,node in enumerate(nodes)}
    pairs = sorted({tuple(sorted((index[e['source']], index[e['target']]))) for e in links})
    for step in range(220):
        forces = [[-x*.008,-y*.008] for x,y in points]
        for i in range(n):
            for j in range(i):
                dx,dy=points[i][0]-points[j][0],points[i][1]-points[j][1]
                dist=max(dx*dx+dy*dy,36)
                strength=350/dist
                fx,fy=dx*strength,dy*strength
                forces[i][0]+=fx; forces[i][1]+=fy
                forces[j][0]-=fx; forces[j][1]-=fy
        for i,j in pairs:
            dx,dy=points[j][0]-points[i][0],points[j][1]-points[i][1]
            distance=max(math.hypot(dx,dy),1)
            strength=(distance-64)*.025/distance
            fx,fy=dx*strength,dy*strength
            forces[i][0]+=fx; forces[i][1]+=fy
            forces[j][0]-=fx; forces[j][1]-=fy
        cooling=.6*(1-step/240)
        for i,(fx,fy) in enumerate(forces):
            points[i][0]+=max(-12,min(12,fx))*cooling
            points[i][1]+=max(-12,min(12,fy))*cooling
    for node,(x,y) in zip(nodes,points):
        node.update(x=round(x,3),y=round(y,3))

def build(data):
    validate(data)
    topic_progress={x['topic_id']:x for x in data['progress']['topics']}
    project_progress={x['project_id']:x for x in data['progress']['projects']}
    nodes=[]
    for table,kind in TYPES.items():
        if kind == 'stage':
            continue
        for row in data[table]:
            node=dict(id=f"{kind}:{row['id']}",hyperskill_id=row['id'],type=kind,title=row['title'],url=row['url'],evidence_ids=row['evidence_ids'])
            if kind == 'topic':
                p=topic_progress.get(row['id'],{})
                status = 'learned' if p.get('is_learned') is True else 'not_learned' if p.get('is_learned') is False else 'unknown'
                node.update(status=status, verified=p.get('is_verified'), verification_status=p.get('verification_status'), applied=p.get('is_applied'), progress_evidence_ids=p.get('evidence_ids',[]))
            if kind == 'project':
                p=project_progress.get(row['id'],{})
                node.update(status=p.get('status','available'), progress_evidence_ids=p.get('evidence_ids',[]))
                node['required_topics_count']=len({e['target'] for e in data['edges'] if e['source']==node['id'] and e['type']=='project_requires'}) if row['id']==113 else None
                node['completed_stage_ids']=p.get('completed_stage_ids')
            nodes.append(node)
    nodes.sort(key=lambda x:x['id'])
    links=sorted(data['edges'],key=lambda x:x['id'])
    layout(nodes,links)
    return dict(schema_version=1,snapshot_date='2026-10-01',nodes=nodes,edges=links,progress=data['progress'],evidence=data['evidence'],coverage=dict(course_topics='complete',topic_progress=data['progress']['courses'][0]['topic_status_coverage'],project_requirements=[113],project_applies='unknown'))

def color(node):
    return COLORS[node.get('status',node['type'])]

def preview(graph):
    nodes=graph['nodes']; by_id={n['id']:n for n in nodes}
    lowx=min(n['x'] for n in nodes); highx=max(n['x'] for n in nodes)
    lowy=min(n['y'] for n in nodes); highy=max(n['y'] for n in nodes)
    scale=min(820/(highx-lowx),430/(highy-lowy))
    pos={n['id']:(450+(n['x']-(lowx+highx)/2)*scale,350+(n['y']-(lowy+highy)/2)*scale) for n in nodes}
    p=graph['progress']['courses'][0]
    learned=sum(n.get('status')=='learned' for n in nodes)
    verified=sum(n.get('verified') is True for n in nodes)
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="660" viewBox="0 0 1200 660" role="img" aria-labelledby="title desc">', '<title id="title">Introduction to Java — personal knowledge graph</title>', f'<desc id="desc">89 course topics. {learned} explicitly learned topics, including {verified} with verified status. Project 113 requires 26 topics; their applied status is unknown. Aggregate progress: 31 of 89 learned, 26 of 85 applied.</desc>', '<rect width="1200" height="660" fill="#101319"/>', '<g font-family="system-ui,sans-serif" fill="#e4e8f1">', '<text x="38" y="43" font-size="13" fill="#98a5bc" letter-spacing="3">PERSONAL KNOWLEDGE / COURSE 08</text>', '<text x="38" y="85" font-size="30">Introduction to Java</text>', f'<text x="38" y="115" font-size="15" fill="#aeb9cc">{p["learned_topics_count"]} / {p["learned_topics_total"]} learned · {p["applied_topics_count"]} / {p["applied_topics_total"]} applied — aggregate only</text>']
    drawn=set()
    for edge in graph['edges']:
        pair=(edge['source'],edge['target'])
        if pair in drawn: continue
        drawn.add(pair)
        x1,y1=pos[pair[0]];x2,y2=pos[pair[1]]
        stroke='#79dcb4' if edge['type']=='project_requires' else '#65728a'
        parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke}" stroke-opacity=".24"/>')
    for node in nodes:
        x,y=pos[node['id']];c=color(node);r=4 if node['type']=='topic' else 5
        title=html.escape(node['title'])
        fill='#101319' if node['type']=='category' or node.get('status')=='available' else c
        if node['type']=='course':
            parts.append(f'<path d="M{x:.2f},{y-7:.2f} l6,7 -6,7 -6,-7 Z" fill="{c}"><title>{title}</title></path>')
        elif node['type']=='project':
            parts.append(f'<rect x="{x-5:.2f}" y="{y-5:.2f}" width="10" height="10" rx="2" fill="{fill}" stroke="{c}"><title>{title}</title></rect>')
        else:
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" stroke="{c}"><title>{title}</title></circle>')
    parts.extend(['<text x="905" y="225" font-size="13" fill="#79dcb4">COMPLETED PROJECT</text>','<text x="905" y="257" font-size="18">Simple Chat Bot</text>','<text x="905" y="282" font-size="18">with Java</text>','<text x="905" y="322" font-size="15">26 required topics</text>','<text x="905" y="348" font-size="13" fill="#aeb9cc">project_requires ≠ project_applies</text>',f'<text x="905" y="401" font-size="14" fill="#79dcb4">● Learned ({verified} verified)</text>','<text x="905" y="429" font-size="14" fill="#aeb9cc">● Not learned / unknown</text>','<text x="905" y="457" font-size="14" fill="#efbb79">■ Active project</text>','<text x="905" y="485" font-size="14" fill="#9aa8ed">■ Available project</text>','<text x="38" y="620" font-size="14" fill="#aeb9cc">COURSE ROADMAP · 89 topics · 46 categories · complete Learned status · Applied unknown · snapshot 2026-10-01</text>','</g></svg>'])
    return '\n'.join(parts)+'\n'

def render(root, check=False):
    graph=build(load(root))
    outputs={'graph.json':json.dumps(graph,indent=2,ensure_ascii=False,sort_keys=True)+'\n','preview.svg':preview(graph)}
    dest=root/'docs/knowledge-graph'
    if not check: dest.mkdir(parents=True,exist_ok=True)
    for name,text in outputs.items():
        path=dest/name
        if check:
            if not path.exists() or path.read_text()!=text:
                raise ValueError(f'stale generated file: {path}')
        else: path.write_text(text)
    print(f"Validated {len(graph['nodes'])} nodes and {len(graph['edges'])} evidence-backed edges; deterministic outputs {'checked' if check else 'written'}.")

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    render(args.root,args.check)
