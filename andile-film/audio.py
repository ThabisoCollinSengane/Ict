"""Synthesised soundtrack for the ANDILE cold open, driven by timeline.json (same cues as the picture).
Usage: python3 audio.py timeline.json out/audio.wav
"""
import json, sys, wave
import numpy as np

TL = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
SR = 48000
DUR = TL['duration']
N = int(SR * DUR)
T = np.arange(N) / SR
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
BEAT = 60.0 / TL['bpm']
O = next(x['start'] for x in TL['shots'] if x['id'] == 'S02') - 3.0  # offset added by the daylight opening
AMB = TL.get('ambience', {})


def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N:
        return
    s = sig[: max(0, N - i0)] if i0 >= 0 else sig[-i0:]
    i0 = max(i0, 0)
    gl, gr = gain * np.sqrt(0.5 * (1 - pan)), gain * np.sqrt(0.5 * (1 + pan))
    L[i0:i0 + len(s)] += s * gl
    R[i0:i0 + len(s)] += s * gr


def tt(d):
    return np.arange(int(d * SR)) / SR


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo > 0:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi > 0:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))


def gate(t0, t1, fi=0.05, fo=0.15):
    return np.clip((T - t0) / fi, 0, 1) * np.clip((t1 - T) / fo, 0, 1)


def noise(d):
    return rng.standard_normal(int(d * SR))


# ---------------- instruments ----------------
def kick(amp=1.0):
    t = tt(0.35)
    f = 48 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * amp


def logdrum(freq, amp=1.0):
    t = tt(0.6)
    f = freq * (1 + 0.6 * np.exp(-t * 35))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    s *= np.exp(-t * 5.5) * np.minimum(1, t / 0.004)
    return np.tanh(s * 2.2) * 0.55 * amp


def shaker(amp=1.0):
    return band(noise(0.06), 6000, 0) * env_ad(int(0.06 * SR), 0.002, 0.018) * amp


def clap(amp=1.0):
    n = noise(0.25)
    e = np.zeros(len(n))
    for k, o in enumerate([0, 0.011, 0.022]):
        i = int(o * SR); e[i:] += env_ad(len(n) - i, 0.001, 0.012 if k < 2 else 0.09)
    return band(n * e, 900, 3500) * amp


def keys_chord(notes, d, amp=1.0):
    t = tt(d)
    s = np.zeros(len(t))
    for f in notes:
        s += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3)
    s *= (1 - np.exp(-t * 40)) * np.exp(-t * 1.1) * (1 + 0.15 * np.sin(2 * np.pi * 5.5 * t))
    return s / len(notes) * amp


def pad(notes, d, amp=1.0, att=1.2):
    t = tt(d)
    s = np.zeros(len(t))
    for f in notes:
        for det in (-0.004, 0.0, 0.004):
            for h, ha in ((1, 1), (2, 0.35), (3, 0.18), (4, 0.08)):
                s += ha * np.sin(2 * np.pi * f * (1 + det) * h * t + rng.uniform(0, 6))
    s *= np.minimum(1, t / att) * np.minimum(1, (d - t) / 0.8)
    return band(s / (len(notes) * 5), 0, 2600) * amp


def whoosh(d=0.45, f0=400, f1=2600, amp=1.0):
    n = noise(d)
    t = tt(d)
    out = np.zeros(len(n))
    segs = 12
    for k in range(segs):
        a, b = k * len(n) // segs, (k + 1) * len(n) // segs
        fc = f0 * (f1 / f0) ** (k / (segs - 1))
        out[a:b] = band(n, fc * 0.6, fc * 1.6)[a:b]
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return out * e * amp


def impact(s=1.0):
    t = tt(1.4)
    f = 38 + 110 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    crack = band(noise(1.4), 1800, 9000) * np.exp(-t * 40)
    sub = np.sin(2 * np.pi * 32 * t) * np.exp(-t * 2.2) * 0.6
    return np.tanh((body * 1.2 + crack * 0.9 + sub) * 1.6 * s) * 0.9


def thud(s=1.0):
    t = tt(0.8)
    f = 45 + 60 * np.exp(-t * 20)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) + band(noise(0.8), 200, 1200)[:len(t)] * np.exp(-t * 25) * 0.5) * s


def shatter(d=1.2):
    out = np.zeros(int(d * SR))
    for _ in range(40):
        i = int(rng.uniform(0, 0.5) ** 1.6 * SR)
        f = rng.uniform(2500, 7500)
        n = int(rng.uniform(0.05, 0.25) * SR)
        t = np.arange(n) / SR
        g = np.sin(2 * np.pi * f * t) * np.exp(-t * rng.uniform(18, 40)) * rng.uniform(0.2, 0.6)
        out[i:i + n] += g[: len(out) - i]
    return out


def clink():
    t = tt(1.2)
    return sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) for f, a, dcy in ((2093, 0.5, 4), (3322, 0.35, 6), (5274, 0.2, 9), (7040, 0.1, 12)))


def step(surface):
    t = tt(0.25)
    tap = np.sin(2 * np.pi * (90 + 120 * np.exp(-t * 60)) * t) * np.exp(-t * 35)
    if surface == 'wet':
        spl = band(noise(0.25), 1500, 7000) * np.exp(-t * 22) * 0.5
        return tap * 0.6 + spl[:len(tap)]
    return tap + band(noise(0.25), 2500, 6000)[:len(t)] * np.exp(-t * 60) * 0.25


def trombone(f0, f1, d):
    t = tt(d)
    f = (f0 + (f1 - f0) * np.clip(t / d, 0, 1)) * (1 + 0.02 * np.sin(2 * np.pi * 6 * t) * np.clip(t / 0.15, 0, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(k * ph) / k for k in range(1, 9))
    s *= np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.08)
    return band(s, 0, 2200) * 0.5


def mixs(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n)
    for x in xs: o[:len(x)] += x
    return o


def reverb(x, secs=2.2, wet=0.25):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * (6.9 / secs))
    ir = band(ir, 200, 7000)
    ir /= np.sqrt(np.sum(ir ** 2))
    m = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]
    return x + y * wet


# ---------------- music buses ----------------
CH = [[220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 392.0], [164.8, 207.7, 246.9, 329.6]]
LOGN = [55.0, 65.4, 73.4, 82.4, 98.0]


def groove_bus(t0, t1, intensity=1.0):
    bus = np.zeros(N)
    def put(sig, t, g=1.0):
        i = int(t * SR)
        if 0 <= i < N:
            k = min(len(sig), N - i); bus[i:i + k] += sig[:k] * g
    nb = int((t1 - t0) / BEAT) + 1
    for b in range(nb):
        tb = t0 + b * BEAT
        put(kick(0.55), tb)
        if b % 2 == 1:
            put(clap(0.5), tb)
        for s16 in range(4):
            put(shaker(0.25 if s16 % 2 == 0 else 0.4), tb + s16 * BEAT / 4)
    bar = 4 * BEAT
    pat = [(0, 0), (3, 2), (6, 1), (10, 3), (11, 2), (14, 0)]
    for k in range(int((t1 - t0) / bar) + 1):
        tb = t0 + k * bar
        put(keys_chord(CH[k % 4], bar, 0.32), tb)
        for s16, n in pat:
            put(logdrum(LOGN[(n + k) % 5], 0.85 * intensity), tb + s16 * BEAT / 4)
    return bus * gate(t0, t1, 0.02, 0.05)


music = np.zeros(N)
for sec in TL['music']:
    a, b, kind = sec['t0'], sec['t1'], sec['kind']
    if kind == 'pad':
        pz = pad([110, 164.8, 196, 246.9, 261.6], b - a + 0.8, 0.95, 0.6); i = int(a * SR)
        music[i:i + len(pz)] += pz[: N - i]
    elif kind == 'seaPad':
        pz = pad([146.8, 220.0, 293.7, 370.0, 440.0], b - a + 0.6, 0.8, 0.5); i = int(a * SR)
        music[i:i + len(pz)] += pz[: N - i]
        for k in range(int((b - a) / (BEAT / 2))):
            f = [587.3, 740.0, 880.0, 1108.7, 880.0, 740.0][k % 6]; tp = tt(0.5)
            pl = (np.sin(2 * np.pi * f * tp) + 0.4 * np.sin(4 * np.pi * f * tp)) * np.exp(-tp * 9) * 0.16
            j = int((a + k * BEAT / 2) * SR); music[j:j + len(pl)] += pl[: N - j]
    elif kind == 'muffled':
        g = groove_bus(a, b)
        music += band(g, 0, 260) * 0.55
    elif kind == 'groove':
        music += groove_bus(a, b) * 0.9
    elif kind == 'grooveLow':
        g = groove_bus(a, b)
        x = np.clip((T - a) / (b - a), 0, 1)
        music += (g * (1 - x) + band(g, 0, 420) * x) * 0.85
    elif kind == 'tension':
        d = b - a
        t = tt(d)
        drone = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 55.7 * t) + 0.25 * np.sin(2 * np.pi * 880 * t) * np.clip(t / d, 0, 1)) * np.minimum(1, t / 0.3)
        music[int(a * SR):int(a * SR) + len(t)] += drone * 0.22
        for hb in (0.35, 0.62, 1.05, 1.32):
            music[int((a + hb) * SR):int((a + hb) * SR) + int(0.35 * SR)] += thud(0.5)[: int(0.35 * SR)]
    elif kind == 'fight':
        bus = np.zeros(N)
        def put(sig, t, g=1.0):
            i = int(t * SR)
            if 0 <= i < N:
                k = min(len(sig), N - i); bus[i:i + k] += sig[:k] * g
        tdrum = a
        while tdrum < 19.3 + O:
            slow = 14.45 + O < tdrum < 15.6 + O or 17.3 + O < tdrum < 18.9 + O
            step16 = BEAT / (1 if slow else 4)
            k = int(round((tdrum - a) / (BEAT / 4)))
            acc = 1.0 if k % 4 == 0 else 0.55
            put(thud(0.45 * acc), tdrum)
            if k % 8 in (0, 3, 6):
                put(logdrum(LOGN[k % 5], 0.7), tdrum)
            tdrum += step16
        t = tt(b - a)
        bus[int(a * SR):int(a * SR) + len(t)] += np.tanh(np.sin(2 * np.pi * 55 * t) * 3) * 0.12 * np.clip((19.35 + O - (a + t)) / 0.2, 0, 1)
        music += bus
    elif kind == 'comic':
        for ts, f0, f1, d in ((21.25 + O, 233, 220, 0.5), (21.8 + O, 220, 164, 0.9)):
            tb = trombone(f0, f1, d); i = int(ts * SR); music[i:i + len(tb)] += tb
    elif kind == 'finale':
        p = pad([110, 164.8, 220, 261.6, 329.6, 392], b - a, 0.7, 0.9)
        music[int(a * SR):int(a * SR) + len(p)] += p
        g = groove_bus(a, 27.0 + O) * np.clip((27.0 + O - T) / 1.0, 0, 1)
        music += g * 0.7
music = reverb(music, 1.8, 0.22)
add(music, 0, 0.8)

# ---------------- ambience ----------------
sea0, sea1 = AMB.get('sea', [0, 3.0])
oce = band(noise(DUR), 80, 1400) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.33 * T + 1)) * gate(sea0, sea1 + 0.05, 0.4, 0.25)
add(band(noise(DUR), 150, 1800) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.21 * T)) * gate(sea0, 3.0, 0.3, 0.1), 0, 0.14, -0.3)
add(oce, 0, 0.42)
rain = band(noise(DUR), 1400, 9000)
rr = AMB.get('rain', [[3.0, 7.55], [26.0, 30.0]])
rmask = gate(rr[0][0], rr[0][1], 0.05, 0.12) + gate(rr[1][0], rr[1][1], 0.08, 0.8)
add(rain * rmask, 0, 0.11, -0.2)
add(band(noise(DUR), 1400, 9000) * rmask, 0, 0.11, 0.2)
drops = np.zeros(N)
for _ in range(900):
    tdp = rng.uniform(0, DUR)
    if rmask[int(tdp * SR) % N] > 0.5:
        i = int(tdp * SR); n = 400
        drops[i:i + n] += band(rng.standard_normal(n), 3000, 0)[: N - i] * np.exp(-np.arange(n) / 60)[: N - i]
add(drops, 0, 0.12)
hum = band(noise(DUR), 40, 180) * rmask
add(hum, 0, 0.15)
crowd = band(noise(DUR), 300, 2500) * (gate(7.5 + O, 12.5 + O, 0.2, 0.3) + gate(14.0 + O, 26.0 + O, 0.3, 0.3) * 0.6)
add(crowd, 0, 0.05)

# ---------------- footsteps (same period formula the rig uses) ----------------
for w in TL['walks']:
    p = w['period']
    k = int(np.ceil((w['t0'] / p - 0.25) * 2))
    while True:
        ts = p * (0.25 + k / 2)
        if ts > w['t1']:
            break
        if ts >= w['t0']:
            g = 0.5 if w['char'] == 'thug' else 0.32
            if w['t0'] >= 26 + O:
                g *= max(0.15, 1 - (ts - 26 - O) / 3)
            add(step(w.get('surface', 'floor')), ts, g, 0.15 if k % 2 else -0.15)
        k += 1

# ---------------- cue SFX ----------------
for c in TL['cues']:
    t, ty, s = c['t'], c['type'], c.get('s', 1.0)
    if ty == 'whoosh':
        if c.get('slow'):
            add(whoosh(0.9, 180, 900, 0.9 * s), t)
        elif c.get('rise'):
            add(whoosh(0.5, 300, 4000, 0.9 * s), t)
        else:
            add(whoosh(0.45, 500, 3000, 0.7 * s), t)
    elif ty == 'splash':
        d = 1.6; tp = tt(d)
        body = band(noise(d), 120, 1500) * np.exp(-tp * 2.6) * np.minimum(1, tp / 0.02)
        spray = band(noise(d), 2500, 10000) * np.exp(-tp * 4.5) * 0.5
        add(reverb(np.pad(body + spray + thud(0.5 * s)[: len(tp)] if len(thud()) >= len(tp) else body + spray, (0, SR // 2)), 1.4, 0.25), t, 0.55 * s, -0.4)
    elif ty == 'horn':
        d = 1.9; tp = tt(d)
        ph = 2 * np.pi * 98 * tp
        hn = sum(np.sin(k * ph + 0.3 * k) / k for k in range(1, 12)) + 0.6 * sum(np.sin(k * 1.5 * ph) / k for k in range(1, 8))
        hn *= np.minimum(1, tp / 0.15) * np.minimum(1, (d - tp) / 0.5)
        add(reverb(np.pad(band(hn, 60, 1800) * 0.25, (0, SR)), 2.5, 0.5), t, 0.5 * s, 0.3)
    elif ty == 'impact':
        add(whoosh(0.12, 1500, 5000, 0.5), t - 0.1)
        add(reverb(np.pad(impact(s), (0, SR)), 1.6, 0.35), t, 0.95)
    elif ty == 'land':
        add(reverb(np.pad(mixs(thud(1.4 * s), impact(0.6)), (0, SR // 2)), 1.4, 0.3), t, 0.85)
        add(shatter(), t + 0.02, 0.5, 0.3)
    elif ty == 'door':
        add(whoosh(0.35, 200, 1200, 0.5), t)
        add(thud(0.25), t + 0.28, 1.0)
    elif ty == 'doorBang':
        add(reverb(np.pad(thud(1.2), (0, SR // 2)), 1.2, 0.3), t + 0.12, 0.9)
        add(band(noise(0.3), 600, 3000) * np.exp(-tt(0.3) * 18), t + 0.12, 0.4)
    elif ty == 'slide':
        d = 1.1
        add(band(noise(d), 300, 2200) * np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) * 0.6, t, 0.45, 0.3)
    elif ty == 'clink':
        add(reverb(np.pad(clink(), (0, SR // 2)), 1.2, 0.3), t, 0.45, 0.3)
    elif ty == 'titleHit':
        d = 0.8
        swell = band(noise(d), 3000, 12000) * (tt(d) / d) ** 3
        add(swell, t - d, 0.35)
        add(reverb(np.pad(mixs(impact(0.9), logdrum(55, 1.2)), (0, SR)), 2.4, 0.4), t, 0.85)

# ---------------- master ----------------
fade = np.clip((DUR - T) / 0.7, 0, 1) * np.clip(T / 0.3, 0, 1)
mix = np.stack([L, R], 1) * fade[:, None]
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89
pcm = (mix * 32767).astype(np.int16)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'audio ok: {DUR}s, {len(TL["cues"])} cues, peak normalised -> {OUT}')
