"""Offline knowledge graph contract and negative validation tests."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
LEARNED=[9,14,15,25,27,30,31,32,36,87,88,89,112,113,146,147,148,152,161,193,259,260,307,308,309,348,571,1248,1476,1761,3538]
VERIFIED=[15,25,31,32,36,87,88,148,152,259,571,1761]
spec=importlib.util.spec_from_file_location('knowledge',ROOT/'scripts/build-knowledge-graph.py')
kg=importlib.util.module_from_spec(spec)
spec.loader.exec_module(kg)

class KnowledgeGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=kg.load(ROOT)
        cls.graph=kg.build(cls.original)
    def setUp(self):
        self.data=copy.deepcopy(self.original)
    def rejects(self, message):
        with self.assertRaisesRegex(ValueError,message): kg.validate(self.data)
    def test_valid_snapshot(self):
        kg.validate(self.data)
        self.assertEqual(len(self.data['topics']),89)
        self.assertEqual(len(self.data['categories']),46)
    def test_no_duplicate_topics(self):
        self.data['topics'].append(self.data['topics'][0]);self.rejects('duplicate IDs')
    def test_no_dangling_edges(self):
        self.data['edges'][0]['target']='topic:999999';self.rejects('dangling edge')
    def test_requires_must_target_topic(self):
        edge=next(e for e in self.data['edges'] if e['type']=='project_requires')
        edge['target']='category:74';self.rejects('invalid project relation')
    def test_missing_evidence_rejected(self):
        self.data['edges'][0]['evidence_ids']=[];self.rejects('missing evidence')
    def test_no_implicit_applies(self):
        edge=copy.deepcopy(next(e for e in self.data['edges'] if e['type']=='project_requires'))
        edge.update(type='project_applies',id='invalid-applies')
        self.data['edges'].append(edge);self.rejects('matching explicit application assertion')
    def test_no_inferred_applied_status(self):
        self.data['progress']['topics'][0]['is_applied']=True;self.rejects('unproven applied topic')
    def test_26_distinct_targets(self):
        edges=[e for e in self.data['edges'] if e['type']=='project_requires' and e['source']=='project:113']
        self.assertEqual(len({e['target'] for e in edges}),26)
        self.assertTrue(all(e['target'].startswith('topic:') for e in edges))
    def test_stage_distribution(self):
        self.assertEqual([len(s['required_topic_ids']) for s in self.data['stages']],[4,5,5,12,0])
    def test_project_380_no_completed_stage_evidence(self):
        p=next(p for p in self.data['progress']['projects'] if p['project_id']==380)
        self.assertEqual(p['completed_stage_ids'],[])
        p['completed_stage_ids']=[1];self.rejects('no completed-stage evidence')
    def test_unknown_progress_preserved(self):
        course=self.data['progress']['courses'][0]
        self.assertEqual(course['learned_topic_ids'],LEARNED);self.assertIsNone(course['applied_topic_ids'])
        topics=[n for n in self.graph['nodes'] if n['type']=='topic']
        self.assertEqual(sorted(n['hyperskill_id'] for n in topics if n['status']=='learned'),LEARNED)
        self.assertEqual(sum(n['status']=='not_learned' for n in topics),58)
        self.assertTrue(all(n['applied'] is None for n in topics))
        self.assertFalse(any(e['type']=='project_applies' for e in self.graph['edges']))
    def test_unproven_full_set_rejected(self):
        self.data['progress']['courses'][0]['learned_topic_ids']=[15];self.rejects('incomplete full status set')
    def test_full_snapshot_coverage(self):
        rows=self.data['progress']['topics']
        self.assertEqual(len(rows),89)
        self.assertEqual({r['topic_id'] for r in rows},set(self.data['courses'][0]['topic_ids']))
        self.assertEqual(sum(r['is_learned'] for r in rows),31)
        self.assertEqual(sum(r['is_skipped'] for r in rows),0)
        self.assertEqual(self.graph['coverage']['topic_progress'],'complete')
    def test_verified_is_separate_from_learned(self):
        rows=self.data['progress']['topics']
        self.assertEqual([r['topic_id'] for r in rows if r['is_verified']],VERIFIED)
        failed=next(r for r in rows if r['topic_id']==113)
        self.assertTrue(failed['is_learned']);self.assertFalse(failed['is_verified'])
        self.assertEqual(failed['verification_status'],'failed')
        evaluation=next(r for r in rows if r['topic_id']==9)
        self.assertTrue(evaluation['is_learned']);self.assertFalse(evaluation['is_verified'])
    def test_cannot_mark_open_topic_learned(self):
        self.data['progress']['topics'][0]['is_learned']=True
        self.rejects('status disagrees with observation')
    def test_cannot_upgrade_verification(self):
        row=next(r for r in self.data['progress']['topics'] if r['topic_id']==113)
        row['is_verified']=True
        self.rejects('verification status mismatch')
    def test_missing_open_topic_is_incomplete(self):
        self.data['progress']['topics'].pop(0)
        self.rejects('incomplete topic coverage')
    def test_missing_snapshot_rejected(self):
        self.data['observations']={}
        self.rejects('missing observation snapshot')
    def test_duplicate_progress_rejected(self):
        self.data['progress']['topics'].append(self.data['progress']['topics'][0])
        self.rejects('duplicate progress')
    def test_preview_reflects_complete_learned_data(self):
        svg=kg.preview(self.graph)
        self.assertIn('31 explicitly learned topics, including 12 with verified status',svg)
        self.assertNotIn('One explicitly known',svg)
        self.assertNotIn('partial personal evidence',svg)
    def test_deterministic(self):
        other=kg.build(copy.deepcopy(self.original))
        self.assertEqual(json.dumps(self.graph,sort_keys=True),json.dumps(other,sort_keys=True))
        self.assertEqual(kg.preview(self.graph),kg.preview(other))
    def test_generated_files_current(self):
        kg.render(ROOT,check=True)
    def test_svg_well_formed(self):
        svg=ET.fromstring(kg.preview(self.graph))
        self.assertEqual(svg.tag,'{http://www.w3.org/2000/svg}svg')
    def test_dependency_reciprocity(self):
        prereq={(e['source'],e['target']) for e in self.data['edges'] if e['type']=='prerequisite'}
        dependent={(e['source'],e['target']) for e in self.data['edges'] if e['type']=='dependent'}
        self.assertEqual(len(prereq),137);self.assertEqual(prereq,dependent)
    def test_multiple_memberships_preserved(self):
        parents={e['source'] for e in self.data['edges'] if e['type']=='hierarchy' and e['target']=='topic:36'}
        self.assertEqual(parents,{'category:35','category:306'})
    def test_sensitive_keys_absent(self):
        forbidden={'user_id','certificate_url','cookies','cookie','authorization','token','session','email','password'}
        def walk(value):
            if isinstance(value,dict):
                self.assertFalse(set(value)&forbidden)
                for v in value.values():walk(v)
            elif isinstance(value,list):
                for v in value:walk(v)
        walk(self.data);walk(self.graph)
    def test_project_113_not_labelled_applied(self):
        project=next(n for n in self.graph['nodes'] if n['id']=='project:113')
        self.assertEqual(project['status'],'completed')
        self.assertEqual(project['required_topics_count'],26)
        self.assertNotIn('applied_topics_count',project)

if __name__=='__main__':unittest.main()
