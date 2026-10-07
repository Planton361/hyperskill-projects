"""Read accepted evidence; write only this isolated prototype. No acquisition."""
import json, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROTECTED=['data/knowledge','state/knowledge-atlas','docs/knowledge-map','prototypes/knowledge-atlas-v6-global','prototypes/knowledge-atlas-v6','prototypes/knowledge-atlas-v6-skill-tree']
def hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in PROTECTED for p in sorted((ROOT/d).rglob('*')) if p.is_file()}
def build():
    read=lambda p:json.loads((ROOT/p).read_text())
    raw=read('prototypes/knowledge-atlas-v6-global/model.json')
    assert len(raw['categories'])==849 and len(raw['topics'])==3106 and not raw['references']
    assert sum(p['is_learned'] is True for p in raw['progress']['topics'])==31
    assert sum(p['is_verified'] is True for p in raw['progress']['topics'])==12
    course=next(c for c in read('data/knowledge/courses.json') if c['id']==8)
    project=next(c for c in read('data/knowledge/projects.json') if c['id']==113)
    stage=next(c for c in read('data/knowledge/stages.json') if c['id']==617)
    req=sorted({int(e['target'].split(':')[1]) for e in read('data/knowledge/edges.json') if e['type']=='project_requires' and e['source']=='project:113'})
    assert (len(course['topic_ids']),len(course['category_ids']),len(req),len(stage['required_topic_ids']))==(89,46,26,12)
    scopes=[dict(scope_type='course',scope_id=8,title=course['title'],explicit_topic_ids=course['topic_ids'],explicit_category_ids=course['category_ids'],evidence_ids=course['evidence_ids']),dict(scope_type='project',scope_id=113,title=project['title'],explicit_topic_ids=req,explicit_category_ids=[],evidence_ids=project['evidence_ids']),dict(scope_type='stage',scope_id=617,title=stage['title'],explicit_topic_ids=sorted(stage['required_topic_ids']),explicit_category_ids=[],evidence_ids=stage['evidence_ids'])]
    for name,data in [('catalog.json',raw),('scopes.json',scopes)]:
        (HERE/name).write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    (HERE/'tests/source.json').write_text(json.dumps({'global_model_sha256':hashlib.sha256((ROOT/'prototypes/knowledge-atlas-v6-global/model.json').read_bytes()).hexdigest(),'observations':raw['observations']},indent=2)+'\n')
if __name__=='__main__':
    import sys
    if '--baseline' in sys.argv:
        p=HERE/'tests/protected-before.json'
        if p.exists(): raise SystemExit('Baseline already exists; refusing overwrite')
        p.write_text(json.dumps(hashes(),indent=2)+'\n')
    elif '--verify' in sys.argv:
        before=json.loads((HERE/'tests/protected-before.json').read_text()); after=hashes()
        result={'unchanged':before==after,'files':len(after),'changed':[k for k in before.keys()|after.keys() if before.get(k)!=after.get(k)]}
        (HERE/'tests/protected-check.json').write_text(json.dumps(result,indent=2)+'\n');print(result);assert result['unchanged']
    else: build()
