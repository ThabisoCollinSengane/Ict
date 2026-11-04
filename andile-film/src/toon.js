import * as THREE from 'three';

// 3-step cel ramp shared by every toon material.
const grads = {};
export function gradTex(steps = 3) {
  if (grads[steps]) return grads[steps];
  const vals = steps === 2 ? [95, 255] : steps === 3 ? [72, 165, 255] : [50, 115, 185, 255];
  const t = new THREE.DataTexture(new Uint8Array(vals), vals.length, 1, THREE.RedFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  t.needsUpdate = true;
  return (grads[steps] = t);
}

export function toon(color, o = {}) {
  const m = new THREE.MeshToonMaterial({ color, gradientMap: gradTex(o.steps || 3) });
  if (o.emissive !== undefined) { m.emissive = new THREE.Color(o.emissive); m.emissiveIntensity = o.ei ?? 1; }
  if (o.map) m.map = o.map;
  if (o.emissiveMap) m.emissiveMap = o.emissiveMap;
  if (o.fog === false) m.fog = false;
  return m;
}

// Unlit colour, allowed above 1.0 so bloom picks it up (neon, screens, lamps).
export function glow(r, g, b, o = {}) {
  const m = new THREE.MeshBasicMaterial({ color: new THREE.Color(r, g, b), fog: o.fog ?? true });
  if (o.transparent) { m.transparent = true; m.opacity = o.opacity ?? 1; m.depthWrite = false; }
  if (o.additive) { m.blending = THREE.AdditiveBlending; m.transparent = true; m.depthWrite = false; m.opacity = o.opacity ?? 1; }
  if (o.side) m.side = o.side;
  if (o.map) m.map = o.map;
  return m;
}

// Inverted-hull outline: back faces pushed out along the normal.
const olMats = {};
export function outlineMat(th, color = 0x120c18) {
  const k = th.toFixed(5) + '_' + color;
  if (olMats[k]) return olMats[k];
  return (olMats[k] = new THREE.ShaderMaterial({
    uniforms: { th: { value: th }, col: { value: new THREE.Color(color) } },
    vertexShader: `uniform float th; void main(){ vec3 p = position + normalize(normal) * th; gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0); }`,
    fragmentShader: `uniform vec3 col; void main(){ gl_FragColor = vec4(col, 1.0); }`,
    side: THREE.BackSide,
  }));
}
export function outline(mesh, th = 0.011, color) {
  const o = new THREE.Mesh(mesh.geometry, outlineMat(th, color));
  o.name = 'ol';
  mesh.add(o);
  return o;
}

// Seeded PRNG so every frame is reproducible.
export function rng(seed) {
  let s = (seed >>> 0) || 1;
  return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
}
export function hash1(n) { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

export const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const lerp = (a, b, u) => a + (b - a) * u;
export const EASE = {
  linear: (u) => u,
  inout: (u) => u * u * (3 - 2 * u),
  in: (u) => u * u,
  out: (u) => 1 - (1 - u) * (1 - u),
  snap: (u) => 1 - Math.pow(1 - u, 4),
  back: (u) => { const c = 1.7; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); },
  hold: (u) => (u < 1 ? 0 : 1),
};

export function textTexture(text, o = {}) {
  const w = o.w || 1024, h = o.h || 256;
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const g = cv.getContext('2d');
  g.clearRect(0, 0, w, h);
  g.font = o.font || "italic bold 150px 'DejaVu Serif'";
  g.textAlign = 'center'; g.textBaseline = 'middle';
  const col = o.color || '#ff4fa3';
  for (const [blur, alpha] of [[38, 0.9], [18, 1], [6, 1]]) {
    g.shadowColor = col; g.shadowBlur = blur; g.globalAlpha = alpha;
    g.fillStyle = col; g.fillText(text, w / 2, h / 2 + 6);
  }
  g.shadowBlur = 0; g.globalAlpha = 1; g.fillStyle = o.core || '#ffe6f3';
  g.fillText(text, w / 2, h / 2 + 6);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// Building facades: a base map (facade + dark windows) and a glow map (lit windows only).
export function windowTextures(seed, o = {}) {
  const r = rng(seed);
  const W = 128, H = 256, cols = o.cols || 6, rows = o.rows || 12;
  const base = document.createElement('canvas'); base.width = W; base.height = H;
  const glowC = document.createElement('canvas'); glowC.width = W; glowC.height = H;
  const b = base.getContext('2d'), gg = glowC.getContext('2d');
  b.fillStyle = o.facade || '#8d89b8'; b.fillRect(0, 0, W, H);
  gg.fillStyle = '#000'; gg.fillRect(0, 0, W, H);
  const cw = W / cols, ch = H / rows;
  for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) {
    const lit = r() < (o.lit ?? 0.38);
    const px = x * cw + cw * 0.2, py = y * ch + ch * 0.22, pw = cw * 0.6, ph = ch * 0.56;
    b.fillStyle = o.win || '#3b3866'; b.fillRect(px, py, pw, ph);
    if (lit) {
      const warm = r() < 0.72;
      gg.fillStyle = warm ? '#ffcf7a' : '#9fd4ff';
      gg.globalAlpha = 0.55 + r() * 0.45; gg.fillRect(px, py, pw, ph); gg.globalAlpha = 1;
    }
  }
  const mk = (c) => { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.magFilter = THREE.NearestFilter; return t; };
  return { map: mk(base), glow: mk(glowC) };
}

// Anime cel shader for characters: crisp 2-tone + soft highlight + rim. Light colour never tints the base hue.
export const CEL = {
  uLightDir: { value: new THREE.Vector3(0.3, 0.8, 0.6).normalize() },
  uShadeTint: { value: new THREE.Color(0.5, 0.4, 0.68) },
  uRim: { value: new THREE.Color(0.3, 0.9, 1.1) },
  uRimDir: { value: new THREE.Vector3(1, 0.2, 0).normalize() },
  uRimAmt: { value: 1.0 },
  uExpo: { value: 1.0 },
};
export function cel(color, o = {}) {
  return new THREE.ShaderMaterial({
    fog: true,
    uniforms: { ...THREE.UniformsUtils.clone(THREE.UniformsLib.fog), uColor: { value: new THREE.Color(color) }, uGloss: { value: o.gloss ?? 0 }, ...CEL },
    vertexShader: `#include <common>
      #include <fog_pars_vertex>
      varying vec3 vN; varying vec3 vV;
      void main(){ vec4 mvPosition = modelViewMatrix * vec4(position, 1.0); vN = normalize(normalMatrix * normal); vV = -mvPosition.xyz;
        gl_Position = projectionMatrix * mvPosition;
        #include <fog_vertex>
      }`,
    fragmentShader: `#include <common>
      #include <fog_pars_fragment>
      uniform vec3 uColor, uShadeTint, uLightDir, uRim, uRimDir; uniform float uRimAmt, uGloss, uExpo;
      varying vec3 vN; varying vec3 vV;
      void main(){
        vec3 N = normalize(vN); vec3 V = normalize(vV);
        vec3 L = normalize((viewMatrix * vec4(uLightDir, 0.0)).xyz);
        float d = dot(N, L);
        vec3 c = mix(uColor * uShadeTint, uColor, smoothstep(-0.03, 0.05, d));
        c = mix(c, uColor * 1.15 + 0.03, smoothstep(0.8, 0.84, d) * 0.45);
        if (uGloss > 0.0) { vec3 H = normalize(L + V); c += vec3(1.0) * smoothstep(0.96, 0.975, dot(N, H)) * uGloss; }
        float rim = smoothstep(0.58, 0.68, 1.0 - max(dot(N, V), 0.0));
        vec3 R = normalize((viewMatrix * vec4(uRimDir, 0.0)).xyz);
        c += uRim * rim * smoothstep(-0.1, 0.4, dot(N, R)) * uRimAmt;
        gl_FragColor = vec4(c * uExpo, 1.0);
        #include <fog_fragment>
      }`,
  });
}
