"""Motion-led edit of genuine VEIL captures with offline English narration."""
import json, subprocess, textwrap
from pathlib import Path
root=Path(__file__).resolve().parent
shots=json.loads((root/'sequence.json').read_text(encoding='utf-8'))['shots']
narration=json.loads((root/'narration.json').read_text(encoding='utf-8'))
def run(args):
    subprocess.run(args,cwd=root,check=True,stdout=subprocess.DEVNULL,stderr=open(root/'render-voiced.log','a',encoding='utf-8'))
def stamp(t):
    return f'{int(t)//3600}:{int(t)%3600//60:02}:{t%60:05.2f}'
base='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Segoe UI,25,&H00E9D554,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,0,0,5,65,65,0,1
Style: Speech,Segoe UI,30,&H00F7F5F1,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,80,80,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
total=0;metrics=[]
for i,(shot,note) in enumerate(zip(shots,narration),1):
    duration=shot['duration'];wav=f'voice-{i:02}.wav'
    seconds=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',wav],cwd=root,text=True).strip())
    tempo=max(1,seconds/(duration-0.7));spoken=seconds/tempo
    metrics.append({'scene':i,'voice_seconds':seconds,'tempo':tempo,'scene_seconds':duration})
    ass=base+f'Dialogue: 0,0:00:00.00,{stamp(duration)},Title,,0,0,0,,{{\\pos(960,945)\\fad(220,220)}}'+note['title']+'\n'
    sentences=[s.strip()+'.' for s in note['voice'].split('. ') if s.strip()]
    start=.25
    for sentence in sentences:
        sentence=sentence.rstrip('.')+'.'
        length=spoken*len(sentence)/sum(len(s) for s in sentences)
        wrapped='\\N'.join(textwrap.wrap(sentence,108))
        ass+=f'Dialogue: 1,{stamp(start)},{stamp(min(duration-.15,start+length))},Speech,,0,0,0,,{{\\pos(960,1010)\\fad(120,120)}}{wrapped}\n'
        start+=length
    assfile=f'scene-{i:02}.ass';(root/assfile).write_text(ass,encoding='utf-8')
    # A subtle camera move keeps the source UI legible; all callouts stay in the editorial band.
    frames=duration*30
    vf=(f"scale=1920:960,zoompan=z='1+0.018*on/{frames}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=1792x896:fps=30,"
        f"pad=1920:1080:64:16:color=0x090f19,subtitles={assfile},"
        f"drawbox=x=64:y=1070:w=1792:h=3:color=0x1e3042:t=fill,"
        f"drawbox=x=64:y=1070:w={int(1792*(total+duration)/165)}:h=3:color=0x36d8ee:t=fill,"
        f"fade=t=in:st=0:d=0.22,fade=t=out:st={duration-.22}:d=0.22")
    run(['ffmpeg','-y','-i',shot['name']+'.png','-i',wav,'-vf',vf,'-af',f'atempo={tempo:.5f},apad,afade=t=in:d=0.06,afade=t=out:st={duration-.2}:d=0.2','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-b:a','160k',f'motion-{i:02}.mp4'])
    total+=duration
    print(f'Scene {i}/13 rendered',flush=True)
(root/'motion-concat.txt').write_text('\n'.join(f"file 'motion-{i:02}.mp4'" for i in range(1,14)),encoding='utf-8')
run(['ffmpeg','-y','-f','concat','-safe','0','-i','motion-concat.txt','-c','copy','-movflags','+faststart','VEIL-SIH-Voiced-Demo.mp4'])
(root/'voice-verification.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print('Finished VEIL-SIH-Voiced-Demo.mp4',flush=True)
