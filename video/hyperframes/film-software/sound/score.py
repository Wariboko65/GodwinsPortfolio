"""Sound design for the software film: no music, the motion carries it.
Recorded CC0 foley (Freesound, via Openverse) for every contact, synthesised air only for moves, one shared room
(OneTake's sfx_palette Score). Times are the composition's own: scene start + the tween's time in that scene.
Usage: python3 score.py foley_dir out.wav"""
import json, os, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.expanduser("~/.claude/skills/onetake/scripts"))
from sfx_palette import Score, air, sub, wood, glass, pan_of, SR

FOLEY, OUT = sys.argv[1], sys.argv[2]
LIB = json.load(open(f"{FOLEY}/library.json"))
rng = np.random.default_rng(11)
def kinds(k): return sorted(n for n, v in LIB.items() if v["kind"] == k)
POOL = {k: kinds(k) for k in ("click", "key", "tap", "pop", "swish", "slide", "scroll")}
cache = {}
def L(name):
    if name not in cache: cache[name] = sf.read(f"{FOLEY}/{name}.wav")[0].astype(np.float64)
    return cache[name]
turn = {k: 0 for k in POOL}
def take(kind):  # rotate through the takes of a kind, never the same one twice in a row
    p = POOL[kind]; turn[kind] = (turn[kind] + 1 + int(rng.integers(0, 2))) % len(p); return L(p[turn[kind]])

S = Score(dur=30)
def hit(kind, t, g, x=960, send=0.25): S.place(take(kind), t=t, gain=g * (0.85 + 0.3 * rng.random()), pan=pan_of(x), send=send)
def move(t, dur, g, x0=960, x1=960, f0=250, f1=2600, send=0.45):  # a move's air: peak lands on its fastest frame
    S.place(air(dur, f0, f1, 1.3, 0.45), t=t, gain=g, pan=pan_of(x0), pan_to=pan_of(x1), send=send)

# ---- hook 0-2.6: the name lands, /software is typed, the camera pushes into the caret
S.place(sub(58, 0.6), t=0.0, gain=0.35, send=0.2); hit("tap", 0.0, 0.35, 400)
for i in range(9): hit("key", 0.7 + i * 0.055, 0.42 if i % 3 == 0 else 0.3, 170 + i * 36, 0.12)
hit("swish", 1.33, 0.18, 600, 0.4)
move(2.12, 0.5, 0.55, 960, 960, 300, 3600, 0.5)
# ---- JOPAD 2.6-11.1: the cursor clicks the slot and that click runs the flow
J = 2.6
move(J + 0.05, 0.45, 0.16, 1700, 1100, 500, 2600)
hit("click", J + 0.56, 0.6, 950, 0.15); hit("click", J + 0.62, 0.35, 950, 0.15)          # mouse down, up
hit("pop", J + 0.62, 0.42, 950)
for k, t in enumerate([0.9, 1.6, 2.3]):
    move(J + t, 0.5, 0.22, 1400, 500, 220, 1800, 0.5)                                       # the camera tracks right
    S.place(glass([880, 988, 1175][k], 0.7, 0.5), t=J + [1.3, 2.0, 2.7][k], gain=0.07, pan=0.1, send=0.55)
hit("tap", J + 1.35, 0.3, 960); hit("pop", J + 2.05, 0.3, 900); hit("slide", J + 2.2, 0.14, 1000)
hit("swish", J + 2.72, 0.3, 1000, 0.4)                                                    # the email flies out
move(J + 3.0, 0.65, 0.3, 960, 960, 180, 1200, 0.55)                                       # pull back to the system
hit("tap", J + 3.35, 0.32, 760)
for i in (0, 2, 4, 6): hit("click", J + 3.65 + i * 0.05, 0.22, 600 + i * 120, 0.2)        # chips (every other one)
move(J + 5.62, 0.36, 0.6, 1600, 200, 400, 4200, 0.4)                                      # whip out
# ---- tunnel 11.1-15.6: one long camera air through the corridor, the count's pulse, the last card lands
T = 11.1
move(T, 2.6, 0.42, 960, 960, 160, 3200, 0.6)
hit("tap", T + 2.4, 0.4, 960); hit("pop", T + 2.72, 0.45, 960)
# ---- Vortex Horizon 15.6-22.6: the square opens into the window, the page scrolls, the filter is clicked
V = 15.6
hit("slide", V + 0.02, 0.32, 960, 0.4); move(V, 0.6, 0.18, 960, 960, 200, 1400)
hit("tap", V + 0.78, 0.25, 500)
move(V + 1.0, 0.5, 0.12, 1700, 1300, 600, 2400)
sc = L(POOL["scroll"][0]); S.place(sc[: int(1.9 * SR)] * np.minimum(1, np.linspace(6, 0, int(1.9 * SR))), t=V + 1.3, gain=0.5, pan=pan_of(1300), send=0.15)
move(V + 3.4, 0.45, 0.12, 1300, 880, 600, 2400)
hit("click", V + 3.95, 0.6, 880, 0.15); hit("click", V + 4.01, 0.33, 880, 0.15)
hit("swish", V + 6.45, 0.38, 960, 0.45)                                                   # the window drops away
# ---- stack 22.6-26: five layers land, a few chips sound per row (not one per chip)
K = 22.6
for r in range(5):
    t0 = K + 0.12 + r * 0.32
    hit("tap", t0, 0.28, 300, 0.2)
    for j in (1, 3, 5): hit("key", t0 + 0.06 + j * 0.035, 0.22, 700 + j * 160, 0.15)
hit("swish", K + 3.05, 0.25, 960, 0.4)
# ---- end 26-30: the claim is the loudest thing in the film, then the mark, then quiet
E = 26.0
for t, g in ((E + 0.0, 0.55), (E + 0.3, 0.7)):
    S.place(sub(52, 0.8), t=t, gain=g, send=0.25); hit("tap", t, g * 0.7, 960, 0.2)
move(E + 1.42, 0.3, 0.25, 960, 960, 400, 3000)
S.place(glass(1318.5, 1.4, 0.4), t=E + 1.65, gain=0.06, send=0.6)
hit("slide", E + 2.25, 0.22, 960, 0.3)
S.write(OUT)
print("wrote", OUT)
