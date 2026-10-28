"""Reusable subtitle, neural narration, stem assembly and ducked mixing tools.
Python 3.10+, FFmpeg; numpy/scipy for PCM assembly, Piper for optional offline synthesis.
"""
import argparse,hashlib,json,re,subprocess,wave
from pathlib import Path
import numpy as np
from scipy.io.wavfile import write
SR=48000

def run(args,**kw):return subprocess.run(args,check=True,**kw)
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
def pcm(path):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ac','1','-ar',str(SR),'-f','f32le','pipe:1']),np.float32).copy()
def write_pcm(path,data):write(str(path),SR,np.asarray(np.clip(data,-1,1)*32767,np.int16))
def words(s):return re.findall(r'[a-z0-9]+',s.lower())
def timestamp(x):return f'{int(x//3600)}:{int(x//60)%60:02}:{x%60:05.2f}'

def subtitles(cues,out,size=40,font='DejaVu Sans',brand='',color='4F4F4F'):
 if not 12<=size<=96:raise ValueError('Invalid subtitle size')
 if not re.fullmatch(r'[0-9A-Fa-f]{6}',color):raise ValueError('Use RGB hex color')
 bgr=color[4:6]+color[2:4]+color[0:2]
 header=f'''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{font},{size},&H00{bgr},&H00{bgr},&H00FFFFFF,&H00000000,0,0,0,0,100,100,0.15,0,1,0,0,2,100,100,40,1
Style: Brand,{font},15,&H00808080,&H00808080,&H00FFFFFF,&H00000000,0,0,0,0,100,100,3,0,1,0,0,8,80,80,31,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 if brand:header+=f'Dialogue: 0,0:00:00.00,{timestamp(cues[-1]["end"])},Brand,,0,0,0,,{brand}\n'
 for c in cues:
  text=c['text'].replace('{','').replace('}','').replace('\n',r'\N')
  header+=f'Dialogue: 0,{timestamp(c["start"])},{timestamp(c["end"])},Caption,,0,0,0,,{{\\fad(120,120)}}{text}\n'
 Path(out).write_text(header)

def tts(cues,root,model,length_scale=1.0):
 from piper import PiperVoice,SynthesisConfig
 model=Path(model).resolve();model_hash=hashlib.sha256(model.read_bytes()).hexdigest()
 voice=PiperVoice.load(model);out=root/'audio/voice';out.mkdir(parents=True,exist_ok=True)
 for i,c in enumerate(cues):
  path=out/f'{i+1:02}.wav';meta=path.with_suffix('.json')
  identity={'text':c['text'],'model_sha256':model_hash,'length_scale':length_scale}
  if not path.exists() or not meta.exists() or json.loads(meta.read_text())!=identity:
   with wave.open(str(path),'wb') as f:voice.synthesize_wav(c['text'],f,SynthesisConfig(length_scale=length_scale))
   meta.write_text(json.dumps(identity,indent=2))
  c['file']=str(path.relative_to(root));c['voice']='Piper / '+model.stem
 return cues

def assemble(cues,root,out,duration):
 track=np.zeros(int(duration*SR),np.float64);report=[]
 for c in cues:
  path=root/c['file'];data=pcm(path)
  # Trim edges only: interior sentence pauses are never discarded.
  size=480;n=len(data)//size;energy=np.sqrt((data[:n*size].reshape(n,size)**2).mean(1));active=np.flatnonzero(energy>10**(-46/20))
  if not len(active):raise RuntimeError(f'Empty speech: {path}')
  left=max(0,int(active[0]*size-.04*SR));right=min(len(data),int((active[-1]+1)*size+.10*SR));data=data[left:right]
  available=c['end']-c['start']-.04;tempo=max(1,len(data)/SR/available)
  if tempo>1.12:raise RuntimeError(f'Widen cue {c["index"]}: requires {tempo:.2f}x tempo')
  if tempo>1.001:
   raw=subprocess.check_output(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0','-af',f'atempo={tempo}','-f','f32le','pipe:1'],input=data.astype(np.float32).tobytes());data=np.frombuffer(raw,np.float32)
  # Same active-speech RMS per phrase, then a single integrated normalization.
  signal=data[np.abs(data)>10**(-42/20)];rms=np.sqrt(np.mean(signal**2));data=data*10**(-23/20)/max(rms,1e-9)
  peak=np.max(np.abs(data));data=data*min(1,10**(-3/20)/peak)
  start=round(c['start']*SR);end=start+len(data)
  if end>round(c['end']*SR):raise RuntimeError('Speech extends beyond caption')
  track[start:end]+=data
  meta_path=path.with_suffix('.json')
  if meta_path.exists() and json.loads(meta_path.read_text()).get('text')!=c['text']:raise ValueError('Narration cache text differs from caption')
  report.append({'index':c.get('index',len(report)+1),'text':c['text'],'caption_start':c['start'],'caption_end':c['end'],'audio_start':start/SR,'audio_end':end/SR,'tempo':tempo,'edge_trim_seconds':[left/SR,(len(pcm(path))-right)/SR]})
 out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);temp=out.with_name('voice-assembled.wav');write_pcm(temp,np.column_stack([track,track]))
 run(['ffmpeg','-v','error','-i',str(temp),'-af','loudnorm=I=-18:TP=-2.5:LRA=7','-ar',str(SR),'-c:a','pcm_s24le','-y',str(out)])
 out.with_name('voice-sync.json').write_text(json.dumps(report,indent=2))

def normalize(inp,out,I=-16,TP=-1.5):
 base=f'loudnorm=I={I}:TP={TP}:LRA=7'
 first=subprocess.run(['ffmpeg','-hide_banner','-i',str(inp),'-af',base+':print_format=json','-f','null','-'],stderr=subprocess.PIPE,text=True,check=True)
 stats=json.loads(first.stderr[first.stderr.rfind('{'):])
 filt=base+f':measured_I={stats["input_i"]}:measured_TP={stats["input_tp"]}:measured_LRA={stats["input_lra"]}:measured_thresh={stats["input_thresh"]}:offset={stats["target_offset"]}:linear=true'
 run(['ffmpeg','-v','error','-i',str(inp),'-af',filt,'-ar',str(SR),'-c:a','pcm_s24le','-y',str(out)])
 return stats

def mix(voice,bgm,sfx,outdir):
 out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
 run(['ffmpeg','-v','error','-i',str(bgm),'-af','loudnorm=I=-30:TP=-9:LRA=7','-ar',str(SR),'-c:a','pcm_s24le','-y',str(out/'bgm-levelled.wav')])
 run(['ffmpeg','-v','error','-i',str(out/'bgm-levelled.wav'),'-i',str(voice),'-filter_complex','[0:a][1:a]sidechaincompress=threshold=0.035:ratio=4:attack=20:release=500:knee=3:detection=rms[duck]','-map','[duck]','-ar',str(SR),'-c:a','pcm_s24le','-y',str(out/'bgm-ducked.wav')])
 duration=float(probe(voice)['format']['duration'])
 run(['ffmpeg','-v','error','-i',str(voice),'-i',str(out/'bgm-ducked.wav'),'-i',str(sfx),'-filter_complex',f'[0:a][1:a][2:a]amix=inputs=3:duration=first,volume=3,afade=t=in:st=0:d=0.08,afade=t=out:st={max(0,duration-.35)}:d=0.35[mix]','-map','[mix]','-ar',str(SR),'-c:a','pcm_s24le','-y',str(out/'premix.wav')])
 stats=normalize(out/'premix.wav',out/'mix.wav');(out/'mix-loudness-pass1.json').write_text(json.dumps(stats,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 s=sub.add_parser('subtitles');s.add_argument('cues');s.add_argument('output');s.add_argument('--size',type=int,default=40);s.add_argument('--brand',default='')
 s=sub.add_parser('voice');s.add_argument('cues');s.add_argument('root');s.add_argument('output');s.add_argument('--duration',type=float,default=58)
 s=sub.add_parser('tts');s.add_argument('cues');s.add_argument('root');s.add_argument('--model',required=True);s.add_argument('--length-scale',type=float,default=1.0)
 s=sub.add_parser('mix');s.add_argument('voice');s.add_argument('bgm');s.add_argument('sfx');s.add_argument('outdir')
 a=p.parse_args()
 if a.command=='subtitles':subtitles(json.loads(Path(a.cues).read_text()),a.output,a.size,brand=a.brand)
 elif a.command=='voice':assemble(json.loads(Path(a.cues).read_text()),Path(a.root),a.output,a.duration)
 elif a.command=='tts':
  cues=tts(json.loads(Path(a.cues).read_text()),Path(a.root),a.model,a.length_scale);Path(a.cues).write_text(json.dumps(cues,indent=2))
 elif a.command=='mix':mix(a.voice,a.bgm,a.sfx,a.outdir)
