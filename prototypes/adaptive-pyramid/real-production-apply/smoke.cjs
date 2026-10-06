const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const R=require('../../../scripts/knowledge_atlas/presentation/registry.cjs'),A=require('../../../scripts/knowledge_atlas/presentation/adaptive.cjs'),check=require('../layout-refinement-tests/invariants.cjs');
const url=(process.env.PRODUCTION_BASE||'http://127.0.0.1:8765')+'/docs/knowledge-map/';
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE});try{
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1}),errors=[],failed=[],httpErrors=[],external=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));page.on('response',r=>{if(r.status()>=400)httpErrors.push(r.url());});page.on('request',r=>{if(!r.url().startsWith(url.split('/docs/')[0]))external.push(r.url());});
 await page.addInitScript(()=>{window.__writes=[];const original=Storage.prototype.setItem;Storage.prototype.setItem=function(...args){window.__writes.push(args[0]);return original.apply(this,args);};});
 await page.goto(url);await page.waitForFunction(()=>window.KnowledgeAtlas);
 const initial=await page.evaluate(()=>({mode:KnowledgeAtlas.views.options.mode,topics:KnowledgeAtlas.views.scope.topics.size,cards:KnowledgeAtlas.views.positions.size,raw:KnowledgeAtlas.views.m.raw,geometry:KnowledgeAtlas.views.m.geometry})),m=R.index(initial.raw,initial.geometry),scenes=[];
 assert.equal(initial.mode,'learned');assert.equal(initial.topics,31);assert.equal(initial.cards,52);
 const settle=()=>page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 async function inspect(name,screenshot=false){await settle();const row=await page.evaluate(()=>{const v=KnowledgeAtlas.views,l=v.local;return{options:v.options,positions:[...l.positions],subtrees:[...l.subtrees],bands:[...l.bands],groups:l.groups,routes:l.routes,hidden:[...l.hidden],bounds:l.bounds,siblingGap:l.siblingGap,minimapSystem:v.metrics.minimapSystem,minimapBounds:v.metrics.minimapBounds};});
  const scope=A.selection(m,row.options),l={...row,positions:new Map(row.positions),subtrees:new Map(row.subtrees),bands:new Map(row.bands),hidden:new Set(row.hidden)};const checks=check(m,scope,l);assert.equal(row.minimapSystem,'local');assert.deepEqual(row.minimapBounds,row.bounds);scenes.push({name,topics:scope.topics.size,cards:l.positions.size,...checks});
  if(screenshot)await page.screenshot({path:path.join(__dirname,name+'.png')});
 }
 await inspect('my-knowledge',true);assert.equal(await page.textContent('#summary'),'31 Topics · 31 learned · 12 verified');
 assert.equal(await page.locator('#context-roots button').count(),5);await page.click('#mini');await settle();assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.metrics.minimapSystem),'local');
 await page.selectOption('#scene','accepted');await page.click('#compact');await inspect('accepted');assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.scope.topics.size),89);
 await page.click('#global');await settle();assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.positions.size),3955);assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.metrics.minimapSystem),'global');await page.screenshot({path:path.join(__dirname,'global.png')});
 for(const [mode,count] of [['course',89],['project',26]]){
  await page.selectOption('#scene',mode);await page.click('#compact');await inspect(mode);assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.scope.topics.size),count);
  if(mode==='project'){await page.selectOption('#stage','617');await page.click('#compact');await inspect('stage617',true);assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.scope.topics.size),12);}
  const before=await page.evaluate(()=>({calls:KnowledgeAtlas.views.metrics.layoutCalls,camera:KnowledgeAtlas.views.cameras.global}));
  await page.click('#highlight');await settle();assert.deepEqual(await page.evaluate(()=>({calls:KnowledgeAtlas.views.metrics.layoutCalls,camera:KnowledgeAtlas.views.cameras.global})),before);assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.positions.size),3955);assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.metrics.minimapSystem),'global');
 }
 // Verify full Project 113 highlight separately from its Stage highlight.
 await page.selectOption('#stage','');await page.click('#highlight');await settle();assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.scope.topics.size),26);
 const calls=await page.evaluate(()=>KnowledgeAtlas.views.metrics.layoutCalls);await page.fill('#search','topic:36');await page.click('#results button');await page.click('#global-show');await settle();assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.selected),'topic:36');assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.mode),'reference');assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.metrics.layoutCalls),calls);
 assert.equal(await page.evaluate(()=>JSON.stringify(KnowledgeAtlas.views.m.geometry)),JSON.stringify(initial.geometry));assert.deepEqual(await page.evaluate(()=>window.__writes),[]);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth===innerWidth&&document.documentElement.scrollHeight===innerHeight),true);
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);assert.deepEqual(httpErrors,[]);assert.deepEqual(external,[]);
 const result={status:'PASS',url,viewport:[1440,900],browser:browser.version(),defaultMyKnowledge:{topics:31,cards:52,verified:12},scenes,globalCards:3955,courseAndProjectHighlightNoRelayout:true,stage617:12,searchShowInGlobal:true,minimapOrientation:true,learnedVerifiedStyling:true,globalReferenceUnchanged:true,errors,failed,httpErrors,external,storageWrites:[]};fs.writeFileSync(__dirname+'/browser-results.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({status:'PASS',url,viewport:result.viewport,browser:result.browser,scenes:scenes.map(s=>({name:s.name,topics:s.topics,cards:s.cards,cardOverlaps:s.cardOverlaps,subtreeOverlaps:s.subtreeOverlaps})),errors,failed,httpErrors},null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
