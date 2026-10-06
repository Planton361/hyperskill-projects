/* Deterministic screen-space text only. Never reads or writes layout coordinates. */
(function(g){
'use strict';
function wrap(text,measure,width,maxLines=3){
 const words=String(text).trim().split(/\s+/),lines=[];let line='';
 for(let word of words){
  if(line&&measure(line+' '+word)>width){lines.push(line);line='';}
  while(measure(word)>width&&word.length>1){let cut=1;while(cut<word.length&&measure(word.slice(0,cut+1))<=width)cut++;if(line){lines.push(line);line='';}lines.push(word.slice(0,cut));word=word.slice(cut);}
  line+=(line?' ':'')+word;
 }
 if(line)lines.push(line);
 const truncated=lines.length>maxLines,out=lines.slice(0,maxLines);
 if(truncated){let last=out.at(-1);while(last.length&&measure(last+'…')>width)last=last.slice(0,-1);out[out.length-1]=last+'…';}
 return {lines:out,truncated};
}
function overlaps(a,b,gap=4){return a.x<b.x+b.w+gap&&a.x+a.w+gap>b.x&&a.y<b.y+b.h+gap&&a.y+a.h+gap>b.y;}
// Mandatory overview labels live outside ordinary budgets/collision suppression.
// Inputs/outputs are screen pixels only; original world nodes are never modified.
function topLevel(ctx,{roots,apex,width,height,top=210,bottom=140}){
 const visible=roots.filter(r=>r.anchorX>=0&&r.anchorX<=width&&r.anchorY>=top&&r.anchorY<=height-bottom);
 const boxes=[];ctx.font='700 16px system-ui';
 if(apex.anchorX>=0&&apex.anchorX<=width&&apex.anchorY>=top&&apex.anchorY<=height-bottom){
  boxes.push({...apex,text:'Hyperskill',lines:['Hyperskill'],fontSize:16,
   x:Math.max(8,Math.min(width-178,apex.anchorX-85)),y:Math.max(top,apex.anchorY-40),w:170,h:34,truncated:false});
 }
 ctx.font='600 14px system-ui';
 const rootBoxes=visible.map(r=>{
  const longestWord=Math.max(...r.text.split(/\s+/).map(t=>ctx.measureText(t).width+1));
  const lines=wrap(r.text,t=>ctx.measureText(t).width,Math.max(90,longestWord,Math.min(180,r.sectorWidth-28)),2).lines;
  const w=Math.max(...lines.map(t=>ctx.measureText(t).width))+22,h=48;
  return {...r,lines,fontSize:14,w,h,x:Math.max(8,Math.min(width-w-8,r.anchorX-w/2)),y:Math.max(top,r.anchorY-70),truncated:false};
 }).sort((a,b)=>a.anchorX-b.anchorX||a.key.localeCompare(b.key));
 // Stable left/right sweep moves label boxes only, retaining leader-line anchors.
 for(let i=1;i<rootBoxes.length;i++)rootBoxes[i].x=Math.max(rootBoxes[i].x,rootBoxes[i-1].x+rootBoxes[i-1].w+10);
 for(let i=rootBoxes.length-1;i>=0;i--)rootBoxes[i].x=Math.min(rootBoxes[i].x,i===rootBoxes.length-1?width-rootBoxes[i].w-8:rootBoxes[i+1].x-rootBoxes[i].w-10);
 const rootY=Math.max(top,...rootBoxes.map(b=>b.y),boxes.length?boxes[0].y+boxes[0].h+16:top);
 for(const b of rootBoxes)b.y=Math.min(height-bottom-b.h,rootY);
 return boxes.concat(rootBoxes);
}
function paintTopLevel(ctx,boxes){
 ctx.save();ctx.globalAlpha=1;ctx.textAlign='center';
 for(const b of boxes){
  ctx.strokeStyle=b.color||'#a9c9e3';ctx.lineWidth=1.2;
  ctx.beginPath();ctx.moveTo(b.anchorX,b.anchorY);ctx.lineTo(Math.max(b.x+8,Math.min(b.x+b.w-8,b.anchorX)),b.y+b.h);ctx.stroke();
  ctx.fillStyle=b.key==='presentation:hyperskill'?'#203a53':'#172c43';
  ctx.beginPath();ctx.roundRect(b.x,b.y,b.w,b.h,6);ctx.fill();ctx.stroke();
  ctx.font=(b.fontSize===16?'700 ':'600 ')+b.fontSize+'px system-ui';ctx.fillStyle='#f0f6ff';
  const start=b.y+(b.h-b.lines.length*18)/2+14;
  b.lines.forEach((text,i)=>ctx.fillText(text,b.x+b.w/2,start+i*18));
 }
 ctx.restore();
}
const api={wrap,overlaps,topLevel,paintTopLevel};if(typeof module!=='undefined')module.exports=api;else g.PyramidLabels=api;
})(globalThis);
