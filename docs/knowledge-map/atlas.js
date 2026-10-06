/* Independent exploratory geography: no V6 geometry, allocation or activation API. */
(function(g){
function freeze(v){if(v&&typeof v==='object'){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
function slot(key){return key.startsWith('category:')?key:'leaf:'+key.split(':')[1];}
function index(raw,geometry){
 freeze(geometry);const slots=new Map(geometry.positions.map(p=>[p.key,p]));
 const nodes=new Map(raw.entities.map(r=>{const p=slots.get(slot(r.key));return [r.key,{...r,...p,key:r.key,slot:p.key,geometry:p,parent:p.primary_parent,children:[]}];}));
 for(const n of nodes.values())for(const prop of ['x','y','w','h','depth','parent','region','geometry'])Object.defineProperty(n,prop,{writable:false});
 for(const n of nodes.values())if(n.parent)nodes.get(n.parent).children.push(n);
 for(const n of nodes.values())n.children.sort((a,b)=>n.sibling_order.indexOf(a.slot)-n.sibling_order.indexOf(b.slot));
 return {raw,geometry,nodes,roots:geometry.root_sectors.map(s=>nodes.get(s.root))};
}
function branch(m,n){return n.kind==='category'?n.region:n;}
function closure(m,seeds){
 const found=new Set(),todo=[...seeds];while(todo.length){const key=todo.pop();if(found.has(key))continue;
  const n=m.nodes.get(key);if(!n)continue;found.add(key);todo.push(...n.parents);
 }return found;
}
function scope(m,mode,id,stage=null){
 if(mode==='global')return new Set(m.nodes.keys());
 if(mode==='my')return closure(m,m.raw.personal);
 if(mode==='course')return closure(m,(m.raw.courses.find(c=>c.id===Number(id))?.scope)||[]);
 const p=m.raw.projects.find(p=>p.id===Number(id));
 return closure(m,stage==null?p?.required||[]:p?.requirements.filter(e=>e.stage_id===Number(stage)).map(e=>e.target)||[]);
}
function search(m,q){q=q.trim().toLowerCase();return q?[...m.nodes.values()].filter(n=>(n.key+' '+n.slot+' '+(n.title||'')).toLowerCase().includes(q)):[];}
function bounds(nodes){const a=[...nodes];return a.length?{x:Math.min(...a.map(n=>n.x)),y:Math.min(...a.map(n=>n.y)),
 w:Math.max(...a.map(n=>n.x+n.w))-Math.min(...a.map(n=>n.x)),h:Math.max(...a.map(n=>n.y+n.h))-Math.min(...a.map(n=>n.y))}:null;}
const api={index,slot,branch,closure,scope,search,bounds};if(typeof module!=='undefined')module.exports=api;else g.GlobalAtlasCore=api;
})(globalThis);
