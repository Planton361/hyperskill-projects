/* Optional dependency: Playwright supplied by the caller; no saved browser state. */
const assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    const errors=[],outside=[];page.on('pageerror',e=>errors.push(e.message));
    const base=process.argv[2]||'http://127.0.0.1:8000/knowledge-graph/';
    page.on('request',r=>{if(new URL(r.url()).origin!==new URL(base).origin)outside.push(r.url());});
    await page.goto(base);await page.waitForSelector('.node');
    assert.equal(await page.locator('.node').count(),147);
    assert.match(await page.locator('#metrics').innerText(),/31 \/ 89 learned.*26 \/ 85 applied/);
    await page.locator('#search').fill('Simple Chat Bot');
    await page.locator('#results button').click();
    assert.match(await page.locator('#details').innerText(),/Status: Completed/);
    assert.match(await page.locator('#details').innerText(),/Required topics: 26/);
    assert.match(await page.locator('#details').innerText(),/project_requires \(26\)/);
    assert.equal(await page.locator('.edge.requires.highlight').count(),26);
    assert.ok(await page.locator('.node.dim').count()>0);
    assert.equal(await page.locator('.node.selected').getAttribute('data-id'),'project:113');
    await page.locator('[data-id="topic:15"]').hover();
    assert.equal(await page.locator('#tooltip').isVisible(),true);
    await page.locator('#metrics').hover();
    assert.equal(await page.locator('.node.selected').getAttribute('data-id'),'project:113');
    const before=await page.locator('#graph > g').getAttribute('transform');
    const box=await page.locator('#graph').boundingBox();
    await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.wheel(0,-200);await page.waitForTimeout(350);
    assert.notEqual(await page.locator('#graph > g').getAttribute('transform'),before);
    const beforePan=await page.locator('#graph > g').getAttribute('transform');
    await page.mouse.move(box.x+15,box.y+15);await page.mouse.down();await page.mouse.move(box.x+65,box.y+55);await page.mouse.up();
    assert.notEqual(await page.locator('#graph > g').getAttribute('transform'),beforePan);
    await page.locator('#fit').click();
    const node=page.locator('[data-id="topic:15"]'), beforeDrag=await node.getAttribute('transform'), nb=await node.locator('circle').boundingBox();
    await page.mouse.move(nb.x+nb.width/2,nb.y+nb.height/2);await page.mouse.down();await page.mouse.move(nb.x+nb.width/2+40,nb.y+nb.height/2+30,{steps:5});await page.mouse.up();
    assert.notEqual(await node.getAttribute('transform'),beforeDrag);
    await page.locator('#knowledge').click();
    assert.equal(await page.locator('.node[data-id^="topic:"]').count(),1);
    assert.equal(await page.locator('[data-id="project:380"]').count(),1);
    await page.locator('#search').fill('StringBuilder');await page.locator('#results button').click();
    assert.equal(await page.locator('#roadmap').getAttribute('aria-pressed'),'true');
    assert.match(await page.locator('#details').innerText(),/Knowledge status: unknown/);
    assert.match(await page.locator('#details').innerText(),/Applied: unknown/);
    await page.keyboard.press('Escape');assert.equal(await page.locator('.node.selected').count(),0);
    await page.locator('#search').fill('impossible-no-match');assert.match(await page.locator('#results').innerText(),/No matching/);
    await page.locator('#search').fill('');
    await page.locator('[data-id="topic:15"]').focus();await page.keyboard.press('Enter');
    assert.match(await page.locator('#details').innerText(),/Learned \/ verified/);
    for(const width of [390,320]){await page.setViewportSize({width,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);}
    assert.deepEqual(errors,[]);assert.deepEqual(outside,[]);
    assert.equal(await page.locator('#error').isVisible(),false);
    assert.equal(await page.evaluate(()=>localStorage.length+sessionStorage.length),0);
    console.log('PASS: nodes, evidence, selection, neighbors, hover, zoom, pan, drag, modes, search, keyboard, mobile, no external requests/storage.');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
