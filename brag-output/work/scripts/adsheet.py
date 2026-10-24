"""Contact sheets of the static ads: 10 per sheet, each labeled with its number."""
import sys, glob
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(f'{src}/ad-*.png'))
font = ImageFont.truetype('site/fonts/JetBrainsMono-Bold.ttf', 22)
CW, CH, cols = 360, 640, 5
for s in range(0, len(fs), 10):
    chunk = fs[s:s + 10]
    sheet = Image.new('RGB', (CW * cols, (CH + 34) * 2), 'white')
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(chunk):
        im = Image.open(f).convert('RGB'); w, h = im.size
        im.thumbnail((CW - 10, CH))
        x, y = (i % cols) * CW, (i // cols) * (CH + 34)
        sheet.paste(im, (x + 5, y + 34))
        d.text((x + 6, y + 4), f"{f.split('ad-')[1][:2]}  {w}x{h}", fill='black', font=font)
    sheet.save(f'{out}/ads-sheet-{s // 10 + 1}.jpg', quality=88)
print('ok')
