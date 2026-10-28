"""Reserved-region contamination scan and reviewed frame repair; no UI simulation."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np

def probe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))

def scan(video,config,output):
 cfg=json.loads(Path(config).read_text());w,h=cfg.get('scan_size',[256,170]);regions=cfg['regions']
 masks=[]
 for r in regions:
  x1,y1,x2,y2=r['box'];mask=np.zeros((h,w),bool)
  mask[round(y1*h):round(y2*h),round(x1*w):round(x2*w)]=True
  if not mask.any():raise ValueError('Empty ROI')
  masks.append(mask)
 v=next(s for s in probe(video)['streams']if s['codec_type']=='video');num,den=map(int,v['avg_frame_rate'].split('/'));fps=num/den
 proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-vf',f'scale={w}:{h}:flags=area','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
 bad=[];n=0
 while True:
  data=proc.stdout.read(w*h*3)
  if not data:break
  if len(data)!=w*h*3:raise RuntimeError('Partial decoded frame')
  rgb=np.frombuffer(data,np.uint8).reshape(h,w,3);flag=False
  for r,mask in zip(regions,masks):
   count=int(((rgb.min(2)<r['dark_below'])&mask).sum())
   flag|=count>=r['min_pixels'] if 'min_pixels'in r else count/mask.sum()>r['max_fraction']
  if flag:bad.append(n)
  n+=1
 if proc.wait():raise RuntimeError('Decode failed')
 spans=[]
 for f in bad:
  if spans and f==spans[-1][1]+1:spans[-1][1]=f
  else:spans.append([f,f])
 report={'input':str(video),'config':str(config),'fps':fps,'frame_count':n,'bad_frames':bad,'spans':spans,'review_required':True}
 Path(output).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='bad_frames'}))

def repair(video,report,output,max_gap,approved):
 if not approved:raise ValueError('Review all candidates; pass --reviewed only after visual approval')
 r=json.loads(Path(report).read_text());bad=sorted(set(r['bad_frames']));fps=r['fps']
 if not bad:raise ValueError('No repair needed')
 longest=run=1
 for a,b in zip(bad,bad[1:]):
  run=run+1 if b==a+1 else 1;longest=max(longest,run)
 if longest>max_gap:raise ValueError('Gap too long; re-record instead of concealing lost interaction')
 expr='+'.join(f'eq(n,{i})'for i in bad)
 subprocess.run(['ffmpeg','-v','warning','-i',str(video),'-vf',f"select='not({expr})',fps={fps}",'-an','-c:v','libx264','-preset','medium','-crf','14','-pix_fmt','yuv420p','-y',str(output)],check=True)
 manifest={'source':str(video),'frames':bad,'max_gap':longest,'method':'PTS preserved; adjacent real samples fill missing slots; no transition, interpolation or generated UI. Audio intentionally separate.'}
 Path(str(output)+'.repair.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
 q=s.add_parser('scan');q.add_argument('video');q.add_argument('config');q.add_argument('output')
 q=s.add_parser('repair');q.add_argument('video');q.add_argument('report');q.add_argument('output');q.add_argument('--max-gap',type=int,default=6);q.add_argument('--reviewed',action='store_true')
 a=p.parse_args()
 if a.cmd=='scan':scan(a.video,a.config,a.output)
 else:repair(a.video,a.report,a.output,a.max_gap,a.reviewed)
