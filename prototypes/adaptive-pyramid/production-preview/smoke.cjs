const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const R=require('../../../scripts/knowledge_atlas/presentation/registry.cjs'),A=require('../../../scripts/knowledge_atlas/presentation/adaptive.cjs'),check=require('../layout-refinement-tests/invariants.cjs');
const base=(process.env.PREVIEW_BASE||'http://127.0.0.1:8765')+'/prototypes/adaptive-pyramid/production-preview/';
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE});try{
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1}),errors=[],failed=[],external=[],writes=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));page.on('request',r=>{if(!r.url().startsWith(base.split('/prototypes/')[0]))external.push(r.url());if(r.method()!=='GET')writes.push(r.method()+' '+r.url());});
 await page.addInitScript(()=>{window.__storageWrites=[];const original=Storage.prototype.setItem;Storage.prototype.setItem=function(...args){window.__storageWrites.push(args[0]);return original.apply(this,args);};});
 const start=performance.now();await page.goto(base+'current/');await page.waitForFunction(()=>window.AtlasV6);await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 const current=await page.evaluate(()=>{const s=AtlasV6.state(),b=AtlasLayout.contentBounds(s.L,s.visible);return {mode:s.mode,visible:s.visible.length,bounds:b,fitScale:s.transform.k,metrics:s.metrics,progress:s.m.raw.progress};});current.readyMs=performance.now()-start;
 await page.screenshot({path:path.join(__dirname,'current-production.png')});
 const targetStart=performance.now();await page.goto(base+'target/');await page.waitForFunction(()=>window.KnowledgeAtlas);const targetReadyMs=performance.now()-targetStart;
 const original=await page.evaluate(()=>({raw:KnowledgeAtlas.views.m.raw,geometry:KnowledgeAtlas.views.m.geometry})),m=R.index(original.raw,original.geometry),scenes=[];
 const sortedProgress=rows=>rows.slice().sort((a,b)=>a.course_id-b.course_id||a.topic_id-b.topic_id);
 assert.deepEqual(sortedProgress(current.progress.topics),sortedProgress(original.raw.progress),'Topic progress semantics changed');
 delete current.progress;
 assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.options.mode),'learned');
 const settle=()=>page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 async function capture(name){await settle();const row=await page.evaluate(()=>{const v=KnowledgeAtlas.views,l=v.local;return {options:v.options,positions:[...l.positions],subtrees:[...l.subtrees],bands:[...l.bands],groups:l.groups,routes:l.routes,hidden:[...l.hidden],bounds:l.bounds,siblingGap:l.siblingGap,raw:v.m.raw,layoutMs:v.metrics.layoutMs,camera:v.camera,labels:v.metrics.labels,topicLabels:v.metrics.readableTopicLabels};});
  const live=R.replaceSnapshot(m,row.raw),s=A.selection(live,row.options),l={...row,positions:new Map(row.positions),subtrees:new Map(row.subtrees),bands:new Map(row.bands),hidden:new Set(row.hidden)},checks=check(live,s,l);
  const ps=[...s.visible].map(k=>m.reference.get(k)),x0=Math.min(...ps.map(p=>p.x)),y0=Math.min(...ps.map(p=>p.y)),w=Math.max(...ps.map(p=>p.x+p.w))-x0,h=Math.max(...ps.map(p=>p.y+p.h))-y0;
  scenes.push({name,topics:s.topics.size,cards:l.positions.size,width:row.bounds.w,height:row.bounds.h,layoutMs:row.layoutMs,fitScale:row.camera.k,labels:row.labels,readableTopicLabels:row.topicLabels,globalMaskBounds:{width:w,height:h},globalMaskAreaRatio:w*h/(row.bounds.w*row.bounds.h),...checks});
  await page.screenshot({path:path.join(__dirname,name+'.png')});return row;
 }
 await capture('my-knowledge');
 const topicGroup=await page.evaluate(()=>KnowledgeAtlas.views.local.groups.slice().sort((a,b)=>b.cards.length-a.cards.length)[0].parent);await page.evaluate(k=>KnowledgeAtlas.focus(k),topicGroup);await capture('topic-group');
 await page.click('#global');await settle();assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.positions.size),3955);await page.screenshot({path:path.join(__dirname,'global.png')});
 for(const [name,options] of [['course',{mode:'course',id:8,stage:null,onlyLearned:false}],['project',{mode:'project',id:113,stage:null,onlyLearned:false}],['stage',{mode:'project',id:113,stage:617,onlyLearned:false}]]){
  await page.evaluate(o=>KnowledgeAtlas.confirm(o,'compact'),options);await capture(name);
  const before=await page.evaluate(()=>({calls:KnowledgeAtlas.views.metrics.layoutCalls,camera:KnowledgeAtlas.views.cameras.global,geometry:JSON.stringify(KnowledgeAtlas.views.m.geometry)}));
  await page.click('#highlight');await settle();assert.deepEqual(await page.evaluate(()=>({calls:KnowledgeAtlas.views.metrics.layoutCalls,camera:KnowledgeAtlas.views.cameras.global,geometry:JSON.stringify(KnowledgeAtlas.views.m.geometry)})),before,'Highlight changed geometry/camera or relaid out');
 }
 // Search and Show in Global use real controls, without learning or a layout call.
 const calls=await page.evaluate(()=>KnowledgeAtlas.views.metrics.layoutCalls);await page.fill('#search','topic:36');await page.click('#results button');await page.click('#global-show');await settle();
 assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.selected),'topic:36');assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.metrics.layoutCalls),calls);assert.equal(await page.evaluate(()=>KnowledgeAtlas.views.mode),'reference');
 await page.evaluate(()=>KnowledgeAtlas.confirm({mode:'learned',stage:null,onlyLearned:false,branch:null},'compact'));
 const growth=await page.evaluate(()=>{const a=KnowledgeAtlas,v=a.views;v.selected=[...v.scope.topics][0];const p=v.local.positions.get(v.selected),c={...v.camera},calls=v.metrics.layoutCalls,next=structuredClone(v.m.raw),r=next.progress.find(r=>r.is_learned===false);next.presentation_fixture=true;r.is_learned=true;a.refreshSnapshot(next);const q=v.local.positions.get(v.selected);return {addedTopic:r.topic_id,learned:v.scope.topics.size,verified:v.scope.verified.size,layoutCalls:v.metrics.layoutCalls-calls,movement:v.metrics.movement,anchorDelta:Math.hypot(p.x*c.k+c.x-q.x*v.camera.k-v.camera.x,p.y*c.k+c.y-q.y*v.camera.k-v.camera.y)};});
 assert.equal(growth.learned,32);assert.equal(growth.verified,12);assert.equal(growth.layoutCalls,1);assert(growth.anchorDelta<1e-8);await page.waitForTimeout(200);await capture('learning-growth');
 assert.equal(await page.evaluate(()=>JSON.stringify(KnowledgeAtlas.views.m.geometry)),JSON.stringify(original.geometry));
 const storageWrites=await page.evaluate(()=>window.__storageWrites);assert.deepEqual(storageWrites,[]);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth===innerWidth&&document.documentElement.scrollHeight===innerHeight),true);
 // Smoke the review package in the same viewport/browser session.
 await page.goto(base);await page.waitForFunction(()=>document.querySelector('iframe').contentWindow.KnowledgeAtlas);await page.click('[data-view="course"]');await page.waitForFunction(()=>document.querySelector('iframe').contentWindow.KnowledgeAtlas?.views.options.mode==='course');
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);assert.deepEqual(external,[]);assert.deepEqual(writes,[]);
 fs.writeFileSync(__dirname+'/browser-results.json',JSON.stringify({status:'PASS',browser:browser.version(),viewport:[1440,900],current,targetReadyMs,scenes,growth,errors,failed,external,writes,storageWrites,highlightNoRelayout:true,globalReferenceUnchanged:true,progressSemanticsUnchanged:true,searchShowInGlobal:true,reviewPageSmoke:true},null,2)+'\n');
 console.log(JSON.stringify({status:'PASS',browser:browser.version(),currentReadyMs:current.readyMs,targetReadyMs,scenes:scenes.map(s=>({name:s.name,cards:s.cards,layoutMs:s.layoutMs,width:s.width,height:s.height})),growth:{addedTopic:growth.addedTopic,average:growth.movement.average,max:growth.movement.max,anchorDelta:growth.anchorDelta},errors,failed},null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
