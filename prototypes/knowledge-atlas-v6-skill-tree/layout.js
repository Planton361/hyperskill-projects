/* Derived from V6.6: measured cards/trays and disjoint depth bands.
   Local geometry is built from the visible personal scope, with no historical checkpoint. */
(function(g){
'use strict';
const VERSION='atlas-v66-personal-1',SCHEMA=1,FONT='14px system-ui';
const TYPE={ROOT:28,MAJOR:21,CATEGORY:17,TOPIC:14,META:10};
const LAYOUT=Object.freeze({rootMajorGap:88,majorDomainGap:82,categoryChildGap:76,categoryTrayGap:68,trayNextLevelGap:72,majorSiblingGap:12,categorySiblingGap:12,traySiblingGap:52,nodeSafeArea:8,traySafeArea:8,majorSafeArea:24,rootSafeArea:12,parentToBus:18,busToChild:30,trayWidth:156,trayMaxWidth:320,trayPadding:8,trayRowGap:4,trayColumnGap:52});
const SPACE={ROOT_MAJOR:LAYOUT.rootMajorGap,MAJOR_CATEGORY:LAYOUT.majorDomainGap,CATEGORY_CATEGORY:LAYOUT.categoryChildGap,CATEGORY_TRAY:LAYOUT.categoryTrayGap,SIBLING_MAJOR:LAYOUT.majorSiblingGap,SIBLING_CATEGORY:LAYOUT.categorySiblingGap,TRAY_INTERNAL_X:LAYOUT.trayColumnGap,TRAY_INTERNAL_Y:LAYOUT.trayRowGap,TRAY_PADDING:LAYOUT.trayPadding};
const categorySize=d=>d===0?TYPE.ROOT:d===1?TYPE.MAJOR:TYPE.CATEGORY;
const POLICY={minWidth:LAYOUT.trayWidth,preferredWidth:LAYOUT.trayWidth,maxWidth:LAYOUT.trayMaxWidth,padX:10,padY:6,gapX:SPACE.TRAY_INTERNAL_X,gapY:SPACE.TRAY_INTERNAL_Y,trayPadding:SPACE.TRAY_PADDING,topicFont:TYPE.TOPIC,topicLine:17,metaFont:TYPE.META};
function wrap(title,measure,max){const lines=[];let line='';for(const word of title.split(/\s+/)){if(line&&measure(line+' '+word)>max){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;}
function topicCard(t,measure){let width=t.type==='reference'?Math.max(112,Math.ceil(measure(t.displayTitle)+44)):POLICY.preferredWidth,lines=wrap(t.displayTitle,measure,width-44);width=Math.max(width,...lines.map(line=>measure(line)).map(w=>w+44));return{key:t.key,lines,width,height:Math.max(29,lines.length*POLICY.topicLine+12)};}
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
function measuredBox(n,depth,measure){
 const font=categorySize(depth),text=t=>measure(t,font,depth===0?650:600),meta=measure('89 / 89 learned',10,400),min=depth===0?260:depth===1?230:144,max=depth===0?300:depth===1?280:180,candidates=[];
 for(let limit=min;limit<=max;limit+=8){const lines=wrap(n.displayTitle||n.title,text,limit-44);if(lines.length>3)continue;const width=Math.max(min,Math.ceil(Math.max(meta,...lines.map(text))+44)),line=font*1.18,height=lines.length*line+(depth>=2?25:30);const score=width*height+width*20+lines.length*100;candidates.push({width,height,font,line,labelLines:lines,metaFont:10,score});}
 return candidates.sort((a,b)=>a.score-b.score)[0]||{width:Math.ceil(text(n.displayTitle||n.title)+44),height:font*1.18+(depth>=2?25:30),font,line:font*1.18,labelLines:[n.displayTitle||n.title],metaFont:10};
}
// Local scene uses ordinary V6.6 card sizes at every depth.
const DEPTH_SCALE=[];
function box(n,depth,measure){const b=measuredBox(n,depth,measure),scale=DEPTH_SCALE[depth]||1;return {...b,width:b.width*scale,height:b.height*scale,font:b.font*scale,line:b.line*scale,metaFont:b.metaFont*scale,scale};}
function categoryChildren(n){return n.children.filter(c=>c.type==='category');}
function levelGap(depth){return depth===0?SPACE.ROOT_MAJOR:depth===1?SPACE.MAJOR_CATEGORY:SPACE.CATEGORY_CATEGORY;}
function extent(rs){return{x0:Math.min(...rs.map(r=>r.x)),x1:Math.max(...rs.map(r=>r.x+r.w)),y0:Math.min(...rs.map(r=>r.y)),y1:Math.max(...rs.map(r=>r.y+r.h))};}
function translate(rs,x,y){return rs.map(r=>({...r,x:r.x+x,y:r.y+y}));}
// Bottom-up complete rectangular envelopes. The parent sits at the center of
// the packed child region; every ancestor consumes the resulting real envelope.
function buildOnce(m,measure,previous=null,config={}){
 if(previous)throw Error('Global geometry does not accept historical checkpoints');
 const records={},plans=new Map(),bands=new Map(),cards=new Map(),depthHeights=new Map(),depthTrays=new Map(),depthY=[0],verticalBands=[];
 let trayPackingMilliseconds=0;
 function measureCards(n,depth){
  const card=box(n,depth,measure);cards.set(n.key,card);
  const started=performance.now();
  // Local rows wrap completely at a compact width; no truncation or hidden rows.
  const band=pack(n.children.filter(AtlasModel.isLeaf),measure,Infinity,1);
  trayPackingMilliseconds+=performance.now()-started;bands.set(n.key,band);
  depthTrays.set(depth,Math.max(depthTrays.get(depth)||0,band.height));
  depthHeights.set(depth,Math.max(depthHeights.get(depth)||0,card.height));
  categoryChildren(n).forEach(c=>measureCards(c,depth+1));
 }
 measureCards(m.root,0);
 // Compact local bands reserve only visible measured content.
 for(let d=0;d<depthHeights.size;d++){
  const cardHeight=depthHeights.get(d),trayHeight=depthTrays.get(d)||0,trayGap=30;
  const nextClearance=24;
  const ownedRequirement=trayHeight?trayGap+trayHeight:18;
  verticalBands.push({depth:d,y:depthY[d],cardHeight,trayHeight,trayGap,nextClearance,ownedRequirement});
  depthY[d+1]=depthY[d]+cardHeight+ownedRequirement+nextClearance;
 }
 function plan(n,depth){
  const cats=categoryChildren(n),card=cards.get(n.key),band=bands.get(n.key),safe=depth<=1?LAYOUT.rootSafeArea:LAYOUT.nodeSafeArea;
  card.height=depthHeights.get(depth);cats.forEach(c=>plan(c,depth+1));
  const gap=depth===0?LAYOUT.majorSiblingGap:LAYOUT.categorySiblingGap;
  const items=cats.map(c=>({key:c.key,width:plans.get(c.key).width}));

  const regionWidth=items.reduce((sum,item)=>sum+item.width,0)+Math.max(0,items.length-1)*gap;
  let cursor=-regionWidth/2,trayLeft=-band.width/2;
  const children={},childTop=depthY[depth+1]-depthY[depth],trayTop=card.height+verticalBands[depth].trayGap;
  const rects=[{x:-card.width/2,y:0,w:card.width,h:card.height,key:n.key,kind:'category'}];
  let height=card.height+safe;
  // Own tray occupies its measured vertical band, not a phantom sibling column.
  if(band.items.length){
   rects.push({x:trayLeft,y:trayTop,w:band.width,h:band.height,key:n.key,kind:'topic-band'});
   height=Math.max(height,trayTop+band.height+LAYOUT.traySafeArea);
  }
  for(const item of items){
   const sub=plans.get(item.key),x=cursor-sub.left;
   children[item.key]={x,y:childTop,width:sub.width,height:sub.height,overflow:false};
   rects.push(...translate(sub.rects,x,childTop));height=Math.max(height,childTop+sub.height);
   cursor+=item.width+gap;
  }
  // The real root card itself supplies its minimum readable region width.
  // No reservation is proportional to Computer science or nonexistent slots.
  const half=Math.max(card.width/2+safe,regionWidth/2,band.items.length?band.width/2+(cats.length?20:4):0),left=-half,right=half,width=2*half;
  records[n.key]={anchor:half,width,height,box:card,band:{left:trayLeft,top:trayTop,width:band.width,height:band.height,columns:band.columns.map(c=>c.width),rows:band.rows},childTop,children,sibling_order:cats.map(c=>c.key),childRegion:{left:-regionWidth/2,right:regionWidth/2}};
  plans.set(n.key,{rects,width,height,left,right,childRegionWidth:regionWidth});
 }
 plan(m.root,0);
 const nodes=[],byKey=new Map(),branches=[],trays=[];
 function place(n,x,y,depth){
  const r=records[n.key],node={data:n,key:n.key,x,y,depth,lines:r.box.labelLines,font:r.box.font,line:r.box.line,cardScale:r.box.scale||1,width:r.box.width,height:r.box.height};
  nodes.push(node);byKey.set(n.key,node);
  const band=bands.get(n.key),bx=x+r.band.left,by=y+r.band.top;
  if(band.items.length){
   trays.push({parent:n.key,x:bx,y:by,width:band.width,height:band.height,topics:band.items.map(i=>i.key)});
   for(const i of band.items){const data=m.nodes.get(i.key),leaf={data,key:i.key,x:bx+i.x+i.width/2,y:by+i.y,depth:depth+1,lines:i.lines,font:TYPE.TOPIC,line:POLICY.topicLine,width:i.width,height:i.height,parent:n.key};nodes.push(leaf);byKey.set(i.key,leaf);}
  }
  for(const c of categoryChildren(n)){const slot=r.children[c.key];place(c,x+slot.x,depthY[depth+1],depth+1);branches.push({parent:n.key,child:c.key});}
 }
 place(m.root,0,0,0);
 // Existing router already unions one short-stem local rail per parent.
 // Compact centered child ports are its inputs; no global rail is allocated.
 const connectorSegments=config.geometryOnly?[]:g.AtlasRouting.hierarchy(branches,byKey,[],[],trays,LAYOUT);
 return{nodes,byKey,branches,connectorSegments,buses:[],trays,bands,events:[],plans,trayPackingMilliseconds,depthY,verticalBands,checkpoint:{layout_schema_version:SCHEMA,layout_algorithm_version:VERSION,categories:records}};
}
function visible(L){return L.nodes;}
function bounds(nodes,edges=[],padding=8){const xs=nodes.flatMap(n=>[n.x-n.width/2,n.x+n.width/2]),ys=nodes.flatMap(n=>[n.y,n.y+n.height]);for(const e of edges)for(const p of e.points||[]){xs.push(p.x);ys.push(p.y);}return{x0:Math.min(...xs)-padding,x1:Math.max(...xs)+padding,y0:Math.min(...ys)-padding,y1:Math.max(...ys)+padding};}
function contentBounds(L,nodes){const keys=new Set(nodes.map(n=>n.key)),edges=[...L.branches.filter(e=>keys.has(e.parent)&&keys.has(e.child)),...L.buses.filter(e=>keys.has(e.parent)&&e.topics.some(k=>keys.has(k)))];const frames=L.trays.filter(t=>keys.has(t.parent)&&t.topics.some(k=>keys.has(k))).map(t=>({points:[{x:t.x,y:t.y},{x:t.x+t.width,y:t.y+t.height}]}));return bounds(nodes,[...edges,...frames]);}
function optimize(m,measure){return buildOnce(m,measure);}
function build(m,measure,previous=null){return buildOnce(m,measure,previous);}
g.AtlasLayout={build,buildOnce,optimize,pack,wrap,visible,bounds,contentBounds,FONT,categorySize,POLICY,SPACE,TYPE,LAYOUT};
})(globalThis);
