/* Renderer only: no Hyperskill requests, credentials, storage, or inferred progress. */
'use strict';
(async function () {
  const response = await fetch('graph.json');
  if (!response.ok) throw new Error(`Graph snapshot unavailable (${response.status})`);
  const graph = await response.json();
  if (!window.d3) throw new Error('Local D3 library unavailable');
  const byId = new Map(graph.nodes.map(n => [n.id, n]));
  const evidence = new Map(graph.evidence.map(e => [e.id, e]));
  const progress = graph.progress.courses[0];
  const el = id => document.getElementById(id);
  const text = (tag, value, parent) => { const n=document.createElement(tag); n.textContent=value; parent.append(n); return n; };
  el('metrics').textContent = `${progress.learned_topics_count} / ${progress.learned_topics_total} learned · ${progress.applied_topics_count} / ${progress.applied_topics_total} applied (aggregate only)`;
  const colors = {course:'#c9afff',category:'#818da9',unknown:'#647087',not_learned:'#647087',learned:'#79dcb4',completed:'#79dcb4',active:'#efbb79',available:'#9aa8ed'};
  const svg=d3.select('#graph'), world=svg.append('g'), edgeLayer=world.append('g'), nodeLayer=world.append('g');
  let mode='roadmap', selected=null, hovered=null, nodeSelection, edgeSelection, visibleNodes=[], simulation;
  function screenSizes(k){
    if(!nodeSelection)return;
    nodeSelection.select('.mark').attr('transform',`scale(${1/k})`).attr('vector-effect','non-scaling-stroke');
    nodeSelection.select('circle').attr('r',13/k);
    nodeSelection.select('text').style('font-size',`${12/k}px`).style('stroke-width',`${4/k}px`).attr('x',13/k).attr('y',4/k);
  }
  const zoom=d3.zoom().scaleExtent([.15,5]).on('zoom', e => {world.attr('transform',e.transform);screenSizes(e.transform.k);});
  svg.call(zoom).on('dblclick.zoom',null);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  // prerequisite and dependent are independent evidence for the same direction.
  // Draw one segment while retaining all typed records for inspection.
  const grouped = new Map();
  graph.edges.forEach(e => { const key=`${e.source}|${e.target}`; if(!grouped.has(key))grouped.set(key,{source:e.source,target:e.target,records:[]});grouped.get(key).records.push(e); });
  const links=[...grouped.values()];
  const endpoint = x => typeof x==='object'?x.id:x;
  function visibleIds() {
    if(mode==='roadmap')return new Set(byId.keys());
    const ids=new Set(graph.nodes.filter(n=>n.type==='course'||n.status==='learned'||['completed','active'].includes(n.status)).map(n=>n.id));
    let changed=true;
    while(changed){changed=false;graph.edges.filter(e=>e.type==='hierarchy').forEach(e=>{if(ids.has(e.target)&&!ids.has(e.source)){ids.add(e.source);changed=true;}});}
    return ids;
  }
  function paint() {
    const focus=hovered||selected, neighbors=new Set(focus?[focus]:[]);
    if(focus)graph.edges.forEach(e=>{if(e.source===focus)neighbors.add(e.target);if(e.target===focus)neighbors.add(e.source);});
    nodeSelection.classed('dim',n=>focus&&!neighbors.has(n.id)).classed('selected',n=>n.id===selected);
    nodeSelection.select('text').attr('display',n=>n.id===focus||n.id===selected||['completed','active'].includes(n.status)||n.type==='course'?null:'none');
    edgeSelection.classed('dim',e=>focus&&endpoint(e.source)!==focus&&endpoint(e.target)!==focus).classed('highlight',e=>focus&&(endpoint(e.source)===focus||endpoint(e.target)===focus));
  }
  function showDetails(id) {
    const panel=el('details');panel.replaceChildren();const node=byId.get(id);
    if(!node){text('h2','A map, not a claim',panel);text('p','Select a topic or project. Required topics are not automatically applied topics.',panel);return;}
    text('h2',node.title,panel);text('small',`${node.type} · Hyperskill ${node.hyperskill_id}`,panel);
    if(node.type==='project'){
      text('p',`Status: ${node.status[0].toUpperCase()+node.status.slice(1)}`,panel);
      text('p',node.required_topics_count===null?'Required topics: not loaded':`Required topics: ${node.required_topics_count}`,panel);
      if(node.completed_stage_ids!==null)text('p',`Completed stages: ${node.completed_stage_ids.length}`,panel);
      text('small','Available means listed in the course, not a verified personal access entitlement.',panel);
    } else if(node.type==='topic') {
      text('p',node.status==='learned'?'Learned':node.status==='not_learned'?'Not learned (explicit)':'Knowledge status: unknown',panel);
      text('p',`Verification: ${node.verification_status ?? 'unknown'}`,panel);
      text('p',node.applied===true?'Applied: explicitly evidenced':node.applied===false?'Applied: explicitly not applied':'Applied: unknown',panel);
    }
    const a=text('a','Open on Hyperskill ↗',panel);a.href=node.url;a.target='_blank';a.rel='noopener noreferrer';
    const edges=graph.edges.filter(e=>e.source===id||e.target===id);
    const groups=d3.group(edges,e=>e.type);
    for(const [type,records] of groups){
      text('h3',`${type} (${records.length})`,panel);const list=text('ul','',panel);
      records.forEach(e=>{const target=e.source===id?e.target:e.source;const li=text('li','',list);const b=text('button',`${e.source===id?'→':'←'} ${byId.get(target).title}`,li);b.onclick=()=>choose(target);b.title=`${e.type}; evidence: ${e.evidence_ids.join(', ')}`;});
    }
    text('h3','Evidence',panel);
    const refs=new Set([...node.evidence_ids,...(node.progress_evidence_ids||[]),...edges.flatMap(e=>e.evidence_ids)]);
    for(const ref of refs){const item=evidence.get(ref);const p=text('p','',panel);text('small',`${ref} · ${item.confidence} · ${item.method} · ${item.observed_on}`,p);if(item.url){const link=text('a','Source JSON',p);link.href=item.url;link.target='_blank';link.rel='noopener noreferrer';}if(item.note)text('small',item.note,p);}
  }
  function choose(id){
    if(id&&!visibleIds().has(id))setMode('roadmap');
    selected=id;hovered=null;el('tooltip').hidden=true;showDetails(id);paint();
  }
  function fit(){
    const rect=el('canvas').getBoundingClientRect();
    const xs=d3.extent(visibleNodes,n=>n.x),ys=d3.extent(visibleNodes,n=>n.y);
    const scale=Math.max(.15,Math.min(1.4,(rect.width-100)/(xs[1]-xs[0]+1),(rect.height-90)/(ys[1]-ys[0]+1)));
    svg.call(zoom.transform,d3.zoomIdentity.translate(rect.width/2,rect.height/2).scale(scale).translate(-(xs[0]+xs[1])/2,-(ys[0]+ys[1])/2));
  }
  function draw(){
    simulation?.stop();const ids=visibleIds();visibleNodes=graph.nodes.filter(n=>ids.has(n.id));
    const visibleLinks=links.filter(e=>ids.has(endpoint(e.source))&&ids.has(endpoint(e.target))).map(e=>({...e,source:endpoint(e.source),target:endpoint(e.target)}));
    edgeSelection=edgeLayer.selectAll('line').data(visibleLinks,e=>`${endpoint(e.source)}|${endpoint(e.target)}`).join('line').attr('vector-effect','non-scaling-stroke').attr('class',e=>`edge${e.records.some(r=>r.type==='project_requires')?' requires':''}`);
    edgeSelection.selectAll('title').data(e=>[e]).join('title').text(e=>e.records.map(r=>r.type).join(' / '));
    nodeSelection=nodeLayer.selectAll('g.node').data(visibleNodes,n=>n.id).join(enter=>{const g=enter.append('g').attr('class','node');g.append('circle').attr('r',13).attr('fill','transparent');g.append('path').attr('class','mark');g.append('text').attr('x',13).attr('y',4);return g;})
      .attr('data-id',n=>n.id).attr('tabindex',0).attr('role','button').attr('aria-label',n=>`${n.title}, ${n.type}, ${n.status||'structural'}`)
      .on('click',(event,n)=>{event.stopPropagation();choose(n.id);})
      .on('keydown',(event,n)=>{if(['Enter',' '].includes(event.key)){event.preventDefault();choose(n.id);}})
      .on('mouseenter',(_,n)=>{hovered=n.id;el('tooltip').textContent=`${n.title} · ${n.status||n.type}`;el('tooltip').hidden=false;paint();})
      .on('mouseleave',()=>{hovered=null;el('tooltip').hidden=true;paint();});
    nodeSelection.select('.mark').attr('d',d3.symbol().type(n=>n.type==='project'?d3.symbolSquare:n.type==='course'?d3.symbolDiamond:d3.symbolCircle).size(n=>n.type==='topic'?45:n.type==='category'?65:115))
      .attr('fill',n=>n.type==='category'||n.status==='available'?'#101319':colors[n.status||n.type]).attr('stroke',n=>colors[n.status||n.type]);
    nodeSelection.select('text').text(n=>n.title);
    function tick(){edgeSelection.attr('x1',e=>e.source.x).attr('y1',e=>e.source.y).attr('x2',e=>e.target.x).attr('y2',e=>e.target.y);nodeSelection.attr('transform',n=>`translate(${n.x},${n.y})`);}
    simulation=d3.forceSimulation(visibleNodes).randomSource(d3.randomLcg(.42)).force('link',d3.forceLink(visibleLinks).id(n=>n.id).distance(65).strength(.12)).force('charge',d3.forceManyBody().strength(-80)).force('collision',d3.forceCollide(13)).force('x',d3.forceX(0).strength(.012)).force('y',d3.forceY(0).strength(.012)).alpha(.12).on('tick',tick);
    nodeSelection.call(d3.drag().on('start',(event,n)=>{if(!event.active&&!reduced)simulation.alphaTarget(.12).restart();n.fx=n.x;n.fy=n.y;}).on('drag',(event,n)=>{n.fx=event.x;n.fy=event.y;n.x=event.x;n.y=event.y;tick();}).on('end',(event,n)=>{simulation.alphaTarget(0);n.fx=null;n.fy=null;}));
    if(reduced)simulation.stop();tick();paint();fit();
    const learned=graph.progress.topics.filter(n=>n.is_learned===true).length;
    const verified=graph.progress.topics.filter(n=>n.is_verified===true).length;
    const complete=progress.topic_status_coverage==='complete';
    el('coverage').textContent=mode==='roadmap'
      ? `${graph.nodes.filter(n=>n.type==='topic').length} course topics · ${learned} learned · ${verified} verified · Learned coverage: ${complete?'complete':'partial'} · Applied IDs unknown`
      : `My Knowledge: ${learned} explicitly learned topics (${verified} verified), completed/active projects and category context.${complete?'':' Other learned IDs are unknown.'}`;
  }
  function setMode(value){mode=value;selected=null;hovered=null;el('roadmap').setAttribute('aria-pressed',String(mode==='roadmap'));el('knowledge').setAttribute('aria-pressed',String(mode==='knowledge'));draw();showDetails(null);}
  el('roadmap').onclick=()=>setMode('roadmap');el('knowledge').onclick=()=>setMode('knowledge');el('fit').onclick=fit;el('clear').onclick=()=>choose(null);
  svg.on('click',()=>choose(null));document.addEventListener('keydown',e=>{if(e.key==='Escape')choose(null);});
  el('search').addEventListener('input',()=>{
    const query=el('search').value.trim().toLocaleLowerCase(),results=el('results');results.replaceChildren();if(!query)return;
    const matches=graph.nodes.filter(n=>['topic','project'].includes(n.type)&&n.title.toLocaleLowerCase().includes(query));
    if(!matches.length)text('span','No matching topics or projects.',results);
    matches.forEach(n=>{const b=text('button',`${n.title} · ${n.type}`,results);b.onclick=()=>choose(n.id);});
  });
  new ResizeObserver(()=>fit()).observe(el('canvas'));
  draw();
})().catch(error=>{const el=document.getElementById('error');el.hidden=false;el.textContent=`Unable to load the graph: ${error.message}. Serve this directory over HTTP; for example: python3 -m http.server 8000 --directory docs`;});
