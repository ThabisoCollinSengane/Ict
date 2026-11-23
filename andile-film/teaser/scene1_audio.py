"""Scene 1 soundtrack, timed from src/scene1.json: nightmare (rings, drone, heartbeat, espeak VO) -> wake (office room tone)."""
import json, wave, subprocess, tempfile, os
import numpy as np
S = json.load(open('src/scene1.json'))
SR = 48000; fps = S['fps']; total = S['frames'] / fps
N = int(total * SR); t = np.arange(N) / SR
rng = np.random.default_rng(7)
mix = np.zeros((N, 2)); wet = np.zeros((N, 2))
F = lambda fr: fr / fps
def tt(d): return np.arange(int(d * SR)) / SR
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))
def add(sig, at, g=1.0, pan=0.0, rev=0.0):
    i = int(at * SR)
    if i >= N or i + len(sig) <= 0: return
    s = sig[max(0, -i):]; i = max(0, i); s = s[:N - i]
    L, R = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    mix[i:i + len(s), 0] += s * g * L; mix[i:i + len(s), 1] += s * g * R
    if rev: wet[i:i + len(s), 0] += s * g * rev * L; wet[i:i + len(s), 1] += s * g * rev * R
def env(x, a, r): return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x * r)
# SA-style telephone ring: 400+450 Hz dual tone, 0.4 on / 0.2 off / 0.4 on
def ring(a=1, detune=1.0):
    x = tt(1.0); tone = np.sin(2 * np.pi * 400 * detune * x) + np.sin(2 * np.pi * 450 * detune * x)
    gate = ((x < 0.4) | ((x > 0.6) & (x < 1.0))).astype(float); gate = band(gate, 0, 200)
    return band(tone * gate, 300, 3500) * 0.3 * a
def heart(a=1):
    x = tt(0.5); f = 40 + 30 * np.exp(-x * 30); th = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(x, 0.004, 14)
    x2 = tt(0.35); f2 = 36 + 20 * np.exp(-x2 * 30); dub = np.sin(2 * np.pi * np.cumsum(f2) / SR) * env(x2, 0.004, 16) * 0.7
    out = np.zeros(int(0.6 * SR)); out[:len(th)] += th; o = int(0.22 * SR); out[o:o + len(dub)] += dub
    return np.tanh(out * 2) * a
def boom(a=1, d=1.6):
    x = tt(d); f = 30 + 80 * np.exp(-x * 12)
    return np.tanh((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.2) + 0.7 * band(rng.standard_normal(len(x)), 1500, 9000) * np.exp(-x * 28)) * 1.8) * a
def whoosh(d=0.4, f0=300, f1=5000, a=1):
    n = rng.standard_normal(int(d * SR)); out = np.zeros(len(n)); k = 12
    for j in range(k):
        s, e = j * len(n) // k, (j + 1) * len(n) // k; fc = f0 * (f1 / f0) ** (j / (k - 1)); out[s:e] = band(n, fc * 0.6, fc * 1.6)[s:e]
    return out * np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2 * a
def tts(text, voice, speed, pitch):
    fd, p = tempfile.mkstemp(suffix='.wav'); os.close(fd)
    subprocess.run(['espeak-ng', '-v', voice, '-s', str(speed), '-p', str(pitch), '-w', p, text], check=True)
    with wave.open(p) as w: sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768.0
    os.remove(p)
    return np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)

# ---------- NIGHTMARE (0 - 500) ----------
end_n = F(S['shots'][4]['to'])
x = tt(end_n)
drone = (np.sin(2 * np.pi * 41 * x) + 0.6 * np.sin(2 * np.pi * 41.7 * x) + 0.3 * np.sin(2 * np.pi * 82.3 * x + np.sin(x * 0.7) * 3))
drone *= np.minimum(1, x / 2.0) * (0.5 + 0.5 * x / end_n)
add(drone * 0.22, 0)
hiss = band(rng.standard_normal(len(x)), 3000, 9000) * (x / end_n) ** 2
add(hiss * 0.06, 0)
# phones: a growing wall of rings across the aisle, detuned and panned
for k in range(60):
    at = rng.uniform(0, F(470)) ** 0.8 * F(470) ** 0.2
    add(ring(rng.uniform(0.3, 1.0), rng.uniform(0.94, 1.06)), at, 0.5 * (0.4 + at / F(470)), rng.uniform(-0.9, 0.9), 0.5)
# heartbeat accelerating through N2-N4
hb = F(100)
while hb < F(470):
    p = (hb - F(100)) / (F(470) - F(100)); add(heart(0.5 + 0.6 * p), hb, 1, 0, 0.2); hb += 0.95 - 0.55 * p
# VO lines
for v in S['vo']:
    at = F(v['at'])
    if v['voice'] == 'robot':
        s = tts(v['text'], 'en-gb+f2', 150, 40); s = np.sign(s) * np.abs(s) ** 0.8
        s = band(s, 350, 3400); add(s, at, 0.9, 0, 0.6)
        add(s, at + 0.12, 0.35, -0.6, 0.6); add(s, at + 0.21, 0.25, 0.6, 0.6)  # echoing operators
    elif v['voice'] == 'leeDream':
        s = tts(v['text'], 'en+f4', 120, 25)
        lo = np.interp(np.arange(int(len(s) * 1.25)) / 1.25, np.arange(len(s)), s)  # octave-ish down
        add(s, at, 0.7, -0.2, 0.9); add(lo, at, 0.7, 0.2, 0.9)
    elif at < end_n:
        s = tts(v['text'], 'en+m3', 175, 55); add(band(s, 200, 5000), at, 0.75, 0, 0.7)
# N3 Lee looming whoosh, N4 riser, N5 glitch + shatter
add(whoosh(1.4, 120, 2000, 0.6), F(196))
r = tt(F(410) - F(290)); add(band(rng.standard_normal(len(r)), 1500, 11000) * (r / r[-1]) ** 3 * 0.35, F(290))
add(np.sin(2 * np.pi * np.cumsum(200 + 1800 * (r / r[-1]) ** 2) / SR) * (r / r[-1]) ** 2 * 0.15, F(290))
for k in range(18):
    at = F(410) + k * 0.13; add(band(rng.standard_normal(int(0.07 * SR)), 800, 8000) * 0.4, at, 1, rng.uniform(-1, 1))
add(boom(1.2, 2.2), F(434), 1, 0, 0.6)  # VUKA
add(whoosh(0.5, 400, 9000, 0.9), F(466))
x = tt(1.2); add(band(rng.standard_normal(len(x)), 2000, 12000) * np.exp(-x * 5) * 0.7, F(472), 1, 0, 0.8)  # white-out shatter

# ---------- AWAKE (500 - 900) ----------
st = F(500); x = tt(total - st)
room = band(rng.standard_normal(len(x)), 80, 900) * 0.05 + band(rng.standard_normal(len(x)), 2000, 6000) * 0.006  # aircon + air
room *= np.minimum(1, x / 1.2)
add(room, st, 1, 0)
murmur = sum(band(rng.standard_normal(len(x)), 250, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(1.5, 4) * x + rng.uniform(0, 6))) for _ in range(4))
add(murmur * 0.012 * np.minimum(1, x / 1.5), st, 1, 0.3)
for k in range(140):  # distant keyboards
    at = st + rng.uniform(0.8, total - st)
    add(band(rng.standard_normal(int(0.02 * SR)), 1500, 7000) * np.exp(-tt(0.02) * 200) * 0.06, at, 1, rng.uniform(-1, 1))
for k in range(3):  # distant phone on another floor
    add(ring(0.12, 1.0), st + 2.0 + k * 3.2, 1, -0.7, 0.4)
add(heart(0.35), st + 0.1); add(heart(0.25), st + 0.95)
# jolt: chair creak, desk bump, papers
j = F(590)
x = tt(0.45); add(band(np.sin(2 * np.pi * np.cumsum(700 + 300 * np.sin(x * 40)) / SR) * env(x, 0.02, 6), 400, 3000) * 0.25, j + 0.05, 1, -0.2)
add(boom(0.5, 0.5), j, 1, -0.1)
for k in range(7): add(whoosh(0.25, 1500, 6000, 0.25), j + 0.03 + k * 0.05, 1, rng.uniform(-0.5, 0.5))
# W3: Andile exhale + LINE-4 hold beeps
x = tt(1.1); add(band(rng.standard_normal(len(x)), 300, 2500) * np.sin(np.pi * x / 1.1) ** 2 * 0.12, F(712))
for k in range(4): add(np.sin(2 * np.pi * 880 * tt(0.12)) * 0.08, F(700) + 0.3 + k * 0.66, 1, 0.4)
# title hit + soft pad
tb = F(816); add(boom(0.9, 2.8), tb, 1, 0, 0.5)
x = tt(total - tb); pad = sum(np.sin(2 * np.pi * f * x) for f in (110, 164.8, 220, 261.6)) / 4
add(band(pad, 0, 1500) * np.minimum(1, x / 0.4) * np.exp(-x * 0.9) * 0.3, tb, 1, 0, 0.5)

# reverb send + master
ir_n = int(2.2 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 3.0); ir /= np.sqrt((ir ** 2).sum())
m = 1 << int(np.ceil(np.log2(N + ir_n)))
for ch in range(2): mix[:, ch] += np.fft.irfft(np.fft.rfft(wet[:, ch], m) * np.fft.rfft(ir, m), m)[:N] * 0.5
mix *= np.clip(np.minimum(t / 0.3, (total - t) / 0.8), 0, 1)[:, None]
mix = np.tanh(mix * 1.5) / np.tanh(1.5); mix /= np.abs(mix).max() + 1e-9; mix *= 0.9
with wave.open('public/s1/scene1.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print(f'scene1 audio ok: {total:.2f}s')
