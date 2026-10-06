/* Prototype only: immutable accepted geometry + additive placement search. */
(function(g){
'use strict';
const clone=v=>JSON.parse(JSON.stringify(v));
const TOKENS=Object.freeze({cardGap:16,trayGap:20,siblingGap:64,stem:28,childStem:30,diversityCell:128,
  beam:64,maxSlots:512,maxBusSlots:24,maxConnector:5200,maxDrift:2400,
  maxWidthGrowth:.75,maxAreaGrowth:1.5,maxIsolation:1600,searchSteps:12});
// Comparison-only policy; legacy scenarios keep their original search and cost.
const COMPARISON=Object.freeze({beam:192,minimumStem:12,growthProbes:[128,256,384],
 weights:Object.freeze({parentDistance:1,maxBus:1,drift:1,whitespace:.25,growth:.25})});
const stable=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(stable).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+stable(v[k])).join(',')+'}';
const round=x=>Math.round(x*1e6)/1e6;
const rect=n=>({key:n.key,x:n.x-n.width/2,y:n.y,w:n.width,h:n.height,kind:'card'});
const trayRect=t=>({key:'tray:'+t.parent,x:t.x,y:t.y,w:t.width,h:t.height,kind:'tray'});
const overlap=(a,b,gap=0)=>a.x<b.x+b.w+gap&&a.x+a.w+gap>b.x&&a.y<b.y+b.h+gap&&a.y+a.h+gap>b.y;
function hitsCard(s,r){const [a,b]=s.points;
 return a.x===b.x?a.x>r.x&&a.x<r.x+r.w&&Math.max(a.y,b.y)>r.y&&Math.min(a.y,b.y)<r.y+r.h:
 a.y>r.y&&a.y<r.y+r.h&&Math.max(a.x,b.x)>r.x&&Math.min(a.x,b.x)<r.x+r.w;
}
function intersects(a,b){
 const [p,q]=a.points,[u,v]=b.points,av=p.x===q.x,bv=u.x===v.x;
 if(av===bv){if(av?p.x!==u.x:p.y!==u.y)return false;return Math.max(Math.min(av?p.y:p.x,av?q.y:q.x),Math.min(bv?u.y:u.x,bv?v.y:v.x))<=Math.min(Math.max(av?p.y:p.x,av?q.y:q.x),Math.max(bv?u.y:u.x,bv?v.y:v.x));}
 const vertical=av?a:b,horizontal=av?b:a,[va,vb]=vertical.points,[ha,hb]=horizontal.points;
 return va.x>=Math.min(ha.x,hb.x)&&va.x<=Math.max(ha.x,hb.x)&&ha.y>=Math.min(va.y,vb.y)&&ha.y<=Math.max(va.y,vb.y);
}
function crossing(a,b){return a.parent!==b.parent&&intersects(a,b);}
function segment(parent,children,a,b,depth){return{parent,children:[...children],depth,points:[a,b],d:`M${a.x},${a.y}L${b.x},${b.y}`};}
function length(s){const [a,b]=s.points;return Math.abs(a.x-b.x)+Math.abs(a.y-b.y);}
function subtractShared(s,existing){
 const [a,b]=s.points,vertical=a.x===b.x,fixed=vertical?a.x:a.y,axis=vertical?'y':'x';
 let ranges=[[Math.min(a[axis],b[axis]),Math.max(a[axis],b[axis])]];
 for(const e of existing){const [p,q]=e.points;
  if(e.parent!==s.parent||(p.x===q.x)!==vertical||(vertical?p.x:p.y)!==fixed)continue;
  const lo=Math.min(p[axis],q[axis]),hi=Math.max(p[axis],q[axis]);
  ranges=ranges.flatMap(([l,h])=>hi<=l||lo>=h?[[l,h]]:[[l,Math.max(l,lo)],[Math.min(h,hi),h]].filter(([x,y])=>x<y));
 }
 return ranges.map(([lo,hi])=>segment(s.parent,s.children,vertical?{x:fixed,y:lo}:{x:lo,y:fixed},vertical?{x:fixed,y:hi}:{x:hi,y:fixed},s.depth));
}
function bounds(geometry){
 const rs=[...geometry.nodes.map(rect),...geometry.trays.map(trayRect)];
 const points=geometry.connectorSegments.flatMap(s=>s.points);
 return {x0:Math.min(...rs.map(r=>r.x),...points.map(p=>p.x))-8,x1:Math.max(...rs.map(r=>r.x+r.w),...points.map(p=>p.x))+8,
 y0:Math.min(...rs.map(r=>r.y),...points.map(p=>p.y))-8,y1:Math.max(...rs.map(r=>r.y+r.h),...points.map(p=>p.y))+8};
}
function ledger(geometry){return [...geometry.nodes.filter(n=>!n.parent).map(rect),...geometry.trays.map(trayRect)];}
function geometryHashInput(geometry){return stable(geometry.nodes.map(n=>({key:n.key,x:n.x,y:n.y,width:n.width,height:n.height})).sort((a,b)=>a.key.localeCompare(b.key)));}
function card(title,depth,measure,height){
 const font=depth===0?28:depth===1?21:17,line=font*1.18,min=depth===0?320:depth===1?300:190,max=depth===0?360:depth===1?340:240;
 const text=t=>measure(t,font,depth===0?650:600),meta=measure('89 / 89 learned',10,400),options=[];
 for(let limit=min;limit<=max;limit+=8){const lines=AtlasLayout.wrap(title,text,limit-44);if(lines.length>3)continue;
  const width=Math.max(min,Math.ceil(Math.max(meta,...lines.map(text))+44)),h=lines.length*line+(depth>=2?25:30);
  options.push({width,height:Math.max(h,height||0),font,line,lines,score:width*h+width*20+lines.length*100});}
 if(!options.length)throw Error('Category exceeds measured display contract');
 const chosen=options.sort((a,b)=>a.score-b.score||a.width-b.width)[0];delete chosen.score;return chosen;
}
function issueValidation(frozen,geometry){
 const old=new Map(frozen.nodes.map(n=>[n.key,n])),rs=ledger(geometry),newKeys=new Set(geometry.nodes.filter(n=>!old.has(n.key)).map(n=>n.key));
 const additions=geometry.connectorSegments.slice(frozen.connectorSegments.length);
 let overlaps=0,crossings=0,throughCards=0,moved=0,invalidPorts=0;
 for(const n of frozen.nodes){const after=geometry.nodes.find(a=>a.key===n.key);if(!after||['x','y','width','height'].some(f=>n[f]!==after[f]))moved++;}
 for(let i=0;i<rs.length;i++)for(let j=i+1;j<rs.length;j++)if((newKeys.has(rs[i].key)||newKeys.has(rs[j].key)||rs[i].key.startsWith('tray:')&&newKeys.has(rs[i].key.slice(5))||rs[j].key.startsWith('tray:')&&newKeys.has(rs[j].key.slice(5)))&&overlap(rs[i],rs[j]))overlaps++;
 for(let i=0;i<geometry.connectorSegments.length;i++)for(let j=i+1;j<geometry.connectorSegments.length;j++)if((i>=frozen.connectorSegments.length||j>=frozen.connectorSegments.length)&&crossing(geometry.connectorSegments[i],geometry.connectorSegments[j]))crossings++;
 for(const s of geometry.connectorSegments)for(const r of rs)if((additions.includes(s)||newKeys.has(r.key)||r.key.startsWith('tray:')&&newKeys.has(r.key.slice(5)))&&hitsCard(s,r))throughCards++;
 for(const route of geometry.activationRoutes||[]){const parent=geometry.nodes.find(n=>n.key===route.parent),child=geometry.nodes.find(n=>n.key===route.child),tray=geometry.trays.find(t=>route.child==='tray:'+t.parent);
  const a=route.points[0],b=route.points.at(-1),target=tray?{x:tray.x+tray.width/2,y:tray.y}:child;
  // Floating point arithmetic guard applies only to ports, never frozen bounds.
  if(!parent||!target||a.x!==parent.x||Math.abs(a.y-(parent.y+parent.height))>1e-9||b.x!==target.x||b.y!==target.y)invalidPorts++;
 }
 return {existing_nodes_moved:moved,overlaps,hierarchy_crossings:crossings,connector_through_cards:throughCards,invalid_ports:invalidPorts};
}
function planGeometry(frozen,fixture,measure,options={}){
 const plan=fixture.plan,rows=new Map(plan.entities.map(r=>[r.id,r])),display=new Map(fixture.display.map(r=>[r.key,r]));
 const oldKeys=new Set(frozen.nodes.map(n=>n.key)),before=clone(frozen),initialBounds=clone(frozen.bounds),frozenRects=ledger(frozen);
 const initial={nodes:[],trays:[],segments:[],routes:[],cost:[],drift:0};
 const blocked=plan.blocked_references.map(r=>clone(typeof r==='string'?rows.get(r):r)).sort((a,b)=>a.id.localeCompare(b.id));
 const allowed=new Set([...plan.new_categories,...plan.new_topics]);
 for(const key of allowed){const r=rows.get(key),d=display.get(key);if(!r||r.renderability!=='RENDERABLE'||r.presentation_activation!=='ACTIVATION_CANDIDATE'||!d||!d.title||d.title!==r.title||d.type!==r.entity_type||d.parent!==r.canonical_parent||!r.activation_reasons.length)throw Error('Geometry requires an explained renderable ActivationPlan candidate: '+key);}
 const depths=new Map(),tops=new Map(),heights=new Map();
 for(const n of frozen.nodes)if(!n.parent){depths.set(n.key,n.depth);tops.set(n.depth,n.y);heights.set(n.depth,Math.max(heights.get(n.depth)||0,n.height));}
 function depth(key,seen=new Set()){
  if(depths.has(key))return depths.get(key);if(seen.has(key))throw Error('Fixture cycle');
  const p=display.get(key)?.parent;if(!p){if(plan.new_roots.includes(key)){depths.set(key,0);return 0;}throw Error('Unplaced candidate');}
  const d=depth(p,new Set([...seen,key]))+1;depths.set(key,d);return d;
 }
 const categories=[...plan.new_categories].sort((a,b)=>depth(a)-depth(b)||a.localeCompare(b));
 const allTopics=[...plan.new_topics].sort();
 const packs=new Map();
 for(const key of categories){const ts=allTopics.filter(t=>display.get(t)?.parent===key).map(t=>display.get(t));packs.set(key,AtlasLayout.pack(ts,measure,Infinity,1));}
 // Existing parent tray growth is deliberately deferred: never mutate its box.
 const unsupported=allTopics.filter(t=>!categories.includes(display.get(t).parent));
 const measured=new Map();
 for(const key of categories){const d=depth(key),c=card(display.get(key).title,d,measure,heights.get(d));measured.set(key,c);heights.set(d,Math.max(heights.get(d)||0,c.height));}
 for(const d of [...new Set(categories.map(depth))].sort((a,b)=>a-b))if(!tops.has(d)){
  const prior=d-1,packHeight=Math.max(0,...categories.filter(k=>depth(k)===prior).map(k=>packs.get(k).height));
  tops.set(d,tops.get(prior)+heights.get(prior)+(packHeight?68+packHeight+72:76));
 }
 let refusal=null,searchEvaluations=0;const search=[];
 if(plan.new_roots.length)refusal='A first global root needs an explicit multi-root design';
 else if(unsupported.length)refusal='Appending Topics to an accepted tray needs a separate additive tray design';
 let frontier=[initial];
 const beam=options.comparison?COMPARISON.beam:TOKENS.beam;
 function scene(s){return {...before,nodes:[...before.nodes,...s.nodes],trays:[...before.trays,...s.trays],connectorSegments:[...before.connectorSegments,...s.segments],activationRoutes:s.routes};}
 function cost(s){const b=bounds(scene(s)),area=(b.x1-b.x0)*(b.y1-b.y0),area0=(initialBounds.x1-initialBounds.x0)*(initialBounds.y1-initialBounds.y0),len=s.segments.reduce((n,e)=>n+length(e),0);
  const legacy=[round(Math.max(0,area-area0)),round(len),round(s.routes.reduce((n,r)=>n+Math.abs(r.points[0].x-r.points.at(-1).x),0)),round(s.drift),...s.nodes.filter(n=>!n.parent).flatMap(n=>[n.x<0?1:0,Math.abs(n.x),n.x])];
  if(!options.comparison)return legacy;
  const root=s.nodes.find(n=>!n.parent&&oldKeys.has(display.get(n.key)?.parent)),parent=root&&frozen.nodes.find(n=>n.key===display.get(root.key).parent),distance=root?Math.abs(root.x-parent.x):0;
  const horizontal=s.routes.map(r=>Math.abs(r.points[0].x-r.points.at(-1).x)),maxBus=Math.max(0,...horizontal),total=s.routes.reduce((n,r)=>n+r.length,0);
  const tie=legacy.slice(4),growth=Math.max(0,b.x1-b.x0-(initialBounds.x1-initialBounds.x0));
  if(options.objective==='parent-distance')return [distance,s.drift,maxBus,total,growth,...tie];
  if(options.objective==='centering')return [s.drift,maxBus,distance,total,growth,...tie];
  if(options.objective==='connector')return [total,maxBus,s.drift,distance,growth,...tie];
  const w=COMPARISON.weights,scale=parent?.width||300;
  const whitespace=s.routes.reduce((n,r)=>n+Math.abs((r.points[1].y-r.points[0].y)-TOKENS.stem),0);
  const score=(w.parentDistance*distance+w.maxBus*maxBus+w.drift*s.drift+w.whitespace*whitespace+w.growth*growth)/scale;
  return [round(score),distance,maxBus,s.drift,total,growth,...tie];}
 function compare(a,b){for(let i=0;i<Math.max(a.cost.length,b.cost.length);i++){const delta=(a.cost[i]||0)-(b.cost[i]||0);if(delta)return delta;}return stable(a.nodes).localeCompare(stable(b.nodes));}
 function attach(s,parent,child,targetKey,targetX,targetY){
  const current=scene(s),rectangles=ledger(current),segments=current.connectorSegments,bottom=round(parent.y+parent.height);
  if(targetY<=bottom)return null;
  const minimumStem=options.comparison?COMPARISON.minimumStem:TOKENS.stem;
  const busValues=[bottom+TOKENS.stem,bottom+minimumStem,targetY-TOKENS.childStem,...segments.filter(e=>e.parent===parent.key&&e.points[0].y===e.points[1].y).map(e=>e.points[0].y),
   ...rectangles.flatMap(r=>[r.y-TOKENS.cardGap,r.y+r.h+TOKENS.cardGap]),...segments.filter(e=>e.points[0].y===e.points[1].y).flatMap(e=>[e.points[0].y-TOKENS.cardGap,e.points[0].y+TOKENS.cardGap])];
  const ys=[...new Set(busValues.map(round))].filter(y=>y>=bottom+minimumStem-1e-9&&y<=targetY-TOKENS.childStem+1e-9).sort((a,b)=>a-b).slice(0,TOKENS.maxBusSlots);
  let best=null;
  for(const y of ys){const points=[{x:parent.x,y:bottom},{x:parent.x,y},{x:targetX,y},{x:targetX,y:targetY}],raw=points.slice(1).map((b,i)=>segment(parent.key,[targetKey],points[i],b,parent.depth)).filter(e=>length(e)>0);
   if(raw.some(e=>rectangles.some(r=>hitsCard(e,r))||segments.some(other=>crossing(e,other))))continue;
   const added=raw.flatMap(e=>subtractShared(e,segments)),full=raw.reduce((n,e)=>n+length(e),0);
   if(full>TOKENS.maxConnector)continue;
   const score=[added.reduce((n,e)=>n+length(e),0),Math.abs(y-(bottom+TOKENS.stem)),y];
   if(!best||score.some((x,i)=>x<best.score[i]&&score.slice(0,i).every((v,j)=>v===best.score[j])))best={added,score,route:{parent:parent.key,child:targetKey,points,length:full,shared_frozen_segments:segments.map((e,i)=>e.parent===parent.key&&raw.some(r=>intersects(r,e))?i:null).filter(i=>i!==null&&i<frozen.connectorSegments.length)}};
  }return best;
 }
 for(const key of refusal?[]:categories){
  const next=[],rejected={collision:0,attachment:0,tray_attachment:0,drift:0},meta=display.get(key),c=measured.get(key),d=depth(key),y=tops.get(d),pack=packs.get(key);
  for(const s of frontier){
   const current=scene(s),parent=current.nodes.find(n=>n.key===meta.parent),rectangles=ledger(current);
   if(!parent)throw Error('Candidate parent absent');
   const siblings=current.nodes.filter(n=>!n.parent&&n.key!==key&&(oldKeys.has(n.key)?frozen.branches.some(b=>b.child===n.key&&b.parent===parent.key):display.get(n.key)?.parent===parent.key));
   const slotValues=[parent.x,...rectangles.flatMap(r=>[r.x-c.width/2-TOKENS.cardGap,r.x+r.w+c.width/2+TOKENS.cardGap]),...rectangles.flatMap(r=>[r.x-pack.width/2-TOKENS.trayGap,r.x+r.w+pack.width/2+TOKENS.trayGap])];
   for(let i=1;i<=TOKENS.searchSteps;i++)slotValues.push(initialBounds.x1+c.width/2+i*TOKENS.siblingGap,initialBounds.x0-c.width/2-i*TOKENS.siblingGap);
   if(options.comparison)for(const growth of COMPARISON.growthProbes){const half=Math.max(c.width,pack.width)/2;slotValues.push(initialBounds.x1+growth-half-8,initialBounds.x0-growth+half+8);}
   const xs=[...new Set(slotValues.map(round))].filter(x=>!siblings.length||x<Math.min(...siblings.map(n=>n.x))||x>Math.max(...siblings.map(n=>n.x))).sort((a,b)=>Math.abs(a-parent.x)-Math.abs(b-parent.x)||b-a).slice(0,TOKENS.maxSlots);
   for(const x of xs){searchEvaluations++;
    const node={key,x,y,depth:d,...c},newRect=rect(node);
    const tray=pack.items.length?{parent:key,x:round(x-pack.width/2),y:round(y+c.height+68),width:pack.width,height:pack.height,topics:pack.items.map(i=>i.key)}:null;
    const ownRects=[newRect,...tray?[trayRect(tray)]:[]];
    if(ownRects.some(r=>rectangles.some(o=>overlap(r,o,r.kind==='tray'?TOKENS.trayGap:TOKENS.cardGap))||current.connectorSegments.some(e=>hitsCard(e,r)))){
     rejected.collision++;continue;
    }
    const t={...s,nodes:[...s.nodes,node],trays:[...s.trays,...tray?[tray]:[]],segments:[...s.segments],routes:[...s.routes]};
    const edge=attach(t,parent,node,key,x,y);if(!edge){rejected.attachment++;continue;}
    t.segments.push(...edge.added);t.routes.push(edge.route);
    if(tray){
     for(const item of pack.items)t.nodes.push({key:item.key,x:round(tray.x+item.x+item.width/2),y:round(tray.y+item.y),depth:d+1,lines:item.lines,font:14,line:17,width:item.width,height:item.height,parent:key});
     const te=attach(t,node,null,'tray:'+key,round(tray.x+tray.width/2),tray.y);if(!te){rejected.tray_attachment++;continue;}
     // The accepted grammar maps each tray stem to all its Topic endpoints.
     te.added.forEach(e=>e.children=[...tray.topics]);t.segments.push(...te.added);t.routes.push(te.route);
    }
    const family=[...siblings,node],drift=Math.abs((Math.min(...family.map(n=>n.x))+Math.max(...family.map(n=>n.x)))/2-parent.x);
    t.drift=Math.max(s.drift,drift);if(t.drift>TOKENS.maxDrift){rejected.drift++;continue;}
    t.cost=cost(t);next.push(t);
   }
  }
  const ranked=next.sort(compare),cells=new Set(),diverse=[];
  for(const s of ranked){const n=s.nodes.find(n=>n.key===key),cell=Math.floor(n.x/TOKENS.diversityCell);if(!cells.has(cell)){cells.add(cell);diverse.push(s);}}
  frontier=[...diverse,...ranked.filter(s=>!diverse.includes(s))].slice(0,beam);
  search.push({category:key,feasible_candidates:next.length,retained:frontier.length,rejected,x_positions:frontier.map(s=>s.nodes.find(n=>n.key===key).x)});
  if(!frontier.length){refusal='No collision-free, crossing-free append slot within prototype thresholds';break;}
 }
 function finalize(state,why=null){
 let chosen=state,localRefusal=why,geometry=scene(chosen),after=bounds(geometry);
 const width0=initialBounds.x1-initialBounds.x0,height0=initialBounds.y1-initialBounds.y0,width=after.x1-after.x0,height=after.y1-after.y0;
 const isolation=Math.max(0,...chosen.nodes.filter(n=>!n.parent).map(n=>{const r=rect(n);return Math.min(...frozenRects.map(o=>Math.hypot(Math.max(0,r.x-o.x-o.w,o.x-r.x-r.w),Math.max(0,r.y-o.y-o.h,o.y-r.y-r.h))));}));
 if(!localRefusal&&((width-width0)/width0>TOKENS.maxWidthGrowth||(width*height-width0*height0)/(width0*height0)>TOKENS.maxAreaGrowth||isolation>TOKENS.maxIsolation)){
  localRefusal='Append-only canvas growth exceeds prototype visual thresholds';chosen=initial;geometry=scene(chosen);after=clone(initialBounds);
 }
 geometry.bounds=after;
 const checks=issueValidation(frozen,geometry),sceneRects=ledger(geometry);
 const gap=(r,o)=>Math.hypot(Math.max(0,r.x-o.x-o.w,o.x-r.x-r.w),Math.max(0,r.y-o.y-o.h,o.y-r.y-r.h));
 function clearance(kind){const candidates=sceneRects.filter(r=>r.kind===kind&&(chosen.nodes.some(n=>n.key===r.key)||r.kind==='tray'&&chosen.trays.some(t=>'tray:'+t.parent===r.key)));
  return candidates.length?round(Math.min(...candidates.flatMap(r=>sceneRects.filter(o=>o.key!==r.key).map(o=>gap(r,o))))):null;}
 if(Object.values(checks).some(Boolean))throw Error('Append-only invariant failed: '+stable(checks));
 const outcome=blocked.length?'METADATA_REQUIRED':localRefusal?'ACTIVATION_REBALANCE_REQUIRED':chosen.nodes.length?'ACTIVATION_REVIEW_REQUIRED':'NO_CHANGE';
 const lengths=chosen.routes.map(r=>r.length);
 const report={schema_version:1,fixture_only:true,existing_nodes:frozen.nodes.length,...checks,
  existing_connectors_preserved:stable(geometry.connectorSegments.slice(0,frozen.connectorSegments.length))===stable(frozen.connectorSegments),
  existing_trays_preserved:stable(geometry.trays.slice(0,frozen.trays.length))===stable(frozen.trays),
  new_categories:chosen.nodes.filter(n=>!n.parent).length,new_topics:chosen.nodes.filter(n=>n.parent).length,new_connectors:chosen.segments.length,
  canvas_before:initialBounds,canvas_after:after,width_growth:round((after.x1-after.x0)-width0),height_growth:round((after.y1-after.y0)-height0),
  average_new_connector_length:round(lengths.length?lengths.reduce((a,b)=>a+b,0)/lengths.length:0),max_new_connector_length:round(Math.max(0,...lengths)),
  parent_centering_drift:round(chosen.drift),max_branch_isolation:round(isolation),new_card_min_clearance:clearance('card'),new_tray_min_clearance:clearance('tray'),blocked_references:blocked,drawn_candidates:chosen.nodes.map(n=>n.key).sort(),
  requested_categories:categories.length,requested_topics:allTopics.length,max_requested_tray_height:Math.max(0,...[...packs.values()].map(p=>p.height)),
  outcome,geometry_outcome:localRefusal?'ACTIVATION_REBALANCE_REQUIRED':chosen.nodes.length?'ACTIVATION_REVIEW_REQUIRED':'NO_CHANGE',refusal:localRefusal,
  geometry_persisted:false,generation:0,search_evaluations:searchEvaluations,search,thresholds:TOKENS,
  activation_reasons:Object.fromEntries(chosen.nodes.map(n=>[n.key,rows.get(n.key).activation_reasons]).sort((a,b)=>a[0].localeCompare(b[0])))};
 return {geometry,report};
 }
 const result=finalize(refusal?initial:frontier.sort(compare)[0]||initial,refusal);
 if(options.retainCandidates&&!refusal)result.candidates=frontier.sort(compare).map(s=>finalize(s)).filter(r=>r.report.outcome==='ACTIVATION_REVIEW_REQUIRED');
 return result;
}
g.ActivationGeometry={plan:planGeometry,validate:issueValidation,stable,geometryHashInput,rect,ledger,overlap,crossing,subtractShared,TOKENS,COMPARISON};
if(typeof module!=='undefined')module.exports=g.ActivationGeometry;
})(globalThis);
