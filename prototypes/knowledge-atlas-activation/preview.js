(function(g){
'use strict';
let fixtures,raw,scenario='baseline',result,performanceRows=[],variants=null,variant='current';
const clone=x=>JSON.parse(JSON.stringify(x));
const accepted=new Set(AtlasBuildGeometry.nodes.map(n=>n.key));
function model(input){
 const m=AtlasModel.model(input);
 for(const row of input.topics.filter(t=>t.fixture_only)){
  const old='topic:'+row.id,n=m.nodes.get(old);m.nodes.delete(old);n.key=row.fixture_key;m.nodes.set(n.key,n);
 }return m;
}
function sceneModel(fixture,geometry){
 const out=clone(raw),keys=new Set(geometry.nodes.map(n=>n.key));
 for(const d of fixture.display.filter(n=>keys.has(n.key))){
  if(d.type==='category')out.categories.push({id:Number(d.key.split(':')[1]),title:d.title,
   canonical_parent_id:Number(d.parent.split(':')[1]),evidence_ids:[],url:'https://hyperskill.org/knowledge-map',fixture_context:true});
  else out.topics.push({id:d.adapter_id,title:d.title,fixture_key:d.key,fixture_only:true,
   canonical_parent_id:Number(d.parent.split(':')[1]),evidence_ids:[],url:null});
 }return out;
}
async function digest(text){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(b=>b.toString(16).padStart(2,'0')).join('');}
async function compute(name){
 const start=performance.now();let r;
 if(name==='small-variants'){
  variants??=SmallActivationVariants.build(AtlasBuildGeometry,fixtures.scenarios.small,AtlasV6.measure);
  r=clone(variants.selected[variant]);
 }else r=ActivationGeometry.plan(AtlasBuildGeometry,fixtures.scenarios[name],AtlasV6.measure);
 performanceRows.push({scenario:name,milliseconds:performance.now()-start});
 r.report.baseline_geometry_hash=await digest(ActivationGeometry.geometryHashInput(AtlasBuildGeometry));
 r.report.candidate_existing_geometry_hash=await digest(ActivationGeometry.geometryHashInput({nodes:r.geometry.nodes.filter(n=>accepted.has(n.key))}));
 return r;
}
function emphasize(){document.querySelectorAll('#graph .node').forEach(el=>el.classList.toggle('activation-candidate',!accepted.has(el.__data__?.key)));}
async function change(name,fit=false){
 scenario=name;result=await compute(name);AtlasV6.loadPreview(sceneModel(fixtures.scenarios[name==='small-variants'?'small':name],result.geometry),result.geometry);
 emphasize();document.querySelector('#scenario').value=name;
 document.querySelector('#variant-controls').hidden=name!=='small-variants';
 document.querySelector('#variant').value=variant;
 const r=result.report;document.querySelector('#activation-report').textContent=[r.outcome,
  ...(r.refusal?[r.refusal]:[]),
  `Blocked on metadata: ${r.blocked_references.length}${r.blocked_references.length?' ('+r.blocked_references.map(b=>b.id).join(', ')+')':''}`,
  `Accepted bounds: ${r.existing_nodes} · moved ${r.existing_nodes_moved}`,
  `New: ${r.new_categories} categories · ${r.new_topics} fixture topics`,
  ...(r.refusal?[`Requested: ${r.requested_categories} categories · ${r.requested_topics} fixture topics; none drawn`]:[]),
  `Overlaps ${r.overlaps} · crossings ${r.hierarchy_crossings}`,
  `Canvas +${r.width_growth}px × +${r.height_growth}px`,
  ...r.blocked_references.map(b=>`${b.id}: ${b.missing_metadata.join(', ')}; ${b.structural_memberships.join(', ')}; ${b.course_reasons.join(', ')}`),
  ...(result.metrics?[`Parent drift ${result.metrics.parent_drift}px (${(result.metrics.normalized_drift*100).toFixed(1)}% of accepted subtree width)`,
   `Max internal/overall drift ${result.metrics.max_all_parent_drift}px`,
   `First connector ${result.metrics.first_connector_length}px · total ${result.metrics.total_route_length}px`,
   `Longest bus ${result.metrics.max_horizontal_bus}px`]:[]),
  'Read-only geometry preview · Generation 0'].join('\n');
 if(fit)AtlasV6.fit(null,false);return result;
}
g.AtlasPrototype={model,change,compute,sceneModel,state:()=>({scenario,result,fixtures,performanceRows,variants,variant}),
 selectVariant:async name=>{if(!['current','parent-distance','centering','connector','balanced'].includes(name))throw Error('Unknown variant');variant=name;return change('small-variants');},
 fitComparison:()=>{const keys=new Set(['category:1164','category:73',...result.report.drawn_candidates]);AtlasV6.fit(keys,false,'comparison');},
 fitExisting:()=>AtlasV6.fit(accepted,false,'overview'),
 focusCandidate:()=>{const root=result.geometry.nodes.find(n=>!accepted.has(n.key)&&!n.parent);if(root)AtlasV6.select(root.key,true);},
 emphasize};
async function init(){
 fixtures=await(await fetch('fixtures/scenarios.json')).json();raw=await(await fetch('../../docs/knowledge-map/model.json')).json();
 while(!g.AtlasV6)await new Promise(r=>setTimeout(r,10));
 document.querySelector('#scenario').onchange=e=>change(e.target.value).catch(showError);
 document.querySelector('#variant').onchange=e=>AtlasPrototype.selectVariant(e.target.value).catch(showError);
 document.querySelector('#fit-comparison').onclick=AtlasPrototype.fitComparison;
 document.querySelector('#fit-existing').onclick=AtlasPrototype.fitExisting;
 document.querySelector('#fit-candidate').onclick=AtlasPrototype.focusCandidate;
 await change(new URLSearchParams(location.search).get('scenario')||'baseline',true);
 g.AtlasPrototype.ready=true;
}
function showError(e){document.querySelector('#error').textContent=e.stack||String(e);console.error(e);}
init().catch(showError);
})(globalThis);
