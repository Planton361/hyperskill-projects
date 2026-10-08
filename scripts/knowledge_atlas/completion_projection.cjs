/* Public serialization and diff only. Learning is delegated to accepted analytics. */
'use strict';
const fs=require('node:fs');
const {create}=require('../../src/myatlas/knowledge-atlas-v6-skill-tree/progress-analytics.js');
const canonical=v=>JSON.stringify(v,(_k,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])):x);
const sorted=xs=>[...new Set(xs)].sort((a,b)=>a-b);
const pick=s=>({state:s.state,eligible:s.eligible,learned:s.learned,verified:s.verified});
function project({catalog,scopes,completion,source}){
 const a=create({catalog,scopes,completion});
 const topics=catalog.topics.map(t=>({topic_id:t.id,...a.topic(t.id)})).filter(t=>t.learned===true||t.verified===true).sort((a,b)=>a.topic_id-b.topic_id).map(t=>({topic_id:t.topic_id,learned:t.learned,verified:t.verified,source:t.evidenceSource,directly_learned:t.directlyLearned,project_learned:t.projectLearned,evidence_ids:[...t.evidence_ids].sort(),observations:t.learningEvidence.map(e=>({...e})).sort((a,b)=>canonical(a)<canonical(b)?-1:canonical(a)>canonical(b)?1:0)}));
 const direct=new Set(topics.filter(t=>t.directly_learned).map(t=>t.topic_id));
 const projects=completion.projects.map(p=>({...p,requirement_topic_count:p.topic_ids.length,already_directly_learned_topic_ids:p.topic_ids.filter(id=>direct.has(id)),additional_to_direct_topic_ids:p.topic_ids.filter(id=>!direct.has(id))})).sort((a,b)=>a.project_id-b.project_id);
 const coverage={};
 for(const type of ['course','project','stage'])coverage[type+'s']=scopes[type+'s'].map(r=>({id:r.scope_id,...pick(a.scope(type,r.scope_id))})).sort((a,b)=>a.id-b.id);
 coverage.categories=catalog.categories.map(r=>({id:r.id,...pick(a.category(r.id))})).sort((a,b)=>a.id-b.id);
 return {schema:2,portfolio:a.portfolio(),course_completion:completion.course_completion||{schema:1,records:[]},course_project_completion:scopes.courses.map(c=>({course_id:c.scope_id,...a.courseProjects(c.scope_id)})).sort((a,b)=>a.course_id-b.course_id),policy:completion.policy,source,completed_project_ids:projects.map(p=>p.project_id),completed_project_count:projects.length,effective_learned_topic_ids:topics.filter(t=>t.learned===true).map(t=>t.topic_id),direct_learned_topic_ids:sorted(direct),project_learned_topic_ids:sorted(projects.flatMap(p=>p.topic_ids)),verified_topic_ids:topics.filter(t=>t.verified===true).map(t=>t.topic_id),topics,projects,global:pick(a.global()),coverage};
}
function diff(current,previous,scopes,catalog){
 const old=previous||{completed_project_ids:[],effective_learned_topic_ids:[],topics:[],projects:[],coverage:{}};
 const subtract=(a,b)=>a.filter(id=>!b.includes(id));
 const oldTopics=new Map(old.topics.map(t=>[t.topic_id,t])),newTopics=new Map(current.topics.map(t=>[t.topic_id,t]));
 const changed=sorted([...oldTopics.keys(),...newTopics.keys()]).filter(id=>canonical(oldTopics.get(id)||null)!==canonical(newTopics.get(id)||null));
 const projectChanges=sorted([...old.completed_project_ids,...current.completed_project_ids]).filter(id=>canonical(old.projects.find(p=>p.project_id===id)||null)!==canonical(current.projects.find(p=>p.project_id===id)||null));
 const oldPortfolio=old.portfolio?old:project({catalog,scopes,completion:{projects:old.projects,course_completion:old.course_completion},source:{}});
 const oldCourseProjects=new Map((oldPortfolio.course_project_completion||[]).map(c=>[c.course_id,c]));
 const courseProjectChanges=current.course_project_completion.filter(c=>canonical(c)!==canonical(oldCourseProjects.get(c.course_id))).map(c=>c.course_id);
 const courseRecordChanges=sorted([...(old.course_completion?.records||[]),...current.course_completion.records].map(r=>r.course_id)).filter(id=>canonical((old.course_completion?.records||[]).filter(r=>r.course_id===id))!==canonical(current.course_completion.records.filter(r=>r.course_id===id)));
 const impacted={};
 for(const type of ['course','project','stage']){const oldCoverage=new Map((old.coverage[type+'s']||[]).map(r=>[r.id,r]));impacted[type+'s']=scopes[type+'s'].filter(r=>(r.explicit_topic_ids||[]).some(id=>changed.includes(id))||(type==='project'&&projectChanges.includes(r.scope_id))||(previous&&canonical(oldCoverage.get(r.scope_id))!==canonical(current.coverage[type+'s'].find(c=>c.id===r.scope_id)))).map(r=>r.scope_id).sort((a,b)=>a-b);}
 const oldCats=new Map((old.coverage.categories||[]).map(r=>[r.id,r]));
 impacted.courses=sorted([...impacted.courses,...courseProjectChanges,...courseRecordChanges]);
 impacted.categories=current.coverage.categories.filter(r=>canonical(oldCats.get(r.id))!==canonical(r)).map(r=>r.id);
 const gained=subtract(current.effective_learned_topic_ids,old.effective_learned_topic_ids),lost=subtract(old.effective_learned_topic_ids,current.effective_learned_topic_ids);
 return {baseline:previous?'accepted_projection':'no_accepted_projection',semantic_change:!!(canonical(current.portfolio)!==canonical(oldPortfolio.portfolio)||changed.length||projectChanges.length||Object.values(impacted).some(ids=>ids.length)),newly_completed_project_ids:subtract(current.completed_project_ids,old.completed_project_ids),removed_or_revoked_project_ids:subtract(old.completed_project_ids,current.completed_project_ids),newly_learned_topic_ids:gained,no_longer_effectively_learned_topic_ids:lost,already_learned_topic_ids:current.project_learned_topic_ids.filter(id=>old.effective_learned_topic_ids.includes(id)),updated_provenance_topic_ids:changed,changed_project_ids:projectChanges,changed_course_project_completion_ids:courseProjectChanges,changed_course_completion_ids:courseRecordChanges,portfolio:current.portfolio,global:current.global,impacted_scopes:impacted};
}
function run(input){
 const projection=project(input);
 let previous=input.previous;
 if(previous&&previous.schema===1)previous=project({...input,completion:previous,source:{baseline:'legacy_accepted_completion_projection'}});
 if(previous&&previous.schema!==2)throw Error('Unsupported accepted projection schema');
 return {projection,changes:diff(projection,previous,input.scopes,input.catalog)};
}
module.exports={project,diff,run};
if(require.main===module)process.stdout.write(JSON.stringify(run(JSON.parse(fs.readFileSync(0,'utf8'))))+'\n');
