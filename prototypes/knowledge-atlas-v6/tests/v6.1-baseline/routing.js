/* Geometry-only routing. Endpoint IDs and relation evidence are untouched. */
(function(g){
'use strict';
function segmentHits(a,b,r){let lo=0,hi=1;const dx=b.x-a.x,dy=b.y-a.y;for(const [p,q]of [[-dx,a.x-r.x],[dx,r.x+r.w-a.x],[-dy,a.y-r.y],[dy,r.y+r.h-a.y]]){if(Math.abs(p)<1e-9){if(q<0)return false;}else{const t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);if(lo>hi)return false;}}return hi>=0&&lo<=1;}
function polylineHits(points,obstacles){return obstacles.filter(r=>points.slice(1).some((b,i)=>segmentHits(points[i],b,r)));}
function rounded(points,radius=10){let d=`M${points[0].x},${points[0].y}`;for(let i=1;i<points.length-1;i++){const a=points[i-1],b=points[i],c=points[i+1],before=Math.hypot(b.x-a.x,b.y-a.y),after=Math.hypot(c.x-b.x,c.y-b.y);if(!before||!after)continue;const r=Math.min(radius,before/2,after/2),p={x:b.x-(b.x-a.x)/before*r,y:b.y-(b.y-a.y)/before*r},q={x:b.x+(c.x-b.x)/after*r,y:b.y+(c.y-b.y)/after*r};d+=`L${p.x},${p.y}Q${b.x},${b.y} ${q.x},${q.y}`;}const last=points.at(-1);return d+`L${last.x},${last.y}`;}
function gridPath(start,end,obstacles){
 const xs=[...new Set([start.x,end.x,...obstacles.flatMap(r=>[r.x-2,r.x+r.w+2])])].sort((a,b)=>a-b),ys=[...new Set([start.y,end.y,...obstacles.flatMap(r=>[r.y-2,r.y+r.h+2])])].sort((a,b)=>a-b),w=xs.length,h=ys.length,total=w*h;
 const blocked=new Uint8Array(total),horizontal=new Uint8Array(total),vertical=new Uint8Array(total);const lower=(arr,value)=>{let lo=0,hi=arr.length;while(lo<hi){const mid=(lo+hi)>>1;if(arr[mid]<value)lo=mid+1;else hi=mid;}return lo;},upper=(arr,value)=>lower(arr,value+1e-6);
 for(const r of obstacles){const x0=lower(xs,r.x),x1=upper(xs,r.x+r.w),y0=lower(ys,r.y),y1=upper(ys,r.y+r.h);for(let y=y0;y<y1;y++){for(let x=x0;x<x1;x++)blocked[y*w+x]=1;for(let x=Math.max(0,x0-1);x<Math.min(w-1,x1);x++)horizontal[y*w+x]=1;}for(let x=x0;x<x1;x++)for(let y=Math.max(0,y0-1);y<Math.min(h-1,y1);y++)vertical[y*w+x]=1;}
 const source=ys.indexOf(start.y)*w+xs.indexOf(start.x),target=ys.indexOf(end.y)*w+xs.indexOf(end.x),distance=new Float64Array(total).fill(Infinity),previous=new Int32Array(total).fill(-1),heap=[];if(blocked[source]||blocked[target])return null;
 function push(id,score){const item={id,score};let i=heap.length;heap.push(item);while(i>0){const p=(i-1)>>1;if(heap[p].score<=score)break;heap[i]=heap[p];i=p;}heap[i]=item;}
 function pop(){const first=heap[0],last=heap.pop();if(heap.length){let i=0;while(i*2+1<heap.length){let c=i*2+1;if(c+1<heap.length&&heap[c+1].score<heap[c].score)c++;if(heap[c].score>=last.score)break;heap[i]=heap[c];i=c;}heap[i]=last;}return first;}
 const heuristic=id=>Math.abs(xs[id%w]-end.x)+Math.abs(ys[Math.floor(id/w)]-end.y);distance[source]=0;push(source,heuristic(source));const seen=new Uint8Array(total);
 while(heap.length){const {id}=pop();if(seen[id])continue;seen[id]=1;if(id===target)break;const x=id%w,y=Math.floor(id/w);const candidates=[];if(x>0&&!horizontal[id-1])candidates.push(id-1);if(x<w-1&&!horizontal[id])candidates.push(id+1);if(y>0&&!vertical[id-w])candidates.push(id-w);if(y<h-1&&!vertical[id])candidates.push(id+w);for(const next of candidates){if(blocked[next]||seen[next])continue;const cost=Math.abs(xs[next%w]-xs[x])+Math.abs(ys[Math.floor(next/w)]-ys[y]);if(distance[id]+cost<distance[next]){distance[next]=distance[id]+cost;previous[next]=id;push(next,distance[next]+heuristic(next));}}}
 if(!Number.isFinite(distance[target]))return null;const points=[];for(let id=target;id!==-1;id=previous[id])points.push({x:xs[id%w],y:ys[Math.floor(id/w)]});points.reverse();return points.filter((p,i)=>!i||i===points.length-1||!((points[i-1].x===p.x&&p.x===points[i+1].x)||(points[i-1].y===p.y&&p.y===points[i+1].y)));
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
g.TreeRouting={route,gridPath,segmentHits,polylineHits,rounded};
})(typeof window==='undefined'?globalThis:window);
/* Box ports: route outside complete card obstacles, then connect to boundary ports. */
(function(g){
function boxRoute(a,b,obstacles,knowledge=false){
 const source={x:a.x,y:knowledge?a.y:a.y+a.height},target={x:b.x,y:b.y},start={x:source.x,y:source.y+(knowledge?-5:5)},end={x:target.x,y:target.y-5},rects=obstacles.map(r=>({...r,x:r.x-2,y:r.y-2,w:r.w+4,h:r.h+4}));
 const lane=knowledge?Math.min(start.y,end.y)-22:(start.y+end.y)/2,candidates=[[start,{x:start.x,y:lane},{x:end.x,y:lane},end]];
 const outerLeft=Math.min(...rects.map(r=>r.x))-12,outerRight=Math.max(...rects.map(r=>r.x+r.w))+12;
 for(const rail of [outerLeft,outerRight])candidates.push([start,{x:start.x,y:start.y+(knowledge?-8:8)},{x:rail,y:start.y+(knowledge?-8:8)},{x:rail,y:end.y-8},{x:end.x,y:end.y-8},end]);
 let middle=candidates.find(points=>!TreeRouting.polylineHits(points,rects).length);
 if(!middle)middle=TreeRouting.gridPath(start,end,rects);
 if(!middle)throw Error('No free card boundary route: '+a.key+' → '+b.key);
 const points=[source,...middle,target].filter((p,i,all)=>!i||p.x!==all[i-1].x||p.y!==all[i-1].y);return{points,d:TreeRouting.rounded(points,2)};
}
g.AtlasRouting={boxRoute,route:(a,b,index,obstacles)=>boxRoute(a,b,obstacles,true).d};
})(globalThis);
