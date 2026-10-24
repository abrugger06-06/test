#!/bin/bash
# Encode work/frames + work/music.wav into ../brag.mp4, with the poster frame baked in as frame 0.
# Usage: scripts/encode.sh [poster_frame_number]   (default 585 = 19.5 s, the settled end card)
set -e
cd "$(dirname "$0")/.."
P=$(printf "%05d" "${1:-585}")
OUT=..
cp "frames/f$P.png" poster.png
ffmpeg -hide_banner -loglevel error -y -i poster.png -q:v 2 "$OUT/brag.jpg"
# Frame 0 becomes the poster; every frame keeps its slot, so audio stays in sync.
mkdir -p enc && cp frames/f*.png enc/ && cp poster.png enc/f00000.png
ffmpeg -hide_banner -loglevel error -y -framerate 30 -i enc/f%05d.png -i music.wav \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -r 30 \
  -c:a aac -b:a 192k -movflags +faststart -t 20 "$OUT/brag.mp4"
rm -rf enc poster.png
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames -of compact "$OUT/brag.mp4"
