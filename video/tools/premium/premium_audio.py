"""Soundtrack for a premium narrated edit: original narration + music bed + sound effects.

- Narration: the video's own voice track, untouched.
- Music: 100 BPM, light and curious; it ducks under the voice (driven by the narration's own
  loudness), drops out for the "So what's the real evidence?" beat and slams back in.
- Effects: one sound per cue registered by lice.html (hook, pops, counters, pin drops, stamps,
  zips, glitch, cut flashes...), so every graphic has its own sound.
Reuses the synthesis helpers from the portfolio's video/build_audio.py.
Usage: python3 premium_audio.py cues.json narration.wav out.wav [--hole START END] [--music-db -15]
  --hole: seconds where the music drops out (a pattern-interrupt beat); --music-db: music level vs. the voice
"""
import json
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
import build_audio as B  # noqa: E402
from build_audio import (SR, air, bell, click, ease_out, ep, filt, fx, glide, impact, midi, noise, pan, place,  # noqa: E402
                         reverse_swell, rms, supersaw, thump, tick, ts)
from pedalboard import (Chorus, Compressor, Delay, Gain, HighpassFilter, HighShelfFilter, LadderFilter, Limiter,  # noqa: E402
                        LowpassFilter, LowShelfFilter, Pedalboard, Reverb, Distortion)

PENTA = B.PENTA
RNG = np.random.default_rng(5)


def music(total, hole):
    bpm = 100
    beat = 60 / bpm
    bar = beat * 4
    n = int(total * SR) + SR
    times = np.arange(n) / SR
    chords = [(50, 54, 57, 61), (47, 50, 54, 57), (43, 47, 50, 54), (45, 49, 52, 57)]
    seg = bar * 2
    h0, h1 = hole
    pad, arp, bass, drums = (np.zeros((2, n)) for _ in range(4))
    for k, t0 in enumerate(np.arange(0, total, seg)):
        notes = chords[k % 4]
        d = seg + 1.0
        clip = sum(supersaw(midi(m), d, voices=4) for m in notes)
        env = np.minimum(1, ts(d) / 0.5) * np.minimum(1, (d - ts(d)) / 1.0)
        place(pad, clip * env, t0, 0.07)
        for st in range(16):  # pizzicato-like 8th-note plucks
            at = t0 + st * beat / 2
            if at > total:
                continue
            m = notes[[0, 2, 1, 3, 2, 3, 1, 2][st % 8]] + 12 + (12 if st % 8 == 5 else 0)
            v = 0.85 if st % 2 == 0 else 0.6
            place(arp, pan(ep(midi(m), 0.3) * np.exp(-ts(0.3) * 6), 0.35 + 0.3 * (st % 2)), at, 0.08 * v)
        root = midi(notes[0] - 12)
        for b in (0, 3, 4, 6):  # bouncy bass rhythm
            bt = t0 + b * beat / 2 * 2 if b < 4 else t0 + b * beat
            d2 = beat * 0.7
            y = (np.sin(2 * np.pi * root * ts(d2)) + 0.25 * np.sin(4 * np.pi * root * ts(d2))) * np.exp(-ts(d2) * 4) * np.minimum(1, ts(d2) / 0.005)
            place(bass, y, bt, 0.3)
    beats = np.arange(0, total, beat)
    K = B.impact(1.0, 0.1, 0.4) * 0
    t = ts(0.35)
    kick = np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t * 34)) / SR) * np.exp(-t * 9))
    for i, bt in enumerate(beats):
        if i % 2 == 0:
            place(drums, kick, bt, 0.42)
        if i % 4 == 2:
            sn = filt(noise(0.18), "band", [1200, 5000]) * np.exp(-ts(0.18) * 28)
            place(drums, sn, bt, 0.12)
        hat = filt(noise(0.04), "high", 8000, 4) * np.exp(-ts(0.04) * 110)
        place(drums, pan(hat, 0.65), bt + beat / 2, 0.07)
    pad = fx(Pedalboard([LadderFilter(mode=LadderFilter.Mode.LPF24, cutoff_hz=1400, resonance=0.1), Chorus(rate_hz=0.3, depth=0.3, mix=0.4),
                         Reverb(room_size=0.8, wet_level=0.35, dry_level=0.7, width=1.0)]), pad)[:, :n]
    arp = fx(Pedalboard([HighpassFilter(250), Delay(delay_seconds=beat * 0.75, feedback=0.25, mix=0.18),
                         Reverb(room_size=0.6, wet_level=0.25, dry_level=0.85, width=1.0)]), arp)[:, :n]
    bass = fx(Pedalboard([Distortion(drive_db=5), LowpassFilter(320)]), bass)[:, :n]
    mix = pad + arp + bass + drums
    # the music drops out for the question, then comes back with the answer
    gate = 1 - (np.clip((times - h0) / 0.08, 0, 1) * (1 - np.clip((times - h1) / 0.05, 0, 1)))
    gate = np.maximum(gate, 0.08)
    fade = np.clip(times / 0.3, 0, 1) * np.clip((total - times) / 0.6, 0, 1)
    return mix * gate * fade


def sfx(total, cues):
    n = int(total * SR) + 2 * SR
    dry = np.zeros((2, n))
    verb = np.zeros((2, n))
    tick_i = 0
    for c in cues:
        k, t = c["kind"], c["t"]
        if k == "hook":
            place(dry, impact(1.0, 0.5, 1.4), t, 0.5)
            for j, m in enumerate((74, 78, 81, 86)):
                place(verb, bell(midi(m), 1.6, 2.4), t + 0.02 + j * 0.03, 0.06)
        elif k == "cut":
            place(dry, thump(120, 60, 0.2, 22), t, 0.14)
            place(dry, air(0.16, 600, 3000, lambda p: (1 - np.clip(p, 0, 1)) ** 2), t, 0.06)
        elif k == "swish":
            d = c.get("dur", 0.3)
            place(dry, air(d, 300, 2400, lambda p: np.sin(np.pi * np.clip(p, 0, 1)) ** 2), t, 0.18)
        elif k == "pop":
            place(dry, thump(190, 90, 0.16), t, 0.25)
            place(verb, ep(midi(PENTA[5 + RNG.integers(0, 4)] + 12), 0.4), t, 0.08)
            place(dry, click(0.01, 4500), t, 0.15)
        elif k == "pill":
            place(dry, thump(160, 80, 0.2), t, 0.25)
            for m in (74, 78, 81):
                place(verb, ep(midi(m + 12), 0.5), t, 0.05)
            place(dry, air(0.25, 500, 3000, lambda p: 3 * (1 - np.clip(p, 0, 1)) ** 2 / 3), t - 0.05, 0.12)
        elif k == "count":
            d, steps = c["dur"], c.get("steps", 18)
            last = -1
            for f in range(int(d * 200) + 1):
                tt = f / 200
                q = int(steps * ease_out(tt / d))
                if q != last:
                    place(dry, tick(1400 + 1500 * q / steps, 0.025), t + tt, 0.16)
                    last = q
        elif k == "ding":
            place(verb, bell(midi(86), 1.6, 2.6), t, 0.14)
            place(verb, bell(midi(93), 1.2, 3.0), t + 0.03, 0.06)
        elif k == "drop":  # map pin landing
            place(dry, glide(0.14, 1400, 500, lambda p: p, False) * np.exp(-ts(0.14) * 10), t, 0.08)
            place(dry, thump(220, 70, 0.22, 16), t + 0.12, 0.3)
        elif k == "zip":
            d = c.get("dur", 0.4)
            y = glide(d, midi(74), midi(86), B.ease_in_out, False) * np.sin(np.pi * ts(d) / d) ** 1.2
            place(verb, y, t, 0.06)
        elif k == "click":
            place(dry, click(0.012, 4000), t, 0.25)
            place(verb, tick(midi(81 + 12), 0.03), t, 0.08)
        elif k == "tick":
            place(verb, tick(midi(PENTA[3 + tick_i % 6] + 12), 0.035), t, 0.12)
            tick_i += 1
        elif k == "stamp":
            place(dry, impact(0.9, 0.3, 0.9), t, 0.42)
            slap = filt(noise(0.06), "band", [700, 3500]) * np.exp(-ts(0.06) * 60)
            place(dry, slap, t, 0.35)
        elif k == "riser":
            d = c.get("dur", 0.8)
            place(dry, reverse_swell(midi(69), d), t, 0.22)
            place(verb, glide(d, midi(57), midi(81), lambda p: p ** 2, False) * (ts(d) / d) ** 2, t, 0.06)
        elif k == "impact":
            big = c.get("big")
            place(dry, impact(1.2 if big else 1.0, 0.5, 1.8 if big else 1.4), t, 0.6 if big else 0.5)
            if big:
                for j, m in enumerate((62, 69, 74, 78)):
                    place(verb, bell(midi(m), 2.5, 1.6), t + j * 0.02, 0.07)
        elif k == "glitch":
            d = 0.3
            tt = ts(d)
            sq = np.sign(np.sin(2 * np.pi * 220 * tt)) * (np.floor(tt * 40) % 2) * np.exp(-tt * 6)
            place(dry, filt(sq, "band", [300, 4000]), t, 0.06)
        elif k == "decay":
            d = c.get("dur", 0.7)
            place(dry, glide(d, midi(74), midi(50), lambda p: p, False) * (1 - ts(d) / d), t, 0.06)
            place(dry, air(d, 800, 5000, lambda p: (1 - np.clip(p, 0, 1))), t, 0.05)
    room = Pedalboard([HighpassFilter(150), Reverb(room_size=0.55, damping=0.5, wet_level=0.35, dry_level=0.85, width=1.0)])
    out = dry + fx(room, verb)[:, :n]
    return fx(Pedalboard([HighpassFilter(40), Compressor(threshold_db=-18, ratio=3, attack_ms=2, release_ms=80)]), out)[:, :n]


def main():
    data = json.load(open(sys.argv[1]))
    total = data["duration"]
    cues = data["cues"]
    voice, vsr = sf.read(sys.argv[2])
    assert vsr == SR
    voice = voice.T
    n = int(total * SR)
    voice = np.pad(voice, ((0, 0), (0, max(0, n - voice.shape[1]))))[:, :n]
    # ducking envelope from the narration's own loudness
    v = np.abs(voice.mean(axis=0))
    win = int(0.03 * SR)
    env = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, mode="same"))
    env = (env > 0.01).astype(float)
    rel = int(0.25 * SR)
    env = np.convolve(env, np.ones(rel) / rel, mode="same")
    env = np.clip(env * 1.5, 0, 1)

    a = sys.argv
    hole = (float(a[a.index("--hole") + 1]), float(a[a.index("--hole") + 2])) if "--hole" in a else (-1, -1)
    mdb = float(a[a.index("--music-db") + 1]) if "--music-db" in a else -15
    m = music(total, hole)[:, :n]
    e = sfx(total, cues)[:, :n]
    vr = rms(voice)
    m *= vr / rms(m) * 10 ** (mdb / 20)
    e *= vr / rms(e) * 10 ** (-7 / 20)
    mix = voice + m * (1 - 0.55 * env) + e
    mix = mix / np.abs(mix).max() * 0.7
    master = Pedalboard([HighpassFilter(35), HighShelfFilter(cutoff_frequency_hz=8000, gain_db=1.5),
                         Compressor(threshold_db=-16, ratio=2.2, attack_ms=10, release_ms=120),
                         Limiter(threshold_db=-1.5, release_ms=80), Gain(-1.5)])
    mix = fx(master, mix)[:, :n]
    sf.write(sys.argv[3], mix.T, SR, subtype="PCM_24")
    print("wrote", sys.argv[3], f"{total:.2f}s")


if __name__ == "__main__":
    main()
