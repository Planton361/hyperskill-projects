/* Focused completion chrome review against the isolated release candidate. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium,launchOptions}=require('../knowledge-atlas-scope-pyramid/tests/browser.cjs');
const root=path.resolve(__dirname,'../..'),base=process.env.ATLAS_PREVIEW||'http://127.0.0.1:8806/hyperskill-projects/knowledge-map/',read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const expected={global:'1306993ec8a1b7a80edda4f620fb96ba5d4803c0d81ded334b92efa85cdf1174',personal:'a60fc22e272079c91f39cfed9c01af5865bae29120e6d6f7801b02da96cd6348',course8:'ab8e05971ca8fb9d077b491a766554f5b84118e068433afe4c17faa7e91fb89b',project113:'33dc51873bcbd33fa6ad2de854dd719e525706bdb764a50578570d1f73e89034',stage617:'24edf473c9e97b7ccbb287464302a4bbf6ffadff33efdc265076b5ae6b51455e'};
const output=path.join(__dirname,'portfolio-review');fs.mkdirSync(output,{recursive:true});
const errors=[],failed=[],external=[],checks=[],fingerprints={},hash=v=>crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');
(async()=>{const browser=await chromium.launch(launchOptions);try{
 const context=await browser.newContext({viewport:{width:1440,height:1000}});
 await context.route('**/*',r=>{if(new URL(r.request().url()).origin!==new URL(base).origin){external.push(r.request().url());return r.abort();}return r.continue();});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failed.push(r.status()+' '+r.url());});
 const frame=()=>page.frameLocator('iframe[data-active=true]');
 const go=async q=>{await page.goto(base+(q||''));await page.waitForFunction(()=>window.AtlasShell?.state().activeFrame?.contentWindow.PublicProgress);if(q?.includes('skill-tree'))await page.waitForFunction(()=>AtlasShell.state().activeFrame.contentWindow.SkillProgress);};
 const geometry=()=>page.evaluate(()=>{const w=AtlasShell.state().activeFrame.contentWindow,L=(w.ScopeApp||w.AtlasV6).state().L;return[L.nodes.map(n=>[n.key,n.x,n.y,n.width,n.height,n.lines]),L.connectorSegments,L.trays,L.checkpoint];});
 await go('?view=skill-tree');fingerprints.personal=hash(await geometry());assert.equal(fingerprints.personal,expected.personal);
 let overview=await frame().locator('#progress-overview').innerText();assert.match(overview,/31 \/ 3,106/);assert.match(overview,/12 verified/);assert.match(overview,/Projects completed\n1\b/);assert.doesNotMatch(overview,/Courses completed|catalog/);assert.doesNotMatch(overview,/0.*Courses completed/);
 await page.screenshot({path:path.join(output,'after-overview.png')});await frame().locator('#progress-expand').click();
 await frame().locator('#progress-panel').getByText('1 / 11', {exact:true}).waitFor();assert.doesNotMatch(await frame().locator('#progress-panel').innerText(),/Not recorded/);
 await page.screenshot({path:path.join(output,'after-panel.png')});
 await page.evaluate(()=>{const w=AtlasShell.state().activeFrame.contentWindow;w.PortfolioGeometry=w.AtlasV6.state().L;w.PortfolioLayoutCalls=0;const old=w.AtlasLayout.build;w.AtlasLayout.build=(...args)=>{w.PortfolioLayoutCalls++;return old(...args);};});
 await frame().locator('#progress-project').selectOption('113');await frame().locator('#progress-stage').selectOption('617');
 assert.match(await frame().locator('#progress-panel').innerText(),/Completed/);assert.equal(await frame().locator('#progress-panel .completion-status').count(),1);assert.match(await frame().locator('#progress-panel').innerText(),/26 \/ 26 learned/);assert.match(await frame().locator('#progress-panel').innerText(),/12 \/ 12 learned/);
 await frame().locator('#progress-course').selectOption('31');assert.match(await frame().locator('#progress-panel').innerText(),/No associated projects/);
 await frame().locator('#progress-course').selectOption('8');await frame().locator('#progress-panel details[data-progress-details] > summary').click();assert.match(await frame().locator('.portfolio-completions').innerText(),/Project 113/);assert.match(await frame().locator('.portfolio-completions').innerText(),/2026-10-08/);
 await frame().locator('#progress-close').click();assert(await frame().locator('#progress-panel').isHidden());
 await page.evaluate(()=>AtlasShell.state().activeFrame.contentWindow.AtlasV6.select('category:73',false));await frame().locator('.category-progress').waitFor();
 await frame().locator('#inspector-pin').click();assert.equal(await frame().locator('#inspector-pin').getAttribute('aria-pressed'),'true');await frame().locator('#inspector-pin').click();await frame().locator('#inspector-close').click();
 await page.locator('#knowledge-query').fill('Java');await page.locator('#knowledge-results button').first().waitFor();await page.locator('#knowledge-query').fill('');
 assert.equal(await page.evaluate(()=>{const w=AtlasShell.state().activeFrame.contentWindow;return w.PortfolioGeometry===w.AtlasV6.state().L&&w.PortfolioLayoutCalls===0;}),true);assert.equal(hash(await geometry()),expected.personal);
 checks.push('Three independent baseline metrics; exact Course8 1/11 and Course31 known-empty; Project/Stage evidence, Category Inspector, Pin/Close/search and no layout rebuild');
 for(const [name,q,text] of [['global','',null],['course8','?course=8','1 / 11'],['project113','?project=113','Completed'],['stage617','?project=113&stage=617','12 / 12 learned']]){
  await go(q);fingerprints[name]=hash(await geometry());assert.equal(fingerprints[name],expected[name]);if(text){await frame().locator('#inspector-toggle').click();assert((await frame().locator('#inspector').innerText()).includes(text));}
 }
 checks.push('All five accepted geometry fingerprints and Course/Project/Stage Inspector completion indicators');
 await page.setViewportSize({width:390,height:844});await go('?view=skill-tree');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 const bounds=await page.evaluate(()=>{const w=AtlasShell.state().activeFrame.contentWindow;return [...w.document.querySelectorAll('#progress-overview,#progress-overview button')].map(e=>{const r=e.getBoundingClientRect();return{left:r.left,right:r.right,width:w.innerWidth};});});assert(bounds.every(b=>b.left>=0&&b.right<=b.width));
 await frame().locator('#progress-expand').click();assert(await frame().locator('#progress-close').isVisible());await page.screenshot({path:path.join(output,'narrow-panel.png')});await frame().locator('#progress-close').click();
 checks.push('390px narrow viewport: readable wrapped counters and usable scrolling/Close, no horizontal overflow');
 const projection=await (await context.request.get(base+'progress.json')).json(),catalog=read('prototypes/knowledge-atlas-scope-pyramid/catalog.json'),scopes=read('prototypes/knowledge-atlas-scope-pyramid/scope-index.json'),engine=require('../../scripts/knowledge_atlas/completion_projection.cjs'),row=scopes.projects.find(p=>p.scope_id===380);
 const completion={policy:projection.policy,projects:[...projection.projects,{project_id:380,status:'completed',attested_by:'owner',source:'validation-only/export.json',observed_at:'2026-10-08T14:00:00Z',requirements_state:'KNOWN',topic_ids:[...new Set(row.explicit_topic_ids)].sort((a,b)=>a-b)}],course_completion:projection.course_completion};
 const grown=engine.project({catalog,scopes,completion,source:{validation_only:true}});assert.equal(grown.global.learned,32);assert.equal(grown.global.verified,12);assert.equal(grown.portfolio.completed_project_count,2);assert.equal(grown.portfolio.completed_course_count,null);
 let fixture=grown;await context.route('**/knowledge-map/progress.json',r=>r.fulfill({contentType:'application/json',body:JSON.stringify(fixture)}));await page.setViewportSize({width:1440,height:1000});await go('?view=skill-tree');
 overview=await frame().locator('#progress-overview').innerText();assert.match(overview,/32 \/ 3,106/);assert.match(overview,/Projects completed\n2\b/);assert.match(overview,/12 verified/);assert.doesNotMatch(overview,/Courses completed/);
 await frame().locator('#progress-expand').click();assert.match(await frame().locator('#progress-panel').innerText(),/2 \/ 11/);
 checks.push('JSON-only synthetic Project380 updates global/project/course knowledge and portfolio, verified remains12 and Course completion remains unrecorded');
 fixture=engine.project({catalog,scopes,source:{validation_only:true},completion:{...projection,course_completion:{schema:1,records:[{course_id:8,is_completed:true,source:'owner',evidence_id:'course-8-fixture',observed_at:'2026-10-08T14:00:00Z'}]}}});await go('?view=skill-tree');
 assert.match(await frame().locator('#progress-overview').innerText(),/Courses completed\n1\b/);assert.match(await frame().locator('#progress-overview').innerText(),/31 \/ 3,106/);await frame().locator('#progress-expand').click();assert.match(await frame().locator('#progress-panel').innerText(),/Completed/);assert.equal(hash(await geometry()),expected.personal);
 checks.push('Explicit Course8 fixture adds1 Course completion without new knowledge, Projects or layout changes');
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);assert.deepEqual(external,[]);
 fs.writeFileSync(path.join(__dirname,'portfolio-browser-results.json'),JSON.stringify({status:'PASS',checks,fingerprints,synthetic:{project_id:380,learned:grown.global.learned,verified:grown.global.verified,completed_projects:grown.portfolio.completed_project_count,course8:grown.course_project_completion.find(c=>c.course_id===8)},errors,failed,external,preview:base},null,2)+'\n');console.log(JSON.stringify({status:'PASS',checks,fingerprints}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1);});
