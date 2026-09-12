import {resolve} from 'node:path';
import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./e2e',fullyParallel:false,workers:1,timeout:180000,
 expect:{timeout:10000},reporter:[['list'],['json',{outputFile:'../artifacts/redesign/smoke-results.json'}]],
 use:{actionTimeout:10000,baseURL:'http://127.0.0.1:8001',viewport:{width:1366,height:768},channel:'msedge',headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 webServer:{command:`"${resolve('../.venv/Scripts/python.exe')}" -m backend.serve_demo --port 8001 --state-dir backend/data/smoke --reset`,cwd:'..',url:'http://127.0.0.1:8001/api/cases/demo',reuseExistingServer:false,timeout:60000},
});
