#!/usr/bin/env python3.14
"""Nosana #NOSvember short-video generator — v2 (graphic-led motion graphics).

9:16 vertical. Each scene = animated vector ILLUSTRATION (hero). Narration lives
only as centered-bottom SUBTITLES (EN white + smaller ID grey). Relaxed tone.
Output: nosana_video/frames/*.png -> nosana_nosvember.mp4
"""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 30
SCENE_SEC = 4.0
BG=(7,11,17); NOS=(0,209,255); GRN=(0,255,170); RED=(255,92,92)
GOLD=(255,200,60); WHITE=(240,246,252); IDC=(175,184,198); DIM=(60,72,88)

FONT_B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def fb(s): return ImageFont.truetype(FONT_B,s)
def fr(s): return ImageFont.truetype(FONT_R,s)

SCENES=[
 {"gfx":"gpu","en":["Your GPU is probably idle right now."],
  "id":["GPU-mu mungkin sedang menganggur sekarang."]},
 {"gfx":"chart","en":["Meanwhile, AI compute is expensive."],
  "id":["Sementara itu, komputasi AI itu mahal."]},
 {"gfx":"node","en":["Nosana connects idle GPUs into one network on Solana."],
  "id":["Nosana menyambung GPU idle jadi satu jaringan di Solana."]},
 {"gfx":"flow","en":["Hosts share their GPUs. Builders rent them on demand."],
  "id":["Host membagikan GPU-nya. Builder menyewa sesuai kebutuhan."]},
 {"gfx":"coin","en":["You earn. They build. AI runs cheaper."],
  "id":["Kamu dapat cuan. Mereka membangun. AI jadi murah."]},
 {"gfx":"logo","en":["DePIN, but make it useful.  #NOSvember #CreatorChallenge"],
  "id":["DePIN, tapi benar-benar berguna."]},
]

def lerp(a,b,t): return a+(b-a)*t
def ease(t): return 1-(1-t)**3
def clamp01(x): return max(0.0,min(1.0,x))
def fade(t,a=0.0,b=1.0): return ease(clamp01((t-a)/(b-a)))

def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        test=(cur+" "+w).strip()
        if d.textbbox((0,0),test,font=font)[2]<=maxw: cur=test
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def background(t):
    img=Image.new("RGB",(W,H),BG)
    for i,(cx,cy,col) in enumerate([(180,420,NOS),(920,1350,GRN)]):
        ox=int(math.sin(t*1.3+i*2)*70); oy=int(math.cos(t*1.1+i)*50)
        lay=Image.new("RGB",(W,H),BG); ld=ImageDraw.Draw(lay)
        r=420; ld.ellipse([cx+ox-r,cy+oy-r,cx+ox+r,cy+oy+r],
                          fill=tuple(int(c*0.16) for c in col))
        lay=lay.filter(ImageFilter.GaussianBlur(180))
        img=Image.blend(img,lay,0.55)
    return img

def scrim(img):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for y in range(int(H*0.55),H):
        k=(y-H*0.55)/(H*0.45)
        od.line([(0,y),(W,y)],fill=(0,0,0,int(190*k)))
    return Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")

def gpu_icon(d,cx,cy,s,col):
    d.rounded_rectangle([cx-s,cy-s*0.7,cx+s,cy+s*0.7],radius=14,
                        outline=col,width=5,fill=(12,18,26))
    for i in range(3):
        for j in range(2):
            chip=s*0.30
            x=cx-s*0.58+i*s*0.58; y=cy-s*0.30+j*s*0.46
            d.rounded_rectangle([x-chip/2,y-chip/2,x+chip/2,y+chip/2],radius=5,fill=col)

def icon_gpu(d,t):
    cx,cy=W//2,int(H*0.40); s=210*fade(t,0.05,0.5)
    col=tuple(int(lerp(DIM[i],RED[i],0.6)) for i in range(3))
    gpu_icon(d,cx,cy,s,col)
    for k in range(3):
        zt=(t*0.6+k*0.33)%1.0; z=fb(int(30+zt*34)); a=int(220*(1-zt))
        d.text((cx+s*0.55+zt*90, cy-s*1.1-zt*140),"z",font=z,
               fill=tuple(int(c*a/255) for c in RED))

def icon_chart(d,t):
    cx,cy=W//2,int(H*0.42); bars=7
    for i in range(bars):
        h=(0.25+0.75*(i/bars))*220*fade(t,0.1+i*0.05,0.5+i*0.05)
        x=cx-260+i*80; col=RED if i>bars//2 else GOLD
        d.rounded_rectangle([x,cy-h,x+56,cy],radius=8,fill=col)
    ap=fade(t,0.5,0.9)
    if ap>0:
        ay=cy-240*ap
        d.line([cx-280,cy-20,cx+260,ay],fill=GOLD,width=8)
        d.polygon([(cx+250,ay-16),(cx+282,ay+4),(cx+250,ay+18)],fill=GOLD)

def icon_node(d,t):
    cx,cy=W//2,int(H*0.42)
    nodes=[(cx,cy),(cx-300,cy-180),(cx-280,cy+180),(cx+300,cy-170),
           (cx+310,cy+170),(cx-60,cy-300),(cx+40,cy+290)]
    for i,(x,y) in enumerate(nodes):
        a=fade(t,0.15+i*0.06,0.45+i*0.06)
        if a<=0: continue
        d.line([cx,cy,x,y],fill=tuple(int(c*a*0.6) for c in NOS),width=3)
    for i,(x,y) in enumerate(nodes):
        a=fade(t,0.15+i*0.06,0.45+i*0.06)
        r=(26 if i==0 else 20)*a; pulse=1+0.12*math.sin(t*4+i)
        d.ellipse([x-r*pulse,y-r*pulse,x+r*pulse,y+r*pulse],
                  fill=tuple(int(c*a) for c in (NOS if i==0 else GRN)))

def icon_flow(d,t):
    cy=int(H*0.42); lx,rx=W//2-300,W//2+300
    for side,col in [(lx,GRN),(rx,NOS)]:
        for k in range(3):
            y=cy-140+k*140; a=fade(t,0.1+k*0.05,0.4+k*0.05)
            d.rounded_rectangle([side-60,y-40,side+60,y+40],radius=12,
                                outline=tuple(int(c*a) for c in col),width=5)
    for k in range(5):
        ph=(t*0.7+k*0.2)%1.0
        x=int(lerp(lx+70,rx-70,ph)); y=cy+int(math.sin(ph*6+k)*30)
        a=int(255*math.sin(ph*math.pi))
        d.ellipse([x-13,y-13,x+13,y+13],fill=tuple(int(c*a/255) for c in NOS))

def icon_coin(d,t):
    cy=int(H*0.42)
    for k,(x,col) in enumerate([(W//2-260,GRN),(W//2,NOS),(W//2+260,GOLD)]):
        a=fade(t,0.08+k*0.08,0.4+k*0.08); bob=int(math.sin(t*3+k)*16); r=54*a
        d.ellipse([x-r,cy+bob-r,x+r,cy+bob+r],fill=tuple(int(c*a) for c in col))
        d.text((x-16,cy+bob-18),"$",font=fb(44),fill=(7,11,17))
    for k in range(3):
        ph=(t*0.8+k*0.33)%1.0; y=int(cy+120-ph*160); a=int(200*(1-ph))
        x=W//2-260+k*260
        d.polygon([(x,y+16),(x-14,y-4),(x+14,y-4)],fill=tuple(int(c*a/255) for c in GRN))

def icon_logo(d,t):
    cx,cy=W//2,int(H*0.40); r=(120+8*math.sin(t*3))*fade(t,0.05,0.45)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=NOS,width=8)
    d.text((cx-58,cy-46),"NOS",font=fb(70),fill=NOS)
    for k in range(10):
        ang=k/10*2*math.pi+t*0.6; rr=r+34
        x=cx+int(math.cos(ang)*rr); y=cy+int(math.sin(ang)*rr)
        d.ellipse([x-7,y-7,x+7,y+7],fill=GRN)

GFX={"gpu":icon_gpu,"chart":icon_chart,"node":icon_node,
     "flow":icon_flow,"coin":icon_coin,"logo":icon_logo}

def subtitles(img,en,idn,t):
    d=ImageDraw.Draw(img); a=fade(t,0.1,0.5)
    fen=fb(48); fid=fr(32); maxw=W-160
    enl=[]
    for seg in en: enl+=wrap(d,seg,fen,maxw)
    idl=[]
    for seg in idn: idl+=wrap(d,seg,fid,maxw)
    line_h=60; id_h=42
    block_h=len(enl)*line_h+16+len(idl)*id_h
    y=int(H*0.80)-block_h//2
    for l in enl:
        bb=d.textbbox((0,0),l,font=fen); x=(W-(bb[2]-bb[0]))//2
        d.text((x+2,y+2),l,font=fen,fill=(0,0,0))
        d.text((x,y),l,font=fen,fill=tuple(int(c*a) for c in WHITE)); y+=line_h
    y+=16
    for l in idl:
        bb=d.textbbox((0,0),l,font=fid); x=(W-(bb[2]-bb[0]))//2
        d.text((x,y),l,font=fid,fill=tuple(int(c*a) for c in IDC)); y+=id_h

def main():
    frames="/home/ubuntu/nosana_video/frames2"
    os.system(f"rm -f {frames}/*.png 2>/dev/null")
    os.makedirs(frames,exist_ok=True)
    per=int(SCENE_SEC*FPS); n=0
    for sc in SCENES:
        for f in range(per):
            t=f/per
            img=background(t)
            GFX[sc["gfx"]](ImageDraw.Draw(img),t)
            img=scrim(img)
            subtitles(img,sc["en"],sc["id"],t)
            img.save(f"{frames}/f_{n:05d}.png"); n+=1
    print("frames:",n,"scenes:",len(SCENES),"total_sec:",len(SCENES)*SCENE_SEC)

if __name__=="__main__": main()