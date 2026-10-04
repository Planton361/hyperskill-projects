/* Candidate/public V6 regression. No repository writes; reports/screenshots are opt-in. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const root=path.resolve(input.root),preview=path.join(root,'docs/knowledge-atlas-preview');
const candidateURL=input.url||'http://atlas.invalid/hyperskill-projects/knowledge-map/';
const referenceURL='http://atlas.invalid/hyperskill-projects/knowledge-atlas-preview/';
const widths=input.widths||[1920,1440,1280,1200,1024,768,430,390,320];
const checks=[],runs=[];
function check(ok,name){assert.ok(ok,name);checks.push(name);}
async function scene(page){return page.evaluate(()=>{
 const s=AtlasV6.state(),round=v=>Math.round(v*1e6)/1e6;
 // Compare exact node geometry and rendered SVG text metrics, rather than the
 // binary spelling of a derived line-height (font * 1.18).
 return {theme:document.body.classList.contains('light')?'light':'dark',palette:[getComputedStyle(document.body).backgroundColor,getComputedStyle(document.body).color],
   nodes:s.L.nodes.map(n=>[n.key,n.x,n.y,n.width,n.height,n.font,n.lines]).sort((a,b)=>a[0].localeCompare(b[0])),
   trays:s.L.trays.map(t=>[t.parent,t.x,t.y,t.width,t.height,t.topics]).sort((a,b)=>a[0].localeCompare(b[0])),
   hierarchy:[...document.querySelectorAll('.taxonomy')].map(p=>[p.getAttribute('d'),p.getAttribute('class')]).sort(),
   rows:[...document.querySelectorAll('.node')].map(n=>[n.dataset.key,n.getAttribute('class'),n.textContent]).sort(),
   text:[...document.querySelectorAll('.node')].map(n=>[n.dataset.key,[...n.querySelectorAll('text')].map(t=>{const b=t.getBBox();return [t.textContent,b.x,b.y,b.width,b.height,getComputedStyle(t).fontFamily,getComputedStyle(t).fontSize];})]).sort(),
   selected:s.selected,mode:s.mode,view:s.viewState,transform:[s.transform.x,s.transform.y,s.transform.k].map(round),
   inspector:document.querySelector('#inspector').innerText,focused:s.focusedRelation?.key||null,
   relations:s.relationProjection?.routes.map(r=>[r.key,r.type,r.source,r.target,r.lca,r.path,r.sameTray]).sort()||[]};
 });}
async function route(page,reference){
 if(reference||!input.url)await page.route('**/*',request=>{
   const u=new URL(request.request().url()),base=reference?referenceURL:candidateURL;
   if(!u.href.startsWith(base))return request.abort();
   const name=decodeURIComponent(u.pathname.slice(new URL(base).pathname.length))||'index.html';
   if(name.includes('..'))return request.abort();
   const p=path.join(preview,name),body=reference?(fs.existsSync(p)?fs.readFileSync(p):null):input.assets[name];
   if(body==null)return request.abort();
   return request.fulfill({body,contentType:name.endsWith('.js')?'application/javascript':name.endsWith('.json')?'application/json':name.endsWith('.css')?'text/css':'text/html'});
 });
}
async function exercise(page,width,theme,reference){
 const errors=[],failed=[],requested=[];page.on('pageerror',e=>errors.push(e.message));
 page.on('requestfailed',r=>failed.push(r.url()));page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('favicon.ico'))failed.push(r.status()+' '+r.url());});
 page.on('request',r=>requested.push(r.url()));await route(page,reference);
 const response=await page.goto(reference?referenceURL:candidateURL);check(response.status()===200,'HTTP 200 '+width+' '+theme);
 await page.waitForFunction(()=>window.AtlasV6);await page.waitForFunction(()=>!AtlasV6.state().transitioning);
 if(await page.evaluate(()=>document.body.classList.contains('light'))!==(theme==='light'))await page.click('#theme');
 check(await page.evaluate(t=>document.body.classList.contains('light')===(t==='light'),theme),'requested theme '+theme);
 if(!reference)check(await page.title()==='Knowledge Atlas'&&await page.locator('h1').innerText()==='Knowledge Atlas','production branding '+width+' '+theme);
 const initial=await page.evaluate(()=>{const s=AtlasV6.state();return {cp:JSON.stringify(s.L.checkpoint),coords:JSON.stringify(s.L.nodes.map(n=>[n.key,n.x,n.y,n.width,n.height])),layout:s.metrics.layout};});
 const snapshots=[];const capture=async name=>snapshots.push({name,value:await scene(page)});
 const wait=()=>page.waitForFunction(()=>!AtlasV6.state().transitioning);
 const search=async text=>{await page.fill('#search',text);await page.press('#search','Enter');await wait();};
 await capture('overview');
 check(await page.evaluate(()=>{const s=AtlasV6.state();return document.querySelectorAll('.node.topic').length===s.m.raw.topics.length&&document.querySelectorAll('.node.category').length===s.m.raw.categories.length;}),'complete taxonomy '+width+' '+theme);
 check(await page.locator('.knowledge').count()===0,'no free knowledge paths '+width+' '+theme);
 for(const title of ['Java','Basics']){await search(title);check(await page.evaluate(title=>{const s=AtlasV6.state();return s.m.nodes.get(s.selected).title===title&&s.fitIntent.kind==='subtree';},title),'category navigation '+title);await capture(title);}
 await search('For loop');check(await page.evaluate(()=>AtlasV6.state().viewState==='topic'&&AtlasV6.state().transform.k*14>=13),'For loop focus');await capture('topic focus');
 for(const type of ['Prerequisite','Dependent']){
   const button=page.locator('[data-relation][aria-label^="'+type+':"]').first();check(await button.count()>0,type+' available');
   const key=await button.getAttribute('data-relation');await button.hover();
   check(await page.evaluate(k=>AtlasV6.state().previewRelation===k,key),'relation hover '+type);
   await button.focus();await button.click();await wait();
   check(await page.evaluate(k=>AtlasV6.state().focusedRelation?.key===k,key),'relation focus '+type);
   check(await page.locator('.knowledge').count()===0,'taxonomy LCA route '+type);await capture(type+' focus');
   await button.press('Escape');check(await page.evaluate(()=>!AtlasV6.state().focusedRelation),'relation keyboard Escape');
 }
 const local=await page.evaluate(()=>{const s=AtlasV6.state();return s.m.connections.find(e=>s.relationIndex.route(e).sameTray)?.key;});
 if(local){await page.evaluate(key=>{const s=AtlasV6.state(),e=s.m.connections.find(e=>e.key===key);AtlasV6.select(e.source,true);AtlasV6.focusRelation(key);},local);await wait();check(await page.evaluate(()=>AtlasV6.state().relationProjection.focused.sameTray&&!document.querySelector('.knowledge')),'same-tray emphasis');await capture('same tray');}
 await page.click('#clear');await page.click('#fit');await wait();
 await page.locator('[data-select="project:113"]').first().click();await wait();
 const required=await page.evaluate(()=>AtlasModel.projectRequirements(AtlasV6.state().m,'project:113').size);
 check(await page.locator('.node.topic.covered').count()===required,'Project 113 derived coverage');await capture('project');
 await page.click('#coverage');await page.click('#coverage');check(await page.locator('.node.topic.covered').count()===required,'show coverage');
 await page.click('#fit-coverage');await wait();await capture('coverage fit');
 const stage=page.locator('[data-stage]').filter({hasText:'Stage 4'});await stage.click();
 const explicit=await page.evaluate(()=>{const s=AtlasV6.state();return AtlasModel.projectRequirements(s.m,'project:113',s.coverage.stageId).size;});
 check(await page.locator('.node.topic.covered').count()===explicit,'Stage 4 explicit coverage');await capture('stage 4');
 await page.click('#roadmap');await capture('roadmap');await page.click('#my');await capture('my knowledge');
 const beforeTheme=await page.evaluate(()=>{const s=AtlasV6.state();return [s.selected,s.transform.x,s.transform.y,s.transform.k];});
 await page.click('#theme');check(await page.evaluate(t=>document.body.classList.contains('light')!==(t==='light'),theme),'theme toggle');
 await page.click('#theme');assert.deepEqual(await page.evaluate(()=>{const s=AtlasV6.state();return [s.selected,s.transform.x,s.transform.y,s.transform.k];}),beforeTheme);check(true,'theme preserves navigation');
 check(await page.evaluate(()=>{const mini=document.querySelector('#minimap');return innerWidth<=700?getComputedStyle(mini).display==='none':getComputedStyle(mini).display!=='none'&&!!mini.querySelector('.mini-viewport');}),'minimap responsive');
 await search('For loop');await page.locator('.node.selected').focus();await page.keyboard.press('Enter');await wait();check(await page.evaluate(()=>AtlasV6.state().viewState==='topic'),'keyboard topic focus');
 if(width<=430){
   await page.locator('#graph').scrollIntoViewIfNeeded();const box=await page.locator('#graph').boundingBox(),x=box.x+box.width/2,y=box.y+box.height/2;
   const session=await page.context().newCDPSession(page),before=await page.evaluate(()=>AtlasV6.state().transform.k);
   await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:x-30,y,id:1},{x:x+30,y,id:2}]});
   await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x-60,y,id:1},{x:x+60,y,id:2}]});
   await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});check(await page.evaluate(k=>AtlasV6.state().transform.k>k,before),'emulated pinch '+width);
   const previous=await page.evaluate(()=>AtlasV6.state().transform.x);
   await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:3}]});
   await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+30,y:y+20,id:3}]});
   await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});check(await page.evaluate(x=>AtlasV6.state().transform.x!==x,previous),'emulated pan '+width);
 }
 await page.click('#clear');await page.click('#fit');await wait();
 check(await page.evaluate(()=>matchMedia('(prefers-reduced-motion: reduce)').matches&&!AtlasV6.state().transitioning),'reduced motion');
 check(await page.evaluate(()=>{const a=document.querySelector('aside').getBoundingClientRect(),g=document.querySelector('#graph').getBoundingClientRect();return document.documentElement.scrollWidth<=innerWidth&&(innerWidth>1200?a.left>=g.right:a.top>=g.bottom);}), 'no overflow / inspector position '+width);
 check(await page.evaluate(b=>{const s=AtlasV6.state();return JSON.stringify(s.L.checkpoint)===b.cp&&JSON.stringify(s.L.nodes.map(n=>[n.key,n.x,n.y,n.width,n.height]))===b.coords&&s.metrics.layout===b.layout;},initial),'immutable geometry/checkpoint during all actions');
 await page.reload();await page.waitForFunction(()=>window.AtlasV6);await wait();
 check(await page.evaluate(b=>JSON.stringify(AtlasV6.state().L.nodes.map(n=>[n.key,n.x,n.y,n.width,n.height]))===b.coords,initial),'reload geometry');
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 check(requested.every(url=>new URL(url).origin===new URL(reference?referenceURL:candidateURL).origin),'subpath-only requests');
 if(input.screenshots&&!reference&&((width===1920&&theme==='dark')||(width===1440&&theme==='light')||(width===390&&theme==='dark'))){
   // Accepted V6 intentionally starts in dark after reload; screenshot the
   // requested theme again without changing that runtime behavior.
   if(theme==='light')await page.click('#theme');
   fs.mkdirSync(input.screenshots,{recursive:true});await page.screenshot({path:path.join(input.screenshots,width+'-'+theme+'-overview.png')});
 }
 return {snapshots,required,explicit,errors,failed};
}
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
 try{
  const model=input.assets?JSON.parse(input.assets['model.json']):await (await fetch(candidateURL+'model.json')).json();
  const cp=input.assets?JSON.parse(input.assets['layout-checkpoint.json']):await (await fetch(candidateURL+'layout-checkpoint.json')).json();
  const reference=JSON.parse(fs.readFileSync(path.join(preview,'model.json')));
  const tables=['courses','categories','topics','projects','stages','edges','progress','evidence'];
  const canonical=x=>Array.isArray(x)?x.map(canonical).sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b))):x&&typeof x==='object'?Object.fromEntries(Object.entries(x).sort().map(([k,v])=>[k,canonical(v)])):x;
  const comparable=cp.presentation_generation===0&&JSON.stringify(canonical(Object.fromEntries(tables.map(k=>[k,model[k]]))))===JSON.stringify(canonical(Object.fromEntries(tables.map(k=>[k,reference[k]]))));
  for(const width of widths)for(const theme of ['dark','light']){
   const options={viewport:{width,height:width===1920?1080:width<=430?844:900},locale:'en-US',deviceScaleFactor:1,reducedMotion:'reduce',hasTouch:width<=430,isMobile:width<=430};
   const page=await browser.newPage(options);const result=await exercise(page,width,theme,false);await page.close();
   if(comparable){const p=await browser.newPage(options);const baseline=await exercise(p,width,theme,true);await p.close();assert.deepEqual(result.snapshots,baseline.snapshots,'accepted Preview differential '+width+' '+theme);check(true,'accepted Preview scenes identical '+width+' '+theme);}
   runs.push({width,theme,project_requirements:result.required,stage4_requirements:result.explicit,scene_hash:hash(JSON.stringify(result.snapshots)),errors:result.errors,failed:result.failed});
  }
  const p=await browser.newPage({viewport:{width:1920,height:1080},locale:'en-US',deviceScaleFactor:1,reducedMotion:'no-preference'});await route(p,false);await p.goto(candidateURL);await p.waitForFunction(()=>window.AtlasV6);await p.fill('#search','For loop');await p.press('#search','Enter');await p.waitForFunction(()=>!AtlasV6.state().transitioning);check(await p.evaluate(()=>AtlasV6.state().viewState==='topic'&&AtlasV6.state().transform.k*14>=13),'animated navigation');await p.close();
  const report={status:'PASS',checks:checks.length,runs,accepted_preview_comparison:comparable?'18 viewport/theme scene sequences identical':'source/geography changed after explicit review; fixed UI assets and runtime contracts validated',browser:browser.version(),physical_device_tests:'NOT_PERFORMED'};
  if(input.report)fs.writeFileSync(input.report,JSON.stringify(report,null,2)+'\n');process.stdout.write(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1);});
