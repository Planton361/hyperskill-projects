/* Derived presentation state only; deliberately no persisted local checkpoint. */
(function(g){
'use strict';
const A=typeof module!=='undefined'?require('./adaptive.cjs'):g.AdaptiveCore;
const C=typeof module!=='undefined'?require('../canonical_runtime/atlas.js'):g.GlobalAtlasCore;
const R=typeof module!=='undefined'?require('./registry.cjs'):g.AtlasRegistry;
function signature(s,collapsed){return JSON.stringify({visible:[...s.visible].sort(),explicit:[...s.explicit].sort(),fixture:s.isFixture,collapsed:[...collapsed].sort()});}
class Views{
 constructor(m,measure){this.m=m;this.measure=measure;this.options={mode:'learned',id:8,stage:null,onlyLearned:false,branch:null};this.scope=A.selection(m,this.options);this.mode='compact';this.local=null;this.collapsed=new Set();this.selected=null;this.cameras={local:{x:0,y:0,k:1},global:{x:0,y:0,k:1}};this.metrics={layoutCalls:0};this.transition=null;}
 get camera(){return this.cameras[this.mode==='compact'?'local':'global'];}
 set camera(c){this.cameras[this.mode==='compact'?'local':'global']=c;}
 confirm(options,mode='compact'){
  if(options.mode!==this.options.mode){this.collapsed.clear();this.selected=null;}
  this.options={...this.options,...options};this.scope=A.selection(this.m,this.options);this.mode=options.mode==='global'?'reference':mode;
  if(this.mode==='compact')this.relayout();return this.scope;
 }
 relayout({animate=false,reducedMotion=false}={}){
  const sig=signature(this.scope,this.collapsed);if(this.local?.signature===sig)return false;
  const before=this.local,oldCamera={...this.cameras.local},old=before?.positions.get(this.selected),anchor=old?{x:old.x*oldCamera.k+oldCamera.x,y:old.y*oldCamera.k+oldCamera.y}:null;
  this.local=A.layout(this.m,this.scope,{collapsed:this.collapsed,measure:this.measure});this.local.signature=sig;this.metrics.layoutCalls++;this.metrics.layoutMs=this.local.durationMs;
  if(before)this.metrics.movement=A.movement(before,this.local);
  const next=this.local.positions.get(this.selected);if(anchor&&next){this.cameras.local={...oldCamera,x:anchor.x-next.x*oldCamera.k,y:anchor.y-next.y*oldCamera.k};this.metrics.anchorDelta=0;}
  this.transition=animate&&before&&!reducedMotion?{before,after:this.local,start:performance.now(),duration:180,oldCamera,newCamera:{...this.cameras.local}}:null;this.metrics.animationMs=this.transition?180:0;
  return true;
 }
 updateSnapshot(raw,{reducedMotion=false}={}){
  this.m=R.replaceSnapshot(this.m,raw);this.scope=A.selection(this.m,this.options);
  // A state-only change never allocates any global slot. Highlight updates need no layout.
  return this.mode==='compact'?this.relayout({animate:true,reducedMotion}):false;
 }
 get positions(){return this.mode==='compact'?this.local?.positions||new Map():this.mode==='mask'?new Map([...this.scope.visible].map(k=>[k,this.m.reference.get(k)])):this.m.reference;}
 get routes(){if(this.mode==='compact')return this.local?.routes||[];if(this.mode==='mask'){const slots=new Set([...this.scope.visible].map(k=>C.slot(k)));return this.m.geometry.hierarchy_routes.filter(r=>slots.has(r.child));}return this.m.geometry.hierarchy_routes;}
 open(key){let n=this.m.nodes.get(key),changed=false;while(n){changed=this.collapsed.delete(n.key)||changed;n=this.m.nodes.get(n.parent);}if(changed)this.relayout();this.selected=key;}
 collapse(key){if(this.m.nodes.get(key)?.kind!=='category')return;this.collapsed.add(key);this.relayout();}
 summarize(){const depth=this.scope.topics.size>1000?0:this.scope.topics.size>=100?1:2;for(const n of this.m.nodes.values())if(n.kind==='category'&&n.depth===depth&&this.scope.visible.has(n.key))this.collapsed.add(n.key);this.relayout();}
}
function interpolate(transition,now){
 const t=Math.max(0,Math.min(1,(now-transition.start)/transition.duration)),blend=t*t*(3-2*t),positions=new Map();
 for(const [k,p]of transition.after.positions){const q=transition.before.positions.get(k);positions.set(k,q?{...p,x:q.x+(p.x-q.x)*blend,y:q.y+(p.y-q.y)*blend,w:q.w+(p.w-q.w)*blend,h:q.h+(p.h-q.h)*blend,opacity:1}:{...p,opacity:t<1?0:1});}
 const camera=Object.fromEntries(['x','y','k'].map(k=>[k,transition.oldCamera[k]+(transition.newCamera[k]-transition.oldCamera[k])*blend]));
 return {positions,camera,t};
}
const api={Views,interpolate,signature};if(typeof module!=='undefined')module.exports=api;else g.AtlasViews=api;
})(globalThis);
