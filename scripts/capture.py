"""Real X11 region recording; Wayland users supply a portal/OBS recording."""
import argparse,json,os,platform,shutil,subprocess
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--output');p.add_argument('--region',default='1280x850+0,0',help='WIDTHxHEIGHT+X,Y');p.add_argument('--fps',type=int,default=60);p.add_argument('--seconds',type=float);a=p.parse_args()
session=os.environ.get('XDG_SESSION_TYPE','unknown');display=os.environ.get('DISPLAY')
state={'os':platform.system(),'session':session,'display':display,'ffmpeg':bool(shutil.which('ffmpeg')),'ffprobe':bool(shutil.which('ffprobe')),'x11_automation':session!='wayland'and bool(display)and platform.system()=='Linux'}
if a.check:print(json.dumps(state,indent=2));raise SystemExit()
if not state['x11_automation']:raise SystemExit('X11 capture unavailable. On Wayland, record with OBS/PipeWire or the desktop portal; import that video into the same post-production pipeline.')
if not a.output:p.error('--output is required')
import re
from pathlib import Path
m=re.fullmatch(r'(\d+)x(\d+)\+(\d+),(\d+)',a.region)
if not m:p.error('Use WIDTHxHEIGHT+X,Y')
w,h,x,y=map(int,m.groups())
if min(w,h)<=0 or w%2 or h%2:p.error('Capture dimensions must be positive and even')
Path(a.output).parent.mkdir(parents=True,exist_ok=True)
cmd=['ffmpeg','-hide_banner','-loglevel','warning','-f','x11grab','-framerate',str(a.fps),'-video_size',f'{w}x{h}','-draw_mouse','1','-i',f'{display}+{x},{y}']
if a.seconds:cmd+=['-t',str(a.seconds)]
cmd+=['-an','-c:v','libx264','-preset','ultrafast','-crf','15','-pix_fmt','yuv420p','-n',a.output]
print('Recording real desktop region. Keep other windows away; press q in this control terminal to stop. Root-window capture requires full-frame contamination review.')
try:subprocess.run(cmd,check=True)
except KeyboardInterrupt:pass
