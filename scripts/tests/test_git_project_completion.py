"""Git evidence and diff contracts; all commits/mutations occur in disposable repos."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT/'scripts/sync-project-completion.py'
CAT = 'src/myatlas/knowledge-atlas-scope-pyramid/catalog.json'
SCOPES = 'src/myatlas/knowledge-atlas-scope-pyramid/scope-index.json'
ACCEPTED = 'data/myatlas/accepted-sync.json'

class GitCompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.git('init','-q');self.git('config','user.email','fixture@example.invalid');self.git('config','user.name','Fixture')
        self.catalog=dict(topics=[dict(id=i) for i in (1,2,3)],categories=[dict(id=100)],memberships={str(i):[100] for i in (1,2,3)},evidence=[dict(id='direct',observed_on='2026-10-01')],progress=dict(topics=[dict(topic_id=1,is_learned=True,is_verified=True,evidence_ids=['direct']),dict(topic_id=2,is_learned=False,is_verified=False,evidence_ids=['direct'])],courses=[],projects=[],stages=[]))
        self.scopes=dict(courses=[dict(scope_id=1,state='KNOWN',explicit_topic_ids=[1,2,3])],projects=[dict(scope_id=i,state=state,explicit_topic_ids=ids) for i,state,ids in [(7,'KNOWN',[1,2]),(8,'KNOWN',[2,3]),(9,'UNKNOWN',None),(10,'KNOWN_EMPTY',[])]],stages=[dict(scope_id=70,state='KNOWN',explicit_topic_ids=[2])])
        self.write(CAT,self.catalog);self.write(SCOPES,self.scopes);self.commit()

    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.DEVNULL)
    def write(self,name,value):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value))
    def commit(self):
        self.git('add','.');self.git('commit','-qm','Disposable evidence fixture')
    def export(self,pid,name=None,status='completed'):
        folder='java/'+(name or str(pid))
        names=['build.gradle.kts','settings.gradle.kts','gradlew','gradlew.bat','gradle/wrapper/gradle-wrapper.jar','gradle/wrapper/gradle-wrapper.properties','src/main/java/Main.java']
        for n in names:
            p=self.root/folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
        meta=dict(schema=2,language='java',directory_name=folder.split('/')[-1],project_id=pid,files={n:hashlib.sha256(b'fixture').hexdigest() for n in names})
        if status:meta['completion']=dict(project_id=pid,status=status,attested_by='owner',observed_at='2026-10-08T12:00:00Z')
        self.write(folder+'/.hyperskill-import.json',meta)
        return folder,meta
    def run_sync(self,success=True):
        r=subprocess.run([sys.executable,'-B',str(CLI),'--root',str(self.root)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0 if success else 1,r.stderr)
        self.assertNotIn(str(self.root),r.stdout+r.stderr)
        return json.loads(r.stdout) if success else r
    def accept(self,result):
        self.write(ACCEPTED,result['projection']);self.commit()

    def test_new_overlap_repeat_and_reproducibility(self):
        baseline=self.run_sync();self.accept(baseline)
        self.export(7);self.export(8);self.export(7,'duplicate');self.commit()
        current=self.run_sync();p=current['projection'];d=current['changes']
        self.assertEqual(p['completed_project_ids'],[7,8]);self.assertEqual(p['completed_project_count'],2)
        self.assertEqual(p['effective_learned_topic_ids'],[1,2,3]);self.assertEqual(p['verified_topic_ids'],[1])
        self.assertEqual(d['newly_learned_topic_ids'],[2,3]);self.assertEqual(d['already_learned_topic_ids'],[1])
        self.assertEqual(d['impacted_scopes']['courses'],[1]);self.assertIn(70,d['impacted_scopes']['stages'])
        self.assertEqual(current,self.run_sync())
        (self.root/'java/7/src/main/java/Main.java').write_text('uncommitted tampering')
        self.assertEqual(current,self.run_sync())  # Reads Git, not dirty files.
        (self.root/'java/7/src/main/java/Main.java').write_text('fixture')
        self.accept(current);self.assertFalse(self.run_sync()['changes']['semantic_change'])
        clone=self.root.parent/(self.root.name+'-clone')
        subprocess.run(['git','clone','-q',str(self.root),str(clone)],check=True)
        self.addCleanup(lambda:__import__('shutil').rmtree(clone))
        result=subprocess.check_output([sys.executable,'-B',str(CLI),'--root',str(clone)])
        self.assertEqual(json.loads(result),self.run_sync())

    def test_incomplete_unknown_empty_missing_and_ambiguous(self):
        self.export(7,status=None);self.export(9);self.export(10);self.commit()
        p=self.run_sync()['projection'];self.assertEqual(p['completed_project_ids'],[9,10]);self.assertEqual(p['effective_learned_topic_ids'],[1])
        folder,meta=self.export(7);del meta['completion']['project_id'];self.write(folder+'/.hyperskill-import.json',meta);self.commit();self.run_sync(False)
        folder,meta=self.export(7);meta['project_id']=8;self.write(folder+'/.hyperskill-import.json',meta);self.commit();self.run_sync(False)
        self.export(7);(self.root/folder/'README.md').write_text('https://hyperskill.org/projects/8');self.commit();self.run_sync(False)
        (self.root/folder/'README.md').unlink();self.export(123456);self.commit();self.run_sync(False)

    def test_removal_revocation_independent_evidence(self):
        self.export(7);self.export(8);self.commit();old=self.run_sync();self.accept(old)
        self.export(7,status='revoked');self.commit()
        r=self.run_sync();self.assertEqual(r['changes']['removed_or_revoked_project_ids'],[7]);self.assertEqual(r['projection']['effective_learned_topic_ids'],[1,2,3]);self.assertEqual(r['projection']['verified_topic_ids'],[1]);self.assertIn(1,r['changes']['updated_provenance_topic_ids'])
        self.accept(r)
        import shutil
        shutil.rmtree(self.root/'java/8');self.commit();r=self.run_sync()
        self.assertEqual(r['projection']['effective_learned_topic_ids'],[1]);self.assertEqual(r['changes']['no_longer_effectively_learned_topic_ids'],[2,3])

    def test_tampered_missing_symlink_and_conflicting_duplicates(self):
        folder,_=self.export(7);self.commit()
        (self.root/folder/'src/main/java/Main.java').unlink();self.commit();self.run_sync(False)
        self.export(7);(self.root/folder/'src/main/java/Main.java').write_text('tampered');self.commit();self.run_sync(False)
        self.export(7);(self.root/folder/'link').symlink_to('/private/workspace');self.commit();self.run_sync(False)
        (self.root/folder/'link').unlink();self.export(7,'duplicate','revoked');self.commit();self.run_sync(False)

    def test_real_legacy(self):
        command=[sys.executable,'-B',str(CLI),'--previous',str(ROOT/'data/myatlas/progress.json')]
        result=json.loads(subprocess.check_output(command));p=result['projection']
        self.assertEqual(p['completed_project_ids'],[113]);self.assertEqual(len(p['project_learned_topic_ids']),26)
        self.assertEqual(p['global']['learned'],31);self.assertEqual(p['global']['verified'],12)
        self.assertFalse(result['changes']['semantic_change']);self.assertEqual(result,json.loads(subprocess.check_output(command)))

    def test_explicit_committed_course_completion_independent_of_projects(self):
        baseline=self.run_sync();self.accept(baseline)
        records=dict(schema=1,records=[dict(course_id=1,is_completed=True,observed_at='2026-10-08T14:00:00Z',source='owner',evidence_id='course-1-fixture')])
        self.write('data/myatlas/course-completions.json',records)
        self.assertIsNone(self.run_sync()['projection']['portfolio']['completed_course_count'])
        self.commit();result=self.run_sync()
        self.assertEqual(result['projection']['portfolio']['completed_course_count'],1)
        self.assertEqual(result['projection']['completed_project_ids'],[])
        self.assertEqual(result['projection']['effective_learned_topic_ids'],[1])
        self.assertEqual(result['projection']['verified_topic_ids'],[1])
        self.assertEqual(result['changes']['changed_course_completion_ids'],[1])
        self.assertEqual(result['changes']['impacted_scopes']['courses'],[1])
        self.assertTrue(any(e['path'].endswith('course-completions.json') for e in result['projection']['source']['evidence']))
        self.accept(result);self.assertFalse(self.run_sync()['changes']['semantic_change'])
