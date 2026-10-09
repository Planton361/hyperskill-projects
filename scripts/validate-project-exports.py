#!/usr/bin/env python3
"""Validate committed export bytes/templates and build in disposable directories."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from export_metadata import validate_completion
from source_adapters import validate_python_export, python_sources

ROOT=Path(__file__).resolve().parents[1]


def validate(root):
    importer=runpy.run_path(str(ROOT/'scripts/import-hyperskill-project'))
    tree=subprocess.check_output(['git','-C',str(root),'ls-tree','-rz','HEAD'])
    entries={}
    for item in tree.split(b'\0'):
        if item:
            meta,name=item.split(b'\t',1);entries[name.decode()]=meta.decode().split()
    markers=sorted(n for n in entries if len(n.split('/'))==3 and n.endswith('/.hyperskill-import.json'))
    if not markers:raise ValueError('No committed exports')
    if any(n.split('/')[0] not in ('java','python') for n in markers):raise ValueError('Unsupported export language')
    for name in entries:
        if len(name.split('/')) >= 3 and name.split('/')[0] in ('java','python') and '/'.join(name.split('/')[:2])+'/.hyperskill-import.json' not in markers:
            raise ValueError('Project directory missing completion/export manifest: '+name)
    results=[];seen=set()
    with tempfile.TemporaryDirectory(prefix='validated-export-build-') as folder:
        for marker in markers:
            prefix=marker.rsplit('/',1)[0]
            target=Path(folder)/prefix
            for name in entries:
                if not name.startswith(prefix+'/'):continue
                mode,kind,oid=entries[name]
                if mode not in ('100644','100755') or kind!='blob':raise ValueError('Non-regular export')
                path=Path(folder)/name;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(subprocess.check_output(['git','-C',str(root),'cat-file','blob',oid]))
                if mode=='100755':path.chmod(0o755)
            meta=json.loads((target/'.hyperskill-import.json').read_text())
            language=prefix.split('/')[0]
            if meta.get('schema')!=2 or meta.get('language')!=language or meta.get('directory_name')!=target.name:raise ValueError('Invalid export identity')
            files=meta['files']
            actual={p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
            if actual!=set(files)|{'README.md','.hyperskill-import.json'}:raise ValueError('Unmanifested export files')
            for name,digest in files.items():
                path=Path(name)
                if path.is_absolute() or '..' in path.parts or path.as_posix()!=name or hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('Export manifest mismatch')
            completion=meta.get('completion')
            if completion:
                validate_completion(completion);pid=completion['project_id']
                if meta.get('project_id')!=pid:raise ValueError('Exact project_id missing/conflicting')
            elif prefix=='java/Simple Chat Bot with Java' and 'Completed as part of [Hyperskill](https://hyperskill.org/projects/113).' in (target/'README.md').read_text().splitlines():
                pid=113  # Existing reviewed legacy evidence only.
            else:raise ValueError('Owner completion attestation missing')
            urls=set(map(int,re.findall(r'https://hyperskill\.org/projects/([1-9][0-9]*)(?![0-9])',(target/'README.md').read_text())))
            if urls!={pid} or pid in seen:raise ValueError('Duplicate or conflicting Project ID')
            seen.add(pid)
            importer['validate']({n:(target/n).read_bytes() for n in files})
            if language=='java':
                texts={Path(n): (target/n).read_text() for n in files if n.startswith('src/main/java/') and n.endswith('.java')}
                main=importer['main_class'](texts,None)
                for name in ('build.gradle.kts','settings.gradle.kts'):
                    expected=(ROOT/'scripts/templates/java-gradle'/ (name+'.in')).read_text()
                    for key,value in {'JAVA_VERSION':str(meta['java_version']),'MAIN_CLASS':main,'PROJECT_NAME':importer['kotlin_string'](target.name)}.items():expected=expected.replace('@'+key+'@',value)
                    if (target/name).read_text()!=expected:raise ValueError('Unreviewed standalone Gradle build logic')
                for name,digest in json.loads((ROOT/'scripts/templates/wrapper-sha256.json').read_text()).items():
                    if hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('Unreviewed wrapper')
                if set(files)!=set(map(str,texts))|set(importer['WRAPPER'])|{'build.gradle.kts','settings.gradle.kts'}:raise ValueError('Unexpected Java resource/build file')
                subprocess.run([str(target/'gradlew'),'--no-daemon','build'],cwd=target,check=True)
            else:
                # Re-run the exact source/dependency/resource adapter on the
                # exported bytes in a disposable Academy-shaped inspection tree.
                inspect=Path(folder)/('python-inspect-'+str(pid));src=inspect/'Lesson/task/src'
                src.mkdir(parents=True)
                for name in files:
                    if not name.startswith('src/'):raise ValueError('Python member outside src')
                    dest=src/name.removeprefix('src/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((target/name).read_bytes())
                payload,main=python_sources(inspect,importer['inventory'],importer['excluded'],importer['PLATFORM'],importer['SECRETS'])
                if set(payload)!=set(files) or meta['entrypoint']!='src/'+main:raise ValueError('Python source contract mismatch')
                validate_python_export(target,meta)
            results.append(dict(project_id=pid,language=language,status='PASS'))
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repository',type=Path,default=ROOT)
    args=parser.parse_args();print(json.dumps(validate(args.repository.resolve()),indent=2))
