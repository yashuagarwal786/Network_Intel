import {chromium} from '../../frontend/node_modules/@playwright/test/index.mjs';
import {mkdir,writeFile,readdir,rename,rm} from 'node:fs/promises';
import path from 'node:path';

const out=path.resolve(import.meta.dirname,'captures');
const videoDir=path.join(out,'raw-video');
await rm(videoDir,{recursive:true,force:true});
await mkdir(videoDir,{recursive:true});
const browser=await chromium.launch({channel:'msedge',headless:true});
const context=await browser.newContext({
  viewport:{width:1920,height:1080},
  deviceScaleFactor:1,
  recordVideo:{dir:videoDir,size:{width:1920,height:1080}},
});
const page=await context.newPage();
const errors=[]; const failed=[]; const external=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
page.on('requestfailed',r=>failed.push(r.url()+': '+r.failure()?.errorText));
await page.route('**/*',route=>{
  const url=route.request().url();
  if(!url.startsWith('http://127.0.0.1:8004')&&!url.startsWith('data:')){external.push(url);return route.abort()}
  return route.continue();
});
const shot=async name=>{await page.waitForTimeout(500);await page.screenshot({path:path.join(out,name+'.png')})};
const btn=name=>page.getByRole('button',{name,exact:true}).first();

await page.goto('http://127.0.0.1:8004/#/app');
await page.getByRole('heading',{name:/^Operation Trinetra/}).waitFor();
await page.waitForTimeout(900);
await shot('01-network-opening');

await btn('Data Sources').click();
await page.locator('.source-grid>article').first().waitFor();
await shot('02-data-sources');
const nerTab=btn('NER & Reports');
if(await nerTab.isVisible()){await nerTab.click();await page.waitForTimeout(600);await shot('03-record-extraction')}

await btn('Entity Resolution').click();
await page.getByText('Exact shared phone',{exact:true}).waitFor();
await shot('04-entity-resolution');

await btn('Network').click();
await page.getByTestId('entity-graph').waitFor();
await btn('Fit graph').click();
await page.waitForTimeout(700);
await shot('05-network-context');
await page.getByRole('combobox',{name:'Path start',exact:true}).selectOption('rahul');
await page.getByRole('combobox',{name:'Path end',exact:true}).selectOption('vikram');
const pathResponse=page.waitForResponse(r=>r.url().includes('/api/cases/demo/path?')&&r.status()===200);
await btn('Find Path').click();
const computed=await (await pathResponse).json();
if(computed.path_length!==6)throw new Error('Expected six-hop path, got '+computed.path_length);
if(computed.evidence_ids.length!==8)throw new Error('Expected eight path evidence references, got '+computed.evidence_ids.length);
await page.getByRole('heading',{name:'6 hops. Every link inspectable.'}).waitFor();
await page.waitForTimeout(1100);
await shot('06-path-intelligence');

const relatedLead=page.getByRole('button',{name:/17 · HIGH/}).first();
if(await relatedLead.isVisible())await relatedLead.click();
else{await btn('Lead Inbox').click();await page.getByText('Communication and connected transfers',{exact:false}).first().click()}
await page.getByRole('heading',{name:'What happened?',exact:true}).waitFor();
await shot('07-lead-explanation');
const transfer=page.locator('.computed-signal').filter({has:page.locator('summary').filter({hasText:'3 connected transfers'})});
await transfer.locator('summary').first().click();
await transfer.getByRole('button',{name:'Open evidence E-TX-01',exact:true}).click();
await page.getByRole('heading',{name:'transactions-2026-08-15.csv',exact:true}).waitFor();
await shot('08-evidence');

await btn('Back to investigation').click();
await page.locator('.review-disclosure>summary').click();
await page.getByRole('textbox',{name:"Reviewer's name",exact:true}).fill('SIH demo investigator');
await page.getByRole('combobox',{name:'Lead review action',exact:true}).selectOption('NEEDS_MORE_EVIDENCE');
await page.getByRole('textbox',{name:'Review reasoning',exact:true}).fill('Verify original CDR rows and transaction purpose before further inquiry.');
await shot('09-human-review');
await btn('Review submission').click();
await btn('Confirm submission').click();
await page.locator('.review-success').waitFor();
await shot('10-review-recorded');

await btn('Audit Trail').click();
await page.getByRole('combobox',{name:'Activity event type',exact:true}).selectOption('LEAD_REVIEW_SUBMITTED');
await btn('Apply filters').click();
await page.locator('.activity-card').first().waitFor();
await shot('11-audit-trail');

await btn('Network').click();
const pathAgain=page.waitForResponse(r=>r.url().includes('/api/cases/demo/path?')&&r.status()===200);
await btn('Find Path').click(); await pathAgain;
await page.getByRole('heading',{name:'6 hops. Every link inspectable.'}).waitFor();
await shot('12-finale-path');

await writeFile(path.join(out,'capture-verification.json'),JSON.stringify({
  captured_at:new Date().toISOString(),viewport:page.viewportSize(),
  product_title:await page.title(),path_length:computed.path_length,
  path_nodes:computed.node_ids,path_relationships:computed.relationship_ids,
  evidence_references:computed.evidence_ids,
  errors,failed_requests:failed,external_requests:external,
},null,2));
await page.close(); await context.close(); await browser.close();
const files=(await readdir(videoDir)).filter(f=>f.endsWith('.webm'));
if(files.length!==1)throw new Error('Expected one browser recording, found '+files.length);
await rm(path.join(out,'current-flow.webm'),{force:true});
await rename(path.join(videoDir,files[0]),path.join(out,'current-flow.webm'));
if(errors.length||failed.length||external.length)throw new Error(JSON.stringify({errors,failed,external},null,2));
console.log('Captured current Network Intel flow at 1920×1080.');
