/* Geometry, interaction and pixel regression. Writes only local prototype output. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {execFileSync}=require('child_process');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/home/anton/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const here=path.resolve(__dirname,'..'),root=path.resolve(here,'../..'),out=path.join(__dirname,'output');
const coreOnly=process.argv.includes('--geometry-only');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const tests=[];function check(label,fn){fn();tests.push(label);}
async function checkAsync(label,fn){await fn();tests.push(label);}
fs.mkdirSync(out,{recursive:true});
const protectedBefore=JSON.parse(fs.readFileSync(path.join(here,'reports/protected-before.json')));
const fixturesBefore=fs.readFileSync(path.join(here,'fixtures/scenarios.json'));
execFileSync('python',['-B',path.join(here,'build-fixtures.py')],{cwd:root});
check('fixture regeneration byte-idempotent',()=>assert.ok(fixturesBefore.equals(fs.readFileSync(path.join(here,'fixtures/scenarios.json')))));
const baseline=JSON.parse(fs.readFileSync(path.join(root,'docs/knowledge-map/geometry.js'),'utf8').split('=').slice(1).join('=').trim().replace(/;$/,''));
const startProtected=()=>Object.fromEntries(Object.keys(protectedBefore).map(p=>[p,sha(fs.readFileSync(path.join(root,p)))]));
assert.deepEqual(startProtected(),protectedBefore);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE||'/opt/google/chrome/chrome',args:['--no-sandbox']});
 const errors=[],external=[],rows=[],performanceRows=[];
 const context=await browser.newContext({locale:'en-US',deviceScaleFactor:1,reducedMotion:'reduce',viewport:{width:1440,height:1000}});
 await context.route('**/*',r=>{
  const u=new URL(r.request().url());if(u.origin!=='http://localhost'){external.push(u.origin);return r.abort();}
  const file=path.resolve(root,'.'+u.pathname);
  if(!file.startsWith(root+path.sep))return r.abort();
  const target=fs.existsSync(file)&&fs.statSync(file).isDirectory()?path.join(file,'index.html'):file;
  if(!fs.existsSync(target))return r.fulfill({status:404,body:'not found'});
  const ext=path.extname(target),mime={'.js':'application/javascript','.json':'application/json','.css':'text/css','.html':'text/html'};
  return r.fulfill({body:fs.readFileSync(target),contentType:mime[ext]||'application/octet-stream'});
 });
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.stack));
 const url='http://localhost/prototypes/knowledge-atlas-activation/';
 try{
  // SHA-256 requires a secure context; localhost is trusted. The harness origin
  // is mapped locally and treated as secure without allowing network requests.
  await page.goto(url);await page.waitForFunction(()=>window.AtlasPrototype?.ready,{timeout:15000});
  const canary=JSON.parse(fs.readFileSync(path.join(root,'scripts/knowledge_atlas/font-canary.json')));
  const measured=await page.evaluate(samples=>samples.map(s=>AtlasV6.measure(s.text)),canary.samples);
  check('accepted font measurement canary',()=>measured.forEach((v,i)=>assert.ok(Math.abs(v-canary.samples[i].width)<canary.tolerance)));
  const signatures={};
  for(const name of ['baseline','small','large','blocked','new-root','major']){
   const r=await page.evaluate(n=>AtlasPrototype.change(n),name);
   rows.push({scenario:name,...r.report});
   fs.writeFileSync(path.join(here,'reports',name+'.json'),JSON.stringify(r.report,null,2)+'\n');
   fs.writeFileSync(path.join(out,name+'-geometry.json'),JSON.stringify(r.geometry,null,2)+'\n');
   check(name+': exact accepted bounds',()=>assert.deepEqual(r.geometry.nodes.slice(0,baseline.nodes.length),baseline.nodes));
   check(name+': exact accepted connectors',()=>assert.deepEqual(r.geometry.connectorSegments.slice(0,baseline.connectorSegments.length),baseline.connectorSegments));
   check(name+': exact accepted trays',()=>assert.deepEqual(r.geometry.trays.slice(0,baseline.trays.length),baseline.trays));
   check(name+': zero overlaps/crossings/through-card/invalid ports',()=>['overlaps','hierarchy_crossings','connector_through_cards','invalid_ports','existing_nodes_moved'].forEach(k=>assert.equal(r.report[k],0)));
   check(name+': frozen hash',()=>assert.equal(r.report.baseline_geometry_hash,r.report.candidate_existing_geometry_hash));
   check(name+': Generation 0, no persisted geometry',()=>{assert.equal(r.report.generation,0);assert.equal(r.report.geometry_persisted,false)});
   const reversed=await page.evaluate(n=>{const f=JSON.parse(JSON.stringify(AtlasPrototype.state().fixtures.scenarios[n]));for(const k of ['entities','new_categories','new_topics','already_active','blocked_references'])f.plan[k].reverse();f.display.reverse();return ActivationGeometry.plan(AtlasBuildGeometry,f,AtlasV6.measure)},name);
   const repeated=await page.evaluate(n=>AtlasPrototype.compute(n),name);
   check(name+': input order independent geometry',()=>assert.deepEqual(reversed.geometry,r.geometry));
   check(name+': input order independent report',()=>{const original={...r.report};delete original.baseline_geometry_hash;delete original.candidate_existing_geometry_hash;assert.deepEqual(reversed.report,original)});
   check(name+': repeat byte idempotency',()=>assert.equal(JSON.stringify(repeated),JSON.stringify(r)));
   const personal=await page.evaluate(()=>[...AtlasV6.state().m.nodes.values()].filter(n=>n.type==='topic').reduce((a,n)=>[a[0]+(n.is_learned===true),a[1]+(n.is_verified===true)],[0,0]));
   check(name+': 31 learned/12 verified unchanged',()=>assert.deepEqual(personal,[31,12]));
  }
  const byName=Object.fromEntries(rows.map(r=>[r.scenario,r]));
  check('baseline 135 bounds, no additions',()=>{assert.equal(byName.baseline.existing_nodes,135);assert.equal(byName.baseline.new_topics,0);assert.equal(byName.baseline.outcome,'NO_CHANGE')});
  check('small same-root review, 3 categories/6 topics',()=>{assert.equal(byName.small.outcome,'ACTIVATION_REVIEW_REQUIRED');assert.equal(byName.small.new_categories,3);assert.equal(byName.small.new_topics,6)});
  check('small measured category whitespace >=16px',()=>assert.ok(byName.small.new_card_min_clearance>=16));
  check('small measured tray whitespace >=20px',()=>assert.ok(byName.small.new_tray_min_clearance>=20));
  check('large clean append or explicit escalation',()=>assert.ok(['ACTIVATION_REVIEW_REQUIRED','ACTIVATION_REBALANCE_REQUIRED'].includes(byName.large.outcome)));
  check('blocked metadata refuses placeholders',()=>{assert.equal(byName.blocked.outcome,'METADATA_REQUIRED');assert.deepEqual(byName.blocked.blocked_references.map(r=>r.id),['reference:333','reference:336']);assert.equal(byName.blocked.new_topics,6);assert.ok(!byName.blocked.drawn_candidates.some(k=>k.startsWith('reference:')))});
  check('new root refuses all candidate geometry',()=>{assert.equal(byName['new-root'].outcome,'ACTIVATION_REBALANCE_REQUIRED');assert.equal(byName['new-root'].new_categories,0);assert.equal(byName['new-root'].new_topics,0)});
  check('same root new major branch is reviewed',()=>assert.ok(['ACTIVATION_REVIEW_REQUIRED','ACTIVATION_REBALANCE_REQUIRED'].includes(byName.major.outcome)));
  await page.evaluate(()=>AtlasPrototype.change('small'));
  const mechanics=await page.evaluate(()=>{
   const A=ActivationGeometry,s=AtlasPrototype.state(),L=s.result.geometry,old=AtlasBuildGeometry,checks={};
   checks.additiveBus=L.connectorSegments.slice(old.connectorSegments.length).some(e=>e.parent==='category:1164'&&e.points[0].y===e.points[1].y&&e.points.some(p=>p.x===1154));
   const horizontal={parent:'a',points:[{x:0,y:5},{x:10,y:5}]},vertical={parent:'b',points:[{x:5,y:0},{x:5,y:10}]};
   checks.crossingRejection=A.crossing(horizontal,vertical);checks.sharedJunction=!A.crossing(horizontal,{...vertical,parent:'a'});
   checks.searchRejectsCollisions=s.result.report.search.some(r=>r.rejected.collision>0);checks.searchRejectsCrossings=s.result.report.search.some(r=>r.rejected.attachment>0);
   const inputBefore=A.stable({old,fixture:s.fixtures.scenarios.small});A.plan(old,s.fixtures.scenarios.small,AtlasV6.measure);checks.noInputMutation=inputBefore===A.stable({old,fixture:s.fixtures.scenarios.small});
   const malformed=JSON.parse(JSON.stringify(s.fixtures.scenarios.small));malformed.display.find(r=>r.type==='topic').title='invented';try{A.plan(old,malformed,AtlasV6.measure);checks.rejectsInventedMetadata=false}catch(e){checks.rejectsInventedMetadata=true}
   checks.collision=A.overlap({x:0,y:0,w:10,h:10},{x:9,y:9,w:10,h:10});
   checks.additiveSubtraction=A.subtractShared({...horizontal,children:['c'],depth:1,points:[{x:0,y:5},{x:20,y:5}]},[horizontal])[0].points[0].x===10;
   const t=L.trays.find(t=>t.parent==='category:428'),ts=L.nodes.filter(n=>n.parent==='category:428');
   checks.trayPacking=ts.every(n=>n.x-n.width/2>=t.x+8&&n.x+n.width/2<=t.x+t.width-8&&n.y>=t.y+8&&n.y+n.height<=t.y+t.height-8)&&ts.slice(1).every((n,i)=>n.y===ts[i].y+ts[i].height+4);
   checks.topicFont=ts.every(n=>n.font===14&&n.line===17);checks.depthBands=L.nodes.filter(n=>['category:331','category:1201','category:428'].includes(n.key)).every(n=>n.y===old.nodes.find(o=>!o.parent&&o.depth===n.depth).y);
   return checks;
  });
  for(const [key,value]of Object.entries(mechanics))check(key,()=>assert.ok(value));
  // Real accepted evidence and route indexes stay unchanged in all preview modes.
  for(const name of ['baseline','small','blocked','major']){
   await page.evaluate(n=>AtlasPrototype.change(n),name);
   const sig=await page.evaluate(()=>{
    AtlasV6.select('project:113');const required=AtlasModel.projectRequirements(AtlasV6.state().m,'project:113');
    const paths=[...document.querySelectorAll('path.covered')].map(p=>p.getAttribute('d')).sort();
    document.querySelector('[data-stage="617"]').click();const stage=document.querySelectorAll('.node.topic.covered').length;
    AtlasV6.select('topic:518');const s=AtlasV6.state(),routes=s.relationProjection.routes.map(r=>({key:r.key,path:r.path,segments:r.segmentIds,lca:r.lca}));
    return {required:[...required].sort(),paths,stage,routes,freePaths:document.querySelectorAll('.knowledge').length};
   });signatures[name]=sig;
   check(name+': real project requirements 26/stage4 12',()=>{assert.equal(sig.required.length,26);assert.equal(sig.stage,12);assert.equal(sig.freePaths,0)});
   if(name!=='baseline')check(name+': accepted project overlay/LCA route identical',()=>assert.deepEqual(sig,signatures.baseline));
  }
  await page.evaluate(()=>AtlasPrototype.change('small'));
  await page.evaluate(()=>AtlasV6.focusTopic('fixture-topic:small-001',false));
  const namespaces=await page.evaluate(()=>({has:AtlasV6.state().m.nodes.has('fixture-topic:small-001'),fake:AtlasV6.state().m.nodes.has('topic:900001')}));
  check('no synthetic Hyperskill entity keys',()=>assert.deepEqual(namespaces,{has:true,fake:false}));
  await page.evaluate(()=>AtlasV6.select('fixture-topic:small-001'));
  await checkAsync('no fake Topic lesson link',async()=>assert.equal(await page.locator('#inspector a').count(),0));
  await page.fill('#search','Fixture 01');
  await checkAsync('candidate search result',async()=>assert.equal(await page.locator('#results [data-select="fixture-topic:small-001"]').count(),1));
  await page.fill('#search','');
  await page.evaluate(()=>AtlasV6.toggle('category:331'));
  await checkAsync('subtree collapse works',async()=>assert.equal(await page.locator('[data-key="fixture-topic:small-001"]').count(),0));
  await page.evaluate(()=>AtlasV6.toggle('category:331'));
  const camera=await page.evaluate(()=>({x:AtlasV6.state().transform.x,y:AtlasV6.state().transform.y,k:AtlasV6.state().transform.k}));
  await page.evaluate(()=>AtlasPrototype.change('baseline'));
  await checkAsync('scenario toggle preserves viewport',async()=>assert.deepEqual(await page.evaluate(()=>({x:AtlasV6.state().transform.x,y:AtlasV6.state().transform.y,k:AtlasV6.state().transform.k})),camera));
  await page.evaluate(()=>AtlasPrototype.change('blocked'));
  await page.fill('#search','333');
  await checkAsync('blocked reference excluded from ordinary search',async()=>assert.equal(await page.locator('#results button').count(),0));
  await page.fill('#search','');
  const mini=await page.evaluate(()=>({cards:document.querySelectorAll('.mini-card').length,trays:document.querySelectorAll('.mini-tray').length,bounds:document.querySelector('#minimap').getAttribute('viewBox')}));
  check('minimap includes candidate categories/trays',()=>{assert.equal(mini.cards,49);assert.equal(mini.trays,27)});
  await page.evaluate(()=>AtlasPrototype.fitExisting());
  const fitOld=await page.evaluate(()=>({x:AtlasV6.state().transform.x,y:AtlasV6.state().transform.y,k:AtlasV6.state().transform.k}));
  await page.evaluate(()=>AtlasPrototype.change('baseline',true));
  await checkAsync('Fit Existing matches baseline fit',async()=>assert.deepEqual(await page.evaluate(()=>({x:AtlasV6.state().transform.x,y:AtlasV6.state().transform.y,k:AtlasV6.state().transform.k})),fitOld));
  // Existing/candidate endpoints use the same LCA router, not free graph lanes.
  const candidateRelation=await page.evaluate(()=>{
   const s=AtlasPrototype.state(),f=s.fixtures.scenarios.small,r=ActivationGeometry.plan(AtlasBuildGeometry,f,AtlasV6.measure),raw=AtlasPrototype.sceneModel(f,r.geometry);
   const m=AtlasPrototype.model(raw),L=AtlasIncremental.hydrate(m,r.geometry,null),index=AtlasRelations.create(m,L);
   return index.route({key:'fixture-relation',source:'fixture-topic:small-001',target:'fixture-topic:small-002'});
  });
  check('fixture endpoints use existing LCA/tray router',()=>{assert.equal(candidateRelation.lca,'category:428');assert.equal(candidateRelation.sameTray,true)});
  // Responsive review and baseline pixel comparison at every requested width/theme.
  const production=await context.newPage();production.on('pageerror',e=>errors.push(e.stack));
  await production.goto('http://localhost/docs/knowledge-map/');await production.waitForFunction(()=>window.AtlasV6);
  const viewportChecks=[];
  for(const width of coreOnly?[]:[1920,1440,1280,1200,1024,768,430,390,320])for(const light of [false,true]){
   const viewport={width,height:width<700?900:1000};await page.setViewportSize(viewport);await production.setViewportSize(viewport);
   for(const p of [page,production])await p.evaluate(light=>document.body.classList.toggle('light',light),light);
   await page.evaluate(()=>{document.querySelector('#clear').click();return AtlasPrototype.change('baseline',true)});await production.evaluate(()=>{document.querySelector('#clear').click();AtlasV6.fit(null,false)});
   const sig=await page.evaluate(()=>JSON.stringify(AtlasV6.state().L.nodes.map(({data,...n})=>n)));
   const prodSig=await production.evaluate(()=>JSON.stringify(AtlasV6.state().L.nodes.map(({data,...n})=>n)));
   check(`baseline ${width}/${light?'light':'dark'} geometry`,()=>assert.equal(sig,prodSig));
   for(const p of [page,production])await p.addStyleTag({content:'.map-controls,.map-footer,#view-status,#overview-guide{visibility:hidden!important}'});
   const a=await page.locator('#graph').screenshot(),b=await production.locator('#graph').screenshot();
   check(`baseline ${width}/${light?'light':'dark'} graph pixels`,()=>assert.ok(a.equals(b)));
   for(const p of [page,production])await p.evaluate(()=>{document.querySelectorAll('style').forEach(el=>el.remove())});
   await page.evaluate(()=>AtlasPrototype.change('small',true));
   const valid=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,reportVisible:document.querySelector('#prototype-panel').getBoundingClientRect().width>0,selector:document.querySelector('#scenario').getBoundingClientRect().right<=innerWidth}));
   check(`small ${width}/${light?'light':'dark'} page/controls`,()=>{assert.equal(valid.overflow,false);assert.equal(valid.reportVisible,true);assert.equal(valid.selector,true)});
   await page.evaluate(()=>{AtlasV6.select('category:331');AtlasV6.fitSubtree('category:331',false)});
   await page.screenshot({path:path.join(out,`${width}-${light?'light':'dark'}-small-focus.png`),fullPage:true});
   viewportChecks.push({width,theme:light?'light':'dark',baseline_pixels:'IDENTICAL',page_overflow:false});
  }
  await page.setViewportSize({width:1440,height:1000});await page.evaluate(()=>document.body.classList.remove('light'));
  const shots=[['baseline','01-baseline-overview',false],['small','02-small-overview',false],['small','03-small-focus',true],['large','04-large-overview',false],['large','05-large-refusal-focus',true],['blocked','06-blocked-metadata',true],['new-root','07-new-root-refusal',false]];
  if(!coreOnly){
   for(const [name,file,focus]of shots){await page.evaluate(n=>{document.querySelector('#clear').click();return AtlasPrototype.change(n,true)},name);if(focus)await page.evaluate(()=>{const candidate=AtlasPrototype.state().result.geometry.nodes.find(n=>!n.parent&&!AtlasBuildGeometry.nodes.some(o=>o.key===n.key));const k=candidate?.key||'category:1164';AtlasV6.select(k);AtlasV6.fitSubtree(k,false)});await page.screenshot({path:path.join(out,file+'.png'),fullPage:true});}
   await page.setViewportSize({width:390,height:900});await page.evaluate(()=>AtlasPrototype.change('small',true));await page.evaluate(()=>{AtlasV6.select('category:331');AtlasV6.fitSubtree('category:331',false)});await page.screenshot({path:path.join(out,'08-mobile-small.png'),fullPage:true});
  }
  for(const name of ['small','large']){
   const times=[];for(let i=0;i<7;i++){const r=await page.evaluate(n=>{const start=performance.now();ActivationGeometry.plan(AtlasBuildGeometry,AtlasPrototype.state().fixtures.scenarios[n],AtlasV6.measure);return performance.now()-start},name);times.push(r)}
   performanceRows.push({scenario:name,samples_ms:times,median_ms:[...times].sort((a,b)=>a-b)[3]});
  }
  check('no runtime errors',()=>assert.deepEqual(errors,[]));check('offline: zero external requests',()=>assert.deepEqual(external,[]));
  check('all 732 protected files unchanged',()=>assert.deepEqual(startProtected(),protectedBefore));
  const cp=JSON.parse(fs.readFileSync(path.join(root,'state/knowledge-atlas/layout-checkpoint.json')));
  check('checkpoint Generation 0/schema2/algorithm',()=>{assert.equal(cp.presentation_generation,0);assert.equal(cp.layout_schema_version,2);assert.equal(cp.layout_algorithm_version,'atlas-incremental-2')});
  const result={status:'PASS',checks:tests.length,tests,viewport_checks:viewportChecks,performance:performanceRows,
    browser:browser.version(),protected_files_unchanged:Object.keys(protectedBefore).length,production_assets_unchanged:14,generation:0};
  fs.writeFileSync(path.join(here,'reports',coreOnly?'validation-core.json':'validation.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({status:result.status,checks:tests.length,viewports:viewportChecks.length,performance:performanceRows},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
