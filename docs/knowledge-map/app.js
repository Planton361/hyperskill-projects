/* V3 renderer: offline, no session/storage/API requests, no inferred knowledge. */
'use strict';
(async () => {
  const started = performance.now(), response = await fetch('model.json');
  if (!response.ok) throw new Error(`Model HTTP ${response.status}`);
  const model = await response.json(), el = id => document.getElementById(id);
  const nodes = [...model.topics.map(t => ({...t, type:'topic'})),
    ...model.projects.filter(p => ['completed','active'].includes(p.status)).map(p => ({...p,type:'project',cluster_id:'projects'}))];
  const byId = new Map(nodes.map(n => [n.key,n])), clusters = new Map(model.layout_clusters.map(c => [c.id,c]));
  // Same directed endpoints, independent typed evidence: draw once, retain every record.
  const connections = model.connections.filter(c => byId.has(c.source) && byId.has(c.target));
  const degrees = new Map(); connections.forEach(e => [e.source,e.target].forEach(k => degrees.set(k,(degrees.get(k)||0)+1)));
  let mode='knowledge', selected=null, hovered=null, projectConnections=false, current=[], edges=[], ns, es;
  const svg=d3.select('#graph'), world=svg.append('g'), clusterLayer=world.append('g'), edgeLayer=world.append('g'), nodeLayer=world.append('g');
  const defs=svg.append('defs');defs.append('marker').attr('id','arrow').attr('viewBox','0 -5 10 10').attr('refX',14).attr('markerWidth',5).attr('markerHeight',5).attr('orient','auto').append('path').attr('d','M0,-4L9,0L0,4').attr('fill','var(--edge)');
  const cache=new Map(); let transform=d3.zoomIdentity;
  const zoom=d3.zoom().scaleExtent([.08,5]).on('zoom',event=>{transform=event.transform;world.attr('transform',transform);paint();});
  svg.call(zoom).on('dblclick.zoom',null).on('click',()=>choose(null,false));
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  function text(tag,value,parent){const n=document.createElement(tag);n.textContent=value;parent.append(n);return n;}
  function wrap(title){const out=[];let line='';for(const word of title.split(/\s+/)){if(line&&(line+' '+word).length>25){out.push(line);line=word;}else line=line?line+' '+word:word;}if(line)out.push(line);return out;}
  // Rectangle force protects the entire right-offset, multiline label, not only its dot.
  function labelForce(){let items=[];const force=alpha=>{
    const tree=d3.quadtree(items,n=>n.x,n=>n.y);
    for(const a of items)tree.visit((q,x0,y0,x1,y1)=>{
      if(x0>a.x+410||x1<a.x-410||y0>a.y+180||y1<a.y-180)return true;
      if(!q.length)for(let leaf=q;leaf;leaf=leaf.next){const b=leaf.data;if(a.order>=b.order)continue;
        const ax=a.x+a.boxW/2-10,bx=b.x+b.boxW/2-10,dx=ax-bx,dy=a.y-b.y;
        const ox=(a.boxW+b.boxW)/2+16-Math.abs(dx),oy=(a.boxH+b.boxH)/2+17-Math.abs(dy);
        if(ox>0&&oy>0){const strength=Math.max(.15,alpha)*.65;if(ox<oy){const v=(dx>=0?1:-1)*ox*strength;a.vx+=v;b.vx-=v;}else{const v=(dy>=0?1:-1)*oy*strength;a.vy+=v;b.vy-=v;}}
      }return false;
    });
  };force.initialize=items_=>{items=items_;};return force;}
  function layout(items,links){
    const keys=[...new Set(items.map(n=>n.cluster_id))].sort();
    const anchors=new Map(keys.map((key,i)=>{const angle=i*2*Math.PI/keys.length-.8,radius=keys.length>1?180+Math.sqrt(items.length)*6:0;return[key,{x:Math.cos(angle)*radius,y:Math.sin(angle)*radius}];}));
    items.forEach((n,i)=>{n.order=i;n.lines=wrap(n.title);n.boxW=Math.max(...n.lines.map(s=>s.length))*8+30;n.boxH=n.lines.length*18+8;const a=anchors.get(n.cluster_id),j=items.slice(0,i).filter(t=>t.cluster_id===n.cluster_id).length;n.x=a.x+Math.cos(j*2.399963)*Math.sqrt(j+1)*75;n.y=a.y+Math.sin(j*2.399963)*Math.sqrt(j+1)*65;});
    const sim=d3.forceSimulation(items).randomSource(d3.randomLcg(.361)).stop()
      .force('link',d3.forceLink(links.map(e=>({...e}))).id(n=>n.key).distance(120).strength(.025))
      .force('charge',d3.forceManyBody().strength(-90))
      .force('nodeCollision',d3.forceCollide(22))
      .force('clusterX',d3.forceX(n=>anchors.get(n.cluster_id).x).strength(.025))
      .force('clusterY',d3.forceY(n=>anchors.get(n.cluster_id).y).strength(.035))
      .force('labels',labelForce());
    sim.tick(items.length>300?130:240);sim.stop();
    // Fixed deterministic settling without alpha cooling; resolve residual overlaps.
    for(let step=0;step<60;step++){const force=labelForce();force.initialize(items);items.forEach(n=>{n.vx=0;n.vy=0;});force(.7);items.forEach(n=>{n.x+=n.vx;n.y+=n.vy;});}
    return anchors;
  }
  function draw(){
    const begin=performance.now();current=nodes.filter(n=>n.type==='project'||mode==='roadmap'||n.is_learned===true).map(n=>({...n}));
    const ids=new Set(current.map(n=>n.key));edges=connections.filter(e=>ids.has(e.source)&&ids.has(e.target)).map(e=>({...e,type:'knowledge'}));
    if(!cache.has(mode)){layout(current,edges);cache.set(mode,new Map(current.map(n=>[n.key,{x:n.x,y:n.y,boxW:n.boxW,boxH:n.boxH,lines:n.lines}])));}
    current.forEach(n=>Object.assign(n,cache.get(mode).get(n.key)));
    ns=nodeLayer.selectAll('g.node').data(current,n=>n.key).join(enter=>{const g=enter.append('g');g.append('circle').attr('class','focus-ring').attr('r',14);g.append('circle').attr('class','verified-ring').attr('r',9);g.append('path').attr('class','dot');g.append('text').attr('class','label');return g;})
      .attr('class',n=>'node '+n.type).attr('data-key',n=>n.key).attr('data-type',n=>n.type).attr('data-status',n=>n.status||'').attr('data-learned',n=>String(n.is_learned??null)).attr('data-verified',n=>String(n.is_learned===true&&n.is_verified===true))
      .attr('tabindex',0).attr('role','button').attr('aria-label',n=>`${n.title}, ${n.type==='project'?n.status:n.is_learned===true?'learned'+(n.is_verified?' and verified':''):n.is_learned===false?'not learned':'unknown'}`)
      .on('click',(event,n)=>{event.stopPropagation();choose(n.key,false);})
      .on('keydown',(event,n)=>{if(['Enter',' '].includes(event.key)){event.preventDefault();choose(n.key,true);}})
      .on('mouseenter',(_,n)=>{hovered=n.key;paint();}).on('mouseleave',()=>{hovered=null;paint();});
    ns.select('.dot').attr('d',d3.symbol().type(n=>n.type==='project'?d3.symbolDiamond:d3.symbolCircle).size(n=>n.type==='project'?95:45));
    ns.select('.verified-ring').attr('display',n=>n.is_learned===true&&n.is_verified===true?null:'none');
    ns.select('.label').selectAll('tspan').data(n=>n.lines).join('tspan').attr('x',15).attr('y',(_,i)=>i*18+4).text(d=>d);
    ns.call(d3.drag().on('start',event=>event.sourceEvent.stopPropagation()).on('drag',(event,n)=>{n.x=event.x;n.y=event.y;tick();}).on('end',(_,n)=>{cache.get(mode).set(n.key,{x:n.x,y:n.y,boxW:n.boxW,boxH:n.boxH,lines:n.lines});}));
    const groups=d3.groups(current.filter(n=>n.type==='topic'),n=>n.cluster_id);
    const obstacles=current.map(n=>({x:n.x+10,y:n.y-14,w:n.boxW,h:n.boxH}));
    const headings=[];
    for(const [key,items] of groups){
      const lines=wrap(clusters.get(key)?.title||key),w=Math.max(...lines.map(s=>s.length))*11,h=lines.length*23;
      const cx=d3.mean(items,n=>n.x)+45,cy=d3.min(items,n=>n.y)-60;
      let placed;
      for(let ring=0;ring<14&&!placed;ring++)for(let slot=0;slot<(ring?12:1);slot++){
        const angle=slot*Math.PI/6,x=cx+Math.cos(angle)*ring*30,y=cy+Math.sin(angle)*ring*30;
        const box={x:x-w/2,y:y-18,w,h};
        if(!obstacles.some(b=>box.x<b.x+b.w+12&&box.x+box.w+12>b.x&&box.y<b.y+b.h+12&&box.y+box.h+12>b.y)){
          placed={key,x,y,w,h,lines};obstacles.push(box);break;
        }
      }
      if(placed)headings.push(placed); // A missing caption is preferable to masking topic knowledge.
    }
    clusterLayer.selectAll('text').data(headings,g=>g.key).join('text').attr('class','cluster-label').attr('x',g=>g.x).attr('y',g=>g.y).attr('text-anchor','middle')
      .selectAll('tspan').data(g=>g.lines.map((line,i)=>({line,x:g.x,i}))).join('tspan').attr('x',d=>d.x).attr('dy',d=>d.i?23:0).text(d=>d.line);
    svg.node().clusterBounds=headings;
    renderEdges();tick();fit();paint();
    el('coverage').textContent=`${mode==='knowledge'?'My Knowledge':'Course Roadmap'} · ${current.filter(n=>n.type==='topic').length} topics · ${current.filter(n=>n.is_learned===true).length} learned · ${current.filter(n=>n.is_learned===true&&n.is_verified===true).length} verified · ${edges.length} knowledge connections`;
    svg.attr('data-ready','true').attr('data-mode',mode).attr('data-render-ms',(performance.now()-begin).toFixed(2));
  }
  function renderEdges(){
    const shown=[...edges];if(selected?.startsWith('project:')&&projectConnections){const ids=new Set(current.map(n=>n.key));for(const e of model.edges.filter(e=>e.type==='project_requires'&&e.source===selected&&ids.has(e.target)))shown.push({...e,records:[e]});}
    es=edgeLayer.selectAll('line').data(shown,e=>`${e.source}|${e.target}|${e.type}`).join('line').attr('class',e=>'edge'+(e.type==='project_requires'?' requires':''))
      .attr('data-source',e=>e.source).attr('data-target',e=>e.target).attr('data-type',e=>e.type).attr('marker-end','url(#arrow)').attr('vector-effect','non-scaling-stroke');
    es.selectAll('title').data(e=>[e]).join('title').text(e=>e.type==='project_requires'?'project_requires (not project_applies)':'prerequisite → dependent; '+e.records.map(r=>r.type).join(' / '));
  }
  function tick(){const lookup=new Map(current.map(n=>[n.key,n]));ns.attr('transform',n=>`translate(${n.x},${n.y})`);es.attr('x1',e=>lookup.get(e.source).x).attr('y1',e=>lookup.get(e.source).y).attr('x2',e=>lookup.get(e.target).x).attr('y2',e=>lookup.get(e.target).y);}
  function paint(){if(!ns)return;const focus=hovered||selected, adjacent=new Set(focus?[focus]:[]);
    if(focus?.startsWith('topic:'))connections.forEach(e=>{if(e.source===focus)adjacent.add(e.target);if(e.target===focus)adjacent.add(e.source);});
    if(focus?.startsWith('project:')&&projectConnections)model.edges.filter(e=>e.type==='project_requires'&&e.source===focus).forEach(e=>adjacent.add(e.target));
    ns.classed('selected',n=>n.key===selected).classed('neighbor',n=>adjacent.has(n.key)&&n.key!==focus).classed('dim',n=>!!focus&&!adjacent.has(n.key));
    // Deterministic LOD; no scene replacement. All 31 learned labels always stay present.
    const visible = n=>n.type==='project'||n.is_learned===true||n.key===selected||n.key===hovered||
      (transform.k>=1.15&&inViewport(n))||(transform.k>=.65&&inViewport(n)&&((degrees.get(n.key)||0)>=3))||
      (transform.k<.65&&(degrees.get(n.key)||0)>=7);
    ns.select('.label').attr('display',n=>visible(n)?null:'none');
    // Close zoom magnifies space, not labels without bound; preserve readability.
    const shrink=Math.min(1,1.25/transform.k);
    ns.select('.label').attr('transform',`scale(${shrink})`);
    es.classed('highlight',e=>!!focus&&(e.source===focus||e.target===focus)).classed('dim',e=>!!focus&&e.source!==focus&&e.target!==focus);
    clusterLayer.attr('opacity',transform.k>1.3?.15:1);
  }
  function inViewport(n){const r=el('canvas').getBoundingClientRect(),x=transform.applyX(n.x),y=transform.applyY(n.y);return x>-100&&x<r.width+100&&y>-100&&y<r.height+100;}
  function move(t){svg.call(zoom.transform,t);}
  function fit(){if(!current.length)return;const r=el('canvas').getBoundingClientRect(),headings=svg.node().clusterBounds||[];const x0=Math.min(d3.min(current,n=>n.x)-35,...headings.map(h=>h.x-h.w/2-20)),y0=Math.min(d3.min(current,n=>n.y)-35,...headings.map(h=>h.y-30)),x1=Math.max(d3.max(current,n=>n.x+n.boxW)+20,...headings.map(h=>h.x+h.w/2+20)),y1=Math.max(d3.max(current,n=>n.y+n.boxH)+20,...headings.map(h=>h.y+h.h+20));const k=Math.min(1.4,(r.width-35)/(x1-x0),(r.height-35)/(y1-y0));move(d3.zoomIdentity.translate(r.width/2,r.height/2).scale(k).translate(-(x0+x1)/2,-(y0+y1)/2));}
  function choose(key,center=true){
    const n=byId.get(key);if(n&&n.type==='topic'&&n.is_learned!==true&&mode==='knowledge')setMode('roadmap');
    selected=key;hovered=null;projectConnections=false;renderEdges();tick();paint();details();
    if(center&&key){const node=current.find(n=>n.key===key),r=el('canvas').getBoundingClientRect();move(d3.zoomIdentity.translate(r.width/2,r.height/2).scale(Math.max(1.1,transform.k)).translate(-node.x,-node.y));}
    svg.attr('data-selected',key||'');
  }
  function details(){const panel=el('details');panel.replaceChildren();const n=byId.get(selected);
    if(!n){text('h2','Connected knowledge',panel);text('p','Select a topic to see its prerequisites and dependents. Projects are separate evidence, not topic-level application claims.',panel);return;}
    text('h2',n.title,panel);
    if(n.type==='topic'){
      text('p',n.is_learned===true?'● Learned (explicit)':n.is_learned===false?'○ Not learned (explicit)':'○ Learning status unknown',panel);
      text('p',n.is_verified===true?'◎ Verified — additional evidence':`Verification: ${n.verification_status??'unknown'} (separate from learned status)`,panel);
      for(const [label,predicate,other] of [['Prerequisites',e=>e.target===n.key,e=>e.source],['Dependents',e=>e.source===n.key,e=>e.target]]){
        text('h3',label,panel);const related=connections.filter(predicate);if(!related.length)text('p','No recorded connections.',panel);
        const ul=text('ul','',panel);for(const edge of related){const li=text('li','',ul),b=text('button',byId.get(other(edge)).title,li);b.onclick=()=>choose(other(edge));}
      }
    }else{
      text('p',`Status: ${n.status}`,panel);text('p',`Required topics: ${n.required_topic_ids?.length??'unknown'}`,panel);
      text('p',`Completed stages: ${n.completed_stage_ids===null?'unknown':n.completed_stage_ids.length}`,panel);
      text('p',`Known stage metadata: ${model.stages.filter(s=>s.project_id===n.id).length}`,panel);
      const b=text('button',projectConnections?'Hide project connections':'Show project connections',panel);b.setAttribute('aria-pressed',String(projectConnections));b.disabled=!n.required_topic_ids;
      b.onclick=()=>{projectConnections=!projectConnections;renderEdges();tick();paint();details();};
      text('p','Project requirements are not proof of topic-level application.',panel);
    }
    const a=text('a','Open on Hyperskill ↗',panel);a.href=n.url;a.target='_blank';a.rel='noopener noreferrer';
    const advanced=text('details','',panel);text('summary','Advanced / Evidence',advanced);
    const records=model.edges.filter(e=>e.source===n.key||e.target===n.key),refs=new Set([...n.evidence_ids,...(n.progress_evidence_ids||[]),...records.flatMap(e=>e.evidence_ids)]);
    text('pre',JSON.stringify({entity:n.key,evidence_ids:n.evidence_ids,progress_evidence_ids:n.progress_evidence_ids,records,sources:model.evidence.filter(e=>refs.has(e.id))},null,2),advanced);
  }
  function setMode(value){mode=value;selected=null;hovered=null;projectConnections=false;el('my').setAttribute('aria-pressed',String(mode==='knowledge'));el('roadmap').setAttribute('aria-pressed',String(mode==='roadmap'));draw();details();}
  el('my').onclick=()=>setMode('knowledge');el('roadmap').onclick=()=>setMode('roadmap');el('fit').onclick=fit;el('clear').onclick=()=>choose(null,false);
  el('closer').onclick=()=>svg.call(zoom.scaleBy,Math.max(1.7,.95/transform.k));
  el('search').addEventListener('input',()=>{const t=performance.now(),query=el('search').value.trim().toLowerCase(),result=el('results');result.replaceChildren();if(query){const matches=nodes.filter(n=>n.title.toLowerCase().includes(query)).slice(0,15);for(const n of matches){const b=text('button',n.title,result);b.onclick=()=>{choose(n.key);result.replaceChildren();};}if(!matches.length)text('p','No matching topics or projects.',result);}result.dataset.responseMs=(performance.now()-t).toFixed(2);});
  el('search').addEventListener('keydown',e=>{if(e.key==='ArrowDown'){e.preventDefault();el('results').querySelector('button')?.focus();}if(e.key==='Enter')el('results').querySelector('button')?.click();});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')choose(null,false);});
  new ResizeObserver(()=>{if(current.length)fit();}).observe(el('canvas'));
  const p=model.progress.courses[0];el('metrics').textContent=`${p.learned_topics_count} / ${p.learned_topics_total} learned · ${model.statistics.verified} verified · ${p.applied_topics_count} / ${p.applied_topics_total} applied (aggregate only)`;
  draw();details();svg.attr('data-initial-ms',(performance.now()-started).toFixed(2));svg.attr('data-reduced-motion',String(reduced));
})().catch(error=>{const node=document.getElementById('error');node.hidden=false;node.textContent=`Unable to load prototype: ${error.message}. Serve the repository root over HTTP.`;console.error(error);});
