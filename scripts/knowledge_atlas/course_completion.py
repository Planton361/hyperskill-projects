"""Explicit public Course completion records, independent of Topic/Project coverage."""
from copy import deepcopy
from datetime import datetime
import re

def validate_records(value, scopes):
    if not isinstance(value, dict) or set(value) != {'schema', 'records'} or type(value['schema']) is not int or value['schema'] != 1 or not isinstance(value['records'], list):
        raise ValueError('Course completion envelope requires schema 1 and records')
    ids = {c['scope_id'] for c in scopes['courses']}
    seen = set()
    for row in value['records']:
        if not isinstance(row, dict) or set(row) != {'course_id', 'is_completed', 'observed_at', 'source', 'evidence_id'}:
            raise ValueError('Exact Course completion fields required')
        if type(row['course_id']) is not int or row['course_id'] not in ids or type(row['is_completed']) is not bool:
            raise ValueError('Exact catalog Course ID and completion boolean required')
        if row['source'] not in ('owner', 'hyperskill'):
            raise ValueError('Explicit owner attestation or observed Hyperskill completion required')
        if not isinstance(row['evidence_id'], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}', row['evidence_id']) or row['evidence_id'] in seen:
            raise ValueError('Unique public evidence ID required')
        seen.add(row['evidence_id'])
        stamp = row['observed_at']
        if not isinstance(stamp, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z', stamp):
            raise ValueError('UTC evidence timestamp required')
        datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    result = deepcopy(value)
    result['records'].sort(key=lambda r:(r['course_id'], r['observed_at'], r['evidence_id']))
    return result
