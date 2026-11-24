"""Builds the explainer's soundtrack and timing.

1. Speaks each narration line with Kokoro TTS (kokoro-onnx).
2. Lays the lines out scene by scene and writes timeline.js, which explainer.html reads,
   so scene lengths and captions follow the voice.
3. Synthesises an original music bed and sound effects (no samples, no licensing).
4. Mixes voice, music (ducked under the voice) and effects into a WAV.

Usage:
  python3 video/build_audio.py <kokoro-model-dir> <out.wav>
The model dir needs kokoro-v1.0.int8.onnx and voices-v1.0.bin from
https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0).
Needs: pip install kokoro-onnx soundfile numpy scipy
"""

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, resample_poly, sosfilt

HERE = Path(__file__).parent
SR = 48000
VOICE = "am_michael"
SPEED = 1.1

# One entry per scene, in the same order as the <section class="scene"> elements.
# min: shortest the scene may be, so its animations finish. Lines: (caption, spoken text).
SCENES = [
    {"min": 5.5, "lines": [
        ("Hi, I’m John Godwin Oamien.", "Hi, I'm John Godwin Oamien."),
        ("A software developer, and a trained environmental engineer.", "A software developer, and a trained environmental engineer."),
    ]},
    {"min": 4.5, "lines": [
        ("My portfolio has two sides: software and engineering.", "My portfolio has two sides: software, and engineering."),
    ]},
    {"min": 9.2, "lines": [
        ("I built JOPAD Advisory’s booking platform.", "I built Jopad Advisory's booking platform."),
        ("Clients book a call, and the invite, Meet link and emails go out on their own.", "Clients book a call, and the invite, Meet link and emails go out on their own."),
    ]},
    {"min": 6.0, "lines": [
        ("Also a React and TypeScript fundraising site, and a concept studio site.", "Also a React and TypeScript fundraising site, and a concept studio site."),
    ]},
    {"min": 4.6, "lines": [
        ("Plus fourteen Frontend Mentor solutions.", "Plus fourteen Frontend Mentor solutions."),
    ]},
    {"min": 7.5, "lines": [
        ("At the NDDC, I inspected solar street-light projects.", "At the N.D.D.C., I inspected solar street-light projects."),
        ("Measuring plinths and poles, checking earthing, and testing lights at night.", "Measuring plinths and poles, checking earthing, and testing lights at night."),
    ]},
    {"min": 7.4, "lines": [
        ("For my final-year research, I weighed 150 kg of hostel waste.", "For my final-year research, I weighed a hundred and fifty kilos of hostel waste."),
        ("The female hostel made five times more. Around 80% was plastic.", "The female hostel made five times more. Around eighty percent was plastic."),
    ]},
    {"min": 6.0, "lines": [
        ("Pick the side of my work you came to see.", "Pick the side of my work you came to see."),
    ]},
]
LEAD = 0.45   # silence at the start of each scene before the voice
GAP = 0.3     # pause between lines
TAIL = 0.45   # pause after the last line before the scene cuts
TARGET = 60.0  # total length; the outro is stretched to reach it


def speak(model_dir):
    from kokoro_onnx import Kokoro

    k = Kokoro(f"{model_dir}/kokoro-v1.0.int8.onnx", f"{model_dir}/voices-v1.0.bin")
    out = []
    for scene in SCENES:
        clips = []
        for caption, spoken in scene["lines"]:
            a, sr = k.create(spoken, voice=VOICE, speed=SPEED, lang="en-us")
            a = resample_poly(a.astype(np.float64), SR, sr)
            # trim leading/trailing near-silence so the layout is tight
            idx = np.where(np.abs(a) > 0.01)[0]
            a = a[max(idx[0] - 480, 0): idx[-1] + 2400]
            clips.append((caption, a))
        out.append(clips)
    return out


def layout(spoken):
    scenes, captions, voice_at = [], [], []
    t = 0.0
    for i, (scene, clips) in enumerate(zip(SCENES, spoken)):
        start = t
        cur = start + (0.6 if i == 0 else LEAD)
        for caption, a in clips:
            d = len(a) / SR
            voice_at.append((cur, a))
            captions.append([round(cur - 0.1, 3), round(cur + d + 0.2, 3), caption, i])
            cur += d + GAP
        end = max(start + scene["min"], cur - GAP + TAIL)
        scenes.append([round(start, 3), round(end, 3)])
        t = end
    # the last scene holds the outro until the target length
    if t < TARGET:
        scenes[-1][1] = round(TARGET, 3)
        t = TARGET
    # hold captions within a scene until the next line starts, never past the scene's end
    for a, b in zip(captions, captions[1:]):
        if a[3] == b[3] and b[0] - a[1] < 0.6:
            a[1] = b[0] - 0.02
    for c in captions:
        c[1] = min(c[1], scenes[c[3]][1] - 0.05)
    return scenes, [c[:3] for c in captions], voice_at, t


# ---------------------------------------------------------------- synthesis helpers
def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tone(freq, dur, harmonics=1, detune=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for h in range(1, harmonics + 1):
        for dt in ((-detune, detune) if detune else (0.0,)):
            y += np.sin(2 * np.pi * freq * (1 + dt) * h * t) / h
    return y


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[n - nr:] *= np.linspace(1, 0, nr)
    return e


def lp(y, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), y)


def hp(y, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), y)


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i] * gain


# ---------------------------------------------------------------- music
def music(total):
    n = int(total * SR)
    pad, bass, arp, drums = (np.zeros(n) for _ in range(4))
    beat = 60 / 96
    bar = beat * 4
    chords = [(50, 54, 57, 61), (47, 50, 54, 57), (43, 47, 50, 54), (45, 49, 52, 54)]  # Dmaj7 Bm7 Gmaj7 A6
    seg = bar * 2
    k = 0
    t = 0.0
    while t < total:
        notes = chords[k % 4]
        clip = sum(tone(midi(m), seg + 0.6, harmonics=6, detune=0.002) for m in notes)
        clip = lp(clip, 1400) * env_adsr(len(clip), 0.6, 0.6)
        place(pad, clip, t, 0.05)
        root = midi(notes[0] - 12)
        for b in range(0, 8, 2):  # bass on beats 1 and 3
            bt = t + b * beat
            if bt < 2.5:
                continue
            c = tone(root, beat * 1.8, harmonics=3) * np.exp(-np.arange(int(beat * 1.8 * SR)) / SR * 2.2)
            place(bass, lp(c, 500), bt, 0.22)
        for s in range(16):  # eighth-note arpeggio
            at = t + s * beat / 2
            if at < 6 or at > total - 3.5:
                continue
            m = notes[[0, 2, 1, 3, 2, 1, 3, 2][s % 8]] + 12
            d = 0.35
            c = (tone(midi(m), d) + tone(midi(m) * 3, d) / 9) * np.exp(-np.arange(int(d * SR)) / SR * 11)
            place(arp, c * env_adsr(len(c), 0.004, 0.02), at, 0.07)
        t += seg
        k += 1
    # light drums from 2.5 s
    kick_n = int(0.3 * SR)
    kt = np.arange(kick_n) / SR
    kick = np.sin(2 * np.pi * (45 * kt + 90 / 25 * (1 - np.exp(-25 * kt)))) * np.exp(-kt * 14)
    rng = np.random.default_rng(7)
    hat = hp(rng.standard_normal(int(0.05 * SR)), 7000) * np.exp(-np.arange(int(0.05 * SR)) / SR * 90)
    bt = 2.5
    i = 0
    while bt < total - 3.0:
        if i % 2 == 0:
            place(drums, kick, bt, 0.35)
        if bt > 6:
            place(drums, hat, bt + beat / 2, 0.06)
        bt += beat
        i += 1
    mix = pad + bass + arp + drums
    fade = np.ones(n)
    fade[: int(1.5 * SR)] = np.linspace(0, 1, int(1.5 * SR))
    fade[-int(3 * SR):] = np.linspace(1, 0, int(3 * SR)) ** 1.5
    return mix * fade


# ---------------------------------------------------------------- sound effects
def whoosh(dur=0.7):
    n = int(dur * SR)
    rng = np.random.default_rng(1)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    # sweep a band upward by mixing progressively brighter filtered copies
    steps = 12
    for s in range(steps):
        f = 300 * (12 ** (s / steps))
        band = sosfilt(butter(2, [f, f * 1.6], "band", fs=SR, output="sos"), noise)
        w = np.exp(-((np.arange(n) / n - s / steps) ** 2) / 0.01)
        out += band * w
    return out * np.sin(np.pi * np.arange(n) / n) ** 2 * 0.9


def tick(f=1800, d=0.05):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 70)


def pop(f0=900, f1=500, d=0.08):
    t = np.arange(int(d * SR)) / SR
    f = f0 + (f1 - f0) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)


def riser(d):
    t = np.arange(int(d * SR)) / SR
    f = 300 * (2.5 ** (t / d))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) * (1 - np.exp(-(d - t) * 30))
    return y * 0.5


def chime():
    d = 2.5
    t = np.arange(int(d * SR)) / SR
    y = np.zeros_like(t)
    for m, g in ((74, 1.0), (81, 0.6), (86, 0.4), (93, 0.2)):
        y += g * np.sin(2 * np.pi * midi(m) * t) * np.exp(-t * (2.5 + m / 40))
    return y * 0.5


def boom():
    d = 1.4
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * (40 * t + 60 / 6 * (1 - np.exp(-6 * t)))) * np.exp(-t * 3.5)


def effects(total, scenes):
    n = int(total * SR)
    fx = np.zeros(n)
    s = [a for a, _ in scenes]
    place(fx, boom(), 0.35, 0.5)
    for start in s[1:]:
        place(fx, whoosh(), start - 0.35, 0.22)
    for lt in (5.2, 6.2, 7.2, 8.2):  # JOPAD flow steps light up
        place(fx, tick(1600 + lt * 60), s[2] + lt, 0.25)
    for i in range(15):  # Frontend Mentor wall
        place(fx, tick(2200 + (i % 5) * 120, 0.03), s[4] + 0.05 + i * 0.07, 0.08)
    place(fx, riser(1.6), s[4] + 1.2, 0.2)
    place(fx, pop(1200, 700), s[4] + 2.8, 0.3)
    for lt in (0.8, 1.1, 1.4, 1.7):  # field photos
        place(fx, pop(), s[5] + lt, 0.18)
    for lt in (1.6, 2.4, 3.2, 4.0):  # checklist
        place(fx, tick(1400), s[5] + lt, 0.2)
    place(fx, riser(2.2), s[6] + 1.0, 0.18)
    place(fx, pop(1100, 650), s[6] + 3.2, 0.25)
    place(fx, whoosh(0.9), s[6] + 2.9, 0.12)
    place(fx, chime(), s[7] + 1.8, 0.35)
    return fx


def main():
    model_dir, out_wav = sys.argv[1], sys.argv[2]
    spoken = speak(model_dir)
    scenes, captions, voice_at, total = layout(spoken)
    print(f"total {total:.2f}s")
    for (a, b), sc in zip(scenes, SCENES):
        print(f"  scene {a:6.2f} – {b:6.2f}  ({b - a:4.2f}s)")
    (HERE / "timeline.js").write_text(
        "// Generated by build_audio.py. Scene times follow the voiceover.\n"
        "window.TIMELINE = " + json.dumps({"duration": round(total, 3), "scenes": scenes, "captions": captions}, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )

    n = int(total * SR) + SR
    voice = np.zeros(n)
    duck = np.zeros(n)
    for at, a in voice_at:
        place(voice, a, at)
        i, j = int((at - 0.15) * SR), int((at + len(a) / SR + 0.25) * SR)
        duck[max(i, 0): j] = 1
    k = int(0.25 * SR)
    duck = np.convolve(duck, np.ones(k) / k, mode="same")  # smooth ramps
    m = np.pad(music(total), (0, SR))
    fx = np.pad(effects(total, scenes), (0, SR))
    voice = voice / (np.abs(voice).max() + 1e-9) * 0.9
    rms = lambda x: np.sqrt((x[np.abs(x) > 1e-4] ** 2).mean())
    # music sits 10 dB under the voice, then ducks a further 9 dB while someone is speaking
    m *= rms(voice) / rms(m) * 10 ** (-10 / 20)
    fx *= rms(voice) / rms(fx) * 10 ** (-10 / 20)
    mix = voice + m * (1 - 0.65 * duck) + fx * (1 - 0.3 * duck)
    mix = mix[: int(total * SR)]
    mix = mix / np.abs(mix).max() * 0.89
    sf.write(out_wav, np.stack([mix, mix], axis=1), SR, subtype="PCM_16")
    print("wrote", out_wav)


if __name__ == "__main__":
    main()
