#!/usr/bin/env python3.14
"""Nosana #NOSvember short-video generator (motion-graphics / kinetic text).

9:16 vertical, bilingual subtitles (EN main + small ID below), relaxed +
to-the-point tone. Renders per-scene frames with PIL then encodes with ffmpeg.
Output: nosana_video/nosana_nosvember.mp4
"""
import os, math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920           # 9:16
FPS = 30
DUR = 34                    # seconds total
BG      = (8, 12, 18)
NOS     = (0, 209, 255)     # Nosana cyan
NOS2    = (0, 255, 180)     # accent green
WHITE   = (240, 246, 252)
GREY    = (150, 160, 175)
IDCLR   = (170, 180, 195)

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def fb(s): return ImageFont.truetype(FONT_B, s)
def fr(s): return ImageFont.truetype(FONT_R, s)

LOGO = "/home/ubuntu/nosana_video/assets/nosana_logo.png"

# ---- scenes: (en_lines, id_lines) shown as kinetic text
SCENES = [
    (["Your GPU", "is probably", "idle right now."],
     ["GPU-mu mungkin", "sedang menganggur", "saat ini."]),
    (["Meanwhile,", "AI compute", "is expensive."],
     ["Sementara itu,", "komputasi AI", "itu mahal."]),
    (["Nosana fixes", "both."],
     ["Nosana", "menyelesaikan", "keduanya."]),
    (["A decentralized", "GPU network", "on Solana."],
     ["Jaringan GPU", "terdesentralisasi", "di Solana."]),
    (["Hosts share", "idle GPUs.", "Builders rent them", "on demand."],
     ["Host menyumbang", "GPU idle-nya.", "Builder sewa", "sesuai kebutuhan."]),
    (["Open-source", "models.", "No lock-in.", "Lower cost."],
     ["Model open-source.", "Tanpa lock-in.", "Biaya lebih murah."]),
    (["You earn.", "They build.", "AI runs cheaper."],
     ["Kamu dapat cuan.", "Mereka membangun.", "AI jadi murah."]),
    (["DePIN, but", "make it useful."],
     ["DePIN, tapi", "benar-benar", "berguna."]),
    (["That's Nosana."],
     ["Itulah Nosana."]),
]
TAG = "#NOSvember  #CreatorChallenge"

def ease(t):
    return 1 - (1 - t) ** 3   # ease-out cubic

def draw_logo(img):
    if os.path.exists(LOGO):
        try:
            lg = Image.open(LOGO).convert("RGBA")
            h = 120
            w = int(lg.width * h / lg.height)
            lg = lg.resize((w, h), Image.LANCZOS)
            img.paste(lg, (W - w - 60, 60), lg)
        except Exception:
            pass

def text_size(d, lines, font):
    ws = [d.textbbox((0, 0), l, font=font)[2] for l in lines]
    hs = [d.textbbox((0, 0), l, font=font)[3] for l in lines]
    return max(ws), sum(hs) + (len(lines) - 1) * 14

def scene_frame(idx, t, d):
    """Render one frame at local time t (0..1) for scene idx."""
    img = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(img)
    # subtle moving gradient blobs (motion-graphics feel)
    for i, (cx, cy, col) in enumerate([(200, 500, NOS), (900, 1200, NOS2)]):
        ox = int(math.sin(t * 3 + i) * 60)
        oy = int(math.cos(t * 2 + i) * 40)
        layer = Image.new("RGB", (W, H), BG)
        ld = ImageDraw.Draw(layer)
        r = 380
        ld.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r],
                   fill=tuple(min(255, int(c * 0.18)) for c in col))
        layer = layer.filter(ImageFilter.GaussianBlur(160))
        img = Image.blend(img, Image.blend(img, layer, 0.5), 0.5)
        dr = ImageDraw.Draw(img)

    draw_logo(img)
    en, idn = SCENES[idx]
    # EN kinetic text: words slide up + fade in, ease-out
    appear = ease(min(1.0, t / 0.35))
    f_en = fb(92)
    total_h = len(en) * 104
    y = H // 2 - total_h // 2 - 60
    for li, line in enumerate(en):
        shift = int((1 - appear) * 60)
        alpha = appear
        col = WHITE if li % 2 == 0 else NOS
        bb = dr.textbbox((0, 0), line, font=f_en)
        x = (W - (bb[2] - bb[0])) // 2
        # shadow for legibility
        dr.text((x + 3, y + li * 104 + shift + 3), line, font=f_en, fill=(0, 0, 0))
        dr.text((x, y + li * 104 + shift), line, font=f_en,
                fill=tuple(int(c * alpha) for c in col))
    # ID subtitle: smaller, bottom area
    f_id = fr(40)
    appear_id = ease(min(1.0, max(0.0, (t - 0.15) / 0.4)))
    idy = H - 420
    for li, line in enumerate(idn):
        bb = dr.textbbox((0, 0), line, font=f_id)
        x = (W - (bb[2] - bb[0])) // 2
        col = tuple(int(c * appear_id) for c in IDCLR)
        dr.text((x, idy + li * 50), line, font=f_id, fill=col)

    # progress bar bottom
    prog = (idx + t) / len(SCENES)
    dr.rectangle([60, H - 90, 60 + int((W - 120) * prog), H - 78], fill=NOS)
    dr.rectangle([60, H - 90, W - 60, H - 78], outline=(40, 48, 60), width=2)

    # final scene: add hashtags
    if idx == len(SCENES) - 1 and t > 0.5:
        f_t = fb(44)
        bb = dr.textbbox((0, 0), TAG, font=f_t)
        x = (W - (bb[2] - bb[0])) // 2
        dr.text((x, H - 300), TAG, font=f_t, fill=NOS2)
    return img

def main():
    outdir = "/home/ubuntu/nosana_video/frames"
    os.makedirs(outdir, exist_ok=True)
    total_frames = DUR * FPS
    per = total_frames / len(SCENES)
    n = 0
    for idx in range(len(SCENES)):
        for f in range(int(per)):
            t = f / per
            img = scene_frame(idx, t, None)
            img.save(f"{outdir}/f_{n:05d}.png")
            n += 1
    # pad remaining frames
    while n < total_frames:
        scene_frame(len(SCENES) - 1, 1.0, None).save(f"{outdir}/f_{n:05d}.png")
        n += 1
    print("frames:", n)

if __name__ == "__main__":
    main()