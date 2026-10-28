# Verification — public local-voice edition

Performed 2026-10-28 using this independent repository; Nor Cards plugin and its existing demo workspace were not changed.

- Built the complete 58-second example from the committed repaired capture, 12 lossless local Piper utterances and JSON configuration. Music and SFX were synthesized again by the shared script. Separate picture, captions, voice, music, SFX and mix outputs are in the ignored `build/` directory.
- Actual final MP4: 1920×1080, 60fps, H.264/yuv420p + AAC/48k/stereo. All 3480 picture frames and audio decoded without error; no near-full-frame black samples detected.
- Full-duration scan of reserved workspace gutters found zero contamination candidates. The 4.8s, 6.15s, 30.8s and 46.1s neighborhoods were extracted at source frame rate. Contact sheets and phone preview were inspected; real editing, drag previews, color change and card states remain intact. ROI detection has explicit scope and is not a mathematical proof about every subject pixel.
- Narration retains every English caption verbatim. All 12 assembled audio clips fit within their caption windows; Piper length scale is1.2, with no additional timing acceleration. See narration-sync.json. Final measured loudness, true peak, BGM attenuation and artifact SHA-256 are recorded in acceptance.json.
- Independent reuse checks used a clearly synthetic three-second color-pattern fixture, not a claimed product demo: two source intervals concatenated, 1280×720/30fps, white captions, no product-specific automation. Both synthesized-music-only and imported-continuous-narration/imported-BGM modes built and passed export/decode/audio checks. Test fixture and generated files stayed outside Git.
- Skill passed the Codex skill-creator frontmatter validator. Python sources compiled, Node modules passed syntax checks. The repository-scoped skill link resolves to the root SKILL.md, so there is no duplicate maintained skill.
- Source capture is inherited from the actual completed Nor Cards production. Ported live-capture helpers were not rerun against the current desktop; they remain environment-specific and must be checked in an isolated Vault before a new take. Wayland capture automation is not claimed.
- No subjective headphone listening was performed in this environment. Audio was verified through actual encoded-stream measurement, caption/clip timing and waveform-driven ducking measurement; naturalness and perceived balance remain a listening-review item.

Reproduce technical checks using the commands in README.md. The public demo contains no Edge-generated narration, model weights, bundled fonts, original desktop-contaminated samples or personal notes.
