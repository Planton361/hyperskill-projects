const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const manifest=JSON.parse(fs.readFileSync(__dirname+'/final-v1/apply-manifest.json'));
const base=(process.env.PREVIEW_BASE||'http://127.0.0.1:8765')+'/prototypes/adaptive-pyramid/production-review/final-v1/view/';
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE});try{
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1}),errors=[],failed=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));page.on('request',r=>{if(!r.url().startsWith(base.split('/prototypes/')[0]))external.push(r.url());});
 await page.addInitScript(()=>{window.__writes=[];Storage.prototype.setItem=function(){window.__writes.push('storage');};});
 await page.goto(base+'target/');await page.waitForFunction(()=>window.KnowledgeAtlas);
 const initial=await page.evaluate(()=>{const v=KnowledgeAtlas.views;return{mode:v.options.mode,topics:v.scope.topics.size,cards:v.positions.size,learned:v.scope.learned.size,verified:v.scope.verified.size,geometry:JSON.stringify(v.m.geometry)};});
 assert.equal(initial.mode,'learned');assert.equal(initial.topics,31);assert.equal(initial.cards,52);assert.equal(initial.learned,31);assert.equal(initial.verified,12);
 const settle=()=>page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await settle();await page.screenshot({path:path.join(__dirname,'exact-my-knowledge.png')});
 await page.selectOption('#scene','accepted');await page.click('#compact');assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.scope.topics.size),89);
 await page.click('#global');await settle();assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.positions.size),3955);await page.screenshot({path:path.join(__dirname,'exact-global.png')});
 const contexts=[];
 for(const [mode,count] of [['course',89],['project',26]]){
  await page.selectOption('#scene',mode);await page.click('#compact');await settle();assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.scope.topics.size),count);
  await page.screenshot({path:path.join(__dirname,'exact-'+mode+'.png')});
  const before=await page.evaluate(()=>({calls:KnowledgeAtlas.views.metrics.layoutCalls,camera:KnowledgeAtlas.views.cameras.global}));
  await page.click('#highlight');await settle();const after=await page.evaluate(()=>({calls:KnowledgeAtlas.views.metrics.layoutCalls,camera:KnowledgeAtlas.views.cameras.global}));assert.deepEqual(after,before);contexts.push({mode,topics:count,highlightNoRelayout:true});
 }
 await page.selectOption('#stage','617');await page.click('#compact');assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.scope.topics.size),12);
 await page.fill('#search','topic:36');await page.click('#results button');await page.click('#global-show');assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.selected),'topic:36');assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.mode),'reference');
 assert.equal(await page.evaluate(()=>JSON.stringify(KnowledgeAtlas.views.m.geometry)),initial.geometry);
 assert.deepEqual(await page.evaluate(()=>window.__writes),[]);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth===innerWidth&&document.documentElement.scrollHeight===innerHeight),true);
 await page.goto(base);await page.waitForFunction(()=>document.querySelector('#bindings').textContent.includes('Manifest / human approval token:'));
 const bindings=await page.textContent('#bindings');assert(bindings.includes(manifest.manifest_fingerprint));assert(bindings.includes(manifest.source_production.fingerprint));assert(bindings.includes(manifest.target_production.fingerprint));assert(bindings.includes('Changed Production files: 24'));
 for(const view of ['current','learned','global','course','project']){await page.click('[data-view="'+view+'"]');await page.waitForFunction(v=>{const w=document.querySelector('iframe').contentWindow;return v==='current'?!!w.AtlasV6:w.KnowledgeAtlas?.views.options.mode===v;},view);}
 await page.screenshot({path:path.join(__dirname,'exact-review.png')});
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);assert.deepEqual(external,[]);
 const result={status:'PASS',browser:browser.version(),viewport:[1440,900],manifest_fingerprint:manifest.manifest_fingerprint,defaultMyKnowledge:{topics:31,cards:52,verified:12},acceptedLandscape:89,contexts,stage617:12,globalCards:3955,globalSearchShowInGlobal:true,learnedVerifiedStyling:true,globalReferenceUnchanged:true,reviewBindingsAndFiveViews:true,errors,failed,external};
 fs.writeFileSync(__dirname+'/browser-results.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
