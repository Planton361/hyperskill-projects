/* Independent exploratory geography: no V6 geometry, allocation or activation API. */
(function(g){
function index(raw){
 const nodes=new Map(raw.entities.map(r=>[r.key,{...r,children:[]} ]));
 for(const n of nodes.values()){
  // One visual position. All memberships remain in raw data and the inspector.
  n.parent=n.parents.includes('category:'+n.canonical_parent)?'category:'+n.canonical_parent:n.parents[0];
  if(n.parent)nodes.get(n.parent).children.push(n);
 }
 for(const n of nodes.values())n.children.sort((a,b)=>a.key.localeCompare(b.key,'en'));
 const roots=raw.roots.map(k=>nodes.get(k));
 function weigh(n,depth){n.depth=depth;n.weight=Math.max(1,n.children.reduce((s,c)=>s+weigh(c,depth+1),0));return n.weight;}
 roots.forEach(n=>weigh(n,0));
 return {raw,nodes,roots};
}
function layout(m){
 // Balanced binary treemap partition; root space is intentionally equal for navigation.
 function partition(items,x,y,w,h){
  if(!items.length)return;
  if(items.length===1){place(items[0],x,y,w,h);return;}
  const total=items.reduce((s,n)=>s+n.weight,0);let sum=0,cut=1;
  for(let i=0;i<items.length-1;i++){sum+=items[i].weight;cut=i+1;if(sum>=total/2)break;}
  const f=sum/total;
  if(w>=h){partition(items.slice(0,cut),x,y,w*f,h);partition(items.slice(cut),x+w*f,y,w*(1-f),h);}
  else {partition(items.slice(0,cut),x,y,w,h*f);partition(items.slice(cut),x,y+h*f,w,h*(1-f));}
 }
 function place(n,x,y,w,h){
  Object.assign(n,{x,y,w,h});
  const pad=Math.min(8,w*.035,h*.035),band=Math.min(34,h*.18);
  partition(n.children,x+pad,y+band,w-2*pad,h-band-pad);
 }
 m.roots.forEach((n,i)=>place(n,(i%3)*2100,Math.floor(i/3)*1700,2040,1640));
 return m;
}
function closure(m,seeds){
 const found=new Set(),todo=[...seeds];while(todo.length){const key=todo.pop();if(found.has(key))continue;
  const n=m.nodes.get(key);if(!n)continue;found.add(key);todo.push(...n.parents);
 }return found;
}
function scope(m,mode,id,stage=null){
 if(mode==='global')return new Set(m.nodes.keys());
 if(mode==='my')return new Set(m.raw.personal);
 if(mode==='course')return closure(m,(m.raw.courses.find(c=>c.id===Number(id))?.scope)||[]);
 const p=m.raw.projects.find(p=>p.id===Number(id));
 return closure(m,stage==null?p?.required||[]:p?.requirements.filter(e=>e.stage_id===Number(stage)).map(e=>e.target)||[]);
}
function search(m,q){q=q.trim().toLowerCase();return q?[...m.nodes.values()].filter(n=>(n.key+' '+(n.title||'')).toLowerCase().includes(q)):[];}
function bounds(nodes){const a=[...nodes];return a.length?{x:Math.min(...a.map(n=>n.x)),y:Math.min(...a.map(n=>n.y)),
 w:Math.max(...a.map(n=>n.x+n.w))-Math.min(...a.map(n=>n.x)),h:Math.max(...a.map(n=>n.y+n.h))-Math.min(...a.map(n=>n.y))}:null;}
const api={index,layout,closure,scope,search,bounds};if(typeof module!=='undefined')module.exports=api;else g.GlobalAtlasCore=api;
})(globalThis);
