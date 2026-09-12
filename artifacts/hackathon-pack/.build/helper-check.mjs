import {importRuntimeModule} from 'file:///C:/Users/tanis/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations/container_tools/runtime_helpers.mjs';
console.log('helper start');
const {PresentationFile, FileBlob}=await importRuntimeModule('@oai/artifact-tool');
console.log('loaded module');
const p=await PresentationFile.importPptx(await FileBlob.load('Z:/XLab/New/Network Intel/artifacts/hackathon-pack/.chart-data-Lnjve7/candidate.pptx'));
console.log('success',p.slides.items.length);
