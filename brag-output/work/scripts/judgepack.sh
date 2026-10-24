#!/bin/bash
# Build the package judges review: frames every 0.25 s on labeled contact sheets + full-res key stills.
set -e
cd "$(dirname "$0")/.."
R=${1:-judge/round}
rm -rf "$R" && mkdir -p "$R/frames"
TS=$(python3 -c "print(' '.join(f'{i*0.25:.2f}' for i in range(80)))")
node scripts/capture.mjs stills "$R/frames" $TS 1.55 6.6 9.95 >/dev/null
python3 - "$R" <<'PY'
import sys, glob
from PIL import Image, ImageDraw, ImageFont
R = sys.argv[1]
fs = sorted(glob.glob(f'{R}/frames/t-*.png'), key=lambda f: float(f.split('t-')[1][:-4]))
grid = [f for f in fs if abs(float(f.split('t-')[1][:-4]) * 4 - round(float(f.split('t-')[1][:-4]) * 4)) < 1e-6]
font = ImageFont.truetype('site/fonts/JetBrainsMono-Bold.ttf', 22)
W, H, C, Rw = 640, 360, 4, 5
for s in range(0, len(grid), C * Rw):
    chunk = grid[s:s + C * Rw]
    sheet = Image.new('RGB', (W * C, (H + 30) * Rw), 'white')
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(chunk):
        x, y = (i % C) * W, (i // C) * (H + 30)
        sheet.paste(Image.open(f).convert('RGB').resize((W, H)), (x, y + 30))
        d.text((x + 8, y + 2), 't = ' + f.split('t-')[1][:-4] + ' s', fill='black', font=font)
    sheet.save(f'{R}/sheet-{s // (C * Rw) + 1}.jpg', quality=88)
keys = ['0.50','1.50','1.55','3.75','6.60','7.75','9.95','12.50','14.00','15.25','18.50','19.50']
for k in keys:
    Image.open(f'{R}/frames/t-{k}.png').convert('RGB').save(f'{R}/key-{k}.jpg', quality=90)
PY
python3 scripts/music.py "$R/music.wav" >/dev/null
ffmpeg -hide_banner -loglevel error -y -i "$R/music.wav" -lavfi "showwavespic=s=2000x300:split_channels=0" "$R/waveform.png"
echo "$R ready: $(ls $R | tr '\n' ' ')"
