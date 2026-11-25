"""Sound design for the engineering film: no music, the drawing, the prints and the chart carry it.
Recorded CC0 foley (Freesound via Openverse): pencil/paper strokes, paper slides, taps, pops; synthesised air only
for moves; one shared room (OneTake sfx_palette Score). Times = scene start + the scene's own tween / clip times
(the Manim drawing's beats come from sources/manim/plinth.py, the chart's from sources/remotion/src/WasteChart.tsx).
Usage: python3 score.py foley_dir out.wav"""
import json, os, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.expanduser("~/.claude/skills/onetake/scripts"))
from sfx_palette import Score, air, sub, glass, pan_of, SR

FOLEY, OUT = sys.argv[1], sys.argv[2]
LIB = json.load(open(f"{FOLEY}/library.json"))
rng = np.random.default_rng(23)
POOL = {k: sorted(n for n, v in LIB.items() if v["kind"] == k) for k in ("click", "key", "tap", "pop", "swish", "slide", "scroll")}
cache = {}
def L(n):
    if n not in cache: cache[n] = sf.read(f"{FOLEY}/{n}.wav")[0].astype(np.float64)
    return cache[n]
turn = {k: 0 for k in POOL}
def take(kind):
    p = POOL[kind]; turn[kind] = (turn[kind] + 1 + int(rng.integers(0, 2))) % len(p); return L(p[turn[kind]])
S = Score(dur=30)
def hit(kind, t, g, x=960, send=0.25): S.place(take(kind), t=t, gain=g * (0.85 + 0.3 * rng.random()), pan=pan_of(x), send=send)
def move(t, dur, g, x0=960, x1=960, f0=250, f1=2600, send=0.45): S.place(air(dur, f0, f1, 1.3, 0.45), t=t, gain=g, pan=pan_of(x0), pan_to=pan_of(x1), send=send)
PENCIL = L("slide3")  # "Underlining Stroke on Paper": the pencil
def stroke(t, dur, g, x=470):  # a pencil stroke cut to the length of the line being drawn
    n = int(dur * SR); s = PENCIL[:n].copy(); f = np.minimum(1, np.minimum(np.arange(n) / (0.01 * SR), (n - np.arange(n)) / (0.04 * SR)))
    S.place(s * f, t=t, gain=g, pan=pan_of(x), send=0.2)

# ---- hook 0-2.6: the name, a pencil line under it, the line slides down to become the plan's first edge
S.place(sub(60, 0.5), t=0.0, gain=0.28, send=0.2); hit("tap", 0.0, 0.3, 400)
stroke(0.45, 0.5, 0.55, 700)
hit("swish", 0.93, 0.15, 400, 0.4)
move(2.0, 0.5, 0.2, 900, 470, 300, 1800)
# ---- site 2.6-15.1: Manim draws the plinth (its beats, from plinth.py), the facts arrive, prints are dealt
P = 2.6
stroke(P + 0.0, 0.7, 0.5)                                   # plan square
stroke(P + 0.7, 0.4, 0.4, 470); hit("key", P + 0.85, 0.22, 470)   # width dimension + its label
stroke(P + 1.15, 0.4, 0.4, 640); hit("key", P + 1.3, 0.22, 640)   # depth dimension
move(P + 1.95, 0.9, 0.22, 470, 470, 200, 1500)              # plan becomes elevation
for j in range(7): stroke(P + 2.85 + j * 0.1, 0.09, 0.28, 440 + j * 10)   # concrete hatch, quick strokes
hit("tap", P + 3.55, 0.45, 470)                             # base plate set down
move(P + 3.85, 0.7, 0.18, 470, 470, 160, 900); S.place(sub(70, 0.5), t=P + 4.3, gain=0.2, send=0.3)  # pole rises, settles
hit("tap", P + 1.1, 0.2, 1300)                              # title lands
hit("key", P + 2.6, 0.25, 1300)                             # the spec line
for i in range(4):
    t = P + 6.5 + i * 0.5
    hit("slide", t, 0.3, 1400, 0.3); hit("tap", t + 0.14, 0.4, 1300 + 120 * (i % 2))   # each print slides, lands
S.place(PENCIL[: int(0.3 * SR)][::-1] * 0.0, t=P + 9.2, gain=0)   # (drawing lifts silently)
hit("swish", P + 9.3, 0.4, 1200, 0.4)                       # prints swept off
hit("slide", P + 9.6, 0.32, 960, 0.3); hit("tap", P + 9.78, 0.45, 960)   # the scale print dealt into the middle
hit("key", P + 10.2, 0.2, 960)
# ---- waste 15.1-26: the print grows into the study; the chart (Remotion) rises, lands, regroups
W = 15.1; C = W + 0.55                                      # chart clip starts 0.55 s into the scene
move(W, 0.6, 0.4, 960, 960, 180, 2600, 0.5)
for i in (0, 2, 4): hit("pop", C + (18 + i * 4) / 30 + 0.12, 0.3, 1000 + i * 128)
S.place(sub(55, 0.7), t=C + 56 / 30, gain=0.5, send=0.25); hit("tap", C + 56 / 30, 0.5, 400)   # 150.4 kg lands
move(C + 150 / 30, 0.5, 0.25, 1300, 1300, 300, 2200)       # bars regroup
for i in (0, 1, 3): hit("pop", C + (158 + i * 5) / 30 + 0.12, 0.28, 1000 + i * 150)
hit("tap", C + 270 / 30, 0.35, 500)                         # 83.5% line
# ---- end 26-30: the claim is the loudest moment, then the mark, then quiet
E = 26.0
for t, g in ((E, 0.5), (E + 0.3, 0.6), (E + 0.55, 0.72)):
    S.place(sub(52, 0.8), t=t, gain=g, send=0.25); hit("tap", t, g * 0.7, 960, 0.2)
move(E + 1.48, 0.3, 0.22, 960, 960, 400, 3000)
S.place(glass(1174.7, 1.4, 0.4), t=E + 1.7, gain=0.06, send=0.6)
hit("slide", E + 2.3, 0.22, 960, 0.3)
S.write(OUT)
