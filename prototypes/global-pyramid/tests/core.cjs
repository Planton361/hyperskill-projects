const assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),C=require('../atlas.js');
const base=path.resolve(__dirname,'..'),raw=JSON.parse(fs.readFileSync(base+'/generated/catalog.json')),geo=JSON.parse(fs.readFileSync(base+'/generated/global-geometry.json')),m=C.index(raw,geo);
const baseline=JSON.stringify(geo),coords=k=>{const n=m.nodes.get(k);return [n.x,n.y,n.w,n.h];};
let overlaps=0;const global=new Map([...m.nodes.keys()].map(k=>[k,coords(k)]));
for(const mode of ['global','my','course','project'])for(const key of C.scope(m,mode,mode==='project'?113:8)){assert.deepEqual(coords(key),global.get(key));assert.strictEqual(m.nodes.get(key).geometry,geo.positions.find(p=>p.key===C.slot(key)));overlaps++;}
assert.equal(C.scope(m,'my').size,135);
assert(!fs.readFileSync(base+'/app.js','utf8').includes('C.layout('));
assert.equal(C.layout,undefined);
const before=new Map([...C.scope(m,'my')].map(k=>[k,coords(k)]));
const added=[];let visible=new Set(before.keys());
for(const seeds of [['reference:333','category:428'],['reference:2931','category:2930']]){
 const next=C.closure(m,[...visible,...seeds]);for(const [k,p]of before)assert.deepEqual(coords(k),p);
 for(const k of seeds){assert.deepEqual(coords(k),(()=>{const p=geo.positions.find(p=>p.key===C.slot(k));return [p.x,p.y,p.w,p.h];})());added.push(k);}
 for(const k of next)before.set(k,coords(k));visible=next;
}
for(const p of raw.progress){p.is_learned=!p.is_learned;p.is_verified=!p.is_verified;}
assert.equal(JSON.stringify(geo),baseline);assert(Object.isFrozen(geo.positions[0]));
assert.throws(()=>{ 'use strict';geo.positions[0].x++;},TypeError);
assert.equal(C.slot('reference:333'),C.slot('topic:333'));
assert.equal(C.scope(m,'project',380).size,0);assert.equal([...C.scope(m,'project',113,617)].filter(k=>k.startsWith('topic:')).length,12);
console.log(JSON.stringify({scopeCoordinateComparisons:overlaps,activations:2,added,maximumDisplacementPx:0,geometryFrozen:true}));
