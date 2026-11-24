#!/usr/bin/env python3.14
"""Nosana #NOSvember video — v3 (attention-first motion graphics).

Graphic-led 9:16. Per-scene illustrated animation + centered-bottom bilingual
subtitles. Attention devices: zoom punch-in, particle field, glow, flash cuts,
screen shake, animated price counter, rich vector icons (GPU/human/AI/logo hub).
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H=1080,1920; FPS=30; SCENE_SEC=4.2
BG=(6,9,15)
NOS=(0,209,255); GRN=(46,255,138); RED=(255,74,74); GOLD=(255,204,64)
PUR=(178,102,255); WHITE=(242,247,252); IDC=(170,180,196); DIM=(70,84,102)

FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def fb(s): return ImageFont.truetype(FB,s)
def fr(s): return ImageFont.truetype(FR,s)

def clamp01(x): return max(0.0,min(1.0,x))
def ease(t): t=clamp01(t); return 1-(1-t)**3
def easeio(t): t=clamp01(t); return t*t*(3-2*t)
def back(t): t=clamp01(t); c=1.70158; return 1+ (c+1)*(t-1)**3 + c*(t-1)**2
def fade(t,a,b): return max(0.05, ease((t-a)/(b-a)))  # floor avoids 0-size fonts/radii
def lerp(a,b,t): return a+(b-a)*t
def rgba(c,a): return tuple(int(x) for x in c)+(int(clamp01(a)*255),)

SCENES=[
 dict(gfx="gpu", en="Your GPU is probably idle right now.",
      id="GPU-mu mungkin sedang menganggur sekarang."),
 dict(gfx="price", en="Meanwhile, AI compute is getting expensive.",
      id="Sementara itu, biaya komputasi AI makin mahal."),
 dict(gfx="network", en="Nosana connects idle GPUs into one network on Solana.",
      id="Nosana menyambung GPU idle jadi satu jaringan di Solana."),
 dict(gfx="market", en="Hosts share their GPUs. Builders rent them on demand.",
      id="Host membagikan GPU-nya. Builder menyewa sesuai kebutuhan."),
 dict(gfx="earn", en="You earn. They build. AI runs cheaper.",
      id="Kamu dapat cuan. Mereka membangun. AI jadi lebih murah."),
 dict(gfx="outro", en="DePIN, but make it useful.",
      id="DePIN, tapi benar-benar berguna."),
]

# ---------- particle field (starfield) ----------
def particle_layer(t, seed=1, n=70):
    rnd=random.Random(seed); lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for i in range(n):
        x=rnd.uniform(0,W); base=rnd.uniform(0,H)
        y=(base - t*rnd.uniform(20,70))%H
        r=rnd.uniform(1.2,3.4); tw=0.5+0.5*math.sin(t*2+i)
        a=0.18+0.5*tw
        d.ellipse([x-r,y-r,x+r,y+r],fill=rgba(NOS if i%3 else GRN,a))
    return lay

def glow(draw_target_img, cx, cy, r, color, strength=0.5):
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=rgba(color,0.6))
    lay=lay.filter(ImageFilter.GaussianBlur(r*0.5))
    return Image.alpha_composite(draw_target_img.convert("RGBA"),
        Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)),lay,strength)).convert("RGB")

def transform_zoom(img, t):
    """zoom punch-in at scene start then settle"""
    z=1.0+0.10*(1-easeio(t/0.35)) + 0.02*math.sin(t*1.5)
    z=max(1.0,z)
    if z<=1.001: return img
    nw,nh=int(W/z),int(H/z)
    x0=(W-nw)//2; y0=(H-nh)//2
    img=img.crop((x0,y0,x0+nw,y0+nh)).resize((W,H),Image.LANCZOS)
    return img

def background(t, accent):
    img=Image.new("RGB",(W,H),BG).convert("RGBA")
    for i,(cx,cy,col) in enumerate([(160,400,accent),(930,1400,GRN)]):
        ox=int(math.sin(t*1.2+i*2)*80); oy=int(math.cos(t*1.0+i)*55)
        lay=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
        r=440; ld.ellipse([cx+ox-r,cy+oy-r,cx+ox+r,cy+oy+r],fill=rgba(col,0.22))
        lay=lay.filter(ImageFilter.GaussianBlur(190))
        img=Image.alpha_composite(img,lay)
    img=Image.alpha_composite(img,particle_layer(t))
    return img.convert("RGB")

def scrim(img):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for y in range(int(H*0.58),H):
        k=(y-H*0.58)/(H*0.42)
        od.line([(0,y),(W,y)],fill=(0,0,0,int(200*k)))
    return Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")

def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        test=(cur+" "+w).strip()
        if d.textbbox((0,0),test,font=font)[2]<=maxw: cur=test
        else:
            if cur: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

def subtitle(img,en,idn,t):
    d=ImageDraw.Draw(img); a=fade(t,0.08,0.4)
    fen=fb(52); fid=fr(34); maxw=W-150
    enl=wrap(d,en,fen,maxw); idl=wrap(d,idn,fid,maxw)
    lh=62; ih=44; bh=len(enl)*lh+14+len(idl)*ih
    y=int(H*0.815)-bh//2
    for l in enl:
        bb=d.textbbox((0,0),l,font=fen); x=(W-(bb[2]-bb[0]))//2
        d.text((x+2,y+3),l,font=fen,fill=(0,0,0))
        d.text((x,y),l,font=fen,fill=tuple(int(c*a) for c in WHITE)); y+=lh
    y+=14
    for l in idl:
        bb=d.textbbox((0,0),l,font=fid); x=(W-(bb[2]-bb[0]))//2
        d.text((x,y),l,font=fid,fill=tuple(int(c*a) for c in IDC)); y+=ih

def shake(img,amt):
    if amt<=0.3: return img
    dx=int(random.uniform(-amt,amt)); dy=int(random.uniform(-amt,amt))
    return img.transform((W,H),Image.AFFINE,(1,0,dx,0,1,dy),
                         resample=Image.BILINEAR,fillcolor=BG)

# ---------- icon library ----------
def human(d,cx,cy,s,col,a=1.0):
    col=tuple(int(c*a) for c in col)
    d.ellipse([cx-s*0.32,cy-s*0.95,cx+s*0.32,cy-s*0.31],fill=col)          # head
    d.rounded_rectangle([cx-s*0.42,cy-s*0.22,cx+s*0.42,cy+s*0.85],radius=int(s*0.2),fill=col)  # body

def robot(d,cx,cy,s,col,a=1.0):
    col=tuple(int(c*a) for c in col)
    d.rounded_rectangle([cx-s*0.5,cy-s*0.6,cx+s*0.5,cy+s*0.8],radius=int(s*0.18),
                        outline=col,width=6)
    d.rounded_rectangle([cx-s*0.3,cy-s*0.42,cx+s*0.3,cy-s*0.12],radius=6,fill=col)  # visor
    d.line([cx,cy-s*0.6,cx,cy-s*0.9],fill=col,width=5)
    d.ellipse([cx-s*0.1,cy-s*1.0,cx+s*0.1,cy-s*0.8],fill=col)  # antenna
    for sx in (-1,1):
        d.line([cx+sx*s*0.5,cy,cx+sx*s*0.78,cy+s*0.25],fill=col,width=5)

def gpu_card(d,cx,cy,s,col,a=1.0):
    col=tuple(int(c*a) for c in col)
    d.rounded_rectangle([cx-s,cy-s*0.66,cx+s,cy+s*0.66],radius=14,
                        outline=col,width=6,fill=(10,15,22))
    for i in range(3):
        for j in range(2):
            ch=s*0.26; x=cx-s*0.55+i*s*0.55; y=cy-s*0.28+j*s*0.44
            d.rounded_rectangle([x-ch/2,y-ch/2,x+ch/2,y+ch/2],radius=4,fill=col)

def logo_mark(d,cx,cy,r,col,ring=True):
    if ring: d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=col,width=max(4,int(r*0.12)))
    f=fb(int(r*0.9))
    bb=d.textbbox((0,0),"N",font=f); d.text((cx-(bb[2]-bb[0])/2,cy-(bb[3]-bb[1])/2-bb[1]),
        "N",font=f,fill=col)

# ---------- scenes ----------
def s_gpu(d,t):
    cx,cy=W//2,int(H*0.40)
    ap=back(t/0.35)
    s=210*min(1.2,ap)
    glow_img=None
    pulse=0.5+0.5*math.sin(t*3)
    gpu_card(d,cx,cy,s,GRN)
    d.ellipse([cx-s*0.34,cy-s*0.34,cx+s*0.34,cy+s*0.34],outline=GRN,width=5)
    for k in range(3):
        zt=(t*0.55+k*0.33)%1.0; f=fb(int(34+zt*40)); a=(1-zt)*0.9
        d.text((cx+s*0.5+zt*110, cy-s*1.15-zt*150),"z",font=f,fill=rgba(GRN,a))

def s_price(d,t):
    cx,cy=W//2,int(H*0.38)
    # rising bars
    for i in range(8):
        h=(0.2+0.8*(i/8))*260*fade(t,0.05+i*0.045,0.35+i*0.045)
        x=cx-330+i*84
        col=RED if i>4 else GOLD
        d.rounded_rectangle([x,cy-h,x+60,cy],radius=8,fill=col)
    # animated price counter ticking up
    prog=easeio((t-0.25)/1.6) if t>0.25 else 0
    val=12+prog*88
    txt=f"${val:,.0f}"
    f=fb(120); a=fade(t,0.2,0.4)
    bb=d.textbbox((0,0),txt,font=f); x=(W-(bb[2]-bb[0]))//2; y=cy-420
    d.text((x+4,y+4),txt,font=f,fill=(0,0,0))
    d.text((x,y),txt,font=f,fill=rgba(RED,a))
    # up arrow pulsing
    ap=fade(t,0.4,0.8)
    if ap>0:
        ay=cy-300+int(math.sin(t*5)*8)
        d.polygon([(cx,ay-46),(cx-34,ay+10),(cx+34,ay+10)],fill=rgba(RED,ap))

def s_network(d,t):
    cx,cy=W//2,int(H*0.40)
    # central Nosana logo as the connector hub
    pulse=0.5+0.5*math.sin(t*3)
    img=img_ if False else None
    r=110+10*pulse
    # glow around hub
    d.ellipse([cx-r-26,cy-r-26,cx+r+26,cy+r+26],outline=rgba(NOS,0.25*pulse+0.1),width=18)
    logo_mark(d,cx,cy,r,NOS)
    sat=[(-360,-210),(-330,210),(360,-200),(370,215),(-90,-330),(70,330)]
    for i,(ox,oy) in enumerate(sat):
        a=fade(t,0.2+i*0.07,0.5+i*0.07)
        if a<=0: continue
        x,y=cx+ox,cy+oy
        d.line([cx,cy,x,y],fill=rgba(NOS,a*0.55),width=4)
        # small gpu on satellite
        gpu_card(d,x,y,34,GRN,a)
        # travelling packet along the line
        ph=(t*0.8+i*0.17)%1.0
        px=cx+ox*ph; py=cy+oy*ph
        d.ellipse([px-8,py-8,px+8,py+8],fill=rgba(WHITE,a))

def s_market(d,t):
    cy=int(H*0.40); lx,rx=W//2-310,W//2+310
    # hosts (humans + gpu) left, builders (robot + gpu) right
    human(d,lx,cy-150,120,GRN,fade(t,0.1,0.4))
    gpu_card(d,lx,cy+110,86,GRN,fade(t,0.18,0.48))
    robot(d,rx,cy-150,110,NOS,fade(t,0.3,0.6))
    gpu_card(d,rx,cy+110,86,NOS,fade(t,0.38,0.68))
    # packet exchange both ways
    for k in range(6):
        ph=(t*0.7+k*0.167)%1.0
        if k%2==0:
            x=int(lerp(lx+80,rx-80,ph)); col=NOS
        else:
            x=int(lerp(rx-80,lx+80,ph)); col=GRN
        y=cy+int(math.sin(ph*6+k)*40)
        a=math.sin(ph*math.pi)
        d.ellipse([x-12,y-12,x+12,y+12],fill=rgba(col,a))

def s_earn(d,t):
    cy=int(H*0.40)
    items=[(W//2-330,human,GOLD,"YOU"),(W//2-110,robot,NOS,"AI"),
           (W//2+110,gpu_card,GRN,"HOSTS"),(W//2+330,robot,PUR,"BUILDERS")]
    for i,(x,fn,col,lab) in enumerate(items):
        a=fade(t,0.1+i*0.1,0.4+i*0.1)
        bob=int(math.sin(t*2.6+i)*14)
        fn(d,x,cy+bob,84 if fn!=human else 92,col,a)
        f=fb(30); bb=d.textbbox((0,0),lab,font=f); lx=x-(bb[2]-bb[0])//2
        d.text((lx,cy+bob+120),lab,font=f,fill=rgba(col,a))
    # floating $ up
    for k in range(6):
        ph=(t*0.7+k*0.167)%1.0; a=math.sin(ph*math.pi)
        x=W//2+int(math.cos(k)*240*ph); y=int(cy+140-ph*220)
        f=fb(int(26+ph*20))
        d.text((x,y),"$",font=f,fill=rgba(GOLD,a))

def s_outro(d,t):
    cx,cy=W//2,int(H*0.40)
    r=(150+10*math.sin(t*2.5))*fade(t,0.05,0.5)
    # orbit ring + nodes
    for k in range(14):
        ang=k/14*2*math.pi+t*0.5
        rr=r+70+18*math.sin(t*2+k)
        x=cx+int(math.cos(ang)*rr); y=cy+int(math.sin(ang)*rr)
        d.ellipse([x-8,y-8,x+8,y+8],fill=rgba(GRN,0.9))
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=NOS,width=10)
    # draw real logo if available, else N mark
    logo_path="/home/ubuntu/nosana_video/assets/nosana_logo.png"
    if os.path.exists(logo_path):
        try:
            lg=Image.open(logo_path).convert("RGBA")
            hs=int(r*1.1); ws=int(lg.width*hs/lg.height)
            if ws>hs*4: ws=int(hs*4); hs=int(lg.height*ws/lg.width)
            lg=lg.resize((max(8,ws),max(8,hs)),Image.LANCZOS)
            img_=img_  # placeholder
            return ("__PASTE__",cx,cy,lg)
        except Exception: pass
    logo_mark(d,cx,cy,r,NOS)
    # tagline + hashtags
    f1=fb(64); tag="DePIN, but useful."
    a=fade(t,0.3,0.7)
    bb=d.textbbox((0,0),tag,font=f1); x=(W-(bb[2]-bb[0]))//2
    d.text((x,cy+r+110),tag,font=f1,fill=rgba(WHITE,a))
    f2=fb(40); tags="#NOSvember   #CreatorChallenge"
    bb=d.textbbox((0,0),tags,font=f2); x=(W-(bb[2]-bb[0]))//2
    d.text((x,cy+r+210),tags,font=f2,fill=rgba(GRN,fade(t,0.5,0.9)))
    return None

GFX={"gpu":s_gpu,"price":s_price,"network":s_network,
     "market":s_market,"earn":s_earn,"outro":s_outro}

def render_frame(idx,t):
    sc=SCENES[idx]; accent=NOS
    img=background(t,accent)
    d=ImageDraw.Draw(img)
    res=GFX[sc["gfx"]](d,t)
    # outro paste real logo if returned
    if isinstance(res,tuple) and res and res[0]=="__PASTE__":
        _,cx,cy,lg=res
        img.paste(lg,(cx-lg.width//2,cy-lg.height//2),lg)
    img=scrim(img)
    subtitle(img,sc["en"],sc["id"],t)
    img=transform_zoom(img,t)
    shk=(6*(1-easeio(t/0.18))) if t<0.18 else 0
    img=shake(img,shk)
    return img

def main():
    out="/home/ubuntu/nosana_video/frames3"
    os.system(f"mkdir -p {out} && rm -f {out}/*.png")
    per=int(SCENE_SEC*FPS); n=0
    for idx in range(len(SCENES)):
        for f in range(per):
            t=f/per
            render_frame(idx,t).save(f"{out}/f_{n:05d}.png"); n+=1
    print("frames:",n,"dur:",len(SCENES)*SCENE_SEC)

if __name__=="__main__": main()