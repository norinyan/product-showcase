# Nor Cards — product demonstration storyboard

Target: **58 seconds**, 16:9 MP4, genuine interactions inside the isolated Obsidian test Vault. Clean, calm, precise. The application, all text changes, animation, dragging, calendar and buttons are recorded live. Do not render substitute UI or manufacture feature transitions.

## Frame and content

- Prefer 1920 × 1080 output at 30 fps, or capture at the display's native resolution and use a centered, constant crop. Record the actual pointer. Do not stretch a small application screenshot to fill a large frame.
- Hide Obsidian sidebars, file tabs, ribbon, status bar and other unrelated chrome **in the demo session only**. Keep one Markdown note open in Live Preview. Never expose DevTools, the terminal, filesystem paths, debug bars or the user's existing notes.
- Center the note column. Preserve the real card's 640 px maximum width, font system, colors, border and shadow. Application-wide zoom at 125–140% is acceptable when needed for a legible recording; never enlarge only an individual control or distort the layout.
- Use a pale, neutral Obsidian workspace so the native warm-white, green and black cards have clear contrast. Keep a comfortable margin around the card and allow the real calendar to open fully on screen.
- Main card starts as the real blank inserted card with default `Tasks` title. Type the following four tasks with genuine keyboard input:
  1. `Review the roadmap`
  2. `Sketch the next idea`
  3. `Share a first draft`
  4. `Plan tomorrow`
- A second small real card may be prepared before recording, below the opening viewport. Its title is `Ideas`; its two tasks are `Keep it simple` and `Make room to think`. It is a staging asset in the dedicated demo note, not an invented feature. Do not alter the user's preview note.
- If both cards plus the calendar cannot fit, use a short, real smooth scroll to recenter the active card. Keep all subsequent operations in a comfortable middle area; do not click against the screen edge.

## Timeline

| Time | Real picture and action | Rhythm / framing | Editorial footer |
|---|---|---|---|
| 00:00–00:02 | Clean Obsidian note area, pointer parked away from the action. | 1.5 s hold gives the viewer room to orient. No animated logo. | `Nor Cards` / `A quieter way to work.` |
| 00:02–00:06 | Open the real command palette with the keyboard; type/select `Insert Nor Card`; the blank `Tasks` card appears with the real current date. | Palette visible briefly, then a clean 0.8 s reveal hold. Native command UI is allowed; terminal/debug interfaces are not. | `A card, right inside your note.` |
| 00:06–00:16 | Type four concise tasks, pressing Enter between them. For a natural editing beat, change `Share a draft` into `Share a first draft` using actual cursor/keyboard input. | Approximately 7–9 characters/s with a 200–350 ms pause at each Enter. Do not type all content instantly. Keep the shell visually stable. | `Write naturally. Press Enter to keep going.` |
| 00:16–00:20 | Move to the first checkbox and complete `Review the roadmap`. | Pause 0.5 s over target, click, allow native 200 ms move animation, then hold final completed position for ≥1 s. | `Finish a task. Keep your focus.` |
| 00:20–00:25 | Hover the right side of `Plan tomorrow` to reveal its real task handle. Drag it above the other unchecked tasks and release. | Approach in 0.5 s, hover 0.45 s, drag in 1.1–1.5 s, hold result ≥1.2 s. Never cross the completed group. | `Put the next step first.` |
| 00:25–00:31 | Reveal the real header handle and drag a whole card to another valid block gap in the same note. Show the actual insertion indicator and saved reordered layout. | A single intentional movement, 1.4–1.8 s drag. Allow surrounding content to settle. Recenter the active main card with a gentle real scroll if required. | `Move the whole card with your thoughts.` |
| 00:31–00:36 | Click the existing palette control: warm white → green → black → warm white. | Three real clicks, each followed by ~0.9 s on the selected color. Keep pointer movements small and avoid lingering over a tooltip. | `Three colors. Nothing extra.` |
| 00:36–00:42 | Click the date, show the real month grid, select **October 29, 2026**. | Hold calendar fully visible for ≥1 s before selecting. Confirm the actual title line changes to `Thu, Oct 29 · 2026`. Do not imply that tasks are filtered by date. | `Choose a date for this card.` |
| 00:42–00:47 | Click `Tasks`, select its current title with the native keyboard, type `Today's focus`, and press Enter or blur. | ~1.5 s typing, then ≥1 s saved-title hold. No form or extra save button. | `Give it a name of your own.` |
| 00:47–00:51 | Click the existing chevron to fold the main card, hold ~0.8 s, click to expand. | Keep the true folded state visible; no crossfade that hides the action. | `A little less when you need it.` |
| 00:51–00:58 | Settle on the real multi-card note, main card and `Ideas` card both clearly visible. Pointer glides into the margin and stops. | One small real scroll if necessary, then ≥3 s uninterrupted final hold. End with a 0.4 s dissolve to the same neutral color, or simply stop on the finished frame. | `Nor Cards` / `Your note. Your pace.` |

The order above is intentional: insertion → natural editing → completion → task drag → whole-card drag → colors → date → title → fold → multi-card ending. Do not omit an interaction just to fit a shorter edit. If actual typing takes longer, trim idle holds, keep the clip between 45 and 60 seconds, and never accelerate the completion/drag animations until they become unreadable.

## Pointer and editing language

- One continuous real interaction take is preferred. A few clean cuts between quiet settled frames are acceptable if they do not fabricate a result or conceal a failed interaction.
- Use eased pointer approaches over 350–650 ms. A tiny pause before each click is enough; no arbitrary mouse wandering or robotic instantaneous teleporting.
- Keep the pointer away from labels during reading holds. No fake rings, glow, giant cursor or animated arrows.
- Drags must originate from the actual task/header handle and travel through real coordinates, with a short pause after native drag begins and before release.
- Editing should look like a person working: brief pauses at words/lines, deliberate selections, no terminal-like streams of text and no menu hopping.
- Silence is acceptable and preferable to unlicensed audio or distracting stock music. No spoken claims about offline sync or untested platforms.

## Overlay and finishing

- Captions are editorial labels outside the application's interaction area, not fake controls. They should be optional, restrained, and never cover a checkbox, title, calendar or drag destination.
- Use local installed modern sans-serif fonts (e.g. Noto Sans / DejaVu Sans), 28–32 px at 1080p, weight 400, near-black on the pale background. Final product name can be 32–36 px / 600. Do not download or package Apple fonts.
- Keep captions to one short line; the opener and ending may use a small secondary line. Prefer a static lower margin at ~88–92% frame height, with 0.15–0.2 s opacity fades. Avoid pill boxes, gradients, animated titles or dramatic scene transitions.
- A constant crop is preferable to repeated zooming. At most one restrained editorial recenter/crop change at a clean cut, if needed to retain readability. Never crop the calendar or drag path.
- Use direct cuts or a 0.2 s dissolve between settled shots. Preserve real task/whole-card movement timing. Do not recreate the motions in post-production.
- FFmpeg export: H.264 `libx264`, `-preset slow -crf 17` (18–19 also acceptable for smaller delivery), `-pix_fmt yuv420p -movflags +faststart`, 30 fps constant frame rate. Do not add audio merely to satisfy a container convention.
- Keep all captures, cue logs, temporary assets, edit scripts and output under `demo/`. Suggested final filename: `demo/nor-cards-demo.mp4`.

## Actual acceptance inspection

1. Probe the exported MP4: 45–60 s, expected dimensions/frame rate, H.264/yuv420p, readable by a standard player.
2. Inspect contact-sheet frames spanning every scene, plus the frame before and after each drag/checkbox operation. Inspect the actual motion at completion, task drag and whole-card drag, not only still screenshots.
3. Confirm no blank/black unintended frames, source-code views, tool windows, tooltip leftovers, clipped calendar, stale drag indicator, duplicated task, editing conflict message or visibly wrong checkbox state.
4. Confirm all ten requested features appear in order with authentic results. Record any interaction that could not be captured truthfully; do not hide it with generated UI or claim script execution alone is video acceptance.
5. Final verification should include a clean final hold where both cards are readable and the pointer has stopped moving.
