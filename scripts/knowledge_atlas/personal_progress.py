"""Pure normalization of an explicit complete Course progress snapshot; no writers."""
from copy import deepcopy
from datetime import datetime
from . import validate
from .catalog import active_projection

FIELDS = {'topic_id', 'is_learned', 'is_completed', 'is_skipped', 'verification_status'}
SNAPSHOT_FIELDS = {'course_id', 'observed_at', 'topics', 'learned_topic_ids',
                   'learned_topics_count', 'skipped_topics_count', 'applied_topic_ids'}


def normalize(data, envelope):
    """Accept sanitized facts only, retain old evidence, recompute redundant indexes.

    Returns an in-memory snapshot. Validation fixtures are tagged in both their
    observation and provenance; callers must never ingest them into real Knowledge.
    """
    require = validate.require
    require(set(envelope) == {'observation', 'evidence'}, 'Explicit observation and provenance required')
    observation, evidence = deepcopy(envelope['observation']), deepcopy(envelope['evidence'])
    require(set(observation) == SNAPSHOT_FIELDS, 'Unknown/missing personal observation fields')
    require(set(evidence) == {'id', 'source', 'method', 'confidence', 'note'}, 'Unknown/missing provenance fields')
    require(all(isinstance(v, str) and v for v in evidence.values()), 'Nonempty provenance required')
    synthetic = evidence['source'] == 'validation-only'
    require((synthetic and evidence['method'] == 'synthetic_disposable_fixture') or
            (evidence['source'] == 'hyperskill' and evidence['method'] == 'user_supplied_authenticated_excerpt'),
            'Unsupported progress evidence provenance')
    require(evidence['confidence'] == 'explicit', 'Explicit personal evidence required')
    require(evidence['id'] not in {e['id'] for e in data['evidence']}, 'Evidence ID already exists')
    require('/' not in evidence['id'] and '..' not in evidence['id'], 'Invalid evidence ID')
    stamp = observation['observed_at']
    require(isinstance(stamp, str), 'Observation timestamp required')
    require(stamp.endswith('Z'), 'UTC observation timestamp required')
    observed_time = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    course = next((c for c in data['courses'] if c['id'] == observation['course_id']), None)
    require(course is not None, 'Unknown course; no membership inference')
    rows = observation['topics']
    require(isinstance(rows, list) and all(isinstance(r, dict) and set(r) == FIELDS for r in rows),
            'Unknown/missing personal topic fields')
    require(all(type(r['topic_id']) is int for r in rows), 'Numeric topic IDs required')
    require(len(rows) == len({r['topic_id'] for r in rows}) and
            {r['topic_id'] for r in rows} == set(course['topic_ids']), 'Complete explicit Course coverage required')
    for r in rows:
        require(all(type(r[f]) is bool for f in ('is_learned', 'is_completed', 'is_skipped')), 'Explicit booleans required')
        require(r['verification_status'] is None or r['verification_status'] in
                ('verified', 'evaluation', 'failed', 'not_verified', 'unknown'), 'Unknown verification status')
    learned = sorted(r['topic_id'] for r in rows if r['is_learned'])
    require(observation['learned_topic_ids'] == learned and observation['learned_topics_count'] == len(learned),
            'Observation learned aggregates disagree')
    require(observation['skipped_topics_count'] == sum(r['is_skipped'] for r in rows), 'Skipped aggregate disagrees')
    require(observation['applied_topic_ids'] is None, 'Application claims require separate explicit evidence')
    previous = [r for r in data['progress']['topics'] if r['course_id'] == course['id']]
    require({r['topic_id'] for r in previous} == set(course['topic_ids']), 'Unknown initial progress coverage')
    require(all(observed_time > datetime.fromisoformat(r['observed_at'].replace('Z', '+00:00')) for r in previous), 'Stale/conflicting observation timestamp')
    result = deepcopy(data)
    filename = 'observations/' + evidence['id'] + '.json'
    require(filename not in data['observations'], 'Observation filename already exists')
    observation['observation_type'] = 'personal_progress'
    if synthetic:
        observation['validation_only'] = True
    evidence.update(snapshot_file=filename, observed_at=stamp, observed_on=stamp[:10], fields=sorted(FIELDS))
    result['observations'][filename] = observation
    result['evidence'].append(evidence)
    by_id = {r['topic_id']: r for r in rows}
    changes = []
    for row in result['progress']['topics']:
        if row['course_id'] != course['id']:
            continue
        supplied = by_id[row['topic_id']]
        for field in sorted(FIELDS - {'topic_id'}):
            if row.get(field) != supplied[field]:
                changes.append({'topic_id': row['topic_id'], 'field': field,
                                'before': row.get(field), 'after': supplied[field]})
        row.update(supplied, is_verified=None if supplied['verification_status'] is None else
                   supplied['verification_status'] == 'verified', observed_at=stamp, evidence_ids=[evidence['id']])
    aggregate = next(r for r in result['progress']['courses'] if r['course_id'] == course['id'])
    old_evidence = {e['id']: e for e in data['evidence']}
    aggregate['evidence_ids'] = [i for i in aggregate['evidence_ids'] if not old_evidence[i].get('snapshot_file')] + [evidence['id']]
    aggregate.update(learned_topic_ids=learned, learned_topics_count=len(learned),
                     learned_observed_at=stamp, skipped_topics_count=observation['skipped_topics_count'],
                     verified_topic_ids=sorted(r['topic_id'] for r in rows if r['verification_status'] == 'verified'))
    validate.validate(active_projection(result))
    return result, {'changes': changes, 'validation_only': synthetic,
                    'observation_file': filename, 'evidence_id': evidence['id']}
