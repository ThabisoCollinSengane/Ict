// Daylight Indian Ocean off Durban: painted ocean, anime cumulus, container ships, breaching humpbacks.
import * as THREE from 'three';
import { toon, glow, cel, outline, rng, windowTextures, clamp, lerp, EASE } from './toon.js';

const C = (c) => new THREE.Color(c);
const SHIP_SPEED = 5.0;
const DECK_Y = 8.0;

function stripeTex(cols, n, w = 256, h = 16, dir = 'x') {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const g = cv.getContext('2d');
  g.fillStyle = cols[0]; g.fillRect(0, 0, w, h);
  g.fillStyle = cols[1];
  for (let i = 0; i < n; i++) {
    const p = (i + 0.5) * (dir === 'x' ? w : h) / n;
    if (dir === 'x') g.fillRect(p - 1.2, 0, 2.4, h); else g.fillRect(0, p - 1.2, w, 2.4);
  }
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}

// ---------- humpback whale (head = local +Y, back = local +Z) ----------
function makeWhale(scale, seed) {
  const outer = new THREE.Group(); outer.rotation.order = 'YXZ';
  const inner = new THREE.Group(); outer.add(inner);
  const body = new THREE.Group(); body.scale.setScalar(scale); body.position.y = -6.1 * scale; inner.add(body);
  const prof = [[0.05, 0], [0.28, 0.3], [0.36, 1.5], [0.72, 3.5], [1.2, 5.5], [1.6, 7.5], [1.66, 8.3], [1.46, 9.6], [1.06, 10.8], [0.56, 11.7], [0.16, 12.1], [0.0, 12.22]]
    .map(([r, y]) => new THREE.Vector2(r, y));
  const dark = cel('#2e3a4e'), white = cel('#eef3f8');
  const bg = new THREE.LatheGeometry(prof, 36); bg.scale(1, 1, 0.86);
  const bm = new THREE.Mesh(bg, dark); body.add(bm); outline(bm, 0.05, 0x0c1220);
  const bellyProf = prof.slice(4, 11).map((v) => new THREE.Vector2(v.x * 1.012, v.y));
  const pleat = stripeTex(['#f4f8fb', '#5a6a80'], 18);
  const belly = new THREE.Mesh(new THREE.LatheGeometry(bellyProf, 24, Math.PI - 1.05, 2.1), cel('#ffffff', { map: pleat }));
  belly.geometry.scale(1, 1, 0.86); body.add(belly);
  // knobby head tubercles
  const r = rng(seed);
  for (let i = 0; i < 12; i++) {
    const y = 10.2 + r() * 1.6, a = (r() - 0.5) * 1.6;
    const rr = lerp(1.06, 0.3, (y - 10.2) / 1.9);
    const k = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 6), dark);
    k.position.set(Math.sin(a) * rr, y, Math.cos(a) * rr * 0.86); body.add(k);
  }
  // dorsal hump
  const df = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.6, 8), dark); df.position.set(0, 4.3, 0.62); df.rotation.x = -0.7; df.scale.set(0.6, 1, 1); body.add(df);
  // long white pectoral fins
  const fins = [];
  for (const s of [1, -1]) {
    const piv = new THREE.Group(); piv.position.set(s * 1.35, 8.2, -0.5); body.add(piv);
    const fin = new THREE.Mesh(new THREE.CapsuleGeometry(0.34, 3.4, 6, 12), white);
    fin.scale.set(1, 1, 0.22); fin.position.y = -2.0; piv.add(fin); outline(fin, 0.035, 0x0c1220);
    const top = new THREE.Mesh(new THREE.CapsuleGeometry(0.3, 3.2, 6, 12), dark); top.scale.set(0.9, 0.95, 0.12); top.position.set(0, -1.9, 0.05); piv.add(top);
    piv.rotation.z = s * (Math.PI / 2 + 0.55); fins.push(piv);
  }
  // flukes
  for (const s of [1, -1]) {
    const fl = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), dark);
    fl.scale.set(1.55, 0.5, 0.12); fl.position.set(s * 1.25, 0.1, 0); fl.rotation.z = s * -0.35; body.add(fl); outline(fl, 0.04, 0x0c1220);
    const fu = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), white);
    fu.scale.set(1.45, 0.42, 0.1); fu.position.set(s * 1.25, 0.08, -0.03); fu.rotation.z = s * -0.35; body.add(fu);
  }
  return { outer, inner, fins, scale };
}

// Breach pose at u in [0,1]: rises near-vertical, rolls, falls onto its back.
function breach(w, u, ev) {
  const L = 12.2 * w.scale;
  const rise = EASE.out(clamp(u / 0.42)), fall = EASE.in(clamp((u - 0.42) / 0.58));
  const yc = lerp(-0.55 * L, 0.38 * L, rise) - fall * 0.95 * L;
  const fwd = u * 0.35 * L;
  const pitch = lerp(0.18, 0.32, rise) + fall * 1.55;
  const hx = Math.sin(ev.heading), hz = Math.cos(ev.heading);
  w.outer.position.set(ev.x + hx * fwd, yc, ev.z + hz * fwd);
  w.outer.rotation.set(pitch, ev.heading, 0);
  w.inner.rotation.y = EASE.inout(clamp((u - 0.25) / 0.6)) * (ev.roll ?? 2.2);
  const spread = Math.sin(clamp(u / 0.9) * Math.PI);
  w.fins.forEach((f, i) => { const s = i === 0 ? 1 : -1; f.rotation.z = s * (Math.PI / 2 + 0.55 - 0.9 * spread); f.rotation.x = 0.25 * spread; });
  w.outer.visible = yc > -0.62 * L;
}

function cumulus(g, mat, x, y, z, s, seed) {
  const r = rng(seed);
  const geo = new THREE.IcosahedronGeometry(1, 3);
  const n = 16;
  for (let i = 0; i < n; i++) {
    const a = r() * Math.PI * 2, d = Math.pow(r(), 0.7);
    const rad = (0.35 + 0.65 * (1 - d) * r() + 0.25) * s;
    const m = new THREE.Mesh(geo, mat);
    const px = x + Math.cos(a) * d * 2.2 * s, pz = z + Math.sin(a) * d * 0.9 * s;
    const py = y + rad * 0.55 + (1 - d) * s * 0.9 * r();
    m.position.set(px, py, pz); m.scale.set(rad * 1.15, rad, rad);
    g.add(m);
  }
  const base = new THREE.Mesh(geo, mat); base.scale.set(2.6 * s, 0.35 * s, 1.1 * s); base.position.set(x, y + 0.2 * s, z); g.add(base);
}

let _wake;
function wakeTex() {
  if (_wake) return _wake;
  const cv = document.createElement('canvas'); cv.width = 64; cv.height = 256;
  const g = cv.getContext('2d'); const r = rng(5);
  for (let i = 0; i < 260; i++) {
    const y = r() * 256, spread = 4 + (y / 256) * 28, x = 32 + (r() - 0.5) * 2 * spread * (r() < 0.5 ? 1 : 0.4);
    g.globalAlpha = (1 - y / 256) * 0.9; g.fillStyle = '#fff'; g.fillRect(x, y, 1.5 + r() * 2, 4 + r() * 10);
  }
  _wake = new THREE.CanvasTexture(cv); _wake.colorSpace = THREE.SRGBColorSpace; return _wake;
}
function cargoShip(g, len, seed) {
  const r = rng(seed);
  const ship = new THREE.Group(); g.add(ship);
  const hullM = toon('#8a2b2b'), topM = toon('#1f2f4f');
  const hull = new THREE.Mesh(new THREE.BoxGeometry(len * 0.16, 5, len), hullM); hull.position.y = 1.5; ship.add(hull);
  const band = new THREE.Mesh(new THREE.BoxGeometry(len * 0.162, 1.2, len * 1.002), topM); band.position.y = 3.4; ship.add(band);
  const bow = new THREE.Mesh(new THREE.ConeGeometry(len * 0.08, len * 0.14, 4), hullM); bow.rotation.set(-Math.PI / 2, 0, Math.PI / 4); bow.scale.set(1, 1, 0.55); bow.position.set(0, 1.9, -len * 0.56); ship.add(bow);
  const cols = ['#c8372d', '#2f6fb0', '#e08a2a', '#3a8a6a', '#e9e4da', '#7a2f8a'];
  const rows = Math.floor(len * 0.7 / 6.5), stack = 3, across = 4;
  const box = new THREE.InstancedMesh(new THREE.BoxGeometry(2.3, 2.4, 6.0), toon('#ffffff'), rows * stack * across);
  const m4 = new THREE.Matrix4(); let k = 0;
  for (let i = 0; i < rows; i++) for (let j = 0; j < stack; j++) for (let a = 0; a < across; a++) {
    m4.makeTranslation((a - (across - 1) / 2) * 2.45, 5.2 + j * 2.5, -len * 0.4 + i * 6.4);
    box.setMatrixAt(k, m4); box.setColorAt(k, C(cols[Math.floor(r() * cols.length)])); k++;
  }
  ship.add(box);
  const bridge = new THREE.Mesh(new THREE.BoxGeometry(len * 0.15, 9, 7), toon('#f2efe8')); bridge.position.set(0, 8, len * 0.4); ship.add(bridge);
  const bwin = new THREE.Mesh(new THREE.BoxGeometry(len * 0.152, 1.0, 7.05), toon('#1d2a40')); bwin.position.set(0, 11, len * 0.4); ship.add(bwin);
  const funnel = new THREE.Mesh(new THREE.BoxGeometry(3, 4, 3), toon('#c8372d')); funnel.position.set(0, 14, len * 0.44); ship.add(funnel);
  const wake = new THREE.Mesh(new THREE.PlaneGeometry(len * 0.3, len * 1.3), glow(1.05, 1.08, 1.1, { transparent: true, opacity: 0.6, map: wakeTex() }));
  wake.rotation.x = -Math.PI / 2; wake.position.set(0, 0.35, len * 1.12); wake.userData.noInk = true; ship.add(wake);
  return ship;
}

export function seaSet(scene) {
  const g = new THREE.Group(); scene.add(g);
  const SUN = new THREE.Vector3(0.35, 0.62, -0.7).normalize();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(1500, 48, 24), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { uSun: { value: SUN }, cH: { value: C('#d8f2ff') }, cM: { value: C('#8ccbf5') }, cT: { value: C('#2a72d0') }, cS: { value: C('#fff6e0') } },
    vertexShader: `varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 uSun,cH,cM,cT,cS; varying vec3 vDir;
      void main(){ vec3 d = normalize(vDir); float y = max(d.y, 0.0);
        vec3 c = mix(cH, cM, smoothstep(0.0, 0.22, y)); c = mix(c, cT, smoothstep(0.18, 0.85, y));
        float s = max(dot(d, uSun), 0.0); c += cS * (0.18 * pow(s, 6.0) + 0.9 * pow(s, 400.0));
        gl_FragColor = vec4(c, 1.0); }`,
  }));
  sky.userData.noInk = true; g.add(sky);

  // painted ocean (follows the camera on a snapped grid)
  const oceanMat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uCam: { value: new THREE.Vector3() }, uSun: { value: SUN },
      cDeep: { value: C('#0d4f9a') }, cMid: { value: C('#1784c4') }, cTurq: { value: C('#2fb6d2') }, cLight: { value: C('#7fe3dc') },
      cFoam: { value: C('#f4fbff') }, cHor: { value: C('#bfe6f7') }, cGlint: { value: new THREE.Color(1.6, 1.55, 1.4) } },
    vertexShader: `uniform float uTime; varying float vH; varying vec3 vW;
      float wave(vec2 p){ return 0.55*sin(p.x*0.11+uTime*0.9) + 0.4*sin(p.y*0.15-uTime*0.7+p.x*0.04) + 0.22*sin((p.x+p.y)*0.32+uTime*1.6) + 0.1*sin(p.x*0.9-p.y*0.7+uTime*2.6); }
      void main(){ vec4 w = modelMatrix * vec4(position,1.0); float h = wave(w.xz); w.y += h; vH = h; vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform float uTime; uniform vec3 uCam,uSun,cDeep,cMid,cTurq,cLight,cFoam,cHor,cGlint; varying float vH; varying vec3 vW;
      float hs(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
      float n2(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(hs(i),hs(i+vec2(1,0)),f.x), mix(hs(i+vec2(0,1)),hs(i+vec2(1,1)),f.x), f.y); }
      float stroke(vec2 p, float dens, float rx, float ry){ vec2 g=floor(p), f=fract(p); if (hs(g) > dens) return 0.0;
        vec2 c=vec2(hs(g+3.1),hs(g+7.7))*0.4+0.3; vec2 d=f-c; d.y += 0.5*d.x*d.x*(hs(g+1.7)-0.5)/rx; d /= vec2(rx, ry); return 1.0-smoothstep(0.75, 1.0, length(d)); }
      vec4 strokeSet(vec2 q, float h, float band){
        float a = stroke(q*vec2(0.5,1.6) + vec2(uTime*0.5, 0.0), 0.2 + 0.32*smoothstep(-0.1, 0.7, h), 0.42, 0.17);
        float b = stroke(q*vec2(1.0,2.9) + vec2(uTime*0.8, 5.0), 0.14 + 0.3*smoothstep(0.0, 0.9, h), 0.4, 0.2);
        float l = stroke(q*vec2(0.65,2.0) + vec2(uTime*0.3, 2.0), 0.3*smoothstep(-0.25, 0.35, band), 0.4, 0.18);
        float dk = stroke(q*vec2(0.36,1.2) + vec2(-uTime*0.25, 9.0), 0.32*(1.0 - smoothstep(-0.7, 0.05, h)), 0.42, 0.16);
        return vec4(max(a*smoothstep(-0.3, 0.3, h), b), l, dk, 0.0);
      }
      void main(){
        float d = length(vW.xz - uCam.xz);
        float h = vH / 1.2;
        float n = n2(vW.xz*0.035 + vec2(uTime*0.02, 0.0));
        float band = h*0.8 + 0.6*n - 0.3;
        vec3 c = cDeep;
        c = mix(c, cMid, step(-0.32, band)); c = mix(c, cTurq, step(0.18, band)); c = mix(c, cLight, step(0.72, band));
        float ca = cos(0.35), sa = sin(0.35); vec2 p = vec2(ca*vW.x - sa*vW.z, sa*vW.x + ca*vW.z);
        float Lg = log2(max(d, 12.0) / 12.0); float l0 = floor(Lg); float fl = Lg - l0;
        vec4 S = mix(strokeSet(p / exp2(l0), h, band), strokeSet(p / exp2(l0 + 1.0), h, band), smoothstep(0.0, 1.0, fl));
        c = mix(c, cDeep*0.7, S.z*0.75);
        c = mix(c, cLight, S.y*0.8);
        c = mix(c, cFoam, S.x);
        vec3 v = normalize(vW - uCam);
        float sd = dot(normalize(v.xz), normalize(uSun.xz));
        if (sd > 0.994 && n2(vW.xz*vec2(0.6,2.0) + uTime*0.6) > 0.8) c = mix(c, cGlint, 0.7);
        c = mix(c, cHor, smoothstep(140.0, 1100.0, d));
        gl_FragColor = vec4(c, 1.0); }`,
  });
  const og = new THREE.PlaneGeometry(2400, 2400, 480, 480); og.rotateX(-Math.PI / 2);
  const ocean = new THREE.Mesh(og, oceanMat); ocean.frustumCulled = false; g.add(ocean);

  // clouds
  const cloudMat = cel('#ffffff', { fog: false });
  const cg = new THREE.Group(); g.add(cg);
  const r = rng(91);
  for (let i = 0; i < 16; i++) {
    const a = -1.3 + (i / 15) * 2.6 + (r() - 0.5) * 0.1, dist = 900 + r() * 250;
    cumulus(cg, cloudMat, Math.sin(a) * dist, 30 + r() * 60, -Math.cos(a) * dist, 45 + r() * 55, 200 + i);
  }
  for (let i = 0; i < 6; i++) cumulus(cg, cloudMat, -500 + r() * 1000, 230 + r() * 120, -400 - r() * 500, 18 + r() * 22, 300 + i);

  // Durban skyline on the horizon
  const city = new THREE.Group(); g.add(city);
  for (let i = 0; i < 40; i++) {
    const w = 18 + r() * 22, h = 30 + Math.pow(r(), 1.5) * 120, x = -500 + i * 25 + r() * 10, z = -1150 - r() * 60;
    const tx = windowTextures(700 + i, { facade: '#e8eef6', win: '#7fa2c8', lit: 0.0 }); tx.map.repeat.set(w / 7, h / 12);
    const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, 20), new THREE.MeshToonMaterial({ color: C(['#c9d6e6', '#b8c6da', '#dfe5ee'][i % 3]), map: tx.map }));
    b.position.set(x, h / 2, z); city.add(b);
  }

  // distant container ships
  const ships = [[-140, -420, 0.15, 160], [120, -620, -0.1, 190], [260, -300, 0.3, 140], [-320, -760, -0.05, 200]].map(([x, z, ry, len], i) => {
    const s = cargoShip(g, len, 40 + i); s.position.set(x, 0, z); s.rotation.y = ry; return s;
  });

  // our ship: deck POV
  const deck = new THREE.Group(); g.add(deck);
  const deckM = toon('#21456c'), pathM = toon('#3a6d99'), railM = toon('#f4ead8'), kickM = toon('#f2a33a'), hullM = toon('#1a2b48');
  const addD = (geo, mat, x, y, z, ol) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); deck.add(m); if (ol) outline(m, ol, 0x14101e); return m; };
  addD(new THREE.BoxGeometry(14, 8, 160), hullM, 0, DECK_Y / 2 - 0.3, -60);
  addD(new THREE.BoxGeometry(14, 0.3, 160), deckM, 0, DECK_Y, -60);
  addD(new THREE.BoxGeometry(2.2, 0.02, 160), pathM, -5.8, DECK_Y + 0.16, -60);
  addD(new THREE.BoxGeometry(0.12, 0.02, 160), toon('#f2c94c'), -6.7, DECK_Y + 0.17, -60);
  addD(new THREE.BoxGeometry(0.06, 0.2, 160), kickM, -6.97, DECK_Y + 0.25, -60);
  addD(new THREE.CylinderGeometry(0.055, 0.055, 160, 8), railM, -7.0, DECK_Y + 1.25, -60, 0.012).rotation.x = Math.PI / 2;
  for (const yy of [0.55, 0.9]) addD(new THREE.CylinderGeometry(0.03, 0.03, 160, 6), railM, -7.0, DECK_Y + yy, -60).rotation.x = Math.PI / 2;
  for (let z = 18; z > -140; z -= 1.6) addD(new THREE.CylinderGeometry(0.045, 0.045, 1.25, 6), railM, -7.0, DECK_Y + 0.63, z, 0.01);
  const corr = stripeTex(['#c8372d', '#9e2a22'], 40, 512, 16);
  const corrB = stripeTex(['#2f6fb0', '#24578c'], 40, 512, 16);
  for (let i = 0; i < 12; i++) for (let j = 0; j < 3; j++) {
    const mat = new THREE.MeshToonMaterial({ color: 0xffffff, map: (i * 3 + j) % 7 === 3 ? corrB : corr });
    addD(new THREE.BoxGeometry(2.44, 2.55, 12.0), mat, -3.4, DECK_Y + 1.42 + j * 2.6, 12 - i * 12.4, 0.02);
  }
  addD(new THREE.BoxGeometry(5, 0.6, 3), toon('#e8e0d0'), -0.5, DECK_Y + 0.45, 6, 0.015);

  // whales + splash particles
  const whales = [makeWhale(1.3, 1), makeWhale(1.15, 2), makeWhale(1.0, 3), makeWhale(1.2, 4)];
  whales.forEach((w) => g.add(w.outer));
  const NP = 900;
  const spl = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1), cel('#ffffff'), NP);
  spl.frustumCulled = false; spl.userData.noInk = true; g.add(spl);
  const foamRing = []; for (let i = 0; i < 4; i++) { const f = new THREE.Mesh(new THREE.RingGeometry(0.6, 1, 40), glow(1.2, 1.25, 1.3, { transparent: true, opacity: 0.8 })); f.rotation.x = -Math.PI / 2; f.userData.noInk = true; g.add(f); foamRing.push(f); }
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), v3 = new THREE.Vector3(), s3 = new THREE.Vector3();

  g.add(new THREE.HemisphereLight('#cfeaff', '#2a5a80', 1.25));
  const sun = new THREE.DirectionalLight('#fff4e0', 2.4); sun.position.copy(SUN).multiplyScalar(300); g.add(sun);

  return {
    group: g, fog: new THREE.Fog('#bfe6f7', 220, 1500), bg: null, bloom: 0.3, deck, paint: 2.6,
    cel: { dir: [SUN.x, SUN.y, SUN.z], shade: [0.66, 0.76, 1.0], rim: [0.5, 0.6, 0.75], rimDir: [-0.3, 0.3, 1], rimAmt: 0.6 },
    update(t, cam, TL, def, lt) {
      oceanMat.uniforms.uTime.value = t; oceanMat.uniforms.uCam.value.copy(cam.position);
      ocean.position.set(Math.round(cam.position.x / 5) * 5, 0, Math.round(cam.position.z / 5) * 5);
      deck.position.z = -SHIP_SPEED * t; deck.visible = !(def && def.hideDeck);
      ships.forEach((s, i) => { s.position.z += 0; s.userData.z0 ??= s.position.z; s.position.z = s.userData.z0 - 4 * t; s.position.y = 0.25 * Math.sin(t * 0.8 + i); });
      cg.position.x = t * 1.5;
      let k = 0;
      const evs = (def && def.whales) || [];
      whales.forEach((w, i) => {
        const ev = evs[i];
        if (!ev) { w.outer.visible = false; foamRing[i].visible = false; return; }
        const u = (t - ev.t0) / ev.dur;
        if (u < 0 || u > 1.05) { w.outer.visible = false; } else breach(w, clamp(u), ev);
        // splash events: exit (rising) and re-entry (falling)
        for (const [te, power, sp] of [[ev.t0 + ev.dur * 0.12, 0.8, 1], [ev.t0 + ev.dur * 0.82, 1.3, 2]]) {
          const age = t - te;
          if (age < 0 || age > 1.8) continue;
          const pr = rng(i * 100 + sp * 7);
          const n = Math.floor(160 * power);
          const ox = ev.x + Math.sin(ev.heading) * (sp === 2 ? 0.5 : 0.1) * 12 * w.scale, oz = ev.z + Math.cos(ev.heading) * (sp === 2 ? 0.5 : 0.1) * 12 * w.scale;
          for (let j = 0; j < n && k < NP; j++) {
            const a = pr() * Math.PI * 2, rad = (0.8 + pr() * 2.6) * w.scale;
            const vh = (2 + pr() * 6) * power, vv = (5 + pr() * 11) * power;
            const x = ox + Math.cos(a) * (rad + vh * age), z = oz + Math.sin(a) * (rad + vh * age);
            const y = Math.max(-1, vv * age - 4.9 * age * age);
            const life = clamp(1 - age / (1.2 + pr() * 0.6));
            const sz = (0.25 + pr() * 0.7) * w.scale * power * (0.4 + 0.6 * life) * (y <= -0.9 ? 0 : 1);
            v3.set(x, y, z); s3.set(sz, sz * (1 + 0.6 * clamp(vv * 0.05)), sz); m4.compose(v3, q, s3); spl.setMatrixAt(k++, m4);
          }
        }
        const fr = foamRing[i], fa = t - (ev.t0 + ev.dur * 0.12);
        fr.visible = fa > 0 && fa < ev.dur * 1.3;
        if (fr.visible) { const sc = (3 + fa * 4) * w.scale; fr.scale.set(sc, sc, sc); fr.position.set(ev.x, 0.45, ev.z); fr.material.opacity = 0.8 * clamp(1 - fa / (ev.dur * 1.3)); }
      });
      for (; k < NP; k++) { m4.makeScale(0, 0, 0); spl.setMatrixAt(k, m4); }
      spl.instanceMatrix.needsUpdate = true;
    },
  };
}
export { SHIP_SPEED, DECK_Y };
