/* Derived directly from V6.6 app.js. See BASELINE.md. */
(function(g){
'use strict';
const $=s=>document.querySelector(s),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const CARD={RADIUS:5,TOPIC_RADIUS:3,HEADER_MAIN:8,HEADER_CATEGORY:5,LABEL_X:34,DISCLOSURE_X:15,META_BOTTOM:7,STATUS_X:12,TOPIC_LABEL_X:24,EVIDENCE_RIGHT:10};
let m,L,selected=null,mode='global',collapsed=new Set(),transform=d3.zoomIdentity,visible=[],fitIntent=null,viewState='overview',transitioning=false,miniBounds=null,navigationId=0;const metrics={},samples={};
const svg=d3.select('#graph');let renderer=null,hovered=null,focusedKey=null,selectionContext=new Set(),pointerDown=null,pointerPosition=null;
// Camera state is synchronous; DOM work consumes only the latest state once/frame.
let cameraFrame=0,graphSize=null,viewportAreas=null;
const inspectorState={open:false,pinned:false};
const descendantCache=new Map(),subtreeCache=new Map(),subtreeSets=new Map(),subtreeBounds=new Map(),fitBounds=new WeakMap();
function scheduleCamera(){if(!cameraFrame)cameraFrame=requestAnimationFrame(renderCamera);}
function renderCamera(){
 if(cameraFrame){cancelAnimationFrame(cameraFrame);cameraFrame=0;}
 if(renderer){if(pointerPosition)hovered=renderer.hit((pointerPosition.x-transform.x)/transform.k,(pointerPosition.y-transform.y)/transform.k);const node=m.nodes.get(hovered),title=AtlasModel.isLeaf(node)?node.displayTitle:'';if($('#graph').title!==title)$('#graph').title=title;renderer.render(transform,viewState,selected,selectionContext,hovered,document.activeElement===$('#graph'));}
 const value=(transform.k*100).toFixed(transform.k<.1?1:0)+'%';if($('#zoom-value').textContent!==value)$('#zoom-value').textContent=value;
 updateOptics();
 $('#orientation-world').setAttribute('transform',`translate(${transform.x},${transform.y}) scale(${transform.k})`);
}
const zoom=d3.zoom().scaleExtent([.0001,4]).on('zoom',e=>{transform=e.transform;if(e.sourceEvent)fitIntent=null;scheduleCamera();});svg.call(zoom).on('dblclick.zoom',null);
function timed(name,fn){const t=performance.now(),v=fn();metrics[name]=performance.now()-t;(samples[name]??=[]).push(metrics[name]);return v;}
const VIEW={duration:220,topicFont:16,subtreeFont:13,minReadingFont:10,pad:24,maxScale:1.3};
function updateOptics(){
 if(!L)return;
 const canvas=$('#canvas'),guide=$('#overview-guide'),status=$('#view-status');
 if(canvas.dataset.view!==viewState)canvas.dataset.view=viewState;
 const hidden=viewState!=='overview';if(guide.hidden!==hidden)guide.hidden=hidden;
 $('#orientation').toggleAttribute('hidden',viewState!=='overview'||m.nodes.get(selected)?.type!=='category');
 const value=viewState==='overview'?'Overview · zoom in to read':viewState==='topic'?(m.nodes.get(selected)?.type==='reference'?'Reference focus':'Topic focus'):transform.k*14<10?'Subtree overview · choose a child to read':'Subtree reading';
 if(status.textContent!==value)status.textContent=value;

}
// Measure both existing view areas only at initialization/container resize.
// The guide is absolute-positioned; measuring its visible area does not change
// canvas bounds. No geometry read follows camera/marker writes during navigation.
function refreshViewport(){
 const guide=$('#overview-guide'),hidden=guide.hidden;if(hidden)guide.hidden=false;
 const r=$('#graph').getBoundingClientRect(),control=$('.map-controls').getBoundingClientRect(),status=$('#view-status').getBoundingClientRect(),g=guide.getBoundingClientRect(),footer=$('.map-footer').getBoundingClientRect();
 if(hidden)guide.hidden=true;
 graphSize={width:r.width,height:r.height};renderer?.resize(r.width,r.height);
 const overlay=inspectorState.open&&!inspectorState.pinned?$('#inspector-drawer').getBoundingClientRect().width:0;
 const area=bottom=>({x:VIEW.pad,y:bottom-r.top+16,width:Math.max(1,r.width-overlay-2*VIEW.pad),height:Math.max(1,r.height-(bottom-r.top+16)-(r.bottom-footer.top+16))});
 viewportAreas={overview:area(Math.max(control.bottom,status.bottom,g.bottom)),reading:area(Math.max(control.bottom,status.bottom))};
}
// Drawer changes only the available camera rectangle; never rebuild the scene.
function setInspector(open,pinned=inspectorState.pinned){
 inspectorState.open=open;inspectorState.pinned=pinned;
 const main=$('main');main.dataset.inspectorOpen=String(open);main.dataset.inspectorPinned=String(pinned);
 $('#inspector-drawer').hidden=!open;$('#inspector-toggle').setAttribute('aria-expanded',String(open));
 $('#inspector-pin').setAttribute('aria-pressed',String(pinned));$('#inspector-pin').textContent=pinned?'Unpin':'Pin';
 refreshViewport();
 if(fitIntent)refitIntent();else keepSelectedVisible();
 scheduleCamera();
}
function keepSelectedVisible(){
 const n=L.byKey.get(selected);if(!n)return;
 const area=viewportArea(),x=n.x*transform.k+transform.x,y=n.y*transform.k+transform.y,w=n.width*transform.k,h=n.height*transform.k;
 const shift=(lo,hi,start,size)=>hi-lo>size?start+size/2-(lo+hi)/2:lo<start?start-lo:hi>start+size?start+size-hi:0;
 const dx=shift(x-w/2,x+w/2,area.x,area.width),dy=shift(y,y+h,area.y,area.height);
 if(dx||dy)navigateCamera(d3.zoomIdentity.translate(transform.x+dx,transform.y+dy).scale(transform.k),null,false);
}
// A small selection-only UI overlay reuses the exact canonical segment paths.
// The accepted tile commands, normal optics and complete semantic scene stay frozen.
function buildOrientation(){
 const group=$('#orientation-world');group.replaceChildren();const n=m.nodes.get(selected);if(n?.type!=='category')return;
 const ns='http://www.w3.org/2000/svg',append=(tag,attrs)=>{const el=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))el.setAttribute(k,v);group.append(el);};
 L.connectorSegments.forEach((e,i)=>{
  const direct=e.parent===selected,path=selectionContext.has(e.parent)&&(e.children||[]).some(k=>selectionContext.has(k));
  if(direct||path)append('path',{d:e.d,'data-segment':i,class:direct?'direct':'ancestor'});
 });
 const keys=new Set([...selectionContext,...n.children.filter(c=>c.type==='category').map(c=>c.key)]);
 for(const key of keys){const c=L.byKey.get(key);if(c)append('rect',{x:c.x-c.width/2,y:c.y,width:c.width,height:c.height,rx:CARD.RADIUS,'data-category':key,class:key===selected?'chosen':selectionContext.has(key)?'ancestor':'direct'});}
}
function viewportArea(){return viewportAreas[viewState==='overview'?'overview':'reading'];}
function navigateCamera(next,intent,animate=true){
 const id=++navigationId;svg.interrupt();fitIntent=intent;transitioning=false;
 if(animate&&!matchMedia('(prefers-reduced-motion: reduce)').matches){transitioning=true;svg.transition().duration(VIEW.duration).call(zoom.transform,next).end().catch(()=>{}).finally(()=>{if(id===navigationId){renderCamera();transitioning=false;}});}
 else{svg.call(zoom.transform,next);renderCamera();}
}
function centerBounds(b,k,area){return d3.zoomIdentity.translate(area.x+area.width/2-(b.x0+b.x1)/2*k,area.y+area.height/2-(b.y0+b.y1)/2*k).scale(k);}
function buildOverviewGuide(){
 const majors=m.root.children.filter(n=>n.type==='category'),branches=['category:521','category:1164','category:1166'].map(k=>m.nodes.get(k)).filter(Boolean);$('#overview-guide').innerHTML=`<span>${esc(m.root.title)}</span><div>${majors.map(n=>`<button data-region="${esc(n.key)}">${esc(n.title)}</button>`).join('')}</div><p class="guide-branches">Computer science: ${branches.map(n=>`<button data-region="${esc(n.key)}">${esc(n.title)}</button>`).join(' · ')}</p>`;
 $('#overview-guide').querySelectorAll('[data-region]').forEach(b=>b.onclick=()=>select(b.dataset.region,true));
}
function buildMinimap(){miniBounds=AtlasLayout.contentBounds(L,L.nodes);}
function boundsForSubtree(key){
 if(!subtreeBounds.has(key)){
  const n=m.nodes.get(key),ns=n?subtreeNodes(n).map(v=>L.byKey.get(v.key)):[];
  subtreeBounds.set(key,ns.length?AtlasLayout.contentBounds(L,ns):null);
 }
 return subtreeBounds.get(key);
}
function descendants(n){if(!descendantCache.has(n.key))descendantCache.set(n.key,[n,...n.children.flatMap(descendants)]);return descendantCache.get(n.key);}
function subtreeNodes(n){
 if(!subtreeCache.has(n.key)){const ns=descendants(n).slice(),keys=new Set(ns.map(v=>v.key));for(const key of m.membershipLeaves.get(n.key)||[])if(!keys.has(key))ns.push(m.nodes.get(key));subtreeCache.set(n.key,ns);}
 return subtreeCache.get(n.key);
}
function path(n){const out=[];while(n){out.unshift(n.displayTitle||n.title);n=m.parent(n);}return out;}
function listButton(key,title){return `<button data-select="${esc(key)}">${esc(title)}</button>`;}
function list(title,items,open=true){return `<details ${open?'open':''}><summary>${esc(title)} (${items.length})</summary><div class="inspector-list">${items.join('')||'<p>None recorded.</p>'}</div></details>`;}
function acceptedProvenance(ids){return list('Advanced / Evidence',[...new Set(ids||[])].map(id=>{const e=m.raw.evidence.find(e=>e.id===id);return e?`<p>${esc(id)}<br>${esc(e.method)} · ${esc(e.observed_on)}<br>${esc(e.note)}${e.url?`<br><a href="${esc(e.url)}" target="_blank" rel="noopener">Source</a>`:''}</p>`:'';}),false);}
function draw(){
 visible=AtlasLayout.visible(L,m,collapsed);
 if(!renderer)renderer=new AtlasTiled.Renderer($('#graph'),$('#minimap'),m,L,descendants,CARD,scheduleCamera);
 inspect();updateOptics();
}
function focusTopic(key,animate=true){timed('Topic focus',()=>{
 viewState='topic';updateOptics();const n=L.byKey.get(key),area=viewportArea(),k=Math.min(VIEW.topicFont/n.font,area.width/(n.width+16),area.height/(n.height+16));
 const b={x0:n.x-n.width/2,x1:n.x+n.width/2,y0:n.y,y1:n.y+n.height};navigateCamera(centerBounds(b,k,area),{kind:'topic',key},animate);
});}
function fit(keys,animate=true,kind=keys?'subtree':'overview'){
 timed(kind==='overview'?'Fit all':'Fit subtree',()=>{
  const ns=visible.filter(n=>!keys||keys.has(n.key));if(!ns.length)return;viewState=kind==='overview'?'overview':'subtree';updateOptics();
  const b=keys?(fitBounds.has(keys)?fitBounds.get(keys):AtlasLayout.contentBounds(L,ns)):miniBounds,area=viewportArea();if(keys&&!fitBounds.has(keys))fitBounds.set(keys,b);const fullScale=Math.min(VIEW.maxScale,area.width/(b.x1-b.x0),area.height/(b.y1-b.y0));
  let k=Math.min(fullScale,kind==='subtree'?VIEW.subtreeFont/14:VIEW.maxScale),targetBounds=b;
  navigateCamera(centerBounds(targetBounds,k,area),{kind,keys:keys?new Set(keys):null},animate);
 });
}
function fitSubtree(key=selected,animate=true){const n=m.nodes.get(key);if(!n)return fit(null,animate);if(!subtreeSets.has(key)){const keys=new Set(subtreeNodes(n).map(n=>n.key));subtreeSets.set(key,keys);fitBounds.set(keys,boundsForSubtree(key));}fit(subtreeSets.get(key),animate,'subtree');}

function refitIntent(){if(!fitIntent)return;const i=fitIntent;if(i.kind==='topic')focusTopic(i.key,false);else fit(i.keys,false,i.kind);}
function provenance(n){
 const ids=[...new Set([...(n.source_ids||[]),...Object.values(n.fact_sources||{}).flat()])];
 return acceptedProvenance([...n.evidence_ids,...n.observations.flatMap(o=>o.evidence_ids||[])])+list('Catalog provenance',ids.map(id=>{
  const entries=m.raw.provenance[id]||[];
  return `<p>${esc(id)}${entries.map(e=>`<br>${esc(e.observation||'')}<br>${esc(e.source?.method||'')} ${esc(e.source?.endpoint_path||e.source?.endpoint||'')}`).join('')}</p>`;
 }),false);
}
function inspect(){
 const n=m.nodes.get(selected),counts=m.raw.counts;let html='';
 if(!n||n===m.root){html=`<p>Global Catalog</p><h2>Global Atlas</h2><p class="stat">${counts.leaves.toLocaleString()} leaf slots</p><p>${counts.categories} categories · 5 roots<br>${counts.RESOLVED_TOPIC} resolved Topic · ${counts.PARTIAL_TOPIC} partial Topics<br>${counts.UNRESOLVED_REFERENCE.toLocaleString()} unresolved references</p><p>${[...m.registry.values()].filter(n=>n.is_learned).length} learned · ${[...m.registry.values()].filter(n=>n.is_verified).length} verified</p>`+list('Root Categories',m.root.children.map(c=>listButton(c.key,c.title)))+`<p class="legend">● Learned · ◎ Verified<br>○ Not learned · ◌ Unknown<br>Slate branches: taxonomy</p><p>Fit All is an orientation view. Select a Category, then fit its subtree; focus a row to read.</p><p>Relation overlays are disabled in this prototype.</p>`;}
 else{
  html=`<h2>${esc(n.displayTitle)}</h2><p class="path">${path(n).map(esc).join(' &gt; ')}</p>`;
  if(n.type==='category'){
   const cats=n.children.filter(c=>c.type==='category'),members=m.structuralChildren.get(n.key)||[],leaves=m.membershipLeaves.get(n.key),shared=members.filter(c=>c.parentKey!==n.key);
   html+=`<p>Category ID ${n.id}<br>${cats.length} child categories<br>${members.filter(AtlasModel.isLeaf).length} direct leaf memberships<br>${leaves.size} distinct descendant leaves<br>${n.leafKeys.length} rows in this physical subtree</p><div class="actions"><button id="focus-subtree">Fit selected subtree</button></div>`+list('Child Categories',cats.map(c=>listButton(c.key,c.title)))+list('Shared leaves located elsewhere',shared.map(c=>listButton(c.key,c.displayTitle)),false);
  }else{
   const label=n.type==='reference'?'Unresolved reference':n.resolution==='RESOLVED_TOPIC'?'Resolved Topic':'Partial Topic';
   html+=`<p class="stat">${label}</p><p>Numeric ID: ${n.id}</p>`;
   if(n.type==='reference')html+='<p>Known from structural membership. Topic title, public URL and theory metadata have not been resolved.</p>';
   else{
    const meta=n.accepted_metadata||{};
    html+=ProgressPresentation.topic(m.analytics,n.id);
    html+=`<p>${n.is_learned===true?'● Learned':n.is_learned===false?'○ Not learned':'◌ Unknown'}${n.is_verified?' · ◎ Verified':''}<br>Verification: ${n.observations.map(o=>esc(o.verification_status)).join(', ')||'unknown'}</p>`;
    if(meta.theory_step_id!=null)html+=`<p>Theory step: ${esc(meta.theory_step_id)}<br>Source: accepted Topic metadata</p>`;
    if(n.theory!=null)html+=`<p>Catalog theory identifier: ${esc(n.theory)}</p>`;
    if(meta.url)html+=`<p><a href="${esc(meta.url)}" target="_blank" rel="noopener">Open in Hyperskill ↗</a></p>`;
    const fields=['parent_id','root_id','hierarchy','children','prerequisites','explicit_prerequisites','followers'];
    html+=list('Topic metadata',fields.filter(k=>Object.hasOwn(n,k)).map(k=>`<p>${esc(k.replaceAll('_',' '))}: ${esc(JSON.stringify(n[k],null,1))}</p>`),false);
    html+='<p>Resolution describes the global capture; existing accepted metadata is retained by the same Topic ID.</p>';
   }
   html+=list('Structural memberships',n.memberships.map(k=>listButton(k,m.nodes.get(k).title)))+`<p>Physical row: ${esc(m.parent(n).title)}${n.memberships.length>1?' · one row shared by all memberships':''}</p>`;
  }
  html+=provenance(n);
 }
 document.querySelector('aside').classList.toggle('has-selection',!!selected);$('#inspector').innerHTML=html;
 $('#inspector').querySelectorAll('[data-select]').forEach(b=>b.onclick=()=>select(b.dataset.select,true));
 $('#focus-subtree')?.addEventListener('click',()=>fitSubtree(selected));
 $('#fit-subtree').disabled=!n||AtlasModel.isLeaf(n);
}
function paintSelection(){
 selectionContext=new Set();let n=m.nodes.get(selected);if(n?.type==='category')while(n){selectionContext.add(n.key);n=m.parent(n);}
 buildOrientation();
 focusedKey=selected;if(renderer)renderer.selectionBounds=selected?boundsForSubtree(selected):null;inspect();updateOptics();scheduleCamera();
 const chosen=m.nodes.get(selected);$('#graph').setAttribute('aria-label',chosen?(chosen.displayTitle||chosen.title)+'; '+chosen.type+'; '+path(chosen).join(' > '):'Complete global taxonomy. Drag to pan; scroll or pinch to zoom. Use arrow keys to select; Enter to focus.');
}
function bindGraphInteraction(){
 const graph=$('#graph');
 const point=e=>{const r=graph.getBoundingClientRect();return{x:(e.clientX-r.left-transform.x)/transform.k,y:(e.clientY-r.top-transform.y)/transform.k};};
 graph.addEventListener('pointerdown',e=>{pointerDown={x:e.clientX,y:e.clientY};});
 graph.addEventListener('click',e=>{if(pointerDown&&Math.hypot(e.clientX-pointerDown.x,e.clientY-pointerDown.y)>4)return;const p=point(e),key=renderer.hit(p.x,p.y);if(key){select(key,AtlasModel.isLeaf(m.nodes.get(key)));graph.focus({preventScroll:true});}});
 graph.addEventListener('pointermove',e=>{const r=graph.getBoundingClientRect();pointerPosition={x:e.clientX-r.left,y:e.clientY-r.top};const key=renderer.hit((pointerPosition.x-transform.x)/transform.k,(pointerPosition.y-transform.y)/transform.k);if(key!==hovered){hovered=key;scheduleCamera();}});
 graph.addEventListener('pointerleave',()=>{pointerPosition=null;hovered=null;graph.title='';scheduleCamera();});
 graph.addEventListener('focus',scheduleCamera);graph.addEventListener('blur',scheduleCamera);
 graph.addEventListener('keydown',e=>{
  const order=renderer.scene.entities,at=order.findIndex(n=>n.key===(focusedKey||selected));
  if(['ArrowDown','ArrowRight','ArrowUp','ArrowLeft','Home','End'].includes(e.key)){
   e.preventDefault();const i=e.key==='Home'?0:e.key==='End'?order.length-1:Math.max(0,Math.min(order.length-1,(at<0?0:at)+(e.key==='ArrowDown'||e.key==='ArrowRight'?1:-1)));
   focusedKey=order[i].key;select(focusedKey,false);$('#announcement').textContent='Selected: '+(m.nodes.get(focusedKey).displayTitle||m.nodes.get(focusedKey).title);
  }else if(e.key==='Enter'||e.key===' '){e.preventDefault();if(focusedKey||selected)select(focusedKey||selected,true);}
 });
}
function select(key,navigate=false){
 const n=m.nodes.get(key);if(!n)return;
 const reading=AtlasModel.isLeaf(n)||navigate,restoreFocus=document.activeElement===$('#graph');
 timed('selection',()=>{
  selected=key;setInspector(true);if(reading)viewState=AtlasModel.isLeaf(n)?'topic':'subtree';
  paintSelection();
  if(restoreFocus)$('#graph').focus({preventScroll:true});
  if(reading){if(AtlasModel.isLeaf(n))focusTopic(key);else fitSubtree(key);}
  $('#announcement').textContent=(reading?'Focused: ':'Selected: ')+(n.displayTitle||n.title);
 });
}
async function init(){
 const start=performance.now(),text=await(await fetch('model.json')).text();let raw;
 m=timed('model parse',()=>{raw=JSON.parse(text);return AtlasModel.model(raw);});
 const scopes=await(await fetch('../knowledge-atlas-scope-pyramid/scope-index.json')).json(),completion=await(await fetch('../../progress.json')).json();
 m.analytics=ProgressAnalytics.create({catalog:raw,scopes,completion});
 for(const n of m.registry.values())if(n.type==='topic'){const state=m.analytics.topic(n.id);n.is_learned=state.learned;n.is_verified=state.verified;}
 const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');
 const measure=(t,font=14,weight=400)=>{ctx.font=weight+' '+font+'px system-ui';return ctx.measureText(t).width;};
 L=timed('layout',()=>AtlasLayout.build(m,measure));metrics['tray packing']=L.trayPackingMilliseconds;
 $('#counts').textContent=`${raw.counts.leaves.toLocaleString()} leaf slots · ${raw.counts.categories} categories · all rendered`;
 $('#mode-summary').textContent=`Global Atlas · 5 roots · ${raw.counts.leaves.toLocaleString()} leaf slots · ${[...m.registry.values()].filter(n=>n.is_learned).length} learned · ${[...m.registry.values()].filter(n=>n.is_verified).length} verified`;
 buildOverviewGuide();buildMinimap();timed('initial render',draw);refreshViewport();bindGraphInteraction();fit(null,false);
 $('#fit').onclick=()=>{if(!inspectorState.pinned)setInspector(false);fit();};$('#fit-subtree').onclick=()=>fitSubtree();
 for(const [id,scale] of [['in',1.4],['out',1/1.4]])$('#'+id).onclick=()=>{fitIntent=null;svg.interrupt();svg.call(zoom.scaleBy,scale);renderCamera();};
 $('#theme').onclick=()=>{document.body.classList.toggle('light');renderer.invalidateStyles();};$('#clear').onclick=()=>{selected=null;paintSelection();};
 $('#inspector-toggle').onclick=()=>setInspector(true);$('#inspector-close').onclick=()=>{setInspector(false);$('#inspector-toggle').focus({preventScroll:true});};
 $('#inspector-pin').onclick=()=>setInspector(true,!inspectorState.pinned);
 $('#inspector-drawer').onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();$('#inspector-close').click();}};
 $('#search').oninput=()=>timed('search',()=>{
  const q=$('#search').value.trim().toLowerCase(),all=[...m.registry.values()],matches=q?all.filter(n=>n.displayTitle.toLowerCase().includes(q)||String(n.id)===q).sort((a,b)=>(String(b.id)===q?1:0)-(String(a.id)===q?1:0)||(b.displayTitle.toLowerCase()===q?1:0)-(a.displayTitle.toLowerCase()===q?1:0)||a.id-b.id).slice(0,12):[];
  $('#results').innerHTML=matches.map(n=>listButton(n.key,n.displayTitle+' · '+(n.type==='reference'?'Unresolved reference':n.type))).join('')||(q?'<p>No matching knowledge.</p>':'');
  $('#results').querySelectorAll('button').forEach(b=>b.onclick=()=>{timed('Search navigation',()=>select(b.dataset.select,true));$('#results').replaceChildren();});
 });
 $('#search').onkeydown=e=>{if(e.key==='Enter')$('#results button')?.click();if(e.key==='ArrowDown'){e.preventDefault();$('#results button')?.focus();}if(e.key==='Escape')$('#results').replaceChildren();};
 new ResizeObserver(([entry])=>{const r=entry.contentRect;if(graphSize&&r.width===graphSize.width&&r.height===graphSize.height)return;refreshViewport();refitIntent();}).observe($('#canvas'));
 metrics['browser initialization']=performance.now()-start;
 g.AtlasV6={state:()=>({m,L,selected,mode,collapsed,transform,metrics,samples,visible,viewState,transitioning,fitIntent,renderer,inspectorState:{...inspectorState},viewportAreas}),select,fit,fitSubtree,focusTopic,measure,draw};
}
init().catch(e=>{$('#error').textContent='Could not load prototype: '+e.message;console.error(e);});
})(globalThis);
