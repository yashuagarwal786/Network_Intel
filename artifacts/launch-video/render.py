"""Reproducible VEIL film. Run: python render.py (vendor dependencies beside script)."""
from pathlib import Path
import sys, asyncio, json, subprocess, math, wave
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import edge_tts
ART=ROOT.parent
SRC=ART/'first-round'/'screenshots'
W,H=1920,1080
BG='#080d17'; WHITE='#eef3fb'; MUTED='#91a4bc'; CYAN='#36d9ec'
FONT='C:/Windows/Fonts/segoeui.ttf'; BOLD='C:/Windows/Fonts/segoeuib.ttf'
for p in ['plates','clips','audio']: (ROOT/p).mkdir(exist_ok=True)
def run(args): subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def font(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)
def txt(d,xy,s,n=30,fill=WHITE,b=False): d.text(xy,s,font=font(n,b),fill=fill)
def centered(d,y,s,n=60,fill=WHITE,b=False):
    box=d.textbbox((0,0),s,font=font(n,b)); txt(d,((W-box[2])/2,y),s,n,fill,b)
def plate(name,chapter='',crop=None,title=None,subtitle=None):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    if name:
        src=Image.open(SRC/name).convert('RGB')
        if crop: src=src.crop(crop)
        src.thumbnail((1776,900),Image.Resampling.LANCZOS)
        # Upscale captured UI consistently, preserving aspect ratio.
        scale=min(1776/src.width,900/src.height)
        src=src.resize((round(src.width*scale),round(src.height*scale)),Image.Resampling.LANCZOS)
        x=(W-src.width)//2; y=94+(900-src.height)//2
        im.paste(src,(x,y)); d=ImageDraw.Draw(im)
        d.rounded_rectangle((x-1,y-1,x+src.width,y+src.height),radius=8,outline='#28344a',width=2)
        txt(d,(74,28),'V E I L',28,CYAN,True)
        txt(d,(260,31),chapter,24,MUTED)
        txt(d,(74,1026),'OPERATION TRINETRA  /  SYNTHETIC DEMONSTRATION',19,MUTED)
        txt(d,(1420,1026),'REAL PRODUCT CAPTURE',19,MUTED)
    else:
        d.line((120,180,240,180),fill=CYAN,width=4)
        txt(d,(120,115),'V E I L  /  INVESTIGATION INTELLIGENCE',23,MUTED)
        if title:
            lines=title.split('\n')
            for j,line in enumerate(lines): txt(d,(120,350+j*102),line,76,WHITE,True)
        if subtitle: txt(d,(124,650),subtitle,30,MUTED)
    return im

# Every UI image below is an existing captured product state. Crops are editorial.
O='08-case-overview.png'; S='01-processed-sources.png'; R='02-resolution-review.png'
N='07-network-default.png'; P='03-network-path.png'; L='04-lead-explanation.png'; E='05-evidence-provenance.png'; A='06-audit-history.png'; T='09-timeline.png'
shots=[
 (None,'',None,'Investigations generate data.','Reports. Calls. Accounts. Vehicles. Locations.'),
 (O,'01 / FRAGMENTED DATA',(204,345,810,660),None,None),
 (None,'',None,'Connections generate\nintelligence.',None),
 (O,'02 / INTRODUCING VEIL',None,None,None),
 (O,'02 / OPERATION TRINETRA',(203,140,1350,333),None,None),
 (S,'02 / DOCUMENTS → ENTITIES',None,None,None),
 (N,'02 / RELATIONSHIPS → GRAPH INTELLIGENCE',None,None,None),
 (S,'03 / DATA BECOMES INTELLIGENCE',None,None,None),
 (S,'03 / CONTROLLED SOURCE RECORDS',(205,140,1348,710),None,None),
 (R,'03 / IDENTITIES REMAIN REVIEWABLE',None,None,None),
 (R,'03 / SOURCE-BACKED RESOLUTION',(204,142,1348,690),None,None),
 (N,'03 / CONNECTED INVESTIGATION',None,None,None),
 (N,'04 / HIDDEN RELATIONSHIPS',None,None,None),
 (N,'04 / INSPECT THE NETWORK',(203,140,976,617),None,None),
 (P,'04 / A COMPUTED CONNECTION',None,None,None),
 (P,'04 / FOLLOW THE SOURCE LINKS',(205,254,975,580),None,None),
 (P,'04 / SIX HOPS. EVERY LINK SOURCED.',(205,295,975,565),None,None),
 (P,'04 / RAHUL SHARMA → VIKRAM SINGH',(205,295,975,565),None,None),
 (L,'04 / FROM CONNECTION TO REVIEW LEAD',None,None,None),
 (L,'04 / CALCULATIONS YOU CAN INSPECT',(987,143,1348,645),None,None),
 (E,'05 / EXPLAINABLE EVIDENCE',None,None,None),
 (E,'05 / EXACT SOURCE',(990,307,1348,665),None,None),
 (E,'05 / FILENAME · ROW · TIMESTAMP',(996,355,1340,537),None,None),
 (E,'05 / THE UNDERLYING RECORD',(1001,551,1340,664),None,None),
 (E,'05 / EVIDENCE IN CONTEXT',None,None,None),
 (R,'06 / HUMAN JUDGMENT',None,None,None),
 (R,'06 / REVIEW THE IDENTITY EVIDENCE',(204,142,1348,690),None,None),
 (A,'06 / THE INVESTIGATOR DECIDES',None,None,None),
 (A,'06 / NEEDS MORE EVIDENCE',(226,448,1326,691),None,None),
 (O,'07 / FROM FRAGMENTED EVIDENCE',(204,345,810,660),None,None),
 (N,'07 / TO CONNECTED INTELLIGENCE',None,None,None),
 (P,'07 / AN EVIDENCE-BACKED VIEW',None,None,None),
 (P,'07 / FOLLOW THE CONNECTION',(205,295,975,565),None,None),
 (None,'',None,'VEIL','From fragmented evidence to explainable intelligence.'),
]
# Higher-resolution captures from the retained, executed judge flow.
J=ART/'judge-video'
def replace_shot(i,name,crop=None):
    old=shots[i]; shots[i]=(str(J/name),old[1],crop,None,None)
for i in [14,15,16,17,31,32]:
    replace_shot(i,'06-path.png',(205,306,1485,770) if i in [15,16,17,32] else None)
replace_shot(18,'08-communication.png')
replace_shot(19,'09-transfers.png',(1504,195,1900,850))
replace_shot(20,'10-evidence.png')
replace_shot(21,'10-evidence.png',(1503,284,1900,617))
replace_shot(22,'10-evidence.png',(1510,324,1895,495))
replace_shot(23,'10-evidence.png',(1510,504,1895,616))
replace_shot(24,'10-evidence.png')
replace_shot(26,'04-resolution.png')
replace_shot(27,'11-review.png',(1505,193,1900,545))
replace_shot(28,'12-audit.png')
# Actual browser interaction excerpts, slowed to give the UI transition time to read.
footage={14:(34.6,1.35),20:(37.5,1.3)}
def clip_path(i): return ROOT/'clips'/f'{i:02}{"-final" if i>=14 else ""}.mp4'
script=[
 (0.8,14.0,"An investigation rarely suffers from a lack of information. The real challenge is finding the connections hidden inside it."),
 (15.5,34.0,"Meet Veil. It transforms fragmented investigation records into a structured, connected intelligence network. This is Operation Trinetra, a synthetic investigation case, moving from documents, to entities, to relationships."),
 (35.5,58.5,"Across supported source formats, Veil extracts people, phone numbers, accounts, vehicles and locations. It preserves the records behind those connections, and brings them into an investigation graph. Possible identity matches remain open to human review."),
 (60.5,72.8,"But visualizing a network isn't enough. Veil computes paths and surfaces review leads, helping investigators see connections that could be difficult to notice manually."),
 (74.0,85.8,"Here, Rahul Sharma connects to Vikram Singh through phones, an intermediary, and bank accounts. Six hops, spanning multiple source records."),
 (89.0,99.4,"The lead brings communication changes and connected transfers into one reviewable explanation. A connection to examine, not a conclusion about guilt."),
 (100.5,112.5,"And every insight remains explainable. Instead of presenting a black box conclusion, Veil traces the relationship back to the underlying evidence."),
 (113.0,124.2,"Here is the transaction source, its exact row and timestamp, and the original excerpt. The verification status stays visible alongside the record."),
 (125.5,136.8,"The system doesn't decide guilt, and it doesn't replace the investigator. Identity proposals can be inspected, confirmed, or reversed."),
 (137.0,144.4,"Here, the investigator requests more evidence, with a reason preserved in the audit trail."),
 (145.5,161.5,"What previously required investigators to manually cross reference records can now become a connected, evidence backed view of an investigation. A smaller search space. Meaningful leads. Human judgment at the center."),
 (163.0,169.4,"Veil. From fragmented evidence to explainable intelligence."),
]

async def voice():
    for i,(start,end,text) in enumerate(script):
        path=ROOT/'audio'/f'voice-{i:02}.mp3'
        if not path.exists():
            await edge_tts.Communicate(text,'en-IN-PrabhatNeural',rate='-5%').save(str(path))
        print('Narration',i,flush=True)

def audio():
    sr=48000; duration=170; t=np.arange(sr*duration,dtype=np.float64)/sr
    music=np.zeros(len(t),np.float32)
    # Original restrained instrumental bed: slow harmonic swells and sparse soft pulses.
    for freq,level in [(110,.012),(164.8138,.006),(220,.003),(261.6256,.003)]:
        music += (level*np.sin(2*np.pi*freq*t + .07*np.sin(.4*t))*(.65+.35*np.sin(.18*t)**2)).astype(np.float32)
    for beat in np.arange(1,169,2.5):
        a=int(beat*sr); n=min(sr//2,len(t)-a); u=np.arange(n)/sr
        music[a:a+n]+=(.012*np.sin(2*np.pi*(440 if int(beat)%2 else 659.25)*u)*np.exp(-u*12)*(1-np.exp(-u*100))).astype(np.float32)
    env=np.interp(t,[0,4,55,75,89,100,124,145,162,168,170],[0,.7,.8,1.35,1.1,.45,.45,.85,1,.5,0])
    music*=env
    mix=np.column_stack((music,music*.96))
    subtitles=[]
    for i,(start,end,text) in enumerate(script):
        mp=ROOT/'audio'/f'voice-{i:02}.mp3'; raw=ROOT/'audio'/f'voice-{i:02}.f32'
        dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(mp)]))
        speed=max(1,dur/(end-start-.2))
        run(['ffmpeg','-y','-i',str(mp),'-af',f'atempo={speed:.5f},loudnorm=I=-18:TP=-2:LRA=7','-ar',str(sr),'-ac','1','-f','f32le',str(raw)])
        v=np.fromfile(raw,np.float32); a=round(start*sr); n=min(len(v),len(t)-a)
        mix[a:a+n]+=v[:n,None]
        # Sentence-level optional subtitles, never paragraphs over the interface.
        sentences=[s.strip()+'.' for s in text.split('.') if s.strip()]
        pos=start; actual=n/sr
        for sentence in sentences:
            length=actual*len(sentence)/sum(map(len,sentences)); subtitles.append((pos,pos+length,sentence));pos+=length
    # Quiet editorial transition ticks, not simulated application feedback.
    for cut in [15,35,60,75,90,100,125,145,165]:
        a=cut*sr; u=np.arange(int(sr*.14))/sr
        fx=(.016*np.sin(2*np.pi*880*u)*np.exp(-u*45)*(1-np.exp(-u*150)))
        mix[a:a+len(u)]+=fx[:,None]
    peak=np.max(np.abs(mix)); mix*=min(1,.94/peak)
    with wave.open(str(ROOT/'audio'/'master.wav'),'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix*32767).astype('<i2').tobytes())
    def stamp(x):
        ms=round(x*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    (ROOT/'VEIL-Launch.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(subtitles)),encoding='utf-8')

def video():
    for i,(name,chapter,crop,title,subtitle) in enumerate(shots):
        p=ROOT/'plates'/f'{i:02}.png'; out=clip_path(i)
        im=plate(name,chapter,crop,title,subtitle)
        if i==33:
            d=ImageDraw.Draw(im); txt(d,(124,760),'INVESTIGATION INTELLIGENCE PLATFORM',23,CYAN)
        im.save(p)
        if out.exists(): continue
        if i in footage:
            start,length=footage[i]
            frame=plate(None); draw=ImageDraw.Draw(frame)
            # Neutral frame around genuine recorded UI; no simulated cursor or controls.
            frame=Image.new('RGB',(W,H),BG); draw=ImageDraw.Draw(frame)
            txt(draw,(74,28),'V E I L',28,CYAN,True);txt(draw,(260,31),chapter,24,MUTED)
            txt(draw,(74,1026),'OPERATION TRINETRA  /  SYNTHETIC DEMONSTRATION',19,MUTED)
            txt(draw,(1450,1026),'PRODUCT RECORDING',19,MUTED)
            frame.save(ROOT/'plates'/f'frame-{i}.png')
            filt=f'[0:v]crop=1920:960:0:0,setpts={5/length}*(PTS-STARTPTS),scale=1776:888,fps=30[v];[1:v][v]overlay=72:100:shortest=1,fade=t=in:st=0:d=0.16,fade=t=out:st=4.84:d=0.16[out]'
            run(['ffmpeg','-y','-ss',str(start),'-t',str(length),'-i',str(J/'page@0c4381ef7da58d7a46494b3d9ff76b7f.webm'),'-loop','1','-i',str(ROOT/'plates'/f'frame-{i}.png'),'-filter_complex',filt,'-map','[out]','-t','5','-r','30','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-an',str(out)])
            print('Rendered real interaction',i,flush=True)
            continue
        frames=150
        # Oversampled source makes slow camera motion stable at 1080p.
        vf="scale=2304:1296,zoompan=z='1+0.022*on/149':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=150:s=1920x1080:fps=30"
        vf+=',fade=t=in:st=0:d=0.16,fade=t=out:st=4.84:d=0.16'
        if i==0: vf+=',fade=t=in:st=0:d=0.7'
        if i==33: vf+=',fade=t=out:st=4:d=1'
        run(['ffmpeg','-y','-i',str(p),'-vf',vf,'-frames:v',str(frames),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-an',str(out)])
        print('Rendered shot',i+1,'/',len(shots),flush=True)
    concat=ROOT/'shots.txt'; concat.write_text('\n'.join("file '"+clip_path(i).as_posix()+"'" for i in range(len(shots))))
    run(['ffmpeg','-y','-reinit_filter','0','-f','concat','-safe','0','-i',str(concat),'-i',str(ROOT/'audio'/'master.wav'),'-i',str(ROOT/'VEIL-Launch.srt'),'-map','0:v','-map','1:a','-map','2:s','-vf','setsar=1','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-c:s','mov_text','-metadata:s:s:0','language=eng','-metadata','title=VEIL | From fragmented evidence to explainable intelligence','-movflags','+faststart','-t','170',str(ROOT/'VEIL-Launch-1080p.mp4')])

if __name__=='__main__':
    (ROOT/'timeline.json').write_text(json.dumps({'duration':170,'fps':30,'resolution':[1920,1080],'shots':[{'start':i*5,'duration':5,'source':s[0],'chapter':s[1],'crop':s[2]} for i,s in enumerate(shots)],'narration':script},indent=2))
    asyncio.run(voice());audio();video()
    print('COMPLETE',flush=True)
