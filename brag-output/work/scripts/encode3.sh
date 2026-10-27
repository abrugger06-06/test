#!/bin/bash
# Encode the v3 lifestyle film: work/frames3 (life.html, 19.5 s) + work/music3.wav into an MP4,
# with the poster (a settled end-card frame) baked in as frame 0.
# Usage: scripts/encode3.sh [poster_frame_number] [out.mp4]   (default 570 = 19.0 s, after the final lid snap; ../brag.mp4)
set -e
cd "$(dirname "$0")/.."
P=$(printf "%05d" "${1:-570}")
OUT=..
MP4="${2:-$OUT/brag.mp4}"
JPG="${MP4%.mp4}.jpg"
cp "frames3/f$P.png" poster.png
ffmpeg -hide_banner -loglevel error -y -i poster.png -q:v 2 "$JPG"
mkdir -p enc && cp frames3/f*.png enc/ && cp poster.png enc/f00000.png
# The score is already mastered (-14 LUFS, true peak about -1.3 dBTP), so it goes in untouched.
ffmpeg -hide_banner -loglevel error -y -framerate 30 -i enc/f%05d.png -i music3.wav -ar 48000 \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -r 30 \
  -c:a aac -b:a 192k -movflags +faststart -t 19.5 "$MP4"
rm -rf enc poster.png
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames -of compact "$MP4"
