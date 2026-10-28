# Real interaction automation

This is the original product-specific interaction research, retained with the case. The wrapper delegates generic input to `scripts/browser.mjs`; live replay entrypoints are under `capture/`.

`interaction.mjs` exports `connectDemo()` and `pause(ms)`. The connection checks both `.test-vault` target title and exact Vault base path before allowing CDP input. It never edits plugin source or notes on its own.

```js
import {connectDemo,pause} from './interaction.mjs';
const ui=await connectDemo();
await ui.click('.nor-card-title');
await ui.key('a',{modifiers:2}); // Linux Ctrl+A, with title focused
await ui.type('Today');
await ui.key('Enter');
ui.close();
```

`point(selector,{index,rx,ry})` returns viewport coordinates and a DOM rectangle. `move(x,y,{duration})` uses a smooth, small curved trajectory; `click()` moves before pressing/releasing; `type()` sends real Chromium text input per character; `key()` sends keyboard events; `drag()` starts native HTML drag with real mouse events then routes Chromium's intercepted native `DragData` using CDP. It never substitutes document updates for a failed native drag. Native drag must be tested by the recording owner in a disposable demo note before a take.

## Selectors

Scope to the real card using `.nor-card-shell[data-nor-id="ID"]`; don't include offscreen drag ghosts.

| Action | Selector / target |
| --- | --- |
| Body editing | `.nor-card-body .cm-content` |
| Task row | `.nor-card-task-line` |
| Complete | `.nor-card-editor-checkbox` (choose by task row) |
| Task drag | `.nor-card-task-line .nor-card-drag-handle` |
| Whole card drag | `.nor-card-header .nor-card-move-handle` |
| Color | `[aria-label="切换卡片颜色"]` |
| Date | `.nor-card-date` |
| Calendar day | `.nor-card-calendar [aria-label="2026-10-29"]` |
| Title | `.nor-card-title` |
| Fold | `[aria-label="折叠卡片"]` |
| Expand | `[aria-label="展开卡片"]` |

Task drag needs at least two nonempty tasks in the same completion group and contiguous list. Complete one of four tasks, then reorder two of the three remaining tasks. Hover the source task row before dragging to fade its handle in. Use the destination row's original rectangle and `ry:.8` to move after it. During dragging the implementation reads stored original row positions; don't chase the shifting preview.

Whole-card drag only drops at top-level Markdown blank lines outside cards/fences/YAML. Query the outer editor via `root.parentElement.cmTile.view`, and use `outer.coordsAtPos(blankOffset,1)` for destination y; x must remain inside `outer.contentDOM` bounds. Take the destination before starting drag. Keep enough empty lines after the two demo cards to provide a visible drop slot.

For insertion, Obsidian's existing `nor-cards:insert-nor-card` command is genuine plugin functionality. Prefer the command palette (`Ctrl+P`, type `Insert Nor Card`, `Enter`) or temporarily bind the command in the isolated test configuration; don't construct a fake card DOM. After insertion the body automatically receives focus. Type tasks with real text input and `Enter`; don't press Enter after the final intended task unless that blank row is part of the shot.

Date click opens the real calendar; selecting `2026-10-29` updates the card date without modifying tasks. The calendar is inserted under the header and increases card height. Close it before other actions.

Title editing is real `contentEditable`: click, `Ctrl+A`, type, Enter. Avoid Ctrl+A while the body has focus (it selects the body). Folding uses the actual header button and instantly hides the body.

## Recording notes

- `xdotool` is not installed here; FFmpeg is available. CDP input does not move the X11 system pointer. This production used XTest tooling for the genuine desktop pointer; no synthetic cursor overlay was added. Do not stage fake card movement or task UI.
- The module exposes `call(method,params)` for CDP screencast or screenshots and `eval()` for bounded setup/readback. Recording setup belongs to the owner; only a dedicated demo note in `.test-vault` may be created, never overwrite the preview note or user notes.
- All drags should be verified against the saved demo note and visible state. A successful `dispatchDragEvent` response is not proof that the task/card moved.
