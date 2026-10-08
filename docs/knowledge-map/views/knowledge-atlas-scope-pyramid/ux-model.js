/* Read-only navigation and personal overlays. No layout or coordinate rules. */
(function(g){
'use strict';
const number=v=>typeof v==='number'&&Number.isSafeInteger(v)&&v>0?v:typeof v==='string'&&/^[1-9]\d*$/.test(v)&&Number.isSafeInteger(Number(v))?Number(v):null;
function create(index,raw,acceptedCourses,evidence){
 const courses=new Map(index.courses.map(s=>[s.scope_id,s])),projects=new Map(index.projects.map(s=>[s.scope_id,s])),stages=new Map(index.stages.map(s=>[s.scope_id,s]));
 const entities=new Map([...raw.categories.map(r=>['category:'+r.id,r]),...raw.topics.map(r=>['topic:'+r.id,r])]);
 const associations=new Map(),evidenceById=new Map(evidence.map(e=>[e.id,e]));
 if(index.course_project_associations){
  const catalog=index.course_project_associations,sources=new Map(catalog.sources.map(s=>[s.id,s]));
  for(const row of catalog.courses){
   const source=sources.get(row.source_id);
   if(!courses.has(row.course_id)||associations.has(row.course_id)||row.complete!==true||!source||source.course_id!==row.course_id||source.endpoint!=='/api/tracks/'+row.course_id||!Array.isArray(row.project_ids)||row.project_ids.some(id=>typeof id!=='number'||!number(id)||!projects.has(id))||new Set(row.project_ids).size!==row.project_ids.length||row.state!==(row.project_ids.length?'KNOWN':'KNOWN_EMPTY'))throw Error('Invalid typed Course Project inventory');
   associations.set(row.course_id,{state:row.state,project_ids:[...row.project_ids],evidence_ids:[row.source_id],unavailable_project_ids:[],observation:catalog.observation,source});
  }
  if(associations.size!==courses.size)throw Error('Incomplete typed Course Project inventory');
 }
 for(const row of acceptedCourses){
  // The accepted normalized Course contract explicitly records the complete
  // captured projects field. Membership is never derived from Topic overlap.
  const sources=(row.evidence_ids||[]).map(id=>evidenceById.get(id)).filter(e=>e?.confidence==='explicit'&&e.fields?.includes('projects'));
  if(!courses.has(row.id)||!sources.length||!Array.isArray(row.project_ids))continue;
  if(row.project_ids.some(id=>!number(id))||new Set(row.project_ids).size!==row.project_ids.length)throw Error('Invalid accepted Course Project IDs');
  if(associations.has(row.id)){if(JSON.stringify([...row.project_ids].sort((a,b)=>a-b))!==JSON.stringify([...associations.get(row.id).project_ids].sort((a,b)=>a-b)))throw Error('Historical Course Project association conflict');continue;}
  associations.set(row.id,{state:'KNOWN',project_ids:[...row.project_ids],evidence_ids:sources.map(e=>e.id),unavailable_project_ids:row.project_ids.filter(id=>!projects.has(id))});
 }
 const analytics=(g.ProgressAnalytics||(typeof require==='function'?require('../knowledge-atlas-v6-skill-tree/progress-analytics.js'):null)).create({catalog:raw,scopes:index});
 const topic=id=>analytics.topic(id);
 const ancestry=new Map();
 function ancestors(id){if(ancestry.has(id))return ancestry.get(id);const result=new Set(),pending=[...(raw.memberships[id]||[])];while(pending.length){const p=pending.pop();if(result.has(p))continue;result.add(p);pending.push(...(raw.memberships[p]||[]));}ancestry.set(id,result);return result;}
 const categoryCache=new Map();
 function categoryProgress(courseId){
  if(!courses.has(courseId))return new Map();if(categoryCache.has(courseId))return categoryCache.get(courseId);
  const result=new Map();for(const row of raw.categories){const p=analytics.categoryInScope(row.id,'course',courseId);if(!p.eligible)continue;
   result.set(row.id,{eligible_ids:new Set([...analytics.descendants(row.id)].filter(id=>courses.get(courseId).explicit_topic_ids.includes(id))),eligible_count:p.eligible,learned:p.learned,verified:p.verified,unknown_learned:p.unknown,unknown_verified:p.verifiedUnknown,fully_learned:p.allLearned,fully_verified:p.allVerified});
  }
  categoryCache.set(courseId,result);return result;
 }
 const association=id=>associations.get(id)||{state:'UNKNOWN',project_ids:null,evidence_ids:[],unavailable_project_ids:[]};
 function normalize(value){
  const section='courses';let course_id=number(value.course_id),project_id=number(value.project_id),stage_id=number(value.stage_id);
  if(!courses.has(course_id))course_id=null;
  if(!projects.has(project_id))project_id=null;
  if(course_id&&(association(course_id).state!=='KNOWN'||!association(course_id).project_ids.includes(project_id)))project_id=null;
  if(!project_id||stages.get(stage_id)?.project_id!==project_id)stage_id=null;
  return{section,course_id,project_id,stage_id};
 }
 function current(state){return state.stage_id?stages.get(state.stage_id):state.project_id?projects.get(state.project_id):state.course_id?courses.get(state.course_id):null;}
 function parse(search){
  const q=new URLSearchParams(search),kind=q.get('scope'),id=number(q.get('id')),sid=number(q.get('stage'))||(kind==='stage'?id:null),pid=number(q.get('project'))||(kind==='project'?id:stages.get(sid)?.project_id),cid=number(q.get('course'))||(kind==='course'?id:null);
  return normalize({section:q.get('section')||(cid?'courses':pid||sid?'projects':'courses'),course_id:cid,project_id:pid,stage_id:sid});
 }
 function url(state){const q=new URLSearchParams({section:state.section}),s=current(state);for(const key of ['course','project','stage'])if(state[key+'_id'])q.set(key,String(state[key+'_id']));if(s){q.set('scope',s.scope_type);q.set('id',String(s.scope_id));}return'?'+q;}
 function choose(state,kind,id){const next={...state};if(kind==='course'){next.course_id=number(id);}else if(kind==='project'){next.project_id=number(id);next.stage_id=null;}else if(kind==='stage')next.stage_id=number(id);return normalize(next);}
 const stageChoices=projectId=>[...stages.values()].filter(s=>s.project_id===projectId).sort((a,b)=>a.order-b.order||a.scope_id-b.scope_id);
 const projectChoices=state=>!state.course_id?[...projects.values()]:association(state.course_id).state==='KNOWN'?association(state.course_id).project_ids.map(id=>projects.get(id)).filter(Boolean):[];
 return{analytics,courses,projects,stages,entities,associations,association,topic,ancestors,categoryProgress,normalize,current,parse,url,choose,stageChoices,projectChoices};
}
g.ScopeUXModel={create,number};if(typeof module!=='undefined')module.exports=g.ScopeUXModel;
})(globalThis);
