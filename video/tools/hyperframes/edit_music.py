"""Cut a music track into a film-length bed from an edit list, with short fades at every edit.
Usage: python3 edit_music.py track.(mp3|wav) out.wav edits.json
edits.json: {"length": 60, "edits": [[film_start, track_start, duration, fade_in, fade_out], ...]}
Gaps between edits stay silent: that is where the picture rests."""
import io, json, subprocess, sys
import numpy as np, soundfile as sf

src, out, plan = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "wav", "-ar", "48000", "-ac", "2", "-"], capture_output=True, check=True).stdout
a, sr = sf.read(io.BytesIO(raw), always_2d=True)
bed = np.zeros((int(plan["length"] * sr), 2))
for fs, ts, dur, fi, fo in plan["edits"]:
    seg = a[int(ts * sr): int((ts + dur) * sr)].copy()
    n = len(seg); t = np.arange(n) / sr
    env = np.clip(t / max(fi, 1e-3), 0, 1) * np.clip((dur - t) / max(fo, 1e-3), 0, 1)
    seg *= env[:, None]
    i0 = int(fs * sr); bed[i0:i0 + n] += seg[: len(bed) - i0]
sf.write(out, bed.astype(np.float32), sr, subtype="PCM_24")
print("wrote", out, f"{len(bed) / sr:.1f}s, {len(plan['edits'])} edits")
