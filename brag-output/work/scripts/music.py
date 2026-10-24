"""Fluxcase Kickstarter ad soundtrack, written as code.

120 BPM (beat = 0.5 s, bar = 2 s), D major, 20 s, 48 kHz stereo.
Bar map (matches brag-plan.md):
  bar 0  0-2   hook: pad + rising ticks, magnet snap on beat 4 (1.5 s)
  bar 1  2-4   reveal: groove enters
  bar 2-3      how it stays shut
  bar 4-5      five sizes (ticks as each base lands)
  bar 6-7      pulls shut (second snap at 14.5 s)
  bar 8-9      outro: final D chord, ring out
Usage: python3 music.py out.wav
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 120
BEAT = 60 / BPM
DUR = 20.0
N = int(SR * DUR)

L = np.zeros(N)
R = np.zeros(N)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def place(sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def env(n, a, d):
    """Attack in seconds, exponential decay time constant in seconds."""
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def kick(gain=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.002, 0.16) * gain


def hat(gain=1.0, seed=0):
    n = int(0.09 * SR)
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)
    x = np.diff(np.concatenate([[0], x]))  # crude highpass
    x = np.diff(np.concatenate([[0], x]))
    return x * env(n, 0.001, 0.018) * 0.12 * gain


def bass(note, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = midi(note)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    e = env(n, 0.006, length * 0.9)
    rel = int(0.03 * SR)
    e[-rel:] *= np.linspace(1, 0, rel)
    return np.tanh(x * 1.4) * e * 0.5


def marimba(note, length=0.6):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = midi(note)
    x = (
        np.sin(2 * np.pi * f * t) * np.exp(-t / 0.35)
        + 0.5 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t / 0.06)
        + 0.2 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t / 0.02)
    )
    a = int(0.002 * SR)
    x[:a] *= np.linspace(0, 1, a)
    return x * 0.32


def bell(note, length=3.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = midi(note)
    x = (
        np.sin(2 * np.pi * f * t) * np.exp(-t / 1.4)
        + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.5)
        + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.2)
    )
    a = int(0.003 * SR)
    x[:a] *= np.linspace(0, 1, a)
    return x * 0.22


def pad(notes, length, a=0.4):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k, note in enumerate(notes):
        f = midi(note)
        for det in (-0.12, 0.12):
            ff = f * 2 ** (det / 12)
            x += np.sin(2 * np.pi * ff * t + k)
            x += 0.3 * np.sin(4 * np.pi * ff * t + k)
    x /= len(notes) * 2
    e = np.ones(n)
    na = int(a * SR)
    e[:na] = np.linspace(0, 1, na)
    nr = int(min(0.6, length / 2) * SR)
    e[-nr:] *= np.linspace(1, 0, nr)
    return x * e * 0.13


def tick(note, gain=1.0):
    """Magnet tick, tuned to the key: short pitched click."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = midi(note)
    rng = np.random.default_rng(note)
    click = rng.standard_normal(n) * np.exp(-t / 0.002) * 0.4
    tone = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.035)
    return (click + tone) * 0.35 * gain


def snap(gain=1.0):
    """The lid closing: a firmer double click, the second the rebound."""
    s = tick(86, 1.6)
    out = np.zeros(int(0.2 * SR))
    out[: len(s)] += s
    s2 = tick(93, 0.5)
    j = int(0.07 * SR)
    out[j : j + len(s2)] += s2[: len(out) - j]
    return out * gain


# Chords per bar (root for bass, triad for pad). D major.
D, Bm, G, A = (50, [62, 66, 69]), (47, [59, 62, 66]), (43, [59, 62, 67]), (45, [61, 64, 69])
bars = [D, D, Bm, G, A, Bm, G, A, D, D]

# Hook bar: pad only, rising ticks on beats 1-3, snap on beat 4.
place(pad(D[1], 2.0, a=0.5), 0.0, 3.0)
place(bass(38, 1.4), 0.0, 0.6)
for i, nt in enumerate([74, 78, 81]):
    place(tick(nt, 1.2 + 0.3 * i), i * BEAT, 1.0, pan=-0.3 + 0.3 * i)
place(snap(), 3 * BEAT, 2.4)
place(kick(0.8), 3 * BEAT, 0.8)

# Groove: bars 1-7 (2 s to 16 s).
for b in range(1, 8):
    t0 = b * 2.0
    root, triad = bars[b]
    place(pad(triad, 2.0, a=0.05), t0, 0.7)
    for k in range(4):
        tb = t0 + k * BEAT
        place(kick(1.0 if k in (0, 2) else 0.7), tb, 0.9)
        place(hat(1.0, seed=b * 8 + k), tb + BEAT / 2, 1.0, pan=0.35)
        if b >= 4:
            place(hat(0.5, seed=b * 8 + k + 100), tb + BEAT / 4 * 3, 1.0, pan=0.35)
    # bass: root on 1, octave pickup on the and of 2, root on 3
    place(bass(root, 0.45), t0, 1.0)
    place(bass(root + 12, 0.22), t0 + 1.5 * BEAT, 0.8)
    place(bass(root, 0.45), t0 + 2 * BEAT, 1.0)
    place(bass(root + 7, 0.22), t0 + 3.5 * BEAT, 0.7)

# Marimba melody (D major pentatonic), 8th-note grid, bars 1-7.
mel = {
    1: [74, None, 78, None, 81, None, 78, 76],
    2: [74, None, 71, None, 74, 76, 78, None],
    3: [79, None, 78, None, 74, None, 71, None],
    4: [76, None, 73, None, 76, 78, 81, None],
    5: [78, None, 74, 78, 81, None, 83, None],
    6: [83, 81, 79, None, 78, None, 74, None],
    7: [76, 78, 81, None, 85, None, 88, None],
}
for b, line in mel.items():
    for k, nt in enumerate(line):
        if nt is not None:
            place(marimba(nt), b * 2.0 + k * BEAT / 2, 1.0, pan=-0.25)

# SFX on the grid, under the music.
place(tick(81, 0.8), 2.0, 0.8)  # reveal pull-back lands
for i, t in enumerate([5.0, 5.5, 6.0, 6.5]):  # magnets light up
    place(tick([74, 78, 81, 86][i], 0.6), t, 0.8, pan=0.2)
for i in range(5):  # five bases land on beats
    place(tick([74, 76, 78, 81, 83][i], 0.9), 9.5 + i * BEAT, 0.9, pan=-0.4 + 0.2 * i)
for i, nt in enumerate([74, 78, 81]):  # lid swings back down
    place(tick(nt, 0.7 + 0.2 * i), 13.0 + i * BEAT, 0.8, pan=0.3)
place(snap(), 14.5, 1.8)  # second snap shut, beat 2 of bar 7

# Outro: final chord on 16 s, ring out to 20 s.
place(kick(1.2), 16.0, 1.0)
place(bass(38, 3.6), 16.0, 1.0)
place(pad([62, 66, 69, 74], 4.0, a=0.02), 16.0, 1.0)
for nt, dt in [(74, 0), (78, 0.02), (81, 0.04), (86, 0.06)]:
    place(bell(nt, 3.8), 16.0 + dt, 1.0, pan=(nt - 80) / 20)

# Simple stereo room: a few short delays.
for d, g in [(0.023, 0.18), (0.037, 0.14), (0.061, 0.1), (0.089, 0.07)]:
    k = int(d * SR)
    L2, R2 = L.copy(), R.copy()
    L[k:] += R2[:-k] * g
    R[k:] += L2[:-k] * g

mix = np.stack([L, R], axis=1)
# Fade the last 0.4 s to silence.
f = int(0.4 * SR)
mix[-f:] *= np.linspace(1, 0, f)[:, None]
mix = np.tanh(mix * 1.1)
mix *= 0.89 / np.max(np.abs(mix))

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", out, f"{DUR}s")
