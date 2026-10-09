/* Cached indexes/coverage: catalog and validated owner evidence, never geometry. */
(function(g){'use strict';
const catalogCache=new WeakMap(),projectionCache=new WeakMap(),presentationCache=new WeakMap();
const PALETTE=Object.freeze({Easy:Object.freeze({tile:'#315f78',accent:'#75bddb'}),Medium:Object.freeze({tile:'#766039',accent:'#dec078'}),Hard:Object.freeze({tile:'#78494f',accent:'#d39293'}),Unknown:Object.freeze({tile:'#414e60',accent:'#93a2b4'})});
function compile(index){
 if(catalogCache.has(index))return catalogCache.get(index);
 const difficulties=new Map(['Easy','Medium','Hard','Unknown'].map(k=>[k,new Set()])),tags=new Map(),primary=new Map([...index.tax.keys()].map(k=>[k,new Set()])),associated=new Map([...index.tax.keys()].map(k=>[k,new Set()])),memberships=new Map();
 for(const p of index.problems.values()){
  difficulties.get(PALETTE[p.difficulty]?p.difficulty:'Unknown').add(p.id);
  for(const tag of p.topicTags){if(!tags.has(tag))tags.set(tag,new Set());tags.get(tag).add(p.id);}
  for(const id of LeetCodeModel.ancestors(index,p.primaryTaxonomyId))primary.get(id).add(p.id);
  const ids=LeetCodeModel.memberships(index,p);memberships.set(p.id,ids);for(const id of ids)associated.get(id).add(p.id);
 }
 const result={index,difficulties,tags,primary,associated,memberships};catalogCache.set(index,result);return result;
}
function summary(ids,solved){let n=0;for(const id of ids)if(solved.has(id))n++;return Object.freeze({total:ids.size,solved:n,percent:ids.size?n/ids.size*100:null});}
function project(compiled,progress){
 let cache=projectionCache.get(compiled);if(!cache){cache=new WeakMap();projectionCache.set(compiled,cache);}if(cache.has(progress))return cache.get(progress);
 const solved=new Set(progress.solvedIds),categories=new Map([...compiled.primary].map(([id,ids])=>[id,Object.freeze({primary:summary(ids,solved),associated:summary(compiled.associated.get(id),solved)})])),tags=new Map([...compiled.tags].map(([tag,ids])=>[tag,summary(ids,solved)]));
 const result={solved,categories,tags,global:summary(new Set(compiled.index.problems.keys()),solved)};cache.set(progress,result);return result;
}
function presentation(L,projection){
 let cache=presentationCache.get(projection);if(!cache){cache=new WeakMap();presentationCache.set(projection,cache);}if(cache.has(L))return cache.get(L);
 const result=new Map(L.regions.map(n=>[n.key,projection.categories.get(n.key)?.primary||summary(new Set(n.data.leafKeys||[]),projection.solved)]));cache.set(L,result);return result;
}
function matches(compiled,{difficulty='all',premium='all',query='',tag=null,category=null}={}){
 let candidates=compiled.index.problems.keys();const sets=[];
 if(difficulty!=='all')sets.push(compiled.difficulties.get(difficulty==='unknown'?'Unknown':difficulty)||new Set());if(tag)sets.push(compiled.tags.get(tag)||new Set());if(category)sets.push(compiled.associated.get(category)||new Set());
 if(sets.length)candidates=sets.reduce((a,b)=>a.size<b.size?a:b);
 const out=new Set();for(const id of candidates)if(sets.every(s=>s.has(id))&&LeetCodeModel.matches(compiled.index.problems.get(id),{premium,query}))out.add(id);return out;
}
const api=Object.freeze({PALETTE,compile,project,presentation,summary,matches});g.LeetCodeVisualState=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
