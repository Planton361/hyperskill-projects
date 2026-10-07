/* Semantics only. No coordinate or layout fields are persisted in projections. */
(function(g){
'use strict';
const sorted=xs=>[...new Set(xs)].sort((a,b)=>a-b);
function project(scope_type,scope_id,explicit_topic_ids,explicit_category_ids,global_catalog){
 const raw=global_catalog,cats=new Map(raw.categories.map(r=>[r.id,r])),topics=new Map(raw.topics.map(r=>[r.id,r]));
 const tids=sorted(explicit_topic_ids),cids=sorted(explicit_category_ids),closure=new Set(),visiting=new Set();
 const parents=id=>sorted(raw.memberships[id]||[]);
 function up(id){if(visiting.has(id))throw Error('Taxonomy cycle: '+id);if(closure.has(id))return;if(!cats.has(id))throw Error('Unknown Category: '+id);visiting.add(id);parents(id).forEach(up);visiting.delete(id);closure.add(id);}
 cids.forEach(up);for(const id of tids){if(!topics.has(id))throw Error('Unknown Topic: '+id);if(!parents(id).length)throw Error('Topic without taxonomy membership: '+id);parents(id).forEach(up);}
 const category_ids=sorted(closure),context_category_ids=category_ids.filter(id=>!cids.includes(id)),roots=category_ids.filter(id=>!parents(id).length);
 const entities=[...category_ids.map(id=>['category',cats.get(id)]),...tids.map(id=>['topic',topics.get(id)])];
 const semantic_identity=Object.fromEntries(entities.map(([type,r])=>[`${type}:${r.id}`,`${type}:${r.id}`]));
 const hierarchy=entities.flatMap(([type,r])=>parents(r.id).map(p=>({parent:`category:${p}`,child:`${type}:${r.id}`})));
 return {scope_type,scope_id,explicit_topic_ids:tids,explicit_category_ids:cids,context_category_ids,used_global_roots:roots,semantic_identity,hierarchy};
}
function model(p,raw){
 const root={key:`presentation:${p.scope_type}:${p.scope_id}`,type:'context',title:`${p.scope_type[0].toUpperCase()+p.scope_type.slice(1)} ${p.scope_id}`,displayTitle:`${p.scope_type[0].toUpperCase()+p.scope_type.slice(1)} ${p.scope_id}`,presentationOnly:true,children:[]};
 const nodes=new Map([[root.key,root]]),categories=new Set([...p.explicit_category_ids,...p.context_category_ids]),topics=new Set(p.explicit_topic_ids);
 for(const [type,rows,ids] of [['category',raw.categories,categories],['topic',raw.topics,topics]])for(const r of rows)if(ids.has(r.id)){
  const memberships=(raw.memberships[r.id]||[]).map(id=>'category:'+id),canonical=r.accepted_metadata?.canonical_parent_id??r.parent_id,owner=memberships.includes('category:'+canonical)?'category:'+canonical:memberships[0];
  const observations=type==='topic'?raw.progress.topics.filter(o=>o.topic_id===r.id):[];
  const n={...r,key:`${type}:${r.id}`,type,displayTitle:r.title,children:[],memberships,parentKey:owner||root.key,scopeRole:type==='topic'||p.explicit_category_ids.includes(r.id)?'explicit':'context',scopeType:p.scope_type,is_learned:observations.some(o=>o.is_learned===true),is_verified:observations.some(o=>o.is_verified===true)};
  nodes.set(n.key,n);
 }
 for(const n of nodes.values())if(n!==root){const parent=nodes.get(n.parentKey);if(!parent)throw Error('Missing local owner: '+n.key);parent.children.push(n);}
 for(const n of nodes.values())n.children.sort((a,b)=>a.id-b.id);
 const isLeaf=n=>n?.type==='topic';
 function summarize(n){n.children.forEach(summarize);n.leafKeys=isLeaf(n)?[n.key]:n.children.flatMap(c=>c.leafKeys);}
 summarize(root);
 // Distinct structural membership coverage includes secondary owners without
 // creating duplicate Topic rows or adding scope membership.
 for(const n of nodes.values())n.taxonomyTopicKeys=[];
 for(const id of p.explicit_topic_ids){const key='topic:'+id,seen=new Set();function visit(k){if(seen.has(k))return;seen.add(k);const n=nodes.get(k);if(!n)return;n.taxonomyTopicKeys.push(key);n.memberships?.forEach(visit);}nodes.get(key).memberships.forEach(visit);}
 root.taxonomyTopicKeys=p.explicit_topic_ids.map(id=>'topic:'+id);
 return {root,nodes,registry:new Map([...nodes].filter(([k])=>k!==root.key)),parent:n=>nodes.get(n?.parentKey),projection:p,raw};
}
function globalTarget(p,key){if(!Object.hasOwn(p.semantic_identity,key))throw Error('Not a semantic scope entity: '+key);return p.semantic_identity[key];}
g.ScopeProjection={project,model,globalTarget};
g.AtlasModel={isLeaf:n=>n?.type==='topic'};
g.ScopePyramid=(type,id,tids,cids,catalog,measure)=>{const projection=project(type,id,tids,cids,catalog),m=model(projection,catalog);return {projection,m,L:g.AtlasLayout.build(m,measure)};};
})(globalThis);
