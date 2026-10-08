/* Identity-only adapter around the unchanged accepted Global application.
   No coordinates copied, no accepted file patched, no persistence. */
(async()=>{
 const frame=document.querySelector('#atlas'),key=new URLSearchParams(location.search).get('key');
 try{
  if(key&&!/^topic:\d+$/.test(key))throw Error('Invalid Topic identity');
  const started=performance.now();
  while(!frame.contentWindow?.AtlasV6){if(performance.now()-started>15000)throw Error('Global Atlas did not initialize');await new Promise(r=>setTimeout(r,30));}
  const api=frame.contentWindow.AtlasV6;
  if(key){if(!api.state().L.byKey.has(key))throw Error('Topic identity has no global position');api.select(key,true);}
  document.querySelector('#status').remove();window.bridgeReady={key,globalKey:key};
 }catch(e){document.querySelector('#status').textContent=e.message;}
})();
