(async()=>{
'use strict';
const $=s=>document.querySelector(s),C=GlobalAtlasCore,A=AdaptiveCore,U=GlobalPyramidUX,L=PyramidLabels;
const [raw,geometry]=await Promise.all(['catalog.json','global-geometry.json'].map(async f=>{const r=await fetch('../global-pyramid/generated/'+f);if(!r.ok)throw Error(f);return r.json();}));
const relations=await (await fetch('../../data/knowledge/edges.json')).json();
const m=C.index(raw,geometry),canvas=$('#map'),ctx=canvas.getContext('2d'),surface=$('#surface'),iframe=$('#atlas'),overlay=$('#atlas-overlay'),oc=overlay.getContext('2d');
const measurement=document.createElement('canvas').getContext('2d'),measure=(text,font)=>{measurement.font=font;return measurement.measureText(text).width;};
const metrics={layoutCalls:0,renderedCards:0,renderedLabels:0,focusMs:0,layoutMs:0},collapsed=new Set(),history=[];
let options={mode:'learned',id:8,stage:null,onlyLearned:false,branch:null,step:0},scope=A.selection(m,options),local=null,view='compact',selected=null,hover=null,cam={x:0,y:0,k:1},width=0,height=0,frame=null,atlasFrame=null,drag=null,transition=null;
const names={learned:'Mein Wissen',accepted:'Akzeptierte Landschaft',course:'Course 8',project:'Project Focus'},colors=['#63c7e3','#b39cf4','#e2be77','#e690b9','#87d7a4'];
const rootIndex=n=>geometry.root_sectors.findIndex(s=>s.root===n.root),color=n=>colors[Math.max(0,rootIndex(n))];
function label(n){return A.title(n,scope);}
function screen(p,camera=cam){return {x:p.x*camera.k+camera.x,y:p.y*camera.k+camera.y,w:p.w*camera.k,h:p.h*camera.k};}
function schedule(){if(frame===null)frame=requestAnimationFrame(()=>{frame=null;draw();});}
function fitBounds(b){const next=U.camera(b,width,height,{left:30,right:30,top:25,bottom:25});if(next)cam={...next,k:Math.min(next.k,1.25)};if(next&&next.k>1.25){cam.x=width/2-(b.x+b.w/2)*cam.k;cam.y=height/2-(b.y+b.h/2)*cam.k;}schedule();}
function positions(){return view==='mask'?new Map([...scope.visible].map(k=>[k,m.nodes.get(k)])):local?.positions||new Map();}
function fit(){if(view==='atlas'){iframe.contentWindow.GlobalAtlas?.fitScope();return;}fitBounds(C.bounds(positions().values()));}
function save(){history.push({selected,cam:{...cam},view});if(history.length>30)history.shift();}
function layout({retain=true}={}){
 const before=local,old=selected&&before?.positions.get(selected),anchor=old?screen(old):null;
 local=A.layout(m,scope,{collapsed,measure});metrics.layoutCalls++;metrics.layoutMs=local.durationMs;metrics.extent=local.bounds;
 if(before)metrics.movement=A.movement(before,local);
 const next=selected&&local.positions.get(selected);
 if(retain&&anchor&&next){cam.x=anchor.x-next.x*cam.k;cam.y=anchor.y-next.y*cam.k;metrics.focusAnchorDelta=Math.hypot(screen(next).x-anchor.x,screen(next).y-anchor.y);}else fitBounds(local.bounds);
 // Optional fade uses final validated positions throughout; no transient collisions.
 if(before&&$('#animate').checked&&!matchMedia('(prefers-reduced-motion: reduce)').matches){transition={start:performance.now()};}else transition=null;
 metrics.animationMs=transition?180:0;
 schedule();
}
function refresh(){
 const st=[...scope.topics],learned=st.filter(k=>scope.learned.has(k)).length,verified=st.filter(k=>scope.verified.has(k)).length;
 $('#summary').textContent=scope.unknown?scope.reason+(st.length?' · '+st.length+' belegte Teilanforderungen':''):scope.isFixture?st.length+' Struktur-Slots · FIXTURE':st.length+' relevante Topics · '+learned+' learned · '+verified+' verified';
 $('#empty').hidden=scope.visible.size>0;$('#empty').textContent=scope.unknown?scope.reason:'Bekannte leere Auswahl · keine passenden Topics';
 $('#view-title').textContent=(scope.isFixture?'Fixture-Vergleich':names[options.mode]||options.mode)+' · '+(view==='compact'?'kompakte lokale Geometrie':view==='mask'?'feste globale Sichtbarkeitsmaske':'Hervorhebung in globaler Referenz');
 $('#fixture-controls').hidden=!scope.isFixture;$('#step').textContent=' Schritt '+(options.step+1)+' / 4';$('#next-step').disabled=options.step>=3||!options.mode.includes('growth');
 $('#global-show').disabled=!selected;$('#collapse').disabled=!selected||m.nodes.get(selected)?.kind!=='category'||view!=='compact';$('#expand').disabled=!selected||view!=='compact';
 for(const id of ['compact','highlight','mask'])$('#'+id).setAttribute('aria-pressed',String(view===({compact:'compact',highlight:'atlas',mask:'mask'}[id])));
 const context=$('#context-roots');context.replaceChildren();for(const n of m.roots){const b=document.createElement('button');b.textContent=n.title+' · '+A.stats(m,scope,n.key).topics;b.className=scope.visible.has(n.key)?'relevant':'';b.onclick=()=>focus(n.key);context.append(b);}
 const branch=$('#branch');branch.replaceChildren(new Option('Gesamte Auswahl',''));for(const n of m.nodes.values())if(n.kind==='category'&&scope.visible.has(n.key)&&A.stats(m,scope,n.key).topics>0&&(n.depth<=3||n.children.some(c=>scope.topics.has(c.key))))branch.add(new Option(label(n)+' · '+A.stats(m,scope,n.key).topics,n.key));branch.value=options.branch||'';
 const crumbs=$('#breadcrumbs');crumbs.replaceChildren();let n=m.nodes.get(selected),path=[];while(n){path.unshift(n);n=m.nodes.get(n.parent);}for(const a of path){const b=document.createElement('button');b.textContent=label(a);b.title=a.key;b.onclick=()=>focus(a.key);crumbs.append(b);}
 $('#pending').textContent='';details();
}
function details(){
 const box=$('#details');box.replaceChildren();if(!selected){box.textContent='Karte auswählen; Doppelklick fokussiert. Details einer Zusammenfassung bleiben über die Suche erreichbar.';return;}
 const n=m.nodes.get(selected),add=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;box.append(e);return e;};
 add('h2',label(n));add('p',n.key+' → '+n.slot);add('p',scope.explicit.has(n.key)?'Explizit in der Auswahl':scope.visible.has(n.key)?'Hierarchiekontext; kein automatischer Lernbeleg':'Außerhalb der Auswahl; reine Inspektion');
 add('p','Globale Position: '+n.x+', '+n.y);if(local?.positions.has(selected)){const p=local.positions.get(selected);add('p','Lokale Position: '+p.x.toFixed(1)+', '+p.y.toFixed(1));}
 if(n.kind==='category'){const st=A.stats(m,scope,n.key);add('p',st.topics+(scope.isFixture?' Fixture-Slots': ' eindeutige relevante Topics · '+st.learned+' learned · '+st.verified+' verified'));}
 else if(scope.isFixture)add('p','Struktureller Lasttest-Slot. Keine echte Topic-Identität, kein erfundener Fortschritt.');
 else {const p=raw.progress.find(r=>r.topic_id===n.id);add('p',p?'learned='+p.is_learned+' · verified='+p.is_verified+' · Status='+p.verification_status:'Persönlicher Fortschritt UNKNOWN');}
 add('p','Alle strukturellen Zugehörigkeiten:');for(const k of n.parents){const b=add('button',(m.nodes.get(k)?.title||k)+(k===n.parent?' · primärer Layout-Elternknoten':' · weitere Zugehörigkeit'));b.onclick=()=>focus(k);}
 const more=add('details',''),summary=document.createElement('summary');summary.textContent='Weitere Beziehungen bei Bedarf';more.append(summary);
 const edges=relations.filter(e=>e.source===selected||e.target===selected),projects=raw.projects.filter(p=>p.required.includes(selected));const p=document.createElement('p');p.textContent=edges.map(e=>e.type+': '+e.source+' → '+e.target).concat(projects.map(p=>p.key+' · explizite Anforderung')).join('\n')||'Keine zusätzlichen belegten Beziehungen';more.append(p);
}
function inspect(key){if(!m.nodes.has(key))return;selected=key;refresh();schedule();}
function focus(key){
 const start=performance.now();if(!m.nodes.has(key))return;save();selected=key;
 if(view==='atlas'){iframe.contentWindow.GlobalAtlas?.focus(key);refresh();metrics.focusMs=performance.now()-start;return;}
 if(view==='compact'&&local.hidden.has(key)){
  let n=m.nodes.get(key);while(n){collapsed.delete(n.key);n=m.nodes.get(n.parent);}layout({retain:false});
 }
 if(view==='compact'&&!local.positions.has(key)){$('#status').textContent='Außerhalb der Auswahl. „In globaler Pyramide zeigen“ öffnet seine globale Position.';refresh();return;}
 const ps=positions(),n=ps.get(key);if(n){const nodes=m.nodes.get(key).kind==='category'?[...ps.values()].filter(p=>A.inside(m,p.key,key)):[n];fitBounds(C.bounds(nodes));}
 refresh();metrics.focusMs=performance.now()-start;schedule();
}
function pending(){ $('#pending').textContent='Auswahl geändert · mit einer Aktion übernehmen'; }
function readOptions(){return {mode:$('#scene').value,id:$('#scene').value==='project'?Number($('#project').value):8,stage:$('#stage').value?Number($('#stage').value):null,onlyLearned:$('#only-learned').checked,branch:$('#branch').value||null,step:options.mode===$('#scene').value?options.step:0};}
function setView(next){view=next;canvas.hidden=view==='atlas';iframe.hidden=overlay.hidden=view!=='atlas';if(view!=='atlas'&&atlasFrame!==null){cancelAnimationFrame(atlasFrame);atlasFrame=null;}refresh();schedule();scheduleAtlas();}
function apply(next){const o=readOptions();if(o.mode!==options.mode){collapsed.clear();selected=null;}options=o;scope=A.selection(m,options);if(next==='compact'&&(!local||JSON.stringify(o)!==JSON.stringify(local.selection.options)))layout({retain:true});setView(next);if(next==='mask')fit();}
function configure(){const project=$('#scene').value==='project';$('#project').disabled=!project;$('#stage').disabled=!project;$('#only-learned').disabled=!['course','project','accepted'].includes($('#scene').value);if($('#only-learned').disabled)$('#only-learned').checked=false;
 const p=raw.projects.find(p=>p.id===Number($('#project').value));$('#stage').replaceChildren(new Option('Alle Anforderungen',''));for(const s of p?.stages||[])$('#stage').add(new Option('Stage '+s.id+' · '+s.title,s.id));pending();}
function draw(){
 if(view==='atlas')return;
 const start=performance.now();ctx.clearRect(0,0,width,height);const slots=new Set([...scope.visible].map(k=>m.nodes.get(k).slot));const ps=positions(),routes=view==='mask'?geometry.hierarchy_routes.filter(r=>slots.has(r.child)):local.routes,drawCam=cam;let opacity=1;
 if(transition&&view==='compact'){
  const t=Math.min(1,(performance.now()-transition.start)/180);opacity=.25+.75*t;
  if(t<1)schedule();else transition=null;
 }
 const sx=x=>x*drawCam.k+drawCam.x,sy=y=>y*drawCam.k+drawCam.y;ctx.strokeStyle='#67879b';ctx.lineWidth=1.2;ctx.globalAlpha=.65*opacity;
 for(const r of routes){ctx.beginPath();r.points.forEach(([x,y],i)=>i?ctx.lineTo(sx(x),sy(y)):ctx.moveTo(sx(x),sy(y)));ctx.stroke();}
 if(view==='compact')for(const group of local.groups){const b=screen(group,drawCam);ctx.fillStyle='#20364a55';ctx.strokeStyle='#3c5c7077';ctx.fillRect(b.x,b.y,b.w,b.h);ctx.strokeRect(b.x,b.y,b.w,b.h);}
 ctx.globalAlpha=opacity;let cards=0,labels=0,readable=0;
 for(const [k,p]of ps){const b=screen(p,drawCam);if(b.x+b.w<0||b.y+b.h<0||b.x>width||b.y>height)continue;cards++;const n=m.nodes.get(k),context=scope.context.has(k),chosen=k===selected||k===hover;
  ctx.fillStyle=chosen?'#34536b':context?'#172739':'#20394c';ctx.strokeStyle=chosen?'#f5d597':color(n);ctx.lineWidth=chosen?2:1;ctx.beginPath();ctx.roundRect(b.x,b.y,Math.max(.5,b.w),Math.max(.5,b.h),Math.min(6,b.w/8));ctx.fill();ctx.stroke();
  if(view==='compact'&&cam.k>=.8&&labels<120){
   ctx.save();ctx.translate(b.x,b.y);ctx.scale(cam.k,cam.k);ctx.font=p.font;ctx.fillStyle=context?'#bdd1df':'#eff6fc';p.lines.forEach((t,i)=>ctx.fillText(t,14,22+i*18));ctx.font='11px system-ui';ctx.fillStyle='#aec9d9';ctx.fillText(p.meta,14,p.h-(p.count?27:12));if(p.count)ctx.fillText(p.count,14,p.h-11);ctx.restore();labels++;if(14*cam.k>=11)readable++;
  }else if(view==='mask'&&cam.k>=.8&&labels<100){ctx.font='12px system-ui';ctx.fillStyle='#e5f0fa';ctx.fillText(label(n).slice(0,32),b.x+4,b.y+Math.min(18,b.h-2));labels++;readable++;}
  if($('#progress').checked&&scope.learned.has(k)){ctx.fillStyle='#78e9a1';ctx.beginPath();ctx.arc(b.x+b.w-7,b.y+7,3.5,0,Math.PI*2);ctx.fill();if(scope.verified.has(k)){ctx.strokeStyle='#fff';ctx.beginPath();ctx.arc(b.x+b.w-7,b.y+7,6,0,Math.PI*2);ctx.stroke();}}
 }
 // Sparse overviews need readable branch names even below card-text zoom.
 // These are measured screen labels; they never change card coordinates.
 const labelBoxes=[];if(cam.k<.8){
  const obstacles=[...ps.values()].map(p=>({...screen(p),key:p.key})),candidates=[...ps.values()].filter(p=>m.nodes.get(p.key).kind==='category').sort((a,b)=>{
   const na=m.nodes.get(a.key),nb=m.nodes.get(b.key),pa=na.depth<=2?na.depth:na.children.some(c=>scope.topics.has(c.key))?3:4,pb=nb.depth<=2?nb.depth:nb.children.some(c=>scope.topics.has(c.key))?3:4;return pa-pb||A.stats(m,scope,b.key).topics-A.stats(m,scope,a.key).topics||a.x-b.x;
  });
  for(const p of candidates){if(labelBoxes.length>=18)break;const b=screen(p);if(b.x+b.w<0||b.x>width||b.y<0||b.y>height)continue;
   const n=m.nodes.get(p.key),text=label(n),lines=L.wrap(text,t=>measure(t,'12px system-ui'),155,2).lines,count=A.stats(m,scope,p.key).topics,caption=count+(scope.isFixture?' Slots':' Topics'),w=Math.max(...lines.map(t=>measure(t,'12px system-ui')),measure(caption,'11px system-ui'))+16,h=lines.length*15+23;
   let placed=null;for(const shift of [0,-38,38,-76,76])for(const side of [-1,1]){const box={key:p.key,x:Math.max(4,Math.min(width-w-4,b.x+b.w/2-w/2+shift)),y:side===-1?b.y-h-7:b.y+b.h+7,w,h};if(box.y<4||box.y+h>height-4||labelBoxes.some(q=>L.overlaps(q,box,6))||obstacles.some(q=>q.key!==p.key&&L.overlaps(q,box,2)))continue;placed=box;break;}if(!placed)continue;
   ctx.strokeStyle='#6f8fa0';ctx.beginPath();ctx.moveTo(b.x+b.w/2,b.y+b.h/2);ctx.lineTo(placed.x+w/2,placed.y+(placed.y<b.y?h:0));ctx.stroke();ctx.fillStyle='#12283cf2';ctx.fillRect(placed.x,placed.y,w,h);ctx.strokeStyle='#47697f';ctx.strokeRect(placed.x,placed.y,w,h);ctx.font='12px system-ui';ctx.fillStyle='#e4f0f8';lines.forEach((t,i)=>ctx.fillText(t,placed.x+8,placed.y+15+i*15));ctx.font='11px system-ui';ctx.fillStyle='#97c6da';ctx.fillText(caption,placed.x+8,placed.y+h-7);labelBoxes.push(placed);labels++;readable++;
  }
 }
 metrics.labelBoxes=labelBoxes;metrics.renderedCards=cards;metrics.renderedLabels=labels;metrics.readableLabels=readable;metrics.drawMs=performance.now()-start;metrics.camera={...cam};metrics.totalCards=ps.size;
 $('#metrics').textContent='Layout '+metrics.layoutMs.toFixed(2)+' ms · '+cards+'/'+ps.size+' Karten · '+labels+' Labels · '+(local?.bounds?Math.round(local.bounds.w)+' × '+Math.round(local.bounds.h):'leer')+' lokal';
 $('#status').textContent=(view==='mask'?'Unveränderte globale Positionen':scope.isFixture?'FIXTURE · keine echten Titel oder Fortschritte':'Lokale Darstellung · fachliche IDs und Ordnung aus globaler Referenz')+' · '+(cam.k*100).toFixed(0)+' % · '+(scope.isFixture?'': 'Vorfahren = Kontext');
}
function scheduleAtlas(){if(view==='atlas'&&atlasFrame===null)atlasFrame=requestAnimationFrame(paintAtlas);}
function paintAtlas(){
 atlasFrame=null;if(view!=='atlas')return;const atlas=iframe.contentWindow.GlobalAtlas;
 if(!atlas){scheduleAtlas();return;}
 const rect=iframe.contentDocument.querySelector('#canvas').getBoundingClientRect(),size=surface.getBoundingClientRect(),d=devicePixelRatio;
 if(overlay.width!==Math.round(size.width*d)||overlay.height!==Math.round(size.height*d)){overlay.width=Math.round(size.width*d);overlay.height=Math.round(size.height*d);}oc.setTransform(d,0,0,d,0,0);oc.clearRect(0,0,size.width,size.height);
 const c=atlas.state().cam,sx=x=>rect.x+c.x+x*c.k,sy=y=>rect.y+c.y+y*c.k;
 oc.save();oc.beginPath();oc.rect(rect.x,rect.y,rect.width,rect.height);oc.clip();oc.strokeStyle='#ffc874';oc.lineWidth=2.2;
 const slots=new Set([...scope.visible].map(k=>m.nodes.get(k).slot));
 for(const r of geometry.hierarchy_routes)if(slots.has(r.child)){oc.beginPath();r.points.forEach(([x,y],i)=>i?oc.lineTo(sx(x),sy(y)):oc.moveTo(sx(x),sy(y)));oc.stroke();}
 for(const k of scope.visible){const n=m.nodes.get(k);oc.strokeStyle=scope.explicit.has(k)?'#ffe2a1':'#79bdd4';oc.strokeRect(sx(n.x)-2,sy(n.y)-2,Math.max(4,n.w*c.k+4),Math.max(4,n.h*c.k+4));}oc.restore();
 metrics.atlasHighlightCount=scope.visible.size;metrics.atlasCamera={...c};$('#status').textContent=scope.visible.size+' Entities/Pfade hervorgehoben · globale Referenzgeometrie · Kamera unverändert durch Auswahl';scheduleAtlas();
}
function zoom(f,x=width/2,y=height/2){if(view==='atlas'){iframe.contentWindow.GlobalAtlas?.zoom(f);return;}const k=Math.max(.0001,Math.min(5,cam.k*f));cam.x=x-(x-cam.x)*k/cam.k;cam.y=y-(y-cam.y)*k/cam.k;cam.k=k;transition=null;schedule();}
function hit(e){const rect=canvas.getBoundingClientRect(),x=(e.clientX-rect.left-cam.x)/cam.k,y=(e.clientY-rect.top-cam.y)/cam.k;return [...positions().values()].reverse().find(p=>x>=p.x&&x<=p.x+p.w&&y>=p.y&&y<=p.y+p.h)?.key;}
canvas.onpointerdown=e=>{canvas.setPointerCapture(e.pointerId);drag={x:e.clientX,y:e.clientY,cam:{...cam},moved:false};};canvas.onpointermove=e=>{if(drag){const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.moved||=Math.abs(dx)+Math.abs(dy)>4;cam.x=drag.cam.x+dx;cam.y=drag.cam.y+dy;schedule();}else{hover=hit(e);const tip=$('#tooltip');tip.hidden=!hover;if(hover){tip.textContent=label(m.nodes.get(hover));const r=canvas.getBoundingClientRect();tip.style.left=Math.min(width-320,Math.max(8,e.clientX-r.left+12))+'px';tip.style.top=Math.min(height-50,e.clientY-r.top+12)+'px';}schedule();}};
canvas.onpointerup=e=>{if(drag&&!drag.moved){const key=hit(e);if(key)inspect(key);}drag=null;};canvas.onpointercancel=()=>drag=null;canvas.onpointerleave=()=>{hover=null;$('#tooltip').hidden=true;schedule();};canvas.ondblclick=e=>{const key=hit(e);if(key)focus(key);};canvas.onwheel=e=>{e.preventDefault();const r=canvas.getBoundingClientRect();zoom(Math.exp(-e.deltaY*.002),e.clientX-r.left,e.clientY-r.top);};
canvas.onkeydown=e=>{if(e.key==='+'||e.key==='=')zoom(1.4);else if(e.key==='-')zoom(1/1.4);else if(e.key.startsWith('Arrow')){cam.x+=e.key==='ArrowLeft'?60:e.key==='ArrowRight'?-60:0;cam.y+=e.key==='ArrowUp'?60:e.key==='ArrowDown'?-60:0;schedule();}else return;e.preventDefault();};
$('#compact').onclick=()=>apply('compact');$('#highlight').onclick=()=>apply('atlas');$('#mask').onclick=()=>apply('mask');$('#fit').onclick=fit;$('#zoom-in').onclick=()=>zoom(1.4);$('#zoom-out').onclick=()=>zoom(1/1.4);
$('#back').onclick=()=>{const prev=history.pop();if(prev){selected=prev.selected;cam=prev.cam;setView(prev.view);}};
$('#collapse').onclick=()=>{if(selected&&m.nodes.get(selected).kind==='category'){collapsed.add(selected);layout();refresh();}};$('#expand').onclick=()=>{if(selected){collapsed.delete(selected);layout();refresh();}};
$('#summarize').onclick=()=>{const depth=scope.topics.size>1000?0:scope.topics.size>=300?1:2;for(const n of m.nodes.values())if(n.kind==='category'&&n.depth===depth&&scope.visible.has(n.key))collapsed.add(n.key);layout({retain:false});refresh();};
$('#next-step').onclick=()=>{if(options.step<3){options.step++;scope=A.selection(m,options);layout();refresh();}};
$('#scene').onchange=configure;$('#project').onchange=configure;$('#stage').onchange=pending;$('#only-learned').onchange=pending;$('#branch').onchange=pending;$('#progress').onchange=schedule;
for(const p of raw.projects)$('#project').add(new Option('Project '+p.id+' · '+p.title+(p.requirements_status==='UNKNOWN'?' · UNKNOWN':''),p.id));$('#project').value='113';configure();
$('#search').oninput=()=>{const q=$('#search').value,found=A.search(m,q),box=$('#results');box.replaceChildren();for(const n of found.slice(0,12)){const b=document.createElement('button');b.textContent=label(n)+' · '+n.key+(local?.hidden.has(n.key)?' · Details öffnen':'');b.onclick=()=>focus(n.key);box.append(b);}if(found.length>12)box.append(document.createTextNode(found.length+' Treffer; Suche eingrenzen'));};$('#search').onkeydown=e=>{if(e.key==='ArrowDown'){$('#results button')?.focus();e.preventDefault();}if(e.key==='Enter')$('#results button')?.click();};
$('#global-show').onclick=()=>{if(!selected)return;setView('atlas');const show=()=>{const atlas=iframe.contentWindow.GlobalAtlas;if(!atlas){requestAnimationFrame(show);return;}atlas.switchScope('global');atlas.focus(selected);scheduleAtlas();};show();};
function resize(){const r=surface.getBoundingClientRect(),oldW=width,oldH=height;width=r.width;height=r.height;const d=devicePixelRatio;canvas.width=Math.round(width*d);canvas.height=Math.round(height*d);ctx.setTransform(d,0,0,d,0,0);if(oldW){cam.x+=(width-oldW)/2;cam.y+=(height-oldH)/2;}else if(local)fitBounds(local.bounds);schedule();}
new ResizeObserver(resize).observe(surface);resize();layout({retain:false});refresh();
globalThis.AdaptivePyramid={m,metrics,measure,apply,focus,inspect,fit,zoom,selection:()=>scope,local:()=>local,state:()=>({options:{...options},view,selected,collapsed:[...collapsed],cam:{...cam}}),setOptions:o=>{if(o.mode!==options.mode){collapsed.clear();selected=null;}options={...options,...o};$('#scene').value=options.mode;$('#project').value=String(options.id);configure();$('#stage').value=options.stage==null?'':String(options.stage);$('#only-learned').checked=options.onlyLearned;scope=A.selection(m,options);layout({retain:false});setView('compact');},setView,render:schedule};
})().catch(e=>{document.querySelector('#status').textContent='Ladefehler: '+e.message;console.error(e);});
