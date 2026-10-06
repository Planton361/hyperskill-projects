/* Verify exact package bytes before displaying the reviewed comparison. */
(async()=>{
 const fetchFile=window.fetch.bind(window),hash=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
 const manifest=await (await fetchFile('../migration-manifest.json')).json(),core=await (await fetchFile('../manifest-core.json')).arrayBuffer();
 if(await hash(core)!==manifest.manifest_fingerprint)throw Error('Manifest review identity mismatch');
 const parsed=JSON.parse(new TextDecoder().decode(core)),without={...manifest};delete without.manifest_fingerprint;
 if(JSON.stringify(parsed)!==JSON.stringify(without))throw Error('Manifest preimage mismatch');
 await Promise.all(Object.entries(manifest.files).map(async([name,expected])=>{const r=await fetchFile('../'+name);if(!r.ok||await hash(await r.arrayBuffer())!==expected)throw Error('Changed package artifact: '+name);}));
 const summary=await (await fetchFile('../review-summary.json')).json(),metrics=summary.displacement.all;
 const box=document.querySelector('#review-bindings');
 function paragraph(t){const p=document.createElement('p');p.textContent=t;box.append(p);}
 paragraph('SOURCE: Current accepted V6 Production');paragraph('TARGET: Canonical Global Pyramid');
 paragraph(`Proposed spatial Generation: ${manifest.contract.source.presentation_generation} → ${manifest.contract.source.presentation_generation+1}. Activation history version ${manifest.contract.source.history_version} is unchanged. This review applies nothing.`);
 paragraph('135 / 135 mapped · 46 Categories · 89 Topics · 31 learned · 12 verified');paragraph('Project 113: 26 requirements · Stage 617: 12 requirements');
 paragraph(`One-time moved: ${metrics.moved} · median ${metrics.median.toFixed(2)} · p95 ${metrics.p95.toFixed(2)} · max ${metrics.max.toFixed(2)} world units`);
 paragraph('Target geometry fingerprint: '+summary.target_geometry_fingerprint);
 const label=document.createElement('label');label.textContent='Human review token — exact migration manifest fingerprint';const token=document.createElement('textarea');token.id='review-token';token.readOnly=true;token.rows=3;token.value=manifest.manifest_fingerprint;label.append(token);box.append(label);
 const copy=document.createElement('button');copy.id='copy-token';copy.textContent='Copy reviewed fingerprint';copy.onclick=async()=>{token.focus();token.select();try{await navigator.clipboard.writeText(token.value);copy.textContent='Copied exact fingerprint';}catch{copy.textContent='Fingerprint selected — press Ctrl+C';}};box.append(copy);
 paragraph('Package bytes verified. This does not establish live source freshness or human approval. No apply control exists.');
 document.querySelector('.ready').textContent=manifest.fixture_only?'FIXTURE PACKAGE · NEVER REAL APPROVAL':'EXACT PACKAGE VERIFIED · AWAITING HUMAN REVIEW';
 window.fetch=(input,init)=>String(input)==='../../generated/global-geometry.json'?fetchFile('../global-geometry.json',init):fetchFile(input,init);
 const script=document.createElement('script');script.src='app.js';document.body.append(script);window.SpatialReview={manifest,summary,packageVerified:true};
})().catch(e=>{document.querySelector('.ready').textContent='STALE_SPATIAL_MIGRATION_PREVIEW';document.querySelector('#context').textContent=e.message;console.error(e);});
