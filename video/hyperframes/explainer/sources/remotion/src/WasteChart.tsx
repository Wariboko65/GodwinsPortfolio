// The hostel solid waste study as one moving chart. Numbers: src/data/engineering.ts (study.daily, study.composition, study.share).
// 0-5 s: six days of weighing rise and the total lands; 5-9 s: the same bars regroup into what the waste was made of;
// 9-13 s: one line lands and the frame holds still.
import React from "react";
import { AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing } from "remotion";

const DAILY = [[23.895, 8.95], [27.75, 4.054], [18.14, 2.03], [17.15, 3.826], [20.34, 2.68], [18.37, 3.26]];
const COMP = [["Plastics", 80.46], ["Food", 11.15], ["Cardboard", 3.2], ["Paper", 2.49], ["Residual", 1.36]] as const; // female hostel, % by weight
const C = { deep: "#0f3a44", paper: "#f2eee5", peach: "#f0a46f", mute: "#b9c9cc" };
const FONTS = `
@font-face { font-family: Newsreader; src: url(${staticFile("newsreader.woff2")}) format("woff2"); font-weight: 200 800; }
@font-face { font-family: Mono; src: url(${staticFile("jbmono.woff2")}) format("woff2"); font-weight: 100 800; }
@font-face { font-family: Schibsted; src: url(${staticFile("schibsted.woff2")}) format("woff2"); font-weight: 400 900; }`;

const fadeBlur = (f: number, at: number, dur = 6) => {
  const p = interpolate(f, [at, at + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return { opacity: p, filter: `blur(${(1 - p) * 8}px)` };
};

export const WasteChart: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const BASE = 820, MAXH = 440, X0 = 1000;
  // phase 2: daily bars hand over to the composition bars (a regroup, not a cut)
  const regroup = spring({ frame: f - 150, fps, config: { damping: 18, stiffness: 90 } });
  const total = 150.4 * interpolate(f, [58, 92], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const numIn = spring({ frame: f - 56, fps, config: { damping: 14, stiffness: 160 } });

  return (
    <AbsoluteFill style={{ background: C.deep, color: C.paper }}>
      <style>{FONTS}</style>
      <div style={{ position: "absolute", left: 160, top: 238, fontFamily: "Mono", fontWeight: 600, fontSize: 26, letterSpacing: "0.08em", color: C.mute, ...fadeBlur(f, 4) }}>
        B.ENG. RESEARCH · RIVERS STATE UNIVERSITY
      </div>
      <div style={{ position: "absolute", left: 156, top: 280, fontFamily: "Newsreader", fontWeight: 500, fontSize: 66, ...fadeBlur(f, 8) }}>
        Hostel solid waste study
      </div>
      <div style={{ position: "absolute", left: 150, top: 380, fontFamily: "Newsreader", fontWeight: 500, fontSize: 230, lineHeight: 1, color: C.peach,
        opacity: Math.min(1, numIn * 1.4), transform: `scale(${1.5 - 0.5 * numIn})`, transformOrigin: "0% 60%", fontVariantNumeric: "tabular-nums" }}>
        {total.toFixed(1)}<span style={{ fontSize: "0.32em" }}> kg</span>
      </div>
      <div style={{ position: "absolute", left: 162, top: 640, fontFamily: "Mono", fontSize: 28, color: C.mute, ...fadeBlur(f, 80) }}>
        weighed · 6 days · 2 hostels · 9 categories
      </div>
      {/* phase 1: the six days */}
      {DAILY.map(([fe, ma], i) => {
        const g = spring({ frame: f - 18 - i * 4, fps, config: { damping: 15, stiffness: 120 } });
        const x = X0 + i * 128;
        const out = 1 - regroup;
        return (
          <React.Fragment key={i}>
            <div style={{ position: "absolute", left: x, top: BASE - (fe / 27.75) * MAXH * g * out, width: 50, height: (fe / 27.75) * MAXH * g * out, background: C.peach, borderRadius: "6px 6px 0 0" }} />
            <div style={{ position: "absolute", left: x + 54, top: BASE - (ma / 27.75) * MAXH * g * out, width: 50, height: (ma / 27.75) * MAXH * g * out, background: C.mute, borderRadius: "6px 6px 0 0" }} />
            <div style={{ position: "absolute", left: x - 6, top: BASE + 16, width: 120, textAlign: "center", fontFamily: "Mono", fontSize: 26, color: C.mute, opacity: g * out }}>Day {i + 1}</div>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: X0, top: BASE + 70, fontFamily: "Mono", fontSize: 24, color: C.mute, opacity: interpolate(f, [30, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) * (1 - regroup) }}>
        <span style={{ color: C.peach }}>■</span> female hostel &nbsp; ■ male hostel · kg per day
      </div>
      {/* phase 2: what it was made of (female hostel, % by weight) */}
      {COMP.map(([label, pct], i) => {
        const g = spring({ frame: f - 158 - i * 5, fps, config: { damping: 13, stiffness: 110 } });
        const x = X0 + i * 150;
        const h = (pct / 80.46) * MAXH * g;
        return (
          <React.Fragment key={label}>
            <div style={{ position: "absolute", left: x, top: BASE - h, width: 104, height: h, background: i === 0 ? C.peach : C.mute, borderRadius: "6px 6px 0 0" }} />
            <div style={{ position: "absolute", left: x - 20, top: BASE - h - 46, width: 144, textAlign: "center", fontFamily: "Mono", fontWeight: 700, fontSize: 28, color: i === 0 ? C.peach : C.paper, opacity: g }}>{pct}%</div>
            <div style={{ position: "absolute", left: x - 20, top: BASE + 16, width: 144, textAlign: "center", fontFamily: "Mono", fontSize: 26, color: C.mute, opacity: g }}>{label}</div>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: X0, top: BASE + 70, fontFamily: "Mono", fontSize: 24, color: C.mute, ...fadeBlur(f, 175) }}>
        female hostel · % by weight · 5 of 9 categories
      </div>
      {/* phase 3: one line lands, then the frame rests */}
      <div style={{ position: "absolute", left: 160, top: 712, fontFamily: "Newsreader", fontStyle: "italic", fontSize: 46, ...fadeBlur(f, 270, 7) }}>
        <b style={{ fontStyle: "normal", color: C.peach, fontWeight: 600 }}>83.5%</b> of it came from the female hostel
      </div>
      <div style={{ position: "absolute", inset: 0, background: C.deep, opacity: interpolate(f, [0, 8], [1, 0], { extrapolateRight: "clamp" }) }} />
    </AbsoluteFill>
  );
};
