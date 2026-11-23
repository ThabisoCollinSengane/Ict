import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { toon, cel, outline, rng, lerp, EASE } from './toon.js';

const OL = 0.011;
const cache = {};
const G = {
  sph: (seg = 20) => (cache['s' + seg] ||= new THREE.SphereGeometry(1, seg, Math.round(seg * 0.7))),
  cap: (r, l) => (cache[`c${r}_${l}`] ||= new THREE.CapsuleGeometry(r, l, 6, 14)),
  cyl: (a, b, h, s = 14) => (cache[`y${a}_${b}_${h}_${s}`] ||= new THREE.CylinderGeometry(a, b, h, s)),
  rbox: (w, h, d, r) => (cache[`b${w}_${h}_${d}_${r}`] ||= new RoundedBoxGeometry(w, h, d, 3, r)),
  tor: (R, r) => (cache[`t${R}_${r}`] ||= new THREE.TorusGeometry(R, r, 8, 28)),
};
const f3 = (v) => +v.toFixed(3);

function mk(parent, geo, mat, p, s = [1, 1, 1], ol = OL, rot) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(p[0], p[1], p[2]);
  m.scale.set(s[0], s[1], s[2]);
  if (rot) m.rotation.set(rot[0], rot[1], rot[2]);
  parent.add(m);
  if (ol) outline(m, ol / ((s[0] + s[1] + s[2]) / 3));
  return m;
}

export const JOINTS = ['hips', 'spine', 'chest', 'neck', 'head', 'shoulderL', 'elbowL', 'handL', 'shoulderR', 'elbowR', 'handR',
  'hipL', 'kneeL', 'ankleL', 'hipR', 'kneeR', 'ankleR'];

export function makeCharacter(spec, scene) {
  const w = spec.build ?? 1, hw = spec.hipW ?? w;
  const M = {
    skin: cel(spec.skin), skinD: cel(new THREE.Color(spec.skin).multiplyScalar(0.72)), hair: cel(spec.hair, { gloss: 0.35 }),
    top: cel(spec.top), under: cel(spec.under ?? spec.top), sleeve: cel(spec.sleeve ?? spec.top),
    fore: cel(spec.fore ?? spec.sleeve ?? spec.top), pants: cel(spec.pants), shoes: cel(spec.shoes),
    sole: cel(spec.sole ?? 0xe8e4dc), eye: cel(0x24140c), iris: cel(spec.iris ?? 0x5a3418), sclera: cel(0xf6f2ee),
    white: new THREE.MeshBasicMaterial({ color: new THREE.Color(0.95, 0.95, 0.95) }),
    lip: cel(spec.lip ?? 0x5a2a24), dark: cel(0x141418), stripe: cel(0xf2f2f2),
    metal: cel(spec.metal ?? 0xdcdce6, { gloss: 0.9 }),
  };
  const root = new THREE.Group(); root.rotation.order = 'YXZ'; root.name = spec.name;
  const body = new THREE.Group(); body.scale.setScalar(spec.scale ?? 1); root.add(body);
  const J = {};
  const jt = (n, p, x, y, z) => { const g = new THREE.Group(); g.position.set(x, y, z); p.add(g); J[n] = g; return g; };

  // torso
  const hips = jt('hips', body, 0, 0.99, 0);
  mk(hips, G.sph(), M.pants, [0, -0.02, 0], [0.165 * hw, 0.12, 0.12]);
  const spine = jt('spine', hips, 0, 0.06, 0);
  mk(spine, G.sph(), M.under, [0, 0.09, 0], [0.145 * w, 0.15, 0.11]);
  const chest = jt('chest', spine, 0, 0.17, 0);
  mk(chest, G.cap(0.15, 0.16), M.top, [0, 0.1, 0], [1.22 * w, 1, 0.8]);
  if (spec.openJacket) mk(chest, G.rbox(0.14, 0.3, 0.03, 0.012), M.under, [0, 0.12, 0.112], [w, 1, 1], 0);
  if (spec.lapels) for (const s of [1, -1]) mk(chest, G.rbox(0.055, 0.2, 0.022, 0.008), M.top, [s * 0.075, 0.17, 0.118], [1, 1, 1], OL, [0.05, 0, s * -0.38]);
  if (spec.tie) mk(chest, G.rbox(0.036, 0.25, 0.014, 0.006), M.dark, [0, 0.09, 0.132], [1, 1, 1], 0);
  if (spec.hood) mk(chest, G.tor(0.105, 0.045), M.under, [0, 0.31, -0.045], [1.15 * w, 1, 1], OL, [Math.PI / 2 + 0.35, 0, 0]);
  if (spec.chain) mk(chest, G.tor(0.1, 0.011), M.metal, [0, 0.24, 0.07], [w, 1, 1], 0, [Math.PI / 2 - 0.45, 0, 0]);
  if (spec.pendant) mk(chest, G.sph(10), M.metal, [0, 0.2, 0.125], [0.016, 0.022, 0.01], 0);
  if (spec.zip) mk(chest, G.rbox(0.012, 0.32, 0.01, 0.004), M.stripe, [0, 0.1, 0.122], [1, 1, 1], 0);

  // head
  const neck = jt('neck', chest, 0, 0.3, 0);
  mk(neck, G.cyl(0.048, 0.055, 0.12), M.skin, [0, 0.03, 0], [1, 1, 1]);
  const head = jt('head', neck, 0, 0.08, 0);
  const hg = new THREE.Group(); hg.scale.setScalar(spec.headScale ?? 1); head.add(hg);
  mk(hg, G.sph(24), M.skin, [0, 0.11, 0], [0.125, 0.14, 0.13]);
  for (const s of [1, -1]) {
    mk(hg, G.sph(12), M.skin, [s * 0.122, 0.1, -0.005], [0.022, 0.035, 0.028]);
    if (!spec.glasses) {
      mk(hg, G.sph(16), M.sclera, [s * 0.047, 0.108, 0.1165], [0.03, 0.027, 0.007], 0);
      mk(hg, G.sph(14), M.iris, [s * 0.045, 0.106, 0.1222], [0.0165, 0.022, 0.005], 0);
      mk(hg, G.sph(10), M.eye, [s * 0.045, 0.105, 0.1262], [0.0085, 0.012, 0.003], 0);
      mk(hg, G.sph(8), M.white, [s * 0.045 + 0.007, 0.114, 0.1292], [0.0058, 0.0066, 0.002], 0);
      mk(hg, G.rbox(0.068, 0.012, 0.012, 0.005), M.eye, [s * 0.048, 0.129, 0.1175], [1, 1, 1], 0, [0, 0, s * -0.12]);
      if (spec.lashes) mk(hg, G.rbox(0.022, 0.008, 0.008, 0.003), M.eye, [s * 0.083, 0.13, 0.108], [1, 1, 1], 0, [0, s * 0.5, s * 0.5]);
    }
    const b = mk(hg, G.rbox(0.058, 0.014, 0.012, 0.005), M.hair, [s * 0.05, 0.158, 0.114], [1, 1, 1], 0);
    J['brow' + (s > 0 ? 'L' : 'R')] = b; b.userData.side = s;
    if (spec.hoops) mk(hg, G.tor(0.022, 0.004), M.metal, [s * 0.128, 0.05, 0], [1, 1, 1], 0, [0, Math.PI / 2, 0]);
  }
  mk(hg, G.sph(10), M.skinD, [0, 0.076, 0.127], [0.011, 0.018, 0.011], 0);
  J.mouth = mk(hg, G.rbox(0.04, 0.009, 0.008, 0.003), M.lip, [0, 0.045, 0.121], [1, 1, 1], 0);
  if (spec.hairStyle !== 'bald') mk(hg, G.sph(22), M.hair, [0, 0.2, -0.022], spec.hairStyle === 'braids' ? [0.14, 0.09, 0.145] : [0.136, 0.083, 0.14]);
  if (spec.hairStyle === 'fade') {
    const r = rng(spec.seed * 13 + 1);
    for (let i = 0; i < 16; i++) {
      const a = (i / 16) * Math.PI * 2, rr = 0.03 + r() * 0.07;
      const x = Math.cos(a) * rr, z = Math.sin(a) * rr - 0.01 + 0.015;
      mk(hg, G.cyl(0.0, 0.032, 0.085, 5), M.hair, [x, 0.262 - rr * 0.35, z], [1, 1, 1], OL * 0.6, [-0.5 - r() * 0.5 + z * 2, r() * 3, x * 3]);
    }
  }
  if (spec.hairStyle === 'curly') {
    const r = rng(7);
    for (let i = 0; i < 22; i++) {
      const a = r() * Math.PI * 2, el = 0.25 + r() * 1.2;
      const x = Math.cos(a) * Math.cos(el) * 0.128, z = Math.sin(a) * Math.cos(el) * 0.13 - 0.022, y = 0.2 + Math.sin(el) * 0.078;
      if (z > 0.07 && y < 0.235) continue;
      mk(hg, G.sph(10), M.hair, [x, y, z], [0.036, 0.03, 0.036], OL * 0.7);
    }
  }
  if (spec.hairStyle === 'braids') {
    for (let i = 0; i < 18; i++) {
      const ang = Math.PI * (0.62 + 0.76 * (i / 17));
      const x = Math.sin(ang) * 0.13, z = Math.cos(ang) * 0.135 - 0.02;
      mk(hg, G.cap(0.017, 0.44), M.hair, [x * 1.04, -0.1, z * 1.04], [1, 1, 1], OL * 0.6, [-z * 0.9, 0, x * 0.9]);
    }
    for (const s of [1, -1]) for (const k of [0, 1]) {
      const x = s * (0.118 - k * 0.012), z = 0.05 - k * 0.03;
      mk(hg, G.cap(0.016, 0.3), M.hair, [x, -0.03, z], [1, 1, 1], OL * 0.6, [-0.05, 0, s * 0.12]);
    }
  }
  if (spec.beard) { mk(hg, G.sph(), M.hair, [0, 0.018, 0.1], [0.034, 0.03, 0.03], 0); mk(hg, G.rbox(0.05, 0.01, 0.01, 0.004), M.hair, [0, 0.062, 0.122], [1, 1, 1], 0); }
  if (spec.glasses) {
    for (const s of [1, -1]) mk(hg, G.rbox(0.064, 0.034, 0.014, 0.006), M.dark, [s * 0.047, 0.122, 0.124], [1, 1, 1], 0);
    mk(hg, G.rbox(0.03, 0.008, 0.008, 0.003), M.dark, [0, 0.128, 0.13], [1, 1, 1], 0);
  }

  // arms
  const sw = Math.sqrt(w);
  for (const [S, s] of [['L', 1], ['R', -1]]) {
    const sh = jt('shoulder' + S, chest, s * 0.205 * w, 0.26, 0);
    mk(sh, G.sph(14), M.sleeve, [0, -0.01, 0], [0.072 * sw, 0.072 * sw, 0.072 * sw]);
    const ar = f3(0.056 * sw);
    mk(sh, G.cap(ar, 0.17), M.sleeve, [0, -0.135, 0]);
    const el = jt('elbow' + S, sh, 0, -0.27, 0);
    mk(el, G.cap(f3(ar * 0.86), 0.15), M.fore, [0, -0.115, 0]);
    const ha = jt('hand' + S, el, 0, -0.24, 0);
    mk(ha, G.rbox(f3(0.072 * sw), 0.09, f3(0.062 * sw), 0.026), M.skin, [0, -0.045, 0.006]);
    if (spec.stripes) {
      mk(sh, G.rbox(0.013, 0.26, 0.013, 0.005), M.stripe, [s * ar * 0.97, -0.135, 0], [1, 1, 1], 0);
      mk(el, G.rbox(0.012, 0.22, 0.012, 0.005), M.stripe, [s * ar * 0.84, -0.115, 0], [1, 1, 1], 0);
    }
  }
  // legs
  const shw = Math.sqrt(hw);
  for (const [S, s] of [['L', 1], ['R', -1]]) {
    const hp = jt('hip' + S, hips, s * 0.092 * hw, -0.03, 0);
    const lr = f3(0.075 * shw);
    mk(hp, G.cap(lr, 0.27), M.pants, [0, -0.21, 0]);
    const kn = jt('knee' + S, hp, 0, -0.44, 0);
    mk(kn, G.cap(f3(lr * 0.82), 0.29), M.pants, [0, -0.2, 0]);
    const an = jt('ankle' + S, kn, 0, -0.44, 0);
    mk(an, G.rbox(0.105, 0.085, 0.25, 0.035), M.shoes, [0, -0.035, 0.045]);
    mk(an, G.rbox(0.11, 0.025, 0.26, 0.01), M.sole, [0, -0.07, 0.045], [1, 1, 1], 0);
    if (spec.stripes) {
      mk(hp, G.rbox(0.014, 0.4, 0.014, 0.005), M.stripe, [s * lr * 0.97, -0.21, 0], [1, 1, 1], 0);
      mk(kn, G.rbox(0.013, 0.42, 0.013, 0.005), M.stripe, [s * lr * 0.8, -0.2, 0], [1, 1, 1], 0);
    }
  }

  scene.add(root);
  const blob = new THREE.Mesh(new THREE.CircleGeometry(0.36 * (spec.scale ?? 1) * Math.sqrt(w), 24),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.42, depthWrite: false }));
  blob.rotation.x = -Math.PI / 2; blob.renderOrder = 1; scene.add(blob);
  return { name: spec.name, root, body, J, spec, blob, seed: spec.seed ?? 1, brow: spec.brow ?? 0.1 };
}

// ---------- poses (radians). Character faces +Z; its left side is +X. ----------
export const P = {};
P.idle = { shoulderL: [0.05, 0, 0.12], shoulderR: [0.05, 0, -0.12], elbowL: [-0.18, 0, 0], elbowR: [-0.18, 0, 0], hipL: [0, 0, 0.03], hipR: [0, 0, -0.03] };
P.idleBig = { shoulderL: [0.05, 0, 0.26], shoulderR: [0.05, 0, -0.26], elbowL: [-0.25, 0, 0], elbowR: [-0.25, 0, 0], hipL: [0, 0, 0.05], hipR: [0, 0, -0.05], brow: 0.3 };
P.pocket = { shoulderL: [0.22, 0, 0.2], elbowL: [-0.5, 0, 0], shoulderR: [0.22, 0, -0.2], elbowR: [-0.5, 0, 0], hipL: [0, 0, 0.04], hipR: [0, 0, -0.04], head: [0.03, 0, 0] };
P.guard = { hips: [0, 0.4, 0], hy: -0.07, spine: [0.12, 0, 0], chest: [0.06, -0.2, 0], head: [0.08, -0.2, 0],
  shoulderL: [-1.05, 0, 0.3], elbowL: [-2.05, 0, 0], shoulderR: [-0.75, 0, -0.35], elbowR: [-2.2, 0, 0],
  hipL: [-0.4, 0, 0.1], kneeL: [0.5, 0, 0], ankleL: [-0.1, 0, 0], hipR: [0.25, 0, -0.12], kneeR: [0.45, 0, 0], ankleR: [0.2, 0, 0], brow: 0.32 };
P.duck = { hips: [0, 0.4, 0], hy: -0.36, spine: [0.5, 0, 0], chest: [0.3, -0.1, 0], head: [-0.55, -0.1, 0],
  shoulderL: [-1.2, 0, 0.3], elbowL: [-2.0, 0, 0], shoulderR: [-0.9, 0, -0.35], elbowR: [-2.1, 0, 0],
  hipL: [-1.15, 0, 0.15], kneeL: [1.75, 0, 0], ankleL: [-0.55, 0, 0], hipR: [-0.35, 0, -0.15], kneeR: [1.6, 0, 0], ankleR: [-0.2, 0, 0], brow: 0.36 };
P.punchR = { hy: -0.14, spine: [0.28, 0, 0], chest: [0.08, 0.55, 0], head: [0, -0.35, 0],
  shoulderR: [-1.4, 0, -0.08], elbowR: [-0.08, 0, 0], shoulderL: [-0.9, 0, 0.45], elbowL: [-2.1, 0, 0],
  hipL: [-0.75, 0, 0.08], kneeL: [0.85, 0, 0], ankleL: [-0.1, 0, 0], hipR: [0.4, 0, -0.06], kneeR: [0.4, 0, 0], ankleR: [0.35, 0, 0], brow: 0.42 };
P.hookWind = { hy: -0.05, hips: [0, -0.25, 0], chest: [0.05, -0.6, 0], head: [0, 0.5, 0],
  shoulderR: [-0.5, 0, -1.15], elbowR: [-1.3, 0, 0], shoulderL: [-0.8, 0, 0.35], elbowL: [-1.7, 0, 0],
  hipL: [-0.35, 0, 0.1], kneeL: [0.35, 0, 0], hipR: [0.2, 0, -0.12], kneeR: [0.3, 0, 0], ankleR: [0.15, 0, 0], brow: 0.38 };
P.hookFollow = { hy: -0.1, hips: [0, 0.35, 0], spine: [0.2, 0, 0], chest: [0.15, 0.75, 0], head: [0, -0.6, 0],
  shoulderR: [-1.45, 0, -0.45], elbowR: [-1.2, 0, 0], shoulderL: [-0.6, 0, 0.5], elbowL: [-1.5, 0, 0],
  hipL: [-0.55, 0, 0.1], kneeL: [0.6, 0, 0], hipR: [0.3, 0, -0.1], kneeR: [0.35, 0, 0], ankleR: [0.3, 0, 0], brow: 0.4, mouth: 1.8 };
P.hitGut = { hy: -0.12, spine: [0.65, 0, 0], chest: [0.3, 0, 0], neck: [-0.1, 0, 0], head: [-0.35, 0, 0],
  shoulderL: [-0.7, 0, 0.5], elbowL: [-1.3, 0, 0], shoulderR: [-0.7, 0, -0.5], elbowR: [-1.3, 0, 0],
  hipL: [-0.4, 0, 0.05], kneeL: [0.55, 0, 0], hipR: [-0.25, 0, -0.05], kneeR: [0.45, 0, 0], mouth: 3.2, brow: -0.25 };
P.kickChamber = { hy: 0.02, spine: [-0.25, 0, -0.25], chest: [-0.1, 0, -0.15], head: [0.1, -0.5, 0.3],
  shoulderL: [-0.4, 0, 1.1], elbowL: [-1.1, 0, 0], shoulderR: [0.3, 0, -0.8], elbowR: [-1.0, 0, 0],
  hipR: [-1.5, 0, -0.75], kneeR: [1.9, 0, 0], ankleR: [0.4, 0, 0], hipL: [0.05, 0, 0.06], kneeL: [0.3, 0, 0], brow: 0.42 };
P.kickExtend = { hy: 0.02, spine: [-0.35, 0, -0.5], chest: [-0.1, 0, -0.2], head: [0.15, -0.7, 0.55],
  shoulderL: [-0.3, 0, 1.25], elbowL: [-0.9, 0, 0], shoulderR: [0.5, 0, -1.0], elbowR: [-0.6, 0, 0],
  hipR: [-1.45, 0, -1.25], kneeR: [0.1, 0, 0], ankleR: [0.6, 0, 0], hipL: [0.1, 0, 0.15], kneeL: [0.25, 0, 0], brow: 0.48 };
P.flyHit = { spine: [-0.4, 0, 0], chest: [-0.2, 0, 0], head: [-0.5, 0, 0],
  shoulderL: [-2.4, 0, 0.5], elbowL: [-0.5, 0, 0], shoulderR: [-2.2, 0, -0.6], elbowR: [-0.4, 0, 0],
  hipL: [-0.9, 0, 0.2], kneeL: [0.8, 0, 0], hipR: [-0.5, 0, -0.25], kneeR: [1.0, 0, 0], mouth: 3.5, brow: -0.3 };
P.down = { shoulderL: [-0.3, 0, 1.2], elbowL: [-0.4, 0, 0], shoulderR: [-0.2, 0, -1.0], elbowR: [-0.6, 0, 0],
  hipL: [-0.2, 0, 0.25], kneeL: [0.4, 0, 0], hipR: [0, 0, -0.2], kneeR: [0.15, 0, 0], head: [0, 0.5, 0], mouth: 2, brow: -0.3 };
P.armsWide = { spine: [-0.08, 0, 0], chest: [-0.1, 0, 0], head: [-0.12, 0, 0],
  shoulderL: [-0.35, 0, 1.35], elbowL: [-0.45, 0, 0], shoulderR: [-0.35, 0, -1.35], elbowR: [-0.45, 0, 0],
  hipL: [0, 0, 0.2], kneeL: [0.1, 0, 0], hipR: [0, 0, -0.2], kneeR: [0.1, 0, 0], mouth: 3.5, brow: -0.35 };
P.shrug = { shoulderL: [-0.2, 0, 0.55], elbowL: [-1.5, 0.6, 0], shoulderR: [-0.2, 0, -0.55], elbowR: [-1.5, -0.6, 0],
  head: [0.05, 0, 0.2], hipL: [0, 0, 0.08], hipR: [0, 0, -0.08], mouth: 2, brow: -0.4 };
P.lean = { spine: [0.22, 0, 0], chest: [0.08, 0, 0], head: [-0.1, 0, 0],
  shoulderL: [-0.75, 0, 0.25], elbowL: [-0.85, 0, 0], shoulderR: [-0.75, 0, -0.25], elbowR: [-0.85, 0, 0],
  hipL: [0, 0, 0.05], hipR: [0.05, 0, -0.05], brow: -0.05 };
P.nodBack = { ...P.lean, head: [0.1, 0.35, 0.25], brow: -0.22 };
P.lookUp = { ...P.lean, head: [-0.05, -0.55, 0], brow: -0.1 };
P.slide = { spine: [0.35, 0, 0], chest: [0.05, 0.2, 0], head: [-0.1, 0, 0],
  shoulderR: [-1.25, 0, -0.15], elbowR: [-0.25, 0, 0], shoulderL: [-0.75, 0, 0.25], elbowL: [-0.85, 0, 0],
  hipL: [0, 0, 0.05], hipR: [0.05, 0, -0.05], brow: -0.15 };
P.shoulderTap = { spine: [0.14, 0, 0], chest: [0.05, 0, 0], shoulderR: [-1.25, 0, 0.05], elbowR: [-0.45, 0, 0],
  shoulderL: [0.05, 0, 0.22], elbowL: [-0.3, 0, 0], hipL: [-0.15, 0, 0.05], kneeL: [0.15, 0, 0], hipR: [0.1, 0, -0.05], brow: 0.32 };
P.lookBack = { ...P.pocket, chest: [0, -0.28, 0], neck: [0, -0.35, 0], head: [0.05, -0.85, 0], brow: 0.48 };
P.catch = { ...P.pocket, shoulderR: [-0.25, 0, -1.2], elbowR: [-0.3, 0, 0], head: [0, 0.35, 0], brow: 0.2 };
P.raiseGlass = { ...P.pocket, shoulderR: [-0.55, 0, -0.45], elbowR: [-1.95, 0, 0], head: [0.05, 0.2, 0], brow: 0.15 };
P.lookDoor = { ...P.pocket, head: [0, 0.35, 0], brow: 0.2 };

function walkPose(ph, style) {
  const s = Math.sin(ph), c = Math.cos(ph);
  const amp = style === 'heavy' ? 0.38 : style === 'quick' ? 0.5 : 0.45;
  const p = {
    hy: -0.035 * s * s - 0.01, hips: [0, 0.1 * s, 0], spine: [0.05, 0, 0], chest: [0.04, -0.16 * s, 0], head: [0.02, 0.06 * s, 0],
    hipL: [-amp * s, 0, 0.03], hipR: [amp * s, 0, -0.03],
    kneeL: [0.12 + 0.85 * Math.max(0, c) ** 2, 0, 0], kneeR: [0.12 + 0.85 * Math.max(0, -c) ** 2, 0, 0],
    ankleL: [-0.12 * c, 0, 0], ankleR: [0.12 * c, 0, 0],
  };
  if (style === 'pocket') {
    p.shoulderL = [0.22 + 0.06 * s, 0, 0.2]; p.shoulderR = [0.22 - 0.06 * s, 0, -0.2];
    p.elbowL = [-0.5, 0, 0]; p.elbowR = [-0.5, 0, 0]; p.brow = 0.15;
  } else {
    const a = style === 'heavy' ? 0.3 : 0.4;
    p.shoulderL = [a * s, 0, style === 'heavy' ? 0.25 : 0.1]; p.shoulderR = [-a * s, 0, style === 'heavy' ? -0.25 : -0.1];
    p.elbowL = [-0.3 - 0.25 * Math.max(0, -s), 0, 0]; p.elbowR = [-0.3 - 0.25 * Math.max(0, s), 0, 0];
    if (style === 'heavy') p.brow = 0.32;
  }
  return p;
}

function dancePose(b, seed) {
  const ph = 2 * Math.PI * b, s = Math.sin(ph), s2 = Math.sin(ph * 0.5 + seed), bob = 0.5 + 0.5 * Math.cos(ph);
  return {
    hy: -0.06 * bob, hips: [0, 0.25 * s2, 0.05 * s], spine: [0.1, 0, 0], chest: [0.05, -0.2 * s2, 0.06 * s], head: [0.12 * Math.cos(ph), 0.2 * s2, 0],
    shoulderL: [-0.6 - 0.4 * s2, 0, 0.4 + 0.2 * s], elbowL: [-1.4, 0, 0], shoulderR: [-0.6 + 0.4 * s2, 0, -0.4 + 0.2 * s], elbowR: [-1.4, 0, 0],
    hipL: [-0.2, 0, 0.12], kneeL: [0.3 + 0.3 * bob, 0, 0], ankleL: [0.1, 0, 0], hipR: [-0.2, 0, -0.12], kneeR: [0.3 + 0.3 * bob, 0, 0], ankleR: [0.1, 0, 0],
    mouth: 1.4,
  };
}

const WALKS = { walk: 'normal', walkPocket: 'pocket', walkHeavy: 'heavy', walkQuick: 'quick' };
export function resolvePose(spec, c, ctx) {
  let name = spec, over = null;
  if (Array.isArray(spec)) { name = spec[0]; over = spec[1]; }
  let base;
  if (WALKS[name]) base = walkPose(2 * Math.PI * ctx.tg / ctx.period(c.name, ctx.tg), WALKS[name]);
  else if (name === 'dance') base = dancePose(ctx.tg * ctx.bpm / 60 + c.seed * 0.37, c.seed);
  else base = P[name] || P.idle;
  return over ? { ...base, ...over } : base;
}

function blendPose(a, b, u) {
  if (a === b || u <= 0) return a;
  if (u >= 1) return b;
  const o = {};
  for (const n of JOINTS) {
    const x = a[n] || [0, 0, 0], y = b[n] || [0, 0, 0];
    o[n] = [lerp(x[0], y[0], u), lerp(x[1], y[1], u), lerp(x[2], y[2], u)];
  }
  for (const k of ['hy', 'brow', 'mouth']) {
    const d = k === 'mouth' ? 1 : k === 'brow' ? undefined : 0;
    const x = a[k] ?? d, y = b[k] ?? d;
    if (x !== undefined || y !== undefined) o[k] = lerp(x ?? y, y ?? x, u);
  }
  return o;
}

function applyPose(c, p, tg) {
  for (const n of JOINTS) {
    const r = p[n];
    if (r) c.J[n].rotation.set(r[0], r[1], r[2]); else c.J[n].rotation.set(0, 0, 0);
  }
  c.J.chest.rotation.x += 0.015 * Math.sin(tg * 2.3 + c.seed); // breathing
  c.J.hips.position.y = 0.99 + (p.hy || 0);
  const brow = p.brow ?? c.brow;
  c.J.browL.rotation.z = brow; c.J.browR.rotation.z = -brow;
  c.J.browL.position.y = c.J.browR.position.y = 0.163 + (brow < 0 ? -brow * 0.02 : 0);
  c.J.mouth.scale.set(p.mouth > 1.5 ? 0.85 : 1, p.mouth || 1, 1);
}

// Evaluate a keyframe track at animation time `at` (shot-local, possibly remapped).
export function evalChar(c, keys, at, ctx) {
  let a = keys[0], b = keys[0], u = 0;
  if (at >= keys[keys.length - 1].t) a = b = keys[keys.length - 1];
  else if (at > keys[0].t) {
    for (let i = 0; i < keys.length - 1; i++) {
      if (at >= keys[i].t && at < keys[i + 1].t) { a = keys[i]; b = keys[i + 1]; u = (at - a.t) / (b.t - a.t); break; }
    }
  }
  const e = EASE[b.ease || 'inout'](u);
  const pu = a.walk ? u : e;
  const pos = [lerp(a.p[0], b.p[0], pu), lerp(a.p[1], b.p[1], pu), lerp(a.p[2], b.p[2], pu)];
  if (b.arc && a !== b) pos[1] += 4 * b.arc * u * (1 - u);
  c.root.position.set(pos[0], pos[1], pos[2]);
  c.root.rotation.set(lerp(a.rx ?? 0, b.rx ?? 0, e), lerp(a.ry ?? 0, b.ry ?? 0, e), 0);
  const pa = resolvePose(a.pose, c, ctx), pb = a === b ? pa : resolvePose(b.pose, c, ctx);
  applyPose(c, blendPose(pa, pb, a.walk ? 0 : e), ctx.tg);
  const lying = Math.abs(c.root.rotation.x) > 0.8;
  const h = Math.max(0, pos[1] - (lying ? 0.15 : 0));
  c.blob.position.set(pos[0] - (lying ? Math.sin(c.root.rotation.y) * 0.8 : 0), (ctx.floorY ?? 0) + 0.012, pos[2] - (lying ? Math.cos(c.root.rotation.y) * 0.8 : 0));
  const k = 1 / (1 + h * 1.4);
  c.blob.scale.set(lying ? 1.6 : k, lying ? 2.6 : k, 1);
  c.blob.rotation.z = lying ? c.root.rotation.y : 0;
  c.blob.material.opacity = 0.42 * k;
}

export const CAST = {
  andile: { name: 'andile', skin: 0x9a6444, lapels: true, iris: 0x6a3a1a, hair: 0x1a1210, hairStyle: 'fade', top: 0x3d6b8f, under: 0xb8b8bc, pants: 0x222428,
    shoes: 0x23304f, openJacket: true, tie: true, hood: true, brow: 0.16, seed: 1 },
  futhi: { name: 'futhi', skin: 0x8a5438, lashes: true, iris: 0x7a4418, hair: 0x1c1414, hairStyle: 'braids', top: 0x1f2a44, under: 0x1f2a44, sleeve: 0x8a5438,
    fore: 0x8a5438, pants: 0x4a6fa5, shoes: 0x2b2b33, hoops: true, pendant: true, metal: 0xe0b040, lip: 0x6a2c34,
    build: 0.86, hipW: 0.95, scale: 0.97, brow: -0.05, seed: 2 },
  sib: { name: 'sib', skin: 0x7e5036, hair: 0x15100e, hairStyle: 'curly', top: 0x1c1c22, under: 0x1c1c22, pants: 0x1c1c22,
    shoes: 0xf0f0f0, sole: 0xffffff, stripes: true, chain: true, zip: true, build: 1.2, scale: 0.93, headScale: 1.06, brow: -0.1, seed: 3 },
  thug: { name: 'thug', skin: 0x6a4430, hair: 0x15100e, hairStyle: 'bald', beard: true, glasses: true, top: 0x8c2a2a, under: 0x151515,
    pants: 0x1d1d22, shoes: 0x111111, sole: 0x222222, openJacket: true, build: 1.42, hipW: 1.25, scale: 1.12, brow: 0.3, seed: 4 },
  crowdA: { name: 'crowdA', skin: 0x6a4430, hair: 0x140f0d, hairStyle: 'braids', top: 0xb0306a, sleeve: 0x6a4430, fore: 0x6a4430,
    pants: 0x2a2a3a, shoes: 0x222222, build: 0.88, scale: 0.96, seed: 5 },
  crowdB: { name: 'crowdB', skin: 0x7b5038, hair: 0x140f0d, hairStyle: 'fade', top: 0x2f8f8f, pants: 0x30303c, shoes: 0xdddddd, seed: 6 },
  crowdC: { name: 'crowdC', skin: 0x5e3c2a, hair: 0x140f0d, hairStyle: 'curly', top: 0xd9a030, pants: 0x2b2440, shoes: 0x333333, build: 1.05, seed: 7 },
};

// Mirror a pose left<->right (used so the punching arm is on the camera side).
export function mirror(p) {
  const o = {};
  for (const [k, v] of Object.entries(p)) {
    if (!Array.isArray(v)) { o[k] = v; continue; }
    const n = k.endsWith('L') ? k.slice(0, -1) + 'R' : k.endsWith('R') ? k.slice(0, -1) + 'L' : k;
    o[n] = [v[0], -v[1], -v[2]];
  }
  return o;
}
P.punchL = mirror(P.punchR);
