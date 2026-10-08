/* The shared planner runs off the interaction thread; semantics are unchanged. */
importScripts('../geometry/measure.js','projection.js','routing.js','layout.js');
let catalog;
const ctx=new OffscreenCanvas(1,1).getContext('2d');
const measure=AtlasMeasure.width;
onmessage=({data})=>{
 if(data.catalog){catalog=data.catalog;return;}
 try{const start=performance.now(),s=data.scope,{projection,L}=ScopePyramid(s.scope_type,s.scope_id,s.explicit_topic_ids,s.explicit_category_ids,catalog,measure);postMessage({job:data.job,projection,L,layoutMs:performance.now()-start});}
 catch(error){postMessage({job:data.job,error:error.message});}
};
