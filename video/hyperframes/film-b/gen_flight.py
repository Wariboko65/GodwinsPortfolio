"""Generates compositions/flight.html: one 3D world, one camera, no cuts. Run: python3 gen_flight.py
World units are px; an element at depth z shows at scale P / (P - (z + W)), where W is the camera's push."""
P = 1200
GRID = ["extensions-manager", "conference-ticket", "multi-step-form", "calculator", "advice-generator", "newsletter", "clipboard",
        "huddle", "testimonials-grid", "fylo-storage", "chat-illustration", "nft-preview", "three-column", "order-summary"]
FLY0, FLY1, W0, W1 = 8.4, 11.6, 0, 9300          # corridor flight: linear push, so each card's pass time is known
SPEED = (W1 - W0) / (FLY1 - FLY0)
PZ = -10500                                       # the paper world's plane
els, tw = [], []

def put(id_, x, y, z, html, cls="", style=""):
    els.append(f'<div id="{id_}" class="o {cls}" style="transform:translate3d({x}px,{y}px,{z}px) translate(-50%,-50%);{style}">{html}</div>')

# --- software world (z = 0): the name, the JOPAD flow
put("fb-win", 0, 0, 0, "", "win")
put("fb-name", 0, -300, 0, 'John Godwin Oamien<span id="fb-cur">_</span>', "name")
put("fb-sub", 0, -170, 0, "/software · Frontend / Full Stack Developer", "mono lime")
nodes = [("01 / BOOK", "Client picks a consultation slot"), ("02 / CHECK", "Server confirms the slot is free"),
         ("03 / SCHEDULE", "Calendar invite and Meet link"), ("04 / CONFIRM", "Confirmation emails go out")]
for i, (n, t) in enumerate(nodes):
    put(f"fb-n{i}", 1900 + i * 380, 60, 0, f'<p class="nn">{n}</p><p class="nt">{t}</p>', "node")
    if i < 3: put(f"fb-wire{i}", 1900 + i * 380 + 190, 60, 0, f'<b id="fb-wb{i}"></b>', "wire")
put("fb-jt", 2470, -260, 0, "JOPAD Advisory", "title")
put("fb-js", 2470, -150, 0, "A booking platform that runs itself · 2026", "mono grey")
# --- the corridor of solutions, deep in z
cards = []
for i, g in enumerate(GRID):
    side = -1 if i % 2 == 0 else 1
    z = -700 - i * 640
    x = 4200 + side * (250 + (i % 3) * 30)
    y = (-150 if (i // 2) % 2 else 150)
    if i == len(GRID) - 1: x, y, z = 4200, 0, -9650
    put(f"fb-c{i}", x, y, z, f'<img src="assets/img/{g}.jpg" alt="">', "card", f"--ry:{-side * 28 if i < len(GRID) - 1 else 0}deg")
    cards.append(z)

# --- the paper world, on one plane far down the corridor
put("fb-paper", 7000, 0, PZ, "", "paper")
put("fb-plinth", 3700, 60, PZ, '<svg viewBox="0 0 600 520" width="600" height="520"><rect id="fb-sq" x="80" y="40" width="380" height="380" fill="none" stroke="#a9471f" stroke-width="6"/>'
    '<path class="fb-d" d="M80 470 H460 M80 456 V484 M460 456 V484" stroke="#a9471f" stroke-width="4" fill="none" pathLength="1"/>'
    '<path class="fb-d" d="M510 40 V420 M496 40 H524 M496 420 H524" stroke="#a9471f" stroke-width="4" fill="none" pathLength="1"/>'
    '<text x="270" y="510" text-anchor="middle" class="dim">450</text><text x="540" y="240" class="dim">450</text></svg>', "plan")
put("fb-et", 4500, -250, PZ, "Field inspection", "serif")
put("fb-es", 4500, -140, PZ, "NDDC · July – December 2025 · PLINTH 450 × 450 × 1000 mm", "mono clay")
photos = [("plinth-measurement", "Measuring a concrete plinth"), ("earthing-installation", "Earthing system"),
          ("pole-measurement", "Checking pole dimensions"), ("streetlights-night", "Night-time functional check")]
for i, (p, c) in enumerate(photos):
    put(f"fb-p{i}", 5300 + i * 780, (-60 if i % 2 else 130), PZ, f'<img src="assets/img/{p}.jpg" alt=""><p>{c}</p>', "photo", f"--rz:{[-2, 1.5, -1, 2][i]}deg")
daily = [[23.895, 8.95], [27.75, 4.054], [18.14, 2.03], [17.15, 3.826], [20.34, 2.68], [18.37, 3.26]]
bars = "".join(f'<i class="bf" style="left:{60 + k * 118}px;height:{f / 27.75 * 400:.0f}px"></i><i class="bm" style="left:{110 + k * 118}px;height:{m / 27.75 * 400:.0f}px"></i>' for k, (f, m) in enumerate(daily))
put("fb-waste", 9500, 40, PZ, f'<p class="wk">B.Eng. research · hostel solid waste study</p><p class="wn"><span id="fb-kg">0.0</span><small> kg</small></p>'
    f'<p class="wm">weighed · 6 days · 2 hostels · 9 categories</p><div class="wb">{bars}</div>', "waste")

# --- the camera: [time, x, y, W, ease]; the world moves opposite to the camera
CAM = [(0.0, 0, 260, 300, None), (2.4, 0, 120, -250, "power2.inOut"), (4.4, -2050, -60, 250, "power2.inOut"),
       (6.6, -2850, -60, 250, "power1.inOut"), (7.6, -2470, 40, -150, "power2.inOut"), (FLY0, -4200, 0, W0, "power2.in"),
       (FLY1, -4200, 0, W1, "none"), (12.6, -3900, -40, -PZ - 150, "power2.out"), (15.0, -4100, -20, -PZ + 120, "power1.inOut"),
       (19.6, -7700, 0, -PZ + 250, "power2.inOut"), (21.2, -9500, 0, -PZ - 120, "power2.inOut"), (24.6, -9500, 20, -PZ + 120, "power1.inOut"),
       (29.0, -7000, 0, -PZ - 4200, "power2.inOut")]
for (t0, *_), (t1, x, y, w, e) in zip(CAM, CAM[1:]):
    tw.append(f'tl.to("#fb-world", {{ x: {x}, y: {y}, z: {w}, duration: {t1 - t0:.3f}, ease: "{e}" }}, {t0});')
x0, y0, w0 = CAM[0][1:4]
tw.insert(0, f'gsap.set("#fb-world", {{ x: {x0}, y: {y0}, z: {w0} }});')
# --- things act as the camera reaches them
tw += [f'tl.fromTo("#fb-cur", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.01, repeat: 5, yoyo: true, repeatDelay: 0.39 }}, 0.4);',
       'tl.fromTo("#fb-sub", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, 1.3);']
for i, t in enumerate([3.6, 4.4, 5.2, 6.0]):
    tw.append(f'tl.fromTo("#fb-n{i}", {{ borderColor: "#2b3038", boxShadow: "0 0 0 rgba(200,241,105,0)" }}, {{ borderColor: "#c8f169", boxShadow: "0 0 60px rgba(200,241,105,0.4)", duration: 0.25 }}, {t});')
    if i < 3: tw.append(f'tl.fromTo("#fb-wb{i}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power2.inOut" }}, {t + 0.25});')
tw += ['tl.fromTo("#fb-jt", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, 6.7);',
       'tl.fromTo("#fb-js", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 6.9);']
for i, z in enumerate(cards[:-1]):
    t_pass = FLY0 + (P * 0.8 - z - W0) / SPEED        # when the card is about to reach the lens
    tw.append(f'tl.to("#fb-c{i}", {{ opacity: 0, duration: 0.1 }}, {t_pass - 0.1:.3f});')
tw.append(f'tl.to("#fb-count", {{ opacity: 0, filter: "blur(10px)", duration: 0.2 }}, {FLY0 + 1.55});')
tw.append(f'{{ const c = {{ v: 0 }}, el = document.getElementById("fb-cnt"); tl.fromTo(c, {{ v: 0 }}, {{ v: 14, duration: 1.7, ease: "none", onUpdate: () => (el.textContent = Math.max(1, Math.ceil(c.v))) }}, {FLY0 - 0.2}); }}')
tw.append(f'tl.fromTo("#fb-count", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {FLY0 - 0.3});')
# the camera passes through the last card: it fades as the lens reaches it, the software world goes with it
tw.append(f'tl.to("#fb-c13", {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, {FLY1 + 0.35});')
tw.append(f'tl.to([".soft"], {{ opacity: 0, duration: 0.3 }}, {FLY1 - 0.4});')
tw += ['tl.fromTo(".fb-d", { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.45, ease: "power2.inOut", stagger: 0.15 }, 13.0);',
       'tl.fromTo(".dim", { opacity: 0 }, { opacity: 1, duration: 0.15, stagger: 0.15 }, 13.35);',
       'tl.fromTo("#fb-et", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, 13.6);',
       'tl.fromTo("#fb-es", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 13.85);',
       'tl.fromTo("#fb-waste .bf, #fb-waste .bm", { scaleY: 0 }, { scaleY: 1, duration: 0.55, ease: "expo.out", stagger: 0.06 }, 20.6);',
       'tl.fromTo("#fb-waste .wn", { opacity: 0, scale: 1.5, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, 22.0);',
       '{ const c = { v: 0 }, el = document.getElementById("fb-kg"); tl.fromTo(c, { v: 0 }, { v: 150.4, duration: 1.0, ease: "power3.out", onUpdate: () => (el.textContent = c.v.toFixed(1)) }, 22.0); }',
       'tl.fromTo("#fb-waste .wm", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 22.6);']

CSS = '''
    @font-face { font-family: "Schibsted Grotesk"; src: url("assets/fonts/schibsted.woff2") format("woff2"); font-weight: 400 900; }
    @font-face { font-family: "Newsreader"; src: url("assets/fonts/newsreader.woff2") format("woff2"); font-weight: 200 800; }
    @font-face { font-family: "JetBrains Mono"; src: url("assets/fonts/jbmono.woff2") format("woff2"); font-weight: 100 800; }
    #root { position: absolute; inset: 0; overflow: hidden; background: #0d0f12; font-family: "Schibsted Grotesk"; color: #eceae4; }
    #fb-view { position: absolute; inset: 0; perspective: 1200px; perspective-origin: 960px 540px;
      background-image: linear-gradient(#2b303844 2px, transparent 2px), linear-gradient(90deg, #2b303844 2px, transparent 2px); background-size: 90px 90px; }
    #fb-world { position: absolute; left: 960px; top: 540px; width: 0; height: 0; transform-style: preserve-3d; }
    .o { position: absolute; left: 0; top: 0; white-space: nowrap; }
    .win { width: 1700px; height: 980px; border: 2px solid #2b3038; border-radius: 28px; background: #12151a; }
    .name { font-weight: 800; font-size: 130px; letter-spacing: -0.04em; }
    .mono { font-family: "JetBrains Mono"; font-weight: 600; font-size: 30px; }
    .lime { color: #c8f169; } .grey { color: #9ea3ab; } .clay { color: #a9471f; }
    .node { width: 330px; height: 270px; background: #16191e; border: 3px solid #2b3038; border-radius: 18px; padding: 26px; white-space: normal; }
    .nn { font-family: "JetBrains Mono"; font-size: 26px; color: #9ea3ab; font-weight: 600; }
    .nt { font-size: 36px; font-weight: 700; line-height: 1.1; margin-top: 16px; }
    .wire { width: 50px; height: 4px; } .wire b { display: block; width: 100%; height: 100%; background: #c8f169; transform-origin: 0 50%; }
    .title { font-weight: 800; font-size: 120px; letter-spacing: -0.03em; }
    .card { width: 460px; height: 290px; border-radius: 14px; overflow: hidden; border: 2px solid #2b3038; box-shadow: 0 30px 80px rgba(0,0,0,0.6); rotate: y var(--ry); }
    .card img, .photo img { width: 100%; height: 100%; object-fit: cover; object-position: top; display: block; }
    #fb-count { position: absolute; left: 0; width: 1920px; top: 800px; text-align: center; font-weight: 800; font-size: 150px; color: #c8f169; letter-spacing: -0.04em; white-space: nowrap; }
    #fb-count small { font-size: 44px; color: #eceae4; letter-spacing: 0; }
    .paper { width: 14000px; height: 9000px; background: #f2eee5; }
    .plan .dim { font-family: "JetBrains Mono"; font-weight: 600; font-size: 34px; fill: #a9471f; }
    .serif { font-family: "Newsreader"; font-weight: 500; font-size: 120px; color: #13272e; letter-spacing: -0.02em; }
    .photo { width: 560px; height: 620px; background: #fbf9f4; padding: 16px 16px 70px; border-radius: 10px; box-shadow: 0 30px 70px rgba(19,39,46,0.22); rotate: z var(--rz); }
    .photo p { position: absolute; left: 20px; bottom: 18px; font-family: "JetBrains Mono"; font-size: 28px; font-weight: 600; color: #13272e; }
    .waste { width: 1700px; height: 1000px; background: #0f3a44; border-radius: 30px; color: #f2eee5; }
    .wk { position: absolute; left: 90px; top: 110px; font-family: "JetBrains Mono"; font-size: 30px; color: #b9c9cc; }
    .wn { position: absolute; left: 80px; top: 180px; font-family: "Newsreader"; font-size: 250px; line-height: 1; color: #f0a46f; transform-origin: 0 60%; }
    .wn small { font-size: 0.3em; }
    .wm { position: absolute; left: 92px; top: 470px; font-family: "JetBrains Mono"; font-size: 30px; color: #b9c9cc; }
    .wb { position: absolute; left: 900px; top: 300px; width: 760px; height: 560px; }
    .wb i { position: absolute; bottom: 0; width: 46px; border-radius: 6px 6px 0 0; transform-origin: 50% 100%; }
    .bf { background: #f0a46f; } .bm { background: #b9c9cc; }
'''
paperw = {"fb-paper", "fb-plinth", "fb-et", "fb-es", "fb-waste"} | {f"fb-p{i}" for i in range(4)}
els = [e.replace('class="o ', 'class="o paperw ', 1) if any(f'id="{s}"' in e for s in paperw) else e for e in els]
tw.append(f'tl.fromTo(".paperw", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.0, ease: "power2.in" }}, {FLY0 + 1.6});')
soft = {"fb-win", "fb-name", "fb-sub", "fb-jt", "fb-js"} | {f"fb-n{i}" for i in range(4)} | {f"fb-wire{i}" for i in range(3)}
els = [e.replace('class="o ', 'class="o soft ', 1) if any(f'id="{s}"' in e for s in soft) else e for e in els]
open("compositions/flight.html", "w").write(f'''<template>
  <style>{CSS}
  </style>
  <div id="root" data-composition-id="flight" data-width="1920" data-height="1080">
    <div id="fb-stage" class="clip" data-start="0" data-duration="30" data-track-index="0" style="position:absolute;inset:0" data-layout-allow-overflow data-layout-allow-overlap>
      <div id="fb-view"><div id="fb-world">
        {chr(10).join("        " + e for e in els)}
      </div></div>
      <div id="fb-count"><span id="fb-cnt">0</span> <small>Frontend Mentor solutions</small></div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + t for t in tw)}
      window.__timelines["flight"] = tl;
    }})();
  </script>
</template>
''')
print("flight.html written:", len(els), "objects,", len(tw), "tweens")
