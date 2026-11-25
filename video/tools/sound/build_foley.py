"""Slice downloaded foley recordings into single hits and write a small, labelled library.
Usage: python3 build_foley.py src_dir out_dir
Short sounds (click, key, tap, pop): each transient becomes its own hit (max 0.45 s), trimmed, faded, -1 dBFS.
Long sounds (swish, slide, scroll): kept whole, trimmed of silence."""
import glob, io, json, os, subprocess, sys
import numpy as np, soundfile as sf

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
SR = 48000
SHORT = ("click", "key", "tap", "pop")

def load(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-f", "wav", "-ar", str(SR), "-ac", "1", "-"], capture_output=True).stdout
    a, _ = sf.read(io.BytesIO(raw)); return a.astype(np.float32)

def env(a, w=0.005):
    n = max(1, int(w * SR)); return np.sqrt(np.convolve(a ** 2, np.ones(n) / n, "same"))

def finish(x, fade_in=0.002, fade_out=0.04):
    n = len(x); f = np.ones(n)
    a, b = int(fade_in * SR), min(n, int(fade_out * SR))
    f[:a] = np.linspace(0, 1, a); f[n - b:] *= np.linspace(1, 0, b)
    x = x * f; return x / (np.abs(x).max() + 1e-9) * 0.89

lib = {}
for p in sorted(glob.glob(f"{src}/*.mp3")):
    name = os.path.basename(p)[:-4]; kind = name.rstrip("0123456789")
    a = load(p)
    if len(a) < SR * 0.05: continue
    e = env(a); thr = e.max() * 0.12
    if kind in SHORT:
        # transients: rising crossings of the threshold, at least 120 ms apart
        on = np.flatnonzero((e[1:] > thr) & (e[:-1] <= thr))
        hits, last = [], -10 ** 9
        for o in on:
            if o - last < 0.12 * SR: continue
            last = o; s = max(0, o - int(0.004 * SR)); seg = a[s: s + int(0.45 * SR)]
            se = env(seg); tail = np.flatnonzero(se > se.max() * 0.02)
            seg = seg[: tail[-1] + int(0.01 * SR)] if len(tail) else seg
            if len(seg) > 0.02 * SR: hits.append(finish(seg))
        for j, h in enumerate(hits[:4]):
            k = f"{name}_{j}"; sf.write(f"{out}/{k}.wav", h, SR, subtype="PCM_24"); lib[k] = {"kind": kind, "dur": round(len(h) / SR, 3)}
    else:
        idx = np.flatnonzero(e > thr * 0.3)
        seg = a[max(0, idx[0] - int(0.01 * SR)): idx[-1] + int(0.05 * SR)]
        k = name; sf.write(f"{out}/{k}.wav", finish(seg, 0.01, 0.15), SR, subtype="PCM_24")
        pk = int(np.argmax(env(seg, 0.02)))
        lib[k] = {"kind": kind, "dur": round(len(seg) / SR, 3), "peak": round(pk / SR, 3)}
json.dump(lib, open(f"{out}/library.json", "w"), indent=1)
from collections import Counter
print(len(lib), "sounds:", dict(Counter(v["kind"] for v in lib.values())))
