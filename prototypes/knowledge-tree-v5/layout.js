/* Category slot ledger; no persisted topic coordinates. */
(function(g){
'use strict';
const GAP=32,LEVEL=900,SCHEMA=2,ALGORITHM="persistent-geography-2";
function box(n){return Math.max(n.data.type==='topic'?190:210,...n.data.lines.map(l=>l.length*(n.depth===0?13:n.depth===1?10:8)+32));}
function initialPlan(m,reserve=.4,previous=null,collapsed=new Set()){
 if(previous?.version!=null&&previous.version!==SCHEMA)throw Error('Unsupported legacy layout schema; explicit migration required');
 if(previous?.layout_schema_version!=null&&previous.layout_schema_version!==SCHEMA)throw Error('Unsupported layout schema; explicit migration required');
 if(previous?.layout_algorithm_version!=null&&previous.layout_algorithm_version!==ALGORITHM)throw Error('Layout algorithm mismatch; explicit migration required');
 const events=[];
 const h=d3.hierarchy(m.root,n=>collapsed.has(n.key)?null:n.children),records={};
 h.eachAfter(n=>{n.box=box(n);n.natural=Math.max(n.box,n.children?n.children.reduce((s,c)=>s+c.natural,0)+GAP*(n.children.length-1):0);if(n.data.type==='topic'){n.slotWidth=n.box;n.anchor=n.box/2;return;}
 const old=previous?.categories[n.data.key],cats=(n.children||[]).filter(c=>c.data.type==='category'),topics=(n.children||[]).filter(c=>c.data.type==='topic');let right=0;const children={};
 for(const c of cats){const prior=old?.children[c.data.key];const left=Math.max(prior?.left||0,right);let width=Math.max(prior?.width||0,c.slotWidth);if(prior&&left>prior.left){const consumed=left-prior.left;const minimum=records[c.data.key].contentWidth;const borrowed=Math.min(consumed,Math.max(0,width-minimum));width=Math.max(minimum,width-consumed);records[c.data.key].width=width;records[c.data.key].borrowedReserve=borrowed;c.slotWidth=width;}children[c.data.key]={left,width,shift:prior?left-prior.left:0,budget:prior?prior.width*.05:0,budgetExceeded:prior?left-prior.left>prior.width*.05:false};right=left+width+GAP;}
 const topicStart=Math.max(old?.topicStart||0,right);let content=topics.length?topicStart+topics.reduce((s,c)=>s+c.box,0)+GAP*(topics.length-1):Math.max(0,right-GAP);content=Math.max(content,n.box);
 // Reserve only major-area and direct-domain subtrees. Ancestor budgets cover
 // already allocated child reserve rather than multiplying it again.
 const relevant=n.depth===1||n.depth===3;
 const width=Math.max(old?.width||0,content,relevant&&!old?n.natural*(1+reserve):0);
 const anchor=old?.anchor??content/2;
 records[n.data.key]={anchor,width,contentWidth:content,naturalWidth:n.natural,topicStart,children};n.slotWidth=width;n.anchor=anchor;
 });
 if(previous){h.eachAfter(n=>{if(n.data.type!=='category')return;const key=n.data.key,p=records[key],old=previous.categories[key];if(!old)return;
 const grew=p.contentWidth>old.contentWidth+.001,overflow=p.contentWidth>old.width+.001;
 if(grew)events.push({level:overflow?2:1,key,reason:overflow?'slot capacity exhausted':'existing reserve',remainingReserve:Math.max(0,p.width-p.contentWidth),widthDelta:p.width-old.width});
 const shifts=Object.entries(p.children).filter(([k,c])=>previous.categories[key]?.children[k]&&c.shift>.001);
 for(const [child,c]of shifts)events.push({level:3,key:child,parent:key,reason:'adjacent slot collision',shift:c.shift,budget:c.budget,budgetExceeded:c.budgetExceeded});
 if(overflow&&n.children?.some(c=>c.data.type==='category'&&records[c.data.key]?.contentWidth>(previous.categories[c.data.key]?.width??Infinity)+.001))events.push({level:n.depth>=2?4:5,key,reason:'child overflow exceeds parent capacity; anchors retained',widthDelta:p.width-old.width});
 });}
 const signature=rs=>JSON.stringify(Object.entries(rs).sort(([a],[b])=>a.localeCompare(b)).map(([key,p])=>[key,p.anchor,p.width,p.topicStart,Object.entries(p.children).sort(([a],[b])=>a.localeCompare(b)).map(([k,c])=>[k,c.left,c.width])]));
 const generation=previous?(previous.generation??0)+(signature(records)!==signature(previous.categories)?1:0):0;
 return{version:1,layout_schema_version:SCHEMA,layout_algorithm_version:ALGORITHM,generation,reserve,gap:GAP,level:LEVEL,categories:records,events};
}
// Only categories are persisted. Topic rows are reconstructed from taxonomy.
const MAX_ROWS=6,ROW_HEIGHT=100;
function canonical(value){return JSON.stringify(value, function(k,v){return v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v;});}
function serialize(plan){
 const categories={};
 for(const key of Object.keys(plan.categories).sort()){
  const p=plan.categories[key],children={};
  for(const k of Object.keys(p.children).sort())children[k]={left:p.children[k].left,width:p.children[k].width};
  categories[key]={category_id:key,parent_id:p.parent_id,sibling_order:p.sibling_order,anchor:p.anchor,width:p.width,reserved_capacity:p.reserved_capacity,growth_limit_width:p.growth_limit_width,topicStart:p.topicStart,topicRowOffset:p.topicRowOffset,children};
 }
 return JSON.stringify({layout_schema_version:SCHEMA,layout_algorithm_version:ALGORITHM,generation:plan.generation,reserve:plan.reserve,gap:GAP,level:LEVEL,categories},null,2)+'\n';
}
function validate(previous){
 const allowed=['layout_schema_version','layout_algorithm_version','generation','reserve','gap','level','categories','events'];if(Object.keys(previous).some(k=>!allowed.includes(k))||!Number.isFinite(previous.reserve)||previous.reserve<0||previous.reserve>1)throw Error('Invalid checkpoint fields');
 if(previous.layout_schema_version!==SCHEMA)throw Error('Incompatible layout schema; explicit migration required');
 if(previous.layout_algorithm_version!==ALGORITHM)throw Error('Incompatible layout algorithm; explicit migration required');
 if(!Number.isSafeInteger(previous.generation)||previous.generation<0)throw Error('Invalid checkpoint generation');
 if(!previous.categories||previous.gap!==GAP||previous.level!==LEVEL)throw Error('Invalid checkpoint structure');
 for(const [key,p]of Object.entries(previous.categories)){
  if(!/^category:[0-9]+$/.test(key)||Object.keys(p).some(k=>!['category_id','parent_id','sibling_order','anchor','width','reserved_capacity','growth_limit_width','topicStart','topicRowOffset','children'].includes(k))||p.category_id!==key||!Number.isSafeInteger(p.sibling_order)||p.sibling_order<0||!['anchor','width','reserved_capacity','growth_limit_width','topicStart'].every(k=>Number.isFinite(p[k])&&p[k]>=0)||p.width<=0||p.reserved_capacity>p.width||p.growth_limit_width<p.width||p.anchor>p.width||!Number.isInteger(p.topicRowOffset)||![0,2].includes(p.topicRowOffset)||!p.children)throw Error('Invalid checkpoint category '+key);
  const slots=Object.entries(p.children).sort((a,b)=>a[1].left-b[1].left);let end=-GAP;
  for(const [child,c]of slots){if(Object.keys(c).some(k=>!['left','width'].includes(k))||!previous.categories[child]||previous.categories[child].parent_id!==key||!Number.isFinite(c.left)||!Number.isFinite(c.width)||c.width<=0||c.left<end+GAP-.001||c.left+c.width>p.width+.001||c.width!==previous.categories[child].width)throw Error('Invalid checkpoint slot '+child);end=c.left+c.width;}
 }
 const roots=Object.keys(previous.categories).filter(k=>previous.categories[k].parent_id===null);
 if(roots.length!==1)throw Error('Invalid checkpoint root count');
 for(const [key,p]of Object.entries(previous.categories)){
  if(p.parent_id!==null&&!previous.categories[p.parent_id]?.children[key])throw Error('Orphan checkpoint category '+key);
  const visited=new Set();let at=key;while(at){if(visited.has(at))throw Error('Cyclic checkpoint category '+key);visited.add(at);at=previous.categories[at]?.parent_id;}
  const orders=Object.keys(p.children).map(k=>previous.categories[k].sibling_order);if(new Set(orders).size!==orders.length)throw Error('Duplicate sibling order '+key);
 }

}
function packing(topics,start,width){
 let x=start,row=0,max=0;const positions=new Map();
 for(const n of topics){const w=box(n);if(x>start&&x+w>width+.001){row++;x=start;}
 positions.set(n.data.key,{left:x,row});x+=w+GAP;max=Math.max(max,x-GAP);}
 return{positions,rows:topics.length?row+1:0,extent:max};
}
function buildPlan(m,reserve=.4,previous=null,collapsed=new Set(),options={}){
 if(options.expectedGeneration!=null&&previous?.generation!==options.expectedGeneration)throw Error('STALE_GENERATION: checkpoint changed');
 if(previous)validate(previous);
 const h=d3.hierarchy(m.root,n=>collapsed.has(n.key)?null:n.children),records={},events=[];
 const fresh=initialPlan(m,reserve,null,collapsed);
 h.eachAfter(n=>{
  if(n.data.type==='topic'){n.box=box(n);return;}
  const key=n.data.key,parent=n.parent?.data.key??null,prior=previous?.categories[key];
  const old=prior?.parent_id===parent?prior:null;
  if(prior&&!old)events.push({level:1,key,reason:'category moved; allocate in destination parent'});
  const cats=(n.children||[]).filter(c=>c.data.type==='category'),topics=(n.children||[]).filter(c=>c.data.type==='topic');
  // Retained siblings preserve ledger order; new siblings append by stable ID.
  cats.sort((a,b)=>{const aa=previous?.categories[a.data.key],bb=previous?.categories[b.data.key];const ai=aa?.parent_id===key?aa.sibling_order:Infinity,bi=bb?.parent_id===key?bb.sibling_order:Infinity;return ai-bi||a.data.id-b.data.id;});
  const children={};let right=0,nextOrder=Math.max(-1,...cats.map(c=>previous?.categories[c.data.key]?.parent_id===key?previous.categories[c.data.key].sibling_order:-1))+1;
  for(const c of cats){const p=records[c.data.key],slot=old?.children[c.data.key];const left=Math.max(slot?.left??0,right);children[c.data.key]={left,width:p.width};p.sibling_order=slot?previous.categories[c.data.key].sibling_order:nextOrder++;if(slot&&left!==slot.left)events.push({level:3,key:c.data.key,parent:key,reason:'minimal adjacent slot shift',shift:left-slot.left});right=left+p.width+GAP;}
  const topicRowOffset=old?.topicRowOffset??(cats.length&&!topics.length?2:0);
  const start=topicRowOffset?0:Math.max(old?.topicStart??(topics.length?fresh?.categories[key]?.topicStart:0)??0,topics.length&&cats.length?right:0);
  const useInitialGeometry=!previous||(!old&&n.depth===1&&cats.length>0);
  let width=Math.max(old?.width??(useInitialGeometry?fresh.categories[key].width:box(n)),box(n),cats.length?right-GAP:0);
  if(topics.length)width=Math.max(width,start+Math.max(...topics.map(box)));
  let packed=packing(topics,start,width);
  if(packed.rows>MAX_ROWS){const total=topics.reduce((a,t)=>a+box(t)+GAP,0);width=Math.max(width,start+Math.ceil(total/MAX_ROWS)+Math.max(...topics.map(box)));packed=packing(topics,start,width);}
  const content=Math.max(box(n),cats.length?right-GAP:0,packed.extent);
  const anchor=old?.anchor??(useInitialGeometry?fresh.categories[key].anchor:width/2);
  records[key]={category_id:key,parent_id:parent,sibling_order:old?.sibling_order??0,anchor,width,reserved_capacity:Math.max(0,width-content),growth_limit_width:old?.growth_limit_width??Math.max(width*(parent===null?2:3),width+12000),topicStart:start,topicRowOffset,children};
  if(old){if(options.changedParents?.includes(key)&&width===old.width)events.push({level:1,key,reason:'topics packed inside existing parent slot'});if(width>old.width){events.push({level:2,key,reason:'local slot extension',widthDelta:width-old.width});if(cats.some(c=>records[c.data.key].width>(old.children[c.data.key]?.width??0)))events.push({level:n.depth>1?4:5,key,reason:n.depth>1?'parent region extension':'ancestor region extension',widthDelta:width-old.width});}else if(canonical(records[key])!==canonical(old))events.push({level:1,key,reason:'parent capacity used or released'});}
 });
 const plan={layout_schema_version:SCHEMA,layout_algorithm_version:ALGORITHM,generation:previous?.generation??0,reserve:previous?.reserve??reserve,gap:GAP,level:LEVEL,categories:records,events};
 if(previous&&serialize(plan)!==serialize(previous))plan.generation++;
 // Vertical rows are bounded inside one taxonomy level. Excessive region growth
 // is rejected, never converted into an implicit global re-layout.
 if(previous){const root=records[m.root.key],oldRoot=previous.categories[m.root.key];const excessive=Object.entries(records).filter(([k,p])=>previous.categories[k]&&p.width>previous.categories[k].growth_limit_width);
 if(excessive.length||root.width>oldRoot.growth_limit_width){const [key,p]=excessive[0]||[m.root.key,root];const affected=Object.keys(records).filter(k=>{let at=k;while(at){if(at===key)return true;at=records[at]?.parent_id;}return false;});for(const e of events)if(e.level>=3&&!affected.includes(e.key))affected.push(e.key);affected.sort();const report={status:'REBALANCE_REQUIRED',affected_ancestor:key,required_width:p.width,available_width:previous.categories[key].width,affected_categories:affected,estimated_displacement:Math.max(0,...events.map(e=>e.shift||e.widthDelta||0))};const error=Error('REBALANCE_REQUIRED: '+key);error.report=report;throw error;}}
 return plan;
}
function classifyLayout(before,after,mode='knowledge-update'){
 if(!['knowledge-update','rebalance-layout'].includes(mode))throw Error('Unknown layout operation');
 const result={};for(const n of before.nodes){const next=after.byKey.get(n.data.key);if(next)result[n.data.key]=n.x===next.x&&n.y===next.y?'STABLE':mode==='rebalance-layout'?'REBALANCE':'LOCAL_MOVE';}return result;
}
function rebalanceLayout(m,previous=null){const p=buildPlan(m,previous?.reserve??.4);p.generation=(previous?.generation??-1)+1;p.events=[{classification:'REBALANCE',reason:'explicit rebalance-layout'}];return p;}
function layout(m,collapsed=new Set(),engine='incremental',plan=null){
 const hierarchy=d3.hierarchy(m.root,n=>collapsed.has(n.key)?null:n.children);
 if(engine==='d3-tree'){d3.tree().nodeSize([1,LEVEL]).separation((a,b)=>(box(a)+box(b))/2+28)(hierarchy);hierarchy.each(n=>n.box=box(n));}
 else if(engine==='packed'){hierarchy.eachAfter(n=>{n.box=box(n);n.span=Math.max(n.box,n.children?n.children.reduce((s,c)=>s+c.span,0)+GAP*(n.children.length-1):0);});function place(n,left){n.x=left+n.span/2;n.y=n.depth*LEVEL;if(n.children){let x=left+(n.span-(n.children.reduce((s,c)=>s+c.span,0)+GAP*(n.children.length-1)))/2;for(const c of n.children){place(c,x);x+=c.span+GAP;}}}place(hierarchy,0);}
 else{const ledger=plan||buildPlan(m,.4,null,collapsed);hierarchy.each(n=>{if(n.children)n.children.sort((a,b)=>(a.data.type===b.data.type?0:a.data.type==='category'?-1:1)||(a.data.type==='category'?ledger.categories[a.data.key].sibling_order-ledger.categories[b.data.key].sibling_order:a.data.id-b.data.id));});function place(n,left){n.box=box(n);n.left=left;n.y=n.depth*(ledger.level||LEVEL);if(n.data.type==='topic'){n.x=left+n.box/2;n.span=n.box;return;}const p=ledger.categories[n.data.key];if(!p)throw Error('Missing category slot '+n.data.key);n.x=left+p.anchor;n.span=p.width;const topics=(n.children||[]).filter(c=>c.data.type==='topic'),packed=packing(topics,p.topicStart,p.width);for(const c of n.children||[]){if(c.data.type==='category')place(c,left+p.children[c.data.key].left);else{const t=packed.positions.get(c.data.key);place(c,left+t.left);c.y+=(t.row+p.topicRowOffset)*ROW_HEIGHT*(ledger.level||LEVEL)/LEVEL;}}}place(hierarchy,0);}
 return{root:hierarchy,nodes:hierarchy.descendants(),links:hierarchy.links(),byKey:new Map(hierarchy.descendants().map(n=>[n.data.key,n]))};
}
function scaffold(m){const h=d3.hierarchy(m.root),domains=h.descendants().filter(n=>n.depth===2&&n.data.type==='category').sort((a,b)=>b.descendants().filter(c=>c.data.is_learned===true).length-a.descendants().filter(c=>c.data.is_learned===true).length||a.data.id-b.data.id),dominant=domains[0];return new Set([...h.descendants().filter(n=>n.depth<=1),...(dominant?[dominant,...(dominant.children||[]).filter(n=>n.data.type==='category')]:[])].map(n=>n.data.key));}
function defaultExpansion(m,mobile){const h=d3.hierarchy(m.root),learned=n=>n.descendants().filter(c=>c.data.type==='topic'&&c.data.is_learned===true).length;const domains=h.descendants().filter(n=>n.depth===2&&n.data.type==='category').sort((a,b)=>learned(b)-learned(a)||a.data.id-b.data.id),dominant=domains[0];const keep=new Set(dominant?dominant.ancestors().map(n=>n.data.key):[m.root.key]);return new Set(h.descendants().filter(n=>n.data.type==='category'&&n.children&&(mobile?!keep.has(n.data.key):n.depth>=2&&learned(n)===0)).map(n=>n.data.key));}
g.TreeLayout={classifyLayout,canonical,serialize,validate,rebalanceLayout,packing,MAX_ROWS,ROW_HEIGHT,buildPlan,layout,defaultExpansion,scaffold,box,GAP,LEVEL,SCHEMA,ALGORITHM};
})(typeof window==='undefined'?globalThis:window);
