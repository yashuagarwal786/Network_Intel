import {PresentationFile,FileBlob} from '@oai/artifact-tool';
import fs from 'node:fs/promises';
const W='Z:/XLab/New/Network Intel/artifacts/hackathon-pack';
const p=await PresentationFile.importPptx(await FileBlob.load(W+'/output/Network-Intel-Internal-Hackathon-Hinglish.pptx'));
await fs.mkdir(W+'/.build/final-render',{recursive:true});
for(let i=0;i<p.slides.items.length;i++){const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(W+'/.build/final-render/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await b.arrayBuffer()));console.log('Final render',i+1);}
