/* Actual V6 Canvas measurement in a disposable, offline browser context. */
const fs=require('fs'),path=require('path');
const candidates=[process.env.PLAYWRIGHT_MODULE,'playwright'].filter(Boolean);
let chromium;for(const name of candidates){try{({chromium}=require(name));break;}catch{}}
if(!chromium){console.error('Playwright required. Set PLAYWRIGHT_MODULE to an installed module; no dependency is downloaded.');process.exit(1);}
(async()=>{
 const input=JSON.parse(fs.readFileSync(0,'utf8'));
 const options={headless:true};if(process.env.CHROMIUM_EXECUTABLE)options.executablePath=process.env.CHROMIUM_EXECUTABLE;
 else if(fs.existsSync('/opt/google/chrome/chrome'))options.executablePath='/opt/google/chrome/chrome';
 const browser=await chromium.launch(options);
 try{
  const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1,locale:'en-US',reducedMotion:'reduce'});
  await page.setContent('<canvas></canvas>');
  const policy=input.canary||JSON.parse(fs.readFileSync(path.join(__dirname,'font-canary.json'),'utf8'));
  const canary=await page.evaluate(policy=>{
   const ctx=document.querySelector('canvas').getContext('2d');ctx.font=policy.font;
   return policy.samples.map(s=>{const m=ctx.measureText(s.text);return {text:s.text,width:m.width,ascent:m.actualBoundingBoxAscent,descent:m.actualBoundingBoxDescent};});
  },policy);
  if(canary.some((s,i)=>['width','ascent','descent'].some(k=>Math.abs(s[k]-policy.samples[i][k])>policy.tolerance)))throw Error('FONT_METRICS_MISMATCH: '+JSON.stringify(canary));
  if(input.action==='canary'){process.stdout.write(JSON.stringify({status:'PASS',samples:canary,browser:browser.version()}));return;}
  if(input.action==='runtime-test'){
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',r=>{
    const url=new URL(r.request().url()),key=decodeURIComponent(url.pathname.slice(1))||'index.html';
    if(url.origin!=='http://atlas.invalid'||!(key in input.assets))return r.abort();
    const contentType=key.endsWith('.js')?'application/javascript':key.endsWith('.json')?'application/json':key.endsWith('.css')?'text/css':'text/html';
    return r.fulfill({body:input.assets[key],contentType});
   });
   await page.goto('http://atlas.invalid/');await page.waitForFunction(()=>window.AtlasV6,{},{timeout:15000});
   const result=await page.evaluate(()=>{
    const s=AtlasV6.state(),raw=s.m.raw,checks=[];
    const check=(ok,label)=>{if(!ok)throw Error('Atlas runtime regression: '+label);checks.push(label);};
    check(s.L.nodes.length===raw.topics.length+raw.categories.length,'unique global nodes');
    check(document.querySelectorAll('.node.topic').length===raw.topics.length,'all topics rendered');
    check(document.querySelectorAll('.node.category').length===raw.categories.length,'all categories rendered');
    check(!document.querySelector('#error').textContent,'no UI error');
    for(const p of raw.projects){
     AtlasV6.select('project:'+p.id);
     const expected=AtlasModel.projectRequirements(s.m,'project:'+p.id).size;
     check(document.querySelector('#inspector h2').textContent===p.title,'project '+p.id+' inspector');
     if(raw.indexes.projects[String(p.id)].requirements_loaded){
      check(!!document.querySelector('#coverage'),'project '+p.id+' coverage control');
      check(document.querySelectorAll('.node.topic.covered').length===expected,'project '+p.id+' requirements');
     }
    }
    for(const stage of raw.stages){
     AtlasV6.select('project:'+stage.project_id);const button=document.querySelector('[data-stage="'+stage.id+'"]');check(!!button,'stage '+stage.id+' control');button.click();
     check(document.querySelectorAll('.node.topic.covered').length===new Set(stage.required_topic_ids).size,'stage '+stage.id+' coverage');
    }
    for(const connection of s.m.connections){check(connection.source.startsWith('topic:')&&connection.target.startsWith('topic:'),'relation topic endpoints');}
    document.querySelector('#clear').click();AtlasV6.fit();
    return {status:'PASS',checks:checks.length,nodes:s.L.nodes.length};
   });
   if(errors.length)throw Error(errors.join('\n'));process.stdout.write(JSON.stringify(result));return;
  }
  await page.route('**/*',r=>r.abort());await page.setContent('<!doctype html><canvas></canvas>');
  for(const name of ['model.js','layout.js','routing.js'])await page.addScriptTag({content:fs.readFileSync(path.join(input.runtime,name),'utf8')});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'layout_update.js'),'utf8')});
  await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'persistent_layout.js'),'utf8')});
  if(input.action.startsWith('activation-')){
   for(const name of ['activation_geometry.js','activation_variants.js'])await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,name),'utf8')});
  }
  const out=await page.evaluate(input=>{
   const ctx=document.querySelector('canvas').getContext('2d'),measure=(t,font=14,weight=400)=>{ctx.font=weight+' '+font+'px system-ui';return ctx.measureText(t).width;};
   if(input.action==='activation-validate')return ActivationGeometry.validate(input.frozen,input.geometry);
   if(input.action==='activation-preview'){
    const initial=ActivationGeometry.plan(input.geometry,input.fixture,measure);
    let result=input.variant==='current'||initial.report.outcome!=='ACTIVATION_REVIEW_REQUIRED'?initial:SmallActivationVariants.build(input.geometry,input.fixture,measure).selected[input.variant];
    if(!result)throw Error('Unknown placement variant');
    return result;
   }
   const m=AtlasModel.model(input.data);
   if(input.action==='bootstrap'){
    const result=AtlasIncremental.bootstrap(m,measure,input.legacy);result.checkpoint=AtlasPersistent.capture(m,result.geometry,result.checkpoint);
    result.geometry=AtlasPersistent.restore(m,measure,result.checkpoint).geometry;return result;
   }
   if(input.action==='restore')return AtlasPersistent.restore(m,measure,input.checkpoint,input.activeKeys);
   const restored=AtlasPersistent.restore(m,measure,input.checkpoint,input.activeKeys);
   const result=AtlasIncremental.update(m,measure,restored.checkpoint,restored.geometry,input.diff,input.rebalance,input.budget);
   if(result.status==='REBALANCE_REQUIRED')return result;
   result.checkpoint=AtlasPersistent.capture(m,result.geometry,result.checkpoint,input.rebalance?null:input.checkpoint);
   result.geometry=AtlasPersistent.restore(m,measure,result.checkpoint).geometry;return result;
  },input);
  process.stdout.write(JSON.stringify(out));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1);});
