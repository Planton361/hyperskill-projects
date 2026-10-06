/* Measured hierarchy-first slots. No knowledge or topic coordinates in checkpoints. */
(function(g){
'use strict';
const VERSION='atlas-readable-2',GAP=32,FONT='40px system-ui',LINE=52;
const categorySize=depth=>depth===0?144:depth===1?96:depth===2?64:depth===3?44:36;
// Narrow complete labels; long tokens may wrap without inserting semantic spaces.
function wrap(title,measure,max=112){const lines=[];let line='';for(const word of title.split(/\s+/)){if(measure(word)>max){if(line){lines.push(line);line='';}let part='';for(const char of word){if(part&&measure(part+char)>max){lines.push(part);part=char;}else part+=char;}line=part;continue;}if(line&&measure(line+' '+word)>max){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;}
function categoryWrap(title,measure,max){const lines=[];let line='';for(const word of title.split(/\s+/)){if(line&&measure(line+' '+word)>max){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;}
function pack(topics,measure,available=420){
 const items=topics.map(t=>({key:t.key,lines:wrap(t.title,measure)}));for(const i of items){i.width=Math.max(...i.lines.map(measure))+46;i.height=Math.max(64,i.lines.length*LINE+24);}
 if(!items.length)return{width:0,height:0,columns:[],items:[]};
 let cols=1;for(let candidate=Math.ceil(items.length/5);candidate>1;candidate--){const rows=Math.ceil(items.length/candidate);let total=(candidate-1)*40;for(let c=0;c<candidate;c++)total+=Math.max(156,...items.slice(c*rows,(c+1)*rows).map(i=>i.width));if(total<=available+.001){cols=candidate;break;}}const rows=Math.ceil(items.length/cols),columns=[];let x=0;
 for(let c=0;c<cols;c++){const entries=items.slice(c*rows,(c+1)*rows),width=Math.max(156,...entries.map(i=>i.width));let y=0;for(const i of entries){i.x=x+22;i.y=y+22;y+=i.height+24;}columns.push({x,width,height:y,keys:entries.map(i=>i.key)});x+=width+40;}
 return{width:x-40,height:Math.max(...columns.map(c=>c.height)),columns,items};
}
function build(m,measure,previous=null){
 if(previous&&(previous.layout_schema_version!==2||previous.layout_algorithm_version!==VERSION))throw Error('Incompatible V6 presentation checkpoint; use the explicit readable-2 checkpoint');
 const records={},bands=new Map();
 function plan(n,depth){const cats=n.children.filter(c=>c.type==='category'),topics=n.children.filter(c=>c.type==='topic');cats.forEach(c=>plan(c,depth+1));const old=previous?.categories[n.key],band=pack(topics,measure,old?.band.width||420);bands.set(n.key,band);
 const font=categorySize(depth),categoryLines=(depth<=2?categoryWrap:wrap)(n.title,t=>measure(t)*font/40,depth<=1?580:depth===2?250:120),labelWidth=Math.max(...categoryLines.map(t=>measure(t)*font/40))+48,line=font*1.2,head=categoryLines.length*line+70+font*.35;
 const bandWidth=Math.max(old?.band.width||0,band.width),bandHeight=Math.max(old?.band.height||0,band.height+(band.height?24:0));
 const children={};let right=0;for(const c of cats){const prior=old?.children[c.key],left=Math.max(prior?.left||0,right);children[c.key]={left,width:records[c.key].width};right=left+records[c.key].width+GAP;}
 const content=Math.max(labelWidth,bandWidth,cats.length?right-GAP:0),width=Math.max(old?.width||0,content+16),anchor=old?.anchor??width/2;
 records[n.key]={anchor,width,labelLines:categoryLines,head,band:{left:old?.band.left??Math.max(12,(width-bandWidth)/2),top:head+24,width:bandWidth,height:bandHeight},childTop:Math.max(old?.childTop||0,head+24+bandHeight+90),children,sibling_order:cats.map(c=>c.key)};
 }
 plan(m.root,0);const nodes=[],byKey=new Map(),branches=[],buses=[];
 function place(n,left,top,depth){const r=records[n.key],font=categorySize(depth),node={data:n,key:n.key,x:left+r.anchor,y:top,depth,lines:r.labelLines,font,line:font*1.2,width:r.width};nodes.push(node);byKey.set(n.key,node);const band=bands.get(n.key),bx=left+r.band.left,by=top+r.band.top;
 if(band.items.length){const center=bx+band.width/2,busY=by-30;buses.push({parent:n.key,d:`M${node.x},${top+r.head-10}V${busY}H${center}`,topics:band.items.map(i=>i.key)});const spines=band.columns.map(c=>bx+c.x+4);buses.push({parent:n.key,d:`M${Math.min(center,...spines)},${busY}H${Math.max(center,...spines)}`,topics:band.items.map(i=>i.key)});for(const c of band.columns){const spine=bx+c.x+4,last=band.items.find(i=>i.key===c.keys.at(-1));buses.push({parent:n.key,d:`M${spine},${busY}V${by+last.y}`,topics:c.keys});}
 for(const item of band.items){const t=n.children.find(t=>t.key===item.key),leaf={data:t,key:t.key,x:bx+item.x,y:by+item.y,depth:depth+1,lines:item.lines,font:40,line:LINE,width:item.width,height:item.height,parent:n.key};nodes.push(leaf);byKey.set(t.key,leaf);buses.push({parent:n.key,topic:t.key,topics:[t.key],d:`M${leaf.x-22},${leaf.y}H${leaf.x-10}`});}}
 for(const c of n.children.filter(c=>c.type==='category')){const slot=r.children[c.key];place(c,left+slot.left,top+r.childTop,depth+1);const child=byKey.get(c.key),lane=child.y-92;branches.push({parent:n.key,child:c.key,d:`M${node.x},${top+r.head-10}V${lane}H${child.x}V${child.y-24}`});}
 }
 place(m.root,0,0,0);return{nodes,byKey,branches,buses,bands,checkpoint:{layout_schema_version:2,layout_algorithm_version:VERSION,categories:records}};
}
function visible(L,m,collapsed){return L.nodes.filter(n=>{let p=m.nodes.get('category:'+n.data.canonical_parent_id);while(p){if(collapsed.has(p.key))return false;p=m.nodes.get('category:'+p.canonical_parent_id);}return true;});}
function bounds(nodes){return{x0:Math.min(...nodes.map(n=>n.data.type==='topic'?n.x-30:n.x-Math.max(...n.lines.map(l=>l.length*n.font*.65))/2))-30,x1:Math.max(...nodes.map(n=>n.data.type==='topic'?n.x+n.width:n.x+Math.max(...n.lines.map(l=>l.length*n.font*.65))/2))+30,y0:Math.min(...nodes.map(n=>n.y))-45,y1:Math.max(...nodes.map(n=>n.y+n.lines.length*n.line+(n.data.type==='category'?92:25)))+30};}
g.AtlasLayout={build,pack,wrap,visible,bounds,FONT,categorySize};
})(globalThis);
