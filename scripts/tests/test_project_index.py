"""Synthetic committed archives, local Git origins and disposable Pages snapshots."""
import copy
import hashlib
import http.server
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.request import urlopen
from unittest.mock import patch

INFRA=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(INFRA))
import project_index as index
import project_index_store as store

class ProjectIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='index-contract-')
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name).resolve(); self.root=self.base/'repo'; self.root.mkdir()
        shutil.copytree(INFRA,self.root/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(INFRA.parent/'site',self.root/'site')
        self.git('init','-q','-b','main'); self.git('config','user.name','Synthetic owner')
        self.git('config','user.email','synthetic@example.invalid')
        self.git('remote','add','origin',index.ORIGIN+'.git')
        self.legacy(113,2,'Simple Chat Bot with Java',statement=True)
        self.legacy(380,2,'Synthetic Legacy 380')
        self.legacy(229,3,'Synthetic Source 229')
        self.first=self.commit()
        self.remote=self.base/'remote.git'
        subprocess.check_call(['git','clone','-q','--bare',str(self.root),str(self.remote)])
        self.live=None; self.fetches=[]
        original=store.git
        def local_git(root,*args):
            args=list(args)
            if args[0] in ('ls-remote','fetch','push'):
                args[args.index('origin')]=str(self.remote)
            return original(root,*args)
        self.patch=patch.object(store,'git',local_git); self.patch.start(); self.addCleanup(self.patch.stop)
        self.redirect=runpy.run_path(str(INFRA/'build-redirects.py'))

    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.PIPE)

    def commit(self):
        self.git('add','-A'); self.git('commit','-qm','Synthetic versioned evidence')
        return self.git('rev-parse','HEAD').decode().strip()

    def advance(self):
        rev=self.commit(); self.git('push','-q',str(self.remote),'main'); return rev

    def legacy(self,pid,schema,title,statement=False):
        path=self.root/'java'/title; code='src/main/java/Main.java' if schema==2 else 'src/Main.java'
        (path/code).parent.mkdir(parents=True); raw=b'own synthetic code; intentionally invalid syntax\n'
        (path/code).write_bytes(raw)
        (path/'README.md').write_text('Completed as part of [Hyperskill](https://hyperskill.org/projects/113).\n' if statement else f'https://hyperskill.org/projects/{pid}\n')
        m=dict(schema=schema,language='java',directory_name=title,files={code:index.sha(raw)})
        if schema==2: m['original_project_name']=title
        else: m['mode']='source-only'
        if not statement:
            m.update(project_id=pid,completion=dict(project_id=pid,status='completed',attested_by='owner',observed_at='2026-10-01T12:00:00Z'))
        (path/'.hyperskill-import.json').write_bytes(index.encode(m))

    def universal(self,pid=900000001):
        path=self.root/'projects'/str(pid); (path/'solution').mkdir(parents=True)
        raw={'README.md':b'Owner synthetic archive\n','solution/Main.kt':b'invalid Kotlin\n',
             'solution/helper.py':b'not Python syntax either\n','solution/unknown.future':b'topic_id=999999; verified=true\n',
             'solution/program':b'own extensionless code\n','solution/data.bin':b'\x00\xff\x01'}
        for name,data in raw.items(): (path/name).write_bytes(data)
        m=dict(schema=4,mode='code-archive',project_id=pid,project_url=f'https://hyperskill.org/projects/{pid}',
               title='Synthetic universal owner project',languages=['kotlin','python'],
               completion=dict(project_id=pid,status='completed',attested_by='owner',confirmed_at='2026-10-02T12:00:00Z'),
               files={name:dict(sha256=index.sha(data),role='resource' if name in ('README.md','solution/data.bin') else 'solution') for name,data in raw.items()})
        (path/'.hyperskill-import.json').write_bytes(index.encode(m)); return path,m

    def fetch(self,url,missing=False):
        self.fetches.append(url)
        if url==store.CURRENT: return self.live
        prefix=index.RAW+'/'
        if not url.startswith(prefix): raise ValueError('Untrusted test URL')
        commit,name=url[len(prefix):].split('/',1)
        return subprocess.check_output(['git','--git-dir',str(self.remote),'show',commit+':'+name],stderr=subprocess.PIPE)

    def publish(self,rev,label,bootstrap=False):
        portfolio=self.base/('portfolio-'+label)
        pointer=store.prepare(self.root,rev,portfolio,bootstrap=bootstrap,fetch=self.fetch)
        pages=self.base/('pages-'+label)
        self.redirect['build'](self.root,rev,pages,portfolio)
        self.live=pointer
        return pages,pointer

    def test_legacy_identity_full_inventory_and_exact_determinism(self):
        raw=index.generate(self.root,self.first)
        self.assertEqual(raw,index.generate(self.root,self.first))
        d=index.validate_index(self.root,raw,self.first)
        self.assertEqual([p['project_id'] for p in d['projects']],[113,229,380])
        for p in d['projects']:
            self.assertEqual(p['evidence_id'],f"hyperskill:{p['project_id']}")
            self.assertNotIn('completed_at',p['completion'])
            self.assertTrue(any(f['path'].endswith('/README.md') for f in p['files']))
            self.assertTrue(any(f['path'].endswith('/.hyperskill-import.json') for f in p['files']))
            for f in p['files']:
                actual=self.git('show',self.first+':'+f['path'])
                self.assertEqual(index.sha(actual),f['sha256'])
                self.assertEqual(hashlib.sha1(f'blob {len(actual)}\0'.encode()+actual).hexdigest(),f['git_blob'])
                if f['role']=='solution': self.assertIn('/blob/'+self.first+'/',f['code_url'])
        self.assertEqual(d['projects'][0]['manifest']['attestation']['path'],'java/Simple Chat Bot with Java/README.md')
        self.assertNotIn(b'generated_at',raw)

    def test_mixed_unknown_and_extensionless_code_no_catalog_or_execution(self):
        self.universal(); rev=self.advance(); d=index.validate_index(self.root,index.generate(self.root,rev))
        p=d['projects'][-1]; self.assertEqual(p['project_id'],900000001)
        self.assertEqual(p['completion']['confirmed_at'],'2026-10-02T12:00:00Z')
        self.assertNotIn('completed_at',p['completion'])
        self.assertEqual(len([f for f in p['files'] if f['role']=='solution']),4)
        self.assertFalse(any(k in p for k in ('topics','verified','course','stage','requirements_state')))
        binary=next(f for f in p['files'] if f['path'].endswith('data.bin'))
        self.assertEqual(binary['role'],'resource'); self.assertNotIn('code_url',binary)

    def test_selected_revision_ignores_uncommitted_and_newer_evidence(self):
        before=index.generate(self.root,self.first); self.universal(); self.advance()
        self.assertEqual(index.generate(self.root,self.first),before)

    def test_revisions_objects_origins_and_uncommitted_implementation_refused(self):
        for rev in ('HEAD','main','0'*40,'A'*40,self.git('rev-parse',self.first+':site/index.html').decode().strip()):
            with self.subTest(rev=rev),self.assertRaises((ValueError,subprocess.CalledProcessError)):
                index.generate(self.root,rev)
        self.git('remote','set-url','origin','https://github.com/attacker/foreign.git')
        with self.assertRaisesRegex(ValueError,'Foreign'): index.generate(self.root,self.first)
        self.git('remote','set-url','origin',index.ORIGIN+'.git')
        (self.root/'scripts/project_index.py').write_text('tampered code')
        rev=self.commit()
        with self.assertRaisesRegex(ValueError,'implementation'): index.generate(self.root,rev)

    def test_independent_validator_rejects_every_manipulated_index_field(self):
        original=index.decode(index.generate(self.root,self.first))
        cases=[]
        for key,value in [('repository','attacker/repo'),('schema',True),('revision','main'),('projects',[])]:
            d=copy.deepcopy(original); d[key]=value; cases.append(d)
        for key,value in [('title','fake'),('evidence_id','hyperskill:999'),('project_url','https://evil.invalid'),('completion',{}),('topic_ids',[15])]:
            d=copy.deepcopy(original); d['projects'][0][key]=value; cases.append(d)
        for key,value in [('sha256','0'*64),('git_blob','0'*40),('path','../evil'),('role','solution'),('code_url',index.ORIGIN+'/blob/main/evil')]:
            d=copy.deepcopy(original); d['projects'][0]['files'][0][key]=value; cases.append(d)
        d=copy.deepcopy(original);d['projects'].append(d['projects'][0]);cases.append(d)
        d=copy.deepcopy(original);d['validator']['implementation_revision']='0'*40;cases.append(d)
        for d in cases:
            with self.subTest(d=d),self.assertRaises((ValueError,subprocess.CalledProcessError)):
                index.validate_index(self.root,index.encode(d))
        with self.assertRaises(ValueError): index.validate_index(self.root,index.encode(original).replace(b'"schema":1',b'"schema":1,"schema":1'))

    def test_invalid_archive_fails_whole_candidate(self):
        path,m=self.universal(); (path/'solution/program').write_text('tampered')
        rev=self.advance()
        with self.assertRaisesRegex(ValueError,'does not match manifest'): index.generate(self.root,rev)
        self.assertIsNone(store.remote_sha(self.root,store.REF))

    def test_duplicate_legacy_and_universal_identity_refused(self):
        self.universal(113);rev=self.advance()
        with self.assertRaisesRegex(ValueError,'Duplicate'):index.generate(self.root,rev)

    def test_symlink_and_special_git_objects_never_indexed(self):
        path,m=self.universal(); code=path/'solution/program'; code.unlink();code.symlink_to('Main.kt')
        rev=self.advance()
        with self.assertRaisesRegex(ValueError,'Non-regular'):index.generate(self.root,rev)

    def test_two_then_three_publications_retain_old_payload_urls_and_redirects(self):
        pages1,p1=self.publish(self.first,'one',bootstrap=True)
        old=index.decode(p1); immutable=self.fetch(old['index_url'])
        self.universal();second=self.advance();pages2,p2=self.publish(second,'two')
        self.universal(900000002);third=self.advance();pages3,p3=self.publish(third,'three')
        self.assertEqual(self.fetch(old['index_url']),immutable)
        self.assertEqual((pages3/'portfolio/revisions'/self.first/'index.json').read_bytes(),immutable)
        self.assertEqual(len(store.validate_bundle(self.root,pages3/'portfolio',third)),3)
        for name in self.redirect['FILES']:
            self.assertEqual((pages1/name).read_bytes(),(pages3/name).read_bytes())
            self.assertEqual((pages3/name).read_bytes(),self.git('show',third+':site/'+name))
        handler=lambda *args,**kw:http.server.SimpleHTTPRequestHandler(*args,directory=str(pages3),**kw)
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with urlopen(f'http://127.0.0.1:{server.server_port}/portfolio/revisions/{self.first}/index.json') as response:
                self.assertEqual(response.read(),immutable)
        finally: server.shutdown();server.server_close();thread.join()

    def test_stale_workflow_and_same_revision_retry_are_safe(self):
        self.publish(self.first,'first',bootstrap=True)
        tip=store.remote_sha(self.root,store.REF)
        pages,pointer=self.publish(self.first,'retry')
        self.assertEqual(tip,store.remote_sha(self.root,store.REF))
        self.universal();second=self.advance()
        with self.assertRaisesRegex(ValueError,'Stale'):store.prepare(self.root,self.first,self.base/'stale',fetch=self.fetch)
        self.assertEqual(tip,store.remote_sha(self.root,store.REF))

    def test_interrupt_after_durable_push_then_retry_preserves_pointer(self):
        def failed(url,missing=False):
            if url!=store.CURRENT:raise ValueError('network interrupted')
            return None
        with self.assertRaisesRegex(ValueError,'interrupted'):
            store.prepare(self.root,self.first,self.base/'failed',bootstrap=True,fetch=failed)
        tip=store.remote_sha(self.root,store.REF)
        self.assertIsNotNone(tip); self.assertIsNone(self.live)
        self.assertFalse((self.base/'failed').exists())
        self.publish(self.first,'recovered',bootstrap=True)
        self.assertEqual(tip,store.remote_sha(self.root,store.REF))

    def test_missing_corrupt_and_mismatched_previous_pointer_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'Missing'):store.prepare(self.root,self.first,self.base/'missing',fetch=self.fetch)
        self.assertIsNone(store.remote_sha(self.root,store.REF))
        self.publish(self.first,'initial',bootstrap=True);valid=self.live
        self.universal();rev=self.advance();tip=store.remote_sha(self.root,store.REF)
        for raw in (b'{}\n',b'truncated',index.encode(dict(index.decode(valid),index_sha256='0'*64)),None):
            self.live=raw
            with self.assertRaises((ValueError,KeyError)):
                store.prepare(self.root,rev,self.base/'bad',bootstrap=True,fetch=self.fetch)
            self.assertEqual(tip,store.remote_sha(self.root,store.REF))
        self.live=valid

    def test_parallel_store_change_and_live_pointer_change_withhold_candidate(self):
        self.publish(self.first,'one',bootstrap=True); self.universal();rev=self.advance()
        actual=store.remote_sha
        def racing(root,ref):
            if ref==store.REF and racing.called: return 'f'*40
            if ref==store.REF: racing.called=True
            return actual(root,ref)
        racing.called=False
        with patch.object(store,'remote_sha',side_effect=racing),self.assertRaisesRegex(ValueError,'Concurrent'):
            store.prepare(self.root,rev,self.base/'racing',fetch=self.fetch)
        old=self.live;counts=0
        def changed(url,missing=False):
            nonlocal counts
            if url==store.CURRENT:
                counts+=1
                return old if counts==1 else b'changed'
            return self.fetch(url,missing)
        with self.assertRaisesRegex(ValueError,'Concurrent live'):
            store.prepare(self.root,rev,self.base/'changed',fetch=changed)
        self.assertFalse((self.base/'changed').exists());self.assertEqual(self.live,old)

    def test_pointer_fields_hosts_branches_hashes_and_revision_are_strict(self):
        raw=index.generate(self.root,self.first);p=index.decode(index.pointer(self.first,'a'*40,raw))
        for key,value in [('schema',True),('repository','evil/repo'),('revision','0'*40),('index_sha256','0'*64),('index_url','https://evil.invalid/index.json'),('index_url',index.RAW+'/main/portfolio/revisions/'+self.first+'/index.json'),('extra','bad')]:
            with self.subTest(key=key),self.assertRaises(ValueError):index.validate_pointer(index.encode(dict(p,**{key:value})),raw)

    def test_unsafe_http_and_artifact_inputs_rejected(self):
        with patch.object(store,'urlopen',side_effect=AssertionError('must not fetch')):
            with self.assertRaisesRegex(ValueError,'Untrusted'):store.get('https://evil.invalid')
        pages,pointer=self.publish(self.first,'valid',bootstrap=True)
        portfolio=pages/'portfolio';(portfolio/'extra').write_text('bad')
        with self.assertRaisesRegex(ValueError,'Unexpected'):store.validate_bundle(self.root,portfolio,self.first)

    def test_payload_unreachable_or_wrong_bytes_withholds_pointer_then_recovers(self):
        def changed(url,missing=False):
            return None if url==store.CURRENT else b'tampered payload'
        with self.assertRaisesRegex(ValueError,'byte-identical'):
            store.prepare(self.root,self.first,self.base/'bad-hash',bootstrap=True,fetch=changed)
        self.assertIsNone(self.live); self.assertFalse((self.base/'bad-hash').exists())
        self.publish(self.first,'recovery',bootstrap=True)

    def test_last_guard_checks_pointer_and_disabled_mode_never_erases_index(self):
        store.refuse_index_removal(self.root,fetch=self.fetch)
        guard=self.base/'guard.json';portfolio=self.base/'guarded'
        candidate=store.prepare(self.root,self.first,portfolio,bootstrap=True,fetch=self.fetch,guard=guard)
        store.publication_guard(self.root,self.first,portfolio,guard,fetch=self.fetch)
        self.live=candidate
        with self.assertRaisesRegex(ValueError,'Concurrent live'):
            store.publication_guard(self.root,self.first,portfolio,guard,fetch=self.fetch)
        with self.assertRaisesRegex(ValueError,'must not erase'):
            store.refuse_index_removal(self.root,fetch=self.fetch)
        self.live=None
        with self.assertRaisesRegex(ValueError,'must not erase'):
            store.refuse_index_removal(self.root,fetch=self.fetch)

    def test_corrupt_durable_store_fails_without_pointer_change(self):
        self.publish(self.first,'valid-store',bootstrap=True);old=self.live
        tip=store.remote_sha(self.root,store.REF)
        payload=subprocess.check_output(
            ['git','-C',str(self.root),'hash-object','-w','--stdin'],input=b'corrupt')
        bad_tree=subprocess.check_output(['git','-C',str(self.root),'mktree'],input=b'100644 blob '+payload.strip()+b'\tevil.json\n').decode().strip()
        bad=subprocess.check_output(['git','-C',str(self.root),'commit-tree',bad_tree,'-p',tip],input=b'Synthetic damaged store\n').decode().strip()
        self.git('push','-q',str(self.remote),bad+':'+store.REF)
        with self.assertRaisesRegex(ValueError,'Corrupt'):
            store.prepare(self.root,self.first,self.base/'corrupt',fetch=self.fetch)
        self.assertEqual(self.live,old)

    def test_normal_git_push_refuses_competing_initial_store_writer(self):
        actual=store.git
        def competing(root,*args):
            if args[0]=='push':
                # Publish another valid orphan commit immediately after the CAS
                # precheck. The subsequent ordinary push must reject it.
                candidate=args[-1].split(':')[0]
                tree_id=self.git('rev-parse',candidate+'^{tree}').decode().strip()
                rival=subprocess.check_output(['git','-C',str(self.root),'commit-tree',tree_id],input=b'Competing synthetic writer\n').decode().strip()
                self.git('push','-q',str(self.remote),rival+':'+store.REF)
            return actual(root,*args)
        with patch.object(store,'git',side_effect=competing),self.assertRaises(subprocess.CalledProcessError):
            store.prepare(self.root,self.first,self.base/'race',bootstrap=True,fetch=self.fetch)
        self.assertIsNone(self.live);self.assertFalse((self.base/'race').exists())

    def test_bounded_fetch_refuses_redirects_and_large_bodies(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def geturl(self):return 'https://evil.invalid'
            def read(self,size):return b'x'*size
        with patch.object(store,'urlopen',return_value=Response()):
            with self.assertRaisesRegex(ValueError,'Redirected'):store.get(store.CURRENT)
        response=Response();response.geturl=lambda:store.CURRENT
        with patch.object(store,'urlopen',return_value=response),patch.object(store,'MAX_BYTES',8):
            with self.assertRaisesRegex(ValueError,'Oversized'):store.get(store.CURRENT)

    def test_explicit_reviewed_recovery_uses_valid_history_and_pins_bad_live_bytes(self):
        self.publish(self.first,'old',bootstrap=True);known=self.live
        self.universal();rev=self.advance();self.live=b'broken live pointer'
        guard=self.base/'recovery-guard';portfolio=self.base/'recovered'
        candidate=store.prepare(self.root,rev,portfolio,fetch=self.fetch,recovery=known,guard=guard)
        store.publication_guard(self.root,rev,portfolio,guard,fetch=self.fetch)
        self.assertEqual(self.live,b'broken live pointer')  # preparation never deploys
        self.assertEqual(index.decode(candidate)['revision'],rev)
        forged=index.encode(dict(index.decode(known),index_sha256='0'*64))
        with self.assertRaisesRegex(ValueError,'hash'):
            store.prepare(self.root,rev,self.base/'forged-recovery',fetch=self.fetch,recovery=forged)

if __name__=='__main__':unittest.main()
