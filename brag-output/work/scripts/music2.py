"""Fluxcase Kickstarter promo soundtrack (v2), written as code.

120 BPM (beat 0.5 s, bar 2 s), D minor, 24 s, 48 kHz stereo. Every hit is tied to the picture
(promo.html); the cue list below is the contract between the two.

  0.0-3.0   hook: sub drone, heartbeat kick, riser, magnet snap + impact on 1.5, half-time tail
  3.0-4.0   snap montage: cuts on 3.0 / 3.5, snaps on 3.25 / 3.75; snare roll and riser into the drop
  4.0       DROP: title card. Full kit, bass, pluck chords (Dm Bb F C). Lid pops 5.0, snaps 5.5
  6.5-10.5  breakdown (no kick): air as the lid opens 6.5, magnet clacks 7.0 (lid) and 7.5 (base),
            glass ticks as the vials rise 8.0, reverse swell, snap back together on 10.0
  10.5      groove back. Tip-over: whoosh, thud as it lands on its side at 11.0
  13.0      five sizes: tuned impacts as the cases land at 13.5, 14.0, 14.5, 15.0, 15.5; build to 16.5
  16.5      Kickstarter card: hit on 16.5, snare roll 17.0-17.5, impact on the date at 17.5, riser out
  19.0      end card: final chord, sub boom, bells; the five lids snap shut together on 22.0
Mix: subs high-passed at 30 Hz, music bus ducked by the kick, peak limiter with 3 dB headroom.
Usage: python3 music2.py out.wav
"""
import sys
import wave

import numpy as np

SR = 48000
BEAT = 0.5
DUR = 24.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
BUS = {b: np.zeros((2, N)) for b in ('drums', 'music', 'fx')}
KICKS = []


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def place(sig, t, gain=1.0, pan=0.0, bus='fx'):
    i = int(round(t * SR))
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i] * gain
    B = BUS[bus]
    B[0, i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    B[1, i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def lowpass(x, fc):
    """One-pole lowpass; fc may be an array (per sample) for sweeps."""
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = a[i] * acc + (1 - a[i]) * x[i]
        y[i] = acc
    return y


def highpass(x, fc):
    return x - lowpass(x, fc)


def noise(dur):
    return rng.standard_normal(int(dur * SR))


# ---------- instruments ----------
def kick(g=1.0, dur=0.45):
    t = tt(dur)
    f = 45 + 120 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.17)
    click = noise(dur) * np.exp(-t / 0.003) * 0.25
    return np.tanh((x + click) * 1.6) * g


def clap(g=1.0):
    t = tt(0.3)
    env = np.zeros_like(t)
    for d in (0, 0.011, 0.022):
        env += np.where(t >= d, np.exp(-(t - d) / 0.012), 0)
    env += np.where(t >= 0.03, np.exp(-(t - 0.03) / 0.09), 0) * 0.6
    x = highpass(noise(0.3), 900) * env
    return x * 0.5 * g


def hat(g=1.0, open_=False):
    d = 0.25 if open_ else 0.06
    t = tt(d)
    x = highpass(highpass(noise(d), 6000), 6000) * np.exp(-t / (0.08 if open_ else 0.015))
    return x * 0.35 * g


def snare(g=1.0):
    t = tt(0.25)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04)
    x = highpass(noise(0.25), 1500) * np.exp(-t / 0.07)
    return (body * 0.5 + x * 0.6) * g


def saw(f, t):
    ph = (f * t) % 1.0
    return 2 * ph - 1


def bass(note, dur, g=1.0, cutoff=500):
    t = tt(dur)
    f = midi(note)
    x = saw(f, t) * 0.6 + saw(f * 1.005, t) * 0.4 + np.sin(2 * np.pi * f / 2 * t) * 0.6
    env = np.minimum(1, t / 0.005) * np.exp(-t / (dur * 1.2))
    rel = min(len(t), int(0.02 * SR))
    env[-rel:] *= np.linspace(1, 0, rel)
    x = lowpass(x, cutoff * (1 + 2 * np.exp(-t / 0.06)))
    return np.tanh(x * env * 1.5) * 0.5 * g


def pluck(notes, dur=0.45, g=1.0):
    t = tt(dur)
    x = np.zeros_like(t)
    for n in notes:
        f = midi(n)
        x += saw(f, t) * 0.5 + np.sin(2 * np.pi * f * t) * 0.5
    x = lowpass(x / len(notes), 3500 * np.exp(-t / 0.12) + 300)
    return x * np.minimum(1, t / 0.003) * np.exp(-t / 0.22) * 0.5 * g


def pad(notes, dur, g=1.0, a=0.3):
    t = tt(dur)
    x = np.zeros_like(t)
    for k, n in enumerate(notes):
        for det in (-0.08, 0.08):
            x += saw(midi(n) * 2 ** (det / 12), t + k * 0.01)
    x = lowpass(x / (2 * len(notes)), 1400)
    env = np.minimum(1, t / a)
    r = int(min(0.8, dur / 2) * SR)
    env[-r:] *= np.linspace(1, 0, r)
    return x * env * 0.25 * g


def sub_drone(dur, note=26, g=1.0):
    t = tt(dur)
    x = np.sin(2 * np.pi * midi(note) * t) + 0.3 * np.sin(2 * np.pi * midi(note + 12) * t)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.2)
    return x * env * 0.35 * g


def riser(dur, g=1.0, f0=300, f1=7000):
    t = tt(dur)
    k = t / dur
    x = noise(dur)
    x = highpass(lowpass(x, f0 + (f1 - f0) * k ** 2), 200)
    return x * k ** 2.2 * 0.6 * g


def whoosh(dur=0.6, g=1.0):
    t = tt(dur)
    k = t / dur
    env = np.sin(np.pi * k) ** 2
    x = lowpass(noise(dur), 400 + 4000 * np.sin(np.pi * k))
    return x * env * 0.8 * g


def impact(g=1.0, note=26):
    t = tt(1.6)
    f = midi(note) * (1 + 1.5 * np.exp(-t * 10))
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.5)
    crack = highpass(noise(1.6), 2000) * np.exp(-t / 0.05) * 0.5
    tail = lowpass(noise(1.6), 1200) * np.exp(-t / 0.4) * 0.25
    return np.tanh((boom + crack + tail) * 1.4) * 0.8 * g


def clack(note=86, g=1.0):
    """The magnet snap: hard click plus a short tuned ring."""
    t = tt(0.25)
    click = noise(0.25) * np.exp(-t / 0.0015) * 0.8
    ring = np.sin(2 * np.pi * midi(note) * t) * np.exp(-t / 0.05)
    body = np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.03)
    return (click + ring * 0.5 + body * 0.6) * 0.6 * g


def bell(note, dur=4.0, g=1.0):
    t = tt(dur)
    f = midi(note)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t / 1.6) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.5)
         + 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.2))
    return x * np.minimum(1, t / 0.003) * 0.25 * g


def reverse_swell(dur=0.5, g=1.0):
    t = tt(dur)
    x = lowpass(noise(dur), 2500) * (t / dur) ** 3
    return x * 0.7 * g


# ---------- arrangement ----------
def K(t, g=1.0, dur=0.45, gain=1.0):
    """A kick on the drum bus; also keys the sidechain duck."""
    place(kick(g, dur), t, gain, bus='drums')
    KICKS.append((t, g * gain))


def glass(note, g=1.0):
    t = tt(0.4)
    x = sum(np.sin(2 * np.pi * midi(note) * m * t) * np.exp(-t / d) for m, d in ((1, 0.15), (2.4, 0.06), (4.1, 0.03)))
    return x * np.minimum(1, t / 0.001) * 0.25 * g


# Hook 0.0-3.0
place(sub_drone(3.1), 0.0, 1.0, bus='music')
for b in (0.0, 0.5, 1.0):
    K(b, 0.55, 0.35, 0.8)
place(riser(1.45, 0.8, 200, 3000), 0.05, 1.0)
place(reverse_swell(0.35), 1.15, 1.0)
place(clack(86, 1.6), 1.5, 1.0)
place(impact(1.0), 1.5, 1.0)
K(1.5, 1.2, 0.6)
place(pad([50, 57, 62, 65], 1.5, 0.5, 0.05), 1.5, 1.0, bus='music')
K(2.5, 0.7, 0.4)

# Snap montage 3.0-4.0
for i, ts in enumerate((3.25, 3.75)):
    place(clack([84, 88][i], 1.3), ts, 1.0, pan=(-0.3, 0.3)[i])
    K(ts, 0.8, 0.45, 0.7)
for ts in (3.0, 3.5):
    place(whoosh(0.25, 0.6), ts - 0.1, 1.0)
for k in range(8):
    place(snare(0.25 + 0.09 * k), 3.0 + k * 0.125, 1.0, bus='drums')
place(riser(1.5, 1.0, 400, 9000), 2.5, 1.0)

# Groove: Dm Bb F C, a chord per bar. Full kit 4.0-6.5 and 10.5-19.0; breakdown 6.5-10.5.
prog = [(38, [62, 65, 69]), (34, [58, 62, 65]), (41, [60, 65, 69]), (36, [60, 64, 67])]
for bar in range(8):          # 4.0 .. 20.0
    t0 = 4.0 + bar * 2.0
    root, chord = prog[bar % 4]
    for k in range(4):
        tb = t0 + k * BEAT
        if tb >= 19.0:
            break
        brk = 6.5 <= tb < 10.5
        if not brk:
            K(tb)
            if k in (1, 3):
                place(clap(1.0), tb, 0.8, bus='drums')
            place(hat(0.8), tb + 0.25, 1.0, pan=0.3, bus='drums')
            place(hat(0.5), tb + 0.125, 1.0, pan=-0.2, bus='drums')
            place(hat(0.4), tb + 0.375, 1.0, pan=-0.2, bus='drums')
            place(bass(root, 0.22, 1.0, 420), tb, 1.0, bus='music')
            place(bass(root + 12, 0.12, 0.6, 600), tb + 0.25, 1.0, bus='music')
        else:
            place(hat(0.35), tb + 0.25, 1.0, pan=0.3, bus='drums')
    if t0 < 19.0:
        brk = 6.5 <= t0 < 10.5
        place(pad(chord, min(2.0, 19.0 - t0), 0.9 if brk else 0.6), t0, 1.0, bus='music')
        if brk:
            place(bass(root, 1.9, 0.7, 260), t0, 1.0, bus='music')
        for k, off in enumerate((0, 0.75, 1.5)):
            if t0 + off < 19.0:
                place(pluck([n + 12 for n in chord], g=0.7 if brk else 1.0), t0 + off, 1.15, pan=-0.25 + 0.25 * k, bus='music')
place(impact(1.1, 26), 4.0, 1.0)
place(clack(88, 1.0), 4.0, 0.8)
# Title: the lid pops on 5.0 and the magnets pull it shut on 5.5
place(clack(93, 0.5), 5.0, 0.6, pan=0.3)
place(clack(86, 1.2), 5.5, 1.0, pan=0.3)

# Exploded view 6.5-10.5
place(whoosh(0.6, 0.9), 6.3, 1.0)
place(clack(81, 1.1), 7.0, 1.0, pan=-0.2)
place(clack(84, 1.1), 7.5, 1.0, pan=0.2)
for j, nt in enumerate((93, 96, 100, 98)):
    place(glass(nt), 8.0 + j * 0.06, 0.8, pan=-0.3 + 0.2 * j)
place(riser(0.9, 0.7, 300, 6000), 9.1, 1.0)
place(reverse_swell(0.6, 1.0), 9.4, 1.0)
place(clack(86, 1.6), 10.0, 1.0)
place(impact(0.8, 33), 10.0, 1.0)
K(10.0, 1.1, 0.5)

# Tip-over: lands on its side at 11.0
place(whoosh(0.4, 0.7), 10.65, 1.0)
K(11.0, 1.3, 0.55, 0.9)
place(impact(0.45, 31), 11.0, 1.0)
place(clack(74, 0.8), 11.0, 0.8)

# Five sizes: a tuned impact per landing, then a build into 16.5
for i, ts in enumerate((13.5, 14.0, 14.5, 15.0, 15.5)):
    place(impact(0.4, 33 + [0, 3, 5, 7, 10][i]), ts, 1.0, pan=-0.4 + 0.2 * i)
    place(clack(81 + [0, 3, 5, 7, 10][i], 0.6), ts, 0.7, pan=-0.4 + 0.2 * i)
place(riser(1.0, 1.0, 400, 9000), 15.5, 1.0)
for k in range(4):
    place(snare(0.3 + 0.15 * k), 16.0 + k * 0.125, 1.0, bus='drums')

# Kickstarter card
place(impact(1.1, 26), 16.5, 1.0)
for k in range(8):
    place(snare(0.25 + 0.1 * k), 17.0 + k * 0.0625, 1.0, bus='drums')
place(impact(1.2, 26), 17.5, 1.0)
place(riser(1.0, 0.9, 500, 10000), 18.0, 1.0)

# End card: final chord, ring out; the lids snap on 22.0
place(impact(1.0, 26), 19.0, 1.0)
K(19.0, 1.3, 0.6)
place(sub_drone(5.0, 26, 1.1), 19.0, 1.0, bus='music')
place(pad([50, 57, 62, 65, 69, 76], 5.0, 1.0, 0.02), 19.0, 1.0, bus='music')
for nt, d in ((74, 0), (77, 0.03), (81, 0.06), (86, 0.09)):
    place(bell(nt, 4.9), 19.0 + d, 1.0, pan=(nt - 80) / 15, bus='music')
place(clack(86, 1.2), 22.0, 0.9)
place(bell(86, 2.0, 0.8), 22.0, 1.0)

# ---------- mix ----------
# Sidechain: the music bus dips under each kick (6 dB, 120 ms recovery).
duck = np.ones(N)
for tk, g in KICKS:
    i = int(tk * SR)
    t = tt(0.25)
    d = 1 - 0.5 * min(1.0, g) * np.exp(-t / 0.12)
    n = min(len(d), N - i)
    duck[i:i + n] = np.minimum(duck[i:i + n], d[:n])
mix = BUS['drums'] + BUS['music'] * duck + BUS['fx']
mix[0], mix[1] = highpass(mix[0], 30), highpass(mix[1], 30)

# Room: short stereo reflections
for d, g in ((0.019, 0.16), (0.031, 0.12), (0.053, 0.09), (0.083, 0.06)):
    k = int(d * SR)
    Lc, Rc = mix[0].copy(), mix[1].copy()
    mix[0, k:] += Rc[:-k] * g
    mix[1, k:] += Lc[:-k] * g

f = int(1.0 * SR)
mix[:, -f:] *= np.linspace(1, 0, f) ** 1.5
# Peak limiter: 5 ms blocks, 1 block lookahead, instant attack, 80 ms release; ceiling -3 dBFS.
mix /= np.percentile(np.abs(mix), 99.9) / 0.6
CEIL, BL = 10 ** (-3 / 20), 240
nb = N // BL + 1
pk = np.zeros(nb)
a = np.abs(mix).max(axis=0)
for b in range(nb):
    seg_ = a[b * BL:(b + 1) * BL]
    pk[b] = seg_.max() if len(seg_) else 0
g = np.minimum(1, CEIL / np.maximum(pk, 1e-9))
g = np.minimum(g, np.concatenate([g[1:], [1]]))
rel = np.exp(-BL / SR / 0.08)
for b in range(1, nb):
    g[b] = min(g[b], g[b - 1] * rel + (1 - rel))
gs = np.interp(np.arange(N), np.arange(nb) * BL + BL / 2, g)
mix = np.clip(mix * gs, -CEIL, CEIL).T
out = sys.argv[1] if len(sys.argv) > 1 else 'music2.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out, DUR, 's', 'peak', np.abs(mix).max(), 'gr_min_db', 20 * np.log10(g.min()))
