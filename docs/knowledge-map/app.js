(function(g){
'use strict';
const $=s=>document.querySelector(s),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const CARD={RADIUS:5,TOPIC_RADIUS:3,HEADER_MAIN:8,HEADER_CATEGORY:5,LABEL_X:34,DISCLOSURE_X:15,META_BOTTOM:7,STATUS_X:12,TOPIC_LABEL_X:24,EVIDENCE_RIGHT:10};
let relationIndex,relationProjection=null,focusedRelation=null,previewRelation=null;
let m,L,selected=null,mode='my',collapsed=new Set(),transform=d3.zoomIdentity,coverage={projectKey:null,enabled:false,stageId:null},visible=[],fitIntent=null,viewState='overview',transitioning=false,miniBounds=null,navigationId=0;const metrics={},samples={};
const svg=d3.select('#graph'),scene=svg.append('g'),traySurfaces=scene.append('g').attr('aria-hidden','true'),taxonomy=scene.append('g'),relations=scene.append('g'),nodes=scene.append('g'),evidence=scene.append('g');
const zoom=d3.zoom().scaleExtent([.0001,4]).on('zoom',e=>{transform=e.transform;if(e.sourceEvent){fitIntent=null;viewState=selected?.startsWith('topic:')?'topic':'subtree';}scene.attr('transform',transform);$('#zoom-value').textContent=(transform.k*100).toFixed(transform.k<.1?1:0)+'%';updateOptics();});svg.call(zoom).on('dblclick.zoom',null);
function timed(name,fn){const t=performance.now(),v=fn();metrics[name]=performance.now()-t;(samples[name]??=[]).push(metrics[name]);return v;}
const VIEW={duration:220,topicFont:16,subtreeFont:13,minReadingFont:10,pad:24,maxScale:1.3};
function updateOptics(){
 if(!L)return;
 $('#canvas').dataset.view=viewState;$('#overview-guide').hidden=viewState!=='overview';
 $('#view-status').textContent=viewState==='overview'?'Overview · zoom in to read':viewState==='topic'?'Topic focus':fitIntent?.kind==='project'?'Project coverage overview':transform.k*14<10?'Subtree overview · choose a child to read':'Subtree reading';
 nodes.selectAll('.core').attr('r',Math.min(7,Math.max(4,1.2/transform.k))).style('stroke-width',Math.min(.65,transform.k*6));nodes.selectAll('.ring').attr('r',Math.min(9,Math.max(7,1.8/transform.k))).style('stroke-width',Math.min(.65,transform.k*6));
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
 const majors=m.root.children.filter(n=>n.type==='category');$('#overview-guide').innerHTML=`<span>${esc(m.root.title)}</span><div>${majors.map(n=>`<button data-region="${esc(n.key)}">${esc(n.title)}</button>`).join('')}</div><p>Java → Basics · Code organization · Working with data · Errorless code</p>`;
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
 const node=m.nodes.get(selected),keys=node?new Set(descendants(node).map(n=>n.key)):new Set(),ns=visible.filter(n=>keys.has(n.key));
 const sb=ns.length?AtlasLayout.contentBounds(L,ns):null;mini.select('.mini-selection').attr('width',sb?sb.x1-sb.x0:0).attr('height',sb?sb.y1-sb.y0:0).attr('x',sb?.x0||0).attr('y',sb?.y0||0);
}
function paintMinimapCoverage(){
 if(!miniBounds)return;const required=coverage.enabled?projection().required:new Set(),anc=new Set();for(const key of required){let n=m.nodes.get(key);while(n){anc.add(n.key);n=m.nodes.get('category:'+n.canonical_parent_id);}}
 const mini=d3.select('#minimap');mini.selectAll('.mini-path').classed('covered',e=>e.children.some(k=>anc.has(k)));mini.selectAll('.mini-card').classed('covered',n=>anc.has(n.key));mini.selectAll('.mini-tray').classed('covered',t=>t.topics.some(k=>required.has(k)));
}
function descendants(n){return[n,...n.children.flatMap(descendants)];}
function path(n){const out=[];while(n){out.unshift(n.title);n=m.nodes.get('category:'+n.canonical_parent_id);}return out;}
function listButton(key,title){return `<button data-select="${esc(key)}">${esc(title)}</button>`;}
function list(title,items,open=true){return `<details ${open?'open':''}><summary>${esc(title)} (${items.length})</summary><div class="inspector-list">${items.join('')||'<p>None recorded.</p>'}</div></details>`;}
function provenance(ids){return list('Advanced / Evidence',[...new Set(ids||[])].map(id=>{const e=m.raw.evidence.find(e=>e.id===id);return e?`<p>${esc(id)}<br>${esc(e.method)} · ${esc(e.observed_on)}<br>${esc(e.note)}${e.url?`<br><a href="${esc(e.url)}" target="_blank" rel="noopener">Source</a>`:''}</p>`:'';}),false);}
function projection(){return AtlasModel.coverageProjection(m,new Set(visible.map(n=>n.key)),coverage.projectKey,coverage.stageId);}
function paintCoverage(){timed('project coverage',()=>{
 evidence.selectAll('*').remove();const active=coverage.enabled&&coverage.projectKey;scene.classed('coverage-active',!!active);nodes.selectAll('.node,.disclosure,.topic-tray').classed('covered',false);traySurfaces.selectAll('.tray-surface').classed('covered',false);nodes.selectAll('.node').attr('aria-label',function(){return this.dataset.baseName;});taxonomy.selectAll('path').classed('covered',false);paintMinimapCoverage();if(!active)return;
 const p=projection(),ancestors=new Set();for(const key of p.required){let n=m.nodes.get(key);while(n){ancestors.add(n.key);n=m.nodes.get('category:'+n.canonical_parent_id);}}
 nodes.selectAll('.node,.disclosure').classed('covered',function(){return ancestors.has(this.dataset.key);});nodes.selectAll('.node').filter(function(){return p.required.has(this.dataset.key);}).attr('aria-label',function(){return this.dataset.baseName+'; required by selected project';});taxonomy.selectAll('.taxonomy').classed('covered',e=>e.children.some(key=>ancestors.has(key)));taxonomy.selectAll('.membership').classed('covered',e=>(e.topics||[]).some(key=>p.required.has(key)));traySurfaces.selectAll('.tray-surface').classed('covered',t=>t.topics.some(k=>p.required.has(k)));nodes.selectAll('.topic-tray').classed('covered',function(){return ancestors.has(this.dataset.parent);});
 for(const [key,item] of p.byKey){const n=L.byKey.get(key),group=evidence.append('g').attr('class','evidence').attr('data-key',key).attr('data-count',item.count).attr('transform',`translate(${n.x},${n.y})`);group.append('text').attr('text-anchor','end').attr('x',n.width/2-CARD.EVIDENCE_RIGHT).attr('y',item.kind==='topic'?n.height/2+4:n.height-12).text(item.kind==='topic'?'◇':'◇ '+item.count);}
});}
function measureObstacles(){return visible.map(n=>({x:n.x-n.width/2,y:n.y,w:n.width,h:n.height,key:n.key,kind:'card'}));}
function relationButton(e,type){const key=type==='prerequisite'?e.source:e.target,title=m.nodes.get(key).title;return `<button data-relation="${esc(e.key)}" aria-label="${type==='prerequisite'?'Prerequisite':'Dependent'}: ${esc(title)}" aria-pressed="${focusedRelation?.key===e.key}"><span class="relation-symbol ${type}" aria-hidden="true">${type==='prerequisite'?'○ ←':'● →'}</span> ${esc(title)}</button>`;}
function relationClasses(selection,lookup){
 selection.classed('relation-path',false).classed('relation-prerequisite',false).classed('relation-dependent',false).classed('relation-shared',false).classed('relation-strong',false).classed('relation-muted',false);
 selection.each(function(d){const item=lookup(d,this);if(!item)return;const types=item.focusedTypes.size?item.focusedTypes:item.types;
  d3.select(this).classed('relation-path',true).classed('relation-prerequisite',types.has('prerequisite')).classed('relation-dependent',types.has('dependent')).classed('relation-shared',types.size>1).classed('relation-strong',item.focusedTypes.size>0).classed('relation-muted',!!relationProjection.focused&&!item.focusedTypes.size);
 });
}
function paintRelations(){
 const topic=m.nodes.get(selected)?.type==='topic',active=topic&&relationProjection?.routes.length>0;scene.classed('relations-active',!!active).classed('relation-focused',!!relationProjection?.focused);
 relationClasses(taxonomy.selectAll('.taxonomy'),(e,el)=>active?relationProjection.segments.get(Number(el.dataset.segment)):null);
 relationClasses(nodes.selectAll('.node'),(n,el)=>active?(n.data.type==='topic'?relationProjection.endpoints:relationProjection.categories).get(el.dataset.key):null);
 relationClasses(traySurfaces.selectAll('.tray-surface'),t=>active?relationProjection.trays.get(t.parent):null);
 nodes.selectAll('.relation-endpoint').remove();
 if(active)nodes.selectAll('.node.topic').each(function(n){const item=relationProjection.endpoints.get(n.key);if(!item)return;for(const type of item.types)d3.select(this).append('circle').attr('class','relation-endpoint '+type).attr('aria-hidden','true').attr('cx',n.width/2-(item.types.size>1&&type==='prerequisite'?15:7)).attr('cy',6).attr('r',2.5);});
 nodes.selectAll('.node').attr('aria-label',function(){const item=active?relationProjection.endpoints.get(this.dataset.key):null;return this.dataset.baseName+(coverage.enabled&&this.classList.contains('covered')&&this.classList.contains('topic')?'; required by selected project':'')+(item?'; direct '+[...item.types].join(' and '):'');});
 $('#inspector').querySelectorAll('[data-relation]').forEach(b=>{b.setAttribute('aria-pressed',focusedRelation?.key===b.dataset.relation?'true':'false');b.classList.toggle('relation-preview',relationProjection?.focused?.key===b.dataset.relation);});
 const status=$('#relation-status');if(status){const r=relationProjection?.focused;status.textContent=r?`${focusedRelation?.key===r.key?'Focused':'Preview'}: ${m.nodes.get(r.source).title} → ${m.nodes.get(r.target).title}`:'All direct relations · hover, focus or tap an entry to trace one.';}
 const clear=$('#clear-relation');if(clear)clear.disabled=!focusedRelation;
}
function renderRelations(){timed('taxonomy relation projection',()=>{
 relations.selectAll('*').remove();
 const direct=m.nodes.get(selected)?.type==='topic'?relationIndex.direct(selected):[];
 if(!direct.some(r=>r.key===focusedRelation?.key))focusedRelation=null;
 if(!direct.some(r=>r.key===previewRelation))previewRelation=null;
 relationProjection=relationIndex.project(selected,previewRelation||focusedRelation?.key);paintRelations();
});}
function previewRelationPath(key){timed('relation hover',()=>{previewRelation=key;relationProjection=relationIndex.project(selected,key||focusedRelation?.key);paintRelations();});}
function focusRelation(key){timed('relation focus',()=>{
 const r=relationIndex.direct(selected).find(r=>r.key===key);focusedRelation=r?{key:r.key,sourceTopicId:r.source,targetTopicId:r.target,type:r.type}:null;previewRelation=null;
 relationProjection=relationIndex.project(selected,focusedRelation?.key);paintRelations();
 $('#announcement').textContent=r?`Focused ${r.type}: ${m.nodes.get(r.source).title} → ${m.nodes.get(r.target).title}`:'Showing all direct relations';
});}
function inspect(){let html='',n=m.nodes.get(selected);if(!selected){const course=m.raw.courses[0],topics=[...m.nodes.values()].filter(n=>n.type==='topic');html=`<p>Course</p><h2>${esc(course.title)}</h2><p class="stat">${topics.length} topics</p><p>${topics.filter(n=>n.is_learned).length} learned · ${topics.filter(n=>n.is_verified).length} verified</p><h3>Project Evidence</h3><div class="inspector-list">${m.raw.projects.filter(p=>m.raw.progress.projects.some(v=>v.project_id===p.id)).map(p=>listButton('project:'+p.id,'◇ '+p.title)).join('')}</div>${list('Course project catalogue',m.raw.projects.filter(p=>!m.raw.progress.projects.some(v=>v.project_id===p.id)).map(p=>listButton('project:'+p.id,'◇ '+p.title)),false)}<p class="legend">● Learned · ◎ Verified<br>○ Not learned · ◌ Unknown<br>◇ Project evidence / requirement<br>Slate branches: taxonomy<br>○ Violet paths: prerequisites<br>● Mint paths: dependents</p><p>Complete taxonomy. Zoom in to read; select to inspect.</p>`;}
else if(n){html=`<h2>${esc(n.title)}</h2><p class="path">${path(n).map(esc).join(' &gt; ')}</p>`;if(n.type==='category'){const ts=descendants(n).filter(n=>n.type==='topic'),cats=n.children.filter(n=>n.type==='category');html+=`<p>${cats.length} child categories<br>${n.children.filter(n=>n.type==='topic').length} direct topics<br>${ts.length} descendant topics<br>${ts.filter(n=>n.is_learned).length} learned · ${ts.filter(n=>n.is_verified).length} verified<br>${ts.filter(n=>m.raw.courses[0].topic_ids.includes(n.id)).length} course topics</p>`;if(coverage.enabled)html+=`<p>◇ ${ts.filter(t=>projection().required.has(t.key)).length} required topics in this subtree</p>`;html+=`<div class="actions"><button id="focus-subtree">Focus subtree</button></div>`+list('Child Categories',cats.map(c=>listButton(c.key,c.title)))+provenance(n.evidence_ids);}
else{const edges=m.connections.filter(e=>e.source===n.key||e.target===n.key),req=m.raw.edges.filter(e=>e.type==='project_requires'&&e.target===n.key);html+=`<p>${n.is_learned===true?'● Learned':n.is_learned===false?'○ Not learned':'◌ Unknown'}${n.is_verified?' · ◎ Verified':''}<br>Verification: ${n.observations.map(o=>esc(o.verification_status)).join(', ')||'unknown'}</p>`+list('Prerequisites',edges.filter(e=>e.target===n.key).map(e=>relationButton(e,'prerequisite')))+list('Dependents',edges.filter(e=>e.source===n.key).map(e=>relationButton(e,'dependent')))+`<p class="relation-legend"><span class="prerequisite">○ Prerequisite</span> · <span class="dependent">● Dependent</span><br>Taxonomy paths are visual routes; the relation remains Topic → Topic.</p><p id="relation-status" role="status"></p><div class="actions"><button id="clear-relation">Show all relations</button></div>`+list('Project Evidence',req.map(e=>{const p=m.raw.projects.find(p=>'project:'+p.id===e.source),s=m.raw.stages.find(s=>s.id===e.stage_id);return listButton(e.source,p.title)+`<p>Required by project${s?' · Stage '+s.position+' — '+esc(s.title):''}</p>`;}))+`<p><a href="${esc(n.url)}" target="_blank" rel="noopener">Open in Hyperskill ↗</a></p>`+list('Additional taxonomy memberships',m.raw.edges.filter(e=>e.type==='hierarchy'&&e.target===n.key&&e.source!=='category:'+n.canonical_parent_id).map(e=>listButton(e.source,m.nodes.get(e.source).title)),false)+provenance([...n.evidence_ids,...n.observations.flatMap(o=>o.evidence_ids),...edges.flatMap(e=>e.evidence.flatMap(v=>v.evidence_ids)),...req.flatMap(e=>e.evidence_ids)]);}}
else{const p=m.raw.projects.find(p=>'project:'+p.id===selected),pr=m.raw.progress.projects.find(v=>v.project_id===p.id),ss=m.raw.stages.filter(s=>s.project_id===p.id).sort((a,b)=>a.position-b.position),req=AtlasModel.projectRequirements(m,selected),known=ss.length>0||m.raw.indexes.projects[String(p.id)].requirements_loaded,completed=pr?.completed_stage_ids;html=`<h2>${esc(p.title)}</h2><p>Status: ${esc(pr?.status||'available')}<br>Stage count: ${p.stage_ids.length}<br>Required topic count: ${known?req.size:'unknown'}<br>Completed stage state: ${completed==null?'unknown':completed.length?completed.map(esc).join(', '):'[] — no completed stages recorded'}</p>${p.description?`<p>${esc(p.description)}</p>`:''}`;if(known){html+=`<div class="actions"><button id="coverage" aria-pressed="${coverage.enabled}">${coverage.enabled?'Hide':'Show'} project coverage</button><button id="fit-coverage">Fit project coverage</button>${[...req].some(key=>!visible.some(n=>n.key===key))?'<button id="reveal">Reveal required topics</button>':''}</div><h3>Stages · explicit new requirements</h3><div class="actions"><button data-stage="all" aria-pressed="${coverage.stageId==null}">All project requirements (${req.size})</button>${ss.map(s=>`<button data-stage="${s.id}" aria-pressed="${coverage.stageId===s.id}">Stage ${s.position} · ${esc(s.title)} (${AtlasModel.projectRequirements(m,selected,s.id).size})</button>`).join('')}</div>`+list('Required Topics',[...req].map(key=>listButton(key,m.nodes.get(key).title)),false);}else html+='<p>Stage requirements have not been loaded.</p>';html+=`<p><a href="${esc(p.url)}" target="_blank" rel="noopener">Open in Hyperskill ↗</a></p>`+provenance(p.evidence_ids);}
document.querySelector('aside').classList.toggle('has-selection',!!selected);document.querySelector('aside').classList.toggle('project-focus',!!(coverage.enabled&&coverage.projectKey));$('#inspector').innerHTML=html;$('#inspector').querySelectorAll('[data-select]').forEach(b=>b.onclick=()=>select(b.dataset.select,true));$('#inspector').querySelectorAll('[data-relation]').forEach(b=>{b.onmouseenter=()=>previewRelationPath(b.dataset.relation);b.onmouseleave=()=>previewRelationPath(document.activeElement?.dataset.relation||null);b.onfocus=()=>previewRelationPath(b.dataset.relation);b.onblur=()=>previewRelationPath(null);b.onclick=()=>focusRelation(b.dataset.relation);b.onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();focusRelation(null);}};});$('#clear-relation')?.addEventListener('click',()=>focusRelation(null));paintRelations();$('#coverage')?.addEventListener('click',()=>{coverage.enabled=!coverage.enabled;paintCoverage();paintRelations();inspect();});$('#fit-coverage')?.addEventListener('click',fitProject);$('#focus-subtree')?.addEventListener('click',()=>fitSubtree(selected));$('#reveal')?.addEventListener('click',()=>{for(const key of AtlasModel.projectRequirements(m,selected))reveal(key);draw();});$('#inspector').querySelectorAll('[data-stage]').forEach(b=>b.onclick=()=>{coverage.stageId=b.dataset.stage==='all'?null:Number(b.dataset.stage);coverage.enabled=true;paintCoverage();inspect();});}
function draw(){
 visible=AtlasLayout.visible(L,m,collapsed);const keys=new Set(visible.map(n=>n.key)),neighbors=new Set(m.connections.filter(e=>e.source===selected||e.target===selected).flatMap(e=>[e.source,e.target]));taxonomy.selectAll('*').remove();
 const context=new Set();let chosen=m.nodes.get(selected);if(chosen?.type==='category')while(chosen){context.add(chosen.key);chosen=m.nodes.get('category:'+chosen.canonical_parent_id);}
 for(const e of L.connectorSegments.filter(e=>keys.has(e.parent)&&e.children.some(key=>keys.has(key))))taxonomy.append('path').datum(e).attr('class','taxonomy depth-'+e.depth+(e.children.some(key=>context.has(key))?' context':'' )).attr('data-segment',L.connectorSegments.indexOf(e)).attr('data-children',e.children.join(' ')).attr('d',e.d);
 for(const e of L.buses.filter(e=>keys.has(e.parent)&&!collapsed.has(e.parent)&&(!e.topic||keys.has(e.topic))))taxonomy.append('path').attr('class','membership').attr('data-parent',e.parent).datum(e).attr('d',e.d);
 nodes.selectAll('*').remove();traySurfaces.selectAll('*').remove();const trayGroups=new Map();for(const t of L.trays.filter(t=>keys.has(t.parent)&&t.topics.some(k=>keys.has(k)))){traySurfaces.append('rect').datum(t).attr('class','tray-surface').attr('data-parent',t.parent).attr('x',t.x).attr('y',t.y).attr('width',t.width).attr('height',t.height).attr('rx',4);trayGroups.set(t.parent,nodes.append('g').attr('class','topic-tray').attr('data-parent',t.parent).attr('role','presentation'));}for(const n of visible){const d=n.data,isTopic=d.type==='topic',baseName=d.title+'; '+d.type+'; '+path(d).join(' > ')+(isTopic?'; '+(d.is_learned?'learned':d.is_learned===false?'not learned':'unknown')+(d.is_verified?'; verified':''):''),group=(isTopic?trayGroups.get(n.parent):nodes).append('g').datum(n).attr('class',`node ${d.type} depth-${n.depth} ${d.is_learned?'learned':d.is_learned==null?'unknown':''} ${selected===d.key?'selected':''} ${neighbors.has(d.key)?'neighbor':''}`).attr('data-key',d.key).attr('data-x',n.x).attr('data-y',n.y).attr('data-base-name',baseName).attr('transform',`translate(${n.x},${n.y})`).attr('tabindex',0).attr('role','button').attr('aria-pressed',selected===d.key).attr('aria-label',baseName);
 group.on('click',e=>{e.stopPropagation();select(d.key,isTopic);}).on('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(d.key,isTopic);}});
 group.append('rect').attr('class','card').attr('x',-n.width/2).attr('y',0).attr('width',n.width).attr('height',n.height).attr('rx',isTopic?CARD.TOPIC_RADIUS:CARD.RADIUS);if(isTopic)group.append('title').text(d.title);
 if(isTopic){group.append('circle').attr('class','core').attr('cx',-n.width/2+CARD.STATUS_X).attr('cy',n.height/2).attr('r',4);if(d.is_verified)group.append('circle').attr('class','ring').attr('cx',-n.width/2+CARD.STATUS_X).attr('cy',n.height/2).attr('r',7);}
 const tx=-n.width/2+(isTopic?CARD.TOPIC_LABEL_X:CARD.LABEL_X),ty=isTopic?n.height/2-(n.lines.length-1)*n.line/2+n.font*.35:(n.depth>=2?CARD.HEADER_CATEGORY:CARD.HEADER_MAIN)+n.font,label=group.append('text').attr('class','label').attr('x',tx).attr('y',ty).style('font-size',n.font+'px');n.lines.forEach((l,i)=>label.append('tspan').attr('x',tx).attr('dy',i?n.line:0).text(l));
 if(!isTopic){const ts=descendants(d).filter(t=>t.type==='topic');group.append('text').attr('class','category-coverage').attr('x',tx).attr('y',n.height-CARD.META_BOTTOM).text(ts.filter(t=>t.is_learned).length+' / '+ts.length+' learned');if(d.children.length){const disclosure=nodes.append('g').attr('class','disclosure').attr('data-key',d.key).attr('transform',`translate(${n.x-n.width/2+CARD.DISCLOSURE_X},${n.y+n.height/2})`).attr('tabindex',0).attr('role','button').attr('aria-label',(collapsed.has(d.key)?'Expand ':'Collapse ')+d.title).attr('aria-expanded',!collapsed.has(d.key)).on('click',e=>{e.stopPropagation();toggle(d.key);}).on('keydown',e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();toggle(d.key);}});disclosure.append('rect').attr('x',-13).attr('y',-16).attr('width',26).attr('height',32).attr('rx',3).attr('fill','transparent');disclosure.append('text').attr('text-anchor','middle').attr('y',5).text(collapsed.has(d.key)?'▸':'▾');}}
 }
 $('#canvas').classList.toggle('roadmap',mode==='roadmap');paintCoverage();renderRelations();inspect();updateOptics();}
function reveal(key){let n=m.nodes.get(key);while(n){collapsed.delete(n.key);n=m.nodes.get('category:'+n.canonical_parent_id);}}
function select(key,navigate=false){
 const n=m.nodes.get(key),reading=n?.type==='topic'||navigate&&n;
 const restoreFocus=document.activeElement?.classList.contains('node');timed('topic selection',()=>{
  if(key.startsWith('project:'))coverage={projectKey:key,enabled:AtlasModel.projectRequirements(m,key).size>0,stageId:null};
  if(selected!==key){focusedRelation=null;previewRelation=null;}selected=key;if(n?.type==='category'&&!reading&&viewState!=='overview')viewState='subtree';if(reading){reveal(key);viewState=n.type==='topic'?'topic':'subtree';}draw();
  if(restoreFocus)nodes.selectAll('.node').filter(function(){return this.dataset.key===key;}).node()?.focus({preventScroll:true});
  if(reading){if(n.type==='topic')focusTopic(key);else fitSubtree(key);}
  $('#announcement').textContent=(reading?(n.type==='topic'?'Topic focus: ':'Subtree view: '):'Selected ')+(n?.title||m.raw.projects.find(p=>'project:'+p.id===key)?.title);
 });
}
function focusTopic(key,animate=true){timed('Topic focus',()=>{
 viewState='topic';updateOptics();const n=L.byKey.get(key),area=viewportArea(),k=Math.min(VIEW.topicFont/n.font,area.width/(n.width+16),area.height/(n.height+16));
 const b={x0:n.x-n.width/2,x1:n.x+n.width/2,y0:n.y,y1:n.y+n.height};navigateCamera(centerBounds(b,k,area),{kind:'topic',key},animate);
});}
function toggle(key){const focus=document.activeElement?.classList.contains('disclosure');collapsed.has(key)?collapsed.delete(key):collapsed.add(key);draw();if(focus)nodes.selectAll('.disclosure').filter(function(){return this.dataset.key===key;}).node()?.focus();}
function fit(keys,animate=true,kind=keys?'project':'overview'){
 timed(kind==='overview'?'Fit all':kind==='subtree'?'Fit subtree':'Project fit',()=>{
  const ns=visible.filter(n=>!keys||keys.has(n.key));if(!ns.length)return;viewState=kind==='overview'?'overview':'subtree';updateOptics();
  const b=AtlasLayout.contentBounds(L,ns),area=viewportArea(),fullScale=Math.min(VIEW.maxScale,area.width/(b.x1-b.x0),area.height/(b.y1-b.y0));
  let k=Math.min(fullScale,kind==='subtree'?VIEW.subtreeFont/14:VIEW.maxScale),targetBounds=b;
  // Mobile keeps the whole landscape rendered and reads a local window into a wide subtree.
  if(kind==='subtree'&&innerWidth<=700&&k*14<VIEW.minReadingFont){
   k=VIEW.subtreeFont/14;const n=L.byKey.get(selected)||ns[0],tray=L.trays.find(t=>t.parent===n.key),child=ns.find(v=>v.data.type==='category'&&v.depth===n.depth+1);
   const readingTray=tray||L.trays.find(t=>keys?.has(t.parent));
   const target=readingTray?{x:readingTray.x+readingTray.width/2,y:readingTray.y+readingTray.height/2}:child?{x:child.x,y:child.y+child.height/2}:{x:n.x,y:n.y+n.height/2};
   if(readingTray){const parent=L.byKey.get(readingTray.parent);targetBounds={x0:Math.min(parent.x-parent.width/2,readingTray.x),x1:Math.max(parent.x+parent.width/2,readingTray.x+readingTray.width),y0:parent.y,y1:readingTray.y+readingTray.height};}
   else targetBounds={x0:target.x,x1:target.x,y0:target.y,y1:target.y};
  }
  navigateCamera(centerBounds(targetBounds,k,area),{kind,keys:keys?new Set(keys):null},animate);
 });
}
function fitSubtree(key=selected,animate=true){const n=m.nodes.get(key);if(!n)return fit(null,animate);fit(new Set(descendants(n).map(n=>n.key)),animate,'subtree');}
function fitProject(animate=true){
 const keys=new Set(projection().byKey.keys()),shown=new Set(visible.map(n=>n.key));
 for(const t of L.trays)if(t.topics.some(k=>keys.has(k)&&shown.has(k))){keys.add(t.parent);t.topics.filter(k=>shown.has(k)).forEach(k=>keys.add(k));}
 fit(keys,animate,'project');
}
function refitIntent(){if(!fitIntent)return;const i=fitIntent;if(i.kind==='topic')focusTopic(i.key,false);else fit(i.keys,false,i.kind);}
function setMode(v){mode=v;$('#my').setAttribute('aria-pressed',v==='my');$('#roadmap').setAttribute('aria-pressed',v==='roadmap');const ts=m.raw.topics,learned=[...m.nodes.values()].filter(n=>n.type==='topic'&&n.is_learned).length,verified=[...m.nodes.values()].filter(n=>n.type==='topic'&&n.is_verified).length;$('#mode-summary').textContent=`${v==='my'?'My Knowledge':'Course Roadmap'} · ${ts.length} topics · ${learned} learned · ${v==='my'?verified+' verified':(ts.length-learned)+' to learn'}`;$('#canvas').classList.toggle('roadmap',v==='roadmap');}
async function init(){document.body.classList.toggle('mini-cards',new URLSearchParams(location.search).get('items')==='mini');const text=await(await fetch('model.json')).text();let raw;m=timed('model parse',()=>{raw=JSON.parse(text);return AtlasModel.model(raw);});const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font=AtlasLayout.FONT;const measure=(t,font=14,weight=400)=>{ctx.font=weight+' '+font+'px system-ui';return ctx.measureText(t).width;};let checkpoint=null;const response=await fetch('layout-checkpoint.json');if(response.ok){checkpoint=await response.json();}L=timed('layout',()=>AtlasLayout.build(m,measure,checkpoint));relationIndex=AtlasRelations.create(m,L);metrics['tray packing']=L.trayPackingMilliseconds;(samples['tray packing']??=[]).push(L.trayPackingMilliseconds);$('#counts').textContent=`${raw.topics.length} topics · ${raw.categories.length} categories · ${m.connections.length} knowledge relations`;setMode('my');buildOverviewGuide();buildMinimap();timed('initial render',draw);fit(null,false);$('#my').onclick=()=>setMode('my');$('#roadmap').onclick=()=>setMode('roadmap');$('#fit').onclick=()=>fit();$('#fit-subtree').onclick=()=>fitSubtree();$('#in').onclick=()=>{fitIntent=null;viewState=selected?.startsWith('topic:')?'topic':'subtree';svg.interrupt();svg.call(zoom.scaleBy,1.4);};$('#out').onclick=()=>{fitIntent=null;viewState=selected?.startsWith('topic:')?'topic':'subtree';svg.interrupt();svg.call(zoom.scaleBy,1/1.4);};$('#theme').onclick=()=>document.body.classList.toggle('light');$('#clear').onclick=()=>{selected=null;coverage={projectKey:null,enabled:false,stageId:null};draw();};$('#search').oninput=()=>timed('search',()=>{const q=$('#search').value.trim().toLowerCase(),all=[...m.nodes.values(),...m.raw.projects.map(p=>({...p,key:'project:'+p.id}))],matches=q?all.filter(n=>n.title.toLowerCase().includes(q)).sort((a,b)=>(a.title.toLowerCase()===q?-1:0)-(b.title.toLowerCase()===q?-1:0)||a.id-b.id).slice(0,12):[];$('#results').innerHTML=matches.map(n=>listButton(n.key,n.title)).join('')||(q?'<p>No matching knowledge.</p>':'');$('#results').querySelectorAll('button').forEach(b=>b.onclick=()=>{timed('Search navigation',()=>select(b.dataset.select,true));$('#results').replaceChildren();});});$('#search').onkeydown=e=>{if(e.key==='Enter')$('#results button')?.click();if(e.key==='ArrowDown'){e.preventDefault();$('#results button')?.focus();}if(e.key==='Escape')$('#results').replaceChildren();};let first=true;new ResizeObserver(()=>{if(first){first=false;return;}refitIntent();}).observe($('#canvas'));
 g.AtlasV6={setCoverage:(enabled)=>{coverage.enabled=enabled;paintCoverage();paintRelations();inspect();},state:()=>({m,L,selected,mode,collapsed,transform,coverage,metrics,samples,visible,viewState,transitioning,fitIntent,focusedRelation,previewRelation,relationProjection,relationIndex}),focusRelation,previewRelationPath,select,toggle,fit,fitSubtree,fitProject,focusTopic,setMode,projection,measure,draw};}
init().catch(e=>{$('#error').textContent='Could not load prototype: '+e.message;console.error(e);});
})(globalThis);
