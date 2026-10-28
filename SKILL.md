---
name: product-showcase
description: Produce real product demonstration videos from a software, website, open-source project, robotics simulation, or supplied recordings. Plan and capture authentic interactions, then edit, caption, narrate, mix and verify a polished MP4 using the shared scripts.
---

# Product Showcase

Create a finished product demonstration, with the actual exported video as the deliverable. This repository is the single maintained skill source. Resolve script paths relative to this file; store each new work's inputs, configuration and outputs in its own workspace. Never reuse Nor Cards selectors for another product.

## Establish the production

Identify the real product or supplied recordings, key actions, audience, duration and delivery format. Infer routine choices from the request. When unspecified, use a 45–60 second, 1920×1080/60fps landscape demo with restrained English editorial captions. A different work may need different framing, language or pacing; do not force it into the Nor Cards storyboard.

Check environment with `python scripts/capture.py --check`. Use an isolated demo account/workspace/Vault and nonpersonal content. Do not modify product code to create a nicer-looking demo unless requested. Read [the worked example](examples/nor-cards/README.md) for the concrete production and [its rights record](examples/nor-cards/RIGHTS.md) before reusing assets.

Write a short storyboard and timed caption cues before recording. Show an intelligible result for each genuine action. Keep short approach pauses, visible drag/drop results and a settled closing hold. Never substitute DOM mutations or recreated UI for failed product interactions.

## Acquire real footage

- **AI-assisted capture:** `scripts/capture.py` records an explicit Linux X11 region using FFmpeg. `scripts/xinput.py` provides real eased pointer/keyboard input; `scripts/browser.mjs` provides Chromium CDP input with an explicit target URL. Product-specific selectors and setup/restore logic belong in that work's example, not the shared scripts. Use `try/finally` to restore temporary presentation settings and input state.
- **Manual footage:** accept the user's recording and authored narration/music. Inspect its dimensions, frame rate, audio, crop and source rights; pass it to the exact same post-production pipeline.
- **Wayland:** X11 root capture and XTest do not capture/control native Wayland reliably. Use OBS/PipeWire or the desktop portal for capture and import the result. Do not claim Wayland automation is implemented. Windows/macOS capture adapters are not verified; supplied recordings can still enter the FFmpeg pipeline where dependencies are available.

Prefer app-framebuffer or isolated-display capture when available. X11 root capture can leak other-window surfaces into otherwise clean frames. Keep control terminals/DevTools outside the capture. Scan the entire take before investing in finishing; a few clean screenshots are insufficient.

## Default visual language

Center the product, hide unrelated chrome in the demo session only, and leave room for genuine popups and drag paths. Preserve product fonts, colors and motion. Use a fixed, proportional composition; no decorative zooming, fake pointers, noisy transitions or invented features.

Default 1080p captions are local sans-serif, 40px/regular, bottom centered, fixed 40px lower margin, 100px side margins, short lines. Color and font are configurable. Confirm the longest line and a phone-size preview from the final video. Do not bundle system/Apple fonts. Keep camera, subtitles and audio changes separate from product behavior.

## Build shared post-production

Use [project.json](examples/nor-cards/project.json) as a small concrete example, not a new framework. Set clip files and start/end ranges, target duration, crop/composition, captions and audio assets. Caption times are **final edited timeline** seconds. Clip durations must total the declared duration. Default coordinates are not suitable for a new product without inspection.

1. Use `scripts/flash.py scan INPUT REGIONS REPORT` only after choosing genuinely empty regions. Review every candidate and neighboring frames. Legitimate dark themes, native drag previews and popups are not defects. If a few confirmed corrupt samples can be recovered, `repair ... --reviewed` preserves timestamps and fills their slots with adjacent real samples. Long gaps, lost decisive actions or widespread contamination require rerecording, not transition masking. Public source assets must not expose leaked private surfaces.
2. Create `cues.json` with `index`, `start`, `end`, `text`; add `file` for per-cue audio. Use `scripts/media.py tts` with an explicitly licensed local Piper model, or provide manual audio. The cache fingerprints model, text and rate. For local AI narration, follow the example's pinned model download and record its rights. Do not assume a free online TTS endpoint grants redistribution rights.
3. `scripts/media.py voice` assembles per-cue audio, trims only edge silence, preserves sentence pauses, verifies caption windows and records sync. It permits at most 1.12× timing correction; widen the scene/caption window rather than rushing speech. Manual continuous narration uses `audio.narration` as a file path instead of `cues`; review its semantic synchronization yourself.
4. `scripts/showcase.py PROJECT --output BUILD` edits/concatenates real clips, writes ASS captions, exports `video-only.mp4`, prepares independent voice/music/SFX stems, ducks BGM beneath voice and muxes `final.mp4`. Music may be provided or the original synthesized Ambient score reused; SFX times are explicit event data. Keep stems so edits do not require rerecording.
5. Default mix: voice −18 LUFS, BGM −30 LUFS before voice-driven compression; 20ms attack/500ms release, gentle boundary fades, final two-pass target −16 LUFS/−1.5dBTP. Prepare all stems to the same length. Encode H.264/yuv420p + AAC/48k/stereo, faststart. Do not normalize silent tracks as though they contained narration.

## Verify and deliver

Run `scripts/verify.py FINAL QA --duration N` with the expected width/height/fps. Supply `--sync` for per-cue narration, `--regions` for the work-specific flash scan, and `--times` for known suspect moments. This checks the actual muxed video, full decoding, missing audio streams, black frames, loudness/peak, narration windows and optional full-take ROI contamination. It extracts contact sheets, phone preview and full-rate neighborhoods.

Inspect actual encoded frames around every key action and each flagged/suspect moment. ROI detection cannot prove the whole picture is clean; review the subject too. Listen for clipped syllables, mechanical timing, music competition and intrusive SFX. If listening/playback is unavailable, report that limit separately from passed technical checks. A script exiting successfully is not audiovisual acceptance.

Deliver MP4, separated stems, cues, project config, sources needed to rebuild, a short verification record and rights/provenance. Preserve existing projects. Publishing is separate authorization: when requested, inspect the staged files for credentials/private content, unlicensed assets, models, environments and large generated intermediates. Put oversized deliveries in a Release rather than Git history. Do not publish unresolved third-party assets or silently replace the user's chosen rights-sensitive material.
