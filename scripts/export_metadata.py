"""Validate explicit owner completion metadata independently of MyAtlas."""
from datetime import datetime


def validate_completion(value):
    if not isinstance(value, dict) or set(value) != {'project_id', 'status', 'attested_by', 'observed_at'}:
        raise ValueError('Completion requires exact project_id/status/attested_by/observed_at fields')
    if type(value['project_id']) is not int or value['project_id'] <= 0:
        raise ValueError('Explicit positive Hyperskill Project ID required')
    if value['status'] != 'completed' or value['attested_by'] != 'owner':
        raise ValueError('Explicit owner completion attestation required')
    stamp = value['observed_at']
    if not isinstance(stamp, str) or not stamp.endswith('Z'):
        raise ValueError('UTC observation timestamp required')
    datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    return value
