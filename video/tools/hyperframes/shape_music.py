"""Shape a music bed to a film: trim onto the beat grid, filter sweeps into drops, gain automation, fades.

Usage: python3 shape_music.py in.wav out.wav plan.json
plan.json: {"offset": 0.425,            # seconds trimmed from the start so a beat lands on t=0
            "length": 30,
            "lpf": [[9.0, 12.4, 280, 3200]],   # cutoff sweeps [t0, t1, f0_hz, f1_hz] (full band outside)
            "gain": [[0, 0], [12.3, 0], [12.35, -24], [12.5, 0]],  # dB points, linear between
            "fade_in": 0.05, "fade_out": [28.6, 30]}
"""
import json, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, resample_poly

src, out, plan = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
a, sr = sf.read(src, always_2d=True)
if sr != 48000:
    a = resample_poly(a, 48000, sr, axis=0); sr = 48000
a = a[int(plan.get("offset", 0) * sr):]
n = int(plan["length"] * sr)
a = np.pad(a, ((0, max(0, n - len(a))), (0, 0)))[:n]
t = np.arange(n) / sr

# filter sweep: blend between log-spaced low-passed copies, so the cutoff glides without zipper noise
cut = np.full(n, 20000.0)
for t0, t1, f0, f1 in plan.get("lpf", []):
    m = (t >= t0) & (t < t1)
    p = (t[m] - t0) / (t1 - t0)
    cut[m] = f0 * (f1 / f0) ** (p ** 1.6)
if (cut < 20000).any():
    freqs = np.geomspace(cut.min() * 0.9, 20000, 14)
    bank = [a if f >= 19000 else sosfiltfilt(butter(4, f, fs=sr, output="sos"), a, axis=0) for f in freqs]
    pos = np.interp(np.log(cut), np.log(freqs), np.arange(len(freqs)))
    lo = np.floor(pos).astype(int); hi = np.minimum(lo + 1, len(freqs) - 1); w = (pos - lo)[:, None]
    bankarr = np.stack(bank)
    a = bankarr[lo, np.arange(n)] * (1 - w) + bankarr[hi, np.arange(n)] * w

pts = plan.get("gain", [[0, 0]])
g = 10 ** (np.interp(t, [p[0] for p in pts], [p[1] for p in pts]) / 20)
fi = plan.get("fade_in", 0.02)
g *= np.clip(t / max(fi, 1e-3), 0, 1)
if "fade_out" in plan:
    f0, f1 = plan["fade_out"]; g *= np.clip((f1 - t) / (f1 - f0), 0, 1) ** 1.5
a = a * g[:, None]
sf.write(out, a.astype(np.float32), sr, subtype="PCM_24")
print("wrote", out, f"{n / sr:.2f}s")
