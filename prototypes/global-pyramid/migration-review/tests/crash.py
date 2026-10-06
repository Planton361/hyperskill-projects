"""Disposable process death injection; cannot target real root."""
import importlib.util
import os
from pathlib import Path
import sys
spec=importlib.util.spec_from_file_location('spatial_review',Path(__file__).resolve().parents[1]/'review.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
root,path,seal,boundary=sys.argv[1:5];root=M.disposable(root)
def fault(name):
    if name==boundary:os._exit(77)
if boundary=='after_candidate_construction':M.make_package(root,Path(sys.argv[5]),root.parent/(root.name+'-draft'),fault)
else:
    original=M.transaction.journal_write
    def write(path,value):
        original(path,value)
        if value['phase']=='COMMITTED':fault('after_durable_commit')
    M.transaction.journal_write=write
    original_recover=M.transaction.recover
    def recover(path,root=None):
        committed=Path(path).exists() and M.read(path)['phase']=='COMMITTED';original_recover(path,root)
        if committed:fault('after_cleanup')
    M.transaction.recover=recover
    M.apply_test(root,Path(path),M.read(seal),fault)
raise RuntimeError('fault boundary not reached: '+boundary)
