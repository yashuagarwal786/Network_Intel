"""Render the Network Intel SIH 26189 premium product film."""
from __future__ import annotations
from pathlib import Path
import sys, subprocess, asyncio, json, math, wave

ROOT=Path(__file__).resolve().parent
VENDOR=ROOT.parent/'launch-video'/'vendor'
sys.path.insert(0,str(VENDOR))
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
import numpy as np
import edge_tts

W,H,FPS,MOTION_FPS,DURATION=1920,1080,30,15,175
CAP=ROOT/'captures'; GEN=ROOT/'generated'; CLIPS=ROOT/'clips'; AUDIO=ROOT/'audio'
for p in [GEN,CLIPS,AUDIO]:p.mkdir(exist_ok=True)
BG=(10,10,15); PANEL=(20,19,27); TEXT=(245,242,248); MUTED=(155,150,163)
VIOLET=(139,92,246); LILAC=(190,166,248); GREEN=(111,169,143); ROSE=(199,91,106)
FONT='C:/Windows/Fonts/segoeui.ttf'; SEMI='C:/Windows/Fonts/seguisb.ttf'; SERIF='C:/Windows/Fonts/georgia.ttf'; MONO='C:/Windows/Fonts/consola.ttf'
LOGO=Path('Z:/XLab/New/Network Intel/frontend/public/assets/network-intel-mark.png')

def run(args):
    r=subprocess.run([str(x) for x in args],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if r.returncode: raise RuntimeError(r.stderr.decode('utf-8','replace')[-4000:])
    return r.stdout
def ff(*args):run(['ffmpeg','-hide_banner','-loglevel','error','-y',*args])
def font(n,kind='sans'):
    return ImageFont.truetype({'sans':FONT,'semi':SEMI,'serif':SERIF,'mono':MONO}[kind],n)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def clamp(x):return max(0,min(1,x))
def fade_window(t,a,b,edge=.7):return clamp((t-a)/edge)*clamp((b-t)/edge)

def background(t=0):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    for x in range(-40,W+40,48):
        for y in range(-40,H+40,48):
            if ((x//48+y//48)%3)==0:d.ellipse((x,y,x+2,y+2),fill=(38,34,49))
    # restrained purple glow
    glow=Image.new('RGBA',(W,H),(0,0,0,0));g=ImageDraw.Draw(glow)
    g.ellipse((1120,-430,2260,710),fill=(94,48,170,30))
    glow=glow.filter(ImageFilter.GaussianBlur(120))
    return Image.alpha_composite(im.convert('RGBA'),glow)

def draw_text(im,xy,s,size,color=TEXT,kind='sans',anchor=None,spacing=4):
    ImageDraw.Draw(im).multiline_text(xy,s,font=font(size,kind),fill=color,anchor=anchor,spacing=spacing)
def line(im,xy,fill,width=2):ImageDraw.Draw(im).line(xy,fill=fill,width=width)
def eyebrow(im,s,x=110,y=76,color=LILAC):
    draw_text(im,(x,y),s.upper(),18,color,'semi');line(im,(x,y+36,x+86,y+36),VIOLET,3)
def wordmark(im,x=110,y=90,scale=.8):
    logo=Image.open(LOGO).convert('RGBA');logo.thumbnail((int(88*scale),int(88*scale)),Image.Resampling.LANCZOS)
    im.alpha_composite(logo,(x,y));draw_text(im,(x+int(106*scale),y+int(4*scale)),'Network Intel',int(46*scale),TEXT,'semi')

records=[
 ('COMPLAINT NARRATIVE','Rahul Sharma','Report · paragraph 4'),
 ('CALL DETAIL RECORD','P101  →  P204','15 Aug · 18:02 IST'),
 ('BANK TRANSACTION','A17  →  A31','INR 75,000 · Row 2'),
 ('VEHICLE RECORD','DEMO-VH-02','Registry reference'),
 ('LOCATION RECORD','A44','Source assertion'),
 ('PERSON MENTION','Vikram Singh','Report · paragraph 7'),
 ('CALL RECORD 014','P101','Metadata only'),
 ('TRANSACTION 027','Account A31','Timestamped record'),
]
positions=[(125,190),(1010,160),(280,445),(1160,410),(700,655),(1290,690),(130,780),(855,850)]

def card(im,x,y,title,value,meta,alpha=255,scale=1):
    ww,hh=int(490*scale),int(145*scale);layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    d.rounded_rectangle((x,y,x+ww,y+hh),9,fill=(*PANEL,alpha),outline=(*((70,62,84)),alpha),width=2)
    d.rectangle((x,y,x+5,y+hh),fill=(*VIOLET,alpha))
    d.text((x+25,y+20),title,font=font(int(15*scale),'semi'),fill=(*LILAC,alpha))
    d.text((x+25,y+53),value,font=font(int(29*scale),'serif'),fill=(*TEXT,alpha))
    d.text((x+25,y+103),meta,font=font(int(14*scale),'mono'),fill=(*MUTED,alpha))
    return Image.alpha_composite(im,layer)

def fragments_scene(t,variant):
    im=background(t);eyebrow(im,'SIH 26189 / THE INVESTIGATION')
    if variant==0:
        draw_text(im,(110,135),'A network never arrives\nas a network.',63,TEXT,'serif')
        count=min(len(records),int(t/0.9)+1)
    else:
        draw_text(im,(110,130),'The records accumulate.\nThe connection does not.',54,TEXT,'serif')
        count=len(records)
    for i in range(count):
        local=clamp((t-i*.55)/.7) if variant==0 else 1
        x,y=positions[i]; drift=18*math.sin(t*.4+i)
        # Keep the opening thesis clear while the evidence fragments accumulate below it.
        y += 135 if y < 780 else 55
        im=card(im,x+drift,y, *records[i],alpha=int(235*local),scale=.78)
    if variant==1:
        d=ImageDraw.Draw(im,'RGBA')
        pts=[(315,295),(1160,255),(435,555),(1265,520),(845,760),(1400,800)]
        for i in range(len(pts)-1):
            a=clamp((t-1-i*.5)/1.2);d.line((*pts[i],*pts[i+1]),fill=(139,92,246,int(95*a)),width=2)
        d.rounded_rectangle((620,925,1300,1003),12,fill=(18,16,24,235),outline=(74,61,94,255),width=2)
        d.text((660,949),'FILES  →  IDENTIFIERS  →  ?  →  ?  →  CONNECTION',font=font(19,'mono'),fill=(*MUTED,255))
    return im.convert('RGB')

def overload_scene(t,variant):
    im=background(t);eyebrow(im,'THE MANUAL SEARCH SPACE')
    d=ImageDraw.Draw(im,'RGBA')
    nodes=[]
    for i in range(46):
        ang=i*2.399+t*.012;rad=90+17*i
        x=W/2+math.cos(ang)*rad*1.18;y=H/2+math.sin(ang)*rad*.58
        nodes.append((x,y));r=3+(i%4);d.ellipse((x-r,y-r,x+r,y+r),fill=(150,130,190,130))
    for i in range(70):
        a=nodes[(i*7)%len(nodes)];b=nodes[(i*13+5)%len(nodes)]
        d.line((*a,*b),fill=(104,82,136,32 if variant==0 else 48),width=1)
    if variant==0:
        draw_text(im,(110,160),'More records.',66,TEXT,'serif');draw_text(im,(110,250),'More cross-referencing.',66,TEXT,'serif')
        draw_text(im,(110,860),'Every new source expands the search space.',24,MUTED)
    else:
        box=(525,380,1395,710);d.rounded_rectangle(box,18,fill=(14,13,19,235),outline=(78,62,101,255),width=2)
        draw_text(im,(W/2,458),'MANUAL CROSS-REFERENCE',19,LILAC,'semi','mm')
        draw_text(im,(W/2,535),'Slow to trace.\nEasy to miss.',52,TEXT,'serif','mm',14)
        draw_text(im,(W/2,655),'The problem is correlation.',20,MUTED,'sans','mm')
    return im.convert('RGB')

def statement_scene(t,title,sub='',kind='question'):
    im=background(t);eyebrow(im,'FROM SEARCH TO UNDERSTANDING')
    a=ease(clamp(t/1.2));x=110+(1-a)*90
    draw_text(im,(x,330),title,68,TEXT,'serif')
    if sub:draw_text(im,(x+4,610),sub,25,MUTED)
    d=ImageDraw.Draw(im,'RGBA');progress=clamp((t-2)/5)
    d.line((110,760,110+int(1500*progress),760),fill=(139,92,246,170),width=3)
    for i in range(6):
        px=110+i*300
        if progress>i/5:d.ellipse((px-7,753,px+7,767),fill=(*VIOLET,255))
    return im.convert('RGB')

def logo_scene(t,final=False):
    im=background(t);a=ease(clamp(t/1.6));layer=Image.new('RGBA',(W,H),(0,0,0,0))
    logo=Image.open(LOGO).convert('RGBA');logo.thumbnail((140,140),Image.Resampling.LANCZOS)
    if final:
        layer.alpha_composite(logo,(W//2-70,240));draw_text(layer,(W/2,430),'NETWORK INTEL',65,TEXT,'semi','mm')
        draw_text(layer,(W/2,535),'From fragmented records to explainable intelligence.',30,LILAC,'serif','mm')
        draw_text(layer,(W/2,710),'SIH 26189  ·  AI-POWERED CRIMINAL NETWORK ANALYSIS SYSTEM',18,MUTED,'semi','mm')
        draw_text(layer,(W/2,755),'MINISTRY OF HOME AFFAIRS',17,MUTED,'sans','mm')
    else:
        layer.alpha_composite(logo,(W//2-70,310));draw_text(layer,(W/2,500),'NETWORK INTEL',68,TEXT,'semi','mm')
        draw_text(layer,(W/2,605),'From fragmented records to explainable intelligence.',29,LILAC,'serif','mm')
    layer.putalpha(int(255*a));return Image.alpha_composite(im,layer).convert('RGB')

def pipeline_scene(t):
    im=background(t);eyebrow(im,'THE TRANSFORMATION')
    draw_text(im,(110,150),'Turn fragments into an investigation.',54,TEXT,'serif')
    stages=[('01','UNDERSTAND'),('02','RESOLVE'),('03','CONNECT'),('04','ANALYZE'),('05','EXPLAIN')]
    d=ImageDraw.Draw(im,'RGBA')
    for i,(num,label) in enumerate(stages):
        x=105+i*355;appear=ease(clamp((t-.5-i*.65)/.7))
        d.rounded_rectangle((x,455,x+285,630),12,fill=(25,22,35,int(230*appear)),outline=(88,68,119,int(255*appear)),width=2)
        d.text((x+24,478),num,font=font(16,'mono'),fill=(*MUTED,int(255*appear)))
        d.text((x+24,545),label,font=font(22,'semi'),fill=(*TEXT,int(255*appear)))
        if i<4:
            p=ease(clamp((t-1.0-i*.65)/.7));d.line((x+285,542,x+342,542),fill=(*VIOLET,int(230*p)),width=3)
    draw_text(im,(110,790),'DATA  →  ENTITIES  →  RELATIONSHIPS  →  NETWORK  →  INTELLIGENCE',21,LILAC,'mono')
    return im.convert('RGB')

def names_scene(t):
    im=background(t);eyebrow(im,'ENTITY RESOLUTION')
    names=['Rahul Sharma','Rahul K. Sharma','R. K. Sharma'];ys=[300,475,650]
    d=ImageDraw.Draw(im,'RGBA')
    for i,(name,y) in enumerate(zip(names,ys)):
        x=130+int((1-ease(clamp((t-i*.5)/1)))*(-260 if i%2==0 else 260))
        d.rounded_rectangle((x,y,x+650,y+110),10,fill=(23,21,31,245),outline=(73,61,92,255),width=2)
        d.text((x+30,y+34),name,font=font(30,'serif'),fill=(*TEXT,255))
    p=ease(clamp((t-2.0)/1.2));line(im,(890,355,1160,525),(*VIOLET,int(255*p)),3);line(im,(890,530,1160,525),(*VIOLET,int(255*p)),3);line(im,(890,705,1160,525),(*VIOLET,int(255*p)),3)
    d.rounded_rectangle((1160,430,1760,620),14,fill=(30,24,43,int(240*p)),outline=(*VIOLET,int(255*p)),width=2)
    d.text((1205,468),'POSSIBLE MATCH',font=font(18,'semi'),fill=(*LILAC,int(255*p)))
    d.text((1205,518),'Evidence + investigator review',font=font(27,'serif'),fill=(*TEXT,int(255*p)))
    d.text((1205,570),'No automatic certainty',font=font(17,'mono'),fill=(*MUTED,int(255*p)))
    return im.convert('RGB')

path_nodes=[('Rahul Sharma','Person'),('P101','Phone'),('P204','Phone'),('Amit Verma','Person'),('A17','Account'),('A31','Account'),('Vikram Singh','Person')]
path_edges=['USES','CALLED','USED BY','CONTROLS','TRANSFERRED TO','CONTROLLED BY']
path_pos=[(175,470),(430,470),(685,470),(950,470),(1205,470),(1460,470),(1715,470)]
def shape(d,x,y,kind,color,width=4,r=35):
    if kind=='Phone':d.rounded_rectangle((x-r*.65,y-r,x+r*.65,y+r),8,outline=color,width=width)
    elif kind=='Account':
        pts=[(x-r,y),(x-r/2,y-r*.86),(x+r/2,y-r*.86),(x+r,y),(x+r/2,y+r*.86),(x-r/2,y+r*.86)]
        d.line(pts+[pts[0]],fill=color,width=width,joint='curve')
    else:d.ellipse((x-r,y-r,x+r,y+r),outline=color,width=width)
def graph_scene(t,hero=False):
    im=background(t);eyebrow(im,'FIND THE HIDDEN CONNECTION' if hero else 'BUILD THE NETWORK')
    title='One question. One inspectable path.' if hero else 'Relationships become visible.'
    draw_text(im,(110,140),title,48,TEXT,'serif')
    d=ImageDraw.Draw(im,'RGBA')
    if hero:
        reveal=clamp((t-1.0)/8.5)*6
    else:reveal=clamp((t-.6)/7.5)*6
    for i,(label,kind) in enumerate(path_nodes):
        x,y=path_pos[i];active=reveal>=i-.05;alpha=255 if active else 42
        if i>0 and reveal>i-1:
            frac=clamp(reveal-(i-1));x0,y0=path_pos[i-1];xx=x0+(x-x0)*frac
            d.line((x0+42,y0,xx-42,y),fill=(*VIOLET,int(235*frac)),width=5)
            if frac>.45:
                mid=(x0+x)//2;d.rectangle((mid-60,y-19,mid+60,y+18),fill=(10,10,15,220));d.text((mid,y),path_edges[i-1],font=font(13,'mono'),fill=(*LILAC,int(255*frac)),anchor='mm')
        shape(d,x,y,kind,(*VIOLET,alpha),5 if active else 2,39)
        d.text((x,y+76),label,font=font(20,'serif'),fill=(*TEXT,alpha),anchor='mm')
        d.text((x,y+110),kind.upper(),font=font(11,'mono'),fill=(*MUTED,alpha),anchor='mm')
    if not hero:
        for x,y,label in [(320,760,'A44'),(1070,770,'R.K. SHARMA'),(1540,760,'LOCATION')]:
            d.ellipse((x-24,y-24,x+24,y+24),outline=(96,82,116,85),width=2);d.text((x,y+55),label,font=font(12,'mono'),fill=(120,112,130,80),anchor='mm')
    if hero and reveal>=5.95:
        a=ease(clamp((t-9.4)/.8));d.rounded_rectangle((560,770,1360,900),14,fill=(28,22,41,int(245*a)),outline=(*VIOLET,int(255*a)),width=2)
        d.text((W//2,807),'CONNECTION DISCOVERED',font=font(20,'semi'),fill=(*LILAC,int(255*a)),anchor='mm')
        d.text((W//2,858),'6 HOPS   ·   8 EVIDENCE REFERENCES',font=font(25,'mono'),fill=(*TEXT,int(255*a)),anchor='mm')
    return im.convert('RGB')

def triad_scene(t):
    im=background(t);eyebrow(im,'TRUST BY DESIGN')
    draw_text(im,(110,150),'An investigation cannot depend on a black box.',50,TEXT,'serif')
    stages=[('EVIDENCE','Source-backed assertion',GREEN),('INFERENCE','System-generated association',VIOLET),('HUMAN REVIEW','Investigator decision',LILAC)]
    d=ImageDraw.Draw(im,'RGBA')
    for i,(a,b,c) in enumerate(stages):
        x=110+i*585;p=ease(clamp((t-.5-i*.75)/.8))
        d.rounded_rectangle((x,430,x+500,680),14,fill=(22,20,29,int(240*p)),outline=(*c,int(255*p)),width=2)
        d.text((x+30,472),a,font=font(19,'semi'),fill=(*c,int(255*p)))
        d.text((x+30,548),b,font=font(28,'serif'),fill=(*TEXT,int(255*p)))
        d.text((x+30,625),'INSPECTABLE',font=font(13,'mono'),fill=(*MUTED,int(255*p)))
        if i<2:d.line((x+500,555,x+558,555),fill=(*VIOLET,int(220*p)),width=3)
    return im.convert('RGB')

def benefits_scene(t):
    im=background(t);eyebrow(im,'THE INVESTIGATIVE SHIFT')
    items=['REDUCE MANUAL CROSS-REFERENCING','REVEAL NON-OBVIOUS PATHS','PRESERVE EVIDENCE PROVENANCE']
    for i,s in enumerate(items):
        a=fade_window(t, i*3.0, i*3.0+4.2,.7)
        if a>0:
            draw_text(im,(W/2,470),s,42,(*TEXT[:3],) if False else TEXT,'semi','mm')
            d=ImageDraw.Draw(im,'RGBA');d.line((560,535,1360,535),fill=(*VIOLET,int(220*a)),width=3)
            # opacity through overlay mask
    draw_text(im,(W/2,720),'ENTITIES  →  RELATIONSHIPS  →  NETWORK  →  REVIEWABLE LEADS',18,LILAC,'mono','mm')
    return im.convert('RGB')

def render_motion(name,duration,renderer):
    out=CLIPS/(name+'.mp4')
    if out.exists():return
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(MOTION_FPS),'-i','-','-vf',f'fade=t=in:st=0:d=0.18,fade=t=out:st={duration-0.22}:d=0.22,fps={FPS}','-an','-c:v','libx264','-preset','ultrafast','-crf','17','-pix_fmt','yuv420p',str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for n in range(round(duration*MOTION_FPS)):
            try:p.stdin.write(renderer(n/MOTION_FPS).tobytes())
            except OSError:
                raise RuntimeError(p.stderr.read().decode('utf-8','replace'))
        p.stdin.close();err=p.stderr.read();code=p.wait()
        if code:raise RuntimeError(err.decode('utf-8','replace'))
    finally:
        if p.poll() is None:p.kill()
    print('motion',name,flush=True)

def ui_clip(name,src,duration,zoom=1.04,cx=.5,cy=.5):
    out=CLIPS/(name+'.mp4')
    if out.exists():return
    frames=round(duration*FPS); z0=zoom;z1=zoom+.025
    vf=f"scale=2304:1296,zoompan=z='{z0}+({z1-z0})*on/{frames-1}':x='iw*{cx}-iw/zoom/2':y='ih*{cy}-ih/zoom/2':d={frames}:s=1920x1080:fps=30,fade=t=in:st=0:d=0.2,fade=t=out:st={duration-0.24}:d=0.24"
    ff('-loop','1','-i',str(CAP/src),'-vf',vf,'-frames:v',str(frames),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(out))
    print('ui',name,flush=True)

def recorded_clip(name,start,length,duration):
    out=CLIPS/(name+'.mp4')
    if out.exists():return
    speed=duration/length
    vf=f"setpts={speed}*(PTS-STARTPTS),fps=30,scale=1920:1080,fade=t=in:st=0:d=0.15,fade=t=out:st={duration-0.2}:d=0.2"
    ff('-ss',str(start),'-t',str(length),'-i',str(CAP/'current-flow.webm'),'-vf',vf,'-t',str(duration),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(out))
    print('recorded',name,flush=True)

voice=[
(.7,6.4,'A criminal network rarely appears in a single file.'),
(7.0,14.6,'One name may sit in a complaint. A phone in a call record. An account in a transaction. A location somewhere else.'),
(15.2,22.6,'The evidence may already exist. The connection may still be buried.'),
(23.3,30.1,'And as records multiply, the search space grows faster than any manual review.'),
(33.1,39.1,'What if those fragments could become one connected investigation?'),
(43.1,45.1,'Network Intel.'),
(50.0,64.8,'It processes supported structured records and controlled report text, turning isolated mentions into entities investigators can work with: people, phones, accounts, vehicles and locations.'),
(67.0,79.7,'Because the same person can appear differently across records, Network Intel proposes possible identity matches. Evidence supports the comparison. Uncertainty stays with the investigator.'),
(82.1,98.3,'Relationships once scattered across files become part of one investigation graph. People, devices and accounts can now be explored in context, without losing the records that support them.'),
(101.0,110.8,'Now ask a question that would otherwise require record-by-record searching. How are Rahul Sharma and Vikram Singh connected?'),
(111.4,122.4,'Network Intel runs a bounded graph search. One sourced step at a time, a six-hop association emerges through P101, P204, Amit Verma, A17 and A31.'),
(125.2,131.7,'But an investigation cannot depend on a black box. Every important connection must remain inspectable.'),
(134.0,143.9,'Here, the analytical lead returns to the transaction file, exact row, timestamp, verification status and original excerpt.'),
(146.0,157.9,'The system surfaces a connection. Evidence supports it. The investigator remains the final authority, able to confirm, reject, defer, or request more evidence.'),
(160.0,168.2,'Less manual cross-referencing. Non-obvious paths made visible. Reviewable leads with their evidence still attached.'),
(169.2,174.7,'The evidence may already be there. Network Intel helps investigators see how it connects.'),
]

async def make_voice():
    for i,(a,b,s) in enumerate(voice):
        p=AUDIO/f'voice-{i:02}.mp3'
        if not p.exists():await edge_tts.Communicate(s,'en-IN-PrabhatNeural',rate='-8%',pitch='-2Hz').save(str(p))
        print('voice',i,flush=True)

def make_audio():
    sr=48000;t=np.arange(sr*DURATION,dtype=np.float64)/sr
    music=np.zeros(len(t),np.float64)
    # Original restrained four-act score: sub pulse, evolving harmonic bed, sparse felt-like tones.
    roots=[55,55,65.406,73.416,55,82.407,73.416]
    bounds=[0,31,49,100,124,159,169,175]
    for j,f in enumerate(roots):
        mask=(t>=bounds[j])&(t<bounds[j+1]);tt=t[mask]-bounds[j]
        attack=np.minimum(1,tt/2);release=np.minimum(1,(bounds[j+1]-t[mask])/2)
        env=attack*release
        music[mask]+=env*(.010*np.sin(2*np.pi*f*tt)+.005*np.sin(2*np.pi*f*1.5*tt)+.003*np.sin(2*np.pi*f*2*tt))
    pulse_env=np.interp(t,[0,8,31,41,49,100,106,118,124,145,159,169,175],[.25,.35,.55,.25,.7,.8,.95,1.25,.65,.38,.65,.55,0])
    for beat in np.arange(1,DURATION,1.5):
        a=int(beat*sr);n=min(int(.45*sr),len(t)-a);u=np.arange(n)/sr
        music[a:a+n]+=.010*pulse_env[a]*np.sin(2*np.pi*(110+25*np.exp(-u*9))*u)*np.exp(-u*8)
    for beat,note in [(41,440),(49,523.25),(106,392),(108,440),(110,493.88),(112,523.25),(114,587.33),(116,659.25),(118,783.99),(169,523.25)]:
        a=int(beat*sr);n=min(int(2.8*sr),len(t)-a);u=np.arange(n)/sr
        tone=.013*np.sin(2*np.pi*note*u)*np.exp(-u*1.4)*(1-np.exp(-u*18))
        music[a:a+n]+=tone
    # soft filtered noise gives the opening texture air
    rng=np.random.default_rng(26189);noise=rng.normal(0,1,len(t));kernel=np.ones(1200)/1200
    smooth=np.convolve(noise,kernel,mode='same');music+=smooth*.006*np.interp(t,[0,31,49,124,145,175],[1,.8,.35,.2,.25,0])
    stereo=np.column_stack((music,music*.97))
    subtitles=[]
    for i,(a,b,s) in enumerate(voice):
        mp=AUDIO/f'voice-{i:02}.mp3';raw=AUDIO/f'voice-{i:02}.f32'
        dur=float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',mp]).decode().strip())
        target=b-a-.12;tempo=max(1,dur/target)
        filters=f'atempo={tempo:.6f},highpass=f=70,lowpass=f=12500,acompressor=threshold=-20dB:ratio=2.2:attack=15:release=160,loudnorm=I=-17:TP=-2:LRA=6'
        ff('-i',str(mp),'-af',filters,'-ar',str(sr),'-ac','1','-f','f32le',str(raw))
        v=np.fromfile(raw,np.float32);start=round(a*sr);n=min(len(v),len(t)-start);stereo[start:start+n]+=v[:n,None]
        subtitles.append((a,a+n/sr,s))
    # sparse, editorial sound cues only
    cues=[(1.1,620,.010),(3.1,720,.009),(7.2,560,.009),(9.0,680,.009),(41.2,880,.015),(49.0,1046,.014)]
    cues += [(106+i*1.65,520+i*75,.011) for i in range(7)]
    cues += [(133.3,760,.009),(145.1,900,.010),(152.0,660,.010),(169.1,1046,.012)]
    for when,freq,level in cues:
        a=int(when*sr);n=min(int(.25*sr),len(t)-a);u=np.arange(n)/sr
        s=level*np.sin(2*np.pi*freq*u)*np.exp(-u*20)*(1-np.exp(-u*90));stereo[a:a+n]+=s[:,None]
    peak=np.max(np.abs(stereo));stereo*=min(1,.95/peak)
    with wave.open(str(AUDIO/'master.wav'),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((stereo*32767).astype('<i2').tobytes())
    def stamp(x):
        ms=round(x*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    (ROOT/'Network-Intel-SIH26189.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(subtitles)),encoding='utf-8')

shots=[
('01-fragments',8),('02-fragments',7),('03-overload',8),('04-manual',8),('05-question',10),('06-brand',8),
('07-pipeline',8),('08-sources-ui',9),('09-names',6),('10-resolution-ui',9),('11-graph-build',10),('12-network-ui',9),
('13-hero-question',6),('14-path-progressive',12),('15-path-live',6),('16-trust',9),('17-evidence-live',5),('18-evidence-close',7),
('19-review-ui',7),('20-audit-ui',7),('21-benefits',10),('22-final',6)]

def make_picture():
    render_motion('01-fragments',8,lambda t:fragments_scene(t,0))
    render_motion('02-fragments',7,lambda t:fragments_scene(t,1))
    render_motion('03-overload',8,lambda t:overload_scene(t,0))
    render_motion('04-manual',8,lambda t:overload_scene(t,1))
    render_motion('05-question',10,lambda t:statement_scene(t,'What if fragmented information\ncould become one connected investigation?','Connect the evidence. Reveal the network.'))
    render_motion('06-brand',8,lambda t:logo_scene(t,False))
    render_motion('07-pipeline',8,pipeline_scene)
    ui_clip('08-sources-ui','02-data-sources.png',9,1.02,.52,.48)
    render_motion('09-names',6,names_scene)
    ui_clip('10-resolution-ui','04-entity-resolution.png',9,1.07,.55,.52)
    render_motion('11-graph-build',10,lambda t:graph_scene(t,False))
    ui_clip('12-network-ui','05-network-context.png',9,1.06,.48,.48)
    render_motion('13-hero-question',6,lambda t:statement_scene(t,'How are Rahul Sharma and\nVikram Singh connected?','A question across multiple source records.'))
    render_motion('14-path-progressive',12,lambda t:graph_scene(t,True))
    recorded_clip('15-path-live',5.7,2.8,6)
    render_motion('16-trust',9,triad_scene)
    recorded_clip('17-evidence-live',8.9,2.4,5)
    ui_clip('18-evidence-close','08-evidence.png',7,1.36,.83,.48)
    ui_clip('19-review-ui','09-human-review.png',7,1.25,.82,.54)
    ui_clip('20-audit-ui','11-audit-trail.png',7,1.14,.52,.51)
    render_motion('21-benefits',10,benefits_scene)
    render_motion('22-final',6,lambda t:logo_scene(t,True))
    concat=ROOT/'concat.txt';concat.write_text('\n'.join("file '"+(CLIPS/(n+'.mp4')).as_posix()+"'" for n,_ in shots),encoding='utf-8')
    ff('-reinit_filter','0','-f','concat','-safe','0','-i',str(concat),'-i',str(AUDIO/'master.wav'),'-i',str(ROOT/'Network-Intel-SIH26189.srt'),'-map','0:v','-map','1:a','-map','2:s','-vf','setsar=1','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-c:s','mov_text','-metadata:s:s:0','language=eng','-metadata','title=Network Intel | SIH 26189','-movflags','+faststart','-t',str(DURATION),str(ROOT/'Network-Intel-SIH26189-Premium-1080p.mp4'))

if __name__=='__main__':
    (ROOT/'timeline.json').write_text(json.dumps({'duration':DURATION,'resolution':[W,H],'fps':FPS,'shots':shots,'voiceover':voice},indent=2),encoding='utf-8')
    asyncio.run(make_voice());make_audio();make_picture();print('COMPLETE',flush=True)
