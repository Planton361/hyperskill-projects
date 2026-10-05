/* External Playwright only. Non-persistent offline context; output stays here. */
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const base=path.resolve(__dirname,'..'),browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1}),errors=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',r=>{const u=new URL(r.request().url()),key=u.pathname.slice(1)||'index.html';
  if(u.origin!=='http://global-atlas.invalid'||key.includes('..')){external.push(u.href);return r.abort();}
  const file=path.join(base,key);if(!fs.existsSync(file))return r.abort();
  return r.fulfill({body:fs.readFileSync(file),contentType:key.endsWith('.json')?'application/json':key.endsWith('.js')?'application/javascript':key.endsWith('.css')?'text/css':'text/html'});
 });
 await page.goto('http://global-atlas.invalid/');await page.waitForFunction(()=>window.GlobalAtlas);
 const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await settle();
 const result=await page.evaluate(async()=>{
  const A=GlobalAtlas,geometry=JSON.stringify([...A.m.nodes.values()].map(n=>[n.key,n.x,n.y,n.w,n.h]));
  const frame=()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  const summarize=a=>({min:Math.min(...a),median:[...a].sort((a,b)=>a-b)[Math.floor(a.length/2)],p95:[...a].sort((a,b)=>a-b)[Math.floor(a.length*.95)],max:Math.max(...a)});
  const overview={...A.metrics},search=[],scope=[],frameDraw=[],response=[];
  for(let i=0;i<60;i++){
   A.search(['Python','reference:333','Java','topic:15'][i%4]);search.push(A.metrics.searchMs);
   const start=performance.now();A.switchScope(['global','my','course','project'][i%4],i%4===3?113:8);scope.push(A.metrics.scopeMs);await frame();response.push(performance.now()-start);frameDraw.push(A.metrics.drawMs);
  }
  A.switchScope('global');const deep=[...A.m.nodes.values()].find(n=>n.depth===8);A.focus(deep.parent);await frame();
  const deepBranch={key:deep.parent,...A.metrics,zoom:A.state().cam.k};A.focus(deep.key);await frame();
  const deepFocus={key:deep.key,...A.metrics,zoom:A.state().cam.k};
  if(A.m.nodes.size!==3955||geometry!==JSON.stringify([...A.m.nodes.values()].map(n=>[n.key,n.x,n.y,n.w,n.h])))throw Error('Scope/focus mutated geography');
  if(A.search('reference:333')[0].kind!=='reference')throw Error('Fake Topic');
  return {browser:navigator.userAgent,viewport:[innerWidth,innerHeight],overview,deepBranch,deepFocus,
   searchMs:summarize(search),scopeMs:summarize(scope),drawMs:summarize(frameDraw),scopeToPaintMs:summarize(response),
   domElements:document.querySelectorAll('*').length,heapBytes:performance.memory?.usedJSHeapSize??null};
 });
 assert.ok(result.overview.initMs<2000,'Initialization regression');assert.ok(result.searchMs.p95<50,'Search regression');assert.ok(result.scopeMs.p95<50,'Scope regression');assert.ok(result.drawMs.p95<100,'Draw regression');assert.ok(result.overview.labels>0&&result.overview.labels<=250,'Semantic overview labels');assert.ok(result.domElements<200,'DOM explosion');
 await page.screenshot({path:path.join(__dirname,'deep-focus.png')});
 await page.evaluate(()=>{GlobalAtlas.switchScope('global');GlobalAtlas.fitGlobal();});await settle();
 await page.screenshot({path:path.join(__dirname,'global-overview.png')});
 assert.equal(await page.locator('#roots button').count(),5);
 await page.locator('#roots button').nth(4).click();assert.equal(await page.evaluate(()=>GlobalAtlas.m.nodes.get(GlobalAtlas.state().selected).title),'Math');await page.locator('#back').click();
 await page.locator('[data-mode=my]').click();await page.locator('#fit-scope').click();await settle();
 assert.equal(await page.evaluate(()=>GlobalAtlas.state().highlight.length),135);
 await page.screenshot({path:path.join(__dirname,'my-atlas.png')});
 await page.locator('[data-mode=course]').click();assert.equal(await page.evaluate(()=>GlobalAtlas.state().highlight.length),135);
 await page.locator('[data-mode=project]').click();assert.match(await page.locator('#details').innerText(),/26 distinct required Topics/);
 await page.locator('#stage').selectOption('617');assert.equal(await page.evaluate(()=>GlobalAtlas.state().highlight.filter(k=>k.startsWith('topic:')).length),12);assert.match(await page.locator('#details').innerText(),/12 explicit Stage required Topics/);
 await page.locator('#fit-scope').click();await settle();await page.screenshot({path:path.join(__dirname,'project-stage.png')});
 await page.locator('#context').selectOption('380');assert.match(await page.locator('#details').innerText(),/UNKNOWN/);assert.equal(await page.evaluate(()=>GlobalAtlas.state().highlight.length),0);
 await page.locator('#search').fill('reference:333');await page.locator('#results button').first().click();await settle();
 assert.match(await page.locator('#details').innerText(),/Structural reference only/);assert.equal(await page.evaluate(()=>GlobalAtlas.state().selected),'reference:333');
 await page.locator('#search').fill('topic:36');await page.locator('#results button').first().click();assert.match(await page.locator('#details').innerText(),/category:35/);assert.match(await page.locator('#details').innerText(),/category:306/);
 const box=await page.locator('#canvas').boundingBox(),before=await page.evaluate(()=>GlobalAtlas.state().cam);
 await page.mouse.move(box.x+200,box.y+200);await page.mouse.wheel(0,-200);await settle();assert.notEqual(await page.evaluate(()=>GlobalAtlas.state().cam.k),before.k);
 await page.mouse.down();await page.mouse.move(box.x+260,box.y+230);await page.mouse.up();await settle();
 await page.locator('#progress').check();await settle();
 await page.locator('#search').fill('no-match-zzzzz');assert.match(await page.locator('#results').innerText(),/No matching/);
 await page.locator('#fit').click();await settle();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.locator('#canvas').focus();const x=await page.evaluate(()=>GlobalAtlas.state().cam.x);await page.keyboard.press('ArrowLeft');assert.notEqual(await page.evaluate(()=>GlobalAtlas.state().cam.x),x);
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);assert.equal(await page.evaluate(()=>localStorage.length+sessionStorage.length),0);
 result.checks='PASS: real forest, all scopes, stage requirements, UNKNOWN project, shared memberships, deep focus, search, pan/zoom, keyboard, progress, no errors/external requests/storage';
 fs.writeFileSync(path.join(__dirname,'browser-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
