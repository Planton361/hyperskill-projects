import copy
import hashlib
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('pyramid',BASE/'build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('docs/knowledge-map','state/knowledge-atlas','data/knowledge') for p in (ROOT/folder).rglob('*') if p.is_file()}
class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=hashes();cls.data=b.snapshot.load_source(ROOT/'data/knowledge');cls.history=json.loads((ROOT/'state/knowledge-atlas/activation-state.json').read_text());cls.model=b.projection.project(cls.data,cls.history);cls.geo=b.geometry(cls.model)
    @classmethod
    def tearDownClass(cls):
        after=hashes();assert cls.before==after
        tracked=subprocess.check_output(['git','ls-files','docs/knowledge-map','state/knowledge-atlas','data/knowledge'],cwd=ROOT,text=True).splitlines()
        baseline={p:hashlib.sha256(subprocess.check_output(['git','show','b666e28:'+p],cwd=ROOT)).hexdigest() for p in tracked}
        assert all(after[p]==v for p,v in baseline.items())
        (BASE/'tests/integrity.json').write_text(json.dumps(dict(before=cls.before,after=after,baseline_main=baseline,changed=[],history_version=cls.history['history_version'],generation=cls.history['layout_generation']),indent=2)+'\n')
    def test_counts_semantics(self):
        self.assertEqual(self.model['counts'],dict(categories=849,topics=89,references=3017,positions=3955,hierarchy=3952))
        ps=self.geo['positions'];self.assertEqual(len(ps),3955);self.assertEqual(len({p['key'] for p in ps}),3955)
        self.assertEqual(sum(p['key'].startswith('leaf:') for p in ps),3106)
        self.assertEqual(len(self.geo['leaf_identity_mapping']),3106)
        alias=next(r for r in self.geo['leaf_identity_mapping'] if r['structural_id']==333)
        self.assertEqual(alias,dict(structural_id=333,slot='leaf:333',semantic_aliases=['reference:333','topic:333']))
        by={n['key']:n for n in self.model['entities']}
        self.assertEqual({by[s['root']]['title'] for s in self.geo['root_sectors']},{'Computer science','Math','Natural science','Product development','Generative AI'})
        self.assertEqual(len(self.geo['root_sectors']),5)
        self.assertEqual(sum(n['resolution']=='RESOLVED_TOPIC' for n in by.values()),1)
        self.assertEqual(sum(n['resolution']=='PARTIAL_TOPIC' for n in by.values()),88)
        for n in by.values():
            if n['kind']=='reference': self.assertFalse({'title','url','theory'} & n.keys())
        self.assertEqual(len(self.model['personal']),135)
        self.assertEqual(sum(p['is_learned'] is True for p in self.model['progress']),31)
        self.assertEqual(sum(p['is_verified'] is True for p in self.model['progress']),12)
        self.assertEqual(sum(p['requirements_status']=='UNKNOWN' for p in self.model['projects']),10)
    def test_regions_order_routes(self):
        sectors=self.geo['root_sectors']
        for a,c in zip(sectors,sectors[1:]):self.assertLess(a['x']+a['w'],c['x'])
        by={p['key']:p for p in self.geo['positions']}
        for n in by.values():
            if not n['parents']:continue
            p=by[n['primary_parent']];r=p['region']
            self.assertLess(p['y']+p['h'],n['y'])
            self.assertGreaterEqual(n['x'],r['x']);self.assertLessEqual(n['x']+n['w'],r['x']+r['w'])
            self.assertLessEqual(n['y']+n['h'],r['y']+r['h'])
            self.assertEqual(n['primary_parent'],min(n['parents'],key=lambda k:(-by[k]['depth'],int(k.split(':')[1]))))
            for parent in n['parents']:self.assertLess(by[parent]['y']+by[parent]['h'],n['y'])
        for n in by.values():
            cs=n['sibling_order'];self.assertEqual(cs,sorted(cs,key=lambda k:(not k.startswith('leaf:'),int(k.split(':')[1]))))
        for i in (36,1425):self.assertEqual(len(by['leaf:'+str(i)]['secondary_memberships']),1)
        for n in by.values():
            xs=[by[k]['x'] for k in n['sibling_order']];self.assertEqual(xs,sorted(xs))
        self.assertEqual(len(self.geo['hierarchy_routes']),3955)
    def test_no_card_overlaps(self):
        active=[]
        for n in sorted(self.geo['positions'],key=lambda n:n['x']):
            active=[a for a in active if a['x']+a['w']>n['x']]
            for a in active:
                self.assertTrue(a['y']+a['h']<=n['y'] or n['y']+n['h']<=a['y'],(a['key'],n['key']))
            active.append(n)
    def test_byte_determinism_and_progress_independence(self):
        first=b.encoded();self.assertEqual(first,b.encoded())
        self.assertEqual(first[1],(BASE/'generated/global-geometry.json').read_bytes())
        self.assertEqual(first[0],(BASE/'generated/catalog.json').read_bytes())
        altered=copy.deepcopy(self.model);altered['personal']=[];altered['progress']=[];altered['courses']=[];altered['projects']=[]
        for n in altered['entities']:n['active']=False;n['title']='SYNTHETIC';n['canonical_parent']=999
        self.assertEqual(b.geometry(altered),self.geo)
        altered['entities'].reverse();self.assertEqual(b.geometry(altered),self.geo)
    def test_valid_reference_promotion(self):
        from knowledge_atlas.catalog import Catalog
        from knowledge_atlas.catalog_observation import ordered_catalog
        catalog=Catalog(self.data);o=copy.deepcopy(next(iter(self.data['catalog_observations'].values())))
        source='source:'+'f'*64;parent=catalog.references[333]['parent_ids'][0]
        row=dict(id=333,title='Synthetic resolution',is_group=False,parent_id=parent,resolution='PARTIAL_TOPIC');row['fact_sources']={k:[source] for k in row if k!='resolution'}
        o['source_pages'].append(dict(id=source,method='GET',path='/api/topics/333',content_type='application/json'));o['topics'].append(row)
        o['unresolved_references']=[r for r in o['unresolved_references'] if r['id']!=333]
        for r in o['hierarchy_records']:
            if r['child_id']==333:r['child_type']='TOPIC'
        promoted=catalog.promote_reference(333,ordered_catalog(o),'observations/synthetic-future.json')
        self.assertEqual(promoted.get_resolution_status(333),'PARTIAL_TOPIC');self.assertEqual(catalog.get_resolution_status(333),'UNRESOLVED_REFERENCE')
        model=copy.deepcopy(self.model)
        n=next(n for n in model['entities'] if n['key']=='reference:333');n.update(key='topic:333',kind='topic',title='Synthetic resolution',resolution='PARTIAL_TOPIC')
        self.assertEqual(promoted.memberships[333],catalog.memberships[333]);self.assertEqual(b.slot(n['key']),'leaf:333')
        self.assertEqual(b.snapshot.encode(b.geometry(model)),b.snapshot.encode(self.geo))
    def test_runtime_projections_and_activations(self):subprocess.run(['node',str(BASE/'tests/core.cjs')],check=True)
if __name__=='__main__':unittest.main()
