const assert=require('node:assert/strict'),collisions=require('../tests/collisions.cjs');
module.exports=function check(m,s,l){
 const ranks=new Map();let categories=0;
 assert.deepEqual(new Set(l.positions.keys()),new Set([...s.visible].filter(k=>!l.hidden.has(k))));
 for(const [key,p]of l.positions){const n=m.nodes.get(key);assert(!('x' in m.entities.get(key)));assert.notEqual(p,m.reference.get(key));
  if(n.kind==='category'){categories++;if(ranks.has(n.depth))assert.equal(p.y,ranks.get(n.depth),'SAME_DEPTH_SAME_RANK '+key);else ranks.set(n.depth,p.y);assert.equal(p.y,l.bands.get(n.depth).y);}
  if(l.positions.has(n.parent))assert(l.positions.get(n.parent).y<p.y,'PARENT_ABOVE_CHILD '+key);
 }
 const families=[m.roots,...[...m.nodes.values()].filter(n=>n.kind==='category').map(n=>n.children.filter(c=>c.kind==='category'))];
 let siblingPairs=0;
 for(const family of families){const visible=family.filter(n=>l.subtrees.has(n.key));for(let i=1;i<visible.length;i++){const a=l.subtrees.get(visible[i-1].key),b=l.subtrees.get(visible[i].key);assert(a.x+a.w+l.siblingGap<=b.x+1e-9,'NO_SIBLING_SUBTREE_OVERLAP '+a.key+'/'+b.key);assert(l.positions.get(a.key).x<l.positions.get(b.key).x,'ORDER_PRESERVED');siblingPairs++;}}
 const contains=(b,p)=>p.x>=b.x-1e-9&&p.x+p.w<=b.x+b.w+1e-9&&p.y>=b.y-1e-9&&p.y+p.h<=b.y+b.h+1e-9;
 for(const [key,b]of l.subtrees){const p=l.positions.get(key);assert(contains(b,p),'Category region');for(const child of b.children)assert(contains(b,l.subtrees.get(child)),'Subtree containment');if(b.children.length){const first=l.subtrees.get(b.children[0]),last=l.subtrees.get(b.children.at(-1));assert(Math.abs(p.x+p.w/2-(first.x+last.x+last.w)/2)<1e-9,'Parent centered over combined children');}}
 for(const tray of l.groups){assert(contains(l.subtrees.get(tray.parent),tray),'Tray subtree containment');const canonical=m.nodes.get(tray.parent).children.filter(n=>s.topics.has(n.key));assert.deepEqual(tray.cards.map(c=>c.key),canonical.map(n=>n.key));for(const c of tray.cards){const p=l.positions.get(c.key);assert(contains(tray,p),'TOPIC_TRAY_CONTAINMENT '+c.key);assert(contains(l.subtrees.get(tray.parent),p));}}
 for(const route of l.routes)assert.equal(m.nodes.get(route.child).parent,route.parent,'Hierarchy route identity');
 return {categories,ranks:[...ranks].sort((a,b)=>a[0]-b[0]),siblingPairs,...collisions(l),cardOverlaps:0,subtreeOverlaps:0,routeCrossings:0};
};
