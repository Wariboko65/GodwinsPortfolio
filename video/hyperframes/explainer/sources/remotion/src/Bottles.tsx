// 14 ancient fragrances, 4 recreated (perfume stickman film). Card starts at film 25.0 s:
// "14" is said at 25.18, "four" at 28.82, "museum in Rome" at 29.68.
import React from "react";
import { AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
const CARD = "#fbf6ea", INK = "#2b2118", AMBER = "#e8a33d", GLASS = "#c9d7dd";
const FONTS = `@font-face { font-family: Mono; src: url(${staticFile("jbmono.woff2")}) format("woff2"); font-weight: 100 800; }
@font-face { font-family: Schibsted; src: url(${staticFile("schibsted.woff2")}) format("woff2"); font-weight: 400 900; }`;
const RECREATED = [2, 5, 8, 12];
const Bottle: React.FC<{ fill: number; dim: number }> = ({ fill, dim }) => (
  <svg viewBox="0 0 60 100" width={96} height={160} style={{ opacity: 1 - 0.65 * dim }}>
    <rect x="22" y="4" width="16" height="12" rx="3" fill={INK} />
    <path d="M24 16 L24 30 L8 46 L8 94 L52 94 L52 46 L36 30 L36 16 Z" fill={GLASS} fillOpacity={0.35} stroke={INK} strokeWidth="4" strokeLinejoin="round" />
    <clipPath id="b"><path d="M24 16 L24 30 L8 46 L8 94 L52 94 L52 46 L36 30 L36 16 Z" /></clipPath>
    <rect x="0" y={94 - 60 * fill} width="60" height={60 * fill} fill={AMBER} clipPath="url(#b)" />
  </svg>
);
export const Bottles: React.FC = () => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const four = spring({ frame: f - Math.round(3.82 * fps), fps, config: { damping: 16, stiffness: 120 } });
  const n = Math.round(interpolate(f, [5, 30], [0, 14], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const lab = (at: number) => interpolate(f, [at, at + 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: CARD, color: INK }}>
      <style>{FONTS}</style>
      <div style={{ position: "absolute", left: 80, top: 70, fontFamily: "Schibsted", fontWeight: 900, fontSize: 200, lineHeight: 1, letterSpacing: "-0.05em", fontVariantNumeric: "tabular-nums" }}>{n}</div>
      <div style={{ position: "absolute", left: 90, top: 280, fontFamily: "Mono", fontWeight: 700, fontSize: 40, opacity: lab(30) }}>ANCIENT FRAGRANCES</div>
      <div style={{ position: "absolute", left: 90, top: 400, display: "grid", gridTemplateColumns: "repeat(7, 128px)", rowGap: 40 }}>
        {Array.from({ length: 14 }, (_, i) => {
          const s = spring({ frame: f - 4 - i * 2, fps, config: { damping: 12, stiffness: 180 } });
          const hit = RECREATED.includes(i);
          return <div key={i} style={{ transform: `translateY(${(1 - s) * 60}px) scale(${0.6 + 0.4 * s})`, opacity: Math.min(1, s * 1.5) }}>
            <Bottle fill={hit ? four * 0.8 : 0} dim={hit ? 0 : four} /></div>;
        })}
      </div>
      <div style={{ position: "absolute", left: 90, top: 870, fontFamily: "Schibsted", fontWeight: 800, fontSize: 56, opacity: lab(Math.round(4.68 * fps)) }}>
        <span style={{ color: AMBER }}>4</span> recreated · museum in Rome
      </div>
    </AbsoluteFill>
  );
};
