# Network Intel — SIH 26189 premium launch film

The final delivery is `Network-Intel-SIH26189-Premium-1080p.mp4`.

The revised female-voice delivery is `Network-Intel-SIH26189-Premium-Female-1080p.mp4` and is the recommended presentation master.

- Runtime: 2:55
- Master: 1920×1080, 30 fps, H.264 High Profile, 16:9
- Audio: 48 kHz stereo AAC, 192 kbps; measured peak −1.8 dBFS
- Captions: optional English subtitle track embedded in the MP4 and supplied as `Network-Intel-SIH26189.srt`
- Narration: Microsoft Prabhat neural Indian English voice, paced and processed for a calm founder-style delivery
- Music: original synthesized instrumental bed and restrained editorial sound cues; no third-party song recording

## Female voice edition

- Narration: Microsoft Neerja Expressive neural Indian English female voice
- Performance: 28 short spoken beats with intentional pauses, varied pace and subtle pitch changes
- Energy: restrained opening, confident product reveal, faster graph-trace build and warm closing statement
- Processing: high-pass and presence shaping, light compression, music ducking and loudness control
- Timing: speech is generated at its performance rate; no digital time-stretching or `atempo` compression
- Captions: optional English subtitle track embedded in the MP4 and supplied as `Network-Intel-SIH26189-Female.srt`
- Verification: `verification-female.json` records every spoken duration, full-stream decode and delivery specs

The opening motion design uses only identifiers and record types from the synthetic Operation Trinetra scenario. The product section uses fresh 1920×1080 captures and interaction footage from the current Network Intel build. No VEIL-branded image is used in the final video.

The film describes graph search as bounded graph search, not AI. Lead 17 is treated as a computed review lead, identity matching as a human-reviewed proposal, and E-TX-01 as a synthetic source record that is not independently verified.

## Production files

- `PRODUCTION-BIBLE.md`: final narrative, complete storyboard, voiceover, claims audit and production plan locked before rendering
- `capture-current.mjs`: reproducible isolated current-product capture
- `render-premium.py`: motion design, narration, score, sound design, subtitle and master-render pipeline
- `render-female-voice.py`: natural female narration, adaptive performance timing, score remix, subtitles and verified remux
- `captures/capture-verification.json`: captured path nodes, relationships and eight evidence references
- `verification.json`: delivery checks
- `timeline.json`: machine-readable shot and voice timing

To reproduce the capture, run an isolated local server on port 8004 with the state directory in `artifacts/premium-launch/state`, then run `node ../artifacts/premium-launch/capture-current.mjs` from `frontend/`. To rerender, run `python artifacts/premium-launch/render-premium.py` from the repository root. Existing narration files are reused unless their matching MP3 is removed.
