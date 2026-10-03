/* Semantic topic endpoints stay intact. This index maps their visual LCA routes
   onto frozen hierarchy segments; it never creates geometry or taxonomy edges. */
(function(g){
'use strict';
function create(m,L){
 const chains=new Map(),edgeSegments=new Map(),trayByTopic=new Map(),routes=new Map();
 for(const t of L.trays)for(const topic of t.topics)trayByTopic.set(topic,t.parent);
 function chain(key){
  if(chains.has(key))return chains.get(key);
  const out=[],seen=new Set();let n=m.nodes.get(key);
  while(n){if(seen.has(n.key))throw Error('Canonical taxonomy cycle: '+key);seen.add(n.key);out.push(n.key);n=n.canonical_parent_id==null?null:m.nodes.get('category:'+n.canonical_parent_id);}
  if(!out.length||out.at(-1)!==m.root.key)throw Error('Incomplete canonical chain: '+key);
  chains.set(key,Object.freeze(out));return chains.get(key);
 }
 L.connectorSegments.forEach((segment,index)=>{for(const child of segment.children){const key=segment.parent+'>'+child;if(!edgeSegments.has(key))edgeSegments.set(key,[]);edgeSegments.get(key).push(index);}});
 function route(edge){
  if(routes.has(edge.key))return routes.get(edge.key);
  if(m.nodes.get(edge.source)?.type!=='topic'||m.nodes.get(edge.target)?.type!=='topic')throw Error('Relation endpoints must be topics');
  const sourceAncestors=chain(edge.source),targetAncestors=chain(edge.target),targetSet=new Set(targetAncestors),lca=sourceAncestors.find(k=>targetSet.has(k));
  const path=[...sourceAncestors.slice(0,sourceAncestors.indexOf(lca)+1),...targetAncestors.slice(0,targetAncestors.indexOf(lca)).reverse()];
  const canonicalEdges=path.slice(1).map((b,i)=>{const a=path[i];return 'category:'+m.nodes.get(a).canonical_parent_id===b?{parent:b,child:a}:{parent:a,child:b};});
  const sameTray=trayByTopic.get(edge.source)!=null&&trayByTopic.get(edge.source)===trayByTopic.get(edge.target),segmentIds=new Set();
  if(!sameTray)for(const e of canonicalEdges)for(const id of edgeSegments.get(e.parent+'>'+e.child)||[])segmentIds.add(id);
  const result={key:edge.key,source:edge.source,target:edge.target,sourceAncestors,targetAncestors,lca,path,canonicalEdges,sameTray,segmentIds:[...segmentIds],categories:path.filter(k=>m.nodes.get(k).type==='category'),trays:[...new Set([trayByTopic.get(edge.source),trayByTopic.get(edge.target)].filter(Boolean))]};
  routes.set(edge.key,result);return result;
 }
 function direct(selected){return m.connections.filter(e=>e.source===selected||e.target===selected).map(e=>({...route(e),type:e.target===selected?'prerequisite':'dependent',counterpart:e.target===selected?e.source:e.target}));}
 // Each physical segment is styled once, even when several routes or types use it.
 function project(selected,focusKey=null){
  const directRoutes=direct(selected),focused=directRoutes.find(r=>r.key===focusKey)||null,segments=new Map(),categories=new Map(),endpoints=new Map(),trays=new Map();
  function add(map,key,r){if(!map.has(key))map.set(key,{types:new Set(),relationKeys:new Set(),focusedTypes:new Set()});const item=map.get(key);item.types.add(r.type);item.relationKeys.add(r.key);if(r===focused)item.focusedTypes.add(r.type);}
  for(const r of directRoutes){for(const id of r.segmentIds)add(segments,id,r);for(const key of r.categories)add(categories,key,r);add(endpoints,r.counterpart,r);for(const key of r.trays)add(trays,key,r);}
  return{routes:directRoutes,focused,segments,categories,endpoints,trays};
 }
 return{chain,route,direct,project};
}
g.AtlasRelations={create};
})(typeof window==='undefined'?globalThis:window);
