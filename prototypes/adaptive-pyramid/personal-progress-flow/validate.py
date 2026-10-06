"""Focused disposable real-pipeline proof. Never writes accepted repository inputs."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas import adaptive_production as A, snapshot, validate
from knowledge_atlas.catalog import active_projection
from knowledge_atlas.personal_progress import normalize
spec = importlib.util.spec_from_file_location('progress_preview', ROOT / 'scripts/preview-adaptive-progress.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
data = snapshot.load_source(ROOT / A.KNOWLEDGE)
validate.validate(active_projection(data))
course = next(c for c in data['courses'] if c['id'] == 8)
rows = sorted((r for r in data['progress']['topics'] if r['course_id'] == 8), key=lambda r: r['topic_id'])
learned_id = next(r['topic_id'] for r in rows if r['is_learned'] is False and r['topic_id'] in course['topic_ids'])
verified_id = next(r['topic_id'] for r in rows if r['is_learned'] is True and r['is_verified'] is False)
original = next(o for o in data['observations'].values() if o['course_id'] == 8)


def fixture(name, stamp, learn=False, verify=False):
    observation = copy.deepcopy(original)
    observation['observed_at'] = stamp
    if learn:
        next(r for r in observation['topics'] if r['topic_id'] == learned_id)['is_learned'] = True
    if verify:
        next(r for r in observation['topics'] if r['topic_id'] == verified_id)['verification_status'] = 'verified'
    observation['learned_topic_ids'] = sorted(r['topic_id'] for r in observation['topics'] if r['is_learned'])
    observation['learned_topics_count'] = len(observation['learned_topic_ids'])
    return {'observation': observation, 'evidence': {'id': 'validation-only-' + name,
            'source': 'validation-only', 'method': 'synthetic_disposable_fixture', 'confidence': 'explicit',
            'note': 'SYNTHETIC / DISPOSABLE VALIDATION ONLY. Not a Hyperskill-reported event; never ingest into accepted Knowledge.'}}


def run(name, envelope, source=ROOT):
    # Exercise the public CLI, not generated-model edits or renderer mutation.
    input_file = HERE / (name + '-observation.json')
    input_file.write_bytes(snapshot.encode(envelope))
    report = json.loads(subprocess.check_output([sys.executable, '-B', str(ROOT / 'scripts/preview-adaptive-progress.py'),
                '--source', str(source), '--observation', str(input_file), '--json'], text=True))
    sandbox = Path(report['disposable_root'])
    if source == ROOT:
        assert A.files(sandbox / 'baseline') == A.files(ROOT / A.PRODUCTION), 'Baseline is not exact deployed Production'
    assert report['production_files_changed'] == ['model.json', 'release-manifest.json']
    loaded = snapshot.load_source(sandbox / A.KNOWLEDGE)
    validate.validate(active_projection(loaded))
    for table in ('courses', 'categories', 'topics', 'projects', 'stages', 'edges'):
        assert loaded[table] == data[table], table
    assert loaded['progress']['projects'] == data['progress']['projects']
    assert all(e in loaded['evidence'] for e in data['evidence']), 'Historical evidence lost'
    assert report['state_unchanged'] and report['global_reference_equal']
    assert A.bound_tree(sandbox, A.STATE) == A.bound_tree(ROOT, A.STATE)
    actual = json.loads((sandbox / 'candidate/model.json').read_bytes())
    assert actual['progress'] == loaded['progress']['topics']
    assert actual['personal'] == json.loads((ROOT / 'docs/knowledge-map/model.json').read_bytes())['personal']
    assert json.loads((sandbox / 'baseline/model.json').read_bytes())['entities'] == actual['entities']
    return report


def main():
    learned = fixture('learned', '2026-10-06T00:00:00Z', learn=True)
    verified = fixture('verified', '2026-10-06T01:00:00Z', verify=True)
    # Focused schema/default-deny cases through the shared normalizer.
    rejected = []
    for name, mutate in [
        ('unsafe field', lambda o: o['observation'].update(account_id='forbidden')),
        ('nonboolean learned', lambda o: o['observation']['topics'][0].update(is_learned=1)),
        ('partial coverage', lambda o: o['observation']['topics'].pop()),
        ('count-only inference', lambda o: o['observation'].update(learned_topics_count=33)),
        ('application inference', lambda o: o['observation'].update(applied_topic_ids=[learned_id])),
        ('duplicate evidence', lambda o: o['evidence'].update(id=data['evidence'][0]['id'])),
        ('stale observation', lambda o: o['observation'].update(observed_at=original['observed_at'])),
        ('unsafe snapshot path', lambda o: o['evidence'].update(id='../escape')),
        ('existing snapshot filename', lambda o: o['evidence'].update(id='learned-2026-10-01')),
    ]:
        bad = copy.deepcopy(learned)
        mutate(bad)
        try:
            normalize(data, bad)
        except (ValueError, TypeError):
            rejected.append(name)
        else:
            raise AssertionError('Accepted invalid observation: ' + name)
    # A malicious TMPDIR or allocator result must fail before any file copying.
    for forbidden in (ROOT, ROOT / A.KNOWLEDGE, ROOT / A.STATE, ROOT / A.PRODUCTION):
        with patch.object(module.tempfile, 'gettempdir', return_value=str(forbidden)), patch.object(module.shutil, 'copytree') as copy_tree:
            try:
                module.preview(ROOT, learned)
            except ValueError:
                pass
            else:
                raise AssertionError('Repository temporary directory accepted')
            copy_tree.assert_not_called()
        with patch.object(module.tempfile, 'mkdtemp', return_value=str(forbidden)), patch.object(module.shutil, 'copytree') as copy_tree:
            try:
                module.preview(ROOT, learned)
            except ValueError:
                pass
            else:
                raise AssertionError('Real-root fixture publication accepted')
            copy_tree.assert_not_called()
    safety = {'redirected_temp_directory_refused': True, 'real_root_publication_refused': True,
              'real_knowledge_state_production_writes': False}
    a, b = run('learned', learned), run('verified', verified)
    assert a['before'] == b['before'] == {'learned': 31, 'verified': 12}
    assert a['after'] == {'learned': 32, 'verified': 12}
    assert b['after'] == {'learned': 31, 'verified': 13}
    assert a['semantic_diff']['changes'] == [{'topic_id': learned_id, 'field': 'is_learned', 'before': False, 'after': True}]
    assert b['semantic_diff']['changes'] == [{'topic_id': verified_id, 'field': 'verification_status', 'before': next(r['verification_status'] for r in rows if r['topic_id'] == verified_id), 'after': 'verified'}]
    sequential = run('sequential', fixture('sequential', '2026-10-06T02:00:00Z', learn=True, verify=True), Path(a['disposable_root']))
    assert sequential['before'] == a['after'] and sequential['after'] == {'learned': 32, 'verified': 13}
    assert len(sequential['semantic_diff']['changes']) == 1
    result = {'status': 'PASS', 'learned_topic_id': learned_id, 'verified_topic_id': verified_id,
              'learned_topic_title': next(t['title'] for t in data['topics'] if t['id'] == learned_id),
              'verified_topic_title': next(t['title'] for t in data['topics'] if t['id'] == verified_id),
              'schema_rejections': rejected, 'disposable_safety': safety, 'scenarios': {'learned': a, 'verified': b, 'sequential': sequential}}
    (HERE / 'pipeline-results.json').write_bytes(snapshot.encode(result))
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
