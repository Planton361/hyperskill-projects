/* Catalog adapter for the V6.6 scene. References never become Topic entities. */
(function(g){
'use strict';
const isLeaf=n=>n?.type==='topic'||n?.type==='reference';
function model(raw){
 const nodes=new Map(),root={key:'atlas:root',type:'context',title:'Global Atlas',children:[],presentationOnly:true};
 nodes.set(root.key,root);
 for(const [type,rows] of [['category',raw.categories],['topic',raw.topics],['reference',raw.references]]){
  for(const row of rows){
   const accepted=row.accepted_metadata,observations=type==='topic'&&accepted?raw.progress.topics.filter(p=>p.topic_id===row.id):[];
   const learned=observations.some(p=>p.is_learned===true)?true:observations.length&&observations.every(p=>p.is_learned===false)?false:null;
   const parents=raw.memberships[row.id]||[],canonical=accepted?.canonical_parent_id??row.parent_id;
   // A reference has only a presentation owner, chosen from its real memberships.
   // This is not new canonical Topic metadata.
   const owner=parents.includes(canonical)?canonical:parents[0];
   const n={...row,key:`${type}:${row.id}`,type,children:[],parentKey:owner==null?root.key:`category:${owner}`,
    memberships:parents.map(id=>'category:'+id),displayTitle:type==='reference'?`ID ${row.id}`:row.title,
    is_learned:learned,is_verified:learned===true&&observations.some(p=>p.is_verified===true),observations,
    evidence_ids:accepted?.evidence_ids||[]};
   nodes.set(n.key,n);
  }
 }
 const parent=n=>nodes.get(n?.parentKey);
 for(const n of nodes.values())if(n!==root){const p=parent(n);if(!p)throw Error('Missing structural parent: '+n.key);p.children.push(n);}
 // Catalog inventories are canonical numeric-ID order, not display-title order.
 for(const n of nodes.values())n.children.sort((a,b)=>a.id-b.id);
 const registry=new Map([...nodes].filter(([,n])=>n!==root));
 function summarize(n,seen=new Set()){
  if(seen.has(n.key))throw Error('Hierarchy cycle');seen.add(n.key);
  n.children.forEach(c=>summarize(c,new Set(seen)));
  n.leafKeys=isLeaf(n)?[n.key]:n.children.flatMap(c=>c.leafKeys);
 }
 summarize(root);
 // Membership graph counts are distinct semantic leaves, including secondary memberships.
 const structuralChildren=new Map();
 for(const n of registry.values())for(const p of n.memberships){if(!structuralChildren.has(p))structuralChildren.set(p,[]);structuralChildren.get(p).push(n);}
 const membershipLeaves=new Map();
 function leaves(key){if(membershipLeaves.has(key))return membershipLeaves.get(key);const out=new Set();for(const n of structuralChildren.get(key)||[])if(isLeaf(n))out.add(n.key);else for(const k of leaves(n.key))out.add(k);membershipLeaves.set(key,out);return out;}
 for(const n of registry.values())if(n.type==='category')leaves(n.key);
 return{raw,nodes,registry,root,parent,connections:[],structuralChildren,membershipLeaves};
}
g.GlobalRegistry={model,isLeaf};
})(globalThis);
