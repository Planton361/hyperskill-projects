const assert=require('node:assert/strict'),fs=require('fs'),C=require('../atlas.js'),UX=require('../ux.js'),L=require('../labels.js');
const measure=t=>t.length*7;
for(const text of ['Fundamentals of data analysis and business analytics','Basic literals: numbers, strings and characters','A'.repeat(100)]){
 const a=L.wrap(text,measure,180,5),b=L.wrap(text,measure,180,5);assert.deepEqual(a,b);assert(a.lines.every(t=>measure(t)<=180));assert(a.lines.length<=5);
}
assert(L.wrap('one two three four five six seven eight',measure,50,2).truncated);
const raw=JSON.parse(fs.readFileSync(__dirname+'/../generated/catalog.json')),geo=JSON.parse(fs.readFileSync(__dirname+'/../generated/global-geometry.json')),m=C.index(raw,geo),before=JSON.stringify(geo),p=UX.projection(m,'my',8);
const regions=UX.regions(m,p,'my');assert.equal(regions.length,5);assert.deepEqual(regions.map(g=>g.node.x),regions.map(g=>g.node.x).sort((a,b)=>a-b));assert.deepEqual(UX.stats(m,p,'category:73'),{topics:69,learned:26,verified:11});
assert.equal(regions.reduce((s,g)=>s+g.count,0),89);assert.equal(JSON.stringify(geo),before);console.log('PASS deterministic wrapping, collision helper, real branch metrics and spatial region order');
