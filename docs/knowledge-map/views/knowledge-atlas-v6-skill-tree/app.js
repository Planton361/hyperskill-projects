/* Derived directly from V6.6 app.js. See BASELINE.md. */
(function(g){
'use strict';
const $=s=>document.querySelector(s),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const CARD={RADIUS:5,TOPIC_RADIUS:3,HEADER_MAIN:8,HEADER_CATEGORY:5,LABEL_X:34,DISCLOSURE_X:15,META_BOTTOM:7,STATUS_X:12,TOPIC_LABEL_X:24,EVIDENCE_RIGHT:10};
let m,L,selected=null,mode='personal',collapsed=new Set(),transform=d3.zoomIdentity,visible=[],fitIntent=null,viewState='overview',transitioning=false,miniBounds=null,navigationId=0;const metrics={},samples={};
const svg=d3.select('#graph'),scene=svg.append('g'),traySurfaces=scene.append('g').attr('aria-hidden','true'),taxonomy=scene.append('g'),nodes=scene.append('g');
const zoom=d3.zoom().scaleExtent([.0001,4]).on('zoom',e=>{transform=e.transform;if(e.sourceEvent){fitIntent=null;viewState=AtlasModel.isLeaf(m?.nodes.get(selected))?'topic':'subtree';}scene.attr('transform',transform);$('#zoom-value').textContent=(transform.k*100).toFixed(transform.k<.1?1:0)+'%';updateOptics();});svg.call(zoom).on('dblclick.zoom',null);
function timed(name,fn){const t=performance.now(),v=fn();metrics[name]=performance.now()-t;(samples[name]??=[]).push(metrics[name]);return v;}
const VIEW={duration:220,topicFont:16,subtreeFont:13,minReadingFont:10,pad:24,maxScale:1.3};
function updateOptics(){
 if(!L)return;
 $('#canvas').dataset.view=viewState;$('#overview-guide').hidden=true;
 $('#view-status').textContent=viewState==='overview'?(transform.k*14>=10?'My Skill Tree · learned and next':'My Skill Tree · focus a branch to read'):viewState==='topic'?(m.nodes.get(selected)?.type==='reference'?'Reference focus':'Topic focus'):transform.k*14<10?'Subtree overview · choose a child to read':'Subtree reading';
 nodes.selectAll('.core').attr('r',Math.min(7,Math.max(4,1.2/transform.k))).style('stroke-width',Math.min(.65,Math.max(.45,transform.k*6)));nodes.selectAll('.ring').attr('r',Math.min(9,Math.max(7,1.8/transform.k))).style('stroke-width',Math.min(.65,transform.k*6));
 updateMinimap();
}
function viewportArea(){
 const r=$('#graph').getBoundingClientRect(),control=$('.map-controls').getBoundingClientRect(),status=$('#view-status').getBoundingClientRect();
 const guide=$('#overview-guide').hidden?status:$('#overview-guide').getBoundingClientRect(),footer=$('.map-footer').getBoundingClientRect();
 return{x:VIEW.pad,y:Math.max(control.bottom,status.bottom,guide.bottom)-r.top+16,width:r.width-2*VIEW.pad,height:r.height-(Math.max(control.bottom,status.bottom,guide.bottom)-r.top+16)-(r.bottom-footer.top+16)};
}
function navigateCamera(next,intent,animate=true){
 const id=++navigationId;svg.interrupt();fitIntent=intent;transitioning=false;
 if(animate&&!matchMedia('(prefers-reduced-motion: reduce)').matches){transitioning=true;svg.transition().duration(VIEW.duration).call(zoom.transform,next).end().catch(()=>{}).finally(()=>{if(id===navigationId)transitioning=false;});}
 else svg.call(zoom.transform,next);
}
function centerBounds(b,k,area){return d3.zoomIdentity.translate(area.x+area.width/2-(b.x0+b.x1)/2*k,area.y+area.height/2-(b.y0+b.y1)/2*k).scale(k);}
function buildOverviewGuide(){
 const majors=m.root.children.filter(n=>n.type==='category');$('#overview-guide').innerHTML=`<span>${esc(m.root.title)}</span><div>${majors.map(n=>`<button data-region="${esc(n.key)}">${esc(n.title)}</button>`).join('')}</div><p>Complete global taxonomy · all leaf slots remain rendered · select a branch to explore</p>`;
 $('#overview-guide').querySelectorAll('[data-region]').forEach(b=>b.onclick=()=>select(b.dataset.region,true));
}
function buildMinimap(){
 miniBounds=AtlasLayout.contentBounds(L,L.nodes);const b=miniBounds,mini=d3.select('#minimap').attr('viewBox',`${b.x0} ${b.y0} ${b.x1-b.x0} ${b.y1-b.y0}`);
 mini.selectAll('*').remove();mini.append('rect').attr('class','mini-background').attr('x',b.x0).attr('y',b.y0).attr('width',b.x1-b.x0).attr('height',b.y1-b.y0);
 mini.selectAll('.mini-path').data(L.connectorSegments).join('path').attr('class','mini-path').attr('d',e=>e.d);
 mini.selectAll('.mini-tray').data(L.trays).join('rect').attr('class','mini-tray').attr('x',t=>t.x).attr('y',t=>t.y).attr('width',t=>t.width).attr('height',t=>t.height);
 mini.selectAll('.mini-card').data(L.nodes.filter(n=>n.data.type==='category')).join('rect').attr('class','mini-card').attr('x',n=>n.x-n.width/2).attr('y',n=>n.y).attr('width',n=>n.width).attr('height',n=>n.height);
 mini.append('rect').attr('class','mini-selection');mini.append('rect').attr('class','mini-viewport');updateMinimap();
}
function updateMinimap(){
 if(!miniBounds)return;const r=$('#graph').getBoundingClientRect(),mini=d3.select('#minimap'),b=miniBounds;
 const x0=Math.max(b.x0,-transform.x/transform.k),y0=Math.max(b.y0,-transform.y/transform.k),x1=Math.min(b.x1,(r.width-transform.x)/transform.k),y1=Math.min(b.y1,(r.height-transform.y)/transform.k);
 mini.select('.mini-viewport').attr('x',x0).attr('y',y0).attr('width',Math.max(0,x1-x0)).attr('height',Math.max(0,y1-y0));
 const node=m.nodes.get(selected),keys=node?new Set(subtreeNodes(node).map(n=>n.key)):new Set(),ns=visible.filter(n=>keys.has(n.key));
 const sb=ns.length?AtlasLayout.contentBounds(L,ns):null;mini.select('.mini-selection').attr('width',sb?sb.x1-sb.x0:0).attr('height',sb?sb.y1-sb.y0:0).attr('x',sb?.x0||0).attr('y',sb?.y0||0);
}
function descendants(n){return[n,...n.children.flatMap(descendants)];}
function subtreeNodes(n){const ns=descendants(n),keys=new Set(ns.map(v=>v.key));for(const key of m.membershipLeaves.get(n.key)||[])if(!keys.has(key))ns.push(m.nodes.get(key));return ns;}
function path(n){const out=[];while(n){out.unshift(n.displayTitle||n.title);n=m.parent(n);}return out;}
function listButton(key,title){return `<button data-select="${esc(key)}">${esc(title)}</button>`;}
function list(title,items,open=true){return `<details ${open?'open':''}><summary>${esc(title)} (${items.length})</summary><div class="inspector-list">${items.join('')||'<p>None recorded.</p>'}</div></details>`;}
function acceptedProvenance(ids){return list('Advanced / Evidence',[...new Set(ids||[])].map(id=>{const e=m.raw.evidence.find(e=>e.id===id);return e?`<p>${esc(id)}<br>${esc(e.method)} · ${esc(e.observed_on)}<br>${esc(e.note)}${e.url?`<br><a href="${esc(e.url)}" target="_blank" rel="noopener">Source</a>`:''}</p>`:'';}),false);}
function draw(){
 visible=AtlasLayout.visible(L,m,collapsed);const keys=new Set(visible.map(n=>n.key)),neighbors=new Set([]);taxonomy.selectAll('*').remove();
 const context=new Set();let chosen=m.nodes.get(selected);if(chosen?.type==='category')while(chosen){context.add(chosen.key);chosen=m.parent(chosen);}
 for(const e of L.connectorSegments.filter(e=>keys.has(e.parent)&&e.children.some(key=>keys.has(key))))taxonomy.append('path').datum(e).attr('class','taxonomy depth-'+e.depth+(e.children.some(key=>context.has(key))?' context':'' )).attr('data-segment',L.connectorSegments.indexOf(e)).attr('data-children',e.children.join(' ')).attr('d',e.d);
 for(const e of L.buses.filter(e=>keys.has(e.parent)&&!collapsed.has(e.parent)&&(!e.topic||keys.has(e.topic))))taxonomy.append('path').attr('class','membership').attr('data-parent',e.parent).datum(e).attr('d',e.d);
 nodes.selectAll('*').remove();traySurfaces.selectAll('*').remove();const trayGroups=new Map();for(const t of L.trays.filter(t=>keys.has(t.parent)&&t.topics.some(k=>keys.has(k)))){traySurfaces.append('rect').datum(t).attr('class','tray-surface').attr('data-parent',t.parent).attr('x',t.x).attr('y',t.y).attr('width',t.width).attr('height',t.height).attr('rx',4);trayGroups.set(t.parent,nodes.append('g').attr('class','topic-tray').attr('data-parent',t.parent).attr('role','presentation'));}for(const n of visible){const d=n.data,isTopic=AtlasModel.isLeaf(d),baseName=(d.displayTitle||d.title)+'; '+d.type+'; '+path(d).join(' > ')+(isTopic?'; '+(d.is_learned?'learned':d.is_next?'next':'unknown')+(d.is_verified?'; verified':''):''),group=(isTopic?trayGroups.get(n.parent):nodes).append('g').datum(n).attr('class',`node ${d.type} depth-${n.depth} ${d.is_learned?'learned':d.is_next?'next':d.is_learned==null?'unknown':''} ${selected===d.key?'selected':''} ${neighbors.has(d.key)?'neighbor':''}`).attr('data-key',d.key).attr('data-x',n.x).attr('data-y',n.y).attr('data-base-name',baseName).attr('transform',`translate(${n.x},${n.y})`).attr('tabindex',0).attr('role','button').attr('aria-pressed',selected===d.key).attr('aria-label',baseName);
 group.on('click',e=>{e.stopPropagation();select(d.key,isTopic);}).on('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(d.key,isTopic);}});
 group.append('rect').attr('class','card').attr('x',-n.width/2).attr('y',0).attr('width',n.width).attr('height',n.height).attr('rx',isTopic?CARD.TOPIC_RADIUS:CARD.RADIUS*(n.cardScale||1));if(isTopic)group.append('title').text((d.displayTitle||d.title));
 if(isTopic){group.append('circle').attr('class','core slot-cue').attr('cx',-n.width/2+CARD.STATUS_X).attr('cy',n.height/2).attr('r',4);if(d.is_verified)group.append('circle').attr('class','ring').attr('cx',-n.width/2+CARD.STATUS_X).attr('cy',n.height/2).attr('r',7);}
 const tx=-n.width/2+(isTopic?CARD.TOPIC_LABEL_X:CARD.LABEL_X*(n.cardScale||1)),ty=isTopic?n.height/2-(n.lines.length-1)*n.line/2+n.font*.35:(n.depth>=2?CARD.HEADER_CATEGORY:CARD.HEADER_MAIN)*(n.cardScale||1)+n.font,label=group.append('text').attr('class','label').attr('x',tx).attr('y',ty).style('font-size',n.font+'px');n.lines.forEach((l,i)=>label.append('tspan').attr('x',tx).attr('dy',i?n.line:0).text(l).each(function(){g.AtlasMeasure.fit(this,n.width-44);}));
 if(!isTopic){const ts=descendants(d).filter(AtlasModel.isLeaf);group.append('text').attr('class','category-coverage').style('font-size',(10*(n.cardScale||1))+'px').attr('x',tx).attr('y',n.height-CARD.META_BOTTOM*(n.cardScale||1)).text(d.type==='context'?'Personal learning':ts.length+' Topics · context');}
 }
 inspect();updateOptics();}
function focusTopic(key,animate=true){timed('Topic focus',()=>{
 viewState='topic';updateOptics();const n=L.byKey.get(key),area=viewportArea(),k=Math.min(VIEW.topicFont/n.font,area.width/(n.width+16),area.height/(n.height+16));
 const b={x0:n.x-n.width/2,x1:n.x+n.width/2,y0:n.y,y1:n.y+n.height};navigateCamera(centerBounds(b,k,area),{kind:'topic',key},animate);
});}
function fit(keys,animate=true,kind=keys?'subtree':'overview'){
 timed(kind==='overview'?'Fit all':'Fit subtree',()=>{
  const ns=visible.filter(n=>!keys||keys.has(n.key));if(!ns.length)return;viewState=kind==='overview'?'overview':'subtree';updateOptics();
  const b=AtlasLayout.contentBounds(L,ns),area=viewportArea(),fullScale=Math.min(VIEW.maxScale,area.width/(b.x1-b.x0),area.height/(b.y1-b.y0));
  let k=Math.min(fullScale,kind==='subtree'?VIEW.subtreeFont/14:VIEW.maxScale),targetBounds=b;
  navigateCamera(centerBounds(targetBounds,k,area),{kind,keys:keys?new Set(keys):null},animate);
 });
}
function fitSubtree(key=selected,animate=true){const n=m.nodes.get(key);if(!n)return fit(null,animate);fit(new Set(subtreeNodes(n).map(n=>n.key)),animate,'subtree');}

function refitIntent(){if(!fitIntent)return;const i=fitIntent;if(i.kind==='topic')focusTopic(i.key,false);else fit(i.keys,false,i.kind);}
function provenance(n){
 const ids=[...new Set([...(n.source_ids||[]),...Object.values(n.fact_sources||{}).flat()])];
 return acceptedProvenance([...n.evidence_ids,...n.observations.flatMap(o=>o.evidence_ids||[])])+list('Catalog provenance',ids.map(id=>{
  const entries=m.raw.provenance[id]||[];
  return `<p>${esc(id)}${entries.map(e=>`<br>${esc(e.observation||'')}<br>${esc(e.source?.method||'')} ${esc(e.source?.path||e.source?.endpoint_path||e.source?.endpoint||'')}`).join('')}</p>`;
 }),false);
}
function inspect(){
 const n=m.nodes.get(selected),counts=m.raw.counts;let html='';
 if(!n||n===m.root){html=`<p>Personal knowledge</p><h2>My Skill Tree</h2><p class="stat">${counts.learned} learned · ${counts.verified} verified</p><p>${counts.next} evidence-backed Next Topic${counts.next===1?'':'s'}<br>${counts.categories} context Categories · ${counts.roots} root domain${counts.roots===1?'':'s'}</p>`+list('Next', [...m.next.keys()].map(k=>listButton(k,m.nodes.get(k).displayTitle)))+list('Root Categories',m.root.children.map(c=>listButton(c.key,c.title)))+`<p>Categories provide context. Learning and verification belong to Topics.</p><p class="legend">● Learned · ◎ Verified<br>◇ Next · explicit prerequisites satisfied</p><p>Select a Category, then fit its subtree. Select a Topic to read its evidence.</p><p><a href="global.html" target="_blank" rel="noopener">Open Global Atlas ↗</a></p>`;}

 else{
  html=`<h2>${esc(n.displayTitle)}</h2><p class="path">${path(n).map(esc).join(' &gt; ')}</p>`;
  if(n.type==='category'){
   const cats=n.children.filter(c=>c.type==='category'),members=m.structuralChildren.get(n.key)||[],leaves=m.membershipLeaves.get(n.key),shared=members.filter(c=>c.parentKey!==n.key);
   html+=`<p>Context Category · ID ${n.id}<br>${cats.length} child categories<br>${members.filter(AtlasModel.isLeaf).length} direct leaf memberships<br>${leaves.size} distinct descendant leaves<br>${n.leafKeys.length} rows in this physical subtree</p><div class="actions"><button id="focus-subtree">Fit selected subtree</button></div>`+list('Child Categories',cats.map(c=>listButton(c.key,c.title)))+list('Shared leaves located elsewhere',shared.map(c=>listButton(c.key,c.displayTitle)),false);
  }else{
   const label=n.type==='reference'?'Unresolved reference':n.resolution==='RESOLVED_TOPIC'?'Resolved Topic':'Partial Topic';
   html+=`<p class="stat">${label}</p><p>Numeric ID: ${n.id}</p>`;
   if(n.type==='reference')html+='<p>Known from structural membership. Topic title, public URL and theory metadata have not been resolved.</p>';
   else{
    const meta=n.accepted_metadata||{};
    html+=`<p>${n.is_learned===true?'● Learned':n.is_next?'◇ Next':'◌ Unknown'}${n.is_verified?' · ◎ Verified':''}<br>Verification: ${n.observations.map(o=>esc(o.verification_status)).join(', ')||'unknown'}<br>Verified: ${n.is_verified?'yes':'no'}</p>`;
    if(meta.theory_step_id!=null)html+=`<p>Theory step: ${esc(meta.theory_step_id)}<br>Source: accepted Topic metadata</p>`;
    if(n.theory!=null)html+=`<p>Catalog theory identifier: ${esc(n.theory)}</p>`;
    if(meta.url)html+=`<p><a href="${esc(meta.url)}" target="_blank" rel="noopener">Open in Hyperskill ↗</a></p>`;
    html+='<p>Resolution describes the global capture; existing accepted metadata is retained by the same Topic ID.</p>';
   }
   html+=`<p>Global identity: ${esc(n.key)}</p><div class="actions"><a id="show-global" href="global.html?key=${encodeURIComponent(n.key)}" target="_blank" rel="noopener">Show in Global Atlas ↗</a></div>`;
   if(n.type==='topic'&&m.analytics)html+=ProgressPresentation.topic(m.analytics,n.id);
   if(n.is_next)html+=`<p>◇ Next: complete captured prerequisite list is satisfied by explicit learned progress.</p>`+list('Required learned Topics',n.nextEvidence.required.map(k=>listButton(k,m.nodes.get(k).displayTitle)))+`<p>Source: ${n.nextEvidence.source_ids.map(esc).join(', ')}</p>`;
   html+=list('Structural memberships',n.memberships.map(k=>m.nodes.has(k)?listButton(k,m.nodes.get(k).title):`<p>${esc(m.global.nodes.get(k).title)} · global context</p>`))+`<p>Physical row: ${esc(m.parent(n).title)}${n.memberships.length>1?' · one row shared by all memberships':''}</p>`;
  }
  html+=provenance(n);
 }
 document.querySelector('aside').classList.toggle('has-selection',!!selected);$('#inspector').innerHTML=html;
 $('#inspector').querySelectorAll('[data-select]').forEach(b=>b.onclick=()=>select(b.dataset.select,true));
 $('#focus-subtree')?.addEventListener('click',()=>fitSubtree(selected));
 $('#fit-subtree').disabled=!n||AtlasModel.isLeaf(n);
}
// Measured full-scene selection redraw was >100 ms. Restyle the same nodes;
// no virtualization, existence change, geometry work or reduced scene content.
function paintSelection(){
 nodes.selectAll('.node').classed('selected',n=>n.key===selected).attr('aria-pressed',n=>n.key===selected);
 const context=new Set();let n=m.nodes.get(selected);if(n?.type==='category')while(n){context.add(n.key);n=m.parent(n);}
 taxonomy.selectAll('.taxonomy').classed('context',e=>e.children.some(k=>context.has(k)));
 inspect();updateOptics();
}
function select(key,navigate=false){
 const n=m.nodes.get(key);if(!n)return;
 const reading=AtlasModel.isLeaf(n)||navigate,restoreFocus=document.activeElement?.classList.contains('node');
 timed('selection',()=>{
  selected=key;if(reading)viewState=AtlasModel.isLeaf(n)?'topic':'subtree';
  paintSelection();
  if(restoreFocus)nodes.selectAll('.node').filter(function(){return this.dataset.key===key;}).node()?.focus({preventScroll:true});
  if(reading){if(AtlasModel.isLeaf(n))focusTopic(key);else fitSubtree(key);}
  $('#announcement').textContent=(reading?'Focused: ':'Selected: ')+(n.displayTitle||n.title);
 });
}
function updateCounts(){
 const c=m.raw.counts;
 $('#counts').textContent=`${c.leaves} Topics · ${c.categories} context Categories · all rendered`;
 $('#mode-summary').textContent=`My Skill Tree · ${c.learned} learned · ${c.verified} verified · ${c.next} Next`;
}
function reflow(extraLearned=[]){
 const old=L.byKey.get(selected),anchor=old?{x:old.x*transform.k+transform.x,y:(old.y+old.height/2)*transform.k+transform.y}:null;
 m=timed('growth projection',()=>AtlasModel.model(m.source,{extraLearned}));
 L=timed('growth layout',()=>AtlasLayout.build(m,g.AtlasV6.measure));
 if(!m.nodes.has(selected))selected=null;
 buildMinimap();updateCounts();draw();
 const n=L.byKey.get(selected);
 if(anchor&&n)navigateCamera(d3.zoomIdentity.translate(anchor.x-n.x*transform.k,anchor.y-(n.y+n.height/2)*transform.k).scale(transform.k),null,false);
 else fit(null,false);
 $('#mode-summary').textContent+=' · Validation-only growth';
 return L;
}
async function init(){
 const start=performance.now(),raw=await(await fetch('model.json')).json();
 raw.projectCompletion=await(await fetch('../../progress.json')).json();
 raw.completionScopes=await(await fetch('../knowledge-atlas-scope-pyramid/scope-index.json')).json();
 m=timed('model parse',()=>{return AtlasModel.model(raw);});
 const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');
 const measure=g.AtlasMeasure.width;
 L=timed('layout',()=>AtlasLayout.build(m,measure));metrics['tray packing']=L.trayPackingMilliseconds;
 updateCounts();
 buildOverviewGuide();buildMinimap();timed('initial render',draw);fit(null,false);
 $('#fit').onclick=()=>fit();$('#fit-subtree').onclick=()=>fitSubtree();
 for(const [id,scale] of [['in',1.4],['out',1/1.4]])$('#'+id).onclick=()=>{fitIntent=null;viewState=AtlasModel.isLeaf(m.nodes.get(selected))?'topic':'subtree';svg.interrupt();svg.call(zoom.scaleBy,scale);};
 $('#theme').onclick=()=>document.body.classList.toggle('light');$('#clear').onclick=()=>{selected=null;paintSelection();};
 $('#search').oninput=()=>timed('search',()=>{
  const q=$('#search').value.trim().toLowerCase(),all=[...m.registry.values()],matches=q?all.filter(n=>n.displayTitle.toLowerCase().includes(q)||String(n.id)===q).sort((a,b)=>(String(b.id)===q?1:0)-(String(a.id)===q?1:0)||(b.displayTitle.toLowerCase()===q?1:0)-(a.displayTitle.toLowerCase()===q?1:0)||a.id-b.id).slice(0,12):[];
  $('#results').innerHTML=matches.map(n=>listButton(n.key,n.displayTitle+' · '+(n.type==='reference'?'Unresolved reference':n.type))).join('')||(q?'<p>No match in My Skill Tree.</p>':'');
  $('#results').querySelectorAll('button').forEach(b=>b.onclick=()=>{timed('Search navigation',()=>select(b.dataset.select,true));$('#results').replaceChildren();});
 });
 $('#search').onkeydown=e=>{if(e.key==='Enter')$('#results button')?.click();if(e.key==='ArrowDown'){e.preventDefault();$('#results button')?.focus();}if(e.key==='Escape')$('#results').replaceChildren();};
 let first=true;new ResizeObserver(()=>{if(first){first=false;return;}refitIntent();}).observe($('#canvas'));
 metrics['browser initialization']=performance.now()-start;
 g.AtlasV6={reflow, state:()=>({m,L,selected,mode,collapsed,transform,metrics,samples,visible,viewState,transitioning,fitIntent}),select,fit,fitSubtree,focusTopic,measure,draw};
}
init().catch(e=>{$('#error').textContent='Could not load prototype: '+e.message;console.error(e);});
})(globalThis);
