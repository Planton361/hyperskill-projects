"""Read-only contracts; synthetic overlays exist only in disposable memory."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
spec = importlib.util.spec_from_file_location('global_atlas_build', BASE/'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ('docs/knowledge-map', 'state/knowledge-atlas', 'data/knowledge')
            for p in (ROOT/folder).rglob('*') if p.is_file()}


class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = hashes()
        cls.data = build.snapshot.load_source(ROOT/'data/knowledge')
        cls.history = json.loads((ROOT/'state/knowledge-atlas/activation-state.json').read_text())
        cls.model = build.project(cls.data, cls.history)

    @classmethod
    def tearDownClass(cls):
        assert hashes() == cls.before, 'Production/state/Knowledge changed'

    def test_counts_roots_identity_and_resolution(self):
        p = self.model
        self.assertEqual(p['counts'], dict(categories=849, topics=89, references=3017, positions=3955, hierarchy=3952))
        self.assertEqual(len(p['roots']), 5)
        by = {r['key']: r for r in p['entities']}
        self.assertEqual(len(by),3955)
        self.assertEqual({by[k]['title'] for k in p['roots']}, {'Computer science','Math','Natural science','Product development','Generative AI'})
        self.assertEqual(sum(r['resolution']=='RESOLVED_TOPIC' for r in by.values()),1)
        self.assertEqual(sum(r['resolution']=='PARTIAL_TOPIC' for r in by.values()),88)
        for r in p['entities']:
            if r['kind']=='reference':
                self.assertNotIn('topic:'+str(r['id']),by)
                self.assertFalse({'title','url','theory','canonical_parent'} & r.keys())
        self.assertEqual(set(by['topic:36']['parents']),{'category:35','category:306'})
        self.assertEqual(len(by['topic:1425']['parents']),2)

    def test_real_scopes_and_history(self):
        self.assertEqual(len(self.model['personal']),135)
        self.assertEqual(sum(r['active'] and r['kind']=='category' for r in self.model['entities']),46)
        self.assertEqual(sum(r['active'] and r['kind']=='topic' for r in self.model['entities']),89)
        c=self.model['courses'][0]
        self.assertEqual((c['id'],len(c['topic_ids']),len(c['category_ids']),len(c['scope'])),(8,89,46,135))
        p=next(p for p in self.model['projects'] if p['id']==113)
        self.assertEqual((p['requirements_status'],len(p['required']),len(p['stages'])),('LOADED',26,5))
        self.assertEqual(len({e['target'] for e in p['requirements'] if e['stage_id']==617}),12)
        self.assertEqual(sum(p['requirements_status']=='UNKNOWN' for p in self.model['projects']),10)
        self.assertEqual(self.history['layout_generation'],0)
        self.assertEqual(self.history['history_version'],0)
        self.assertEqual(self.history['events'],[])
        self.assertEqual(sum(p['is_learned'] is True for p in self.model['progress']),31)
        self.assertEqual(sum(p['is_verified'] is True for p in self.model['progress']),12)

    def test_determinism_and_no_mutation(self):
        before=build.snapshot.encode(self.data)
        expected=build.snapshot.encode(self.model)
        self.assertEqual(build.encoded(),expected)
        self.assertEqual(build.encoded(),expected)
        self.assertEqual((BASE/'generated/catalog.json').read_bytes(),expected)
        self.assertEqual(before,build.snapshot.encode(self.data))
        self.assertEqual(hashes(),self.before)

    def test_synthetic_many_to_many_and_growth(self):
        d=copy.deepcopy(self.data)
        for i in range(20):
            c=copy.deepcopy(d['courses'][0]);c['id']=90000+i;c['title']='SYNTHETIC Course';d['courses'].append(c)
            p=copy.deepcopy(next(p for p in d['projects'] if p['id']==113));p['id']=91000+i;p['title']='SYNTHETIC Project';p['stage_ids']=[];d['projects'].append(p)
            for e in self.data['edges']:
                if e['type']=='project_requires' and e['source']=='project:113':
                    new=copy.deepcopy(e);new['id']='synthetic:'+str(i)+':'+e['id'];new['source']=f'project:{p["id"]}';d['edges'].append(new)
        h=copy.deepcopy(self.history);h['active_categories']=[r['key'] for r in self.model['entities'] if r['kind']=='category']
        p=build.project(d,h)
        self.assertEqual(len(p['entities']),3955)
        self.assertEqual(len(p['courses']),21)
        self.assertEqual(len(p['projects']),31)
        self.assertTrue(all(len(c['scope'])==135 for c in p['courses']))
        self.assertTrue(all(len(r['required'])==26 for r in p['projects'] if r['id']>=91000))
        self.assertEqual(sum(r['active'] for r in p['entities']),938)
        self.assertEqual(hashes(),self.before)

    def test_future_course_relevant_reference_is_not_promoted(self):
        d=copy.deepcopy(self.data)
        c=copy.deepcopy(d['courses'][0]);c.update(id=99999,title='SYNTHETIC unresolved membership',topic_ids=[333],category_ids=[],project_ids=[])
        d['courses'].append(c)
        p=build.project(d,self.history)
        self.assertIn('reference:333',p['courses'][-1]['scope'])
        self.assertNotIn('topic:333',{r['key'] for r in p['entities']})
        self.assertEqual(len(p['entities']),3955)

    def test_renderer_contracts(self):
        subprocess.run(['node',str(BASE/'tests/core.cjs')],check=True,cwd=ROOT)


if __name__=='__main__': unittest.main()
