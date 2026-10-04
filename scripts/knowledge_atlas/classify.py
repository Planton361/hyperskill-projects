"""Explicit orthogonal contracts. Zero means an enforced, exact geometry guard."""
CONTRACTS = {
    'NO_CHANGE': ('none', 'any mutation', 0),
    'PROGRESS_ONLY': ('styling, counts, inspector', 'geography, checkpoint', 0),
    'PROJECT_STATE_ONLY': ('project/stage status, inspector', 'geography, checkpoint', 0),
    'PROJECT_EVIDENCE_ONLY': ('requirements, evidence, coverage', 'geography, checkpoint', 0),
    'RELATION_ONLY': ('relations, automatic LCA routes', 'geography, checkpoint', 0),
    'COURSE_MEMBERSHIP_ONLY': ('course membership, overlays, filters, counts', 'duplication, geography, checkpoint', 0),
    'NEW_TOPIC': ('append locally, reserve, bounded ancestor expansion', 'silent global rebalance', None),
    'REMOVED_TOPIC': ('remove row; retain surviving positions and capacity', 'global compaction', None),
    'NEW_CATEGORY': ('append stable sibling slot, bounded local expansion', 'silent global reset', None),
    'REMOVED_CATEGORY': ('remove empty category; retain surviving slots', 'implicit reparent', None),
    'REPARENT_CATEGORY': ('explicit migration only', 'ordinary update', None),
    'NEW_COURSE': ('membership; independently classify new taxonomy', 'topic duplication', 0),
    'LAYOUT_SCHEMA_CHANGE': ('explicit migration only', 'ordinary update', None),
    'LAYOUT_ALGORITHM_CHANGE': ('explicit migration only', 'ordinary update', None),
    'NEW_PROJECT': ('data-driven inspector, stages, coverage', 'geography, checkpoint', 0),
    'REMOVED_PROJECT': ('remove project evidence/UI', 'geography, checkpoint', 0),
    'REMOVED_COURSE': ('remove membership/UI', 'geography, checkpoint', 0),
    'REPARENT_TOPIC': ('explicit migration only', 'ordinary update', None),
    'METADATA_ONLY': ('data/inspector; title changes require review', 'silent geometry mutation', 0),
    'EVIDENCE_ONLY': ('provenance indexes', 'geography, checkpoint', 0),
}
STRUCTURAL = {'NEW_TOPIC', 'REMOVED_TOPIC', 'NEW_CATEGORY', 'REMOVED_CATEGORY',
              'REPARENT_CATEGORY', 'REPARENT_TOPIC', 'LAYOUT_SCHEMA_CHANGE', 'LAYOUT_ALGORITHM_CHANGE'}
MIGRATIONS = {'REPARENT_CATEGORY', 'REPARENT_TOPIC', 'LAYOUT_SCHEMA_CHANGE', 'LAYOUT_ALGORITHM_CHANGE'}
