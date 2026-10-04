/* Presentation mutations only. Model facts are always read from AtlasModel. */
(function(g){
'use strict';
const SCHEMA=2,ALGORITHM='atlas-incremental-2',clone=x=>JSON.parse(JSON.stringify(x));
function serialize(L){return {nodes:L.nodes.map(({data,...n})=>n),trays:L.trays,branches:L.branches,
 connectorSegments:L.connectorSegments,buses:[],bounds:AtlasLayout.contentBounds(L,L.nodes)};}
function hydrate(m,geometry,checkpoint){
 const nodes=geometry.nodes.map(n=>({...n,data:m.nodes.get(n.key)})),byKey=new Map(nodes.map(n=>[n.key,n]));
 return {...geometry,nodes,byKey,checkpoint,bands:new Map(),plans:new Map(),events:[],trayPackingMilliseconds:0};
}
function bootstrap(m,measure,legacy,generation=0){
 const L=AtlasLayout.build(m,measure,legacy),geometry=serialize(L),categories={};
 for(const [key,r] of Object.entries(L.checkpoint.categories)){
  const n=L.byKey.get(key);
  categories[key]={slot_anchor:{x:n.x,y:n.y},visible_extent:{left:-r.anchor,top:0,width:r.width,height:r.height},
   allocated_width:r.width,allocated_height:r.height,reserved_capacity:{width:0,height:0},
   sibling_order:r.sibling_order,topic_order:m.nodes.get(key).children.filter(n=>n.type==='topic').map(n=>n.key)};
 }
 const checkpoint={layout_schema_version:SCHEMA,layout_algorithm_version:ALGORITHM,presentation_generation:generation,categories};
 refresh(m,geometry,checkpoint,false);
 return {geometry,checkpoint,events:[],repacked_trays:[]};
}
function categoryCard(n,depth,measure){
 const font=AtlasLayout.categorySize(depth),text=t=>measure(t,font,depth===0?650:600),min=depth===0?320:depth===1?300:190,max=depth===0?360:depth===1?340:240,candidates=[];
 for(let limit=min;limit<=max;limit+=8){const lines=AtlasLayout.wrap(n.title,text,limit-44);if(lines.length>3)continue;const width=Math.max(min,Math.ceil(Math.max(measure('89 / 89 learned',10,400),...lines.map(text))+44)),line=font*1.18,height=lines.length*line+(depth>=2?25:30);candidates.push({width,height,font,line,lines,score:width*height+width*20+lines.length*100});}
 const r=candidates.sort((a,b)=>a.score-b.score)[0];if(!r)throw Error('Category label requires explicit layout migration: '+n.key);delete r.score;return r;
}
function refresh(m,geometry,cp,expand=true){
 const byKey=new Map(geometry.nodes.map(n=>[n.key,n])),trays=new Map(geometry.trays.map(t=>[t.parent,t]));
 function visit(n){
  const r=cp.categories[n.key],a=byKey.get(n.key);let left=-a.width/2-16,right=a.width/2+16,bottom=a.height+16;
  for(const c of n.children.filter(c=>c.type==='category')){visit(c);const child=cp.categories[c.key],b=byKey.get(c.key),e=child.visible_extent;left=Math.min(left,b.x-a.x+e.left);right=Math.max(right,b.x-a.x+e.left+e.width);bottom=Math.max(bottom,b.y-a.y+e.height);}
  const t=trays.get(n.key);if(t){left=Math.min(left,t.x-a.x-20);right=Math.max(right,t.x-a.x+t.width+20);bottom=Math.max(bottom,t.y-a.y+t.height+20);}
  // Retain allocated left boundary so append growth never recenters an old region.
  left=Math.min(left,r.visible_extent.left);
  const width=right-left,height=bottom;
  if(expand){r.allocated_width=Math.max(r.allocated_width,width);r.allocated_height=Math.max(r.allocated_height,height);}
  r.visible_extent={left,top:0,width,height};r.slot_anchor={x:a.x,y:a.y};
  r.reserved_capacity={width:Math.max(0,r.allocated_width-width),height:Math.max(0,r.allocated_height-height)};
 }
 visit(m.root);
}
function update(m,measure,previous,geometry,diff,rebalance=false,budget={max:Infinity,significant:100,major:Infinity}){
 const generation=previous.presentation_generation;
 if(rebalance)return bootstrap(m,measure,null,generation+1);
 const cp=clone(previous),out=clone(geometry),byKey=new Map(out.nodes.map(n=>[n.key,n])),trays=new Map(out.trays.map(t=>[t.parent,t])),events=[],repacks=new Set();
 const live=new Set(m.nodes.keys());out.nodes=out.nodes.filter(n=>live.has(n.key));out.trays=out.trays.filter(t=>live.has(t.parent));
 for(const key of diff.label_changes||[]){
  const n=m.nodes.get(key),a=byKey.get(key);if(!n||!a)continue;
  if(n.type==='category'){
   Object.assign(a,categoryCard(n,a.depth,measure));
   const t=trays.get(key);if(t&&t.y<a.y+a.height+68){const dy=a.y+a.height+68-t.y;t.y+=dy;for(const k of t.topics)byKey.get(k).y+=dy;repacks.add(key);}
  }else{
   const t=trays.get(a.parent),card=AtlasLayout.pack([n],measure,Infinity,1).items[0],dy=card.height-a.height;
   a.lines=card.lines;a.width=card.width;a.height=card.height;
   for(const k of t.topics)if(byKey.get(k).y>a.y)byKey.get(k).y+=dy;
   t.height+=dy;t.width=Math.max(t.width,card.width+16);repacks.add(t.parent);
  }
 }
 for(const k of Object.keys(cp.categories))if(!live.has(k))delete cp.categories[k];
 for(const n of m.nodes.values())if(n.type==='category'&&cp.categories[n.key]){
  const r=cp.categories[n.key];r.sibling_order=r.sibling_order.filter(k=>live.has(k));r.topic_order=r.topic_order.filter(k=>live.has(k));
  r.sibling_order.push(...n.children.filter(c=>c.type==='category'&&!r.sibling_order.includes(c.key)).sort((a,b)=>a.id-b.id).map(c=>c.key));
  r.topic_order.push(...n.children.filter(c=>c.type==='topic'&&!r.topic_order.includes(c.key)).sort((a,b)=>a.id-b.id).map(c=>c.key));
 }
 function shift(n,dx,dy){
  const a=byKey.get(n.key);a.x+=dx;a.y+=dy;
  if(n.type==='category'){
   cp.categories[n.key].slot_anchor={x:a.x,y:a.y};const t=trays.get(n.key);if(t){t.x+=dx;t.y+=dy;}
   for(const c of n.children)if(byKey.has(c.key))shift(c,dx,dy);
  }
 }
 function insert(n,depth,x,y){
  const card=categoryCard(n,depth,measure),a={key:n.key,x,y,depth,...card};byKey.set(n.key,a);out.nodes.push(a);
  cp.categories[n.key]={slot_anchor:{x,y},visible_extent:{left:-card.width/2-16,top:0,width:card.width+32,height:card.height+16},
   allocated_width:card.width+32,allocated_height:card.height+16,reserved_capacity:{width:0,height:0},
   sibling_order:n.children.filter(c=>c.type==='category').sort((a,b)=>a.id-b.id).map(c=>c.key),topic_order:[],slot_row:0};
 }
 function visit(n,depth){
  const r=cp.categories[n.key],a=byKey.get(n.key),gap=depth===0?112:64;
  let cursor=null,wrappedBottom=a.y+r.allocated_height+82;
  for(const key of r.sibling_order){
   const c=m.nodes.get(key);
   if(!cp.categories[key]){
    const card=categoryCard(c,depth+1,measure),right=r.visible_extent.left+r.allocated_width;
    const wrap=cursor!==null&&cursor+card.width+32>right;
    const prior=r.sibling_order.slice(0,r.sibling_order.indexOf(key)).filter(k=>byKey.has(k));
    const x=wrap?(byKey.get(prior.at(-1))?.x||a.x):cursor===null?a.x:a.x+cursor+card.width/2+16;
    insert(c,depth+1,x,wrap?wrappedBottom:a.y+a.height+82);cp.categories[key].slot_row=wrap?1:0;
    events.push({level:2,region:n.key,action:wrap?'append wrapped local category slot':'append category slot',category:key});
   }
   visit(c,depth+1);
   const cr=cp.categories[key],b=byKey.get(key),left=b.x-a.x+cr.visible_extent.left;
   const minimumY=a.y+a.height+76;if(b.y<minimumY)shift(c,0,minimumY-b.y);
   if(cr.slot_row){wrappedBottom=Math.max(wrappedBottom,b.y+cr.allocated_height+82);}
   else{
    if(cursor!==null&&left<cursor-.001){const dx=cursor-left;shift(c,dx,0);events.push({level:3,region:n.key,action:'shift immediate sibling subtree',category:key,displacement:dx});}
    cursor=byKey.get(key).x-a.x+cr.visible_extent.left+cr.allocated_width+gap;
   }
  }
  const wanted=n.children.filter(c=>c.type==='topic').map(c=>c.key),old=trays.get(n.key);
  const added=wanted.filter(k=>!byKey.has(k)).sort((a,b)=>m.nodes.get(a).id-m.nodes.get(b).id);
  const removed=(old?.topics||[]).filter(k=>!live.has(k));
  if(added.length||removed.length){
   repacks.add(n.key);let t=old;
   if(!t){t={parent:n.key,x:r.sibling_order.length?a.x+cursor:a.x-118,y:a.y+a.height+68,width:236,height:16,topics:[]};trays.set(n.key,t);out.trays.push(t);}
   t.topics=t.topics.filter(k=>live.has(k));r.topic_order=r.topic_order.filter(k=>live.has(k));
   const pack=AtlasLayout.pack(added.map(k=>m.nodes.get(k)),measure,Infinity,1);
   let bottom=Math.max(t.y+8,...t.topics.map(k=>byKey.get(k).y+byKey.get(k).height+4));
   for(const item of pack.items){const c=m.nodes.get(item.key),leaf={key:c.key,x:t.x+8+item.width/2,y:bottom,depth:depth+1,lines:item.lines,font:14,line:17,width:item.width,height:item.height,parent:n.key};byKey.set(c.key,leaf);out.nodes.push(leaf);bottom+=item.height+4;t.topics.push(c.key);if(!r.topic_order.includes(c.key))r.topic_order.push(c.key);}
   if(t.topics.length){t.width=Math.max(t.width,pack.width);t.height=Math.max(t.height,bottom-t.y+4);}else{trays.delete(n.key);out.trays=out.trays.filter(t=>t.parent!==n.key);}
   events.push({level:1,region:n.key,action:'local tray append/remove',added,removed});
  }
  const t=trays.get(n.key);
  if(t&&cursor!==null&&t.x<a.x+cursor+20){const dx=a.x+cursor+20-t.x;t.x+=dx;for(const key of t.topics)byKey.get(key).x+=dx;repacks.add(n.key);events.push({level:2,region:n.key,action:'expand lateral tray slot',displacement:dx});}
  const priorWidth=r.allocated_width,priorHeight=r.allocated_height;
  // Refresh only this region; children have already settled bottom-up.
  let left=r.visible_extent.left,right=a.width/2+16,bottom=a.height+16;
  for(const k of r.sibling_order){const b=byKey.get(k),cr=cp.categories[k];left=Math.min(left,b.x-a.x+cr.visible_extent.left);right=Math.max(right,b.x-a.x+cr.visible_extent.left+cr.allocated_width);bottom=Math.max(bottom,b.y-a.y+cr.allocated_height);}
  if(t){left=Math.min(left,t.x-a.x-20);right=Math.max(right,t.x-a.x+t.width+20);bottom=Math.max(bottom,t.y-a.y+t.height+20);}
  r.visible_extent={left,top:0,width:right-left,height:bottom};r.allocated_width=Math.max(r.allocated_width,right-left);r.allocated_height=Math.max(r.allocated_height,bottom);
  r.reserved_capacity={width:r.allocated_width-(right-left),height:r.allocated_height-bottom};
  if(r.allocated_width>priorWidth)events.push({level:depth===0?5:4,region:n.key,action:'expand parent capacity',required_width:r.allocated_width,available_width:priorWidth});
  if(r.allocated_height>priorHeight)events.push({level:depth===0?5:4,region:n.key,action:'expand vertical capacity',required_height:r.allocated_height,available_height:priorHeight});
 }
 visit(m.root,0);
 out.trays=out.trays.filter(t=>trays.has(t.parent));
 out.branches=[];for(const n of m.nodes.values())if(n.type==='category'&&n.canonical_parent_id!==null)out.branches.push({parent:'category:'+n.canonical_parent_id,child:n.key});
 out.connectorSegments=AtlasRouting.hierarchy(out.branches,byKey,[],[],out.trays,AtlasLayout.LAYOUT);out.buses=[];
 out.bounds=AtlasLayout.contentBounds({...out,byKey},out.nodes);
 const moves=geometry.nodes.filter(n=>n.key.startsWith('category:')&&byKey.has(n.key)).map(n=>({key:n.key,depth:n.depth,d:Math.hypot(n.x-byKey.get(n.key).x,n.y-byKey.get(n.key).y)}));
 const affected=moves.filter(n=>n.d>.001),max=Math.max(0,...affected.map(n=>n.d)),significant=100*affected.filter(n=>n.d>1).length/moves.length;
 if(max>budget.max||significant>budget.significant||affected.some(n=>n.depth===1&&n.d>budget.major)){
  const event=[...events].reverse().find(e=>e.required_width)||{region:m.root.key,required_width:cp.categories[m.root.key].allocated_width,available_width:previous.categories[m.root.key].allocated_width};
  return {status:'REBALANCE_REQUIRED',affected_region:event.region,required_width:event.required_width,available_width:event.available_width,
   affected_categories:affected.map(n=>n.key).sort(),estimated_displacement:max,significant_percentage:significant,events};
 }
 const changed=JSON.stringify(cp.categories)!==JSON.stringify(previous.categories);cp.presentation_generation=generation+(changed?1:0);
 out.nodes.sort((a,b)=>a.key.localeCompare(b.key));out.trays.sort((a,b)=>a.parent.localeCompare(b.parent));
 return {geometry:out,checkpoint:cp,events,repacked_trays:[...repacks].sort()};
}
g.AtlasIncremental={bootstrap,update,hydrate,serialize};
})(globalThis);
