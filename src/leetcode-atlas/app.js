/* One persistent CPU world; reused V6.6 shell, camera and Inspector. */
(async function () {
'use strict';
const $=id=>document.getElementById(id), M=LeetCodeModel;
const [catalog,taxonomy,ledger,sources]=await Promise.all(['catalog','taxonomy','progress','sources'].map(async name=>{
 const response=await fetch('data/'+name+'.json');if(!response.ok)throw Error('Cannot load '+name);return response.json();
}));
const index=M.validate(catalog,taxonomy), progress=M.projectProgress(index,ledger,{publicOnly:true});
const V=LeetCodeVisualState,compiled=V.compile(index),projection=V.project(compiled,progress);let coverage;
await document.fonts.load('14px Atlas');await document.fonts.load('600 17px Atlas');await document.fonts.ready;
const canvas=$('world'),ctx=canvas.getContext('2d'), mini=$('minimap'),mc=mini.getContext('2d'),measureContext=document.createElement('canvas').getContext('2d');
const widthCache=new Map();
function measure(text,size=14,weight=400){const key=[text,size,weight].join('|');if(!widthCache.has(key)){measureContext.font=weight+' '+size+'px Atlas';widthCache.set(key,measureContext.measureText(text).width);}return widthCache.get(key);}
const mode='optimized-cpu';let activeTag=null,activeCategory=null,backStack=[];let view='global',m,L,bounds,selected=null,transform=d3.zoomIdentity,raf=0,W=0,H=0,painted=0,miniTransform,problemLimit=50,layoutBuilds=0,fitIntent={key:null,branch:true};
const inspectorState={open:false,pinned:false};
let visual;const allIds=new Set(index.problems.keys());const scenes=new Map(),filters=()=>({difficulty:$('difficulty').value,premium:$('premium').value});
function el(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function button(label,action,className){const e=el('button',label,className);e.type='button';e.onclick=action;return e;}
function link(label,url,className){const a=el('a',label,className);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;}
function palette(name){return getComputedStyle(document.documentElement).getPropertyValue('--'+name).trim();}
function layout(){
 if(L)return;
 const start=performance.now();m=M.buildHierarchy(index,progress,{view:'global'});L=LeetCodeOptimizedCPU.build(m,measure);layoutBuilds++;
 coverage=V.presentation(L,projection);bounds=L.bounds;scenes.set('catalog-taxonomy',{m,L,milliseconds:performance.now()-start});
 $('world-count').textContent=catalog.problems.length+' problems placed';renderTaxonomy();renderGuide();updateVisual();renderResults();inspect();requestPaint();
}
function progressMeter(stats,label){
 const meter=el('div',undefined,'progress-meter');meter.setAttribute('role','progressbar');meter.setAttribute('aria-label',label);meter.setAttribute('aria-valuemin','0');meter.setAttribute('aria-valuemax',String(stats.total));meter.setAttribute('aria-valuenow',String(stats.solved));meter.setAttribute('aria-valuetext',stats.solved+' / '+stats.total+' solved'+(stats.percent===null?'':', '+stats.percent.toFixed(1)+'%'));
 const fill=el('i');fill.style.width=(stats.percent||0)+'%';meter.append(fill);return meter;
}
function installSummary(){
 const host=$('filter-context'),global=el('div',undefined,'global-progress');global.id='global-progress';const stats=projection.global;
 global.append(el('span',stats.solved+' / '+stats.total.toLocaleString('en-US')+' solved','progress-count'),progressMeter(stats,'Loaded catalog solved progress'),el('strong',(stats.percent||0).toFixed(stats.solved?(stats.percent<1?2:1):0)+'%'));
 const distribution=el('div',undefined,'difficulty-distribution');distribution.id='difficulty-distribution';distribution.append(el('span','Catalog','distribution-label'));
 const bar=el('div',undefined,'distribution-bar');bar.setAttribute('role','img');bar.setAttribute('aria-label',[...compiled.difficulties].map(([name,ids])=>name+': '+ids.size).join(', '));
 for(const [name,ids] of compiled.difficulties){if(!ids.size)continue;const color=V.PALETTE[name].accent,segment=el('i');segment.style.flex=String(ids.size);segment.style.background=color;segment.title=name+': '+ids.size;bar.append(segment);const label=el('span',name+' '+ids.size.toLocaleString('en-US'),'difficulty-legend');const swatch=el('i');swatch.style.background=color;label.prepend(swatch);distribution.append(label);}
 distribution.insertBefore(bar,distribution.children[1]);host.append(global,distribution);
}
function updateVisual(){
 const query=$('search').value.trim(),f=filters(),active=Boolean(query||activeTag||activeCategory||f.difficulty!=='all'||f.premium!=='all');
 const matches=active?V.matches(compiled,{...f,query,tag:activeTag,category:activeCategory}):new Set(),regions=new Set();
 for(const id of matches)for(const category of compiled.memberships.get(id))regions.add(category);
 visual={active,matches,regions,solved:projection.solved,coverage,category:activeCategory};
 if(!activeTag)$('inspect-content')?.querySelector('.tag-coverage')?.remove();
 $('atlas-context').textContent='Local · partial'+(active?' · '+matches.size+' highlighted':'');requestPaint();
}
installSummary();

const zoom=d3.zoom().scaleExtent([.0001,4]).on('zoom',event=>{if(event.sourceEvent)fitIntent=null;transform=event.transform;$('problem-tooltip').hidden=true;requestPaint();});
d3.select(canvas).call(zoom).on('dblclick.zoom',null);
function goTransform(next,animate=false){const target=d3.select(canvas);target.interrupt();if(animate)target.transition().duration(160).call(zoom.transform,next);else target.call(zoom.transform,next);}
function viewportArea(){
 const r=canvas.getBoundingClientRect(),controls=document.querySelector('.map-controls').getBoundingClientRect(),guide=$('overview-guide').getBoundingClientRect();
 const narrow=matchMedia('(max-width:700px)').matches,drawer=$('inspector-drawer').getBoundingClientRect();
 const overlay=inspectorState.open&&!inspectorState.pinned&&!narrow?drawer.width:0;
 const top=Math.max(controls.bottom-r.top+12,getComputedStyle($('overview-guide')).visibility==='hidden'?0:guide.bottom-r.top+12,24),bottom=inspectorState.open&&narrow?Math.min(H-38,drawer.top-r.top-12):H-38;
 return{x0:0,y0:Math.min(top,H-80),x1:Math.max(1,W-overlay),y1:bottom};
}
function fitBox(b,maxScale=1.3){
 const a=viewportArea(),pad=Math.min(24,(a.x1-a.x0)/8),width=Math.max(1,a.x1-a.x0-2*pad),height=Math.max(1,a.y1-a.y0-48);
 const k=Math.max(.0001,Math.min(maxScale,width/Math.max(1,b.x1-b.x0),height/Math.max(1,b.y1-b.y0)));
 goTransform(d3.zoomIdentity.translate((a.x0+a.x1)/2-k*(b.x0+b.x1)/2,(a.y0+a.y1)/2-k*(b.y0+b.y1)/2).scale(k));
}
function refit(){if(!L||!W||!H)return;if(fitIntent?.key)focus(fitIntent.key,fitIntent.branch,fitIntent.detail);else if(fitIntent)fitBox(bounds);else{keepSelectedVisible();requestPaint();}}
function keepSelectedVisible(){
 const n=L.byKey.get(selected);if(!n)return;const a=viewportArea(),x=n.x*transform.k+transform.x,y=n.y*transform.k+transform.y,w=n.width*transform.k,h=n.height*transform.k;
 const shift=(lo,hi,start,size)=>hi-lo>size?start+size/2-(lo+hi)/2:lo<start?start-lo:hi>start+size?start+size-hi:0;
 const dx=shift(x-w/2,x+w/2,a.x0,a.x1-a.x0),dy=shift(y,y+h,a.y0,a.y1-a.y0);
 if(dx||dy)goTransform(d3.zoomIdentity.translate(transform.x+dx,transform.y+dy).scale(transform.k));
}
function fit(){
 if(inspectorState.open&&!inspectorState.pinned)setInspector(false);
 fitIntent={key:null,branch:true};$('overview-guide').hidden=false;fitBox(bounds);$('map-status').textContent='Overview · select a Topic to focus';
}
function focus(key,wholeBranch=false,detail=true,animate=false){
 let n=L.byKey.get(key);if(!n){const ids=progress.coverage.get(key)?.members;if(ids?.size)n=L.byKey.get([...ids].sort()[0]);}if(!n)return;
 fitIntent={key,branch:wholeBranch,detail};$('overview-guide').hidden=true;
 if(n.data.type==='problem'||!detail){fitBox({x0:n.rect.x,y0:n.y,x1:n.rect.x+n.width,y1:n.y+n.height},n.data.type==='problem'?1.25:1.3);}
 else{
  // Reading focus is a screen-space target, never a whole-Category fit.
  // Keep orientation commands separate; the same immutable world is panned.
  const a=viewportArea(),narrow=matchMedia('(max-width:700px)').matches;
  const target=narrow?200:220,k=target/L.policy.tileWidth;
  const primary=progress.coverage.get(key)?.primary||new Set(n.data.leafKeys||[]);
  let content=[...primary].map(id=>L.byKey.get(id)).filter(Boolean).sort((a,b)=>a.y-b.y||a.rect.x-b.rect.x||a.key.localeCompare(b.key));
  if(!content.length)content=[...(progress.coverage.get(key)?.members||[])].map(id=>L.byKey.get(id)).filter(Boolean).sort((a,b)=>a.y-b.y||a.rect.x-b.rect.x||a.key.localeCompare(b.key));
  const first=content[0];
  if(first){
   const grid=L.grids.find(g=>g.bank===first.physicalParent),available=a.x1-a.x0-40;
   const cols=Math.max(1,Math.min(grid?.cols||1,Math.floor((available+L.policy.gap*k)/(target+L.policy.gap*k))));
   const rowWidth=cols*target+(cols-1)*L.policy.gap*k;
   const x=(a.x0+a.x1)/2-first.rect.x*k-rowWidth/2;
   const y=a.y0+96-first.y*k;
   goTransform(d3.zoomIdentity.translate(x,y).scale(k),animate);
  }
 }

 $('map-status').textContent=(index.problems.has(key)?'Problem · ':'Topic · ')+(index.problems.has(key)?index.problems.get(key).displayNumber+'. '+index.problems.get(key).title:index.tax.get(key)?.title||n.presentationTitle);
 if(n.data.type==='problem'&&n.text.truncated)tooltip(n,W/2,H/2);
}
function setInspector(open){
 inspectorState.open=open;$('inspector-drawer').hidden=!open;
 $('map-main').dataset.inspectorOpen=String(open);$('map-main').dataset.inspectorPinned=String(inspectorState.pinned);
 $('inspector-toggle').setAttribute('aria-expanded',String(open));
 $('inspector-pin').textContent=inspectorState.pinned?'Unpin':'Pin';$('inspector-pin').setAttribute('aria-pressed',String(inspectorState.pinned));
 $('inspector-pin').setAttribute('aria-label',inspectorState.pinned?'Unpin Inspector over map':'Pin Inspector beside map');
 resize();
}

function setHash(){history.replaceState(null,'','#'+view+(selected?'/'+encodeURIComponent(selected):''));}
function select(key,{focusCard=true,branch=false}={}){
 const presentation=L.byKey.get(key);if(presentation?.data.kind==='bank')key=presentation.data.parent;
 remember();activeTag=null;activeCategory=index.tax.has(key)&&key!==M.ROOT?key:null;if(activeCategory)$('search').value='';selected=key;$('branch-menu').open=false;$('search-results').replaceChildren();$('search').setAttribute('aria-expanded','false');
 updateVisual();inspect();setInspector(true);if(focusCard)focus(key,branch,true,true);setHash();requestPaint();
}
function renderGuide(){
 const host=$('overview-guide');host.replaceChildren();
 for(const f of taxonomy.nodes.filter(n=>n.kind==='family'))host.append(button(f.title,()=>select(f.id,{branch:true})));
 host.hidden=false;
}
function renderTaxonomy(){
 const host=$('taxonomy');host.replaceChildren();
 for(const f of taxonomy.nodes.filter(n=>n.kind==='family')){
  const det=el('details'),sum=el('summary',f.title);det.append(sum);host.append(det);
  for(const c of taxonomy.nodes.filter(n=>n.parent===f.id)){
   const child=el('details'),heading=el('summary',c.title);child.append(heading);det.append(child);
   child.append(button('Explore branch',()=>select(c.id,{branch:true}),'pattern'));
   for(const p of taxonomy.nodes.filter(n=>n.parent===c.id)){
    const row=button(p.title,()=>select(p.id,{branch:true}),'pattern');const count=progress.coverage.get(p.id);row.append(el('span',String(count.primary.size)));child.append(row);
   }
  }
 }
}
function resultButton(p){const row=button(p.displayNumber+'. '+(p.title||'Title not recorded'),()=>select(p.id),'result');row.dataset.problemId=p.id;row.append(el('small',(p.difficulty||'Difficulty unknown')+' · '+(p.premium==='unknown'?'Availability unknown':p.premium==='premium'?'Premium':'Free')));return row;}
function renderResults(){
 const query=$('search').value.trim(),rows=m.selected.filter(p=>M.matches(p,{query}));
 const exact=p=>[p.id,p.displayNumber,p.slug].some(v=>v.toLowerCase()===query.toLowerCase());rows.sort((a,b)=>Number(exact(b))-Number(exact(a)));
 $('result-count').textContent=rows.length+' of '+catalog.problems.length+' loaded problems';$('search').setAttribute('aria-expanded',String(Boolean(query)));
 const host=$('search-results');host.replaceChildren();
 if(query){for(const t of index.tax.values())if((t.title+' '+t.id).toLowerCase().includes(query.toLowerCase())){const row=button(t.title,()=>select(t.id,{branch:true}),'result');row.dataset.taxonomyId=t.id;row.append(el('small','Topic / Category'));host.append(row);}rows.slice(0,problemLimit).forEach(p=>host.append(resultButton(p)));if(!rows.length)host.append(el('p','No matching loaded problems.','small muted'));if(rows.length>problemLimit)host.append(button('Show next 50',()=>{problemLimit+=50;renderResults();},'result'));}
 const all=$('problem-list');all.replaceChildren();m.selected.slice(0,problemLimit).forEach(p=>all.append(resultButton(p)));if(m.selected.length>problemLimit)all.append(button('Show next 50',()=>{problemLimit+=50;renderResults();},'result'));
}
function label(host,title){host.append(el('div',title,'inspect-label'));}
function inspect(){
 const host=$('inspect-content');host.replaceChildren();const p=index.problems.get(selected),t=index.tax.get(selected||M.ROOT);$('inspector-drawer').classList.toggle('has-selection',Boolean(selected));$('fit-subtree').disabled=!selected;
 if(p){
  host.append(el('div','PROBLEM '+p.displayNumber,'kicker'),el('h2',p.title||'Title not recorded'));
  host.append(el('span',p.difficulty||'Difficulty unknown','chip '+(p.difficulty||'').toLowerCase()),el('span',p.premium==='unknown'?'Availability unknown':p.premium==='premium'?'Premium':'Free','chip'));
  const state=progress.byProblem.get(p.id),box=el('div',state.state==='solved'?'Solved · owner-attested':state.state==='attempted'?'Attempted · evidenced':'Not yet recorded as solved','progress-state');
  if(state.evidence.length)box.append(el('small',state.evidence.length+' evidence record(s).'));host.append(box);host.append(el('p',p.id,'small identity'));
  if(state.solvedDate)host.append(el('p','Solved date: '+state.solvedDate,'small'));
  for(const e of state.evidence)host.append(link('Solution · '+e.solution.language,e.solution.repositoryUrl+'/blob/'+e.solution.commitSha+'/'+e.solution.path,'outbound'));
  label(host,'Primary placement');
  const primary=index.tax.get(p.primaryTaxonomyId),category=index.tax.get(primary.parent);
  host.append(button(category.title+' / '+primary.title,()=>select(primary.id,{branch:true}),'path-button'));
  label(host,'Topic tags');p.topicTags.forEach(tag=>{const b=button(tag,()=>{remember();activeTag=tag;activeCategory=null;$('search').value=tag;updateVisual();inspect();renderResults();},'member-link tag');host.append(b);});
  if(!p.topicTags.length)host.append(el('p','Topic tags not recorded.','small muted'));
  label(host,'Associated Categories');
  for(const id of M.memberships(index,p))if(index.tax.get(id).kind==='category'){
   const b=button(index.tax.get(id).title,()=>select(id,{branch:true}),'member-link');b.dataset.categoryId=id;host.append(b);
  }
  label(host,'Related techniques');
  for(const id of p.secondaryTaxonomyIds)host.append(button(index.tax.get(id).title,()=>select(id,{branch:true}),'member-link'));
  if(!p.secondaryTaxonomyIds.length)host.append(el('p','No additional reviewed memberships.','small muted'));
  host.append(link('Open problem on LeetCode ↗',p.canonicalUrl,'outbound'));
  const det=el('details',undefined,'data-details');det.append(el('summary','Identity & provenance'));
  const dl=el('dl');for(const [k,v] of [['Canonical MyAtlas ID',p.id],['Official internal ID',p.officialQuestionId||'Not obtained'],['Display number',p.displayNumber],['Catalog status',p.catalogStatus],['Tag coverage',p.tagsCompleteness],['Study plans',p.studyPlanIds===null?'Not reviewed':p.studyPlanIds.join(', ')||'None recorded'],['Source',p.provenance.datasetUrl||p.provenance.url],['Source revision',p.provenance.sourceRevision||'Reviewed sample'],['Reviewed',p.provenance.reviewedAt],['Method',p.provenance.method],['Availability',p.provenance.availabilityNote],['Placement',p.placement.reason]]){dl.append(el('dt',k),el('dd',v));}det.append(dl);host.append(det);if(p.provenance.reviewedComparison&&Object.keys(p.provenance.reviewedComparison).length){const comparison=el('details',undefined,'data-details');comparison.append(el('summary','Reviewed record comparison'),el('p',JSON.stringify(p.provenance.reviewedComparison)));host.append(comparison);}
 }else if(t){
  const c=progress.coverage.get(t.id),inScope=()=>true,primaryIds=[...c.primary].filter(inScope),memberIds=[...c.members].filter(inScope);host.append(el('div',t.id===M.ROOT?'LEETCODE':t.kind.toUpperCase(),'kicker'),el('h2',t.id===M.ROOT?'LeetCode Atlas':t.title));
  const stats=projection.categories.get(t.id),box=el('div',undefined,'category-progress');
  for(const [name,value]of [['Primary branch',stats.primary],['Associated',stats.associated]]){const row=el('div',undefined,'coverage-row');row.dataset.coverage=name==='Primary branch'?'primary':'associated';row.append(el('span',name+' · '+(value.total?value.solved+' / '+value.total+' solved':'No Problems'),'coverage-count'));if(value.total)row.append(progressMeter(value,name+' solved progress'));box.append(row);}
  host.append(box);
  const coverage=el('details',undefined,'data-details');coverage.append(el('summary','About coverage'),el('p','The MyAtlas taxonomy is curated, not an official LeetCode hierarchy. Coverage describes the partial catalog. Categories can share members; the global solved count uses unique IDs. Empty coverage does not mean completion.'));host.append(coverage);
  if(L.byKey.has(t.id)||c.members.size)host.append(button('Focus this branch',()=>focus(t.id,true),'path-button'));
  label(host,'Primary problems');const primary=primaryIds.map(id=>index.problems.get(id));primary.slice(0,50).forEach(p=>host.append(resultButton(p)));
  if(!primary.length)host.append(el('p','No physical primary block; associated problems remain navigable.','small muted'));
  if(primary.length>50)host.append(el('p','First 50 shown. Use problem search for every loaded identity.','small muted'));
  const related=memberIds.filter(id=>!c.primary.has(id));if(related.length){label(host,'Related problems');related.slice(0,50).forEach(id=>host.append(resultButton(index.problems.get(id))));}
  if(t.evidence?.length){const det=el('details',undefined,'data-details');det.append(el('summary','Taxonomy evidence'));for(const id of t.evidence){const s=sources.sources.find(s=>s.id===id);if(s)det.append(link(s.id.replace('source:',''),s.url,'outbound'));}host.append(det);}
 }else{host.append(el('h2','Identity not loaded'),el('p','This preview has a partial catalog. No title-based match was attempted.','inspect-copy'));}
 if(activeTag){const stats=projection.tags.get(activeTag);if(stats){const row=el('div',undefined,'tag-coverage coverage-row');row.dataset.tag=activeTag;row.append(el('span',activeTag+' · '+stats.solved+' / '+stats.total+' associated Problems solved','coverage-count'));if(stats.total)row.append(progressMeter(stats,'Associated '+activeTag+' progress'));host.append(row);}}

}
let relationKey=null,relationCache;
function related(){const key=(selected||'')+'|'+(activeTag||'');if(key!==relationKey){relationKey=key;relationCache=LeetCodeOptimizedCPU.relations(index,progress,selected,activeTag,allIds);}return relationCache;}
function labelObstacles(){const r=canvas.getBoundingClientRect(),b=mini.getBoundingClientRect();return b.width&&b.height?[{x0:b.left-r.left,y0:b.top-r.top,x1:b.right-r.left,y1:b.bottom-r.top}]:[];}
function remember(){backStack.push({view,selected,filters:filters(),query:$('search').value,transform,fitIntent,activeTag,activeCategory,inspector:{...inspectorState}});if(backStack.length>30)backStack.shift();$('history-back').disabled=false;}
$('history-back').onclick=()=>{const b=backStack.pop();if(!b)return;({view,selected,activeTag,activeCategory}=b);$('difficulty').value=b.filters.difficulty;$('premium').value=b.filters.premium;$('search').value=b.query;updateVisual();renderResults();inspect();fitIntent=b.fitIntent;inspectorState.pinned=b.inspector.pinned;setInspector(b.inspector.open);goTransform(b.transform);$('history-back').disabled=!backStack.length;setHash();};
function requestPaint(){if(!raf)raf=requestAnimationFrame(()=>{raf=0;paint();});}
function paint(){
 if(!L||!W||!H)return;const start=performance.now(),dpr=devicePixelRatio||1,colors=Object.fromEntries(['line','topic','category','root','border','text','muted','mint','accent','hollow'].map(k=>[k,palette(k)]));
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
 const a=viewportArea(),details=LeetCodeOptimizedCPU.paint(ctx,L,transform,W,H,colors,selected,related(),visual,{...a,obstacles:labelObstacles()});
 $('zoom-label').textContent=(transform.k*100).toFixed(1)+'%';paintMini();window.LeetCodeAtlas.lastPaint={milliseconds:performance.now()-start,total:L.nodes.length,...details};
}
function paintMini(){
 mc.clearRect(0,0,mini.width,mini.height);
 const k=Math.min((mini.width-12)/(bounds.x1-bounds.x0),(mini.height-12)/(bounds.y1-bounds.y0)),tx=(mini.width-(bounds.x1-bounds.x0)*k)/2,ty=(mini.height-(bounds.y1-bounds.y0)*k)/2;miniTransform={k,x:tx,y:ty};
 for(const n of L.regions)if(n.depth<=2){mc.fillStyle=visual.active&&visual.regions.has(n.key)?'#cfa75e':palette('muted');mc.fillRect(tx+n.rect.x*k,ty+n.y*k,n.width*k,n.height*k);mc.strokeStyle=palette('border');mc.strokeRect(tx+n.rect.x*k,ty+n.y*k,n.width*k,n.height*k);}
 for(const id of visual.solved){const n=L.byKey.get(id);mc.fillStyle='#65e0a0';mc.fillRect(tx+n.x*k,ty+n.y*k,2,2);}
 if(L.byKey.has(selected)){const n=L.byKey.get(selected);mc.strokeStyle=palette('accent');mc.strokeRect(tx+n.rect.x*k,ty+n.y*k,Math.max(2,n.width*k),Math.max(2,n.height*k));}
 const a=viewportArea();mc.strokeStyle=palette('text');mc.strokeRect(tx+(a.x0-transform.x)/transform.k*k,ty+(a.y0-transform.y)/transform.k*k,(a.x1-a.x0)/transform.k*k,(a.y1-a.y0)/transform.k*k);
}
function resize(){const r=$('canvas-container').getBoundingClientRect();W=r.width;H=r.height;canvas.width=Math.round(W*devicePixelRatio);canvas.height=Math.round(H*devicePixelRatio);refit();requestPaint();}
new ResizeObserver(resize).observe($('canvas-container'));
function presentationHit(x,y){
 const indicator=window.LeetCodeAtlas.lastPaint?.progressIndicators?.find(h=>x>=h.box.x0&&x<=h.box.x1&&y>=h.box.y0&&y<=h.box.y1);if(indicator)return L.byKey.get(indicator.key);
 const heading=window.LeetCodeAtlas.lastPaint?.headingLayout?.headings.find(h=>x>=h.box.x0&&x<=h.box.x1&&y>=h.box.y0&&y<=h.box.y1);
 return heading?L.byKey.get(heading.key):LeetCodeOptimizedCPU.hit(L,(x-transform.x)/transform.k,(y-transform.y)/transform.k);
}
canvas.addEventListener('click',event=>{if(event.defaultPrevented)return;const r=canvas.getBoundingClientRect(),n=presentationHit(event.clientX-r.left,event.clientY-r.top);if(n)select(n.key);});
canvas.addEventListener('dblclick',()=>focus(selected,true));
function tooltip(n,x,y){
 const tip=$('problem-tooltip');if(!n){tip.hidden=true;return;}const p=n.data.problem;
 tip.textContent=p?'#'+p.displayNumber+' '+p.title+'\n'+p.difficulty+' · '+(progress.byProblem.get(p.id).state==='solved'?'Solved':'Not yet recorded as solved')+'\n'+(p.topicTags.join(' · ')||'Unclassified / needs review'):n.presentationTitle;tip.hidden=false;
 const r=tip.getBoundingClientRect();tip.style.left=Math.max(8,Math.min(W-r.width-8,x+12))+'px';tip.style.top=Math.max(8,Math.min(H-r.height-8,y+12))+'px';
}
canvas.addEventListener('mousemove',e=>{const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;tooltip(presentationHit(x,y),x,y);});
canvas.addEventListener('mouseleave',()=>{$('problem-tooltip').hidden=true;});
let keyboardProblem=null;
function keyboardTitle(step=0){
 const a=viewportArea(),cx=(a.x0+a.x1)/2,cy=(a.y0+a.y1)/2;
 const candidates=LeetCodeOptimizedCPU.visible(L,{x0:(a.x0-transform.x)/transform.k,y0:(a.y0-transform.y)/transform.k,x1:(a.x1-transform.x)/transform.k,y1:(a.y1-transform.y)/transform.k}).sort((a,b)=>a.y-b.y||a.rect.x-b.rect.x||a.key.localeCompare(b.key));
 if(!candidates.length)return;
 let i=candidates.findIndex(n=>n.key===keyboardProblem);
 if(i<0){let best=Infinity;candidates.forEach((n,j)=>{const d=(n.x*transform.k+transform.x-cx)**2+((n.y+n.height/2)*transform.k+transform.y-cy)**2;if(d<best){best=d;i=j;}});}
 else i=(i+step+candidates.length)%candidates.length;
 const n=candidates[i];keyboardProblem=n.key;canvas.dataset.keyboardProblemId=n.key;
 tooltip(n,n.x*transform.k+transform.x,(n.y+n.height/2)*transform.k+transform.y);
}
canvas.setAttribute('aria-describedby','problem-tooltip');
canvas.setAttribute('aria-label','LeetCode Atlas. Use brackets to browse visible Problem titles; Enter to focus. Arrow keys pan.');
canvas.addEventListener('focus',()=>keyboardTitle());
canvas.addEventListener('blur',()=>{$('problem-tooltip').hidden=true;});

function scaleBy(k){fitIntent=null;d3.select(canvas).call(zoom.scaleBy,k);}
canvas.addEventListener('keydown',e=>{if(e.key==='['||e.key===']'){keyboardTitle(e.key==='['?-1:1);e.preventDefault();return;}if(e.key==='Enter'&&keyboardProblem){select(keyboardProblem);e.preventDefault();return;}if(e.key==='+'||e.key==='='){scaleBy(1.3);e.preventDefault();}if(e.key==='-'){scaleBy(1/1.3);e.preventDefault();}const dir={ArrowLeft:[50,0],ArrowRight:[-50,0],ArrowUp:[0,50],ArrowDown:[0,-50]}[e.key];if(dir){fitIntent=null;goTransform(d3.zoomIdentity.translate(transform.x+dir[0],transform.y+dir[1]).scale(transform.k));e.preventDefault();}});
mini.addEventListener('click',e=>{if(!miniTransform)return;fitIntent=null;const r=mini.getBoundingClientRect(),x=((e.clientX-r.left)*mini.width/r.width-miniTransform.x)/miniTransform.k,y=((e.clientY-r.top)*mini.height/r.height-miniTransform.y)/miniTransform.k;goTransform(d3.zoomIdentity.translate(W/2-x*transform.k,H/2-y*transform.k).scale(transform.k));});
$('search').oninput=()=>{activeTag=null;activeCategory=null;problemLimit=50;renderResults();updateVisual();};
$('search').onkeydown=e=>{if(e.key==='ArrowDown'||e.key==='Enter'){const first=$('search-results').querySelector('button');if(first){e.preventDefault();if(e.key==='Enter')first.click();else first.focus();}}};
function changeFilters(){updateVisual();renderResults();}
for(const id of ['difficulty','premium'])$(id).onchange=changeFilters;
$('reset-filters').onclick=()=>{$('difficulty').value='all';$('premium').value='all';$('search').value='';activeTag=null;activeCategory=null;changeFilters();};
$('fit').onclick=fit;$('fit-subtree').onclick=()=>focus(selected,true,false);$('zoom-in').onclick=()=>scaleBy(1.4);$('zoom-out').onclick=()=>scaleBy(1/1.4);

$('inspector-toggle').onclick=()=>{inspect();setInspector(true);};$('inspector-close').onclick=()=>setInspector(false);
$('inspector-pin').onclick=()=>{inspectorState.pinned=!inspectorState.pinned;setInspector(true);};
$('clear').onclick=()=>{selected=null;activeTag=null;activeCategory=null;updateVisual();inspect();setHash();requestPaint();};
document.addEventListener('keydown',e=>{if(e.key==='Escape'){$('branch-menu').open=false;$('search-results').replaceChildren();setInspector(false);}});
document.addEventListener('click',e=>{if(!$('branch-menu').contains(e.target))$('branch-menu').open=false;if(!$('knowledge-search').contains(e.target))$('search-results').replaceChildren();});
window.LeetCodeAtlas={state:()=>({mode,activeTag,activeCategory,compiled,projection,coverage,visual,relations:related(),index,progress,m,L,view,selected,transform,scenes,filters:filters(),inspectorState:{...inspectorState},layoutBuilds,viewportArea:viewportArea(),bounds,fitIntent}),select,fit,focus,measure,repaint:paint,lastPaint:null};
function surface(next){
 const leetcode=next==='leetcode';$('view-content').hidden=!leetcode;$('hyperskill-reference').hidden=leetcode;
 document.querySelectorAll('#application-nav a').forEach(a=>a.toggleAttribute('aria-current',false));$('nav-'+(leetcode?'leetcode':next==='skill-tree'?'skill-tree':'atlas')).setAttribute('aria-current','page');
 const url=new URL(location.href);url.searchParams.delete('layout');url.searchParams.set('view',next);history.replaceState(null,'',url);
 if(!leetcode){const frame=$('hyperskill-reference'),src='../../../build/pages/knowledge-map/?view='+next;if(frame.dataset.view!==next){frame.dataset.view=next;frame.src=src;}}else resize();
}
// Local shell emulation: accepted Hyperskill pages run in their own frame.
// Only their redundant outer header is hidden in memory; release files and worlds are untouched.
$('hyperskill-reference').onload=()=>{const d=$('hyperskill-reference').contentDocument;if(d?.getElementById('application-header')){d.getElementById('application-header').hidden=true;d.getElementById('application-header').style.display='none';d.getElementById('view-content').style.height='100dvh';}};
document.querySelectorAll('#application-nav a').forEach(a=>a.onclick=e=>{e.preventDefault();surface(a.dataset.surface);});
function restore(){const [,key]=location.hash.slice(1).split('/');view='global';try{selected=key?decodeURIComponent(key):null;}catch{selected='invalid-route';}activeCategory=index.tax.has(selected)&&selected!==M.ROOT?selected:null;layout();resize();if(key){inspect();setInspector(true);focus(selected,index.tax.has(selected));}setHash();}
window.addEventListener('hashchange',restore);restore();surface(new URLSearchParams(location.search).get('view')||'leetcode');document.body.dataset.ready='true';
})().catch(error=>{console.error(error);const p=document.createElement('p');p.className='error';p.textContent='LeetCode Atlas could not load: '+error.message;document.querySelector('main').replaceChildren(p);});
