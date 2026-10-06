/* V6.1: variable-sized box tidy tree, compact vertical contours and packed topic grids. */
(function(g){
'use strict';
const VERSION='atlas-boxed-1',SCHEMA=3,FONT='14px system-ui',GAP=18,LEVEL_GAP=26;
const categorySize=d=>d===0?28:d===1?21:17;
const POLICY={minWidth:180,preferredWidth:204,maxWidth:276,padX:12,padY:8,gapX:12,gapY:8,topicFont:14,topicLine:17,metaFont:10};
function wrap(title,measure,max){const lines=[];let line='';for(const word of title.split(/\s+/)){if(line&&measure(line+' '+word)>max){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;}
function topicCard(t,measure){let width=POLICY.preferredWidth,lines=wrap(t.title,measure,width-54);while(lines.length>3&&width<POLICY.maxWidth){width=Math.min(POLICY.maxWidth,width+12);lines=wrap(t.title,measure,width-54);}width=Math.max(width,...lines.map(measure).map(w=>w+54));return{key:t.key,lines,width,height:Math.max(36,lines.length*POLICY.topicLine+16)};}
function pack(topics,measure,available=Infinity){
 const items=topics.map(t=>topicCard(t,measure));if(!items.length)return{width:0,height:0,columns:[],rows:0,items:[],gapX:12,gapY:8};
 const count=items.length,target=count<=4?1:count<=10?2:count<=18?3:4,candidates=[];
 for(let cols=1;cols<=Math.min(4,count);cols++){const rows=Math.ceil(count/cols),widths=Array.from({length:cols},(_,c)=>Math.max(POLICY.minWidth,...items.slice(c*rows,(c+1)*rows).map(i=>i.width))),heights=Array.from({length:rows},(_,r)=>Math.max(...items.filter((_,i)=>i%rows===r).map(i=>i.height))),width=widths.reduce((a,b)=>a+b,0)+(cols-1)*12,height=heights.reduce((a,b)=>a+b,0)+(rows-1)*8,aspect=width/height;
 const score=Math.abs(Math.log(aspect/1.3))+.38*Math.abs(cols-target)+(width>available+.01?.5*Math.log(width/Math.max(180,available)):0);candidates.push({cols,rows,widths,heights,width,height,score});}
 const chosen=candidates.sort((a,b)=>a.score-b.score||a.cols-b.cols)[0],columns=[];let x=0;for(let c=0;c<chosen.cols;c++){let y=0;const entries=items.slice(c*chosen.rows,(c+1)*chosen.rows);for(let r=0;r<entries.length;r++){entries[r].x=x;entries[r].y=y;entries[r].width=chosen.widths[c];entries[r].height=chosen.heights[r];y+=chosen.heights[r]+8;}columns.push({x,width:chosen.widths[c],keys:entries.map(i=>i.key)});x+=chosen.widths[c]+12;}
 return{...chosen,columns,items,gapX:12,gapY:8};
}
function box(n,depth,measure){const font=categorySize(depth),preferred=depth===0?302:depth===1?248:184,max=depth<=1?330:260;let width=preferred,lines=wrap(n.title,t=>measure(t)*font/14,width-44);while(lines.length>3&&width<max){width+=12;lines=wrap(n.title,t=>measure(t)*font/14,width-44);}width=Math.max(width,...lines.map(t=>measure(t)*font/14+44));const line=font*1.2,height=lines.length*line+34;return{width,height,font,line,labelLines:lines,metaFont:10};}
function extent(rs){return{x0:Math.min(...rs.map(r=>r.x)),x1:Math.max(...rs.map(r=>r.x+r.w)),y0:Math.min(...rs.map(r=>r.y)),y1:Math.max(...rs.map(r=>r.y+r.h))};}
function translate(rs,x,y){return rs.map(r=>({...r,x:r.x+x,y:r.y+y}));}
function separation(placed,rects){let shift=-Infinity;for(const a of placed)for(const b of rects)if(a.y<b.y+b.h+12&&a.y+a.h+12>b.y)shift=Math.max(shift,a.x+a.w+GAP-b.x);return shift;}
// Place complete category subtree contours in bounded shelves. Every child stays below its parent.
function intersects(a,b,gap=12){return a.x<b.x+b.w+gap&&a.x+a.w+gap>b.x&&a.y<b.y+b.h+gap&&a.y+a.h+gap>b.y;}
function collides(a,b){return a.some(r=>b.some(s=>intersects(r,s)));}
function compactChildren(cats,plans){
 if(!cats.length)return{};
 const widths=cats.map(c=>plans.get(c.key).width),minimum=Math.max(...widths),sum=widths.reduce((a,b)=>a+b,0)+GAP*(cats.length-1),options=[minimum,minimum*1.25,minimum*1.55,minimum*2+GAP,...widths.flatMap((a,i)=>widths.slice(i+1).map(b=>a+b+GAP)),sum].filter((v,i,all)=>v<=sum+.1&&all.indexOf(v)===i);let best;
 for(const limit of options){const placed=[],slots={};let usedRight=0,usedBottom=0;
 for(const c of cats){const sub=plans.get(c.key),b=extent(sub.rects),norm=translate(sub.rects,-b.x0,0),xs=new Set([0,Math.max(0,limit-sub.width)]),ys=new Set([0]);
 for(const r of placed){xs.add(r.x+r.w+GAP);xs.add(Math.max(0,r.x-sub.width-GAP));ys.add(r.y+r.h+GAP);}
 const candidatesX=[...xs].filter(x=>x>=0&&x+sub.width<=limit+.1).sort((a,b)=>a-b),candidatesY=[...ys].sort((a,b)=>a-b);let chosen;
 for(const y of candidatesY){for(const x of candidatesX){const rs=translate(norm,x,y);if(collides(placed,rs))continue;const right=Math.max(usedRight,x+sub.width),bottom=Math.max(usedBottom,y+sub.height),score=right*bottom+bottom*minimum*.35+y*minimum*.08;if(!chosen||score<chosen.score)chosen={x,y,rs,score,right,bottom};}if(chosen&&y>chosen.bottom)break;}
 if(!chosen){const y=usedBottom+GAP;chosen={x:0,y,rs:translate(norm,0,y),right:Math.max(usedRight,sub.width),bottom:y+sub.height};}
 slots[c.key]={x:chosen.x-b.x0,y:chosen.y,width:sub.width,height:sub.height,overflow:false};placed.push(...chosen.rs);usedRight=chosen.right;usedBottom=chosen.bottom;
 }
 const aspect=usedRight/usedBottom,score=usedRight*usedBottom*(1+.23*Math.abs(Math.log(aspect/1.1)));if(!best||score<best.score)best={slots,score,width:usedRight,height:usedBottom};
 }
 const center=best.width/2;for(const slot of Object.values(best.slots))slot.x-=center;return best.slots;
}
function build(m,measure,previous=null){
 if(previous&&(previous.layout_schema_version!==SCHEMA||previous.layout_algorithm_version!==VERSION))throw Error('V6.1 requires its explicit schema-3 boxed checkpoint; old presentation checkpoints are archived, never silently loaded');
 const records={},plans=new Map(),bands=new Map(),events=[];
 function plan(n,depth){const cats=n.children.filter(c=>c.type==='category'),topics=n.children.filter(c=>c.type==='topic'),old=previous?.categories[n.key],card=box(n,depth,measure);cats.forEach(c=>plan(c,depth+1));const band=pack(topics,measure,old?.band.width||Infinity);bands.set(n.key,band);const childTop=Math.max(old?.childTop||0,card.height+LEVEL_GAP+(band.height?band.height+40:0)),children={},placed=[];
 const packed=!old&&depth>0?compactChildren(cats,plans):null;let first=true;
 for(const c of cats){const sub=plans.get(c.key),prior=old?.children[c.key];let y=prior?Math.max(prior.y,childTop):childTop,x=prior?.x??packed?.[c.key].x??0,overflow=prior?.overflow||false;
 if(packed)y=childTop+packed[c.key].y;
 if(old&&!prior){y=Math.max(childTop,old.height+54);x=0;overflow=true;events.push({kind:'local-new-branch',key:c.key,parent:n.key});}
 if(old&&depth>0){let rs=translate(sub.rects,x,y);if(collides(placed,rs)){const candidates=[...new Set(placed.flatMap(a=>sub.rects.map(b=>a.y+a.h+GAP-b.y)))].filter(v=>v>=y).sort((a,b)=>a-b);const free=candidates.find(v=>!collides(placed,translate(sub.rects,x,v)));y=free??Math.max(...placed.map(r=>r.y+r.h))+GAP;events.push({kind:'local-vertical-growth',key:c.key,parent:n.key});}}
 else if(!packed&&!first&&!prior){const needed=separation(placed,translate(sub.rects,0,y));if(Number.isFinite(needed))x=needed;}
 children[c.key]={x,y,width:sub.width,height:sub.height,overflow};placed.push(...translate(sub.rects,x,y));first=false;
 }
 if(!old&&depth===0&&cats.length){const center=(children[cats[0].key].x+children[cats.at(-1).key].x)/2;for(const slot of Object.values(children))slot.x-=center;for(const r of placed)r.x-=center;}

 const own=[{x:-card.width/2,y:0,w:card.width,h:card.height,key:n.key,kind:'category'}];if(band.items.length)own.push({x:-band.width/2-8,y:card.height+LEVEL_GAP-18,w:band.width+16,h:band.height+18,key:n.key,kind:'topic-band'});
 const rects=[...own,...placed],b=extent(rects),width=b.x1-b.x0,height=b.y1,record={anchor:0,width,height,box:card,band:{left:-band.width/2,top:card.height+LEVEL_GAP,width:band.width,height:band.height,columns:band.columns.map(c=>c.width),rows:band.rows,gapX:12,gapY:8},childTop,children,sibling_order:cats.map(c=>c.key)};
 records[n.key]=record;plans.set(n.key,{rects,width,height});
 }
 plan(m.root,0);const nodes=[],byKey=new Map(),branches=[],buses=[];
 function place(n,x,y,depth){const r=records[n.key],node={data:n,key:n.key,x,y,depth,lines:r.box.labelLines,font:r.box.font,line:r.box.line,width:r.box.width,height:r.box.height};nodes.push(node);byKey.set(n.key,node);const band=bands.get(n.key),bx=x+r.band.left,by=y+r.band.top;
 if(band.items.length){const busY=by-16,spines=band.columns.map(c=>bx+c.x-6);buses.push({parent:n.key,topics:band.items.map(i=>i.key),points:[{x,y:y+node.height},{x,y:busY},{x:Math.min(...spines),y:busY},{x:Math.max(...spines),y:busY}]});
 for(const c of band.columns){const spine=bx+c.x-6,entries=band.items.filter(i=>c.keys.includes(i.key)),last=entries.at(-1);buses.push({parent:n.key,topics:c.keys,points:[{x:spine,y:busY},{x:spine,y:by+last.y+last.height/2}]});}
 for(const i of band.items){const t=n.children.find(t=>t.key===i.key),leaf={data:t,key:t.key,x:bx+i.x+i.width/2,y:by+i.y,depth:depth+1,lines:i.lines,font:14,line:17,width:i.width,height:i.height,parent:n.key};nodes.push(leaf);byKey.set(t.key,leaf);buses.push({parent:n.key,topic:t.key,topics:[t.key],points:[{x:leaf.x-leaf.width/2-6,y:leaf.y+leaf.height/2},{x:leaf.x-leaf.width/2,y:leaf.y+leaf.height/2}]});}}
 for(const c of n.children.filter(c=>c.type==='category')){const slot=r.children[c.key];place(c,x+slot.x,y+slot.y,depth+1);branches.push({parent:n.key,child:c.key});}
 }
 place(m.root,0,0,0);
 const obstacles=nodes.map(n=>({x:n.x-n.width/2,y:n.y,w:n.width,h:n.height,key:n.key,kind:'card'}));
 for(const e of branches){const a=byKey.get(e.parent),b=byKey.get(e.child),route=g.AtlasRouting.boxRoute(a,b,obstacles);e.d=route.d;e.points=route.points;}
 for(const e of buses)e.d=e.points.map((p,i)=>(i?'L':'M')+p.x+','+p.y).join('');
 return{nodes,byKey,branches,buses,bands,events,checkpoint:{layout_schema_version:SCHEMA,layout_algorithm_version:VERSION,categories:records}};
}
function visible(L,m,collapsed){return L.nodes.filter(n=>{let p=m.nodes.get('category:'+n.data.canonical_parent_id);while(p){if(collapsed.has(p.key))return false;p=m.nodes.get('category:'+p.canonical_parent_id);}return true;});}
function bounds(nodes){return{x0:Math.min(...nodes.map(n=>n.x-n.width/2))-16,x1:Math.max(...nodes.map(n=>n.x+n.width/2))+16,y0:Math.min(...nodes.map(n=>n.y))-16,y1:Math.max(...nodes.map(n=>n.y+n.height))+16};}
g.AtlasLayout={build,pack,wrap,visible,bounds,FONT,categorySize,POLICY};
})(globalThis);
