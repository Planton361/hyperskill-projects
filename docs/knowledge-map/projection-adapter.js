/* Release boundary validation; the accepted aggregator remains authoritative. */
(() => {
const original=ProgressAnalytics.create;
ProgressAnalytics.create=function(input){
 const projection=input.completion||input.catalog.projectCompletion;
 if(projection?.schema!==2)throw Error('Generated public projection required');
 const analytics=original(input),learned=[],verified=[];
 for(const topic of input.catalog.topics){const s=analytics.topic(topic.id);if(s.learned===true)learned.push(topic.id);if(s.verified===true)verified.push(topic.id);}
 const sort=ids=>[...ids].sort((a,b)=>a-b);
 for(const [actual,expected] of [[learned,projection.effective_learned_topic_ids],[verified,projection.verified_topic_ids]])
  if(JSON.stringify(sort(actual))!==JSON.stringify(sort(expected)))throw Error('Public projection and source evidence disagree');
 globalThis.PublicProgress=projection;return analytics;
};
})();
