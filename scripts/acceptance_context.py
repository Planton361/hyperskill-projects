"""Environment for disposable MyAtlas acceptance, never production publication."""
import os


def isolated_myatlas_environment():
    """Keep tooling settings, but do not inherit another repository's revision/ref."""
    env = dict(os.environ)
    for name in ('GITHUB_SHA', 'GITHUB_REF', 'GITHUB_REF_NAME', 'GITHUB_REF_TYPE',
                 'GITHUB_HEAD_REF', 'GITHUB_BASE_REF'):
        env.pop(name, None)
    env['MYATLAS_PRE_RELEASE_PROGRESS'] = '1'
    return env
