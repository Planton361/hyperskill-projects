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
const api={wrap,overlaps};if(typeof module!=='undefined')module.exports=api;else g.PyramidLabels=api;
})(globalThis);
