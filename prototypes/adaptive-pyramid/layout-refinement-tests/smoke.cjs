const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '../../../scripts/knowledge_atlas/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.env.CHROMIUM_EXECUTABLE});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:900}});
    const errors = [], failed = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('requestfailed', r => failed.push(r.url()));
    await page.goto('http://127.0.0.1:8765/docs/knowledge-map-adaptive-preview/');
    await page.waitForFunction(() => window.KnowledgeAtlas);
    const result = await page.evaluate(() => {
      const a = KnowledgeAtlas, v = a.views, before = JSON.stringify(v.m.geometry);
      a.confirm({mode:'learned'}, 'compact');
      const learned = v.scope.topics.size, localCards = v.positions.size;
      a.confirm({mode:'project',id:113,stage:617}, 'compact');
      const stageTopics = v.scope.topics.size;
      a.confirm({mode:'global'}, 'reference');
      return {learned, localCards, stageTopics, globalCards:v.positions.size,
        globalUnchanged:JSON.stringify(v.m.geometry) === before,
        previewStatus:document.querySelector('#status').textContent};
    });
    assert.equal(result.learned,31); assert.equal(result.stageTopics,12);
    assert.equal(result.globalCards,3955); assert.equal(result.globalUnchanged,true);
    assert(result.localCards > 31); assert(!result.previewStatus.includes('failed'));
    assert.deepEqual(errors,[]); assert.deepEqual(failed,[]);
    console.log(JSON.stringify({status:'PASS',browser:browser.version(),...result,errors,failed},null,2));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode=1; });
