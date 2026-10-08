/* Optional. Correctness uses exactly the same painter on the main thread. */
importScripts('tile-paint.js');
let scene,styles;
onmessage=e=>{
 const q=e.data;
 try{
  if(q.type==='init'){scene=q.scene;styles=q.styles;postMessage({type:'ready'});return;}
  const start=performance.now(),t=AtlasTilePaint.tile(scene,styles,q.rank,q.x,q.y,q.size,(w,h)=>new OffscreenCanvas(w,h)),bitmap=t.canvas.transferToImageBitmap();t.canvas.width=t.canvas.height=0;
  postMessage({type:'tile',id:q.id,generation:q.generation,bitmap,ms:performance.now()-start,commands:t.ids.length},[bitmap]);
 }catch(error){postMessage({type:'error',message:String(error)});}
};
