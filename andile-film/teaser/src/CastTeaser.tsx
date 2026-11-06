import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing } from 'remotion';
import T from './teaser.json';

type Member = (typeof T.cast)[number] & { villain?: boolean };
const ORANGE = '#E2563C';
const FONT = "'DejaVu Sans', 'Liberation Sans', sans-serif";
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const rand = (seed: number) => { const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

const SpeedLines: React.FC<{ cx: number; cy: number; t: number; color?: string; seed: number; n?: number }> = ({ cx, cy, t, color = '#fff', seed, n = 46 }) => {
  const { width, height } = useVideoConfig();
  const R = Math.hypot(width, height);
  return (
    <svg width={width} height={height} style={{ position: 'absolute', inset: 0, opacity: t }}>
      {Array.from({ length: n }).map((_, i) => {
        const a = (i / n) * Math.PI * 2 + rand(seed + i) * 0.12;
        const r0 = R * (0.18 + 0.12 * rand(seed * 3 + i)) * (1.4 - t * 0.4);
        const w = 2 + rand(seed + i * 7) * 9;
        return <line key={i} x1={cx + Math.cos(a) * r0} y1={cy + Math.sin(a) * r0} x2={cx + Math.cos(a) * R} y2={cy + Math.sin(a) * R}
          stroke={color} strokeWidth={w} strokeLinecap="round" opacity={0.35 + 0.5 * rand(seed + i * 13)} />;
      })}
    </svg>
  );
};

const Panel: React.FC<{ src: string; x: number; y: number; w: number; h: number; skew?: number; zoom: number; pos?: string; rot?: number; border?: string }> =
  ({ src, x, y, w, h, skew = 0.07, zoom, pos = 'top center', rot = 0, border = '#fff' }) => {
    const poly = `polygon(${skew * 100}% 0, 100% 0, ${100 - skew * 100}% 100%, 0 100%)`;
    return (
      <div style={{ position: 'absolute', left: x, top: y, width: w, height: h, transform: `rotate(${rot}deg)`, filter: 'drop-shadow(14px 16px 0 rgba(0,0,0,0.75))' }}>
        <div style={{ position: 'absolute', inset: 0, background: '#0d0a12', clipPath: poly }} />
        <div style={{ position: 'absolute', inset: 6, background: border, clipPath: poly }} />
        <div style={{ position: 'absolute', inset: 13, clipPath: poly, overflow: 'hidden', background: '#8f8fa0' }}>
          <Img src={src} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: pos, transform: `scale(${zoom})`, transformOrigin: '50% 30%' }} />
        </div>
      </div>
    );
  };

const Grain: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)' }} />
      <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0, opacity: 0.09, mixBlendMode: 'overlay' }}>
        <filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 30} /></filter>
        <rect width="100%" height="100%" filter="url(#g)" />
      </svg>
    </AbsoluteFill>
  );
};

const CharacterBeat: React.FC<{ c: Member; i: number }> = ({ c, i }) => {
  const f = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const V = height > width;
  const B = T.beat;
  const enter = spring({ frame: f, fps, config: { damping: 16, stiffness: 170, mass: 0.7 } });
  const headIn = spring({ frame: f - 6, fps, config: { damping: 11, stiffness: 190 } });
  const cardIn = spring({ frame: f - 9, fps, config: { damping: 15, stiffness: 160 } });
  const exit = interpolate(f, [B - 7, B], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const shiftX = -exit * width * 0.7;
  const blur = exit * 18;
  const zoom = interpolate(f, [0, B], [1.04, 1.13]);
  const flash = interpolate(f, [0, 4], [0.85, 0], clamp);
  const speed = interpolate(f, [0, 16], [1, 0], clamp);
  const shake = c.villain ? interpolate(f, [0, 10], [14, 0], clamp) * Math.sin(f * 2.7) : 0;
  const stripe = (f * 7) % 90;

  // layout
  const L = V
    ? { bx: 70, by: 130, bw: 640, bh: 1260, hx: 650, hy: 230, hw: 380, hh: 450, nx: 70, ny: 1450, name: 118, giant: 300, cx: 400, cy: 700 }
    : { bx: 150, by: 60, bw: 470, bh: 960, hx: 620, hy: 120, hw: 330, hh: 400, nx: 860, ny: 600, name: 128, giant: 360, cx: 380, cy: 520 };

  const nameSize = Math.min(L.name, Math.floor((V ? 900 : 960) / (c.name.length * 0.74)));
  return (
    <AbsoluteFill style={{ background: c.dark, overflow: 'hidden', fontFamily: FONT }}>
      <AbsoluteFill style={{ background: `repeating-linear-gradient(120deg, ${c.dark} 0px, ${c.dark} 45px, ${c.accent}22 45px, ${c.accent}22 90px)`, transform: `translateX(${stripe}px)`, width: width + 200, left: -100 }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at ${(L.cx / width) * 100}% ${(L.cy / height) * 100}%, ${c.accent}66 0%, transparent 55%)` }} />
      <div style={{ position: 'absolute', left: 0, top: V ? 1180 : 240, whiteSpace: 'nowrap', fontSize: L.giant, fontWeight: 900, letterSpacing: '0.05em', color: 'transparent',
        WebkitTextStroke: `3px ${c.accent}55`, transform: `translateX(${width * 0.9 - f * 22}px)` }}>{c.name} {c.name}</div>
      <SpeedLines cx={L.cx} cy={L.cy} t={speed} seed={i * 50 + 3} color={c.villain ? '#ff3b3b' : '#ffffff'} />

      <div style={{ position: 'absolute', inset: 0, transform: `translateX(${shiftX + shake}px)`, filter: blur > 0.5 ? `blur(${blur}px)` : undefined }}>
        <div style={{ transform: `translateX(${(1 - enter) * width * 0.6}px)` }}>
          <Panel src={staticFile(`${c.file}_body.png`)} x={L.bx} y={L.by} w={L.bw} h={L.bh} zoom={zoom} />
        </div>
        <div style={{ position: 'absolute', inset: 0, transform: `scale(${0.6 + 0.4 * headIn})`, transformOrigin: `${L.hx + L.hw / 2}px ${L.hy + L.hh / 2}px`, opacity: Math.min(1, headIn * 1.5) }}>
          <Panel src={staticFile(`${c.file}_head.png`)} x={L.hx} y={L.hy} w={L.hw} h={L.hh} skew={0.05} zoom={1.02 + 0.06 * (f / B)} pos="center 30%" rot={V ? 5 : -4} border={c.accent} />
        </div>
        <div style={{ position: 'absolute', left: L.nx, top: L.ny, transform: `translateX(${(1 - cardIn) * 700}px)`, opacity: Math.min(1, cardIn * 2) }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 18, marginBottom: 14 }}>
            <span style={{ fontSize: 30, fontWeight: 800, color: c.accent, letterSpacing: '0.2em' }}>{c.id}</span>
            <span style={{ fontSize: 24, fontWeight: 800, color: c.villain ? '#fff' : '#0d0a12', background: c.villain ? '#d62828' : '#f4f1ec', padding: '6px 16px', letterSpacing: '0.18em', transform: 'skewX(-12deg)' }}>{c.side}</span>
          </div>
          <div style={{ position: 'relative', display: 'inline-block', padding: '10px 46px 14px 30px', transform: 'skewX(-9deg)' }}>
            <div style={{ position: 'absolute', inset: 0, background: ORANGE, boxShadow: '12px 12px 0 #0d0a12' }} />
            <div style={{ position: 'relative', fontSize: nameSize, fontWeight: 900, color: '#fff', letterSpacing: '0.04em', lineHeight: 1, transform: 'skewX(9deg)', whiteSpace: 'nowrap' }}>{c.name}</div>
          </div>
          <div style={{ marginTop: 26, fontSize: 34, fontWeight: 800, color: '#f4f1ec', letterSpacing: '0.18em', textShadow: '0 3px 0 #000' }}>{c.role}</div>
          <div style={{ marginTop: 14, display: 'inline-block', fontSize: 24, fontWeight: 700, color: '#0d0a12', background: c.accent, padding: '6px 14px', letterSpacing: '0.24em' }}>{c.origin}</div>
        </div>
      </div>
      <AbsoluteFill style={{ background: c.villain ? '#ff2a2a' : '#ffffff', opacity: flash * (c.villain ? 0.7 : 1) }} />
    </AbsoluteFill>
  );
};

const Intro: React.FC = () => {
  const f = useCurrentFrame();
  const { fps, height, width } = useVideoConfig();
  const V = height > width;
  const k = interpolate(f, [2, 14], [0, 1], clamp);
  const slam = spring({ frame: f - 18, fps, config: { damping: 9, stiffness: 220 } });
  const shake = interpolate(f, [18, 30], [12, 0], clamp) * Math.sin(f * 3.1);
  const flash = interpolate(f, [18, 23], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ background: '#07050c', fontFamily: FONT, alignItems: 'center', justifyContent: 'center' }}>
      {f >= 18 && <SpeedLines cx={width / 2} cy={height / 2} t={interpolate(f, [18, 40], [1, 0.25], clamp)} seed={7} color="#E2563C" n={60} />}
      <div style={{ position: 'absolute', top: V ? '38%' : '30%', fontSize: V ? 34 : 30, fontWeight: 800, letterSpacing: `${0.2 + 0.3 * k}em`, color: '#f4f1ec', opacity: k }}>DURBAN · KWAZULU-NATAL</div>
      <div style={{ transform: `translateX(${shake}px) scale(${1.6 - 0.6 * slam})`, opacity: f >= 18 ? 1 : 0, textAlign: 'center' }}>
        <div style={{ fontSize: V ? 120 : 150, fontWeight: 900, color: '#fff', letterSpacing: '0.08em', lineHeight: 1, textShadow: '10px 10px 0 #E2563C' }}>MEET THE</div>
        <div style={{ fontSize: V ? 200 : 230, fontWeight: 900, color: '#E2563C', letterSpacing: '0.1em', lineHeight: 1.05, textShadow: '10px 10px 0 #0d0a12' }}>CAST</div>
      </div>
      <AbsoluteFill style={{ background: '#fff', opacity: flash }} />
    </AbsoluteFill>
  );
};

const Outro: React.FC = () => {
  const f = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const V = height > width;
  const cols = V ? 2 : 5, rows = V ? 5 : 2;
  const cw = width / cols, ch = height / rows;
  const logo = spring({ frame: f - 46, fps, config: { damping: 12, stiffness: 120 } });
  const dim = interpolate(f, [40, 56], [0, 0.72], clamp);
  const fade = interpolate(f, [T.outro - 16, T.outro - 1], [0, 1], clamp);
  const flash = interpolate(f, [46, 52], [0.9, 0], clamp);
  return (
    <AbsoluteFill style={{ background: '#07050c', fontFamily: FONT }}>
      {T.cast.map((c, i) => {
        const s = spring({ frame: f - i * 2.5, fps, config: { damping: 13, stiffness: 200 } });
        const col = i % cols, row = Math.floor(i / cols);
        return (
          <div key={c.id} style={{ position: 'absolute', left: col * cw, top: row * ch, width: cw, height: ch, overflow: 'hidden',
            transform: `scale(${0.4 + 0.6 * s})`, opacity: Math.min(1, s * 1.4), borderRight: '6px solid #07050c', borderBottom: '6px solid #07050c' }}>
            <Img src={staticFile(`${c.file}_head.png`)} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center 25%', transform: `scale(${1.05 + 0.05 * (f / T.outro)})` }} />
            <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 10, background: c.accent }} />
          </div>
        );
      })}
      <AbsoluteFill style={{ background: '#07050c', opacity: dim }} />
      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', opacity: Math.min(1, logo * 1.3) }}>
        <div style={{ textAlign: 'center', transform: `scale(${1.25 - 0.25 * logo})` }}>
          <div style={{ fontSize: V ? 150 : 230, fontWeight: 900, color: '#fff', letterSpacing: `${(V ? 0.45 : 0.9) - (V ? 0.3 : 0.5) * logo}em`, paddingLeft: `${(V ? 0.45 : 0.9) - (V ? 0.3 : 0.5) * logo}em`, lineHeight: 1,
            textShadow: '0 0 40px rgba(255,80,160,0.55), 10px 10px 0 #E2563C' }}>ANDILE</div>
          <div style={{ height: 8, background: '#E2563C', width: `${logo * 70}%`, margin: '34px auto' }} />
          <div style={{ fontSize: V ? 30 : 38, fontWeight: 800, color: '#E2563C', letterSpacing: V ? '0.14em' : '0.3em' }}>SEASON 1 · EPISODE 1 — HEMINGWAY'S</div>
          <div style={{ marginTop: 30, fontSize: V ? 30 : 30, fontWeight: 700, color: '#f4f1ec', letterSpacing: '0.5em', opacity: interpolate(f, [70, 85], [0, 1], clamp) }}>COMING SOON</div>
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ background: '#fff', opacity: flash }} />
      <AbsoluteFill style={{ background: '#000', opacity: fade }} />
    </AbsoluteFill>
  );
};

export const CastTeaser: React.FC = () => {
  const { height, width } = useVideoConfig();
  const V = height > width;
  const outroStart = T.intro + T.cast.length * T.beat;
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      <Sequence durationInFrames={T.intro}><Intro /></Sequence>
      {T.cast.map((c, i) => (
        <Sequence key={c.id} from={T.intro + i * T.beat} durationInFrames={T.beat}><CharacterBeat c={c as Member} i={i} /></Sequence>
      ))}
      <Sequence from={outroStart} durationInFrames={T.outro}><Outro /></Sequence>
      <Grain />
      {!V && <><div style={{ position: 'absolute', left: 0, right: 0, top: 0, height: 54, background: '#000' }} /><div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 54, background: '#000' }} /></>}
      <Audio src={staticFile('teaser_audio.wav')} />
    </AbsoluteFill>
  );
};
