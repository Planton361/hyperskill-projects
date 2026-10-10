"""Dependency, identity and resource boundaries of the language adapters."""
import json
import runpy
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from source_adapters import python_sources, workspace, project_url, detect
I=runpy.run_path(str(ROOT/'scripts/import-hyperskill-project'))


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.task=self.root/'Lesson/task';self.task.mkdir(parents=True)
        (self.root/'course-info.yaml').write_text('title: Fixture\nprogramming_language: Python\n')
        self.main=self.task/'main.py';self.main.write_text('print("hello")\n')

    def analyze(self):
        return python_sources(self.root,I['inventory'],I['excluded'],I['PLATFORM'],I['SECRETS'])

    def test_detect_from_nested_source_and_exact_remote_metadata(self):
        self.assertEqual(workspace(self.main),self.root)
        self.assertEqual(detect(self.root),'python')
        with self.assertRaises(ValueError):detect(self.root,'java')
        with self.assertRaises(ValueError):project_url(self.root)
        (self.root/'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 380\n  ide_files: https://hyperskill.org/api/projects/380/additional-files/additional_files.json\n')
        self.assertEqual(project_url(self.root),'https://hyperskill.org/projects/380')
        with self.assertRaises(ValueError):project_url(self.root,'https://hyperskill.org/projects/113')

    def test_python_unknown_dependencies_and_dynamic_execution_stop(self):
        for text in ['import requests\n','import os\n','import subprocess\n','eval("1")\n','import importlib\n','print(__builtins__)\n','from . import local\n']:
            with self.subTest(text=text):
                self.main.write_text(text)
                with self.assertRaises(ValueError):self.analyze()
        self.main.write_text('print("hello")\n')
        (self.root/'requirements.txt').write_text('requests==2.0\n')
        with self.assertRaises(ValueError):self.analyze()
        (self.root/'requirements.txt').write_text('# no dependencies\n');self.analyze()

    def test_python_resources_require_literal_existing_readonly_paths(self):
        for text in ['open("../outside.txt")\n','open(input())\n','reader = open\nreader("outside.txt")\n','open("data.txt", "w")\n']:
            self.main.write_text(text)
            with self.assertRaises(ValueError):self.analyze()
        self.main.write_text('print("hello")\n');resource=self.task/'data.txt';resource.write_text('hello\n')
        with self.assertRaises(ValueError):self.analyze()
        self.main.write_text('with open("data.txt") as f:\n    print(f.read())\n');payload,entry=self.analyze()
        self.assertEqual(entry,'main.py');self.assertEqual(payload['src/data.txt'],b'hello\n')
        resource.unlink();resource.symlink_to(self.main)
        with self.assertRaises(ValueError):self.analyze()

    def test_python_invalid_source_and_unknown_build_metadata_stop(self):
        self.main.write_text('def broken(\n')
        with self.assertRaisesRegex(ValueError,'Invalid Python'):self.analyze()
        self.main.write_text('print("fixture")\n');(self.task/'setup.py').write_text('print("must never execute")\n')
        with self.assertRaises(ValueError):self.analyze()
