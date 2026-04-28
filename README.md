# AI Video Editor Assistant (AI 编导助手)

这是一个智能化的极客视频剪辑工作站。基于 Python FastAPI 和 Gemini 1.5/2.5 多模态大模型，帮你实现从**素材扫盘检索**到**自然语言自动剪辑成片**的全流程式工作。

## 🌟 核心亮点

- **智能素材扫盘**：无需手动打标签！利用 Gemini 的多模态能力，自动对文件夹内的所有 `.mp4/.mov` 视频提取语义标签、高光时刻和画面描述，并落库至 SQLite。
- **视觉相似度分类**：系统能根据画面的特征词，自动对散乱的素材进行聚类（如“阳光”、“运动”、“微笑”）。
- **自然语言对话式剪辑 (Smart Edit Pro)**：不用再辛苦拖拽轨道，只需要在对话框输入 _“帮我剪一个赛博朋克风的高光，节奏快一点”_。AI 就会从你的素材库里精准挑选片段，并生成带时间戳、带转场建议的编辑轨道！
- **原生应用体验与即时预览**：封装了 PyWebView，具备类似 Mac 原生 App 的体验；并内嵌仿“剪映 / Premiere”的监视器和多轨道时间线，点击轨道即可实时预览素材截断片段！
- **一键 FFmpeg 无损混剪**：后端通过 Python 直接调用 FFmpeg 引擎，点击导出即可将时间线上 AI 挑出的所有异构碎片视频（智能缩放至 1080P/30fps）拼接成最终成片！

## 🚀 如何运行

### 环境准备

你需要安装 Python 3.9+，并在系统中通过 Homebrew 安装 FFmpeg：
```bash
brew install ffmpeg
```

### 一键启动 (Mac 推荐)
直接在访达中双击 `Launch_AI_Editor.command` 文件，系统将自动配置环境并拉起全屏桌面应用程序。

### 手动启动
```bash
# 1. 建立虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置密钥
cp .env.example .env
# 在 .env 中填入你的 GEMINI_API_KEY

# 4. 启动服务端与 GUI
python app_window.py
```

## 🛠️ 技术栈
- **后端**：FastAPI, SQLite, Python `subprocess` (FFmpeg)
- **大模型**：`google-generativeai` (Gemini 1.5/2.5 Pro & Flash)
- **前端**：Vanilla JS, HTML5, CSS3 (Glassmorphism, Dark Mode)
- **原生封装**：PyWebView
