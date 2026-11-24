"""Builds the explainer's soundtrack: original music plus sound effects, no voice.

How the sound is kept in step with the picture:
- The music is 96 BPM, so one bar is 2.5 s and every scene is a whole number of bars.
  Scene times go to timeline.js, which explainer.html reads.
- cues.mjs reads every animation from the page itself (when each element moves, what it is,
  where it sits on screen). Each cue gets a sound shaped to its motion: slides get a swipe whose
  loudness follows the element's speed, counters tick on the digits, bars glide in pitch as they
  grow, and everything is panned to its position on screen.
- Tonal effects are tuned to the key of the music (D major) so they sit inside it.

All sounds are synthesised here (no samples, so no licensing questions) and processed with
Spotify's pedalboard (reverb, chorus, delay, filters, compression, limiting).

Usage:
  python3 video/build_audio.py <out.wav>
Needs: pip install numpy scipy soundfile pedalboard, plus Playwright (for cues.mjs).
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
BPM = 96
BEAT = 60 / BPM
BAR = BEAT * 4

# Bars per scene, in the order of the <section class="scene"> elements:
# intro, two profiles, JOPAD, Jason + Vortex, Frontend Mentor, NDDC, waste study, outro.
SCENE_BARS = [2, 2, 4, 3, 2, 4, 4, 3]

# D major pentatonic, for effects that should sound "in key"
PENTA = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86]
RNG = np.random.default_rng(11)


# ================================================================ basics
def timeline():
    scenes, t = [], 0.0
    for bars in SCENE_BARS:
        scenes.append([round(t, 3), round(t + bars * BAR, 3)])
        t += bars * BAR
    return scenes, t


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def ts(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return RNG.standard_normal(int(d * SR))


def filt(y, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), y)


def fx(board, y, tail=0.0):
    """Run a mono or stereo signal through a pedalboard chain; returns stereo (2, n)."""
    y = np.atleast_2d(y).astype(np.float32)
    if y.shape[0] == 1:
        y = np.vstack([y, y])
    if tail:
        y = np.pad(y, ((0, 0), (0, int(tail * SR))))
    return board(y, SR).astype(np.float64)


def pan(y, x):
    """Equal-power pan of a mono signal. x: 0 = left, 1 = right (or an array per sample)."""
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
    y = np.sin(2 * np.pi * freq * t + I * np.sin(2 * np.pi * freq * ratio * t))
    env = np.exp(-t * amp_decay) * np.minimum(1, t / attack)
    return y * env


def ep(freq, d=0.6):          # soft electric-piano pluck
    return fm(freq, d, ratio=1.0, index=1.8, idx_decay=9, amp_decay=6) + 0.25 * fm(freq * 2, d, 1.0, 0.8, 12, 9)


def bell(freq, d=2.0, decay=2.5):  # glassy bell
    return fm(freq, d, ratio=3.5, index=3.0, idx_decay=4, amp_decay=decay) * 0.7 + fm(freq, d, 1.0, 0.5, 3, decay * 0.8) * 0.4


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


# ================================================================ music
def music(total, scenes):
    n = int(total * SR) + SR
    s = [a for a, _ in scenes]
    groove = (s[2], s[7])               # full drums from JOPAD until the outro
    breakdown = (s[5], s[5] + BAR)      # one bar of air into the engineering half

    def drums_on(t):
        return groove[0] <= t < groove[1] and not (breakdown[0] <= t < breakdown[1])

    chords = [(50, 54, 57, 61), (47, 50, 54, 57), (43, 47, 50, 54), (45, 49, 52, 57)]  # Dmaj7 Bm7 Gmaj7 A(add)
    seg = BAR * 2

    # --- kicks drive the sidechain pump
    kicks = []
    t = 0.0
    while t < total - 0.01:
        if drums_on(t) or (s[1] <= t < groove[0] and abs(t / BAR - round(t / BAR)) < 1e-6):
            kicks.append(t)
        t = round(t + BEAT, 6)
    pump = np.ones(n)
    for k in kicks:
        i = int(k * SR)
        d = int(BEAT * SR)
        seg_t = np.arange(d) / SR
        g = 1 - 0.45 * np.exp(-seg_t / 0.11)
        j = min(n, i + d)
        pump[i:j] = np.minimum(pump[i:j], g[: j - i])

    # --- pad: supersaw chords through a ladder filter, chorus and a big reverb
    pad = np.zeros((2, n))
    for k, t0 in enumerate(np.arange(0, total, seg)):
        notes = chords[k % 4]
        d = seg + 1.0
        clip = sum(supersaw(midi(m), d) for m in notes)
        env = np.minimum(1, ts(d) / 0.8) * np.minimum(1, (d - ts(d)) / 1.0)
        place(pad, clip * env, t0, 0.12)
    pad = fx(Pedalboard([LadderFilter(mode=LadderFilter.Mode.LPF24, cutoff_hz=900, resonance=0.15),
                         Chorus(rate_hz=0.3, depth=0.35, mix=0.5),
                         Reverb(room_size=0.9, damping=0.5, wet_level=0.45, dry_level=0.7, width=1.0)]), pad)[:, :n]
    # open the filter as the piece builds: brighter layer faded in from the JOPAD scene
    bright = np.zeros((2, n))
    for k, t0 in enumerate(np.arange(0, total, seg)):
        if t0 < s[2] - seg:
            continue
        notes = chords[k % 4]
        d = seg + 1.0
        clip = sum(supersaw(midi(m + 12), d, voices=3) for m in notes[1:])
        env = np.minimum(1, ts(d) / 0.5) * np.minimum(1, (d - ts(d)) / 1.0)
        place(bright, clip * env, t0, 0.05)
    bright = fx(Pedalboard([LadderFilter(mode=LadderFilter.Mode.LPF12, cutoff_hz=2600, resonance=0.1),
                            Chorus(rate_hz=0.5, depth=0.5, mix=0.6),
                            Reverb(room_size=0.85, wet_level=0.5, dry_level=0.5, width=1.0)]), bright)[:, :n]
    bright_env = np.clip((np.arange(n) / SR - s[2] + 2) / 4, 0, 1)
    bright_env *= np.where((np.arange(n) / SR >= breakdown[0]) & (np.arange(n) / SR < breakdown[1]), 0.4, 1)

    # --- bass: warm sub with a touch of saturation
    bass = np.zeros((2, n))
    for k, t0 in enumerate(np.arange(0, total, seg)):
        root = midi(chords[k % 4][0] - 12)
        for b in range(8):
            bt = t0 + b * BEAT
            if bt < s[1] or bt >= total - BAR or breakdown[0] <= bt < breakdown[1]:
                continue
            if bt < groove[0] and b % 4:
                continue
            d = BEAT * (0.85 if bt >= groove[0] else 3.6)
            t = ts(d)
            y = np.sin(2 * np.pi * root * t) + 0.3 * np.sin(4 * np.pi * root * t) + 0.12 * np.sin(6 * np.pi * root * t)
            y *= np.minimum(1, t / 0.006) * np.minimum(1, (d - t) / 0.04) * (0.75 + 0.25 * np.exp(-t * 5))
            place(bass, y, bt, 0.32)
    bass = fx(Pedalboard([Distortion(drive_db=6), LowpassFilter(320), Gain(-3)]), bass)[:, :n]

    # --- arpeggio: electric-piano plucks with a dotted-eighth delay
    arp = np.zeros((2, n))
    for k, t0 in enumerate(np.arange(0, total, seg)):
        notes = chords[k % 4]
        for st in range(16):
            at = t0 + st * BEAT / 2
            if at < s[1] or at > total - 1.2:
                continue
            m = notes[[0, 2, 1, 3, 2, 1, 3, 2][st % 8]] + 12 + (12 if st % 4 == 3 else 0)
            vel = 0.75 + 0.25 * (st % 2 == 0) + RNG.uniform(-0.05, 0.05)
            place(arp, pan(ep(midi(m)), 0.35 + 0.3 * (st % 2)), at, 0.075 * vel)
    arp = fx(Pedalboard([HighpassFilter(200), Delay(delay_seconds=BEAT * 0.75, feedback=0.3, mix=0.22),
                         Reverb(room_size=0.7, wet_level=0.3, dry_level=0.8, width=1.0)]), arp)[:, :n]

    # --- drums
    def kick():
        t = ts(0.4)
        f = 48 + 110 * np.exp(-t * 32)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
        click = filt(noise(0.4), "high", 2500) * np.exp(-t * 400) * 0.25
        return np.tanh(1.6 * (body + click)) * 0.9

    def clap():
        d = 0.22
        b = filt(noise(d), "band", [1000, 3000]) * np.exp(-ts(d) * 25)
        y = np.zeros_like(b)
        for k, g in ((0, 1.0), (0.011, 0.75), (0.022, 0.55)):
            i = int(k * SR)
            y[i:] += b[: len(b) - i] * g
        return y * 0.5

    def hat(d, bright=8000):
        return filt(noise(d), "high", bright, 4) * np.exp(-ts(d) / (d / 4))

    kk = np.zeros((2, n))
    cl = np.zeros((2, n))
    hh = np.zeros((2, n))
    K = kick()
    i = 0
    t = 0.0
    while t < total - 0.01:
        if drums_on(t):
            place(kk, K, t, 0.6)
            if i % 2 == 1:
                place(cl, clap(), t + 0.004, 0.38)
            place(hh, pan(hat(0.09), 0.62), t + BEAT / 2, 0.1 * RNG.uniform(0.85, 1.0))
            for q in (0.25, 0.75):
                place(hh, pan(hat(0.03, 9500), 0.7), t + q * BEAT, 0.04 * RNG.uniform(0.7, 1.0))
        elif t in kicks:
            place(kk, K, t, 0.4)
        t = round(t + BEAT, 6)
        i += 1
    cl = fx(Pedalboard([Reverb(room_size=0.4, damping=0.6, wet_level=0.25, dry_level=0.9, width=0.8)]), cl)[:, :n]
    drums = kk + cl + fx(Pedalboard([HighShelfFilter(cutoff_frequency_hz=9000, gain_db=2)]), hh)[:, :n]

    mix = (pad + bright * bright_env * 0.8 + bass + arp * 0.9) * pump * 0.9 + drums
    t = np.arange(n) / SR
    fade = np.clip(t / 1.2, 0, 1) * np.clip((total - t) / 4.0, 0, 1) ** 1.5
    return mix * fade


# ================================================================ sound effects
def swipe(d, x0, x1, bright=2800, gain=1.0):
    """Air swipe whose loudness follows an ease-out slide's speed and whose pan follows the element."""
    t = ts(d)
    speed = 3 * (1 - np.clip(t / d, 0, 1)) ** 2          # derivative of ease-out cubic
    att = np.minimum(1, t / 0.012)
    # soft and dark: felt more than heard, so slides never turn into a noisy "shh"
    y = filt(filt(noise(d), "band", [180, bright]), "low", bright * 0.8) * speed * att
    return pan(y * gain, x0 + (x1 - x0) * ease_out(t / d))


def thump(f0=140, f1=60, d=0.25):
    t = ts(d)
    f = f1 + (f0 - f1) * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18)


def click(d=0.012, f=3500):
    return filt(noise(d), "band", [f * 0.6, f * 1.6]) * np.exp(-ts(d) * 300)


def shutter():
    y = np.zeros(int(0.12 * SR))
    for k, g, f in ((0, 1.0, 2400), (0.045, 0.7, 1800)):
        c = filt(noise(0.03), "band", [f * 0.7, f * 1.5]) * np.exp(-ts(0.03) * 160)
        i = int(k * SR)
        y[i:i + len(c)] += c * g
    return y


def tick(f, d=0.03):
    t = ts(d)
    return (np.sin(2 * np.pi * f * t) * 0.7 + click(d, f * 1.5)[: len(t)] * 0.6) * np.exp(-t * 120)


def glide(d, f0, f1, curve, speed_env=True):
    t = ts(d)
    p = curve(t / d)
    f = f0 * (f1 / f0) ** p
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08)
    if speed_env:
        env *= 0.35 + 0.65 * (1 - np.clip(t / d, 0, 1)) ** 1.5
    return y * env


def reverse_swell(freq, d=1.0):
    """A bell rung through a long reverb, reversed: a soft swell that peaks on the cut."""
    b = bell(freq, 0.25, 6) + 0.6 * bell(freq * 1.5, 0.25, 6)
    wet = fx(Pedalboard([Reverb(room_size=0.95, damping=0.3, wet_level=1.0, dry_level=0.0, width=1.0)]), b, tail=d)
    wet = wet[:, : int(d * SR)][:, ::-1]
    t = ts(d)
    return wet * (t / d) ** 1.5


def effects(total, scenes, cues):
    n = int(total * SR) + 2 * SR
    dry = np.zeros((2, n))
    verb = np.zeros((2, n))      # send to a shared room so all effects sit in one space
    s = [a for a, _ in scenes]
    chords_root = [62, 59, 55, 57]  # pad chord roots (an octave up) for each 5 s section

    def root_at(t):
        return chords_root[int(t // (BAR * 2)) % 4]

    # scene changes: a soft reversed-bell swell into the cut and a gentle low thump on it
    for st in s[1:]:
        place(dry, reverse_swell(midi(root_at(st) + 12), 0.9), st - 0.9, 0.16)
        place(dry, thump(110, 45, 0.5), st, 0.22)
    place(verb, bell(midi(74), 2.5, 1.8), 0.0, 0.08)      # first frame

    # drop low-priority cues that land on top of a more important one
    major = [c for c in cues if c["kind"] not in ("small",)]
    keep = []
    for c in cues:
        if c["kind"] == "small" and any(abs(c["t"] - m["t"]) < 0.15 for m in major):
            continue
        keep.append(c)

    counters = {}
    for c in keep:
        k, t, x = c["kind"], c["t"], c["x"]
        idx = counters.setdefault((k, c["scene"]), 0)
        counters[(k, c["scene"])] = idx + 1

        if k == "title":
            big = c.get("size", 80) > 120
            place(dry, swipe(0.3, x - 0.02, x, 1400, 0.035 if big else 0.025), t)
            place(dry, pan(thump(150 if big else 190, 70, 0.22), x), t + 0.01, 0.30 if big else 0.18)
            place(verb, pan(ep(midi(PENTA[(idx + c["scene"]) % 5] + 12), 0.5), x), t + 0.01, 0.09)
        elif k == "small":
            place(verb, pan(tick(midi(PENTA[5 + idx % 4] + 12)), x), t + 0.01, 0.06)
        elif k in ("panel", "card"):
            x0 = x - 0.12 if k == "panel" and x < 0.5 else x + 0.12 if k == "panel" else x
            place(dry, swipe(c["dur"], x0, x, 1500, 0.04), t)
            place(dry, pan(thump(120, 55, 0.3), x), t + 0.02, 0.2)
            place(verb, pan(ep(midi(PENTA[2 + idx * 2] + 12), 0.6), x), t + 0.02, 0.07)
        elif k == "item":
            place(dry, pan(click(0.01, 4200), x), t, 0.35)
            place(verb, pan(ep(midi(PENTA[3 + idx] + 12), 0.4), x), t, 0.08)
        elif k == "tile":
            place(verb, pan(bell(midi(PENTA[3 + idx % 8] + 12), 0.5, 9), x), t, 0.05 * (1 - idx / 24))
            place(dry, pan(click(0.008, 6000), x), t, 0.12)
        elif k == "photo":
            place(dry, pan(thump(170, 80, 0.2), x), t, 0.2)
            place(dry, pan(shutter(), x), t + 0.02, 0.22)
        elif k == "node":
            place(dry, pan(thump(160, 90, 0.15), x), t, 0.14)
            place(verb, pan(ep(midi(PENTA[idx] + 12), 0.5), x), t, 0.06)
        elif k == "lit":
            m = (74, 78, 81, 86)[c["index"] % 4]
            place(verb, pan(bell(midi(m), 1.6, 2.2), x), t, 0.14)
            place(dry, pan(click(0.01, 5000), x), t, 0.15)
        elif k == "wire":
            d = c["dur"]
            tt = ts(d)
            m0 = (74, 78, 81)[idx % 3]
            m1 = (78, 81, 86)[idx % 3]
            y = glide(d, midi(m0), midi(m1), ease_in_out, speed_env=False) * 0.25
            y += filt(noise(d), "band", [2000, 7000]) * 0.4
            y *= np.sin(np.pi * tt / d) ** 1.2                  # loudest mid-draw, like the line's speed
            place(dry, pan(y, c["x"] + (c["x1"] - c["x"]) * ease_in_out(tt / d)), t, 0.10)
        elif k == "count":
            V, d = c["value"], c["dur"]
            step = 1 if V <= 20 else 5
            last = -1
            prev_t = -1
            for f in range(int(d * SR / 240) + 1):            # sample the page's ease-out at 200 Hz
                tt = f * 240 / SR
                v = V * ease_out(tt / d)
                q = int(v // step)
                if q != last and tt - prev_t > 0.028:
                    place(dry, pan(tick(1500 + 1400 * v / V), x), t + tt, 0.16)
                    last, prev_t = q, tt
            place(verb, pan(bell(midi(86), 1.8, 2.5), x), t + d * 0.92, 0.12)
            place(dry, pan(thump(200, 90, 0.2), x), t + d * 0.92, 0.18)
        elif k == "bar":
            d = c["dur"]
            semis = 12 * c["pct"] / 100 + 2                    # a longer bar rises further
            f0 = midi(62)
            y = glide(d, f0, f0 * 2 ** (semis / 12), ease_out)
            tt = ts(d)
            place(dry, pan(y, c["x"] + (c["x1"] - c["x"]) * ease_out(tt / d)), t, 0.09)
            place(dry, pan(click(0.01, 3000), c["x1"]), t + d * 0.55, 0.15)
        elif k == "stat":
            place(dry, pan(thump(120, 45, 0.6), x), t, 0.35)
            for m in (62, 66, 69, 74):
                place(verb, pan(ep(midi(m), 1.0), x), t + 0.01, 0.05)
        elif k == "cta":
            for j, m in enumerate((74, 78, 81, 86)):
                place(verb, pan(bell(midi(m), 3.0, 1.6), 0.5), t + j * 0.06, 0.12)
            place(dry, thump(130, 50, 0.5), t, 0.25)

    room = Pedalboard([HighpassFilter(150), Reverb(room_size=0.6, damping=0.5, wet_level=0.35, dry_level=0.85, width=1.0)])
    out = dry + fx(room, verb)[:, :n]
    return fx(Pedalboard([HighpassFilter(40), Compressor(threshold_db=-18, ratio=3, attack_ms=2, release_ms=80)]), out)[:, :n]


# ================================================================ main
def main():
    out_wav = sys.argv[1]
    scenes, total = timeline()
    (HERE / "timeline.js").write_text(
        "// Generated by build_audio.py. Scenes are whole bars of the 96 BPM music.\n"
        "window.TIMELINE = " + json.dumps({"duration": round(total, 3), "scenes": scenes}) + ";\n",
        encoding="utf-8",
    )
    cues = json.loads(subprocess.run(["node", str(HERE / "cues.mjs")], check=True, capture_output=True, text=True).stdout)
    print(f"{len(cues)} animation cues")

    n = int(total * SR)
    m = music(total, scenes)[:, :n]
    e = effects(total, scenes, cues)[:, :n]
    e *= rms(m) / rms(e) * 10 ** (-3 / 20)
    mix = m + e
    master = Pedalboard([
        HighpassFilter(35),
        LowShelfFilter(cutoff_frequency_hz=90, gain_db=-2.0),
        HighShelfFilter(cutoff_frequency_hz=7000, gain_db=3.0),
        Compressor(threshold_db=-16, ratio=2.2, attack_ms=15, release_ms=150),
        Limiter(threshold_db=-1.5, release_ms=80),
        Gain(-1.5),  # the limiter adds make-up gain; bring the ceiling back under 0 dBFS
    ])
    mix = mix / np.abs(mix).max() * 0.7
    mix = fx(master, mix)[:, :n]
    t = np.arange(n) / SR
    mix *= np.clip((total - t) / 0.05, 0, 1)
    sf.write(out_wav, mix.T, SR, subtype="PCM_24")
    print(f"total {total:.2f}s; wrote {out_wav}")


if __name__ == "__main__":
    main()
