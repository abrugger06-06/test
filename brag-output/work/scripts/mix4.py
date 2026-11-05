"""Mix and encode the Fluxcase Kickstarter explainer (voiced cut).

Lays the ten narration takes (work/vo/*.mp3, downloaded from the ElevenLabs flow) over the score (work/music4.wav),
ducks the music under every voice line, masters the mix to -14 LUFS integrated with a limiter ceiling of -2.8 dBTP
(room for AAC overshoot, so the MP4 measures at or below -1 dBTP), encodes work/frames4 + the mix to an MP4 with the
poster (a settled end-card frame) baked in as frame 0, and prints the loudness measured on the encoded file.

Usage, from work/:   python3 scripts/mix4.py                      -> ../fluxcase-explainer.mp4 / .jpg
                     python3 scripts/mix4.py --no-voice OUT.mp4   -> a picture-and-score preview, no narration
Voice placement (file, start in seconds) is the VO table below; it matches CAPS in site/explainer.html.
"""
import os
import re
import subprocess
import sys
import wave

import numpy as np

SR = 48000
DUR = 36.0
N = int(SR * DUR)
POSTER_FRAME = 1050   # 35.0 s: the end card, lids shut, settled
VO = [   # line, voice, file, start
    (1, 'Chris',   'vo/l01a.mp3', 0.10),
    (2, 'Jessica', 'vo/l02a.mp3', 2.05),
    (3, 'River',   'vo/l03b.mp3', 7.30),
    (4, 'Chris',   'vo/l04b.mp3', 12.05),
    (5, 'Jessica', 'vo/l05b.mp3', 15.50),
    (6, 'River',   'vo/l06a.mp3', 19.55),
    (7, 'Chris',   'vo/l07a.mp3', 22.10),
    (8, 'Jessica', 'vo/l08a.mp3', 26.80),
    (10, 'Chris',  'vo/l10b.mp3', 33.00),
]
VO_LUFS = -16.0      # each line is gained to this before placement, so the three voices sit level
DUCK_DB = -10.0      # music under speech
MUSIC_DB = -3.0      # music trim against the voices before the final normalisation
CEIL_DB = -2.8       # the block limiter lands about 0.3 dB over this and AAC adds about 0.9 dB, so the MP4 stays under -1 dBTP


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def decode(path):
    """Any audio file -> float32 stereo at SR, via ffmpeg."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True)
    if r.returncode:
        raise SystemExit(f'ffmpeg could not decode {path}: {r.stderr.decode()[:300]}')
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).T.astype(float)


def lufs(path):
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1])


def write(path, x):
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x.T, -1, 1) * 32767).astype('<i2').tobytes())


def oversample(x, OS=4):
    n = x.shape[1]
    X = np.fft.rfft(x, axis=1)
    Y = np.zeros((x.shape[0], n * OS // 2 + 1), complex)
    Y[:, :X.shape[1]] = X
    return np.fft.irfft(Y, n * OS, axis=1) * OS


def limit(x, ceil_db=CEIL_DB, BL=240, OS=4):
    """True-peak limiter: 5 ms blocks on the 4x-oversampled signal, 1 block lookahead, 80 ms release."""
    ceil = 10 ** (ceil_db / 20)
    n = x.shape[1]
    nb = n // BL + 1
    a = np.abs(oversample(x, OS)).max(axis=0)
    pk = np.array([a[b * BL * OS:(b + 1) * BL * OS].max() if b * BL < n else 0 for b in range(nb)])
    g = np.minimum(1, ceil / np.maximum(pk, 1e-9))
    g = np.minimum(g, np.concatenate([g[1:], [1]]))
    g = np.minimum(g, np.concatenate([[1], g[:-1]]))
    rel = np.exp(-BL / SR / 0.08)
    for b in range(1, nb):
        g[b] = min(g[b], g[b - 1] * rel + (1 - rel))
    gs = np.interp(np.arange(n), np.arange(nb) * BL + BL / 2, g)
    return x * gs, g


def smooth_env(e, attack=0.02, release=0.35):
    """One-pole attack/release follower on a rectified envelope."""
    ka, kr = np.exp(-1 / (SR * attack)), np.exp(-1 / (SR * release))
    y = np.empty_like(e)
    acc = 0.0
    for i in range(len(e)):
        v = e[i]
        acc = ka * acc + (1 - ka) * v if v > acc else kr * acc + (1 - kr) * v
        y[i] = acc
    return y


def main():
    no_voice = '--no-voice' in sys.argv
    vo_dir = 'vo'
    argv = sys.argv[1:]
    if '--vo-dir' in argv:   # another folder of the same file names (used to test the mix stage with stand-in audio)
        i = argv.index('--vo-dir'); vo_dir = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    skip_encode = '--audio-only' in argv
    args = [a for a in argv if not a.startswith('--')]
    out_mp4 = args[0] if args else ('explainer-novoice-preview.mp4' if no_voice else '../fluxcase-explainer.mp4')
    out_jpg = os.path.splitext(out_mp4)[0] + '.jpg'
    music = decode('music4.wav')[:, :N]
    if music.shape[1] < N:
        music = np.pad(music, ((0, 0), (0, N - music.shape[1])))

    vo = np.zeros((2, N))
    if not no_voice:
        files = [os.path.join(vo_dir, os.path.basename(f)) for _, _, f, _ in VO]
        missing = [f for f in files if not os.path.exists(f)]
        if missing:
            raise SystemExit('missing narration files: ' + ', '.join(missing) + '\n(download the takes from the ElevenLabs flow into work/vo/, or pass --no-voice for a preview)')
        tmp = os.path.join(vo_dir, '_tmp.wav')
        for (line, voice, _, t0), f in zip(VO, files):
            x = decode(f)
            # trim leading/trailing silence below -50 dBFS, then gain the line to VO_LUFS (measured on the trimmed clip)
            a = np.abs(x).max(axis=0)
            idx = np.where(a > 10 ** (-50 / 20))[0]
            x = x[:, max(0, idx[0] - int(0.01 * SR)):min(x.shape[1], idx[-1] + int(0.05 * SR))]
            write(tmp, x)
            lv, _ = lufs(tmp)
            x = x * 10 ** ((VO_LUFS - lv) / 20)
            i = int(round(t0 * SR))
            n = min(x.shape[1], N - i)
            vo[:, i:i + n] += x[:, :n]
            print(f'line {line:2d} {voice:8s} {f}  at {t0:6.2f} s  len {x.shape[1] / SR:5.2f} s  (gain {VO_LUFS - lv:+.1f} dB)')
        os.remove(tmp)
    # duck the music under the voices
    env = smooth_env(np.abs(vo).max(axis=0))
    thr = 10 ** (-40 / 20)
    duck = 1 - (1 - 10 ** (DUCK_DB / 20)) * np.clip(env / thr, 0, 1)
    mix = music * duck * 10 ** (MUSIC_DB / 20) + vo
    mix[:, :240] *= np.linspace(0, 1, 240)
    f = int(0.5 * SR)
    mix[:, -f:] *= np.linspace(1, 0, f) ** 1.5

    # master: gain to -14 LUFS through the true-peak limiter (measured with ffmpeg ebur128)
    mix /= max(1e-9, np.abs(mix).max())
    gain = 1.0
    for _ in range(4):
        y, g = limit(mix * gain)
        write('mix4.wav', y)
        lv, tp = lufs('mix4.wav')
        if abs(lv + 14) < 0.2:
            break
        gain *= 10 ** ((-14 - lv) / 20)
    print(f'mix4.wav  LUFS {lv:.1f}  true peak {tp:.1f} dBTP  max GR {20 * np.log10(g.min()):.1f} dB')
    if skip_encode:
        return

    # encode
    nframes = len([f for f in os.listdir('frames4') if f.startswith('f') and f.endswith('.png')])
    if nframes < N // (SR // 30):
        raise SystemExit(f'frames4 holds {nframes} frames, expected {N // (SR // 30)}')
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', f'frames4/f{POSTER_FRAME:05d}.png', '-q:v', '2', out_jpg])
    os.makedirs('enc4', exist_ok=True)
    for f in os.listdir('enc4'):
        os.remove(os.path.join('enc4', f))
    for f in sorted(os.listdir('frames4')):
        if f.endswith('.png'):
            os.link(os.path.join('frames4', f), os.path.join('enc4', f))
    os.remove('enc4/f00000.png')
    os.link(f'frames4/f{POSTER_FRAME:05d}.png', 'enc4/f00000.png')
    r = run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-framerate', '30', '-i', 'enc4/f%05d.png', '-i', 'mix4.wav', '-ar', '48000',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', '30',
             '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', str(DUR), out_mp4])
    if r.returncode:
        raise SystemExit('encode failed: ' + r.stderr[-500:])
    for f in os.listdir('enc4'):
        os.remove(os.path.join('enc4', f))
    os.rmdir('enc4')
    lv, tp = lufs(out_mp4)
    print(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames', '-of', 'compact', out_mp4]).stdout.strip())
    print(f'{out_mp4}: integrated {lv:.1f} LUFS, true peak {tp:.1f} dBTP (AAC, measured with ffmpeg ebur128); poster {out_jpg}')


if __name__ == '__main__':
    main()
