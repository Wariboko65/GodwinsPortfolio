"""Builds the explainer's soundtrack and timing: music and sound effects only, no voice.

The edit is locked to the music. At 96 BPM one bar is 2.5 s, and every scene is a whole
number of bars, so each cut lands on a downbeat with a hit under it.

1. Writes timeline.js (scene start/end times), which explainer.html reads.
2. Synthesises an original music bed and sound effects (no samples, no licensing).
3. Mixes them into a stereo WAV for render.mjs to mux into the MP4.

Usage:
  python3 video/build_audio.py <out.wav>
Needs: pip install numpy scipy soundfile
"""

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

HERE = Path(__file__).parent
SR = 48000
BPM = 96
BEAT = 60 / BPM
BAR = BEAT * 4

# Bars per scene, in the order of the <section class="scene"> elements:
# intro, two profiles, JOPAD, Jason + Vortex, Frontend Mentor, NDDC, waste study, outro.
SCENE_BARS = [2, 2, 4, 3, 2, 4, 4, 3]


def timeline():
    scenes, t = [], 0.0
    for bars in SCENE_BARS:
        scenes.append([round(t, 3), round(t + bars * BAR, 3)])
        t += bars * BAR
    return scenes, t


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


def decay(d, rate):
    return np.exp(-np.arange(int(d * SR)) / SR * rate)


def lp(y, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), y)


def hp(y, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), y)


def bp(y, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), y)


def place(buf, clip, at, gain=1.0):
    i = int(round(at * SR))
    if i >= len(buf) or i + len(clip) <= 0:
        return
    if i < 0:
        clip, i = clip[-i:], 0
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i] * gain


RNG = np.random.default_rng(7)


def noise(d):
    return RNG.standard_normal(int(d * SR))


# ---------------------------------------------------------------- drum and fx voices
def kick():
    t = np.arange(int(0.35 * SR)) / SR
    return np.sin(2 * np.pi * (45 * t + 110 / 25 * (1 - np.exp(-25 * t)))) * np.exp(-t * 11)


def clap():
    body = bp(noise(0.18), 900, 2600) * decay(0.18, 22)
    flams = np.zeros_like(body)
    for k, g in ((0, 1.0), (0.012, 0.7), (0.024, 0.5)):
        place(flams, body[: len(body) - int(k * SR)], k, g)
    return flams * 0.5


def hat(d=0.05):
    return hp(noise(d), 7000) * decay(d, 90)


def whoosh(d=0.8):
    n = int(d * SR)
    src = noise(d)
    out = np.zeros(n)
    steps = 14
    for s in range(steps):
        f = 250 * (14 ** (s / steps))
        w = np.exp(-((np.arange(n) / n - s / steps) ** 2) / 0.012)
        out += bp(src, f, min(f * 1.6, SR / 2 - 100)) * w
    return out * np.sin(np.pi * np.arange(n) / n) ** 2


def impact():
    d = 1.6
    t = np.arange(int(d * SR)) / SR
    sub = np.sin(2 * np.pi * (38 * t + 70 / 7 * (1 - np.exp(-7 * t)))) * np.exp(-t * 3)
    crack = lp(noise(d), 3000) * np.exp(-t * 30) * 0.5
    return sub + crack


def tick(f=1800, d=0.05):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 70)


def pop(f0=900, f1=500, d=0.09):
    t = np.arange(int(d * SR)) / SR
    f = f0 + (f1 - f0) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38)


def riser(d, f0=250, f1=900):
    t = np.arange(int(d * SR)) / SR
    f = f0 * (f1 / f0) ** (t / d)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * bp(noise(d), 2000, 8000)
    return y * (t / d) ** 2 * (1 - np.exp(-(d - t) * 40))


def chime():
    d = 3.0
    t = np.arange(int(d * SR)) / SR
    y = np.zeros_like(t)
    for m, g in ((74, 1.0), (81, 0.6), (86, 0.45), (93, 0.25)):
        y += g * np.sin(2 * np.pi * midi(m) * t) * np.exp(-t * (2.0 + m / 45))
    return y


def counter(d, steps):
    """Rapid ticks that speed up, for numbers counting up."""
    y = np.zeros(int(d * SR) + SR // 10)
    for i in range(steps):
        p = i / steps
        at = d * (1 - (1 - p) ** (1 / 3))  # inverse of the page's cubic ease-out, so ticks match the digits
        place(y, tick(2000 + 900 * p, 0.025), at, 0.6)
    return y


# ---------------------------------------------------------------- music
def music(total, scenes):
    n = int(total * SR) + SR
    pad, bass, arp, drums = (np.zeros(n) for _ in range(4))
    chords = [(50, 54, 57, 61), (47, 50, 54, 57), (43, 47, 50, 54), (45, 49, 52, 54)]  # Dmaj7 Bm7 Gmaj7 A6
    s = [a for a, _ in scenes]
    drums_in = s[2]                    # full groove from the JOPAD scene
    breakdown = (s[5], s[5] + BAR)     # one bar of air when the engineering half starts
    outro = s[7]

    def drums_on(t):
        return drums_in <= t < outro and not (breakdown[0] <= t < breakdown[1])

    seg = BAR * 2
    for k, t in enumerate(np.arange(0, total, seg)):
        notes = chords[k % 4]
        clip = sum(tone(midi(m), seg + 0.8, harmonics=6, detune=0.002) for m in notes)
        clip = lp(clip, 1600) * env_adsr(len(clip), 0.5, 0.8)
        place(pad, clip, t, 0.06)
        root = midi(notes[0] - 12)
        for b in range(8):  # bass: root on every beat once the groove is in, half-time before
            bt = t + b * BEAT
            if bt < s[1] or bt >= total - BAR or (bt < drums_in and b % 2) or breakdown[0] <= bt < breakdown[1]:
                continue
            d = BEAT * (0.9 if bt >= drums_in else 1.8)
            c = tone(root, d, harmonics=4) * decay(d, 3.5) * env_adsr(int(d * SR), 0.005, 0.05)
            place(bass, lp(c, 600), bt, 0.3)
        for st in range(16):  # eighth-note arpeggio
            at = t + st * BEAT / 2
            if at < s[1] or at > total - 1.0:
                continue
            m = notes[[0, 2, 1, 3, 2, 1, 3, 2][st % 8]] + 12 + (12 if st % 4 == 3 else 0)
            d = 0.4
            c = (tone(midi(m), d) + tone(midi(m) * 3, d) / 9) * decay(d, 10)
            place(arp, c * env_adsr(len(c), 0.004, 0.02), at, 0.08)

    K, C = kick(), clap()
    bt, i = 0.0, 0
    while bt < total:
        if drums_on(bt):
            place(drums, K, bt, 0.55)                                 # four on the floor
            if i % 2 == 1:
                place(drums, C, bt, 0.35)                             # clap on 2 and 4
            place(drums, hat(), bt + BEAT / 2, 0.09)                  # open offbeat hat
            place(drums, hat(0.025), bt + BEAT / 4, 0.035)            # 16th shuffle
            place(drums, hat(0.025), bt + 3 * BEAT / 4, 0.035)
        elif bt < drums_in and i % 4 == 0:
            place(drums, K, bt, 0.35)                                 # intro: one soft kick per bar
        bt += BEAT
        i += 1

    mix = pad + bass + arp + drums
    fade = np.ones(n)
    fade[: int(0.8 * SR)] = np.linspace(0, 1, int(0.8 * SR))
    end = int(total * SR)
    fade[end - int(4 * SR): end] = np.linspace(1, 0, int(4 * SR)) ** 1.5
    fade[end:] = 0
    return mix * fade


# ---------------------------------------------------------------- sound effects
def effects(total, scenes):
    n = int(total * SR) + SR
    fx = np.zeros(n)
    s = [a for a, _ in scenes]

    place(fx, impact(), 0.0, 0.7)
    place(fx, pop(1100, 600), 0.4, 0.35)          # "John Godwin"
    place(fx, pop(1300, 700), 0.7, 0.35)          # "Oamien"
    place(fx, whoosh(0.6), 2.4, 0.25)             # tagline
    for start in s[1:]:
        place(fx, riser(BAR / 2), start - BAR / 2, 0.18)
        place(fx, whoosh(), start - 0.45, 0.4)
        place(fx, impact(), start, 0.45)

    # two profiles slide in from either side
    place(fx, whoosh(0.5), s[1] + 0.0, 0.25)
    place(fx, whoosh(0.5), s[1] + 0.25, 0.25)

    # JOPAD: nodes arrive, then light up in order with rising pitches, wires zip between them
    for k, lt in enumerate((1.4, 1.8, 2.2, 2.6)):
        place(fx, pop(800 + k * 120, 500 + k * 80), s[2] + lt, 0.3)
    for k, lt in enumerate((5.2, 6.2, 7.2, 8.2)):
        place(fx, tick(midi(74 + (0, 4, 7, 12)[k]), 0.18) * 0.8, s[2] + lt, 0.5)
        if k < 3:
            place(fx, whoosh(0.5), s[2] + lt + 0.4, 0.12)
    place(fx, chime(), s[2] + 8.25, 0.12)

    # Jason and Vortex cards, list items
    place(fx, whoosh(0.5), s[3] + 0.2, 0.25)
    place(fx, whoosh(0.5), s[3] + 0.6, 0.25)
    for lt in (1.0, 1.3, 1.6):
        place(fx, tick(1500), s[3] + lt, 0.35)

    # Frontend Mentor wall: one blip per tile, then the counter
    for i in range(15):
        place(fx, tick(2000 + (i % 5) * 150, 0.03), s[4] + 0.05 + i * 0.07, 0.25)
    place(fx, counter(1.6, 14), s[4] + 1.2, 0.5)
    place(fx, pop(1400, 800, 0.12), s[4] + 2.8, 0.45)

    # NDDC: photos snap in, checklist items tick
    for lt in (0.8, 1.1, 1.4, 1.7):
        place(fx, pop(), s[5] + lt, 0.35)
        place(fx, hp(noise(0.04), 3000) * decay(0.04, 120), s[5] + lt, 0.15)  # shutter click
    for lt in (1.6, 2.4, 3.2, 4.0):
        place(fx, tick(1300, 0.08), s[5] + lt, 0.4)

    # Waste study: counter to 150.4, bars grow, the plastics line lands
    place(fx, counter(2.2, 26), s[6] + 1.0, 0.45)
    place(fx, pop(1200, 700, 0.12), s[6] + 3.2, 0.45)
    place(fx, riser(1.2, 200, 600), s[6] + 3.0, 0.2)
    place(fx, riser(1.2, 200, 400), s[6] + 3.3, 0.12)
    place(fx, pop(700, 400, 0.15), s[6] + 5.2, 0.5)

    # Outro: name, the two paths, then the URL with a chime
    place(fx, pop(1100, 600), s[7] + 0.9, 0.3)
    place(fx, pop(1300, 700), s[7] + 1.1, 0.3)
    place(fx, chime(), s[7] + 1.8, 0.45)
    return fx


def main():
    out_wav = sys.argv[1]
    scenes, total = timeline()
    (HERE / "timeline.js").write_text(
        "// Generated by build_audio.py. Scenes are whole bars of the 96 BPM music.\n"
        "window.TIMELINE = " + json.dumps({"duration": round(total, 3), "scenes": scenes}) + ";\n",
        encoding="utf-8",
    )
    m = music(total, scenes)
    fx = effects(total, scenes)
    rms = lambda x: np.sqrt((x[np.abs(x) > 1e-4] ** 2).mean())
    fx *= rms(m) / rms(fx) * 10 ** (-2 / 20)
    mix = (m + fx)[: int(total * SR)]
    mix = mix / np.abs(mix).max() * 0.89
    sf.write(out_wav, np.stack([mix, mix], axis=1), SR, subtype="PCM_16")
    print(f"total {total:.2f}s, scenes {scenes}")
    print("wrote", out_wav)


if __name__ == "__main__":
    main()
