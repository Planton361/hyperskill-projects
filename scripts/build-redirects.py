#!/usr/bin/env python3
"""Package committed legacy redirects plus an optional verified portfolio snapshot."""
import argparse
from pathlib import Path
import shutil
from project_index import ROOT, git, tree, blob, revision
from project_index_store import validate_bundle

FILES = {'.nojekyll', 'index.html', 'redirect.js', 'knowledge-map/index.html',
         'knowledge-map/global.html', 'leetcode-atlas/index.html', 'leetcode-progress/index.html'}

def build(root, selected, output, portfolio=None):
    revision(root,selected)
    entries=tree(root,selected)
    names={n[5:] for n in entries if n.startswith('site/')}
    if names!=FILES or any(entries['site/'+n][:2]!=['100644','blob'] for n in FILES):
        raise ValueError('Unexpected/non-regular committed redirect assets')
    if portfolio is not None: validate_bundle(root,portfolio,selected)
    output=Path(output)
    if output.exists() or any(p.is_symlink() for p in (output,*output.parents)):
        raise ValueError('Fresh safe Pages output directory required')
    output.mkdir(parents=True)
    for name in sorted(FILES):
        path=output/name; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(blob(root,entries['site/'+name][2]))
    if portfolio is not None:
        shutil.copytree(portfolio,output/'portfolio')
        validate_bundle(root,output/'portfolio',selected)
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision')
    parser.add_argument('--output',type=Path,default=ROOT/'build/pages')
    parser.add_argument('--portfolio',type=Path)
    args=parser.parse_args()
    if args.portfolio and not args.revision: parser.error('--portfolio requires explicit --revision')
    selected=args.revision or git(ROOT,'rev-parse','HEAD').decode().strip()
    build(ROOT,selected,args.output,args.portfolio)
    print('Packaged all 7 unchanged legacy redirects'+(' and validated retained portfolio.' if args.portfolio else '.'))
