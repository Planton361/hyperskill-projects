"""Current architecture decision; historical strict-global reviews confer no approval."""
DECISION = 'adaptive-dual-view-1'
PRODUCTION_MIGRATION = 'PAUSED_PENDING_ADAPTIVE_VIEW_ACCEPTANCE'


def require_strict_migration_approval():
    raise ValueError('STRICT_GLOBAL_MIGRATION_PAUSED: dual-view architecture supersedes '
                     'strict Version A; all historical packages are non-applicable')
