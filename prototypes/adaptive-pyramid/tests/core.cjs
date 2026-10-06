const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const base=path.resolve(__dirname,'..'),C=require('../../global-pyramid/atlas.js'),A=require('../core.cjs');
const raw=JSON.parse(fs.readFileSync(base+'/../global-pyramid/generated/catalog.json')),geo=JSON.parse(fs.readFileSync(base+'/../global-pyramid/generated/global-geometry.json')),m=C.index(raw,geo);
const original=[...m.nodes.values()].map(n=>[n.key,n.x,n.y,n.w,n.h,n.parent,n.sibling_order]),geometryJSON=JSON.stringify(geo);
const measure=(text,font)=>text.length*(font.includes('15px')?7.6:font.includes('14px')?7.1:5.5);
const collisionChecks=require('./collisions.cjs');

function verify(s,l){
 const expected=new Set([...s.visible].filter(k=>!l.hidden.has(k)));assert.deepEqual(new Set(l.positions.keys()),expected);assert.equal(new Set([...l.positions.values()].map(p=>p.slot)).size,l.positions.size);
 for(const group of l.groups){const parent=m.nodes.get(group.parent),expected=parent.children.filter(n=>n.kind!=='category'&&expectedVisible(n,s,l)).map(n=>n.key);assert.deepEqual(group.cards.map(c=>c.key),expected);let prev=-Infinity;for(const c of group.cards){const pos=l.positions.get(c.key),rank=pos.y*1000000+pos.x;assert(rank>prev,'row-major order');prev=rank;}}
 for(const n of m.nodes.values())if(n.kind==='category'&&l.positions.has(n.key)){
  const cs=n.children.filter(c=>c.kind==='category'&&l.positions.has(c.key));for(let i=1;i<cs.length;i++)assert(l.positions.get(cs[i-1].key).x<l.positions.get(cs[i].key).x,'category sibling order');
 }
 return collisionChecks(l);
}
function expectedVisible(n,s,l){return s.visible.has(n.key)&&!l.hidden.has(n.key);}
const scenes=[{mode:'learned'},{mode:'accepted'},{mode:'course',id:8},{mode:'course',id:8,onlyLearned:true},{mode:'project',id:113},{mode:'project',id:113,onlyLearned:true},{mode:'project',id:113,stage:617},{mode:'project',id:113,stage:617,onlyLearned:true},{mode:'project',id:380},{mode:'project',id:113,stage:618},...['load-300','load-1000','full'].map(f=>({mode:'fixture:'+f}))];
const results=[];for(const o of scenes){const s=A.selection(m,o),l=A.layout(m,s,{measure});const checks=verify(s,l);const repeated=A.layout(m,A.selection(m,o),{measure});assert.deepEqual([...l.positions], [...repeated.positions]);assert.deepEqual(l.routes,repeated.routes);results.push({options:o,topics:s.topics.size,visible:s.visible.size,unknown:s.unknown,cards:l.positions.size,bounds:l.bounds,layoutMs:l.durationMs,...checks});}
const learned=A.selection(m),accepted=A.selection(m,{mode:'accepted'}),course=A.selection(m,{mode:'course',id:8}),project=A.selection(m,{mode:'project',id:113}),stage=A.selection(m,{mode:'project',id:113,stage:617});
assert.deepEqual(learned.explicit,new Set(raw.progress.filter(p=>p.is_learned===true).map(p=>'topic:'+p.topic_id)));
assert.deepEqual(accepted.explicit,new Set(raw.personal));assert.deepEqual(course.topics,new Set(raw.courses.find(c=>c.id===8).topic_ids.map(id=>'topic:'+id)));assert.deepEqual(project.topics,new Set(raw.projects.find(p=>p.id===113).required));assert.deepEqual(stage.topics,new Set(raw.projects.find(p=>p.id===113).stages.find(s=>s.id===617).required_topic_ids.map(id=>'topic:'+id)));
assert([...learned.context].every(k=>!learned.learned.has(k)));assert(accepted.topics.size>learned.topics.size);assert.equal(C.slot('reference:333'),C.slot('topic:333'));assert.equal(m.nodes.get('topic:36').parents.length,2);
assert.equal(A.search(m,'reference:36')[0].key,'topic:36');assert.equal(A.search(m,'topic:333')[0].key,'reference:333');assert.equal(A.search(m,'leaf:333').length,1);
const collapseSet=new Set(m.roots.map(n=>n.key)),collapsed=A.layout(m,accepted,{measure,collapsed:collapseSet});verify(accepted,collapsed);assert.equal(collapsed.positions.size,1);assert.equal(collapsed.positions.get(m.roots[0].key).stats.topics,accepted.topics.size);
const growth=[];for(const name of ['growth-branch','growth-wide']){let before;for(let step=0;step<4;step++){const s=A.selection(m,{mode:'fixture:'+name,step}),l=A.layout(m,s,{measure});verify(s,l);if(before)growth.push({fixture:name,step,movement:A.movement(before,l)});before=l;assert.equal(s.learned.size,0);assert.equal(s.verified.size,0);}}
// One comparison for each global entity, after all local operations.
assert.equal(JSON.stringify(geo),geometryJSON);let comparisons=0;for(const row of original){const n=m.nodes.get(row[0]);assert.deepEqual([n.key,n.x,n.y,n.w,n.h,n.parent,n.sibling_order],row);comparisons++;}
fs.writeFileSync(__dirname+'/core-results.json',JSON.stringify({scenes:results,growth,globalEntityComparisons:comparisons,globalDisplacement:0,checks:'PASS IDs, aliases, membership, unknown vs empty, card/route collisions, order, repeatability, collapse, fixture isolation, immutable global geometry'},null,2)+'\n');console.log(JSON.stringify({scenes:results,globalEntityComparisons:comparisons,checks:'PASS'},null,2));
module.exports={collisionChecks,verify};
