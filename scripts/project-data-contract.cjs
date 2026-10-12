/* Invoke the merged browser reader and accepted analytics; no progress inference here. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=process.argv[2],input=JSON.parse(fs.readFileSync(0,'utf8'));
const load=p=>require(path.join(root,p));
const reader=load('src/supplements/hyperskill-index-v1/reader.js');
const projection=load('src/supplements/hyperskill-index-v1/projection.js');
const analytics=load('src/myatlas/knowledge-atlas-v6-skill-tree/progress-analytics.js');
const index=reader.payload(reader.decode(input.index),{revision:input.revision});
const snapshot=projection.create({catalog:input.inputs.catalog,scopes:input.inputs.scopes,baseline:input.expected,
 catalogBinding:input.binding,analytics}).snapshot(index);
const expected=input.expected;
assert.deepEqual(snapshot.register.completed_project_ids,index.projects.map(p=>p.project_id));
assert.equal(snapshot.register.completed_project_count,index.projects.length);
for(const key of ['effective_learned_topic_ids','verified_topic_ids','completed_project_ids','course_completion','global'])
 assert.deepEqual(snapshot.completion[key],expected[key],key);
for(const row of snapshot.register.projects){
 const original=(expected.completion_register?.projects||expected.projects).find(p=>p.project_id===row.project_id);
 assert.ok(original,'Missing independently scanned identity');
 assert.deepEqual(row.topic_ids,original.topic_ids);
 assert.equal(row.requirements_state,original.requirements_state==='KNOWN'&&!original.topic_ids.length?'KNOWN_EMPTY':original.requirements_state);
}
process.stdout.write(JSON.stringify({completed_project_ids:snapshot.register.completed_project_ids,completed_project_count:snapshot.register.completed_project_count,
 unmapped_project_ids:snapshot.register.unmapped_project_ids,global:snapshot.completion.global,verified_topic_ids:snapshot.completion.verified_topic_ids,
 course_completion:snapshot.completion.course_completion,catalog_binding:input.binding})+'\n');
