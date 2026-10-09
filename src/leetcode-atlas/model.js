/* LeetCode semantic boundary. No Hyperskill data, state, or progress imports. */
(function (g) {
'use strict';
const ROOT = 'lc:root';
const fail = message => { throw new Error(message); };
const unique = (values, label) => { if (new Set(values).size !== values.length) fail('Duplicate ' + label); };
const officialUrl = value => typeof value === 'string' && /^https:\/\/leetcode\.com\/problems\/[a-z0-9-]+\/$/.test(value);
const allowedProblemFields = new Set(['id','platform','site','catalog','officialQuestionId','displayNumber','title','slug','canonicalUrl','urlAliases','difficulty','premium','topicTags','tagsCompleteness','primaryTaxonomyId','secondaryTaxonomyIds','placement','studyPlanIds','catalogStatus','provenance']);
function validate(catalog, taxonomy) {
 if (catalog.schemaVersion !== 1 || taxonomy.schemaVersion !== 1) fail('Unsupported schema version');
 if (!['partial','complete-snapshot'].includes(catalog.coverage.state)) fail('Explicit catalog coverage required');
 if (catalog.coverage.state === 'complete-snapshot' && (catalog.coverage.officialTotal !== catalog.problems.length || !catalog.coverage.snapshotEvidence?.sourceSnapshotId || !catalog.coverage.snapshotEvidence?.rightsRef || !catalog.coverage.snapshotEvidence?.reviewedAt)) fail('Complete snapshot requires reviewed scope, total and rights evidence');
 if (catalog.coverage.loaded !== catalog.problems.length) fail('Incorrect loaded count');
 unique(taxonomy.nodes.map(n => n.id), 'taxonomy ID');
 const tax = new Map(taxonomy.nodes.map(n => [n.id,n]));
 if (!tax.has(ROOT) || tax.get(ROOT).parent !== null) fail('Missing independent LeetCode root');
 for (const n of tax.values()) {
  if (!n.id.startsWith('lc:') || !n.title || !Array.isArray(n.tags)) fail('Invalid taxonomy node');
  let cursor = n; const seen = new Set();
  while (cursor.id !== ROOT) {
   if (seen.has(cursor.id)) fail('Taxonomy cycle');
   seen.add(cursor.id); cursor = tax.get(cursor.parent);
   if (!cursor) fail('Orphan taxonomy node');
  }
 }
 unique(catalog.problems.map(p => p.id), 'problem ID');
 unique(catalog.problems.map(p => p.canonicalUrl), 'canonical URL');
 unique(catalog.problems.map(p => p.site + ':' + p.catalog + ':' + p.displayNumber), 'display number binding');
 unique(catalog.problems.filter(p => p.officialQuestionId !== null).map(p => p.site + ':' + p.officialQuestionId), 'official question ID');
 const aliases = new Set();
 for (const p of catalog.problems) {
  if (Object.keys(p).some(k => !allowedProblemFields.has(k))) fail('Non-metadata problem field');
  if (!/^lc:problem:[a-z0-9-]+$/.test(p.id) || p.platform !== 'leetcode' || p.site !== 'leetcode.com' || !['algorithms','dataset-evaluation'].includes(p.catalog)) fail('Invalid problem identity');
  if (typeof p.displayNumber !== 'string' || !p.displayNumber.trim()) fail('Missing display number');
  if (p.officialQuestionId !== null && (typeof p.officialQuestionId !== 'string' || !p.officialQuestionId)) fail('Invalid official question ID');
  if (!officialUrl(p.canonicalUrl) || p.canonicalUrl !== 'https://leetcode.com/problems/' + p.slug + '/') fail('Invalid canonical URL');
  for (const url of [p.canonicalUrl,...p.urlAliases]) {
   if (!officialUrl(url) || aliases.has(url)) fail('Conflicting or invalid URL alias');
   aliases.add(url);
  }
  if (p.title !== null && (typeof p.title !== 'string' || !p.title.trim())) fail('Invalid title');
  if (![null,'Easy','Medium','Hard'].includes(p.difficulty)) fail('Invalid difficulty');
  if (!['free','premium','unknown'].includes(p.premium)) fail('Invalid Premium status');
  if (!Array.isArray(p.topicTags) || p.topicTags.some(t => typeof t !== 'string' || !t.trim())) fail('Invalid topic tags');
  unique(p.topicTags, 'topic tag');
  if (!['complete-as-observed','partial','unknown'].includes(p.tagsCompleteness)) fail('Invalid tag completeness');
  if (p.studyPlanIds !== null && (!Array.isArray(p.studyPlanIds) || p.studyPlanIds.some(x => typeof x !== 'string'))) fail('Invalid study plans');
  if (!['observed-public-page','retired','unavailable','unknown'].includes(p.catalogStatus)) fail('Invalid catalog status');
  if (tax.get(p.primaryTaxonomyId)?.kind !== 'pattern') fail('Missing explicit primary pattern');
  if (!Array.isArray(p.secondaryTaxonomyIds)) fail('Missing secondary memberships');
  unique(p.secondaryTaxonomyIds,'secondary membership');
  if (p.secondaryTaxonomyIds.some(id => tax.get(id)?.kind !== 'pattern' || id === p.primaryTaxonomyId)) fail('Invalid secondary membership');
  if (p.placement?.taxonomyVersion !== taxonomy.version || !p.placement.reason) fail('Missing placement provenance');
  if (!p.provenance?.sourceId || !officialUrl(p.provenance.url) || !p.provenance.reviewedAt || !p.provenance.method) fail('Missing metadata provenance');
 }
 return {catalog,taxonomy,tax,problems:new Map(catalog.problems.map(p => [p.id,p]))};
}
function ancestors(index, id) {
 const result=[];
 for (let n=index.tax.get(id); n; n=index.tax.get(n.parent)) result.push(n.id);
 return result;
}
function memberships(index,p) {
 return new Set([p.primaryTaxonomyId,...p.secondaryTaxonomyIds].flatMap(id => ancestors(index,id)));
}
function resolveIdentity(index, identity) {
 const p=index.problems.get(identity?.problemId);
 if (!p || identity.displayNumber !== p.displayNumber || ![p.canonicalUrl,...p.urlAliases].includes(identity.canonicalUrl)) fail('Unresolved or conflicting exact problem identity');
 return p;
}
function projectProgress(index, ledger, {publicOnly=false}={}) {
 if (ledger.schemaVersion !== 1 || ledger.domain !== 'leetcode' || !Array.isArray(ledger.evidence)) fail('Invalid LeetCode evidence ledger');
 const events=new Map(), revoked=new Set();
 for (const e of ledger.evidence) {
  if (!/^lc:event:[a-zA-Z0-9-]+$/.test(e.eventId)) fail('Invalid evidence ID');
  if (events.has(e.eventId)) {
   if (JSON.stringify(events.get(e.eventId)) !== JSON.stringify(e)) fail('Conflicting evidence ID');
   continue;
  }
  resolveIdentity(index,e.identity);
  if (!['solved','attempted','retract'].includes(e.kind) || e.sourceType !== 'git-owner-attestation' || e.attestedBy !== 'owner') fail('Unsupported evidence claim; official acceptance requires a future verified adapter');
  if (typeof e.public !== 'boolean' || !/^\d{4}-\d\d-\d\dT/.test(e.recordedAt) || !Number.isFinite(Date.parse(e.recordedAt))) fail('Invalid evidence provenance');
  if (e.occurredAt !== null && (!/^\d{4}-\d\d-\d\dT/.test(e.occurredAt) || !Number.isFinite(Date.parse(e.occurredAt)))) fail('Invalid solved/attempted date');
  if (e.kind !== 'retract') {
   const s=e.solution;
   if (!s || !/^https:\/\/[a-z0-9.-]+\/[^?#]+$/i.test(s.repositoryUrl) || !/^[a-f0-9]{40}$/.test(s.commitSha) || !s.path || s.path.startsWith('/') || s.path.split('/').includes('..') || !s.language) fail('Missing exact Git solution evidence');
  }
  events.set(e.eventId,e);
 }
 for (const e of events.values()) if (e.kind === 'retract') {
  const target=events.get(e.retracts);
  if (!target || target.kind === 'retract' || target.identity.problemId !== e.identity.problemId) fail('Invalid evidence retraction');
  revoked.add(target.eventId);
 }
 const byProblem=new Map([...index.problems.keys()].map(id => [id,{state:'not-recorded',solvedDate:null,officialAccepted:false,evidence:[]}]));
 for (const e of events.values()) {
  if (e.kind === 'retract' || revoked.has(e.eventId) || (publicOnly && !e.public)) continue;
  const row=byProblem.get(e.identity.problemId); row.evidence.push(e);
  if (e.kind === 'solved') row.state='solved';
  else if (row.state !== 'solved') row.state='attempted';
 }
 for (const row of byProblem.values()) {
  row.evidence.sort((a,b) => a.recordedAt.localeCompare(b.recordedAt) || a.eventId.localeCompare(b.eventId));
  row.solvedDate=row.evidence.filter(e => e.kind === 'solved' && e.occurredAt).map(e => e.occurredAt).sort()[0] || null;
 }
 const solvedIds=new Set([...byProblem].filter(([,p]) => p.state === 'solved').map(([id]) => id));
 const attemptedIds=new Set([...byProblem].filter(([,p]) => p.state === 'attempted').map(([id]) => id));
 const coverage=new Map([...index.tax.keys()].map(id => [id,{primary:new Set(),members:new Set(),solved:new Set()}]));
 for (const p of index.problems.values()) {
  for (const id of ancestors(index,p.primaryTaxonomyId)) coverage.get(id).primary.add(p.id);
  for (const id of memberships(index,p)) { const c=coverage.get(id);c.members.add(p.id);if(solvedIds.has(p.id))c.solved.add(p.id); }
 }
 return {byProblem,solvedIds,attemptedIds,coverage,uniqueSolved:solvedIds.size,uniqueAttempted:attemptedIds.size};
}
function matches(p,{difficulty='all',premium='all',query=''}={}) {
 if (difficulty !== 'all' && (p.difficulty || 'unknown') !== difficulty) return false;
 if (premium !== 'all' && p.premium !== premium) return false;
 const q=query.trim().toLowerCase();
 return !q || [p.id,p.displayNumber,p.title || '',p.slug,...p.topicTags].some(s => s.toLowerCase().includes(q));
}
// Large branches get bounded presentation groups, never semantic taxonomy nodes.
function bucketLeaves(model, size=128) {
 for (const n of [...model.nodes.values()]) {
  const leaves=n.children.filter(isLeaf);
  if (leaves.length<=size) continue;
  const categories=n.children.filter(c=>!isLeaf(c));
  leaves.sort((a,b)=>a.key.localeCompare(b.key));
  for(let i=0;i<leaves.length;i+=size) {
   const key='lc:layout-group:'+n.key+':'+Math.floor(i/size),children=leaves.slice(i,i+size);
   const group={key,type:'category',kind:'layout-group',parent:n.key,semanticParent:n.key,displayTitle:'Problems · group '+(Math.floor(i/size)+1),children,leafKeys:children.map(c=>c.key)};
   for(const leaf of children) { leaf.semanticParent=n.key;leaf.parent=key; }
   model.nodes.set(key,group);categories.push(group);
  }
  n.children=categories;
 }
 return model;
}
const isLeaf=n=>n.type==='problem';
function buildHierarchy(index,progress,{view='global',difficulty='all',premium='all'}={}) {
 if (!['global','personal'].includes(view)) fail('Unknown LeetCode view');
 const nodes=new Map(index.taxonomy.nodes.map(n => [n.id,{...n,key:n.id,displayTitle:n.title,type:'category',children:[],leafKeys:[]}]));
 const root=nodes.get(ROOT);root.displayTitle=view==='personal'?'My LeetCode Tree':'Problem Atlas';
 for (const n of nodes.values()) if(n.parent) nodes.get(n.parent).children.push(n);
 const selected=[...index.problems.values()].sort((a,b)=>a.id.localeCompare(b.id)).filter(p => matches(p,{difficulty,premium}) && (view==='global' || progress.byProblem.get(p.id).state !== 'not-recorded'));
 for (const p of selected) {
  const n={key:p.id,type:'problem',problem:p,parent:p.primaryTaxonomyId,displayTitle:p.displayNumber+'. '+(p.title || 'Title not recorded'),children:[]};
  nodes.set(n.key,n);nodes.get(n.parent).children.push(n);
 }
 function visit(n) {
  for(const child of n.children) if(child.type==='category')visit(child);
  if(view==='personal') n.children=n.children.filter(c => c.type==='problem' || c.leafKeys.length);
  n.leafKeys=n.children.flatMap(c => c.type==='problem'?[c.key]:c.leafKeys);
 }
 visit(root);
 const reachable=new Map();(function walk(n){reachable.set(n.key,n);n.children.forEach(walk);})(root);
 return bucketLeaves({root,nodes:reachable,view,selected});
}
const api={ROOT,validate,ancestors,memberships,resolveIdentity,projectProgress,matches,buildHierarchy,bucketLeaves,isLeaf};
g.LeetCodeModel=Object.freeze(api);
if(typeof module!=='undefined')module.exports=api;
})(globalThis);
