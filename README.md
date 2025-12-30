# CyberFeng (赛博枫枫子) 🤖

> 一个基于大模型的端云协同多模态语音交互系统。
> 
> *“你是一个AI助手，名字叫CyberFeng。你的说话风格要酷一点，简短有力。”*

## 📖 项目介绍

CyberFeng 是一个集成了语音识别 (ASR)、大语言模型 (LLM) 和语音合成 (TTS) 的全栈语音助手项目。它能够“听懂”用户的语音指令，通过云端大模型进行思考与角色扮演，并使用定制化的音色（GPT-SoVITS）进行语音回复。

本项目旨在探索 AIoT（人工智能物联网）的端云协同模式，未来计划接入 ESP32 嵌入式硬件，实现软硬结合的实体语音助手。

## 📂 项目结构

```text
CyberFeng/
├── audio/                  # 音频文件存储
│   ├── raw/                # 原始录音文件 (输入)
│   ├── converted/          # 格式转换后的音频 (用于API调用)
│   └── trans/              # TTS 生成的回复音频 (输出)
├── json/
│   └── stt_output/         # 语音识别结果的 JSON 缓存
├── lib/                    # 核心功能模块库
│   ├── stt.py              # 语音识别模块 (DashScope)
│   ├── llm.py              # 大模型对话模块 (Google Gemini)
│   └── tts.py              # 语音合成客户端 (GPT-SoVITS)
├── src/                    # (预留) 网络通信与扩展模块
├── main.py                 # 项目主入口
├── requirements.txt        # Python 依赖清单
├── .env                    # 环境变量配置文件 (需自行创建)
└── README.md               # 项目说明文档
```

## 🛠 技术栈

本项目融合了多家前沿 AI 技术与工程化实践：

*   **编程语言**: Python 3.10+
*   **语音识别 (ASR)**: [阿里云 DashScope](https://help.aliyun.com/zh/dashscope/) (通义听悟 / Paraformer)
    *   利用 FFmpeg 进行音频格式预处理。
*   **大语言模型 (LLM)**: [Google Gemini](https://ai.google.dev/) (gemini-2.5-flash)
    *   通过 Prompt Engineering 定制赛博朋克角色人设。
*   **语音合成 (TTS)**: [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
    *   私有化部署的高质量 TTS 服务。
    *   封装了 RESTful API 客户端，支持流式传输与模型切换。
*   **硬件 (开发中)**: ESP32 (计划用于音频采集与播放)。

## 🧩 实现过程与原理

系统采用了经典的 **"听-想-说"** 三段式架构，各模块解耦设计：

1.  **听 (STT - lib/stt.py)**
    *   接收原始音频文件（如 `.m4a`）。
    *   调用 `ffmpeg` 将其转换为 API 兼容的格式（如 `.wav` 或 `.mp3`）。
    *   发送至阿里云 DashScope 接口，解析返回的 JSON 数据提取文本。

2.  **想 (LLM - lib/llm.py)**
    *   接收 STT 转换后的文本。
    *   加载系统提示词 (System Prompt)：设定 AI 为“CyberFeng”，性格热情且酷。
    *   调用 Google Gemini API 生成回复文本。

3.  **说 (TTS - lib/tts.py)**
    *   接收 LLM 生成的回复文本。
    *   通过封装好的 `Infer` 类，向本地或远程运行的 GPT-SoVITS 服务发送 POST 请求。
    *   支持动态切换参考音频 (`ref_audio_path`) 以复刻特定音色。
    *   获取返回的音频流并保存到本地 `audio/trans/` 目录。

## 🚀 如何使用

### 1. 克隆项目
```bash
git clone https://github.com/Yao0454/CyberFeng.git
cd CyberFeng
```

### 2. 安装依赖
建议使用虚拟环境 (venv 或 conda)：
```bash
pip install -r requirements.txt
```
*注意：你需要确保系统中已安装 `ffmpeg` 并配置了环境变量。*

### 3. 配置环境变量
在项目根目录创建 `.env` 文件，填入你的 API Key：
```ini
# 阿里云 DashScope API Key (用于语音识别)
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# Google Gemini API Key (用于大模型对话)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxx
```

### 4. 部署 TTS 服务 (GPT-SoVITS)
本项目依赖 GPT-SoVITS 作为后端 TTS 服务。
1.  下载并运行 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)。
2.  启动 API 服务：
    ```bash
    python api_v2.py -a 0.0.0.0 -p 9880 -c GPT_SoVITS/configs/tts_infer.yaml
    ```
3.  确保模型文件已放置在服务端指定目录。

### 5. 运行主程序
修改 `main.py` 中的 `tts_addr` 为你的 TTS 服务器地址，然后运行：
```bash
python main.py
```

## 📄 开源说明

本项目遵循 [MIT License](LICENSE) 开源协议。
你可以自由地使用、修改和分发本项目，但请保留原作者的版权声明。

---
*Created by Yao0454 | 2025*