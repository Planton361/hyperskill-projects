/* Offline, no network beyond static same-origin assets; no persistent browser state. */
(async()=>{
const $=s=>document.querySelector(s),C=GlobalAtlasCore,UX=GlobalPyramidUX,L=PyramidLabels,start=performance.now(),metrics={};
const [raw,geometry]=await Promise.all(['catalog.json','global-geometry.json'].map(async f=>(await fetch('generated/'+f)).json()));metrics.loadMs=performance.now()-start;
let t=performance.now();const m=C.index(raw,geometry);metrics.hydrateMs=performance.now()-t;
const canvas=$('#canvas'),ctx=canvas.getContext('2d'),mini=$('#mini'),mc=mini.getContext('2d');
let mode='global',context=8,stage=null,highlight=C.scope(m,mode,context),selected=null,cam={x:0,y:0,k:1},width,height,drag=null,frame=null,labelHits=[];
const personal=new Map();for(const p of raw.progress){if(!personal.has(p.topic_id))personal.set(p.topic_id,[]);personal.get(p.topic_id).push(p);}
let regions=[],regionIndex=-1;
let ghostPolicy='local',view=UX.projection(m,mode,context,stage,ghostPolicy,selected);
const courseBadges=UX.projection(m,'course',8).explicit,projectBadges=UX.projection(m,'project',113).explicit;
const history=[],colors=['#36658e','#686096','#3d786e','#946841','#825f80'];
function label(n){return n.title||`Unresolved reference #${n.id}`;}
const tooltip=document.createElement('div');tooltip.id='label-tooltip';tooltip.hidden=true;$('#map').append(tooltip);const ancestorMenu=document.createElement('div');ancestorMenu.id='ancestor-jump';ancestorMenu.setAttribute('role','navigation');ancestorMenu.setAttribute('aria-label','Hidden hierarchy ancestors');ancestorMenu.hidden=true;$('#map').append(ancestorMenu);
function schedule(){if(frame==null)frame=requestAnimationFrame(()=>{frame=null;draw();});}
function root(n){while(n.parent)n=m.nodes.get(n.parent);return n;}
function draw(){
 const began=performance.now();ctx.clearRect(0,0,width,height);let objects=0,activeObjects=0,ghostObjects=0,labels=0;const candidates=[],cardObstacles=[],scopeColor=mode==='project'?'#f5bf6c':mode==='course'?'#c3a5ff':'#86bff5';
 const sx=x=>x*cam.k+cam.x,sy=y=>y*cam.k+cam.y;
 for(const sector of geometry.root_sectors){const n=m.nodes.get(sector.root);if(mode!=='global'&&!view.corridor.has(n.key))continue;ctx.fillStyle=colors[m.roots.indexOf(n)]+(mode==='global'?'14':'09');ctx.beginPath();ctx.moveTo(sx(n.x+n.w/2),sy(n.y));ctx.lineTo(sx(sector.x+sector.w),sy(sector.y+sector.h));ctx.lineTo(sx(sector.x),sy(sector.y+sector.h));ctx.closePath();ctx.fill();}
 // Dedicated far-zoom labels are reserved before local labels and painted last.
 const rootLayer=mode==='global'&&cam.k<=.01;
 const apex=geometry.presentation_super_root;
 const topLabels=rootLayer?L.topLevel(ctx,{width,height,
  apex:{key:apex.key,anchorX:sx(apex.x+apex.w/2),anchorY:sy(apex.y+apex.h/2)},
  roots:m.roots.map((n,i)=>({key:n.key,text:label(n),color:colors[i],
   anchorX:sx(n.x+n.w/2),anchorY:sy(n.y+n.h/2),sectorWidth:geometry.root_sectors[i].w*cam.k}))}):[];
 // Every connector is a projection of a persisted master route; no new routes.
 for(const route of geometry.hierarchy_routes){const n=bySlot.get(route.child);if(!n)continue;const relevant=view.corridor.has(n.key),inspect=view.inspected.has(n.key),ghost=view.ghosts.has(n.key);
  if(mode!=='global'&&!relevant&&!inspect&&!ghost)continue;
  ctx.globalAlpha=mode==='global'?.32:inspect?.65:relevant?.65:.07;ctx.strokeStyle=inspect?'#e2eaf4':relevant&&mode!=='global'?scopeColor:'#667e99';ctx.lineWidth=inspect||relevant&&mode!=='global'?1.3:.8;
  ctx.beginPath();route.points.forEach((p,i)=>{if(i)ctx.lineTo(sx(p[0]),sy(p[1]));else ctx.moveTo(sx(p[0]),sy(p[1]));});ctx.stroke();
 }
 ctx.globalAlpha=1;
 for(const n of m.nodes.valuesSorted){
  const active=view.explicit.has(n.key),ancestor=view.ancestors.has(n.key),inspected=view.inspected.has(n.key),ghost=view.ghosts.has(n.key),chosen=n.key===selected;
  if(mode!=='global'&&!active&&!ghost&&!inspected)continue;
  const x=sx(n.x),y=sy(n.y),w=n.w*cam.k,h=n.h*cam.k;
  if(x+w<0||y+h<210||x>width||y>height-30)continue;
  const alpha=mode==='global'||active||chosen?1:inspected?.5:ancestor?.3:.085;
  ctx.globalAlpha=alpha;ctx.fillStyle=mode==='global'?(n.kind==='category'?colors[m.roots.indexOf(root(n))]:n.kind==='reference'?'#485363':'#6593b8'):active?scopeColor:'#71839a';
  if(w<22||h<12){ctx.beginPath();ctx.arc(x+w/2,y+h/2,chosen?5:active&&mode!=='global'?2.8:1.1,0,Math.PI*2);ctx.fill();}
  else {ctx.beginPath();ctx.roundRect(x,y,w,h,Math.min(8,h/4));ctx.fill();ctx.strokeStyle=chosen?'#fff':mode==='global'&&n.active?'#86bff5':'#102138';ctx.lineWidth=chosen?2:1;ctx.stroke();}
  if(chosen&&!active&&mode!=='global'){ctx.strokeStyle='#ffda8f';ctx.setLineDash([4,3]);ctx.strokeRect(x-3,y-3,Math.max(8,w+6),Math.max(8,h+6));ctx.setLineDash([]);}
  if($('#progress').checked&&n.kind==='topic'&&(mode==='global'||active||chosen)){
   const rows=personal.get(n.id)||[],learned=rows.some(p=>p.is_learned===true),verified=rows.some(p=>p.is_verified===true);
   const px=w>22?x+8:x+w/2,py=h>12?y+h/2:y+h/2;
   if(learned){ctx.fillStyle='#4ee1ae';ctx.beginPath();ctx.arc(px,py,w>22?3:2,0,Math.PI*2);ctx.fill();}
   if(verified){ctx.strokeStyle='#fff';ctx.lineWidth=1.3;ctx.beginPath();ctx.arc(px,py,w>22?5:3,0,Math.PI*2);ctx.stroke();}
  }
  if(w>40&&h>28)cardObstacles.push({x,y,w,h,key:n.key});
  objects++;if(active)activeObjects++;else ghostObjects++;
  const density=view.density.get(n.key)||0,major=n.kind==='category'&&(n.depth<=2||n.region.w*cam.k>90),close=w>=90&&h>=16;
  const ancestorLabel=ancestor&&density>0&&(major||n.children.some(c=>c.kind!=='category'));
  const shouldLabel=chosen||n.depth===0||(mode==='global'?close||n.kind==='category'&&n.depth<=1:active&&(n.kind==='category'?major||close:close)||ancestorLabel||inspected&&major);
  if(shouldLabel&&!(rootLayer&&n.depth===0)){
   candidates.push({n,x:x+w/2,y:y+h/2,w,h,alpha,text:label(n)+(n.kind==='category'&&density&&mode!=='global'?` · ${density} Topics`:''),priority:chosen?0:n.depth===0?1:(active||ancestorLabel)&&n.kind==='category'?2:close?3:4});
  }
 }
 ctx.globalAlpha=1;labelHits=topLabels.filter(b=>b.key!==apex.key);const occupied=[...topLabels],labelStarted=performance.now();
 for(const item of candidates.sort((a,b)=>a.priority-b.priority||a.n.depth-b.n.depth||a.n.x-b.n.x||a.n.id-b.n.id)){
  if(labels>=90)break;const {n,x,y,alpha}=item,chosen=n.key===selected;ctx.font=(n.depth===0?'600 13':'12')+'px system-ui';
  const sector=n.depth===0?geometry.root_sectors.find(s=>s.root===n.key):null;
  const limit=n.depth===0?Math.max(70,Math.min(170,sector.w*cam.k-26)):chosen?Math.min(360,Math.max(180,item.w-20),width-40):n.kind==='category'?220:Math.max(100,Math.min(280,item.w-20));
  const wrapped=L.wrap(label(n),t=>ctx.measureText(t).width,limit,chosen?5:n.depth===0?2:3),lines=wrapped.lines;
  const caption=n.kind==='category'&&mode!=='global'&&view.density.get(n.key)?`${view.density.get(n.key)} ${mode==='project'?'required':'scope'} Topics`:'';
  const tw=Math.max(...lines.map(t=>ctx.measureText(t).width),caption?ctx.measureText(caption).width:0),labelH=lines.length*16+(caption?16:0)+12;
  let labelY=item.h>=labelH+16?y-item.h/2+8:y-item.h/2-labelH-12;
  if(n.depth===0)labelY=Math.max(210,y-60);
  const b={x:Math.max(8,Math.min(width-tw-24,x-tw/2-8)),y:labelY,w:tw+16,h:labelH,key:n.key,lines,caption,truncated:wrapped.truncated};
  if(chosen)b.y=Math.max(210,Math.min(height-140-labelH,b.y));
  if(b.y<210||b.y+b.h>height-140||occupied.some(a=>L.overlaps(a,b))||(!chosen&&cardObstacles.some(a=>a.key!==n.key&&L.overlaps(a,b,0))))continue;
  occupied.push(b);labelHits.push(b);ctx.globalAlpha=chosen?1:Math.max(.7,alpha);ctx.strokeStyle=mode==='global'?'#667e99':scopeColor;ctx.lineWidth=.8;
  if(item.h<labelH+16){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(Math.max(b.x,Math.min(b.x+b.w,x)),b.y+b.h);ctx.stroke();}
  ctx.fillStyle='#101f31f5';ctx.beginPath();ctx.roundRect(b.x,b.y,b.w,b.h,5);ctx.fill();ctx.fillStyle='#e3edf7';lines.forEach((text,i)=>ctx.fillText(text,b.x+8,b.y+18+i*16));
  if(caption){ctx.font='11px system-ui';ctx.fillStyle=mode==='project'?'#f5bf6c':mode==='course'?'#c3a5ff':'#afccea';ctx.fillText(caption,b.x+8,b.y+18+lines.length*16);}
  labels++;
 }
 L.paintTopLevel(ctx,topLabels);labels+=topLabels.length;
 metrics.topLevelLabels=topLabels.map(({key,text,lines,x,y,w,h,fontSize,anchorX,anchorY})=>({key,text,lines,x,y,w,h,fontSize,anchorX,anchorY}));
 metrics.labelMs=performance.now()-labelStarted;metrics.labelBoxes=labelHits.map(({key,x,y,w,h,lines,truncated})=>({key,x,y,w,h,lines,truncated}));
 ctx.globalAlpha=1;metrics.drawMs=performance.now()-began;metrics.objects=objects;metrics.activeObjects=activeObjects;metrics.ghostObjects=ghostObjects;metrics.labels=labels;metrics.labelKeys=labelHits.map(b=>b.key);
 $('#zoom').textContent=(cam.k*100).toFixed(cam.k<.01?2:0)+'%';$('#status').textContent=`${objects} visible marks · ${ghostObjects} context · ${labels} labels · fixed global slots`;
 drawMinimap(scopeColor);metrics.drawMs=performance.now()-began;
}
function drawMinimap(color){
 const W=220,H=130,B=geometry.bounds,x=v=>6+v/B.w*(W-12),y=v=>6+v/B.h*(H-12);mc.clearRect(0,0,W,H);
 for(const s of geometry.root_sectors){mc.fillStyle=colors[geometry.root_sectors.indexOf(s)]+'35';mc.fillRect(x(s.x),y(s.y),s.w/B.w*(W-12),s.h/B.h*(H-12));}
 mc.strokeStyle='#6e809555';mc.lineWidth=.5;mc.beginPath();for(const r of geometry.hierarchy_routes)r.points.forEach((p,i)=>{if(i)mc.lineTo(x(p[0]),y(p[1]));else mc.moveTo(x(p[0]),y(p[1]));});mc.stroke();
 for(const k of view.explicit){const n=m.nodes.get(k);mc.fillStyle=color;mc.fillRect(x(n.x),y(n.y),1.5,1.5);}
 const rect=(b,c,dash=[])=>{if(!b)return;mc.strokeStyle=c;mc.setLineDash(dash);mc.lineWidth=1.4;mc.strokeRect(x(b.x),y(b.y),Math.max(2,b.w/B.w*(W-12)),Math.max(2,b.h/B.h*(H-12)));mc.setLineDash([]);};
 rect(UX.scopeBounds(m,view),color,[3,2]);if(selected)rect(C.branch(m,m.nodes.get(selected)),'#72e0c9');rect({x:-cam.x/cam.k,y:-cam.y/cam.k,w:width/cam.k,h:height/cam.k},'#fff');
 mini.setAttribute('aria-label',`Complete five-root world. ${mode} scope. Focus: ${selected?label(m.nodes.get(selected)):'overview'}. Enter fits scope; arrow keys pan.`);metrics.minimap={scope:UX.scopeBounds(m,view),focus:selected,world:{...B}};
}
const bySlot=new Map([...m.nodes.values()].map(n=>[n.slot,n]));
m.nodes.valuesSorted=[...m.nodes.values()].sort((a,b)=>a.depth-b.depth||a.key.localeCompare(b.key));
function fitBounds(b,save=true){const began=performance.now(),next=UX.camera(b,width,height,{left:32,right:32,top:220,bottom:140});if(!next)return false;if(save)history.push({cam:{...cam},selected});cam=next;metrics.fitMs=performance.now()-began;schedule();return true;}
function fit(nodes,save=true){const a=[...nodes];const b=a.length===1&&m.nodes.has(a[0].key)?UX.focusBounds(m,view,a[0].key):C.bounds(a.map(n=>C.branch(m,n)));return fitBounds(b,save);}
function fitScope(){const previous={cam:{...cam},selected};selected=null;regionIndex=-1;refreshProjection();summary();const began=performance.now();const b=mode==='global'?geometry.bounds:UX.scopeBounds(m,view);const ok=fitBounds(b,false);if(ok)history.push(previous);metrics.fitScopeMs=performance.now()-began;if(!ok)$('#status').textContent='Requirements UNKNOWN — no evidenced scope extent';return ok;}
function refreshProjection(){view=UX.projection(m,mode,context,stage,ghostPolicy,selected);highlight=view.corridor;}
function focus(key){const began=performance.now(),previous={cam:{...cam},selected};detail(key);fitBounds(UX.focusBounds(m,view,key),false);history.push(previous);metrics.navigationMs=performance.now()-began;}
function navigateRegion(delta){if(!regions.length)return false;const index=regionIndex<0?(delta<0?regions.length-1:0):(regionIndex+delta+regions.length)%regions.length;focus(regions[index].node.key);return true;}
function clearFocus(){selected=null;regionIndex=-1;ancestorMenu.hidden=true;tooltip.hidden=true;refreshProjection();summary();controlsDetail();fitScope();}
function controlsDetail(){$('#details').textContent=mode==='project'&&view.unknown?'Requirements UNKNOWN — no complete evidence loaded':'Choose a revealed region or search the complete global world. Focus reveals no new Knowledge.';}
function summary(){
 const titles={global:'Global pyramid',my:'My Atlas',course:'Course '+context,project:'Project '+context},topics=[...view.explicit].filter(k=>!k.startsWith('category:')).length,categories=[...view.explicit].filter(k=>k.startsWith('category:')).length;
 const text=mode==='global'?'3,955 global positions · 5 roots · 849 Categories · 3,106 leaf slots':mode==='my'?'135 active positions · 46 Categories · 89 Topics · 31 learned · 12 verified':mode==='course'?`${categories} explicit Categories · ${topics} explicit Topics · ancestors are context`:view.unknown?'Requirements UNKNOWN · evidence is incomplete':`${raw.projects.find(p=>p.id===context).required.length} required Topics`+(stage?` · Stage ${stage}: ${topics} Topics`:' · 5 loaded Stages');
 $('#scope-heading').textContent=titles[mode];$('#scope-info').textContent=text;$('#scope-summary').textContent=titles[mode]+' · '+text;$('#fit-scope').textContent='Fit '+(mode==='global'?'Global':mode==='my'?'My Atlas':mode==='course'?'Course':'Project');$('#fit-scope').disabled=view.unknown;
 $('#scope-semantics').textContent=mode==='project'?'Amber = explicit requirements · dim = ancestor context · green dot = learned · white ring = verified':mode==='course'?'Purple = explicit Course membership · dim = ancestor context · green dot = learned · white ring = verified':mode==='my'?'Blue = active geography · green dot = learned · white ring = verified':'All reserved geography · green dot = learned · white ring = verified';document.body.dataset.scope=mode;$('#scope-info').classList.toggle('unknown',view.unknown);$('#stage').classList.toggle('stage-selected',stage!=null);if(mode==='project')$('#stage').value=stage==null?'':String(stage);
 regions=UX.regions(m,view,mode);regionIndex=selected?regions.findIndex(g=>UX.inside(m.nodes.get(selected),g.node,m)):-1;
 const regionSelect=$('#region-select');regionSelect.replaceChildren(new Option(mode==='global'?'All five roots':'All relevant regions',''));for(const g of regions)regionSelect.add(new Option(label(g.node)+` · ${g.count} ${mode==='global'?'leaf slots':'Topics'}`,g.node.key));regionSelect.value=regionIndex<0?'':regions[regionIndex].node.key;
 $('#previous-region').disabled=$('#next-region').disabled=!regions.length;regionSelect.disabled=!regions.length;$('#region-indicator').textContent=regionIndex<0?`${regions.length} regions`: `${regionIndex+1} / ${regions.length}`;
 const branches=$('#branches');branches.replaceChildren();if(mode!=='global'&&!view.unknown){const heading=document.createElement('p');heading.textContent='Revealed geography · observed progress';branches.append(heading);for(const group of regions){const button=document.createElement('button'),stats=UX.stats(m,view,group.node.key);button.textContent=label(group.node)+` · ${stats.topics} ${mode==='project'?'required':'scope'} Topics`;const meta=document.createElement('span');meta.textContent=`${stats.learned} learned · ${stats.verified} verified`;button.append(meta);button.onclick=()=>focus(group.node.key);branches.append(button);}}
 for(const button of $('#roots').children){const count=view.density.get(button.dataset.key)||0;button.classList.toggle('dormant-root',mode!=='global'&&!view.corridor.has(button.dataset.key));button.classList.toggle('relevant-root',mode!=='global'&&view.corridor.has(button.dataset.key));const title=m.nodes.get(button.dataset.key).title;button.textContent=title+(mode!=='global'&&count?` · ${count}`:'');button.title=mode==='global'?title:`${title}: ${count} scope Topics`;button.setAttribute('aria-label',mode==='global'?'Focus '+title:`Focus ${title}: ${count} scope Topics`);}
 const topicGroups=$('#topic-groups');topicGroups.replaceChildren(new Option('Focus a Topic group…',''));topicGroups.hidden=mode==='global'||view.unknown;const groups=new Map();for(const key of (mode==='global'?[]:view.explicit)){const n=m.nodes.get(key);if(n.kind==='category'||!n.parent)continue;groups.set(n.parent,(groups.get(n.parent)||0)+1);}for(const [key,count]of [...groups].sort((a,b)=>m.nodes.get(a[0]).x-m.nodes.get(b[0]).x))topicGroups.add(new Option(label(m.nodes.get(key))+` · ${count} Topics`,key));
 const crumbs=$('#breadcrumbs');crumbs.replaceChildren();ancestorMenu.hidden=true;ancestorMenu.replaceChildren();
 if(selected){const path=[];let n=m.nodes.get(selected);while(n){path.unshift(n);n=m.nodes.get(n.parent);}const visible=path.length>4?[path[0],null,...path.slice(-2)]:path;
 for(const n of visible){if(!n){const more=document.createElement('button');more.textContent='…';more.title='Choose any hidden ancestor';more.setAttribute('aria-label','Show all ancestors');more.setAttribute('aria-expanded','false');more.onclick=()=>{ancestorMenu.hidden=!ancestorMenu.hidden;more.setAttribute('aria-expanded',String(!ancestorMenu.hidden));if(!ancestorMenu.hidden)ancestorMenu.querySelector('button')?.focus();};crumbs.append(more);for(const a of path.slice(1,-2)){const b=document.createElement('button');b.textContent=label(a);b.onclick=()=>focus(a.key);ancestorMenu.append(b);}continue;}
 const b=document.createElement('button');b.textContent=label(n);b.title=label(n);b.setAttribute('aria-label','Focus '+label(n));if(n.key===selected)b.setAttribute('aria-current','page');b.onclick=()=>focus(n.key);crumbs.append(b);}}

}
function detail(key){
 selected=key;refreshProjection();summary();const n=m.nodes.get(key),p=$('#details');p.replaceChildren();
 const add=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;p.append(e);return e;};
 add('h2',label(n));add('p',`${n.key} → ${n.slot} · ${n.resolution}`);add('p',`Global slot: (${n.x}, ${n.y}), ${n.w} × ${n.h}. Primary layout parent: ${n.parent||'presentation:hyperskill'}`);add('p',n.active?'Active in My Atlas · accepted ACTIVE_HISTORY':'Dormant in My Atlas · inspecting this slot does not activate it');add('p',view.explicit.has(key)?'Explicitly relevant in this scope':view.corridor.has(key)?'Ancestor context · not explicit scope membership':'Outside this scope · inspection only');
 if(n.kind==='reference')add('p','Structural reference only. Topic identity, title, URL and theory metadata are unresolved.');
 else add('p','Canonical parent: '+(n.canonical_parent==null?'root / not supplied':'category:'+n.canonical_parent));
 const focusButton=add('button',n.kind==='category'?'Focus branch':'Focus entity');focusButton.onclick=()=>fit([n]);
 add('p','All structural parent memberships:');for(const k of n.parents){const b=add('button',label(m.nodes.get(k))+' · '+k);b.onclick=()=>focus(k);}
 if(n.children.length){add('p',`Focus children (${n.children.length}; first 24 shown):`);for(const child of (mode==='global'?n.children:n.children.filter(c=>view.corridor.has(c.key)).length?n.children.filter(c=>view.corridor.has(c.key)):n.children).slice(0,24)){const b=add('button',label(child)+' · '+child.key);b.onclick=()=>focus(child.key);}}
 add('p','Display path (other memberships above):');const path=[];let a=n;while(a){path.unshift(a);a=m.nodes.get(a.parent);}for(const a of path){const b=add('button',label(a));b.onclick=()=>focus(a.key);}
 const courses=raw.courses.filter(c=>(n.kind==='category'?c.category_ids:c.topic_ids).includes(n.id));add('p','Explicit Course membership: '+(courses.map(c=>c.key).join(', ')||'none recorded'));
 const projects=raw.projects.filter(p=>p.required.includes(key));add('p','Explicit Project requirements: '+(projects.map(p=>p.key).join(', ')||'none recorded; unloaded Projects remain unknown'));
 for(const project of projects)for(const s of project.stages.filter(s=>project.requirements.some(e=>e.target===key&&e.stage_id===s.id)))add('p',`${project.key} / ${s.key} · Stage ${s.position}: ${s.title}`);
 if(n.kind==='topic'){const ps=raw.progress.filter(p=>p.topic_id===n.id);add('p','Personal observations: '+(ps.map(p=>`learned=${p.is_learned}; verified=${p.is_verified}; status=${p.verification_status}`).join(' | ')||'unknown'));}
 const ev=add('details',''),evidenceSummary=document.createElement('summary');evidenceSummary.textContent='Evidence and provenance';ev.append(evidenceSummary);const pre=document.createElement('pre');pre.textContent=JSON.stringify({fact_sources:n.fact_sources,evidence_ids:n.evidence_ids,structural_memberships:n.parents,observations:raw.observations},null,2);ev.append(pre);schedule();
}
function switchScope(next,id=context,stageId=null){const began=performance.now();mode=next;context=Number(id);stage=stageId;refreshProjection();summary();document.querySelector('aside').scrollTop=0;for(const b of document.querySelectorAll('[data-mode]'))b.setAttribute('aria-pressed',b.dataset.mode===mode);metrics.scopeMs=performance.now()-began;schedule();}
function controls(){
 const select=$('#context');select.replaceChildren();const rows=mode==='course'?raw.courses:mode==='project'?raw.projects:[];
 select.hidden=!rows.length;for(const r of rows){const o=document.createElement('option');o.value=r.id;o.textContent=r.title+(r.requirements_status==='UNKNOWN'?' · requirements UNKNOWN':'');select.append(o);}if(rows.length){context=rows.some(r=>r.id===context)?context:mode==='project'?113:rows[0].id;select.value=context;}
 const ss=$('#stage');ss.replaceChildren(new Option('All requirements',''));ss.hidden=mode!=='project';
 if(mode==='project'){const p=raw.projects.find(p=>p.id===context);for(const s of p.stages)ss.add(new Option(`Stage ${s.position}: ${s.title}`,s.id));$('#details').textContent=`${p.title} · ${p.requirements_status==='UNKNOWN'?'Requirements UNKNOWN; no complete loaded evidence':p.required.length+' distinct required Topics · '+p.stages.length+' loaded Stages'}`;}
 if(mode==='global')$('#details').textContent='Complete captured taxonomy: 849 Categories + 3,106 structural leaf slots. Five root sectors share a presentation-only anchor. Focus a root, then search or zoom into a branch.';
 if(mode==='my')$('#details').textContent='ACTIVE_HISTORY: 46 Categories + 89 Topics. Strict visibility at global coordinates; dormant slots retain their space. Focus a branch or search for a readable card. No compaction.';
 if(mode==='course')$('#details').textContent='Course '+context+': explicit membership plus structural ancestor context. Taxonomy alone never establishes membership. All coordinates are global.';
 selected=null;stage=null;
}
for(const b of document.querySelectorAll('[data-mode]'))b.onclick=()=>{mode=b.dataset.mode;controls();switchScope(mode,context);};
$('#context').onchange=()=>{context=Number($('#context').value);controls();switchScope(mode,context);};$('#stage').onchange=()=>{
 const id=$('#stage').value||null;switchScope(mode,context,id);const p=raw.projects.find(p=>p.id===context),s=p.stages.find(s=>s.id===Number(id));
 $('#details').textContent=s?`${p.title} / Stage ${s.position}: ${s.title} · ${new Set(s.required_topic_ids).size} explicit Stage required Topics · cumulative inventory: ${s.cumulative_required_topic_ids==null?'UNKNOWN':new Set(s.cumulative_required_topic_ids).size+' explicitly recorded Topics'}`:`${p.title} · ${p.requirements_status==='UNKNOWN'?'Requirements UNKNOWN':p.required.length+' distinct required Topics'}`;
};
$('#fit').onclick=()=>fit([{kind:"category",region:geometry.bounds}]);$('#fit-scope').onclick=fitScope;$('#back').onclick=()=>{if(history.length){const previous=history.pop();cam=previous.cam;selected=previous.selected;refreshProjection();summary();if(selected)detail(selected);else controlsDetail();schedule();}};
function zoom(f,x=width/2,y=height/2){const k=Math.max(.0001,Math.min(500,cam.k*f));cam.x=x-(x-cam.x)*k/cam.k;cam.y=y-(y-cam.y)*k/cam.k;cam.k=k;schedule();}
$('#zoom-in').onclick=()=>zoom(1.5);$('#zoom-out').onclick=()=>zoom(1/1.5);$('#topic-groups').onchange=()=>{const key=$('#topic-groups').value;if(key)focus(key);};$('#progress').onchange=schedule;$('#ghost').onchange=()=>{ghostPolicy=$('#ghost').value;refreshProjection();schedule();};
function search(q){const t=performance.now(),results=C.search(m,q);metrics.searchMs=performance.now()-t;return results;}
$('#search').oninput=()=>{const results=search($('#search').value),box=$('#results');box.replaceChildren();if(!results.length&&$('#search').value)box.textContent='No matching entity';for(const n of results.slice(0,40)){const b=document.createElement('button');const course=courseBadges.has(n.key),project=projectBadges.has(n.key);const title=document.createElement('strong');title.textContent=label(n);const description=document.createElement('span');description.textContent=(n.kind==='category'?'Category':n.kind==='topic'?'Topic':'Unresolved reference')+' · '+n.key+' · '+(n.active?'active':'dormant')+(course?' · Course relevant':'')+(project?' · Project relevant':'')+(n.kind==='reference'?' · unresolved reference':'');b.append(title,description);b.onclick=()=>focus(n.key);box.append(b);}if(results.length>40)box.append(document.createTextNode(`${results.length} matches · refine search`));};
for(const n of m.roots){const b=document.createElement('button');b.textContent=n.title;b.dataset.key=n.key;b.onclick=()=>focus(n.key);$('#roots').append(b);}
function hit(e){const rect=canvas.getBoundingClientRect(),sx=e.clientX-rect.left,sy=e.clientY-rect.top,label=labelHits.find(b=>sx>=b.x&&sx<=b.x+b.w&&sy>=b.y&&sy<=b.y+b.h);if(label)return m.nodes.get(label.key);const x=(sx-cam.x)/cam.k,y=(sy-cam.y)/cam.k;return [...m.nodes.valuesSorted].reverse().find(n=>(mode==='global'||view.explicit.has(n.key)||view.ghosts.has(n.key)||view.inspected.has(n.key))&&x>=n.x&&x<=n.x+n.w&&y>=n.y&&y<=n.y+n.h);}
canvas.onwheel=e=>{e.preventDefault();const r=canvas.getBoundingClientRect();zoom(Math.exp(-e.deltaY*.002),e.clientX-r.left,e.clientY-r.top);};
canvas.onpointerdown=e=>{canvas.setPointerCapture(e.pointerId);drag={x:e.clientX,y:e.clientY,ox:cam.x,oy:cam.y,moved:false};};
canvas.onpointermove=e=>{if(!drag){const n=hit(e);tooltip.hidden=!n;if(n){tooltip.textContent=label(n);const r=canvas.getBoundingClientRect();tooltip.style.left=Math.max(8,Math.min(width-350,e.clientX-r.left+12))+'px';tooltip.style.top=Math.min(height-60,e.clientY-r.top+18)+'px';}}if(drag){const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.moved ||=Math.abs(dx)+Math.abs(dy)>4;cam.x=drag.ox+dx;cam.y=drag.oy+dy;schedule();}};
canvas.onpointerup=e=>{if(drag&&!drag.moved){const n=hit(e);if(n)detail(n.key);}drag=null;};canvas.onpointercancel=()=>drag=null;canvas.onpointerleave=()=>tooltip.hidden=true;
canvas.ondblclick=e=>{const n=hit(e);if(n){detail(n.key);fit([n]);}};
canvas.onkeydown=e=>{if(e.key==='+'||e.key==='=')zoom(1.5);else if(e.key==='-')zoom(1/1.5);else if(e.key.startsWith('Arrow')){cam.x+=e.key==='ArrowLeft'?80:e.key==='ArrowRight'?-80:0;cam.y+=e.key==='ArrowUp'?80:e.key==='ArrowDown'?-80:0;schedule();}else return;e.preventDefault();};
mini.onclick=e=>{const r=mini.getBoundingClientRect();cam.x=width/2-((e.clientX-r.left)/r.width*220-6)/208*geometry.bounds.w*cam.k;cam.y=height/2-((e.clientY-r.top)/r.height*130-6)/118*geometry.bounds.h*cam.k;schedule();};

$('#region-select').onchange=()=>{if($('#region-select').value)focus($('#region-select').value);else fitScope();};$('#previous-region').onclick=()=>navigateRegion(-1);$('#next-region').onclick=()=>navigateRegion(1);
$('#search').onkeydown=e=>{if(e.key==='ArrowDown'){e.preventDefault();$('#results button')?.focus();}else if(e.key==='Enter'){const first=$('#results button');if(first){e.preventDefault();first.click();}}};
document.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();if(!ancestorMenu.hidden){ancestorMenu.hidden=true;$('#breadcrumbs button[aria-expanded]')?.setAttribute('aria-expanded','false');$('#breadcrumbs button[aria-expanded]')?.focus();}else {clearFocus();canvas.focus();}}else if(e.altKey&&(e.key==='ArrowLeft'||e.key==='ArrowRight')){e.preventDefault();navigateRegion(e.key==='ArrowLeft'?-1:1);}});
mini.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();fitScope();}else if(e.key.startsWith('Arrow')){canvas.onkeydown(e);}};

function resize(){const r=canvas.getBoundingClientRect(),oldWidth=width,oldHeight=height;const center=oldWidth?{x:(oldWidth/2-cam.x)/cam.k,y:(oldHeight/2-cam.y)/cam.k}:null;width=r.width;height=r.height;const d=Math.min(devicePixelRatio,2);canvas.width=width*d;canvas.height=height*d;ctx.setTransform(d,0,0,d,0,0);mini.width=220;mini.height=130;if(center){cam.x=width/2-center.x*cam.k;cam.y=height/2-center.y*cam.k;schedule();}else fit([{kind:"category",region:geometry.bounds}],false);}
new ResizeObserver(resize).observe(canvas);controls();refreshProjection();summary();resize();metrics.initMs=performance.now()-start;
globalThis.GlobalAtlas={m,metrics,search,switchScope:(next,id=context,stageId=null)=>{mode=next;context=Number(id);controls();switchScope(next,context,stageId);},focus,fitScope,navigateRegion,clearFocus,setGhost:policy=>{ghostPolicy=policy;$('#ghost').value=policy;refreshProjection();schedule();},zoom,fitGlobal:()=>fit([{kind:"category",region:geometry.bounds}]),state:()=>({mode,context,stage,selected,regionIndex,regions:regions.map(g=>g.node.key),ghostPolicy,explicit:[...view.explicit],ghosts:[...view.ghosts],cam:{...cam},count:m.nodes.size,highlight:[...highlight]})};
})().catch(e=>{document.querySelector('#status').textContent='Prototype failed to load: '+e.message;console.error(e);});
