const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium,launchOptions}=require('./browser.cjs');
const mode=process.argv[2]||'after',base=process.env.SCOPE_URL||'http://127.0.0.1:8812/prototypes/knowledge-atlas-scope-pyramid/';
(async()=>{const browser=await chromium.launch(launchOptions);try{
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:2});
 if(mode==='before')await page.route('**/layout.js',r=>r.fulfill({contentType:'text/javascript',body:fs.readFileSync(process.env.BASELINE_LAYOUT,'utf8')}));
 if(mode==='before'&&process.env.BASELINE_SCOPE_CSS)await page.route('**/scope.css',r=>r.fulfill({contentType:'text/css',body:fs.readFileSync(process.env.BASELINE_SCOPE_CSS,'utf8')}));
 await page.goto(base);await page.waitForFunction(()=>window.ScopeApp);
 const results=[];
 for(const type of ['course','project','stage']){
 await page.evaluate(type=>ScopeApp.load(ScopeApp.state().scopes.find(s=>s.scope_type===type)),type);
 results.push(await page.evaluate(()=>{
 const {m,L,projection,transform,layoutMs}=ScopeApp.state(),b=ScopeApp.bounds(),groups=new Map();
 for(const n of L.nodes.filter(n=>n.data.type==='category')){let owner=n.data;while(m.parent(owner)&&m.parent(owner)!==m.root)owner=m.parent(owner);const key=owner.key+':'+n.depth;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(n.y);}
 const deviations=[],ranges=[];for(const ys of groups.values()){const mean=ys.reduce((a,v)=>a+v,0)/ys.length;deviations.push(...ys.map(y=>Math.abs(y-mean)));ranges.push(Math.max(...ys)-Math.min(...ys));}
 const spans=L.branches.map(e=>Math.max(...e.points.map(p=>p.x))-Math.min(...e.points.map(p=>p.x))),dist=a=>{a.sort((x,y)=>x-y);return{mean:a.reduce((s,v)=>s+v,0)/a.length,median:a[Math.floor(a.length*.5)]||0,p95:a[Math.floor(a.length*.95)]||0,max:a.at(-1)||0};};
 const minimap=document.querySelector('#minimap').getBoundingClientRect(),minimapOcclusions=[...document.querySelectorAll('#world .node, #world .tray-surface')].filter(el=>{const r=el.getBoundingClientRect();return Math.min(r.right,minimap.right)>Math.max(r.left,minimap.left)+.01&&Math.min(r.bottom,minimap.bottom)>Math.max(r.top,minimap.top)+.01;}).map(el=>el.dataset.key||'tray');
 const rects=L.nodes.map(n=>({x:n.x-n.width/2,y:n.y,w:n.width,h:n.height,key:n.key})),trays=L.trays.map(t=>({x:t.x,y:t.y,w:t.width,h:t.height,topics:t.topics})),overlap=(a,b)=>Math.min(a.x+a.w,b.x+b.w)>Math.max(a.x,b.x)+.001&&Math.min(a.y+a.h,b.y+b.h)>Math.max(a.y,b.y)+.001;
 let overlapCount=0;for(let i=0;i<rects.length;i++)for(let j=i+1;j<rects.length;j++)if(overlap(rects[i],rects[j]))overlapCount++;
 for(const t of trays)for(const r of rects)if(!t.topics.includes(r.key)&&overlap(t,r))overlapCount++;
 for(let i=0;i<trays.length;i++)for(let j=i+1;j<trays.length;j++)if(overlap(trays[i],trays[j]))overlapCount++;
 const area=L.nodes.filter(n=>n.data.type!=='topic').reduce((s,n)=>s+n.width*n.height,0)+L.trays.reduce((s,t)=>s+t.width*t.height,0),worldWidth=b.x1-b.x0,worldHeight=b.y1-b.y0;
 return{overlapCount,minimapOcclusions,scope:projection.scope_type,worldWidth,worldHeight,fitAllScale:transform.k,projectedTopicPx:14*transform.k,averageSameDepthYDeviation:deviations.reduce((s,v)=>s+v,0)/deviations.length,maxSameDepthYDeviation:Math.max(...deviations),maxSameDepthYRange:Math.max(...ranges),connectorSpan:dist(spans),whitespaceRatio:1-area/(worldWidth*worldHeight),layoutMs,depthBands:Object.fromEntries([...groups].map(([k,ys])=>[k,[...new Set(ys)]]))};
 }));
 assert.equal(results.at(-1).overlapCount,0,type+' zero overlaps');
 if(mode==='after')assert.deepEqual(results.at(-1).minimapOcclusions,[],type+' minimap does not cover Fit All content');
 if(process.env.CAPTURE==='1'&&(mode==='after'||type==='course'))await page.screenshot({path:path.join(__dirname,`level-${type}-${mode}.png`)});
 }
 fs.writeFileSync(path.join(__dirname,`level-${mode}.json`),JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results,null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
