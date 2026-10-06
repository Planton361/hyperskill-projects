/* Read-only selections and derived local geometry. No Catalog or progress writes. */
(function(g){
'use strict';
const C=typeof module!=='undefined'?require('../canonical_runtime/atlas.js'):g.GlobalAtlasCore;
const L=typeof module!=='undefined'?require('../canonical_runtime/labels.js'):g.PyramidLabels;
function keyFor(m,id){return m.nodes.has('topic:'+id)?'topic:'+id:m.nodes.has('reference:'+id)?'reference:'+id:null;}
function search(m,q){const alias=/^(?:topic|reference|leaf):(\d+)$/.exec(q.trim());if(alias){const n=m.nodes.get(keyFor(m,Number(alias[1])));return n?[n]:[];}return C.search(m,q);}
function progress(m){return {learned:new Set(m.raw.progress.filter(r=>r.is_learned===true).map(r=>'topic:'+r.topic_id)),verified:new Set(m.raw.progress.filter(r=>r.is_verified===true).map(r=>'topic:'+r.topic_id))};}
function ordered(m){const out=[];function walk(n){if(n.kind!=='category')out.push(n.key);for(const c of n.children)walk(c);}m.roots.forEach(walk);return out;}
function fixture(m,name,step=0){
 const slots=ordered(m),groups=new Map();for(const k of slots){const p=m.nodes.get(k).parent;if(!groups.has(p))groups.set(p,[]);groups.get(p).push(k);}
 if(name==='growth-branch'){const group=[...groups.values()].find(a=>a.length>=12);return new Set(group.slice(0,[1,3,6,12][Math.min(3,step)]));}
 if(name==='growth-wide'){const a=[...groups.values()],list=[];for(let i=0;i<12;i++)for(const group of a.filter((_,j)=>j%Math.max(1,Math.floor(a.length/8))===0))if(group[i])list.push(group[i]);return new Set(list.slice(0,[4,8,16,32][Math.min(3,step)]));}
 if(name==='broad'){const roots=m.roots.map(r=>slots.filter(k=>m.nodes.get(k).root===r.key)),list=[];for(let i=0;i<20;i++)for(const a of roots)if(a[i])list.push(a[i]);return new Set(list);}
 return new Set(slots.slice(0,name==='load-100'?100:name==='load-300'?300:name==='load-1000'?1000:slots.length));
}
function selection(m,opts={}){
 const o={mode:'learned',id:8,stage:null,onlyLearned:false,branch:null,step:0,...opts},p=progress(m);let explicit=new Set(),unknown=false,reason='';
 const isFixture=o.mode.startsWith('fixture:');
 if(o.mode==='global')explicit=new Set(m.nodes.keys());
 else if(isFixture)explicit=fixture(m,o.mode.slice(8),o.step);
 else if(o.mode==='learned')explicit=new Set(p.learned);
 else if(o.mode==='accepted')explicit=new Set(m.raw.personal);
 else if(o.mode==='course'){
  const c=m.raw.courses.find(c=>c.id===Number(o.id));unknown=!c;reason=unknown?'Kursmitgliedschaft UNKNOWN':'';
  if(c)explicit=new Set([...c.category_ids.map(id=>'category:'+id),...c.topic_ids.map(id=>keyFor(m,id)).filter(Boolean)]);
 }else if(o.mode==='project'){
  const project=m.raw.projects.find(p=>p.id===Number(o.id)),stage=project?.stages.find(s=>s.id===Number(o.stage));
  if(o.stage!=null){unknown=!stage||stage.required_topic_ids===null;if(stage?.required_topic_ids)explicit=new Set(stage.required_topic_ids.map(id=>keyFor(m,id)).filter(Boolean));}
  else {unknown=!project||project.requirements_status==='UNKNOWN';explicit=new Set(project?.required||[]);}
  reason=unknown?'Requirements UNKNOWN — vollständige Anforderungsmenge nicht belegt':'';
 }
 explicit=new Set([...explicit].filter(k=>m.nodes.has(k)));
 if(o.onlyLearned&&!isFixture)explicit=new Set([...explicit].filter(k=>p.learned.has(k)));
 if(o.branch){const branch=m.nodes.get(o.branch);explicit=new Set([...explicit].filter(k=>inside(m,k,branch?.key)));}
 const visible=C.closure(m,explicit),topics=new Set([...explicit].filter(k=>m.nodes.get(k).kind!=='category'));
 const counts=new Map();for(const k of topics)for(const a of C.closure(m,[k])){if(!counts.has(a))counts.set(a,{topics:0,learned:0,verified:0});const c=counts.get(a);c.topics++;if(!isFixture&&p.learned.has(k))c.learned++;if(!isFixture&&p.verified.has(k))c.verified++;}
 return {options:o,explicit,visible,topics,context:new Set([...visible].filter(k=>!explicit.has(k))),unknown,reason,isFixture,learned:isFixture?new Set():p.learned,verified:isFixture?new Set():p.verified,counts};
}
function inside(m,key,branch){let n=m.nodes.get(key);while(n){if(n.key===branch)return true;n=m.nodes.get(n.parent);}return false;}
function stats(m,s,key){return s.counts.get(key)||{topics:0,learned:0,verified:0};}
function title(n,s){return s.isFixture?(n.kind==='category'?'Fixture Category #':'Fixture Slot #')+n.id:n.title||'Unaufgelöste Referenz #'+n.id;}
function card(m,s,n,measure,collapsed=false){
 const category=n.kind==='category',font=category?'600 15px system-ui':'14px system-ui',max=category?220:200,min=category?168:156;
 const lines=L.wrap(title(n,s),t=>measure(t,font),max-28,8).lines,st=category?stats(m,s,n.key):null;
 const meta=category?(collapsed?'Zusammenfassung · ':'')+st.topics+(s.isFixture?' Slots':' Topics'):(s.isFixture?'Fixture · kein Fortschritt':s.learned.has(n.key)?'learned'+(s.verified.has(n.key)?' · verified':''):s.explicit.has(n.key)?'explizit · nicht gelernt':'Kontext');
 const count=category?(s.isFixture?'Keine Fortschrittsbehauptung':st.learned+' learned · '+st.verified+' verified'):'';
 const w=Math.ceil(Math.max(min,Math.min(max,Math.max(...lines.map(t=>measure(t,font)),measure(meta,'11px system-ui'),measure(count,'11px system-ui'))+28)));
 return {key:n.key,slot:n.slot,parent:n.parent,kind:n.kind,w,h:lines.length*18+(category?52:36),lines,font,meta,count,collapsed,stats:st,context:s.context.has(n.key)};
}
function layout(m,s,{collapsed=new Set(),measure}={}){
 if(!measure)throw Error('Explicit text measurement required');
 const start=performance.now(),positions=new Map(),groups=[],routes=[],hidden=new Set(),allCards=new Map();
 function hide(n){for(const c of n.children)if(s.visible.has(c.key)){hidden.add(c.key);hide(c);}}
 for(const k of collapsed)if(s.visible.has(k))hide(m.nodes.get(k));
 for(const k of s.visible)if(!hidden.has(k))allCards.set(k,card(m,s,m.nodes.get(k),measure,collapsed.has(k)));
 // Rectangular subtree contours deliberately forbid cross-depth interleaving.
 // This is the conservative tidy-tree variant needed by the full subtree-box contract.
 const padding=16,siblingGap=36,topGap=32,bottomGap=40,bands=new Map(),subtrees=new Map();
 function build(n){
  const a=allCards.get(n.key),children=[];let tray=null;
  if(!a.collapsed){
   const cards=n.children.filter(c=>c.kind!=='category'&&allCards.has(c.key)).map(c=>allCards.get(c.key));
   if(cards.length){
    const columns=Math.min(3,Math.ceil(Math.sqrt(cards.length/2))),colW=Array.from({length:columns},(_,col)=>Math.max(...cards.filter((_,i)=>i%columns===col).map(c=>c.w))),rows=[];
    for(let i=0;i<cards.length;i+=columns)rows.push(Math.max(...cards.slice(i,i+columns).map(c=>c.h)));
    const offsets=[24];for(let col=1;col<columns;col++)offsets.push(offsets[col-1]+colW[col-1]+28);
    let y=12;cards.forEach((c,i)=>{if(i&&i%columns===0)y+=rows[Math.floor(i/columns)-1]+14;c.localX=offsets[i%columns];c.localY=y;});
    tray={key:'group:'+n.key,parent:n.key,group:true,cards,w:offsets.at(-1)+colW.at(-1)+12,h:24+rows.reduce((a,b)=>a+b,0)+14*(rows.length-1),columns};groups.push(tray);
   }
   for(const c of n.children)if(c.kind==='category'&&allCards.has(c.key))children.push(build(c));
  }
  if(!bands.has(n.depth))bands.set(n.depth,{depth:n.depth,categoryHeight:0,trayHeight:0});
  const band=bands.get(n.depth);band.categoryHeight=Math.max(band.categoryHeight,a.h);band.trayHeight=Math.max(band.trayHeight,tray?.h||0);
  const childrenWidth=children.reduce((sum,c)=>sum+c.w,0)+Math.max(0,children.length-1)*siblingGap;
  const w=Math.max(a.w,tray?.w||0,childrenWidth)+padding*2;
  return {node:n,card:a,tray,children,childrenWidth,w};
 }
 const roots=m.roots.filter(n=>allCards.has(n.key)).map(build),maxDepth=Math.max(-1,...bands.keys());let rankY=0;
 for(let d=0;d<=maxDepth;d++){
  const band=bands.get(d)||{depth:d,categoryHeight:0,trayHeight:0};band.y=rankY;band.trayY=rankY+band.categoryHeight+topGap;
  band.childBusY=band.trayY+band.trayHeight+bottomGap/2;bands.set(d,band);
  rankY=band.trayY+band.trayHeight+bottomGap;
 }
 function place(t,left){
  const {node:n,card:a,tray,children}=t,band=bands.get(n.depth),center=left+t.w/2,p={...a,x:center-a.w/2,y:band.y};positions.set(n.key,p);
  let bottom=p.y+p.h;
  if(tray){
   Object.assign(tray,{x:center-tray.w/2,y:band.trayY});bottom=Math.max(bottom,tray.y+tray.h);
   for(const c of tray.cards){const q={...c,x:tray.x+c.localX,y:tray.y+c.localY};positions.set(c.key,q);const rail=q.x-10,bus=tray.y-16;
    routes.push({parent:n.key,child:c.key,points:[[center,p.y+p.h],[center,bus],[rail,bus],[rail,q.y+q.h/2],[q.x,q.y+q.h/2]]});
   }
  }
  let childLeft=center-t.childrenWidth/2;
  for(const child of children){
   place(child,childLeft);const q=positions.get(child.node.key),corridor=left+padding/2,bus=band.childBusY;
   // Descend beside the parent's tray, then distribute below it to child ranks.
   const points=tray?[[center,p.y+p.h],[center,tray.y-16],[corridor,tray.y-16],[corridor,bus],[q.x+q.w/2,bus],[q.x+q.w/2,q.y]]:[[center,p.y+p.h],[center,bus],[q.x+q.w/2,bus],[q.x+q.w/2,q.y]];
   routes.push({parent:n.key,child:q.key,points});bottom=Math.max(bottom,subtrees.get(q.key).y+subtrees.get(q.key).h-padding);childLeft+=child.w+siblingGap;
  }
  subtrees.set(n.key,{key:n.key,parent:n.parent,depth:n.depth,x:left,y:p.y-padding,w:t.w,h:bottom-p.y+padding*2,children:children.map(c=>c.node.key)});
 }
 let left=0;for(const root of roots){place(root,left);left+=root.w+siblingGap;}
 const bounds=C.bounds(subtrees.values());
 // Keep exact rank values: normalize all geometry by the same translation.
 if(bounds){const dx=bounds.x,dy=bounds.y;for(const p of positions.values()){p.x-=dx;p.y-=dy;}for(const t of groups){t.x-=dx;t.y-=dy;}for(const b of subtrees.values()){b.x-=dx;b.y-=dy;}for(const b of bands.values()){b.y-=dy;b.trayY-=dy;b.childBusY-=dy;}for(const r of routes)r.points=r.points.map(([x,y])=>[x-dx,y-dy]);bounds.x=0;bounds.y=0;}
 return {positions,groups,routes,bounds,hidden,subtrees,bands,siblingGap,padding,durationMs:performance.now()-start,algorithm:'depth-banded-rectangular-contour-tidy@1',coordinateSystem:'local',selection:s};
}

function movement(before,after){const a=[];for(const [k,p]of before.positions){const q=after.positions.get(k);if(q)a.push({key:k,dx:q.x-p.x,dy:q.y-p.y,distance:Math.hypot(q.x-p.x,q.y-p.y)});}const distances=a.map(p=>p.distance).sort((a,b)=>a-b);return {existing:a.length,moved:a.filter(p=>p.distance>0).length,average:a.reduce((sum,p)=>sum+p.distance,0)/(a.length||1),median:distances[Math.floor(distances.length/2)]||0,max:distances.at(-1)||0,entities:a};}
const api={selection,layout,progress,ordered,fixture,inside,stats,title,movement,search};if(typeof module!=='undefined')module.exports=api;else g.AdaptiveCore=api;
})(globalThis);
