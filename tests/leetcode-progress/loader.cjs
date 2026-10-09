const {test}=require('node:test'),assert=require('node:assert/strict'),R=require('../../src/leetcode-progress/loader.js');
const now=Date.parse('2026-10-09T12:00:00.000Z'),ids=new Set(['lc:problem:p0001','lc:problem:eval-00002']);
const row={problemId:'lc:problem:p0001',source:'manual-owner-attestation'};
const doc=(solved=[row])=>({schemaVersion:1,updatedAt:'2026-10-09T01:29:07.735Z',solved});
const response=value=>new Response(JSON.stringify(value),{headers:{'content-type':'application/json'}});
test('strict public schema, exact identities, duplicate elimination and unresolved classification',()=>{
 const v=R.validate(doc([row,row,{...row,problemId:'lc:problem:p9999'}]),ids,now);
 assert.equal(v.document.solved.length,2);assert.equal(v.duplicates,1);assert.deepEqual(v.resolved,[row]);assert.equal(v.unresolved[0].problemId,'lc:problem:p9999');
 for(const value of [{...doc(),token:'forbidden'}, {...doc(),schemaVersion:2}, {...doc(),updatedAt:'2026-02-30T12:00:00.000Z'},
  {...doc(),updatedAt:'2030-01-01T00:00:00.000Z'},doc([{...row,problemId:'1'}]),doc([{...row,code:'forbidden'}]),
  doc([{...row,source:'invented'}]),doc([row,{...row,source:'accepted-dom-owner-confirmed'}])])assert.throws(()=>R.validate(value,ids,now));
});
test('anonymous GET, coalesced loads, minute cache, forced refresh and authoritative undo',async()=>{
 let calls=0,clock=now,value=doc();const reader=R.create({ids,now:()=>clock,fetch:async(url,options)=>{
  calls++;assert.equal(url,R.URL);assert.equal(options.credentials,'omit');assert.equal(options.referrerPolicy,'no-referrer');assert.equal(options.method,'GET');
  assert.deepEqual(Object.keys(options.headers),['Accept']);return response(value);
 }});
 const [a,b]=await Promise.all([reader.load(),reader.load()]);assert.equal(calls,1);assert.strictEqual(a,b);assert.equal(a.value.resolved.length,1);
 assert.equal((await reader.load()).cache,true);assert.equal(calls,1);
 value=doc([]);assert.equal((await reader.load({force:true})).value.resolved.length,0);assert.equal(calls,2);
 clock+=60001;await reader.load();assert.equal(calls,3);
});
test('offline initial load is unknown; malformed refresh preserves last good snapshot',async()=>{
 let mode='offline';const reader=R.create({ids,now:()=>now,fetch:async()=>{if(mode==='offline')throw Error('offline');if(mode==='broken')return new Response('{bad json');return response(doc());}});
 const first=await reader.load();assert.equal(first.status,'unavailable');assert.equal(first.value,null);assert.equal(first.checkedAt,null);
 mode='ok';const good=await reader.load();mode='broken';const stale=await reader.load({force:true});assert.equal(stale.status,'stale');assert.strictEqual(stale.value,good.value);assert.equal(stale.checkedAt,good.checkedAt);
 assert.equal((await reader.load()).status,'stale','A cache hit must not hide a failed refresh');
});
test('optional session cache is validated, limited to 24 hours and independent of browser storage policy',async()=>{
 let raw=null,clock=now;const storage={getItem:()=>raw,setItem:(k,v)=>{raw=v;}};
 await R.create({ids,storage,now:()=>clock,fetch:async()=>response(doc())}).load();assert(!raw.includes('token'));
 clock+=61000;const stale=await R.create({ids,storage,now:()=>clock,fetch:async()=>{throw Error('offline');}}).load();assert.equal(stale.status,'stale');assert.equal(stale.value.resolved.length,1);
 clock+=86400001;assert.equal((await R.create({ids,storage,now:()=>clock,fetch:async()=>{throw Error('offline');}}).load()).value,null);
 raw='{broken';assert.equal((await R.create({storage,fetch:async()=>response(doc())}).load()).status,'published');
 const blocked={getItem:()=>{throw Error('blocked');},setItem:()=>{throw Error('blocked');}};
 assert.equal((await R.create({storage:blocked,fetch:async()=>response(doc())}).load()).status,'published');
});
test('oversized body and timeout cannot replace validated progress',async()=>{
 const huge=R.create({fetch:async()=>new Response('x'.repeat(R.MAX_BYTES+1))});assert.equal((await huge.load()).status,'unavailable');
 const timeout=R.create({timeout:5,fetch:async(url,o)=>new Promise((resolve,reject)=>o.signal.addEventListener('abort',()=>reject(Error('timeout'))))});
 assert.equal((await timeout.load()).status,'unavailable');
});
test('public projection is disposable and an undo resets the overlay without modifying local evidence',()=>{
 const members=new Set(ids),base={byProblem:new Map([...ids].map(id=>[id,{state:'not-recorded',evidence:[],officialAccepted:false}])),
  coverage:new Map([['category',{primary:members,members,solved:new Set()}]]),solvedIds:new Set(),attemptedIds:new Set(),uniqueSolved:0,uniqueAttempted:0};
 const before=JSON.stringify([...base.byProblem]),one=R.project(base,R.validate(doc(),ids,now));assert.equal(one.uniqueSolved,1);assert.equal(one.coverage.get('category').solved.size,1);
 const undo=R.project(base,R.validate(doc([]),ids,now));assert.equal(undo.uniqueSolved,0);assert.equal(JSON.stringify([...base.byProblem]),before);assert.equal(base.coverage.get('category').solved.size,0);
});
