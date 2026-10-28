"""Verify the exported artifact, not just the editor's exit status."""
import argparse,json,re,subprocess
from pathlib import Path
from media import probe
p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('output');p.add_argument('--duration',type=float,required=True);p.add_argument('--width',type=int,default=1920);p.add_argument('--height',type=int,default=1080);p.add_argument('--fps',type=float,default=60);p.add_argument('--regions');p.add_argument('--sync');p.add_argument('--times',type=float,nargs='*',default=[]);a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
info=probe(a.video);v=next(s for s in info['streams']if s['codec_type']=='video');audio=next(s for s in info['streams']if s['codec_type']=='audio');num,den=map(int,v['avg_frame_rate'].split('/'))
if (v['width'],v['height'],v['codec_name'],v['pix_fmt'])!=(a.width,a.height,'h264','yuv420p')or abs(num/den-a.fps)>.001:raise ValueError('Unexpected video specifications')
if audio['codec_name']!='aac'or audio['channels']!=2 or audio['sample_rate']!='48000':raise ValueError('Missing or unexpected AAC audio')
if abs(float(info['format']['duration'])-a.duration)>.05:raise ValueError('Unexpected duration')
r=subprocess.run(['ffmpeg','-hide_banner','-xerror','-i',a.video,'-vf','blackdetect=d=0.016:pix_th=0.10:pic_th=0.98','-f','null','-'],stderr=subprocess.PIPE,text=True,check=True);(out/'decode-and-blackcheck.txt').write_text(r.stderr)
if re.search(r'black_start:',r.stderr):raise ValueError('Black frames detected; inspect report before delivery')
r=subprocess.run(['ffmpeg','-hide_banner','-i',a.video,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-'],stderr=subprocess.PIPE,text=True,check=True);loudness=json.loads(r.stderr[r.stderr.rfind('{'):]);(out/'loudness.json').write_text(json.dumps(loudness,indent=2))
if not -16.5<=float(loudness['input_i'])<=-15.5 or float(loudness['input_tp'])>-1:raise ValueError('Audio loudness/peak outside target')
if a.sync:
 sync=json.loads(Path(a.sync).read_text())
 if not all(c['caption_start']<=c['audio_start']<c['audio_end']<=c['caption_end']for c in sync):raise ValueError('Narration outside caption windows')
if a.regions:
 from flash import scan
 scan(a.video,a.regions,out/'flash-report.json')
 if json.loads((out/'flash-report.json').read_text())['bad_frames']:raise ValueError('Flash candidates found; review, do not auto-hide')
# Inspect actual encoded frames, including full-rate neighborhoods of suspect times.
for t in a.times:
 first=max(0,round((t-.2)*a.fps));last=min(round(a.duration*a.fps)-1,first+23)
 subprocess.run(['ffmpeg','-v','error','-i',a.video,'-vf',f"select='between(n,{first},{last})',scale=480:270,tile=4x6",'-frames:v','1','-y',str(out/f'frames-{t:g}.jpg')],check=True)
subprocess.run(['ffmpeg','-v','error','-i',a.video,'-vf',f'fps=12/{a.duration},scale=480:270,tile=4x3','-frames:v','1','-y',str(out/'contact-sheet.jpg')],check=True)
subprocess.run(['ffmpeg','-v','error','-ss',str(min(9,a.duration/2)),'-i',a.video,'-vf','scale=390:-2','-frames:v','1','-y',str(out/'phone-preview.png')],check=True)
(out/'video-info.json').write_text(json.dumps(info,indent=2));report={'resolution':[v['width'],v['height']],'fps':num/den,'duration':float(info['format']['duration']),'full_decode':'passed','black_frames':'none detected','loudness_lufs':float(loudness['input_i']),'true_peak_dbtp':float(loudness['input_tp']),'roi_flash_scan':'passed'if a.regions else'not requested','narration_windows':'passed'if a.sync else'not requested','subjective_listening':'not performed by this script'};(out/'acceptance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
