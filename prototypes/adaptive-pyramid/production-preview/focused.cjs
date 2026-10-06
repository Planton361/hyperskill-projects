const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../..'),A=require(root+'/scripts/knowledge_atlas/presentation/adaptive.cjs'),R=require(root+'/scripts/knowledge_atlas/presentation/registry.cjs'),V=require(root+'/scripts/knowledge_atlas/presentation/views.cjs'),check=require('../layout-refinement-tests/invariants.cjs');
const raw=JSON.parse(fs.readFileSync(__dirname+'/target/model.json')),geometry=JSON.parse(fs.readFileSync(__dirname+'/target/global-reference.json')),m=R.index(raw,geometry),before=JSON.stringify(geometry),measure=(s,f)=>s.length*(f.includes('15px')?7.6:f.includes('14px')?7.1:5.5);
assert.equal(fs.readFileSync(__dirname+'/target/adaptive.cjs','utf8'),fs.readFileSync(root+'/scripts/knowledge_atlas/presentation/adaptive.cjs','utf8'));
assert.deepEqual(fs.readFileSync(__dirname+'/target/global-reference.json'),fs.readFileSync(root+'/prototypes/global-pyramid/generated/global-geometry.json'));
const learned=new Set(raw.progress.filter(p=>p.is_learned===true).map(p=>'topic:'+p.topic_id));
const expected=new Set(learned);for(const key of learned){let n=m.nodes.get(key);while(n.parent){expected.add(n.parent);n=m.nodes.get(n.parent);}}
const personal=A.selection(m,{mode:'learned'});assert.deepEqual(personal.explicit,learned);assert.deepEqual(personal.visible,expected);assert.equal(learned.size,31);assert.equal(expected.size,52);
const accepted=A.selection(m,{mode:'accepted'});assert.equal(accepted.topics.size,89);assert.equal(personal.verified.size,12);
const scenes=[];for(const o of [{mode:'learned'},{mode:'accepted'},{mode:'course',id:8},{mode:'project',id:113},{mode:'project',id:113,stage:617}]){
 const s=A.selection(m,o),l=A.layout(m,s,{measure}),repeat=A.layout(m,s,{measure});
 assert.deepEqual([...l.positions],[...repeat.positions]);assert.deepEqual(l.routes,repeat.routes);assert.deepEqual([...l.subtrees],[...repeat.subtrees]);
 scenes.push({options:o,topics:s.topics.size,cards:l.positions.size,width:l.bounds.w,height:l.bounds.h,...check(m,s,l)});
 if(o.mode==='course'){const c=raw.courses.find(c=>c.id===8);assert.deepEqual(s.topics,new Set(c.topic_ids.map(id=>'topic:'+id)));}
 if(o.mode==='project'){const p=raw.projects.find(p=>p.id===113),ids=o.stage?p.stages.find(t=>t.id===617).required_topic_ids.map(id=>'topic:'+id):p.required;assert.deepEqual(s.topics,new Set(ids.filter(k=>!k.startsWith('category:'))));}
}
assert.deepEqual(A.selection(m,{mode:'course',id:8,onlyLearned:true}).topics,learned);
assert(A.selection(m,{mode:'project',id:380}).unknown);assert(!A.selection(m,{mode:'project',id:113,stage:618}).unknown);assert.equal(A.selection(m,{mode:'project',id:113,stage:618}).topics.size,0);
const v=new V.Views(m,measure);v.confirm({mode:'learned'});v.cameras.global={x:123,y:456,k:.15};
for(const o of [{mode:'course',id:8},{mode:'project',id:113}]){const n=v.metrics.layoutCalls,local=v.local;v.confirm(o,'reference');assert.equal(v.metrics.layoutCalls,n);assert.equal(v.local,local);assert.deepEqual(v.camera,{x:123,y:456,k:.15});assert.equal(v.positions.size,3955);}
assert.equal(A.search(m,'leaf:36')[0].key,'topic:36');assert.equal(JSON.stringify(geometry),before);
fs.writeFileSync(__dirname+'/focused-results.json',JSON.stringify({status:'PASS',myKnowledgeIDs:[...expected].sort(),explicitLearnedIDs:[...learned].sort(),scenes,highlightNoRelayout:true,globalReferenceUnchanged:true,courseMembershipExact:true,projectRequirementsExact:true,unknownVsEmpty:true,searchAliases:true},null,2)+'\n');
console.log(JSON.stringify({status:'PASS',scenes:scenes.map(s=>({options:s.options,topics:s.topics,cards:s.cards,cardOverlaps:s.cardOverlaps,subtreeOverlaps:s.subtreeOverlaps})),highlightNoRelayout:true},null,2));
