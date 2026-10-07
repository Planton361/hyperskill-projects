const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium,launchOptions}=require('./browser.cjs');
const base=process.env.SCOPE_URL||'http://127.0.0.1:8810/prototypes/knowledge-atlas-scope-pyramid/';
const sha=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
(async()=>{const browser=await chromium.launch(launchOptions);try{
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:2}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(base);await page.waitForFunction(()=>window.ScopeApp);
 const result=await page.evaluate(()=>{
 const {catalog,scopes}=ScopeApp.state(),before=JSON.stringify(catalog),measure=ScopeApp.measure,all=[],failures=[];
 const check=(v,msg)=>{if(!v)failures.push(msg);},same=(a,b)=>JSON.stringify(a)===JSON.stringify(b),sort=a=>[...a].sort(),eps=.001;
 const rect=n=>({x:n.x-n.width/2,y:n.y,w:n.width,h:n.height,key:n.key}),overlap=(a,b)=>Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>eps&&Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>eps;
 const geom=L=>[L.nodes.map(n=>[n.key,n.x,n.y,n.width,n.height,n.lines]),L.connectorSegments.map(e=>[e.parent,e.children,e.points]),L.trays,L.checkpoint];
 const dist=a=>{a.sort((x,y)=>x-y);return Object.fromEntries(['min','median','p90','p95','max'].map((k,i)=>[k,a[Math.floor((a.length-1)*[0,.5,.9,.95,1][i])]||0]));};
 const cats=new Map(catalog.categories.map(c=>[c.id,c])),topics=new Map(catalog.topics.map(t=>[t.id,t]));
 function independentClosure(s){const ids=new Set(s.explicit_category_ids),queue=[...s.explicit_category_ids,...s.explicit_topic_ids];while(queue.length){for(const p of catalog.memberships[queue.shift()]||[])if(!ids.has(p)){ids.add(p);queue.push(p);}}return [...ids].sort((a,b)=>a-b);}
 function test(s){const start=performance.now(),out=ScopePyramid(s.scope_type,s.scope_id,s.explicit_topic_ids,s.explicit_category_ids,catalog,measure),ms=performance.now()-start,{m,L,projection:p}=out,label=s.scope_type+':'+s.scope_id;
  check(same([...p.explicit_category_ids,...p.context_category_ids].sort((a,b)=>a-b),independentClosure(s)),label+' independent minimal closure');
  const reverse=ScopePyramid(s.scope_type,s.scope_id,[...s.explicit_topic_ids].reverse(),[...s.explicit_category_ids].reverse(),catalog,measure);
  check(same(p,reverse.projection),label+' deterministic projection');check(same(geom(L),geom(reverse.L)),label+' deterministic geometry');
  check(L.nodes.length===1+p.explicit_topic_ids.length+p.explicit_category_ids.length+p.context_category_ids.length,label+' exact node inventory');
  check(new Set(L.nodes.map(n=>n.key)).size===L.nodes.length,label+' no semantic duplication');
  check(m.root.presentationOnly&&!p.semantic_identity[m.root.key]&&m.root.type==='context',label+' presentation nonsemantic');
  check(same(m.root.children.map(n=>n.id),p.used_global_roots),label+' only used roots');
  const expectedEdges=[...m.registry.values()].flatMap(n=>(catalog.memberships[n.id]||[]).map(id=>'category:'+id+'>'+n.key)).sort();check(same(p.hierarchy.map(e=>e.parent+'>'+e.child).sort(),expectedEdges),label+' all structural memberships');
  for(const n of m.registry.values()){check(ScopeProjection.globalTarget(p,n.key)===n.key,label+' exact Global '+n.key);check((n.type==='topic'?topics:cats).get(n.id).title===n.title,label+' title identity');check(n.scopeRole===(n.type==='topic'||p.explicit_category_ids.includes(n.id)?'explicit':'context'),label+' context is not membership');}
  const rs=L.nodes.map(rect),trays=L.trays.map(t=>({x:t.x,y:t.y,w:t.width,h:t.height,key:'tray:'+t.parent,topics:t.topics})),hits=[],routing=[],clipped=[],order=[];
  for(let i=0;i<rs.length;i++)for(let j=i+1;j<rs.length;j++)if(overlap(rs[i],rs[j]))hits.push([rs[i].key,rs[j].key]);
  for(const t of trays){for(const r of rs)if(!t.topics.includes(r.key)&&overlap(t,r))hits.push([t.key,r.key]);for(const key of t.topics){const r=rect(L.byKey.get(key));check(r.x>=t.x-eps&&r.y>=t.y-eps&&r.x+r.w<=t.x+t.w+eps&&r.y+r.h<=t.y+t.h+eps,label+' complete tray');}}
  for(let i=0;i<trays.length;i++)for(let j=i+1;j<trays.length;j++)if(overlap(trays[i],trays[j]))hits.push([trays[i].key,trays[j].key]);
  for(const e of L.connectorSegments){check(e.points.every((p,i,ps)=>!i||p.x===ps[i-1].x||p.y===ps[i-1].y),label+' orthogonal route');for(const r of [...rs,...trays])if(TreeRouting.polylineHits(e.points,[{x:r.x+eps,y:r.y+eps,w:r.w-2*eps,h:r.h-2*eps}]).length)routing.push([e.parent,r.key]);}
  for(const e of L.branches){const a=L.byKey.get(e.parent),b=L.byKey.get(e.child);check(same(e.points[0],{x:a.x,y:a.y+a.height})&&same(e.points.at(-1),{x:b.x,y:b.y}),label+' endpoint');}
  for(const [key,r]of Object.entries(L.checkpoint.categories)){const n=m.nodes.get(key),cats=n.children.filter(c=>c.type==='category');if(!same(r.routes.rows.flatMap(r=>r.keys).filter(k=>k!=='tray'),cats.map(c=>c.key)))order.push(key);
   for(const row of r.routes.rows){const ns=row.keys.filter(k=>k!=='tray').map(k=>L.byKey.get(k));check(ns.every((n,i)=>!i||n.x>ns[i-1].x&&n.y===ns[i-1].y),label+' local sibling alignment');}
   const expected=n.children.filter(AtlasModel.isLeaf).map(c=>c.key);if(!same(L.bands.get(key).columns.flatMap(c=>c.keys),expected))order.push(key);
  }
  for(const n of L.nodes){const topic=n.data.type==='topic',limit=n.width-44;for(const line of n.lines)if(measure(line,n.font,topic?400:n.depth===0?650:600)>limit+eps)clipped.push(n.key);check(n.lines.join(' ')===n.data.title.replace(/\s+/g,' ').trim(),label+' complete title '+n.key);}
  check(!hits.length,label+' zero overlaps '+JSON.stringify(hits.slice(0,3)));check(!routing.length,label+' valid routing '+JSON.stringify(routing.slice(0,3)));check(!clipped.length,label+' no clipping');check(!order.length,label+' canonical order');
  const plan=L.plans.get(m.root.key),w=plan.width+16,h=plan.height+16,k=Math.min(1.3,1392/w,684/h),columns={};for(const t of L.trays){const c=L.bands.get(t.parent).columns.length;columns[c]=(columns[c]||0)+1;}
  const spans=L.branches.map(e=>Math.max(...e.points.map(p=>p.x))-Math.min(...e.points.map(p=>p.x)));for(const t of L.trays){const group=L.routingGroups.get(t.parent),a=L.byKey.get(t.parent);spans.push(Math.max(a.x,t.x+t.width/2,group.spine??a.x)-Math.min(a.x,t.x+t.width/2,group.spine??a.x));}
  all.push({scope:label,synthetic:s.scope_type==='synthetic',explicitTopics:p.explicit_topic_ids.length,explicitCategories:p.explicit_category_ids.length,contextCategories:p.context_category_ids.length,rootCount:p.used_global_roots.length,worldWidth:w,worldHeight:h,aspectRatio:w/h,fitAllScale:k,projectedTopicFont:14*k,trayCount:L.trays.length,trayColumns:columns,connectorSpan:dist(spans),connectorSegmentLength:dist(L.connectorSegments.map(e=>Math.abs(e.points[1].x-e.points[0].x)+Math.abs(e.points[1].y-e.points[0].y))),layoutMs:ms,overlapCount:hits.length,routeCollisionCount:routing.length,clippedTitleCount:clipped.length,orderViolations:order.length,learned:[...m.registry.values()].filter(n=>n.is_learned).length,verified:[...m.registry.values()].filter(n=>n.is_verified).length,geometry:geom(L),semantic:p});
 }
 scopes.forEach(test);
 check(same(all.slice(0,3).map(r=>[r.explicitTopics,r.explicitCategories]),[[89,46],[26,0],[12,0]]),'known evidence counts');
 // Disposable sampling from known identities is a stress fixture, never evidence.
 const owners=new Map(),roots=new Map();function rootOf(id){let p=(catalog.memberships[id]||[])[0];return p==null?id:rootOf(p);}
 for(const t of catalog.topics){const owner=(catalog.memberships[t.id]||[])[0];if(!owners.has(owner))owners.set(owner,[]);owners.get(owner).push(t.id);const root=rootOf(t.id);if(!roots.has(root))roots.set(root,[]);roots.get(root).push(t.id);}
 const branches=[...owners].sort((a,b)=>a[0]-b[0]),rootLists=[...roots].sort((a,b)=>a[0]-b[0]).map(([,ids])=>ids.sort((a,b)=>a-b));
 const spread=count=>{const out=[];for(let i=0;out.length<count;i++)for(const ids of rootLists)if(i<ids.length&&out.length<count)out.push(ids[i]);return out;};
 for(const [id,ids]of [['one',[catalog.topics.slice().sort((a,b)=>b.title.length-a.title.length||a.id-b.id)[0].id]],['five-one-branch',branches.find(([,ids])=>ids.length>=5)[1].slice(0,5)],['twenty-several-branches',spread(20)],['hundred-multiple-roots',spread(100)],['three-hundred',spread(300)]])test({scope_type:'synthetic',scope_id:id,explicit_topic_ids:ids,explicit_category_ids:[]});
 check(all[6].rootCount===5&&all[7].rootCount===5,'synthetic multi-root coverage');
 check(all[4].trayCount===1,'five Topics same branch');
 check(JSON.stringify(catalog)===before,'catalog never mutated');
 check(catalog.categories.length===849&&catalog.topics.length===3106&&catalog.references.length===0,'global full-title foundation');
 check(catalog.progress.topics.filter(p=>p.is_learned).length===31&&catalog.progress.topics.filter(p=>p.is_verified).length===12,'global personal state');
 let unknown=false;try{ScopeProjection.project('synthetic','invalid',[-1],[],catalog);}catch(e){unknown=true;}check(unknown,'reject unknown membership');
 const only=ScopeProjection.project('synthetic','category-only',[],[catalog.categories[0].id],catalog);check(only.explicit_topic_ids.length===0,'Category does not infer Topic membership');
 return{all,failures,foundation:{categories:849,topics:3106,unresolved:0,learned:31,verified:12},checks:'All real and synthetic layouts: exact inventory, independent minimal closure, shuffled-input determinism, semantic uniqueness, full titles, complete memberships, canonical order/alignment, rows/trays/card overlap, orthogonal routes/endpoints/card avoidance, exact identity mapping, unchanged catalog.'};
 });
 for(const r of result.all){r.geometrySha256=sha(r.geometry);delete r.geometry;fs.writeFileSync(path.join(__dirname,r.scope.replace(':','-')+'-semantic.json'),JSON.stringify(r.semantic,null,2)+'\n');delete r.semantic;}
 const dom=[];
 for(const type of ['course','project','stage']){await page.evaluate(type=>ScopeApp.load(ScopeApp.state().scopes.find(s=>s.scope_type===type)),type);
  dom.push(await page.evaluate(()=>{const issues=[];for(const el of document.querySelectorAll('#world .node')){const n=ScopeApp.state().L.byKey.get(el.dataset.key),labels=[...el.querySelectorAll('text')].map(t=>({text:t.textContent,b:t.getBBox()}));for(const {text,b}of labels)if(b.x<0||b.y<0||b.x+b.width>n.width+.01||b.y+b.height>n.height+.01)issues.push([n.key,text,'outside card']);for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){const a=labels[i].b,b=labels[j].b;if(Math.min(a.x+a.width,b.x+b.width)>Math.max(a.x,b.x)+.01&&Math.min(a.y+a.height,b.y+b.height)>Math.max(a.y,b.y)+.01)issues.push([n.key,'text overlap']);}}
  return{type:ScopeApp.state().projection.scope_type,textIssues:issues,rendered:document.querySelectorAll('#world .node').length};}));
  if(process.env.CAPTURE==='1')await page.screenshot({path:path.join(__dirname,type+'-fit-all.png')});
 }
 // Actual search, Inspector, camera and exact-ID Global bridge; never edits Global.
 const beforeNav=await page.evaluate(()=>({builds:ScopeApp.state().builds,L:ScopeApp.state().L.nodes.map(n=>[n.key,n.x,n.y])}));
 await page.locator('#search').fill('36');await page.locator('#search').press('Enter');
 assert.equal(await page.evaluate(()=>ScopeApp.state().selected),'topic:36');
 assert.match(await page.locator('#inspector').innerText(),/Stage requirement/);assert.match(await page.locator('#inspector').innerText(),/Learned/);assert.match(await page.locator('#inspector').innerText(),/Verified/);
 if(process.env.CAPTURE==='1')await page.screenshot({path:path.join(__dirname,'stage-topic-focus-inspector.png')});
 await page.locator('#fit-subtree').click();await page.locator('#fit').click();await page.locator('#in').click();await page.mouse.move(680,400);await page.mouse.down();await page.mouse.move(730,420);await page.mouse.up();await page.locator('#out').click();await page.locator('#minimap').click({position:{x:90,y:56}});
 assert.deepEqual(await page.evaluate(()=>({builds:ScopeApp.state().builds,L:ScopeApp.state().L.nodes.map(n=>[n.key,n.x,n.y])})),beforeNav);
 const bridge=await browser.newPage({viewport:{width:1440,height:900}});for(const key of ['topic:36','category:3']){await bridge.goto(base+'global.html?key='+encodeURIComponent(key));await bridge.waitForFunction(k=>window.resolvedGlobalKey===k,key);assert.equal(await bridge.locator('iframe').evaluate((el)=>el.contentWindow.AtlasV6.state().selected),key);}
 result.dom=dom;result.browserErrors=errors;result.interactions={searchExactId:true,requirementLearnedVerifiedTogether:true,topicFocus:true,subtreeFit:true,fitAll:true,panZoomMinimap:true,noNavigationRelayout:true,actualGlobalTopicAndCategory:true};
 for(const d of dom)if(d.textIssues.length)result.failures.push(d.type+' DOM text issues '+JSON.stringify(d.textIssues));result.failures.push(...errors);
 fs.writeFileSync(path.join(__dirname,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result.all,null,2));console.log('FAILURES',result.failures);assert.deepEqual(result.failures,[]);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
