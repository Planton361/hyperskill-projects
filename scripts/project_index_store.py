"""Append-only own-repository Git storage and verified Pages publication inputs."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.error import HTTPError
from urllib.request import Request, HTTPRedirectHandler, build_opener

from project_index import (REPOSITORY, ORIGIN, RAW, SHA, ROOT, git, repository,
                           revision, tree, blob, decode, encode, sha, generate,
                           validate_index, pointer, validate_pointer)

REF = 'refs/heads/portfolio-index-store'
CURRENT = 'https://planton361.github.io/hyperskill-projects/portfolio/current.json'
MAX_BYTES = 64 * 1024 * 1024

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Redirected publication URL refused before following it')

def urlopen(request,timeout):
    return build_opener(NoRedirect()).open(request,timeout=timeout)

def ancestor(root, older, newer):
    result=subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',older,newer],
                          env=dict(os.environ,GIT_NO_REPLACE_OBJECTS='1'),capture_output=True)
    if result.returncode not in (0,1):
        raise ValueError('Cannot establish source revision ancestry')
    return result.returncode == 0

def remote_sha(root, ref):
    lines=git(root,'ls-remote','origin',ref).decode().splitlines()
    if not lines: return None
    if len(lines)!=1 or lines[0].split()[1]!=ref or not SHA.fullmatch(lines[0].split()[0]):
        raise ValueError('Ambiguous remote revision')
    return lines[0].split()[0]

def current_main(root, selected):
    if remote_sha(root,'refs/heads/main') != selected:
        raise ValueError('Stale workflow: selected commit is no longer canonical main')

def load_store(root, commit):
    if commit is None: return {}
    revision(root,commit)
    items={}
    for name,(mode,kind,oid) in tree(root,commit).items():
        match=re.fullmatch(r'portfolio/revisions/([a-f0-9]{40})/index\.json',name)
        if not match or mode!='100644' or kind!='blob':
            raise ValueError('Corrupt/non-regular immutable store inventory')
        source=match[1]; raw=blob(root,oid)
        validate_index(root,raw,source)
        items[source]=raw
    if not items: raise ValueError('Existing store must not silently become empty')
    return items

def fetch_store(root):
    tip=remote_sha(root,REF)
    if tip:
        git(root,'fetch','--no-tags','origin',REF)
        if git(root,'rev-parse','FETCH_HEAD').decode().strip()!=tip:
            raise ValueError('Concurrent immutable store update; retry from fresh inputs')
    return tip,load_store(root,tip)

def get(url, *, missing=False):
    """Bounded HTTPS fetch, no host-changing redirects and no empty fallback."""
    if not (url==CURRENT or re.fullmatch(re.escape(RAW)+r'/[a-f0-9]{40}/portfolio/revisions/[a-f0-9]{40}/index\.json',url)):
        raise ValueError('Untrusted publication URL')
    try:
        with urlopen(Request(url,headers={'Cache-Control':'no-cache','Accept':'application/json'}),timeout=30) as response:
            if response.geturl()!=url: raise ValueError('Redirected publication URL refused')
            raw=response.read(MAX_BYTES+1)
    except HTTPError as error:
        if missing and error.code==404: return None
        raise ValueError('Publication source unavailable; last-known-good retained') from error
    if len(raw)>MAX_BYTES: raise ValueError('Oversized publication source')
    return raw

def previous_pointer(root, items, *, selected=None, bootstrap=False, fetch=get):
    raw=fetch(CURRENT,missing=True)
    if raw is None:
        if not bootstrap or set(items)-{selected}:
            raise ValueError('Missing previous pointer: explicit reviewed bootstrap/recovery required')
        return None
    p=decode(raw)
    if not isinstance(p,dict) or set(p)!={'schema','repository','revision','index_url','index_sha256'}:
        raise ValueError('Invalid previous pointer fields')
    payload=fetch(p.get('index_url',''))  # host checked before any network request
    validate_pointer(raw,payload)
    validate_index(root,payload,p['revision'])
    if items.get(p['revision'])!=payload:
        raise ValueError('Published pointer payload absent/conflicting in durable store')
    return raw

def stage(root, rev, *, bootstrap=False, fetch=get):
    """Persist immutable payload first; never touch the live pointer here."""
    root=repository(root); revision(root,rev); current_main(root,rev)
    raw=generate(root,rev); validate_index(root,raw,rev)
    tip,items=fetch_store(root)
    prior=previous_pointer(root,items,selected=rev,bootstrap=bootstrap,fetch=fetch)
    for source in items:
        if not ancestor(root,source,rev):
            raise ValueError('Stale/divergent source revision would overwrite newer history')
    if rev in items:
        if items[rev]!=raw: raise ValueError('Attempt to mutate a published immutable revision')
        return tip,items,prior
    items[rev]=raw
    # Isolated temporary index: no working-tree or real Git-index mutation.
    with tempfile.TemporaryDirectory(prefix='portfolio-store-index-') as folder:
        env=dict(os.environ,GIT_NO_REPLACE_OBJECTS='1',GIT_INDEX_FILE=str(Path(folder)/'index'),
                 GIT_AUTHOR_NAME='github-actions[bot]',GIT_COMMITTER_NAME='github-actions[bot]',
                 GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',
                 GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
        def command(*args,input=None):
            return subprocess.check_output(['git','-C',str(root),*args],input=input,env=env)
        command('read-tree',tip if tip else '--empty')
        oid=command('hash-object','-w','--stdin',input=raw).decode().strip()
        command('update-index','--add','--cacheinfo',f'100644,{oid},portfolio/revisions/{rev}/index.json')
        tree_id=command('write-tree').decode().strip()
        commit=command('commit-tree',tree_id,*(['-p',tip] if tip else []),input=f'Validated project index {rev}\n'.encode()).decode().strip()
    if load_store(root,commit)!=items:
        raise ValueError('Immutable store preservation check failed')
    current_main(root,rev)
    if remote_sha(root,REF)!=tip:
        raise ValueError('Concurrent publication changed durable store; retry')
    # Ordinary Git fast-forward refuses competing writers, including initial creation.
    git(root,'push','origin',commit+':'+REF)
    if remote_sha(root,REF)!=commit:
        raise ValueError('Interrupted/concurrent store push; retry, never force')
    return commit,items,prior

def prepare(root, rev, destination, *, bootstrap=False, fetch=get, guard=None):
    """Return validated artifact inputs only after immutable HTTP bytes are available."""
    commit,items,prior=stage(root,rev,bootstrap=bootstrap,fetch=fetch)
    raw=items[rev]
    candidate=pointer(rev,commit,raw)
    url=decode(candidate)['index_url']
    served=fetch(url)
    if served!=raw: raise ValueError('Immutable payload not reachable/byte-identical; pointer withheld')
    validate_index(root,served,rev); validate_pointer(candidate,served)
    current_main(root,rev)
    # Reject a changed published pointer between initial read and artifact build.
    current=fetch(CURRENT,missing=True)
    if current!=prior: raise ValueError('Concurrent live pointer update; candidate withheld')
    destination=Path(destination)
    if destination.exists() or any(p.is_symlink() for p in (destination,*destination.parents)):
        raise ValueError('Fresh safe publication staging directory required')
    destination.mkdir(parents=True)
    for source,payload in sorted(items.items()):
        path=destination/'revisions'/source/'index.json'; path.parent.mkdir(parents=True); path.write_bytes(payload)
    # Pointer is written last and with same-directory atomic replacement.
    temporary=destination/'current.pending'
    temporary.write_bytes(candidate); temporary.replace(destination/'current.json')
    if guard is not None:
        Path(guard).write_bytes(encode(dict(revision=rev,
            previous_pointer_sha256=sha(prior) if prior is not None else None,
            candidate_pointer_sha256=sha(candidate))))
    return candidate

def publication_guard(root, rev, portfolio, guard, *, fetch=get):
    """Check again immediately before the one serialized Pages deployment."""
    current_main(root,rev)
    validate_bundle(root,portfolio,rev)
    record=decode(Path(guard).read_bytes())
    candidate=(Path(portfolio)/'current.json').read_bytes()
    if record.get('revision')!=rev or record.get('candidate_pointer_sha256')!=sha(candidate):
        raise ValueError('Tampered publication guard/candidate')
    prior=fetch(CURRENT,missing=True)
    if (sha(prior) if prior is not None else None)!=record.get('previous_pointer_sha256'):
        raise ValueError('Concurrent live pointer update before deployment')
    p=decode(candidate);payload=fetch(p['index_url'])
    validate_pointer(candidate,payload);validate_index(root,payload,rev)
    current_main(root,rev)

def refuse_index_removal(*,fetch=get):
    if fetch(CURRENT,missing=True) is not None:
        raise ValueError('Index already exists: disabled mode must not erase retained portfolio')

def validate_bundle(root, portfolio, rev):
    portfolio=Path(portfolio)
    if any(p.is_symlink() or not (p.is_file() or p.is_dir()) for p in (portfolio,*portfolio.rglob('*'))):
        raise ValueError('Unsafe portfolio artifact member')
    files={p.relative_to(portfolio).as_posix():p.read_bytes() for p in portfolio.rglob('*') if p.is_file()}
    if 'current.json' not in files: raise ValueError('Missing artifact pointer')
    raw=files.pop('current.json'); items={}
    for name,payload in files.items():
        match=re.fullmatch(r'revisions/([a-f0-9]{40})/index\.json',name)
        if not match: raise ValueError('Unexpected portfolio artifact member')
        validate_index(root,payload,match[1]); items[match[1]]=payload
    if rev not in items: raise ValueError('Missing current artifact payload')
    validate_pointer(raw,items[rev])
    return items
