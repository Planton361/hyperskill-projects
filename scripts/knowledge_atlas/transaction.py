"""POSIX transaction: atomic directory exchange, durable journal, rollback/recovery."""
import contextlib
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def durable_file(path, content):
    with open(path, 'wb') as handle:
        handle.write(content); handle.flush(); os.fsync(handle.fileno())


def inventory(path):
    if not path.exists(): return None
    h = hashlib.sha256()
    for p in sorted(path.rglob('*')):
        if p.is_symlink(): raise ValueError('transaction destination contains symlink: ' + str(p))
        if p.is_file():
            h.update(p.relative_to(path).as_posix().encode()); h.update(b'\0'); h.update(p.read_bytes())
    return h.hexdigest()


@contextlib.contextmanager
def lock(root, write=False):
    """Directory flock: no lock file or read-only filesystem mutation."""
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        try: fcntl.flock(fd, (fcntl.LOCK_EX if write else fcntl.LOCK_SH) | fcntl.LOCK_NB)
        except BlockingIOError as e: raise ValueError('UPDATE_IN_PROGRESS: another Atlas operation holds the lock') from e
        yield
    finally: os.close(fd)


def exchange(a, b):
    """Linux renameat2 exchange is atomic even for non-empty directories."""
    libc = ctypes.CDLL(None, use_errno=True)
    fn = getattr(libc, 'renameat2', None)
    if fn is None: raise ValueError('ATOMIC_EXCHANGE_UNSUPPORTED: Linux renameat2 required')
    if fn(-100, os.fsencode(a), -100, os.fsencode(b), 2):
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code))


def journal_write(path, value):
    tmp = path.with_suffix('.tmp')
    durable_file(tmp, (json.dumps(value, sort_keys=True, indent=2)+'\n').encode())
    os.replace(tmp, path); sync_dir(path.parent)


def recover(journal, root=None):
    """Explicit writer recovery; readers only report journal presence."""
    journal = Path(journal)
    if not journal.exists(): return
    value = json.loads(journal.read_text())
    if value.get('schema_version') != 1: raise ValueError('unknown transaction journal schema')
    if value.get('phase') not in ('COMMITTING','COMMITTED'): raise ValueError('unknown transaction phase')
    for item in value['entries']:
        target, stage = Path(item['target']), Path(item['stage'])
        if stage.parent != target.parent or not stage.name.startswith('.atlas-candidate-') or stage.is_symlink():
            raise ValueError('RECOVERY_REQUIRED: invalid candidate directory')
        if root:
            root = Path(root).resolve()
            if not (target == root/'state/knowledge-atlas' or target == root/'docs/knowledge-atlas-preview' or
                    target.is_relative_to(root/'prototypes')):
                raise ValueError('RECOVERY_REQUIRED: unauthorized journal target')
    if value['phase'] != 'COMMITTED':
        for item in reversed(value['entries']):
            target, stage = Path(item['target']), Path(item['stage'])
            actual = inventory(target)
            if actual == item['candidate']:
                if item['existed']:
                    if inventory(stage) != item['before']: raise ValueError('RECOVERY_REQUIRED: previous directory unavailable')
                    exchange(target, stage)
                else: os.replace(target, stage)
                sync_dir(target.parent)
            elif actual != item['before']:
                raise ValueError('RECOVERY_REQUIRED: external modification prevents safe rollback')
    for item in value['entries']:
        stage = Path(item['stage'])
        if stage.exists(): shutil.rmtree(stage)
    journal.unlink(); sync_dir(journal.parent)


def publish(root, destinations, fault=None, preflight=None, journal=None):
    """All candidates validated before entry. All visible targets rollback on failure."""
    root = Path(root)
    journal = Path(journal or root / 'state/.knowledge-atlas-transaction.json')
    journal.parent.mkdir(parents=True, exist_ok=True)
    if journal.exists(): raise ValueError('RECOVERY_REQUIRED: run --recover-transaction')
    entries = []
    try:
        for target, outputs in destinations:
            target = Path(target); target.parent.mkdir(parents=True, exist_ok=True)
            stage = Path(tempfile.mkdtemp(prefix='.atlas-candidate-', dir=target.parent))
            entry = {'target': str(target), 'stage': str(stage), 'existed': target.exists(), 'before': inventory(target)}
            entries.append(entry)
            for name, content in outputs.items():
                p = stage / name; p.parent.mkdir(parents=True, exist_ok=True); durable_file(p, content)
            for directory in sorted((p for p in stage.rglob('*') if p.is_dir()), reverse=True): sync_dir(directory)
            sync_dir(stage); entry['candidate'] = inventory(stage)
        if preflight: preflight()
        value = {'schema_version': 1, 'phase': 'COMMITTING', 'entries': entries}
        journal_write(journal, value)
        if fault: fault('before_final_rename')
        for i, item in enumerate(entries):
            target, stage = Path(item['target']), Path(item['stage'])
            if item['existed']: exchange(target, stage)
            else: os.replace(stage, target)
            sync_dir(target.parent)
            if fault: fault('after_publish_' + str(i))
        value['phase'] = 'COMMITTED'; journal_write(journal, value)
    except BaseException:
        if journal.exists(): recover(journal,root)
        else:
            for item in entries:
                p = Path(item['stage'])
                if p.exists(): shutil.rmtree(p)
        raise
    # A durable COMMITTED record is the commit point. Cleanup failure is recoverable,
    # and must never be reported as an aborted update after publication succeeded.
    try: recover(journal,root)
    except OSError: pass
