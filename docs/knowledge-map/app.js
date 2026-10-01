'use strict';
(async()=>{
performance.mark('km:start');
const m=await(await fetch('model.json')).json(),$=id=>document.getElementById(id);
const T=new Map(m.topics.map(t=>[t.key,t])),D=new Map(m.domains.map(d=>[d.id,d])),S=new Map(m.subdomains.map(s=>[s.id,s])),P=new Map(m.projects.map(p=>[p.key,p]));
let state={},scene=[],quiet=false;
const text=(tag,value,parent)=>{const e=document.createElement(tag);e.textContent=value;parent.append(e);return e;};
const button=(p,label,fn)=>{const b=text('button',label,p);b.onclick=fn;return b;};
const eligible=t=>(state.course==='all'||t.course_ids.includes(Number(state.course)))&&(state.mode==='roadmap'||t.is_learned===true);
const count=(field,id)=>{const a=m.topics.filter(t=>t[field]===id&&(state.course==='all'||t.course_ids.includes(Number(state.course))));return{total:a.length,learned:a.filter(t=>t.is_learned===true).length,verified:a.filter(t=>t.is_learned===true&&t.is_verified).length};};
const incident=id=>m.connections.filter(e=>e.source===id||e.target===id);
function decode(){const q=new URLSearchParams(location.search),s={mode:q.get('mode')==='roadmap'?'roadmap':'knowledge',course:q.get('course')||'all',page:Math.max(0,Math.floor(Number(q.get('page'))||0))};
if(s.course!=='all'&&!m.courses.some(c=>String(c.id)===s.course))s.course='all';
const t=T.get('topic:'+q.get('topic')),sub=S.get('subdomain:'+q.get('subdomain')),d=D.get('domain:'+q.get('domain')),p=P.get('project:'+q.get('project'));
if(p){s.project=p.key;s.connections=q.get('connections')==='1'&&p.required_topic_ids!==null;}
else if(t){s.topic=t.key;s.subdomain=t.subdomain_id;s.domain=t.domain_id;if(t.is_learned!==true)s.mode='roadmap';if(s.course!=='all'&&!t.course_ids.includes(Number(s.course)))s.course='all';}
else if(sub){s.subdomain=sub.id;s.domain=sub.domain_id;}else if(d)s.domain=d.id;return s;}
function url(s){const q=new URLSearchParams();if(s.mode==='roadmap')q.set('mode','roadmap');if(s.course!=='all')q.set('course',s.course);for(const key of ['project','topic','subdomain','domain'])if(s[key]){q.set(key,s[key].split(':')[1]);break;}if(s.connections)q.set('connections','1');if(s.page)q.set('page',s.page);return location.pathname+(q.size?'?'+q:'');}
function nav(next){state={mode:state.mode||'knowledge',course:state.course||'all',page:0,...next};history.pushState(null,'',url(state));render();$('level').setAttribute('tabindex','-1');$('level').focus({preventScroll:true});}
const domain=d=>nav({domain:d.id}),sub=s=>nav({domain:s.domain_id,subdomain:s.id});
const topic=t=>nav({topic:t.key,domain:t.domain_id,subdomain:t.subdomain_id,mode:t.is_learned===true?state.mode:'roadmap',course:state.course!=='all'&&!t.course_ids.includes(Number(state.course))?'all':state.course});
function parent(){if(state.project)nav({});else if(state.topic)sub(S.get(state.subdomain));else if(state.subdomain)domain(D.get(state.domain));else nav({});}
const svg=d3.select('#map'),world=svg.append('g'),edgesLayer=world.append('g'),nodes=world.append('g');
svg.append('defs').append('marker').attr('id','arrow').attr('viewBox','0 0 10 10').attr('refX',10).attr('refY',5).attr('markerWidth',6).attr('markerHeight',6).attr('orient','auto').append('path').attr('class','edge-arrow').attr('d','M0 0L10 5L0 10');
const zoom=d3.zoom().scaleExtent([.7,4]).on('zoom',e=>world.attr('transform',e.transform)).on('end',e=>{
if(quiet||!e.sourceEvent)return;
if(e.transform.k>1.8){const a=scene.filter(n=>['domain','subdomain'].includes(n.type));const w=$('canvas').clientWidth,h=$('canvas').clientHeight;
a.sort((x,y)=>Math.hypot(e.transform.applyX(x.x)-w/2,e.transform.applyY(x.y)-h/2)-Math.hypot(e.transform.applyX(y.x)-w/2,e.transform.applyY(y.y)-h/2));if(a[0])a[0].type==='domain'?domain(a[0]):sub(a[0]);}
else if(e.transform.k<.75&&(state.domain||state.project))parent();});
svg.call(zoom).on('dblclick.zoom',null);
const action=n=>n.type==='domain'?domain(n):n.type==='subdomain'?sub(n):n.type==='topic'?topic(n):inspect();
function render(){
const started=performance.now(),w=$('canvas').clientWidth,mobile=w<600;let level='domains',all=[],edges=[];
if(state.project&&state.connections){level='project';const ids=new Set(P.get(state.project).required_topic_ids||[]);all=m.topics.filter(t=>ids.has(t.id)&&eligible(t));}
else if(state.topic){level='topic';const ids=new Set(incident(state.topic).flatMap(e=>[e.source,e.target]));all=[T.get(state.topic),...m.topics.filter(t=>t.key!==state.topic&&ids.has(t.key)&&eligible(t))];}
else if(state.subdomain){level='topics';all=m.topics.filter(t=>t.subdomain_id===state.subdomain&&eligible(t));}
else if(state.domain){level='subdomains';all=m.subdomains.filter(s=>s.domain_id===state.domain).map(s=>({...s,key:s.id,type:'subdomain',count:count('subdomain_id',s.id)})).filter(s=>state.mode==='roadmap'?s.count.total:s.count.learned);}
else all=m.domains.map(d=>({...d,key:d.id,type:'domain',count:count('domain_id',d.id)})).filter(d=>state.mode==='roadmap'?d.count.total:d.count.learned);
const topicScene=['topic','topics','project'].includes(level),cap=topicScene?(mobile?6:24):(mobile?4:12),per=level==='topic'?cap-1:cap,total=level==='topic'?all.length-1:all.length;
state.page=Math.min(state.page,Math.max(0,Math.ceil(total/per)-1));
const visible=level==='topic'?[all[0],...all.slice(1).slice(state.page*per,(state.page+1)*per)]:all.slice(state.page*per,(state.page+1)*per);
scene=visible.map(n=>({...n,type:n.type||'topic'}));
const cols=mobile?1:Math.min(3,Math.max(1,Math.floor(w/320)),Math.max(1,Math.ceil(Math.sqrt(scene.length)))),rows=Math.max(1,Math.ceil(scene.length/cols));
scene.forEach((n,i)=>{n.x=mobile?(level==='topic'&&i?48:28):25+(i%cols)*(w/cols);});
if(level==='project')scene.push({...P.get(state.project),type:'project',x:28,y:35});
for(const n of scene){const chars=mobile?Math.floor((w-n.x-30)/8):Math.max(14,Math.floor((w/cols-55)/8)),lines=[''];for(const word of n.title.split(' ')){let i=lines.length-1;if(lines[i]&&lines[i].length+word.length+1>chars)lines.push(word);else lines[i]+=(lines[i]?' ':'')+word;}n.labelLines=lines;n.countY=Math.max(48,(lines.length-1)*19+22);}
const rowHeight=Math.max(mobile?82:100,...scene.map(n=>n.countY+27)),height=Math.max(mobile?330:430,rows*rowHeight+90)+(level==='project'?70:0);
$('canvas').style.height=height+'px';svg.attr('viewBox','0 0 '+w+' '+height);
scene.forEach((n,i)=>{if(n.type!=='project')n.y=(level==='project'?125:65)+Math.floor(i/cols)*rowHeight;});
const pos=new Map(scene.map(n=>[n.key,n]));
if(level==='topic')edges=incident(state.topic).filter(e=>pos.has(e.source)&&pos.has(e.target)).map(e=>({...e,type:e.records.some(r=>r.type==='prerequisite')?'prerequisite':'dependent'}));
if(level==='project')edges=m.edges.filter(e=>e.type==='project_requires'&&e.source===state.project&&pos.has(e.target));
edgesLayer.selectAll('path').data(edges,e=>e.source+'|'+e.target).join('path').attr('class',e=>'edge '+(e.type==='project_requires'?'requires':'')).attr('data-type',e=>e.type).attr('data-source',e=>e.source).attr('data-target',e=>e.target).attr('fill','none').attr('marker-end','url(#arrow)').attr('d',(e,i)=>{const a=pos.get(e.source),b=pos.get(e.target);if(mobile&&e.type==='project_requires'){const lane=3+i*2;return 'M'+(a.x-12)+','+a.y+' C'+lane+','+a.y+' '+lane+','+b.y+' '+(b.x-12)+','+b.y;}const length=Math.hypot(b.x-a.x,b.y-a.y)||1,dx=(b.x-a.x)/length,dy=(b.y-a.y)/length;return 'M'+(a.x+12*dx)+','+(a.y+12*dy)+' L'+(b.x-12*dx)+','+(b.y-12*dy);});
const g=nodes.selectAll('g.node').data(scene,n=>n.key).join(enter=>{const n=enter.append('g');for(const c of ['hit','mark','verification'])n.append('circle').attr('class',c);n.append('text').attr('class','label');n.append('text').attr('class','count');return n;});
const status=n=>n.is_learned===true?'Learned'+(n.is_verified?' · Verified':''):n.is_learned===false?'Not learned':'Unknown';
g.attr('class',n=>'node '+(n.type==='topic'?(n.is_learned===true?'learned':n.is_learned===false?'not-learned':'unknown'):'structural')+(n.key===state.topic?' selected':'')).attr('data-key',n=>n.key).attr('data-type',n=>n.type).attr('data-learned',n=>n.type==='topic'?String(n.is_learned):null).attr('transform',n=>'translate('+n.x+','+n.y+')').attr('role','button').attr('tabindex',0).attr('aria-label',n=>n.title+' · '+(n.count?n.count.learned+' learned':n.type==='topic'?status(n):n.status)).on('click',(e,n)=>{e.stopPropagation();action(n);}).on('keydown',(e,n)=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();action(n);}});
g.select('.hit').attr('r',22);g.select('.mark').attr('r',n=>n.type==='topic'?5:10);g.select('.verification').attr('r',9).attr('display',n=>n.is_learned===true&&n.is_verified?null:'none');
g.select('.label').attr('x',18).attr('y',-5).attr('font-size',16).each(function(n){const label=d3.select(this).text('');n.labelLines.forEach((line,i)=>label.append('tspan').attr('x',18).attr('dy',i?19:0).text(line));});
g.select('.count').attr('x',18).attr('y',n=>n.countY).attr('font-size',12).text(n=>n.count?n.count.learned+' learned · '+n.count.verified+' verified':n.type==='topic'?status(n):n.status);
quiet=true;svg.call(zoom.transform,d3.zoomIdentity);quiet=false;
svg.attr('data-level',level).attr('data-mode',state.mode).attr('data-ready','true');
$('my').setAttribute('aria-pressed',state.mode==='knowledge');$('roadmap').setAttribute('aria-pressed',state.mode==='roadmap');$('course').value=state.course;
$('level').textContent={domains:'Domain overview',subdomains:'Domain focus',topics:'Subdomain focus',topic:'Topic focus',project:'Project connections'}[level];
$('visible').textContent=visible.length+' / '+all.length+' in scope · '+edges.length+' evidenced edges'+(level==='topic'?' · direct neighbors only':'');
$('pagination').hidden=total<=per;$('previous').disabled=state.page===0;$('next').disabled=(state.page+1)*per>=total;
$('breadcrumbs').replaceChildren();button($('breadcrumbs'),'All knowledge',()=>nav({}));
if(state.domain)button($('breadcrumbs'),D.get(state.domain).title,()=>domain(D.get(state.domain)));
if(state.subdomain)button($('breadcrumbs'),S.get(state.subdomain).title,()=>sub(S.get(state.subdomain)));
if(state.topic)text('span',T.get(state.topic).title,$('breadcrumbs'));if(state.project)text('span',P.get(state.project).title,$('breadcrumbs'));
$('area-nav').replaceChildren();if(!topicScene)for(const n of visible)button($('area-nav'),n.title+' · '+n.count.learned+' learned',()=>action(n));
$('projects').replaceChildren();for(const p of m.projects.filter(p=>state.mode==='roadmap'||['completed','active'].includes(p.status)))button($('projects'),p.title+' · '+p.status,()=>nav({project:p.key}));
inspect();svg.attr('data-render-ms',(performance.now()-started).toFixed(3));
}
function inspect(){
const box=$('details');box.replaceChildren();const n=state.project?P.get(state.project):state.topic?T.get(state.topic):state.subdomain?S.get(state.subdomain):state.domain?D.get(state.domain):null;
text('h2',n?n.title:'Explore your recorded knowledge',box);if(!n){text('p','Start with a domain. Topics and evidence appear as you navigate.',box);return;}
if(state.project){text('p','Status: '+n.status,box);text('p','Required topics: '+(n.required_topic_ids===null?'not loaded':n.required_topic_ids.length)+' · project_requires',box);text('p','Completed stages: '+(n.completed_stage_ids===null?'inventory not loaded':n.completed_stage_ids.length),box);
const stages=m.stages.filter(s=>s.project_id===n.id);text('h3','Known stage metadata ('+stages.length+')',box);for(const s of stages)text('p',(s.position||'')+' · '+s.title,box);if(!stages.length)text('p','Stage metadata not loaded; this does not prove there are no stages.',box);
if(n.required_topic_ids!==null)button(box,'Show project connections',()=>nav({...state,connections:true,page:0}));text('p','Requirements do not prove topic-level application. Applied IDs remain unknown.',box);}
else if(state.topic){text('p',n.is_learned===true?'Learned · is_learned === true':n.is_learned===false?'Not learned (explicit)':'Learning status unknown',box);text('p','Verified: '+(n.is_verified?'yes (additional evidence)':'not explicitly verified')+' · Applied: unknown',box);
text('h3','Direct prerequisites / dependents',box);const neighbors=incident(n.key),list=text('div','',box);let neighborPage=0;
const showNeighbors=()=>{list.replaceChildren();for(const e of neighbors.slice(neighborPage*20,(neighborPage+1)*20)){const other=T.get(e.source===n.key?e.target:e.source);button(list,(e.target===n.key?'Prerequisite: ':'Dependent: ')+other.title,()=>topic(other));}if(neighbors.length>20){text('p','Page '+(neighborPage+1)+' / '+Math.ceil(neighbors.length/20),list);if(neighborPage)button(list,'Previous neighbors',()=>{neighborPage--;showNeighbors();});if((neighborPage+1)*20<neighbors.length)button(list,'Next neighbors',()=>{neighborPage++;showNeighbors();});}};showNeighbors();
text('h3','Evidence',box);const refs=new Set([...(n.progress_evidence_ids||[]),...(n.evidence_ids||[]),...incident(n.key).flatMap(e=>e.records.flatMap(r=>r.evidence_ids||[]))]);for(const id of refs){const e=m.evidence.find(e=>e.id===id);text('p',id+(e?' · '+(e.confidence||e.method||'recorded source'):''),box);}}
else{const c=count(state.subdomain?'subdomain_id':'domain_id',n.id);text('p',c.learned+' learned · '+c.verified+' verified · '+c.total+' course topics',box);text('p','Curated hierarchy-based display grouping, not a capability or prerequisite assertion.',box);}
if(n.url){const a=text('a','Open Hyperskill source ↗',box);a.href=n.url;a.rel='noopener noreferrer';}
}
function search(){const started=performance.now(),query=$('search').value.trim().toLowerCase();$('results').replaceChildren();
if(query){const items=[...m.topics.map(t=>({...t,type:'topic'})),...m.domains.map(d=>({...d,type:'domain'})),...m.subdomains.map(s=>({...s,type:'subdomain'})),...m.projects.map(p=>({...p,type:'project'}))],hits=items.filter(n=>n.title.toLowerCase().includes(query));
for(const n of hits.slice(0,20))button($('results'),n.title+' · '+n.type+(n.type==='topic'?' · '+(n.is_learned===true?'learned':n.is_learned===false?'not learned':'unknown'):''),()=>{if(n.type==='topic')topic(n);else if(n.type==='domain')domain(n);else if(n.type==='subdomain')sub(n);else nav({project:n.key});$('search').value='';$('results').replaceChildren();$('details').setAttribute('tabindex','-1');$('details').focus();});
if(!hits.length)text('p','No matching recorded entities.', $('results'));if(hits.length>20)text('p','First 20 matches; refine your search.', $('results'));}
$('results').dataset.responseMs=(performance.now()-started).toFixed(3);}
$('search').oninput=search;$('search').onkeydown=e=>{if(e.key==='ArrowDown'){$('results').querySelector('button')?.focus();e.preventDefault();}if(e.key==='Escape')$('results').replaceChildren();};
$('my').onclick=()=>nav({mode:'knowledge'});$('roadmap').onclick=()=>nav({mode:'roadmap'});$('reset').onclick=()=>nav({});$('back').onclick=parent;
$('in').onclick=()=>{const n=scene.find(n=>['domain','subdomain'].includes(n.type));if(n)action(n);else svg.call(zoom.scaleBy,1.2);};$('out').onclick=parent;
$('previous').onclick=()=>nav({...state,page:state.page-1});$('next').onclick=()=>nav({...state,page:state.page+1});
for(const c of m.courses){const o=text('option',c.title,$('course'));o.value=c.id;}$('course').onchange=()=>nav({course:$('course').value});
const aggregate=m.progress.courses.find(c=>c.course_id===8);
$('totals').textContent=m.statistics.learned+' / '+m.statistics.total+' learned · '+m.statistics.verified+' verified'+(aggregate?' · '+aggregate.applied_topics_count+' / '+aggregate.applied_topics_total+' applied (course 8 aggregate only)':'');
addEventListener('popstate',()=>{state=decode();render();});let timer;addEventListener('resize',()=>{clearTimeout(timer);timer=setTimeout(render,100);});
state=decode();history.replaceState(null,'',url(state));render();performance.mark('km:ready');
})().catch(e=>{const el=document.getElementById('error');el.hidden=false;el.textContent='Serve this folder over HTTP. '+e.message;});
