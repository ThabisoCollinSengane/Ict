import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { buildSets } from './sets.js';
import { makeCharacter, evalChar, CAST } from './rig.js';
import { SHOTS } from './shots.js';
import { EASE, clamp, lerp, CEL } from './toon.js';

const q = new URLSearchParams(location.search);
const W = +(q.get('w') || 1280), H = +(q.get('h') || 720), portrait = H > W;
document.documentElement.style.setProperty('--u', Math.min(W, H) / 100 + 'px');
document.body.classList.toggle('portrait', portrait);
const TL = await (await fetch('./timeline.json')).json();

const canvas = document.getElementById('c');
canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, W / H, 0.05, 2500);
const sets = buildSets(scene);
const cast = {};
for (const k in CAST) cast[k] = makeCharacter(CAST[k], scene);

const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
const composer = new EffectComposer(renderer, rt);
composer.setPixelRatio(1); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.8, 0.45, 1.0);
composer.addPass(bloom);
composer.addPass(new OutputPass());
const fin = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, uFrame: { value: 0 }, uFlash: { value: 0 }, uInv: { value: 0 }, uSpeed: { value: 0 },
    uSpeedC: { value: new THREE.Vector2(0.5, 0.5) }, uLetter: { value: portrait ? 0 : 0.055 }, uAspect: { value: W / H },
    uFade: { value: 0 }, uChroma: { value: 0 }, uRes: { value: new THREE.Vector2(W, H) } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float uFrame,uFlash,uInv,uSpeed,uLetter,uAspect,uFade,uChroma; uniform vec2 uSpeedC,uRes; varying vec2 vUv;
    float hs(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
    void main(){
      vec2 uv = vUv; vec3 c;
      if (uChroma > 0.0) { vec2 d = (uv - 0.5) * uChroma * 0.014; c = vec3(texture2D(tDiffuse, uv + d).r, texture2D(tDiffuse, uv).g, texture2D(tDiffuse, uv - d).b); }
      else c = texture2D(tDiffuse, uv).rgb;
      float l = dot(c, vec3(0.299, 0.587, 0.114));
      c = mix(vec3(l), c, 1.12);
      c += vec3(0.014, 0.0, 0.03) * (1.0 - l);
      if (uSpeed > 0.0) {
        vec2 p = uv - uSpeedC; p.x *= uAspect; float ang = atan(p.y, p.x); float r = length(p);
        float s = step(0.7, hs(vec2(floor(ang * 70.0), floor(uFrame * 0.5))));
        float m = s * smoothstep(0.16, 0.6, r) * uSpeed;
        c = mix(c, vec3(1.0, 0.98, 0.96), m * 0.8);
      }
      if (uInv > 0.5) { float k = step(0.36, l); c = mix(vec3(0.97, 0.95, 1.0), vec3(0.06, 0.03, 0.08), k); }
      vec2 qv = uv - 0.5; qv.x *= uAspect * 0.75;
      c *= 1.0 - 0.42 * smoothstep(0.35, 0.95, length(qv) * 1.25);
      c += (hs(uv * uRes + uFrame * 13.17) - 0.5) * 0.04;
      c = mix(c, vec3(1.0, 0.97, 0.95), uFlash);
      c = mix(c, vec3(0.0), uFade);
      if (uv.y < uLetter || uv.y > 1.0 - uLetter) c = vec3(0.0);
      gl_FragColor = vec4(c, 1.0);
    }`,
});
composer.addPass(fin);

const shotAt = (t) => { let s = TL.shots[0]; for (const x of TL.shots) if (t >= x.start - 1e-6) s = x; return s; };
const period = (name, tg) => { for (const w of TL.walks) if (w.char === name && tg >= w.t0 - 0.6 && tg <= w.t1 + 1.6) return w.period; return 1.0; };
function remap(r, lt) {
  for (let i = 0; i < r.length - 1; i++) if (lt <= r[i + 1][0]) return lerp(r[i][1], r[i + 1][1], clamp((lt - r[i][0]) / (r[i + 1][0] - r[i][0])));
  const a = r[r.length - 2], b = r[r.length - 1]; return b[1] + (lt - b[0]) * (b[1] - a[1]) / (b[0] - a[0]);
}
function evalCam(keys, lt) {
  let a = keys[0], b = keys[0], u = 0;
  if (lt >= keys[keys.length - 1].t) a = b = keys[keys.length - 1];
  else if (lt > keys[0].t) for (let i = 0; i < keys.length - 1; i++) if (lt >= keys[i].t && lt < keys[i + 1].t) { a = keys[i]; b = keys[i + 1]; u = (lt - a.t) / (b.t - a.t); break; }
  const e = EASE[b.ease || 'inout'](u);
  const L3 = (x, y) => [lerp(x[0], y[0], e), lerp(x[1], y[1], e), lerp(x[2], y[2], e)];
  return { pos: L3(a.pos, b.pos), look: L3(a.look, b.look), fov: lerp(a.fov, b.fov, e), roll: lerp(a.roll || 0, b.roll || 0, e), up: a.up && b.up ? L3(a.up, b.up) : a.up || b.up };
}
function fxAt(t) {
  let flash = 0, inv = 0, shake = 0, chroma = 0;
  for (const c of TL.cues) {
    if (c.type !== 'impact' && c.type !== 'land') continue;
    const d = t - c.t, s = c.s || 1;
    if (d < 0 || d > 0.6) continue;
    if (c.type === 'impact') {
      if (d < 1 / TL.fps - 1e-6) inv = 1;
      else flash = Math.max(flash, 0.75 * s * Math.max(0, 1 - (d - 1 / TL.fps) / 0.16));
      chroma = Math.max(chroma, s * Math.max(0, 1 - d / 0.35));
    } else flash = Math.max(flash, 0.25 * Math.max(0, 1 - d / 0.12));
    shake = Math.max(shake, s * Math.pow(Math.max(0, 1 - d / 0.45), 2));
  }
  return { flash, inv, shake, chroma };
}

const els = { kicker: document.getElementById('kicker'), name: document.getElementById('name'), sub: document.getElementById('sub'), title: document.getElementById('title') };
function overlays(t) {
  const act = {};
  for (const x of TL.texts) if (t >= x.t0 && t <= x.t1) act[x.el] = x;
  for (const k in els) {
    const x = act[k], el = els[k];
    if (!x) { el.style.opacity = 0; continue; }
    const a = clamp((t - x.t0) / 0.25) * clamp((x.t1 - t) / 0.25);
    el.style.opacity = a;
    if (k === 'kicker') { el.textContent = x.text; el.style.transform = `translateY(${(1 - a) * 12}px)`; }
    if (k === 'name') { el.querySelector('.nm').textContent = x.text; el.querySelector('.role').textContent = x.sub; el.style.transform = `translateX(${(1 - EASE.out(clamp((t - x.t0) / 0.35))) * -60}px) skewX(-8deg)`; }
    if (k === 'sub') { el.querySelector('.l1').textContent = x.text; el.querySelector('.l2').textContent = x.sub; }
    if (k === 'title') {
      const u = EASE.out(clamp((t - x.t0) / 1.4));
      el.querySelector('.t1').textContent = x.text; el.querySelector('.t2').textContent = x.sub;
      el.querySelector('.t1').style.letterSpacing = lerp(portrait ? 0.5 : 1.1, portrait ? 0.16 : 0.42, u) + 'em';
      el.querySelector('.rule').style.width = (u * 100) + '%';
      el.style.opacity = clamp((t - x.t0) / 0.5);
    }
  }
}

const tmp = new THREE.Vector3();
window.renderAt = (frame) => {
  const t = frame / TL.fps;
  const shot = shotAt(t), def = SHOTS[shot.id], lt = t - shot.start;
  const at = def.remap ? remap(def.remap, lt) : lt;
  for (const k in sets) sets[k].group.visible = k === shot.set;
  const S = sets[shot.set];
  scene.fog = S.fog; scene.background = S.bg; bloom.strength = S.bloom;
  const cc = { ...((shot.set === 'club' && t >= 14 && t < 21 && S.celFight) || S.cel), ...(def.cel || {}) };
  CEL.uLightDir.value.set(...cc.dir).normalize(); CEL.uShadeTint.value.setRGB(...cc.shade);
  CEL.uRim.value.setRGB(...cc.rim); CEL.uRimDir.value.set(...cc.rimDir).normalize(); CEL.uRimAmt.value = cc.rimAmt;

  // characters
  const ctx = { tg: t, period, bpm: TL.bpm, floorY: def.floorY || 0 };
  for (const k in cast) {
    const c = cast[k], tr = def.chars[k];
    c.root.visible = c.blob.visible = !!tr;
    if (tr) evalChar(c, tr, at, ctx);
  }

  // camera
  const cs = def.camFn ? def.camFn(lt) : evalCam(def.cam, lt);
  const pos = new THREE.Vector3(...cs.pos), look = new THREE.Vector3(...cs.look);
  let fov = cs.fov;
  if (def.track) {
    const k = def.track, c = cast[k.char].root.position;
    const w = (k.w ?? 1) * EASE.inout(clamp((lt - k.t0) / k.ramp));
    look.lerp(new THREE.Vector3(c.x + k.off[0], c.y + k.off[1], c.z + k.off[2]), w);
  }
  if (portrait) {
    const pr = def.portrait || {}, hcov = pr.hcov ?? 0.65, back = pr.back ?? 1;
    const fh = 2 * Math.atan(Math.tan(fov * Math.PI / 360) * 16 / 9) * hcov;
    fov = Math.min(95, 2 * Math.atan(Math.tan(fh / 2) * H / W) * 180 / Math.PI);
    if (back !== 1) pos.sub(look).multiplyScalar(back).add(look);
  }
  const fx = fxAt(t);
  if (fx.shake > 0) {
    const s = fx.shake;
    pos.x += s * 0.09 * Math.sin(t * 91.0); pos.y += s * 0.07 * Math.sin(t * 113.0 + 1.3); pos.z += s * 0.05 * Math.sin(t * 71.0 + 2.1);
    look.x += s * 0.05 * Math.sin(t * 97.0 + 0.5); look.y += s * 0.05 * Math.sin(t * 83.0 + 2.2);
  }
  camera.position.copy(pos);
  camera.up.set(...(cs.up || [0, 1, 0])).normalize();
  camera.lookAt(look);
  if (cs.roll) camera.rotateZ(cs.roll);
  camera.fov = fov; camera.updateProjectionMatrix();

  // props
  const club = sets.club;
  const ang = def.door ? def.door(lt) : t >= 21 ? -1.75 : 0;
  club.door.rotation.y = ang;
  const op = clamp(Math.abs(ang) / 1.75);
  club.doorway.material.color.setRGB(0.22 + 0.95 * op, 0.13 + 0.62 * op, 0.09 + 0.32 * op);
  club.doorLight.intensity = 9 * op;
  if (def.glass) {
    const v = def.glass(at);
    if (v === 'hand') { cast.andile.root.updateMatrixWorld(true); cast.andile.J.handR.getWorldPosition(tmp); club.glass.position.set(tmp.x, tmp.y - 0.11, tmp.z); }
    else club.glass.position.set(v[0], 1.18, v[1]);
  } else club.glass.position.set(6.25, 1.18, -3.4);

  TL.noCones = !!def.noCones;
  S.update(t, camera, TL);

  // post
  fin.uniforms.uFrame.value = frame;
  fin.uniforms.uFlash.value = fx.flash; fin.uniforms.uInv.value = fx.inv; fin.uniforms.uChroma.value = fx.chroma;
  let sp = 0;
  for (const s of TL.speedLines) if (t >= s.t0 && t <= s.t1) {
    sp = (s.s || 1) * (1 - (t - s.t0) / (s.t1 - s.t0));
    tmp.set(...s.at).project(camera); fin.uniforms.uSpeedC.value.set(tmp.x * 0.5 + 0.5, tmp.y * 0.5 + 0.5);
  }
  fin.uniforms.uSpeed.value = sp;
  let fade = 0;
  for (const f of TL.fades) if (t >= f.t0 && t <= f.t1) fade = lerp(f.from, f.to, (t - f.t0) / (f.t1 - f.t0));
  fin.uniforms.uFade.value = fade;
  overlays(t);
  composer.render();
  return shot.id;
};

// warm up every set so shader compiles don't land inside timed frames
for (const f of [0, 80, 200, 400]) window.renderAt(f);
window.READY = true;
