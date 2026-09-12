# VEIL judge video

## Voiced motion edition

`VEIL-SIH-Voiced-Demo.mp4` adds an offline synthesized English voiceover
(Microsoft Zira Desktop), subtle camera moves, short fades, scene headlines,
and sentence captions to the genuine captured product screens. It retains the
165-second storyline. It is an editorial motion treatment of actual captures,
not a new product animation or a claim of continuously recorded mouse motion.
The original silent edition remains available.

Narration: `narration.json`. Voice generation: `voice.ps1`.
Render: `.venv/Scripts/python.exe artifacts/judge-video/render-voiced.py`.
Voice timing measurements: `voice-verification.json`.

VEIL-SIH-Judge-Demo.mp4 is a 165-second, 1920×1080 captioned edit made from
13 genuine browser screenshots captured during an executed product flow.
It uses held product scenes and cuts, not continuous mouse-motion footage.
There is no voiceover or music. Captions are burned in and also supplied as SRT.

The source browser recording is retained as a WebM file. The final MP4 removes
loading/waiting and holds evidence for reading. No analytical results were
mocked. sequence.json includes the actual six-hop response and page-error list.

The sequence used an isolated backend/data/video-demo state on port 8002:
prepared sources, original records, alias review and confirmation, Rahul search,
computed Rahul–Vikram path, computed Lead 17, communication calculation,
transaction calculation, exact evidence, Needs More Evidence review, audit,
and the highlighted path finale.

Render: `.venv/Scripts/python.exe artifacts/judge-video/render.py`.
Capture script: `frontend/record-demo.mjs` (requires a fresh isolated demo on 8002).
No product feature changes were made.
