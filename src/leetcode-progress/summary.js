(function(){
'use strict';
let storage;try{storage=sessionStorage;}catch{storage=null;}
const reader=MyAtlasReadOnlyProgress.create({storage}),button=document.getElementById('refresh');
async function refresh(force=false){
 button.disabled=true;
 try{
  const state=await reader.load({force});document.body.dataset.publicState=state.status;
  const value=state.value,records=document.getElementById('records');records.replaceChildren();
  document.getElementById('total').textContent='Confirmed solved count: '+(value?value.document.solved.length:'unknown');
  document.getElementById('status').textContent=value?(state.error?state.error+' ':'')+'Source updated '+value.document.updatedAt+' · Checked '+state.checkedAt+(state.cache?' · cached':''):state.error;
  if(value)for(const row of value.document.solved){const item=document.createElement('li');item.textContent=row.problemId+' · '+row.source;records.append(item);}
 }finally{button.disabled=false;}
}
button.addEventListener('click',()=>refresh(true));document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')refresh();});refresh();
})();
