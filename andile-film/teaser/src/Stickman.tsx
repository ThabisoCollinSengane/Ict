// Procedural stickman rig with clothes. Everything is drawn in a local frame facing right with the hip at (0,0);
// `f` mirrors it. Angles in degrees: limbs measured from straight down, positive = forward.
import React from 'react';

export type Pose = {
  x: number; y: number; f: 1 | -1; lean: number; head: number;
  aB: number; eB: number; aF: number; eF: number; // back / front arm: shoulder angle, elbow flex
  tB: number; kB: number; tF: number; kF: number; // back / front leg: thigh angle, knee bend
  mouth: number; brow: number; blink: number; phone?: number; sx?: number; sy?: number;
};
export type Outfit = {
  skin: string; hair: 'fade' | 'bun' | 'bucket'; top: string; top2?: string; shirt: string; tie?: string; pants: string; shoe: string;
  glasses?: boolean; hood?: string; headphones?: boolean; lanyard?: boolean; vest?: string; heels?: boolean;
};

const T = 150, U = 74, Fa = 70, Th = 96, Sh = 94, R = 38, INK = '#14110f';
const rad = (d: number) => (d * Math.PI) / 180;
const dn = (p: [number, number], len: number, a: number): [number, number] => [p[0] + Math.sin(rad(a)) * len, p[1] + Math.cos(rad(a)) * len];
const shade = (hex: string, k: number) => {
  const n = parseInt(hex.slice(1), 16), c = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => Math.round(v * k));
  return `rgb(${c.join(',')})`;
};
const line = (a: [number, number], b: [number, number], c: string, w: number, k?: string) => (
  <g key={k}>
    <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={INK} strokeWidth={w + 8} strokeLinecap="round" />
    <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={c} strokeWidth={w} strokeLinecap="round" />
  </g>
);

export const Stickman: React.FC<{ p: Pose; o: Outfit }> = ({ p, o }) => {
  const l = p.lean;
  const N: [number, number] = [Math.sin(rad(l)) * T, -Math.cos(rad(l)) * T];
  const S: [number, number] = [N[0] - Math.sin(rad(l)) * 14, N[1] + Math.cos(rad(l)) * 14];
  const hA = l + p.head;
  const H: [number, number] = [N[0] + Math.sin(rad(hA)) * (R + 10), N[1] - Math.cos(rad(hA)) * (R + 10)];
  const arm = (a: number, e: number) => { const E = dn(S, U, a); return [E, dn(E, Fa, a + e)] as const; };
  const leg = (t: number, k: number) => { const K = dn([0, 0], Th, t); return [K, dn(K, Sh, t - k)] as const; };
  const [EB, WB] = arm(p.aB, p.eB), [EF, WF] = arm(p.aF, p.eF);
  const [KB, FB] = leg(p.tB, p.kB), [KF, FF] = leg(p.tF, p.kF);
  const sleeve = o.top, sleeveB = shade(o.top, 0.78), pantsB = shade(o.pants, 0.78);
  const shoe = (F: [number, number], c: string, k: string) => o.heels
    ? <g key={k}><path d={`M${F[0] - 10} ${F[1] - 4} L${F[0] + 24} ${F[1] + 4} L${F[0] + 24} ${F[1] + 10} L${F[0] - 12} ${F[1] + 10} Z`} fill={c} stroke={INK} strokeWidth={4} strokeLinejoin="round" /><line x1={F[0] - 8} y1={F[1] + 8} x2={F[0] - 8} y2={F[1] + 20} stroke={INK} strokeWidth={5} /></g>
    : <g key={k}><path d={`M${F[0] - 16} ${F[1] - 8} Q${F[0] + 4} ${F[1] - 16} ${F[0] + 30} ${F[1] + 2} L${F[0] + 30} ${F[1] + 12} L${F[0] - 16} ${F[1] + 12} Z`} fill={c} stroke={INK} strokeWidth={4} strokeLinejoin="round" /><rect x={F[0] - 16} y={F[1] + 6} width={46} height={6} fill="#fff" stroke={INK} strokeWidth={2} /></g>;
  const hand = (W: [number, number], k: string) => <circle key={k} cx={W[0]} cy={W[1]} r={11} fill={o.skin} stroke={INK} strokeWidth={4} />;
  const eyeY = -4, blink = p.blink > 0.5;
  const mouthH = 3 + p.mouth * 16;
  return (
    <g transform={`translate(${p.x} ${p.y}) scale(${p.f * (p.sx ?? 1)} ${p.sy ?? 1})`}>
      {/* back leg + arm */}
      {line([0, 0], KB, pantsB, 24, 'lb1')}{line(KB, FB, pantsB, 22, 'lb2')}{shoe(FB, shade(o.shoe, 0.8), 'sb')}
      {line(S, EB, sleeveB, 22, 'ab1')}{line(EB, WB, sleeveB, 20, 'ab2')}{hand(WB, 'hb')}
      {/* hood behind the head */}
      {o.hood ? <path d={`M${N[0] - 34} ${N[1] + 6} Q${N[0] - 44} ${N[1] - 40} ${N[0] - 6} ${N[1] - 30} L${N[0] + 22} ${N[1] + 6} Z`} fill={o.hood} stroke={INK} strokeWidth={4} /> : null}
      {/* torso */}
      <g transform={`rotate(${l})`}>
        <path d={`M-30 ${-T + 8} Q0 ${-T - 4} 30 ${-T + 8} L26 6 Q0 14 -24 6 Z`} fill={o.shirt} stroke={INK} strokeWidth={5} strokeLinejoin="round" />
        {o.tie ? <path d={`M-2 ${-T + 10} L6 ${-T + 10} L9 ${-T + 82} L2 ${-T + 94} L-5 ${-T + 82} Z`} fill={o.tie} stroke={INK} strokeWidth={3} /> : null}
        {o.vest ? <path d={`M-28 ${-T + 14} L28 ${-T + 14} L25 4 L-23 4 Z`} fill={o.vest} stroke={INK} strokeWidth={4} /> : null}
        {o.vest ? <><rect x={-25} y={-T + 64} width={50} height={9} fill="#e8e8e8" stroke={INK} strokeWidth={2} /><rect x={-24} y={-T + 96} width={48} height={9} fill="#e8e8e8" stroke={INK} strokeWidth={2} /></> : null}
        {/* open jacket: two panels */}
        <path d={`M-31 ${-T + 8} L-6 ${-T + 6} L-10 ${-T + 70} L-6 10 L-27 8 Z`} fill={o.top} stroke={INK} strokeWidth={5} strokeLinejoin="round" />
        <path d={`M31 ${-T + 8} L8 ${-T + 6} L14 ${-T + 70} L10 10 L27 8 Z`} fill={o.top2 ?? o.top} stroke={INK} strokeWidth={5} strokeLinejoin="round" />
        {o.lanyard ? <><path d={`M-12 ${-T + 8} L0 ${-T + 60} L12 ${-T + 8}`} fill="none" stroke="#c8202f" strokeWidth={4} /><rect x={-9} y={-T + 58} width={18} height={24} rx={2} fill="#fff" stroke={INK} strokeWidth={3} /></> : null}
        {o.headphones ? <path d={`M-24 ${-T + 2} Q0 ${-T + 26} 24 ${-T + 2}`} fill="none" stroke={INK} strokeWidth={9} strokeLinecap="round" /> : null}
        <rect x={-26} y={-2} width={52} height={10} fill={shade(o.pants, 0.6)} stroke={INK} strokeWidth={3} />
      </g>
      {/* front leg */}
      {line([0, 0], KF, o.pants, 24, 'lf1')}{line(KF, FF, o.pants, 22, 'lf2')}{shoe(FF, o.shoe, 'sf')}
      {/* head */}
      <g transform={`translate(${H[0]} ${H[1]}) rotate(${hA})`}>
        <rect x={-9} y={R - 6} width={18} height={16} fill={o.skin} stroke={INK} strokeWidth={4} />
        <circle r={R} fill={o.skin} stroke={INK} strokeWidth={5} />
        <ellipse cx={-R + 6} cy={4} rx={8} ry={11} fill={o.skin} stroke={INK} strokeWidth={4} />
        {o.hair === 'fade' ? <><path d={`M${-R - 1} 2 Q${-R - 4} ${-R - 6} 4 ${-R - 6} Q${R + 2} ${-R - 2} ${R - 4} -14 L${R - 14} -18 Q4 -30 -18 -14 L-26 4 Z`} fill="#18110d" stroke={INK} strokeWidth={4} /><path d="M-14 -24 L10 -27" stroke="#d6a274" strokeWidth={2} /></> : null}
        {o.hair === 'bun' ? <><circle cx={-R + 4} cy={-R + 6} r={17} fill="#1a1210" stroke={INK} strokeWidth={4} /><path d={`M${-R - 1} 6 Q${-R - 2} ${-R - 4} 4 ${-R - 5} Q${R + 2} ${-R} ${R - 2} -10 Q6 -26 -20 -10 L-28 10 Z`} fill="#1a1210" stroke={INK} strokeWidth={4} /></> : null}
        {o.hair === 'bucket' ? <><path d={`M${-R - 14} -12 L${R + 14} -12 L${R} -24 Q0 ${-R - 22} ${-R} -24 Z`} fill="#e8b23a" stroke={INK} strokeWidth={4} strokeLinejoin="round" /></> : null}
        {/* face (front of head = +x) */}
        <g transform="translate(14 0)">
          {blink ? <path d={`M2 ${eyeY} L14 ${eyeY}`} stroke={INK} strokeWidth={4} strokeLinecap="round" /> : <ellipse cx={9} cy={eyeY} rx={5} ry={7} fill={INK} />}
          <path d={`M0 ${eyeY - 14 - p.brow * 3} L18 ${eyeY - 16 + p.brow * 4}`} stroke={INK} strokeWidth={5} strokeLinecap="round" />
          {o.glasses ? <><rect x={-2} y={eyeY - 10} width={22} height={18} rx={3} fill="rgba(255,255,255,.18)" stroke={INK} strokeWidth={4} /><line x1={-2} y1={eyeY - 4} x2={-20} y2={eyeY - 6} stroke={INK} strokeWidth={3} /></> : null}
          <ellipse cx={8} cy={20} rx={7} ry={mouthH / 2} fill="#5a1a1a" stroke={INK} strokeWidth={3} />
        </g>
      </g>
      {/* front arm on top */}
      {line(S, EF, sleeve, 22, 'af1')}{line(EF, WF, sleeve, 20, 'af2')}
      {p.phone ? <rect x={WF[0] - 2} y={WF[1] - 30} width={22} height={38} rx={4} fill="#111" stroke="#666" strokeWidth={2} opacity={p.phone} transform={`rotate(-15 ${WF[0]} ${WF[1]})`} /> : null}
      {hand(WF, 'hf')}
    </g>
  );
};

// ---------- pose helpers ----------
export const STAND = (x: number, ground: number, f: 1 | -1): Pose => ({
  x, y: ground - 188, f, lean: 2, head: 0, aB: -8, eB: 10, aF: 8, eF: 10, tB: -6, kB: 2, tF: 6, kF: 2, mouth: 0, brow: 0, blink: 0,
});
// walk / run cycle overlay; ph in radians, k = stride (1 walk, 1.6 run)
export const gait = (p: Pose, ph: number, k = 1): Pose => {
  const s = Math.sin(ph), c = Math.cos(ph);
  return {
    ...p,
    y: p.y - Math.abs(c) * 7 * k, lean: p.lean + 4 * k,
    tF: 26 * k * s, kF: 8 + 34 * k * Math.max(0, Math.cos(ph - 0.9)),
    tB: -26 * k * s, kB: 8 + 34 * k * Math.max(0, Math.cos(ph + Math.PI - 0.9)),
    aF: -24 * k * s, eF: 20 + 25 * k, aB: 24 * k * s, eB: 20 + 25 * k,
  };
};
export const mix = (a: Pose, b: Partial<Pose>, t: number): Pose => {
  const o: any = { ...a };
  for (const k of Object.keys(b) as (keyof Pose)[]) if (typeof b[k] === 'number' && typeof a[k] === 'number') o[k] = (a[k] as number) + ((b[k] as number) - (a[k] as number)) * t;
  return o;
};
// talking mouth from frame: syllable-like flaps with pauses
export const talk = (fr: number, seed: number) => {
  const syl = Math.abs(Math.sin(fr * 0.85 + seed)) * (0.6 + 0.4 * Math.sin(fr * 0.31 + seed * 2));
  const pause = Math.sin(fr * 0.12 + seed) > 0.75 ? 0.15 : 1;
  return Math.max(0, syl * pause);
};
