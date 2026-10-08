/* Focused pure UX contracts, including disposable multi-membership fixtures. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {create}=require('../ux-model.js'),root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p))),base='prototypes/knowledge-atlas-scope-pyramid/';
const index=read(base+'scope-index.json'),catalog=read(base+'catalog.json'),accepted=read('data/knowledge/courses.json'),evidence=read('data/knowledge/evidence.json'),ux=create(index,catalog,accepted,evidence);
assert.equal(ux.courses.size,52);assert.equal(ux.projects.size,391);assert.equal(ux.stages.size,1967);
assert.equal(ux.associations.size,52);assert.deepEqual(ux.association(8).project_ids,accepted[0].project_ids);assert.match(ux.association(8).observation,/course-project-associations/);assert.equal(ux.association(2).state,'KNOWN');assert.equal(ux.association(2).project_ids.length,43);assert.equal(ux.association(3).project_ids.length,36);for(const id of [31,41,57,60]){assert.equal(ux.association(id).state,'KNOWN_EMPTY');assert.deepEqual(ux.association(id).project_ids,[]);}assert.equal([...ux.associations.values()].filter(r=>r.state==='UNKNOWN').length,0);
assert.deepEqual(ux.projectChoices(ux.normalize({section:'courses',course_id:8})).map(s=>s.scope_id),accepted[0].project_ids);assert.equal(ux.projectChoices(ux.normalize({section:'projects'})).length,391);
// Optional Course filtering and legacy Projects routes use one combined context.
const neutral=ux.normalize({});assert.equal(ux.projectChoices(neutral).length,391);assert.equal(neutral.course_id,null);
const pairs=[...ux.associations].flatMap(([cid,a])=>a.project_ids.map(pid=>[cid,pid]));assert.equal(pairs.length,867);assert.equal(new Set(pairs.map(p=>p.join(':'))).size,867);
const targets=new Set(pairs.map(p=>p[1]));assert.equal(targets.size,299);const outside=[...ux.projects.keys()].filter(id=>!targets.has(id));assert.equal(outside.length,92);
for(const id of outside)assert.equal(ux.normalize({project_id:id}).project_id,id,'all unassociated catalog identities remain selectable');
const unfilteredStage=ux.choose(ux.normalize({course_id:8,project_id:113,stage_id:617}),'course',null);assert.equal(unfilteredStage.project_id,113);assert.equal(unfilteredStage.stage_id,617);assert.equal(unfilteredStage.course_id,null);assert.equal(ux.projectChoices(unfilteredStage).length,391);
assert.deepEqual(ux.choose(unfilteredStage,'course',8),ux.normalize({course_id:8,project_id:113,stage_id:617}),'compatible filter retains deepest selection');
assert.equal(ux.choose(unfilteredStage,'project',null).stage_id,null);assert.equal(ux.current(ux.choose(unfilteredStage,'project',null)),null);
assert.equal(ux.parse('?section=projects&scope=stage&id=617').section,'courses');assert.equal(ux.parse('?section=projects&scope=stage&id=617').stage_id,617);
let state=ux.normalize({section:'courses',course_id:8,project_id:113,stage_id:617});assert.equal(ux.current(state).scope_id,617);assert.deepEqual(ux.parse(ux.url(state)),state);
state=ux.choose(state,'stage',null);assert.equal(ux.current(state).scope_id,113);state=ux.choose(state,'project',null);assert.equal(ux.current(state).scope_id,8);state=ux.choose(state,'course',null);assert.equal(ux.current(state),null);
assert.deepEqual(ux.choose({section:'courses',course_id:8,project_id:113,stage_id:617},'course',2),{section:'courses',course_id:2,project_id:null,stage_id:null});
assert.equal(ux.normalize({section:'courses',course_id:8,project_id:95}).project_id,null);assert.equal(ux.normalize({section:'courses',course_id:2,project_id:113}).project_id,null);
assert.equal(ux.normalize({section:'projects',project_id:113,stage_id:2266}).stage_id,null);
assert.deepEqual(ux.stageChoices(113).map(s=>s.scope_id),[614,615,616,617,618]);
assert.equal(ux.parse('?scope=stage&id=617').project_id,113);assert.equal(ux.parse('?scope=course&id=08').course_id,null);
assert.equal(ux.topic(36).learned,true);assert.equal(ux.topic(36).verified,true);assert.equal(ux.topic(1).learned,false);
const unknown=catalog.topics.find(t=>!catalog.progress.topics.some(r=>r.topic_id===t.id));assert.equal(ux.topic(unknown.id).learned,null);assert.equal(ux.topic(unknown.id).verified,null);
const progress=ux.categoryProgress(8);for(const cid of [35,306])assert(progress.get(cid).eligible_ids.has(36),'shared Topic counts under both structural memberships');
const allCourseTopics=new Set(index.courses.find(c=>c.scope_id===8).explicit_topic_ids);for(const p of progress.values())assert([...p.eligible_ids].every(id=>allCourseTopics.has(id)));
// Independent descendants walk validates the upward aggregation on actual data.
const children=new Map();for(const [child,parents] of Object.entries(catalog.memberships))for(const parent of parents){if(!children.has(parent))children.set(parent,[]);children.get(parent).push(+child);}
for(const [cid,p] of progress){const seen=new Set(),queue=[cid],eligible=new Set();while(queue.length){for(const id of children.get(queue.pop())||[]){if(seen.has(id))continue;seen.add(id);if(allCourseTopics.has(id))eligible.add(id);queue.push(id);}}assert.deepEqual([...p.eligible_ids].sort((a,b)=>a-b),[...eligible].sort((a,b)=>a-b));assert.equal(p.fully_learned,p.eligible_count>0&&[...eligible].every(id=>ux.topic(id).learned===true));}
// Disposable synthetic evidence is not persisted or treated as Hyperskill facts.
const fixtureIndex={courses:[{scope_id:1,title:'Fixture',explicit_topic_ids:[101,102,103]}],projects:[],stages:[]};
const raw={categories:[{id:1},{id:2},{id:3},{id:4}],topics:[{id:101},{id:102},{id:103}],memberships:{2:[1],3:[1],101:[2,3],102:[2],103:[3]},progress:{topics:[{topic_id:101,is_learned:true,is_verified:false},{topic_id:102,is_learned:true,is_verified:true}]}};
const fixture=create(fixtureIndex,raw,[],[]),p=fixture.categoryProgress(1);assert.equal(p.get(1).eligible_count,3);assert.equal(p.get(2).eligible_count,2);assert.equal(p.get(2).fully_learned,true);assert.equal(p.get(2).fully_verified,false);assert.equal(p.get(3).eligible_count,2);assert.equal(p.get(3).unknown_learned,1);assert.equal(p.get(3).fully_learned,false);assert.equal(p.get(1).fully_learned,false);assert(!p.has(4));
raw.progress.topics.push({topic_id:103,is_verified:true});const verifiedOnly=create(fixtureIndex,raw,[],[]);assert.equal(verifiedOnly.topic(103).learned,null);assert.equal(verifiedOnly.topic(103).verified,true);assert.equal(verifiedOnly.categoryProgress(1).get(3).fully_learned,false);
assert.equal(index.projects.filter(p=>p.state==='UNKNOWN').length,16);assert.equal(index.projects.filter(p=>p.state==='KNOWN'&&!p.explicit_topic_ids.length).length,5);assert.equal(index.stages.filter(s=>!s.explicit_topic_ids.length).length,328);
console.log(JSON.stringify({status:'PASS',course_project_coverage:'48 known nonempty / 4 known empty / 0 UNKNOWN',source_project_ids:accepted[0].project_ids,multiple_memberships:'PASS',unknown_false_completion:'PASS',url_roundtrip_deselect:'PASS',explicit_progress:'PASS'},null,2));
