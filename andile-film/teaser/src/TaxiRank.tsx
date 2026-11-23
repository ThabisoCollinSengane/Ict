// Stickman style test: Andile & Lee at a Durban taxi rank (isiZulu dialogue, English subs).
import React from 'react';
import { AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame, Easing, random } from 'remotion';
import { Stickman, Outfit, Pose, STAND, gait, mix, talk } from './Stickman';
import D from './taxirank.json';

const W = 1920, H = 1080, G = 940; // G = ground line for the front characters
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const ez = Easing.bezier(0.45, 0, 0.25, 1);
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ramp = (fr: number, a: number, b: number) => interpolate(fr, [a, b], [0, 1], { easing: ez, ...clamp });
const speaking = (who: string, fr: number) => D.lines.some((l) => l.who === who && fr >= l.from && fr < l.to);
const blinkAt = (fr: number, seed: number) => ((fr + seed) % 97 < 4 ? 1 : 0);

const ANDILE: Outfit = { skin: '#8a5a3a', hair: 'fade', top: '#2f5fb8', shirt: '#e9e7ee', tie: '#1b2346', pants: '#26262b', shoe: '#1f3a78', hood: '#9a9aa6' };
const LEE: Outfit = { skin: '#9a6444', hair: 'bun', top: '#1d2a52', shirt: '#ffffff', tie: '#c8202f', pants: '#1d2a52', shoe: '#111', glasses: true, headphones: true, lanyard: true, heels: true };
const GAATJIE: Outfit = { skin: '#6e4630', hair: 'bucket', top: '#3b8f4a', top2: '#3b8f4a', shirt: '#f4d23c', pants: '#3b5a86', shoe: '#eee', vest: '#ff7a1a' };

// ---------- characters ----------
const andile = (fr: number): { p: Pose; o: number } => {
  let p = STAND(1070, G, -1), o = 1;
  if (fr < 110) {
    const t = interpolate(fr, [18, 110], [0, 1], clamp);
    p = gait({ ...p, x: lerp(2080, 1070, t) }, fr * 0.33);
    if (fr > 100) p = mix(p, STAND(1070, G, -1), ramp(fr, 100, 112));
  } else if (fr < 160) {
    p = mix(p, { head: 20, aF: 55, eF: 85, phone: 1, brow: 0 }, ramp(fr, 110, 122));
    p.y += Math.sin(fr * 0.15) * 1.5;
  } else if (fr < 176) { // startled by "Andile!" and turns round
    const j = Math.sin(Math.PI * interpolate(fr, [160, 172], [0, 1], clamp));
    p = { ...p, y: p.y - j * 34, brow: 3, aF: 120 * j, eF: 30, aB: -110 * j, head: -8, f: fr < 167 ? -1 : 1, sx: Math.max(0.25, Math.abs(Math.cos(Math.PI * interpolate(fr, [162, 172], [0, 1], clamp)))) };
  } else if (fr < 240) {
    p = { ...p, f: 1, lean: -4, brow: 1.5, head: -4 + Math.sin(fr * 0.07) * 2, aF: 10, eF: 25, aB: -12, eB: 20 };
  } else if (fr < 304) { // explaining with both hands
    const g = Math.sin(fr * 0.22);
    p = { ...p, f: 1, lean: 4, brow: 2, head: 4 * g, aF: 38 + 12 * g, eF: 55, aB: 30 - 10 * g, eB: 50, y: p.y + Math.abs(g) * 3 };
  } else if (fr < 360) { // caught out: hand behind head
    p = mix({ ...p, f: 1 }, { head: 12, lean: 6, aF: 165, eF: 115, brow: 2.5, aB: -6 }, ramp(fr, 304, 318));
  } else if (fr < 386) { // HOOT jump
    const j = Math.sin(Math.PI * interpolate(fr, [361, 376], [0, 1], clamp));
    p = { ...p, f: 1, y: p.y - j * 60, aF: 160 * j + 10, eF: 10, aB: -160 * j, eB: 10, brow: 3, tF: 25 * j, kF: 50 * j, tB: -15 * j, kB: 40 * j };
  } else if (fr < 424) { // runs for the taxi
    const t = interpolate(fr, [388, 422], [0, 1], { easing: Easing.in(Easing.quad), ...clamp });
    p = gait({ ...p, f: -1, x: lerp(1070, 830, t), lean: 10 }, fr * 0.6, 1.6);
  } else { // hops in through the sliding door
    const t = interpolate(fr, [424, 434], [0, 1], clamp);
    p = { ...gait({ ...p, f: -1, x: lerp(820, 700, t) }, fr * 0.6, 1.4), y: p.y - Math.sin(Math.PI * t) * 50 - t * 30, sx: 1 - 0.3 * t, sy: 1 - 0.3 * t };
    o = 1 - t;
  }
  p.mouth = speaking('ANDILE', fr) ? talk(fr, 1.3) : fr >= 361 && fr < 372 ? 0.9 : 0;
  p.blink = blinkAt(fr, 11);
  return { p, o };
};

const lee = (fr: number): Pose => {
  let p = STAND(1450, G, -1);
  if (fr < 176) {
    const t = interpolate(fr, [118, 172], [0, 1], { easing: Easing.out(Easing.quad), ...clamp });
    p = gait({ ...p, x: lerp(2200, 1450, t) }, fr * 0.36, 0.8);
    if (fr >= 146) p = { ...p, aF: 150, eF: 25 + 15 * Math.sin(fr * 0.6) }; // waving
    if (fr > 166) p = mix(p, STAND(1450, G, -1), ramp(fr, 166, 176));
  } else if (fr < 240) { // arms crossed
    p = mix(p, { lean: -4, head: -6 + Math.sin(fr * 0.1) * 3, aF: 72, eF: 115, aB: 62, eB: 118, brow: -1.5 }, ramp(fr, 176, 186));
  } else if (fr < 304) { // hand on hip, tapping foot
    p = { ...p, lean: -2, head: 4, aF: 22, eF: -70, aB: -10, eB: 10, brow: -1, tF: 8, kF: 4 + 10 * Math.max(0, Math.sin(fr * 0.55)) };
  } else if (fr < 360) { // pushes glasses up
    p = mix({ ...p, lean: -2, aF: 22, eF: -70 }, { aF: 150, eF: 140, head: -6, brow: -2 }, ramp(fr, 304, 318));
  } else if (fr < 410) {
    const j = Math.sin(Math.PI * interpolate(fr, [362, 375], [0, 1], clamp));
    p = { ...p, y: p.y - j * 36, brow: 3, aF: 100 * j + 20, eF: 30, aB: -90 * j, eB: 20, head: -6 };
    if (fr > 388) p = { ...p, head: 14, lean: 6, aF: 20, eF: 20, brow: 1 }; // watches him run
  } else { // Hhayi bo! arms up
    const g = Math.sin(fr * 0.4);
    p = mix({ ...p, head: 14, lean: 6 }, { aF: 165, eF: 25 + 8 * g, aB: -165, eB: 25, head: -12, lean: -6, brow: 3 }, ramp(fr, 410, 418));
  }
  p.mouth = speaking('LEE', fr) ? talk(fr, 4.1) : 0;
  p.blink = blinkAt(fr, 47);
  return p;
};

const gaatjie = (fr: number): { p: Pose; o: number } => {
  let p = STAND(830, G - 14, 1), o = 1;
  if (fr < 80) { // calling passengers: finger up (Umlazi hand sign), bouncing
    const b = Math.sin(fr * 0.5);
    p = { ...p, aF: 168, eF: 8 + 6 * b, aB: -30 + 15 * b, eB: 40, y: p.y - Math.abs(b) * 6, head: -8, brow: 1, lean: -3 };
  } else if (fr < 360) { // leaning on the taxi, bored
    p = mix(p, { lean: -10, x: 815, aF: 70, eF: 115, aB: 60, eB: 118, head: 6 + 4 * Math.sin(fr * 0.05), tF: 18, kF: 10, tB: -2 }, ramp(fr, 80, 96));
    if (fr > 240 && fr < 300) p.head = -10; // eavesdrops
  } else if (fr < 430) { // impatient: points at Andile
    const b = Math.sin(fr * 0.7);
    p = { ...p, lean: 12, aF: 92 + 6 * b, eF: 0, aB: 40, eB: 90, brow: -2.5, head: -4 };
    if (fr > 410) p = { ...p, aF: 150, eF: 40 };
  } else { // jumps in after Andile
    const t = interpolate(fr, [430, 438], [0, 1], clamp);
    p = { ...p, f: -1, x: lerp(830, 720, t), y: p.y - Math.sin(Math.PI * t) * 40, sx: 1 - 0.3 * t, sy: 1 - 0.3 * t };
    o = 1 - t;
  }
  p.mouth = speaking('GAATJIE', fr) ? Math.max(talk(fr, 2.2), 0.3) : D.whistles.some((w) => fr >= w && fr < w + 12) ? 0.55 : 0;
  p.blink = blinkAt(fr, 23);
  return { p, o };
};

// ---------- set ----------
const Sky: React.FC = () => (<>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#58b4ec" /><stop offset="0.7" stopColor="#bfe3f5" /><stop offset="1" stopColor="#ffe6b8" /></linearGradient>
    <pattern id="win" width="22" height="26" patternUnits="userSpaceOnUse"><rect width="22" height="26" fill="#9db7ca" /><rect x="5" y="6" width="11" height="13" fill="#d8e9f3" /></pattern>
  </defs>
  <rect width={W} height={H} fill="url(#sky)" />
  {[[60, 210], [190, 300], [320, 250], [470, 360], [600, 280], [760, 400], [900, 330], [1040, 260], [1900, 300], [1780, 380]].map(([x, h], i) => (
    <rect key={i} x={x} y={640 - h} width={120} height={h} fill="url(#win)" stroke="#7c95a8" strokeWidth={4} />
  ))}
  {/* Moses Mabhida stadium arch */}
  <path d="M1180 640 Q1300 470 1440 300 Q1520 230 1560 300 Q1680 470 1760 640" fill="none" stroke="#fff" strokeWidth={14} />
  <path d="M1180 640 Q1300 470 1440 300 Q1520 230 1560 300 Q1680 470 1760 640" fill="none" stroke="#9fb4c3" strokeWidth={3} />
  <ellipse cx={1470} cy={630} rx={330} ry={46} fill="#e9eef2" stroke="#9fb4c3" strokeWidth={4} />
  {/* palms */}
  {[[1130, 1], [1840, -1]].map(([x, d], i) => (
    <g key={i}>
      <path d={`M${x} 760 Q${x + 18 * d} 600 ${x - 6 * d} 470`} stroke="#7a5532" strokeWidth={16} fill="none" strokeLinecap="round" />
      {[-70, -30, 10, 50, 100, 140].map((a, j) => <path key={j} d={`M${x - 6 * d} 470 q${Math.cos((a * Math.PI) / 180) * 90} ${-30 + Math.abs(a) * 0.5} ${Math.cos((a * Math.PI) / 180) * 150} ${40 + Math.abs(a) * 0.4}`} stroke="#2f8a45" strokeWidth={14} fill="none" strokeLinecap="round" />)}
    </g>
  ))}
</>);

const Shelter: React.FC = () => (<>
  <rect x={0} y={760} width={W} height={H - 760} fill="#cfc7b6" />
  <rect x={0} y={752} width={W} height={14} fill="#9c9483" />
  {[0, 1, 2, 3, 4, 5].map((i) => <path key={i} d={`M${120 + i * 330} 1080 L${250 + i * 330} 790`} stroke="#f2c230" strokeWidth={12} />)}
  {[260, 980, 1700].map((x) => <rect key={x} x={x} y={120} width={22} height={650} fill="#2f7d4f" stroke="#1b3d27" strokeWidth={4} />)}
  <path d="M-20 70 L1940 70 L1940 150 L-20 150 Z" fill="#a9b4ba" stroke="#5f6a70" strokeWidth={5} />
  {Array.from({ length: 64 }, (_, i) => <line key={i} x1={i * 31} y1={74} x2={i * 31} y2={146} stroke="#7f8b91" strokeWidth={3} />)}
  <g transform="translate(560 160)">
    <line x1={40} y1={-12} x2={40} y2={8} stroke="#333" strokeWidth={4} /><line x1={440} y1={-12} x2={440} y2={8} stroke="#333" strokeWidth={4} />
    <rect width={480} height={96} rx={8} fill="#11603a" stroke="#fff" strokeWidth={5} />
    <text x={240} y={42} textAnchor="middle" fontFamily="DejaVu Sans, sans-serif" fontWeight={800} fontSize={32} fill="#fff">IRENKI YAMATEKISI</text>
    <text x={240} y={78} textAnchor="middle" fontFamily="DejaVu Sans, sans-serif" fontWeight={700} fontSize={24} fill="#ffd34d">BAY 7 · UMLAZI · eTHEKWINI</text>
  </g>
  {/* fruit stall */}
  <g transform="translate(1560 610)">
    <path d="M-30 0 Q130 -90 290 0 Z" fill="#e23b3b" stroke="#14110f" strokeWidth={5} />
    <path d="M50 -40 Q130 -90 210 -40 L190 0 L70 0 Z" fill="#fff" opacity={0.8} />
    <line x1={130} y1={0} x2={130} y2={140} stroke="#444" strokeWidth={6} />
    <rect x={0} y={110} width={260} height={60} fill="#b07a45" stroke="#14110f" strokeWidth={5} />
    {Array.from({ length: 9 }, (_, i) => <circle key={i} cx={22 + i * 27} cy={102} r={13} fill={i % 3 === 2 ? '#f5d53a' : '#f39021'} stroke="#14110f" strokeWidth={3} />)}
    <rect x={70} y={180} width={120} height={36} fill="#fff" stroke="#14110f" strokeWidth={3} />
    <text x={130} y={206} textAnchor="middle" fontFamily="DejaVu Sans, sans-serif" fontWeight={800} fontSize={20} fill="#c8202f">IZITHELO R10</text>
  </g>
</>);

const Taxi: React.FC<{ fr: number }> = ({ fr }) => {
  const hoot = D.hoots.some((h) => fr >= h && fr < h + 6);
  const go = fr > 438 ? (fr - 438) ** 2 * 3.2 : 0;
  const vib = Math.sin(fr * 2.1) * 1.2 + (hoot ? -5 : 0);
  return (
    <g transform={`translate(${40 - go} ${905 + vib})`}>
      <ellipse cx={360} cy={8} rx={380} ry={16} fill="rgba(0,0,0,.25)" />
      <path d="M0 -60 L0 -230 Q4 -290 80 -300 L700 -300 Q740 -298 740 -250 L740 -60 Z" fill="#f4f4f2" stroke="#14110f" strokeWidth={6} strokeLinejoin="round" />
      <path d="M0 -150 L740 -150 L740 -128 L0 -128 Z" fill="#1b6fd1" /><path d="M0 -124 L740 -124 L740 -116 L0 -116 Z" fill="#f2c230" />
      <path d="M20 -170 L20 -228 Q24 -270 90 -276 L150 -276 L150 -170 Z" fill="#26343f" stroke="#14110f" strokeWidth={5} />
      {[170, 300].map((x) => <rect key={x} x={x} y={-276} width={112} height={100} rx={6} fill="#26343f" stroke="#14110f" strokeWidth={5} />)}
      <rect x={560} y={-276} width={160} height={100} rx={6} fill="#26343f" stroke="#14110f" strokeWidth={5} />
      {/* open sliding door */}
      <rect x={430} y={-282} width={120} height={222} fill="#0e1418" stroke="#14110f" strokeWidth={5} />
      <rect x={444} y={-200} width={92} height={56} fill="#3a2e28" />
      {/* driver silhouette */}
      <circle cx={95} cy={-232} r={22} fill="#0b0f12" /><path d="M70 -200 Q95 -222 120 -200 L120 -176 L70 -176 Z" fill="#0b0f12" />
      <rect x={-10} y={-96} width={30} height={22} rx={4} fill="#ffe28a" stroke="#14110f" strokeWidth={4} />
      <rect x={724} y={-110} width={22} height={30} rx={4} fill="#e8402f" stroke="#14110f" strokeWidth={4} />
      {[140, 600].map((x) => <g key={x}><circle cx={x} cy={-50} r={56} fill="#1a1a1a" stroke="#14110f" strokeWidth={5} /><circle cx={x} cy={-50} r={26} fill="#b9bec3" stroke="#14110f" strokeWidth={4} /></g>)}
      <rect x={0} y={-72} width={740} height={14} fill="#c9cdd0" stroke="#14110f" strokeWidth={4} />
      <text x={600} y={-200} fontFamily="DejaVu Sans, sans-serif" fontWeight={800} fontSize={26} fill="#f2c230" textAnchor="middle">UMLAZI</text>
      {hoot ? <g transform="translate(-60 -160)"><text fontFamily="DejaVu Sans, sans-serif" fontWeight={900} fontSize={70} fill="#fff" stroke="#14110f" strokeWidth={6} paintOrder="stroke" transform="rotate(-12)">PHAAP!</text></g> : null}
    </g>
  );
};

const CROWD: { x: number; o: Outfit; f: 1 | -1; s: number }[] = [
  { x: 1240, f: -1, s: 0.5, o: { skin: '#7a4e34', hair: 'fade', top: '#b84a3a', shirt: '#eee', pants: '#444', shoe: '#222' } },
  { x: 1330, f: 1, s: 0.48, o: { skin: '#a8714e', hair: 'bun', top: '#d98e2b', shirt: '#fff', pants: '#2f4f6f', shoe: '#222' } },
  { x: 1960, f: -1, s: 0.52, o: { skin: '#5e3a28', hair: 'fade', top: '#4b7f3a', shirt: '#ddd', pants: '#333', shoe: '#eee' } },
  { x: 1120, f: 1, s: 0.46, o: { skin: '#c99a76', hair: 'bun', top: '#7d4fa0', shirt: '#fff', pants: '#222', shoe: '#111' } },
];

const Sub: React.FC<{ fr: number }> = ({ fr }) => {
  const l = D.lines.find((x) => fr >= x.from && fr < x.to);
  if (!l) return null;
  const o = interpolate(fr, [l.from, l.from + 4, l.to - 5, l.to], [0, 1, 1, 0], clamp);
  const c = l.who === 'LEE' ? '#ffb347' : l.who === 'ANDILE' ? '#7fc8ff' : '#9be37a';
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 44, textAlign: 'center', opacity: o, fontFamily: 'DejaVu Sans, sans-serif' }}>
      <div style={{ fontSize: 46, fontWeight: 800, color: '#fff', textShadow: '0 0 6px #000, 0 3px 0 #000, 0 0 16px #000' }}>
        <span style={{ color: c, marginRight: 14 }}>{l.who}</span>{l.zu}
      </div>
      {l.en ? <div style={{ fontSize: 30, fontWeight: 600, color: '#e6e6e6', fontStyle: 'italic', textShadow: '0 0 6px #000, 0 2px 0 #000' }}>{l.en}</div> : null}
    </div>
  );
};

export const TaxiRank: React.FC = () => {
  const fr = useCurrentFrame();
  const A = andile(fr), L = lee(fr), Gt = gaatjie(fr);
  const zoom = interpolate(fr, [150, 200, 350, 362, 380], [1, 1.12, 1.18, 1.18, 1], { easing: ez, ...clamp });
  const shake = fr >= 360 && fr < 372 ? `translate(${(random(`x${fr}`) - 0.5) * 18}px, ${(random(`y${fr}`) - 0.5) * 18}px)` : '';
  const endO = interpolate(fr, [446, 458], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ background: '#000', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `${shake} scale(${zoom})`, transformOrigin: '1230px 640px' }}>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
          <Sky />
          <Shelter />
          {CROWD.map((c, i) => {
            const p = STAND(0, 0, c.f); const b = Math.sin(fr * 0.08 + i * 1.7);
            const pose = { ...p, head: 5 * b, aF: 10 + 8 * b, mouth: Math.max(0, Math.sin(fr * 0.5 + i)) * (i % 2 ? 0.6 : 0), blink: blinkAt(fr, i * 31) };
            return <g key={i} transform={`translate(${c.x} ${770}) scale(${c.s})`} opacity={0.92}><Stickman p={{ ...pose, x: 0, y: -188 }} o={c.o} /></g>;
          })}
          <Taxi fr={fr} />
          <g opacity={Gt.o}><Stickman p={Gt.p} o={GAATJIE} /></g>
          <Stickman p={L} o={LEE} />
          <g opacity={A.o}><Stickman p={A.p} o={ANDILE} /></g>
          {fr >= 160 && fr < 172 ? <text x={1070} y={600} fontFamily="DejaVu Sans, sans-serif" fontWeight={900} fontSize={80} fill="#fff" stroke="#14110f" strokeWidth={6} paintOrder="stroke">!</text> : null}
          {fr >= 361 && fr < 380 ? <><text x={1000} y={560} fontFamily="DejaVu Sans, sans-serif" fontWeight={900} fontSize={80} fill="#fff" stroke="#14110f" strokeWidth={6} paintOrder="stroke">!!</text><text x={1420} y={560} fontFamily="DejaVu Sans, sans-serif" fontWeight={900} fontSize={70} fill="#fff" stroke="#14110f" strokeWidth={6} paintOrder="stroke">!</text></> : null}
        </svg>
      </AbsoluteFill>
      <Sub fr={fr} />
      <AbsoluteFill style={{ background: 'rgba(0,0,0,.6)', opacity: endO, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
        <div style={{ fontFamily: 'DejaVu Sans, sans-serif', fontWeight: 900, fontSize: 150, color: '#fff', letterSpacing: 30 }}>ANDILE</div>
        <div style={{ fontFamily: 'DejaVu Sans Mono, monospace', fontSize: 34, color: '#ffd34d', letterSpacing: 10 }}>STICKMAN TEST · eTHEKWINI</div>
      </AbsoluteFill>
      <Audio src={staticFile('taxirank.wav')} />
    </AbsoluteFill>
  );
};
