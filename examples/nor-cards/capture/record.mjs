import {spawn} from 'node:child_process';
import {writeFile} from 'node:fs/promises';
import {connectDemo,pause} from './interaction.mjs';
import {setup,pointer,viewport,notePath} from './setup.mjs';
const ui=await connectDemo(),mouse=pointer(),events=[];let recorder,main,origin;
const physical=p=>({x:viewport.x+p.x,y:viewport.y+p.y});
const mark=(name,detail={})=>{const item={name,seconds:+((performance.now()-origin)/1000).toFixed(3),...detail};events.push(item);console.log(JSON.stringify(item));};
const at=async seconds=>pause(Math.max(0,origin+seconds*1000-performance.now()));
const click=async(selector,options)=>mouse.send({action:'click',...physical(await ui.point(selector,options)),duration:.65});
const bodyText=()=>ui.eval(`document.querySelector(${JSON.stringify(main+' .cm-content')}).cmTile.view.state.doc.toString()`);
const check=(v,label)=>{if(!v)throw Error(label);};
async function finishRecorder(){if(recorder&&!recorder.killed){recorder.stdin.write('q\n');await new Promise(r=>recorder.once('close',r));}}
try{
 await setup(ui,mouse);
 await ui.eval(`(()=>{const id='nor-cards:insert-nor-card';if(!window.norDemoHotkey)window.norDemoHotkey={id,keys:app.hotkeyManager.getHotkeys(id)};app.hotkeyManager.setHotkeys(id,[{modifiers:['Mod','Shift'],key:'N'}]);app.hotkeyManager.bake();app.workspace.getMostRecentLeaf().view.editor.focus();})()`);
 recorder=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-f','x11grab','-framerate','60','-video_size',`${viewport.width}x${viewport.height}`,'-draw_mouse','1','-i',`${process.env.DISPLAY}+${viewport.x},${viewport.y}`,'-c:v','libx264','-preset','ultrafast','-crf','15','-pix_fmt','yuv420p','-y','build/capture/raw/take-05.mp4'],{stdio:['pipe','ignore','inherit']});
 origin=performance.now();mark('recording');await at(2.2);
 await ui.key('n',{modifiers:10});await pause(350);
 const id=await ui.eval(`(()=>{const e=[...document.querySelectorAll('.nor-card-shell')].find(e=>e.dataset.norId!=='demo-ideas');if(!e)throw Error('Shortcut did not insert a card');return e.dataset.norId;})()`);main=`.nor-card-shell[data-nor-id="${id}"]`;mark('inserted');
 await at(4.2);mark('editing');
 for(const [i,text]of ['Review the roadmap','Sketch the next idea','Share a first draft','Plan tomorrow'].entries()){
  if(i){await ui.key('Enter');await pause(320);}
  await ui.type(text,{interval:66,jitter:12});await pause(180);
 }
 await mouse.send({action:'move',...physical({x:1090,y:705}),duration:.6});mark('typed');
 await at(16.0);await click(`${main} input[type="checkbox"]`);await pause(400);
 check((await bodyText()).endsWith('- [x] Review the roadmap'),'Completion did not persist');mark('completed');
 await at(19.2);
 let from=physical(await ui.point(`${main} .nor-card-drag-handle`,{index:0})),to=physical(await ui.point(`${main} .nor-card-task-line`,{index:2,ry:.82}));
 await mouse.send({action:'drag',...from,toX:to.x,toY:to.y,duration:1.6});await pause(350);
 check((await bodyText()).startsWith('- [ ] Share a first draft\n- [ ] Plan tomorrow\n- [ ] Sketch the next idea'),'Task drag did not reorder');mark('task-sorted');
 await at(24.2);
 const target=await ui.eval(`(()=>{const root=document.querySelector(${JSON.stringify(main)}),outer=root.parentElement.cmTile.view;const r=outer.coordsAtPos(0,1),c=outer.contentDOM.getBoundingClientRect();return {x:c.left+80,y:r.top+9};})()`);
 from=physical(await ui.point('.nor-card-shell[data-nor-id="demo-ideas"] .nor-card-move-handle'));to=physical(target);
 await mouse.send({action:'drag',...from,toX:to.x,toY:to.y,duration:2.1});await pause(450);
 check(await ui.eval(`document.querySelector('.nor-card-shell').dataset.norId==='demo-ideas'`),'Whole card drag did not reorder');mark('card-moved');
 // Park the real pointer in the margin after the native move.
 await mouse.send({action:'move',...physical({x:1090,y:705}),duration:.6});await pause(250);
 await at(30.2);
 for(const color of ['green','black','white']){await click(`${main} [aria-label="切换卡片颜色"]`);await pause(660);check(await ui.eval(`document.querySelector(${JSON.stringify(main)}).dataset.norColor===${JSON.stringify(color)}`),'Color did not cycle');mark('color-'+color);}
 await at(35.5);await click(`${main} .nor-card-date`);await pause(650);mark('calendar-open');
 await click(`${main} .nor-card-calendar [aria-label="2026-10-29"]`);await pause(350);
 check(await ui.eval(`document.querySelector(${JSON.stringify(main+' .nor-card-date')}).textContent==='Thu, Oct 29 · 2026'`),'Date did not save');mark('date-selected');
 await at(40.8);
 const titlePoint=physical(await ui.point(`${main} .nor-card-title`));
 await mouse.send({action:'click',...titlePoint,count:2,duration:.65});await pause(180);
 check(await ui.eval(`document.activeElement===document.querySelector(${JSON.stringify(main+' .nor-card-title')})&&document.getSelection().toString()==='Tasks'`),'Title word is not selected');
 await mouse.send({action:'type',text:'Today, by design',interval:.035});await mouse.send({action:'key',key:'Return'});await pause(350);
 check(await ui.eval(`document.querySelector(${JSON.stringify(main+' .nor-card-title')}).textContent==='Today, by design'`),'Title did not update');mark('title-renamed');
 await at(45.6);await click(`${main} [aria-label="折叠卡片"]`);await pause(800);mark('folded');
 await click(`${main} [aria-label="展开卡片"]`);await pause(650);mark('expanded');
 await at(50.0);await click('.nor-card-shell[data-nor-id="demo-ideas"] [aria-label="展开卡片"]');await pause(400);
 await click('.nor-card-shell[data-nor-id="demo-ideas"] [aria-label="切换卡片颜色"]');await pause(350);
 await mouse.send({action:'move',...physical({x:1080,y:705}),duration:.9});
 await ui.eval('app.workspace.getMostRecentLeaf().view.save()');
 await ui.screenshot('build/capture/final-state.png');
 const markdown=await ui.eval('app.workspace.getMostRecentLeaf().view.editor.getValue()');await writeFile('build/capture/final-note.md',markdown);mark('multi-card');
 await at(58.0);mark('finished');await finishRecorder();await writeFile('build/capture/events.json',JSON.stringify(events,null,2)+'\n');
}catch(error){console.error(error);await finishRecorder();await writeFile('build/capture/events.json',JSON.stringify(events,null,2)+'\n');process.exitCode=1;}
finally{ui.close();mouse.close();}
