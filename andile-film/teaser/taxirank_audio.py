"""Taxi-rank stickman test soundtrack, timed from src/taxirank.json: rank ambience, maskandi-style guitar,
taxi hooter + gaatjie whistle, character 'voice blips' under the isiZulu subtitles, and action foley."""
import json, wave
import numpy as np
D = json.load(open('src/taxirank.json'))
SR = 48000; fps = D['fps']; total = D['frames'] / fps
N = int(total * SR); t = np.arange(N) / SR
rng = np.random.default_rng(11)
mix = np.zeros((N, 2))
F = lambda fr: fr / fps
def tt(d): return np.arange(int(d * SR)) / SR
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))
def add(sig, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i + len(sig) <= 0: return
    s = sig[max(0, -i):]; i = max(0, i); s = s[:N - i]
    mix[i:i + len(s), 0] += s * g * np.sqrt(0.5 * (1 - pan)); mix[i:i + len(s), 1] += s * g * np.sqrt(0.5 * (1 + pan))
def pluck(freq, d=0.9, a=1.0):  # Karplus-Strong guitar string
    n = int(SR / freq); buf = rng.uniform(-1, 1, n); out = np.zeros(int(d * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]; buf[i % n] = 0.5 * (buf[i % n] + buf[(i + 1) % n]) * 0.996
    return out * a
def hooter(d=0.45):
    x = tt(d); s = np.sign(np.sin(2 * np.pi * 415 * x)) + np.sign(np.sin(2 * np.pi * 520 * x))
    return band(s, 300, 4000) * np.minimum(1, x / 0.01) * np.minimum(1, (d - x) / 0.03) * 0.25
def whistle(d=0.4):
    x = tt(d); f = 2900 + 250 * np.sign(np.sin(2 * np.pi * 28 * x))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, x / 0.01) * np.minimum(1, (d - x) / 0.05) * 0.25
def blip(f0, d=0.09):
    x = tt(d); f = f0 * (1 + 0.15 * np.sin(x * 60)); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    return band(s, 150, 3500) * np.sin(np.pi * x / d) * 0.35
def whoosh(d=0.3, f0=400, f1=4000, a=1):
    n = rng.standard_normal(int(d * SR)); out = np.zeros(len(n)); k = 10
    for j in range(k):
        s, e = j * len(n) // k, (j + 1) * len(n) // k; fc = f0 * (f1 / f0) ** (j / (k - 1)); out[s:e] = band(n, fc * 0.6, fc * 1.6)[s:e]
    return out * np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2 * a
def step(a=0.3): return band(rng.standard_normal(int(0.06 * SR)), 100, 1500) * np.exp(-tt(0.06) * 60) * a

# ambience: crowd murmur, traffic rumble, distant hoots, birds
x = tt(total)
add(sum(band(rng.standard_normal(N), 250, 1500) * (0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(0.3, 1.2) * x + i)) for i in range(3)) * 0.02, 0)
add(band(rng.standard_normal(N), 30, 200) * 0.06, 0)
for k in range(5): add(hooter(0.2) * 0.25, rng.uniform(1, total - 1), 1, rng.uniform(-1, 1))
for k in range(6):
    xx = tt(0.12); add(np.sin(2 * np.pi * np.cumsum(3500 + 900 * np.sin(xx * 90)) / SR) * np.sin(np.pi * xx / 0.12) * 0.03, rng.uniform(0, total), 1, rng.uniform(-1, 1))
# taxi idle engine until it drives off
idle = band(np.sign(np.sin(2 * np.pi * 32 * x)) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * x)), 30, 400) * 0.06
idle[int(F(438) * SR):] *= np.exp(-np.arange(N - int(F(438) * SR)) / SR * 0.8)
add(idle, 0, 1, -0.5)
xx = tt(total - F(436)); add(band(np.sign(np.sin(2 * np.pi * np.cumsum(40 + 60 * xx) / SR)), 40, 800) * 0.12 * np.exp(-xx * 0.9), F(436), 1, -0.7)
# maskandi-style guitar: fast picked pattern on a I-IV-V loop (ducks under dialogue a little)
beat = 60 / 132 / 2
prog = [[196.0, 246.9, 293.7], [261.6, 329.6, 392.0], [293.7, 370.0, 440.0], [261.6, 329.6, 392.0]]
pat = [0, 2, 1, 2, 0, 1, 2, 1]
i = 0; tb = 0.2
while tb < total - 1.0:
    ch = prog[(i // 16) % 4]; n = ch[pat[i % 8]] * (2 if i % 8 in (2, 6) else 1)
    add(pluck(n, 0.5, 0.18), tb, 1, 0.25)
    if i % 8 == 0: add(pluck(ch[0] / 2, 0.8, 0.22), tb, 1, 0.1)
    i += 1; tb += beat
# hooter + whistle cues
for h in D['hoots']: add(hooter(0.5 if h == 360 else 0.3), F(h), 1.2, -0.5)
for w in D['whistles']: add(whistle(0.45), F(w), 1, -0.4)
# voice blips under subtitles (placeholder for real recorded isiZulu lines)
pitch = {'LEE': 255, 'ANDILE': 150, 'GAATJIE': 120}
pan = {'LEE': 0.4, 'ANDILE': 0.0, 'GAATJIE': -0.5}
for l in D['lines']:
    n_syl = max(2, len(l['zu'].replace(' ', '')) // 3)
    span = F(l['to'] - 6) - F(l['from'])
    for k in range(n_syl):
        at = F(l['from']) + span * k / n_syl
        add(blip(pitch[l['who']] * rng.uniform(0.9, 1.25), 0.07 + 0.04 * rng.random()), at, 1, pan[l['who']])
# foley: footsteps, jumps, run, door slide
for fr in range(22, 110, 10): add(step(0.25), F(fr), 1, 0.4)
for fr in range(122, 172, 11): add(step(0.35) * 1.3, F(fr), 1, 0.6)
add(whoosh(0.25, 600, 4000, 0.4), F(160)); add(whoosh(0.3, 500, 5000, 0.5), F(361))
for fr in range(388, 424, 5): add(step(0.4), F(fr), 1, 0)
xx = tt(0.5); add(band(rng.standard_normal(len(xx)), 400, 3000) * np.sin(np.pi * xx / 0.5) * 0.15, F(428), 1, -0.3)
xx = tt(0.25); add(band(rng.standard_normal(len(xx)), 80, 600) * np.exp(-xx * 20) * 0.5, F(440), 1, -0.3)  # door slam
# master
mix *= np.clip(np.minimum(t / 0.3, (total - t) / 0.8), 0, 1)[:, None]
mix = np.tanh(mix * 1.6) / np.tanh(1.6); mix /= np.abs(mix).max() + 1e-9; mix *= 0.9
with wave.open('public/taxirank.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print(f'taxirank audio ok: {total:.2f}s')
