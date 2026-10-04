"""Security, evidence boundaries and frozen-production regression of global data."""
import base64
import copy
import json
import os
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas import snapshot, validate, build, state
from knowledge_atlas.catalog_observation import sanitize, validate_observation, security_guard, forest, ordered_catalog
from knowledge_atlas.catalog import Catalog, active_projection, compare_catalogs, summary
from knowledge_atlas.observations import load


def entry(path, payload, stamp='2026-10-04T12:00:00.000Z', encoded=False):
    text = json.dumps(payload)
    return {'startedDateTime': stamp, 'request': {'method': 'GET', 'url': 'https://hyperskill.org' + path,
            'headers': [{'name': 'Authorization', 'value': 'synthetic-secret'}]},
            'response': {'status': 200, 'content': {'mimeType': 'application/json',
                         'text': base64.b64encode(text.encode()).decode() if encoded else text,
                         **({'encoding': 'base64'} if encoded else {})}}}


def fixture():
    rows = [{'id': i, 'title': 'Domain ' + str(i), 'parent_id': None,
             'children': [i + 100], 'descendants': [i + 100], 'learned_descendants_count': 99} for i in range(1, 6)]
    return {'log': {'entries': [entry('/api/topic-relations?page=1&page_size=100',
             {'meta': {'page': 1, 'has_previous': False, 'has_next': False}, 'topic-relations': rows}),
             entry('/api/learning-activities', {'learning-activities': [
                 {'id': 'synthetic-private-activity', 'topic_id': 101, 'title': 'One Topic', 'progress': {'user_id': 999}}]}),
             entry('/api/topics/102', {'topics': [{'id': 102, 'title': 'Another Topic', 'is_group': False,
                   'parent_id': 2, 'children': [], 'hierarchy': [2], 'root_id': 2, 'theory': 1002,
                   'prerequisites': [101], 'explicit_prerequisites': [{'source': 101, 'kind': 1, 'user_id': 999}],
                   'followers': [103], 'enabled': True, 'progress_id': 'private', 'created_by': 999,
                   'description': 'Lesson content excluded'}]})]}}


class SanitizerTests(unittest.TestCase):
    def test_positive_allowlist(self):
        o = sanitize(fixture())
        security_guard(o)
        text = snapshot.encode(o).decode()
        for rejected in ('synthetic-secret', 'private-activity', 'Lesson content', 'learned_descendants_count', 'enabled', 'created_by'):
            self.assertNotIn(rejected, text)
        self.assertEqual([r['resolution'] for r in o['topics']], ['PARTIAL_TOPIC', 'RESOLVED_TOPIC'])
        self.assertEqual(len(o['unresolved_references']), 3)
        self.assertEqual(o['prerequisite_records'][0]['source_id'], 101)
        self.assertEqual(o['follower_records'][0]['target_id'], 103)
        self.assertEqual(o['coverage']['reported_total'], None)

    def test_recursive_security_guard(self):
        for value in ({'nested': [{'csrf': 'secret'}]}, {'user_id': 12}, {'title': 'Bearer synthetic'},
                      {'title': 'person@example.org'}, {'title': '/home/private/capture.har'},
                      {'title': 'https://example.org/?token=secret'}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                security_guard(value)

    def test_secret_in_approved_title_fails_closed(self):
        h = fixture()
        d = json.loads(h['log']['entries'][0]['response']['content']['text'])
        d['topic-relations'][0]['title'] = 'token=synthetic-secret'
        h['log']['entries'][0]['response']['content']['text'] = json.dumps(d)
        with self.assertRaisesRegex(ValueError, 'Sensitive value'):
            sanitize(h)

    def test_unknown_observation_and_personal_fields_rejected(self):
        o = sanitize(fixture())
        o['topics'][0]['is_learned'] = True
        with self.assertRaises(ValueError): validate_observation(o)
        with tempfile.TemporaryDirectory() as d:
            Path(d, 'bad.json').write_text('{"observation_type":"arbitrary"}')
            with self.assertRaises(ValueError): load(d)

    def test_deterministic_order_base64_duplicates(self):
        h = fixture()
        expected = snapshot.encode(sanitize(h))
        h['log']['entries'].reverse()
        h['log']['entries'].append(copy.deepcopy(h['log']['entries'][0]))
        for e in h['log']['entries']:
            c = e['response']['content']
            d = json.loads(c['text'])
            for v in d.values():
                if isinstance(v, list): v.reverse()
            c['text'] = base64.b64encode(json.dumps(d).encode()).decode()
            c['encoding'] = 'base64'
        self.assertEqual(snapshot.encode(sanitize(h)), expected)
        self.assertEqual(snapshot.encode(ordered_catalog(sanitize(h))), expected)

    def test_scoped_map_does_not_establish_global_catalog(self):
        h = fixture()
        h['log']['entries'][0]['request']['url'] += '&track_id=8'
        with self.assertRaisesRegex(ValueError, 'No global'): sanitize(h)

    def test_missing_pagination_and_conflicting_duplicates(self):
        for case in ('missing', 'unfinished', 'conflict'):
            h = fixture()
            e = h['log']['entries'][0]
            d = json.loads(e['response']['content']['text'])
            if case == 'missing':
                e['request']['url'] = 'https://hyperskill.org/api/topic-relations?page=2&page_size=100'
                d['meta']['page'] = 2
            elif case == 'unfinished': d['meta']['has_next'] = True
            else:
                h['log']['entries'].append(copy.deepcopy(e))
                d['topic-relations'][0]['title'] = 'Conflicting title'
            e['response']['content']['text'] = json.dumps(d)
            with self.subTest(case=case), self.assertRaises(ValueError): sanitize(h)

    def test_cross_page_collisions_and_short_intermediate_pages(self):
        h = fixture()
        first = h['log']['entries'][0]
        d = json.loads(first['response']['content']['text'])
        d['meta']['has_next']=True
        first['request']['url']='https://hyperskill.org/api/topic-relations?page=1&page_size=5'
        first['response']['content']['text']=json.dumps(d)
        second=copy.deepcopy(first)
        second['request']['url']='https://hyperskill.org/api/topic-relations?page=2&page_size=5'
        d['meta']={'page':2,'has_previous':True,'has_next':False}
        d['topic-relations']=d['topic-relations'][:1]
        second['response']['content']['text']=json.dumps(d)
        h['log']['entries'].append(second)
        with self.assertRaisesRegex(ValueError,'Duplicate structural IDs'):sanitize(h)
        d=json.loads(first['response']['content']['text']);d['topic-relations']=d['topic-relations'][:4]
        first['response']['content']['text']=json.dumps(d)
        with self.assertRaisesRegex(ValueError,'Incomplete pagination page'):sanitize(h)

    def test_missing_parent_field_cannot_become_root(self):
        h=fixture();first=h['log']['entries'][0]
        d=json.loads(first['response']['content']['text']);del d['topic-relations'][0]['parent_id']
        first['response']['content']['text']=json.dumps(d)
        with self.assertRaisesRegex(ValueError,'Missing structural'):sanitize(h)

    def test_type_cannot_be_inferred_from_leaf_or_group(self):
        h = fixture()
        d = json.loads(h['log']['entries'][2]['response']['content']['text'])
        d['topics'][0]['is_group'] = True
        h['log']['entries'][2]['response']['content']['text'] = json.dumps(d)
        o = sanitize(h)
        self.assertEqual([t['id'] for t in o['topics']], [101])
        self.assertIn(102, [r['id'] for r in o['unresolved_references']])

    def test_hierarchy_path_order_is_meaningful(self):
        h = fixture()
        d = json.loads(h['log']['entries'][2]['response']['content']['text'])
        d['topics'][0]['hierarchy'] = [5, 2]
        h['log']['entries'][2]['response']['content']['text'] = json.dumps(d)
        self.assertEqual(sanitize(h)['topics'][1]['hierarchy'], [5, 2])

    def test_forest_validation(self):
        o = sanitize(fixture())
        self.assertEqual(len(forest(o['categories'])['roots']), 5)
        for kind in ('parent', 'self', 'descendant', 'duplicate', 'unreachable_cycle'):
            rows = copy.deepcopy(o['categories'])
            if kind == 'parent': rows[0]['parent_id'] = 99
            elif kind == 'self': rows[0]['children'].append(rows[0]['id'])
            elif kind == 'descendant': rows[0]['descendants'] = []
            elif kind == 'duplicate': rows.append(copy.deepcopy(rows[0]))
            else:
                rows[0]['parent_id'], rows[1]['parent_id'] = 2, 1
                rows[0]['children'].append(2); rows[1]['children'].append(1)
            with self.subTest(kind=kind), self.assertRaises(ValueError): forest(rows)


class GlobalCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = snapshot.load_source(ROOT/'data/knowledge')
        cls.o = next(iter(cls.data['catalog_observations'].values()))
        cls.catalog = Catalog(cls.data)

    def test_capture_acceptance_counts(self):
        v = validate_observation(self.o)
        self.assertEqual((len(v['roots']), v['category_count'], v['leaf_reference_count'], v['hierarchy_count']), (5,849,3106,3952))
        self.assertEqual((v['category_hierarchy_count'], v['leaf_membership_count'], v['maximum_leaf_depth']), (844,3108,8))
        self.assertEqual(len(self.o['topics']), 89)
        self.assertEqual(sum(t['resolution'] == 'RESOLVED_TOPIC' for t in self.o['topics']), 1)
        self.assertEqual(sum(t['resolution'] == 'PARTIAL_TOPIC' for t in self.o['topics']), 88)
        self.assertEqual(len(self.o['unresolved_references']), 3017)
        pages = sorted([s for s in self.o['source_pages'] if s['path']=='/api/topic-relations'], key=lambda p:p['page'])
        self.assertEqual([p['page'] for p in pages], list(range(1,10)))
        self.assertEqual([p['returned_record_count'] for p in pages], [100]*8+[49])
        self.assertTrue(all(p['reported_total'] is None for p in pages))
        self.assertEqual({r['title'] for r in self.o['categories'] if r['parent_id'] is None},
                         {'Computer science','Math','Natural science','Product development','Generative AI'})

    def test_course_regression_all_facts_and_progress(self):
        p = self.catalog.get_course_projection(8)
        self.assertEqual([len(p[k]) for k in ('categories','topics','hierarchy_records')], [46,89,136])
        self.assertEqual({r['id'] for r in p['topics']}, {r['id'] for r in self.data['topics']})
        self.assertEqual({r['id'] for r in p['categories']}, {r['id'] for r in self.data['categories']})
        self.assertEqual({(r['parent_id'],r['child_id']) for r in p['hierarchy_records']},
                         {(int(e['source'].split(':')[1]),int(e['target'].split(':')[1])) for e in self.data['edges'] if e['type']=='hierarchy'})
        self.assertEqual(snapshot.canonical(p['progress']), snapshot.canonical(self.data['progress']))
        self.assertEqual(sum(r['is_learned'] for r in p['progress']['topics']),31)
        self.assertEqual(sum(r['is_verified'] is True for r in p['progress']['topics']),12)
        for kind in ('prerequisite', 'dependent'):
            self.assertEqual(len([e for e in p['accepted_edges'] if e['type']==kind]),137)
        self.assertEqual(len(self.catalog.get_project_context(113)['topics']),26)
        self.assertEqual(len([e for e in p['accepted_edges'] if e['type']=='project_requires' and e.get('stage_id')==617]),12)
        self.assertFalse(any(e['type']=='project_applies' for e in self.data['edges']))

    def test_multiple_memberships_and_ancestors(self):
        self.assertEqual(self.catalog.memberships[36], {35,306})
        self.assertEqual(self.catalog.memberships[1425], {1260,1423})
        self.assertTrue({'category:35','category:306'} <= set(self.catalog.get_catalog_ancestors(36)))
        self.assertEqual(self.catalog.get_catalog_ancestors('category:1162'), [])

    def test_global_identity_no_fake_topics(self):
        self.assertEqual(len(self.catalog.categories),849)
        self.assertEqual(len(self.catalog.topics),89)
        self.assertEqual(len(self.catalog.references),3017)
        self.assertNotIn('topic:333',self.catalog.topics)
        self.assertEqual(self.catalog.get_resolution_status(333), 'UNRESOLVED_REFERENCE')
        self.assertEqual(self.catalog.get_resolution_status('topic:518'), 'RESOLVED_TOPIC')
        self.assertEqual(self.catalog.get_resolution_status(9), 'PARTIAL_TOPIC')

    def test_dormancy_not_personal_state(self):
        r = self.catalog.get_relevance('category:331')
        self.assertEqual(r, {'catalog_known':True,'course_relevant':False,'project_relevant':False,
                             'learned':None,'verified':None,'dormant':True})
        self.assertTrue(self.catalog.get_relevance(333)['dormant'])
        self.assertTrue(self.catalog.get_relevance(9)['course_relevant'])
        self.assertEqual(self.catalog.get_project_context(380)['topics'], [])
        self.assertFalse(self.catalog.get_relevance(9, {'course_ids': [],'project_ids':[380]})['project_relevant'])

    def test_representative_global_branches_remain_dormant(self):
        active_categories = {r['id'] for r in self.catalog.get_course_projection(8)['categories']}
        # Names are not keys: the catalog contains more than one "Math" label.
        for title, identifier in (('Python',331), ('Kotlin',209), ('Math',525), ('Generative AI',4055)):
            category = self.catalog.categories[f'category:{identifier}']
            self.assertEqual(category['title'], title)
            relevance = self.catalog.get_relevance(f'category:{identifier}')
            self.assertTrue(relevance['catalog_known'], title)
            self.assertTrue(relevance['dormant'], title)
            self.assertFalse(relevance['course_relevant'], title)
            self.assertNotIn(identifier, active_categories, title)
            self.assertNotIn('hidden', category)
            self.assertNotIn('visible', category)

    def test_pilot_leaves_remain_unresolved(self):
        self.assertEqual(self.catalog.memberships[333], {428})
        category = self.catalog.categories['category:428']
        self.assertEqual(set(category['children']), {333,336,335,404,399,418})
        for identifier in category['children']:
            self.assertEqual(self.catalog.get_resolution_status(identifier),'UNRESOLVED_REFERENCE')
            self.assertNotIn(f'topic:{identifier}',self.catalog.topics)
            self.assertNotIn('title',self.catalog.references[identifier])

    def test_scope_queries_do_not_allocate_or_delete_not_learned_nodes(self):
        global_view = self.catalog.get_projection('GLOBAL_CATALOG')
        self.assertEqual([len(global_view[k]) for k in ('categories','topics','unresolved_references','hierarchy_records')], [849,89,3017,3952])
        personal = self.catalog.get_projection('PERSONAL', course_ids=[8])
        self.assertEqual(len(personal['topics']),89)
        self.assertTrue(any(r['is_learned'] is False for r in personal['progress']['topics']))
        self.assertEqual(self.catalog.get_projection('PROJECT_CONTEXT',project_id=113),self.catalog.get_project_context(113))
        with self.assertRaises(ValueError):self.catalog.get_projection('COURSE',course_ids=[])

    def test_global_refresh_changes_and_missing_candidates(self):
        updated = copy.deepcopy(self.catalog)
        updated.categories['category:331']['title'] = 'Synthetic metadata change'
        updated.categories['category:331']['parent_id'] = 525
        updated.global_relations['prerequisite_records'].append({'source_id':9,'target_id':333})
        changes=compare_catalogs(self.catalog,updated)
        self.assertTrue({'GLOBAL_METADATA_CHANGE','GLOBAL_REPARENT','GLOBAL_RELATION_CHANGE','GLOBAL_CATALOG_ONLY'} <= set(changes['change_types']))
        removed=copy.deepcopy(self.catalog)
        removed.categories.pop('category:331')
        result=compare_catalogs(self.catalog,removed)
        self.assertEqual(result['categories']['missing_candidates'],['category:331'])
        self.assertIn('GLOBAL_MISSING_CATEGORY_CANDIDATE',result['change_types'])

    def test_missing_snapshot_positions_are_retained_and_reported(self):
        rows=[{k:v for k,v in r.items() if k!='fact_sources'} for r in self.o['categories']
              if r['id']!=4055 and 'category:4055' not in self.catalog.get_catalog_ancestors(r['id'])]
        later=sanitize({'log':{'entries':[entry('/api/topic-relations?page=1&page_size=1000',
                      {'meta':{'page':1,'has_next':False,'has_previous':False},'topic-relations':rows},
                      stamp='2027-03-01T12:00:00.000Z')]}})
        data=copy.deepcopy(self.data)
        data['catalog_observations']['observations/synthetic-refresh.json']=later
        refreshed=Catalog(data)
        self.assertIn('category:4055',refreshed.categories)
        result=compare_catalogs(self.catalog,refreshed)
        self.assertIn('category:4055',result['categories']['missing_candidates'])
        self.assertIn('GLOBAL_MISSING_CATEGORY_CANDIDATE',result['change_types'])
        self.assertIn('GLOBAL_RELATION_CHANGE',result['change_types'])

    def test_many_to_many_course_activation_reuses_identity(self):
        data = copy.deepcopy(self.data)
        course = copy.deepcopy(data['courses'][0]);course['id']=42
        data['courses'].append(course)
        c=Catalog(data)
        p=c.get_tracked_courses_projection([8,42])
        self.assertEqual(len(p['topics']),89)
        self.assertEqual(len(c.topics),89)
        course['topic_ids']=[333];course['category_ids']=[];course['project_ids']=[]
        c=Catalog(data);p=c.get_course_projection(42)
        self.assertEqual([r['id'] for r in p['unresolved_references']], [333])
        self.assertEqual(p['topics'], [])
        self.assertTrue(c.get_relevance(333,{'course_ids':[42]})['course_relevant'])
        self.assertEqual(len(c.topics),89)
        course['topic_ids']=[999999]
        self.assertEqual(Catalog(data).get_course_projection(42)['unknown_candidates'],[999999])

    def test_promotion_preserves_history_and_requires_explicit_metadata(self):
        # Synthetic future evidence is confined to the test, never repository data.
        o = copy.deepcopy(self.o)
        parent = self.catalog.references[333]['parent_ids'][0]
        source_id = 'source:' + 'f'*64
        record = {'id':333,'title':'Synthetic resolution','is_group':False,'parent_id':parent,
                  'resolution':'PARTIAL_TOPIC'}
        record['fact_sources']={k:[source_id] for k in record if k!='resolution'}
        o['source_pages'].append({'id':source_id,'method':'GET','path':'/api/topics/333','content_type':'application/json'})
        o['topics'].append(record)
        o['unresolved_references']=[r for r in o['unresolved_references'] if r['id']!=333]
        for r in o['hierarchy_records']:
            if r['child_id']==333:r['child_type']='TOPIC'
        promoted=self.catalog.promote_reference(333, ordered_catalog(o), 'observations/synthetic-future.json')
        self.assertEqual(promoted.get_resolution_status(333),'PARTIAL_TOPIC')
        self.assertEqual(self.catalog.get_resolution_status(333),'UNRESOLVED_REFERENCE')
        self.assertEqual(promoted.memberships[333],self.catalog.memberships[333])
        self.assertEqual(promoted.reference_history[333],self.catalog.reference_history[333])
        change=compare_catalogs(self.catalog,promoted)
        self.assertIn('REFERENCE_RESOLVED',change['change_types'])
        self.assertNotIn('GLOBAL_NEW_TOPIC',change['change_types'])
        with self.assertRaises(ValueError):self.catalog.promote_reference(333,self.o)

    def test_global_diff_is_separate_from_presentation_diff(self):
        active = active_projection(self.data)
        validate.validate(active)
        self.assertEqual(snapshot.index(self.data),snapshot.index(active))
        self.assertEqual(compare_catalogs(self.catalog,self.catalog)['change_types'],['NO_CHANGE'])
        report=summary(self.data)
        self.assertIn('GLOBAL_CATALOG_ONLY',report['change_types'])
        self.assertNotIn('GLOBAL_REPARENT',report['change_types'])
        self.assertFalse(report['active_projection_changed'])
        self.assertEqual(report['global_additions'],{'categories':803,'topics':0,'references':3017})

    def test_legacy_observations_still_load(self):
        personal,global_observations=load(ROOT/'data/knowledge/observations')
        self.assertEqual(len(personal),1)
        self.assertEqual(len(global_observations),1)
        self.assertEqual(next(iter(personal.values()))['learned_topics_count'],31)
        self.assertNotIn('observation_type',next(iter(personal.values())))

    def test_production_bytes_checkpoint_geometry_generation(self):
        data=active_projection(self.data)
        runtime=ROOT/'prototypes/knowledge-atlas-v6'
        checkpoint,before=state.read(ROOT/'state/knowledge-atlas')
        geometry=json.loads((ROOT/'docs/knowledge-map/geometry.js').read_text().removeprefix('globalThis.AtlasBuildGeometry=').strip().removesuffix(';'))
        candidate=state.complete(data,checkpoint,geometry)
        self.assertEqual(candidate,before)
        outputs=build.artifacts(runtime,data,checkpoint,geometry,candidate)
        production=build.production_outputs(outputs,ROOT/'docs/knowledge-atlas-preview')
        with tempfile.TemporaryDirectory(prefix='atlas-catalog-production-') as d:
            for name,payload in production.items():
                target=Path(d)/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
                self.assertEqual(target.read_bytes(),(ROOT/'docs/knowledge-map'/name).read_bytes(), name)
        self.assertEqual(set(production),{p.relative_to(ROOT/'docs/knowledge-map').as_posix()
                                        for p in (ROOT/'docs/knowledge-map').rglob('*') if p.is_file()})
        self.assertEqual(outputs['layout-checkpoint.json'],(ROOT/'state/knowledge-atlas/layout-checkpoint.json').read_bytes())
        self.assertEqual(checkpoint['presentation_generation'],0)
        self.assertEqual(snapshot.ordered_digest(geometry),before['geometry_fingerprint'])

    @unittest.skipUnless(os.environ.get('HYPERSKILL_GLOBAL_HAR'),'Optional local raw HAR acceptance test')
    def test_actual_har_idempotency_and_reordered_requests(self):
        har=json.loads(Path(os.environ['HYPERSKILL_GLOBAL_HAR']).read_text())
        first=snapshot.encode(sanitize(har))
        self.assertEqual(first,snapshot.encode(sanitize(har)))
        random.Random(42).shuffle(har['log']['entries'])
        self.assertEqual(first,snapshot.encode(sanitize(har)))
        self.assertEqual(first,snapshot.encode(self.o))


if __name__=='__main__':unittest.main()
