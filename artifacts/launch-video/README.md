# VEIL launch film

Open **VEIL-Launch-1080p.mp4**. Runtime: 2 minutes 50 seconds. 1920 × 1080, 30 fps, H.264 video and stereo AAC audio. English subtitles are optional in the MP4 and supplied separately as `VEIL-Launch.srt`.

The film combines real, previously captured VEIL product screens with two excerpts from the retained browser recording, editorial close-ups, gentle camera movement, title cards and short fades. It is an edited launch film, not a continuous live screen recording. All investigation data shown is synthetic. No product features, analytical results or statistics were fabricated for the film.

The male Indian English narration uses Microsoft Prabhat neural speech synthesis. It is AI narration, not a recording of a human performer. The quiet instrumental bed and transition tones were synthesized specifically for this edit; no songs or third-party music recordings are included.

## Edit or reproduce

`render.py` contains the shot list, crops, timing, narration text, music synthesis and export pipeline. `timeline.json` is a readable timeline. Narration MP3s and the mixed WAV are under `audio/`. All original source images and the browser recording remain in the adjacent `../first-round/screenshots/` and `../judge-video/` directories.

Requirements: Python, FFmpeg and FFprobe on PATH, Segoe UI fonts on Windows, and the Python packages Pillow, NumPy and edge-tts. Packages have been installed locally under `vendor/` for this workspace; no application dependency files were changed.

Run from the repository root:

```powershell
python artifacts/launch-video/render.py
```

Previously generated voice files are reused, so the current project rerenders without network access. Regenerating a changed voice segment requires network access to the speech service. When changing a shot, remove only its matching generated MP4 from `clips/` before rerendering. When changing narration, remove only its matching `audio/voice-NN.mp3`.

## Editorial boundaries

- The computed six-hop path is an association search, not a chronological event sequence or a finding of guilt.
- Extraction is described in terms of supported source formats; the film does not claim universal document understanding.
- The evidence retains the exact source locator, excerpt and unverified synthetic-record status.
- The recorded investigator decision is “Needs more evidence”.
- Approximately three seconds after the path explanation are reserved without narration, for the connection to register.

Source provenance: `../../docs/demo/DEMO-RUNBOOK.md`, `../judge-video/README.md`, `../judge-video/sequence.json` and `../first-round/api/path.json` document the prepared scenario, captures and computed path.
