/* Personal projection: identities from the composed Catalog, scope from evidence.
   No global coordinates, inference from taxonomy, or persistence. */
(function(g){
'use strict';
const isLeaf=GlobalRegistry.isLeaf;
function model(raw,options={}){
 const global=GlobalRegistry.model(raw),learned=new Set(raw.progress.topics.filter(p=>p.is_learned===true).map(p=>'topic:'+p.topic_id));
 const analytics=raw.projectCompletion?(g.ProgressAnalytics||(typeof require==='function'?require('./progress-analytics.js'):null)).create({catalog:raw,scopes:raw.completionScopes}):null;
 if(analytics){learned.clear();for(const t of raw.topics)if(analytics.topic(t.id).learned===true)learned.add('topic:'+t.id);}
 const verified=new Set(raw.progress.topics.filter(p=>p.is_verified===true).map(p=>'topic:'+p.topic_id));
 for(const key of options.extraLearned||[]){if(global.nodes.get(key)?.type!=='topic')throw Error('Growth needs an existing Topic');learned.add(key);}
 if(analytics){verified.clear();for(const t of raw.topics)if(analytics.topic(t.id).verified===true)verified.add('topic:'+t.id);}
 const contexts=new Set(raw.progress.courses.map(p=>p.course_id));
 const relevant=new Set(raw.courses.filter(c=>contexts.has(c.id)).flatMap(c=>c.topic_ids).map(id=>'topic:'+id));
 const next=new Map();
 for(const n of global.registry.values()){
  // Missing arrays are unknown. Only a directly captured, sourced, nonempty
  // prerequisite list can establish this frontier. Filtered edges cannot.
  if(n.type!=='topic'||learned.has(n.key)||!relevant.has(n.key)||!Array.isArray(n.prerequisites)||!n.prerequisites.length||!n.fact_sources?.prerequisites?.length)continue;
  const required=[...new Set([...n.prerequisites,...(n.explicit_prerequisites||[]).map(p=>p.source),
    ...raw.edges.filter(e=>['prerequisite','dependent'].includes(e.type)&&e.target===n.key).map(e=>Number(e.source.split(':')[1]))])];
  if(required.every(id=>learned.has('topic:'+id)))next.set(n.key,{required:required.map(id=>'topic:'+id),source_ids:n.fact_sources.prerequisites,context_ids:[...contexts],basis:'Complete captured prerequisite list; all required Topics explicitly learned'});
 }
 const fixture=options.fixtureKeys!=null;
 const scope=new Set(fixture?options.fixtureKeys:[...learned,...next.keys()]);
 for(const key of scope)if(!isLeaf(global.nodes.get(key)))throw Error('Scope contains a non-leaf or unknown identity: '+key);
 const keep=new Set([global.root.key,...scope]);
 // Canonical ancestor closure only; secondary memberships stay as Inspector facts.
 for(const key of scope){let n=global.parent(global.nodes.get(key));while(n){keep.add(n.key);n=global.parent(n);}}
 const nodes=new Map();
 for(const key of keep){const n=global.nodes.get(key),leaf=isLeaf(n);nodes.set(key,{...n,children:[],
  title:n===global.root?'My Skill Tree':n.title,displayTitle:n===global.root?'My Skill Tree':n.displayTitle,
  is_learned:leaf&&!fixture?learned.has(key):false,is_verified:leaf&&!fixture?verified.has(key):false,
  is_next:!fixture&&next.has(key),nextEvidence:next.get(key)||null,is_context:!leaf,
  validationOnly:fixture||options.extraLearned?.includes(key)||false});}
 const root=nodes.get(global.root.key),parent=n=>nodes.get(n?.parentKey);
 for(const n of nodes.values())if(n!==root)parent(n).children.push(n);
 for(const n of nodes.values())n.children.sort((a,b)=>a.id-b.id);
 const summarize=n=>{n.children.forEach(summarize);n.leafKeys=isLeaf(n)?[n.key]:n.children.flatMap(c=>c.leafKeys);};summarize(root);
 const registry=new Map([...nodes].filter(([,n])=>n!==root)),structuralChildren=new Map(),membershipLeaves=new Map();
 for(const n of registry.values())for(const p of n.memberships||[])if(nodes.has(p)){if(!structuralChildren.has(p))structuralChildren.set(p,[]);structuralChildren.get(p).push(n);}
 const leaves=key=>{if(membershipLeaves.has(key))return membershipLeaves.get(key);const out=new Set();for(const n of structuralChildren.get(key)||[])if(isLeaf(n))out.add(n.key);else for(const k of leaves(n.key))out.add(k);membershipLeaves.set(key,out);return out;};
 for(const n of registry.values())if(n.type==='category')leaves(n.key);
 const counts={learned:fixture?0:[...scope].filter(k=>learned.has(k)).length,verified:fixture?0:[...scope].filter(k=>verified.has(k)).length,next:fixture?0:next.size,
  leaves:scope.size,categories:[...registry.values()].filter(n=>n.type==='category').length,roots:root.children.length};
 return{analytics,raw:{...raw,counts},source:raw,nodes,registry,root,parent,connections:[],structuralChildren,membershipLeaves,global,scope,next,fixture};
}
g.AtlasModel={model,isLeaf};
})(globalThis);
