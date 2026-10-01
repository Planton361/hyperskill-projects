/* Real source data only; caller supplies Playwright, no sessions or synthetic fixtures. */
const {chromium,firefox}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const runtime=path.join(__dirname,'../../docs/knowledge-map');
const model=JSON.parse(fs.readFileSync(path.join(runtime,'model.json')));
const base=process.argv[2]||'http://127.0.0.1:8000/knowledge-map/';
const engine=process.env.ENGINE||'chromium';
assert(['chromium','firefox'].includes(engine),'ENGINE must be chromium or firefox');
const expected=fs.readFileSync(path.join(runtime,'model.json'));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
async function labelStats(p){return p.locator('.node .label').evaluateAll(labels=>{
 const visible=labels.filter(l=>getComputedStyle(l).display!=='none'),boxes=visible.map(l=>{const b=l.getBoundingClientRect();return{x:b.x,y:b.y,w:b.width,h:b.height,key:l.parentElement.dataset.key};});
 const overlaps=[];for(let i=0;i<boxes.length;i++)for(let j=0;j<i;j++){const a=boxes[i],b=boxes[j];if(Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>1&&Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>1)overlaps.push([a.key,b.key]);}
 return{visible:visible.length,overlaps,fontMin:Math.min(...visible.map(t=>parseFloat(getComputedStyle(t).fontSize)*t.getScreenCTM().a))};});}
async function search(p,q){await p.locator('#search').fill(q);await p.locator('#results button').first().click();await p.mouse.move(0,0);}
(async()=>{
 const executable=engine==='firefox'?process.env.FIREFOX_EXECUTABLE:process.env.CHROMIUM_EXECUTABLE;
 const browser=await (engine==='firefox'?firefox:chromium).launch({headless:true,...(executable?{executablePath:executable}:{})});
 const report={engine,version:browser.version(),base,runs:[],runtimeFiles:{},note:'Real source regression; touch emulated only in Chromium, no saved browser state.'};
 try{
 for(const width of [1440,1280,1200,1024,768,430,390,320])for(const theme of ['dark','light']){
  const context=await browser.newContext({viewport:{width,height:1100},colorScheme:theme,reducedMotion:'reduce',...(engine==='chromium'&&width<=430?{hasTouch:true}:{})});
  const p=await context.newPage(),errors=[],bad=[],consoleErrors=[];
  p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});p.on('response',r=>{if(r.status()>=400)bad.push({url:r.url(),status:r.status()});});
  p.on('requestfailed',r=>bad.push({url:r.url(),error:r.failure()?.errorText}));
  p.on('request',r=>{if(new URL(r.url()).origin!==new URL(base).origin)bad.push({url:r.url(),error:'Unexpected external request'});});
  const response=await p.goto(base,{waitUntil:'networkidle'});assert.equal(response.status(),200);
  await p.locator('#graph[data-ready=true]').waitFor();
  assert.equal(await p.locator('#my').getAttribute('aria-pressed'),'true');
  assert.equal(await p.locator('.node[data-type=topic]').count(),31);assert.equal(await p.locator('.node[data-type=project]').count(),2);assert.equal(await p.locator('.node[data-verified=true]').count(),12);
  assert.equal(await p.locator('.node[data-learned=false]').count(),0);assert.equal(await p.locator('.edge[data-type=knowledge]').count(),38);assert.equal(await p.locator('.edge.requires').count(),0);
  const labels=await labelStats(p),captions=await p.locator('.cluster-label').count();assert.equal(labels.visible,33);
  const layout=await p.evaluate(()=>{const c=document.querySelector('#canvas').getBoundingClientRect(),a=document.querySelector('aside').getBoundingClientRect();return{canvasWidth:c.width,inspectorBelow:a.top>=c.bottom,inspectorWithinPage:a.right<=innerWidth,grid:getComputedStyle(document.querySelector('main')).gridTemplateColumns};});
  assert.equal(layout.inspectorBelow,width<=1200);assert(layout.inspectorWithinPage);
  if(width===1024)assert(labels.fontMin>13);
  for(const t of model.topics.filter(t=>t.is_learned))assert.equal((await p.locator(`.node[data-key="${t.key}"] .label`).textContent()).replace(/\s/g,''),t.title.replace(/\s/g,''));
  assert.deepEqual(await p.locator('.node[data-type=topic]').evaluateAll(ns=>ns.map(n=>n.dataset.key).sort()),model.topics.filter(t=>t.is_learned===true).map(t=>t.key).sort());
  assert.equal(await p.locator('.node[data-type=category],.edge[data-type=hierarchy],.edge[data-type=project_applies]').count(),0);
  const clipped=await p.locator('.node[data-learned=true] .label').evaluateAll(ns=>{const c=document.querySelector('#canvas').getBoundingClientRect();return ns.filter(n=>{const r=n.getBoundingClientRect();return r.left<c.left-1||r.right>c.right+1||r.top<c.top-1||r.bottom>c.bottom+1;}).map(n=>n.textContent);});assert.deepEqual(clipped,[]);
  const filenames=[];
  async function shot(name){if(!process.env.SCREENSHOT_DIR)return;const file=`${engine}-${width}-${theme}-${name}.png`;await p.screenshot({path:path.join(process.env.SCREENSHOT_DIR,file),fullPage:true});filenames.push(file);}
  await shot('my-knowledge-fit');
  const positions=await p.locator('.node').evaluateAll(ns=>ns.map(n=>[n.dataset.key,n.getAttribute('transform')]));
  const selections=[];
  for(const [q,id] of [['For loop',89],['Types and variables',14],['IntelliJ IDEA',260],['String',9]]){
   // Exact title prevents a String-containing topic from becoming the chosen result.
   await p.locator('#search').fill(q);await p.locator('#results button').getByText(q,{exact:true}).click();await p.mouse.move(0,0);
   assert.equal(await p.locator('#graph').getAttribute('data-selected'),`topic:${id}`);assert.equal(await p.locator('#details h2').innerText(),q);
   const edges=model.connections.filter(e=>(e.source===`topic:${id}`||e.target===`topic:${id}`)&&model.topics.some(t=>t.key===e.source&&t.is_learned)&&model.topics.some(t=>t.key===e.target&&t.is_learned));
   assert.equal(await p.locator('.edge.highlight').count(),edges.length);assert.equal(await p.locator('.node.neighbor').count(),new Set(edges.flatMap(e=>[e.source,e.target]).filter(k=>k!==`topic:${id}`)).size);
   assert(await p.locator('.node.dim').count()>0);selections.push({topic:id,highlightedEdges:edges.length});
   if(id===89){await shot('for-loop-selected');const bounds=await p.locator(`.node[data-key="topic:${id}"]`).evaluate(n=>{const m=n.getScreenCTM(),c=document.querySelector('#canvas').getBoundingClientRect();return{nx:m.e,ny:m.f,cx:c.x+c.width/2,cy:c.y+c.height/2};});assert(Math.abs(bounds.nx-bounds.cx)<2);assert(Math.abs(bounds.ny-bounds.cy)<2);
    await p.locator('#graph').scrollIntoViewIfNeeded();const node=p.locator('.node[data-key="topic:89"]'),beforeDrag=await node.getAttribute('transform'),b=await node.evaluate(n=>{const m=n.getScreenCTM();return{x:m.e,y:m.f};});
    await p.mouse.move(b.x,b.y);await p.mouse.down();await p.mouse.move(b.x+25,b.y+20,{steps:3});await p.mouse.up();assert.notEqual(await node.getAttribute('transform'),beforeDrag);
   }
   await p.locator('#clear').click();assert.equal(await p.locator('.node.dim').count(),0);assert.equal(await p.locator('.edge.highlight').count(),0);
  }
  await search(p,'Simple Chat');assert((await p.locator('#details').innerText()).includes('Required topics: 26'));assert.equal(await p.locator('.edge.requires').count(),0);
  await p.locator('#details button').filter({hasText:'Show project connections'}).click();await p.mouse.move(0,0);assert.equal(await p.locator('.edge.requires').count(),26);assert.equal(await p.locator('.node.neighbor').count(),26);
  if(width===1440)await shot('project-113-connections');
  await p.locator('#clear').click();assert.equal(await p.locator('.edge.requires').count(),0);
  await p.locator('#roadmap').click();await p.mouse.move(0,0);
  assert.equal(await p.locator('.node[data-type=topic]').count(),89);assert.equal(await p.locator('.node[data-learned=false]').count(),58);assert.equal(await p.locator('.node[data-verified=true]').count(),12);assert.equal(await p.locator('.edge[data-type=knowledge]').count(),137);
  const roadmap=await labelStats(p);if(width===1440)await shot('course-roadmap');
  await p.locator('#closer').click();await p.locator('#closer').click();await p.locator('#closer').click();
  const close=await labelStats(p);assert.equal(await p.locator('.node[data-type=topic]').count(),89);
  const missing=await p.locator('.node[data-type=topic]').evaluateAll(ns=>ns.filter(n=>{const m=n.getScreenCTM(),r=document.querySelector('#canvas').getBoundingClientRect();return m.e>r.x&&m.e<r.right&&m.f>r.y&&m.f<r.bottom&&getComputedStyle(n.querySelector('.label')).display==='none';}).map(n=>n.dataset.key));assert.deepEqual(missing,[]);
  await p.locator('#my').click();await p.locator('.node[data-key="topic:89"]').focus();await p.keyboard.press('Enter');assert.equal(await p.locator('#details h2').innerText(),'For loop');await p.keyboard.press('Escape');
  await p.locator('#search').fill('For loop');await p.locator('#search').press('ArrowDown');await p.keyboard.press('Enter');assert.equal(await p.locator('#details h2').innerText(),'For loop');
  await p.locator('#clear').click();await p.locator('#fit').click();
  let touch='not applicable';
  if(width<=430&&engine==='chromium'){
   const session=await context.newCDPSession(p);await p.locator('#graph').scrollIntoViewIfNeeded();const r=await p.locator('#graph').boundingBox(),x=r.x+r.width/2,y=r.y+r.height/2;
   const before=await p.locator('#graph > g').getAttribute('transform');
   await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{id:0,x:x-20,y},{id:1,x:x+20,y}]});
   await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{id:0,x:x-60,y},{id:1,x:x+60,y}]});await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
   assert.notEqual(await p.locator('#graph > g').getAttribute('transform'),before);
   const panBefore=await p.locator('#graph > g').getAttribute('transform');
   await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{id:0,x:r.x+8,y:r.y+12}]});await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{id:0,x:r.x+32,y:r.y+36}]});await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
   assert.notEqual(await p.locator('#graph > g').getAttribute('transform'),panBefore);await session.detach();touch='pinch + pan tested';
  }
  for(let i=0;i<3;i++){await p.reload({waitUntil:'networkidle'});await p.locator('#graph[data-ready=true]').waitFor();assert.deepEqual(await p.locator('.node').evaluateAll(ns=>ns.map(n=>[n.dataset.key,n.getAttribute('transform')])),positions);}
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);assert.deepEqual(consoleErrors,[]);assert.deepEqual(bad,[]);
  report.runs.push({width,theme,labels,layout,captions,roadmap,close,selections,touch,reloadsIdentical:3,noOverflow:true,errors,consoleErrors,bad,screenshots:filenames});
  console.log(JSON.stringify(report.runs.at(-1)));await context.close();
 }
 report.resize=[];
 for(const theme of ['dark','light']){
 const ctx=await browser.newContext({viewport:{width:1440,height:1100},colorScheme:theme}),p=await ctx.newPage();await p.goto(base);await p.locator('#graph[data-ready=true]').waitFor();
 for(const width of [1280,1200,1152,1100,1024,900,768,430,390,320,1440]){
  await p.locator('#closer').click();await p.setViewportSize({width,height:1100});await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const auto=await p.locator('#graph > g').getAttribute('transform');await p.locator('#fit').click();assert.equal(await p.locator('#graph > g').getAttribute('transform'),auto,'ResizeObserver must already produce the same Fit');
  assert.equal(await p.locator('.node[data-type=topic]').count(),31);const labels=await labelStats(p);if(width===1024)assert(labels.fontMin>13);
  report.resize.push({theme,width,automaticFit:true,font:labels.fontMin});
 }await ctx.close();
 }
 const ctx=await browser.newContext();for(const file of ['index.html','app.js','style.css','model.json','vendor/d3-7.9.0.min.js','vendor/D3-LICENSE']){const r=await ctx.request.get(base+(file==='index.html'?'':file));assert.equal(r.status(),200);const bytes=await r.body();const local=fs.readFileSync(path.join(runtime,file));assert.equal(sha(bytes),sha(local));report.runtimeFiles[file]={status:r.status(),sha256:sha(bytes)};}
 assert.equal(report.runtimeFiles['model.json'].sha256,sha(expected));await ctx.close();
 if(process.env.RESULTS_PATH)fs.writeFileSync(process.env.RESULTS_PATH,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({engine,runs:report.runs.length,resizeChecks:report.resize.length,runtimeHashes:Object.keys(report.runtimeFiles).length}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
