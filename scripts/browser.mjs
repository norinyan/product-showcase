import {writeFile} from 'node:fs/promises';


export const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));


/** Real Chromium input. Caller explicitly chooses the target URL and session. */
export async function connectCDP({port=9222,url,title=''}={}) {
  if(!url)throw Error('An explicit target URL is required');
  const targets=await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const matches=targets.filter(t=>t.url===url&&t.title.includes(title));
  if(matches.length!==1)throw Error('Expected exactly one explicit CDP target; refine title or close duplicate sessions');
  const target=matches[0];
  const ws=new WebSocket(target.webSocketDebuggerUrl),pending=new Map(),listeners=new Map();let sequence=0,closed=false;
  await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
  ws.onmessage=event=>{
    const message=JSON.parse(event.data);
    if(message.id){const item=pending.get(message.id);if(!item)return;pending.delete(message.id);message.error?item.reject(Error(JSON.stringify(message.error))):item.resolve(message.result);}
    else for(const listener of listeners.get(message.method)??[])listener(message.params);
  };
  ws.onclose=()=>{closed=true;for(const p of pending.values())p.reject(Error('CDP closed'));pending.clear();};
  const call=(method,params={})=>new Promise((resolve,reject)=>{
    if(closed){reject(Error('CDP closed'));return;}
    const id=++sequence;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));
  });
  const evaluate=async(expression,{byValue=true}={})=>{
    const result=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:byValue});
    if(result.exceptionDetails)throw Error(result.exceptionDetails.exception?.description??JSON.stringify(result.exceptionDetails));
    return byValue?result.result.value:result.result;
  };
  let mouse={x:80,y:80};
  const move=async(x,y,{duration=650,buttons=0,steps=Math.max(12,Math.round(duration/16)),curve=14}={})=>{
    const from={...mouse},dx=x-from.x,dy=y-from.y,length=Math.hypot(dx,dy)||1;
    const started=performance.now();
    for(let i=1;i<=steps;i++){
      const t=i/steps,u=t*t*(3-2*t),bend=Math.sin(Math.PI*t)*curve;
      const position={x:from.x+dx*u-dy/length*bend,y:from.y+dy*u+dx/length*bend};
      await call('Input.dispatchMouseEvent',{type:'mouseMoved',...position,buttons,button:buttons?'left':'none'});
      mouse=position;
      await pause(Math.max(0,started+duration*t-performance.now()));
    }
    mouse={x,y};
  };
  const point=async(selector,{index=0,rx=.5,ry=.5}={})=>{
    const value=await evaluate(`(()=>{const e=[...document.querySelectorAll(${JSON.stringify(selector)})].filter(e=>e.isShown?.()??e.getBoundingClientRect().height>0)[${index}];if(!e)throw Error('Selector missing: '+${JSON.stringify(selector)});const r=e.getBoundingClientRect();return {x:r.left+r.width*${rx},y:r.top+r.height*${ry},left:r.left,top:r.top,width:r.width,height:r.height};})()`);
    return value;
  };
  const click=async(target,{duration=550,pauseBefore=100,count=1,...pointOptions}={})=>{
    const p=typeof target==='string'?await point(target,pointOptions):target;
    await move(p.x,p.y,{duration});await pause(pauseBefore);
    await call('Input.dispatchMouseEvent',{type:'mousePressed',x:p.x,y:p.y,button:'left',buttons:1,clickCount:count});await pause(65);
    await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:p.x,y:p.y,button:'left',buttons:0,clickCount:count});
  };
  const keys={Enter:{key:'Enter',code:'Enter',windowsVirtualKeyCode:13,nativeVirtualKeyCode:13},Escape:{key:'Escape',code:'Escape',windowsVirtualKeyCode:27},Backspace:{key:'Backspace',code:'Backspace',windowsVirtualKeyCode:8},Tab:{key:'Tab',code:'Tab',windowsVirtualKeyCode:9},ArrowDown:{key:'ArrowDown',code:'ArrowDown',windowsVirtualKeyCode:40},ArrowUp:{key:'ArrowUp',code:'ArrowUp',windowsVirtualKeyCode:38},End:{key:'End',code:'End',windowsVirtualKeyCode:35},Home:{key:'Home',code:'Home',windowsVirtualKeyCode:36}};
  const key=async(name,{modifiers=0}={})=>{
    const entry=keys[name]??{key:name,code:`Key${name.toUpperCase()}`,windowsVirtualKeyCode:name.toUpperCase().charCodeAt(0)};
    await call('Input.dispatchKeyEvent',{type:'rawKeyDown',...entry,modifiers});
    await pause(45);await call('Input.dispatchKeyEvent',{type:'keyUp',...entry,modifiers});
  };
  const type=async(text,{interval=60,jitter=15}={})=>{
    for(const char of [...text]){
      if(char==='\n')await key('Enter');else await call('Input.insertText',{text:char});
      // Deterministic cadence keeps repeated takes comparable.
      await pause(interval+(Math.sin(char.codePointAt(0)*1.3)+1)*jitter/2);
    }
  };
  const waitEvent=(name,timeout=2500)=>{
    let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});
    const handler=params=>{cleanup();resolve(params);};
    const timer=setTimeout(()=>{cleanup();reject(Error(`Timeout: ${name}`));},timeout);
    const cleanup=()=>{clearTimeout(timer);listeners.get(name)?.delete(handler);};
    if(!listeners.has(name))listeners.set(name,new Set());listeners.get(name).add(handler);
    return {promise,cancel:cleanup};
  };
  /** Real browser dragstart, followed by CDP native drag routing with its DragData.
   * This does not mutate note text or invoke plugin controllers directly.
   * If native interception is unavailable it throws; callers must not silently
   * substitute a fake document reorder in a recording.
   */
  const drag=async(source,destination,{duration=1500,hover=300,dropPause=240}={})=>{
    const from=typeof source==='string'?await point(source):source;
    const to=typeof destination==='string'?await point(destination):destination;
    await move(from.x,from.y,{duration:500});await pause(hover);
    await call('Input.setInterceptDrags',{enabled:true});
    const intercepted=waitEvent('Input.dragIntercepted',3000);
    // Register the rejection handler immediately while the mouse events run.
    const dragResult=intercepted.promise.then(data=>({data}),error=>({error}));
    try{
      await call('Input.dispatchMouseEvent',{type:'mousePressed',x:from.x,y:from.y,button:'left',buttons:1,clickCount:1});
      await pause(130);
      await move(from.x+12,from.y+7,{duration:180,buttons:1,curve:0,steps:8});
      const result=await dragResult;if(result.error)throw result.error;
      const data=result.data.data;
      await call('Input.dispatchDragEvent',{type:'dragEnter',x:from.x+12,y:from.y+7,data});
      const start={...mouse},started=performance.now(),steps=Math.max(24,Math.round(duration/25));
      for(let i=1;i<=steps;i++){
        const t=i/steps,u=t*t*(3-2*t),x=start.x+(to.x-start.x)*u,y=start.y+(to.y-start.y)*u;
        await call('Input.dispatchDragEvent',{type:'dragOver',x,y,data});
        mouse={x,y};await pause(Math.max(0,started+duration*t-performance.now()));
      }
      await pause(dropPause);await call('Input.dispatchDragEvent',{type:'drop',x:to.x,y:to.y,data});
      await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:to.x,y:to.y,button:'left',buttons:0,clickCount:1});
    }finally{
      intercepted.cancel();await call('Input.setInterceptDrags',{enabled:false});
      await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:mouse.x,y:mouse.y,button:'left',buttons:0,clickCount:1});
    }
  };
  const screenshot=async(path,{clip}={})=>{const result=await call('Page.captureScreenshot',{format:'png',...(clip?{clip}:{})});await writeFile(path,Buffer.from(result.data,'base64'));};
  const close=()=>ws.close();
  return {call,eval:evaluate,point,move,click,key,type,drag,screenshot,close,get mouse(){return {...mouse};},target};
}
