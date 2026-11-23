"""Soundtrack for the cast teaser, timed from src/teaser.json (one drum bar per character)."""
import json, wave
import numpy as np
T = json.load(open('src/teaser.json'))
SR = 48000; fps = T['fps']
total = (T['intro'] + len(T['cast']) * T['beat'] + T['outro']) / fps
N = int(total * SR); t = np.arange(N) / SR
rng = np.random.default_rng(3)
mix = np.zeros((N, 2))
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
def kick(a=1):
    x = tt(0.4); f = 45 + 110 * np.exp(-x * 32); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 8) * a
def clap(a=1):
    n = rng.standard_normal(int(0.3 * SR)); e = np.exp(-tt(0.3) * 22); return band(n * e, 900, 4000) * a
def hat(a=1):
    return band(rng.standard_normal(int(0.05 * SR)), 7000, 0) * np.exp(-tt(0.05) * 70) * a
def logdrum(fr, a=1):
    x = tt(0.55); f = fr * (1 + 0.6 * np.exp(-x * 35)); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh((np.sin(ph) + 0.35 * np.sin(2 * ph)) * np.exp(-x * 6) * 2.4) * 0.5 * a
def whoosh(d=0.35, f0=400, f1=4000, a=1):
    n = rng.standard_normal(int(d * SR)); out = np.zeros(len(n)); k = 10
    for j in range(k):
        s, e = j * len(n) // k, (j + 1) * len(n) // k; fc = f0 * (f1 / f0) ** (j / (k - 1)); out[s:e] = band(n, fc * 0.6, fc * 1.6)[s:e]
    return out * np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2 * a
def boom(a=1, d=1.6):
    x = tt(d); f = 32 + 90 * np.exp(-x * 14)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.4)
    crack = band(rng.standard_normal(len(x)), 1500, 9000) * np.exp(-x * 30)
    return np.tanh((body + 0.8 * crack) * 1.8) * a
def stab(notes, d=0.9, a=1):
    x = tt(d); s = sum(np.sin(2 * np.pi * n * x) + 0.4 * np.sin(4 * np.pi * n * x) for n in notes)
    return band(s / len(notes), 0, 3000) * np.exp(-x * 3.5) * np.minimum(1, x / 0.01) * a

beat = 60 / T['bpm']
t_cast = T['intro'] / fps
t_out = (T['intro'] + len(T['cast']) * T['beat']) / fps
# intro: drone + riser + slam on "MEET THE CAST"
x = tt(t_cast); add(np.sin(2 * np.pi * 55 * x) * np.minimum(1, x / 0.4) * 0.25, 0)
add(whoosh(0.55, 200, 5000, 0.8), 18 / fps - 0.5); add(boom(0.9), 18 / fps); add(stab([220, 261.6, 329.6], 1.0, 0.5), 18 / fps)
# groove: one bar (4 beats) per character
notes = [55.0, 65.4, 73.4, 82.4, 98.0]
for b in range(int((t_out - t_cast) / beat)):
    tb = t_cast + b * beat
    add(kick(0.9), tb)
    if b % 2 == 1: add(clap(0.45), tb, 1, 0.1)
    add(hat(0.25), tb + beat / 2, 1, -0.2); add(hat(0.15), tb, 1, 0.2)
    if b % 4 in (0, 2): add(logdrum(notes[(b // 4) % 5], 0.8), tb + (0 if b % 4 == 0 else beat * 0.75))
# per-character entrance hits
for i, c in enumerate(T['cast']):
    te = (T['intro'] + i * T['beat']) / fps
    add(whoosh(0.3, 500, 6000, 0.55), te - 0.22, 1, 0.3 if i % 2 else -0.3)
    if c.get('villain'):
        add(boom(1.0, 1.4), te); add(stab([110, 116.5, 164.8], 1.2, 0.45), te)
    else:
        add(boom(0.45, 0.8), te); add(stab([440 * 2 ** (n / 12) for n in (0, 4, 7)][: 2 + i % 2], 0.4, 0.18), te)
# outro: head slams, riser, title boom
for i in range(len(T['cast'])): add(boom(0.25, 0.4), t_out + i * 2.5 / fps, 1, (i % 5 - 2) * 0.2)
t_logo = t_out + 46 / fps
r = tt(t_logo - t_out - 0.2); add(band(rng.standard_normal(len(r)), 2500, 12000) * (r / r[-1]) ** 3 * 0.5, t_out + 0.2)
add(boom(1.3, 2.6), t_logo); add(stab([110, 164.8, 220, 277.2], 2.4, 0.6), t_logo); add(logdrum(55, 1.3), t_logo)
# reverb + master
ir_n = int(1.6 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 4.3); ir /= np.sqrt((ir ** 2).sum())
m = 1 << int(np.ceil(np.log2(N + ir_n)))
for ch in range(2): mix[:, ch] += np.fft.irfft(np.fft.rfft(mix[:, ch], m) * np.fft.rfft(ir, m), m)[:N] * 0.18
mix *= np.clip(np.minimum(t / 0.05, (total - t) / 0.6), 0, 1)[:, None]
mix = np.tanh(mix * 1.4) / np.tanh(1.4); mix /= np.abs(mix).max() + 1e-9; mix *= 0.9
with wave.open('public/teaser_audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print(f'teaser audio ok: {total:.2f}s')
