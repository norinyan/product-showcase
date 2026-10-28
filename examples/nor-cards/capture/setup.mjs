import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {connectDemo,pause} from './interaction.mjs';
export const viewport={x:112,y:74,width:1280,height:850};
export const notePath='Nor Cards Product Demo.md';
export function pointer(){
 const proc=spawn('python3',['../../scripts/xinput.py'],{stdio:['pipe','pipe','inherit']}),queue=[];
 createInterface({input:proc.stdout}).on('line',line=>{const result=JSON.parse(line),item=queue.shift();result.error?item.reject(Error(result.error)):item.resolve(result);});
 return {send:a=>new Promise((resolve,reject)=>{queue.push({resolve,reject});proc.stdin.write(JSON.stringify(a)+'\n');}),close:()=>proc.stdin.end()};
}
export async function setup(ui,mouse){
 if(process.env.XDG_SESSION_TYPE==='wayland'||!process.env.DISPLAY)throw Error('This historical replay requires an X11 session');
 await mkdir('build/capture/raw',{recursive:true});
 const windows=execFileSync('xwininfo',['-root','-tree'],{encoding:'utf8'}).split('\n').filter(line=>line.includes(' - .test-vault - Obsidian '));
 if(windows.length!==1)throw Error('Expected exactly one isolated test-vault X11 window');
 const id=parseInt(windows[0].match(/0x[0-9a-f]+/i)[0],16);
 const info=execFileSync('xwininfo',['-id',String(id)],{encoding:'utf8'});
 const value=label=>Number(info.match(new RegExp(label+':\\s*(-?\\d+)'))[1]);
 const geometry={id,x:value('Absolute upper-left X'),y:value('Absolute upper-left Y'),width:value('Width'),height:value('Height')};
 await ui.eval(`(()=>{if(!window.norDemoGeometry)window.norDemoGeometry=${JSON.stringify(geometry)};})()`);
 await mouse.send({action:'window',id,x:96,y:64,width:1312,height:892});
 await ui.eval(`(()=>{if(!window.norDemoRestore)window.norDemoRestore={path:app.workspace.getActiveFile()?.path,mode:app.workspace.getMostRecentLeaf()?.getViewState()?.state};})()`);
 const base='\n\n\n> [!nor-card|white-standard-demo-ideas]- Nor Card <!-- nor-title:Ideas -->\n> - [ ] Make room for a new idea\n> - [ ] Keep the details close\n\n\n';
 await ui.eval(`(async()=>{const path=${JSON.stringify(notePath)},text=${JSON.stringify(base)};let f=app.vault.getAbstractFileByPath(path);if(f)throw Error('Demo note already exists; refusing overwrite');f=await app.vault.create(path,text);window.norDemoCreatedNote=true;const leaf=app.workspace.getLeaf(false);await leaf.openFile(f);await leaf.setViewState({type:'markdown',state:{file:path,mode:'source',source:false}});leaf.view.editor.setCursor({line:0,ch:0});})()`);
 // Presentation only: hide unrelated application chrome. Card styles stay intact.
 await ui.eval(`(()=>{document.getElementById('nor-demo-stage')?.remove();const s=document.createElement('style');s.id='nor-demo-stage';s.textContent=${JSON.stringify(`
.titlebar,.workspace-ribbon,.workspace-split.mod-left-split,.workspace-split.mod-right-split,.status-bar,.workspace-tab-header-container,.view-header,.inline-title,.metadata-container{display:none!important}
.workspace-split.mod-root{padding:0!important}.workspace-leaf{box-shadow:none!important}

.markdown-source-view.mod-cm6 .cm-sizer{max-width:640px!important;min-width:0!important;margin:0 auto!important}
.markdown-source-view.mod-cm6 .cm-content:not(.nor-card-shell *){padding-top:52px!important;padding-bottom:80px!important}

.workspace-leaf-resize-handle,.view-content>.markdown-reading-view>.markdown-preview-view>.markdown-preview-sizer>.mod-header{display:none!important}
.tooltip{display:none!important}
.markdown-source-view.mod-cm6 .cm-scroller::-webkit-scrollbar{width:0!important;height:0!important}
`)};document.head.appendChild(s);})()`);
 await pause(700);
 await mouse.send({action:'move',x:viewport.x+1120,y:viewport.y+680,duration:.3});
 await ui.screenshot('build/capture/stage.png');
 return base;
}
if(import.meta.url===new URL(process.argv[1],`file://${process.cwd()}/`).href){const ui=await connectDemo(),mouse=pointer();try{await setup(ui,mouse);console.log(await ui.eval('({width:innerWidth,height:innerHeight})'));}finally{ui.close();mouse.close();}}
