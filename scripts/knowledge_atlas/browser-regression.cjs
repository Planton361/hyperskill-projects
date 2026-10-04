/* Adapt the accepted V6 relation/navigation checks to a read-only offline harness. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const {execFileSync}=require('child_process');
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
 // The same read-only CI step validates the installed production package after
 // promotion, including the exact accepted Preview scene comparison.
 const root=path.resolve(__dirname,'../..'),production=path.join(root,'docs/knowledge-map');
 if(fs.existsSync(path.join(production,'release-manifest.json'))){
  // Packaging/rollback fixtures use the OS temporary directory, never docs/state.
  execFileSync('python',['-B','-m','unittest','knowledge_atlas.test_production','-v'],{env:{...process.env,PYTHONPATH:path.join(root,'scripts')},stdio:'inherit',timeout:60000});
  const assets={};const walk=dir=>{for(const entry of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,entry.name);if(entry.isDirectory())walk(p);else assets[path.relative(production,p).split(path.sep).join('/')]=fs.readFileSync(p,'utf8');}};walk(production);
  const result=execFileSync(process.execPath,[path.join(__dirname,'production_regression.cjs')],{input:JSON.stringify({root,assets}),encoding:'utf8',timeout:240000,maxBuffer:4*1024*1024});
  console.log(result);
 }
})().catch(e=>{console.error(e);process.exit(1);});
