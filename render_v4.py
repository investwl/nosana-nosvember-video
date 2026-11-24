#!/usr/bin/env python3.14
"""Nosana #NOSvember — v4 'competition edition'.

Narrative: HOOK -> PROBLEM -> SOLUTION -> HOW IT WORKS -> BENEFIT -> CLOSE.
Premium dark-tech commercial. 1080x1920, 30fps, ~25s. Bilingual subs (EN big).
Scene transitions are CROSSFADES (connected, not separate slides).
Headline hierarchy: short punchy HEADLINE (top) + full sentence as bottom subtitle.
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W,H=1080,1920; FPS=30
BG=(5,8,14); NAVY=(10,16,28)
NOS=(0,209,255); GRN=(46,255,138); RED=(255,74,74); GOLD=(255,204,64); PUR=(178,102,255)
WHITE=(242,247,252); IDC=(206,215,230); DIM=(90,104,124)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def fb(s): return ImageFont.truetype(FB,s)
def fr(s): return ImageFont.truetype(FR,s)

def clamp01(x): return max(0.0,min(1.0,x))
def ease(t): t=clamp01(t); return 1-(1-t)**3
def easeio(t): t=clamp01(t); return t*t*(3-2*t)
def backout(t): t=clamp01(t); c=1.7; return 1+(c+1)*(t-1)**3+c*(t-1)**2
def fade(t,a,b): return max(0.05, ease((t-a)/(b-a)))
def lerp(a,b,t): return a+(b-a)*t
def rgba(c,a): return tuple(int(x) for x in c)+(int(clamp01(a)*255),)

# ---------- scene table ----------
SCENE_SEC=4.2; XF=0.6  # crossfade duration (s)
SCENES=[
 dict(gfx="hook", head="YOUR GPU IS", head_hi="IDLE",
      en="Your GPU is sitting idle, doing nothing.",
      id="GPU-mu sedang menganggur, tak melakukan apa-apa."),
 dict(gfx="demand", head="MEANWHILE,", head_hi="AI DEMAND",
      en="Meanwhile, demand for AI compute keeps climbing.",
      id="Sementara itu, kebutuhan komputasi AI terus meningkat."),
 dict(gfx="network", head="MEET", head_hi="NOSANA",
      en="Nosana is a decentralized GPU network on Solana.",
      id="Nosana adalah jaringan GPU terdesentralisasi di Solana."),
 dict(gfx="flow", head="HOW IT", head_hi="WORKS",
      en="GPU hosts provide compute. AI builders access it on demand.",
      id="Host GPU menyediakan komputasi. Builder AI memakainya sesuai kebutuhan."),
 dict(gfx="benefit", head="TURN IDLE", head_hi="INTO USEFUL",
      en="Turn idle GPU power into useful AI compute.",
      id="Ubah GPU menganggur jadi komputasi AI yang berguna."),
 dict(gfx="close", head="DEPIN, BUT", head_hi="USEFUL",
      en="Powering the next generation of AI compute.",
      id="Mendukung generasi baru komputasi AI."),
]

# ---------- background / depth ----------
def particle_layer(t, n=60, seed=7):
    rnd=random.Random(seed); lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for i in range(n):
        x=rnd.uniform(0,W); base=rnd.uniform(0,H)
        y=(base - t*rnd.uniform(18,55))%H
        r=rnd.uniform(1.0,2.8); tw=0.5+0.5*math.sin(t*1.8+i)
        d.ellipse([x-r,y-r,x+r,y+r],fill=rgba(NOS if i%3 else GRN,0.12+0.4*tw))
    return lay

def grid(t):
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    hz=int(H*0.60); cx=W//2; a=0.085
    for i in range(1,15):
        y=hz+int((i**1.7)*12)
        if y>=H: break
        d.line([(0,y),(W,y)],fill=rgba(NOS,a*(0.3+0.7*i/15)),width=2)
    for i in range(-9,10):
        d.line([(cx+i*42,hz),(cx+i*270,H)],fill=rgba(NOS,a*0.8),width=2)
    return lay

def background(t):
    img=Image.new("RGB",(W,H),BG).convert("RGBA")
    for i,(cx,cy,col) in enumerate([(170,380,NOS),(940,1380,GRN)]):
        ox=int(math.sin(t*1.1+i*2)*80); oy=int(math.cos(t*0.9+i)*55)
        lay=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
        r=450; ld.ellipse([cx+ox-r,cy+oy-r,cx+ox+r,cy+oy+r],fill=rgba(col,0.20))
        lay=lay.filter(ImageFilter.GaussianBlur(200))
        img=Image.alpha_composite(img,lay)
    img=Image.alpha_composite(img,grid(t))
    img=Image.alpha_composite(img,particle_layer(t))
    return img.convert("RGB")

def bloom(img, thresh=200, strength=0.6, radius=18):
    base=img.convert("RGB"); qw,qh=W//4,H//4
    small=base.resize((qw,qh),Image.BILINEAR)
    def bright(c): return c.point(lambda v:int(max(0,(v-thresh))*2.2) if v>thresh else 0)
    bp=Image.merge("RGB",[bright(small.getchannel(i)) for i in range(3)])
    bp=bp.filter(ImageFilter.GaussianBlur(max(2,radius//4)))
    screened=ImageChops.invert(ImageChops.multiply(ImageChops.invert(small),
                                                   ImageChops.invert(bp)))
    return Image.blend(base, screened.resize((W,H),Image.BILINEAR), strength)

def scrim(img):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for y in range(int(H*0.56),H):
        k=(y-H*0.56)/(H*0.44); od.line([(0,y),(W,y)],fill=(0,0,0,int(205*k)))
    return Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")

# ---------- icon library (vector) ----------
def gpu_card(d,cx,cy,s,col,a=1.0,thick=6):
    col=tuple(int(c*a) for c in col)
    d.rounded_rectangle([cx-s,cy-s*0.66,cx+s,cy+s*0.66],radius=14,
                        outline=col,width=thick,fill=(9,14,21))
    for i in range(3):
        for j in range(2):
            ch=s*0.26; x=cx-s*0.55+i*s*0.55; y=cy-s*0.28+j*s*0.44
            d.rounded_rectangle([x-ch/2,y-ch/2,x+ch/2,y+ch/2],radius=4,fill=col)

def robot(d,cx,cy,s,col,a=1.0):
    col=tuple(int(c*a) for c in col)
    d.rounded_rectangle([cx-s*0.5,cy-s*0.6,cx+s*0.5,cy+s*0.8],radius=int(s*0.18),outline=col,width=6)
    d.rounded_rectangle([cx-s*0.3,cy-s*0.42,cx+s*0.3,cy-s*0.12],radius=6,fill=col)
    d.line([cx,cy-s*0.6,cx,cy-s*0.9],fill=col,width=5)
    d.ellipse([cx-s*0.1,cy-s*1.0,cx+s*0.1,cy-s*0.8],fill=col)
    for sx in (-1,1): d.line([cx+sx*s*0.5,cy,cx+sx*s*0.78,cy+s*0.25],fill=col,width=5)

def logo_mark(d,cx,cy,r,col):
    pass  # replaced by real logo assets below

ASSETS="/home/ubuntu/nosana_video/assets"
_ic=Image.open(f"{ASSETS}/nosana_icon.png").convert("RGBA")
_wd=Image.open(f"{ASSETS}/nosana_word.png").convert("RGBA")
def paste_icon(img,cx,cy,h):
    """real Nosana icon mark, centered at (cx,cy) with height h"""
    w=int(_ic.width*h/_ic.height); ic=_ic.resize((w,h),Image.LANCZOS)
    img.paste(ic,(int(cx-w/2),int(cy-h/2)),ic)
def paste_word(img,cx,cy,h):
    w=int(_wd.width*h/_wd.height); wd=_wd.resize((w,h),Image.LANCZOS)
    img.paste(wd,(int(cx-w/2),int(cy-h/2)),wd)
def hub_logo(img,d,cx,cy,r,t,pulse=0.5):
    """glow ring + dark disc + real Nosana icon, centered (for network hubs)."""
    d.ellipse([cx-r-30,cy-r-30,cx+r+30,cy+r+30],outline=rgba(NOS,0.22*pulse+0.08),width=20)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(9,14,21),outline=NOS,width=8)
    paste_icon(img,cx,cy,int(r*1.05))

def headline(d,head,hi,t):
    """top headline with two-tone hierarchy"""
    a=fade(t,0.05,0.35)
    f1=fb(58); f2=fb(112)
    b1=d.textbbox((0,0),head,font=f1); y=int(H*0.135)
    x=(W-(b1[2]-b1[0]))//2
    d.text((x+2,y+3),head,font=f1,fill=(0,0,0))
    d.text((x,y),head,font=f1,fill=rgba(DIM,a))
    b2=d.textbbox((0,0),hi,font=f2); x2=(W-(b2[2]-b2[0]))//2; y2=y+74
    d.text((x2+3,y2+3),hi,font=f2,fill=(0,0,0))
    d.text((x2,y2),hi,font=f2,fill=rgba(NOS,a))

def subtitle(img,en,idn,t):
    d=ImageDraw.Draw(img); a=fade(t,0.1,0.42)
    fen=fb(50); fid=fr(48); maxw=W-170
    def wrap(text,font):
        words=text.split(); lines=[]; cur=""
        for w in words:
            test=(cur+" "+w).strip()
            if d.textbbox((0,0),test,font=font)[2]<=maxw: cur=test
            else:
                if cur: lines.append(cur)
                cur=w
        if cur: lines.append(cur)
        return lines
    enl=wrap(en,fen); idl=wrap(idn,fid)
    lh=60; ih=56; bh=len(enl)*lh+14+len(idl)*ih
    y=int(H*0.845)-bh//2
    for l in enl:
        bb=d.textbbox((0,0),l,font=fen); x=(W-(bb[2]-bb[0]))//2
        d.text((x+2,y+3),l,font=fen,fill=(0,0,0))
        d.text((x,y),l,font=fen,fill=rgba(WHITE,a)); y+=lh
    y+=14
    for l in idl:
        bb=d.textbbox((0,0),l,font=fid); x=(W-(bb[2]-bb[0]))//2
        d.text((x+2,y+2),l,font=fid,fill=(0,0,0))
        d.text((x,y),l,font=fid,fill=rgba(IDC,a)); y+=ih

# ---------- scene illustrations ----------
def g_hook(img,d,t):
    cx,cy=W//2,int(H*0.47)
    s=230*fade(t,0.05,0.4)
    # GPU asleep — dim, slow breathing, Zzz
    br=0.5+0.5*math.sin(t*1.6)
    col=tuple(int(lerp(DIM[i],GRN[i],0.35+0.2*br)) for i in range(3))
    gpu_card(d,cx,cy,s,col,thick=7)
    d.ellipse([cx-s*0.34,cy-s*0.34,cx+s*0.34,cy+s*0.34],outline=col,width=5)
    for k in range(3):
        zt=(t*0.5+k*0.33)%1.0; f=fb(int(58+zt*64)); a=(1-zt)*0.9   # bigger Zzz
        # anchored to the GPU's top-right corner
        d.text((cx+s*0.62+zt*70, cy-s*0.95-zt*120),"z",font=f,fill=rgba(GRN,a))
    # quick interruption flash at t~0.5 (attention spike)
    if 0.45<t<0.6:
        k=1-abs((t-0.52)/0.08)
        d.rounded_rectangle([cx-s,cy-s*0.66,cx+s,cy+s*0.66],radius=14,
                            outline=rgba(WHITE,k*0.7),width=8)

def g_demand(img,d,t):
    cx,cy=W//2,int(H*0.47)
    n=9
    for i in range(n):
        h=(0.15+0.85*(i/n))*300*fade(t,0.05+i*0.04,0.32+i*0.04)
        x=cx-360+i*82
        col=tuple(int(lerp(GOLD[j],NOS[j],i/n)) for j in range(3))
        d.rounded_rectangle([x,cy-h,x+62,cy],radius=8,fill=col)
    # rising trend line + arrow
    ap=fade(t,0.45,0.85)
    if ap>0.05:
        pts=[(cx-360+i*82, cy-(0.15+0.85*(i/n))*300+20) for i in range(n)]
        d.line(pts,fill=rgba(GRN,ap),width=6)
        ex,ey=pts[-1]
        d.polygon([(ex+8,ey-30),(ex+40,ey+8),(ex+2,ey+16)],fill=rgba(GRN,ap))
    # workload dots streaming up (demand)
    for k in range(8):
        ph=(t*0.6+k*0.125)%1.0; a=math.sin(ph*math.pi)
        x=cx-330+k*82; y=int(cy-ph*360)
        d.ellipse([x+20,y-7,x+34,y+7],fill=rgba(WHITE,a*0.7))

def g_network(img,d,t):
    cx,cy=W//2,int(H*0.47)
    pulse=0.5+0.5*math.sin(t*3)
    r=120+8*pulse
    hub_logo(img,d,cx,cy,r,t,pulse)
    sat=[(-380,-200),(-350,220),(380,-190),(390,230),(-120,-340),(100,350),(-400,10),(410,-10)]
    for i,(ox,oy) in enumerate(sat):
        a=fade(t,0.15+i*0.05,0.42+i*0.05)
        if a<=0.05: continue
        x,y=cx+ox,cy+oy
        # trim connector so it stops at the hub ring, not through the N
        ux,uy=ox/ math.hypot(ox,oy), oy/math.hypot(ox,oy)
        sx,sy=cx+ux*(r+8),cy+uy*(r+8)
        d.line([sx,sy,x,y],fill=rgba(NOS,a*0.5),width=4)
        gpu_card(d,x,y,38,GRN,a,thick=5)
        ph=(t*0.8+i*0.13)%1.0
        px=cx+ox*ph; py=cy+oy*ph
        d.ellipse([px-9,py-9,px+9,py+9],fill=rgba(WHITE,a))

def g_flow(img,d,t):
    cy=int(H*0.47); lx,rx=W//2-330,W//2+330; mx=W//2
    # left: GPU host, center: Nosana network, right: AI builder
    gpu_card(d,lx,cy,120,GRN,fade(t,0.08,0.35),thick=7)
    pulse=0.5+0.5*math.sin(t*3); rr=96+6*pulse
    hub_logo(img,d,mx,cy,rr,t,pulse)
    robot(d,rx,cy,118,NOS,fade(t,0.5,0.78))
    # labels
    for x,lab,col,a in [(lx,"GPU HOST",GRN,fade(t,0.15,0.4)),(mx,"NOSANA",NOS,fade(t,0.3,0.55)),
                        (rx,"AI BUILDER",NOS,fade(t,0.6,0.85))]:
        f=fb(32); bb=d.textbbox((0,0),lab,font=f)
        d.text((x-(bb[2]-bb[0])//2,cy+170),lab,font=f,fill=rgba(col,a))
    # resource flow host -> network -> builder (two hops)
    for k in range(6):
        ph=(t*0.8+k*0.167)%1.0; a=math.sin(ph*math.pi)
        x1=int(lerp(lx+130,mx-rr,ph)); d.ellipse([x1-11,cy-11,x1+11,cy+11],fill=rgba(GRN,a))
        x2=int(lerp(mx+rr,rx-140,ph)); d.ellipse([x2-11,cy-11,x2+11,cy+11],fill=rgba(NOS,a))

def g_benefit(img,d,t):
    cx,cy=W//2,int(H*0.46)
    # metaphor: idle GPU -> tokens flow -> AI queue served (NOT a repeat of network hub)
    # left: single GPU powering up (green glow grows)
    ga=fade(t,0.05,0.35)
    gpu_card(d,cx-300,cy-120,120,GRN,ga,thick=7)
    f=fb(30); lab="IDLE GPU"
    bb=d.textbbox((0,0),lab,font=f)
    d.text((cx-300-(bb[2]-bb[0])//2,cy+10),lab,font=f,fill=rgba(GRN,ga))
    # center: flowing tokens along an arc toward the queue
    for k in range(6):
        ph=(t*0.7+k*0.167)%1.0; a=math.sin(ph*math.pi)
        x=int(lerp(cx-180,cx+120,ph)); y=cy-120+int(math.sin(ph*math.pi)*-40)
        d.ellipse([x-11,y-11,x+11,y+11],fill=rgba(NOS,a))
    # right: AI builder being served (robot lights up)
    robot(d,cx+300,cy-120,120,NOS,fade(t,0.4,0.7))
    lab="AI WORKLOADS"
    bb=d.textbbox((0,0),lab,font=f)
    d.text((cx+300-(bb[2]-bb[0])//2,cy+10),lab,font=f,fill=rgba(NOS,fade(t,0.45,0.75)))
    # proper progress bar with track + % counter
    bx,by,bw,bh=cx-320,cy+200,640,46
    d.rounded_rectangle([bx,by,bx+bw,by+bh],radius=12,outline=DIM,width=4)  # full track
    prog=easeio((t-0.3)/1.6) if t>0.3 else 0.0
    fw=int(bw*prog)
    if fw>8:
        d.rounded_rectangle([bx,by,bx+fw,by+bh],radius=12,fill=GRN)
    # % label centered above track
    pct=int(prog*100)
    f2=fb(56); pt=f"{pct}%"
    bb=d.textbbox((0,0),pt,font=f2)
    d.text((cx-(bb[2]-bb[0])//2+2,by-96+2),pt,font=f2,fill=(0,0,0))
    d.text((cx-(bb[2]-bb[0])//2,by-96),pt,font=f2,fill=rgba(GRN,fade(t,0.3,0.6)))
    f=fb(32); lab="GPU UTILIZED"
    bb=d.textbbox((0,0),lab,font=f)
    d.text((cx-(bb[2]-bb[0])//2,by+bh+18),lab,font=f,fill=rgba(WHITE,fade(t,0.4,0.8)))

def g_close(img,d,t):
    cx,cy=W//2,int(H*0.47)
    r=(140+8*math.sin(t*2.4))*fade(t,0.05,0.45)
    for k in range(14):
        ang=k/14*2*math.pi+t*0.5; rr=r+74+16*math.sin(t*2+k)
        x=cx+int(math.cos(ang)*rr); y=cy+int(math.sin(ang)*rr)
        d.ellipse([x-8,y-8,x+8,y+8],fill=rgba(GRN,0.9))
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=NOS,width=10)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(9,14,21))
    paste_icon(img,cx,cy,int(r*1.0))          # real Nosana icon in the ring
    # real wordmark below the ring as the brand lockup
    paste_word(img,cx,cy+r+70,56)
    # CTA
    a=fade(t,0.45,0.85); f=fb(46); cta="Explore Nosana →"
    bb=d.textbbox((0,0),cta,font=f); x=(W-(bb[2]-bb[0]))//2
    d.text((x+2,cy+r+120+2),cta,font=f,fill=(0,0,0))
    d.text((x,cy+r+120),cta,font=f,fill=rgba(GRN,a))
    # hashtags
    f2=fb(40); tags="#NOSvember   #CreatorChallenge"
    bb=d.textbbox((0,0),tags,font=f2); x=(W-(bb[2]-bb[0]))//2
    d.text((x+2,cy+r+196+2),tags,font=f2,fill=(0,0,0))
    d.text((x,cy+r+196),tags,font=f2,fill=rgba(WHITE,fade(t,0.55,0.9)))

GFX={"hook":g_hook,"demand":g_demand,"network":g_network,
     "flow":g_flow,"benefit":g_benefit,"close":g_close}

def compose(idx,t):
    sc=SCENES[idx]
    img=background(t)
    GFX[sc["gfx"]](img,ImageDraw.Draw(img),t)
    headline(ImageDraw.Draw(img),sc["head"],sc["head_hi"],t)
    img=bloom(img)
    img=scrim(img)
    subtitle(img,sc["en"],sc["id"],t)
    return img

def main():
    out="/home/ubuntu/nosana_video/frames4"
    os.system(f"mkdir -p {out} && rm -f {out}/*.png")
    per=int(SCENE_SEC*FPS); xf=int(XF*FPS); n=0; prev=None
    for idx in range(len(SCENES)):
        for f in range(per):
            t=f/per
            img=compose(idx,t)
            if idx>0 and f<xf:                      # crossfade from previous scene
                a=f/xf
                pimg=compose(idx-1,(per-xf+f)/per)
                img=Image.blend(pimg,img,easeio(a))
            img.save(f"{out}/f_{n:05d}.png"); n+=1
    print("frames:",n,"dur:",len(SCENES)*SCENE_SEC)

if __name__=="__main__": main()
