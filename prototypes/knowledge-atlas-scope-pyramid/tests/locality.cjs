// Disposable taxonomy: these identities and relationships are never evidence.
const assert=require('node:assert/strict');
require('../projection.js');require('../routing.js');require('../layout.js');
const raw={categories:[{id:10,title:'Alpha'},{id:11,title:'Child A'},{id:12,title:'Leaf A'},{id:20,title:'Beta'},{id:21,title:'Child B'},{id:22,title:'Leaf B'}],topics:[{id:111,title:'Short'},{id:222,title:'Other'}],memberships:{11:[10],12:[11],111:[12],21:[20],22:[21],222:[22]},progress:{topics:[]}};
const measure=(s,font=14)=>s.length*font*.5,make=r=>ScopePyramid('synthetic','locality',r.topics.map(t=>t.id),[],r,measure);
const a=make(raw),tall=structuredClone(raw);
for(let i=0;i<100;i++){const id=1000+i;tall.topics.push({id,title:'A full title with several words to wrap across multiple lines'});tall.memberships[id]=[12];}
const b=make(tall),other=structuredClone(tall);other.categories[0].title='A much longer unrelated root title that requires more than a single line';const c=make(other);
assert.deepEqual(a.L.levelCoherence.cardDepthBands,b.L.levelCoherence.cardDepthBands,'tray height does not participate in depth bands');
assert.deepEqual(b.L.levelCoherence.cardDepthBands['category:20'],c.L.levelCoherence.cardDepthBands['category:20'],'independent root card bands');
const beta=L=>[20,21,22,222].map(id=>{const n=L.byKey.get((id===222?'topic:':'category:')+id),r=L.byKey.get('category:20');return[n.key,n.x-r.x,n.y-r.y,n.width,n.height];});
assert.deepEqual(beta(a.L),beta(b.L),'tall unrelated tray does not affect Beta internal geometry');
assert.deepEqual(beta(b.L).filter(r=>r[0].startsWith('category:')),beta(c.L).filter(r=>r[0].startsWith('category:')),'tall unrelated root card does not affect Beta Category baselines');
assert(AtlasLayout.LEVEL.maxPenaltyRatio>0&&AtlasLayout.LEVEL.maxPenaltyRatio<=1,'bounded level penalty');
console.log('PASS: card-only bands, independent roots, local tray overflow, bounded scoring');
