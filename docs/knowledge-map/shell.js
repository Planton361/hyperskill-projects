/* One shell/router; Atlas filters select existing Global or local content. */
(() => {
 'use strict';
 const frames=new Map(),content=document.querySelector('#map-content'),loading=document.querySelector('#loading'),filters=document.querySelector('#atlas-filters'),links=[...document.querySelectorAll('#application-nav a')];
 const types=['course','project','stage'];let route,rememberedAtlas={view:'atlas'},nav,ux,revision=0,activeFrame=null,scopeHost;
 const number=v=>/^[1-9]\d*$/.test(String(v||''))?String(v):null;
 function parse(search){
  const q=new URLSearchParams(search),view=['personal','skill-tree'].includes(q.get('view'))?'skill-tree':'atlas',r={view};
  if(view==='atlas'){
   for(const type of types)if(number(q.get(type)))r[type]=number(q.get(type));
   if(types.includes(q.get('scope'))&&number(q.get('id')))r[q.get('scope')]=number(q.get('id'));
   if(/^(topic|category):[1-9]\d*$/.test(q.get('key'))){for(const type of types)delete r[type];r.key=q.get('key');}
  }
  return r;
 }
 const href=r=>'?'+new URLSearchParams(r);
 const atlasRoute=value=>{const r={view:'atlas'};for(const type of types)if(value[type+'_id'])r[type]=String(value[type+'_id']);return r;};
 const kind=r=>r.view==='skill-tree'?'personal':types.some(type=>r[type])?'scope':'global';
 const equivalent=(a,b)=>Object.keys({...a,...b}).every(key=>a[key]===b[key]);
 function snapshot(){return activeFrame?.contentWindow.ScopeApp?.snapshotView()||null;}
 function mark(){
  for(const link of links){if(link.dataset.view===route.view)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');}
  filters.hidden=false;document.querySelector('#view-content').dataset.view=route.view;document.querySelector('#nav-atlas').href=href(rememberedAtlas);
  document.title='Knowledge Atlas · '+(route.view==='atlas'?'Atlas':'My Skill Tree');
 }
 function save(previous=snapshot()){history.replaceState({route,atlasRoute:rememberedAtlas,scopeView:previous},'',href(route));}
 function commit(next,mode='push',previous){
  if(mode==='push')save(previous);
  route=next;if(route.view==='atlas')rememberedAtlas={...route};
  const state={route,atlasRoute:rememberedAtlas};history[mode==='push'?'pushState':'replaceState'](state,'',href(route));mark();
 }
 const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
 async function frameFor(type){
  if(frames.has(type)){await frames.get(type).ready;return frames.get(type).frame;}
  const frame=document.createElement('iframe');frame.className='atlas-view';frame.title=({global:'Complete Global Atlas',personal:'My Skill Tree',scope:'Local Scope Pyramid'})[type];frame.dataset.active='false';frame.setAttribute('aria-hidden','true');frame.inert=true;
  const record={frame};frames.set(type,record);
  frame.src=new URL(({global:'views/knowledge-atlas-v6-global/',personal:'views/knowledge-atlas-v6-skill-tree/',scope:'views/knowledge-atlas-scope-pyramid/?section=courses'})[type],location.href).href;content.append(frame);
  record.ready=(async()=>{
   const start=performance.now();while(true){const win=frame.contentWindow,api=type==='scope'?win.ScopeApp:win.AtlasV6;
    if(api&&(type==='scope'?!api.state().busy:api.state().L)){new MutationObserver(()=>{if(activeFrame===frame)syncSearch();}).observe(win.document.querySelector('#results'),{childList:true,subtree:true});return;}
    if(performance.now()-start>60000)throw Error(frame.title+' did not initialize');await sleep(30);
   }
  })();await record.ready;return frame;
 }
 async function catalog(){
  if(!scopeHost)scopeHost=(async()=>{const frame=await frameFor('scope');ux=frame.contentWindow.ScopeApp.state().ux;return frame;})();
  return scopeHost;
 }
 function desired(r){return ux.parse(href(r));}
 function choices(type){return type==='course'?[...ux.courses.values()]:type==='project'?ux.projectChoices(nav):ux.stageChoices(nav.project_id);}
 function options(type){
  if(!ux)return;const select=document.querySelector('#'+type+'-choice'),input=document.querySelector('#'+type+'-search'),q=input.value.trim().toLowerCase(),rows=choices(type),active=nav[type+'_id'],disabled=type==='stage'&&!nav.project_id||type==='project'&&nav.course_id&&ux.association(nav.course_id).state==='UNKNOWN';
  let label=type==='course'?'No Course · all Projects':type==='project'?(disabled?'Project associations unknown':nav.course_id?'No Project · show Course':'No Project · show Global'):'No Stage · show Project';
  if(!disabled&&!rows.length)label=type==='stage'?'Explicitly no Stages':'No projects in this course';
  select.replaceChildren(new Option(label,''));const matches=rows.filter(row=>!q||row.title.toLowerCase().includes(q)||String(row.scope_id)===q);
  for(const row of matches)select.add(new Option(`${type==='stage'?row.order+'. ':''}${row.scope_id} · ${row.title}${row.state==='UNKNOWN'?' · Requirements not established':''}`,row.scope_id));
  if(active&&!matches.some(row=>row.scope_id===active)){const row=rows.find(row=>row.scope_id===active);if(row)select.add(new Option(`${row.scope_id} · ${row.title} · selected`,row.scope_id));}
  select.value=active?String(active):'';select.title=active?rows.find(row=>row.scope_id===active)?.title||'':'';select.disabled=disabled;input.disabled=disabled;select.dataset.state=disabled?'UNAVAILABLE':rows.length?'KNOWN':'EMPTY';
 }
 function selectors(){
  if(!ux)return;for(const type of types)options(type);
  const stage=document.querySelector('#stage-filter');stage.hidden=!nav.project_id;stage.inert=!nav.project_id;
  const parts=types.filter(type=>nav[type+'_id']).map(type=>{const row=ux[type+'s'].get(nav[type+'_id']);return`${type[0].toUpperCase()+type.slice(1)} ${row.scope_id}`;});
  const current=ux.current(nav);if(current)parts.push(current.state==='UNKNOWN'?'Requirements not established':`${current.explicit_topic_ids.length} explicit Topics`);else parts.push('Complete Global Atlas');
  const context=document.querySelector('#atlas-context');context.textContent=parts.join(' › ');context.title=context.textContent;
  const association=nav.course_id?ux.association(nav.course_id):null;
  document.querySelector('#association-status').textContent=association?association.state==='UNKNOWN'?'Course associations UNKNOWN':association.state==='KNOWN_EMPTY'?'No projects in this course':`${association.project_ids.length} evidenced Projects in Course`:`All ${ux.projects.size} Projects · optional Course filter`;
 }
 function activate(frame){
  for(const record of frames.values()){
   const chosen=record.frame===frame;
   if(!chosen&&record.frame.dataset.active==='true'){const rect=record.frame.getBoundingClientRect();record.frame.style.width=rect.width+'px';record.frame.style.height=rect.height+'px';}
   if(chosen){record.frame.style.width='100%';record.frame.style.height='100%';}
   record.frame.dataset.active=String(chosen);record.frame.setAttribute('aria-hidden',String(!chosen));record.frame.inert=!chosen;
  }
  activeFrame=frame;syncSearch();
 }
 async function display(value,{restore=null,fitGlobal=false,forceIdentity=false}={}){
  const token=++revision;loading.hidden=false;loading.textContent=value.view==='atlas'?'Opening Atlas…':'Opening My Skill Tree…';
  try{
   await catalog();if(token!==revision)return;
   if(value.view==='atlas'){
    nav=desired(value);const normalized=atlasRoute(nav);if(value.key)normalized.key=value.key;
    if(!equivalent(normalized,route))commit(normalized,'replace');selectors();
   }
   const type=kind(route),frame=await frameFor(type);if(token!==revision)return;const win=frame.contentWindow;
   if(type==='scope'){
    const api=win.ScopeApp;
    if(!equivalent(api.state().nav,nav))await api.navigate(nav,{historyMode:'none',restore});
    while(api.state().busy){if(token!==revision)return;await sleep(30);}
   }else if(type==='global'){
    if(route.key){if(!win.AtlasV6.state().m.registry.has(route.key))throw Error('Unknown Global identity: '+route.key);if(forceIdentity||win.AtlasV6.state().selected!==route.key)win.AtlasV6.select(route.key,true);}
    else if(fitGlobal)win.AtlasV6.fit(null,false);
   }
   if(token!==revision)return;activate(frame);loading.hidden=true;
  }catch(error){if(token===revision){loading.hidden=false;loading.textContent=error.message;console.error(error);}}
 }
 async function navigate(next,{reset=false,forceIdentity=false,previous}={}){
  next=parse(href(next));const oldKind=kind(route),changed=!equivalent(next,route);
  if(!changed&&!reset&&!forceIdentity)return;
  if(changed)commit(next,'push',previous);
  await display(next,{fitGlobal:reset||oldKind==='scope'&&kind(next)==='global',forceIdentity});
 }
 function choose(type,id){if(!ux)return;for(const field of types)document.querySelector('#'+field+'-search').value='';return navigate(atlasRoute(ux.choose(nav,type,id)));}
 // A single visible search forwards to each renderer's original search contract.
 // Results retain their source order, labels, identity and click handlers.
 function syncSearch(){
  const d=activeFrame?.contentDocument,input=d?.querySelector('#search'),proxy=document.querySelector('#knowledge-query'),target=document.querySelector('#knowledge-results');
  proxy.value=input?.value||'';proxy.disabled=!input||input.disabled;proxy.placeholder=input?.placeholder||'Find knowledge…';
  target.replaceChildren();const source=d?.querySelector('#results');
  if(source)for(const node of source.children){const clone=node.cloneNode(true);if(node.tagName==='BUTTON')clone.onclick=()=>{node.click();syncSearch();};target.append(clone);}
  document.querySelector('#view-theme').hidden=!d?.querySelector('#theme');
 }
 const query=document.querySelector('#knowledge-query');
 query.oninput=()=>{const w=activeFrame?.contentWindow,input=w?.document.querySelector('#search');if(input){input.value=query.value;input.dispatchEvent(new w.Event('input',{bubbles:true}));syncSearch();}};
 query.onkeydown=e=>{const w=activeFrame?.contentWindow,input=w?.document.querySelector('#search');if(!input)return;
  if(e.key==='ArrowDown'&&!w.ScopeApp){e.preventDefault();document.querySelector('#knowledge-results button')?.focus();return;}
  input.dispatchEvent(new w.KeyboardEvent('keydown',{key:e.key,bubbles:true,cancelable:true}));syncSearch();
 };
 document.querySelector('#view-theme').onclick=()=>activeFrame?.contentDocument.querySelector('#theme')?.click();
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.querySelector('#knowledge-search').contains(e.target)){activeFrame?.contentDocument.querySelector('#results')?.replaceChildren();syncSearch();query.focus();}});
 window.AtlasShell=Object.freeze({
  isViewFrame:win=>[...frames.values()].some(record=>record.frame.contentWindow===win),
  scopeChanged:(value,previous,mode)=>{if(route.view!=='atlas')return;const next=atlasRoute(value);commit(next,mode,previous);display(next);},
  showGlobal:key=>navigate({view:'atlas',...(key?{key}:{})},{forceIdentity:true}),navigate,choose,
  state:()=>({route:{...route},rememberedAtlas:{...rememberedAtlas},nav:nav&&{...nav},ux,activeFrame,frames:[...frames.keys()]})
 });
 for(const link of links)link.addEventListener('click',event=>{if(event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();if(link.dataset.view!==route.view)navigate(link.dataset.view==='atlas'?rememberedAtlas:{view:'skill-tree'});});
 for(const type of types){
  const input=document.querySelector('#'+type+'-search'),select=document.querySelector('#'+type+'-choice');input.oninput=()=>options(type);select.onchange=()=>choose(type,select.value);
  input.onkeydown=event=>{if(event.key==='ArrowDown'){event.preventDefault();select.focus();}if(event.key==='Escape'){input.value='';options(type);}if(event.key==='Enter'&&ux){const q=input.value.trim().toLowerCase(),row=choices(type).find(row=>String(row.scope_id)===q)||choices(type).find(row=>row.title.toLowerCase().includes(q));if(q&&row)choose(type,row.scope_id);}};
 }
 document.querySelector('#reset-filters').onclick=()=>{for(const type of types)document.querySelector('#'+type+'-search').value='';navigate({view:'atlas'},{reset:true});};
 window.addEventListener('popstate',event=>{const previous=kind(route);route=parse(location.search);rememberedAtlas=event.state?.atlasRoute||rememberedAtlas;if(route.view==='atlas')rememberedAtlas={...route};mark();display(route,{restore:event.state?.scopeView,fitGlobal:previous==='scope'&&kind(route)==='global'&&!route.key});});
 rememberedAtlas=history.state?.atlasRoute||rememberedAtlas;route=parse(location.search);commit(route,'replace');display(route);
})();
