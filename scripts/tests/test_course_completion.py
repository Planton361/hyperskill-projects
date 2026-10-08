import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from knowledge_atlas.course_completion import validate_records

class CourseCompletionTests(unittest.TestCase):
    scopes={'courses':[{'scope_id':8}]}
    def record(self):return dict(course_id=8,is_completed=True,source='owner',observed_at='2026-10-08T14:00:00Z',evidence_id='course-8-fixture')
    def test_empty_and_explicit(self):
        self.assertEqual(validate_records({'schema':1,'records':[]},self.scopes),{'schema':1,'records':[]})
        envelope={'schema':1,'records':[self.record()]};before=copy.deepcopy(envelope);self.assertEqual(validate_records(envelope,self.scopes),envelope);self.assertEqual(envelope,before)
        envelope['records'][0]['source']='hyperskill';self.assertEqual(validate_records(envelope,self.scopes),envelope)
    def test_reject_missing_ambiguous_private_unknown(self):
        for field,value in [('course_id',True),('course_id',999),('is_completed',1),('source','inferred'),('observed_at','yesterday'),('evidence_id','/private/workspace')]:
            r=self.record();r[field]=value
            with self.assertRaises(ValueError):validate_records({'schema':1,'records':[r]},self.scopes)
        with self.assertRaises(ValueError):validate_records({'schema':1,'records':[self.record(),self.record()]},self.scopes)
        r=self.record();del r['observed_at']
        with self.assertRaises(ValueError):validate_records({'schema':1,'records':[r]},self.scopes)
        with self.assertRaises(ValueError):validate_records({'schema':True,'records':[]},self.scopes)
