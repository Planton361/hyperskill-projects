/* Geometry-only routing. Endpoint IDs and relation evidence are untouched. */
(function(g){
'use strict';
function segmentHits(a,b,r){let lo=0,hi=1;const dx=b.x-a.x,dy=b.y-a.y;for(const [p,q]of [[-dx,a.x-r.x],[dx,r.x+r.w-a.x],[-dy,a.y-r.y],[dy,r.y+r.h-a.y]]){if(Math.abs(p)<1e-9){if(q<0)return false;}else{const t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);if(lo>hi)return false;}}return hi>=0&&lo<=1;}
function polylineHits(points,obstacles){return obstacles.filter(r=>points.slice(1).some((b,i)=>segmentHits(points[i],b,r)));}
function rounded(points,radius=10){let d=`M${points[0].x},${points[0].y}`;for(let i=1;i<points.length-1;i++){const a=points[i-1],b=points[i],c=points[i+1],before=Math.hypot(b.x-a.x,b.y-a.y),after=Math.hypot(c.x-b.x,c.y-b.y);if(!before||!after)continue;const r=Math.min(radius,before/2,after/2),p={x:b.x-(b.x-a.x)/before*r,y:b.y-(b.y-a.y)/before*r},q={x:b.x+(c.x-b.x)/after*r,y:b.y+(c.y-b.y)/after*r};d+=`L${p.x},${p.y}Q${b.x},${b.y} ${q.x},${q.y}`;}const last=points.at(-1);return d+`L${last.x},${last.y}`;}
function gridPath(start,end,obstacles){
 const xs=[...new Set([start.x,end.x,...obstacles.flatMap(r=>[r.x-.2,r.x+r.w+.2])])].sort((a,b)=>a-b),ys=[...new Set([start.y,end.y,...obstacles.flatMap(r=>[r.y-.2,r.y+r.h+.2])])].sort((a,b)=>a-b),w=xs.length,h=ys.length,total=w*h;
 const blocked=new Uint8Array(total),horizontal=new Uint8Array(total),vertical=new Uint8Array(total);const lower=(arr,value)=>{let lo=0,hi=arr.length;while(lo<hi){const mid=(lo+hi)>>1;if(arr[mid]<value)lo=mid+1;else hi=mid;}return lo;},upper=(arr,value)=>lower(arr,value+1e-6);
 for(const r of obstacles){const x0=lower(xs,r.x),x1=upper(xs,r.x+r.w),y0=lower(ys,r.y),y1=upper(ys,r.y+r.h);for(let y=y0;y<y1;y++){for(let x=x0;x<x1;x++)blocked[y*w+x]=1;for(let x=Math.max(0,x0-1);x<Math.min(w-1,x1);x++)horizontal[y*w+x]=1;}for(let x=x0;x<x1;x++)for(let y=Math.max(0,y0-1);y<Math.min(h-1,y1);y++)vertical[y*w+x]=1;}
 const source=ys.indexOf(start.y)*w+xs.indexOf(start.x),target=ys.indexOf(end.y)*w+xs.indexOf(end.x),distance=new Float64Array(total).fill(Infinity),previous=new Int32Array(total).fill(-1),heap=[];if(blocked[source]||blocked[target])return null;
 function push(id,score){const item={id,score};let i=heap.length;heap.push(item);while(i>0){const p=(i-1)>>1;if(heap[p].score<=score)break;heap[i]=heap[p];i=p;}heap[i]=item;}
 function pop(){const first=heap[0],last=heap.pop();if(heap.length){let i=0;while(i*2+1<heap.length){let c=i*2+1;if(c+1<heap.length&&heap[c+1].score<heap[c].score)c++;if(heap[c].score>=last.score)break;heap[i]=heap[c];i=c;}heap[i]=last;}return first;}
 const heuristic=id=>Math.abs(xs[id%w]-end.x)+Math.abs(ys[Math.floor(id/w)]-end.y);distance[source]=0;push(source,heuristic(source));const seen=new Uint8Array(total);
 while(heap.length){const {id}=pop();if(seen[id])continue;seen[id]=1;if(id===target)break;const x=id%w,y=Math.floor(id/w);const candidates=[];if(x>0&&!horizontal[id-1])candidates.push(id-1);if(x<w-1&&!horizontal[id])candidates.push(id+1);if(y>0&&!vertical[id-w])candidates.push(id-w);if(y<h-1&&!vertical[id])candidates.push(id+w);for(const next of candidates){if(blocked[next]||seen[next])continue;const cost=Math.abs(xs[next%w]-xs[x])+Math.abs(ys[Math.floor(next/w)]-ys[y]);if(distance[id]+cost<distance[next]){distance[next]=distance[id]+cost;previous[next]=id;push(next,distance[next]+heuristic(next));}}}
 if(!Number.isFinite(distance[target]))return null;const points=[];for(let id=target;id!==-1;id=previous[id])points.push({x:xs[id%w],y:ys[Math.floor(id/w)]});points.reverse();return points.filter((p,i)=>!i||i===points.length-1||!((points[i-1].x===p.x&&p.x===points[i+1].x)||(points[i-1].y===p.y&&p.y===points[i+1].y)));
}

function lowBendPath(start,end,obstacles){
 const xs=[...new Set([start.x,end.x,...obstacles.flatMap(r=>[r.x-.2,r.x+r.w+.2])])].sort((a,b)=>a-b),ys=[...new Set([start.y,end.y,...obstacles.flatMap(r=>[r.y-.2,r.y+r.h+.2])])].sort((a,b)=>a-b),w=xs.length,h=ys.length,total=w*h;
 const blocked=new Uint8Array(total),horizontal=new Uint8Array(total),vertical=new Uint8Array(total);const lower=(arr,value)=>{let lo=0,hi=arr.length;while(lo<hi){const mid=(lo+hi)>>1;if(arr[mid]<value)lo=mid+1;else hi=mid;}return lo;},upper=(arr,value)=>lower(arr,value+1e-6);
 for(const r of obstacles){const x0=lower(xs,r.x),x1=upper(xs,r.x+r.w),y0=lower(ys,r.y),y1=upper(ys,r.y+r.h);for(let y=y0;y<y1;y++){for(let x=x0;x<x1;x++)blocked[y*w+x]=1;for(let x=Math.max(0,x0-1);x<Math.min(w-1,x1);x++)horizontal[y*w+x]=1;}for(let x=x0;x<x1;x++)for(let y=Math.max(0,y0-1);y<Math.min(h-1,y1);y++)vertical[y*w+x]=1;}
 const source=ys.indexOf(start.y)*w+xs.indexOf(start.x),target=ys.indexOf(end.y)*w+xs.indexOf(end.x),distance=new Float64Array(total*3).fill(Infinity),previous=new Int32Array(total*3).fill(-1),heap=[];if(blocked[source]||blocked[target])return null;
 function push(id,score){const item={id,score};let i=heap.length;heap.push(item);while(i>0){const p=(i-1)>>1;if(heap[p].score<=score)break;heap[i]=heap[p];i=p;}heap[i]=item;}
 function pop(){const first=heap[0],last=heap.pop();if(heap.length){let i=0;while(i*2+1<heap.length){let c=i*2+1;if(c+1<heap.length&&heap[c+1].score<heap[c].score)c++;if(heap[c].score>=last.score)break;heap[i]=heap[c];i=c;}heap[i]=last;}return first;}
 const heuristic=state=>{const id=Math.floor(state/3);return Math.abs(xs[id%w]-end.x)+Math.abs(ys[Math.floor(id/w)]-end.y)},origin=source*3;distance[origin]=0;push(origin,heuristic(origin));const seen=new Uint8Array(total*3);let finish=-1;
 while(heap.length){const {id:state}=pop();if(seen[state])continue;seen[state]=1;const id=Math.floor(state/3),dir=state%3;if(id===target){finish=state;break;}const x=id%w,y=Math.floor(id/w),candidates=[];if(x>0&&!horizontal[id-1])candidates.push([id-1,1]);if(x<w-1&&!horizontal[id])candidates.push([id+1,1]);if(y>0&&!vertical[id-w])candidates.push([id-w,2]);if(y<h-1&&!vertical[id])candidates.push([id+w,2]);for(const [next,axis]of candidates){const ns=next*3+axis;if(blocked[next]||seen[ns])continue;const cost=Math.abs(xs[next%w]-xs[x])+Math.abs(ys[Math.floor(next/w)]-ys[y])+(dir&&dir!==axis?40:0);if(distance[state]+cost<distance[ns]){distance[ns]=distance[state]+cost;previous[ns]=state;push(ns,distance[ns]+heuristic(ns));}}}
 if(finish<0)return null;const points=[];for(let state=finish;state!==-1;state=previous[state]){const id=Math.floor(state/3);points.push({x:xs[id%w],y:ys[Math.floor(id/w)]});}points.reverse();return points.filter((p,i)=>!i||i===points.length-1||!((points[i-1].x===p.x&&p.x===points[i+1].x)||(points[i-1].y===p.y&&p.y===points[i+1].y)));
}

function hash(key){let h=0;for(const c of key)h=(h*31+c.charCodeAt(0))>>>0;return h;}
function route(a,b,kind='lanes',obstacles=[],key=a.data?.key+'>'+b.data?.key,nodes=[]){
 const start={x:a.x,y:a.y-12},end={x:b.x,y:b.y-12},lane=Math.min(a.y,b.y)-82;
 if(kind==='quadratic'){const offset=110+hash(key)%7*18;const control={x:(a.x+b.x)/2,y:Math.min(a.y,b.y)-offset};const points=Array.from({length:65},(_,i)=>{const t=i/64,u=1-t;return{x:u*u*start.x+2*u*t*control.x+t*t*end.x,y:u*u*start.y+2*u*t*control.y+t*t*end.y};});return{d:`M${start.x},${start.y}Q${control.x},${control.y} ${end.x},${end.y}`,points};}
 if(kind==='cubic'){
 // Frozen V5 control geometry and its estimated-category obstacle scoring.
 const s={x:a.x,y:a.y+12},e={x:b.x,y:b.y-12};let best=Infinity,chosen=lane;const category=nodes.length?nodes.filter(n=>n.data.type==='category').map(n=>({x:n.x-Math.max(...n.data.lines.map(t=>t.length*(n.depth===0?13:n.depth===1?11:9)))/2-5,y:n.y+14,w:Math.max(...n.data.lines.map(t=>t.length*(n.depth===0?13:n.depth===1?11:9)))+10,h:n.data.lines.length*(n.depth<=1?26:19)+8})):obstacles.filter(r=>r.kind==='category-label');for(const v of [lane,lane-80,lane-170,Math.max(a.y,b.y)+110,Math.max(a.y,b.y)+220]){let hits=0;for(let i=1;i<80;i++){const t=i/80,u=1-t,x=u*u*u*a.x+3*u*u*t*(a.x+42)+3*u*t*t*(b.x-42)+t*t*t*b.x,y=u*u*u*s.y+3*u*t*v+t*t*t*e.y;if(category.some(r=>x>r.x&&x<r.x+r.w&&y>r.y&&y<r.y+r.h))hits++;}if(hits<best){best=hits;chosen=v;}if(!hits)break;}const c1={x:a.x+42,y:chosen},c2={x:b.x-42,y:chosen};const points=Array.from({length:65},(_,i)=>{const t=i/64,u=1-t;return{x:u*u*u*s.x+3*u*u*t*c1.x+3*u*t*t*c2.x+t*t*t*e.x,y:u*u*u*s.y+3*u*u*t*c1.y+3*u*t*t*c2.y+t*t*t*e.y};});return{d:`M${s.x},${s.y}C${c1.x},${c1.y} ${c2.x},${c2.y} ${e.x},${e.y}`,points};}
 // Two horizontal lanes in empty level gaps, joined by a verified free vertical rail.
 let mixed=hash(key);mixed=Math.imul(mixed^(mixed>>>16),0x45d9f3b);mixed=Math.imul(mixed^(mixed>>>16),0x45d9f3b);mixed=(mixed^(mixed>>>16))>>>0;const jitter=(mixed%4093)/4093*12;const offset=180+(mixed%4093)/4093*154,ay=a.y-offset,by=b.y-offset;
 const xs=new Set([a.x,b.x,(a.x+b.x)/2]);for(const r of obstacles){xs.add(r.x-16-jitter);xs.add(r.x+r.w+16+jitter);}const allX=obstacles.flatMap(r=>[r.x,r.x+r.w]);xs.add(Math.min(a.x,b.x,...allX)-80);xs.add(Math.max(a.x,b.x,...allX)+80);
 let best=null;for(const x of xs){const p=[start,{x:a.x,y:ay},{x,y:ay},{x,y:by},{x:b.x,y:by},end].filter((p,i,ps)=>i===0||p.x!==ps[i-1].x||p.y!==ps[i-1].y);if(polylineHits(p,obstacles).length)continue;const length=p.slice(1).reduce((s,b,i)=>s+Math.hypot(b.x-p[i].x,b.y-p[i].y),0),score=length+p.length*20;if(!best||score<best.score)best={points:p,score};}
 if(!best){const points=gridPath(start,end,obstacles);if(points)best={points,score:0};}
 if(!best)throw Error('No unobstructed routing lane for '+key+'; ports: '+obstacles.filter(r=>segmentHits(start,start,r)||segmentHits(end,end,r)).map(r=>r.key+':'+r.kind).join(','));
 return{d:rounded(best.points),points:best.points};
}
g.TreeRouting={route,gridPath,lowBendPath,segmentHits,polylineHits,rounded};
})(typeof window==='undefined'?globalThis:window);
/* Box ports: route outside complete card obstacles, then connect to boundary ports. */
(function(g){
function boxRoute(a,b,obstacles,knowledge=false){
 const sameColumn=Math.abs(a.x-b.x)<Math.min(a.width,b.width)/2,direction=b.x>=a.x?1:-1,source=knowledge?{x:a.x+(sameColumn?1:direction)*a.width/2,y:a.y+a.height/2}:{x:a.x,y:a.y+a.height},target=knowledge?{x:b.x+(sameColumn?1:-direction)*b.width/2,y:b.y+b.height/2}:{x:b.x,y:b.y},start=knowledge?{x:source.x+(sameColumn?1:direction)*3,y:source.y}:{x:source.x,y:source.y+3},end=knowledge?{x:target.x+(sameColumn?1:-direction)*3,y:target.y}:{x:target.x,y:target.y-3},rects=obstacles.map(r=>({...r,x:r.x-2,y:r.y-2,w:r.w+4,h:r.h+4}));
 const lane=knowledge?Math.min(start.y,end.y)-22:(start.y+end.y)/2,candidates=knowledge?[[start,{x:start.x,y:end.y},end],[start,{x:end.x,y:start.y},end],[start,{x:start.x,y:lane},{x:end.x,y:lane},end]]:[[start,{x:start.x,y:lane},{x:end.x,y:lane},end]];
 const outerLeft=Math.min(...rects.map(r=>r.x))-12,outerRight=Math.max(...rects.map(r=>r.x+r.w))+12;
 for(const rail of [outerLeft,outerRight])candidates.push([start,{x:start.x,y:start.y+(knowledge?-8:8)},{x:rail,y:start.y+(knowledge?-8:8)},{x:rail,y:end.y-8},{x:end.x,y:end.y-8},end]);
 let middle=candidates.find(points=>!TreeRouting.polylineHits(points,rects).length);
 if(!middle)middle=TreeRouting.gridPath(start,end,rects);
 if(!middle)throw Error('No free card boundary route: '+a.key+' → '+b.key);
 const points=[source,...middle,target].filter((p,i,all)=>!i||p.x!==all[i-1].x||p.y!==all[i-1].y);return{points,d:TreeRouting.rounded(points,2)};
}
g.AtlasRouting={boxRoute,route:(a,b,index,obstacles)=>boxRoute(a,b,obstacles,true).d};
})(globalThis);

/* Composition pass: shared orthogonal category trunks, independent of knowledge lanes. */
(function(g){
const clean=ps=>ps.filter((p,i)=>!i||p.x!==ps[i-1].x||p.y!==ps[i-1].y).filter((p,i,all)=>!i||i===all.length-1||!((all[i-1].x===p.x&&p.x===all[i+1].x)||(all[i-1].y===p.y&&p.y===all[i+1].y)));
const path=ps=>ps.map((p,i)=>(i?'L':'M')+p.x+','+p.y).join('');
function sharedSegments(branches,byKey){const axes=new Map();for(const e of branches)for(let i=1;i<e.points.length;i++){const a=e.points[i-1],b=e.points[i],vertical=a.x===b.x,key=e.parent+'|'+(vertical?'v':'h')+'|'+(vertical?a.x:a.y);if(!axes.has(key))axes.set(key,[]);axes.get(key).push({parent:e.parent,child:e.child,vertical,fixed:vertical?a.x:a.y,lo:vertical?Math.min(a.y,b.y):Math.min(a.x,b.x),hi:vertical?Math.max(a.y,b.y):Math.max(a.x,b.x)});}
 const result=[];for(const rows of axes.values()){const r0=rows[0],junctions=[...axes.values()].filter(a=>a[0].parent===r0.parent&&a[0].vertical!==r0.vertical).flatMap(a=>a.filter(r=>r.lo<=r0.fixed&&r.hi>=r0.fixed).map(r=>r.fixed));const stops=[...new Set([...rows.flatMap(r=>[r.lo,r.hi]),...junctions.filter(v=>rows.some(r=>v>=r.lo&&v<=r.hi))])].sort((a,b)=>a-b);for(let i=1;i<stops.length;i++){const lo=stops[i-1],hi=stops[i],members=rows.filter(r=>r.lo<=lo&&r.hi>=hi);if(!members.length||hi-lo<.001)continue;const r=members[0],points=r.vertical?[{x:r.fixed,y:lo},{x:r.fixed,y:hi}]:[{x:lo,y:r.fixed},{x:hi,y:r.fixed}];result.push({parent:r.parent,children:[...new Set(members.map(r=>r.child))],depth:byKey.get(r.parent).depth,points,d:path(points)});}}return result;
}
function hierarchy(branches,byKey,obstacles,buses,trays=[],tokens){
 const groups=new Map();for(const e of branches){if(!groups.has(e.parent))groups.set(e.parent,[]);groups.get(e.parent).push(e);}
 for(const t of trays)if(!groups.has(t.parent))groups.set(t.parent,[]);
 const all=[];
 for(const [parent,edges]of groups){
  const a=byKey.get(parent),source={x:a.x,y:a.y+a.height},busY=source.y+tokens.parentToBus;
  for(const e of edges){const b=byKey.get(e.child);e.points=clean([source,{x:a.x,y:busY},{x:b.x,y:busY},{x:b.x,y:b.y}]);e.d=path(e.points);all.push(e);}
  const t=trays.find(t=>t.parent===parent);if(t){const target={x:t.x+t.width/2,y:t.y},e={parent,child:t.topics[0],topics:t.topics,points:clean([source,{x:a.x,y:busY},{x:target.x,y:busY},target])};e.d=path(e.points);all.push(e);}
 }
 const result=sharedSegments(all,byKey);
 for(const segment of result)segment.children=[...new Set(segment.children.flatMap(k=>all.find(e=>e.parent===segment.parent&&e.child===k)?.topics||[k]))];
 return result;
}
g.AtlasRouting.hierarchy=hierarchy;g.AtlasRouting.sharedSegments=sharedSegments;
})(globalThis);

/* Personal packing places an owner's tray above its child band. Bypass that
   related tray at a measured flank; all other rails retain V6.6 ports. */
(function(g){
 const clean=ps=>ps.filter((p,i)=>!i||p.x!==ps[i-1].x||p.y!==ps[i-1].y);
 const path=ps=>ps.map((p,i)=>(i?'L':'M')+p.x+','+p.y).join('');
 g.AtlasRouting.hierarchy=function(branches,byKey,obstacles,buses,trays=[],tokens){
  const groups=new Map();for(const e of branches){if(!groups.has(e.parent))groups.set(e.parent,[]);groups.get(e.parent).push(e);}
  for(const t of trays)if(!groups.has(t.parent))groups.set(t.parent,[]);
  const all=[];
  for(const [parent,edges]of groups){
   const a=byKey.get(parent),source={x:a.x,y:a.y+a.height},stemY=source.y+tokens.parentToBus,t=trays.find(t=>t.parent===parent);
   for(const e of edges){const b=byKey.get(e.child);let points;
    if(t){const flank=t.x+t.width+10,rail=t.y+t.height+12;points=[source,{x:a.x,y:stemY},{x:flank,y:stemY},{x:flank,y:rail},{x:b.x,y:rail},{x:b.x,y:b.y}];}
    else points=[source,{x:a.x,y:stemY},{x:b.x,y:stemY},{x:b.x,y:b.y}];
    e.points=clean(points);e.d=path(e.points);all.push(e);
   }
   if(t){const target={x:t.x+t.width/2,y:t.y},e={parent,child:t.topics[0],topics:t.topics,points:clean([source,{x:a.x,y:stemY},{x:target.x,y:stemY},target])};e.d=path(e.points);all.push(e);}
  }
  const segments=g.AtlasRouting.sharedSegments(all,byKey);
  for(const s of segments)s.children=[...new Set(s.children.flatMap(k=>all.find(e=>e.parent===s.parent&&e.child===k)?.topics||[k]))];
  return segments;
 };
})(globalThis);
