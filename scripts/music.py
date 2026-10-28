"""Original ambient/minimal electronic score and quiet UI foley.
No recordings, samples, third-party melodies or external music assets.
Generated BGM/SFX are dedicated to CC0 1.0 in audio/LICENSE.txt.
"""
from pathlib import Path
import json,argparse
import numpy as np
from scipy.signal import butter,sosfilt
from scipy.io.wavfile import write
p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--duration',type=float,required=True);p.add_argument('--events');a=p.parse_args()
OUT=Path(a.output);OUT.mkdir(parents=True,exist_ok=True)
SR=48000;DURATION=a.duration;N=int(SR*DURATION);rng=np.random.default_rng(84)
def hz(midi):return 440*2**((midi-69)/12)
def lowpass(x,cutoff):return sosfilt(butter(2,cutoff,fs=SR,output='sos'),x,axis=0)
def wav(name,x):write(str(OUT/name),SR,np.asarray(np.clip(x,-1,1)*32767,np.int16))
def dbscale(x,db):return x*10**(db/20)
# Slow four-chord, extended harmony; no dramatic rises or foreground melody.
music=np.zeros((N,2),np.float64)
chords=[[50,57,60,64,69],[48,55,59,62,67],[53,60,64,67,72],[45,52,55,59,64]]
for k,start in enumerate(np.arange(0,DURATION,7.25)):
 length=min(10.25,DURATION-start);n=int(length*SR);t=np.arange(n)/SR
 attack=np.clip(t/2.8,0,1);release=np.clip((length-t)/3.,0,1);env=np.sin(attack*np.pi/2)**2*np.sin(release*np.pi/2)**2
 for j,note in enumerate(chords[k%4]):
  f=hz(note);phase=rng.uniform(0,2*np.pi);pan=.2+.6*j/4
  for channel,detune in enumerate([-.001,.001]):
   wave=np.sin(2*np.pi*f*(1+detune)*t+phase)+.14*np.sin(2*np.pi*f*2*t+phase*.7)
   music[int(start*SR):int(start*SR)+n,channel]+=wave*env*(.75 if (channel==0)==(pan<.5)else.55)/len(chords[0])
# Restrained bell accents: a sparse, original pitch sequence.
for k,start in enumerate(np.arange(2.0,max(2.0,DURATION-2),3.625)):
 n=int(min(3.,DURATION-start)*SR);t=np.arange(n)/SR;note=chords[(k//2)%4][2+(k%3)]+12
 tone=(np.sin(2*np.pi*hz(note)*t)+.12*np.sin(2*np.pi*hz(note)*2.01*t))*np.exp(-t*2.4)*np.minimum(t/.012,1)*.11
 idx=int(start*SR);music[idx:idx+n,0]+=tone*.7;music[idx:idx+n,1]+=tone*.5
music=lowpass(music,2200)
# Small stereo delay gives a soft ambient bed without a harsh rhythm.
for delay,gain in [(0.37,.16),(.73,.08)]:
 offset=int(delay*SR);music[offset:,1]+=gain*music[:-offset,0];music[offset:,0]+=gain*music[:-offset,1]
fade=np.minimum(np.arange(N)/SR/2.8,1)*np.minimum((N-np.arange(N))/SR/3.0,1)
music*=fade[:,None];music/=max(np.max(np.abs(music)),1e-8)
wav('bgm-original.wav',dbscale(music,-16))
# Foley consists of short, low-volume original tones; no stock sound samples.
sfx=np.zeros((N,2));events=[]
def sound(kind,start):
 dur={'complete':.22,'drop':.18,'color':.085}[kind];t=np.arange(int(dur*SR))/SR
 if kind=='complete':tone=(np.sin(2*np.pi*660*t)+.4*np.sin(2*np.pi*990*t))*np.exp(-t*23)*(1-np.exp(-t*800))
 elif kind=='drop':tone=(np.sin(2*np.pi*(170*t-90*t*t))+.15*rng.normal(size=len(t)))*np.exp(-t*35)*(1-np.exp(-t*500))
 else:tone=np.sin(2*np.pi*820*t)*np.exp(-t*70)*(1-np.exp(-t*1200))
 tone=lowpass(tone,3000);tone=tone/max(np.max(np.abs(tone)),1e-8)*10**(-26/20)
 i=int(start*SR);sfx[i:i+len(tone),:]+=tone[:,None];events.append({'type':kind,'time':start,'peak_dbfs':-26})
for event in json.loads(Path(a.events).read_text()) if a.events else []:
 if not 0<=event['time']<DURATION-.25:raise ValueError('SFX event outside timeline')
 sound(event['type'],event['time'])
wav('sfx.wav',sfx)
(OUT/'sfx-events.json').write_text(json.dumps(events,indent=2))
print('Original CC0 music and SFX generated')
