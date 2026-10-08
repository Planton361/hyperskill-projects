/* Entry adapter only. The parent shell is the sole main-view/history owner. */
(() => {
 'use strict';
 const script=document.currentScript.src,shellURL=new URL('../../index.html',script);
 const embedded=window.self!==window.top&&window.parent.AtlasShell?.isViewFrame(window);
 if(!embedded){
  const source=new URL(location.href),q=source.searchParams;
  let view=source.pathname.includes('knowledge-atlas-v6-skill-tree/')?'skill-tree':'atlas';
  if(source.pathname.endsWith('/global.html'))view='atlas';
  shellURL.searchParams.set('view',view);
  for(const name of ['scope','id','course','project','stage','key'])if(q.has(name))shellURL.searchParams.set(name,q.get(name));
  location.replace(shellURL.href);
  return;
 }
 document.documentElement.dataset.atlasEmbedded='true';
 window.AtlasViewHost=Object.freeze({ownsFilters:true,scopeChanged:(nav,previous,mode)=>window.parent.AtlasShell.scopeChanged(nav,previous,mode)});
 // Contextual exact identities are routed by the shell in the current tab.
 document.addEventListener('click',event=>{
  const link=event.target.closest('a[href]');if(!link)return;
  const target=new URL(link.href);
  if(target.origin!==location.origin||!target.pathname.endsWith('/global.html'))return;
  event.preventDefault();window.parent.AtlasShell.showGlobal(target.searchParams.get('key'));
 });
 // Remove the Skill Tree's general-switching Inspector link while preserving
 // every contextual Show in Global action and all Inspector data.
 document.addEventListener('DOMContentLoaded',()=>{
  const fit=document.querySelector('#fit-subtree');if(fit)fit.textContent='Fit subtree';
  const toggle=document.querySelector('#inspector-toggle');if(toggle?.closest('.map-controls'))document.querySelector('#canvas').append(toggle);
  // The personal renderer predates drawer chrome. Adapt its existing aside,
  // selection observer and clear handler without touching rendering or data.
  if(location.pathname.includes('knowledge-atlas-v6-skill-tree/')){
   const main=document.querySelector('main'),aside=document.querySelector('aside'),top=aside.querySelector('.inspector-top'),clear=document.querySelector('#clear');
   let open=false,pinned=false,lastKey=null;
   aside.id='inspector-drawer';clear.textContent='Clear';
   const tools=document.createElement('div');tools.className='inspector-tools';
   const pin=document.createElement('button');pin.id='inspector-pin';pin.textContent='Pin';pin.setAttribute('aria-label','Pin Inspector beside map');
   const close=document.createElement('button');close.id='inspector-close';close.textContent='×';close.setAttribute('aria-label','Close Inspector');
   const show=document.createElement('button');show.id='inspector-toggle';show.textContent='Inspector';show.setAttribute('aria-controls','inspector-drawer');document.querySelector('#canvas').append(show);
   tools.append(pin,clear,close);top.append(tools);
   const set=(value)=>{open=value;aside.hidden=!open;main.dataset.inspectorOpen=String(open);main.dataset.inspectorPinned=String(pinned);pin.textContent=pinned?'Unpin':'Pin';pin.setAttribute('aria-pressed',String(pinned));show.setAttribute('aria-expanded',String(open));};
   show.onclick=()=>set(true);close.onclick=()=>{set(false);show.focus({preventScroll:true});};pin.onclick=()=>{pinned=!pinned;set(true);};aside.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();close.click();}});
   document.addEventListener('click',e=>{if(e.target.closest('.node,[data-select]'))set(true);},true);
   document.addEventListener('keydown',e=>{if(e.target.closest('.node')&&['Enter',' '].includes(e.key))set(true);},true);
   new MutationObserver(()=>{const key=window.AtlasV6?.state().selected;if(key&&key!==lastKey)set(true);lastKey=key;}).observe(aside,{attributes:true,attributeFilter:['class'],childList:true,subtree:true});set(false);
  }
  // Keep the overview's secondary branch navigation accessible in Inspector.
  const guide=document.querySelector('#overview-guide');
  if(guide)new MutationObserver(()=>{
   const source=guide.querySelector('.guide-branches'),aside=document.querySelector('aside');if(!source||!aside||aside.querySelector('.root-context'))return;
   const details=document.createElement('details');details.className='root-context';const title=document.createElement('summary');title.textContent='Global branch shortcuts';details.append(title);
   const copy=source.cloneNode(true);for(const [i,b] of [...copy.querySelectorAll('button')].entries())b.onclick=()=>source.querySelectorAll('button')[i].click();details.append(copy);aside.append(details);
  }).observe(guide,{childList:true});
 });
 const prune=()=>document.querySelectorAll('a[href="global.html"]').forEach(link=>link.closest('p')?.remove());
 new MutationObserver(prune).observe(document.documentElement,{childList:true,subtree:true});
})();
