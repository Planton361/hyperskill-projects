/* Adapt the accepted V6 relation/navigation checks to a read-only offline harness. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const runtime=path.resolve(__dirname,'../../prototypes/knowledge-atlas-v6');
 const options={headless:true};if(process.env.CHROMIUM_EXECUTABLE)options.executablePath=process.env.CHROMIUM_EXECUTABLE;
 const browser=await chromium.launch(options);
 try{
  const page=await browser.newPage({locale:'en-US',deviceScaleFactor:1,viewport:{width:1920,height:1080},reducedMotion:'reduce'}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',r=>{const u=new URL(r.request().url()),key=u.pathname.slice(1)||'index.html',p=path.join(runtime,key);
   if(u.origin!=='http://atlas.invalid'||key.includes('..')||!fs.existsSync(p))return r.abort();
   return r.fulfill({body:fs.readFileSync(p),contentType:key.endsWith('.js')?'application/javascript':key.endsWith('.json')?'application/json':key.endsWith('.css')?'text/css':'text/html'});
  });
  await page.goto('http://atlas.invalid/');await page.waitForFunction(()=>window.AtlasV6);
  const result=await page.evaluate(()=>{
   const s=AtlasV6.state(),before=JSON.stringify(s.L.nodes.map(n=>[n.key,n.x,n.y,n.width,n.height])),cp=JSON.stringify(s.L.checkpoint),checks=[];
   const check=(ok,label)=>{if(!ok)throw Error(label);checks.push(label);};
   AtlasV6.select('project:113');check(document.querySelectorAll('.node.topic.covered').length===26,'accepted Project 113 requirements');
   const stage=document.querySelector('[data-stage="617"]')||[...document.querySelectorAll('[data-stage]')].find(b=>b.textContent.startsWith('Stage 4'));
   stage.click();check(document.querySelectorAll('.node.topic.covered').length===12,'accepted Stage 4 requirements');
   const topic=[...s.m.nodes.values()].find(n=>n.type==='topic'&&n.title==='For loop');AtlasV6.select(topic.key,true);
   check(s.L===AtlasV6.state().L,'no layout rebuild during navigation');
   const route=AtlasV6.state().relationProjection.routes.find(r=>!r.sameTray);check(!!route,'automatic taxonomy route');
   AtlasV6.focusRelation(route.key);check(!document.querySelector('.knowledge'),'no free cross-graph relation paths');
   check(AtlasV6.state().focusedRelation.key===route.key,'relation focus');
   check(before===JSON.stringify(s.L.nodes.map(n=>[n.key,n.x,n.y,n.width,n.height]))&&cp===JSON.stringify(s.L.checkpoint),'accepted geometry preserved');
   check(document.documentElement.scrollWidth<=innerWidth,'no desktop page overflow');
   return {status:'PASS',checks};
  });
  assert.deepEqual(errors,[]);console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
