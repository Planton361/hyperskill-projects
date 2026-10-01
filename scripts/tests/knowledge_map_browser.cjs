/* Real-source runtime checks; no synthetic fixtures, account/session or production writes. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.argv[2]||'http://127.0.0.1:8000/knowledge-map/';
const path=require('node:path');
const model=JSON.parse(fs.readFileSync(path.join(__dirname,'../../docs/knowledge-map/model.json')));
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
 const reports=[],ready=p=>p.locator('#map[data-ready="true"]').waitFor();
 const collect=async(p,mode)=>{
  await p.locator(mode==='roadmap'?'#roadmap':'#my').click();
  const domainNames=await p.locator('#area-nav button').allTextContents(),found=new Set();
  for(const dn of domainNames){
   await p.locator('#area-nav button').filter({hasText:dn}).click();
   const subNames=await p.locator('#area-nav button').allTextContents();
   for(const sn of subNames){
    await p.locator('#area-nav button').filter({hasText:sn}).click();
    while(true){
     const rows=await p.locator('.node[data-type="topic"]').evaluateAll(ns=>ns.map(n=>({key:n.dataset.key,learned:n.dataset.learned})));
     rows.forEach(n=>{found.add(n.key);if(mode==='knowledge')assert.equal(n.learned,'true');});
     assert.equal(await p.locator('.edge').count(),0);
     await labelBounds(p);
     if(await p.locator('#pagination').isHidden()||await p.locator('#next').isDisabled())break;
     await p.locator('#next').click();
    }
    await p.locator('#back').click();
   }
   await p.locator('#back').click();
  }
  return [...found].sort();
 };
 async function labelBounds(p){
  const data=await p.locator('.node').evaluateAll(ns=>ns.map(n=>{const l=n.querySelector('.label').getBoundingClientRect(),c=n.querySelector('.count').getBoundingClientRect(),map=document.querySelector('#map').getBoundingClientRect();return{title:n.getAttribute('aria-label'),fits:l.right<=map.right+1&&l.left>=map.left-1,noOverlap:l.bottom<=c.top+2};}));
  assert(data.every(d=>d.fits),'Clipped labels: '+JSON.stringify(data.filter(d=>!d.fits)));
  assert(data.every(d=>d.noOverlap),'Label/status overlap: '+JSON.stringify(data.filter(d=>!d.noOverlap)));
 }
 try{
 for(const width of [1440,768,390,320])for(const theme of ['dark','light']){
  const context=await browser.newContext({viewport:{width,height:1000},colorScheme:theme,reducedMotion:'reduce'}),p=await context.newPage();
  const errors=[],failed=[],http=[],requests=[];
  p.on('pageerror',e=>errors.push(e.message));p.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text());});
  const cdp=await context.newCDPSession(p);await cdp.send('Network.enable');cdp.on('Network.responseReceived',e=>{if(e.response.status>=400)http.push({url:e.response.url,status:e.response.status});});
  p.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()}));p.on('response',r=>{if(r.status()>=400)http.push({url:r.url(),status:r.status()});});
  p.on('request',r=>requests.push(r.url()));
  assert.equal((await p.goto(base)).status(),200);await ready(p);
  assert.equal(await p.evaluate(()=>d3.version),'7.9.0');
  assert.equal(await p.locator('.node[data-type="domain"]').count(),2);
  await labelBounds(p);
  const learned=await collect(p,'knowledge');
  assert.deepEqual(learned,model.topics.filter(t=>t.is_learned===true).map(t=>t.key).sort());
  const roadmap=await collect(p,'roadmap');
  assert.deepEqual(roadmap,model.topics.map(t=>t.key).sort());
  for(const [q,level] of [['domain=java','subdomains'],['topic=89','topic'],['project=113','domains'],['mode=roadmap','domains']]){
   assert.equal((await p.goto(base+'?'+q)).status(),200);await ready(p);assert.equal(await p.locator('#map').getAttribute('data-level'),level);
  }
  await p.goto(base);await ready(p);
  await p.locator('.node[data-key="domain:java"]').focus();await p.keyboard.press('ArrowRight');
  assert.equal(await p.locator('.node[data-key="domain:java"]').evaluate(n=>getComputedStyle(n).outlineStyle),'solid');
  await p.keyboard.press('Enter');
  assert.equal(await p.locator('#map').getAttribute('data-level'),'subdomains');
  await p.locator('#area-nav button').filter({hasText:'Java foundations'}).click();
  assert.equal(await p.locator('#map').getAttribute('data-level'),'topics');
  await p.locator('#search').fill('For loop');await p.locator('#search').press('ArrowDown');await p.keyboard.press('Enter');
  assert.equal(await p.locator('#details h2').innerText(),'For loop');assert(p.url().includes('topic=89'));
  assert((await p.locator('.edge').count())>0);await labelBounds(p);
  const edgeValid=await p.locator('.edge').evaluateAll((es,source)=>es.every(e=>source.some(s=>s.source===e.dataset.source&&s.target===e.dataset.target&&s.type===e.dataset.type)),model.edges);assert(edgeValid);
  await p.goBack();assert.equal(await p.locator('#map').getAttribute('data-level'),'topics');
  await p.goForward();assert.equal(await p.locator('#details h2').innerText(),'For loop');
  await p.reload();await ready(p);assert.equal(await p.locator('#details h2').innerText(),'For loop');
  if(process.env.SCREENSHOT_DIR)await p.screenshot({path:path.join(process.env.SCREENSHOT_DIR,'topic-'+width+'-'+theme+'.png'),fullPage:true});
  await p.goto(base+'?project=113');await ready(p);assert.equal(await p.locator('.edge').count(),0);
  assert((await p.locator('#details').innerText()).includes('Required topics: 26'));
  await p.locator('#details button').filter({hasText:'Show project connections'}).click();
  const targets=new Set();
  while(true){
   for(const t of await p.locator('.edge[data-type="project_requires"]').evaluateAll(es=>es.map(e=>e.dataset.target)))targets.add(t);
   assert.equal(await p.locator('.edge[data-type="project_applies"]').count(),0);await labelBounds(p);
   if(await p.locator('#pagination').isHidden()||await p.locator('#next').isDisabled())break;
   await p.locator('#next').click();
  }
  assert.equal(targets.size,26);
  await p.locator('#projects button').filter({hasText:'My First Project'}).click();
  assert((await p.locator('#details').innerText()).includes('Completed stages: 0'));
  assert.equal(await p.locator('.edge').count(),0);
  await p.goto(base);await ready(p);await p.locator('#map').hover();await p.mouse.wheel(0,-700);await p.waitForTimeout(350);
  assert.equal(await p.locator('#map').getAttribute('data-level'),'subdomains');
  const a11y=await p.evaluate(()=>({noOverflow:document.documentElement.scrollWidth<=innerWidth,reducedMotion:matchMedia('(prefers-reduced-motion:reduce)').matches,namedNodes:[...document.querySelectorAll('.node')].every(n=>n.getAttribute('aria-label')&&n.getAttribute('tabindex')==='0')}));
  assert(a11y.noOverflow);assert(a11y.reducedMotion);assert(a11y.namedNodes);
  if(errors.length||http.length||failed.length)console.log(JSON.stringify({errors,http,failed}));
  assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);assert.deepEqual(http,[]);
  assert(requests.every(r=>r.startsWith(base)));
  reports.push({width,theme,learned:learned.length,roadmap:roadmap.length,projectRequires:targets.size,deepLinks:true,history:true,searchKeyboard:true,wheelZoom:true,labelBounds:true,...a11y,consoleErrors:errors,httpErrors:http,failedRequests:failed});
  console.log('PASS '+width+' '+theme);await context.close();
 }
 console.log(JSON.stringify(reports,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
