const fs=require('fs');
const {chromium}=require('/private/tmp/cks/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1600,height:1500}});
 await page.setContent('<html><body style="background:white;margin:24px"><div id="diagram"></div></body></html>');
 await page.addScriptTag({path:'/private/tmp/cks/node_modules/mermaid/dist/mermaid.min.js'});
 const source=fs.readFileSync('/tmp/peer-status-validation-2/diagram.mmd','utf8');
 const result=await page.evaluate(async source=>{mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'default'});const {svg}=await mermaid.render('peer-freshness',source);document.getElementById('diagram').innerHTML=svg;return {nodes:document.querySelectorAll('.node').length,edges:document.querySelectorAll('.edgePath').length,svg};},source);
 fs.writeFileSync('/tmp/peer-status-validation-2/diagram.svg',result.svg);
 await page.screenshot({path:'/tmp/peer-status-validation-2/diagram.png',fullPage:true});
 console.log(JSON.stringify({render:'passed',nodes:result.nodes,svgBytes:result.svg.length}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
