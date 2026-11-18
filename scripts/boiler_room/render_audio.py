#!/usr/bin/env python3
"""Boiler Room narration renderer.

Usage: python3 render_audio.py SCRIPT.txt OUT.mp3 [--voice af_heart] [--speed 1.0] [--title "..."]

Script format: paragraphs separated by blank lines; a line '--- Label' (e.g. '--- News') is a section
break and starts a chapter with that label. The first chapter is 'Intro'.
Needs: pip install kokoro-onnx soundfile ; ffmpeg. Downloads the Kokoro model from GitHub releases
into ~/.cache/boiler-room on first run. Prints a JSON line with duration_sec and bytes.
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

import numpy as np

MODEL_URLS = {
    "kokoro-v1.0.int8.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}
SR = 24000


def ensure_models(cache: Path):
    cache.mkdir(parents=True, exist_ok=True)
    for name, url in MODEL_URLS.items():
        p = cache / name
        if not p.exists() or p.stat().st_size < 1_000_000:
            subprocess.run(["curl", "-sSL", "--retry", "3", "-o", str(p), url], check=True)
    return cache / "kokoro-v1.0.int8.onnx", cache / "voices-v1.0.bin"


def chime(seconds=1.4):
    """Two soft bell tones, used as the intro and outro sting."""
    t = np.linspace(0, seconds, int(SR * seconds), endpoint=False)
    out = np.zeros_like(t)
    for f, start, amp in ((659.25, 0.0, 0.16), (987.77, 0.18, 0.12)):
        tt = np.clip(t - start, 0, None)
        env = np.where(t >= start, np.exp(-tt * 3.2), 0.0)
        out += amp * env * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt))
    fade = np.minimum(1.0, np.linspace(0, 40, len(t)))
    return (out * fade).astype(np.float32)


def chunks_for(paragraph: str, limit=360):
    sentences = re.split(r"(?<=[.!?])\s+", paragraph.strip())
    buf = ""
    for s in sentences:
        if buf and len(buf) + 1 + len(s) > limit:
            yield buf
            buf = s
        else:
            buf = f"{buf} {s}".strip()
    if buf:
        yield buf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("out")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--title", default="Boiler Room")
    ap.add_argument("--cache", default=str(Path.home() / ".cache" / "boiler-room"))
    a = ap.parse_args()

    from kokoro_onnx import Kokoro

    model, voices = ensure_models(Path(a.cache))
    k = Kokoro(str(model), str(voices))

    text = Path(a.script).read_text(encoding="utf-8")
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]

    def silence(sec):
        return np.zeros(int(SR * sec), dtype=np.float32)

    parts = [chime(), silence(0.5)]
    chapters = [{"label": "Intro", "start": 0.0}]
    t0 = time.time()
    for b in blocks:
        if b.startswith("---"):
            parts.append(silence(0.9))
            label = b.lstrip("-").strip() or f"Part {len(chapters) + 1}"
            chapters.append({"label": label, "start": round(sum(len(p) for p in parts) / SR, 1)})
            continue
        for c in chunks_for(b):
            audio, sr = k.create(c, voice=a.voice, speed=a.speed, lang="en-us")
            assert sr == SR, sr
            parts.append(audio.astype(np.float32))
            parts.append(silence(0.22))
        parts.append(silence(0.45))
    parts += [silence(0.4), chime()]
    pcm = np.concatenate(parts)
    peak = float(np.max(np.abs(pcm))) or 1.0
    pcm = (pcm / peak * 0.89).astype(np.float32)

    wav = Path(a.out).with_suffix(".wav")
    import soundfile as sf
    sf.write(str(wav), pcm, SR)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ac", "1", "-ar", "24000", "-codec:a", "libmp3lame", "-b:a", "48k",
        "-metadata", f"title={a.title}", "-metadata", "artist=Boiler Room",
        "-metadata", "album=Boiler Room", "-metadata", "genre=Podcast",
        a.out,
    ], check=True)
    wav.unlink()
    dur = len(pcm) / SR
    print(json.dumps({"duration_sec": round(dur, 1), "bytes": os.path.getsize(a.out),
                      "chapters": chapters,
                      "render_sec": round(time.time() - t0, 1),
                      "words": len(re.findall(r"\b\w[\w'-]*\b", text))}))


if __name__ == "__main__":
    main()
