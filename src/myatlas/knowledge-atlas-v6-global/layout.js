/* Derived from V6.6: measured cards/trays and local contour packing.
   Global geometry is built from the current catalog, with no historical checkpoint. */
(function(g){
'use strict';
const VERSION='atlas-v66-global-5-full-titles',SCHEMA=2,FONT='14px system-ui';
const TYPE={ROOT:28,MAJOR:21,CATEGORY:17,TOPIC:14,META:10};
const LAYOUT=Object.freeze({rootMajorGap:88,majorDomainGap:82,categoryChildGap:76,categoryTrayGap:68,trayNextLevelGap:72,majorSiblingGap:112,categorySiblingGap:24,traySiblingGap:52,nodeSafeArea:12,traySafeArea:12,majorSafeArea:24,rootSafeArea:24,parentToBus:28,busToChild:30,trayWidth:220,trayMaxWidth:320,trayPadding:8,trayRowGap:4,trayColumnGap:24});
const SPACE={ROOT_MAJOR:LAYOUT.rootMajorGap,MAJOR_CATEGORY:LAYOUT.majorDomainGap,CATEGORY_CATEGORY:LAYOUT.categoryChildGap,CATEGORY_TRAY:LAYOUT.categoryTrayGap,SIBLING_MAJOR:LAYOUT.majorSiblingGap,SIBLING_CATEGORY:LAYOUT.categorySiblingGap,TRAY_INTERNAL_X:LAYOUT.trayColumnGap,TRAY_INTERNAL_Y:LAYOUT.trayRowGap,TRAY_PADDING:LAYOUT.trayPadding};
const categorySize=d=>d===0?TYPE.ROOT:d===1?TYPE.MAJOR:TYPE.CATEGORY;
const POLICY={minWidth:LAYOUT.trayWidth,preferredWidth:LAYOUT.trayWidth,maxWidth:LAYOUT.trayMaxWidth,padX:10,padY:6,gapX:SPACE.TRAY_INTERNAL_X,gapY:SPACE.TRAY_INTERNAL_Y,trayPadding:SPACE.TRAY_PADDING,topicFont:TYPE.TOPIC,topicLine:17,metaFont:TYPE.META};
function wrap(title,measure,max){const lines=[];let line='';for(const word of title.split(/\s+/)){if(line&&measure(line+' '+word)>max){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;}
function topicCard(t,measure){let width=POLICY.preferredWidth,lines=wrap(t.displayTitle,measure,width-44);while(lines.length>3&&width<POLICY.maxWidth){width=Math.min(POLICY.maxWidth,width+12);lines=wrap(t.displayTitle,measure,width-44);}width=Math.max(width,...lines.map(line=>measure(line)).map(w=>w+44));return{key:t.key,lines,width,height:Math.max(29,lines.length*POLICY.topicLine+12)};}
function pack(topics,measure,available=Infinity,forcedCols=null,weights={width:1,height:1}){
 const items=topics.map(t=>topicCard(t,measure));if(!items.length)return{width:0,height:0,columns:[],rows:0,items:[],gapX:POLICY.gapX,gapY:POLICY.gapY,padding:POLICY.trayPadding};
 const candidates=[];
 for(let cols=1;cols<=Math.min(4,items.length);cols++){
 const rows=Math.ceil(items.length/cols);if((cols-1)*rows>=items.length)continue;const widths=Array.from({length:cols},(_,c)=>Math.max(...items.slice(c*rows,(c+1)*rows).map(i=>i.width))),heights=Array.from({length:rows},(_,r)=>Math.max(...items.filter((_,i)=>i%rows===r).map(i=>i.height))),width=widths.reduce((a,b)=>a+b,0)+(cols-1)*POLICY.gapX+2*POLICY.trayPadding,height=Math.max(...Array.from({length:cols},(_,c)=>{const group=items.slice(c*rows,(c+1)*rows);return group.reduce((sum,i)=>sum+i.height,0)+(group.length-1)*POLICY.gapY;}))+2*POLICY.trayPadding,area=items.reduce((a,i)=>a+i.width*i.height,0),unused=(width*height-area)/(width*height),aspect=width/height;
 const error=items.length>=3?Math.max(0,Math.log(1.2/aspect),Math.log(aspect/2.5)):0;const score=weights.width*width+weights.height*height+120*error+20*unused+(width>available?40*Math.log(width/available):0);candidates.push({cols,rows,widths,heights,width,height,score,unused,aspectError:error});}
 const balanced=candidates.filter(c=>items.length<2||(c.width/c.height>=.8&&c.width/c.height<=4)),viable=balanced.length?balanced:candidates;const chosen=candidates.find(c=>c.cols===forcedCols)||viable.sort((a,b)=>a.score-b.score||a.cols-b.cols)[0],columns=[];let x=POLICY.trayPadding;
 for(let c=0;c<chosen.cols;c++){let y=POLICY.trayPadding;const entries=items.slice(c*chosen.rows,(c+1)*chosen.rows);for(let r=0;r<entries.length;r++){entries[r].x=x;entries[r].y=y;entries[r].width=chosen.widths[c];y+=entries[r].height+POLICY.gapY;}columns.push({x,width:chosen.widths[c],keys:entries.map(i=>i.key)});x+=chosen.widths[c]+POLICY.gapX;}
 return{...chosen,columns,items,gapX:POLICY.gapX,gapY:POLICY.gapY,padding:POLICY.trayPadding,candidates:viable.map(c=>({columns:c.cols,width:c.width,height:c.height,score:c.score,aspectError:c.aspectError}))};
}
function measuredBox(n,depth,measure,m){
 const font=categorySize(depth),text=t=>measure(t,font,depth===0?650:600),meta=measure(n.leafKeys.length+' slots · '+n.leafKeys.filter(k=>m.nodes.get(k).is_learned).length+' learned',10,400),min=depth===0?180:depth===1?160:140,max=depth===0?360:depth===1?300:240,candidates=[];
 for(let limit=min;limit<=max;limit+=8){const lines=wrap(n.displayTitle||n.title,text,limit-44);if(lines.length>3)continue;const width=Math.max(min,Math.ceil(Math.max(meta,...lines.map(text))+44)),line=font*1.18,height=lines.length*line+(depth>=2?25:30);const score=width*height+width*20+lines.length*100;candidates.push({width,height,font,line,labelLines:lines,metaFont:10,score});}
 return candidates.sort((a,b)=>a.score-b.score)[0]||{width:Math.ceil(text(n.displayTitle||n.title)+44),height:font*1.18+(depth>=2?25:30),font,line:font*1.18,labelLines:[n.displayTitle||n.title],metaFont:10};
}
// Text measurement is the only source of card size. Subtree space is separate.
function categoryChildren(n){return n.children.filter(c=>c.type==='category');}
function translate(rs,x,y){return rs.map(r=>({...r,x:r.x+x,y:r.y+y}));}
const PACKING=Object.freeze({siblingGap:24,rootGap:64,childGap:LAYOUT.parentToBus+LAYOUT.busToChild,trayGap:LAYOUT.parentToBus+LAYOUT.busToChild,rowGap:64,corridor:12,spineGap:24,extremeWidth:6000,rowWidth:3600,maxTrayColumns:4});
// Piecewise contours include cards, complete trays and reserved routing corridors.
// Unlike rectangular envelopes they allow a short branch to occupy a tall
// neighbour's unused space while maintaining left-to-right order at every Y.
function contour(rects){
 const events=[];for(const r of rects){events.push({y:r.y,r,start:true},{y:r.y+r.h,r,start:false});}
 events.sort((a,b)=>a.y-b.y);const active=new Set(),out=[];let i=0;
 while(i<events.length){const y=events[i].y;while(i<events.length&&events[i].y===y){const e=events[i++];if(e.start)active.add(e.r);else active.delete(e.r);}const next=events[i]?.y;if(next>y&&active.size){let left=Infinity,right=-Infinity;for(const r of active){left=Math.min(left,r.x);right=Math.max(right,r.x+r.w);}const prev=out.at(-1);if(prev&&prev.y1===y&&prev.left===left&&prev.right===right)prev.y1=next;else out.push({y0:y,y1:next,left,right});}}
 return out;
}
function separation(a,b,gap){let i=0,j=0,dx=0;while(i<a.length&&j<b.length){const p=a[i],q=b[j];if(p.y0<q.y1&&q.y0<p.y1)dx=Math.max(dx,p.right+gap-q.left);if(p.y1<=q.y1)i++;else j++;}return dx;}
function buildOnce(m,measure,previous=null,config={}){
 if(previous)throw Error('Global geometry does not accept historical checkpoints');
 const records={},plans=new Map(),bands=new Map(),cards=new Map();let trayPackingMilliseconds=0;
 function measureCards(n,depth){
  cards.set(n.key,{...measuredBox(n,depth,measure,m),scale:1});
  const started=performance.now(),topics=n.children.filter(AtlasModel.isLeaf);
  // Short trays retain a single reading column; larger ones compare at most
  // four column-major alternatives using the existing V6.6 measurement/pack.
  const choices=Array.from({length:topics.length>=8?Math.min(PACKING.maxTrayColumns,topics.length):1},(_,i)=>pack(topics,measure,Infinity,i+1));
  const band=choices.sort((a,b)=>(a.width+1.35*a.height)-(b.width+1.35*b.height)||a.width-b.width)[0];
  trayPackingMilliseconds+=performance.now()-started;bands.set(n.key,band);
  categoryChildren(n).forEach(c=>measureCards(c,depth+1));
 }
 measureCards(m.root,0);
 function rowPack(items,gap){
  let rects=[],positions={},last=-Infinity;
  for(const item of items){const x=rects.length?Math.max(last+gap,separation(contour(rects),item.contour,gap)):0;positions[item.key]=x;rects.push(...translate(item.rects,x,0));last=x;}
  const left=Math.min(...rects.map(r=>r.x)),right=Math.max(...rects.map(r=>r.x+r.w)),shift=-(left+right)/2;
  rects=translate(rects,shift,0);for(const k in positions)positions[k]+=shift;
  return{items,rects,positions,width:right-left,height:Math.max(...rects.map(r=>r.y+r.h))};
 }
 function plan(n,depth){
  const cats=categoryChildren(n),card=cards.get(n.key),band=bands.get(n.key);cats.forEach(c=>plan(c,depth+1));
  const items=cats.map(c=>({key:c.key,...plans.get(c.key)}));
  if(band.items.length){const rects=[{x:-band.width/2,y:0,w:band.width,h:band.height,key:n.key,kind:'topic-band'}];items.push({key:'tray',rects,contour:contour(rects),width:band.width,height:band.height});}
  const gap=depth===0?PACKING.rootGap:PACKING.siblingGap,rows=[];
  if(items.length){const whole=rowPack(items,gap);
   // Never wrap the five roots. Only contiguous complete sibling subtrees
   // may form modules, and only after measured contour/tray packing is broad.
   if(depth>0&&cats.length>=3&&whole.width>PACKING.extremeWidth&&whole.width>whole.height*2.4){
    const options=[[whole]];
    for(const count of [2,3,4]){
     const target=Math.max(PACKING.rowWidth,whole.width/count),candidate=[];let pending=[];
     for(const item of items){const next=rowPack([...pending,item],gap);if(pending.length&&next.width>target){candidate.push(rowPack(pending,gap));pending=[];}pending.push(item);}if(pending.length)candidate.push(rowPack(pending,gap));options.push(candidate);
    }
    const cost=rs=>Math.max(...rs.map(r=>r.width))+1.8*(rs.reduce((sum,r)=>sum+r.height,0)+(rs.length-1)*PACKING.rowGap);
    options.sort((a,b)=>cost(a)-cost(b)||a.length-b.length);rows.push(...options[0]);
   }else rows.push(whole);
  }
  const children={},rects=[{x:-card.width/2,y:0,w:card.width,h:card.height,key:n.key,kind:'category'}];
  let trayLeft=-band.width/2,trayTop=card.height+PACKING.trayGap,y=card.height+PACKING.childGap;
  for(const [rowIndex,row] of rows.entries()){
   row.y=y;row.busY=y-LAYOUT.busToChild;
   rects.push(...translate(row.rects,0,y));
   for(const item of row.items){const x=row.positions[item.key];if(item.key==='tray'){trayLeft=x-band.width/2;trayTop=y;}else children[item.key]={x,y,width:item.width,height:item.height,row:rowIndex,overflow:rows.length>1};}
   y+=row.height+PACKING.rowGap;
  }
  const spine=rows.length>1?Math.min(...rects.map(r=>r.x))-PACKING.spineGap:null;
  const routes={spine,rows:rows.map(r=>({y:r.y,busY:r.busY,keys:r.items.map(i=>i.key),ports:r.items.map(i=>r.positions[i.key])}))};
  const addCorridor=(x0,y0,x1,y1)=>{const p=PACKING.corridor/2;rects.push({x:Math.min(x0,x1)-p,y:Math.min(y0,y1),w:Math.abs(x1-x0)+2*p,h:Math.max(1,Math.abs(y1-y0)),key:n.key,kind:'routing'});};
  if(rows.length){addCorridor(0,card.height,0,rows[0].busY);if(spine!==null)addCorridor(spine,rows[0].busY,spine,rows.at(-1).busY);
   for(const row of rows){const ports=row.items.map(i=>row.positions[i.key]),xs=[...ports,spine??0,...(row===rows[0]?[0]:[])];addCorridor(Math.min(...xs),row.busY,Math.max(...xs),row.busY);for(const x of ports)addCorridor(x,row.busY,x,row.y);}
  }
  const left=Math.min(...rects.map(r=>r.x)),right=Math.max(...rects.map(r=>r.x+r.w)),height=Math.max(...rects.map(r=>r.y+r.h)),width=right-left;
  records[n.key]={anchor:-left,width,height,box:card,cardBounds:{x0:-card.width/2,y0:0,x1:card.width/2,y1:card.height},subtreeBounds:{x0:left,y0:0,x1:right,y1:height},band:{left:trayLeft,top:trayTop,width:band.width,height:band.height,columns:band.columns.map(c=>c.width),rows:band.rows},children,sibling_order:cats.map(c=>c.key),routes};
  plans.set(n.key,{rects,contour:contour(rects),width,height,left,right,rows:routes.rows});
 }
 plan(m.root,0);
 const nodes=[],byKey=new Map(),branches=[],trays=[],routingGroups=new Map();
 function place(n,x,y,depth){
  const r=records[n.key],node={data:n,key:n.key,x,y,depth,lines:r.box.labelLines,font:r.box.font,line:r.box.line,cardScale:1,width:r.box.width,height:r.box.height};
  node.cardBounds={x0:x-node.width/2,y0:y,x1:x+node.width/2,y1:y+node.height};node.subtreeBounds={x0:x+r.subtreeBounds.x0,y0:y,x1:x+r.subtreeBounds.x1,y1:y+r.subtreeBounds.y1};
  nodes.push(node);byKey.set(n.key,node);
  routingGroups.set(n.key,{spine:r.routes.spine===null?null:x+r.routes.spine,rows:r.routes.rows.map(row=>({...row,y:y+row.y,busY:y+row.busY,ports:row.ports.map(p=>x+p)}))});
  const band=bands.get(n.key),bx=x+r.band.left,by=y+r.band.top;
  if(band.items.length){trays.push({parent:n.key,x:bx,y:by,width:band.width,height:band.height,topics:band.items.map(i=>i.key)});for(const i of band.items){const data=m.nodes.get(i.key),leaf={data,key:i.key,x:bx+i.x+i.width/2,y:by+i.y,depth:depth+1,lines:i.lines,font:TYPE.TOPIC,line:POLICY.topicLine,width:i.width,height:i.height,parent:n.key};nodes.push(leaf);byKey.set(i.key,leaf);}}
  for(const c of categoryChildren(n)){const slot=r.children[c.key];place(c,x+slot.x,y+slot.y,depth+1);branches.push({parent:n.key,child:c.key});}
 }
 place(m.root,0,0,0);
 const connectorSegments=config.geometryOnly?[]:g.AtlasRouting.hierarchy(branches,byKey,[],[],trays,LAYOUT,routingGroups);
 return{nodes,byKey,branches,connectorSegments,buses:[],trays,bands,events:[],plans,routingGroups,trayPackingMilliseconds,checkpoint:{layout_schema_version:SCHEMA,layout_algorithm_version:VERSION,categories:records}};
}
function visible(L){return L.nodes;}
function bounds(nodes,edges=[],padding=8){const xs=nodes.flatMap(n=>[n.x-n.width/2,n.x+n.width/2]),ys=nodes.flatMap(n=>[n.y,n.y+n.height]);for(const e of edges)for(const p of e.points||[]){xs.push(p.x);ys.push(p.y);}return{x0:Math.min(...xs)-padding,x1:Math.max(...xs)+padding,y0:Math.min(...ys)-padding,y1:Math.max(...ys)+padding};}
function contentBounds(L,nodes){const keys=new Set(nodes.map(n=>n.key)),edges=[...L.branches.filter(e=>keys.has(e.parent)&&keys.has(e.child)),...L.buses.filter(e=>keys.has(e.parent)&&e.topics.some(k=>keys.has(k)))];const frames=L.trays.filter(t=>keys.has(t.parent)&&t.topics.some(k=>keys.has(k))).map(t=>({points:[{x:t.x,y:t.y},{x:t.x+t.width,y:t.y+t.height}]}));return bounds(nodes,[...edges,...frames]);}
function optimize(m,measure){return buildOnce(m,measure);}
function build(m,measure,previous=null){return buildOnce(m,measure,previous);}
g.AtlasLayout={build,buildOnce,optimize,pack,wrap,visible,bounds,contentBounds,FONT,categorySize,POLICY,SPACE,TYPE,LAYOUT,PACKING};
})(globalThis);
