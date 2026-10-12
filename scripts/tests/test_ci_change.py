"""Git event deltas cannot admit edits, renames or infrastructure to data-only CI."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from scripts.ci_change import classify

class ChangePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.git('init','-q','-b','main');self.git('config','user.name','Fixture');self.git('config','user.email','fixture@example.invalid')
        self.write('scripts/reader.js','accepted reader');self.base=self.commit()

    def git(self,*args):return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.DEVNULL)
    def write(self,name,raw):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(raw)
    def commit(self):
        self.git('add','-A');self.git('commit','-qm','Synthetic delta');return self.git('rev-parse','HEAD').decode().strip()
    def archive(self,pid=123):
        self.write(f'projects/{pid}/.hyperskill-import.json',json.dumps({'schema':4}))
        self.write(f'projects/{pid}/README.md','owner fixture')
        self.write(f'projects/{pid}/solution/program','text')
    def test_new_archives_push_and_pr_are_data_only(self):
        self.archive();self.archive(456);head=self.commit()
        for event in ('push','pull_request'):
            result=classify(self.root,self.base,head,event)
            self.assertEqual(result['change_class'],'A');self.assertEqual(result['project_ids'],[123,456])
    def test_existing_archive_addition_edit_delete_and_rename_are_full(self):
        self.archive();base=self.commit()
        for name in ('solution/new','solution/program','README.md'):
            with self.subTest(name=name):
                self.write('projects/123/'+name,'changed');head=self.commit()
                self.assertEqual(classify(self.root,base,head,'push')['change_class'],'B')
                base=head
        self.git('mv','projects/123','projects/456');head=self.commit()
        self.assertEqual(classify(self.root,base,head,'pull_request')['change_class'],'B')
    def test_mixed_policy_reader_validator_workflow_unknown_and_bad_id_are_full(self):
        for name in ('scripts/ci_change.py','scripts/validate-project-exports.py','scripts/reader.js','.github/workflows/check.yml','docs/contract.md','projects/0123/solution/code','projects/9007199254740992/solution/code'):
            with self.subTest(name=name):
                self.git('checkout','-q','-b','case'+str(len(self.git('branch'))),self.base)
                self.archive();self.write(name,'changed');head=self.commit()
                self.assertEqual(classify(self.root,self.base,head,'push')['change_class'],'B')
    def test_symlink_and_gitlink_fail_closed(self):
        self.archive();code=self.root/'projects/123/solution/program';code.unlink();code.symlink_to('/etc/hosts')
        self.assertEqual(classify(self.root,self.base,self.commit(),'push')['change_class'],'B')
        self.git('update-index','--add','--cacheinfo','160000',self.base,'projects/999/solution/submodule')
        self.git('commit','-qm','Fixture gitlink');head=self.git('rev-parse','HEAD').decode().strip()
        self.assertEqual(classify(self.root,self.base,head,'pull_request')['change_class'],'B')
    def test_missing_zero_base_nonfastforward_empty_and_health_are_full(self):
        self.archive();head=self.commit()
        for base in ('0'*40,'missing','f'*40,head):
            self.assertEqual(classify(self.root,base,head,'push')['change_class'],'B')
        self.assertEqual(classify(self.root,head,self.base,'push')['change_class'],'B')
        for event in ('schedule','workflow_dispatch'):
            self.assertEqual(classify(self.root,self.base,head,event)['change_class'],'C')
    def test_pr_merge_base_excludes_unrelated_base_updates(self):
        self.git('checkout','-qb','feature');self.archive();feature=self.commit()
        self.git('checkout','-q','main');self.write('scripts/base-change','base update');base=self.commit()
        self.git('checkout','-q','feature');self.git('merge','-q','--no-edit','main');merge=self.git('rev-parse','HEAD').decode().strip()
        self.assertEqual(classify(self.root,base,merge,'pull_request')['change_class'],'A')

    def test_workflow_requires_data_and_full_infrastructure_acceptance_without_pending_filters(self):
        root=Path(__file__).resolve().parents[2]
        workflow=(root/'.github/workflows/project-atlas-acceptance.yml').read_text()
        self.assertIn("if: needs.policy.outputs.class != 'A'",workflow)
        self.assertIn('needs: [policy, data-contract, pages-compatibility]',workflow)
        self.assertIn('test "$POLICY" = success && test "$DATA" = success',workflow)
        self.assertIn('test "$FULL" = success',workflow)
        self.assertIn('test "$FULL" = skipped',workflow)
        self.assertIn('scenario: [committed, java, python, unknown, unmapped, growth]',workflow)
        self.assertIn("'diff','--quiet',review,'origin/main'",workflow)
        self.assertIn("if os.environ['EVENT'] != 'pull_request':",workflow)
        for name in ('project-atlas-acceptance.yml','owner-publish-check.yml','projects.yml','pages-redirects.yml'):
            raw=(root/'.github/workflows'/name).read_text()
            self.assertNotIn('    paths:',raw)
            self.assertIn("base.stdout==Path(path).read_bytes()",raw)
            self.assertIn("if: steps.bootstrap.outputs.trusted == 'true'",raw)
        action=(root/'.github/actions/change-policy/action.yml').read_text()
        self.assertIn("base+':scripts/ci_change.py'",action)
        self.assertNotIn('eval(',action)
