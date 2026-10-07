/* Optional regeneration of the three retained final review views. */
const fs=require('node:fs'),path=require('node:path');
const {chromium,launchOptions}=require('./browser.cjs');
(async()=>{const browser=await chromium.launch(launchOptions);try{
 const out=path.join(__dirname,'generated');fs.mkdirSync(out,{recursive:true});
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:2});await page.goto(process.env.ATLAS_URL||'http://127.0.0.1:8791');await page.waitForFunction(()=>window.AtlasV6);
 for(const [name,key]of [['global',null],['programming-languages','category:1164'],['topic','topic:518']]){
  if(key)await page.evaluate(key=>AtlasV6.select(key,key.startsWith('topic:')),key);else await page.evaluate(()=>AtlasV6.fit(null,false));
  await page.waitForFunction(()=>!AtlasV6.state().transitioning);await page.evaluate(()=>AtlasV6.state().renderer.settled());await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  await page.screenshot({path:path.join(out,name+'.png')});
 }
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
