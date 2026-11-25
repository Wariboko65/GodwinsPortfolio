"""Generates Film C's scene files ("Verbs on the beat"). Edit the VERBS tables, then run: python3 gen_scenes.py
Every cut sits on the music's beat grid: beat k = k * BEAT seconds (the bed is trimmed so beat 0 is t = 0)."""
BEAT = 0.48786
def b(k): return round(k * BEAT * 30) / 30  # snap to frames
FONTS = '''@font-face { font-family: "Schibsted Grotesk"; src: url("assets/fonts/schibsted.woff2") format("woff2"); font-weight: 400 900; }
    @font-face { font-family: "Newsreader"; src: url("assets/fonts/newsreader.woff2") format("woff2"); font-weight: 200 800; }
    @font-face { font-family: "JetBrains Mono"; src: url("assets/fonts/jbmono.woff2") format("woff2"); font-weight: 100 800; }'''
C = {"dark": ("#0d0f12", "#eceae4", "#c8f169"), "lime": ("#c8f169", "#0d0f12", "#0d0f12"), "surf": ("#1d2127", "#eceae4", "#c8f169"),
     "paper": ("#f2eee5", "#13272e", "#a9471f"), "clay": ("#a9471f", "#f2eee5", "#f2eee5"), "deep": ("#0f3a44", "#f2eee5", "#f0a46f")}

# verb, ground, layout, proof html, label  (each verb holds 4 beats: word on beat 0, proof on 1, label on 2)
SW = [("BOOKS", "dark", "left", '<div class="nodes"><div class="nd on">01 / BOOK<b>Client picks a consultation slot</b></div><div class="nd">02 / CHECK<b>Server confirms the slot is free</b></div></div>', "JOPAD Advisory · contract · 2026"),
      ("SCHEDULES", "lime", "top", '<div class="nodes"><div class="nd on">03 / SCHEDULE<b>Calendar invite and Meet link</b></div><div class="nd on">04 / CONFIRM<b>Confirmation emails go out</b></div></div>', "Node · Express · MongoDB · Google Calendar API"),
      ("SHIPS", "surf", "grid", "GRID", "14 Frontend Mentor solutions"),
      ("ANIMATES", "dark", "right", '<div class="shot"><img src="assets/img/extensions-manager.jpg?shot" alt=""></div>', "Browser Extensions Manager · React · Framer Motion"),
      ("DESIGNS", "lime", "left", '<div class="shot"><img src="assets/img/vortex-hero.jpg" alt=""></div>', "Vortex Horizon · 2022")]
EN = [("INSPECTS", "paper", "right", '<div class="photo"><img src="assets/img/plinth-measurement.jpg" alt=""></div>', "Plinth · 450 × 450 × 1000 mm · NDDC"),
      ("MEASURES", "clay", "left", '<div class="photo"><img src="assets/img/pole-measurement.jpg" alt=""></div>', "Checking pole dimensions"),
      ("CHECKS", "deep", "right", '<div class="photo"><img src="assets/img/streetlights-night.jpg" alt=""></div>', "Night-time functional check"),
      ("WEIGHS", "paper", "num", '<div class="num"><span class="cnt" data-to="150.4">0</span><small> kg</small></div>', "6 days · 2 hostels · 9 categories"),
      ("SORTS", "deep", "top", '<div class="bars">' + "".join(f'<div class="bar"><span>{v}%</span><i style="height:{v / 80.46 * 300:.0f}px"></i><em>{k}</em></div>' for k, v in [("Plastics", 80.46), ("Food", 11.15), ("Cardboard", 3.2), ("Paper", 2.49), ("Residual", 1.36)]) + '</div>', "Female hostel · % by weight · 9 categories in all")]
GRID = ["extensions-manager", "conference-ticket", "multi-step-form", "calculator", "advice-generator", "newsletter", "clipboard", "huddle", "testimonials-grid", "fylo-storage", "chat-illustration", "nft-preview", "three-column", "order-summary"]

CSS = '''
    #root { position: absolute; inset: 0; overflow: hidden; font-family: "Schibsted Grotesk"; }
    .v { position: absolute; inset: 0; }
    .v .field { position: absolute; inset: 0; }
    .v .word { position: absolute; font-weight: 800; letter-spacing: -0.05em; line-height: 0.85; white-space: nowrap; }
    .v .proof { position: absolute; }
    .v .lab { position: absolute; font-family: "JetBrains Mono"; font-weight: 600; font-size: 34px; letter-spacing: 0.02em; white-space: nowrap; }
    .nodes { display: flex; gap: 24px; }
    .nd { width: 420px; height: 230px; border-radius: 18px; border: 3px solid currentColor; padding: 26px 28px; font-family: "JetBrains Mono"; font-size: 26px; font-weight: 600; opacity: 0.55; }
    .nd.on { opacity: 1; }
    .nd b { display: block; font-family: "Schibsted Grotesk"; font-size: 40px; line-height: 1.08; margin-top: 16px; font-weight: 700; }
    .shot { width: 860px; height: 540px; border-radius: 18px; overflow: hidden; box-shadow: 0 40px 90px rgba(0,0,0,0.45); }
    .shot img, .photo img { width: 100%; height: 100%; object-fit: cover; object-position: top; display: block; }
    .photo { width: 620px; height: 780px; border-radius: 10px; overflow: hidden; box-shadow: 0 40px 90px rgba(0,0,0,0.35); }
    .grid { display: grid; grid-template-columns: repeat(7, 230px); gap: 14px; }
    .grid div { height: 150px; border-radius: 10px; overflow: hidden; }
    .grid img { width: 100%; height: 100%; object-fit: cover; object-position: top; display: block; }
    .num { font-family: "Newsreader"; font-weight: 500; font-size: 330px; line-height: 1; white-space: nowrap; font-variant-numeric: tabular-nums; }
    .num small { font-size: 0.3em; }
    .bars { display: flex; align-items: flex-end; gap: 40px; height: 440px; }
    .bar { width: 200px; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; }
    .bar i { display: block; width: 120px; border-radius: 8px 8px 0 0; background: currentColor; }
    .bar span { font-family: "JetBrains Mono"; font-weight: 700; font-size: 34px; margin-bottom: 10px; }
    .bar em { font-style: normal; font-family: "JetBrains Mono"; font-size: 28px; margin-top: 12px; color: #f2eee5; }
'''

def verb_block(sid, i, verb, ground, layout, proof, label, t0):
    bg, ink, acc = C[ground]
    W = {"left": "left:110px;top:120px;font-size:300px", "right": "right:110px;top:120px;font-size:300px", "top": "left:110px;top:110px;font-size:270px",
         "grid": "left:110px;top:90px;font-size:260px", "num": "left:110px;top:110px;font-size:300px"}[layout]
    if layout == "grid":
        proof = '<div class="grid">' + "".join(f'<div><img src="assets/img/{g}.jpg" alt=""></div>' for g in GRID) + "</div>"
    P = {"left": "left:110px;top:470px", "right": "right:110px;top:420px", "top": "left:110px;top:470px", "grid": "left:110px;top:400px", "num": "left:100px;top:420px"}[layout]
    if layout in ("right",) and "photo" in proof: P = "left:150px;top:200px"
    if layout == "left" and "photo" in proof: P = "right:150px;top:200px"
    if layout == "left" and "shot" in proof: P = "right:110px;top:420px"
    if layout == "right" and "shot" in proof: P = "left:110px;top:420px"
    L = "left:116px;bottom:70px" if layout != "right" else "right:116px;bottom:70px"
    if "photo" in proof: L = ("right:116px" if layout == "left" else "left:116px") + ";bottom:90px"
    if "photo" in proof:  # word beside the photo, never over it
        W = ("left:820px" if layout == "right" else "left:110px") + ";top:330px;font-size:190px"
        P = ("left:110px" if layout == "right" else "right:110px") + ";top:150px"
        L = ("left:826px" if layout == "right" else "left:116px") + ";top:560px"
    dur = b(4)
    return (f'<div id="{sid}-v{i}" class="v clip" data-start="{t0}" data-duration="{dur}" data-track-index="0">'
            f'<div class="field" style="background:{bg}"></div>'
            f'<div class="proof" id="{sid}-p{i}" style="{P};color:{acc}">{proof}</div>'
            f'<div class="word" id="{sid}-w{i}" style="{W};color:{ink}">{verb}</div>'
            f'<div class="lab" id="{sid}-l{i}" style="{L};color:{acc}">{label}</div></div>')

def verb_scene(sid, verbs, slot_beats):
    blocks, tw = [], []
    for i, v in enumerate(verbs):
        t0 = b(4 * i)
        blocks.append(verb_block(sid, i, *v, t0))
        tw.append(f'''tl.fromTo("#{sid}-w{i}", {{ scale: 1.14, filter: "blur(10px)", transformOrigin: "0% 50%" }}, {{ scale: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }}, {t0});
      tl.fromTo("#{sid}-p{i}", {{ y: 260, opacity: 0, filter: "blur(14px)" }}, {{ y: 0, opacity: 1, filter: "blur(0px)", duration: 0.38, ease: "expo.out" }}, {t0 + b(1)});
      tl.fromTo("#{sid}-l{i}", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out" }}, {t0 + b(2)});''')
        if "cnt" in v[3]:
            tw.append(f'''{{ const c = {{ v: 0 }}, el = document.querySelector("#{sid}-p{i} .cnt"); tl.fromTo(c, {{ v: 0 }}, {{ v: 150.4, duration: {b(2)}, ease: "power3.out", onUpdate: () => (el.textContent = c.v.toFixed(1)) }}, {t0 + b(1)}); }}''')
        if "grid" in (v[3] if v[3] != "GRID" else "grid"):
            tw.append(f'tl.fromTo("#{sid}-p{i} .grid div", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(1.6)", stagger: 0.035 }}, {t0 + b(1)});')
        if "bars" in v[3]:
            tw.append(f'tl.fromTo("#{sid}-p{i} .bars i", {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.45, ease: "expo.out", stagger: 0.06 }}, {t0 + b(1)});')
    dur = b(slot_beats)
    return f'''<template>
  <style>
    {FONTS}
    {CSS}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
    {chr(10).join("    " + x for x in blocks)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + x for x in tw)}
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
'''

open("compositions/software.html", "w").write(verb_scene("software", SW, 20))
open("compositions/engineering.html", "w").write(verb_scene("engineering", EN, 20))
print("scenes written; slots", b(8), b(28), b(30), b(50), b(52))

# ---- hook, the bridge into the drop, and the end card
HOOK = [("BUILDS", "dark"), ("CODE.", "lime"), ("BUILDS", "paper"), ("CONCRETE.", "clay")]
hb, ht = [], []
for i, (w, g) in enumerate(HOOK):
    bg, ink, acc = C[g]
    t0 = b(2 * i)
    hb.append(f'<div id="hook-c{i}" class="v clip" data-start="{t0}" data-duration="{b(2)}" data-track-index="0"><div class="field" style="background:{bg}"></div>'
              f'<div class="word" id="hook-w{i}" style="left:0;width:1920px;text-align:center;top:330px;font-size:{380 if len(w) < 8 else 330}px;color:{ink}">{w}</div></div>')
    ht.append(f'tl.fromTo("#hook-w{i}", {{ scale: {1.0 if i == 0 else 1.18}, filter: "blur({0 if i == 0 else 12}px)" }}, {{ scale: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }}, {t0});')
open("compositions/hook.html", "w").write(f'''<template>
  <style>
    {FONTS}
    {CSS}
  </style>
  <div id="root" data-composition-id="hook" data-width="1920" data-height="1080">
    {chr(10).join("    " + x for x in hb)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + x for x in ht)}
      window.__timelines["hook"] = tl;
    }})();
  </script>
</template>
''')

# the bridge: the word rolls like a slot machine from code to concrete, into the drop
ROLL = ["CODE", "REACT", "NODE", "STEEL", "SOIL", "CONCRETE"]
open("compositions/bridge.html", "w").write(f'''<template>
  <style>
    {FONTS}
    {CSS}
    #bridge-win {{ position: absolute; left: 0; width: 1920px; top: 380px; height: 300px; overflow: hidden; }}
    #bridge-reel {{ position: absolute; left: 0; width: 1920px; top: 0; }}
    #bridge-reel div {{ height: 300px; text-align: center; font-weight: 800; font-size: 280px; line-height: 300px; letter-spacing: -0.05em; color: #eceae4; }}
    #bridge-reel div:last-child {{ color: #a9471f; }}
    #bridge-and {{ position: absolute; left: 0; width: 1920px; top: 250px; text-align: center; font-family: "JetBrains Mono"; font-weight: 600; font-size: 44px; color: #c8f169; }}
  </style>
  <div id="root" data-composition-id="bridge" data-width="1920" data-height="1080">
    <div id="bridge-stage" class="v clip" data-start="0" data-duration="{b(2)}" data-track-index="0">
      <div class="field" style="background:#0d0f12"></div>
      <div id="bridge-and">and off the screen:</div>
      <div id="bridge-win"><div id="bridge-reel">{"".join(f"<div>{w}</div>" for w in ROLL)}</div></div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#bridge-and", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12 }}, 0);
      tl.fromTo("#bridge-reel", {{ y: 0 }}, {{ y: -{300 * (len(ROLL) - 1)}, duration: {b(2) - 0.12}, ease: "power2.inOut" }}, 0);
      window.__timelines["bridge"] = tl;
    }})();
  </script>
</template>
''')

NAME = "John Godwin Oamien"
spans = "".join("<span>&nbsp;</span>" if c == " " else f"<span>{c}</span>" for c in NAME)
open("compositions/endcard.html", "w").write(f'''<template>
  <style>
    {FONTS}
    #root {{ position: absolute; inset: 0; overflow: hidden; font-family: "Schibsted Grotesk"; }}
    #end-dark {{ position: absolute; left: 0; top: 0; width: 960px; height: 1080px; background: #0d0f12; }}
    #end-paper {{ position: absolute; left: 960px; top: 0; width: 960px; height: 1080px; background: #f2eee5; }}
    .end-both {{ position: absolute; left: 0; width: 1920px; top: 300px; text-align: center; font-weight: 800; font-size: 400px; letter-spacing: -0.05em; line-height: 1; }}
    #end-bd {{ color: #c8f169; clip-path: inset(0 960px 0 0); }}
    #end-bl {{ color: #a9471f; clip-path: inset(0 0 0 960px); }}
    .end-name {{ position: absolute; left: 0; top: 380px; width: 1920px; text-align: center; font-weight: 800; font-size: 150px; letter-spacing: -0.04em; white-space: nowrap; }}
    .end-name span {{ display: inline-block; }}
    #end-dn {{ color: #eceae4; clip-path: inset(0 960px 0 0); }}
    #end-ln {{ color: #13272e; clip-path: inset(0 0 0 960px); }}
    #end-sw {{ position: absolute; left: 600px; top: 590px; font-family: "JetBrains Mono"; font-weight: 600; font-size: 36px; color: #c8f169; }}
    #end-en {{ position: absolute; left: 1100px; top: 582px; font-family: "Newsreader"; font-style: italic; font-weight: 500; font-size: 44px; color: #a9471f; }}
    #end-url {{ position: absolute; left: 960px; top: 730px; transform: translateX(-50%); font-family: "JetBrains Mono"; font-weight: 700; font-size: 36px; color: #0d0f12; background: #c8f169; border-radius: 999px; padding: 14px 34px; white-space: nowrap; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1920" data-height="1080">
    <div id="end-stage" class="clip" data-start="0" data-duration="{30 - b(50):.3f}" data-track-index="0" style="position:absolute;inset:0">
      <div id="end-dark"></div><div id="end-paper"></div>
      <div id="end-bd" class="end-both" data-layout-allow-overlap data-layout-allow-occlusion>BOTH.</div><div id="end-bl" class="end-both" data-layout-allow-overlap data-layout-allow-occlusion>BOTH.</div>
      <div id="end-dn" class="end-name" data-layout-allow-occlusion data-layout-allow-overlap>{spans}</div>
      <div id="end-ln" class="end-name" data-layout-allow-occlusion data-layout-allow-overlap>{spans}</div>
      <div id="end-sw">/software</div><div id="end-en">/engineering</div>
      <div id="end-url">godwins-portfolio.vercel.app</div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo(".end-both", {{ scale: 1.2, filter: "blur(12px)" }}, {{ scale: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }}, 0);
      tl.to(".end-both", {{ opacity: 0, filter: "blur(14px)", duration: 0.15, ease: "power3.in" }}, {b(2) - 0.15});
      const sp = gsap.utils.toArray("#end-dn span, #end-ln span");
      sp.forEach((s, i) => tl.fromTo(s, {{ opacity: 0, y: 60, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }}, {b(2)} + (i % {len(NAME)}) * 0.025));
      tl.fromTo(["#end-sw", "#end-en"], {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15, stagger: 0.06 }}, {b(4)});
      tl.fromTo("#end-url", {{ clipPath: "inset(0 100% 0 0 round 999px)" }}, {{ clipPath: "inset(0 0% 0 0 round 999px)", duration: 0.4, ease: "power3.inOut" }}, {b(5)});
      window.__timelines["endcard"] = tl;
    }})();
  </script>
</template>
''')
hosts = [("hook", 0, b(8)), ("software", b(8), b(28)), ("bridge", b(28), b(30)), ("engineering", b(30), b(50)), ("endcard", b(50), 30)]
idx = "\n      ".join(f'<div id="{h}" data-composition-id="{h}" data-composition-src="compositions/{h}.html" data-start="{s:.4f}" data-duration="{e - s:.4f}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>' for h, s, e in hosts)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #0d0f12; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
    </style>
  </head>
  <body>
    <!-- Film C: "Verbs on the beat". 30 s, music only; every cut on the bed's beat grid. Generated by gen_scenes.py. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="30" data-width="1920" data-height="1080" data-motion-blur="on">
      {idx}
      <!--AUDIO-->
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
''')
