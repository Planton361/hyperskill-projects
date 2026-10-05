const assert=require('node:assert/strict'),C=require('../atlas.js'),raw=require('../generated/catalog.json');
const m=C.layout(C.index(raw)),geometry=JSON.stringify([...m.nodes.values()].map(n=>[n.key,n.x,n.y,n.w,n.h]));
assert.equal(m.nodes.size,3955);assert.equal(m.roots.length,5);assert.equal(Math.max(...[...m.nodes.values()].map(n=>n.depth)),8);
for(const n of m.nodes.values()){assert.ok(n.w>0&&n.h>0);if(n.parent){const p=m.nodes.get(n.parent);assert.ok(n.x>=p.x&&n.y>=p.y&&n.x+n.w<=p.x+p.w+.001&&n.y+n.h<=p.y+p.h+.001);}}
for(let i=0;i<100;i++){assert.equal(C.scope(m,'global').size,3955);assert.equal(C.scope(m,'my').size,135);assert.equal(C.scope(m,'course',8).size,135);assert.equal([...C.scope(m,'project',113)].filter(k=>k.startsWith('topic:')).length,26);assert.equal(C.scope(m,'project',380).size,0);}
assert.equal([...C.scope(m,'project',113,617)].filter(k=>k.startsWith('topic:')).length,12);
assert.equal(C.search(m,'reference:333')[0].kind,'reference');assert.ok(C.search(m,'Python').length>0);
assert.equal(m.nodes.size,3955);assert.equal(JSON.stringify([...m.nodes.values()].map(n=>[n.key,n.x,n.y,n.w,n.h])),geometry);
const d=structuredClone(raw);d.courses.push({...d.courses[0],id:99999,key:'course:99999',title:'SYNTHETIC'});d.projects.push({...d.projects.find(p=>p.id===113),id:99999,key:'project:99999',title:'SYNTHETIC'});
const mm=C.layout(C.index(d));assert.deepEqual(C.scope(mm,'course',99999),C.scope(mm,'course',8));assert.deepEqual(C.scope(mm,'project',99999),C.scope(mm,'project',113));assert.equal(mm.nodes.size,3955);
assert.equal(JSON.stringify([...mm.nodes.values()].map(n=>[n.key,n.x,n.y,n.w,n.h])),geometry);
d.personal=d.entities.filter(n=>n.kind!=='reference').map(n=>n.key);const grown=C.layout(C.index(d));assert.equal(C.scope(grown,'my').size,938);assert.equal(grown.nodes.size,3955);assert.equal(JSON.stringify([...grown.nodes.values()].map(n=>[n.key,n.x,n.y,n.w,n.h])),geometry);
console.log('PASS: geometry, roots, depth, deduplication, scopes, synthetic sharing, search, references');
