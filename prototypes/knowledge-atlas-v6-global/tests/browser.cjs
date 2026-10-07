/* The repository already locks Playwright in scripts/knowledge_atlas.
   No machine-local module or browser path is a required dependency. */
const path=require('node:path');
const playwright=process.env.PLAYWRIGHT_MODULE||path.resolve(__dirname,'../../../scripts/knowledge_atlas/node_modules/playwright');
const {chromium}=require(playwright);
const launchOptions={headless:true};
if(process.env.ATLAS_BROWSER_EXECUTABLE)launchOptions.executablePath=process.env.ATLAS_BROWSER_EXECUTABLE;
module.exports={chromium,launchOptions};
