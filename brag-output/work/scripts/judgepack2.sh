#!/bin/bash
# Judge package for the v2 promo (promo.html, 23 s): every 0.25 s on labeled sheets, key frames, waveform.
set -e
cd "$(dirname "$0")/.."
R=${1:-judge/p1}
rm -rf "$R" && mkdir -p "$R/frames"
KEYS="0.00 1.50 3.25 3.75 4.00 5.12 7.00 7.80 8.50 9.00 10.40 11.00 12.00 12.25 12.60 13.00 15.80 16.75 17.50 18.00 20.60 21.10"
TS=$(python3 -c "print(' '.join(f'{i*0.25:.2f}' for i in range(92)))")
PAGE=promo.html node scripts/capture.mjs stills "$R/frames" $TS 5.12 7.80 10.40 12.60 15.80 16.70 20.60 21.10 >/dev/null
python3 - "$R" "$KEYS" <<'PY'
import sys, glob
from PIL import Image, ImageDraw, ImageFont
R, keys = sys.argv[1], sys.argv[2].split()
font = ImageFont.truetype('site/fonts/JetBrainsMono-Bold.ttf', 22)
grid = [f'{R}/frames/t-{i*0.25:.2f}.png' for i in range(92)]
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
python3 scripts/music2.py "$R/music.wav" >/dev/null
ffmpeg -hide_banner -loglevel error -y -i "$R/music.wav" -lavfi "showwavespic=s=2400x300:split_channels=0" "$R/waveform.png"
echo "$R ready: $(ls $R | grep -c key) keys, $(ls $R | grep -c sheet) sheets"
