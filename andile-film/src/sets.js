import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { toon, glow, outline, rng, hash1, textTexture, windowTextures, clamp } from './toon.js';

const C = (c) => new THREE.Color(c);
const V = (x, y, z) => new THREE.Vector3(x, y, z);

function add(g, geo, mat, p, rot, ol) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(p[0], p[1], p[2]);
  if (rot) m.rotation.set(rot[0], rot[1], rot[2]);
  g.add(m);
  if (ol) outline(m, ol);
  return m;
}

function skyDome(cols, sun, opts = {}) {
  return new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { uSun: { value: sun }, cH: { value: C(cols[0]) }, cP: { value: C(cols[1]) }, cV: { value: C(cols[2]) }, cT: { value: C(cols[3]) },
      cSun: { value: new THREE.Color(...(opts.sunCol || [3.0, 2.2, 1.3])) }, uSunAmt: { value: opts.sunAmt ?? 1 }, uStars: { value: opts.stars ?? 0 } },
    vertexShader: `varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 uSun,cH,cP,cV,cT,cSun; uniform float uSunAmt,uStars; varying vec3 vDir;
      float h(vec3 p){ return fract(sin(dot(p, vec3(12.9898,78.233,37.719)))*43758.5453); }
      void main(){ vec3 d = normalize(vDir); float y = d.y;
        vec3 c = cH;
        c = mix(c, cP, smoothstep(0.02, 0.16, y));
        c = mix(c, cV, smoothstep(0.14, 0.40, y));
        c = mix(c, cT, smoothstep(0.36, 0.88, y));
        float s = max(dot(d, uSun), 0.0);
        c += uSunAmt * (cSun * 0.32 * pow(s, 14.0) + cSun * 0.55 * pow(s, 160.0));
        if (s > 0.9994) c = mix(c, cSun, uSunAmt);
        if (uStars > 0.0 && y > 0.15) { vec3 q = floor(d * 380.0); float st = h(q); if (st > 0.9975) c += vec3(0.9,0.9,1.0) * uStars * (st - 0.9975) * 400.0; }
        gl_FragColor = vec4(c, 1.0); }`,
  }));
}

function palm(g, x, z, hgt, lean, matT, matF, ol) {
  const grp = new THREE.Group(); grp.position.set(x, 0, z); g.add(grp);
  const segs = 6; let px = 0, py = 0;
  for (let i = 0; i < segs; i++) {
    const seg = new THREE.Mesh(new THREE.CylinderGeometry(0.16 - i * 0.012, 0.2 - i * 0.012, hgt / segs + 0.05, 8), matT);
    const nx = px + lean * (i / segs) * 0.35; seg.position.set(nx, py + hgt / segs / 2, 0); seg.rotation.z = -lean * 0.12;
    grp.add(seg); if (ol) outline(seg, ol); px = nx; py += hgt / segs;
  }
  for (let k = 0; k < 8; k++) {
    const f = new THREE.Mesh(new THREE.ConeGeometry(0.42, 3.4, 5), matF);
    f.geometry.translate(0, 1.7, 0);
    f.scale.set(1, 1, 0.18);
    f.position.set(px, py, 0);
    f.rotation.set(0, (k / 8) * Math.PI * 2, 1.85 + (k % 2) * 0.25);
    f.rotation.order = 'YZX';
    grp.add(f); if (ol) outline(f, ol);
  }
  return grp;
}

function skyline(g, seed, o) {
  const r = rng(seed);
  for (let i = 0; i < o.n; i++) {
    const w = o.wMin + r() * (o.wMax - o.wMin), d = 8 + r() * 6;
    const center = 1 - Math.min(1, Math.abs((i / o.n) - 0.45) * 2.2);
    const h = o.hMin + Math.pow(r(), 1.5) * (o.hMax - o.hMin) * (0.5 + center);
    const x = o.x0 + (i / o.n) * (o.x1 - o.x0) + (r() - 0.5) * 6;
    const z = o.z0 - r() * o.zd;
    const tx = windowTextures(seed * 31 + i, { facade: o.facade, win: o.win, lit: o.lit });
    tx.map.repeat.set(Math.max(1, w / 7), Math.max(1, h / 12)); tx.glow.repeat.copy(tx.map.repeat);
    const m = new THREE.MeshToonMaterial({ color: C(o.colors[i % o.colors.length]), map: tx.map, emissive: C(0xffffff), emissiveMap: tx.glow, emissiveIntensity: o.ei ?? 1.4 });
    add(g, new THREE.BoxGeometry(w, h, d), m, [x, h / 2, z]);
    if (r() < 0.35) add(g, new THREE.BoxGeometry(0.4, 4, 0.4), glow(2.5, 0.4, 0.4), [x, h + 2, z]);
  }
}

// ---------------- OCEAN AT DUSK ----------------
function oceanSet(scene) {
  const g = new THREE.Group(); scene.add(g);
  const SUN = V(0.1, 0.06, -1).normalize();
  g.add(skyDome(['#ffb36a', '#f0789a', '#6b4aa6', '#1f1d5e'], SUN));

  const oceanMat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uCam: { value: V(0, 0, 0) }, uSun: { value: SUN },
      cDeep: { value: C('#1d2f6b') }, cMid: { value: C('#2e5aa8') }, cLight: { value: C('#5a8fd6') }, cFoam: { value: C('#f2f4ff') },
      cHor: { value: C('#f2a07a') }, cSunP: { value: new THREE.Color(2.2, 1.6, 0.9) } },
    vertexShader: `uniform float uTime; varying float vH; varying vec3 vW;
      float wave(vec2 p){ return 0.35*sin(p.x*0.18+uTime*1.1) + 0.25*sin(p.y*0.23-uTime*0.9+p.x*0.05) + 0.12*sin((p.x+p.y)*0.5+uTime*2.0) + 0.06*sin(p.x*1.3-p.y*0.9+uTime*3.1); }
      void main(){ vec4 w = modelMatrix * vec4(position,1.0); float h = wave(w.xz); w.y += h; vH = h; vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform float uTime; uniform vec3 uCam,uSun,cDeep,cMid,cLight,cFoam,cHor,cSunP; varying float vH; varying vec3 vW;
      float hs(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
      float n2(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(hs(i),hs(i+vec2(1,0)),f.x), mix(hs(i+vec2(0,1)),hs(i+vec2(1,1)),f.x), f.y); }
      void main(){
        float d = length(vW.xz - uCam.xz);
        float band = vH * 1.25 + 0.3 * n2(vW.xz * 0.12 + vec2(uTime * 0.15, 0.0)) - 0.15;
        vec3 c = cDeep; if (band > -0.12) c = cMid; if (band > 0.38) c = cLight;
        float f = n2(vec2(vW.x * 0.55, vW.z * 2.4) + vec2(uTime * 0.35, uTime * 0.1));
        if (vH > 0.38 && f > 0.58) c = cFoam;
        float f2 = n2(vec2(vW.x * 1.7, vW.z * 6.0) - vec2(uTime * 0.6, 0.0));
        if (f2 > 0.86 && d < 120.0) c = mix(c, cFoam, 0.85);
        vec3 v = normalize(vW - uCam);
        float sa = dot(normalize(v.xz), normalize(uSun.xz));
        float gl = n2(vW.xz * vec2(0.9, 3.0) + vec2(0.0, uTime * 0.8));
        if (sa > 0.992 - 0.004 * smoothstep(40.0, 260.0, d) && gl > 0.52) c = cSunP;
        c = mix(c, cHor, smoothstep(50.0, 330.0, d));
        gl_FragColor = vec4(c, 1.0); }`,
  });
  const og = new THREE.PlaneGeometry(800, 800, 280, 280); og.rotateX(-Math.PI / 2);
  const ocean = add(g, og, oceanMat, [0, 0, -120]);

  // cumulus clouds (toon spheres, purple undersides)
  const cloudMat = toon('#ffeef0', { emissive: '#3b2c66', ei: 0.55, fog: false });
  const cg = new THREE.IcosahedronGeometry(1, 3);
  const r = rng(11);
  const clouds = new THREE.Group(); g.add(clouds);
  for (let k = 0; k < 11; k++) {
    const cx = -520 + k * 100 + (r() - 0.5) * 50, cz = -560 - r() * 140, cy = 30 + r() * 80;
    const sc = 0.7 + r() * 0.8;
    for (let i = 0; i < 9; i++) {
      const m = new THREE.Mesh(cg, cloudMat);
      const rr = (18 + r() * 28) * sc;
      m.position.set(cx + (r() - 0.5) * 90 * sc, cy + Math.abs(r() - 0.3) * 40 * sc, cz + (r() - 0.5) * 30);
      m.scale.set(rr * 1.25, rr, rr);
      clouds.add(m);
    }
  }
  // Durban beachfront skyline + beach + palms
  skyline(g, 5, { n: 48, x0: -260, x1: 280, z0: -212, zd: 34, wMin: 8, wMax: 17, hMin: 14, hMax: 64,
    colors: ['#3a3466', '#433a70', '#2f2d5c', '#4a3b6e'], facade: '#9c93c4', win: '#4a4478', lit: 0.42, ei: 1.5 });
  add(g, new THREE.BoxGeometry(900, 0.6, 18), toon('#c98a6a'), [0, 0.2, -200]);
  const trunk = toon('#3a2a3a'), frond = toon('#1f3a3c');
  for (let i = 0; i < 26; i++) palm(g, -250 + i * 21 + r() * 6, -192 - r() * 4, 9 + r() * 5, (r() - 0.5) * 2, trunk, frond);
  // ships on the horizon
  const hull = toon('#7a2a30'), deck = toon('#e8e0e0');
  for (const [x, z, s] of [[-140, -120, 1.2], [110, -150, 1], [40, -95, 0.7]]) {
    add(g, new THREE.BoxGeometry(14 * s, 1.8 * s, 3 * s), hull, [x, 0.6, z]);
    add(g, new THREE.BoxGeometry(3 * s, 2.6 * s, 2.6 * s), deck, [x - 4.5 * s, 2.6 * s, z]);
    for (let k = 0; k < 4; k++) add(g, new THREE.BoxGeometry(1.8 * s, 1.2 * s, 2.6 * s), toon(['#2f6fa0', '#c04a3a', '#d9a030', '#3a8a6a'][k]), [x - 1 + k * 2 * s, 1.9 * s, z]);
  }
  // lights
  const sun = new THREE.DirectionalLight('#ffb27a', 2.4); sun.position.copy(SUN).multiplyScalar(500); g.add(sun);
  const fill = new THREE.DirectionalLight('#ff8fb0', 0.7); fill.position.set(0, 60, 300); g.add(fill);
  g.add(new THREE.HemisphereLight('#8a7ad0', '#2a1f4a', 0.6));

  return { group: g, fog: new THREE.Fog('#f2a07a', 80, 520), bg: null, bloom: 0.5,
    cel: { dir: [0.1, 0.5, -1], shade: [0.6, 0.45, 0.7], rim: [1.2, 0.7, 0.4], rimDir: [0.1, 0.1, -1], rimAmt: 1 },
    update(t, cam) { oceanMat.uniforms.uTime.value = t; oceanMat.uniforms.uCam.value.copy(cam.position); clouds.position.x = t * 2.5; } };
}

// ---------------- STREET AT NIGHT, RAIN ----------------
function streetSet(scene) {
  const g = new THREE.Group(); scene.add(g);
  const sky = skyDome(['#5a3274', '#3a2660', '#1d1a48', '#0a0c24'], V(-0.4, 0.5, -0.8).normalize(), { sunCol: [1.2, 1.25, 1.4], sunAmt: 0.45, stars: 1 });
  g.add(sky);
  add(g, new THREE.PlaneGeometry(200, 120), toon('#1b1e2c', { steps: 2 }), [0, 0, 0], [-Math.PI / 2, 0, 0]);
  add(g, new THREE.BoxGeometry(80, 0.16, 4.6), toon('#4c5170'), [0, 0.08, -4.3]);
  for (let i = -20; i < 20; i++) add(g, new THREE.BoxGeometry(0.04, 0.01, 4.6), toon('#2e3148'), [i * 1.5, 0.165, -4.3]);
  add(g, new THREE.BoxGeometry(80, 0.2, 0.25), toon('#5a5d70'), [0, 0.1, -2.0]);
  // road markings
  for (let i = -10; i < 12; i++) add(g, new THREE.PlaneGeometry(2.2, 0.14), toon('#c9c4b0'), [i * 4, 0.012, 3.2], [-Math.PI / 2, 0, 0]);

  // Hemingway's facade
  const fac = windowTextures(77, { facade: '#7fa4ac', win: '#2a3a44', lit: 0.5, rows: 10 });
  fac.map.repeat.set(3, 1.4); fac.glow.repeat.set(3, 1.4);
  const facMat = new THREE.MeshToonMaterial({ color: C('#3d6470'), map: fac.map, emissive: C(0xffffff), emissiveMap: fac.glow, emissiveIntensity: 1.2 });
  add(g, new THREE.BoxGeometry(16, 10, 1.2), facMat, [0, 7.0, -7.1]);
  add(g, new THREE.BoxGeometry(16, 3.6, 1.2), toon('#22343c'), [0, 1.8, -7.1]);
  add(g, new THREE.BoxGeometry(16.4, 0.3, 1.6), toon('#15232a'), [0, 3.65, -6.9]);
  add(g, new THREE.BoxGeometry(1.9, 2.7, 0.2), toon('#120a10'), [0, 1.35, -6.42]);
  add(g, new THREE.PlaneGeometry(1.7, 0.4), glow(2.0, 1.2, 0.6), [0, 2.9, -6.41]);
  for (const x of [-4.6, 4.6]) {
    add(g, new THREE.PlaneGeometry(3.4, 2.1), glow(0.62, 0.2, 0.5), [x, 1.75, -6.41]);
    for (let k = 0; k < 3; k++) add(g, new THREE.BoxGeometry(0.06, 2.1, 0.06), toon('#101018'), [x - 1.1 + k * 1.1, 1.75, -6.38]);
  }
  const sign = add(g, new THREE.PlaneGeometry(6.2, 1.55), glow(1.25, 1.25, 1.25, { additive: true, map: textTexture("Hemingway's") }), [0, 4.45, -6.35]);
  add(g, new THREE.BoxGeometry(6.6, 1.8, 0.15), toon('#0d0a14'), [0, 4.45, -6.45]);
  const neonP = glow(3.2, 0.5, 1.8), neonC = glow(0.4, 2.4, 3.2);
  add(g, new THREE.BoxGeometry(16, 0.07, 0.07), neonP, [0, 3.35, -6.38]);
  for (const x of [-1.08, 1.08]) add(g, new THREE.BoxGeometry(0.07, 2.8, 0.07), neonC, [x, 1.4, -6.36]);
  add(g, new THREE.BoxGeometry(5.2, 0.12, 1.5), toon('#5a1a2a'), [0, 3.05, -5.8], [0.18, 0, 0], 0.02);

  // neighbours
  const nb = [[-15, 13, 14, '#3d2f4a', 81], [14, 11, 12, '#283a52', 82], [-29, 16, 14, '#2a3045', 83], [27, 14, 14, '#3a2f3f', 84]];
  for (const [x, h, w, col, sd] of nb) {
    const t = windowTextures(sd, { facade: '#a99cc0', win: '#2c2840', lit: 0.45 }); t.map.repeat.set(w / 4, h / 4); t.glow.repeat.copy(t.map.repeat);
    add(g, new THREE.BoxGeometry(w, h, 1.2), new THREE.MeshToonMaterial({ color: C(col), map: t.map, emissive: C(0xffffff), emissiveMap: t.glow, emissiveIntensity: 1.2 }), [x, h / 2, -7.4]);
  }
  skyline(g, 9, { n: 30, x0: -110, x1: 110, z0: -70, zd: 50, wMin: 8, wMax: 16, hMin: 18, hMax: 58,
    colors: ['#1c1a33', '#221e3c', '#18172e'], facade: '#6a6390', win: '#22203a', lit: 0.5, ei: 1.3 });

  // palms + lamps + car
  const trunk = toon('#4a3a40'), frond = toon('#1f4a3a');
  for (const x of [-11, -5.6, 5.6, 11]) palm(g, x, -5.7, 6.2, x > 0 ? 0.6 : -0.6, trunk, frond, 0.02);
  const lampLights = [];
  for (const x of [-8, 3.5]) {
    add(g, new THREE.CylinderGeometry(0.07, 0.09, 5, 8), toon('#2a2a33'), [x, 2.5, -2.4], null, 0.015);
    add(g, new THREE.BoxGeometry(0.9, 0.12, 0.3), toon('#2a2a33'), [x + 0.4, 5.0, -2.4]);
    add(g, new THREE.BoxGeometry(0.5, 0.08, 0.26), glow(3, 2.2, 1.2), [x + 0.65, 4.93, -2.4]);
    const L = new THREE.PointLight('#ffb070', 26, 13, 2); L.position.set(x + 0.65, 4.7, -2.4); g.add(L); lampLights.push(L);
    add(g, new THREE.CircleGeometry(2.2, 24), glow(0.5, 0.33, 0.16, { additive: true, opacity: 0.5 }), [x + 0.65, 0.17, -3.0], [-Math.PI / 2, 0, 0]);
  }
  const car = new THREE.Group(); car.position.set(8.2, 0, 1.1); g.add(car);
  const body = toon('#7a1f2b'), dark = toon('#0e1420');
  const cb = new THREE.Mesh(new RoundedBoxGeometry(4.3, 0.85, 1.85, 3, 0.25), body); cb.position.y = 0.75; car.add(cb); outline(cb, 0.02);
  const cab = new THREE.Mesh(new RoundedBoxGeometry(2.3, 0.7, 1.65, 3, 0.25), dark); cab.position.set(-0.2, 1.42, 0); car.add(cab); outline(cab, 0.02);
  for (const [x, z] of [[-1.4, 0.9], [1.4, 0.9], [-1.4, -0.9], [1.4, -0.9]]) {
    const wh = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.25, 16), toon('#0a0a0a')); wh.rotation.x = Math.PI / 2; wh.position.set(x, 0.38, z); car.add(wh);
  }
  const hl = glow(3, 2.6, 1.8); for (const z of [0.6, -0.6]) { const h = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.16, 0.36), hl); h.position.set(-2.16, 0.85, z); car.add(h); }
  const tl = glow(3, 0.2, 0.25); for (const z of [0.65, -0.65]) { const h = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.14, 0.3), tl); h.position.set(2.16, 0.85, z); car.add(h); }

  // wet-street reflections (additive streaks)
  const refl = (x, z, w, l, r, gg, b, o = 0.55) => add(g, new THREE.PlaneGeometry(w, l), glow(r, gg, b, { additive: true, opacity: o }), [x, 0.015, z], [-Math.PI / 2, 0, 0]);
  refl(0, -1.2, 4.5, 3.6, 1.0, 0.18, 0.6); refl(-1.08, -0.6, 0.35, 4.8, 0.15, 0.8, 1.1, 0.6); refl(1.08, -0.6, 0.35, 4.8, 0.15, 0.8, 1.1, 0.6);
  refl(-4.6, -1.0, 2.6, 3.0, 0.5, 0.12, 0.38, 0.45); refl(4.6, -1.0, 2.6, 3.0, 0.5, 0.12, 0.38, 0.45);
  refl(6.0, 3.0, 1.0, 5.0, 0.6, 0.05, 0.06, 0.5);
  const r = rng(21);
  for (let i = 0; i < 14; i++) add(g, new THREE.CircleGeometry(0.5 + r() * 0.9, 20), toon('#2c3350', { steps: 2 }), [-14 + r() * 26, 0.17 + (r() < 0.5 ? 0 : -0.155), -4 + r() * 8], [-Math.PI / 2, 0, 0]).scale.set(1.6, 0.7, 1);

  // rain
  const N = 2600, rp = new Float32Array(N * 6), seeds = [];
  for (let i = 0; i < N; i++) seeds.push([-18 + r() * 34, r() * 14, -6.5 + r() * 18, 0.25 + r() * 0.35]);
  const rg = new THREE.BufferGeometry(); rg.setAttribute('position', new THREE.BufferAttribute(rp, 3));
  const rain = new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: new THREE.Color(0.75, 0.82, 1.0), transparent: true, opacity: 0.5, fog: false }));
  rain.frustumCulled = false; g.add(rain);

  g.add(new THREE.HemisphereLight('#6a78c8', '#1a1426', 1.0));
  const moon = new THREE.DirectionalLight('#9fb4ff', 0.9); moon.position.set(-6, 12, 9); g.add(moon);
  const pink = new THREE.PointLight('#ff4fa3', 40, 18, 2); pink.position.set(0, 4.0, -4.6); g.add(pink);

  return { group: g, fog: new THREE.Fog('#1a1838', 22, 150), bg: null, bloom: 0.9,
    cel: { dir: [-0.35, 0.75, 0.55], shade: [0.42, 0.4, 0.68], rim: [1.1, 0.35, 0.75], rimDir: [0.2, 0.25, -1], rimAmt: 1.0 },
    update(t, cam) {
      const H = 14, sp = 15;
      for (let i = 0; i < N; i++) {
        const s = seeds[i]; const y = H - ((s[1] + sp * t) % H); const L = s[3];
        const x = s[0] + cam.position.x * 0.0, z = s[2];
        rp[i * 6] = x - 0.04; rp[i * 6 + 1] = y + L; rp[i * 6 + 2] = z;
        rp[i * 6 + 3] = x; rp[i * 6 + 4] = y; rp[i * 6 + 5] = z;
      }
      rg.attributes.position.needsUpdate = true;
      rain.position.x = Math.round(cam.position.x / 34) * 34 * 0;
      const fl = hash1(Math.floor(t * 14)) < 0.06 ? 0.35 : 1;
      sign.material.color.setScalar(1.25 * fl); pink.intensity = 40 * fl;
    } };
}

// ---------------- CLUB INTERIOR ----------------
function clubSet(scene) {
  const g = new THREE.Group(); scene.add(g);
  add(g, new THREE.PlaneGeometry(24, 24), toon('#140f1e', { steps: 2 }), [0, 0, -1], [-Math.PI / 2, 0, 0]);
  add(g, new THREE.BoxGeometry(24, 7, 0.3), toon('#2a1640'), [0, 3.5, -9.95]);
  add(g, new THREE.BoxGeometry(0.3, 7, 24), toon('#24123a'), [-10.15, 3.5, -1]);
  add(g, new THREE.BoxGeometry(0.3, 7, 24), toon('#1f1236'), [10.15, 3.5, -1]);
  add(g, new THREE.BoxGeometry(24, 7, 0.3), toon('#1a0f2c'), [0, 3.5, 11]);
  add(g, new THREE.PlaneGeometry(24, 24), toon('#0c0814'), [0, 6.6, -1], [Math.PI / 2, 0, 0]);
  // wall paneling stripes
  for (let i = -9; i <= 9; i += 1.5) add(g, new THREE.BoxGeometry(0.08, 7, 0.05), toon('#3a2054'), [i, 3.5, -9.78]);
  // door
  add(g, new THREE.BoxGeometry(2.0, 2.85, 0.1), toon('#3a2a20'), [0, 1.42, -9.8]);
  const doorway = add(g, new THREE.PlaneGeometry(1.6, 2.6), glow(0.2, 0.12, 0.08), [0, 1.3, -9.74]);
  const doorPivot = new THREE.Group(); doorPivot.position.set(-0.8, 0, -9.68); g.add(doorPivot);
  const door = new THREE.Mesh(new THREE.BoxGeometry(1.6, 2.6, 0.1), toon('#5a2230')); door.position.set(0.8, 1.3, 0); doorPivot.add(door); outline(door, 0.02);
  const knob = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), toon('#d9b050')); knob.position.set(1.4, 1.25, 0.08); doorPivot.add(knob);
  const doorLight = new THREE.PointLight('#ffc07a', 0, 9, 2); doorLight.position.set(0, 1.8, -9.0); g.add(doorLight);
  // neon sign + tubes
  add(g, new THREE.PlaneGeometry(5.2, 1.3), glow(1.2, 1.2, 1.2, { additive: true, map: textTexture("Hemingway's") }), [0, 4.5, -9.75]);
  const nP = glow(3.2, 0.45, 1.8), nC = glow(0.35, 2.3, 3.2);
  add(g, new THREE.BoxGeometry(7.6, 0.07, 0.07), nP, [-5.6, 3.4, -9.75]); add(g, new THREE.BoxGeometry(7.6, 0.07, 0.07), nP, [5.6, 3.4, -9.75]);
  add(g, new THREE.BoxGeometry(0.07, 0.07, 18), nC, [-9.95, 3.0, -1]);
  add(g, new THREE.BoxGeometry(0.07, 0.07, 18), nP, [9.95, 4.6, -1]);
  // bar
  add(g, new THREE.BoxGeometry(0.9, 1.1, 11), toon('#4a1c22'), [6, 0.55, -1.5], null, 0.02);
  add(g, new THREE.BoxGeometry(1.15, 0.08, 11.3), toon('#2a1015'), [6, 1.14, -1.5], null, 0.015);
  add(g, new THREE.BoxGeometry(0.04, 0.04, 11), glow(0.22, 1.15, 1.6), [5.52, 0.98, -1.5]);
  add(g, new THREE.BoxGeometry(0.4, 2.4, 10.5), toon('#2a1520'), [9.75, 2.2, -1.5]);
  add(g, new THREE.BoxGeometry(0.05, 0.05, 10.5), glow(1.4, 0.85, 0.32), [9.5, 1.45, -1.5]);
  add(g, new THREE.BoxGeometry(0.05, 0.05, 10.5), glow(1.4, 0.85, 0.32), [9.5, 2.35, -1.5]);
  const bottleCols = ['#d9a030', '#3a8a5a', '#5a9ad9', '#c94a3a', '#e8e0c0'];
  const r = rng(33);
  for (const y of [1.65, 2.55]) for (let i = 0; i < 24; i++) {
    const col = C(bottleCols[Math.floor(r() * bottleCols.length)]);
    const m = new THREE.MeshToonMaterial({ color: col, emissive: col, emissiveIntensity: 0.35 });
    add(g, new THREE.CylinderGeometry(0.055, 0.06, 0.28 + r() * 0.1, 8), m, [9.42, y, -6.4 + i * 0.42]);
  }
  for (const z of [-6.2, -4.9, -3.6, 4.6, 5.9]) {
    add(g, new THREE.CylinderGeometry(0.22, 0.22, 0.08, 16), toon('#8a1f3a'), [5.0, 0.8, z], null, 0.015);
    add(g, new THREE.CylinderGeometry(0.035, 0.035, 0.76, 8), toon('#9aa0b0'), [5.0, 0.4, z]);
    add(g, new THREE.CylinderGeometry(0.2, 0.22, 0.03, 16), toon('#9aa0b0'), [5.0, 0.02, z]);
  }
  // booths
  for (const z of [-6, -2, 2]) {
    add(g, new THREE.BoxGeometry(1.2, 0.5, 2.4), toon('#5a1428'), [-9.3, 0.25, z], null, 0.015);
    add(g, new THREE.BoxGeometry(0.3, 1.3, 2.4), toon('#6a1830'), [-9.85, 0.75, z], null, 0.015);
    add(g, new THREE.CylinderGeometry(0.45, 0.45, 0.06, 16), toon('#2a1a20'), [-8.4, 0.75, z]);
    add(g, new THREE.CylinderGeometry(0.06, 0.06, 0.75, 8), toon('#2a1a20'), [-8.4, 0.37, z]);
  }
  // dancefloor tiles
  const TI = 10, TJ = 10;
  const tiles = new THREE.InstancedMesh(new THREE.BoxGeometry(0.94, 0.05, 0.94), new THREE.MeshBasicMaterial({ color: 0xffffff }), TI * TJ);
  const m4 = new THREE.Matrix4(); let k = 0;
  for (let i = 0; i < TI; i++) for (let j = 0; j < TJ; j++) { m4.makeTranslation(-7.5 + i, 0.025, -6 + j); tiles.setMatrixAt(k, m4); tiles.setColorAt(k, C(0)); k++; }
  g.add(tiles);
  // light cones + disco ball
  const cones = [];
  const coneGeo = new THREE.ConeGeometry(1.7, 6.2, 24, 1, true); coneGeo.translate(0, -3.1, 0);
  for (const [x, z, cr, cg2, cb] of [[-5, -3, 0.9, 0.2, 0.7], [-1, 1, 0.2, 0.7, 0.9], [-3, -5, 0.7, 0.3, 0.9]]) {
    const c = add(g, coneGeo, glow(cr, cg2, cb, { additive: true, opacity: 0.07, side: THREE.DoubleSide }), [x, 6.5, z]); cones.push(c);
  }
  const ball = add(g, new THREE.IcosahedronGeometry(0.38, 1), toon('#dfe4ff', { emissive: '#6a6a90', ei: 0.8, steps: 2 }), [-3, 5.7, -1]);
  add(g, new THREE.CylinderGeometry(0.01, 0.01, 0.9, 4), toon('#333'), [-3, 6.15, -1]);
  // glass prop
  const glass = new THREE.Group(); g.add(glass);
  const gl1 = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.04, 0.13, 14), toon('#cfe8ff', { emissive: '#406080', ei: 0.5 })); gl1.position.y = 0.065; glass.add(gl1); outline(gl1, 0.006);
  const gl2 = new THREE.Mesh(new THREE.CylinderGeometry(0.041, 0.037, 0.08, 14), glow(1.6, 0.8, 0.2)); gl2.position.y = 0.05; glass.add(gl2);
  glass.position.set(5.7, 1.18, -3.4);

  g.add(new THREE.HemisphereLight('#7a5aa8', '#120a1a', 0.9));
  const key = new THREE.DirectionalLight('#ffd9e8', 1.0); key.position.set(2, 8, 6); g.add(key);
  const pinkL = new THREE.PointLight('#ff3fa0', 34, 16, 2); pinkL.position.set(-3, 4, -1); g.add(pinkL);
  const cyanL = new THREE.PointLight('#3fd8ff', 22, 10, 2); cyanL.position.set(6.4, 3.0, -0.5); g.add(cyanL);

  const pal = { groove: ['#ff2fa0', '#2fd8ff', '#7a3cff', '#1a1030'], fight: ['#ff2040', '#ff2fa0', '#400818', '#1a0610'], dim: ['#2a1030', '#101828', '#1a0d24', '#0a0610'] };
  const tmp = new THREE.Color();
  return { group: g, fog: new THREE.Fog('#160c26', 10, 42), bg: C('#07040c'), bloom: 0.85, door: doorPivot, doorway, doorLight, glass,
    cel: { dir: [0.25, 0.8, 0.65], shade: [0.48, 0.38, 0.66], rim: [0.35, 0.95, 1.15], rimDir: [1, 0.25, -0.2], rimAmt: 1.0 },
    celFight: { dir: [0.25, 0.8, 0.65], shade: [0.45, 0.32, 0.55], rim: [1.25, 0.25, 0.45], rimDir: [-0.6, 0.35, -0.7], rimAmt: 1.15 },
    update(t, cam, TL) {
      const beat = t * TL.bpm / 60, bi = Math.floor(beat), bf = beat - bi;
      const mode = t >= 12.5 && t < 14.0 ? 'dim' : t >= 14.0 && t < 21.0 ? 'fight' : 'groove';
      const P = pal[mode];
      const land = TL.cues.find((c) => c.type === 'land');
      let k = 0;
      for (let i = 0; i < TI; i++) for (let j = 0; j < TJ; j++) {
        const pidx = ((i + j + bi) % 3 + 3) % 3;
        const on = mode === 'dim' ? 0.35 : ((i * 7 + j * 3 + bi) % 5 === 0 ? 1.6 : 0.85);
        tmp.set(P[pidx]).multiplyScalar(on * (mode === 'dim' ? 1 : 0.75 + 0.5 * (1 - bf)));
        if (land && t >= land.t && t < land.t + 1.4) {
          const d = Math.hypot(-7.5 + i - (-2.6), -6 + j - (-0.5)); const rr = (t - land.t) * 7;
          const ring = Math.max(0, 1 - Math.abs(d - rr) / 1.2) * (1 - (t - land.t) / 1.4);
          tmp.r += ring * 1.3; tmp.g += ring * 0.9; tmp.b += ring * 1.2;
        }
        tiles.setColorAt(k++, tmp);
      }
      tiles.instanceColor.needsUpdate = true;
      cones.forEach((c, i) => { c.visible = !TL.noCones; c.rotation.z = Math.sin(t * 0.8 + i * 2) * 0.45; c.rotation.x = Math.cos(t * 0.6 + i) * 0.3; c.material.opacity = mode === 'dim' ? 0.02 : 0.07; });
      ball.rotation.y = t * 0.9;
      pinkL.intensity = mode === 'dim' ? 8 : mode === 'fight' ? 30 + 20 * (1 - bf) : 34;
      pinkL.color.set(mode === 'fight' ? '#ff2a40' : '#ff3fa0');
    } };
}

export function buildSets(scene) {
  return { ocean: oceanSet(scene), street: streetSet(scene), club: clubSet(scene) };
}
