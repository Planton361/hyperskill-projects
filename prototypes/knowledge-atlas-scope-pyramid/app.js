(function(g){
'use strict';
const $=s=>document.querySelector(s),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const svg=d3.select('#graph'),world=d3.select('#world'),ctx=document.createElement('canvas').getContext('2d');
const measure=(t,font=14,weight=400)=>{ctx.font=`${weight} ${font}px system-ui`;return ctx.measureText(t).width;};
let catalog,index,scopes,ux,nav,scope,m,L,projection,selected,mini,transform=d3.zoomIdentity,layoutMs,busy=false,builds=0,job=0,worker,pending,cameraIntent=null;
const cache=new Map(),inspectorState={open:false,pinned:false};
const zoom=d3.zoom().scaleExtent([.02,4]).on('zoom',e=>{if(e.sourceEvent)cameraIntent=null;transform=e.transform;world.attr('transform',transform);$('#zoom-value').textContent=Math.round(transform.k*100)+'%';updateMini();});svg.call(zoom).on('dblclick.zoom',null);
function bounds(){const p=L.plans.get(m.root.key);return{x0:p.left-8,y0:-8,x1:p.right+8,y1:p.height+8};}
function camera(b,max=1.3){const r=$('#graph').getBoundingClientRect(),available={x:24,y:62,w:Math.max(1,r.width-48-(inspectorState.open&&!inspectorState.pinned?$('#inspector-drawer').getBoundingClientRect().width+22:0)),h:r.height-112},k=Math.min(max,available.w/(b.x1-b.x0),available.h/(b.y1-b.y0));svg.call(zoom.transform,d3.zoomIdentity.translate(available.x+available.w/2-(b.x0+b.x1)/2*k,available.y+available.h/2-(b.y0+b.y1)/2*k).scale(k));}
function fit(){if(!L)return;cameraIntent={kind:'fit'};camera(bounds());$('#status').textContent=`Fit All · ${(14*transform.k).toFixed(1)} px Topic text`;}
function focusTopic(key=selected){const n=L?.byKey.get(key);if(n?.data.type!=='topic')return;select(key);cameraIntent={kind:'topic',key};camera({x0:n.x-n.width/2-30,x1:n.x+n.width/2+30,y0:n.y-36,y1:n.y+n.height+36},16/14);$('#status').textContent='Topic Focus · full title';}
function fitSubtree(key=selected||m?.root.key){if(!L)return;let n=L.byKey.get(key);if(n?.data.type==='topic')n=L.byKey.get(n.parent);if(n){cameraIntent={kind:'subtree',key:n.key};camera(n.subtreeBounds);$('#status').textContent='Fit subtree · '+n.data.title;}}
function ancestors(n){const a=[];while(n){a.unshift(n);n=m.parent(n);}return a;}
function categoryStats(id){return nav.course_id?(ux.categoryProgress(nav.course_id).get(id)||{eligible_count:0,learned:0,verified:0,unknown_learned:0,unknown_verified:0,fully_learned:false,fully_verified:false}):null;}
function topicClasses(id){const s=ux.topic(id);return[s.learned===true?'learned':s.learned===false?'not-learned':'unknown',s.verified===true?'verified':''].join(' ');}
function categoryClasses(id){const p=categoryStats(id);return[p?.fully_learned?'course-complete':'',p?.fully_verified?'course-verified':''].join(' ');}
function coverageLabel(n){const p=n.data.type==='category'?categoryStats(n.data.id):null;return p?`${p.learned} / ${p.eligible_count} learned`:`${n.data.taxonomyTopicKeys.length} Topics · ${n.data.type==='context'?'view':n.data.scopeRole}`;}
function accessibleTitle(n){if(n.data.type==='topic'){const p=ux.topic(n.data.id);return`${n.data.title}; Topic ${n.data.id}; ${p.learned===true?'Learned':p.learned===false?'Not learned':'Learning unknown'}; ${p.verified===true?'Verified':p.verified===false?'Not verified':'Verification unknown'}`;}const p=n.data.type==='category'?categoryStats(n.data.id):null;return p?`${n.data.title}; ${p.learned} / ${p.eligible_count} learned within Course ${nav.course_id}; ${p.verified} / ${p.eligible_count} verified within this Course${p.fully_learned?'; Fully learned within this Course':''}`:n.data.title;}
function setInspector(open,pinned=inspectorState.pinned){inspectorState.open=open;inspectorState.pinned=pinned;const main=$('main');main.dataset.inspectorOpen=String(open);main.dataset.inspectorPinned=String(pinned);$('#inspector-drawer').hidden=!open;$('#inspector-toggle').setAttribute('aria-expanded',String(open));$('#inspector-pin').setAttribute('aria-pressed',String(pinned));$('#inspector-pin').textContent=pinned?'Unpin':'Pin';refitCamera();updateMini();}
function refitCamera(){
 if(!L)return;if(!cameraIntent){keepSelectedVisible();return;}
 if(cameraIntent.kind==='fit'){camera(bounds());$('#status').textContent=`Fit All · ${(14*transform.k).toFixed(1)} px Topic text`;return;}
 const n=L.byKey.get(cameraIntent.key);if(!n)return;
 if(cameraIntent.kind==='topic')camera({x0:n.x-n.width/2-30,x1:n.x+n.width/2+30,y0:n.y-36,y1:n.y+n.height+36},16/14);else camera(n.subtreeBounds);
}
function keepSelectedVisible(){
 const n=L?.byKey.get(selected);if(!n||!inspectorState.open)return;
 const r=$('#graph').getBoundingClientRect(),overlay=!inspectorState.pinned?$('#inspector-drawer').getBoundingClientRect().width+22:0,w=Math.max(1,r.width-48-overlay),h=r.height-112;
 const x=(n.x-n.width/2)*transform.k+transform.x,y=n.y*transform.k+transform.y,nw=n.width*transform.k,nh=n.height*transform.k;
 const shift=(lo,size,start,space)=>size>space?start+space/2-(lo+size/2):lo<start?start-lo:lo+size>start+space?start+space-lo-size:0;
 const dx=shift(x,nw,24,w),dy=shift(y,nh,62,h);if(dx||dy)svg.call(zoom.transform,d3.zoomIdentity.translate(transform.x+dx,transform.y+dy).scale(transform.k));
}
function paintSelection(){world.selectAll('.node').classed('selected',d=>d.key===selected).attr('aria-pressed',d=>String(d.key===selected));const chain=new Set(ancestors(m?.nodes.get(selected)).map(a=>a.key));world.selectAll('.taxonomy').classed('selected-path',d=>chain.has(d.parent)&&d.children.some(k=>chain.has(k)));}
function select(key){if(!m?.nodes.has(key))return;selected=key;$('#graph').setAttribute('aria-label',accessibleTitle(L.byKey.get(key)));paintSelection();inspect();setInspector(true);}
function viewLabel(){return scope?`${scope.title}; ${scope.scope_type} ${scope.scope_id} pyramid`:'Knowledge Atlas; no scope selected';}
function clearEntity(){selected=null;$('#graph').setAttribute('aria-label',viewLabel());paintSelection();if(inspectorState.open)inspect();}
const stateText=(v,positive,negative)=>v===true?positive:v===false?negative:'Unknown';
function relationLink(id){const key=ux.entities.has('topic:'+id)?'topic:'+id:ux.entities.has('category:'+id)?'category:'+id:null;if(!key)return`<p>Native ID ${esc(id)} · Outside captured Global Catalog</p>`;const entity=ux.entities.get(key);return m.nodes.has(key)?`<button class="path-button" data-key="${key}">${esc(entity.title)} · ${key}</button>`:`<a class="relation-global" href="global.html?key=${encodeURIComponent(key)}" target="_blank" rel="noopener">${esc(entity.title)} · ${key} ↗ Global</a>`;}
function nativeRelations(n){return ['prerequisites','followers'].map(field=>`<details><summary>Native Topic ${field}</summary>${!Object.hasOwn(n,field)?'<p>Not established</p>':n[field].length?n[field].map(relationLink).join(''):'<p>Explicit empty set</p>'}</details>`).join('');}
function contextHtml(){return[['course',nav.course_id],['project',nav.project_id],['stage',nav.stage_id]].filter(([,id])=>id).map(([type,id])=>{const s=ux[type+'s'].get(id);return`<button class="path-button" data-context="${type}">${type[0].toUpperCase()+type.slice(1)} ${id} · ${esc(s.title)}</button>`;}).join(' → ');}
function inspect(){
 if(!scope){$('#inspector').innerHTML='<h2>No scope selected</h2><p>Select a Course or Project to inspect its evidenced knowledge.</p>';return;}
 const n=m?.nodes.get(selected)||m?.root;
 if(!n){$('#inspector').innerHTML=`<h2>${esc(scope.title)}</h2><p>${contextHtml()}</p>`+ProgressPresentation.scope(ux.analytics,scope);bindInspector();return;}
 const s=n.type==='topic'?ux.topic(n.id):null,exact=n.type!=='context';
 const role=n.type==='context'?'Presentation only':n.scopeRole==='context'?'Context Category':scope.scope_type==='course'?'Course membership':scope.scope_type==='stage'?'Stage-local requirement':'Project study-plan requirement';
 let html=`<h2>${esc(n.title)}</h2><p>${esc(n.type[0].toUpperCase()+n.type.slice(1))} · ${esc(n.key)}</p><div><span class="badge">${role}</span>${s?.learned===true?'<span class="badge personal">Learned</span>':''}${s?.verified===true?'<span class="badge personal">Verified</span>':''}</div><details open><summary>Scope context</summary><p>${contextHtml()}</p></details>`;
 if(s)html+=ProgressPresentation.topic(ux.analytics,n.id);
 if(n.type==='category')html+=ProgressPresentation.category(ux.analytics,n.id,scope);
 if(n.type==='context')html+=ProgressPresentation.scope(ux.analytics,scope);
 html+=`<details open><summary>Taxonomy path</summary><p class="path">${ancestors(n).map(a=>`<button class="path-button" data-key="${a.key}">${esc(a.title)}</button>`).join(' → ')}</p></details>`;
 if(exact)html+=`<a id="global-link" target="_blank" rel="noopener" href="global.html?key=${encodeURIComponent(ScopeProjection.globalTarget(projection,n.key))}">Show in Global ↗</a><details><summary>Structural memberships</summary>${n.memberships.map(k=>`<button class="path-button" data-key="${k}">${esc(m.nodes.get(k)?.title||k)}</button>`).join('')||'<p>Global root</p>'}</details>`;
 if(n.type==='topic')html+=nativeRelations(n);
 if(n.type==='category')html+=`<details><summary>Topics in this scope (${n.taxonomyTopicKeys.length})</summary>${n.taxonomyTopicKeys.map(k=>`<button class="path-button" data-key="${k}">${esc(m.nodes.get(k).title)}</button>`).join('')}</details>`;
 html+=`<div class="actions"><button id="read-selected">${n.type==='topic'?'Topic Focus':'Fit subtree'}</button></div>`;$('#inspector').innerHTML=html;bindInspector();$('#read-selected').onclick=()=>n.type==='topic'?focusTopic(n.key):fitSubtree(n.key);
}
function bindInspector(){$('#inspector').querySelectorAll('[data-progress-category]').forEach(b=>b.onclick=()=>{const key='category:'+b.dataset.progressCategory;if(m?.nodes.has(key))select(key);else window.parent.AtlasShell.showGlobal(key);});$('#inspector').querySelectorAll('[data-key]').forEach(b=>b.onclick=()=>select(b.dataset.key));$('#inspector').querySelectorAll('[data-context]').forEach(b=>b.onclick=()=>{const type=b.dataset.context;return navigate({...nav,...(type==='course'?{project_id:null,stage_id:null}:type==='project'?{stage_id:null}:{})});});}
function render(){world.selectAll('*').remove();
 world.append('g').selectAll('path').data(L.connectorSegments).join('path').attr('class',d=>'taxonomy depth-'+d.depth).attr('d',d=>d.d);
 world.append('g').selectAll('rect').data(L.trays).join('rect').attr('class','tray-surface').attr('x',d=>d.x).attr('y',d=>d.y).attr('width',d=>d.width).attr('height',d=>d.height).attr('rx',4);
 const nodes=world.append('g').selectAll('g').data(L.nodes).join('g').attr('class',n=>`node ${n.data.type} depth-${n.depth} ${n.data.scopeRole==='context'?'context-category':''} ${n.data.type==='topic'?topicClasses(n.data.id):categoryClasses(n.data.id)}`).attr('data-key',n=>n.key).attr('transform',n=>`translate(${n.x-n.width/2},${n.y})`).attr('tabindex',0).attr('role','button').attr('aria-label',n=>accessibleTitle(n)).on('click',(_,n)=>select(n.key)).on('dblclick',(_,n)=>n.data.type==='topic'?focusTopic(n.key):fitSubtree(n.key)).on('keydown',(e,n)=>{if(e.key==='Enter'){e.preventDefault();select(n.key);}if(e.key===' '){e.preventDefault();n.data.type==='topic'?focusTopic(n.key):fitSubtree(n.key);}});
 nodes.append('rect').attr('class','card').attr('width',n=>n.width).attr('height',n=>n.height).attr('rx',n=>n.data.type==='topic'?3:5);
 nodes.filter(n=>n.data.scopeRole==='explicit').append('rect').attr('class','scope-stripe').attr('x',0).attr('y',5).attr('width',2).attr('height',n=>n.height-10);
 nodes.append('title').text(accessibleTitle);
 nodes.filter(n=>n.data.type==='category'&&categoryStats(n.data.id)?.fully_learned).append('path').attr('class','completion-check').attr('d','M 7 13 L 10 16 L 16 9');
 nodes.each(function(n){const group=d3.select(this),topic=n.data.type==='topic';if(topic){group.append('circle').attr('class','core').attr('cx',12).attr('cy',n.height/2).attr('r',3.5);if(ux.topic(n.data.id).verified===true)group.append('circle').attr('class','ring').attr('cx',12).attr('cy',n.height/2).attr('r',6);}
  group.selectAll('text.label').data(n.lines).join('text').attr('class','label').attr('x',topic?24:22).attr('y',(_,i)=>(topic?6:8)+n.font+i*n.line).style('font-size',n.font+'px').text(s=>s);
  if(!topic)group.append('text').attr('class','category-coverage').attr('x',22).attr('y',n.height-7).text(coverageLabel(n));
 });
 const b=bounds(),k=Math.min(172/(b.x1-b.x0),104/(b.y1-b.y0));mini={k,x:90-(b.x0+b.x1)/2*k,y:56-(b.y0+b.y1)/2*k};const mm=d3.select('#minimap');mm.selectAll('*').remove();mm.selectAll('rect').data(L.nodes).join('rect').attr('x',n=>mini.x+(n.x-n.width/2)*k).attr('y',n=>mini.y+n.y*k).attr('width',n=>Math.max(1,n.width*k)).attr('height',n=>Math.max(1,n.height*k));mm.append('rect').attr('class','mini-viewport');
}
function updateMini(){if(!mini)return;const r=$('#graph').getBoundingClientRect();d3.select('.mini-viewport').attr('x',mini.x-transform.x/transform.k*mini.k).attr('y',mini.y-transform.y/transform.k*mini.k).attr('width',r.width/transform.k*mini.k).attr('height',r.height/transform.k*mini.k);}
function choices(type){return type==='course'?[...ux.courses.values()]:type==='project'?ux.projectChoices(nav):ux.stageChoices(nav.project_id);}
function options(type){
 const select=$('#'+type+'-choice'),input=$('#'+type+'-search'),q=input.value.trim().toLowerCase(),active=nav[type+'_id'],available=choices(type),filtered=available.filter(s=>!q||s.title.toLowerCase().includes(q)||String(s.scope_id)===q),disabled=type==='project'&&nav.course_id&&ux.association(nav.course_id).state==='UNKNOWN'||type==='stage'&&!nav.project_id;
 select.replaceChildren();let placeholder=type==='course'?'No Course · all Projects':type==='project'?(disabled?'Project associations unknown':nav.course_id?'No Project · show Course':'Select Project…'):'No Stage · show Project';
 if(!disabled&&!available.length)placeholder=type==='stage'?'Explicitly no Stages':'No projects in this course';
 select.add(new Option(placeholder,''));for(const s of filtered)select.add(new Option(`${type==='stage'?s.order+'. ':''}${s.scope_id} · ${s.title}${s.state==='UNKNOWN'?' · Requirements not established':''}`,s.scope_id));
 if(active&&!filtered.some(s=>s.scope_id===active)){const current=available.find(s=>s.scope_id===active);if(current)select.add(new Option(`${current.scope_id} · ${current.title} · selected`,current.scope_id));}
 select.value=active?String(active):'';select.disabled=disabled;input.disabled=disabled;select.dataset.state=disabled?'UNKNOWN':available.length?'KNOWN':'EMPTY';
}
function selectors(){
 if(g.AtlasViewHost?.ownsFilters)return;
 $('#course-control').hidden=false;$('#stage-control').hidden=!nav.project_id;
 for(const type of ['course','project','stage'])options(type);
 const parts=[['course',nav.course_id],['project',nav.project_id],['stage',nav.stage_id]].filter(([,id])=>id).map(([type,id])=>{const r=ux[type+'s'].get(id);return`${type[0].toUpperCase()+type.slice(1)} ${id} · ${r.title}`;});
 $('#scope-title').textContent=['Courses & Projects',...parts].join(' > ');$('#scope-title').title=$('#scope-title').textContent;
 const association=nav.course_id?ux.association(nav.course_id):null;
 $('#association-note').textContent=association?association.state==='UNKNOWN'?'Course → Project associations UNKNOWN':association.state==='KNOWN_EMPTY'?'No projects in this course · complete explicit Track.projects inventory':association.source?`${association.project_ids.length} explicitly associated Projects · ${association.source.endpoint} · Track.projects`:`${association.project_ids.length} explicitly associated Projects · accepted source ${association.evidence_ids.join(', ')}`:`All ${ux.projects.size} catalog Projects · optional Course filter`;
 $('#clear-selection').disabled=!scope;$('#reset-view').disabled=false;
}
function controls(enabled){for(const id of ['fit','fit-subtree','topic-focus','out','in'])$('#'+id).disabled=!enabled;$('#inspector-toggle').disabled=!scope;$('#search').disabled=!enabled;$('#minimap').toggleAttribute('hidden',!enabled);}
function stopJob(){++job;if(pending){pending.resolve(false);pending=null;}if(worker){worker.terminate();worker=null;}}
function prepare(){
 selected=null;m=L=projection=mini=null;busy=false;$('#graph').setAttribute('aria-label',viewLabel());world.selectAll('*').remove();d3.select('#minimap').selectAll('*').remove();$('#zoom-value').textContent='—';$('#results').replaceChildren();$('#search').value='';setInspector(false);$('#scope-message').hidden=true;$('#error').textContent='';controls(false);
 document.body.style.setProperty('--scope',({course:'#b7b0d9',project:'#f3bc4d',stage:'#85bddf'})[scope?.scope_type]||'#b7b0d9');
}
function snapshotView(){return{nav:{...nav},selected,camera:{x:transform.x,y:transform.y,k:transform.k},inspector:{...inspectorState},intent:cameraIntent?{...cameraIntent}:null};}
async function navigate(value,{historyMode='push',restore=null}={}){
 const pinnedOpen=inspectorState.open&&inspectorState.pinned;const normalized=ux.normalize(value),changed=JSON.stringify(nav)!==JSON.stringify(normalized);
 if((historyMode==='push'&&changed)||historyMode==='replace')AtlasViewHost.scopeChanged(normalized,snapshotView(),historyMode);
 nav=normalized;scope=ux.current(nav);stopJob();const thisJob=job;prepare();selectors();
 const message=$('#scope-message');
 if(!scope){message.hidden=false;message.dataset.state='NEUTRAL';message.textContent='Select a Course or Project · Course filter is optional';$('#status').textContent='No scope selected';if(pinnedOpen){inspect();setInspector(true);}return;}
 if(scope.state==='UNKNOWN'){message.hidden=false;message.dataset.state='UNKNOWN';message.textContent='Requirements not established';$('#status').textContent='UNKNOWN · No complete Project scope evidenced';if(restore?.inspector?.open||pinnedOpen){inspect();setInspector(true,restore?.inspector?.pinned??inspectorState.pinned);}return;}
 const key=scope.scope_type+':'+scope.scope_id;
 let result=cache.get(key);
 if(!result){
  busy=true;message.textContent='Building local pyramid…';message.dataset.state='BUILDING';message.hidden=false;$('#status').textContent='Computing selected scope';builds++;
  result=await new Promise((resolve,reject)=>{pending={resolve,reject};const w=new Worker('layout-worker.js');worker=w;w.postMessage({catalog});w.onmessage=({data})=>{if(data.job!==job)return;pending=null;w.terminate();worker=null;data.error?reject(Error(data.error)):resolve(data);};w.onerror=e=>{if(thisJob!==job)return;pending=null;w.terminate();worker=null;reject(Error(e.message));};w.postMessage({job:thisJob,scope});}).catch(e=>{busy=false;message.hidden=true;$('#error').textContent=e.message;throw e;});
  if(!result||thisJob!==job)return;
  cache.set(key,result);if(cache.size>4)cache.delete(cache.keys().next().value);
 }
 ({L,projection,layoutMs}=result);m=ScopeProjection.model(projection,catalog);for(const n of L.nodes)n.data=m.nodes.get(n.key);busy=false;render();controls(true);fit();
 const empty=!scope.explicit_topic_ids.length&&!scope.explicit_category_ids.length;message.hidden=!empty;message.dataset.state=empty?'EMPTY':'KNOWN';if(empty)message.textContent=scope.scope_type==='stage'?'Known empty · No Stage-local Topics listed':'Known empty · No Project study-plan Topics listed';
 if(pinnedOpen&&!restore){inspect();setInspector(true);}
 if(restore){cameraIntent=restore.intent||null;if(m.nodes.has(restore.selected)){selected=restore.selected;paintSelection();}if(restore.camera)svg.call(zoom.transform,d3.zoomIdentity.translate(restore.camera.x,restore.camera.y).scale(restore.camera.k));if(restore.inspector?.open){inspect();setInspector(true,restore.inspector.pinned);}}
}
function choose(type,id){for(const input of document.querySelectorAll('.scope-control input'))input.value='';return navigate(ux.choose(nav,type,id));}
function load(s){if(!s)return;const next=s.scope_type==='course'?{section:'courses',course_id:s.scope_id}:s.scope_type==='project'?{section:'courses',project_id:s.scope_id}:{section:'courses',project_id:ux.stages.get(Number(s.scope_id))?.project_id,stage_id:s.scope_id};return navigate(next);}
function resetView(){for(const input of document.querySelectorAll('.scope-control input'))input.value='';$('#search').value='';$('#results').replaceChildren();return navigate({section:'courses'}).then(()=>{setInspector(false,false);cameraIntent=null;svg.call(zoom.transform,d3.zoomIdentity);});}
async function init(){
 const read=async path=>{const r=await fetch(path);if(!r.ok)throw Error('Missing local catalog input');return r.json();};
 let acceptedCourses,evidence;[catalog,index,acceptedCourses,evidence]=await Promise.all(['catalog.json','scope-index.json','../../data/knowledge/courses.json','../../data/knowledge/evidence.json'].map(read));
 catalog.projectCompletion=await read('../project-completion/progress.json');
 if(!catalog.projectCompletion.course_completion)catalog.projectCompletion.course_completion=await read('../project-completion/course-completions.json');
 scopes=[...index.courses,...index.projects,...index.stages];ux=ScopeUXModel.create(index,catalog,acceptedCourses,evidence);
 if(!g.AtlasViewHost?.ownsFilters)for(const type of ['course','project','stage']){
  const input=$('#'+type+'-search'),select=$('#'+type+'-choice');input.oninput=()=>options(type);
  input.onkeydown=e=>{if(e.key==='ArrowDown'){e.preventDefault();select.focus();}if(e.key==='Escape'){input.value='';options(type);}if(e.key==='Enter'){const q=input.value.trim().toLowerCase(),s=choices(type).find(s=>String(s.scope_id)===q)||choices(type).find(s=>s.title.toLowerCase().includes(q));if(q&&s)choose(type,s.scope_id).catch(console.error);}};
  select.onchange=()=>choose(type,select.value).catch(console.error);
 }
 $('#fit').onclick=fit;$('#fit-subtree').onclick=()=>fitSubtree();$('#topic-focus').onclick=()=>focusTopic();$('#close').onclick=()=>{setInspector(false);$('#inspector-toggle').focus({preventScroll:true});};$('#inspector-toggle').onclick=()=>{if(!inspectorState.open)inspect();setInspector(!inspectorState.open);};$('#inspector-pin').onclick=()=>setInspector(true,!inspectorState.pinned);$('#inspector-clear').onclick=clearEntity;$('#inspector-drawer').onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();$('#close').click();}};
 $('#in').onclick=()=>{cameraIntent=null;svg.call(zoom.scaleBy,1.4);};$('#out').onclick=()=>{cameraIntent=null;svg.call(zoom.scaleBy,1/1.4);};
 $('#minimap').onclick=e=>{if(!mini)return;cameraIntent=null;const r=e.currentTarget.getBoundingClientRect(),x=(e.clientX-r.left-mini.x)/mini.k,y=(e.clientY-r.top-mini.y)/mini.k,gr=$('#graph').getBoundingClientRect();svg.call(zoom.transform,d3.zoomIdentity.translate(gr.width/2-x*transform.k,gr.height/2-y*transform.k).scale(transform.k));};
 $('#search').oninput=()=>{const q=$('#search').value.trim().toLowerCase(),matches=q&&m?[...m.registry.values()].filter(n=>n.title.toLowerCase().includes(q)||String(n.id)===q||n.key===q).sort((a,b)=>(String(b.id)===q?1:0)-(String(a.id)===q?1:0)||a.id-b.id):[];$('#results').innerHTML=matches.slice(0,20).map(n=>`<button data-key="${n.key}">${esc(n.title)} · ${n.key}</button>`).join('');$('#results').querySelectorAll('button').forEach(b=>b.onclick=()=>{const n=m.nodes.get(b.dataset.key);select(n.key);n.type==='topic'?focusTopic(n.key):fitSubtree(n.key);$('#results').replaceChildren();});};$('#search').onkeydown=e=>{if(e.key==='Enter')$('#results button')?.click();if(e.key==='Escape')$('#results').replaceChildren();};
 window.addEventListener('resize',()=>{if(L)updateMini();});
 g.ScopeApp={state:()=>({catalog,index,scopes,ux,nav,scope,m,L,projection,transform,layoutMs,builds,busy,selected,inspectorState:{...inspectorState}}),load,navigate,choose,resetView,measure,fit,select,fitSubtree,focusTopic,bounds,setInspector,snapshotView};
 await navigate(ux.parse(location.search),{historyMode:'none'});
}
init().catch(e=>{$('#error').textContent=e.message;console.error(e);});
})(globalThis);
