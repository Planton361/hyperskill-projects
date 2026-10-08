/* Full V6.6 scene. Technical raster levels never change semantic commands.
   Frozen world geometry; screen-constant SVG optics stay exact in a batched ink pass. */
(function(g){
'use strict';
const OPTICS_VERSION='v66-overview-progress-2';
const P=AtlasTilePaint,SIZE=512,CAP=96*1024*1024,LEVELS=Object.freeze(Array.from({length:13},(_,i)=>i-9));
function resolveStyles(){
 const host=document.querySelector('#canvas'),old=host.dataset.view,svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.style.cssText='position:absolute;width:0;height:0;overflow:hidden;pointer-events:none';host.append(svg);
 const table={},pending=[];
 function capture(){for(const [name,e]of pending.splice(0)){const s=getComputedStyle(e);table[name]={fill:s.fill,stroke:s.stroke,opacity:Number(s.opacity)*Number(s.fillOpacity),strokeOpacity:Number(s.opacity)*Number(s.strokeOpacity),width:parseFloat(s.strokeWidth),dash:s.strokeDasharray==='none'?[]:s.strokeDasharray.split(/[ ,]+/).map(parseFloat),fontFamily:s.fontFamily,weight:s.fontWeight};}}
 function style(name,classes,tag,child){const group=document.createElementNS(svg.namespaceURI,'g');group.setAttribute('class',classes);const e=document.createElementNS(svg.namespaceURI,tag);e.setAttribute('class',child);group.append(e);svg.append(group);pending.push([name,e]);}
 host.dataset.view='subtree';
 for(const [name,classes]of [['cat0','node context depth-0'],['cat1','node category depth-1'],['cat','node category depth-2'],['topic','node topic'],['learned','node topic learned'],['unknown','node topic unknown'],['reference','node reference unknown'],['selectedCat0','node context depth-0 selected'],['selectedCat1','node category depth-1 selected'],['selectedCat','node category depth-2 selected'],['selectedTopic','node topic selected'],['selectedReference','node reference selected']]){style(name,classes,'rect','card');style(name+'Label',classes,'text','label');style(name+'Core',classes,'circle','core');}
 style('meta','node category','text','category-coverage');style('ring','node topic learned','circle','ring');style('tray','','rect','tray-surface');style('edge','','path','taxonomy depth-2');style('edge0','','path','taxonomy depth-0');style('edge1','','path','taxonomy depth-1');style('context','','path','taxonomy context');style('membership','','path','membership');
 capture();host.dataset.view='overview';style('trayOverview','','rect','tray-surface');
 for(let depth=0;depth<=5;depth++){style('catOverview'+depth,'node '+(depth===0?'context':'category')+' depth-'+depth,'rect','card');style('edgeOverview'+depth,'','path','taxonomy depth-'+depth);}
 capture();host.dataset.view=old||'overview';svg.remove();return Object.freeze(table);
}
// Explicit view state controls emphasis; camera scale only converts the
// unchanged marker centre and restrained screen-space size into world units.
const PROGRESS_FRACTION=.4;
function markerOptics(c,k,view){
 const progress=c.kind==='ring'||c.style==='learnedCore';
 if(view==='overview'&&progress){
  // Outer (stroke-inclusive) squares of distinct Topics are disjoint even
  // diagonally. Neighbours are precomputed once; no frame-time pair search.
  const limit=Math.min(PROGRESS_FRACTION*(c.progressClearance??Infinity)*k,.85*(c.foreignRowClearance??Infinity)*k),ringOuter=Math.min(2.8+.75/2,limit);
  if(c.kind==='ring'){const width=Math.min(.75,ringOuter*.45);return{radius:(ringOuter-width/2)/k,width};}
  const outer=Math.min(1.65+.65/2,limit,c.progressVerified?ringOuter*.46:Infinity);
  return{radius:outer/k,width:0};
 }
 return{radius:c.kind==='core'?Math.min(7,Math.max(4,1.2/k)):Math.min(9,Math.max(7,1.8/k)),width:c.kind==='ring'?Math.min(.65,k*6):Math.min(.65,Math.max(.45,k*6))};
}
function progressNeighbours(inks,byKey){
 const anchors=inks.filter(c=>c.kind==='core'&&c.style==='learnedCore'),rings=new Map(inks.filter(c=>c.kind==='ring').map(c=>[c.entity,c]));
 for(const c of anchors){let distance=Infinity,clearance=Infinity,rowClearance=Infinity;
  for(const other of anchors){if(other.entity===c.entity)continue;
   const dx=Math.abs(c.x-other.x),dy=Math.abs(c.y-other.y),row=byKey.get(other.entity);
   distance=Math.min(distance,Math.hypot(dx,dy));clearance=Math.min(clearance,Math.max(dx,dy));
   rowClearance=Math.min(rowClearance,Math.max(row.x-c.x,c.x-row.x-row.w,row.y-c.y,c.y-row.y-row.h,0));
  }
  const metadata={progressDistance:distance,progressClearance:clearance,foreignRowClearance:rowClearance,progressVerified:rings.has(c.entity)};
  Object.assign(c,metadata);if(rings.has(c.entity))Object.assign(rings.get(c.entity),metadata);
 }
}
function overviewStyle(kind,depth){return(kind==='edge'?'edgeOverview':'catOverview')+Math.min(5,depth);}
function compile(m,L,descendants,CARD,styles=resolveStyles()){
 const commands=[],inks=[],entities=[],byKey=new Map(),measure=document.createElement('canvas').getContext('2d'),family=styles.catLabel.fontFamily;
 const push=(c)=>{c.id='command:'+commands.length;commands.push(Object.freeze(c));};
 function text(key,text,x,y,font,weight,style,maxWidth){measure.font=weight+' '+font+'px '+family;const metric=measure.measureText(text);push({entity:key,kind:'text',text,x,y,font:measure.font,style,maxWidth,bounds:{x0:x-(metric.actualBoundingBoxLeft??0)-1,y0:y-(metric.actualBoundingBoxAscent??font)-1,x1:x+(metric.actualBoundingBoxRight??metric.width)+1,y1:y+(metric.actualBoundingBoxDescent??font*.3)+1}});}
 for(const t of L.trays)inks.push({id:'tray:'+t.parent,kind:'tray',entity:t.parent,x:t.x,y:t.y,w:t.width,h:t.height,r:4,bounds:{x0:t.x,y0:t.y,x1:t.x+t.width,y1:t.y+t.height}});
 for(const [kind,paths]of [['edge',L.connectorSegments],['membership',L.buses]])for(const [i,e]of paths.entries()){const ps=e.points||[...e.d.matchAll(/[ML]\s*(-?[\d.]+)[ ,](-?[\d.]+)/g)].map(a=>({x:+a[1],y:+a[2]}));inks.push({id:kind+':'+i,kind,entity:e.parent,children:e.children||[],depth:e.depth,d:e.d,bounds:{x0:Math.min(...ps.map(p=>p.x)),y0:Math.min(...ps.map(p=>p.y)),x1:Math.max(...ps.map(p=>p.x)),y1:Math.max(...ps.map(p=>p.y))}});}
 for(const n of L.nodes){const d=n.data,leaf=AtlasModel.isLeaf(d),style=leaf?(d.type==='reference'?'reference':d.is_learned?'learned':d.is_learned==null?'unknown':'topic'):n.depth===0?'cat0':n.depth===1?'cat1':'cat',x=n.x-n.width/2,y=n.y,bounds={x0:x,y0:y,x1:x+n.width,y1:y+n.height},r=leaf?CARD.TOPIC_RADIUS:CARD.RADIUS*(n.cardScale||1);
  const entity={key:n.key,type:d.type,learned:d.is_learned,verified:d.is_verified,x,y,w:n.width,h:n.height,r,style,bounds,order:entities.length,labels:[]};entities.push(Object.freeze(entity));byKey.set(n.key,entity);
  // Transparent Topic surfaces remain real commands and hit regions.
  push({entity:n.key,kind:'rect',x,y,w:n.width,h:n.height,r,style,bounds});
  if(!leaf)inks.push({id:'outline:'+n.key,kind:'outline',entity:n.key,depth:n.depth,x,y,w:n.width,h:n.height,r,style,bounds});
  const tx=x+(leaf?CARD.TOPIC_LABEL_X:CARD.LABEL_X*(n.cardScale||1)),ty=leaf?n.height/2-(n.lines.length-1)*n.line/2+n.font*.35:(n.depth>=2?CARD.HEADER_CATEGORY:CARD.HEADER_MAIN)*(n.cardScale||1)+n.font;
  for(const [i,line]of n.lines.entries()){text(n.key,line,tx,y+ty+i*n.line,n.font,leaf?400:n.depth===0?650:600,style+'Label',n.width-44);entity.labels.push(commands.at(-1));}
  if(!leaf){const ts=descendants(d).filter(AtlasModel.isLeaf);text(n.key,ts.length+' slots · '+ts.filter(t=>t.is_learned).length+' learned',tx,y+n.height-CARD.META_BOTTOM*(n.cardScale||1),10*(n.cardScale||1),400,'meta');entity.labels.push(commands.at(-1));}
  else{inks.push({id:'core:'+n.key,kind:'core',entity:n.key,x:x+CARD.STATUS_X,y:y+n.height/2,style:style+'Core',bounds});if(d.is_learned)inks.push({id:'progress-row:'+n.key,kind:'progress-row',entity:n.key,x,y,w:n.width,h:n.height,r,style:'learnedCore',bounds});if(d.is_verified)inks.push({id:'ring:'+n.key,kind:'ring',entity:n.key,x:x+CARD.STATUS_X,y:y+n.height/2,style:'ring',bounds});}
 }
 progressNeighbours(inks,byKey);
 for(const e of entities)Object.freeze(e.labels);for(const c of inks)Object.freeze(c);
 const bounds=AtlasLayout.contentBounds(L,L.nodes),scene=Object.freeze({geometryVersion:L.checkpoint.layout_algorithm_version,commands:Object.freeze(commands),inks:Object.freeze(inks),entities:Object.freeze(entities),bounds:Object.freeze(bounds),tree:P.index(commands),inkTree:P.index(inks),hitTree:P.index(entities)});
 return{scene,byKey};
}
class Renderer{
 constructor(canvas,minimap,m,L,descendants,CARD,onReady){
  const start=performance.now(),styles=resolveStyles(),compiled=compile(m,L,descendants,CARD,styles);this.scene=compiled.scene;this.entityIds=Object.freeze(this.scene.entities.filter(e=>e.type!=='context').map(e=>e.key));this.commandIds=Object.freeze([...this.scene.commands,...this.scene.inks].map(c=>c.id));this.byKey=compiled.byKey;this.canvas=canvas;this.mini=minimap;this.ctx=canvas.getContext('2d');this.styles=styles;this.cache=new Map();this.pending=new Map();this.queue=[];this.generation=0;this.bytes=0;this.clock=0;this.worker=null;this.workerBusy=false;this.onReady=onReady;this.paths=new Map(this.scene.inks.filter(c=>c.d||c.kind==='outline'||c.kind==='tray'||c.kind==='progress-row').map(c=>{const path=c.d?new Path2D(c.d):new Path2D();if(!c.d)P.rounded(path,c.x,c.y,c.w,c.h,c.r);return[c.id,path];}));this.baseRank=Math.max(LEVELS[0],Math.floor(Math.log2(1024/(this.scene.bounds.x1-this.scene.bounds.x0))));this.baseRank=Math.min(this.baseRank,-7);this.metrics={compileMs:performance.now()-start,hits:0,misses:0,evictions:0,generated:0,generationMs:[],blockingMs:[],compositeMs:[],inkMs:[],frameMs:[],fallbacks:0,mode:'main-thread'};
  this.prewarm();this.startWorker();
 }
 sample(name,value){const a=this.metrics[name];a.push(value);if(a.length>8192)a.splice(0,a.length-8192);}
 release(image){if(image.close)image.close();else image.width=image.height=0;}
 key(rank,x,y){return this.scene.geometryVersion+':'+OPTICS_VERSION+':'+rank+':'+x+':'+y;}
 tiles(rank,b=this.scene.bounds){const r=2**rank,s=SIZE/r,o=this.scene.bounds;return{x0:Math.max(0,Math.floor((b.x0-o.x0)/s)),y0:Math.max(0,Math.floor((b.y0-o.y0)/s)),x1:Math.min(Math.ceil((o.x1-o.x0)/s)-1,Math.floor((b.x1-o.x0)/s)),y1:Math.min(Math.ceil((o.y1-o.y0)/s)-1,Math.floor((b.y1-o.y0)/s))};}
 create(w,h){const c=document.createElement('canvas');c.width=w;c.height=h;return c;}
 prewarm(){const start=performance.now(),t=this.tiles(this.baseRank);for(let y=t.y0;y<=t.y1;y++)for(let x=t.x0;x<=t.x1;x++){const a=performance.now(),tile=P.tile(this.scene,this.styles,this.baseRank,x,y,SIZE,(w,h)=>this.create(w,h));this.put(this.baseRank,x,y,tile.canvas,true);this.sample('blockingMs',performance.now()-a);this.metrics.generated++;}this.metrics.prewarmMs=performance.now()-start;this.buildMini();}
 startWorker(){if(typeof Worker==='undefined'||typeof OffscreenCanvas==='undefined')return;try{const w=new Worker('tile-worker.js');w.onmessage=e=>{const q=e.data;if(q.type==='ready'){this.workerReady=true;this.pump();}else if(q.type==='tile'){this.workerBusy=false;const job=this.pending.get(q.id);this.pending.delete(q.id);if(job&&q.generation===this.generation){this.put(job.rank,job.x,job.y,q.bitmap);this.metrics.generated++;this.sample('generationMs',q.ms);this.onReady();}else q.bitmap.close();this.pump();}else if(q.type==='error')this.workerFailed();};w.onerror=()=>this.workerFailed();w.postMessage({type:'init',scene:this.scene,styles:this.styles});this.worker=w;this.metrics.mode='worker';}catch(e){this.workerFailed();}}
 workerFailed(){this.worker?.terminate();this.worker=null;this.workerReady=false;this.workerBusy=false;this.metrics.mode='main-thread';for(const job of this.pending.values())this.queue.push(job);this.pending.clear();this.pump();}
 put(rank,x,y,image,pinned=false){const key=this.key(rank,x,y),bytes=image.width*image.height*4;this.cache.set(key,{rank,x,y,image,bytes,pinned,used:++this.clock});this.bytes+=bytes;while(this.bytes>CAP){let oldest=null;for(const t of this.cache.values())if(!t.pinned&&(!oldest||t.used<oldest.used))oldest=t;if(!oldest)throw Error('Pinned overview exceeds tile cap');this.cache.delete(this.key(oldest.rank,oldest.x,oldest.y));this.bytes-=oldest.bytes;this.release(oldest.image);this.metrics.evictions++;}}
 request(rank,x,y){const id=this.key(rank,x,y);if(this.pending.has(id)||this.queue.some(j=>j.id===id))return;this.metrics.misses++;this.queue.push({id,rank,x,y,generation:this.generation});this.pump();}
 pump(){if(this.worker){if(!this.workerReady||this.workerBusy||!this.queue.length)return;this.workerBusy=true;const job=this.queue.shift();this.pending.set(job.id,job);this.worker.postMessage({...job,type:'tile',size:SIZE});return;}if(this.mainScheduled||!this.queue.length)return;this.mainScheduled=true;setTimeout(()=>{this.mainScheduled=false;const job=this.queue.shift();if(job&&job.generation===this.generation&&!this.cache.has(job.id)){const start=performance.now(),tile=P.tile(this.scene,this.styles,job.rank,job.x,job.y,SIZE,(w,h)=>this.create(w,h));this.put(job.rank,job.x,job.y,tile.canvas);this.metrics.generated++;this.sample('blockingMs',performance.now()-start);this.onReady();}this.pump();},0);}
 resize(w,h,dpr=devicePixelRatio){this.width=w;this.height=h;this.dpr=dpr;const width=Math.round(w*dpr),height=Math.round(h*dpr);if(this.canvas.width!==width)this.canvas.width=width;if(this.canvas.height!==height)this.canvas.height=height;}
 hit(x,y){return P.query(this.scene.hitTree,{x0:x,y0:y,x1:x,y1:y}).map(i=>this.scene.entities[i]).filter(e=>x>=e.x&&x<=e.x+e.w&&y>=e.y&&y<=e.y+e.h).sort((a,b)=>b.order-a.order)[0]?.key||null;}
 stroke(ctx,s,k,path){if(s.stroke==='none'||s.width===0)return;ctx.strokeStyle=s.stroke;ctx.globalAlpha=s.strokeOpacity;ctx.lineWidth=s.width/k;ctx.setLineDash(s.dash.map(x=>x/k));if(path)ctx.stroke(path);else ctx.stroke();ctx.setLineDash([]);}
 ink(ctx,t,view,context,clip,part){const k=t.k,ids=P.query(this.scene.inkTree,clip).sort((a,b)=>a-b),batches=new Map(),progressGlyphs=[];let progressRows=null;const batch=(style,c)=>{if(!batches.has(style))batches.set(style,new Path2D());const p=batches.get(style);if(this.paths.has(c.id))p.addPath(this.paths.get(c.id));else if(c.kind==='core'||c.kind==='ring'){const r=markerOptics(c,k,view).radius;p.moveTo(c.x+r,c.y);p.arc(c.x,c.y,r,0,Math.PI*2);}else P.rounded(p,c.x,c.y,c.w,c.h,c.r);};
 for(const i of ids){const c=this.scene.inks[i];if(!P.boxIntersects(c.bounds,clip))continue;
  if(view==='overview'&&c.kind==='progress-row'&&part==='back'){(progressRows??=new Path2D()).addPath(this.paths.get(c.id));continue;}
  if(view==='overview'&&part==='front'&&(c.kind==='ring'||c.kind==='core'&&c.style==='learnedCore')){progressGlyphs.push(c);continue;}
  if(part==='back'){if(c.kind==='tray'){const s=this.styles[view==='overview'?'trayOverview':'tray'];ctx.globalAlpha=s.opacity;ctx.fillStyle=s.fill;ctx.fill(this.paths.get(c.id));batch(view==='overview'?'trayOverview':'tray',c);}else if(c.d)batch(c.kind==='membership'?'membership':view==='overview'?overviewStyle('edge',c.depth):c.children.some(key=>context.has(key))?'context':c.depth===0?'edge0':c.depth===1?'edge1':'edge',c);}
  else if(c.kind==='outline')batch(view==='overview'?overviewStyle('category',c.depth):c.style,c);else if(c.kind==='core'||c.kind==='ring')batch(c.style,c);
 }
 const ordered=view==='overview'&&part==='front'?[...batches].sort(([a],[b])=>Number(a==='learnedCore'||a==='ring')-Number(b==='learnedCore'||b==='ring')):batches;
 for(const [style,p]of ordered){const s={...this.styles[style]};if(part==='front'&&(style.endsWith('Core')||style==='ring')){s.width=markerOptics({kind:style==='ring'?'ring':'core',style},k,view).width;if(style!=='ring'){ctx.fillStyle=s.fill;ctx.globalAlpha=s.opacity;ctx.fill(p);}}this.stroke(ctx,s,k,p);}
 // Learned tint occupies the original disjoint row rectangle, behind text.
 if(progressRows){ctx.fillStyle=this.styles.learnedCore.fill;ctx.globalAlpha=.28;ctx.fill(progressRows);}
 for(const c of progressGlyphs){const optics=markerOptics(c,k,view),s={...this.styles[c.style],width:optics.width};ctx.beginPath();ctx.arc(c.x,c.y,optics.radius,0,Math.PI*2);if(c.kind==='core'){ctx.fillStyle=s.fill;ctx.globalAlpha=s.opacity;ctx.fill();}else this.stroke(ctx,s,k);}
 }
 render(t,view,selected,context=new Set(),hover=null,focused=false){if(!this.width)return;if(this.dpr!==devicePixelRatio){this.resize(this.width,this.height);this.buildMini();}const started=performance.now(),ctx=this.ctx,dpr=this.dpr,k=t.k,o=this.scene.bounds,pad=3/k,clip={x0:-t.x/k-pad,y0:-t.y/k-pad,x1:(this.width-t.x)/k+pad,y1:(this.height-t.y)/k+pad};
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,this.width,this.height);ctx.setTransform(k*dpr,0,0,k*dpr,t.x*dpr,t.y*dpr);let a=performance.now();this.ink(ctx,t,view,context,clip,'back');this.sample('inkMs',performance.now()-a);
 const rank=Math.max(this.baseRank,Math.min(LEVELS.at(-1),Math.ceil(Math.log2(k*dpr)))),r=2**rank,tileRange=this.tiles(rank,clip),visibleJobs=new Set();a=performance.now();ctx.setTransform(dpr,0,0,dpr,0,0);ctx.globalAlpha=1;ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
 for(let y=tileRange.y0;y<=tileRange.y1;y++)for(let x=tileRange.x0;x<=tileRange.x1;x++){const id=this.key(rank,x,y);visibleJobs.add(id);let tile=this.cache.get(id);if(tile)this.metrics.hits++;else{this.request(rank,x,y);this.metrics.fallbacks++;for(let lower=rank-1;lower>=this.baseRank&&!tile;lower--)tile=this.cache.get(this.key(lower,Math.floor(x/2**(rank-lower)),Math.floor(y/2**(rank-lower))));}if(!tile)throw Error('Complete overview fallback missing');tile.used=++this.clock;
 const tr=2**tile.rank,worldSize=SIZE/r,wx=o.x0+x*worldSize,wy=o.y0+y*worldSize,sx=(wx-o.x0)*tr-tile.x*SIZE+2,sy=(wy-o.y0)*tr-tile.y*SIZE+2,sw=worldSize*tr;
 ctx.drawImage(tile.image,sx,sy,sw,sw,wx*k+t.x,wy*k+t.y,worldSize*k,worldSize*k);
 }
 // Discard obsolete unstarted work. At most one worker job is in flight.
 this.queue=this.queue.filter(j=>visibleJobs.has(j.id));this.sample('compositeMs',performance.now()-a);ctx.setTransform(k*dpr,0,0,k*dpr,t.x*dpr,t.y*dpr);a=performance.now();this.ink(ctx,t,view,context,clip,'front');this.interaction(ctx,t,selected,hover,focused,view);this.sample('inkMs',performance.now()-a);ctx.globalAlpha=1;this.updateMini(t,selected);this.sample('frameMs',performance.now()-started);this.last={t:{x:t.x,y:t.y,k:t.k},view,selected};
 }
 interaction(ctx,t,selected,hover,focused,view){for(const key of [...new Set([hover,selected].filter(Boolean))]){const e=this.byKey.get(key);if(!e)continue;const leaf=e.type==='topic'||e.type==='reference',style=key===selected?(leaf?e.type==='reference'?'selectedReference':'selectedTopic':e.style==='cat0'?'selectedCat0':e.style==='cat1'?'selectedCat1':'selectedCat'):leaf?'selectedCat':e.style,s={...this.styles[style]};if(key===hover&&key!==selected){s.width=leaf?1.2:this.styles[e.style].width;s.stroke=leaf?this.styles.cat.stroke:this.styles.selectedCat.stroke;s.strokeOpacity=1;}
 ctx.fillStyle=s.fill;ctx.globalAlpha=s.opacity;ctx.beginPath();P.rounded(ctx,e.x,e.y,e.w,e.h,e.r);ctx.fill();this.stroke(ctx,s,t.k);for(const c of e.labels)P.paint(ctx,{...c,style:key===selected&&c.style!=='meta'?'selectedTopicLabel':c.style},this.styles);
 for(const c of this.scene.inks.filter(c=>c.entity===key&&(c.kind==='core'||c.kind==='ring'))){const optics=markerOptics(c,t.k,view),r=optics.radius,s={...this.styles[c.style],width:optics.width};ctx.beginPath();ctx.arc(c.x,c.y,r,0,Math.PI*2);if(c.kind==='core'){ctx.fillStyle=s.fill;ctx.globalAlpha=s.opacity;ctx.fill();}this.stroke(ctx,s,t.k);}
 }}
 buildMini(){const d=devicePixelRatio,w=178,h=72,c=this.create(Math.round(w*d),Math.round(h*d)),ctx=c.getContext('2d'),b=this.scene.bounds,k=Math.min(w/(b.x1-b.x0),h/(b.y1-b.y0)),t={k,x:(w-(b.x1-b.x0)*k)/2-b.x0*k,y:(h-(b.y1-b.y0)*k)/2-b.y0*k};ctx.setTransform(k*d,0,0,k*d,t.x*d,t.y*d);this.ink(ctx,t,'overview',new Set(),b,'back');for(const command of this.scene.commands)P.paint(ctx,command,this.styles);this.ink(ctx,t,'overview',new Set(),b,'front');if(this.miniBase)this.release(this.miniBase);this.miniBase=c;this.miniTransform=t;this.mini.width=c.width;this.mini.height=c.height;}
 updateMini(t,selected){const ctx=this.mini.getContext('2d'),d=devicePixelRatio,a=this.miniTransform;ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,this.mini.width,this.mini.height);ctx.drawImage(this.miniBase,0,0);ctx.setTransform(d,0,0,d,0,0);ctx.lineWidth=1;ctx.strokeStyle=this.styles.catLabel.fill;ctx.fillStyle=this.styles.catLabel.fill;ctx.globalAlpha=.08;const b=this.scene.bounds,x0=Math.max(b.x0,-t.x/t.k),y0=Math.max(b.y0,-t.y/t.k),x1=Math.min(b.x1,(this.width-t.x)/t.k),y1=Math.min(b.y1,(this.height-t.y)/t.k),x=a.x+x0*a.k,y=a.y+y0*a.k,w=Math.max(0,x1-x0)*a.k,h=Math.max(0,y1-y0)*a.k;ctx.fillRect(x,y,w,h);ctx.globalAlpha=1;ctx.strokeRect(x,y,w,h);if(selected){const e=this.selectionBounds;if(e){ctx.strokeStyle=this.styles.selectedCat.stroke;ctx.lineWidth=1.3;ctx.strokeRect(e.x0*a.k+a.x,e.y0*a.k+a.y,(e.x1-e.x0)*a.k,(e.y1-e.y0)*a.k);}}}
 invalidateStyles(){this.generation++;this.worker?.terminate();this.worker=null;this.workerBusy=false;this.workerReady=false;for(const t of this.cache.values())this.release(t.image);this.cache.clear();this.bytes=0;this.queue=[];this.pending.clear();this.styles=resolveStyles();this.prewarm();this.startWorker();this.onReady();}
 inventoryForLevel(rank){if(!LEVELS.includes(rank))throw Error('Unsupported raster resolution');return Object.freeze({rank,semantic_entity_ids:this.entityIds,render_command_ids:this.commandIds});}
 stats(){return{...this.metrics,geometryVersion:this.scene.geometryVersion,opticsVersion:OPTICS_VERSION,tiles:this.cache.size,bytes:this.bytes,cap:CAP,queued:this.queue.length,inFlight:this.pending.size,baseRank:this.baseRank,levels:LEVELS,size:SIZE,semanticEntities:this.entityIds,commandIds:this.commandIds};}
 async settled(){while(this.queue.length||this.pending.size||this.mainScheduled)await new Promise(r=>setTimeout(r,10));await new Promise(r=>requestAnimationFrame(r));}
}
g.AtlasTiled={Renderer,compile,resolveStyles,markerOptics,overviewStyle,progressFraction:PROGRESS_FRACTION,opticsVersion:OPTICS_VERSION,levels:LEVELS,tileSize:SIZE,memoryCap:CAP};
})(globalThis);
