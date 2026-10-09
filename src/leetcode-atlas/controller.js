/* Attach public progress to the existing CPU world; never call its layout builder. */
(function(){
'use strict';
let started=false;
function start(){
 if(started||!window.LeetCodeAtlas)return;started=true;
 const atlas=LeetCodeAtlas,host=document.getElementById('filter-context'),panel=document.createElement('div');panel.id='public-progress-panel';
 const button=document.createElement('button');button.id='refresh-public-progress';button.textContent='Refresh progress';
 const status=document.createElement('span');status.id='public-progress-status';status.setAttribute('role','status');
 const details=document.createElement('details');details.id='public-progress-details';
 const summary=document.createElement('summary');summary.textContent='Details';
 const diagnostics=document.createElement('div');diagnostics.id='public-progress-diagnostics';
 details.append(summary,diagnostics);panel.append(status,button);host.append(panel,details);
 let storage;try{storage=sessionStorage;}catch{storage=null;}
 const reader=MyAtlasReadOnlyProgress.create({ids:new Set(atlas.state().index.problems.keys()),storage});
 let current=null;
 async function refresh(force=false){
  button.disabled=true;status.textContent=current?.value?current.value.document.solved.length+' published · refreshing':'Checking progress…';
  atlas.setPublicProgressStatus(current?.value?'stale':'loading');
  try{
   current=await reader.load({force});if(current.value)atlas.setPublicProgress(current.value);
   atlas.setPublicProgressStatus(current.status);document.body.dataset.publicState=current.status;
   const value=current.value;
   status.textContent=value?value.document.solved.length+' published'+(current.status==='stale'?' · stale':''):'Progress unavailable';
   diagnostics.textContent=value?(current.error?current.error+' ':'')+value.resolved.length+' solved in this catalog · '+value.document.solved.length+' published'+
    (value.unresolved.length?' · '+value.unresolved.length+' unresolved ID(s): '+value.unresolved.map(r=>r.problemId).join(', '):'')+
    ' · Source updated '+value.document.updatedAt+' · Checked '+current.checkedAt+(current.cache?' · cached':''):current.error;
  }finally{button.disabled=false;}
 }
 button.addEventListener('click',()=>refresh(true));
 document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')refresh();});
 window.MyAtlasPublicIntegration={refresh:()=>refresh(true),state:()=>current};refresh();
}
window.addEventListener('atlas-ready',start);start();
})();
