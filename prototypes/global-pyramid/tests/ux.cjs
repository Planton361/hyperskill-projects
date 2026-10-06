'use strict';
const assert=require('node:assert/strict'),fs=require('fs'),C=require('../atlas.js'),UX=require('../ux.js');
const raw=JSON.parse(fs.readFileSync(__dirname+'/../generated/catalog.json')),geo=JSON.parse(fs.readFileSync(__dirname+'/../generated/global-geometry.json')),m=C.index(raw,geo),before=JSON.stringify(geo);
for(const mode of ['global','my','course','project'])for(const ghost of ['none','ancestors','local']){
 const p=UX.projection(m,mode,mode==='project'?113:8,null,ghost);
 for(const k of new Set([...p.explicit,...p.corridor,...p.ghosts])){const n=m.nodes.get(k),slot=geo.positions.find(p=>p.key===n.slot);assert.deepEqual([n.x,n.y,n.w,n.h],[slot.x,slot.y,slot.w,slot.h]);}
 const bounds=UX.scopeBounds(m,p);if(bounds){const cam=UX.camera(bounds,1024,768);assert(Number.isFinite(cam.k)&&cam.k>0);}
 UX.focusBounds(m,p,'category:73');UX.focusBounds(m,p,'reference:333');
}
const project=UX.projection(m,'project',113,617);assert.equal([...project.explicit].filter(k=>k.startsWith('topic:')).length,12);assert(project.ancestors.size>0);assert([...project.ancestors].every(k=>!project.explicit.has(k)));
assert.equal(UX.projection(m,'course',8).explicit.size,135);assert(UX.projection(m,'my',8,null,'local').ghosts.size>UX.projection(m,'my',8,null,'ancestors').ghosts.size);
assert.equal(UX.scopeBounds(m,UX.projection(m,'project',380)),null);assert(UX.projection(m,'project',380).unknown);
const inspected=UX.projection(m,'my',8,null,'none','reference:333');assert(!inspected.explicit.has('reference:333'));assert(inspected.inspected.has('reference:333'));
const focused=UX.focusBounds(m,project,'category:73'),region=m.nodes.get('category:73').region;assert(focused.w<=region.w);assert(focused.h<=region.h);
raw.courses.push({id:99999,category_ids:[],topic_ids:[333]});const synthetic=UX.projection(m,'course',99999);assert.deepEqual([...synthetic.explicit],['reference:333']);assert(synthetic.ancestors.size>0);assert([...synthetic.ancestors].every(k=>!synthetic.explicit.has(k)));
assert.equal(JSON.stringify(geo),before);console.log('PASS UX projections, scope/branch cameras, ghosts, explicit membership, UNKNOWN, dormant inspection, exact geometry');
