/* Reconstruct derived geometry from presentation allocation, without topic x/y. */
(function(g){
'use strict';
const round=x=>Math.round(x*1e6)/1e6;
function capture(m,geometry,internal,previous=null){
 const nodes=new Map(geometry.nodes.map(n=>[n.key,n])),trays=new Map(geometry.trays.map(t=>[t.parent,t])),categories={};
 for(const n of m.nodes.values())if(n.type==='category'){
  const a=nodes.get(n.key),parent=nodes.get('category:'+n.canonical_parent_id),r=internal.categories[n.key],t=trays.get(n.key),old=previous?.categories[n.key];
  const priorRows=old?.tray_allocation?.rows||[],rowKeys=priorRows.map(s=>s.key);
  if(t)for(const key of t.topics)if(!rowKeys.includes(key))rowKeys.push(key);
  const rows=rowKeys.map(key=>{const a=nodes.get(key),old=priorRows.find(s=>s.key===key);return a?{key,width:a.width,height:a.height}:old;});
  categories[n.key]={...r,slot_row:r.slot_row||0,
   slot_anchor:{x:round(a.x-(parent?.x||0)),y:round(a.y-(parent?.y||0))},
   card_allocation:{width:a.width,height:a.height,font:a.font,line:a.line},
   tray_allocation:t?{left:round(t.x-a.x),top:round(t.y-a.y),width:t.width,height:t.height,padding:8,row_gap:4,rows}:null};
 }
 return {state_schema_version:2,layout_schema_version:2,layout_algorithm_version:'atlas-incremental-2',
  presentation_generation:internal.presentation_generation,categories};
}
function restore(m,measure,cp,activeKeys=null){
 const live=activeKeys?new Set(activeKeys):new Set(m.nodes.keys()),parents=new Map();
 for(const [key,r]of Object.entries(cp.categories))for(const child of r.sibling_order)parents.set(child,key);
 const nodes=[],byKey=new Map(),trays=[],branches=[],internal=JSON.parse(JSON.stringify(cp));
 function visit(key,px,py,depth){
  const r=cp.categories[key];if(!r)throw Error('Missing persistent region '+key);
  const n=m.nodes.get(key),a={key,x:px+r.slot_anchor.x,y:py+r.slot_anchor.y,depth,...r.card_allocation};
  const min=depth===0?320:depth===1?300:190,max=depth===0?360:depth===1?340:240,font=a.font;
  const text=t=>measure(t,font,depth===0?650:600),candidates=[];
  for(let limit=min;limit<=max;limit+=8){const lines=AtlasLayout.wrap(n?.title||'',text,limit-44);if(lines.length>3)continue;const width=Math.max(min,Math.ceil(Math.max(measure('89 / 89 learned',10,400),...lines.map(text))+44)),height=lines.length*font*1.18+(depth>=2?25:30);candidates.push({lines,score:width*height+width*20+lines.length*100});}
  a.lines=candidates.sort((a,b)=>a.score-b.score)[0]?.lines||[n?.title||''];
  nodes.push(a);byKey.set(key,a);internal.categories[key].slot_anchor={x:a.x,y:a.y};
  const allocation=r.tray_allocation;
  if(allocation){
   const t={parent:key,x:a.x+allocation.left,y:a.y+allocation.top,width:0,height:0,topics:[]};let offset=allocation.padding;
   for(const slot of allocation.rows){
    if(live.has(slot.key)){
     const topic=m.nodes.get(slot.key),item=topic?AtlasLayout.pack([topic],measure,Infinity,1).items[0]:null;
     const leaf={key:slot.key,x:t.x+allocation.padding+slot.width/2,y:t.y+offset,depth:depth+1,
       lines:item?.lines||[''],font:14,line:17,width:slot.width,height:slot.height,parent:key};nodes.push(leaf);byKey.set(slot.key,leaf);t.topics.push(slot.key);
     t.width=Math.max(t.width,slot.width+2*allocation.padding);t.height=offset+slot.height+allocation.padding;
    }
    offset+=slot.height+allocation.row_gap;
   }
   if(t.topics.length)trays.push(t);
  }
  for(const child of r.sibling_order){visit(child,a.x,a.y,depth+1);branches.push({parent:key,child});}
 }
 const roots=Object.keys(cp.categories).filter(k=>!parents.has(k));if(roots.length!==1)throw Error('Invalid persistent region tree');visit(roots[0],0,0,0);
 const connectorSegments=AtlasRouting.hierarchy(branches,byKey,[],[],trays,AtlasLayout.LAYOUT),L={nodes,byKey,trays,branches,connectorSegments,buses:[]};
 if(Object.values(cp.categories).some(r=>r.slot_row)){
  for(const e of branches)if(cp.categories[e.child].slot_row){
   const a=byKey.get(e.parent),b=byKey.get(e.child),r=cp.categories[e.parent],rail=a.x+r.visible_extent.left+r.allocated_width-8,bus=a.y+a.height+28;
   e.points=[{x:a.x,y:a.y+a.height},{x:a.x,y:bus},{x:rail,y:bus},{x:rail,y:b.y-30},{x:b.x,y:b.y-30},{x:b.x,y:b.y}];
   e.d=e.points.map((p,i)=>(i?'L':'M')+p.x+','+p.y).join('');
  }
  const all=[...branches];for(const t of trays){const a=byKey.get(t.parent),source={x:a.x,y:a.y+a.height},target={x:t.x+t.width/2,y:t.y};all.push({parent:t.parent,child:t.topics[0],topics:t.topics,points:[source,{x:a.x,y:source.y+28},{x:target.x,y:source.y+28},target]});}
  L.connectorSegments=AtlasRouting.sharedSegments(all,byKey);
  for(const segment of L.connectorSegments)segment.children=[...new Set(segment.children.flatMap(k=>all.find(e=>e.parent===segment.parent&&e.child===k)?.topics||[k]))];
 }
 return {geometry:AtlasIncremental.serialize(L),checkpoint:internal};
}
g.AtlasPersistent={capture,restore};
})(globalThis);
