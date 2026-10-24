#!/bin/bash
# Judge package for the v3 lifestyle promo (life.html, 19.5 s): every 0.25 s on labeled sheets, key frames, waveform.
set -e
cd "$(dirname "$0")/.."
R=${1:-judge/l1}
rm -rf "$R" && mkdir -p "$R/frames"
KEYS="0.00 0.30 0.60 1.00 2.25 2.75 3.25 3.75 4.00 5.20 7.00 7.60 9.00 9.80 10.00 11.50 12.00 13.80 14.75 15.00 16.00 17.60 18.10"
TS=$(python3 -c "print(' '.join(f'{i*0.25:.2f}' for i in range(78)))")
PAGE=life.html node scripts/capture.mjs stills "$R/frames" $TS 0.30 0.60 5.20 7.60 9.80 13.80 14.75 17.60 18.10 >/dev/null
python3 - "$R" "$KEYS" <<'PY'
import sys, glob
from PIL import Image, ImageDraw, ImageFont
R, keys = sys.argv[1], sys.argv[2].split()
font = ImageFont.truetype('site/fonts/JetBrainsMono-Bold.ttf', 22)
grid = [f'{R}/frames/t-{i*0.25:.2f}.png' for i in range(78)]
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
for k in keys:
    Image.open(f'{R}/frames/t-{k}.png').convert('RGB').save(f'{R}/key-{k}.jpg', quality=90)
PY
python3 scripts/music3.py "$R/music.wav" >/dev/null
ffmpeg -hide_banner -loglevel error -y -i "$R/music.wav" -lavfi "showwavespic=s=2400x300:split_channels=0" "$R/waveform.png"
echo "$R ready: $(ls $R | grep -c key) keys, $(ls $R | grep -c sheet) sheets"
