/* V6.2: measured variable-size contours and bounded global grid feedback. */
(function(g){
'use strict';
const VERSION='atlas-compact-2',SCHEMA=4,FONT='14px system-ui',GAP=10,LEVEL_GAP=12;
const categorySize=d=>d===0?28:d===1?21:17;
const POLICY={minWidth:180,preferredWidth:180,maxWidth:276,padX:12,padY:8,gapX:10,gapY:6,topicFont:14,topicLine:17,metaFont:10};
function wrap(title,measure,max){const lines=[];let line='';for(const word of title.split(/\s+/)){if(line&&measure(line+' '+word)>max){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;}
function topicCard(t,measure){let width=POLICY.preferredWidth,lines=wrap(t.title,measure,width-54);while(lines.length>3&&width<POLICY.maxWidth){width=Math.min(POLICY.maxWidth,width+12);lines=wrap(t.title,measure,width-54);}width=Math.max(width,...lines.map(measure).map(w=>w+54));return{key:t.key,lines,width,height:Math.max(36,lines.length*POLICY.topicLine+16)};}
function pack(topics,measure,available=Infinity,forcedCols=null,weights={width:1,height:1}){
 const items=topics.map(t=>topicCard(t,measure));if(!items.length)return{width:0,height:0,columns:[],rows:0,items:[],gapX:10,gapY:6};
 const candidates=[];
 for(let cols=1;cols<=Math.min(5,items.length);cols++){
 const rows=Math.ceil(items.length/cols);if((cols-1)*rows>=items.length)continue;const widths=Array.from({length:cols},(_,c)=>Math.max(POLICY.minWidth,...items.slice(c*rows,(c+1)*rows).map(i=>i.width))),heights=Array.from({length:rows},(_,r)=>Math.max(...items.filter((_,i)=>i%rows===r).map(i=>i.height))),width=widths.reduce((a,b)=>a+b,0)+(cols-1)*10,height=Math.max(...Array.from({length:cols},(_,c)=>{const group=items.slice(c*rows,(c+1)*rows);return group.reduce((sum,i)=>sum+i.height,0)+(group.length-1)*6;})),area=items.reduce((a,i)=>a+i.width*i.height,0),unused=(width*height-area)/(width*height),aspect=width/height;
 const score=weights.width*width+weights.height*height+30*Math.abs(Math.log(aspect/1.5))+20*unused+(width>available?40*Math.log(width/available):0);candidates.push({cols,rows,widths,heights,width,height,score,unused});}
 const chosen=candidates.find(c=>c.cols===forcedCols)||candidates.sort((a,b)=>a.score-b.score||a.cols-b.cols)[0],columns=[];let x=0;
 for(let c=0;c<chosen.cols;c++){let y=0;const entries=items.slice(c*chosen.rows,(c+1)*chosen.rows);for(let r=0;r<entries.length;r++){entries[r].x=x;entries[r].y=y;entries[r].width=chosen.widths[c];y+=entries[r].height+6;}columns.push({x,width:chosen.widths[c],keys:entries.map(i=>i.key)});x+=chosen.widths[c]+10;}
 return{...chosen,columns,items,gapX:10,gapY:6,candidates:candidates.map(c=>({columns:c.cols,width:c.width,height:c.height,score:c.score}))};
}
function box(n,depth,measure){
 const font=categorySize(depth),text=t=>measure(t,font,depth===0?650:600),meta=measure('89 / 89 learned',10,400),min=depth===0?260:depth===1?190:Math.ceil(meta+44),max=depth===0?320:depth===1?240:220,candidates=[];
 for(let limit=min;limit<=max;limit+=8){const lines=wrap(n.title,text,limit-44);if(lines.length>3)continue;const width=Math.max(min,Math.ceil(Math.max(meta,...lines.map(text))+44)),line=font*1.18,height=lines.length*line+(depth>=2?25:30);const score=width*height+width*20+lines.length*100;candidates.push({width,height,font,line,labelLines:lines,metaFont:10,score});}
 return candidates.sort((a,b)=>a.score-b.score)[0]||{width:Math.ceil(text(n.title)+44),height:font*1.18+(depth>=2?25:30),font,line:font*1.18,labelLines:[n.title],metaFont:10};
}
function levelGap(depth){return depth===0?24:depth===1?18:8;}
function extent(rs){return{x0:Math.min(...rs.map(r=>r.x)),x1:Math.max(...rs.map(r=>r.x+r.w)),y0:Math.min(...rs.map(r=>r.y)),y1:Math.max(...rs.map(r=>r.y+r.h))};}
function translate(rs,x,y){return rs.map(r=>({...r,x:r.x+x,y:r.y+y}));}
function separation(placed,rects){let shift=-Infinity;for(const a of placed)for(const b of rects)if(a.y<b.y+b.h+8&&a.y+a.h+8>b.y)shift=Math.max(shift,a.x+a.w+GAP-b.x);return shift;}
// Place complete category subtree contours in bounded shelves. Every child stays below its parent.
function intersects(a,b,gap=8){return a.x<b.x+b.w+gap-.001&&a.x+a.w+gap-.001>b.x&&a.y<b.y+b.h+gap-.001&&a.y+a.h+gap-.001>b.y;}
function collides(a,b){return a.some(r=>b.some(s=>intersects(r,s)));}
// Sweep actual rectangle contours: a subtree's empty interior is usable by its sibling.
function compactChildren(cats,plans,config={},key){
 if(!cats.length)return{};
 const cacheKey=config.cache?JSON.stringify([key,cats.map(c=>plans.get(c.key).rects),config.contourAspect,config.contourPenalty,config.regions?.[key]]):null;if(config.cache?.has(cacheKey))return config.cache.get(cacheKey);
 const gap=8,widths=cats.map(c=>plans.get(c.key).width),minimum=Math.max(...widths),sum=widths.reduce((a,b)=>a+b,0)+GAP*(cats.length-1),options=[minimum,minimum*1.15,minimum*1.3,minimum*1.5,minimum*1.8,minimum*2+GAP,...widths.flatMap((a,i)=>widths.slice(i+1).map(b=>a+b+GAP)),sum].filter((v,i,all)=>v<=sum+.1&&all.indexOf(v)===i);let best;const alternatives=[];
 for(const limit of options){const placed=[],slots={};let usedRight=0,usedBottom=0;
 for(const c of cats){const sub=plans.get(c.key),b=extent(sub.rects),norm=translate(sub.rects,-b.x0,0),ys=new Set([0,usedBottom+gap]);
 for(const a of placed)for(const r of norm){const after=a.y+a.h+gap-r.y,before=a.y-r.y-r.h-gap;if(after>=0)ys.add(after);if(before>=0)ys.add(before);}
 let chosen;
 for(const y of [...ys].sort((a,b)=>a-b)){
 const forbidden=[];for(const a of placed)for(const r of norm)if(a.y<r.y+y+r.h+gap&&a.y+a.h+gap>r.y+y)forbidden.push([a.x-r.x-r.w-gap,a.x+a.w-r.x+gap]);
 forbidden.sort((a,b)=>a[0]-b[0]);let x=0;for(const [lo,hi]of forbidden){if(lo<x+1e-7&&hi>x)x=hi;}
 if(x+sub.width>limit+.01)continue;
 const right=Math.max(usedRight,x+sub.width),bottom=Math.max(usedBottom,y+sub.height),score=right*bottom+bottom*minimum*.35+y*minimum*.08;
 if(!chosen||score<chosen.score)chosen={x,y,score,right,bottom};
 }
 if(!chosen){const y=usedBottom+GAP;chosen={x:0,y,right:Math.max(usedRight,sub.width),bottom:y+sub.height};}
 slots[c.key]={x:chosen.x-b.x0,y:chosen.y,width:sub.width,height:sub.height,overflow:false};placed.push(...translate(norm,chosen.x,chosen.y));usedRight=chosen.right;usedBottom=chosen.bottom;
 }
 const aspect=usedRight/usedBottom,score=usedRight*usedBottom*(1+(config.contourPenalty??.23)*Math.abs(Math.log(aspect/(config.contourAspect??1.5))));const candidate={slots,score,width:usedRight,height:usedBottom};alternatives.push(candidate);if(!best||score<best.score)best=candidate;
 }
 best=alternatives[config.regions?.[key]]||best;const index=alternatives.indexOf(best),center=best.width/2;for(const slot of Object.values(best.slots))slot.x-=center;const result={slots:best.slots,alternatives:alternatives.map(a=>({width:a.width,height:a.height})),index};config.cache?.set(cacheKey,result);return result;
}
function buildOnce(m,measure,previous=null,config={}){
 if(previous&&(previous.layout_schema_version!==SCHEMA||previous.layout_algorithm_version!==VERSION))throw Error('V6.2 requires its explicit schema-4 compact checkpoint; old presentation checkpoints are archived, never silently loaded');
 const records={},plans=new Map(),bands=new Map(),events=[];
 function plan(n,depth){const cats=n.children.filter(c=>c.type==='category'),topics=n.children.filter(c=>c.type==='topic'),old=previous?.categories[n.key],card=box(n,depth,measure);cats.forEach(c=>plan(c,depth+1));const band=pack(topics,measure,old?.band.width||Infinity,old?.band.columns.length||config.columns?.[n.key],config.weights);bands.set(n.key,band);const childTop=Math.max(old?.childTop||0,card.height+levelGap(depth)+(band.height?band.height+28:0)),children={},placed=[];
 const packing=!old&&depth>0&&cats.length?compactChildren(cats,plans,config,n.key):null,packed=packing?.slots;let first=true;
 for(const c of cats){const sub=plans.get(c.key),prior=old?.children[c.key];let y=prior?Math.max(prior.y,childTop):childTop,x=prior?.x??packed?.[c.key].x??0,overflow=prior?.overflow||false;
 if(packed)y=childTop+packed[c.key].y;
 if(old&&!prior){y=Math.max(childTop,old.height+54);x=0;overflow=true;events.push({kind:'local-new-branch',key:c.key,parent:n.key});}
 if(old&&depth>0){let rs=translate(sub.rects,x,y);if(collides(placed,rs)){const candidates=[...new Set(placed.flatMap(a=>sub.rects.map(b=>a.y+a.h+GAP-b.y)))].filter(v=>v>=y).sort((a,b)=>a-b);const free=candidates.find(v=>!collides(placed,translate(sub.rects,x,v)));y=free??Math.max(...placed.map(r=>r.y+r.h))+GAP;events.push({kind:'local-vertical-growth',key:c.key,parent:n.key});}}
 else if(!packed&&!first&&!prior){const needed=separation(placed,translate(sub.rects,0,y));if(Number.isFinite(needed))x=needed;}
 children[c.key]={x,y,width:sub.width,height:sub.height,overflow};placed.push(...translate(sub.rects,x,y));first=false;
 }
 if(!old&&depth===0&&cats.length){const center=(children[cats[0].key].x+children[cats.at(-1).key].x)/2;for(const slot of Object.values(children))slot.x-=center;for(const r of placed)r.x-=center;}

 const own=[{x:-card.width/2,y:0,w:card.width,h:card.height,key:n.key,kind:'category'}];if(band.items.length)own.push({x:-band.width/2-8,y:card.height+LEVEL_GAP-10,w:band.width+16,h:band.height+10,key:n.key,kind:'topic-band'});
 const rects=[...own,...placed],b=extent(rects),width=b.x1-b.x0,height=b.y1,record={anchor:0,width,height,box:card,band:{left:-band.width/2,top:card.height+LEVEL_GAP,width:band.width,height:band.height,columns:band.columns.map(c=>c.width),rows:band.rows,gapX:10,gapY:6},childTop,children,sibling_order:cats.map(c=>c.key)};
 delete record.box.score;records[n.key]=record;plans.set(n.key,{rects,width,height,packing});
 }
 plan(m.root,0);const nodes=[],byKey=new Map(),branches=[],buses=[];
 function place(n,x,y,depth){const r=records[n.key],node={data:n,key:n.key,x,y,depth,lines:r.box.labelLines,font:r.box.font,line:r.box.line,width:r.box.width,height:r.box.height};nodes.push(node);byKey.set(n.key,node);const band=bands.get(n.key),bx=x+r.band.left,by=y+r.band.top;
 if(band.items.length){const busY=by-7,spines=band.columns.map(c=>bx+c.x-6);buses.push({parent:n.key,topics:band.items.map(i=>i.key),points:[{x,y:y+node.height},{x,y:busY},{x:Math.min(...spines),y:busY},{x:Math.max(...spines),y:busY}]});
 for(const c of band.columns){const spine=bx+c.x-6,entries=band.items.filter(i=>c.keys.includes(i.key)),last=entries.at(-1);buses.push({parent:n.key,topics:c.keys,points:[{x:spine,y:busY},{x:spine,y:by+last.y+last.height/2}]});}
 for(const i of band.items){const t=n.children.find(t=>t.key===i.key),leaf={data:t,key:t.key,x:bx+i.x+i.width/2,y:by+i.y,depth:depth+1,lines:i.lines,font:14,line:17,width:i.width,height:i.height,parent:n.key};nodes.push(leaf);byKey.set(t.key,leaf);buses.push({parent:n.key,topic:t.key,topics:[t.key],points:[{x:leaf.x-leaf.width/2-6,y:leaf.y+leaf.height/2},{x:leaf.x-leaf.width/2,y:leaf.y+leaf.height/2}]});}}
 for(const c of n.children.filter(c=>c.type==='category')){const slot=r.children[c.key];place(c,x+slot.x,y+slot.y,depth+1);branches.push({parent:n.key,child:c.key});}
 }
 place(m.root,0,0,0);
 const obstacles=nodes.map(n=>({x:n.x-n.width/2,y:n.y,w:n.width,h:n.height,key:n.key,kind:'card'}));
 if(!config.geometryOnly)for(const e of branches){const a=byKey.get(e.parent),b=byKey.get(e.child),route=g.AtlasRouting.boxRoute(a,b,obstacles);e.d=route.d;e.points=route.points;}
 for(const e of buses)e.d=e.points.map((p,i)=>(i?'L':'M')+p.x+','+p.y).join('');
 return{nodes,byKey,branches,buses,bands,events,plans,checkpoint:{layout_schema_version:SCHEMA,layout_algorithm_version:VERSION,categories:records}};
}
function visible(L,m,collapsed){return L.nodes.filter(n=>{let p=m.nodes.get('category:'+n.data.canonical_parent_id);while(p){if(collapsed.has(p.key))return false;p=m.nodes.get('category:'+p.canonical_parent_id);}return true;});}
function bounds(nodes,edges=[],padding=8){const xs=nodes.flatMap(n=>[n.x-n.width/2,n.x+n.width/2]),ys=nodes.flatMap(n=>[n.y,n.y+n.height]);for(const e of edges)for(const p of e.points||[]){xs.push(p.x);ys.push(p.y);}return{x0:Math.min(...xs)-padding,x1:Math.max(...xs)+padding,y0:Math.min(...ys)-padding,y1:Math.max(...ys)+padding};}
function contentBounds(L,nodes){const keys=new Set(nodes.map(n=>n.key)),edges=[...L.branches.filter(e=>keys.has(e.parent)&&keys.has(e.child)),...L.buses.filter(e=>keys.has(e.parent)&&e.topics.some(k=>keys.has(k)))];return bounds(nodes,edges);}
// Offline/checkpoint creation feedback. Runtime with a checkpoint uses only stable local packing.
function optimize(m,measure){
 const started=performance.now(),budget={width:1640,height:861},cache=new Map(),visited=new Set(),history=[];
 const metric=L=>{const b=bounds(L.nodes),width=b.x1-b.x0,height=b.y1-b.y0,wx=width/budget.width,hy=height/budget.height;return{width,height,scale:1/Math.max(wx,hy),bottleneck:wx>hy?'width':'height',whitespace:1-L.nodes.reduce((sum,n)=>sum+n.width*n.height,0)/(width*height)};};
 const signature=c=>JSON.stringify([c.contourAspect,Object.entries(c.columns||{}).sort(),Object.entries(c.regions||{}).sort()]);
 const initial=buildOnce(m,measure,null,{geometryOnly:true}),initialMetric=metric(initial),weights={width:1,height:Math.round(budget.width/budget.height*(initialMetric.bottleneck==='height'?1.05:.95)*10)/10};
 let beam=[.8,1.2,1.5,1.8].map(contourAspect=>{const config={weights,contourAspect,contourPenalty:.23,columns:{},regions:{},geometryOnly:true,cache},L=buildOnce(m,measure,null,config);visited.add(signature(config));return{config,L,metric:metric(L)};});
 const sort=(a,b)=>b.metric.scale-a.metric.scale||a.metric.whitespace-b.metric.whitespace;beam.sort(sort);let best=beam[0];
 for(let pass=0;pass<18;pass++){
 const pool=[];
 for(const row of beam){const choices=[];
 for(const [key,v]of row.L.bands)if(v.items.length>1){const configs=[...v.candidates].sort((a,b)=>row.metric.bottleneck==='height'?a.height-b.height:a.width-b.width);for(const c of configs)if(c.columns!==v.columns.length)choices.push({kind:'columns',key,value:c.columns});}
 for(const [key,v]of row.L.plans)if(v.packing)for(let i=0;i<v.packing.alternatives.length;i++)if(i!==v.packing.index)choices.push({kind:'regions',key,value:i});
 for(const c of choices){const config={...row.config,[c.kind]:{...row.config[c.kind],[c.key]:c.value}},hash=signature(config);if(visited.has(hash))continue;visited.add(hash);const L=buildOnce(m,measure,null,config);pool.push({config,L,metric:metric(L)});}
 }
 if(!pool.length)break;pool.sort(sort);beam=[.8,1.2,1.5,1.8].map(aspect=>pool.find(row=>row.config.contourAspect===aspect)).filter(Boolean);beam.sort(sort);if(sort(beam[0],best)<0)best=beam[0];history.push({pass,...best.metric});if(best.metric.scale*14>=10.2)break;
 }
 const finalists=[best,...beam].sort(sort).slice(0,4).map(row=>{const L=buildOnce(m,measure,null,{...row.config,geometryOnly:false}),b=contentBounds(L,L.nodes);return{L,scale:Math.min(budget.width/(b.x1-b.x0),budget.height/(b.y1-b.y0))};}).sort((a,b)=>b.scale-a.scale);
 const result=finalists[0].L;result.optimization={initial:initialMetric,weights,budget,history,evaluations:visited.size,milliseconds:performance.now()-started,finalScale:finalists[0].scale};return result;
}
function build(m,measure,previous=null){return previous?buildOnce(m,measure,previous):optimize(m,measure);}
g.AtlasLayout={build,buildOnce,optimize,pack,wrap,visible,bounds,contentBounds,FONT,categorySize,POLICY};
})(globalThis);
