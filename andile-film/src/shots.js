// Per-shot camera + character choreography. Times are shot-local seconds.
// Character keys: { t, p:[x,y,z], ry, rx, pose, ease, walk, arc }. `remap` = slow-motion curve [real, anim].
import { EASE, clamp, lerp } from './toon.js';

const HP = Math.PI / 2;
const still = (p, ry, pose) => [{ t: 0, p, ry, pose }];
const crowd = (pose = 'dance') => ({
  crowdA: still([-5.2, 0, -3.8], 0.6, pose), crowdB: still([-6.2, 0, 1.8], 2.2, pose), crowdC: still([-3.8, 0, 3.2], 3.6, pose),
});
const futhiBar = still([7.05, 0, -0.5], -HP, 'lean');
const doorKeys = (keys) => (lt) => {
  for (let i = keys.length - 1; i >= 0; i--) if (lt >= keys[i][0]) {
    const a = keys[i], b = keys[i + 1]; if (!b) return a[1];
    const u = (lt - a[0]) / (b[0] - a[0]); return lerp(a[1], b[1], EASE[b[2] || 'inout'](u));
  }
  return keys[0][1];
};

export const SHOTS = {
  S01: {
    cam: [{ t: 0, pos: [0, 2.0, 84], look: [0, 6, -200], fov: 40 }, { t: 3, pos: [6, 10, -22], look: [0, 30, -220], fov: 36, ease: 'linear' }],
    chars: {}, portrait: { hcov: 0.75 },
  },
  S02: {
    floorY: 0.16,
    cam: [{ t: 0, pos: [-6.1, 0.95, -2.55], look: [-9.0, 1.25, -3.9], fov: 40 }, { t: 3, pos: [-2.0, 1.0, -2.6], look: [-4.7, 1.3, -3.9], fov: 36, ease: 'linear' }],
    chars: { andile: [{ t: 0, p: [-9.2, 0.16, -3.9], ry: HP, pose: 'walkPocket', walk: true }, { t: 3, p: [-4.7, 0.16, -3.9], ry: HP, pose: 'walkPocket' }] },
    portrait: { hcov: 0.7, back: 1.05 },
  },
  S03: {
    floorY: 0.16,
    cam: [{ t: 0, pos: [-4.0, 1.25, 0.7], look: [-4.3, 1.45, -3.9], fov: 34 }, { t: 1.5, pos: [-1.8, 1.3, 0.7], look: [-2.1, 1.5, -3.9], fov: 34, ease: 'linear' }],
    chars: { andile: [{ t: 0, p: [-4.7, 0.16, -3.9], ry: HP, pose: 'walkPocket', walk: true }, { t: 1.5, p: [-2.45, 0.16, -3.9], ry: HP, pose: 'walkPocket' }] },
    portrait: { hcov: 0.62, back: 1.1 },
  },
  S04: {
    cam: [{ t: 0, pos: [-6.4, 4.3, 7.4], look: [2.0, 1.0, -3.6], fov: 46 }, { t: 2, pos: [-5.4, 3.8, 6.6], look: [2.4, 1.0, -3.4], fov: 44 }],
    chars: {
      andile: [{ t: 0, p: [0, 0, -9.3], ry: 0.54, pose: 'pocket' }, { t: 0.35, p: [0, 0, -9.3], ry: 0.54, pose: 'walkPocket', walk: true }, { t: 2.0, p: [1.65, 0, -6.5], ry: 0.54, pose: 'walkPocket' }],
      futhi: [{ t: 0, p: [7.05, 0, -0.5], ry: -HP, pose: 'lean' }, { t: 0.7, p: [7.05, 0, -0.5], ry: -HP, pose: 'lean' }, { t: 1.1, p: [7.05, 0, -0.5], ry: -HP, pose: 'lookUp' }],
      thug: still([-1.2, 0, 0.4], 2.6, 'dance'), ...crowd(),
    },
    door: doorKeys([[0, 0], [0.3, -1.75, 'snap']]),
    portrait: { hcov: 0.8, back: 1.15 },
  },
  S05: {
    cam: [{ t: 0, pos: [4.25, 1.74, -0.98], look: [7.05, 1.5, -0.45], fov: 27 }, { t: 1.5, pos: [4.35, 1.73, -0.95], look: [7.05, 1.52, -0.45], fov: 25 }],
    chars: {
      andile: still([4.9, 0, -0.5], HP, 'pocket'),
      futhi: [{ t: 0, p: [7.05, 0, -0.5], ry: -HP, pose: 'lean' }, { t: 0.5, p: [7.05, 0, -0.5], ry: -HP, pose: 'lean' }, { t: 0.85, p: [7.05, 0, -0.5], ry: -HP, pose: 'nodBack' }],
      thug: still([-1.2, 0, 0.4], 2.6, 'dance'), ...crowd(),
    },
    portrait: { hcov: 0.72 },
  },
  S06: {
    cam: [{ t: 0, pos: [2.7, 0.42, 2.3], look: [3.2, 1.55, -0.4], fov: 48 }, { t: 1.5, pos: [3.1, 0.38, 2.0], look: [4.0, 1.7, -0.45], fov: 44 }],
    chars: {
      thug: [{ t: 0, p: [2.6, 0, -0.25], ry: HP, pose: 'walkHeavy', walk: true }, { t: 1.0, p: [4.15, 0, -0.45], ry: HP, pose: 'walkHeavy' }, { t: 1.4, p: [4.15, 0, -0.45], ry: HP, pose: 'shoulderTap' }],
      andile: still([4.9, 0, -0.5], HP, 'pocket'), futhi: futhiBar, ...crowd(),
    },
    portrait: { hcov: 0.7, back: 1.1 },
  },
  S07: {
    cam: [{ t: 0, pos: [5.75, 1.76, 0.62], look: [4.92, 1.7, -0.45], fov: 29, roll: 0.16 }, { t: 1.5, pos: [5.55, 1.75, 0.4], look: [4.92, 1.7, -0.45], fov: 25, roll: 0.2 }],
    chars: {
      andile: [{ t: 0, p: [4.9, 0, -0.5], ry: HP, pose: 'pocket' }, { t: 0.3, p: [4.9, 0, -0.5], ry: HP, pose: 'pocket' }, { t: 0.95, p: [4.9, 0, -0.5], ry: HP, pose: 'lookBack' }],
      thug: still([4.15, 0, -0.45], HP, 'shoulderTap'), futhi: futhiBar, ...crowd(),
    },
    portrait: { hcov: 0.7 },
  },
  S08: {
    remap: [[0, 0], [0.45, 0.45], [1.2, 0.75], [1.5, 1.05]],
    cam: [{ t: 0, pos: [4.45, 1.25, 3.3], look: [4.4, 1.15, -0.5], fov: 40 }, { t: 1.5, pos: [4.4, 1.1, 2.9], look: [4.4, 1.0, -0.5], fov: 38 }],
    chars: {
      andile: [{ t: 0, p: [4.95, 0, -0.5], ry: -HP, pose: 'pocket' }, { t: 0.35, p: [4.95, 0, -0.5], ry: -HP, pose: 'guard', ease: 'snap' },
        { t: 0.62, p: [4.95, 0, -0.5], ry: -HP, pose: 'duck', ease: 'snap' }, { t: 1.05, p: [4.95, 0, -0.5], ry: -HP, pose: 'duck' }],
      thug: [{ t: 0, p: [3.9, 0, -0.5], ry: HP, pose: 'idleBig' }, { t: 0.35, p: [3.9, 0, -0.5], ry: HP, pose: 'hookWind' },
        { t: 0.72, p: [4.05, 0, -0.5], ry: HP, pose: 'hookFollow', ease: 'snap' }, { t: 1.05, p: [4.08, 0, -0.5], ry: HP, pose: 'hookFollow' }],
      futhi: futhiBar, ...crowd(),
    },
    portrait: { hcov: 0.95, back: 1.35 },
  },
  S09: {
    remap: [[0, 0], [0.22, 0.22], [0.6, 0.3], [1.0, 0.68]],
    cam: [{ t: 0, pos: [3.8, 0.75, 1.1], look: [4.35, 1.15, -0.5], fov: 48, roll: -0.1 }, { t: 1.0, pos: [3.7, 0.7, 0.95], look: [4.25, 1.2, -0.5], fov: 45, roll: -0.12 }],
    chars: {
      andile: [{ t: 0, p: [4.95, 0, -0.5], ry: -HP, pose: 'duck' }, { t: 0.2, p: [4.8, 0, -0.5], ry: -HP, pose: 'punchL', ease: 'snap' }, { t: 0.68, p: [4.78, 0, -0.5], ry: -HP, pose: 'punchL' }],
      thug: [{ t: 0, p: [4.08, 0, -0.5], ry: HP, pose: 'hookFollow' }, { t: 0.22, p: [4.08, 0, -0.5], ry: HP, pose: 'hookFollow' },
        { t: 0.3, p: [3.85, 0, -0.5], ry: HP, pose: 'hitGut', ease: 'snap' }, { t: 0.68, p: [3.72, 0, -0.5], ry: HP, pose: 'hitGut' }],
      futhi: futhiBar,
    },
    portrait: { hcov: 0.95, back: 1.25 },
  },
  S10: {
    remap: [[0, 0], [0.7, 0.7], [0.9, 0.78], [2.5, 1.35]],
    camFn: (lt) => {
      const u = EASE.inout(clamp(lt / 2.5)), a = 1.25 + u * 1.3, R = 3.4;
      const f = EASE.inout(clamp((lt - 0.8) / 1.5));
      return { pos: [4.3 + R * Math.cos(a), 1.0 + 0.9 * u, -0.5 + R * Math.sin(a)], look: [lerp(4.2, 2.3, f), lerp(1.15, 1.35, f), lerp(-0.5, -0.8, f)], fov: 44 + 6 * f };
    },
    track: { char: 'thug', t0: 0.75, ramp: 0.5, w: 0.85, off: [-0.8, 0.7, 0] },
    chars: {
      andile: [{ t: 0, p: [4.78, 0, -0.5], ry: -HP, pose: 'punchL' }, { t: 0.15, p: [4.78, 0, -0.5], ry: -HP, pose: 'guard' },
        { t: 0.4, p: [4.7, 0, -0.5], ry: -HP + Math.PI * 1.25, pose: 'kickChamber', arc: 0.12 },
        { t: 0.7, p: [4.65, 0, -0.5], ry: Math.PI * 2, pose: 'kickExtend', ease: 'out' }, { t: 1.0, p: [4.65, 0, -0.5], ry: Math.PI * 2, pose: 'kickExtend' },
        { t: 1.35, p: [4.65, 0, -0.5], ry: Math.PI * 1.5, pose: 'guard' }],
      thug: [{ t: 0, p: [3.72, 0, -0.5], ry: HP, pose: 'hitGut' }, { t: 0.68, p: [3.72, 0, -0.5], ry: HP, pose: 'hitGut' },
        { t: 0.74, p: [3.55, 0.1, -0.5], ry: HP, rx: -0.15, pose: 'flyHit', ease: 'snap' }, { t: 1.35, p: [1.5, 0.95, -0.9], ry: HP, rx: -0.9, pose: 'flyHit', ease: 'linear' }],
      futhi: futhiBar, ...crowd(),
    },
    portrait: { hcov: 0.95, back: 1.25 },
  },
  S11: {
    cam: [{ t: 0, pos: [-2.3, 5.0, -0.55], look: [-2.3, 0, -0.53], fov: 56, up: [1, 0, 0] }, { t: 2, pos: [-2.6, 4.3, -0.55], look: [-2.6, 0, -0.53], fov: 54, up: [1, 0, 0.18] }],
    noCones: true,
    chars: {
      thug: [{ t: 0, p: [1.3, 1.0, -0.9], ry: HP, rx: -1.0, pose: 'flyHit' }, { t: 0.35, p: [-1.3, 0.18, -0.5], ry: HP, rx: -1.5708, pose: 'down', ease: 'in' },
        { t: 0.9, p: [-1.8, 0.18, -0.5], ry: HP, rx: -1.5708, pose: 'down', ease: 'out' }],
      andile: still([4.65, 0, -0.5], -HP, 'guard'),
      crowdA: [{ t: 0, p: [-5.2, 0, -3.8], ry: 0.6, pose: 'dance' }, { t: 0.5, p: [-5.2, 0, -3.8], ry: 0.6, pose: 'dance' }, { t: 0.9, p: [-5.2, 0, -3.8], ry: 0.9, pose: 'shrug' }],
      crowdB: [{ t: 0, p: [-6.2, 0, 1.8], ry: 2.2, pose: 'dance' }, { t: 0.55, p: [-6.2, 0, 1.8], ry: 2.2, pose: 'dance' }, { t: 0.95, p: [-6.2, 0, 1.8], ry: 2.0, pose: 'idle' }],
      crowdC: [{ t: 0, p: [-3.8, 0, 3.2], ry: 3.6, pose: 'dance' }, { t: 0.45, p: [-3.8, 0, 3.2], ry: 3.6, pose: 'dance' }, { t: 0.85, p: [-3.8, 0, 3.2], ry: 3.3, pose: 'armsWide' }],
    },
    portrait: { hcov: 0.85 },
  },
  S12: {
    cam: [{ t: 0, pos: [1.6, 1.45, -4.6], look: [0, 1.45, -9.0], fov: 34 }, { t: 2.5, pos: [1.3, 1.45, -5.2], look: [0, 1.5, -9.0], fov: 33 }],
    chars: {
      sib: [{ t: 0, p: [0, 0, -9.5], ry: 0, pose: 'idle' }, { t: 0.15, p: [0, 0, -9.5], ry: 0, pose: 'armsWide', ease: 'snap' },
        { t: 0.2, p: [0, 0, -9.5], ry: 0, pose: 'walkQuick', walk: true }, { t: 0.7, p: [0, 0, -8.75], ry: 0, pose: 'walkQuick' },
        { t: 0.95, p: [0, 0, -8.7], ry: 0, pose: 'armsWide', ease: 'back' }, { t: 1.5, p: [0, 0, -8.7], ry: 0, pose: 'armsWide' },
        { t: 1.85, p: [0, 0, -8.7], ry: -0.25, pose: 'shrug' }],
      crowdA: still([-5.2, 0, -3.8], 0.9, 'idle'),
    },
    door: doorKeys([[0, 0], [0.16, -1.95, 'snap'], [0.4, -1.75, 'out']]),
    portrait: { hcov: 0.7 },
  },
  S13: {
    cam: [{ t: 0, pos: [3.6, 1.55, -2.75], look: [5.15, 1.38, -0.5], fov: 38 }, { t: 2.5, pos: [3.85, 1.55, -2.45], look: [5.15, 1.4, -0.45], fov: 34 }],
    chars: {
      andile: [{ t: 0, p: [4.95, 0, -0.4], ry: Math.PI, pose: 'lookDoor' }, { t: 1.3, p: [4.95, 0, -0.4], ry: Math.PI, pose: 'lookDoor' },
        { t: 1.5, p: [4.95, 0, -0.4], ry: Math.PI, pose: 'catch', ease: 'snap' }, { t: 1.9, p: [4.95, 0, -0.4], ry: Math.PI, pose: 'catch' },
        { t: 2.4, p: [4.95, 0, -0.4], ry: Math.PI, pose: 'raiseGlass' }],
      futhi: [{ t: 0, p: [6.95, 0, -3.3], ry: -HP, pose: 'lean' }, { t: 0.2, p: [6.95, 0, -3.3], ry: -HP, pose: 'lean' },
        { t: 0.4, p: [6.95, 0, -3.3], ry: -HP, pose: 'slide', ease: 'snap' }, { t: 0.9, p: [6.95, 0, -3.3], ry: -HP, pose: 'slide' },
        { t: 1.4, p: [6.95, 0, -3.3], ry: -HP, pose: 'nodBack' }],
      ...crowd('idle'),
    },
    glass: (lt) => (lt < 0.4 ? [6.25, -3.4] : lt < 1.5 ? (() => { const u = EASE.out((lt - 0.4) / 1.1); return [lerp(6.25, 5.7, u), lerp(-3.4, -0.55, u)]; })() : 'hand'),
    portrait: { hcov: 0.75, back: 1.15 },
  },
  S14: {
    floorY: 0.16,
    cam: [{ t: 0, pos: [0.6, 1.3, 5.6], look: [0, 4.3, -6.4], fov: 40 }, { t: 4, pos: [0.4, 17, 10], look: [0, 20, -110], fov: 44, ease: 'inout' }],
    chars: { andile: [{ t: 0, p: [0.3, 0.16, -5.6], ry: HP, pose: 'walkPocket', walk: true }, { t: 4, p: [6.3, 0.16, -4.9], ry: HP, pose: 'walkPocket', walk: true }] },
    portrait: { hcov: 0.75 },
  },
};
