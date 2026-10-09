#!/usr/bin/env python3
"""Package the owner-approved CPU snapshot beside the frozen Hyperskill runtime."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from knowledge_atlas.leetcode_cpu_package import adapt_cpu, adapt_top_ui

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/leetcode-atlas'
OUTPUT = ROOT / 'build/pages/leetcode-atlas'
FILES = ['BASELINE.json', 'app.js', 'index.html', 'model.js', 'optimized-cpu.js', 'visual-state.js',
         'style.css', 'controller.js', 'integration.css', 'LICENSE', 'NOTICE.txt',
         'data/catalog.json', 'data/taxonomy.json', 'data/sources.json', 'data/progress.json']
SHARED = {
    'src/leetcode-progress/loader.js': 'loader.js',
    'src/myatlas/knowledge-atlas-v6-global/style.css': 'assets/global.css',
    'src/myatlas/knowledge-atlas-navigation/shell.css': 'assets/shell.css',
    'src/myatlas/knowledge-atlas-v6-global/vendor/d3-7.9.0.min.js': 'assets/d3-7.9.0.min.js',
    'src/myatlas/knowledge-atlas-v6-global/vendor/D3-LICENSE': 'assets/D3-LICENSE',
    'scripts/knowledge_atlas/fonts/NotoSans-Regular.ttf': 'assets/NotoSans-Regular.ttf',
    'scripts/knowledge_atlas/fonts/NotoSans-Bold.ttf': 'assets/NotoSans-Bold.ttf',
    'scripts/knowledge_atlas/fonts/OFL.txt': 'assets/OFL.txt',
}


def checked(source):
    path = ROOT / source
    raw = path.read_bytes()
    if path.is_symlink() or raw != subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:' + source]):
        raise ValueError('Uncommitted or unsafe CPU source: ' + source)
    return raw


def validate_snapshot():
    baseline = json.loads((SOURCE / 'BASELINE.json').read_bytes())
    for name, expected in baseline['files'].items():
        if hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Accepted CPU source changed: ' + name)
    for name, expected in baseline['localEvaluationInputs'].items():
        if hashlib.sha256((SOURCE / 'data' / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Accepted snapshot changed: ' + name)
    catalog = json.loads((SOURCE / 'data/catalog.json').read_bytes())
    if len(catalog['problems']) != 3511 or len({p['id'] for p in catalog['problems']}) != 3511:
        raise ValueError('Accepted identity inventory changed')
    if json.loads((SOURCE / 'data/progress.json').read_bytes())['evidence']:
        raise ValueError('Never package personal solved evidence')
    if {str(p.relative_to(SOURCE)) for p in SOURCE.rglob('*') if p.is_file()} != set(FILES):
        raise ValueError('Unexpected CPU publication inventory')
    return baseline


def build():
    checked('scripts/build-leetcode-atlas.py')
    checked('scripts/knowledge_atlas/leetcode_cpu_package.py')
    baseline = validate_snapshot()
    if any(p.is_symlink() for p in [OUTPUT, *OUTPUT.parents]):
        raise ValueError('Unsafe CPU build destination')
    # Read and validate every input before replacing this route alone.
    assets = {name: checked('src/leetcode-atlas/' + name) for name in FILES if name != 'BASELINE.json'}
    checked('src/leetcode-atlas/BASELINE.json')
    assets.update({target: checked(source) for source, target in SHARED.items()})
    app = adapt_cpu(assets['app.js'].decode())
    app = app.replace("'Local · partial'", "'Snapshot · partial'")
    old = "function surface(next){\n"
    if app.count(old) != 1:
        raise ValueError('Reviewed navigation adapter no longer matches')
    app = app.replace(old, old + " if(next!=='leetcode'){location.assign(new URL('../knowledge-map/?view='+next,location.href));return;}\n")
    app = app.replace('../../../build/pages/knowledge-map/', '../knowledge-map/')
    # Public navigation opens the unchanged V6.6 route; no iframe shell edits.
    frame_handler = next(line for line in app.splitlines() if line.startswith("$('hyperskill-reference').onload="))
    app = app.replace(frame_handler, '')
    assets['app.js'] = app.encode()
    html = assets.pop('index.html').decode()
    html = html.replace("connect-src 'self';", "connect-src 'self' https://raw.githubusercontent.com;")
    html = html.replace('../../../src/myatlas/knowledge-atlas-v6-global/style.css', 'assets/global.css')
    html = html.replace('../../../src/myatlas/knowledge-atlas-navigation/shell.css', 'assets/shell.css')
    html = html.replace('../../../src/myatlas/knowledge-atlas-v6-global/vendor/d3-7.9.0.min.js', 'assets/d3-7.9.0.min.js')
    html = html.replace('href="?view=atlas"', 'href="../knowledge-map/?view=atlas"')
    html = html.replace('href="?view=skill-tree"', 'href="../knowledge-map/?view=skill-tree"')
    html = html.replace('LeetCode · MyAtlas local review', 'LeetCode CPU Atlas · MyAtlas')
    html = html.replace('<link rel="icon"', '<link rel="license" href="LICENSE"><link rel="icon"')
    html = html.replace('<link rel="stylesheet" href="style.css">', '<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="integration.css">')
    html = adapt_top_ui(html)
    html = html.replace('<script src="app.js"></script>', '<script src="loader.js"></script><script src="app.js"></script><script src="controller.js"></script>')
    html = html.replace('Problem Atlas · 18 problems in catalog · 0 solved · Partial catalog', 'Metadata snapshot · Public progress loading')
    assets['index.html'] = html.encode()
    assets['style.css'] = assets['style.css'].decode().replace('../../../scripts/knowledge_atlas/fonts/', 'assets/').encode()
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    for name, raw in assets.items():
        target = OUTPUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    result = {'route': 'leetcode-atlas/', 'sourceCommit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'identities': 3511, 'geometrySHA256': baseline['geometrySHA256'],
              'publicationBasis': 'owner-approved metadata-only snapshot; publisher-declared MIT; no separate LeetCode grant claimed',
              'inventory': {name: hashlib.sha256(raw).hexdigest() for name, raw in assets.items()}}
    (ROOT / 'build/leetcode-cpu-manifest.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(build(), sort_keys=True, indent=2))
