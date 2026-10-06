/* One semantic registry, separate immutable reference positions, no Catalog x/y. */
(function(g){
'use strict';
const C=typeof module!=='undefined'?require('../canonical_runtime/atlas.js'):g.GlobalAtlasCore;
function freeze(v){if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
function index(raw,geometry){
 freeze(raw);freeze(geometry);
 const entities=new Map(raw.entities.map(e=>[e.key,e])),slots=new Map(geometry.positions.map(p=>[p.key,p])),reference=new Map(),nodes=new Map();
 if(entities.size!==raw.entities.length)throw Error('Duplicate semantic identity');
 for(const e of entities.values()){
  if(['x','y','w','h'].some(k=>k in e))throw Error('Catalog contains presentation coordinates');
  const p=slots.get(C.slot(e.key));if(!p)throw Error('Missing global reference '+e.key);reference.set(e.key,p);
  // Taxonomy adapter inherits the single semantic record, without copying coordinates.
  const n=Object.assign(Object.create(e),{entity:e,slot:p.key,parent:p.primary_parent,depth:p.depth,root:p.root,sibling_order:p.sibling_order,children:[]});nodes.set(e.key,n);
 }
 for(const n of nodes.values())if(n.parent)nodes.get(n.parent).children.push(n);
 for(const n of nodes.values()){n.children.sort((a,b)=>n.sibling_order.indexOf(a.slot)-n.sibling_order.indexOf(b.slot));Object.freeze(n.children);Object.freeze(n);}
 return {raw,entities,nodes,reference,geometry,roots:geometry.root_sectors.map(s=>nodes.get(s.root))};
}
function replaceSnapshot(m,raw){
 if(JSON.stringify(raw.entities)!==JSON.stringify(m.raw.entities)||JSON.stringify(raw.hierarchy)!==JSON.stringify(m.raw.hierarchy))throw Error('Registry changed; rebuild reference-bound preview');
 for(const r of raw.progress){if(!m.entities.has('topic:'+r.topic_id))throw Error('Unknown progress identity');if(r.is_verified!==(r.verification_status==='verified'))throw Error('Verification status mismatch');}
 freeze(raw);return {...m,raw};
}
const api={index,replaceSnapshot,freeze};if(typeof module!=='undefined')module.exports=api;else g.AtlasRegistry=api;
})(globalThis);
