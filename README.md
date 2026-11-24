# Nosana #NOSvember — Motion-Graphics Short Video

Generator for a bilingual (EN + ID subtitle) kinetic-text short video about
[Nosana](https://nosana.io) — a DePIN GPU compute network on Solana — built for the
**#NOSvember CreatorChallenge** on Superteam Earn (Creative category).

## Output
- `nosana_nosvember.mp4` — 1080×1920 (9:16), 34s, 30fps, H.264.
- Motion-graphics / kinetic text: relaxed, to-the-point, easy to digest.
- Main text in English, smaller Indonesian subtitle below, brand progress bar.

## How it works
1. `render.py` draws each scene (animated gradient blobs + easing kinetic text +
   dual-language subtitles) into PNG frames with Pillow.
2. ffmpeg stitches frames into the final MP4.

## Run
```bash
pip install pillow          # Pillow only
python3  render_v2.py      # -> frames/*.png (1020 frames)
ffmpeg -framerate 30 -i frames/f_%05d.png \
  -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart \
  nosana_nosvember.mp4
```

## Scenes
Idle GPU → expensive AI compute → Nosana fixes both → decentralized GPU on Solana →
hosts share / builders rent → open-source, no lock-in → you earn, they build →
DePIN but useful → That's Nosana (#NOSvember #CreatorChallenge).

Educational/creative content — not financial advice.
