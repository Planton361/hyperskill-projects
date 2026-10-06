/* Offline comparison/regression harness. Only prototype reports/captures written. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/home/anton/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const here=path.resolve(__dirname,'..'),root=path.resolve(here,'../..'),out=path.join(__dirname,'output');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const before=JSON.parse(fs.readFileSync(path.join(here,'reports/refinement-before.json')));
const protectedFiles=JSON.parse(fs.readFileSync(path.join(here,'reports/protected-before.json')));
const checks=[];function check(label,fn){fn();checks.push(label)}
async function checkAsync(label,fn){await fn();checks.push(label)}
const baseline=JSON.parse(fs.readFileSync(path.join(root,'docs/knowledge-map/geometry.js'),'utf8').split('=').slice(1).join('=').trim().replace(/;$/,''));
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE||'/opt/google/chrome/chrome',args:['--no-sandbox']});
 const context=await browser.newContext({locale:'en-US',deviceScaleFactor:1,reducedMotion:'reduce',viewport:{width:1920,height:1200}}),errors=[],external=[];
 await context.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!=='http://localhost'){external.push(u.origin);return r.abort()}const file=path.resolve(root,'.'+u.pathname);if(!file.startsWith(root+path.sep))return r.abort();const target=fs.existsSync(file)&&fs.statSync(file).isDirectory()?path.join(file,'index.html'):file;if(!fs.existsSync(target))return r.fulfill({status:404,body:'not found'});const ext=path.extname(target),mime={'.js':'application/javascript','.json':'application/json','.css':'text/css','.html':'text/html'};return r.fulfill({body:fs.readFileSync(target),contentType:mime[ext]||'application/octet-stream'})});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.stack));
 try{
  await page.goto('http://localhost/prototypes/knowledge-atlas-activation/');await page.waitForFunction(()=>window.AtlasPrototype?.ready);
  const semanticBefore=await page.evaluate(()=>JSON.stringify(AtlasPrototype.state().fixtures.scenarios.small));
  await page.evaluate(()=>AtlasPrototype.change('small-variants'));
  const inventory=await page.evaluate(()=>AtlasPrototype.state().variants);
  check('five valid objective selections',()=>assert.equal(Object.keys(inventory.selected).length,5));
  check('multiple distinct candidate placements',()=>assert.ok(inventory.inventory.distinct_geometry_positions>=4));
  const growth=inventory.inventory.growth_groups;
  for(const width of [128,256,384])check('valid growth probe '+width,()=>assert.ok(growth.some(r=>r.width_growth===width)));
  const m=inventory.selected.current.metrics;
  check('current 1291 drift explained',()=>assert.equal((m.new_root_center_x-m.parent_center_x)/2,1291));
  check('current source 1164/Programming languages',()=>{assert.equal(m.parent_id,'category:1164');assert.equal(m.parent_title,'Programming languages')});
  check('normalized comparison uses accepted subtree width',()=>assert.equal(m.accepted_parent_subtree_width,5676));
  check('centering lowers overall maximum drift',()=>assert.ok(inventory.selected.centering.metrics.max_all_parent_drift<m.max_all_parent_drift));
  check('parent distance exposes internal tradeoff',()=>{assert.ok(inventory.selected['parent-distance'].metrics.first_connector_length<m.first_connector_length);assert.ok(inventory.selected['parent-distance'].metrics.max_all_parent_drift>m.max_all_parent_drift)});
  check('growth did not improve minimum parent distance',()=>assert.ok(growth.filter(r=>[128,256,384].includes(r.width_growth)).every(r=>r.min_parent_distance===growth[0].min_parent_distance)));
  check('growth increases hierarchy route length',()=>assert.ok(growth.filter(r=>[128,256,384].includes(r.width_growth)).every(r=>r.min_connector>growth[0].min_connector)));
  await checkAsync('semantic plan/fixture input immutable',async()=>assert.equal(await page.evaluate(()=>JSON.stringify(AtlasPrototype.state().fixtures.scenarios.small)),semanticBefore));
  const reversed=await page.evaluate(()=>{const f=JSON.parse(JSON.stringify(AtlasPrototype.state().fixtures.scenarios.small));f.display.reverse();for(const k of ['entities','new_categories','new_topics','already_active'])f.plan[k].reverse();return SmallActivationVariants.build(AtlasBuildGeometry,f,AtlasV6.measure)});
  check('comparison serialization order-independent',()=>assert.equal(JSON.stringify(reversed),JSON.stringify(inventory)));
  const repeated=await page.evaluate(()=>SmallActivationVariants.build(AtlasBuildGeometry,AtlasPrototype.state().fixtures.scenarios.small,AtlasV6.measure));
  check('comparison serialization byte-idempotent',()=>assert.equal(JSON.stringify(repeated),JSON.stringify(inventory)));
  let camera=null;
  for(const [name,candidate]of Object.entries(inventory.selected)){
   const r=candidate.report;
   check(name+': exact frozen nodes',()=>assert.deepEqual(candidate.geometry.nodes.slice(0,135),baseline.nodes));
   check(name+': exact 26 trays',()=>assert.deepEqual(candidate.geometry.trays.slice(0,26),baseline.trays));
   check(name+': exact 119 segments',()=>assert.deepEqual(candidate.geometry.connectorSegments.slice(0,119),baseline.connectorSegments));
   check(name+': all hard constraints',()=>['existing_nodes_moved','overlaps','hierarchy_crossings','connector_through_cards','invalid_ports'].forEach(k=>assert.equal(r[k],0)));
   check(name+': review, three categories/six topics',()=>{assert.equal(r.outcome,'ACTIVATION_REVIEW_REQUIRED');assert.equal(r.new_categories,3);assert.equal(r.new_topics,6)});
   await page.evaluate(n=>{document.querySelector('#clear').click();return AtlasPrototype.selectVariant(n)},name);
   await page.evaluate(()=>AtlasPrototype.fitComparison());
   const transform=await page.evaluate(()=>({x:AtlasV6.state().transform.x,y:AtlasV6.state().transform.y,k:AtlasV6.state().transform.k}));
   if(camera)check(name+': identical comparison camera',()=>assert.deepEqual(transform,camera));else camera=transform;
   await checkAsync(name+': no false project-focus label',async()=>assert.equal(await page.locator('#view-status').innerText(),'Activation comparison'));
   await page.screenshot({path:path.join(out,'small-'+name+'.png'),fullPage:true});
   await page.evaluate(()=>{AtlasV6.select('category:331');AtlasV6.fitSubtree('category:331',false)});
   await page.screenshot({path:path.join(out,'small-'+name+'-focused.png'),fullPage:true});
   fs.writeFileSync(path.join(out,'small-'+name+'-geometry.json'),JSON.stringify(candidate.geometry,null,2)+'\n');
  }
  const outcomes={};for(const name of ['baseline','small','large','blocked','new-root']){
   const r=await page.evaluate(n=>AtlasPrototype.change(n),name);outcomes[name]=r.report.outcome;
   check(name+': unchanged expected outcome',()=>assert.equal(r.report.outcome,{baseline:'NO_CHANGE',small:'ACTIVATION_REVIEW_REQUIRED',large:'ACTIVATION_REBALANCE_REQUIRED',blocked:'METADATA_REQUIRED','new-root':'ACTIVATION_REBALANCE_REQUIRED'}[name]));
  }
  const viewports=[];
  for(const width of [1920,1440,1280,1200,1024,768,430,390,320])for(const light of [false,true]){
   await page.setViewportSize({width,height:width<700?900:1100});await page.evaluate(light=>document.body.classList.toggle('light',light),light);
   await page.evaluate(()=>AtlasPrototype.selectVariant('centering'));await page.evaluate(()=>AtlasPrototype.fitComparison());
   const dom=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,selectorFits:document.querySelector('#variant').getBoundingClientRect().right<=innerWidth,control:document.querySelector('#variant-controls').hidden,old:ActivationGeometry.validate(AtlasBuildGeometry,AtlasPrototype.state().result.geometry)}));
   check(width+'/'+light+': variant controls/viewport',()=>{assert.equal(dom.overflow,false);assert.equal(dom.selectorFits,true);assert.equal(dom.control,false)});
   check(width+'/'+light+': immutable valid geometry',()=>Object.values(dom.old).forEach(v=>assert.equal(v,0)));
   viewports.push({width,light,page_overflow:false});
   if([390,1440].includes(width))await page.screenshot({path:path.join(out,'variants-'+width+'-'+(light?'light':'dark')+'.png'),fullPage:true});
  }
  check('fixture JSON never rewritten',()=>assert.equal(sha(fs.readFileSync(path.join(here,'fixtures/scenarios.json'))),before['fixtures/scenarios.json']));
  check('default small report byte-identical',()=>assert.equal(sha(fs.readFileSync(path.join(here,'reports/small.json'))),before['reports/small.json']));
  check('all 732 pre-existing files unchanged',()=>{for(const[p,hash]of Object.entries(protectedFiles))assert.equal(sha(fs.readFileSync(path.join(root,p))),hash,p)});
  check('no browser runtime errors',()=>assert.deepEqual(errors,[]));check('no external network',()=>assert.deepEqual(external,[]));
  fs.writeFileSync(path.join(here,'reports/small-variant-comparison.json'),JSON.stringify({selected:Object.fromEntries(Object.entries(inventory.selected).map(([k,r])=>[k,r.metrics])),inventory:inventory.inventory},null,2)+'\n');
  fs.writeFileSync(path.join(here,'reports/variants-validation.json'),JSON.stringify({status:'PASS',checks:checks.length,tests:checks,viewports,outcomes,frozen_files:732,generation:0},null,2)+'\n');
  console.log(JSON.stringify({status:'PASS',checks:checks.length,candidates:inventory.inventory.valid_candidates,outcomes},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
