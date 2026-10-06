import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'scripts'))
from knowledge_atlas import canonical as C, canonical_activation as CA, pipeline, snapshot, transaction, layout_update, activation_persistence as AP
spec=importlib.util.spec_from_file_location('review',ROOT/'prototypes/global-pyramid/migration-review/review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
BASE=Path(__file__).resolve().parent
ENV=dict(os.environ,PLAYWRIGHT_MODULE='/home/anton/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright',CHROMIUM_EXECUTABLE='/opt/google/chrome/chrome')
CALLS=[]
os.environ.update({k:v for k,v in ENV.items() if k in ('PLAYWRIGHT_MODULE','CHROMIUM_EXECUTABLE')})
def clone(root):
    root.mkdir()
    for n in ('scripts','docs/knowledge-map','docs/knowledge-atlas-preview','state/knowledge-atlas','data/knowledge','prototypes/knowledge-atlas-v6'):
        shutil.copytree(ROOT/n,root/n,ignore=shutil.ignore_patterns('__pycache__','tests','build'))
    if (ROOT/'prototypes/knowledge-atlas-v6/build').exists():shutil.copytree(ROOT/'prototypes/knowledge-atlas-v6/build',root/'prototypes/knowledge-atlas-v6/build')
    g=root/'prototypes/global-pyramid/generated';g.mkdir(parents=True)
    for n in ('global-geometry.json','catalog.json'):shutil.copyfile(ROOT/'prototypes/global-pyramid/generated'/n,g/n)
    (root/'.atlas-disposable-test').write_text('spatial-migration-tests-v1\n')
def tree(root):return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
def cli(root,*args,success=True):
    began=time.perf_counter()
    p=subprocess.run([sys.executable,'-B',str(root/'scripts/update-knowledge-atlas.py'),*map(str,args),'--json'],env=ENV,capture_output=True,text=True,timeout=120)
    try:result=json.loads(p.stdout)
    except Exception:raise AssertionError(p.stdout+p.stderr)
    if success and p.returncode:raise AssertionError(result)
    CALLS.append(dict(arguments=list(map(str,args)),status=result['status'],elapsed_ms=(time.perf_counter()-began)*1000))
    return result

def evidence(root,numeric,relevant=True):
    """Explicit fixture metadata/hierarchy in TEMP only; no planner overrides."""
    g=C.read(root/'docs/knowledge-map/generated/global-geometry.json');slots={n['key']:n for n in g['positions']};chain=C.path(slots,'leaf:'+str(numeric));loaded=snapshot.load_source(root/'data/knowledge');catalog=C.validate_structure(loaded,g)
    ev=dict(id='fixture-'+str(numeric),confidence='explicit',fields=['id','title','canonical_parent_id','theory_step_id','url'],method='disposable_fixture',source='fixture',url='https://example.invalid/fixture/'+str(numeric),observed_on='2026-10-05',note='Temporary test evidence only')
    loaded['evidence'].append(ev)
    category_ids={r['id'] for r in loaded['categories']}
    for key in chain[:-1]:
        i=int(key.split(':')[1]);slot=slots[key];parent=int(slot['primary_parent'].split(':')[1]) if slot['primary_parent'] else None
        if i not in category_ids:
            loaded['categories'].append(dict(id=i,title=catalog.categories[key]['title'],canonical_parent_id=parent,url='https://example.invalid/category/'+str(i),evidence_ids=[ev['id']]))
            if parent is not None:loaded['edges'].append(dict(id='fixture-cat-'+str(i),type='hierarchy',source='category:'+str(parent),target=key,evidence_ids=[ev['id']]))
    parent=int(slots['leaf:'+str(numeric)]['primary_parent'].split(':')[1]);loaded['topics'].append(dict(id=numeric,title='Disposable Topic '+str(numeric),canonical_parent_id=parent,theory_step_id=100000+numeric,url='https://example.invalid/topic/'+str(numeric),evidence_ids=[ev['id']]))
    loaded['edges'].append(dict(id='fixture-topic-'+str(numeric),type='hierarchy',source='category:'+str(parent),target='topic:'+str(numeric),evidence_ids=[ev['id']]))
    if relevant:loaded['edges'].append(dict(id='fixture-requires-'+str(numeric),type='project_requires',source='project:113',target='topic:'+str(numeric),evidence_ids=[ev['id']]))
    for n in snapshot.TABLES:(root/'data/knowledge'/f'{n}.json').write_bytes(snapshot.encode(loaded[n]))

def preview(root,out):
    return cli(root,'--activation-preview',out,'--project',113,success=False)['manifest']
def reveal(root,out):
    m=preview(root,out);assert m['outcome']=='ACTIVATION_REVIEW_REQUIRED',m
    result=cli(root,'--approve-activation',out/'activation-manifest.json','--reviewed-fingerprint',m['manifest_fingerprint'])
    return m,result

class Durable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.home=Path(cls.tmp.name);cls.legacy=cls.home/'legacy';clone(cls.legacy)
        files,_=R.P.artifacts(cls.legacy);prev=cls.home/'preview';prev.mkdir()
        for n,b in files.items():(prev/n).write_bytes(b)
        cls.folder=cls.home/'review';m=R.make_package(cls.legacy,prev,cls.folder);s=R.approve(cls.legacy,cls.folder/'migration-manifest.json',m['manifest_fingerprint']);cls.migrated=cls.home/'migrated';shutil.copytree(cls.legacy,cls.migrated);R.apply_test(cls.migrated,cls.folder/'migration-manifest.json',s)
        cls.results=[]
    @classmethod
    def tearDownClass(cls):
        (BASE/'e2e-results.json').write_bytes(snapshot.encode(cls.results));(BASE/'performance.json').write_bytes(snapshot.encode(CALLS));cls.tmp.cleanup()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.home=Path(self.temp.name);self.root=self.home/'root';shutil.copytree(self.migrated,self.root)
    def tearDown(self):self.temp.cleanup()
    def test_normal_cli_end_to_end(self):
        start=time.perf_counter();before=C.restore(self.root/'state/knowledge-atlas');old=copy.deepcopy(before[3]);master=copy.deepcopy(before[4]);knowledge=tree(self.root/'data/knowledge')
        for arg in ('--check','--dry-run','--production'):self.assertEqual(cli(self.root,arg)['status'],'SAFE_TO_APPLY')
        # Poison legacy placement entry points in the disposable installed tree.
        # Normal restore/preview/reveal must still succeed without evaluating them.
        for name in ('activation_geometry.js','persistent_layout.js','layout_update.js'):
            (self.root/'scripts/knowledge_atlas'/name).write_text("throw Error('LEGACY PLACEMENT MUST NOT RUN');\n")
        built=tree(self.root/'docs/knowledge-map');state=tree(self.root/'state/knowledge-atlas');self.assertFalse(cli(self.root,'--production')['applied']);self.assertEqual(built,tree(self.root/'docs/knowledge-map'));self.assertEqual(knowledge,tree(self.root/'data/knowledge'))
        with patch.object(layout_update,'update',side_effect=AssertionError('No additive update')),patch.object(R.P,'construct',side_effect=AssertionError('No prototype geometry generation')):
            cli(self.root,'--check');self.assertEqual(C.restore(self.root/'state/knowledge-atlas')[3],old)
        comparisons=0;steps=[]
        for id in (333,334):
            frozen=C.restore(self.root/'state/knowledge-atlas')[3];evidence(self.root,id);m,r=reveal(self.root,self.home/('reveal-'+str(id)));now=C.restore(self.root/'state/knowledge-atlas');current={n['key']:n for n in now[3]['positions']}
            for n in frozen['positions']:self.assertEqual(n,current[n['key']]);comparisons+=1
            slot=next(n for n in master['positions'] if n['key']=='leaf:'+str(id));self.assertEqual([current['topic:'+str(id)][k] for k in ('x','y','w','h')],[slot[k] for k in ('x','y','w','h')]);self.assertEqual(now[0]['presentation_generation'],1);steps.append(dict(topic=id,generation=1,history_version=now[2]['history_version'],old_displacement=0))
            self.assertFalse(cli(self.root,'--approve-activation',self.home/('reveal-'+str(id))/'activation-manifest.json','--reviewed-fingerprint',m['manifest_fingerprint'])['applied'])
            cli(self.root,'--check')
        self.assertEqual(C.restore(self.root/'state/knowledge-atlas')[4],master)
        nochange=preview(self.root,self.home/'same');self.assertEqual(nochange['outcome'],'NO_CHANGE');self.assertEqual(nochange['expected_generation_change'],0)
        geom=copy.deepcopy(C.restore(self.root/'state/knowledge-atlas')[3]);hist=C.restore(self.root/'state/knowledge-atlas')[2]['history_version']
        # Progress observations must remain consistent: use the new fixture Topics
        # outside the original complete Course observation, with explicit evidence.
        p=C.read(self.root/'data/knowledge/progress.json');courses=C.read(self.root/'data/knowledge/courses.json');courses.append({**courses[0],'id':99,'title':'Disposable Course','topic_ids':[333],'category_ids':[],'project_ids':[],'topics_count':1,'evidence_ids':['fixture-333']});(self.root/'data/knowledge/courses.json').write_bytes(snapshot.encode(courses));p['topics'].append(dict(topic_id=333,course_id=99,is_learned=True,is_verified=True,is_skipped=False,verification_status='verified',is_completed=False,evidence_ids=['fixture-333']))
        (self.root/'data/knowledge/progress.json').write_bytes(snapshot.encode(p));cli(self.root,'--production');self.assertEqual(C.restore(self.root/'state/knowledge-atlas')[3],geom)
        p=C.read(self.root/'data/knowledge/projects.json');p[0]['title']+=' (fixture metadata)';(self.root/'data/knowledge/projects.json').write_bytes(snapshot.encode(p));cli(self.root,'--production');self.assertEqual(C.restore(self.root/'state/knowledge-atlas')[3],geom)
        progress=C.read(self.root/'data/knowledge/progress.json');project=next(r for r in progress['projects'] if r['project_id']==380);project.update(status='completed',is_completed=True,evidence_ids=['fixture-333']);course=next(r for r in progress['courses'] if r['course_id']==8);course['active_project']=None;course['completed_projects'].append(380);course['evidence_ids'].append('fixture-333');(self.root/'data/knowledge/progress.json').write_bytes(snapshot.encode(progress));cli(self.root,'--production');self.assertEqual(C.restore(self.root/'state/knowledge-atlas')[3],geom)
        for table in ('topics','courses','stages'):
            rows=C.read(self.root/'data/knowledge'/f'{table}.json')
            if table=='topics':next(r for r in rows if r['id']==333)['url']='https://example.invalid/enriched-333'
            elif table=='courses':next(r for r in rows if r['id']==99).update(topic_ids=[333,334],topics_count=2,evidence_ids=['fixture-333','fixture-334'])
            else:next(r for r in rows if r['id']==617)['evidence_ids'].append('fixture-333')
            (self.root/'data/knowledge'/f'{table}.json').write_bytes(snapshot.encode(rows));cli(self.root,'--production');self.assertEqual(C.restore(self.root/'state/knowledge-atlas')[3],geom)
        self.assertEqual(C.restore(self.root/'state/knowledge-atlas')[2]['history_version'],hist);cli(self.root,'--check')
        browser=subprocess.run(['node',str(BASE/'browser.cjs'),str(self.root/'docs/knowledge-map')],env=ENV,capture_output=True,text=True,timeout=90);self.assertEqual(browser.returncode,0,browser.stdout+browser.stderr)
        self.results.append(dict(scenario='migration-normal-updater-two-reveals-reference-promotion-semantic-updates',status='PASS',steps=steps,existing_record_comparisons=comparisons,maximum_displacement=0,generation=1,history_version=hist,layout_search=False,elapsed_ms=(time.perf_counter()-start)*1000))
    def test_structural_metadata_authority_refusals(self):
        oldstate=tree(self.root/'state/knowledge-atlas');oldprod=tree(self.root/'docs/knowledge-map')
        # Missing metadata remains a structural reference and cannot be published.
        edges=C.read(self.root/'data/knowledge/edges.json');edges.append(dict(id='missing-333',type='project_requires',source='project:113',target='topic:333',evidence_ids=['project-113']))
        original=(self.root/'data/knowledge/edges.json').read_bytes();(self.root/'data/knowledge/edges.json').write_bytes(snapshot.encode(edges));r=cli(self.root,'--dry-run',success=False);self.assertEqual(r['status'],'METADATA_REQUIRED',r);(self.root/'data/knowledge/edges.json').write_bytes(original)
        for label in ('unknown-topic','new-category','reparent','new-root','fingerprint','schema','partial'):
            with self.subTest(label=label):
                file=self.root/('data/knowledge/topics.json' if label in ('unknown-topic','reparent') else 'data/knowledge/categories.json' if label in ('new-category','new-root') else 'state/knowledge-atlas/spatial-authority.json');saved=file.read_bytes();v=json.loads(saved)
                if label=='unknown-topic':v.append({**v[0],'id':999999,'title':'Unknown fixture'})
                elif label in ('new-category','new-root'):v.append({**v[0],'id':999999,'title':'Unknown category','canonical_parent_id':None if label=='new-root' else 1162})
                elif label=='reparent':v[0]['canonical_parent_id']=1162
                elif label=='fingerprint':v['geometry_fingerprint']='0'*64
                elif label=='schema':v['schema_version']=99
                else:v.pop('master_asset')
                file.write_bytes(snapshot.encode(v));r=cli(self.root,'--production',success=False);self.assertIn(r['status'],(C.EXTENSION,C.MIGRATION),r);file.write_bytes(saved)
        self.assertEqual(tree(self.root/'state/knowledge-atlas'),oldstate);self.assertEqual(tree(self.root/'docs/knowledge-map'),oldprod)
    def test_review_tokens_and_stale_sources(self):
        evidence(self.root,333);folder=self.home/'preview';m=preview(self.root,folder);path=folder/'activation-manifest.json'
        self.assertEqual(cli(self.root,'--approve-activation',path,'--reviewed-fingerprint','0'*64,success=False)['status'],'STALE_ACTIVATION_PREVIEW')
        g=folder/'candidate-geometry.json';saved=g.read_bytes();v=json.loads(saved);v['positions'][0]['x']+=1;g.write_bytes(snapshot.encode(v));self.assertEqual(cli(self.root,'--approve-activation',path,'--reviewed-fingerprint',m['manifest_fingerprint'],success=False)['status'],'STALE_ACTIVATION_PREVIEW');g.write_bytes(saved)
        p=self.root/'data/knowledge/projects.json';saved=p.read_bytes();p.write_bytes(saved+b' ');# Byte formatting alone is semantic canonical-equivalent; use actual evidence change.
        v=json.loads(saved);v[0]['title']+=' changed';p.write_bytes(snapshot.encode(v));self.assertEqual(cli(self.root,'--approve-activation',path,'--reviewed-fingerprint',m['manifest_fingerprint'],success=False)['status'],'STALE_ACTIVATION_PREVIEW');p.write_bytes(saved)
        # Consistently rehashed candidate cannot reuse a previously copied token.
        v=json.loads(g.read_bytes());v['positions'][0]['x']+=1;g.write_bytes(snapshot.encode(v));m2=copy.deepcopy(m);m2['files']['candidate-geometry.json']=C.sha(g.read_bytes());m2.pop('manifest_fingerprint');m2['manifest_fingerprint']=C.fp(m2);path.write_bytes(snapshot.encode(m2));self.assertEqual(cli(self.root,'--approve-activation',path,'--reviewed-fingerprint',m['manifest_fingerprint'],success=False)['status'],'STALE_ACTIVATION_PREVIEW')
    def test_exact_approval_does_not_allocate_or_rebuild(self):
        evidence(self.root,333);folder=self.home/'review';m=CA.package_preview(self.root,folder,context={'mode':'PROJECT_FOCUS','project_ids':[113]})
        actual=layout_update.bridge
        with patch.object(layout_update,'bridge',side_effect=AssertionError('Approval must not layout/browser/rebuild')),patch.object(build_module(),'artifacts',side_effect=AssertionError('Exact publication')):
            r=AP.approve(self.root,folder/'activation-manifest.json',reviewed_fingerprint=m['manifest_fingerprint']);self.assertTrue(r['applied'])
        self.assertEqual((self.root/'docs/knowledge-map/target-geometry.json').read_bytes(),(folder/'candidate-geometry.json').read_bytes())
    def test_fault_rollback_and_hard_crash(self):
        evidence(self.root,333);folder=self.home/'preview';m=CA.package_preview(self.root,folder,context={'mode':'PROJECT_FOCUS','project_ids':[113]});oldstate=tree(self.root/'state/knowledge-atlas');oldprod=tree(self.root/'docs/knowledge-map');results=[]
        for boundary in ('before_authority_validation','after_candidate_creation','before_state_staging','after_state_staging','after_production_staging','before_swaps','after_state_swap','after_production_swap','before_commit_record'):
            def fault(n):
                if n==boundary:raise RuntimeError(boundary)
            with self.subTest(boundary=boundary):
                with self.assertRaises(RuntimeError):AP.approve(self.root,folder/'activation-manifest.json',reviewed_fingerprint=m['manifest_fingerprint'],fault=fault)
                self.assertEqual(tree(self.root/'state/knowledge-atlas'),oldstate);self.assertEqual(tree(self.root/'docs/knowledge-map'),oldprod)
                p=subprocess.run([sys.executable,'-B',str(BASE/'crash.py'),str(self.root),str(folder/'activation-manifest.json'),m['manifest_fingerprint'],boundary],env=ENV);self.assertEqual(p.returncode,77)
                cli(self.root,'--recover-transaction');self.assertEqual(tree(self.root/'state/knowledge-atlas'),oldstate);self.assertEqual(tree(self.root/'docs/knowledge-map'),oldprod);self.assertFalse(list((self.root/'state').glob('.atlas-candidate-*')));self.assertFalse(list((self.root/'docs').glob('.atlas-candidate-*')));results.append(dict(boundary=boundary,recovery='OLD_CANONICAL'))
        for boundary in ('after_commit_record','after_cleanup'):
            for target,files in [(self.root/'state/knowledge-atlas',oldstate),(self.root/'docs/knowledge-map',oldprod)]:
                shutil.rmtree(target);target.mkdir()
                for n,b in files.items():p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            p=subprocess.run([sys.executable,'-B',str(BASE/'crash.py'),str(self.root),str(folder/'activation-manifest.json'),m['manifest_fingerprint'],boundary],env=ENV);self.assertEqual(p.returncode,77);cli(self.root,'--recover-transaction');self.assertIn('topic:333',C.restore(self.root/'state/knowledge-atlas')[0]['accepted_inventory']);cli(self.root,'--check');results.append(dict(boundary=boundary,recovery='NEW_CANONICAL'))
        (BASE/'recovery-results.json').write_bytes(snapshot.encode(results))
    def test_real_guard_and_protected_hashes(self):
        with self.assertRaisesRegex(ValueError,'REAL_CANONICAL_PUBLICATION_FORBIDDEN'):C.writer_guard(ROOT)
        baseline=C.read(BASE/'baseline.json');self.assertTrue(all(C.sha((ROOT/n).read_bytes())==h for n,h in baseline.items()))

    def test_metadata_promotion_before_relevance_has_no_geometry_event(self):
        before=C.restore(self.root/'state/knowledge-atlas');self.assertIn(333,C.validate_structure(snapshot.load_source(self.root/'data/knowledge'),before[4]).references)
        evidence(self.root,333,relevant=False);cli(self.root,'--production');after=C.restore(self.root/'state/knowledge-atlas')
        self.assertEqual(before[3],after[3]);self.assertEqual(after[0]['presentation_generation'],1);self.assertEqual(after[2]['history_version'],0)
        raw=C.read(self.root/'docs/knowledge-map/generated/catalog.json');node=next(n for n in raw['entities'] if n['key']=='topic:333');self.assertFalse(node['active']);self.assertFalse(any(n['key']=='reference:333' for n in raw['entities']))
        edges=C.read(self.root/'data/knowledge/edges.json');edges.append(dict(id='fixture-relevant-333',type='project_requires',source='project:113',target='topic:333',evidence_ids=['fixture-333']));(self.root/'data/knowledge/edges.json').write_bytes(snapshot.encode(edges));reveal(self.root,self.home/'review');cli(self.root,'--check')

    def test_missing_topic_step_and_url_block_reveal(self):
        evidence(self.root,333);p=self.root/'data/knowledge/topics.json';rows=C.read(p);row=next(r for r in rows if r['id']==333);row['theory_step_id']=None;row['url']=None;p.write_bytes(snapshot.encode(rows))
        before=tree(self.root/'state/knowledge-atlas');m=preview(self.root,self.home/'review');self.assertEqual(m['outcome'],'METADATA_REQUIRED');self.assertFalse((self.home/'review/view').exists());self.assertEqual(tree(self.root/'state/knowledge-atlas'),before)

    def test_deterministic_reveal_and_missing_token(self):
        evidence(self.root,333);one=self.home/'one';two=self.home/'two'
        m=preview(self.root,one);again=preview(self.root,two)
        self.assertEqual(m,again);self.assertEqual(tree(one),tree(two))
        state=tree(self.root/'state/knowledge-atlas');production=tree(self.root/'docs/knowledge-map')
        with self.assertRaisesRegex(ValueError,'REVIEW_FINGERPRINT_REQUIRED'):
            AP.approve(self.root,one/'activation-manifest.json')
        file=self.root/'scripts/knowledge_atlas/canonical_runtime/style.css'
        file.write_bytes(file.read_bytes()+b'\n/* changed validator-bound runtime */\n')
        self.assertEqual(cli(self.root,'--approve-activation',one/'activation-manifest.json','--reviewed-fingerprint',m['manifest_fingerprint'],success=False)['status'],'STALE_ACTIVATION_PREVIEW')
        self.assertEqual(tree(self.root/'state/knowledge-atlas'),state);self.assertEqual(tree(self.root/'docs/knowledge-map'),production)

def build_module():
    from knowledge_atlas import build
    return build
if __name__=='__main__':unittest.main()
