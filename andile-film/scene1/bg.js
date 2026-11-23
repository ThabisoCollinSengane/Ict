// Background plates for Scene 1 ("Bad Dream"): a Durban call centre, nightmare and daytime versions.
// renderAt(frame) draws plate `shot` (URL param) at local frame `frame`. Deterministic: no clocks, seeded noise.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { toon, glow, rng, hash1, windowTextures, clamp, lerp, EASE } from '../src/toon.js';

const q = new URLSearchParams(location.search);
const W = +(q.get('w') || 1920), H = +(q.get('h') || 1080), SHOT = q.get('shot') || 'N1';
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('c'), antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, W / H, 0.05, 900);
const C = (c) => new THREE.Color(c);

const ROW = 3.0;
function office(mode) {
  const night = mode === 'night';
  const g = new THREE.Group(); scene.add(g);
  const rows = night ? 70 : 9;
  const r = rng(night ? 11 : 5);
  const fabric = toon(night ? '#2a1a26' : '#5d7088'), top = toon(night ? '#1c1418' : '#d9d4cc'), metal = toon(night ? '#1a1216' : '#3a3f4a');
  const chairM = toon(night ? '#120c10' : '#23262e'), bezel = toon('#16161c');
  const screens = [], phones = [], lamps = [];
  const add = (geo, mat, x, y, z, ry = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.rotation.y = ry; g.add(m); return m; };
  const desk = new THREE.BoxGeometry(1.6, 0.05, 0.8), part = new THREE.BoxGeometry(1.62, 1.25, 0.05), side = new THREE.BoxGeometry(0.05, 1.25, 0.82);
  const mon = new THREE.BoxGeometry(0.58, 0.36, 0.04), scr = new THREE.PlaneGeometry(0.52, 0.3), stand = new THREE.BoxGeometry(0.06, 0.18, 0.06);
  const seat = new THREE.BoxGeometry(0.5, 0.08, 0.5), back = new THREE.BoxGeometry(0.5, 0.55, 0.06), phone = new THREE.BoxGeometry(0.2, 0.06, 0.16), led = new THREE.BoxGeometry(0.04, 0.02, 0.04);
  for (let k = 0; k < rows; k++) {
    const z = -1.6 - k * ROW;
    for (const x of [-3.7, -2.0, 2.0, 3.7]) {
      add(desk, top, x, 0.74, z); add(part, fabric, x, 0.62 + 0.0, z - 0.42); add(side, fabric, x + (x < 0 ? -0.82 : 0.82), 0.62, z);
      add(new THREE.BoxGeometry(0.05, 0.72, 0.05), metal, x - 0.7, 0.36, z + 0.3); add(new THREE.BoxGeometry(0.05, 0.72, 0.05), metal, x + 0.7, 0.36, z + 0.3);
      const mx = x + (r() - 0.5) * 0.2;
      add(mon, bezel, mx, 1.05, z - 0.22); add(stand, bezel, mx, 0.85, z - 0.24);
      const sc = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const s = add(scr, sc, mx, 1.05, z - 0.199); screens.push({ m: sc, k, x, seed: r() * 100 });
      add(phone, bezel, x + 0.5, 0.79, z - 0.05);
      const lm = new THREE.MeshBasicMaterial({ color: 0x000000 }); add(led, lm, x + 0.5, 0.83, z - 0.1); phones.push({ m: lm, seed: r() * 100, k });
      const ch = new THREE.Group(); ch.position.set(x + (r() - 0.5) * 0.3, 0, z + 0.62); ch.rotation.y = (r() - 0.5) * 0.6; g.add(ch);
      const s1 = new THREE.Mesh(seat, chairM); s1.position.y = 0.48; ch.add(s1);
      const s2 = new THREE.Mesh(back, chairM); s2.position.set(0, 0.82, 0.24); ch.add(s2);
      const s3 = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.44, 6), metal); s3.position.y = 0.22; ch.add(s3);
    }
    for (const x of [-2.85, 2.85]) {
      const lm = new THREE.MeshBasicMaterial({ color: 0xffffff });
      add(new THREE.BoxGeometry(1.2, 0.03, 0.6), lm, x, 2.98, z); lamps.push({ m: lm, k, seed: r() * 100 });
    }
  }
  const len = rows * ROW + 4;
  const floor = add(new THREE.PlaneGeometry(14, len + 10), toon(night ? '#0e0a0d' : '#3e4b5c', { steps: 2 }), 0, 0, -len / 2 + 2); floor.rotation.x = -Math.PI / 2;
  const aisle = add(new THREE.PlaneGeometry(2.0, len + 10), toon(night ? '#1a0e12' : '#55657a', { steps: 2 }), 0, 0.005, -len / 2 + 2); aisle.rotation.x = -Math.PI / 2;
  const ceil = add(new THREE.PlaneGeometry(14, len + 10), toon(night ? '#07050a' : '#c9cdd4', { steps: 2 }), 0, 3.0, -len / 2 + 2); ceil.rotation.x = Math.PI / 2;
  for (let k = 0; k < rows; k += 1) { const t = add(new THREE.BoxGeometry(14, 0.02, 0.03), toon(night ? '#140d12' : '#aab0ba'), 0, 2.99, -0.1 - k * ROW); }
  if (!night) {
    // left wall with notice boards, right wall of windows onto Durban (Moses Mabhida arch)
    add(new THREE.BoxGeometry(0.2, 3, len + 10), toon('#cfc8bc'), -5.3, 1.5, -len / 2 + 2);
    for (let k = 0; k < rows; k += 2) {
      add(new THREE.BoxGeometry(0.03, 0.8, 1.2), toon('#2f5f8a'), -5.18, 1.7, -2 - k * ROW);
      add(new THREE.BoxGeometry(0.035, 0.5, 0.8), toon('#e9e4da'), -5.17, 1.75, -2 - k * ROW);
    }
    add(new THREE.BoxGeometry(14, 3, 0.2), toon('#cfc8bc'), 0, 1.5, -len + 1.5);
    add(new THREE.BoxGeometry(0.2, 0.7, len + 10), toon('#bdb6aa'), 5.3, 0.35, -len / 2 + 2);
    add(new THREE.BoxGeometry(0.2, 0.25, len + 10), toon('#bdb6aa'), 5.3, 2.9, -len / 2 + 2);
    for (let z = 1; z > -len; z -= 2.4) add(new THREE.BoxGeometry(0.16, 2.1, 0.12), toon('#4a5260'), 5.3, 1.75, z);
    const sky = new THREE.Mesh(new THREE.PlaneGeometry(400, 160), new THREE.ShaderMaterial({
      uniforms: { a: { value: C('#d6eefc') }, b: { value: C('#5aa8ea') } }, depthWrite: false,
      vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
      fragmentShader: 'uniform vec3 a,b; varying vec2 vUv; void main(){ gl_FragColor = vec4(mix(a, b, smoothstep(0.35, 1.0, vUv.y)), 1.0); }',
    }));
    sky.position.set(150, 30, -40); sky.rotation.y = -Math.PI / 2; sky.userData.noInk = true; g.add(sky);
    for (let i = 0; i < 26; i++) {
      const hgt = 8 + r() * 40, w = 6 + r() * 10, z = 30 - i * 6 - r() * 3, x = 70 + r() * 40;
      const tx = windowTextures(300 + i, { facade: '#e8eef6', win: '#8aa6c4', lit: 0 }); tx.map.repeat.set(w / 6, hgt / 10);
      add(new THREE.BoxGeometry(w, hgt, w), new THREE.MeshToonMaterial({ color: C(['#d7dee8', '#c6d0de', '#e6e2da'][i % 3]), map: tx.map }), x, hgt / 2 - 6, z);
    }
    const arch = new THREE.Mesh(new THREE.TorusGeometry(34, 0.9, 8, 48, Math.PI), toon('#f4f4f2')); arch.position.set(95, -6, -55); arch.rotation.set(0, Math.PI / 2 - 0.35, 0); g.add(arch);
    const bowl = new THREE.Mesh(new THREE.CylinderGeometry(26, 30, 12, 32, 1, true), toon('#e8e6e0')); bowl.position.set(95, -2, -55); g.add(bowl);
    const ocean = add(new THREE.PlaneGeometry(400, 200), toon('#2f8fc2', { steps: 2 }), 200, -6, -40); ocean.rotation.x = -Math.PI / 2;
  }
  const lights = new THREE.Group(); g.add(lights);
  if (night) {
    lights.add(new THREE.HemisphereLight('#5a1020', '#05020a', 0.7));
    const red = new THREE.PointLight('#ff2030', 30, 26, 1.6); red.position.set(0, 2.6, -8); lights.add(red); g.userData.red = red;
    const d = new THREE.DirectionalLight('#ff6060', 0.5); d.position.set(2, 6, 5); lights.add(d);
  } else {
    lights.add(new THREE.HemisphereLight('#e8f2ff', '#5a5a62', 1.25));
    const sun = new THREE.DirectionalLight('#fff1d8', 1.6); sun.position.set(10, 8, 2); lights.add(sun);
  }
  return { g, screens, phones, lamps, night,
    fog: night ? new THREE.Fog('#0b0306', 4, 55) : new THREE.Fog('#dfe8f0', 30, 140),
    update(f) {
      for (const s of screens) {
        if (night) {
          const fl = hash1(Math.floor(f / 3) + s.seed) < 0.12 ? 0.25 : 1;
          const pulse = 0.75 + 0.25 * Math.sin(f * 0.21 + s.seed);
          s.m.color.setRGB(2.2 * pulse * fl, 0.12 * fl, 0.16 * fl);
        } else s.m.color.setRGB(0.55, 0.85, 1.05);
      }
      for (const p of phones) {
        const on = night ? (Math.floor(f / 6 + p.seed) % 2 === 0) : (Math.floor(f / 15 + p.seed) % 7 === 0);
        p.m.color.setRGB(on ? 3 : 0.1, on ? 0.15 : 0.02, on ? 0.1 : 0.02);
      }
      for (const l of lamps) {
        if (night) { const on = hash1(l.seed + Math.floor(f / 4)) < 0.18; l.m.color.setRGB(on ? 1.8 : 0.03, on ? 0.2 : 0.01, on ? 0.25 : 0.01); }
        else l.m.color.setRGB(1.6, 1.6, 1.55);
      }
      if (night && g.userData.red) g.userData.red.intensity = 26 + 10 * Math.sin(f * 0.15);
    } };
}
const sets = { night: office('night'), day: office('day') };

// ---- shots: camera per local frame ----
const SH = {
  N1: { set: 'night', cam: (f) => ({ pos: [0, 1.55, 3 - 0.09 * f], look: [0, 1.35, -80], fov: 48 }) },
  N2: { set: 'night', cam: () => ({ pos: [0.6, 1.25, 0.6], look: [-3.2, 1.1, -7], fov: 45 }) },
  N3: { set: 'night', cam: () => ({ pos: [0, 1.1, 2], look: [0, 2.0, -90], fov: 40 }) },
  N4: { set: 'night', cam: (f) => { const u = EASE.inout(clamp(f / 119)); const d = lerp(12, 2.0, u); const fov = 2 * Math.atan(4.23 / (2 * d)) * 180 / Math.PI; return { pos: [0, 1.45, -6 + d], look: [0, 1.4, -6], fov }; } },
  W1: { set: 'day', cam: () => ({ pos: [-2.0, 1.0, -0.2], look: [-1.6, 2.5, -3.2], fov: 62 }) },
  W2: { set: 'day', cam: () => ({ pos: [-1.0, 1.4, 1.5], look: [4.5, 1.3, -3.0], fov: 46 }) },
  W3: { set: 'day', cam: () => ({ pos: [-0.5, 1.45, 0.5], look: [4.5, 1.5, -2.0], fov: 34 }) },
};

// ---- post: ink lines from normals/depth + bloom ----
const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 }));
composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
const nrt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType });
const ndMat = new THREE.ShaderMaterial({
  vertexShader: `#include <common>
    varying vec3 vNn; varying float vD;
    void main(){
      #include <beginnormal_vertex>
      #include <defaultnormal_vertex>
      #include <begin_vertex>
      #include <project_vertex>
      vNn = normalize(transformedNormal); vD = -mvPosition.z; }`,
  fragmentShader: `varying vec3 vNn; varying float vD; void main(){ gl_FragColor = vec4(normalize(vNn) * 0.5 + 0.5, log2(1.0 + max(vD, 0.0)) / log2(901.0)); }`,
});
const ink = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, tND: { value: null }, uRes: { value: new THREE.Vector2(W, H) }, uInkCol: { value: new THREE.Color(0.1, 0.07, 0.12) } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: `uniform sampler2D tDiffuse, tND; uniform vec2 uRes; uniform vec3 uInkCol; varying vec2 vUv;
    vec4 ND(vec2 o){ return texture2D(tND, vUv + o / uRes); }
    void main(){
      vec4 c0 = ND(vec2(0.0)); float dep = c0.a; vec3 col = texture2D(tDiffuse, vUv).rgb;
      vec4 a = ND(vec2(1.0, 0.0)), b = ND(vec2(-1.0, 0.0)), c = ND(vec2(0.0, 1.0)), d = ND(vec2(0.0, -1.0));
      float dd = max(max(abs(a.a - dep), abs(b.a - dep)), max(abs(c.a - dep), abs(d.a - dep)));
      vec3 n0 = c0.rgb * 2.0 - 1.0;
      float nd = 1.0 - min(min(dot(n0, a.rgb * 2.0 - 1.0), dot(n0, b.rgb * 2.0 - 1.0)), min(dot(n0, c.rgb * 2.0 - 1.0), dot(n0, d.rgb * 2.0 - 1.0)));
      float e = max(smoothstep(0.012, 0.03, dd), smoothstep(0.22, 0.45, nd) * step(dep, 0.999)) * (1.0 - smoothstep(0.55, 0.8, dep));
      gl_FragColor = vec4(mix(col, col * uInkCol, e * 0.85), 1.0);
    }`,
});
ink.uniforms.tND.value = nrt.texture;
composer.addPass(ink);
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.7, 0.5, 1.0); composer.addPass(bloom);
composer.addPass(new OutputPass());
const inkHide = [];
scene.traverse((o) => { const m = o.material; if (o.userData.noInk || (m && (m.transparent || (m.isShaderMaterial && !m.uniforms?.uColor)))) inkHide.push(o); });

window.renderAt = (frame) => {
  const sh = SH[SHOT]; const S = sets[sh.set];
  for (const k in sets) sets[k].g.visible = k === sh.set;
  scene.fog = S.fog; scene.background = new THREE.Color(sh.set === 'night' ? '#0b0306' : '#dfe8f0');
  bloom.strength = sh.set === 'night' ? 0.9 : 0.35;
  S.update(frame + (SHOT === 'N4' ? 200 : SHOT === 'N2' ? 100 : 0));
  const c = sh.cam(frame);
  camera.position.set(...c.pos); camera.lookAt(new THREE.Vector3(...c.look)); camera.fov = c.fov; camera.updateProjectionMatrix();
  for (const o of inkHide) { o.userData._v = o.visible; o.visible = false; }
  const bg = scene.background; scene.background = null; scene.overrideMaterial = ndMat;
  renderer.setRenderTarget(nrt); renderer.setClearColor(0x8080ff, 1); renderer.clear(); renderer.render(scene, camera);
  renderer.setRenderTarget(null); renderer.setClearColor(0x000000, 1); scene.overrideMaterial = null; scene.background = bg;
  for (const o of inkHide) o.visible = o.userData._v;
  composer.render();
};
window.renderAt(0);
window.READY = true;
