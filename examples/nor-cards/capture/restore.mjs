import {writeFile} from 'node:fs/promises';
import {connectDemo} from './interaction.mjs';
import {pointer,notePath} from './setup.mjs';
const ui=await connectDemo(),mouse=pointer();
try{
const result=await ui.eval(`(async()=>{
 const restore=window.norDemoRestore,hotkey=window.norDemoHotkey,geometry=window.norDemoGeometry;
 if(hotkey){if(hotkey.keys)app.hotkeyManager.setHotkeys(hotkey.id,hotkey.keys);else app.hotkeyManager.removeHotkeys(hotkey.id);app.hotkeyManager.bake();}
 document.getElementById('nor-demo-stage')?.remove();
 const leaf=app.workspace.getMostRecentLeaf();
 if(restore?.path){const original=app.vault.getAbstractFileByPath(restore.path);if(original){await leaf.openFile(original);if(restore.mode)await leaf.setViewState({type:'markdown',state:restore.mode});}}
 const demo=app.vault.getAbstractFileByPath(${JSON.stringify(notePath)});if(demo&&window.norDemoCreatedNote)await app.vault.delete(demo);
 delete window.norDemoCreatedNote;delete window.norDemoRestore;delete window.norDemoHotkey;delete window.norDemoGeometry;
 return {vault:app.vault.adapter.basePath,demoNoteRemoved:!app.vault.getAbstractFileByPath(${JSON.stringify(notePath)}),presentationRemoved:!document.getElementById('nor-demo-stage'),originalNoteReopened:app.workspace.getActiveFile()?.path===restore?.path,hotkeyRestored:true,geometry};
})()`);
if(result.geometry)await mouse.send({action:'window',...result.geometry});
await writeFile('build/capture/restore-report.json',JSON.stringify(result,null,2)+'\n');console.log(result);
}finally{ui.close();mouse.close();}
