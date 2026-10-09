/* Refactors regular-cpu-experiment/grid.js: uniform grids, discrete module
   planning and measured glyph guards. Reuses cpu-experiment relationships.
   Neither progress nor filters are geometry inputs. No continuous leaf cuts. */
(function(g){
'use strict';
const POLICY=Object.freeze({gap:8,padding:12,header:52,moduleGap:12,bankCapacity:96,titleFont:14,titleLine:18,titleLines:3,targetAspect:1.45});
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),snap=v=>Math.ceil(v/4)*4;
function wrap(value,width,measure,size=14,weight=400){
 const lines=[];let line='';for(const word of String(value).split(/\s+/)){const next=line?line+' '+word:word;if(line&&measure(next,size,weight)>width){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);return lines;
}
function shorten(value,width,measure,size=14,weight=400){if(measure(value,size,weight)<=width)return value;let lo=0,hi=value.length;while(lo<hi){const mid=Math.ceil((lo+hi)/2);if(measure(value.slice(0,mid)+'…',size,weight)<=width)lo=mid;else hi=mid-1;}return value.slice(0,lo).trimEnd()+'…';}
function cardPolicy(problems,measure){
 const samples=[240,264,288,312,336].map(width=>{const lines=problems.map(p=>wrap(p.title||'Title not recorded',width-28,measure).length),full=lines.filter(n=>n<=3).length;return{width,full,coverage:full/Math.max(1,problems.length),maxLines:Math.max(0,...lines)};});
 const chosen=samples.find(s=>s.coverage>=.99)||samples.at(-1);
 const tileHeight=snap(32+(POLICY.titleLines-1)*POLICY.titleLine+18+10+16+8);
 return {...POLICY,tileWidth:chosen.width,tileHeight,measurements:{samples,selected:chosen,problems:problems.length,criterion:'smallest width with >=99% full titles in 3 measured 14px lines; height reserves number, 3 title lines, tags and padding'}};
}
function textPlan(p,P,measure){
 const width=P.tileWidth-28,full=wrap(p.title||'Title not recorded',width,measure),lines=full.slice(0,3);
 if(full.length>3)lines[2]=shorten(lines[2]+' …',width,measure);
 const tags=p.topicTags||[],primary=tags.find(t=>p.placement?.topicMemberships?.[t]===p.primaryTaxonomyId),ordered=primary?[primary,...tags.filter(t=>t!==primary)]:tags;
 let shown=ordered.slice(0,2),remaining=tags.length-shown.length,value=shown.join(' · ')+(remaining?' +'+remaining:'');
 if(measure(value,10)>width){shown=ordered.slice(0,1);remaining=tags.length-shown.length;value=shown.join('')+(remaining?' +'+remaining:'');}
 if(!tags.length)value='Unclassified · needs review';
 return{lines,fullLines:full,truncated:full.length>3,tags:shorten(value,width,measure,10),displayedTags:shown,remainingTags:remaining,number:'#'+p.displayNumber,difficulty:p.difficulty||'Unknown'};
}
function pruneFree(free){return free.filter((r,i)=>r.w>0&&r.h>0&&!free.some((b,j)=>j!==i&&b.x<=r.x&&b.y<=r.y&&b.x+b.w>=r.x+r.w&&b.y+b.h>=r.y+r.h&&(j<i||b.w*b.h>r.w*r.h)));}
// Bounded non-rotating MaxRects / bottom-left placement. Searches MODULES only,
// never individual Problems. Split all intersecting maximal free rectangles.
function pack(items,limit,gap){
 let free=[{x:0,y:0,w:limit,h:items.reduce((s,i)=>s+Math.max(...i.options.map(o=>o.height))+gap,0)}],placed=[];
 for(const item of items){let best=null;
  for(const r of free)for(const o of item.options){if(o.width+gap>r.w+.01||o.height+gap>r.h+.01)continue;
   const score=[r.y+o.height,r.x,o.width*o.height];if(!best||score[0]<best.score[0]||score[0]===best.score[0]&&(score[1]<best.score[1]||score[1]===best.score[1]&&score[2]<best.score[2]))best={key:item.key,x:r.x,y:r.y,width:o.width,height:o.height,plan:o,score};}
  if(!best)return null;placed.push(best);const used={x:best.x,y:best.y,w:best.width+gap,h:best.height+gap},split=[];
  for(const r of free){if(used.x>=r.x+r.w||used.x+used.w<=r.x||used.y>=r.y+r.h||used.y+used.h<=r.y){split.push(r);continue;}
   if(used.x>r.x)split.push({...r,w:used.x-r.x});if(used.x+used.w<r.x+r.w)split.push({...r,x:used.x+used.w,w:r.x+r.w-used.x-used.w});
   if(used.y>r.y)split.push({...r,h:used.y-r.y});if(used.y+used.h<r.y+r.h)split.push({...r,y:used.y+used.h,h:r.y+r.h-used.y-used.h});}
  free=pruneFree(split);
 }
 return{children:placed,width:Math.max(0,...placed.map(p=>p.x+p.width)),height:Math.max(0,...placed.map(p=>p.y+p.height))};
}
function bestOptions(options){
 const sorted=options.sort((a,b)=>a.score-b.score||a.width-b.width||a.height-b.height),out=[];
 for(const p of sorted)if(!out.some(o=>Math.abs(Math.log(o.width/o.height)-Math.log(p.width/p.height))<.18)){out.push(p);if(out.length===3)break;}
 return out.length?out:[sorted[0]];
}
function build(model,measure){
 const started=performance.now(),data=new Map(),plans=new Map(),nodes=[],byKey=new Map(),grids=[],aliases=new Map();
 for(const n of model.nodes.values())if(n.kind!=='layout-group')data.set(n.key,{...n,children:[]});
 for(const n of data.values())if(n.key!==model.root.key){n.parent=n.type==='problem'?(n.problem?.primaryTaxonomyId||n.semanticParent||n.parent):n.parent;data.get(n.parent).children.push(n);}
 const allProblems=[...data.values()].filter(n=>n.type==='problem'),P=cardPolicy(allProblems.map(n=>n.problem),measure),root=data.get(model.root.key),empty=[];
 function clean(n){n.children=n.children.filter(c=>c.type==='problem'||clean(c));if(n.type!=='problem'&&!n.children.length){empty.push(n.key);return false;}return true;}clean(root);
 // Collapse only a redundant Category->single Topic presentation wrapper. Both
 // semantic IDs remain mapped to the same physical module; no identity is merged.
 for(const n of data.values())if(n.kind==='category'&&n.children.length===1&&n.children[0].kind==='pattern'){
  const child=n.children[0],parent=data.get(n.parent);child.presentationTitle=n.title===child.title?child.title:n.title+' / '+child.title;parent.children=parent.children.map(c=>c===n?child:c);aliases.set(n.key,child.key);
 }
 const title=n=>n.presentationTitle||n.displayTitle||n.title;
 function gridOptions(n,leaves){
  const count=leaves.length,options=[],max=Math.max(1,Math.min(count,Math.ceil(Math.sqrt(count*P.tileHeight/P.tileWidth)*3)));
  for(let cols=1;cols<=max;cols++){const rows=Math.ceil(count/cols),width=2*P.padding+cols*(P.tileWidth+P.gap)-P.gap,height=P.header+2*P.padding+rows*(P.tileHeight+P.gap)-P.gap;
   const aspect=width/height,unused=cols*rows-count,extreme=Math.max(0,Math.abs(Math.log(aspect))-Math.log(3));
   const score=width*height*(1+.04*Math.log(aspect/P.targetAspect)**2+2*extreme**2)+unused*P.tileWidth*P.tileHeight*.3;
   options.push({width,height,cols,rows,leaves,children:[],score,title:title(n),key:n.key});}
  return bestOptions(options);
 }
 function modules(n,items){
  items.sort((a,b)=>Math.min(...b.options.map(o=>o.width*o.height))-Math.min(...a.options.map(o=>o.width*o.height))||a.key.localeCompare(b.key));
  const area=items.reduce((s,i)=>s+Math.min(...i.options.map(o=>o.width*o.height)),0),minimum=Math.max(...items.map(i=>Math.min(...i.options.map(o=>o.width)))),limits=new Set([snap(minimum+P.moduleGap)]);
  for(const ratio of [.75,1,1.2,1.45,1.7,2,2.4])for(const factor of [1,1.12])limits.add(snap(Math.max(minimum+P.moduleGap,Math.sqrt(area*ratio)*factor)));
  const options=[];
  for(const limit of limits){const p=pack(items,limit,P.moduleGap);if(!p)continue;const width=p.width+2*P.padding,height=p.height+P.header+2*P.padding,aspect=width/height;
   const score=width*height*(1+(n.kind==='root'?.06:.025)*Math.log(aspect/P.targetAspect)**2);
   options.push({...p,width,height,leaves:[],score,title:title(n),key:n.key});}
  if(!options.length)throw Error('No bounded module packing');return bestOptions(options);
 }
 function plan(n){
  const leaves=n.children.filter(c=>c.type==='problem').sort((a,b)=>Number(a.problem.displayNumber)-Number(b.problem.displayNumber)||a.key.localeCompare(b.key)),cats=n.children.filter(c=>c.type!=='problem');
  if(!cats.length){
   if(leaves.length<=P.bankCapacity)plans.set(n.key,gridOptions(n,leaves));
   else{const banks=[];for(let i=0;i<leaves.length;i+=P.bankCapacity){const bank={key:'bank:'+n.key+':'+i,displayTitle:(n.title||n.displayTitle)+' · bank '+(i/P.bankCapacity+1),kind:'bank',type:'category',parent:n.key,leafKeys:leaves.slice(i,i+P.bankCapacity).map(p=>p.key)};data.set(bank.key,bank);banks.push({key:bank.key,options:gridOptions(bank,leaves.slice(i,i+P.bankCapacity))});}plans.set(n.key,modules(n,banks));}
  }else{if(leaves.length)throw Error('Mixed semantic branch not supported');for(const c of cats)plan(c);plans.set(n.key,modules(n,cats.map(c=>({key:c.key,options:plans.get(c.key)}))));}
 }
 plan(root);
 function place(n,p,x,y,depth,parent=null){
  const record={key:n.key,data:n,x:x+p.width/2,y,width:p.width,height:p.height,header:P.header,depth,font:14,line:18,lines:wrap(p.title,p.width-24,measure,14,600),rect:{x,y,w:p.width,h:p.height},presentationTitle:p.title,physicalParent:parent};nodes.push(record);byKey.set(n.key,record);
  if(p.leaves.length){const gx=x+P.padding,gy=y+P.header+P.padding,grid={parent:n.kind==='bank'?n.parent:n.key,bank:n.key,x:gx,y:gy,cols:p.cols,rows:p.rows,count:p.leaves.length,leaves:p.leaves};grids.push(grid);
   p.leaves.forEach((leaf,i)=>{const col=i%p.cols,row=Math.floor(i/p.cols),lx=gx+col*(P.tileWidth+P.gap),ly=gy+row*(P.tileHeight+P.gap),tile={key:leaf.key,data:leaf,x:lx+P.tileWidth/2,y:ly,width:P.tileWidth,height:P.tileHeight,header:0,depth:depth+1,font:14,line:18,column:col,row,physicalParent:n.key,rect:{x:lx,y:ly,w:P.tileWidth,h:P.tileHeight},text:textPlan(leaf.problem,P,measure)};nodes.push(tile);byKey.set(tile.key,tile);});}
  for(const c of p.children)place(data.get(c.key),c.plan,x+P.padding+c.x,y+P.header+P.padding+c.y,depth+1,n.key);
 }
 place(root,plans.get(root.key)[0],0,0,0);for(const [alias,key]of aliases)if(byKey.has(key))byKey.set(alias,byKey.get(key));
 const regions=nodes.filter(n=>n.data.type!=='problem'),leaves=nodes.filter(n=>n.data.type==='problem'),bound=byKey.get(root.key).rect;
 return{nodes,byKey,regions,leaves,grids,aliases,empty,policy:P,bounds:{x0:0,y0:0,x1:bound.w,y1:bound.h},kind:'optimized-cpu-floorplan',milliseconds:performance.now()-started};
}
function visible(L,b){
 const out=[],P=L.policy;
 for(const grid of L.grids){const x1=grid.x+grid.cols*(P.tileWidth+P.gap)-P.gap,y1=grid.y+grid.rows*(P.tileHeight+P.gap)-P.gap;if(x1<b.x0||grid.x>b.x1||y1<b.y0||grid.y>b.y1)continue;
  const c0=clamp(Math.floor((b.x0-grid.x)/(P.tileWidth+P.gap)),0,grid.cols-1),c1=clamp(Math.floor((b.x1-grid.x)/(P.tileWidth+P.gap)),0,grid.cols-1),r0=clamp(Math.floor((b.y0-grid.y)/(P.tileHeight+P.gap)),0,grid.rows-1),r1=clamp(Math.floor((b.y1-grid.y)/(P.tileHeight+P.gap)),0,grid.rows-1);
  for(let r=r0;r<=r1;r++)for(let c=c0;c<=c1;c++){const leaf=grid.leaves[r*grid.cols+c];if(leaf)out.push(L.byKey.get(leaf.key));}}
 return out;
}
function hit(L,x,y){const P=L.policy;for(const grid of L.grids){const col=Math.floor((x-grid.x)/(P.tileWidth+P.gap)),row=Math.floor((y-grid.y)/(P.tileHeight+P.gap));if(col<0||col>=grid.cols||row<0||row>=grid.rows)continue;const leaf=grid.leaves[row*grid.cols+col],n=leaf&&L.byKey.get(leaf.key);if(n&&x>=n.rect.x&&x<=n.rect.x+n.width&&y>=n.y&&y<=n.y+n.height)return n;}return [...L.regions].reverse().find(n=>x>=n.rect.x&&x<=n.rect.x+n.width&&y>=n.y&&y<=n.y+n.height);}
// Exact set projection retained from the original CPU experiment.
function relations(index,progress,selected,activeTag,visibleIds){
 const problem=index.problems.get(selected),regions=new Set(),problems=new Set(),links=[];
 if(problem){problems.add(problem.id);for(const id of LeetCodeModel.memberships(index,problem))regions.add(id);for(const id of problem.secondaryTaxonomyIds)links.push({from:problem.id,to:id});}
 else if(index.tax.has(selected))for(const id of progress.coverage.get(selected).members)if(visibleIds.has(id))problems.add(id);
 if(activeTag){problems.clear();for(const p of index.problems.values())if(visibleIds.has(p.id)&&p.topicTags.includes(activeTag))problems.add(p.id);}return{regions,problems,links};
}
// Presentation cache only: no world dimensions or coordinates are changed.
const headingCaches=new WeakMap();
const cardCaches=new WeakMap();
const glyphCaches=new WeakMap(),TILE_ONLY=Object.freeze({level:0,reason:'number-area'});
function glyphMetric(ctx,value,size,weight=400){
 let cache=glyphCaches.get(ctx);if(!cache){cache=new Map();glyphCaches.set(ctx,cache);}
 const key=weight+'|'+size+'|'+value;ctx.font=weight+' '+size+'px Atlas';
 if(!cache.has(key)){if(cache.size>=16384)cache.clear();cache.set(key,ctx.measureText(value));}return cache.get(key);
}
function screenCardPlan(ctx,n,screenWidth,screenHeight,solved=false){
 // Conservative 2px buckets reuse wrapping during motion, never exceed the
 // actual card. This presentation cache is independent of the world text plan.
 const w=Math.floor(screenWidth/2)*2,h=Math.floor(screenHeight/2)*2;
 if(w<24||h<18)return TILE_ONLY;
 let cache=cardCaches.get(ctx);if(!cache){cache=new Map();cardCaches.set(ctx,cache);}
 const title=n.data.problem.title||'Title not recorded',key=n.key+'|'+w+'|'+h+'|'+solved+'|'+title;
 if(cache.has(key))return cache.get(key);
 const pad=clamp(w*.04,4,10),padY=clamp(h*.04,4,6),width=w-2*pad,numberSize=Math.round(clamp(w*11/240,11,13)),titleSize=Math.round(clamp(w*14/240,14,18)),metaSize=11;
 const measure=(value,size,weight=400)=>glyphMetric(ctx,value,size,weight).width;
 const number=n.text.number+(solved?' ✓':''),numberLine=numberSize+3,titleLine=titleSize+3,metaLine=metaSize+3;
 const plan={level:0,width:w,height:h,pad,padY,usableWidth:width,title,number,numberSize,titleSize,metaSize,numberY:padY,titleY:padY+numberLine+3,titleLine,lines:[],truncated:false,reason:'number-glyph-fit'};
 if(measure(number,numberSize,600)+2<=width&&2*padY+numberLine<=h){
  plan.level=1;plan.reason='number-only-capacity';
  const full=wrap(title,width-2,value=>measure(value,titleSize)),fit=Math.min(3,Math.floor((h-padY-plan.titleY)/titleLine));
  if(fit>=1){
   plan.lines=full.slice(0,fit).map(line=>shorten(line,width-2,value=>measure(value,titleSize)));plan.truncated=full.length>fit||plan.lines.some((line,i)=>line!==full[i]);
   if(plan.truncated)plan.lines[plan.lines.length-1]=shorten(plan.lines.at(-1).replace(/…$/,'')+' …',width-2,value=>measure(value,titleSize));
   if(plan.lines.length){plan.level=2;plan.reason='number-and-title';}
   // Metadata is added only when it does not displace a title line.
   const diff=n.text.difficulty,numberWidth=measure(number,numberSize,600),diffWidth=measure(diff,metaSize),titleBottom=plan.titleY+plan.lines.length*titleLine;
   if(plan.level===2&&numberWidth+diffWidth+14<=width&&titleBottom+3+metaLine+padY<=h){
    plan.level=3;plan.reason='full-metadata';plan.difficulty=diff;plan.diffWidth=diffWidth+2;
    plan.tags=shorten(n.text.tags,width-2,value=>measure(value,metaSize));plan.tagsY=h-padY-metaLine;
   }
  }
 }
 if(cache.size>=8192)cache.clear();cache.set(key,plan);return plan;
}
function headingPlan(ctx,value,width,size){
 let cache=headingCaches.get(ctx);if(!cache){cache=new Map();headingCaches.set(ctx,cache);}
 const available=Math.floor(width),key=size+'|'+available+'|'+value;
 if(cache.has(key))return cache.get(key);
 ctx.font='600 '+size+'px Atlas';
 const lines=wrap(value,available,text=>ctx.measureText(text).width,size,600);
 const result=lines.length<=2&&lines.every(line=>ctx.measureText(line).width<=available)?lines:null;
 if(cache.size>4096)cache.clear();cache.set(key,result);return result;
}
function headingLayout(ctx,L,t,clip,obstacles,selected){
 const boxes=[],out=[],rejected=[],overlap=(a,b)=>a.x0<b.x1&&a.x1>b.x0&&a.y0<b.y1&&a.y1>b.y0;
 const regions=[...L.regions].filter(n=>n.depth>0).sort((a,b)=>a.depth-b.depth||a.key.localeCompare(b.key));
 for(const n of regions){
  const r={x0:n.rect.x*t.k+t.x,y0:n.y*t.k+t.y,x1:(n.rect.x+n.width)*t.k+t.x,y1:(n.y+n.height)*t.k+t.y};
  const v={x0:Math.max(r.x0,clip.x0),y0:Math.max(r.y0,clip.y0),x1:Math.min(r.x1,clip.x1),y1:Math.min(r.y1,clip.y1)};
  if(v.x1-v.x0<30||v.y1-v.y0<20)continue;
  const level=n.depth<=2?1:n.data.kind==='bank'?3:2,size=level===1?Math.round(clamp(14*t.k,13,16)):level===2?Math.round(clamp(14*t.k,12,14)):12;
  if(n.data.kind==='bank'&&n.header*t.k<size+9)continue;
  const shared=out.find(h=>h.name===n.presentationTitle&&h.region.x0<=r.x0&&h.region.x1>=r.x1&&h.region.y0<=r.y0&&h.region.y1>=r.y1);
  if(shared){
   const dx=Math.max(0,r.x0+5-shared.box.x0),dy=Math.max(0,r.y0+3-shared.box.y0),b={x0:shared.box.x0+dx,x1:shared.box.x1+dx,y0:shared.box.y0+dy,y1:shared.box.y1+dy};
   if(b.x1<=Math.min(r.x1,clip.x1)-2&&b.y1<=Math.min(r.y1,clip.y1)-2&&![...boxes.filter(box=>box!==shared.box),...obstacles].some(box=>overlap(b,box))){
    Object.assign(shared.box,b);shared.associations.push(n.key);if(L.byKey.get(selected)===n){shared.key=n.key;shared.selected=true;}continue;
   }
  }
  const x=v.x0+5,width=v.x1-v.x0-10,lines=headingPlan(ctx,n.presentationTitle,width-12,size);
  if(!lines){rejected.push({key:n.key,reason:'full-name-width'});continue;}
  ctx.font='600 '+size+'px Atlas';
  const lineHeight=size+3,height=lines.length*lineHeight+6;
  // When zoomed out, a heading badge can cover only its own unreadable cards.
  // At reading scales it stays in the natural header, unless sticky at a
  // clipped viewport edge. That badge reserves its area from Problem text.
  const sticky=r.y0<clip.y0,readingStack=v.y0<clip.y0+128&&out.some(h=>h.sticky);
  const headerBottom=t.k>=.68&&!sticky&&!readingStack?r.y0+(n.header+L.policy.padding)*t.k-2:Math.min(v.y1-4,v.y0+Math.max(height,128));
  let y=v.y0+3,box={x0:x,y0:y,x1:x+Math.min(width,Math.max(...lines.map(line=>ctx.measureText(line).width))+12),y1:y+height};
  // Stable hierarchy-first order; move down only inside the bounded own header.
  for(let attempts=0;attempts<8;attempts++){
   const blockers=[...boxes,...obstacles].filter(b=>overlap(box,b));if(!blockers.length)break;
   y=Math.max(...blockers.map(b=>b.y1))+3;box={...box,y0:y,y1:y+height};
  }
  if(box.y1>headerBottom||box.y1>v.y1-2||box.x1>v.x1-2||[...boxes,...obstacles].some(b=>overlap(box,b))){rejected.push({key:n.key,reason:'header-space-or-collision'});continue;}
  boxes.push(box);out.push({key:n.key,name:n.presentationTitle,associations:[n.key],level,size,lines,lineHeight,box,region:r,sticky,selected:L.byKey.get(selected)===n});
  if(out.length>=160)break;
 }
 return{headings:out,boxes,rejected};
}
const DIFFICULTY=Object.freeze({Easy:{tile:'#315f78',accent:'#75bddb'},Medium:{tile:'#766039',accent:'#dec078'},Hard:{tile:'#78494f',accent:'#d39293'},Unknown:{tile:'#414e60',accent:'#93a2b4'}});
function progressLayout(ctx,L,t,clip,headings,obstacles,coverage){
 const out=[],boxes=[],intersects=(a,b)=>a.x0<b.x1&&a.x1>b.x0&&a.y0<b.y1&&a.y1>b.y0;
 if(!coverage)return out;
 for(const h of [...headings.headings].sort((a,b)=>Number(b.selected)-Number(a.selected)||a.level-b.level)){
  const n=L.byKey.get(h.key),stats=coverage.get(h.key);if(!stats?.total||n.data.kind==='bank'||t.k<.3&&h.level>1&&!h.selected)continue;
  const value=stats.solved+' / '+stats.total.toLocaleString('en-US')+' solved',width=Math.max(68,Math.ceil(glyphMetric(ctx,value,11).width)+10),height=22;
  const r=h.region,x0=Math.max(r.x0,clip.x0)+4,x1=Math.min(r.x1,clip.x1)-3,y1=Math.min(r.y1,clip.y1)-3;
  const candidates=[{x0:h.box.x1+5,y0:h.box.y0,x1:h.box.x1+5+width,y1:h.box.y0+height},{x0:h.box.x0,y0:h.box.y1+3,x1:h.box.x0+width,y1:h.box.y1+3+height}];
  const headerBottom=t.k>=.68&&!h.sticky?r.y0+(n.header+L.policy.padding)*t.k-2:Math.min(y1,Math.max(r.y0,clip.y0)+128);
  const box=candidates.find(b=>b.x0>=x0&&b.x1<=x1&&b.y1<=y1&&b.y1<=headerBottom&&![...headings.boxes,...boxes,...obstacles].some(o=>intersects(b,o)));
  if(!box)continue;out.push({key:h.key,box,value,stats});boxes.push(box);if(out.length>=32)break;
 }
 return out;
}
function paint(ctx,L,t,W,H,colors,selected,related,visual,viewport){
 const clip={x0:Math.max(0,viewport?.x0||0),y0:Math.max(0,viewport?.y0||0),x1:Math.min(W,viewport?.x1??W),y1:Math.min(H,viewport?.y1??H)},obstacles=viewport?.obstacles||[],labels=[],suppressed=[],styles=[],categoryLabels=[],occupied=[],MAX_LABELS=1200;
 const intersects=(a,b)=>a.x0<b.x1&&a.x1>b.x0&&a.y0<b.y1&&a.y1>b.y0;
 const screen=n=>({x:n.rect.x*t.k+t.x,y:n.y*t.k+t.y,w:n.width*t.k,h:n.height*t.k}),on=r=>r.x+r.w>=0&&r.x<=W&&r.y+r.h>=0&&r.y<=H;
 const textRect=r=>{const x=Math.max(r.x,clip.x0+1),y=Math.max(r.y,clip.y0+1);return{x,y,w:Math.max(0,Math.min(r.x+r.w,clip.x1-1)-x),h:Math.max(0,Math.min(r.y+r.h,clip.y1-1)-y)};};
 const world={x0:(-t.x)/t.k,y0:(-t.y)/t.k,x1:(W-t.x)/t.k,y1:(H-t.y)/t.k},leaves=visible(L,world);
 // A readable Problem has priority over a heading badge covering its body.
 // Major overview names remain unaffected while cards are genuinely tiny.
 const protectedCards=[];
 for(const n of leaves){const r=screen(n),b=textRect(r);if(on(r)&&screenCardPlan(ctx,n,b.w,b.h,visual.solved.has(n.key)).level>=2)protectedCards.push({x0:r.x,y0:r.y,x1:r.x+r.w,y1:r.y+r.h});}
 const headings=headingLayout(ctx,L,t,clip,[...obstacles,...protectedCards],selected);
 const progressIndicators=progressLayout(ctx,L,t,clip,headings,[...obstacles,...protectedCards],visual.coverage);
 const headingBudget=progressIndicators.length+headings.headings.reduce((s,h)=>s+h.lines.length,0);
 function text(value,x,y,width,height,size,weight,key,kind,color=colors.text,collision=false){
  const budget=kind==='category'?MAX_LABELS:MAX_LABELS-headingBudget;
  if(size<9.5||labels.length>=budget){suppressed.push({key,kind,reason:size<9.5?'font-size':'budget'});return false;}ctx.textAlign='left';ctx.textBaseline='alphabetic';const m=glyphMetric(ctx,value,size,weight),base=y+m.actualBoundingBoxAscent+1,b={key,kind,text:value,size,x0:x-m.actualBoundingBoxLeft,y0:base-m.actualBoundingBoxAscent,x1:x+m.actualBoundingBoxRight,y1:base+m.actualBoundingBoxDescent};
  const reason=width<m.width+2?'width':height<m.actualBoundingBoxAscent+m.actualBoundingBoxDescent+2?'height':b.x0<clip.x0+1||b.x1>clip.x1-1||b.y0<clip.y0+1||b.y1>clip.y1-1?'viewport':obstacles.some(o=>intersects(o,b))?'ui-obstacle':kind!=='category'&&kind!=='progress'&&[...headings.boxes,...progressIndicators.map(h=>h.box)].some(o=>intersects(o,b))?'heading':collision&&occupied.some(o=>intersects(o,b))?'collision':null;
  if(reason){suppressed.push({key,kind,reason});return false;}
  ctx.fillStyle=color;ctx.fillText(value,x,base);labels.push(b);if(collision)occupied.push({...b,x0:b.x0-3,x1:b.x1+3,y0:b.y0-3,y1:b.y1+3});return true;
 }
 let painted=0;
 for(const n of L.regions){const r=screen(n);if(!on(r))continue;painted++;const active=n.key===selected||L.byKey.get(selected)===n,member=related.regions.has(n.key),filtered=visual.active&&visual.regions.has(n.key);
  ctx.fillStyle=n.depth===0?colors.root:colors.category;ctx.strokeStyle=filtered?'#e5b85b':active||member?colors.accent:colors.border;ctx.lineWidth=filtered||active?1.5:.6;ctx.fillRect(r.x,r.y,r.w,r.h);ctx.strokeRect(r.x,r.y,r.w,r.h);
 }
 const cardDetails=[];
 for(const n of leaves){const r=screen(n);if(!on(r))continue;painted++;const solved=visual.solved.has(n.key),filtered=visual.active&&visual.matches.has(n.key),dim=visual.active&&!filtered,member=related.problems.has(n.key),active=n.key===selected;
  const difficulty=DIFFICULTY[n.data.problem.difficulty]?n.data.problem.difficulty:'Unknown',palette=DIFFICULTY[difficulty],compact=r.w<160||r.h<76;
  const fill=solved?'#206647':compact?palette.tile:member?'#253344':colors.topic,border=solved?'#7fe7a2':active||member?colors.accent:colors.border;
  const alpha=solved?1:dim?.62:1;ctx.globalAlpha=alpha;ctx.fillStyle=fill;ctx.fillRect(r.x,r.y,r.w,r.h);ctx.strokeStyle=border;ctx.lineWidth=solved?Math.max(1.2,2*t.k):active?2:.5;ctx.strokeRect(r.x+.3,r.y+.3,Math.max(0,r.w-.6),Math.max(0,r.h-.6));
  if(!compact){ctx.fillStyle=palette.accent;ctx.fillRect(r.x+1,r.y+1,Math.min(4,r.w*.08),Math.max(0,r.h-2));}
  else if(solved){ctx.fillStyle=palette.accent;ctx.fillRect(r.x+r.w*.68,r.y+1,Math.max(0,r.w*.25),Math.max(0,Math.min(4,r.h*.3)));}
  if(filtered){ctx.strokeStyle='#efbf62';ctx.lineWidth=2.2;ctx.strokeRect(r.x-1,r.y-1,r.w+2,r.h+2);}
  if(solved&&!compact){ctx.fillStyle='#8bf1b2';ctx.fillRect(r.x+1,r.y+r.h-5,Math.max(0,r.w-2),3);}
  ctx.globalAlpha=1;styles.push({key:n.key,solved,filtered,dim,fill,border,filterBorder:filtered?'#efbf62':null,difficulty,accent:palette.accent,compact,alpha});
  const b=textRect(r),p=screenCardPlan(ctx,n,b.w,b.h,solved);if(!p.level)continue;
  const x=b.x+p.pad,width=p.usableWidth;
  const numberDrawn=text(p.number,x,b.y+p.numberY,width,p.numberSize+3,p.numberSize,600,n.key,'number',solved?'#8bf1b2':colors.text);
  let titlesDrawn=0;p.lines.forEach((value,i)=>{if(text(value,x,b.y+p.titleY+i*p.titleLine,width,p.titleLine,p.titleSize,400,n.key,'title'))titlesDrawn++;});
  if(p.level===3){const diffColor=palette.accent;
   text(p.difficulty,b.x+p.width-p.pad-p.diffWidth,b.y+p.numberY,p.diffWidth,p.metaSize+3,p.metaSize,400,n.key,'difficulty',diffColor);
   text(p.tags,x,b.y+p.tagsY,width,p.metaSize+3,p.metaSize,400,n.key,'tags',colors.muted);
  }
  cardDetails.push({key:n.key,level:p.level,screenWidth:r.w,screenHeight:r.h,labelWidth:b.w,labelHeight:b.h,titleFont:p.titleSize,numberFont:p.numberSize,lines:p.lines,truncated:p.truncated,numberDrawn,titlesDrawn,reason:p.reason});
 }
 // Headings use readable screen typography; their backgrounds and glyphs remain
 // inside their own projected region. No partial name or unrelated-card overlay.
 for(const h of headings.headings){const b=h.box;ctx.fillStyle=colors.root;ctx.globalAlpha=.96;ctx.fillRect(b.x0,b.y0,b.x1-b.x0,b.y1-b.y0);ctx.globalAlpha=1;
  let shown=0;h.lines.forEach((value,i)=>{if(text(value,b.x0+4,b.y0+3+i*h.lineHeight,b.x1-b.x0-8,h.lineHeight,h.size,600,h.key,'category',h.selected?colors.accent:colors.text))shown++;});
  if(shown===h.lines.length)categoryLabels.push(...h.associations);
 }
 // Coverage uses precomputed distinct primary IDs, never viewport counts.
 for(const h of progressIndicators){const b=h.box;ctx.fillStyle=colors.root;ctx.fillRect(b.x0,b.y0,b.x1-b.x0,b.y1-b.y0);
  text(h.value,b.x0+4,b.y0+1,b.x1-b.x0-8,14,11,400,h.key,'progress',h.stats.solved?'#8bf1b2':colors.muted);
  const x=b.x0+4,w=b.x1-b.x0-8,y=b.y1-4;ctx.fillStyle='#30414d';ctx.fillRect(x,y,w,3);ctx.fillStyle='#65d99b';ctx.fillRect(x,y,w*(h.stats.percent||0)/100,3);
 }
 // No unbounded relation graph. One selected Problem's secondary links only.
 ctx.save();ctx.strokeStyle='#9c9bbd';ctx.lineWidth=1;ctx.setLineDash([4,3]);let links=0;
 for(const e of related.links){const a=L.byKey.get(e.from),b=L.byKey.get(e.to);if(!a||!b)continue;ctx.beginPath();ctx.moveTo(a.x*t.k+t.x,(a.y+a.height/2)*t.k+t.y);ctx.lineTo((b.rect.x+8)*t.k+t.x,(b.y+12)*t.k+t.y);ctx.stroke();links++;}ctx.restore();
 return{painted,leaves:leaves.length,problemCards:leaves.map(n=>n.key),labels,labelBounds:labels,suppressedLabels:suppressed,categoryLabels,headingLayout:headings,progressIndicators,cardDetails,styles,links,labelLimit:MAX_LABELS};
}
const api={POLICY,build,wrap,shorten,cardPolicy,textPlan,pack,visible,hit,relations,screenCardPlan,DIFFICULTY,paint};g.LeetCodeOptimizedCPU=Object.freeze(api);if(typeof module!=='undefined')module.exports=api;
})(globalThis);
