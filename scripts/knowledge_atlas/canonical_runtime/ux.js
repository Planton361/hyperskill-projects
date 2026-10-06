/* Presentation-only projections and cameras. No layout generation or geometry writes. */
(function(g){
'use strict';
const C=typeof module!=='undefined'?require('./atlas.js'):g.GlobalAtlasCore;
function projection(m,mode,id,stage=null,ghost='local',selected=null){
 let explicit;
 if(mode==='global')explicit=new Set(m.nodes.keys());
 else if(mode==='my')explicit=new Set(m.raw.personal);
 else if(mode==='course'){const c=m.raw.courses.find(c=>c.id===Number(id));explicit=new Set(c?[...c.category_ids.map(i=>'category:'+i),...c.topic_ids.map(i=>m.nodes.has('topic:'+i)?'topic:'+i:'reference:'+i)]:[]);}
 else {const p=m.raw.projects.find(p=>p.id===Number(id));explicit=new Set(stage==null?p?.required||[]:p?.requirements.filter(e=>e.stage_id===Number(stage)).map(e=>e.target)||[]);}
 explicit=new Set([...explicit].filter(k=>m.nodes.has(k)));
 const corridor=C.closure(m,explicit),ancestors=new Set([...corridor].filter(k=>!explicit.has(k))),ghosts=new Set();
 if(ghost!=='none')for(const k of ancestors)ghosts.add(k);
 if(mode!=='global'&&ghost==='local')for(const k of corridor){const n=m.nodes.get(k),p=m.nodes.get(n.parent);if(p)for(const sibling of p.children)if(!corridor.has(sibling.key))ghosts.add(sibling.key);}
 const inspected=selected?C.closure(m,[selected]):new Set();
 const density=new Map();
 for(const k of explicit){const n=m.nodes.get(k);if(n.kind==='category')continue;let a=n;while(a){density.set(a.key,(density.get(a.key)||0)+1);a=m.nodes.get(a.parent);}}
 return {explicit,corridor,ancestors,ghosts,inspected,density,unknown:mode==='project'&&m.raw.projects.find(p=>p.id===Number(id))?.requirements_status==='UNKNOWN'};
}
function inside(n,branch,m){let a=n;while(a){if(a.key===branch.key)return true;a=m.nodes.get(a.parent);}return false;}
function focusBounds(m,p,key){const n=m.nodes.get(key);if(!n)return null;if(n.kind!=='category')return C.bounds([n]);
 const relevant=[...p.explicit].map(k=>m.nodes.get(k)).filter(a=>inside(a,n,m));
 // In a revealed branch fit the cards, never the full dormant allocated region.
 return relevant.length&&relevant.length<m.nodes.size?C.bounds([n,...relevant]):n.region;
}
function scopeBounds(m,p){
 const seeds=[...p.explicit].map(k=>m.nodes.get(k)),leaves=seeds.filter(n=>n.kind!=='category');
 if(!seeds.length)return null;
 // Immediate structural parents provide local context. Root corridors remain available
 // outside the viewport and on the complete-world minimap.
 return C.bounds(leaves.length?[...leaves,...new Set(leaves.flatMap(n=>n.parents.map(k=>m.nodes.get(k))))]:seeds);
}
function camera(b,width,height,pad={left:32,right:32,top:155,bottom:155}){
 if(!b)return null;const w=Math.max(1,width-pad.left-pad.right),h=Math.max(1,height-pad.top-pad.bottom),k=Math.min(6,w/Math.max(1,b.w),h/Math.max(1,b.h));
 return {k,x:pad.left+w/2-(b.x+b.w/2)*k,y:pad.top+h/2-(b.y+b.h/2)*k};
}
function branchGroups(m,p,depth=2){const groups=new Map();for(const key of p.explicit){let n=m.nodes.get(key);if(n.kind==='category')continue;while(n.parent&&n.depth>depth)n=m.nodes.get(n.parent);if(!groups.has(n.key))groups.set(n.key,{node:n,count:0});groups.get(n.key).count++;}return [...groups.values()].sort((a,b)=>b.count-a.count||a.node.x-b.node.x);}
function stats(m,p,key){
 const branch=m.nodes.get(key),topics=[...p.explicit].map(k=>m.nodes.get(k)).filter(n=>n.kind!=='category'&&inside(n,branch,m)),rows=m.raw.progress;
 return {topics:topics.length,learned:topics.filter(n=>rows.some(r=>r.topic_id===n.id&&r.is_learned===true)).length,verified:topics.filter(n=>rows.some(r=>r.topic_id===n.id&&r.is_verified===true)).length};
}
function regions(m,p,mode){return (mode==='global'?m.roots.map(node=>({node,count:p.density.get(node.key)||0})):branchGroups(m,p)).sort((a,b)=>a.node.x-b.node.x||a.node.id-b.node.id);}
const api={projection,scopeBounds,focusBounds,camera,branchGroups,inside,stats,regions};if(typeof module!=='undefined')module.exports=api;else g.GlobalPyramidUX=api;
})(globalThis);
