const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.resolve(__dirname,'../../../scripts/knowledge_atlas/node_modules/playwright'));
module.exports={chromium,launchOptions:{headless:true,...(process.env.ATLAS_BROWSER_EXECUTABLE?{executablePath:process.env.ATLAS_BROWSER_EXECUTABLE}:{})}};
