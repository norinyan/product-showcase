import {fileURLToPath} from 'node:url';
import {connectCDP,pause} from '../../../scripts/browser.mjs';
export {pause};
const expectedVault=fileURLToPath(new URL('../.test-vault',import.meta.url));
export async function connectDemo({port=Number(process.env.NOR_DEMO_CDP_PORT||9333)}={}) {
 const ui=await connectCDP({port,url:'app://obsidian.md/index.html',title:'.test-vault'});
 if(await ui.eval('app.vault.adapter.basePath')!==expectedVault){ui.close();throw Error('Wrong vault; refusing interaction');}
 return ui;
}
