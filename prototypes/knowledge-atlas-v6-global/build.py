#!/usr/bin/env python3
"""Read the validated composed Catalog; write only this isolated prototype."""
import collections
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas.catalog import Catalog
from knowledge_atlas.snapshot import load_source


def project():
    data = load_source(ROOT / 'data/knowledge')
    catalog = Catalog(data)
    raw = dict(categories=list(catalog.categories.values()), topics=list(catalog.topics.values()),
               references=list(catalog.references.values()),
               memberships={str(k): sorted(v) for k, v in catalog.memberships.items()},
               hierarchy=sorted(catalog.latest_hierarchy),
               progress=data['progress'], evidence=data['evidence'],
               provenance=catalog.provenance, observations=catalog.observation_ids)
    raw['counts'] = dict(categories=len(raw['categories']), leaves=len(raw['topics']) + len(raw['references']),
                         **collections.Counter(r['resolution'] for r in raw['topics'] + raw['references']))
    return raw


if __name__ == '__main__':
    start = time.perf_counter()
    raw = project()
    (HERE / 'model.json').write_text(json.dumps(raw, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    result = dict(counts=raw['counts'], build_ms=(time.perf_counter()-start)*1000)
    (HERE / 'tests/build-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
