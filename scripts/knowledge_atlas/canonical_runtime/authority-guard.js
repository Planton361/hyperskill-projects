/* Explicit authority contract; refuse unsupported versions instead of V6 fallback. */
(async()=>{
 const [authority,cp,target,master]=await Promise.all(['spatial-authority.json','layout-checkpoint.json','target-geometry.json','generated/global-geometry.json'].map(async p=>(await fetch(p)).json()));
 const fields=['catalog_fingerprint','geometry_fingerprint','geometry_schema_version','geometry_sha256','kind','layout_algorithm_version','master_asset','review_candidate_fingerprint','schema_version','slot_contract'];
 if(JSON.stringify(Object.keys(authority).sort())!==JSON.stringify(fields)||authority.kind!=='global-canonical-pyramid'||authority.schema_version!==1||authority.master_asset!=='generated/global-geometry.json'||cp.state_schema_version!==3||cp.presentation_generation!==1||authority.geometry_fingerprint!==master.geometry_fingerprint||JSON.stringify(cp.spatial_authority)!==JSON.stringify(authority))throw Error('Unsupported/conflicting spatial authority');
 const slots=new Map(master.positions.map(n=>[n.key,n]));for(const n of target.positions){const p=slots.get(n.slot);if(!p||['x','y','w','h'].some(k=>n[k]!==p[k]))throw Error('Canonical slot mismatch');}
 const script=document.createElement('script');script.src='app.js';document.body.append(script);window.SpatialAuthority={authority,checkpoint:cp,target,master};
})().catch(e=>{document.querySelector('#status').textContent='SPATIAL_AUTHORITY_INVALID · '+e.message;console.error(e);});
