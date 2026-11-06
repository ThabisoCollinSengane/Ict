// ANDILE — Episode 1, Scene 1 "Bad Dream": Andile's call-centre nightmare, then waking at his desk with Lee.
import React from 'react';
import { AbsoluteFill, Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame, Easing, random } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { Puppet, Rig } from './Puppet';
import S from './scene1.json';

const W = 1920, H = 1080;
const RIG: Record<string, Rig> = {
  andile_body: { neck: 0.864, pivotX: 0.5, waist: 0.5 },
  lee_body: { neck: 0.874, pivotX: 0.47, waist: 0.55 },
  andile_h1: { neck: 0.24, pivotX: 0.55, waist: -1 },
  andile_h2: { neck: 0.2, pivotX: 0.5, waist: -1 },
  lee_h1: { neck: 0.3, pivotX: 0.5, waist: -1 },
};
const art = (n: string) => staticFile(`s1/${n}.png`);
const plate = (shot: string, f: number) => staticFile(`s1/bg/${shot}/f${String(Math.max(0, f)).padStart(4, '0')}.png`);
const sin = Math.sin;
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const ez = Easing.bezier(0.45, 0, 0.2, 1);

const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThreeCanvas width={W} height={H} orthographic camera={{ position: [0, 0, 100], near: 0.1, far: 1000, zoom: 1 }} gl={{ antialias: true, alpha: true }} style={{ position: 'absolute', inset: 0 }}>
    {children}
  </ThreeCanvas>
);

const Plate: React.FC<{ src: string; scale?: number; blur?: number; filter?: string; ox?: number; oy?: number }> = ({ src, scale = 1, blur = 0, filter = '', ox = 0, oy = 0 }) => (
  <Img src={src} style={{ position: 'absolute', inset: 0, width: W, height: H, transform: `translate(${ox}px,${oy}px) scale(${scale})`, filter: `${blur ? `blur(${blur}px)` : ''} ${filter}` }} />
);

const Vignette: React.FC<{ a?: number; color?: string }> = ({ a = 0.8, color = '0,0,0' }) => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 50%, rgba(${color},0) 45%, rgba(${color},${a}) 100%)` }} />
);

const Grain: React.FC<{ o?: number }> = ({ o = 0.09 }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ opacity: o, mixBlendMode: 'overlay' }}>
      <svg width={W} height={H}>
        <filter id={`g${f % 6}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={f % 6} /><feColorMatrix type="saturate" values="0" /></filter>
        <rect width={W} height={H} filter={`url(#g${f % 6})`} />
      </svg>
    </AbsoluteFill>
  );
};

const Bars: React.FC = () => (<>
  <div style={{ position: 'absolute', left: 0, right: 0, top: 0, height: 66, background: '#000' }} />
  <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 66, background: '#000' }} />
</>);

// Subtitles: speaker tag + line, typed on, isiZulu in amber
const Sub: React.FC<{ who?: string; text: string; dur: number; robot?: boolean }> = ({ who, text, dur, robot }) => {
  const f = useCurrentFrame();
  const n = Math.floor(interpolate(f, [0, Math.min(18, dur * 0.4)], [0, text.length], clamp));
  const o = interpolate(f, [0, 4, dur - 6, dur], [0, 1, 1, 0], clamp);
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 96, textAlign: 'center', opacity: o, fontFamily: robot ? 'DejaVu Sans Mono, monospace' : 'DejaVu Sans, sans-serif', fontSize: 40, fontWeight: 700, color: robot ? '#ff5b6b' : '#fff', textShadow: '0 0 6px #000, 0 3px 0 #000, 0 0 18px rgba(0,0,0,.8)', letterSpacing: robot ? 3 : 0.5 }}>
      {who ? <span style={{ color: who === 'LEE' ? '#ffb347' : '#7fc8ff', marginRight: 14 }}>{who}</span> : null}
      {text.slice(0, n)}
    </div>
  );
};

const RedPulse: React.FC<{ rate?: number; a?: number }> = ({ rate = 0.35, a = 0.25 }) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ background: '#ff0022', mixBlendMode: 'screen', opacity: a * (0.5 + 0.5 * sin(f * rate)) ** 3 }} />;
};

const SpeedLines: React.FC<{ o: number }> = ({ o }) => {
  const f = useCurrentFrame();
  const lines = Array.from({ length: 70 }, (_, i) => {
    const a = random(`sl${i}-${Math.floor(f / 2)}`) * Math.PI * 2, r0 = 380 + random(`r${i}-${Math.floor(f / 2)}`) * 260;
    const w = 2 + random(`w${i}`) * 7;
    return <path key={i} d={`M ${960 + Math.cos(a) * r0} ${540 + Math.sin(a) * r0} L ${960 + Math.cos(a + 0.012 * w) * 1400} ${540 + Math.sin(a + 0.012 * w) * 1400} L ${960 + Math.cos(a - 0.012 * w) * 1400} ${540 + Math.sin(a - 0.012 * w) * 1400} Z`} fill="#fff" />;
  });
  return <svg width={W} height={H} style={{ position: 'absolute', opacity: o, mixBlendMode: 'overlay' }}>{lines}</svg>;
};

const shake = (f: number, amp: number) => `translate(${(random(`x${f}`) - 0.5) * amp}px, ${(random(`y${f}`) - 0.5) * amp}px)`;

// ---------- shots ----------
const N1: React.FC = () => {
  const f = useCurrentFrame();
  return (<AbsoluteFill style={{ background: '#000' }}>
    <Plate src={plate('N1', Math.min(f, 99))} filter="contrast(1.15) saturate(1.2)" />
    <RedPulse rate={0.55} a={0.18} />
    <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(20,0,4,.0) 30%, rgba(30,0,6,.75) 100%)' }} />
    <div style={{ position: 'absolute', left: 120, top: 120, fontFamily: 'DejaVu Sans Mono, monospace', color: '#ff6a7a', fontSize: 26, letterSpacing: 6, opacity: interpolate(f, [8, 20, 70, 85], [0, 1, 1, 0], clamp) }}>
      UMHLANGA · 03:12 AM<br /><span style={{ opacity: 0.6 }}>QUEUE: 999+ CALLERS WAITING</span>
    </div>
    <Sequence from={22} durationInFrames={76}><Sub robot text={S.lines.ivr} dur={76} /></Sequence>
  </AbsoluteFill>);
};

const N2: React.FC = () => {
  const f = useCurrentFrame();
  const twitch = f > 52 && f < 60 ? 0.09 * sin((f - 52) * 2.4) : 0;
  return (<AbsoluteFill style={{ background: '#000', transform: shake(f, f > 50 ? 6 : 1.5) }}>
    <Plate src={plate('N2', Math.min(f, 99))} filter="brightness(.8) contrast(1.2)" />
    <Stage>
      <Puppet src={art('andile_body')} x={560} y={120 - f * 0.4} h={1300} rig={RIG.andile_body}
        pose={{ breath: sin(f * 0.5) * 1.6, headRot: -0.04 + twitch + 0.02 * sin(f * 0.13), lean: 0.03 * sin(f * 0.07), tint: [1, 0.3, 0.38], tintAmt: 0.8, bright: 0.8, glow: [0.9, 0.05, 0.15] }} />
    </Stage>
    {/* foreground desk + monitor back in silhouette */}
    <svg width={W} height={H} style={{ position: 'absolute' }}>
      <defs><linearGradient id="dk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#2a0a10" /><stop offset="1" stopColor="#050102" /></linearGradient></defs>
      <rect x={0} y={810} width={W} height={270} fill="url(#dk)" />
      <rect x={0} y={806} width={W} height={6} fill="#ff4057" opacity={0.55} />
    </svg>
    <RedPulse rate={0.9} a={0.22} />
    <Vignette a={0.9} />
    <Sequence from={8} durationInFrames={90}><Sub robot text={S.lines.hold} dur={90} /></Sequence>
  </AbsoluteFill>);
};

const N3: React.FC = () => {
  const f = useCurrentFrame();
  const grow = interpolate(f, [0, 90], [1, 1.25], { easing: ez, ...clamp });
  const flick = random(`fl${f}`) > 0.92 ? 0.4 : 1;
  return (<AbsoluteFill style={{ background: '#000' }}>
    <Plate src={plate('N3', 0)} scale={1 + f * 0.0015} filter="brightness(.7)" />
    <AbsoluteFill style={{ transform: `scale(${grow})`, transformOrigin: '50% 40%', opacity: interpolate(f, [0, 22], [0, 1], clamp) * flick }}>
      <Stage>
        <Puppet src={art('lee_h1')} x={960 - 470} y={-60} h={1170} rig={RIG.lee_h1}
          pose={{ headRot: 0.05 * sin(f * 0.05), tint: [1, 0.35, 0.4], tintAmt: 0.75, bright: 0.9, alpha: 0.88, glow: [1, 0.1, 0.2] }} />
      </Stage>
    </AbsoluteFill>
    <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 30%, rgba(10,0,2,.95) 85%)' }} />
    <RedPulse rate={0.25} a={0.2} />
    <Sequence from={24} durationInFrames={66}><Sub who="LEE" text={S.lines.leeDream} dur={66} /></Sequence>
  </AbsoluteFill>);
};

const N4: React.FC = () => {
  const f = useCurrentFrame();
  const beat = Math.max(0, sin(f * 0.42)) ** 8;
  const amp = interpolate(f, [0, 119], [2, 22], clamp);
  return (<AbsoluteFill style={{ background: '#000', transform: shake(f, amp) }}>
    <Plate src={plate('N4', Math.min(f, 119))} filter="contrast(1.25)" />
    <SpeedLines o={interpolate(f, [20, 70], [0, 0.85], clamp)} />
    <AbsoluteFill style={{ transform: `scale(${1 + 0.02 * beat + f * 0.0012})`, transformOrigin: '50% 30%' }}>
      <Stage>
        <Puppet src={art('andile_h1')} x={960 - 440} y={-150} h={1270} rig={RIG.andile_h1}
          pose={{ headRot: 0.03 * sin(f * 0.21), headY: -0.004 * beat, tint: [1, 0.55, 0.55], tintAmt: 0.45, bright: 0.95 + 0.15 * beat, glow: [1, 0.15, 0.2] }} />
      </Stage>
    </AbsoluteFill>
    <AbsoluteFill style={{ background: '#ff0030', mixBlendMode: 'multiply', opacity: 0.35 + 0.25 * beat }} />
    <Vignette a={0.95} color="20,0,4" />
    <Sequence from={30} durationInFrames={85}><Sub who="ANDILE" text={S.lines.andileDream} dur={85} /></Sequence>
  </AbsoluteFill>);
};

const N5: React.FC = () => {
  const f = useCurrentFrame();
  const strobe = f % 6 < 3;
  const split = interpolate(f, [0, 60], [4, 40], clamp);
  const wake = interpolate(f, [24, 30], [0, 1], clamp);
  const white = interpolate(f, [62, 70, 78, 90], [0, 1, 1, 0], clamp);
  return (<AbsoluteFill style={{ background: '#000', transform: shake(f, 30) }}>
    <AbsoluteFill style={{ mixBlendMode: 'screen' }}>
      <Plate src={plate('N4', 119)} ox={-split} filter="sepia(1) hue-rotate(-50deg) saturate(6)" />
    </AbsoluteFill>
    <AbsoluteFill style={{ mixBlendMode: 'screen', opacity: 0.8 }}>
      <Plate src={plate('N1', 99 - (f % 20))} ox={split} scale={1.1} filter="hue-rotate(160deg) saturate(3)" />
    </AbsoluteFill>
    {Array.from({ length: 9 }, (_, i) => {
      const y = random(`gy${i}-${Math.floor(f / 3)}`) * H, h = 8 + random(`gh${i}-${Math.floor(f / 3)}`) * 60;
      return <div key={i} style={{ position: 'absolute', left: 0, right: 0, top: y, height: h, background: i % 2 ? '#ff0040' : '#00e5ff', opacity: 0.35, transform: `translateX(${(random(`gx${i}${f}`) - 0.5) * 300}px)`, mixBlendMode: 'screen' }} />;
    })}
    <AbsoluteFill style={{ background: strobe ? 'rgba(255,0,40,.25)' : 'transparent' }} />
    <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', opacity: wake, transform: `scale(${1 + f * 0.01})` }}>
      <div style={{ fontFamily: 'DejaVu Sans, sans-serif', fontWeight: 900, fontSize: 260, color: '#fff', letterSpacing: 20, textShadow: `${split / 2}px 0 #ff0040, ${-split / 2}px 0 #00e5ff` }}>VUKA!</div>
      <div style={{ fontFamily: 'DejaVu Sans Mono, monospace', fontSize: 34, color: '#ffd0d6', letterSpacing: 18 }}>WAKE UP</div>
    </div>
    <AbsoluteFill style={{ background: '#fff', opacity: white }} />
    <AbsoluteFill style={{ background: '#000', opacity: interpolate(f, [80, 90], [0, 1], clamp) }} />
  </AbsoluteFill>);
};

const Eyelids: React.FC<{ open: number }> = ({ open }) => {
  const g = (1 - open) * 560;
  return (<svg width={W} height={H} style={{ position: 'absolute' }}>
    <path d={`M0 0 H${W} V${g - 80} Q${W / 2} ${g + 120} 0 ${g - 80} Z`} fill="#000" />
    <path d={`M0 ${H} H${W} V${H - g + 80} Q${W / 2} ${H - g - 120} 0 ${H - g + 80} Z`} fill="#000" />
  </svg>);
};

const W1: React.FC = () => {
  const f = useCurrentFrame();
  const open = interpolate(f, [0, 14, 20, 24, 44], [0, 0.45, 0.2, 0.25, 1], clamp);
  const blur = interpolate(f, [0, 50], [22, 0], { easing: ez, ...clamp });
  return (<AbsoluteFill style={{ background: '#000' }}>
    <AbsoluteFill style={{ filter: `blur(${blur}px)` }}>
      <Plate src={plate('W1', 0)} filter="brightness(1.05)" />
      <Stage>
        <Puppet src={art('lee_body')} x={1040} y={30} h={1750} rig={RIG.lee_body}
          pose={{ lean: -0.12 + 0.01 * sin(f * 0.1), headRot: 0.18 + 0.03 * sin(f * 0.08), breath: sin(f * 0.25) }} />
      </Stage>
    </AbsoluteFill>
    <AbsoluteFill style={{ background: 'linear-gradient(200deg, rgba(255,240,210,.35), rgba(255,255,255,0) 50%)', mixBlendMode: 'screen' }} />
    <Eyelids open={open} />
    <Sequence from={40} durationInFrames={40}><Sub who="LEE" text={S.lines.leeWake} dur={40} /></Sequence>
  </AbsoluteFill>);
};

const Papers: React.FC<{ t: number }> = ({ t }) => (<svg width={W} height={H} style={{ position: 'absolute' }}>
  {Array.from({ length: 7 }, (_, i) => {
    const vx = (random(`pv${i}`) - 0.3) * 18, vy = -14 - random(`pu${i}`) * 10, r = (random(`pr${i}`) - 0.5) * 30;
    const x = 520 + i * 40 + vx * t, y = 790 + vy * t + 0.45 * t * t;
    return t > 0 && y < 1200 ? <rect key={i} x={x} y={y} width={90} height={118} fill="#f4f1ea" stroke="#333" strokeWidth={2} transform={`rotate(${r * t * 0.6} ${x + 45} ${y + 59})`} /> : null;
  })}
</svg>);

const Desk: React.FC<{ y?: number }> = ({ y = 800 }) => (<svg width={W} height={H} style={{ position: 'absolute' }}>
  <defs><linearGradient id="dw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#d9d3c7" /><stop offset="0.08" stopColor="#bdb5a6" /><stop offset="1" stopColor="#7d7567" /></linearGradient></defs>
  <rect x={0} y={y} width={W} height={H - y} fill="url(#dw)" />
  <rect x={0} y={y} width={W} height={5} fill="#fff" opacity={0.8} />
  <rect x={0} y={y + 5} width={W} height={4} fill="#1c1a17" opacity={0.6} />
  <rect x={300} y={y - 24} width={330} height={26} rx={6} fill="#23262b" stroke="#0d0e10" strokeWidth={3} />
  <rect x={1060} y={y - 18} width={120} height={20} rx={8} fill="#1d1f22" />
</svg>);

const W2: React.FC = () => {
  const f = useCurrentFrame();
  const jolt = interpolate(f, [8, 13, 30], [0, 1, 0.35], { easing: Easing.out(Easing.cubic), ...clamp });
  const look = interpolate(f, [26, 40], [0, 1], { easing: ez, ...clamp });
  return (<AbsoluteFill style={{ background: '#000', transform: f > 8 && f < 18 ? shake(f, 10) : undefined }}>
    <Plate src={plate('W2', 0)} />
    <Stage>
      <Puppet src={art('lee_body')} x={1330} y={130} h={1060} rig={RIG.lee_body}
        pose={{ breath: sin(f * 0.2), headRot: 0.04 * sin(f * 0.06) - 0.06, lean: -0.02 }} />
      <Puppet src={art('andile_body')} x={330} y={190 - jolt * 110} h={1500} rig={RIG.andile_body}
        pose={{ breath: sin(f * 0.35) * (1 + jolt), headRot: interpolate(f, [0, 8], [0.35, 0.35], clamp) * (1 - jolt) * (1 - look) - 0.12 * look - 0.06 * jolt, lean: 0.12 * (1 - jolt) * (1 - look) - 0.04 * jolt, squash: -0.02 * jolt }} />
    </Stage>
    <Desk y={800} />
    <Papers t={Math.max(0, f - 10) * 0.9} />
    {f > 9 && f < 22 ? <div style={{ position: 'absolute', left: 470, top: 90, fontFamily: 'DejaVu Sans, sans-serif', fontWeight: 900, fontSize: 90, color: '#fff', WebkitTextStroke: '4px #000', transform: `rotate(-8deg) scale(${interpolate(f, [9, 14], [0.6, 1.1], clamp)})` }}>!!</div> : null}
    <Sequence from={44} durationInFrames={76}><Sub who="LEE" text={S.lines.leeLine4} dur={76} /></Sequence>
  </AbsoluteFill>);
};

const W3: React.FC = () => {
  const f = useCurrentFrame();
  const sigh = interpolate(f, [10, 40, 70], [0, 1, 0.3], clamp);
  const blink = f > 62 && f < 66;
  return (<AbsoluteFill style={{ background: '#000' }}>
    <Plate src={plate('W3', 0)} blur={7} scale={1.06} />
    <Stage>
      <Puppet src={art('andile_h2')} x={300} y={-60 + sigh * 18} h={1150} rig={RIG.andile_h2}
        pose={{ headRot: -0.05 * sigh + 0.015 * sin(f * 0.1), headY: -0.01 * sigh, bright: blink ? 0.92 : 1 }} />
    </Stage>
    <div style={{ position: 'absolute', right: 150, top: 180, width: 470, padding: '22px 30px', background: 'rgba(8,20,32,.82)', border: '2px solid #2fd0ff', borderRadius: 10, fontFamily: 'DejaVu Sans Mono, monospace', color: '#bfefff', fontSize: 26, boxShadow: '0 0 40px rgba(47,208,255,.35)', transform: `translateY(${interpolate(f, [0, 12], [40, 0], { easing: ez, ...clamp })}px)`, opacity: interpolate(f, [0, 10], [0, 1], clamp) }}>
      <div style={{ color: '#fff', fontWeight: 700, letterSpacing: 4 }}>SHAKA CONNECT · CX</div>
      <div style={{ marginTop: 14 }}><span style={{ color: f % 20 < 10 ? '#ff4d5e' : '#5a1a22' }}>●</span> LINE 4 — ON HOLD</div>
      <div style={{ marginTop: 6, fontSize: 44, color: '#ffcf5a' }}>10:{String(3 + Math.floor(f / 30)).padStart(2, '0')}</div>
    </div>
    <Vignette a={0.45} />
    <Sequence from={14} durationInFrames={92}><Sub who="ANDILE" text={S.lines.andileWake} dur={92} /></Sequence>
  </AbsoluteFill>);
};

const Title: React.FC = () => {
  const f = useCurrentFrame();
  const o = interpolate(f, [6, 22], [0, 1], clamp);
  return (<AbsoluteFill style={{ background: '#000' }}>
    <Plate src={plate('W2', 0)} filter="brightness(.45) saturate(.7)" scale={1 + f * 0.0008} />
    <Stage>
      <Puppet src={art('lee_body')} x={1330} y={130} h={1060} rig={RIG.lee_body} pose={{ bright: 0.5, breath: sin(f * 0.2), headRot: -0.06 }} />
      <Puppet src={art('andile_body')} x={330} y={160} h={1500} rig={RIG.andile_body} pose={{ bright: 0.5, breath: sin(f * 0.35), headRot: -0.1 }} />
    </Stage>
    <Desk y={800} />
    <AbsoluteFill style={{ background: 'rgba(0,0,0,.45)' }} />
    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: o }}>
      <div style={{ fontFamily: 'DejaVu Sans, sans-serif', fontWeight: 900, fontSize: 200, letterSpacing: interpolate(f, [6, 60], [70, 34], { easing: ez, ...clamp }), color: '#fff', textShadow: '0 0 30px rgba(255,60,80,.6)' }}>ANDILE</div>
      <div style={{ marginTop: 10, height: 4, width: interpolate(f, [14, 40], [0, 760], { easing: ez, ...clamp }), background: '#e2203a' }} />
      <div style={{ marginTop: 22, fontFamily: 'DejaVu Sans Mono, monospace', fontSize: 38, letterSpacing: 12, color: '#ffd8a8' }}>EPISODE 1 · BAD DREAM</div>
    </div>
    <AbsoluteFill style={{ background: '#000', opacity: interpolate(f, [72, 90], [0, 1], clamp) }} />
  </AbsoluteFill>);
};

const SHOTS: Record<string, React.FC> = { N1, N2, N3, N4, N5, W1, W2, W3, T: Title };

export const Scene1: React.FC = () => (
  <AbsoluteFill style={{ background: '#000' }}>
    {S.shots.map((s) => {
      const C = SHOTS[s.id];
      return <Sequence key={s.id} from={s.from} durationInFrames={s.to - s.from}><C /></Sequence>;
    })}
    <Grain o={0.08} />
    <Bars />
    <Audio src={staticFile('s1/scene1.wav')} />
  </AbsoluteFill>
);
