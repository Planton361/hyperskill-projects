/* Immutable scene paint/index shared by the main-thread fallback and tile worker. */
(function(g){
'use strict';
function boxIntersects(a,b){return a.x0<=b.x1&&a.x1>=b.x0&&a.y0<=b.y1&&a.y1>=b.y0;}
function index(items){
 function build(ids){const b={x0:Infinity,y0:Infinity,x1:-Infinity,y1:-Infinity};for(const i of ids){const r=items[i].bounds;b.x0=Math.min(b.x0,r.x0);b.y0=Math.min(b.y0,r.y0);b.x1=Math.max(b.x1,r.x1);b.y1=Math.max(b.y1,r.y1);}if(ids.length<=12)return{b,ids};const axis=b.x1-b.x0>b.y1-b.y0?'x':'y';ids.sort((i,j)=>(items[i].bounds[axis+'0']+items[i].bounds[axis+'1'])-(items[j].bounds[axis+'0']+items[j].bounds[axis+'1'])||i-j);const half=ids.length>>1;return{b,left:build(ids.slice(0,half)),right:build(ids.slice(half))};}
 return build(items.map((_,i)=>i));
}
function query(tree,b,out=[]){if(!boxIntersects(tree.b,b))return out;if(tree.ids)out.push(...tree.ids);else{query(tree.left,b,out);query(tree.right,b,out);}return out;}
function rounded(ctx,x,y,w,h,r){r=Math.min(r,w/2,h/2);ctx.moveTo(x+r,y);ctx.lineTo(x+w-r,y);ctx.arcTo(x+w,y,x+w,y+r,r);ctx.lineTo(x+w,y+h-r);ctx.arcTo(x+w,y+h,x+w-r,y+h,r);ctx.lineTo(x+r,y+h);ctx.arcTo(x,y+h,x,y+h-r,r);ctx.lineTo(x,y+r);ctx.arcTo(x,y,x+r,y,r);ctx.closePath();}
function paint(ctx,c,styles){const s=styles[c.style];ctx.globalAlpha=s.opacity??1;ctx.fillStyle=s.fill;if(c.kind==='text'){ctx.font=c.font;ctx.textBaseline='alphabetic';ctx.fillText(c.text,c.x,c.y);}else if(c.kind==='rect'){ctx.beginPath();rounded(ctx,c.x,c.y,c.w,c.h,c.r);ctx.fill();}}
function tile(scene,styles,rank,x,y,size,create){
 const r=2**rank,bleed=2,canvas=create(size+2*bleed,size+2*bleed),ctx=canvas.getContext('2d'),wx=scene.bounds.x0+x*size/r,wy=scene.bounds.y0+y*size/r,b={x0:wx-bleed/r,y0:wy-bleed/r,x1:wx+(size+bleed)/r,y1:wy+(size+bleed)/r};
 ctx.setTransform(r,0,0,r,bleed-wx*r,bleed-wy*r);
 const ids=query(scene.tree,b).filter(i=>boxIntersects(scene.commands[i].bounds,b)).sort((a,b)=>a-b);
 for(const i of ids)paint(ctx,scene.commands[i],styles);
 return{canvas,ids,bleed};
}
g.AtlasTilePaint={boxIntersects,index,query,rounded,paint,tile};
})(globalThis);
