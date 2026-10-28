"""Fluxcase Kickstarter promo soundtrack (v3, lifestyle cut), written as code.

120 BPM (beat 0.5 s, bar 2 s), D major (D A Bm G), 19.5 s, 48 kHz stereo. Warm and organic: Rhodes-style
keys, claps, shaker, tambourine and open hats, with light foley from each set. The magnet clacks stay the
hero sound. The cue list is the contract with the picture (life.html):

  0.0       full hit on frame 0 (kick, clap, crash, clack); the lid drops in, clack + impact on 1.0
  2.0-4.0   montage, a cut per beat: snap with a quartz clink 2.25; lamp click with the snap 2.75;
            the lid is pulled shut on the case packed in the open pouch 3.25; snap 3.75; fill into the drop
  4.0       DROP + crash: title on the kitchen counter. Lid pops 5.0, snaps 5.5
  6.5-9.5   how it works, groove kept light: clacks 6.75 (lid) and 7.0 (base), glass on 7.25, riser,
            snap and impact on 9.0
  9.5-10.0  the case rolls in on its side (roll rumble) and rocks to rest on 10.0 (knock); close-up cut 11.0
  12.0-13.5 five sizes land on the shelf every 0.375 s (16th grid); full drop-out 14.375-14.5
  14.5      Kickstarter panel + crash; snap, impact and bells on the date at 15.0
  16.0      end card on the shelf + crash + bell; lids lift 17.5, final hit 18.0 (the loudest); ring out
Mix: bass high-passed at 50 Hz, drums shelved down below 80 Hz, music bus ducked by the kick; gained to
-14 LUFS (ffmpeg ebur128) into a 4x-oversampled true-peak limiter.
Usage: python3 music3.py out.wav
"""
import re
import subprocess
import sys
import wave

import numpy as np

SR = 48000
BEAT = 0.5
DUR = 19.5
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
    f = 55 + 120 * np.exp(-t * 30)
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
    """Band-limited sawtooth (PolyBLEP), so high notes do not alias."""
    ph = (f * t) % 1.0
    dt = f / SR
    y = 2 * ph - 1
    a = ph < dt
    x = ph[a] / dt
    y[a] -= x + x - x * x - 1
    b = ph > 1 - dt
    x = (ph[b] - 1) / dt
    y[b] -= x * x + x + x + 1
    return y


def bass(note, dur, g=1.0, cutoff=500):
    t = tt(dur)
    f = midi(note)
    x = saw(f, t) * 0.6 + saw(f * 1.005, t) * 0.4 + np.sin(2 * np.pi * f * t) * 0.6
    env = np.minimum(1, t / 0.005) * np.exp(-t / (dur * 1.2))
    rel = min(len(t), int(0.02 * SR))
    env[-rel:] *= np.linspace(1, 0, rel)
    x = lowpass(x, cutoff * (1 + 2 * np.exp(-t / 0.06)))
    return highpass(highpass(np.tanh(x * env * 1.5), 50), 50) * 0.5 * g


def pluck(notes, dur=0.45, g=1.0):
    t = tt(dur)
    x = np.zeros_like(t)
    for n in notes:
        f = midi(n)
        x += saw(f, t) * 0.5 + np.sin(2 * np.pi * f * t) * 0.5
    x = lowpass(x / len(notes), 5000 * np.exp(-t / 0.15) + 900)
    return x * np.minimum(1, t / 0.003) * np.exp(-t / 0.22) * 0.5 * g


def pad(notes, dur, g=1.0, a=0.3):
    t = tt(dur)
    x = np.zeros_like(t)
    for k, n in enumerate(notes):
        for det in (-0.08, 0.08):
            x += saw(midi(n) * 2 ** (det / 12), t + k * 0.01)
    x = lowpass(x / (2 * len(notes)), 2400)
    env = np.minimum(1, t / a)
    r = int(min(0.8, dur / 2) * SR)
    env[-r:] *= np.linspace(1, 0, r)
    return x * env * 0.25 * g


def sub_drone(dur, note=38, g=1.0):
    t = tt(dur)
    x = np.sin(2 * np.pi * midi(note) * t) + 0.3 * np.sin(2 * np.pi * midi(note + 12) * t)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.2)
    return highpass(highpass(x * env, 50), 50) * 0.35 * g


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
    place(kick(g, dur), t, gain * 0.75, bus='drums')
    KICKS.append((t, g * gain))


def glass(note, g=1.0):
    t = tt(0.4)
    x = sum(np.sin(2 * np.pi * midi(note) * m * t) * np.exp(-t / d) for m, d in ((1, 0.15), (2.4, 0.06), (4.1, 0.03)))
    return x * np.minimum(1, t / 0.001) * 0.25 * g


def crash(g=1.0):
    t = tt(2.0)
    x = highpass(highpass(noise(2.0), 3000), 3000) * np.exp(-t / 0.7) + highpass(noise(2.0), 6000) * np.exp(-t / 0.08)
    return x * 0.35 * g


def lead(note, dur=0.2, g=1.0):
    """A short square-ish lead in the 1-3 kHz band for presence on phone speakers."""
    t = tt(dur)
    f = midi(note)
    # band-limited square: odd harmonics up to 16 kHz, plus a soft octave
    x = sum(np.sin(2 * np.pi * f * h * t) / h for h in range(1, int(16000 / f) + 1, 2)) * (2 / np.pi) * 0.5
    x = lowpass(x + np.sin(2 * np.pi * 2 * f * t) * 0.3, 4000)
    return x * np.minimum(1, t / 0.004) * np.exp(-t / 0.09) * 0.22 * g


def rhodes(notes, dur=0.6, g=1.0):
    """Electric-piano style keys: a bell-ish attack over a warm sine body, with a soft tremolo."""
    t = tt(dur)
    x = np.zeros_like(t)
    for n in notes:
        f = midi(n)
        x += np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.15) \
            + 0.12 * np.sin(2 * np.pi * 3.0 * f * t) * np.exp(-t / 0.05)
    x *= (1 + 0.15 * np.sin(2 * np.pi * 5.5 * t)) / len(notes)
    return x * np.minimum(1, t / 0.004) * np.exp(-t / (dur * 0.6)) * 0.35 * g


def shaker(g=1.0):
    t = tt(0.09)
    return highpass(highpass(noise(0.09), 5000), 5000) * np.minimum(1, t / 0.012) * np.exp(-t / 0.03) * 0.25 * g


def tamb(g=1.0):
    t = tt(0.18)
    jing = sum(np.sin(2 * np.pi * f * t) for f in (6800, 8200, 9600, 11100)) * 0.15
    return (highpass(noise(0.18), 6000) * 0.5 + jing) * np.exp(-t / 0.06) * 0.3 * g


def clink(g=1.0):
    """Ceramic or glass set down on stone."""
    t = tt(0.5)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, d in ((2200, 0.12), (3450, 0.08), (5100, 0.05)))
    return (x * 0.3 + noise(0.5) * np.exp(-t / 0.004) * 0.5) * g


def click(g=1.0):
    """A lamp switch."""
    t = tt(0.06)
    return (noise(0.06) * np.exp(-t / 0.002) + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.01) * 0.6) * 0.7 * g


def zipper(dur=0.25, g=1.0):
    t = tt(dur)
    teeth = (np.sin(2 * np.pi * 95 * t / dur * dur * (1 + t / dur)) > 0.6).astype(float)
    x = highpass(noise(dur), 2500) * (0.3 + 0.7 * teeth) * np.sin(np.pi * t / dur)
    return x * 0.35 * g


def setdown(g=1.0):
    """A plastic case set down on fabric: soft low thud."""
    t = tt(0.25)
    return (np.sin(2 * np.pi * 110 * t) * np.exp(-t / 0.05) + lowpass(noise(0.25), 900) * np.exp(-t / 0.03) * 0.6) * 0.6 * g


def roll(dur=0.5, g=1.0):
    """A plastic case rolling on its side across a wooden desk, slowing down: a low rumble with a seam tick
    once per turn."""
    t = tt(dur)
    k = t / dur
    body = lowpass(noise(dur), 420) * (1 - k) ** 0.6 * 1.6
    phase = np.cumsum(2.0 * (1 - k) ** 1.2 + 0.4) / SR   # turns per second, slowing
    ticks = np.zeros_like(t)
    for n in range(1, int(phase[-1]) + 1):
        i = int(np.searchsorted(phase, n))
        if i < len(t) - 400:
            ticks[i:i + 400] += np.exp(-np.arange(400) / 60.0) * (1 - k[i])
    return (body + lowpass(noise(dur), 2500) * ticks * 1.2) * 0.6 * g


def tap(g=1.0):
    """A fingertip on plastic."""
    t = tt(0.08)
    return (lowpass(noise(0.08), 3000) * np.exp(-t / 0.006) + np.sin(2 * np.pi * 620 * t) * np.exp(-t / 0.015) * 0.5) * 0.6 * g


# Hook 0.0-2.0: a full hit on frame 0
K(0.0, 1.2, 0.45)
place(impact(0.8, 38), 0.0, 1.0)
place(clap(1.0), 0.0, 1.2, bus='drums')
place(crash(0.8), 0.0, 1.0)
place(clack(91, 1.0), 0.0, 1.0)
place(riser(0.95, 0.8, 600, 7000), 0.05, 1.0)
place(clack(86, 1.6), 1.0, 1.0)
place(impact(0.8, 38), 1.0, 1.0)
K(1.0, 1.0, 0.5)

# Montage 2.0-4.0
place(clack(84, 1.4), 2.25, 1.0, pan=-0.3)
place(clink(0.9), 2.25, 1.0, pan=-0.3)   # the lid meeting the case on quartz
place(click(0.8), 2.75, 1.0, pan=0.3)
place(clack(88, 1.4), 2.75, 1.0, pan=0.3)
place(clack(86, 1.4), 3.25, 1.0, pan=0.25)   # the lid pulled shut on the case in the pouch
place(clack(91, 1.5), 3.75, 1.0, pan=0.2)
for k in range(4):
    place(snare(0.3 + 0.15 * k), 3.5 + k * 0.125, 1.0, bus='drums')
place(riser(0.9, 0.8, 400, 9000), 3.1, 1.0)
for j, tc in enumerate((2.0, 2.5, 3.0, 3.5)):   # a keys stab and a clap on every montage cut
    place(rhodes([n + 12 for n in (61, 64, 69)], 0.45, 1.0), tc, 2.5, pan=0.15, bus='music')   # the bar's own chord (A)
    place(clap(0.7), tc, 0.6, pan=-0.2, bus='drums')

# Groove: D A Bm G, a chord per bar, from frame 0 to 18.0; lighter (no kick, no clap) under the 6.5-9.0 explainer.
prog = [(38, [62, 66, 69]), (33, [61, 64, 69]), (35, [62, 66, 71]), (31, [62, 67, 71])]
SKIP_KICK = {0.0, 1.0, 10.0, 14.5}
DROP = (14.375, 14.5)
for bar in range(10):        # 0.0 .. 20.0
    t0 = bar * 2.0
    root, chord = prog[bar % 4]
    for k in range(4):
        tb = t0 + k * BEAT
        if tb >= 18.0:
            continue
        light = 6.5 <= tb < 9.0
        if not light and tb not in SKIP_KICK:
            K(tb)
        if not light and k in (1, 3):
            place(clap(1.0), tb, 1.3, bus='drums')
            place(clap(0.6), tb + 0.012, 0.9, pan=0.35, bus='drums')
        for q in range(4):   # shaker sixteenths
            ts = tb + q * 0.125
            if not (DROP[0] <= ts < DROP[1]):
                place(shaker(1.0 if q % 2 else 0.6), ts, 1.0, pan=-0.35, bus='drums')
        if not (DROP[0] <= tb + 0.25 < DROP[1]):
            place(hat(0.9 if 1.0 <= tb < 4.0 else 0.7, open_=True), tb + 0.25, 1.0, pan=0.3, bus='drums')
            if k in (1, 3):
                place(tamb(1.0), tb + 0.25, 1.0, pan=0.4, bus='drums')
        if k in (0, 2):
            place(bass(root + 12, 0.24, 0.7, 520), tb, 1.0, bus='music')
        if not (DROP[0] <= tb + 0.25 < DROP[1]):
            place(bass(root + 24, 0.14, 0.75, 700), tb + 0.25, 1.0, bus='music')
        if tb >= 1.0 and not light:   # rhodes on the off-beats from the lid close
            place(rhodes([n + 12 for n in chord], 0.4), tb + 0.25, 2.8, pan=-0.2, bus='music')
        if light:
            for j, off in enumerate((0, 0.25)):
                place(glass(chord[(k * 2 + j) % 3] + 12, 1.3), tb + off, 1.0, pan=-0.3 + 0.6 * j, bus='music')
            if k in (0, 2):
                place(kick(0.45, 0.3), tb, 0.6, bus='drums')   # a soft pulse keeps time under the explainer
    if t0 < 18.0:
        place(rhodes([n - 12 for n in chord] + [chord[0]], 1.9), t0, 2.4, bus='music')
        place(pad([n + 12 for n in chord], min(2.0, 18.0 - t0), 1.1), t0, 1.0, bus='music')
        for k, off in enumerate((0, 0.75, 1.5)):
            if t0 + off < 18.0:
                place(pluck([n + 12 for n in chord], dur=0.5), t0 + off, 2.6, pan=-0.25 + 0.25 * k, bus='music')
                place(pluck([n + 24 for n in chord], dur=0.6), t0 + off, 3.2, pan=0.25 - 0.25 * k, bus='music')

# Title drop on 4.0; lid pop 5.0, snap 5.5
place(impact(1.0, 38), 4.0, 1.0)
place(crash(1.0), 4.0, 1.0)
place(clack(93, 0.6), 5.0, 0.7, pan=0.3)
place(clack(86, 1.4), 5.5, 1.0, pan=0.3)

# How it works 6.5-9.5
place(whoosh(0.5, 0.8), 6.3, 1.0)
place(clack(81, 1.6), 6.75, 1.0, pan=-0.2)
place(clack(84, 1.6), 7.0, 1.0, pan=0.2)
for j, nt in enumerate((93, 96, 100, 98)):
    place(glass(nt, 1.4), 7.25 + j * 0.06, 1.0, pan=-0.3 + 0.2 * j)
place(riser(1.0, 0.9, 300, 7000), 8.0, 1.0)
place(clack(86, 1.4), 9.0, 1.0)
place(impact(0.7, 38), 9.0, 1.0)
K(9.0, 1.0, 0.5)

# The roll in, at rest on 10.0
place(roll(0.5, 1.3), 9.5, 1.0, pan=0.2)
K(10.0, 1.0, 0.5)
place(impact(0.45, 33), 10.0, 1.0)
place(setdown(1.8), 10.0, 1.0)   # the case rocks to rest
place(setdown(0.7), 10.15, 1.0)

# Five sizes, every 0.375 s
for i, ts in enumerate((12.0, 12.375, 12.75, 13.125, 13.5)):
    place(impact(0.55, 38 + [0, 2, 4, 5, 7][i]), ts, 1.0, pan=-0.4 + 0.2 * i)
    place(clack(81 + [0, 2, 4, 5, 7][i], 1.1), ts, 1.0, pan=-0.4 + 0.2 * i)
place(riser(0.35, 0.9, 400, 9000), 14.0, 1.0)

# Kickstarter panel 14.5-16.0
place(impact(1.0, 38), 14.5, 1.0)
place(crash(1.0), 14.5, 1.0)
place(clack(93, 0.6), 14.5, 0.7, pan=0.3)
place(clack(86, 1.4), 15.0, 1.0, pan=0.3)
place(impact(0.8, 45), 15.0, 1.0)
place(bell(86, 1.0, 0.9), 15.0, 1.0, bus='music')
place(bell(81, 1.0, 0.6), 15.02, 1.0, pan=-0.3, bus='music')
for k in range(8):
    place(snare(0.25 + 0.1 * k), 15.5 + k * 0.0625, 1.0, bus='drums')
place(riser(0.5, 0.8, 500, 10000), 15.5, 1.0)

# End card 16.0-19.5: lids lift on 17.5, final hit on 18.0
place(impact(0.9, 38), 16.0, 1.0)
place(bell(86, 1.2, 0.9), 16.0, 1.0, bus='music')
place(crash(0.9), 16.0, 1.0)
place(riser(0.5, 0.6, 400, 6000), 17.5, 1.0)
place(clack(93, 0.6), 17.5, 0.7)
place(clack(86, 1.5), 18.0, 1.0)
place(impact(0.7, 38), 18.0, 1.0)
place(crash(0.8), 18.0, 1.0)
K(18.0, 0.7, 0.6)
place(clap(0.9), 18.0, 1.0, bus='drums')
place(rhodes([50, 57, 62, 66, 69], 1.5, 1.4), 18.0, 1.0, bus='music')
place(pad([50, 57, 62, 66, 69, 74], 1.5, 1.2, 0.02), 18.0, 1.0, bus='music')
for nt, d in ((74, 0), (78, 0.03), (81, 0.06), (86, 0.09)):
    place(bell(nt, 1.5, 1.1), 18.0 + d, 1.0, pan=(nt - 80) / 15, bus='music')

# ---------- mix ----------
# Sidechain: the music bus dips under each kick (6 dB, 120 ms recovery).
duck = np.ones(N)
for tk, g in KICKS:
    i = int(tk * SR)
    t = tt(0.25)
    d = 1 - 0.5 * min(1.0, g) * np.exp(-t / 0.12)
    n = min(len(d), N - i)
    duck[i:i + n] = np.minimum(duck[i:i + n], d[:n])
for bb in ('drums', 'music'):
    i0, i1 = int(DROP[0] * SR), int(DROP[1] * SR)
    ramp = np.full(i1 - i0, 0.02); ramp[:480] = np.linspace(1, 0.02, 480)   # down within 10 ms
    BUS[bb][:, i0:i1] *= ramp
    BUS['fx'][:, i0:i1] *= ramp
dr = BUS['drums']
dr = dr - 0.3 * np.stack([lowpass(dr[0], 80), lowpass(dr[1], 80)])   # about -3 dB below 80 Hz
mix = dr * 0.8 + BUS['music'] * duck + BUS['fx']   # drums about 2 dB down into the limiter
mix[0], mix[1] = highpass(mix[0], 35), highpass(mix[1], 35)

# Room: short stereo reflections
for d, g in ((0.019, 0.16), (0.031, 0.12), (0.053, 0.09), (0.083, 0.06)):
    k = int(d * SR)
    Lc, Rc = mix[0].copy(), mix[1].copy()
    mix[0, k:] += Rc[:-k] * g
    mix[1, k:] += Lc[:-k] * g

f = int(0.5 * SR)
mix[:, -f:] *= np.linspace(1, 0, f) ** 1.5
mix[:, :240] *= np.linspace(0, 1, 240)   # 5 ms fade-in so frame 0 cannot click
CEIL, BL, OS = 10 ** (-2.0 / 20), 240, 4   # leaves room for AAC overshoot


def oversample(x):
    """4x band-limited upsampling (FFT zero-padding), used only to find inter-sample peaks."""
    n = x.shape[1]
    X = np.fft.rfft(x, axis=1)
    Y = np.zeros((x.shape[0], n * OS // 2 + 1), complex)
    Y[:, :X.shape[1]] = X
    return np.fft.irfft(Y, n * OS, axis=1) * OS


def limit(x):
    """True-peak limiter: 5 ms blocks on the 4x-oversampled signal, 1 block lookahead, instant attack,
    80 ms release. No clipping; the gain curve alone keeps peaks under the ceiling."""
    nb = N // BL + 1
    a = np.abs(oversample(x)).max(axis=0)
    pk = np.array([a[b * BL * OS:(b + 1) * BL * OS].max() if b * BL < N else 0 for b in range(nb)])
    g = np.minimum(1, CEIL / np.maximum(pk, 1e-9))
    g = np.minimum(g, np.concatenate([g[1:], [1]]))
    g = np.minimum(g, np.concatenate([[1], g[:-1]]))
    rel = np.exp(-BL / SR / 0.08)
    for b in range(1, nb):
        g[b] = min(g[b], g[b - 1] * rel + (1 - rel))
    gs = np.interp(np.arange(N), np.arange(nb) * BL + BL / 2, g)
    return x * gs, g


def write(path, x):
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x.T * 32767).astype('<i2').tobytes())


def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1])


# Gain to -14 LUFS through the limiter (two passes: the limiter's own loss is measured, then made up).
out = sys.argv[1] if len(sys.argv) > 1 else 'music3.wav'
mix /= np.abs(mix).max()
gain = 1.0
for _ in range(3):
    y, g = limit(mix * gain)
    write(out, y)
    lv, tp = lufs(out)
    if abs(lv + 14) < 0.3:
        break
    gain *= 10 ** ((-14 - lv) / 20)
print('wrote', out, DUR, 's', 'LUFS', lv, 'true peak dBTP', tp, 'max GR dB', round(20 * np.log10(g.min()), 1))
print('limiter GR dB, worst block within 0.5 s of each hit:', {t: round(20 * np.log10(g[int(t * SR / BL):int((t + 0.5) * SR / BL)].min() + 1e-9), 1) for t in (0.0, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 9.0, 14.5, 15.0, 16.0, 18.0)})
print('worst block in 2.0-4.0:', round(20 * np.log10(g[int(2.0 * SR / BL):int(4.0 * SR / BL)].min()), 1))
