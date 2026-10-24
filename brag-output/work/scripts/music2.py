"""Fluxcase Kickstarter promo soundtrack (v2), written as code.

120 BPM (beat 0.5 s, bar 2 s), D minor, 24 s, 48 kHz stereo. Every hit is tied to the picture
(promo.html); the cue list below is the contract between the two.

  0.0-2.5   cold open: sub drone, heartbeat kick, riser, magnet snap + impact at 1.5
  2.5-4.0   snap montage: a snap on 2.75, 3.25, 3.75; snare roll and riser into the drop
  4.0       DROP: title card. Full kit, saw bass, pluck chords (Dm Bb F C)
  7.5       whoosh into the exploded view; clacks at 8.0 (lid), 8.5 (lid magnets), 9.0 (base
            magnets), 9.5 (vials); reverse swell and snap back together at 11.0
  11.5      tip-over scene: thud at 12.0 (tips), knock at 12.75 (back upright)
  14.0      five sizes: tuned impacts as cases land at 14.5, 15.0, 15.5, 16.0, 16.5
  17.5      Kickstarter card: riser, filter sweep, impact on the date at 18.5
  19.5      end card: final chord, sub boom, ring out to 24.0
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
L = np.zeros(N)
R = np.zeros(N)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def place(sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


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
# Cold open
place(sub_drone(2.6), 0.0, 1.0)
for b in (0.0, 0.5, 1.0):
    place(kick(0.55, 0.35), b, 0.8)
place(riser(1.45, 0.8, 200, 3000), 0.05, 1.0)
place(reverse_swell(0.35), 1.15, 1.0)
place(clack(86, 1.6), 1.5, 1.0)
place(impact(1.0), 1.5, 1.0)

# Snap montage
for i, ts in enumerate((2.75, 3.25, 3.75)):
    place(clack([81, 84, 88][i], 1.3), ts, 1.0, pan=(-0.3, 0.0, 0.3)[i])
    place(kick(0.8), ts, 0.7)
place(sub_drone(1.5, 26, 0.8), 2.5, 1.0)
for k in range(8):
    place(snare(0.25 + 0.09 * k), 3.0 + k * 0.125, 1.0)
place(riser(1.5, 1.0, 400, 9000), 2.5, 1.0)

# Main groove 4.0-17.5 (Dm Bb F C), chord per bar
prog = [(38, [62, 65, 69]), (34, [58, 62, 65]), (41, [60, 65, 69]), (36, [60, 64, 67])]
for bar in range(7):          # 4.0 .. 18.0
    t0 = 4.0 + bar * 2.0
    if t0 >= 17.5:
        break
    root, chord = prog[bar % 4]
    place(pad(chord, 2.0, 0.6), t0, 1.0)
    for k in range(4):
        tb = t0 + k * BEAT
        if tb >= 17.5:
            break
        place(kick(1.0), tb, 1.0)
        if k in (1, 3):
            place(clap(1.0), tb, 0.8)
        place(hat(0.8), tb + 0.25, 1.0, pan=0.3)
        place(hat(0.5), tb + 0.125, 1.0, pan=-0.2)
        place(hat(0.4), tb + 0.375, 1.0, pan=-0.2)
        place(bass(root, 0.22, 1.0, 420), tb, 1.0)
        place(bass(root + 12, 0.12, 0.6, 600), tb + 0.25, 1.0)
    for k, off in enumerate((0, 0.75, 1.5)):
        if t0 + off < 17.5:
            place(pluck([n + 12 for n in chord]), t0 + off, 0.9, pan=-0.25 + 0.25 * k)
place(impact(1.1, 26), 4.0, 1.0)
place(clack(88, 1.0), 4.0, 0.8)

# Exploded view
place(whoosh(0.7, 1.0), 7.15, 1.0)
for ts, nt in ((8.0, 81), (8.5, 84), (9.0, 88), (9.5, 91)):
    place(clack(nt, 1.0), ts, 0.9, pan=0.25)
place(reverse_swell(0.6, 1.0), 10.4, 1.0)
place(clack(86, 1.5), 11.0, 1.0)
place(impact(0.6, 33), 11.0, 1.0)

# Tip-over
place(whoosh(0.5, 0.7), 11.3, 1.0)
place(kick(1.2, 0.5), 12.0, 0.9)
place(clack(74, 0.8), 12.0, 0.8)
place(kick(0.9, 0.4), 12.75, 0.8)
place(clack(81, 0.7), 12.75, 0.7)

# Five sizes landing
for i, ts in enumerate((14.5, 15.0, 15.5, 16.0, 16.5)):
    place(impact(0.35, 33 + [0, 3, 5, 7, 10][i]), ts, 1.0, pan=-0.4 + 0.2 * i)

# Kickstarter card: riser, sweep, impact on the date
place(riser(1.0, 1.1, 500, 10000), 17.5, 1.0)
place(whoosh(0.5, 0.8), 17.3, 1.0)
place(impact(1.2, 26), 18.5, 1.0)
place(pad([62, 65, 69, 72], 1.0, 0.8, 0.05), 18.5, 1.0)

# End card: final chord, ring out
place(impact(1.0, 26), 19.5, 1.0)
place(kick(1.3, 0.6), 19.5, 1.0)
place(sub_drone(4.5, 26, 1.1), 19.5, 1.0)
place(pad([50, 57, 62, 65, 69, 76], 4.5, 1.0, 0.02), 19.5, 1.0)
for nt, d in ((74, 0), (77, 0.03), (81, 0.06), (86, 0.09)):
    place(bell(nt, 4.4), 19.5 + d, 1.0, pan=(nt - 80) / 15)

# Room: short stereo reflections
for d, g in ((0.019, 0.16), (0.031, 0.12), (0.053, 0.09), (0.083, 0.06)):
    k = int(d * SR)
    L2, R2 = L.copy(), R.copy()
    L[k:] += R2[:-k] * g
    R[k:] += L2[:-k] * g

mix = np.stack([L, R], axis=1)
f = int(1.0 * SR)
mix[-f:] *= np.linspace(1, 0, f)[:, None] ** 1.5
mix = np.tanh(mix * 1.2)
mix *= 0.89 / np.max(np.abs(mix))
out = sys.argv[1] if len(sys.argv) > 1 else 'music2.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out, DUR, 's')
