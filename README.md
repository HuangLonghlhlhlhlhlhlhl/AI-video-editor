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

## 🆕 最新更新日志

### v2.0.0 (Gravity Edit Pro - 工业级界面升级)
- **🎨 专业级 NLE 界面重构**：全面采用达芬奇 (DaVinci Resolve) 与 Premiere Pro 风格的深色工业级 UI (Gravity Pro Design System)。
- **🎛️ SPA 模块化工作流**：引入底部导航栏，无缝切换 Media (素材), Cut (剪辑), Edit (主工作区), Color (调色), Fairlight (音频), Deliver (导出) 模块。
- **✨ 增强型监视器与检查器**：重构 AI 助理面板，将其与专业的属性检查器 (Inspector) 深度集成，实现交互的商业级进化。
- **📊 专业波形与时间轴渲染**：引入全局 Mac 风格滚动条，深度定制 Tailwind CSS 玻璃拟物 (Glassmorphism) 与原生磁性时间轴 (Magnetic Timeline) 视觉表现。

### v1.0.0 (核心 AI 剪辑版本)
- **✨ 剪映级实战化 UI**：引入全套极客风暗黑工作台布局，包含横向时间轴、实时监视器与 AI 助理交互区。
- **📁 原生导入交互**：使用 PyWebView 实现底层调用，支持调用 macOS 原生访达界面选择素材文件夹。
- **🪄 画风智能聚类**：依据 Gemini 提取出的高频“语义特征”，自动为散乱的原片素材进行归类与建库。
- **🎬 时间轴互动预览**：AI 生成剪辑轨道后，点击时间轴上的区块，监视器会自动挂载原素材，并在截取的时间段内无缝精准播放。
- **🚀 后台渲染引擎**：开发独立后台 Export Engine。一键“导出”，自动调用本地 FFmpeg 核心将非结构化异构切片统一缩放为 1080P 宽屏并合并输出成片！
