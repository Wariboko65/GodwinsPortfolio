"""Make rotated takes of the bundled SFX with more depth: slowed/pitched-down versions and a
low-shelf + short-room 'deep' version. Usage: python3 sfx_variants.py sfx_dir out_dir"""
import os, subprocess, io, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from pedalboard import Pedalboard, LowShelfFilter, HighShelfFilter, Reverb, Compressor, HighpassFilter

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
def load(name):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f"{src}/{name}.mp3", "-f", "wav", "-ar", "48000", "-ac", "2", "-"], capture_output=True).stdout
    a, sr = sf.read(io.BytesIO(raw), always_2d=True); return a.T.astype(np.float32)
def slow(a, ratio):  # play slower and lower, like a tape slowed down
    return resample_poly(a, int(round(ratio * 100)), 100, axis=1).astype(np.float32)
deep = Pedalboard([HighpassFilter(28), LowShelfFilter(cutoff_frequency_hz=120, gain_db=4.5), HighShelfFilter(cutoff_frequency_hz=7000, gain_db=-2),
                   Compressor(threshold_db=-14, ratio=2.5, attack_ms=5, release_ms=120), Reverb(room_size=0.35, damping=0.6, wet_level=0.16, dry_level=0.9, width=1.0)])
def save(name, a):
    a = a / max(1e-6, np.abs(a).max()) * 0.89  # -1 dBFS peak
    sf.write(f"{out}/{name}.wav", a.T, 48000, subtype="PCM_24")
for name in ["whoosh", "pop", "click-soft", "key-press", "impact-bass-1", "impact-bass-2", "riser", "whoosh-cinematic"]:
    a = load(name)
    save(name, deep(a, 48000))
    if name in ("whoosh", "pop", "key-press"):
        save(name + "-lo", deep(slow(a, 1.18), 48000))
        save(name + "-lo2", deep(slow(a, 1.4), 48000))
print("ok", sorted(os.listdir(out)))
