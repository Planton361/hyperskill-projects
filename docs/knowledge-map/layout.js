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

/* Presentation mutations only. Model facts are always read from AtlasModel. */
(function(g){
'use strict';
const SCHEMA=2,ALGORITHM='atlas-incremental-2',clone=x=>JSON.parse(JSON.stringify(x));
function serialize(L){return {nodes:L.nodes.map(({data,...n})=>n),trays:L.trays,branches:L.branches,
 connectorSegments:L.connectorSegments,buses:[],bounds:AtlasLayout.contentBounds(L,L.nodes)};}
function hydrate(m,geometry,checkpoint){
 const nodes=geometry.nodes.map(n=>({...n,data:m.nodes.get(n.key)})),byKey=new Map(nodes.map(n=>[n.key,n]));
 return {...geometry,nodes,byKey,checkpoint,bands:new Map(),plans:new Map(),events:[],trayPackingMilliseconds:0};
}
function bootstrap(m,measure,legacy,generation=0){
 const L=AtlasLayout.build(m,measure,legacy),geometry=serialize(L),categories={};
 for(const [key,r] of Object.entries(L.checkpoint.categories)){
  const n=L.byKey.get(key);
  categories[key]={slot_anchor:{x:n.x,y:n.y},visible_extent:{left:-r.anchor,top:0,width:r.width,height:r.height},
   allocated_width:r.width,allocated_height:r.height,reserved_capacity:{width:0,height:0},
   sibling_order:r.sibling_order,topic_order:m.nodes.get(key).children.filter(n=>n.type==='topic').map(n=>n.key)};
 }
 const checkpoint={layout_schema_version:SCHEMA,layout_algorithm_version:ALGORITHM,presentation_generation:generation,categories};
 refresh(m,geometry,checkpoint,false);
 return {geometry,checkpoint,events:[],repacked_trays:[]};
}
function categoryCard(n,depth,measure){
 const font=AtlasLayout.categorySize(depth),text=t=>measure(t,font,depth===0?650:600),min=depth===0?320:depth===1?300:190,max=depth===0?360:depth===1?340:240,candidates=[];
 for(let limit=min;limit<=max;limit+=8){const lines=AtlasLayout.wrap(n.title,text,limit-44);if(lines.length>3)continue;const width=Math.max(min,Math.ceil(Math.max(measure('89 / 89 learned',10,400),...lines.map(text))+44)),line=font*1.18,height=lines.length*line+(depth>=2?25:30);candidates.push({width,height,font,line,lines,score:width*height+width*20+lines.length*100});}
 const r=candidates.sort((a,b)=>a.score-b.score)[0];if(!r)throw Error('Category label requires explicit layout migration: '+n.key);delete r.score;return r;
}
function refresh(m,geometry,cp,expand=true){
 const byKey=new Map(geometry.nodes.map(n=>[n.key,n])),trays=new Map(geometry.trays.map(t=>[t.parent,t]));
 function visit(n){
  const r=cp.categories[n.key],a=byKey.get(n.key);let left=-a.width/2-16,right=a.width/2+16,bottom=a.height+16;
  for(const c of n.children.filter(c=>c.type==='category')){visit(c);const child=cp.categories[c.key],b=byKey.get(c.key),e=child.visible_extent;left=Math.min(left,b.x-a.x+e.left);right=Math.max(right,b.x-a.x+e.left+e.width);bottom=Math.max(bottom,b.y-a.y+e.height);}
  const t=trays.get(n.key);if(t){left=Math.min(left,t.x-a.x-20);right=Math.max(right,t.x-a.x+t.width+20);bottom=Math.max(bottom,t.y-a.y+t.height+20);}
  // Retain allocated left boundary so append growth never recenters an old region.
  left=Math.min(left,r.visible_extent.left);
  const width=right-left,height=bottom;
  if(expand){r.allocated_width=Math.max(r.allocated_width,width);r.allocated_height=Math.max(r.allocated_height,height);}
  r.visible_extent={left,top:0,width,height};r.slot_anchor={x:a.x,y:a.y};
  r.reserved_capacity={width:Math.max(0,r.allocated_width-width),height:Math.max(0,r.allocated_height-height)};
 }
 visit(m.root);
}
function update(m,measure,previous,geometry,diff,rebalance=false,budget={max:Infinity,significant:100,major:Infinity}){
 const generation=previous.presentation_generation;
 if(rebalance)return bootstrap(m,measure,null,generation+1);
 const cp=clone(previous),out=clone(geometry),byKey=new Map(out.nodes.map(n=>[n.key,n])),trays=new Map(out.trays.map(t=>[t.parent,t])),events=[],repacks=new Set();
 const live=new Set(m.nodes.keys());out.nodes=out.nodes.filter(n=>live.has(n.key));out.trays=out.trays.filter(t=>live.has(t.parent));
 for(const key of diff.label_changes||[]){
  const n=m.nodes.get(key),a=byKey.get(key);if(!n||!a)continue;
  if(n.type==='category'){
   Object.assign(a,categoryCard(n,a.depth,measure));
   const t=trays.get(key);if(t&&t.y<a.y+a.height+68){const dy=a.y+a.height+68-t.y;t.y+=dy;for(const k of t.topics)byKey.get(k).y+=dy;repacks.add(key);}
  }else{
   const t=trays.get(a.parent),card=AtlasLayout.pack([n],measure,Infinity,1).items[0],dy=card.height-a.height;
   a.lines=card.lines;a.width=card.width;a.height=card.height;
   for(const k of t.topics)if(byKey.get(k).y>a.y)byKey.get(k).y+=dy;
   t.height+=dy;t.width=Math.max(t.width,card.width+16);repacks.add(t.parent);
  }
 }
 for(const k of Object.keys(cp.categories))if(!live.has(k))delete cp.categories[k];
 for(const n of m.nodes.values())if(n.type==='category'&&cp.categories[n.key]){
  const r=cp.categories[n.key];r.sibling_order=r.sibling_order.filter(k=>live.has(k));r.topic_order=r.topic_order.filter(k=>live.has(k));
  r.sibling_order.push(...n.children.filter(c=>c.type==='category'&&!r.sibling_order.includes(c.key)).sort((a,b)=>a.id-b.id).map(c=>c.key));
  r.topic_order.push(...n.children.filter(c=>c.type==='topic'&&!r.topic_order.includes(c.key)).sort((a,b)=>a.id-b.id).map(c=>c.key));
 }
 function shift(n,dx,dy){
  const a=byKey.get(n.key);a.x+=dx;a.y+=dy;
  if(n.type==='category'){
   cp.categories[n.key].slot_anchor={x:a.x,y:a.y};const t=trays.get(n.key);if(t){t.x+=dx;t.y+=dy;}
   for(const c of n.children)if(byKey.has(c.key))shift(c,dx,dy);
  }
 }
 function insert(n,depth,x,y){
  const card=categoryCard(n,depth,measure),a={key:n.key,x,y,depth,...card};byKey.set(n.key,a);out.nodes.push(a);
  cp.categories[n.key]={slot_anchor:{x,y},visible_extent:{left:-card.width/2-16,top:0,width:card.width+32,height:card.height+16},
   allocated_width:card.width+32,allocated_height:card.height+16,reserved_capacity:{width:0,height:0},
   sibling_order:n.children.filter(c=>c.type==='category').sort((a,b)=>a.id-b.id).map(c=>c.key),topic_order:[],slot_row:0};
 }
 function visit(n,depth){
  const r=cp.categories[n.key],a=byKey.get(n.key),gap=depth===0?112:64;
  let cursor=null,wrappedBottom=a.y+r.allocated_height+82;
  for(const key of r.sibling_order){
   const c=m.nodes.get(key);
   if(!cp.categories[key]){
    const card=categoryCard(c,depth+1,measure),right=r.visible_extent.left+r.allocated_width;
    const wrap=cursor!==null&&cursor+card.width+32>right;
    const prior=r.sibling_order.slice(0,r.sibling_order.indexOf(key)).filter(k=>byKey.has(k));
    const x=wrap?(byKey.get(prior.at(-1))?.x||a.x):cursor===null?a.x:a.x+cursor+card.width/2+16;
    insert(c,depth+1,x,wrap?wrappedBottom:a.y+a.height+82);cp.categories[key].slot_row=wrap?1:0;
    events.push({level:2,region:n.key,action:wrap?'append wrapped local category slot':'append category slot',category:key});
   }
   visit(c,depth+1);
   const cr=cp.categories[key],b=byKey.get(key),left=b.x-a.x+cr.visible_extent.left;
   const minimumY=a.y+a.height+76;if(b.y<minimumY)shift(c,0,minimumY-b.y);
   if(cr.slot_row){wrappedBottom=Math.max(wrappedBottom,b.y+cr.allocated_height+82);}
   else{
    if(cursor!==null&&left<cursor-.001){const dx=cursor-left;shift(c,dx,0);events.push({level:3,region:n.key,action:'shift immediate sibling subtree',category:key,displacement:dx});}
    cursor=byKey.get(key).x-a.x+cr.visible_extent.left+cr.allocated_width+gap;
   }
  }
  const wanted=n.children.filter(c=>c.type==='topic').map(c=>c.key),old=trays.get(n.key);
  const added=wanted.filter(k=>!byKey.has(k)).sort((a,b)=>m.nodes.get(a).id-m.nodes.get(b).id);
  const removed=(old?.topics||[]).filter(k=>!live.has(k));
  if(added.length||removed.length){
   repacks.add(n.key);let t=old;
   if(!t){t={parent:n.key,x:r.sibling_order.length?a.x+cursor:a.x-118,y:a.y+a.height+68,width:236,height:16,topics:[]};trays.set(n.key,t);out.trays.push(t);}
   t.topics=t.topics.filter(k=>live.has(k));r.topic_order=r.topic_order.filter(k=>live.has(k));
   const pack=AtlasLayout.pack(added.map(k=>m.nodes.get(k)),measure,Infinity,1);
   let bottom=Math.max(t.y+8,...t.topics.map(k=>byKey.get(k).y+byKey.get(k).height+4));
   for(const item of pack.items){const c=m.nodes.get(item.key),leaf={key:c.key,x:t.x+8+item.width/2,y:bottom,depth:depth+1,lines:item.lines,font:14,line:17,width:item.width,height:item.height,parent:n.key};byKey.set(c.key,leaf);out.nodes.push(leaf);bottom+=item.height+4;t.topics.push(c.key);if(!r.topic_order.includes(c.key))r.topic_order.push(c.key);}
   if(t.topics.length){t.width=Math.max(t.width,pack.width);t.height=Math.max(t.height,bottom-t.y+4);}else{trays.delete(n.key);out.trays=out.trays.filter(t=>t.parent!==n.key);}
   events.push({level:1,region:n.key,action:'local tray append/remove',added,removed});
  }
  const t=trays.get(n.key);
  if(t&&cursor!==null&&t.x<a.x+cursor+20){const dx=a.x+cursor+20-t.x;t.x+=dx;for(const key of t.topics)byKey.get(key).x+=dx;repacks.add(n.key);events.push({level:2,region:n.key,action:'expand lateral tray slot',displacement:dx});}
  const priorWidth=r.allocated_width,priorHeight=r.allocated_height;
  // Refresh only this region; children have already settled bottom-up.
  let left=r.visible_extent.left,right=a.width/2+16,bottom=a.height+16;
  for(const k of r.sibling_order){const b=byKey.get(k),cr=cp.categories[k];left=Math.min(left,b.x-a.x+cr.visible_extent.left);right=Math.max(right,b.x-a.x+cr.visible_extent.left+cr.allocated_width);bottom=Math.max(bottom,b.y-a.y+cr.allocated_height);}
  if(t){left=Math.min(left,t.x-a.x-20);right=Math.max(right,t.x-a.x+t.width+20);bottom=Math.max(bottom,t.y-a.y+t.height+20);}
  r.visible_extent={left,top:0,width:right-left,height:bottom};r.allocated_width=Math.max(r.allocated_width,right-left);r.allocated_height=Math.max(r.allocated_height,bottom);
  r.reserved_capacity={width:r.allocated_width-(right-left),height:r.allocated_height-bottom};
  if(r.allocated_width>priorWidth)events.push({level:depth===0?5:4,region:n.key,action:'expand parent capacity',required_width:r.allocated_width,available_width:priorWidth});
  if(r.allocated_height>priorHeight)events.push({level:depth===0?5:4,region:n.key,action:'expand vertical capacity',required_height:r.allocated_height,available_height:priorHeight});
 }
 visit(m.root,0);
 out.trays=out.trays.filter(t=>trays.has(t.parent));
 out.branches=[];for(const n of m.nodes.values())if(n.type==='category'&&n.canonical_parent_id!==null)out.branches.push({parent:'category:'+n.canonical_parent_id,child:n.key});
 out.connectorSegments=AtlasRouting.hierarchy(out.branches,byKey,[],[],out.trays,AtlasLayout.LAYOUT);out.buses=[];
 out.bounds=AtlasLayout.contentBounds({...out,byKey},out.nodes);
 const moves=geometry.nodes.filter(n=>n.key.startsWith('category:')&&byKey.has(n.key)).map(n=>({key:n.key,depth:n.depth,d:Math.hypot(n.x-byKey.get(n.key).x,n.y-byKey.get(n.key).y)}));
 const affected=moves.filter(n=>n.d>.001),max=Math.max(0,...affected.map(n=>n.d)),significant=100*affected.filter(n=>n.d>1).length/moves.length;
 if(max>budget.max||significant>budget.significant||affected.some(n=>n.depth===1&&n.d>budget.major)){
  const event=[...events].reverse().find(e=>e.required_width)||{region:m.root.key,required_width:cp.categories[m.root.key].allocated_width,available_width:previous.categories[m.root.key].allocated_width};
  return {status:'REBALANCE_REQUIRED',affected_region:event.region,required_width:event.required_width,available_width:event.available_width,
   affected_categories:affected.map(n=>n.key).sort(),estimated_displacement:max,significant_percentage:significant,events};
 }
 const changed=JSON.stringify(cp.categories)!==JSON.stringify(previous.categories);cp.presentation_generation=generation+(changed?1:0);
 out.nodes.sort((a,b)=>a.key.localeCompare(b.key));out.trays.sort((a,b)=>a.parent.localeCompare(b.parent));
 return {geometry:out,checkpoint:cp,events,repacked_trays:[...repacks].sort()};
}
g.AtlasIncremental={bootstrap,update,hydrate,serialize};
})(globalThis);

AtlasLayout.build=(m,measure,cp)=>AtlasIncremental.hydrate(m,AtlasBuildGeometry,cp);
