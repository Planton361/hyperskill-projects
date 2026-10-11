"""Versioned synthetic archives, adversarial inventories and reader parity."""
import copy
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import unittest
from unittest.mock import patch
from scripts.tests import test_import


class UniversalValidationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=test_import.ImportTests('test_dry_run_is_read_only_and_reports_exact_owner_evidence')
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.repo,self.archive=self.fixture.repo,self.fixture.target
        with patch.object(sys,'path',[str(self.repo/'scripts'),*sys.path]):
            self.validate=runpy.run_path(str(self.repo/'scripts/validate-project-exports.py'))['validate']
        self.fixture.invoke(); self.fixture.commit_archive()
        self.original=self.fixture.git('rev-parse','HEAD').decode().strip()
        self.baseline=self.fixture.manifest()
        atlas=os.environ.get('MYATLAS_ROOT')
        self.reader=runpy.run_path(str(Path(atlas)/'scripts/knowledge_atlas/external_export_scan.py'))['scan'] if atlas else None

    def assert_reader(self, accepted):
        if self.reader:
            actual=self.reader(self.repo,{'projects':[]})
            self.assertEqual(not actual['rejected'],accepted,actual)
            if accepted:
                self.assertEqual(actual['learned_topic_ids'],[])
                self.assertEqual(actual['completion_register']['unmapped_project_ids'],[7])

    def commit_mutation(self):
        self.fixture.git('add','-A','projects'); self.fixture.git('commit','-qm','TEST ONLY malformed archive')

    def restore_fixture(self):
        # Only disposable Git fixture paths are restored between adversarial cases.
        self.fixture.git('reset','--hard',self.original)

    def write_manifest(self, value):
        (self.archive/'.hyperskill-import.json').write_text(json.dumps(value))

    def test_positive_versioned_archive_agrees_with_merged_reader(self):
        self.assertEqual(self.validate(self.repo)[0]['project_id'],7)
        self.assert_reader(True)

    def test_missing_additional_tampered_files_and_hashes_are_rejected_by_both(self):
        for mutation in ('missing','extra','bytes','hash','role','unlisted-directory'):
            with self.subTest(mutation=mutation):
                self.restore_fixture()
                code=self.archive/self.fixture.code_path
                manifest=copy.deepcopy(self.baseline)
                if mutation=='missing': code.unlink()
                elif mutation=='extra': (self.archive/'solution/extra').write_text('extra')
                elif mutation=='bytes': code.write_text('modified')
                elif mutation=='hash': manifest['files'][self.fixture.code_path]['sha256']='0'*64; self.write_manifest(manifest)
                elif mutation=='role': manifest['files'][self.fixture.code_path]['role']='verified'; self.write_manifest(manifest)
                else: (self.archive/'original-solution').mkdir(); (self.archive/'original-solution/code').write_text('unexpected')
                self.commit_mutation()
                with self.assertRaises(ValueError): self.validate(self.repo)
                self.assert_reader(False)

    def test_exact_manifest_identity_fields_times_and_roles_fail_closed(self):
        mutations=[('schema',True),('schema',3),('mode','source-only'),('project_id',True),
                   ('project_id','7'),('project_id',9007199254740992),('project_url','https://hyperskill.org/projects/07'),
                   ('languages',['Kotlin','kotlin']),('title',' bad '),('extra','topic_id=999999')]
        for key,value in mutations:
            with self.subTest(key=key,value=value):
                self.restore_fixture(); manifest=copy.deepcopy(self.baseline); manifest[key]=value
                self.write_manifest(manifest); self.commit_mutation()
                with self.assertRaises((ValueError,TypeError)): self.validate(self.repo)
                self.assert_reader(False)
        for key,value in [('project_id',8),('status','revoked'),('attested_by','academy'),
                          ('confirmed_at','2026-02-30T00:00:00Z'),('completed_at','2026-10-09T00:00:00Z')]:
            self.restore_fixture(); manifest=copy.deepcopy(self.baseline); manifest['completion'][key]=value
            self.write_manifest(manifest); self.commit_mutation()
            with self.assertRaises(ValueError): self.validate(self.repo)
            self.assert_reader(False)

    def test_duplicate_json_keys_rejected_in_committed_manifest(self):
        path=self.archive/'.hyperskill-import.json'
        path.write_text(path.read_text().replace('"schema": 4','"schema": 4, "schema": 4'))
        self.commit_mutation()
        with self.assertRaisesRegex(ValueError,'Duplicate'): self.validate(self.repo)
        self.assert_reader(False)

    def test_duplicate_ids_across_legacy_formats_and_four_are_prevented(self):
        # Versioned copies are in this disposable repository only.
        for title in ('Simple Chat Bot with Java','My First Project with Java','Zookeeper with Java'):
            shutil.copytree(test_import.INFRA/'java'/title,self.repo/'java'/title)
        self.fixture.git('add','java'); self.fixture.git('commit','-qm','TEST ONLY immutable historical evidence copies')
        self.assertEqual({r['project_id'] for r in self.validate(self.repo)},{7,113,229,380})
        for pid in (113,229,380):
            (self.fixture.source/'course-remote-info.yaml').write_text(f'hyperskill_project:\n  id: {pid}\n')
            self.assertIn('Duplicate',self.fixture.invoke(success=False))
        duplicate=self.repo/'projects/113'; shutil.copytree(self.archive,duplicate)
        manifest=copy.deepcopy(self.baseline); manifest['project_id']=113; manifest['project_url']='https://hyperskill.org/projects/113'; manifest['completion']['project_id']=113
        # Duplicate ID must fail even when its entire own inventory is valid.
        readme=duplicate/'README.md'; readme.write_text('Project: https://hyperskill.org/projects/113\n')
        import hashlib
        manifest['files']['README.md']['sha256']=hashlib.sha256(readme.read_bytes()).hexdigest()
        (duplicate/'.hyperskill-import.json').write_text(json.dumps(manifest))
        self.commit_mutation()
        with self.assertRaisesRegex(ValueError,'Duplicate'): self.validate(self.repo)

    def test_symlink_and_gitlink_objects_rejected_before_blob_reads(self):
        path=self.archive/self.fixture.code_path; path.unlink()
        path.symlink_to(self.fixture.source/'course-info.yaml')
        self.commit_mutation()
        with patch.dict(self.validate.__globals__,git=lambda root,*args: (_ for _ in ()).throw(AssertionError('Blob read before preflight')) if args[0]=='cat-file' else subprocess_git(root,*args)):
            with self.assertRaisesRegex(ValueError,'Non-regular'): self.validate(self.repo)
        self.assert_reader(False)
        self.restore_fixture()
        self.fixture.git('update-index','--add','--cacheinfo','160000,'+self.original+',projects/8')
        self.fixture.git('commit','-qm','TEST ONLY forbidden submodule')
        with self.assertRaisesRegex(ValueError,'Non-directory'): self.validate(self.repo)


def subprocess_git(root,*args):
    import subprocess
    return subprocess.check_output(['git','-C',str(root),*args])


@unittest.skipUnless(os.environ.get('MYATLAS_ROOT'),'Reader parity runs in cross-repository CI with exact MyAtlas checkout')
class ReaderParityRequirementTests(unittest.TestCase):
    def test_checkout_has_schema_four_support(self):
        atlas=Path(os.environ['MYATLAS_ROOT'])
        text=(atlas/'scripts/knowledge_atlas/external_export_scan.py').read_text()
        self.assertIn('def _universal_files(',text)
        self.assertTrue((atlas/'docs/contracts/hyperskill-code-archive-v4.md').is_file())
