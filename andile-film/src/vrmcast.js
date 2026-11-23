// Anime cast from VRoid VRM models (MToon shader, rigged, spring-bone hair, face expressions),
// recoloured per character and driven by the same pose/keyframe system as the primitive rig.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';
import { resolvePose, JOINTS } from './rig.js';
import { lerp, EASE, clamp, hash1 } from './toon.js';

const SPEC = {
  andile: { file: 'C', skin: '#a8714e', hair: '#17110f', top: '#3d6b8f', bottom: '#25272e', shoes: '#23304f', scale: 1.05, seed: 1 },
  futhi: { file: 'B', skin: '#94603f', hair: '#1a1212', top: '#22305a', bottom: '#4a6fa5', shoes: '#2b2b33', scale: 1.0, seed: 2 },
  sib: { file: 'C', skin: '#8a5a3c', hair: '#15100e', top: '#1e1e26', bottom: '#1e1e26', shoes: '#f0f0f0', scale: 0.96, sx: 1.14, seed: 3 },
  thug: { file: 'C', skin: '#6e4632', hair: '#110d0c', top: '#9a2c2c', bottom: '#1d1d22', shoes: '#111111', scale: 1.16, sx: 1.28, seed: 4 },
  crowdA: { file: 'A', skin: '#7a4c34', hair: '#140f0d', top: '#b0306a', bottom: '#2a2a3a', shoes: '#222222', scale: 0.98, seed: 5 },
  crowdB: { file: 'C', skin: '#8b5a3e', hair: '#140f0d', top: '#2f8f8f', bottom: '#30303c', shoes: '#dddddd', scale: 1.0, seed: 6 },
  crowdC: { file: 'B', skin: '#6a4430', hair: '#140f0d', top: '#d9a030', bottom: '#2b2440', shoes: '#333333', scale: 0.97, seed: 7 },
};

const BONES = {
  hips: 'hips', spine: 'spine', chest: 'chest', neck: 'neck', head: 'head',
  shoulderL: 'leftUpperArm', elbowL: 'leftLowerArm', handL: 'leftHand',
  shoulderR: 'rightUpperArm', elbowR: 'rightLowerArm', handR: 'rightHand',
  hipL: 'leftUpperLeg', kneeL: 'leftLowerLeg', ankleL: 'leftFoot',
  hipR: 'rightUpperLeg', kneeR: 'rightLowerLeg', ankleR: 'rightFoot',
};
const Z = new THREE.Vector3(0, 0, 1);
// VRM0 normalized rigs face -Z (left arm along -X); poses are authored facing +Z, so mirror through Ry(pi).
const QD = { L: new THREE.Quaternion().setFromAxisAngle(Z, Math.PI / 2 * 0.97), R: new THREE.Quaternion().setFromAxisAngle(Z, -Math.PI / 2 * 0.97) };
const QDi = { L: QD.L.clone().invert(), R: QD.R.clone().invert() };

function tint(mat, hex, opts = {}) {
  const c = new THREE.Color(hex);
  if (opts.flat) { mat.map = null; mat.shadeMultiplyTexture = null; }
  if (mat.color) mat.color.copy(c).multiplyScalar(opts.gain ?? 1);
  if (mat.shadeColorFactor) mat.shadeColorFactor.copy(c).multiply(new THREE.Color(0.55, 0.45, 0.7));
  mat.needsUpdate = true;
}

function styleMaterial(mat, s) {
  const n = (mat.name || '').toLowerCase();
  if (mat.isMToonMaterial) {
    mat.shadingToonyFactor = 0.95;
    mat.shadingShiftFactor = -0.05;
    const eye = n.includes('eye') || n.includes('face') && !n.includes('skin');
    if (mat.parametricRimColorFactor) { if (eye) mat.parametricRimColorFactor.setRGB(0, 0, 0); else { mat.parametricRimColorFactor.setRGB(0.16, 0.16, 0.2); mat.parametricRimFresnelPowerFactor = 5.0; mat.parametricRimLiftFactor = 0.0; } }
    if (mat.emissive) mat.emissive.setRGB(0, 0, 0);
    if (mat.matcapFactor) mat.matcapFactor.setRGB(0, 0, 0);
    if (mat.isOutline || mat.outlineWidthMode !== undefined) { if (mat.outlineColorFactor) mat.outlineColorFactor.setRGB(0.08, 0.05, 0.1); }
  }
  if (n.includes('skin')) tint(mat, s.skin, { gain: 1.12 });
  else if (n.includes('hair')) tint(mat, s.hair, { gain: 2.2 });
  else if (n.includes('tops')) tint(mat, s.top, { flat: true });
  else if (n.includes('bottoms')) tint(mat, s.bottom, { flat: true });
  else if (n.includes('shoes')) tint(mat, s.shoes, { flat: true });
  else if (n.includes('facemouth')) tint(mat, s.skin, { gain: 1.25 });
  else if (n.includes('eyeiris')) tint(mat, '#7a4a28', { gain: 1.6 });
}

export async function loadVRMCast(scene, which) {
  const loader = new GLTFLoader();
  loader.register((p) => new VRMLoaderPlugin(p));
  const cast = {};
  for (const name of which) {
    const s = SPEC[name];
    const gltf = await loader.loadAsync(`./assets/vrm/AvatarSample_${s.file}.vrm`);
    const vrm = gltf.userData.vrm;
    VRMUtils.removeUnnecessaryVertices(gltf.scene);
    VRMUtils.rotateVRM0(vrm);
    vrm.scene.traverse((o) => {
      if (o.isMesh) {
        o.frustumCulled = false;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        mats.forEach((m) => styleMaterial(m, s));
      }
    });
    const root = new THREE.Group(); root.rotation.order = 'YXZ'; root.name = name;
    const body = new THREE.Group(); body.scale.set(s.scale * (s.sx || 1), s.scale, s.scale * (s.sx ? Math.sqrt(s.sx) : 1));
    body.add(vrm.scene); root.add(body); scene.add(root);
    const blob = new THREE.Mesh(new THREE.CircleGeometry(0.34 * s.scale * (s.sx || 1), 24),
      new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.42, depthWrite: false }));
    blob.rotation.x = -Math.PI / 2; blob.renderOrder = 1; scene.add(blob);
    const hipsNode = vrm.humanoid.getNormalizedBoneNode('hips');
    const raw = (b) => vrm.humanoid.getRawBoneNode(b);
    cast[name] = {
      name, vrm, root, body, blob, seed: s.seed, isVRM: true, brow: 0.1, spec: s,
      hipsY: hipsNode.position.y, J: { handR: raw('rightHand'), handL: raw('leftHand'), head: raw('head') },
    };
  }
  return cast;
}

const q = new THREE.Quaternion(), qe = new THREE.Quaternion(), eu = new THREE.Euler();
function applyVRMPose(c, p, tg) {
  const h = c.vrm.humanoid;
  for (const j of JOINTS) {
    const node = h.getNormalizedBoneNode(BONES[j]);
    if (!node) continue;
    const r = p[j] || [0, 0, 0];
    eu.set(-r[0], r[1], -r[2], 'XYZ'); qe.setFromEuler(eu);
    if (j === 'shoulderL' || j === 'shoulderR') { const k = j.slice(-1); node.quaternion.copy(qe).multiply(QD[k]); }
    else if (j === 'elbowL' || j === 'elbowR' || j === 'handL' || j === 'handR') { const k = j.slice(-1); node.quaternion.copy(QDi[k]).multiply(qe).multiply(QD[k]); }
    else node.quaternion.copy(qe);
  }
  const ch = h.getNormalizedBoneNode('chest');
  if (ch) ch.rotation.x -= 0.015 * Math.sin(tg * 2.3 + c.seed);
  // finger curl: fists in fighting poses, relaxed otherwise
  const curl = p.fist ?? ((p.brow ?? 0) > 0.3 ? 1.25 : 0.4);
  for (const side of ['left', 'right']) {
    const sg = side === 'left' ? 1 : -1;
    for (const f of ['Index', 'Middle', 'Ring', 'Little']) for (const seg of ['Proximal', 'Intermediate', 'Distal']) {
      const nd = h.getNormalizedBoneNode(side + f + seg); if (nd) nd.rotation.set(0, 0, sg * curl * (seg === 'Proximal' ? 0.9 : 1.1));
    }
    for (const seg of ['Proximal', 'Intermediate', 'Distal']) { const nd = h.getNormalizedBoneNode(side + 'Thumb' + seg); if (nd) nd.rotation.set(0, 0, sg * curl * 0.25); }
  }
  const hips = h.getNormalizedBoneNode('hips');
  hips.position.y = c.hipsY + (p.hy || 0) * (c.hipsY / 0.99);
  // face: expressions from the pose's brow/mouth channels + deterministic blinks
  const em = c.vrm.expressionManager;
  if (em) {
    const brow = p.brow ?? 0.1, mouth = p.mouth ?? 1;
    em.setValue('angry', clamp((brow - 0.18) * 3.2));
    em.setValue('happy', clamp((-brow - 0.08) * 3) * (mouth > 1.6 ? 0 : 1));
    em.setValue('aa', clamp((mouth - 1.2) / 2));
    em.setValue('surprised', clamp((mouth - 2.5) / 1.5) * (brow < 0 ? 1 : 0));
    const per = 3.1 + hash1(c.seed) * 1.4, ph = ((tg + c.seed * 0.77) % per) / per * per;
    em.setValue('blink', ph < 0.12 ? Math.sin((ph / 0.12) * Math.PI) : 0);
  }
}

function placeAt(c, keys, at, ctx) {
  let a = keys[0], b = keys[0], u = 0;
  if (at >= keys[keys.length - 1].t) a = b = keys[keys.length - 1];
  else if (at > keys[0].t) for (let i = 0; i < keys.length - 1; i++) if (at >= keys[i].t && at < keys[i + 1].t) { a = keys[i]; b = keys[i + 1]; u = (at - a.t) / (b.t - a.t); break; }
  const e = EASE[b.ease || 'inout'](u), pu = a.walk ? u : e;
  const pos = [lerp(a.p[0], b.p[0], pu), lerp(a.p[1], b.p[1], pu), lerp(a.p[2], b.p[2], pu)];
  if (b.arc && a !== b) pos[1] += 4 * b.arc * u * (1 - u);
  c.root.position.set(pos[0], pos[1], pos[2]);
  c.root.rotation.set(lerp(a.rx ?? 0, b.rx ?? 0, e), lerp(a.ry ?? 0, b.ry ?? 0, e), 0);
  const pa = resolvePose(a.pose, c, ctx), pb = a === b ? pa : resolvePose(b.pose, c, ctx);
  const w = a.walk ? 0 : e, pose = {};
  for (const n of JOINTS) { const x = pa[n] || [0, 0, 0], y = pb[n] || [0, 0, 0]; pose[n] = [lerp(x[0], y[0], w), lerp(x[1], y[1], w), lerp(x[2], y[2], w)]; }
  for (const k of ['hy', 'brow', 'mouth']) { const x = pa[k], y = pb[k]; if (x !== undefined || y !== undefined) pose[k] = lerp(x ?? y, y ?? x, w); }
  applyVRMPose(c, pose, ctx.tg);
  return pos;
}

// Deterministic evaluation incl. spring-bone hair: re-simulate the last 0.8 s of the shot at 60 Hz.
export function evalVRM(c, keys, ctx, shotStart, t, remapFn) {
  const t0 = Math.max(shotStart, t - 0.8), dt = 1 / 60;
  c.vrm.springBoneManager?.reset();
  let tt = t0;
  for (; tt < t - 1e-6; tt += dt) {
    placeAt(c, keys, remapFn(tt - shotStart), { ...ctx, tg: tt });
    c.vrm.update(Math.min(dt, t - tt));
  }
  const pos = placeAt(c, keys, remapFn(t - shotStart), { ...ctx, tg: t });
  c.vrm.update(0);
  const lying = Math.abs(c.root.rotation.x) > 0.8, hgt = Math.max(0, pos[1] - (ctx.floorY ?? 0) - (lying ? 0.15 : 0));
  c.blob.position.set(pos[0] - (lying ? Math.sin(c.root.rotation.y) * 0.8 : 0), (ctx.floorY ?? 0) + 0.012, pos[2] - (lying ? Math.cos(c.root.rotation.y) * 0.8 : 0));
  const k = 1 / (1 + hgt * 1.4);
  c.blob.scale.set(lying ? 1.6 : k, lying ? 2.6 : k, 1); c.blob.rotation.z = lying ? c.root.rotation.y : 0;
  c.blob.material.opacity = 0.42 * k;
}
