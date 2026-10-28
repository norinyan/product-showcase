# Nor Cards — 标准制作案例

作品仓库：**https://github.com/norinyan/nor-cards**

[最终公开版 MP4](nor-cards-showcase.mp4) · [分镜概览](contact-sheet.jpg) · [实际时间线](storyboard.md) · [素材授权](RIGHTS.md)

58 秒、1920×1080/60fps，真实 Obsidian 1.14.5 / Nor Cards 2.5.0 交互。依次展示插入卡片、自然编辑、完成动画、任务排序、整卡移动、三色切换、日期选择、标题修改、折叠展开和多卡片。字幕40px；新版公开配音为本地 Piper LJSpeech，原英文文案、视觉风格和节奏不变。

## 重建整个后期流程

在仓库根目录完成依赖安装后：

```bash
python scripts/showcase.py examples/nor-cards/project.json --output examples/nor-cards/build
python scripts/verify.py examples/nor-cards/build/final.mp4 examples/nor-cards/build/qa \
  --duration 58 --regions examples/nor-cards/gutters-final.json \
  --sync examples/nor-cards/build/audio/voice-sync.json --times 4.8 6.15 30.8 46.1
```

`assets/source.mp4` 是本次真实录制经确认的66帧污染修复后的源视频；`repair.json` 保留逐帧清单。缺失样本由相邻真实帧填回原时间槽，无变速、光流、生成UI或掩盖转场。原始 X11 污染片含工作桌面碎片，不公开；原始工程和 Edge 配音版本仍完整保留于本机原项目，未被改写。

`assets/voice/*.flac` 是公开版本地TTS原始句子，按 `cues.json` 重新组装、裁边缘静音和同步；`scripts/music.py` 按实际 `sfx-events.json` 重新合成原创 Ambient 和音效。源录屏、配音片段、时间线和配置均已提交，所有较大的中间轨在忽略的 `build/` 中重新生成，模型不随仓库分发。成片约数MB，直接提交，无需Release。

## 重新生成本地 AI 配音

离线重建不需模型；只有重新合成声音需要先下载已核实许可的模型。固定版本和SHA-256见 `voice-model.json`：

```bash
python scripts/download_voice.py examples/nor-cards/voice-model.json --output .models
mkdir -p examples/nor-cards/build/retake
cp examples/nor-cards/cues.json examples/nor-cards/build/retake/cues.json
python scripts/media.py tts examples/nor-cards/build/retake/cues.json \
  examples/nor-cards/build/retake --model .models/en_US-ljspeech-high.onnx --length-scale 1.2
python scripts/media.py voice examples/nor-cards/build/retake/cues.json \
  examples/nor-cards/build/retake examples/nor-cards/build/retake/voice.wav --duration 58
```

将 `audio.narration` 指向新的完整 `voice.wav`，即可重用画面和其他音轨。若新句子超出字幕窗口，脚本报错；先调整镜头/字幕长度，不用大幅加速填塞。

## 重新拍摄：作品专属部分

`capture/` 保留实际制作使用的 Obsidian 操作脚本；通用 CDP 与 X11 输入位于根目录 `scripts/`。这是本案例的历史自动化，**不冒充任意作品通用操作**。当前后期重建已实际验证；移植后的录制脚本仅做语法/边界检查，未重新操作用户当前桌面。

重拍需要：Linux **X11**、Node22+、xwininfo、libX11/libXtst；自行打开位于 `examples/nor-cards/.test-vault` 的独立 Obsidian Vault，安装对应 Nor Cards 版本、启用插件，并启用本地 CDP9333。脚本检查窗口标题与Vault绝对路径，不连接正式知识库。窗口几何与实际月历操作需按新拍摄日期/屏幕检查；本次历史日期为2026-10-29，不保证换机器后无需调整。

在 `examples/nor-cards/` 执行：

```bash
set -e
trap 'node capture/restore.mjs' EXIT
node capture/record.mjs
```

新拍素材只写入忽略的 `build/capture/`，不会替换已验收源素材。即使失败也运行恢复逻辑；保留窗口/笔记/快捷键恢复报告。不要在重拍时同时操作目标窗口。Wayland请手动录制后导入共享流程，不使用此X11自动化。

## 验收记录

见 [verification.md](verification.md)。机器检查、实际抽帧视觉检查和主观试听分别记录，不相互冒充。
