const assert=require('node:assert/strict');
function collisionChecks(layout){
 // Bucketed broad phase, including hierarchy segments; no all-pairs matrix.
 const size=240,buckets=new Map(),boxkeys=p=>{const keys=[];for(let x=Math.floor(p.x/size);x<=Math.floor((p.x+p.w)/size);x++)for(let y=Math.floor(p.y/size);y<=Math.floor((p.y+p.h)/size);y++)keys.push(x+','+y);return keys;};
 let pairs=0,segments=0;const overlap=(a,b)=>a.x<b.x+b.w-.001&&a.x+a.w>b.x+.001&&a.y<b.y+b.h-.001&&a.y+a.h>b.y+.001;
 for(const p of layout.positions.values()){
  const candidates=new Set(boxkeys(p).flatMap(k=>buckets.get(k)||[]));for(const q of candidates){pairs++;assert(!overlap(p,q),'overlap '+p.key+' / '+q.key);}
  for(const k of boxkeys(p)){if(!buckets.has(k))buckets.set(k,[]);buckets.get(k).push(p);}
 }
 for(const r of layout.routes)for(let i=1;i<r.points.length;i++){
  const [a,b]=[r.points[i-1],r.points[i]],rect={x:Math.min(a[0],b[0]),y:Math.min(a[1],b[1]),w:Math.abs(a[0]-b[0]),h:Math.abs(a[1]-b[1])};assert(rect.w===0||rect.h===0,'non-orthogonal route');
  const candidates=new Set(boxkeys(rect).flatMap(k=>buckets.get(k)||[]));for(const p of candidates)if(p.key!==r.parent&&p.key!==r.child){segments++;const crosses=rect.w===0?rect.x>p.x+.001&&rect.x<p.x+p.w-.001&&rect.y<p.y+p.h-.001&&rect.y+rect.h>p.y+.001:rect.y>p.y+.001&&rect.y<p.y+p.h-.001&&rect.x<p.x+p.w-.001&&rect.x+rect.w>p.x+.001;assert(!crosses,'route '+r.parent+' → '+r.child+' crosses '+p.key);}
 }
 return {candidatePairs:pairs,segmentCandidates:segments};
}
module.exports=collisionChecks;
