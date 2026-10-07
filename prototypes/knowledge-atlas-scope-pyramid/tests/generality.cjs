const {chromium,launchOptions}=require('./browser.cjs'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch(launchOptions);try{const page=await browser.newPage({viewport:{width:1440,height:900}});await page.goto(process.env.SCOPE_URL||'http://127.0.0.1:8810/prototypes/knowledge-atlas-scope-pyramid/');await page.waitForFunction(()=>window.ScopeApp);
 const check=await page.evaluate(()=>{
  const {catalog,scopes}=ScopeApp.state(),raw=structuredClone(catalog),offset=100000;
  for(const rows of [raw.categories,raw.topics])for(const n of rows){n.id+=offset;if(n.parent_id!=null)n.parent_id+=offset;if(n.accepted_metadata?.canonical_parent_id!=null)n.accepted_metadata.canonical_parent_id+=offset;}
  raw.memberships=Object.fromEntries(Object.entries(raw.memberships).map(([k,ids])=>[+k+offset,ids.map(id=>id+offset)]));raw.progress.topics.forEach(p=>p.topic_id+=offset);
  const results=[];for(const s of scopes){const original=ScopePyramid(s.scope_type,s.scope_id,s.explicit_topic_ids,s.explicit_category_ids,catalog,ScopeApp.measure),relabeled=ScopePyramid(s.scope_type,s.scope_id,s.explicit_topic_ids.map(id=>id+offset),s.explicit_category_ids.map(id=>id+offset),raw,ScopeApp.measure);
   const positions=L=>L.nodes.map(n=>[n.data.type,n.data.title,n.x,n.y,n.width,n.height,n.lines]);results.push({scope:s.scope_type,allSemanticIdsRelabeledWithoutGeometryChange:JSON.stringify(positions(original.L))===JSON.stringify(positions(relabeled.L))});
  }
  return results;
 });
 const code=fs.readFileSync(path.join(__dirname,'../layout.js'),'utf8'),forbidden=/\b(?:course|project|stage|113|617)\b|Computer science|Java|Programming languages/i;
 const result={idRemapping:check,noScopeTypesIdsOrBranchNamesInLayout:!forbidden.test(code),engineEntrypoint:'ScopePyramid → ScopeProjection.project/model → AtlasLayout.build',layoutImplementations:1};
 fs.writeFileSync(path.join(__dirname,'generality.json'),JSON.stringify(result,null,2)+'\n');assert(result.noScopeTypesIdsOrBranchNamesInLayout);assert(check.every(r=>r.allSemanticIdsRelabeledWithoutGeometryChange));console.log(result);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
