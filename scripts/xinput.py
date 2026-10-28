"""Real X11 pointer input. No UI is drawn or simulated by this helper."""
import ctypes as C, json, sys, time, math
X=C.CDLL('libX11.so.6');T=C.CDLL('libXtst.so.6')
X.XOpenDisplay.argtypes=[C.c_char_p];X.XOpenDisplay.restype=C.c_void_p
d=X.XOpenDisplay(None)
if not d: raise RuntimeError('Cannot open X display')
X.XDefaultRootWindow.argtypes=[C.c_void_p];X.XDefaultRootWindow.restype=C.c_ulong
X.XFlush.argtypes=[C.c_void_p];X.XSync.argtypes=[C.c_void_p,C.c_int]
X.XMoveResizeWindow.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_int,C.c_uint,C.c_uint]
X.XRaiseWindow.argtypes=[C.c_void_p,C.c_ulong];X.XSetInputFocus.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_ulong]
T.XTestFakeMotionEvent.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_ulong]
T.XTestFakeButtonEvent.argtypes=[C.c_void_p,C.c_uint,C.c_int,C.c_ulong]
X.XQueryPointer.argtypes=[C.c_void_p,C.c_ulong]+[C.c_void_p]*7
T.XTestFakeKeyEvent.argtypes=[C.c_void_p,C.c_uint,C.c_int,C.c_ulong]
X.XStringToKeysym.argtypes=[C.c_char_p];X.XStringToKeysym.restype=C.c_ulong
X.XKeysymToKeycode.argtypes=[C.c_void_p,C.c_ulong];X.XKeysymToKeycode.restype=C.c_uint
root=X.XDefaultRootWindow(d)
def key(name,down):
 code=X.XKeysymToKeycode(d,X.XStringToKeysym(name.encode()))
 if not code:raise ValueError('Unknown key '+name)
 T.XTestFakeKeyEvent(d,code,int(down),0);X.XFlush(d)
def tap(name):key(name,True);time.sleep(.025);key(name,False);time.sleep(.025)

def point():
 r=C.c_ulong();c=C.c_ulong();rx=C.c_int();ry=C.c_int();wx=C.c_int();wy=C.c_int();mask=C.c_uint()
 X.XQueryPointer(d,root,C.byref(r),C.byref(c),C.byref(rx),C.byref(ry),C.byref(wx),C.byref(wy),C.byref(mask))
 return rx.value,ry.value
def move(x,y,duration=.6,curve=10):
 sx,sy=point();dx=x-sx;dy=y-sy;length=max(1,math.hypot(dx,dy));start=time.monotonic();steps=max(2,int(duration*60))
 for i in range(1,steps+1):
  t=i/steps;u=t*t*(3-2*t);bend=math.sin(math.pi*t)*curve
  T.XTestFakeMotionEvent(d,-1,round(sx+dx*u-dy/length*bend),round(sy+dy*u+dx/length*bend),0);X.XFlush(d)
  time.sleep(max(0,start+duration*t-time.monotonic()))
def button(down):T.XTestFakeButtonEvent(d,1,int(down),0);X.XFlush(d)
for raw in sys.stdin:
 try:
  a=json.loads(raw);action=a['action']
  if action=='window':
   w=int(a['id']);X.XMoveResizeWindow(d,w,a['x'],a['y'],a['width'],a['height']);X.XRaiseWindow(d,w);X.XSetInputFocus(d,w,1,0);X.XFlush(d);time.sleep(.3)
  elif action=='move':move(a['x'],a['y'],a.get('duration',.6))
  elif action=='click':
   move(a['x'],a['y'],a.get('duration',.5))
   for _ in range(a.get('count',1)):
    button(True);time.sleep(.06);button(False);time.sleep(.08)
  elif action=='drag':
   move(a['x'],a['y'],.5);time.sleep(.35);button(True);time.sleep(.15);move(a['toX'],a['toY'],a.get('duration',1.5),0);time.sleep(a.get('hold',.45));button(False)
  elif action=='key':
   for modifier in a.get('modifiers',[]):key(modifier,True)
   tap(a['key'])
   for modifier in reversed(a.get('modifiers',[])):key(modifier,False)
  elif action=='type':
   names={' ':'space',',':'comma',"'":'apostrophe','-':'minus','.':'period'}
   for char in a['text']:
    shift=char.isupper()
    if shift:key('Shift_L',True)
    tap(names.get(char,char.lower()))
    if shift:key('Shift_L',False)
    time.sleep(a.get('interval',.045))
  elif action=='point':pass
  else:raise ValueError(action)
  print(json.dumps({'ok':True,'point':point()}),flush=True)
 except Exception as e: print(json.dumps({'error':str(e)}),flush=True)
