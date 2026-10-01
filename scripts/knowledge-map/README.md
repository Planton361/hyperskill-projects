# Knowledge Map build contract

This directory contains **curated display configuration**, not Hyperskill facts.
Domain → Subdomain → Topic follows the existing canonical category ancestry.
Secondary hierarchy relations remain preserved in the raw tables. Counts use
unique stable topic IDs. The only capability definition is Control Flow evidence,
IDs 25, 89, 87, 88: currently 4/4 learned and 3/4 verified, never proficiency.

## Rebuild / verify

From repository root, with Python 3.10+:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build-knowledge-map.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build-knowledge-map.py --check
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p 'test_*.py'
~~~

The generator reads normalized data/knowledge tables, the complete observations
used by the existing validator, display-map.json and capabilities.json. It reuses
the existing Knowledge Graph source validator without running that generator.
Outputs are docs/knowledge-map/model.json and generated/profile-learning-summary.md.
--check validates and compares them without writes. --root supports isolated roots.
No network, credentials, sessions or account access are needed.

Unmapped topics, missing evidence, dangling edges, invalid personal/application
assertions and conflicting equally recent progress observations fail generation.
Do not silently invent display placements or infer applied topics.

Runtime files are separately maintained under docs/knowledge-map. They were
reviewed from preview commit 81d979c719b251356a77861cf454780a30c6338f; D3 7.9.0
and its license are vendored locally. The generated model is not source-of-truth.
It currently matches the public preview's model byte-for-byte.

## UI contract

Overview renders domains only, domain focus subdomains, subdomain focus paged
topics. Topic focus replaces the scene with the selection and direct evidenced
neighbors. Project evidence is separate; project_requires renders only after
Show project connections. Unknown requirements are not an empty known set.

My Knowledge draws only is_learned === true topics. Verification is additional
evidence, not proficiency; failed assessment does not reverse explicit learning.
Applied IDs remain null, with only the recorded aggregate shown.

Wheel zoom >1.8 enters the nearest visible structural area; <0.75 returns up.
Buttons and breadcrumbs provide equivalent accessible navigation. Query links
encode domain/subdomain/topic/project, mode, course, page and connection opt-in.
History pushState/popstate restores semantic context; camera and inspector
pagination are transient. Topic scenes cap at 24 desktop / 6 mobile plus an
optional project hub. Tablet columns adapt to width; rows adapt to label wrapping.
Focus outline is rectangular, distinct from the small Verified ring.

## Local runtime tests

~~~bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
~~~

Install Playwright outside the repository or provide PLAYWRIGHT_MODULE and
CHROMIUM_EXECUTABLE. No storage state or account sessions are used.

~~~bash
node scripts/tests/knowledge_map_browser.cjs http://127.0.0.1:8000/knowledge-map/
node scripts/tests/knowledge_graph_browser.cjs http://127.0.0.1:8000/knowledge-graph/
~~~

The V2 test visits every real topic, deep links, project requirements, keyboard
and history in 1440/768/390/320 widths and both themes. Optional SCREENSHOT_DIR
writes screenshots only to a caller-supplied local directory. No fixtures or
screenshots are published.

## Release isolation

The legacy docs/knowledge-graph and the normalized dataset must remain unchanged
in this release. The production URL after reviewed merge is:
https://planton361.github.io/hyperskill-projects/knowledge-map/

Current Pages publishes main/docs: pushing knowledge-map-release alone does NOT
make this production route live. No automatic merge, Pages-setting change or
profile integration belongs to this build process. The generated Markdown is only
a proposal; it uses absolute production links and at most four knowledge-area rows
(including Other), one course and one completed-project evidence item.
