"""Builds the soundtrack for motion.html: original music plus sound effects, no voice.

- Music: 120 BPM, so one bar is 2 s and the picture's cuts land on downbeats. The sections
  (intro, groove, a breakdown into the engineering half, outro) come from window.TIMELINE.
- Effects: cues.mjs returns every cue the page registers (letters assembling, slams, camera
  whips, zoom-throughs, fly-ins, counters, bars growing...) with its time and on-screen x
  position. Each cue gets a sound shaped to its motion and panned to where it happens.
  Tonal effects use the key of the music (D major).

Everything is synthesised here (no samples, no licensing) and processed with Spotify's
pedalboard (reverb, chorus, delay, filters, compression, limiting).

Usage:   python3 video/build_audio.py <out.wav>
Needs:   pip install numpy scipy soundfile pedalboard   (and Playwright, for cues.mjs)
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from pedalboard import (Chorus, Compressor, Delay, Distortion, Gain, HighpassFilter, HighShelfFilter,
                        LadderFilter, Limiter, LowpassFilter, LowShelfFilter, Pedalboard, Reverb)
from scipy.signal import butter, sosfilt

HERE = Path(__file__).parent
SR = 48000
PENTA = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86, 88, 90, 93]  # D major pentatonic
RNG = np.random.default_rng(11)


# ================================================================ helpers
def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def ts(d):
    return np.arange(max(1, int(d * SR))) / SR


def noise(d):
    return RNG.standard_normal(max(1, int(d * SR)))


def filt(y, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), y)


def fx(board, y, tail=0.0):
    y = np.atleast_2d(y).astype(np.float32)
    if y.shape[0] == 1:
        y = np.vstack([y, y])
    if tail:
        y = np.pad(y, ((0, 0), (0, int(tail * SR))))
    return board(y, SR).astype(np.float64)


def pan(y, x):
    x = 0.12 + 0.76 * np.clip(x, 0, 1)
    th = x * np.pi / 2
    return np.vstack([y * np.cos(th), y * np.sin(th)]) * np.sqrt(2)


def place(buf, clip, at, gain=1.0):
    clip = np.atleast_2d(clip)
    if clip.shape[0] == 1:
        clip = np.vstack([clip, clip])
    i = int(round(at * SR))
    if i < 0:
        clip, i = clip[:, -i:], 0
    j = min(buf.shape[1], i + clip.shape[1])
    if j > i:
        buf[:, i:j] += clip[:, : j - i] * gain


def ease_out(x):
    return 1 - (1 - np.clip(x, 0, 1)) ** 3


def ease_in_out(x):
    x = np.clip(x, 0, 1)
    return np.where(x < 0.5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)


def rms(y):
    a = y[np.abs(y) > 1e-4]
    return np.sqrt((a ** 2).mean()) if a.size else 1e-9


# ================================================================ instruments
def fm(freq, d, ratio=1.0, index=2.0, idx_decay=6.0, amp_decay=4.0, attack=0.003):
    t = ts(d)
    I = index * np.exp(-t * idx_decay)
    return np.sin(2 * np.pi * freq * t + I * np.sin(2 * np.pi * freq * ratio * t)) * np.exp(-t * amp_decay) * np.minimum(1, t / attack)


def ep(freq, d=0.6):
    return fm(freq, d, 1.0, 1.8, 9, 6) + 0.25 * fm(freq * 2, d, 1.0, 0.8, 12, 9)


def bell(freq, d=2.0, decay=2.5):
    return fm(freq, d, 3.5, 3.0, 4, decay) * 0.7 + fm(freq, d, 1.0, 0.5, 3, decay * 0.8) * 0.4


def supersaw(freq, d, voices=5, spread=0.012):
    t = ts(d)
    L = np.zeros_like(t)
    R = np.zeros_like(t)
    hmax = int(min(14, 9000 / freq))
    for v in range(voices):
        det = 1 + spread * (v - (voices - 1) / 2) / ((voices - 1) / 2)
        ph = RNG.uniform(0, 2 * np.pi)
        s = sum(np.sin(2 * np.pi * freq * det * h * t + ph * h) / h for h in range(1, hmax + 1))
        w = v / (voices - 1)
        L += s * np.cos(w * np.pi / 2)
        R += s * np.sin(w * np.pi / 2)
    return np.vstack([L, R]) / voices


def thump(f0=140, f1=60, d=0.25, rate=18):
    t = ts(d)
    f = f1 + (f0 - f1) * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * rate)


def click(d=0.012, f=3500):
    return filt(noise(d), "band", [f * 0.6, min(f * 1.6, 20000)]) * np.exp(-ts(d) * 300)


def tick(f, d=0.03):
    t = ts(d)
    return (np.sin(2 * np.pi * f * t) * 0.7 + click(d, min(f * 1.5, 9000))[: len(t)] * 0.6) * np.exp(-t * 120)


def shutter():
    y = np.zeros(int(0.12 * SR))
    for k, g, f in ((0, 1.0, 2400), (0.045, 0.7, 1800)):
        c = filt(noise(0.03), "band", [f * 0.7, f * 1.5]) * np.exp(-ts(0.03) * 160)
        i = int(k * SR)
        y[i:i + len(c)] += c * g
    return y


def glide(d, f0, f1, curve, speed_env=True):
    t = ts(d)
    f = f0 * (f1 / f0) ** curve(t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.3 * np.sin(2 * ph)
    env = np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08)
    if speed_env:
        env *= 0.35 + 0.65 * (1 - np.clip(t / d, 0, 1)) ** 1.5
    return y * env


def air(d, lo=200, hi=1800, shape=None):
    """Soft, dark air movement. shape: amplitude curve over the duration."""
    t = ts(d)
    y = filt(filt(noise(d), "band", [lo, hi]), "low", hi * 0.9)
    return y * (shape(t / d) if shape is not None else np.sin(np.pi * t / d))


def reverse_swell(freq, d=0.8):
    b = bell(freq, 0.25, 6) + 0.6 * bell(freq * 1.5, 0.25, 6)
    wet = fx(Pedalboard([Reverb(room_size=0.95, damping=0.3, wet_level=1.0, dry_level=0.0, width=1.0)]), b, tail=d)
    wet = wet[:, : int(d * SR)][:, ::-1]
    return wet * (ts(d) / d) ** 1.5


def impact(gain_low=1.0, bright=0.5, d=1.4):
    t = ts(d)
    sub = np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-t * 14)) / SR) * np.exp(-t * 3.2) * gain_low
    body = filt(noise(d), "band", [120, 900]) * np.exp(-t * 22) * 0.6
    top = filt(noise(d), "high", 3500) * np.exp(-t * 45) * bright * 0.5
    return np.tanh(1.3 * (sub + body + top))


# ================================================================ music
def music(tl):
    total = tl["duration"]
    bpm = tl["bpm"]
    beat = 60 / bpm
    bar = beat * 4
    n = int(total * SR) + SR
    g0, g1 = tl["groove"]
    b0, b1 = tl["breakdown"]
    outro = tl["outro"]

    def drums_on(t):
        return g0 <= t < g1 and not (b0 <= t < b1)

    chords = [(50, 54, 57, 61), (47, 50, 54, 57), (43, 47, 50, 54), (45, 49, 52, 57)]  # Dmaj7 Bm7 Gmaj7 A
    seg = bar * 2
    times = np.arange(n) / SR

    beats = [round(k * beat, 6) for k in range(int(total / beat) + 1)]
    kicks = [t for t in beats if drums_on(t)]
    pump = np.ones(n)
    for k in kicks:
        i = int(k * SR)
        d = int(beat * SR)
        g = 1 - 0.5 * np.exp(-(np.arange(d) / SR) / 0.09)
        j = min(n, i + d)
        pump[i:j] = np.minimum(pump[i:j], g[: j - i])

    # pad
    pad = np.zeros((2, n))
    for k, t0 in enumerate(np.arange(0, total, seg)):
        d = seg + 1.0
        clip = sum(supersaw(midi(m), d) for m in chords[k % 4])
        env = np.minimum(1, ts(d) / 0.6) * np.minimum(1, (d - ts(d)) / 1.0)
        place(pad, clip * env, t0, 0.12)
    pad = fx(Pedalboard([LadderFilter(mode=LadderFilter.Mode.LPF24, cutoff_hz=1100, resonance=0.15),
                         Chorus(rate_hz=0.3, depth=0.35, mix=0.5),
                         Reverb(room_size=0.9, damping=0.5, wet_level=0.45, dry_level=0.7, width=1.0)]), pad)[:, :n]
    bright = np.zeros((2, n))
    for k, t0 in enumerate(np.arange(0, total, seg)):
        d = seg + 1.0
        clip = sum(supersaw(midi(m + 12), d, voices=3) for m in chords[k % 4][1:])
        env = np.minimum(1, ts(d) / 0.4) * np.minimum(1, (d - ts(d)) / 1.0)
        place(bright, clip * env, t0, 0.05)
    bright = fx(Pedalboard([LadderFilter(mode=LadderFilter.Mode.LPF12, cutoff_hz=3000, resonance=0.1),
                            Chorus(rate_hz=0.5, depth=0.5, mix=0.6),
                            Reverb(room_size=0.85, wet_level=0.5, dry_level=0.5, width=1.0)]), bright)[:, :n]
    bright_env = np.clip((times - g0 + 0.5) / 1.0, 0, 1) * np.where((times >= b0) & (times < b1), 0.35, 1.0)

    # intro: the arp sweeps open into the first drop
    # bass
    bass = np.zeros((2, n))
    for k, t0 in enumerate(np.arange(0, total, seg)):
        root = midi(chords[k % 4][0] - 12)
        for b in range(8):
            bt = t0 + b * beat
            if bt < g0 or bt >= outro or (b0 <= bt < b1 and b % 4):
                continue
            d = beat * 0.9 if drums_on(bt) else beat * 3.6
            t = ts(d)
            y = np.sin(2 * np.pi * root * t) + 0.3 * np.sin(4 * np.pi * root * t) + 0.12 * np.sin(6 * np.pi * root * t)
            y *= np.minimum(1, t / 0.006) * np.minimum(1, (d - t) / 0.04) * (0.75 + 0.25 * np.exp(-t * 5))
            place(bass, y, bt, 0.34)
            # an octave pickup on the last 8th of each bar, for drive
            if drums_on(bt) and b % 4 == 3:
                place(bass, np.sin(2 * np.pi * root * 2 * ts(beat * 0.4)) * np.exp(-ts(beat * 0.4) * 8), bt + beat / 2, 0.14)
    bass = fx(Pedalboard([Distortion(drive_db=7), LowpassFilter(340), Gain(-3)]), bass)[:, :n]

    # arp: 16ths once the groove is in, 8ths in intro/outro
    arp = np.zeros((2, n))
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]
    for k, t0 in enumerate(np.arange(0, total, seg)):
        notes = chords[k % 4]
        for st in range(32):
            at = t0 + st * beat / 4
            if at > total - 1.0:
                continue
            fast = drums_on(at)
            if not fast and st % 2:
                continue
            m = notes[pattern[(st // (1 if fast else 2)) % 8]] + 12 + (12 if st % 8 == 6 else 0)
            vel = (0.8 if st % 4 == 0 else 0.6) + RNG.uniform(-0.05, 0.05)
            place(arp, pan(ep(midi(m), 0.4), 0.3 + 0.4 * ((st // 2) % 2)), at, 0.07 * vel)
    arp = fx(Pedalboard([HighpassFilter(220), Delay(delay_seconds=beat * 0.75, feedback=0.28, mix=0.2),
                         Reverb(room_size=0.7, wet_level=0.3, dry_level=0.8, width=1.0)]), arp)[:, :n]
    intro_open = np.clip(times / g0, 0, 1) ** 2
    arp_env = np.where(times < g0, 0.25 + 0.75 * intro_open, 1.0)

    # drums
    def kick():
        t = ts(0.42)
        body = np.sin(2 * np.pi * np.cumsum(50 + 120 * np.exp(-t * 34)) / SR) * np.exp(-t * 8.5)
        clickk = filt(noise(0.42), "high", 2500) * np.exp(-t * 400) * 0.3
        return np.tanh(1.7 * (body + clickk)) * 0.9

    def clap():
        d = 0.24
        b = filt(noise(d), "band", [900, 3200]) * np.exp(-ts(d) * 24)
        y = np.zeros_like(b)
        for k, g in ((0, 1.0), (0.011, 0.75), (0.022, 0.55)):
            i = int(k * SR)
            y[i:] += b[: len(b) - i] * g
        return y * 0.55

    def hat(d, brightf=8000):
        return filt(noise(d), "high", brightf, 4) * np.exp(-ts(d) / (d / 4))

    kk, cl, hh = (np.zeros((2, n)) for _ in range(3))
    K = kick()
    for i, t in enumerate(beats):
        if t >= total:
            break
        if drums_on(t):
            place(kk, K, t, 0.62)
            if i % 2 == 1:
                place(cl, clap(), t + 0.004, 0.4)
            place(hh, pan(hat(0.08), 0.62), t + beat / 2, 0.11 * RNG.uniform(0.85, 1.0))
            for q in (0.25, 0.75):
                place(hh, pan(hat(0.028, 9500), 0.7), t + q * beat, 0.045 * RNG.uniform(0.7, 1.0))
        elif b0 <= t < b1 and i % 4 == 0:
            place(kk, K, t, 0.35)   # breakdown: one soft kick per bar
    # snare roll into the drops after the intro and the breakdown
    for end in (g0, b1):
        for r in range(8):
            at = end - beat * 2 + r * beat / 4
            place(cl, clap(), at, 0.08 + 0.3 * (r / 8) ** 2)
    cl = fx(Pedalboard([Reverb(room_size=0.4, damping=0.6, wet_level=0.25, dry_level=0.9, width=0.8)]), cl)[:, :n]
    drums = kk + cl + fx(Pedalboard([HighShelfFilter(cutoff_frequency_hz=9000, gain_db=2)]), hh)[:, :n]

    # sub hits on the drops
    hits = np.zeros((2, n))
    for d in tl["drops"]:
        place(hits, impact(1.0, 0.2, 1.6), d, 0.35)

    mix = (pad + bright * bright_env * 0.8 + bass + arp * arp_env * 0.9) * pump * 0.9 + drums + hits
    fade = np.clip(times / 0.4, 0, 1) * np.clip((total - times) / 2.5, 0, 1) ** 1.5
    return mix * fade


# ================================================================ effects
def effects(tl, cues):
    total = tl["duration"]
    n = int(total * SR) + 2 * SR
    dry = np.zeros((2, n))
    verb = np.zeros((2, n))
    counters = {}

    for c in cues:
        k, t, x = c["kind"], c["t"], c["x"]
        idx = c.get("idx", counters.get(k, 0))
        counters[k] = counters.get(k, 0) + 1

        if k == "letters":
            for i in range(c["n"]):
                m = PENTA[5 + (i * 2) % 7]
                place(verb, pan(tick(midi(m + 12), 0.025), 0.3 + 0.4 * i / max(1, c["n"] - 1)), t + i * c["gap"] + 0.05, 0.05)
            place(verb, pan(ep(midi(74), 0.8), x), t, 0.05)
        elif k == "slam":
            soft = c.get("soft")
            place(dry, pan(impact(0.8, 0.35, 1.0), x), t, 0.22 if soft else 0.4)
            place(verb, pan(ep(midi(62), 1.0) + ep(midi(69), 1.0) * 0.6, x), t, 0.05 if soft else 0.08)
        elif k == "flip":
            place(dry, reverse_swell(midi(74), 0.5), t - 0.5, 0.18)
            place(dry, pan(impact(0.7, 0.8, 1.0), x), t, 0.42)
            place(verb, pan(bell(midi(81), 1.4, 3), x), t, 0.1)
        elif k == "whip":
            d = c.get("dur", 0.4)
            shape = lambda p: np.sin(np.pi * np.clip(p, 0, 1)) ** 2 * (p ** 1.5)
            px = np.linspace(0.5, 0.5 + 0.45 * c.get("dir", 1), int(d * SR))
            place(dry, pan(air(d, 250, 1800, shape), px), t, 0.24)
            place(dry, thump(90, 45, 0.4, 9), t + d, 0.3)
        elif k == "fly":
            d = c.get("dur", 0.5)
            speed = lambda p: 3 * (1 - np.clip(p, 0, 1)) ** 2 / 3
            px = np.linspace(0.5 + (x - 0.5) * 2.2, x, int(d * SR))
            place(dry, pan(air(d, 220, 1600, speed), px), t, 0.16 if c.get("soft") else 0.3)
            place(dry, pan(thump(150, 70, 0.2), x), t + d * 0.25, 0.12)
        elif k == "through":
            d = c.get("dur", 0.5)
            rev = c.get("reverse")
            up = lambda p: np.clip(p, 0, 1) ** 2.2
            down = lambda p: (1 - np.clip(p, 0, 1)) ** 2.2
            place(dry, air(d, 180, 2000 if c.get("bright") else 1300, down if rev else up), t, 0.2)
            f0, f1 = (midi(62), midi(86)) if not rev else (midi(86), midi(62))
            place(verb, glide(d, f0, f1, ease_in_out, False) * (ts(d) / d) ** (0.5 if rev else 2) * 0.5, t, 0.08)
            place(dry, thump(110, 45, 0.5, 8), t + d, 0.28)
        elif k == "pop":
            place(dry, pan(thump(170, 80, 0.18), x), t, 0.2)
            place(verb, pan(ep(midi(PENTA[idx % 8] + 12), 0.5), x), t, 0.07)
        elif k == "lit":
            m = (74, 78, 81, 86)[idx % 4]
            place(verb, pan(bell(midi(m), 1.6, 2.2), x), t, 0.15)
            place(dry, pan(click(0.01, 5000), x), t, 0.18)
        elif k == "wire":
            d = c.get("dur", 0.6)
            m0, m1 = [(74, 78), (78, 81), (81, 86)][idx % 3]
            tt = ts(d)
            y = glide(d, midi(m0), midi(m1), ease_in_out, False) * 0.3 + filt(noise(d), "band", [2500, 5000]) * 0.06
            y *= np.sin(np.pi * tt / d) ** 1.2
            place(dry, pan(y, np.linspace(x - 0.05, x + 0.05, len(tt))), t, 0.1)
        elif k == "tick":
            place(verb, pan(tick(midi(PENTA[3 + idx % 8] + 12)), x), t, 0.12)
        elif k == "tile":
            place(verb, pan(bell(midi(PENTA[3 + idx % 9] + 12), 0.5, 9), x), t, 0.045)
            place(dry, pan(click(0.008, 6000), x), t, 0.1)
        elif k == "count":
            V, d, step = c["value"], c["dur"], c.get("step", 1)
            last, prev_t = -1, -1.0
            for f in range(int(d * 200) + 1):
                tt = f / 200
                v = V * ease_out(tt / d)
                q = int(v // step)
                if q != last and tt - prev_t > 0.028:
                    place(dry, pan(tick(1500 + 1400 * v / V), x), t + tt, 0.16)
                    last, prev_t = q, tt
            place(verb, pan(bell(midi(86), 1.8, 2.5), x), t + d * 0.9, 0.13)
            place(dry, pan(thump(200, 90, 0.2), x), t + d * 0.9, 0.18)
        elif k == "photo":
            place(dry, pan(thump(170, 80, 0.2), x), t, 0.18)
            place(dry, pan(shutter(), x), t + 0.02, 0.2)
        elif k == "draw":
            d = c.get("dur", 1.0)
            tt = ts(d)
            scratch = filt(noise(d), "band", [2500, 4500]) * (0.3 + 0.7 * np.abs(np.sin(2 * np.pi * 6 * tt))) * np.sin(np.pi * tt / d)
            place(dry, pan(scratch, x), t, 0.025)
            for j in range(5):  # a soft tonal tick as each line of the drawing starts
                place(verb, pan(tick(midi(PENTA[5 + j] + 12), 0.03), x), t + j * 0.14, 0.06)
        elif k == "item":
            place(dry, pan(click(0.01, 4200), x), t, 0.3)
            place(verb, pan(ep(midi(PENTA[3 + idx] + 12), 0.4), x), t, 0.07)
        elif k == "rise":
            d = c.get("dur", 0.8)
            place(dry, air(d, 300, 1200, lambda p: np.sin(np.pi * np.clip(p, 0, 1)) * 0.8), t, 0.08)
            place(verb, glide(d, midi(57), midi(69), ease_in_out, False) * np.sin(np.pi * ts(d) / d), t, 0.04)
        elif k == "grow":
            d = c.get("dur", 0.6)
            semis = 3 + 14 * c.get("pitch", 0.5)
            place(dry, pan(glide(d, midi(62), midi(62) * 2 ** (semis / 12), ease_out), x), t, 0.07)
            place(dry, pan(click(0.01, 3000), x), t + d * 0.5, 0.1)
        elif k == "glow":
            for j, m in enumerate((78, 81, 86, 90)):
                place(verb, pan(bell(midi(m), 1.5, 3), x), t + j * 0.05, 0.06)
            place(dry, air(0.6, 2000, 8000, lambda p: np.sin(np.pi * np.clip(p, 0, 1))), t, 0.05)
        elif k == "stat":
            place(dry, pan(impact(1.0, 0.4, 1.2), x), t, 0.38)
            for m in (62, 66, 69, 74):
                place(verb, pan(ep(midi(m), 1.0), x), t + 0.01, 0.05)
        elif k == "cta":
            for j, m in enumerate((74, 78, 81, 86)):
                place(verb, pan(bell(midi(m), 3.0, 1.6), 0.5), t + j * 0.06, 0.12)
            place(dry, thump(130, 50, 0.5), t, 0.25)

    room = Pedalboard([HighpassFilter(150), Reverb(room_size=0.6, damping=0.5, wet_level=0.35, dry_level=0.85, width=1.0)])
    out = dry + fx(room, verb)[:, :n]
    return fx(Pedalboard([HighpassFilter(40), Compressor(threshold_db=-18, ratio=3, attack_ms=2, release_ms=80)]), out)[:, :n]


def main():
    out_wav = sys.argv[1]
    data = json.loads(subprocess.run(["node", str(HERE / "cues.mjs")], check=True, capture_output=True, text=True).stdout)
    tl, cues = data["timeline"], data["cues"]
    print(f"{len(cues)} cues; {tl['bpm']} BPM; {tl['duration']} s")
    n = int(tl["duration"] * SR)
    m = music(tl)[:, :n]
    e = effects(tl, cues)[:, :n]
    e *= rms(m) / rms(e) * 10 ** (-2 / 20)
    mix = m + e
    mix = mix / np.abs(mix).max() * 0.7
    master = Pedalboard([
        HighpassFilter(35),
        LowShelfFilter(cutoff_frequency_hz=90, gain_db=-1.5),
        HighShelfFilter(cutoff_frequency_hz=7000, gain_db=3.0),
        Compressor(threshold_db=-16, ratio=2.4, attack_ms=12, release_ms=140),
        Limiter(threshold_db=-1.5, release_ms=80),
        Gain(-1.5),  # the limiter adds make-up gain; keep the ceiling under 0 dBFS
    ])
    mix = fx(master, mix)[:, :n]
    t = np.arange(n) / SR
    mix *= np.clip((tl["duration"] - t) / 0.05, 0, 1)
    sf.write(out_wav, mix.T, SR, subtype="PCM_24")
    print("wrote", out_wav)


if __name__ == "__main__":
    main()
