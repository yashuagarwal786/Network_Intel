import {PresentationFile,FileBlob} from '@oai/artifact-tool';
import fs from 'node:fs/promises';
console.log('import start');
const p=await PresentationFile.importPptx(await FileBlob.load('Z:/XLab/New/Network Intel/artifacts/hackathon-pack/.build/candidate.pptx'));
console.log('import success', p.slides.items.length);
process.exit(0);
