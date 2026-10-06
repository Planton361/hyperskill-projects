import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'scripts'))
from knowledge_atlas import activation_persistence as AP, canonical as C, transaction
root,path,token,boundary=sys.argv[1:];C.writer_guard(root)
if boundary=='after_commit_record':
    original=transaction.journal_write
    def write(p,v):
        original(p,v)
        if v['phase']=='COMMITTED':os._exit(77)
    transaction.journal_write=write
if boundary=='after_cleanup':
    original=transaction.recover
    def recover(p,root=None):
        committed=Path(p).exists() and C.read(p)['phase']=='COMMITTED';original(p,root)
        if committed:os._exit(77)
    transaction.recover=recover
AP.approve(Path(root),Path(path),reviewed_fingerprint=token,fault=lambda n:os._exit(77) if n==boundary else None)
