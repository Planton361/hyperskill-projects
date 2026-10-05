/* Read-only, presentation-only comparison of one unchanged ActivationPlan. */
(function(g){
'use strict';
const A=g.ActivationGeometry,round=n=>Math.round(n*1e6)/1e6;
const median=values=>{const a=[...values].sort((a,b)=>a-b),i=Math.floor(a.length/2);return a.length%2?a[i]:(a[i-1]+a[i])/2;};
const routeLength=points=>points.slice(1).reduce((sum,p,i)=>sum+Math.abs(p.x-points[i].x)+Math.abs(p.y-points[i].y),0);
function metrics(frozen,result,fixture){
 const ids=new Set(frozen.nodes.map(n=>n.key)),nodes=result.geometry.nodes.filter(n=>!ids.has(n.key));
 const root=nodes.find(n=>!n.parent&&frozen.nodes.some(o=>o.key===fixture.display.find(d=>d.key===n.key)?.parent));
 const parentKey=fixture.display.find(d=>d.key===root.key).parent,parent=frozen.nodes.find(n=>n.key===parentKey);
 const allParents=new Map(frozen.branches.map(b=>[b.child,b.parent]));
 function belongs(key){let n=key;while(n){if(n===parentKey)return true;n=allParents.get(n);}return false;}
 const parentRects=A.ledger(frozen).filter(r=>belongs(r.key.startsWith('tray:')?r.key.slice(5):r.key));
 const parentWidth=Math.max(...parentRects.map(r=>r.x+r.w))-Math.min(...parentRects.map(r=>r.x));
 const categoryRects=nodes.filter(n=>!n.parent).map(A.rect),trayRects=result.geometry.trays.slice(frozen.trays.length).map(t=>({x:t.x,y:t.y,w:t.width,h:t.height}));
 const newRects=[...categoryRects,...trayRects],left=Math.min(...newRects.map(r=>r.x)),right=Math.max(...newRects.map(r=>r.x+r.w)),center=(left+right)/2;
 const combinedLeft=Math.min(left,...parentRects.map(r=>r.x)),combinedRight=Math.max(right,...parentRects.map(r=>r.x+r.w));
 const siblings=frozen.branches.filter(b=>b.parent===parentKey).map(b=>frozen.nodes.find(n=>n.key===b.child));
 const family=[...siblings,root],parentDrift=Math.abs((Math.min(...family.map(n=>n.x))+Math.max(...family.map(n=>n.x)))/2-parent.x);
 const first=result.geometry.activationRoutes.find(r=>r.parent===parentKey&&r.child===root.key);
 const childCounts=new Map();for(const b of frozen.branches)childCounts.set(b.parent,(childCounts.get(b.parent)||0)+1);
 const siblingsLengths=frozen.branches.filter(b=>childCounts.get(b.parent)>1).map(b=>routeLength(b.points));
 const typical=median(siblingsLengths),buses=result.geometry.activationRoutes.map(r=>Math.abs(r.points[2].x-r.points[1].x));
 const physical=result.geometry.connectorSegments.slice(frozen.connectorSegments.length).reduce((sum,s)=>sum+routeLength(s.points),0);
 const whitespace=result.geometry.activationRoutes.reduce((sum,r)=>sum+Math.abs((r.points[1].y-r.points[0].y)-A.TOKENS.stem),0);
 return {parent_id:parentKey,parent_title:fixture.plan.entities.find(r=>r.id===parentKey).title,parent_center_x:parent.x,
  new_root_center_x:root.x,new_subtree_center_x:center,new_subtree_width:right-left,
  root_horizontal_offset:Math.abs(root.x-parent.x),subtree_horizontal_offset:Math.abs(center-parent.x),
  parent_drift:parentDrift,max_all_parent_drift:result.report.parent_centering_drift,
  accepted_parent_subtree_width:parentWidth,normalized_drift:round(parentDrift/parentWidth),
  combined_parent_subtree_center_x:(combinedLeft+combinedRight)/2,combined_bbox_center_drift:Math.abs((combinedLeft+combinedRight)/2-parent.x),
  normalized_max_drift:round(result.report.parent_centering_drift/parentWidth),
  first_connector_length:first.length,total_route_length:round(result.geometry.activationRoutes.reduce((sum,r)=>sum+r.length,0)),
  added_physical_connector_length:round(physical),max_horizontal_bus:Math.max(...buses),first_bus_y:first.points[1].y,
  existing_sibling_center_distance:Math.min(...siblings.map(s=>Math.abs(root.x-s.x))),
  existing_sibling_edge_gap:Math.min(...siblings.map(s=>Math.max(0,Math.abs(root.x-s.x)-(root.width+s.width)/2))),
  typical_existing_sibling_connector_length:typical,existing_sibling_connector_samples:siblingsLengths.length,
  connector_ratio:round(first.length/typical),whitespace_deviation:round(whitespace),
  width_growth:result.report.width_growth,height_growth:result.report.height_growth,
  existing_displacement:result.report.existing_nodes_moved,overlaps:result.report.overlaps,crossings:result.report.hierarchy_crossings,
  invalid_ports:result.report.invalid_ports,outcome:result.report.outcome};
}
function build(frozen,fixture,measure){
 const current=A.plan(frozen,fixture,measure),pool=new Map(),runs=[];
 const identity=r=>A.stable(r.geometry.nodes.filter(n=>!frozen.nodes.some(o=>o.key===n.key)).map(n=>({key:n.key,x:n.x,y:n.y,width:n.width,height:n.height})))+'|'+A.stable(r.geometry.activationRoutes);
 function add(r){if(r.report.outcome!=='ACTIVATION_REVIEW_REQUIRED')return;const checks=A.validate(frozen,r.geometry);if(Object.values(checks).some(Boolean))throw Error('Invalid alternative');pool.set(identity(r),{...r,metrics:metrics(frozen,r,fixture)});}
 add(current);
 for(const objective of ['parent-distance','centering','connector','balanced']){
  const result=A.plan(frozen,fixture,measure,{comparison:true,objective,retainCandidates:true});
  runs.push({objective,valid_retained:result.candidates.length,search:result.report.search});
  result.candidates.forEach(add);
 }
 const candidates=[...pool.values()];
 const keys={
  'parent-distance':r=>[r.metrics.root_horizontal_offset,r.metrics.max_all_parent_drift,r.metrics.max_horizontal_bus,r.metrics.total_route_length,r.metrics.width_growth],
  'centering':r=>[r.metrics.max_all_parent_drift,r.metrics.max_horizontal_bus,r.metrics.parent_drift,r.metrics.width_growth],
  'connector':r=>[r.metrics.total_route_length,r.metrics.max_horizontal_bus,r.metrics.max_all_parent_drift,r.metrics.root_horizontal_offset,r.metrics.width_growth],
  'balanced':r=>{const m=r.metrics,w=A.COMPARISON.weights;return[(w.parentDistance*m.root_horizontal_offset+w.maxBus*m.max_horizontal_bus+w.drift*m.max_all_parent_drift+w.whitespace*m.whitespace_deviation+w.growth*m.width_growth)/frozen.nodes.find(n=>n.key===m.parent_id).width,m.max_horizontal_bus,m.parent_drift,m.width_growth];}
 };
 function pick(name){return [...candidates].sort((a,b)=>{const x=keys[name](a),y=keys[name](b);for(let i=0;i<x.length;i++)if(x[i]!==y[i])return x[i]-y[i];return identity(a).localeCompare(identity(b));})[0];}
 const selected={current:{...current,metrics:metrics(frozen,current,fixture)}};
 for(const name of Object.keys(keys))selected[name]=pick(name);
 const growthGroups={};for(const c of candidates){const k=c.metrics.width_growth;growthGroups[k]??={count:0,min_parent_distance:Infinity,min_max_drift:Infinity,min_connector:Infinity};const group=growthGroups[k];group.count++;group.min_parent_distance=Math.min(group.min_parent_distance,c.metrics.root_horizontal_offset);group.min_max_drift=Math.min(group.min_max_drift,c.metrics.max_all_parent_drift);group.min_connector=Math.min(group.min_connector,c.metrics.total_route_length);}
 return {selected,inventory:{valid_candidates:candidates.length,distinct_geometry_positions:new Set(candidates.map(r=>A.geometryHashInput(r.geometry))).size,
  search_scope:'Minima among valid retained evaluated candidates, not exhaustive global optima',runs,
  growth_groups:Object.entries(growthGroups).map(([growth,data])=>({width_growth:Number(growth),...data})).sort((a,b)=>a.width_growth-b.width_growth),
  comparison_policy:A.COMPARISON,semantic_plan_unchanged:true,default_search_unchanged:true}};
}
g.SmallActivationVariants={build,metrics};
})(globalThis);
