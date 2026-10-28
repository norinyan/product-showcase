"""Shared edit/caption/audio/export pipeline, driven by a small project JSON."""
import argparse,json,subprocess,sys
from pathlib import Path
from media import assemble,subtitles,mix,normalize,probe

def run(args):subprocess.run([str(x)for x in args],check=True)
def validate_cues(cues,duration):
 end=0
 for c in cues:
  if not 0<=float(c['start'])<float(c['end'])<=duration:raise ValueError('Caption outside timeline')
  if c['start']<end:raise ValueError('Overlapping caption/voice windows')
  if not c['text'].strip():raise ValueError('Empty caption')
  end=c['end']

def prepare_audio(path,out,duration):
 run(['ffmpeg','-v','error','-i',path,'-af',f'apad,atrim=duration={duration},asetpts=PTS-STARTPTS','-ar','48000','-ac','2','-c:a','pcm_s24le','-y',out])

def build(config_path,output):
 config_path=Path(config_path).resolve();root=config_path.parent;cfg=json.loads(config_path.read_text());out=Path(output).resolve();out.mkdir(parents=True,exist_ok=True)
 duration=float(cfg['duration']);v=cfg.get('video',{});width=v.get('width',1920);height=v.get('height',1080);fps=v.get('fps',60)
 cap=cfg['captions'];cues=json.loads((root/cap['file']).read_text());validate_cues(cues,duration)
 subtitles(cues,out/'captions.ass',cap.get('size',40),cap.get('font','DejaVu Sans'),cap.get('brand',''),cap.get('color','4F4F4F'))
 # Filter paths are relative to the output directory; paths never enter shell commands.
 inputs=[];chains=[];total=0
 for i,clip in enumerate(cfg['clips']):
  source=root/clip['file'];meta=probe(source);length=float(meta['format']['duration']);start=float(clip.get('start',0));end=float(clip.get('end',length))
  if not 0<=start<end<=length+.03:raise ValueError('Clip bounds outside source')
  total+=end-start;inputs+=['-i',str(source)]
  filters=[f'trim=start={start}:end={end}','setpts=PTS-STARTPTS']
  if v.get('crop'):filters+=['crop='+':'.join(map(str,v['crop']))]
  content=v.get('content_size',[width,height]);offset=v.get('offset',[0,0]);background=v.get('background','white')
  filters+=[f'scale={content[0]}:{content[1]}:flags=lanczos',f'pad={width}:{height}:{offset[0]}:{offset[1]}:color={background}',f'fps={fps}','setsar=1']
  chains.append(f'[{i}:v]'+','.join(filters)+f'[clip{i}]')
 if abs(total-duration)>.04:raise ValueError(f'Clip durations {total} must match project duration {duration}')
 tail=f'concat=n={len(cfg["clips"])}:v=1:a=0,ass=captions.ass'
 if v.get('fade_in',0):tail+=f',fade=t=in:st=0:d={v["fade_in"]}:color={background}'
 if v.get('fade_out',0):tail+=f',fade=t=out:st={duration-v["fade_out"]}:d={v["fade_out"]}:color={background}'
 chains.append(''.join(f'[clip{i}]'for i in range(len(cfg['clips'])))+tail+'[video]')
 subprocess.run(['ffmpeg','-v','warning',*inputs,'-filter_complex',';'.join(chains),'-map','[video]','-t',str(duration),'-an','-c:v','libx264','-preset','medium','-crf',str(v.get('crf',17)),'-pix_fmt','yuv420p','-movflags','+faststart','-y','video-only.mp4'],cwd=out,check=True)
 audio=cfg.get('audio',{});stems=out/'audio';stems.mkdir(exist_ok=True)
 narration=audio.get('narration')
 if narration=='cues':assemble(cues,root,stems/'voice.wav',duration)
 elif narration:
  prepare_audio(root/narration,stems/'voice-prepared.wav',duration);normalize(stems/'voice-prepared.wav',stems/'voice.wav',I=-18,TP=-2.5)
 else:
  run(['ffmpeg','-v','error','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',duration,'-c:a','pcm_s24le','-y',stems/'voice.wav'])
 # The original score/foley generator is used only when requested.
 if audio.get('music')=='synthesize' or audio.get('sfx_events'):
  args=[sys.executable,Path(__file__).with_name('music.py'),stems,'--duration',duration]
  if audio.get('sfx_events'):args+=['--events',root/audio['sfx_events']]
  run(args)
 for key,default in [('music','bgm-original.wav'),('sfx','sfx.wav')]:
  value=audio.get(key);dest=stems/default
  if value and value!='synthesize':prepare_audio(root/value,dest,duration)
  elif not(value=='synthesize' or key=='sfx'and audio.get('sfx_events')):
   run(['ffmpeg','-v','error','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',duration,'-c:a','pcm_s24le','-y',dest])
 mix(stems/'voice.wav',stems/'bgm-original.wav',stems/'sfx.wav',stems)
 run(['ffmpeg','-v','warning','-i',out/'video-only.mp4','-i',stems/'mix.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',duration,'-movflags','+faststart','-y',out/'final.mp4'])
 (out/'project-resolved.json').write_text(json.dumps(cfg,indent=2));print(out/'final.mp4')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('project');p.add_argument('--output',required=True);a=p.parse_args();build(a.project,a.output)
