"""Validate explicit owner completion metadata independently of MyAtlas."""
from datetime import datetime, timezone
import re


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
    if not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z', stamp):
        raise ValueError('Exact UTC completion timestamp required')
    if datetime.fromisoformat(stamp.replace('Z', '+00:00')) > datetime.now(timezone.utc):
        raise ValueError('Completion timestamp is in the future')
    return value
