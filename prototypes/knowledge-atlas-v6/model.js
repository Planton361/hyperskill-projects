(function(g){
function wrap(title){return [title];}
function model(raw){const nodes=new Map();for(const type of ['category','topic'])for(const row of raw[type==='category'?'categories':'topics']){const observations=raw.progress.topics.filter(p=>p.topic_id===row.id);const learned=observations.some(p=>p.is_learned===true)?true:observations.length&&observations.every(p=>p.is_learned===false)?false:null;nodes.set(`${type}:${row.id}`,{...row,key:`${type}:${row.id}`,type,children:[],lines:wrap(row.title,type==='category'?18:25),is_learned:learned,is_verified:learned===true&&observations.some(p=>p.is_verified===true),observations});}let root;for(const n of nodes.values()){if(n.canonical_parent_id==null)root=n;else{const p=nodes.get(`category:${n.canonical_parent_id}`);if(!p)throw Error('Missing canonical parent '+n.key);p.children.push(n);}}for(const n of nodes.values())n.children.sort((a,b)=>(a.type===b.type?0:a.type==='category'?-1:1)||a.id-b.id);const connections=new Map();for(const e of raw.edges.filter(e=>['prerequisite','dependent'].includes(e.type))){const key=e.source+'>'+e.target;if(!connections.has(key))connections.set(key,{key,source:e.source,target:e.target,evidence:[]});connections.get(key).evidence.push(e);}return{raw,nodes,root,connections:[...connections.values()].sort((a,b)=>a.key.localeCompare(b.key))};}
// Coverage is derived from distinct observed requirements, never learning state.
function projectRequirements(m,projectKey,stageId=null){
 return new Set(m.raw.edges.filter(e=>e.type==='project_requires'&&e.source===projectKey&&(stageId==null||e.stage_id===stageId)).map(e=>e.target));
}
function coverageProjection(m,visibleKeys,projectKey,stageId=null){
 const required=projectRequirements(m,projectKey,stageId),byKey=new Map();
 for(const key of required){
  const topic=m.nodes.get(key);if(!topic||topic.type!=='topic')throw Error('Invalid required topic '+key);
  let representative=topic;
  while(representative&&!visibleKeys.has(representative.key))representative=m.nodes.get('category:'+representative.canonical_parent_id);
  if(!representative)throw Error('No visible coverage ancestor for '+key);
  if(!byKey.has(representative.key))byKey.set(representative.key,{kind:representative.type==='topic'?'topic':'rollup',topics:new Set(),count:0});
  const indicator=byKey.get(representative.key);indicator.topics.add(key);indicator.count=indicator.topics.size;
 }
 return{required,byKey,total:required.size};
}

g.AtlasModel={model,projectRequirements,coverageProjection};
})(globalThis);
