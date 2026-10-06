/* Read-only selections and derived local geometry. No Catalog or progress writes. */
(function(g){
'use strict';
const C=typeof module!=='undefined'?require('../global-pyramid/atlas.js'):g.GlobalAtlasCore;
const L=typeof module!=='undefined'?require('../global-pyramid/labels.js'):g.PyramidLabels;
const F=typeof module!=='undefined'?require('./vendor/d3-flextree-2.1.2.cjs'):g.d3;
function keyFor(m,id){return m.nodes.has('topic:'+id)?'topic:'+id:m.nodes.has('reference:'+id)?'reference:'+id:null;}
function search(m,q){const alias=/^(?:topic|reference|leaf):(\d+)$/.exec(q.trim());if(alias){const n=m.nodes.get(keyFor(m,Number(alias[1])));return n?[n]:[];}return C.search(m,q);}
function progress(m){return {learned:new Set(m.raw.progress.filter(r=>r.is_learned===true).map(r=>'topic:'+r.topic_id)),verified:new Set(m.raw.progress.filter(r=>r.is_verified===true).map(r=>'topic:'+r.topic_id))};}
function ordered(m){const out=[];function walk(n){if(n.kind!=='category')out.push(n.key);for(const c of n.children)walk(c);}m.roots.forEach(walk);return out;}
function fixture(m,name,step=0){
 const slots=ordered(m),groups=new Map();for(const k of slots){const p=m.nodes.get(k).parent;if(!groups.has(p))groups.set(p,[]);groups.get(p).push(k);}
 if(name==='growth-branch'){const group=[...groups.values()].find(a=>a.length>=12);return new Set(group.slice(0,[1,3,6,12][Math.min(3,step)]));}
 if(name==='growth-wide'){const a=[...groups.values()],list=[];for(let i=0;i<12;i++)for(const group of a.filter((_,j)=>j%Math.max(1,Math.floor(a.length/8))===0))if(group[i])list.push(group[i]);return new Set(list.slice(0,[4,8,16,32][Math.min(3,step)]));}
 return new Set(slots.slice(0,name==='load-300'?300:name==='load-1000'?1000:slots.length));
}
function selection(m,opts={}){
 const o={mode:'learned',id:8,stage:null,onlyLearned:false,branch:null,step:0,...opts},p=progress(m);let explicit=new Set(),unknown=false,reason='';
 const isFixture=o.mode.startsWith('fixture:');
 if(isFixture)explicit=fixture(m,o.mode.slice(8),o.step);
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
 function build(n){
  const a=allCards.get(n.key),children=[];
  if(!a.collapsed){
   const leaves=n.children.filter(c=>c.kind!=='category'&&s.visible.has(c.key)&&!hidden.has(c.key));
   if(leaves.length){
    const cards=leaves.map(c=>allCards.get(c.key)),columns=Math.min(3,Math.ceil(Math.sqrt(cards.length/2))),colW=Array.from({length:columns},(_,col)=>Math.max(...cards.filter((_,i)=>i%columns===col).map(c=>c.w))),rows=[];
    // Row heights belong only to this Topic group, never to a global depth.
    for(let i=0;i<cards.length;i+=columns)rows.push(Math.max(...cards.slice(i,i+columns).map(c=>c.h)));
    const offsets=[24];for(let col=1;col<columns;col++)offsets.push(offsets[col-1]+colW[col-1]+28);
    let y=12;cards.forEach((c,i)=>{if(i&&i%columns===0)y+=rows[Math.floor(i/columns)-1]+14;c.localX=offsets[i%columns];c.localY=y;});
    const tray={key:'group:'+n.key,parent:n.key,group:true,cards,w:offsets.at(-1)+colW.at(-1)+12,h:12+rows.reduce((a,b)=>a+b,0)+14*(rows.length-1)+12,columns};groups.push(tray);children.push(tray);
   }
   for(const c of n.children)if(c.kind==='category'&&s.visible.has(c.key)&&!hidden.has(c.key))children.push(build(c));
  }
  return {...a,children};
 }
 const roots=m.roots.filter(n=>s.visible.has(n.key)&&!hidden.has(n.key)).map(build);
 // Visible secondary-context branches use the same deterministic primary forest.
 const apex={key:'presentation:compact',w:220,h:64,children:roots};
 const engine=F.flextree({nodeSize:n=>[n.data.w,n.data.h+60],spacing:36}),tree=engine.hierarchy(apex);engine(tree);
 tree.eachBefore(t=>{
  const d=t.data,x=t.x-d.w/2,y=t.y;
  if(d.key===apex.key)return;
  if(d.group){
   Object.assign(d,{x,y});for(const c of d.cards){const p={...c,x:x+c.localX,y:y+c.localY};positions.set(c.key,p);
    const parent=positions.get(d.parent),bus=parent.y+parent.h+24,rail=p.x-10;
    routes.push({parent:d.parent,child:c.key,points:[[parent.x+parent.w/2,parent.y+parent.h],[parent.x+parent.w/2,bus],[rail,bus],[rail,p.y+p.h/2],[p.x,p.y+p.h/2]]});
   }
  }else positions.set(d.key,{...allCards.get(d.key),x,y});
 });
 for(const p of positions.values())if(p.kind==='category'&&p.parent&&positions.has(p.parent)){
  const a=positions.get(p.parent),bus=a.y+a.h+24;routes.push({parent:a.key,child:p.key,points:[[a.x+a.w/2,a.y+a.h],[a.x+a.w/2,bus],[p.x+p.w/2,bus],[p.x+p.w/2,p.y]]});
 }
 const bounds=C.bounds(positions.values());if(bounds){for(const p of positions.values()){p.x-=bounds.x;p.y-=bounds.y;}for(const t of groups){t.x-=bounds.x;t.y-=bounds.y;}for(const r of routes)r.points=r.points.map(([x,y])=>[x-bounds.x,y-bounds.y]);bounds.x=0;bounds.y=0;}
 return {positions,groups,routes,bounds,hidden,durationMs:performance.now()-start,algorithm:'d3-flextree@2.1.2',coordinateSystem:'local',selection:s};
}
function movement(before,after){const a=[];for(const [k,p]of before.positions){const q=after.positions.get(k);if(q)a.push({key:k,dx:q.x-p.x,dy:q.y-p.y,distance:Math.hypot(q.x-p.x,q.y-p.y)});}const distances=a.map(p=>p.distance).sort((a,b)=>a-b);return {existing:a.length,moved:a.filter(p=>p.distance>0).length,median:distances[Math.floor(distances.length/2)]||0,max:distances.at(-1)||0,entities:a};}
const api={selection,layout,progress,ordered,fixture,inside,stats,title,movement,search};if(typeof module!=='undefined')module.exports=api;else g.AdaptiveCore=api;
})(globalThis);
