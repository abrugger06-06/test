#!/bin/bash
# Encode the v2 promo: work/frames2 (promo.html, 23 s) + work/music2.wav into ../brag.mp4,
# with the poster (a settled end-card frame) baked in as frame 0.
# Usage: scripts/encode2.sh [poster_frame_number]   (default 660 = 22.0 s, after the final lid snap)
set -e
cd "$(dirname "$0")/.."
P=$(printf "%05d" "${1:-660}")
OUT=..
cp "frames2/f$P.png" poster.png
ffmpeg -hide_banner -loglevel error -y -i poster.png -q:v 2 "$OUT/brag.jpg"
mkdir -p enc && cp frames2/f*.png enc/ && cp poster.png enc/f00000.png
# The score is already mastered (-14 LUFS, true peak about -1.3 dBTP), so it goes in untouched.
ffmpeg -hide_banner -loglevel error -y -framerate 30 -i enc/f%05d.png -i music2.wav -ar 48000 \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -r 30 \
  -c:a aac -b:a 192k -movflags +faststart -t 23 "$OUT/brag.mp4"
rm -rf enc poster.png
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames -of compact "$OUT/brag.mp4"
