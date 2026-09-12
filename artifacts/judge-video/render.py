"""Render the genuine captured UI scenes as a captioned 165-second MP4."""
import json, subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'sequence.json').read_text(encoding='utf-8'))
def timecode(seconds):
    return f'{seconds//3600:02}:{seconds%3600//60:02}:{seconds%60:02},000'
lines=[]; captions=[]; start=0
for i,scene in enumerate(data['shots'],1):
    lines.extend([f"file '{scene['name']}.png'",f"duration {scene['duration']}"])
    words=scene['caption'].split(); wrapped=[]; line=''
    for word in words:
        if len(line+' '+word)>90: wrapped.append(line);line=word
        else: line=(line+' '+word).strip()
    wrapped.append(line)
    captions.append(f"{i}\n{timecode(start)} --> {timecode(start+scene['duration'])}\n"+'\n'.join(wrapped)+'\n')
    start+=scene['duration']
lines.append(f"file '{data['shots'][-1]['name']}.png'")
(root/'frames.txt').write_text('\n'.join(lines),encoding='utf-8')
(root/'captions.srt').write_text('\n'.join(captions),encoding='utf-8')
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i','frames.txt','-vf',"pad=1920:1080:0:0:color=0x090f19,subtitles=captions.srt:force_style='FontName=Arial,FontSize=9,PrimaryColour=&H00FFFFFF,Outline=0,Shadow=0,MarginV=8,Alignment=2'",'-t',str(start),'-r','30','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart','VEIL-SIH-Judge-Demo.mp4'],cwd=root,check=True)
print(f'Rendered {start}s captioned MP4')

