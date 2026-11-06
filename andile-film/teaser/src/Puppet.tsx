// Live2D-style puppet: a 2D character drawing on a finely subdivided mesh, bent in the vertex shader
// (head tilt/turn about the neck, breathing chest, upper-body lean, jolt), so the art moves without seams.
import React, { useEffect, useMemo, useState } from 'react';
import * as THREE from 'three';
import { continueRender, delayRender, useVideoConfig } from 'remotion';
import { useThree } from '@react-three/fiber';

export type Rig = { neck: number; pivotX: number; waist: number };
export type Pose = {
  headRot?: number; headX?: number; headY?: number; breath?: number; lean?: number;
  squash?: number; tint?: [number, number, number]; tintAmt?: number; bright?: number; alpha?: number; glow?: [number, number, number];
};

const VS = `
uniform float uW, uH, uNeck, uWaist, uHeadRot, uBreath, uLean, uSquash; uniform vec2 uPivot, uHeadOff;
varying vec2 vUv;
vec2 rot(vec2 p, vec2 c, float a){ vec2 d = (p - c) * vec2(uW, uH); float s = sin(a), co = cos(a); d = vec2(co*d.x - s*d.y, s*d.x + co*d.y); return c + d / vec2(uW, uH); }
void main(){
  vUv = uv; vec2 p = uv;
  float wU = smoothstep(uWaist - 0.06, uWaist + 0.06, uv.y);
  float wH = smoothstep(uNeck - 0.03, uNeck + 0.015, uv.y);
  float chest = wU * (1.0 - wH);
  p.x = mix(p.x, uPivot.x + (p.x - uPivot.x) * (1.0 + 0.022 * uBreath), chest);
  p.y += 0.006 * uBreath * wU;
  p = mix(p, rot(p, vec2(uPivot.x, uWaist), uLean), wU);
  vec2 pivotNow = mix(uPivot, rot(uPivot, vec2(uPivot.x, uWaist), uLean), 1.0);
  p = mix(p, rot(p, pivotNow, uHeadRot) + uHeadOff, wH);
  p.y = mix(p.y, p.y * (1.0 - uSquash), 1.0);
  gl_Position = projectionMatrix * modelViewMatrix * vec4((p.x - 0.5) * uW, (p.y - 0.5) * uH, 0.0, 1.0);
}`;
const FS = `
uniform sampler2D uTex; uniform vec3 uTint, uGlow; uniform float uTintAmt, uBright, uAlpha; varying vec2 vUv;
void main(){
  vec4 c = texture2D(uTex, vUv);
  vec3 col = c.rgb * uBright;
  col = mix(col, col * uTint, uTintAmt);
  float edge = smoothstep(0.9, 0.2, c.a) * c.a * 2.0;
  col += uGlow * edge;
  gl_FragColor = vec4(col, c.a * uAlpha);
  #include <colorspace_fragment>
}`;

const cache: Record<string, THREE.Texture> = {};
// Textures load async; the ThreeCanvas only redraws on frame change, so redraw once the texture arrives
// and only then release the render hold.
const useTex = (src: string) => {
  const [tex, setTex] = useState<THREE.Texture | null>(cache[src] || null);
  const [handle] = useState(() => (cache[src] ? null : delayRender('texture ' + src)));
  const { advance } = useThree();
  useEffect(() => {
    if (cache[src]) { setTex(cache[src]); return; }
    new THREE.TextureLoader().load(src, (t) => {
      t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; cache[src] = t; setTex(t);
    }, undefined, () => { if (handle !== null) continueRender(handle); });
  }, [src]);
  useEffect(() => {
    if (!tex) return;
    advance(performance.now());
    if (handle !== null) requestAnimationFrame(() => continueRender(handle));
  }, [tex]);
  return tex;
};

// x,y: top-left of the sprite box in composition pixels; h: displayed height in pixels
export const Puppet: React.FC<{ src: string; x: number; y: number; h: number; rig: Rig; pose: Pose; z?: number; flip?: boolean }> =
  ({ src, x, y, h, rig, pose, z = 0, flip = false }) => {
    const { width, height } = useVideoConfig();
    const tex = useTex(src);
    const geo = useMemo(() => new THREE.PlaneGeometry(1, 1, 28, 72), []);
    const mat = useMemo(() => new THREE.ShaderMaterial({
      vertexShader: VS, fragmentShader: FS, transparent: true, depthWrite: false, depthTest: false,
      uniforms: {
        uTex: { value: null }, uW: { value: 1 }, uH: { value: 1 }, uNeck: { value: 0.86 }, uWaist: { value: 0.5 }, uPivot: { value: new THREE.Vector2(0.5, 0.86) },
        uHeadOff: { value: new THREE.Vector2() }, uHeadRot: { value: 0 }, uBreath: { value: 0 }, uLean: { value: 0 }, uSquash: { value: 0 },
        uTint: { value: new THREE.Color(1, 1, 1) }, uTintAmt: { value: 0 }, uBright: { value: 1 }, uAlpha: { value: 1 }, uGlow: { value: new THREE.Color(0, 0, 0) },
      },
    }), []);
    if (!tex) return null;
    const img = tex.image as HTMLImageElement;
    const w = (h * img.width) / img.height;
    const U = mat.uniforms;
    U.uTex.value = tex; U.uW.value = w; U.uH.value = h;
    U.uNeck.value = rig.neck; U.uWaist.value = rig.waist; U.uPivot.value.set(rig.pivotX, rig.neck);
    U.uHeadRot.value = pose.headRot ?? 0; U.uHeadOff.value.set(pose.headX ?? 0, pose.headY ?? 0);
    U.uBreath.value = pose.breath ?? 0; U.uLean.value = pose.lean ?? 0; U.uSquash.value = pose.squash ?? 0;
    U.uTint.value.setRGB(...(pose.tint ?? [1, 1, 1])); U.uTintAmt.value = pose.tintAmt ?? 0; U.uBright.value = pose.bright ?? 1;
    U.uAlpha.value = pose.alpha ?? 1; U.uGlow.value.setRGB(...(pose.glow ?? [0, 0, 0]));
    return <mesh geometry={geo} material={mat} renderOrder={z} scale={[flip ? -1 : 1, 1, 1]} position={[x + w / 2 - width / 2, height / 2 - y - h / 2, z]} />;
  };
