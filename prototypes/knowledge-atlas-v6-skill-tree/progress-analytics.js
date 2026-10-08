/* Pure semantic-ID evidence aggregation. No renderer, I/O, clock or mutations. */
(function(g){
'use strict';
function create({catalog,scopes,progress=catalog.progress,evidence=catalog.evidence,provenance=catalog.provenance,completion=catalog.projectCompletion}){
 const topics=new Set(catalog.topics.map(t=>t.id)),categories=new Map(catalog.categories.map(c=>[c.id,c]));
 const sources=new Map((evidence||[]).map(e=>[e.id,e])),observations=new Map(),children=new Map(),cache=new Map();
 const sourced=row=>(row.evidence_ids||[]).some(id=>sources.has(id)||provenance?.[id]);
 const date=row=>[row.observed_at,row.learned_observed_at,...(row.evidence_ids||[]).map(id=>sources.get(id)?.observed_on)].filter(Boolean).sort().at(-1)||null;
 // Resolve each field independently at its newest accepted evidence. Equal-date
 // conflicting values remain unknown; older true never overrides newer false.
 for(const row of progress.topics||[]){if(!topics.has(row.topic_id)||!sourced(row))continue;
  if(!observations.has(row.topic_id))observations.set(row.topic_id,[]);observations.get(row.topic_id).push(row);
 }
 function state(rows,field){const candidates=rows.filter(r=>typeof r[field]==='boolean');if(!candidates.length)return null;
  const latest=candidates.map(date).sort().at(-1),values=new Set(candidates.filter(r=>date(r)===latest).map(r=>r[field]));return values.size===1?[...values][0]:null;
 }
 for(const [id,parents] of Object.entries(catalog.memberships))for(const parent of parents){if(!categories.has(parent))continue;if(!children.has(parent))children.set(parent,new Set());children.get(parent).add(Number(id));}
 function descendants(id,seen=new Set()){
  if(!categories.has(id))throw Error('Unknown Category ID '+id);if(cache.has(id))return new Set(cache.get(id));if(seen.has(id))throw Error('Category membership cycle');
  const out=new Set(),next=new Set([...seen,id]);for(const child of children.get(id)||[])if(topics.has(child))out.add(child);else if(categories.has(child))for(const t of descendants(child,next))out.add(t);
  cache.set(id,out);return new Set(out);
 }
 const projectEvidence=new Map();
 for(const row of completion?.projects||[]){
  const scope=scopes.projects.find(s=>s.scope_id===row.project_id);
  if(row.status!=="completed"||row.attested_by!=="owner"||!row.observed_at||!row.source)throw Error("Invalid completion projection");
  if(!scope||scope.state==="UNKNOWN")continue;
  if(JSON.stringify([...new Set(scope.explicit_topic_ids)].sort((a,b)=>a-b))!==JSON.stringify(row.topic_ids))throw Error("Stale completion requirements; rescan for review");
  for(const id of row.topic_ids){if(!topics.has(id))throw Error("Unknown completed requirement Topic");if(!projectEvidence.has(id))projectEvidence.set(id,[]);projectEvidence.get(id).push(row);}
 }
 const effective=(id,rows)=>projectEvidence.has(id)||state(rows,"is_learned")===true?true:state(rows,"is_learned");
 function aggregate(ids,{state:scopeState='KNOWN',topicObservations=observations,includeProjects=true}={}){
  if(scopeState==='UNKNOWN'||ids==null)return{state:'UNKNOWN',eligible:null,learned:null,notLearned:null,unknown:null,verified:null,verifiedUnknown:null,remaining:null,lastObserved:null,allLearned:false,allVerified:false};
  const eligibleIds=[...new Set(ids)];for(const id of eligibleIds)if(!topics.has(id))throw Error('Unknown Topic ID '+id);
  let learned=0,notLearned=0,unknown=0,verified=0,verifiedUnknown=0,lastObserved=null;
  for(const id of eligibleIds){const rows=topicObservations.get(id)||[],l=includeProjects?effective(id,rows):state(rows,'is_learned'),v=state(rows,'is_verified');if(l===true)learned++;else if(l===false)notLearned++;else unknown++;if(v===true)verified++;else if(v===null)verifiedUnknown++;
   for(const row of [...rows,...(includeProjects?projectEvidence.get(id)||[]:[])]){const d=date(row);if(d&&(!lastObserved||d>lastObserved))lastObserved=d;}
  }
  const eligible=eligibleIds.length;return{state:eligible?'KNOWN':'KNOWN_EMPTY',eligible,learned,notLearned,unknown,verified,verifiedUnknown,remaining:eligible-learned,lastObserved,allLearned:eligible>0&&learned===eligible,allVerified:eligible>0&&verified===eligible};
 }
 const scopeMaps=Object.fromEntries(['course','project','stage'].map(type=>[type,new Map(scopes[type+'s'].map(s=>[s.scope_id,s]))]));
 function scope(type,id){const row=scopeMaps[type]?.get(id);if(!row)throw Error('Unknown '+type+' ID '+id);return aggregate(row.explicit_topic_ids,{state:row.state});}
 function categoryInScope(id,type,scopeId){const ids=descendants(id),row=scopeMaps[type]?.get(scopeId);if(!row)throw Error('Unknown scope');if(row.state==='UNKNOWN')return aggregate(null);const members=new Set(row.explicit_topic_ids);return aggregate([...ids].filter(t=>members.has(t)));}
 function category(id,courseId=null){return courseId==null?aggregate(descendants(id)):categoryInScope(id,'course',courseId);}
 function topic(id){if(!topics.has(id))throw Error('Unknown Topic ID '+id);const rows=observations.get(id)||[],latest=rows.map(date).sort().at(-1)||null;
  const verificationStatuses=[...new Set(rows.filter(r=>date(r)===latest).map(r=>r.verification_status).filter(Boolean))];
  const projects=projectEvidence.get(id)||[],directlyLearned=state(rows,'is_learned')===true;
  return{directlyLearned,projectLearned:projects.length>0,evidenceSource:directlyLearned?(projects.length?'both':'directly observed learned'):(projects.length?'learned through completed Project':null),learningEvidence:[...rows.map(r=>({source:(r.evidence_ids||[]).join(', '),observed_at:date(r),is_learned:r.is_learned})),...projects.map(r=>({source:r.source,project_id:r.project_id,observed_at:r.observed_at,is_learned:true}))],learned:effective(id,rows),verified:state(rows,'is_verified'),verificationStatuses,evidence_ids:[...new Set(rows.flatMap(r=>r.evidence_ids||[]))],lastObserved:[latest,...projects.map(r=>r.observed_at)].filter(Boolean).sort().at(-1)||null};
 }
 function officialCourseProgress(id){
  const course=scopeMaps.course.get(id);if(!course)throw Error('Unknown Course');
  const rows=(progress.courses||[]).filter(r=>r.course_id===id&&sourced(r)).sort((a,b)=>(date(a)||'').localeCompare(date(b)||'')),snapshot=rows.at(-1);
  const unknown=()=>({...aggregate(null),lastObserved:snapshot?date(snapshot):null});
  if(!snapshot||snapshot.topic_status_coverage!=='complete'||course.state==='UNKNOWN')return unknown();
  const stamp=snapshot.learned_observed_at||date(snapshot),scoped=new Map();
  // A global Topic observation in another Course is knowledge evidence, not a
  // personal snapshot for this Course. Require the complete dated local set.
  for(const id of new Set(course.explicit_topic_ids)){const local=(observations.get(id)||[]).filter(r=>r.course_id===course.scope_id&&date(r)===stamp);if(state(local,'is_learned')===null)return unknown();scoped.set(id,local);}
  const result=aggregate(course.explicit_topic_ids,{topicObservations:scoped,includeProjects:false});
  if(result.eligible!==snapshot.learned_topics_total||result.learned!==snapshot.learned_topics_count)return unknown();
  return result;
 }
 function personalStatus(type,id){if(type==='project'){const p=(completion?.projects||[]).filter(p=>p.project_id===id).sort((a,b)=>a.observed_at.localeCompare(b.observed_at)).at(-1);if(p)return{status:'completed',lastObserved:p.observed_at};}const rows=(progress[type+'s']||[]).filter(r=>r[type+'_id']===id&&sourced(r)).sort((a,b)=>(date(a)||'').localeCompare(date(b)||''));const row=rows.at(-1);return row?{status:row.status||null,lastObserved:date(row)}:null;}
 // Portfolio entities remain independent of Topic knowledge and official snapshots.
 const completedProjectIds=[...new Set((completion?.projects||[]).map(p=>p.project_id))].sort((a,b)=>a-b);
 if(completedProjectIds.some(id=>!scopeMaps.project.has(id)))throw Error('Unknown completed Project ID');
 const courseRecords=completion?.course_completion?.records||[];
 for(const r of courseRecords){if(!scopeMaps.course.has(r.course_id)||typeof r.is_completed!=='boolean'||!['owner','hyperskill'].includes(r.source)||!r.evidence_id||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(r.observed_at)||!Number.isFinite(Date.parse(r.observed_at)))throw Error('Invalid explicit Course completion record');}
 function completionStatus(type,id){
  if(!scopeMaps[type]?.has(id))throw Error('Unknown completion scope');
  if(type==='project'){
   const exports=(completion?.projects||[]).filter(p=>p.project_id===id);
   if(exports.length)return{state:'COMPLETED',completed:true,evidence:exports.map(p=>({source:p.attested_by+' · '+p.source,observed_at:p.observed_at,project_id:id}))};
  }
  const explicit=(progress[type+'s']||[]).filter(r=>r[type+'_id']===id&&sourced(r)&&date(r)&& (typeof r.is_completed==='boolean'||['completed','not_completed'].includes(r.status))).map(r=>({is_completed:typeof r.is_completed==='boolean'?r.is_completed:r.status==='completed',observed_at:date(r),source:(r.evidence_ids||[]).join(', ')}));
  if(type==='course')explicit.push(...courseRecords.filter(r=>r.course_id===id));
  if(!explicit.length)return{state:'NOT_RECORDED',completed:null,evidence:[]};
  const latest=Math.max(...explicit.map(r=>Date.parse(r.observed_at))),values=new Set(explicit.filter(r=>Date.parse(r.observed_at)===latest).map(r=>r.is_completed));
  const completed=values.size===1?[...values][0]:null;
  return{state:completed===true?'COMPLETED':completed===false?'NOT_COMPLETED':'NOT_RECORDED',completed,evidence:explicit.map(r=>({source:r.source,observed_at:r.observed_at,evidence_id:r.evidence_id||null}))};
 }
 function courseProjects(id){
  if(!scopeMaps.course.has(id))throw Error('Unknown Course');
  const inventory=scopes.course_project_associations?.courses.find(c=>c.course_id===id);
  if(!inventory||inventory.complete!==true||inventory.state==='UNKNOWN')return{state:'UNKNOWN',eligible:null,completed:null,completed_project_ids:null};
  const ids=[...new Set(inventory.project_ids)];if(ids.some(id=>!scopeMaps.project.has(id)))throw Error('Unknown associated Project');
  const done=ids.filter(id=>completedProjectIds.includes(id)).sort((a,b)=>a-b);
  return{state:ids.length?'KNOWN':'KNOWN_EMPTY',eligible:ids.length,completed:done.length,completed_project_ids:done,evidence_id:inventory.source_id};
 }
 function portfolio(){
  const statuses=[...scopeMaps.course.keys()].map(id=>({id,...completionStatus('course',id)})),recorded=statuses.filter(s=>s.evidence.length),done=statuses.filter(s=>s.completed===true).map(s=>s.id).sort((a,b)=>a-b);
  return{completed_project_ids:[...completedProjectIds],completed_project_count:completedProjectIds.length,project_catalog_count:scopeMaps.project.size,course_catalog_count:scopeMaps.course.size,course_completion_state:recorded.length?'RECORDED':'NOT_RECORDED',completed_course_count:recorded.length?done.length:null,completed_course_ids:done,recorded_course_ids:recorded.map(s=>s.id).sort((a,b)=>a-b)};
 }
 return{portfolio,courseProjects,completionStatus,aggregate,descendants,category,categoryInScope,topic,officialCourseProgress,scope,scopeMaps,categories,children,newLearnedTopicIds:()=>[...projectEvidence.keys()].filter(id=>state(observations.get(id)||[],'is_learned')!==true).sort((a,b)=>a-b),global:()=>aggregate(topics),personalStatus,courseObserved:id=>(progress.courses||[]).some(r=>r.course_id===id&&sourced(r))};
}
const api={create};if(typeof module!=='undefined')module.exports=api;g.ProgressAnalytics=api;
})(globalThis);
