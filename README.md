# Product Showcase

AI 辅助、也支持手动操作的数字作品展示视频工作流。适合软件、网站、开源项目和机器人仿真：真实录屏 → 剪辑 → 字幕 → 本地 AI 配音 → BGM / 音效 → MP4。默认风格极简、自然、克制，按作品调整。不是视频编辑软件，也不生成虚假的产品界面。

[标准案例：Nor Cards](examples/nor-cards/README.md) · [播放成片](examples/nor-cards/nor-cards-showcase.mp4) · [Codex Skill](SKILL.md)

## 安装

Linux 已验证。需要 Python 3.10+、FFmpeg/FFprobe（含 libass、libx264）、本机 DejaVu Sans。自动录制还需 X11；Chromium 自动操作需 Node.js 22+。Wayland 使用 OBS/PipeWire 或桌面录屏导入，尚未实现原生输入自动化；不宣称其他系统的录制兼容性。

```bash
git clone https://github.com/norinyan/product-showcase.git
cd product-showcase
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/capture.py --check
```

Ubuntu/Debian 缺少系统依赖时：`sudo apt install python3-venv ffmpeg fonts-dejavu-core`。X11 原生输入另需 `libx11-6 libxtst6 x11-utils`。

## 作为 Codex Skill 使用

仓库根目录的 `SKILL.md` 是唯一维护源；仓库自带 `.agents/skills/product-showcase` 软链接，在本项目内可发现。需要跨项目调用时，按 [Codex 官方文档](https://developers.openai.com/codex/skills/)安装为符号链接，无需复制：

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)" ~/.agents/skills/product-showcase
```

然后在 Codex 中调用：

> 使用 $product-showcase，为这个网站制作约 50 秒的真实交互展示视频。只用独立测试账户，输出 1080p/60fps MP4、分轨和验收记录。

或直接让 Codex 读取本仓库 `SKILL.md`；已有录屏也可以：

> 使用 Product Showcase，基于这些仿真录屏和文案制作完整展示视频，保留真实画面，配英文字幕和本地 AI 配音。

## 复现示例 / 手动制作

示例自带已修复的真实源视频、字幕时间线和许可已核实的本地语音片段，**无需联网或下载模型即可重建**：

```bash
python scripts/showcase.py examples/nor-cards/project.json --output examples/nor-cards/build
python scripts/verify.py examples/nor-cards/build/final.mp4 examples/nor-cards/build/qa \
  --duration 58 --regions examples/nor-cards/gutters-final.json \
  --sync examples/nor-cards/build/audio/voice-sync.json --times 4.8 6.15 30.8 46.1
```

手动录屏可导入现有文件，或先选择不含控制终端的X11区域：

```bash
python scripts/capture.py --output /path/to/work/raw.mp4 --region 1280x720+100,100 --seconds 58
```

制作新作品：在独立工作目录放置录屏，参考示例的 `project.json` / `cues.json` 修改素材路径、剪辑区间、构图和时间线，再运行相同命令。字幕时间以剪辑后的最终时间线为准；片段总长须等于 `duration`。无 Nor Cards 专属代码依赖。

- `clips`：真实视频的文件、起止秒数；支持多个片段拼接。
- `video`：输出尺寸/fps、可选裁切、内容尺寸和偏移、背景、首尾淡入淡出。
- `captions`：文案文件、字号、字体、RGB文字颜色和可选品牌文字。
- `audio.narration`：`cues` 使用逐句音频，或填写自己录制/授权的连续旁白路径。
- `audio.music`：自己的授权音乐路径，或 `synthesize` 生成本项目原创 Ambient；`sfx_events` 指向音效时间表，或用 `sfx` 导入音轨。

想重新生成 AI 配音：看[示例说明](examples/nor-cards/README.md#重新生成本地-ai-配音)。手动提供的连续旁白不做语义强制对齐，需自行核对节奏。音乐、音效均可省略；提供不同长度的音轨会补静音/裁至片长。所有音轨都缺省时应先添加旁白或音乐，不制作伪装有声的空成片。

输出包括 `video-only.mp4`、ASS字幕、独立 voice/BGM/SFX、最终混音和 `final.mp4`。默认 H.264 + AAC，目标 −16 LUFS / −1.5dBTP，BGM 自动随旁白降低。技术检查通过后仍须查看画面并试听；详见 Skill 验收流程。

代码 MIT；示例媒体与语音来源见 [RIGHTS.md](examples/nor-cards/RIGHTS.md)。模型、虚拟环境、私人原片和大型中间文件不进 Git；较大交付使用 GitHub Release。
