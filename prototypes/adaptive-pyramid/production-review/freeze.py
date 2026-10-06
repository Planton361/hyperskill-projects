"""Freeze the validated adaptive bytes in a new, non-overwriting review package."""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from knowledge_atlas import adaptive_production as A

ROOT = Path(__file__).resolve().parents[3]
DEST = Path(__file__).parent / 'final-v1'

def main():
    A.pending(ROOT)
    baseline = json.loads((ROOT / 'prototypes/adaptive-pyramid/production-preview/protected-before.json').read_bytes())
    bindings = {}
    for folder in (A.PRODUCTION, A.STATE, A.KNOWLEDGE):
        b = A.bound_tree(ROOT, folder)
        A.require(b['inventory'] == baseline[folder]['files'], 'Source changed since validated preview: ' + folder)
        for name, sha in b['inventory'].items():
            import hashlib
            A.require(hashlib.sha256(subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:' + name])).hexdigest() == sha, 'Source differs from HEAD: ' + name)
        bindings[folder] = b
    first, second = A.candidate(ROOT), A.candidate(ROOT)
    A.require(first == second, 'Non-deterministic target build')
    A.require(first == A.files(ROOT / 'prototypes/adaptive-pyramid/production-preview/target'), 'Validated target changed; rebuild preview first')
    source = A.files(ROOT / A.PRODUCTION)
    semantic = A.semantics(ROOT, source['model.json'], first['model.json'])
    target_binding = {'inventory': A.inventory(first, A.PRODUCTION + '/'),
                      'fingerprint': A.digest(A.inventory(first, A.PRODUCTION + '/'))}
    plan = A.diff(A.inventory(source), A.inventory(first))
    out = {'source-production-inventory.json': A.canonical(bindings[A.PRODUCTION]),
           'target-production-inventory.json': A.canonical(target_binding),
           'production-diff.json': A.canonical(plan), 'semantic-invariance.json': A.canonical(semantic)}
    out.update({'view/current/' + n: b for n, b in source.items()})
    out.update({'view/target/' + n: b for n, b in first.items()})
    html = (ROOT / 'prototypes/adaptive-pyramid/production-preview/index.html').read_text()
    start, end = html.index('<section>'), html.index('</section>') + len('</section>')
    html = html[:start] + html[end:]
    html = html.replace('<iframe id="preview"', '<p style="padding:0 24px"><strong>NO STATE / KNOWLEDGE / GENERATION CHANGE</strong></p><pre id="bindings" style="padding:0 24px;white-space:pre-wrap">Loading exact review bindings…</pre><iframe id="preview"')
    html = html.replace('</body>', '')
    html = html.replace('</html>', '<script>fetch("../apply-manifest.json").then(r=>r.json()).then(m=>{document.querySelector("#bindings").textContent="Source Production: "+m.source_production.fingerprint+"\\nTarget Production: "+m.target_production.fingerprint+"\\nManifest / human approval token: "+m.manifest_fingerprint+"\\nChanged Production files: "+m.production_diff.filter(r=>r.action!=="unchanged").length;});</script></html>')
    out['view/index.html'] = html.encode()
    out['README.md'] = b'''# Exact adaptive Production review

Open view/ through a localhost server. Review Current Production, Target My Knowledge,
Target Global, Target Course and Target Project. The page displays the exact source,
target and manifest fingerprints and the changed-file count.

NO STATE / KNOWLEDGE / GENERATION CHANGE. Local geometry remains derived.
This package grants no approval itself. Real Production has not been replaced.

After separate explicit human approval only, the operator command is:

python3 -B scripts/update-knowledge-atlas.py --apply-adaptive-production /absolute/path/to/apply-manifest.json --reviewed-fingerprint EXACT_MANIFEST_FINGERPRINT --confirm-production-replacement

Copy manifest_fingerprint from apply-manifest.json or the review page. No environment
bypass exists. Any change to the source bindings, implementation or package requires
a new review. Do not run the legacy --production command to publish this candidate.
The transient publication journal is outside State; no durable State is introduced.
Canonical identity uses UTF-8 sorted compact JSON, without timestamps. Manifest identity
hashes all fields except manifest_fingerprint. Package identity hashes all package files
except apply-manifest.json, avoiding self-reference. Inventories bind relative paths to
file SHA256; Production inventories use docs/knowledge-map/ prefixes.
'''
    manifest = {'schema_version': 1, 'operation': 'adaptive-production-replacement',
                'destination': A.PRODUCTION, 'source_identity': A.identity(ROOT),
                'source_production': bindings[A.PRODUCTION], 'source_state': bindings[A.STATE],
                'source_knowledge': bindings[A.KNOWLEDGE], 'implementation': A.implementation(ROOT),
                'global_reference_sha256': A.inventory({'reference': first['global-reference.json']})['reference'],
                'target_production': target_binding, 'production_diff': plan,
                'semantic_invariance': semantic, 'state_migration': False,
                'package_inventory': A.inventory(out), 'target_package_fingerprint': A.digest(A.inventory(out))}
    manifest['manifest_fingerprint'] = A.digest(manifest)
    out['apply-manifest.json'] = A.canonical(manifest)
    DEST.mkdir()  # Never overwrite an existing review, including a partial one.
    for name, content in out.items():
        p = DEST / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    A.validate(ROOT, (DEST / 'apply-manifest.json').resolve(), manifest['manifest_fingerprint'], True)
    for folder in bindings:
        A.require(A.bound_tree(ROOT, folder) == bindings[folder], 'Protected source changed during freeze')
    print(json.dumps({'status': 'PASS', 'package': str(DEST),
                      'manifest_fingerprint': manifest['manifest_fingerprint'],
                      'source_production_fingerprint': bindings[A.PRODUCTION]['fingerprint'],
                      'target_production_fingerprint': target_binding['fingerprint'],
                      'changed_files': sum(r['action'] != 'unchanged' for r in plan)}, indent=2))

if __name__ == '__main__': main()
