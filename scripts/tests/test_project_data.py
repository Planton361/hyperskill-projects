"""Thirty actual generic imports, in one disposable Git repository, with full data acceptance each."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ci_change import classify
from project_data import validate_data
from project_index import git

ROOT=Path(__file__).resolve().parents[2]

class ProjectDataTests(unittest.TestCase):
    def test_thirty_sequential_imports_use_same_data_path_and_preserve_baseline(self):
        atlas_env=os.environ.get('MYATLAS_ROOT')
        self.assertTrue(atlas_env,'MYATLAS_ROOT required; never silently skip reader acceptance')
        atlas=Path(atlas_env).resolve()
        with tempfile.TemporaryDirectory(prefix='thirty-universal-imports-') as folder:
            base=Path(folder).resolve();repo=base/'repo'
            subprocess.run(['git','clone','-q',str(ROOT),str(repo)],check=True)
            subprocess.run(['git','-C',str(repo),'remote','set-url','origin','https://github.com/Planton361/hyperskill-projects.git'],check=True)
            subprocess.run(['git','-C',str(repo),'config','user.name','Synthetic owner'],check=True)
            subprocess.run(['git','-C',str(repo),'config','user.email','fixture@example.invalid'],check=True)
            baseline=json.loads((atlas/'docs/contracts/hyperskill-baseline-v1.json').read_text())
            hashes={n:hashlib.sha256((repo/n).read_bytes()).hexdigest() for n in baseline['archive_sha256']}
            self.assertEqual(hashes,baseline['archive_sha256']);self.assertEqual(len(hashes),22)
            scopes=json.loads((atlas/'src/myatlas/knowledge-atlas-scope-pyramid/scope-index.json').read_text())
            known=next(p['scope_id'] for p in scopes['projects'] if p['state']=='KNOWN' and p['explicit_topic_ids'] and p['scope_id'] not in (113,229,380))
            unknown=next(p['scope_id'] for p in scopes['projects'] if p['state']=='UNKNOWN' and p['scope_id'] not in (113,229,380))
            previous=git(repo,'rev-parse','HEAD').decode().strip()
            initial=validate_data(repo,atlas,previous)
            ids=[known,unknown]+list(range(900001000,900001028))
            reports=[]
            for i,pid in enumerate(ids):
                source=base/f'owner-{i}';source.mkdir()
                choices=[{'Main.java':'solution'},{'main.py':'solution'},{'Main.kt':'solution'},{'main.js':'solution'},
                         {'source.future':'solution','program':'solution'},{'Main.java':'solution','helper.py':'solution','Extra.kt':'solution','input.bin':'resource'}]
                files=choices[i%len(choices)]
                for name,role in files.items():
                    (source/name).write_bytes(b'\x00\xff\x01' if role=='resource' else b'// topic_id=999999; verified=true; deliberately not executable syntax\n')
                selection=base/f'selection-{i}.json';selection.write_text(json.dumps({'schema':1,'files':files}))
                before={n:(source/n).read_bytes() for n in files}
                subprocess.run(['python3.12','-B',str(repo/'scripts/import-hyperskill-project'),str(source),'--files-from',str(selection),
                    '--project-url',f'https://hyperskill.org/projects/{pid}','--title',f'Synthetic project {i}',
                    '--confirmed-at','2026-10-08T12:00:00Z'],check=True,stdout=subprocess.DEVNULL)
                self.assertEqual(before,{n:(source/n).read_bytes() for n in files})
                subprocess.run(['git','-C',str(repo),'add','projects'],check=True)
                subprocess.run(['git','-C',str(repo),'commit','-qm',f'TEST ONLY import {i}'],check=True)
                head=git(repo,'rev-parse','HEAD').decode().strip()
                for event in ('push','pull_request'):
                    policy=classify(repo,previous,head,event)
                    self.assertEqual(policy['change_class'],'A');self.assertFalse(policy['full_required'])
                report=validate_data(repo,atlas,head);reports.append(report)
                self.assertEqual(report['completed_project_count'],4+i)
                self.assertEqual(report['completed_project_ids'],sorted([113,229,380,*ids[:i+1]]))
                self.assertEqual(report['verified_topic_ids'],initial['verified_topic_ids'])
                self.assertEqual(report['course_completion'],initial['course_completion'])
                if i: self.assertEqual(report['global']['learned'],reports[0]['global']['learned'])
                self.assertEqual(report['unmapped_project_ids'],ids[2:i+1])
                previous=head
            self.assertEqual(hashes,{n:hashlib.sha256((repo/n).read_bytes()).hexdigest() for n in hashes})
            print(json.dumps(dict(synthetic_imports=30,final_count=reports[-1]['completed_project_count'],final_revision=previous,
                                 index_sha256=reports[-1]['index_sha256'],baseline_files=22,verified=12,course_records=0)))
