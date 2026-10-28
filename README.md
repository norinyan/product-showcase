# Product Showcase

## 项目定位

AI 辅助、也支持手动操作的数字作品展示视频工作流，适用于软件、网站、开源项目和机器人仿真。从真实录屏或已有素材出发，完成剪辑、字幕、AI配音、BGM、音效和最终MP4，默认风格极简、干净、自然、克制。

[标准案例：Nor Cards](examples/nor-cards/README.md) · [示例成片](examples/nor-cards/nor-cards-showcase.mp4) · [Codex Skill](SKILL.md)

## 安装与环境要求

Linux已验证。需要 Python 3.10+、FFmpeg/FFprobe（含libass、libx264）和本机DejaVu Sans。自动录制使用X11，Chromium自动操作需Node.js 22+；X11输入另需 `libx11-6 libxtst6 x11-utils`。Wayland使用OBS/PipeWire或桌面录屏后导入，尚未实现原生输入自动化；其他系统的录制兼容性未经验证。

```bash
git clone https://github.com/norinyan/product-showcase.git
cd product-showcase
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/capture.py --check
```

Ubuntu/Debian基础依赖：`sudo apt install python3-venv ffmpeg fonts-dejavu-core`。

## 怎么调用

根目录 `SKILL.md` 是唯一维护源，仓库内已有发现用软链接。需要跨项目调用时，在仓库根目录执行以下命令，保持同一份文件，无需复制：

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)" ~/.agents/skills/product-showcase
```

也可以直接让Codex读取本仓库的 `SKILL.md`。发现机制见 [Codex官方文档](https://developers.openai.com/codex/skills/)。

从作品开始：

> 使用 $product-showcase，为这个网站制作约50秒的真实交互展示视频。只用独立测试账户，输出1080p/60fps MP4及分轨。

从已有素材开始：

> 使用 $product-showcase，基于这些机器人仿真录屏和文案制作完整展示视频，配英文字幕和本地AI配音。

完整制作默认由主Agent协调录制、视觉、声音三个子Agent，统一时间线，完成内部检查和必要修正后交付。局部修改只分配需要的角色；没有子Agent工具时顺序执行并说明。完整分工、阶段检查和交付标准集中在Skill中，不另设协作手册。

## 手动使用和复现

Nor Cards示例自带真实源视频、字幕时间线和许可已核实的本地语音片段，无需联网或下载模型即可重建后期：

```bash
python scripts/showcase.py examples/nor-cards/project.json --output examples/nor-cards/build
python scripts/verify.py examples/nor-cards/build/final.mp4 examples/nor-cards/build/qa \
  --duration 58 --regions examples/nor-cards/gutters-final.json \
  --sync examples/nor-cards/build/audio/voice-sync.json --times 4.8 6.15 30.8 46.1
```

新作品在独立工作目录放置素材，参考示例 [project.json](examples/nor-cards/project.json) 设置剪辑、构图及音轨，用 [cues.json](examples/nor-cards/cues.json) 设置最终时间线上的字幕和逐句旁白，再运行相同脚本。已有旁白/BGM/音效可直接导入；只有重新生成AI配音才需下载模型，命令见 [示例说明](examples/nor-cards/README.md#重新生成本地-ai-配音)。作品专属操作不进入通用脚本。

若需手动录制，先选择不含控制终端的X11区域，再运行：

```bash
python scripts/capture.py --output /path/to/work/raw.mp4 --region 1280x720+100,100 --seconds 58
```

当前示例已验证后期重建；新增多Agent分工是执行规范，尚未用新作品完成整套实拍验证。技术检查不能替代实际画面检查和试听，现有案例的具体范围见 [验收记录](examples/nor-cards/verification.md)。

## 产物与授权

指定的输出目录保存 `video-only.mp4`、`captions.ass`、`audio/` 中的独立旁白/BGM/音效及混音，以及 `final.mp4`。默认H.264 + AAC、1080p/60fps，混音目标−16 LUFS/−1.5dBTP；构图和格式可按作品调整，分轨便于替换。

代码MIT，示例媒体及模型来源见 [RIGHTS.md](examples/nor-cards/RIGHTS.md)。不打包字体或模型；私人原片、虚拟环境和大体积中间文件不进Git，过大成片使用GitHub Release。发布与推送按用户授权执行。
