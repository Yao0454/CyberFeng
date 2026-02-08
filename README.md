
# CyberFeng (赛博枫枫子) 🤖

## 🧱 Python 类功能接口（推荐用法）

本项目的核心能力封装在 `lib/` 下，均提供「加载模型 / 卸载模型」的生命周期接口，避免每次调用都重复加载导致慢、占显存。

> 说明：本文档已更新为 **本地推理版本**：
> - **LLM**：vLLM 本地加载 Qwen2.5 Instruct（支持手动加载/卸载）
> - **STT**：FunASR 本地 Paraformer（支持手动加载/卸载）
> - 模型缓存目录：`models/`（LLM `download_dir` 使用该目录；STT 当前也会在项目下使用该目录）

---

### 1) `lib/llm.py`：`LLM`（vLLM，本地大模型）

#### 初始化
- `LLM(_modelpath, _temperature=0.7, _top_p=0.8, _max_tokens=512, _gpu_memory_utilization=0.3)`

常用参数：
- `_modelpath`：模型路径或 Hugging Face 模型ID（例如 `Qwen/Qwen2.5-1.5B-Instruct`）
- `_gpu_memory_utilization`：vLLM 显存利用率（越大可用 KV Cache 越多，但会占用更多显存）

#### 生命周期接口
- `load_model() -> None`
  - 作用：加载模型到显存并初始化 tokenizer / sampling params
- `unload_model() -> None`
  - 作用：卸载模型并清理显存（`torch.cuda.empty_cache()`）
- `get_model_status -> bool`（属性）
  - 作用：查看模型是否已加载

#### 推理接口
- `get_response(text: str, filename: str) -> Optional[str]`
  - 返回：模型回复文本
  - 副作用：把结构化输出保存到 `json/llm_output/{filename}.json`

#### 参数调整
- `set_sampling_params(_temperature, _top_p, _max_tokens) -> None`
- `set_gpu_memory_utilization(gpu_memory_utilization: float) -> None`
  - 如果模型已加载：会先卸载再按新显存参数重载

#### 使用示例
```python
from lib.llm import LLM

llm = LLM(
    _modelpath="Qwen/Qwen2.5-1.5B-Instruct",
    _temperature=0.7,
    _top_p=0.8,
    _max_tokens=256,
    _gpu_memory_utilization=0.3,
)

llm.load_model()
reply = llm.get_response("你好，请用一句话介绍你自己", "demo_llm_01")
print("LLM:", reply)
llm.unload_model()
```

---

### 2) `lib/stt.py`：`STT`（FunASR，本地语音转文字）

#### 初始化
- `STT(_raw_path: str)`
  - `_raw_path`：原始音频文件路径（例如 `.m4a` / `.wav`）

#### 生命周期接口
- `load_model() -> None`
  - 作用：加载 Paraformer-zh（并启用 VAD），默认使用 GPU（`device="cuda"`）
- `unload_model() -> None`
  - 作用：卸载模型并清理显存
- `get_model_status -> bool`（属性）
  - 作用：查看模型是否已加载

#### 推理接口
- `process_audio() -> tuple[str, str]`
  - 返回：`(text, filename)`
  - 如果模型未加载，会自动调用 `load_model()`
- `get_text -> str`（属性）
  - 返回：等价于 `process_audio()[0]`

#### 音频处理接口
- `convert_audio(raw_path) -> tuple[str, str]`
  - 作用：调用 `ffmpeg` 将音频转换为 16kHz / 单声道 / s16 的 wav
  - 返回：`(converted_path, filename)`

#### 使用示例
```python
from lib.stt import STT

stt = STT("/CyberFeng/audio/raw/Sample3.m4a")
stt.load_model()

text, filename = stt.process_audio()
print("STT:", text, "filename:", filename)

stt.unload_model()
```

---

### 3) 串联示例：STT -> LLM
```python
from lib.stt import STT
from lib.llm import LLM

stt = STT("/CyberFeng/audio/raw/Sample3.m4a")
llm = LLM("Qwen/Qwen2.5-1.5B-Instruct")

stt.load_model()
llm.load_model()

text, filename = stt.process_audio()
reply = llm.get_response(text, filename)
print("reply:", reply)

llm.unload_model()
stt.unload_model()
```

> 一个基于大模型的端云协同多模态语音交互系统。
> 
> *“你是一个AI助手，名字叫CyberFeng。你的说话风格要酷一点，简短有力。”*


<!-- STATS:START -->
<!-- 此部分内容将由 GitHub Actions 自动更新 -->
<!-- STATS:END -->

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
├── firmware/               # ESP32 硬件端代码 (PlatformIO)
│   ├── src/                # C++ 源码 (main.cpp, ui.cpp)
│   ├── lib/                # 硬件驱动库
│   ├── platformio.ini      # 硬件项目配置文件
│   └── diagram.json        # Wokwi 仿真电路图
├── json/
│   ├── stt_output/         # 语音识别结果的 JSON 缓存
│   └── llm_output/         # 大模型输出的 JSON 缓存
├── lib/                    # 核心功能模块库 (Python)
│   ├── stt.py              # 语音识别模块 (本地 FunASR，可加载/卸载)
│   ├── llm.py              # 大模型对话模块 (本地 vLLM，可加载/卸载)
│   └── tts.py              # 语音合成客户端 (GPT-SoVITS)
├── models/                 # 本地模型/缓存目录（LLM/STT 都会下载到这里）
├── src/                    # 后端服务模块
│   └── webAPI.py           # FastAPI 接口服务 (供 ESP32 调用)
├── main.py                 # 项目主入口 / 本地测试脚本
├── requirements.txt        # Python 依赖清单
├── .env                    # 环境变量配置文件 (需自行创建)
└── README.md               # 项目说明文档
```

## 🛠 技术栈

本项目融合了多家前沿 AI 技术与工程化实践：

*   **编程语言**: Python 3.10+ (后端), C++ (硬件)
*   **Web 框架**: [FastAPI](https://fastapi.tiangolo.com/) (提供 RESTful 接口)
*   **语音识别 (ASR / STT)**: 本地 [FunASR](https://github.com/modelscope/FunASR) (Paraformer-zh)
    *   利用 FFmpeg 进行音频格式预处理（16kHz 单声道 wav）。
    *   支持手动 `load_model()` / `unload_model()` 管理显存与资源。
*   **大语言模型 (LLM)**: 本地 [vLLM](https://github.com/vllm-project/vllm) 加载 Qwen2.5 Instruct
    *   同样支持手动 `load_model()` / `unload_model()`。
    *   通过 Chat Template 注入 System Prompt（角色提示词）。
*   **语音合成 (TTS)**: [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
    *   私有化部署的高质量 TTS 服务。
    *   封装了 RESTful API 客户端，支持流式传输与模型切换。
*   **硬件开发 (IoT)**: [PlatformIO](https://platformio.org/)
    *   **主控**: ESP32 DevKit V1
    *   **显示**: SSD1306 OLED (I2C)
    *   **仿真**: Wokwi Simulator

## 🧩 实现过程与原理

系统采用了经典的 **"听-想-说"** 三段式架构，并增加了 **端云交互** 层：

1.  **听 (STT - lib/stt.py，本地 FunASR)**
    *   接收原始音频文件（如 `.m4a`）。
    *   调用 `ffmpeg` 转换为 **16kHz / 单声道 / s16 wav**。
    *   使用本地 FunASR `paraformer-zh` 推理得到文本（可选 VAD/标点模型）。
    *   支持手动加载/卸载模型，避免每次识别都重复加载。

2.  **想 (LLM - lib/llm.py，本地 vLLM)**
    *   接收 STT 结果文本。
    *   使用 tokenizer 的 Chat Template 组装 `system/user/assistant`，注入角色提示词（System Prompt）。
    *   vLLM 本地推理生成回复文本，并将输出以更清晰的结构写入 `json/llm_output/`。

3.  **说 (TTS - lib/tts.py)**
    *   接收 LLM 生成的回复文本。
    *   通过封装好的 `Infer` 类，向本地或远程运行的 GPT-SoVITS 服务发送 POST 请求。
    *   支持动态切换参考音频 (`ref_audio_path`) 以复刻特定音色。
    *   获取返回的音频流并保存到本地 `audio/trans/` 目录。

4.  **端云交互 (Web API - src/webAPI.py)**
    *   使用 FastAPI 搭建 HTTP 服务器，监听 `/chat` 接口。
    *   ESP32 通过 WiFi 上传录音文件。
    *   服务器编排 STT -> LLM -> TTS 全流程，并将生成的音频流直接返回给 ESP32。

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

本地 STT 需要额外依赖（如未写入 `requirements.txt` 请手动安装）：
```bash
pip install funasr modelscope torchaudio
```

*注意：你需要确保系统中已安装 `ffmpeg` 并配置了环境变量。*

### 3. 配置环境变量

#### 3.1 API Key（可选）
如果你只使用 **本地 STT/LLM**，可以不配置 Key；如果仍保留云端能力再按需添加。

在项目根目录创建 `.env` 文件（可选）：
```ini
# 可选：如果你仍在使用 DashScope 的云端能力
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
```

#### 3.2 下载代理（可选）
如果你需要给 Hugging Face / ModelScope 下载挂代理（用哪个填哪个）：
- 在终端运行前设置环境变量，或在代码最前面 `os.environ[...] = ...`
- 常见写法如下（示例端口 7890）：
```text
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

#### 3.3 国内镜像（可选）
如果你从 Hugging Face 下载很慢，可以设置：
```text
HF_ENDPOINT=https://hf-mirror.com
```

### 4. 部署 TTS 服务 (GPT-SoVITS)
本项目依赖 GPT-SoVITS 作为后端 TTS 服务。
1.  下载并运行 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)。
2.  启动 API 服务：
    ```bash
    python api_v2.py -a 0.0.0.0 -p 9880 -c GPT_SoVITS/configs/tts_infer.yaml
    ```
3.  确保模型文件已放置在服务端指定目录。

### 5. 启动后端服务 (Web API)
本项目提供了一个 FastAPI 服务供 ESP32 调用。
```bash
# 在项目根目录下运行
python src/webAPI.py
# 或者使用 uvicorn
uvicorn src.webAPI:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 烧录 ESP32 固件
1.  使用 VS Code 打开 `firmware/` 目录（或通过 PlatformIO 插件打开）。
2.  修改 `firmware/src/main.cpp` 中的 WiFi 信息和服务器 IP 地址。
3.  连接 ESP32 开发板，点击 PlatformIO 的 **Upload** 按钮进行烧录。
4.  或者使用 Wokwi 插件打开 `firmware/diagram.json` 进行仿真测试。

### 7. 本地测试 (可选)
如果你没有硬件，也可以直接运行 `main.py` 进行本地测试：
修改 `main.py` 中的 `tts_addr` 为你的 TTS 服务器地址，然后运行：
```bash
python main.py
```

## 📄 开源说明

本项目遵循 [MIT License](LICENSE) 开源协议。
你可以自由地使用、修改和分发本项目，但请保留原作者的版权声明。

---
*Created by Yao0454 | 2025*
