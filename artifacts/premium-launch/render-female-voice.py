"""Create the natural female-narration edition of the Network Intel launch film."""
from __future__ import annotations

import asyncio
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT.parent / "launch-video" / "vendor"
sys.path.insert(0, str(VENDOR))

import edge_tts
import numpy as np

DURATION = 175
SR = 48_000
VOICE = "en-IN-NeerjaExpressiveNeural"
AUDIO = ROOT / "audio-female"
AUDIO.mkdir(exist_ok=True)
SOURCE = ROOT / "Network-Intel-SIH26189-Premium-1080p.mp4"
OUTPUT = ROOT / "Network-Intel-SIH26189-Premium-Female-1080p.mp4"
SRT = ROOT / "Network-Intel-SIH26189-Female.srt"
MASTER = AUDIO / "female-master.wav"

# Short performance beats preserve phrasing and let silence do part of the storytelling.
# rate and pitch change by act, giving the reveal and graph trace more lift while the
# evidence section settles into a calm, authoritative delivery.
VOICEOVER = [
    (0.70, 5.85, "A criminal network rarely appears in a single file.", "-4%", "-1Hz"),
    (6.55, 10.55, "It appears in fragments.", "-5%", "-1Hz"),
    (10.50, 15.25, "A name, a phone number, an account, a location.", "+2%", "+0Hz"),
    (15.35, 19.25, "The evidence is there.", "-5%", "-1Hz"),
    (19.75, 23.05, "But the connection can stay buried.", "-3%", "-1Hz"),
    (23.75, 30.10, "And as records multiply, manual review becomes slower... and harder to scale.", "+1%", "+0Hz"),
    (33.00, 39.45, "So, what if every fragment could become part of one connected investigation?", "+1%", "+1Hz"),
    (42.45, 46.15, "This is Network Intel.", "+2%", "+1Hz"),
    (49.60, 55.80, "It turns supported investigation records into entities an investigator can work with.", "+1%", "+0Hz"),
    (56.20, 64.80, "People, phones, accounts, vehicles, and locations, all connected to their source.", "+2%", "+1Hz"),
    (67.00, 72.65, "The same person may appear differently across different records.", "-1%", "+0Hz"),
    (73.00, 79.70, "Network Intel proposes a possible match, then leaves the decision with the investigator.", "+1%", "+0Hz"),
    (82.00, 87.10, "Now, those scattered relationships begin to form a network.", "+2%", "+1Hz"),
    (87.45, 98.00, "People, devices, and accounts can be explored together, without losing the evidence behind them.", "+2%", "+1Hz"),
    (101.00, 105.75, "Here is the question that matters.", "+3%", "+1Hz"),
    (106.10, 110.75, "How are Rahul Sharma and Vikram Singh connected?", "+4%", "+2Hz"),
    (111.15, 115.55, "Network Intel traces the graph.", "+5%", "+2Hz"),
    (115.90, 122.75, "One sourced step at a time... a six-hop association emerges.", "+4%", "+2Hz"),
    (125.00, 128.55, "And this is where trust matters.", "-3%", "-1Hz"),
    (128.90, 132.65, "Investigations can't depend on a black box.", "-3%", "-1Hz"),
    (134.00, 139.50, "Open the lead, and the path returns to evidence.", "-2%", "+0Hz"),
    (139.55, 145.98, "The exact file, row, timestamp, verification status, and original excerpt.", "+1%", "+0Hz"),
    (146.00, 151.35, "The system surfaces the connection. The evidence supports review.", "-1%", "+0Hz"),
    (151.70, 157.90, "But the investigator remains the final authority.", "-2%", "-1Hz"),
    (160.00, 164.50, "Less manual cross-referencing.", "+2%", "+1Hz"),
    (164.75, 168.45, "Non-obvious paths, made visible.", "+3%", "+1Hz"),
    (169.00, 171.85, "The evidence may already be there.", "-2%", "+0Hz"),
    (171.95, 174.90, "Network Intel reveals the connection.", "+4%", "+1Hz"),
]


def run(args: list[str | Path]) -> bytes:
    result = subprocess.run([str(a) for a in args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", "replace")[-5000:])
    return result.stdout


def ff(*args: str | Path) -> None:
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode().strip())


def bump_rate(rate: str, amount: int) -> str:
    return f"{int(rate.rstrip('%')) + amount:+d}%"


async def make_voices() -> list[dict]:
    report = []
    for i, (start, end, text, base_rate, pitch) in enumerate(VOICEOVER):
        mp3 = AUDIO / f"voice-{i:02d}.mp3"
        chosen_rate = base_rate
        # Re-generate rather than digitally time-compress. Most clips fit at their
        # performance rate; the fallback only asks the voice model to speak faster.
        for bump in (0, 4, 8, 12, 16):
            chosen_rate = bump_rate(base_rate, bump)
            await edge_tts.Communicate(text, VOICE, rate=chosen_rate, pitch=pitch, volume="+2%").save(str(mp3))
            spoken = duration(mp3)
            if spoken <= end - start:
                break
        if spoken > end - start:
            raise RuntimeError(f"Voice clip {i} is {spoken:.2f}s but its window is only {end-start:.2f}s")
        report.append({"index": i, "start": start, "window_end": end, "spoken_end": round(start + spoken, 3), "duration": round(spoken, 3), "rate": chosen_rate, "pitch": pitch, "text": text})
        print(f"voice {i:02d}: {spoken:.2f}s at {chosen_rate}", flush=True)
    return report


def music_stem(t: np.ndarray) -> np.ndarray:
    music = np.zeros(len(t), np.float64)
    roots = [55, 55, 65.406, 73.416, 55, 82.407, 73.416]
    bounds = [0, 31, 49, 100, 124, 159, 169, 175]
    for j, freq in enumerate(roots):
        mask = (t >= bounds[j]) & (t < bounds[j + 1])
        local = t[mask] - bounds[j]
        attack = np.minimum(1, local / 2)
        release = np.minimum(1, (bounds[j + 1] - t[mask]) / 2)
        env = attack * release
        music[mask] += env * (
            .010 * np.sin(2 * np.pi * freq * local)
            + .005 * np.sin(2 * np.pi * freq * 1.5 * local)
            + .003 * np.sin(2 * np.pi * freq * 2 * local)
        )
    pulse = np.interp(t, [0, 8, 31, 41, 49, 100, 106, 118, 124, 145, 159, 169, 175], [.25, .35, .55, .25, .70, .80, 1.05, 1.35, .70, .38, .70, .68, 0])
    for beat in np.arange(1, DURATION, 1.5):
        a = int(beat * SR)
        n = min(int(.45 * SR), len(t) - a)
        u = np.arange(n) / SR
        music[a:a+n] += .010 * pulse[a] * np.sin(2*np.pi*(110 + 25*np.exp(-u*9))*u) * np.exp(-u*8)
    for when, note in [(41, 440), (49, 523.25), (106, 392), (108, 440), (110, 493.88), (112, 523.25), (114, 587.33), (116, 659.25), (118, 783.99), (169, 523.25)]:
        a = int(when * SR)
        n = min(int(2.8 * SR), len(t) - a)
        u = np.arange(n) / SR
        music[a:a+n] += .013 * np.sin(2*np.pi*note*u) * np.exp(-u*1.4) * (1-np.exp(-u*18))
    # Slowly varying air without an expensive full-length convolution.
    rng = np.random.default_rng(26189)
    control_t = np.arange(0, DURATION + .25, .25)
    air = np.interp(t, control_t, rng.normal(0, 1, len(control_t)))
    music += air * .00045 * np.interp(t, [0, 31, 49, 124, 145, 175], [1, .8, .35, .2, .25, 0])
    return music


def stamp(value: float) -> str:
    ms = round(value * 1000)
    return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"


def mix_audio(report: list[dict]) -> None:
    t = np.arange(SR * DURATION, dtype=np.float64) / SR
    music = music_stem(t)
    duck = np.ones(len(t), np.float64)
    for item in report:
        a = max(0, int((item["start"] - .18) * SR))
        b = min(len(t), int((item["spoken_end"] + .28) * SR))
        attack = min(int(.16 * SR), max(1, b-a))
        release = min(int(.28 * SR), max(1, b-a))
        duck[a:b] = np.minimum(duck[a:b], .46)
        duck[a:a+attack] = np.minimum(duck[a:a+attack], np.linspace(1, .46, attack))
        duck[b-release:b] = np.minimum(duck[b-release:b], np.linspace(.46, 1, release))
    stereo = np.column_stack((music * duck, music * duck * .97))
    subtitles = []
    for item in report:
        i = item["index"]
        raw = AUDIO / f"voice-{i:02d}.f32"
        ff("-i", AUDIO / f"voice-{i:02d}.mp3", "-af", "highpass=f=75,lowpass=f=13500,equalizer=f=2800:t=q:w=1.2:g=1.0,acompressor=threshold=-21dB:ratio=2:attack=12:release=150,loudnorm=I=-16.5:TP=-2:LRA=7", "-ar", str(SR), "-ac", "1", "-f", "f32le", raw)
        voice = np.fromfile(raw, np.float32)
        start = round(item["start"] * SR)
        n = min(len(voice), len(t) - start)
        # Centered narration, with a tiny stereo spread for a polished voice-over image.
        stereo[start:start+n, 0] += voice[:n] * .985
        stereo[start:start+n, 1] += voice[:n]
        subtitles.append((item["start"], item["start"] + n/SR, item["text"]))
    cues = [(1.1, 620, .010), (3.1, 720, .009), (7.2, 560, .009), (9.0, 680, .009), (41.2, 880, .015), (49.0, 1046, .014)]
    cues += [(106+i*1.65, 520+i*75, .0125) for i in range(7)]
    cues += [(133.3, 760, .009), (145.1, 900, .010), (152.0, 660, .010), (169.1, 1046, .013)]
    for when, freq, level in cues:
        a = int(when * SR)
        n = min(int(.25 * SR), len(t)-a)
        u = np.arange(n)/SR
        cue = level*np.sin(2*np.pi*freq*u)*np.exp(-u*20)*(1-np.exp(-u*90))
        stereo[a:a+n] += cue[:, None]
    peak = float(np.max(np.abs(stereo)))
    stereo *= min(1, .81/peak)  # conservative headroom before AAC encoding
    with wave.open(str(MASTER), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes((stereo*32767).astype("<i2").tobytes())
    SRT.write_text("\n\n".join(f"{i+1}\n{stamp(a)} --> {stamp(b)}\n{text}" for i, (a, b, text) in enumerate(subtitles)), encoding="utf-8")


def mux() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    ff("-i", SOURCE, "-i", MASTER, "-i", SRT, "-map", "0:v:0", "-map", "1:a:0", "-map", "2:s:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-metadata", "title=Network Intel | SIH 26189 | Female Voice Edition", "-movflags", "+faststart", "-t", str(DURATION), OUTPUT)


def verify(report: list[dict]) -> None:
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", OUTPUT]))
    decode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(OUTPUT), "-f", "null", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if decode.returncode:
        raise RuntimeError(decode.stderr.decode("utf-8", "replace")[-5000:])
    loudness = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(OUTPUT), "-map", "0:a:0", "-af", "volumedetect", "-f", "null", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    loud_text = loudness.stderr.decode("utf-8", "replace")
    measured = [line.strip() for line in loud_text.splitlines() if "mean_volume" in line or "max_volume" in line]
    result = {
        "file": OUTPUT.name,
        "voice": VOICE,
        "duration": float(probe["format"]["duration"]),
        "streams": [{"type": s["codec_type"], "codec": s["codec_name"], "width": s.get("width"), "height": s.get("height"), "sample_rate": s.get("sample_rate"), "channels": s.get("channels")} for s in probe["streams"]],
        "audio_measurements": measured,
        "full_decode": "passed",
        "no_time_stretching": True,
        "voice_clips": report,
    }
    (ROOT / "verification-female.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "duration": result["duration"], "audio": measured}, indent=2), flush=True)


async def main() -> None:
    report = await make_voices()
    mix_audio(report)
    mux()
    verify(report)


if __name__ == "__main__":
    asyncio.run(main())
