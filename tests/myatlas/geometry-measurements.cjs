/* Every supported scope uses frozen widths; a missing width must fail closed. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),source=path.join(root,'src/myatlas'),context=vm.createContext({performance,console});
for(const file of ['geometry/measure.js','knowledge-atlas-scope-pyramid/routing.js','knowledge-atlas-scope-pyramid/layout.js','knowledge-atlas-scope-pyramid/projection.js'])vm.runInContext(fs.readFileSync(path.join(source,file),'utf8'),context);
const raw=fs.readFileSync(path.join(source,'knowledge-atlas-scope-pyramid/catalog.json')),catalog=JSON.parse(raw),index=JSON.parse(fs.readFileSync(path.join(source,'knowledge-atlas-scope-pyramid/scope-index.json')));
assert.equal(context.AtlasMeasure.metadata.catalog_sha256,crypto.createHash('sha256').update(raw).digest('hex'));
assert.throws(()=>context.AtlasMeasure.width('unreviewed new catalog label'),/Missing accepted structural measurement/);
assert.throws(()=>context.AtlasMeasure.width('3106 slots · 3107 learned',10),/Missing accepted/);
function spans(text,font,weight){const words=text.split(/\s+/);for(let i=0;i<words.length;i++)for(let j=i+1;j<=words.length;j++)assert(Number.isFinite(context.AtlasMeasure.width(words.slice(i,j).join(' '),font,weight)));}
for(const t of catalog.topics)spans(t.title,14,400);
for(const c of catalog.categories)for(const [f,w]of [[17,600],[21,600],[28,650]])spans(c.title,f,w);
let scopes=0,nodes=0;const counts=new Set([0,3106]);for(const s of [...index.courses,...index.projects,...index.stages])if(s.state==='KNOWN'){
 const p=context.ScopeProjection.project(s.scope_type,s.scope_id,s.explicit_topic_ids,s.explicit_category_ids,catalog),m=context.ScopeProjection.model(p,catalog);scopes++;nodes+=m.nodes.size;spans(m.root.displayTitle,28,650);for(const n of m.nodes.values())if(n.type!=='topic')counts.add(n.leafKeys.length);
}
const full=context.ScopeProjection.model(context.ScopeProjection.project('course',0,catalog.topics.map(t=>t.id),catalog.categories.map(c=>c.id),catalog),catalog);for(const n of full.nodes.values())if(n.type!=='topic')counts.add(n.leafKeys.length);
for(const count of counts)for(let learned=0;learned<=count;learned++)assert(Number.isFinite(context.AtlasMeasure.width(count+' slots · '+learned+' learned',10)));
console.log(JSON.stringify({status:'PASS',known_scopes:scopes,total_scope_nodes:nodes,unknown_width_rejected:true,catalog_digest:true,future_counts:true}));
