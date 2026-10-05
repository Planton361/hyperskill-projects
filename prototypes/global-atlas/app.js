/* Offline, no network beyond static same-origin assets; no persistent browser state. */
(async()=>{
const $=s=>document.querySelector(s),C=GlobalAtlasCore,start=performance.now(),metrics={};
const raw=await (await fetch('generated/catalog.json')).json();metrics.loadMs=performance.now()-start;
let t=performance.now();const m=C.index(raw);C.layout(m);metrics.layoutMs=performance.now()-t;
const canvas=$('#canvas'),ctx=canvas.getContext('2d'),mini=$('#mini'),mc=mini.getContext('2d');
let mode='global',context=8,stage=null,highlight=C.scope(m,mode,context),selected=null,cam={x:0,y:0,k:1},width,height,drag=null,frame=null,labelHits=[];
const personal=new Map();for(const p of raw.progress){if(!personal.has(p.topic_id))personal.set(p.topic_id,[]);personal.get(p.topic_id).push(p);}
const history=[],colors=['#36658e','#686096','#3d786e','#946841','#825f80'];
function label(n){return n.title||`Unresolved reference #${n.id}`;}
function schedule(){if(frame==null)frame=requestAnimationFrame(()=>{frame=null;draw();});}
function root(n){while(n.parent)n=m.nodes.get(n.parent);return n;}
function draw(){
 const began=performance.now();ctx.clearRect(0,0,width,height);let objects=0,labels=0;const candidates=[];
 const scopeColor=mode==='project'?'#f5bf6c':mode==='course'?'#c3a5ff':'#86bff5';
 for(const n of m.nodes.valuesSorted){
  const x=n.x*cam.k+cam.x,y=n.y*cam.k+cam.y,w=n.w*cam.k,h=n.h*cam.k;
  if(x+w<0||y+h<0||x>width||y>height||w<1.2||h<1.2)continue;
  const inScope=highlight.has(n.key),r=m.roots.indexOf(root(n));
  ctx.globalAlpha=mode==='global'||inScope?1:.18;
  ctx.fillStyle=n.kind==='category'?colors[r]:n.kind==='reference'?'#293440':'#5580a6';
  if(mode!=='global'&&inScope)ctx.fillStyle=n.kind==='category'?'#304862':scopeColor;
  if($('#progress').checked&&n.kind==='topic'){
   const p=personal.get(n.id)||[];if(p.some(p=>p.is_learned===true))ctx.fillStyle='#52b598';
  }
  ctx.fillRect(x+.5,y+.5,Math.max(0,w-1),Math.max(0,h-1));objects++;
  ctx.strokeStyle=n.key===selected?'#fff':mode==='global'&&n.active?'#86bff5':'#101c2c';ctx.lineWidth=n.key===selected?2:1;ctx.strokeRect(x+.5,y+.5,w-1,h-1);
  if(n.kind!=='category'&&w>=10&&h>=10){ctx.fillStyle=n.kind==='reference'?'#a2adba':'#e2eaf4';ctx.font='12px system-ui';ctx.fillText(n.kind==='reference'?'◇':'○',x+3,y+Math.min(h-2,15));}
  if($('#progress').checked&&(personal.get(n.id)||[]).some(p=>p.is_verified===true)&&n.kind==='topic'&&w>8&&h>8){ctx.strokeStyle='#fff';ctx.strokeRect(x+3,y+3,w-6,h-6);}
  const band=n.children.length?Math.min(34,n.h*.18)*cam.k:h;
  if(w>85&&(band>=15||(n.kind==='category'&&h>80)))candidates.push({n,x,y,w,alpha:ctx.globalAlpha});
 }
 ctx.globalAlpha=1;
 // Screen-space label budget and collision checks, independent of tiny world headers.
 const occupied=[];labelHits=[];for(const {n,x,y,w,alpha} of candidates){
  if(labels>=250||y<100||y>height-30)continue;
  ctx.font=(n.depth===0?'bold 15':'12')+'px system-ui';let text=label(n),tw=ctx.measureText(text).width;
  const limit=Math.min(w-14,300);while(tw>limit&&text.length>2){text=text.slice(0,-2)+'…';tw=ctx.measureText(text).width;}
  const b={x:x+3,y:y+2,w:tw+10,h:21};if(occupied.some(a=>b.x<a.x+a.w&&b.x+b.w>a.x&&b.y<a.y+a.h&&b.y+b.h>a.y))continue;
  occupied.push(b);labelHits.push({...b,key:n.key});ctx.globalAlpha=alpha;ctx.fillStyle='#101c2ced';ctx.fillRect(b.x,b.y,b.w,b.h);ctx.fillStyle='#f3f6fb';ctx.fillText(text,b.x+5,b.y+16);labels++;
 }ctx.globalAlpha=1;
 // Selected secondary memberships are connections, never extra leaf copies.
 const n=m.nodes.get(selected);if(n){ctx.strokeStyle='#ffda8f';ctx.lineWidth=2;ctx.setLineDash([5,4]);for(const p of n.parents.filter(p=>p!==n.parent)){const a=m.nodes.get(p);ctx.beginPath();ctx.moveTo((n.x+n.w/2)*cam.k+cam.x,(n.y+n.h/2)*cam.k+cam.y);ctx.lineTo((a.x+a.w/2)*cam.k+cam.x,(a.y+10)*cam.k+cam.y);ctx.stroke();}ctx.setLineDash([]);}
 metrics.drawMs=performance.now()-began;metrics.objects=objects;metrics.labels=labels;
 $('#zoom').textContent=Math.round(cam.k*100)+'%';$('#status').textContent=`${mode.toUpperCase()} · ${highlight.size} scope positions / ${m.nodes.size} total · ${objects} painted · ${labels} labels · ${metrics.drawMs.toFixed(1)} ms/frame`;
 mc.clearRect(0,0,150,90);for(const n of m.roots){mc.fillStyle=colors[m.roots.indexOf(n)];mc.fillRect(n.x/6300*150,n.y/3400*90,n.w/6300*150,n.h/3400*90);}
 mc.strokeStyle='#fff';mc.strokeRect(-cam.x/cam.k/6300*150,-cam.y/cam.k/3400*90,width/cam.k/6300*150,height/cam.k/3400*90);
}
m.nodes.valuesSorted=[...m.nodes.values()].sort((a,b)=>a.depth-b.depth||a.key.localeCompare(b.key));
function fit(nodes,save=true){const b=C.bounds(nodes);if(!b)return;if(save)history.push({...cam});const usable=height-135;cam.k=Math.min(500,(width-50)/b.w,usable/b.h);cam.x=width/2-(b.x+b.w/2)*cam.k;cam.y=110+usable/2-(b.y+b.h/2)*cam.k;schedule();}
function detail(key){
 selected=key;const n=m.nodes.get(key),p=$('#details');p.replaceChildren();
 const add=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;p.append(e);return e;};
 add('h2',label(n));add('p',`${n.key} · ${n.resolution}`);add('p',n.active?'Accepted ACTIVE_HISTORY entity (global projection geometry)':'Catalog-known, outside accepted personal geography');
 if(n.kind==='reference')add('p','Structural reference only. Topic identity, title, URL and theory metadata are unresolved.');
 else add('p','Canonical parent: '+(n.canonical_parent==null?'root / not supplied':'category:'+n.canonical_parent));
 const focus=add('button',n.kind==='category'?'Focus branch':'Focus entity');focus.onclick=()=>fit([n]);
 add('p','All structural parent memberships:');for(const k of n.parents){const b=add('button',label(m.nodes.get(k))+' · '+k);b.onclick=()=>{detail(k);fit([m.nodes.get(k)]);};}
 add('p','Display path (other memberships above):');const path=[];let a=n;while(a){path.unshift(a);a=m.nodes.get(a.parent);}for(const a of path){const b=add('button',label(a));b.onclick=()=>{detail(a.key);fit([a]);};}
 const courses=raw.courses.filter(c=>(n.kind==='category'?c.category_ids:c.topic_ids).includes(n.id));add('p','Explicit Course membership: '+(courses.map(c=>c.key).join(', ')||'none recorded'));
 const projects=raw.projects.filter(p=>p.required.includes(key));add('p','Explicit Project requirements: '+(projects.map(p=>p.key).join(', ')||'none recorded; unloaded Projects remain unknown'));
 for(const project of projects)for(const s of project.stages.filter(s=>project.requirements.some(e=>e.target===key&&e.stage_id===s.id)))add('p',`${project.key} / ${s.key} · Stage ${s.position}: ${s.title}`);
 if(n.kind==='topic'){const ps=raw.progress.filter(p=>p.topic_id===n.id);add('p','Personal observations: '+(ps.map(p=>`learned=${p.is_learned}; verified=${p.is_verified}; status=${p.verification_status}`).join(' | ')||'unknown'));}
 const ev=add('details',''),summary=document.createElement('summary');summary.textContent='Evidence and provenance';ev.append(summary);const pre=document.createElement('pre');pre.textContent=JSON.stringify({fact_sources:n.fact_sources,evidence_ids:n.evidence_ids,structural_memberships:n.parents,observations:raw.observations},null,2);ev.append(pre);schedule();
}
function switchScope(next,id=context,stageId=null){const began=performance.now();mode=next;context=Number(id);stage=stageId;highlight=C.scope(m,mode,context,stage);for(const b of document.querySelectorAll('[data-mode]'))b.setAttribute('aria-pressed',b.dataset.mode===mode);metrics.scopeMs=performance.now()-began;schedule();}
function controls(){
 const select=$('#context');select.replaceChildren();const rows=mode==='course'?raw.courses:mode==='project'?raw.projects:[];
 select.hidden=!rows.length;for(const r of rows){const o=document.createElement('option');o.value=r.id;o.textContent=r.title+(r.requirements_status==='UNKNOWN'?' · requirements UNKNOWN':'');select.append(o);}if(rows.length){context=rows.some(r=>r.id===context)?context:mode==='project'?113:rows[0].id;select.value=context;}
 const ss=$('#stage');ss.replaceChildren(new Option('All requirements',''));ss.hidden=mode!=='project';
 if(mode==='project'){const p=raw.projects.find(p=>p.id===context);for(const s of p.stages)ss.add(new Option(`Stage ${s.position}: ${s.title}`,s.id));$('#details').textContent=`${p.title} · ${p.requirements_status==='UNKNOWN'?'Requirements UNKNOWN; no complete loaded evidence':p.required.length+' distinct required Topics · '+p.stages.length+' loaded Stages'}`;}
 stage=null;
}
for(const b of document.querySelectorAll('[data-mode]'))b.onclick=()=>{mode=b.dataset.mode;controls();switchScope(mode,context);};
$('#context').onchange=()=>{context=Number($('#context').value);controls();switchScope(mode,context);};$('#stage').onchange=()=>{
 const id=$('#stage').value||null;switchScope(mode,context,id);const p=raw.projects.find(p=>p.id===context),s=p.stages.find(s=>s.id===Number(id));
 $('#details').textContent=s?`${p.title} / Stage ${s.position}: ${s.title} · ${new Set(s.required_topic_ids).size} explicit Stage required Topics · cumulative inventory: ${s.cumulative_required_topic_ids==null?'UNKNOWN':new Set(s.cumulative_required_topic_ids).size+' explicitly recorded Topics'}`:`${p.title} · ${p.requirements_status==='UNKNOWN'?'Requirements UNKNOWN':p.required.length+' distinct required Topics'}`;
};
$('#fit').onclick=()=>fit(m.roots);$('#fit-scope').onclick=()=>{const scope=[...highlight].map(k=>m.nodes.get(k)),leaves=scope.filter(n=>n.kind!=='category');fit(leaves.length?leaves:scope);};$('#back').onclick=()=>{if(history.length){cam=history.pop();schedule();}};
function zoom(f,x=width/2,y=height/2){const k=Math.max(.02,Math.min(500,cam.k*f));cam.x=x-(x-cam.x)*k/cam.k;cam.y=y-(y-cam.y)*k/cam.k;cam.k=k;schedule();}
$('#zoom-in').onclick=()=>zoom(1.5);$('#zoom-out').onclick=()=>zoom(1/1.5);$('#progress').onchange=schedule;
function search(q){const t=performance.now(),results=C.search(m,q);metrics.searchMs=performance.now()-t;return results;}
$('#search').oninput=()=>{const results=search($('#search').value),box=$('#results');box.replaceChildren();if(!results.length&&$('#search').value)box.textContent='No matching entity';for(const n of results.slice(0,40)){const b=document.createElement('button');b.textContent=label(n)+' · '+n.key;b.onclick=()=>{detail(n.key);fit([n]);};box.append(b);}if(results.length>40)box.append(document.createTextNode(`${results.length} matches · refine search`));};
for(const n of m.roots){const b=document.createElement('button');b.textContent=n.title;b.onclick=()=>{detail(n.key);fit([n]);};$('#roots').append(b);}
function hit(e){const rect=canvas.getBoundingClientRect(),sx=e.clientX-rect.left,sy=e.clientY-rect.top,label=labelHits.find(b=>sx>=b.x&&sx<=b.x+b.w&&sy>=b.y&&sy<=b.y+b.h);if(label)return m.nodes.get(label.key);const x=(sx-cam.x)/cam.k,y=(sy-cam.y)/cam.k;return [...m.nodes.valuesSorted].reverse().find(n=>x>=n.x&&x<=n.x+n.w&&y>=n.y&&y<=n.y+n.h);}
canvas.onwheel=e=>{e.preventDefault();const r=canvas.getBoundingClientRect();zoom(Math.exp(-e.deltaY*.002),e.clientX-r.left,e.clientY-r.top);};
canvas.onpointerdown=e=>{canvas.setPointerCapture(e.pointerId);drag={x:e.clientX,y:e.clientY,ox:cam.x,oy:cam.y,moved:false};};
canvas.onpointermove=e=>{if(drag){const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.moved ||=Math.abs(dx)+Math.abs(dy)>4;cam.x=drag.ox+dx;cam.y=drag.oy+dy;schedule();}};
canvas.onpointerup=e=>{if(drag&&!drag.moved){const n=hit(e);if(n)detail(n.key);}drag=null;};canvas.onpointercancel=()=>drag=null;
canvas.ondblclick=e=>{const n=hit(e);if(n){detail(n.key);fit([n]);}};
canvas.onkeydown=e=>{if(e.key==='+'||e.key==='=')zoom(1.5);else if(e.key==='-')zoom(1/1.5);else if(e.key.startsWith('Arrow')){cam.x+=e.key==='ArrowLeft'?80:e.key==='ArrowRight'?-80:0;cam.y+=e.key==='ArrowUp'?80:e.key==='ArrowDown'?-80:0;schedule();}else return;e.preventDefault();};
mini.onclick=e=>{const r=mini.getBoundingClientRect();cam.x=width/2-(e.clientX-r.left)/r.width*6300*cam.k;cam.y=height/2-(e.clientY-r.top)/r.height*3400*cam.k;schedule();};
function resize(){const r=canvas.getBoundingClientRect();width=r.width;height=r.height;const d=Math.min(devicePixelRatio,2);canvas.width=width*d;canvas.height=height*d;ctx.setTransform(d,0,0,d,0,0);mini.width=150;mini.height=90;fit(m.roots,false);}
new ResizeObserver(resize).observe(canvas);controls();resize();metrics.initMs=performance.now()-start;
globalThis.GlobalAtlas={m,metrics,search,switchScope,focus:key=>{detail(key);fit([m.nodes.get(key)]);},fitGlobal:()=>fit(m.roots),state:()=>({mode,context,stage,selected,cam:{...cam},count:m.nodes.size,highlight:[...highlight]})};
})().catch(e=>{document.querySelector('#status').textContent='Prototype failed to load: '+e.message;console.error(e);});
