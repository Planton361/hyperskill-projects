/* V6.5: measured, disjoint subtree regions; viewport-independent geometry. */
(function(g){
'use strict';
const VERSION='atlas-spatial-5',SCHEMA=5,FONT='14px system-ui';
const TYPE={ROOT:28,MAJOR:21,CATEGORY:17,TOPIC:14,META:10};
const LAYOUT=Object.freeze({rootMajorGap:88,majorDomainGap:82,categoryChildGap:76,categoryTrayGap:68,trayNextLevelGap:72,majorSiblingGap:112,categorySiblingGap:64,traySiblingGap:52,nodeSafeArea:16,traySafeArea:20,majorSafeArea:24,rootSafeArea:24,parentToBus:28,busToChild:30,trayWidth:220,trayMaxWidth:320,trayPadding:8,trayRowGap:4,trayColumnGap:52});
const SPACE={ROOT_MAJOR:LAYOUT.rootMajorGap,MAJOR_CATEGORY:LAYOUT.majorDomainGap,CATEGORY_CATEGORY:LAYOUT.categoryChildGap,CATEGORY_TRAY:LAYOUT.categoryTrayGap,SIBLING_MAJOR:LAYOUT.majorSiblingGap,SIBLING_CATEGORY:LAYOUT.categorySiblingGap,TRAY_INTERNAL_X:LAYOUT.trayColumnGap,TRAY_INTERNAL_Y:LAYOUT.trayRowGap,TRAY_PADDING:LAYOUT.trayPadding};
const categorySize=d=>d===0?TYPE.ROOT:d===1?TYPE.MAJOR:TYPE.CATEGORY;
const POLICY={minWidth:LAYOUT.trayWidth,preferredWidth:LAYOUT.trayWidth,maxWidth:LAYOUT.trayMaxWidth,padX:10,padY:6,gapX:SPACE.TRAY_INTERNAL_X,gapY:SPACE.TRAY_INTERNAL_Y,trayPadding:SPACE.TRAY_PADDING,topicFont:TYPE.TOPIC,topicLine:17,metaFont:TYPE.META};
function wrap(title,measure,max){const lines=[];let line='';for(const word of title.split(/\s+/)){if(line&&measure(line+' '+word)>max){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;}
function topicCard(t,measure){let width=POLICY.preferredWidth,lines=wrap(t.title,measure,width-44);while(lines.length>3&&width<POLICY.maxWidth){width=Math.min(POLICY.maxWidth,width+12);lines=wrap(t.title,measure,width-44);}width=Math.max(width,...lines.map(measure).map(w=>w+44));return{key:t.key,lines,width,height:Math.max(29,lines.length*POLICY.topicLine+12)};}
function pack(topics,measure,available=Infinity,forcedCols=null,weights={width:1,height:1}){
 const items=topics.map(t=>topicCard(t,measure));if(!items.length)return{width:0,height:0,columns:[],rows:0,items:[],gapX:POLICY.gapX,gapY:POLICY.gapY,padding:POLICY.trayPadding};
 const candidates=[];
 for(let cols=1;cols<=Math.min(4,items.length);cols++){
 const rows=Math.ceil(items.length/cols);if((cols-1)*rows>=items.length)continue;const widths=Array.from({length:cols},(_,c)=>Math.max(POLICY.minWidth,...items.slice(c*rows,(c+1)*rows).map(i=>i.width))),heights=Array.from({length:rows},(_,r)=>Math.max(...items.filter((_,i)=>i%rows===r).map(i=>i.height))),width=widths.reduce((a,b)=>a+b,0)+(cols-1)*POLICY.gapX+2*POLICY.trayPadding,height=Math.max(...Array.from({length:cols},(_,c)=>{const group=items.slice(c*rows,(c+1)*rows);return group.reduce((sum,i)=>sum+i.height,0)+(group.length-1)*POLICY.gapY;}))+2*POLICY.trayPadding,area=items.reduce((a,i)=>a+i.width*i.height,0),unused=(width*height-area)/(width*height),aspect=width/height;
 const error=items.length>=3?Math.max(0,Math.log(1.2/aspect),Math.log(aspect/2.5)):0;const score=weights.width*width+weights.height*height+120*error+20*unused+(width>available?40*Math.log(width/available):0);candidates.push({cols,rows,widths,heights,width,height,score,unused,aspectError:error});}
 const balanced=candidates.filter(c=>items.length<2||(c.width/c.height>=.8&&c.width/c.height<=4)),viable=balanced.length?balanced:candidates;const chosen=candidates.find(c=>c.cols===forcedCols)||viable.sort((a,b)=>a.score-b.score||a.cols-b.cols)[0],columns=[];let x=POLICY.trayPadding;
 for(let c=0;c<chosen.cols;c++){let y=POLICY.trayPadding;const entries=items.slice(c*chosen.rows,(c+1)*chosen.rows);for(let r=0;r<entries.length;r++){entries[r].x=x;entries[r].y=y;entries[r].width=chosen.widths[c];y+=entries[r].height+POLICY.gapY;}columns.push({x,width:chosen.widths[c],keys:entries.map(i=>i.key)});x+=chosen.widths[c]+POLICY.gapX;}
 return{...chosen,columns,items,gapX:POLICY.gapX,gapY:POLICY.gapY,padding:POLICY.trayPadding,candidates:viable.map(c=>({columns:c.cols,width:c.width,height:c.height,score:c.score,aspectError:c.aspectError}))};
}
function box(n,depth,measure){
 const font=categorySize(depth),text=t=>measure(t,font,depth===0?650:600),meta=measure('89 / 89 learned',10,400),min=depth===0?320:depth===1?300:190,max=depth===0?360:depth===1?340:240,candidates=[];
 for(let limit=min;limit<=max;limit+=8){const lines=wrap(n.title,text,limit-44);if(lines.length>3)continue;const width=Math.max(min,Math.ceil(Math.max(meta,...lines.map(text))+44)),line=font*1.18,height=lines.length*line+(depth>=2?25:30);const score=width*height+width*20+lines.length*100;candidates.push({width,height,font,line,labelLines:lines,metaFont:10,score});}
 return candidates.sort((a,b)=>a.score-b.score)[0]||{width:Math.ceil(text(n.title)+44),height:font*1.18+(depth>=2?25:30),font,line:font*1.18,labelLines:[n.title],metaFont:10};
}
function categoryChildren(n){const children=n.children.filter(c=>c.type==='category');if(n.title==='Java'){const order=['Basics','Code organization','Working with data','Errorless code'];children.sort((a,b)=>(order.indexOf(a.title)<0?order.length:order.indexOf(a.title))-(order.indexOf(b.title)<0?order.length:order.indexOf(b.title)));}return children;}
function levelGap(depth){return depth===0?SPACE.ROOT_MAJOR:depth===1?SPACE.MAJOR_CATEGORY:SPACE.CATEGORY_CATEGORY;}
function extent(rs){return{x0:Math.min(...rs.map(r=>r.x)),x1:Math.max(...rs.map(r=>r.x+r.w)),y0:Math.min(...rs.map(r=>r.y)),y1:Math.max(...rs.map(r=>r.y+r.h))};}
function translate(rs,x,y){return rs.map(r=>({...r,x:r.x+x,y:r.y+y}));}
// Bottom-up measurement never borrows a sibling region's empty space.
function buildOnce(m,measure,previous=null,config={}){
 if(previous&&(previous.layout_schema_version!==SCHEMA||previous.layout_algorithm_version!==VERSION))throw Error('V6.5 requires its explicit spatial checkpoint');
 const records={},plans=new Map(),bands=new Map(),events=[],cards=new Map(),depthHeights=new Map(),depthTrays=new Map();let trayPackingMilliseconds=0;
 function measureCards(n,depth){const card=box(n,depth,measure);cards.set(n.key,card);const started=performance.now(),band=pack(n.children.filter(c=>c.type==='topic'),measure,Infinity,1);trayPackingMilliseconds+=performance.now()-started;bands.set(n.key,band);depthTrays.set(depth,Math.max(depthTrays.get(depth)||0,band.height));depthHeights.set(depth,Math.max(depthHeights.get(depth)||0,card.height));n.children.filter(c=>c.type==='category').forEach(c=>measureCards(c,depth+1));}
 measureCards(m.root,0);for(const [key,card]of cards){const n=m.nodes.get(key);let depth=0,p=n;while(p.canonical_parent_id!=null){p=m.nodes.get('category:'+p.canonical_parent_id);if(!p)break;depth++;}card.height=depthHeights.get(depth);}
 function plan(n,depth){
  const cats=categoryChildren(n),topics=n.children.filter(c=>c.type==='topic'),old=previous?.categories[n.key],card=cards.get(n.key);
  cats.forEach(c=>plan(c,depth+1));
  const band=bands.get(n.key);
  const safe=depth===0?LAYOUT.rootSafeArea:depth===1?LAYOUT.majorSafeArea:LAYOUT.nodeSafeArea;
  const gap=depth===0?LAYOUT.majorSiblingGap:LAYOUT.categorySiblingGap;
  const preferredChildTop=card.height+((depthTrays.get(depth)||0)?LAYOUT.categoryTrayGap+depthTrays.get(depth)+LAYOUT.trayNextLevelGap:levelGap(depth));
  const childTop=old?.childTop||preferredChildTop;
  const packedWidth=cats.reduce((sum,c)=>sum+plans.get(c.key).width,0)+Math.max(0,cats.length-1)*gap;
  const children={};
  let cursor=old&&cats.length&&old.children[cats[0].key]?old.children[cats[0].key].x-previous.categories[cats[0].key].anchor:-packedWidth/2;
  const own=[{x:-card.width/2,y:0,w:card.width,h:card.height,key:n.key,kind:'category'}],rects=[...own];
  let left=-card.width/2-safe,right=card.width/2+safe,height=card.height+safe;
  for(const c of cats){
   const sub=plans.get(c.key),prior=old?.children[c.key];
   const x=prior?Math.max(prior.x,cursor-sub.left):cursor-sub.left;
   const y=Math.max(childTop,prior?.y||0);
   children[c.key]={x,y,width:sub.width,height:sub.height,overflow:false};
   rects.push(...sub.rects.map(r=>({...r,x:r.x+x,y:r.y+y})));
   left=Math.min(left,x+sub.left);right=Math.max(right,x+sub.right);height=Math.max(height,y+sub.height);cursor=x+sub.right+gap;
  }
  // Direct topics have their own lateral region, never beneath a category drop.
  const trayLeft=cats.length?Math.max(right+gap+LAYOUT.traySafeArea,old?.band.left||0):-band.width/2;
  const trayTop=card.height+LAYOUT.categoryTrayGap;
  if(band.height){rects.push({x:trayLeft,y:trayTop,w:band.width,h:band.height,key:n.key,kind:'topic-band'});left=Math.min(left,trayLeft-LAYOUT.traySafeArea);right=Math.max(right,trayLeft+band.width+LAYOUT.traySafeArea);height=Math.max(height,trayTop+band.height+LAYOUT.traySafeArea);}
  if(old){left=Math.min(left,-old.anchor);right=Math.max(right,old.width-old.anchor);height=Math.max(height,old.height);}
  const width=right-left;
  const record={anchor:-left,width,height,box:card,band:{left:trayLeft,top:trayTop,width:band.width,height:band.height,columns:band.columns.map(c=>c.width),rows:band.rows,gapX:POLICY.gapX,gapY:POLICY.gapY,padding:POLICY.trayPadding},childTop,children,sibling_order:cats.map(c=>c.key)};
  delete record.box.score;records[n.key]=record;plans.set(n.key,{rects,width,height,left,right});
 }
 plan(m.root,0);const nodes=[],byKey=new Map(),branches=[],buses=[],trays=[];
 function place(n,x,y,depth){
  const r=records[n.key],node={data:n,key:n.key,x,y,depth,lines:r.box.labelLines,font:r.box.font,line:r.box.line,width:r.box.width,height:r.box.height};nodes.push(node);byKey.set(n.key,node);
  const band=bands.get(n.key),bx=x+r.band.left,by=y+r.band.top;
  if(band.items.length){
   trays.push({parent:n.key,x:bx,y:by,width:band.width,height:band.height,topics:band.items.map(i=>i.key)});
   // A mixed parent uses the same trunk, with the category bus below its reserved tray.
   buses.push({parent:n.key,topics:band.items.map(i=>i.key),points:[{x,y:y+node.height},{x,y:y+node.height+LAYOUT.parentToBus},{x:bx+band.width/2,y:y+node.height+LAYOUT.parentToBus},{x:bx+band.width/2,y:by}]});
   for(const i of band.items){const t=n.children.find(t=>t.key===i.key),leaf={data:t,key:t.key,x:bx+i.x+i.width/2,y:by+i.y,depth:depth+1,lines:i.lines,font:TYPE.TOPIC,line:POLICY.topicLine,width:i.width,height:i.height,parent:n.key};nodes.push(leaf);byKey.set(t.key,leaf);}
  }
  for(const c of n.children.filter(c=>c.type==='category')){const slot=r.children[c.key];place(c,x+slot.x,y+slot.y,depth+1);branches.push({parent:n.key,child:c.key});}
 }
 place(m.root,0,0,0);
 const connectorSegments=!config.geometryOnly?g.AtlasRouting.hierarchy(branches,byKey,[],buses,trays,LAYOUT):[];
  buses.length=0; // Tray paths are unioned into the hierarchy, so shared trunks render once.
 for(const e of buses)e.d=e.points.map((p,i)=>(i?'L':'M')+p.x+','+p.y).join('');
 return{nodes,byKey,branches,connectorSegments,buses,trays,bands,events,plans,trayPackingMilliseconds,checkpoint:{layout_schema_version:SCHEMA,layout_algorithm_version:VERSION,categories:records}};
}
function visible(L,m,collapsed){return L.nodes.filter(n=>{let p=m.nodes.get('category:'+n.data.canonical_parent_id);while(p){if(collapsed.has(p.key))return false;p=m.nodes.get('category:'+p.canonical_parent_id);}return true;});}
function bounds(nodes,edges=[],padding=8){const xs=nodes.flatMap(n=>[n.x-n.width/2,n.x+n.width/2]),ys=nodes.flatMap(n=>[n.y,n.y+n.height]);for(const e of edges)for(const p of e.points||[]){xs.push(p.x);ys.push(p.y);}return{x0:Math.min(...xs)-padding,x1:Math.max(...xs)+padding,y0:Math.min(...ys)-padding,y1:Math.max(...ys)+padding};}
function contentBounds(L,nodes){const keys=new Set(nodes.map(n=>n.key)),edges=[...L.branches.filter(e=>keys.has(e.parent)&&keys.has(e.child)),...L.buses.filter(e=>keys.has(e.parent)&&e.topics.some(k=>keys.has(k)))];const frames=L.trays.filter(t=>keys.has(t.parent)&&t.topics.some(k=>keys.has(k))).map(t=>({points:[{x:t.x,y:t.y},{x:t.x+t.width,y:t.y+t.height}]}));return bounds(nodes,[...edges,...frames]);}
function optimize(m,measure){return buildOnce(m,measure);}
function build(m,measure,previous=null){return buildOnce(m,measure,previous);}
g.AtlasLayout={build,buildOnce,optimize,pack,wrap,visible,bounds,contentBounds,FONT,categorySize,POLICY,SPACE,TYPE,LAYOUT};
})(globalThis);
