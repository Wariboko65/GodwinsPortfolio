"""The NDDC street-light plinth (450 x 450 x 1000 mm, src/data/engineering.ts) as a technical drawing that
builds itself: plan view -> morphs into the elevation -> concrete hatch -> pole and base plate.
Manim Community Edition. Render: manim -qh --fps 30 -r 1920,1080 plinth.py Plinth
Background = the film's paper ground (#f2eee5), so the clip sits in the scene without a matte."""
from manim import *

PAPER, INK, CLAY, POLE = "#f2eee5", "#13272e", "#a9471f", "#2f6fb5"
U = 1 / 200  # scene units per mm: 450 mm -> 2.25, 1000 mm -> 5.0
MONO = "JetBrains Mono"

def dim_h(left, right, y, label):
    """horizontal dimension line with end ticks and a centred label below it"""
    l = Line([left, y, 0], [right, y, 0], color=CLAY, stroke_width=4)
    t1 = Line([left, y - 0.15, 0], [left, y + 0.15, 0], color=CLAY, stroke_width=4)
    t2 = Line([right, y - 0.15, 0], [right, y + 0.15, 0], color=CLAY, stroke_width=4)
    txt = Text(label, font=MONO, weight=BOLD, color=CLAY).scale(0.5).next_to(l, DOWN, buff=0.15)
    return VGroup(l, t1, t2), txt

def dim_v(x, bottom, top, label):
    l = Line([x, bottom, 0], [x, top, 0], color=CLAY, stroke_width=4)
    t1 = Line([x - 0.15, bottom, 0], [x + 0.15, bottom, 0], color=CLAY, stroke_width=4)
    t2 = Line([x - 0.15, top, 0], [x + 0.15, top, 0], color=CLAY, stroke_width=4)
    txt = Text(label, font=MONO, weight=BOLD, color=CLAY).scale(0.5).next_to(l, RIGHT, buff=0.2)
    return VGroup(l, t1, t2), txt

class Plinth(Scene):
    def construct(self):
        self.camera.background_color = PAPER
        W, H = 450 * U, 1000 * U
        cx, base = -3.6, -2.75
        # 1. plan view: the square seen from above
        plan = Square(side_length=W, color=INK, stroke_width=5).move_to([cx, base + W / 2 + 0.6, 0])
        pl = Text("PLAN", font=MONO, weight=BOLD, color=INK).scale(0.4).next_to(plan, UP, buff=0.25)
        dw, tw = dim_h(plan.get_left()[0], plan.get_right()[0], plan.get_bottom()[1] - 0.45, "450")
        dd, td = dim_v(plan.get_right()[0] + 0.45, plan.get_bottom()[1], plan.get_top()[1], "450")
        self.play(Create(plan), FadeIn(pl, shift=DOWN * 0.1), run_time=0.7, rate_func=rate_functions.ease_out_cubic)
        self.play(Create(dw), FadeIn(tw), run_time=0.45)
        self.play(Create(dd), FadeIn(td), run_time=0.45)
        self.wait(0.35)
        # 2. the square becomes the elevation: same width, 1000 mm tall
        elev = Rectangle(width=W, height=H, color=INK, stroke_width=5).move_to([cx, base + H / 2, 0])
        el = Text("ELEVATION", font=MONO, weight=BOLD, color=INK).scale(0.4).next_to(elev, UP, buff=0.25)
        dw2, tw2 = dim_h(elev.get_left()[0], elev.get_right()[0], elev.get_bottom()[1] - 0.45, "450")
        dh, th = dim_v(elev.get_right()[0] + 0.45, elev.get_bottom()[1], elev.get_top()[1], "1000 mm")
        self.play(Transform(plan, elev), Transform(pl, el), Transform(dw, dw2), Transform(tw, tw2),
                  ReplacementTransform(dd, dh), ReplacementTransform(td, th), run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)
        # 3. concrete: a diagonal hatch fills the section
        lines = VGroup()
        x0, x1, y0, y1 = elev.get_left()[0], elev.get_right()[0], elev.get_bottom()[1], elev.get_top()[1]
        k = 0.34
        for i in range(-14, 8):  # 45-degree lines clipped to the rectangle by hand
            a = x0 + i * k
            p = [(a, y0), (a + (y1 - y0), y1)]
            (ax, ay), (bx, by) = p
            if bx < x0 or ax > x1: continue
            if ax < x0: ay += x0 - ax; ax = x0
            if bx > x1: by -= bx - x1; bx = x1
            lines.add(Line([ax, ay, 0], [bx, by, 0], color=INK, stroke_width=2, stroke_opacity=0.35))
        self.play(LaggedStartMap(Create, lines, lag_ratio=0.08), run_time=0.7)
        # 4. base plate and the pole rise from the top face
        plate = Rectangle(width=W * 0.7, height=0.12, color=POLE, fill_color=POLE, fill_opacity=1).next_to(elev, UP, buff=0)
        pole = Rectangle(width=0.32, height=1.25, color=POLE, fill_color=POLE, fill_opacity=1, stroke_width=0).next_to(plate, UP, buff=0)
        self.play(FadeIn(plate, shift=DOWN * 0.15), run_time=0.3)
        self.play(GrowFromEdge(pole, DOWN), FadeOut(pl), run_time=0.7, rate_func=rate_functions.ease_out_cubic)
        self.wait(5.2)
