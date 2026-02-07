from pathlib import Path
from typing import List, Optional, Union

import requests


class TTS:
    def __init__(self, _api_addr: str) -> None:
        """
        在这里输入你的 APIKEY
        """
        if not _api_addr.startswith("http://") and not _api_addr.startswith("https://"):
            _api_addr = f"http://{_api_addr}"

        self.api_addr: str = _api_addr
        self.mode: str = ""
        self.payload: dict = {}
        self.params: dict = {}
        self.server_addr = "/mnt/data/GPTSoVits"

    def post(self) -> Optional[requests.Response]:
        # 发POST请求给GPT_SoVits
        url = f"{self.api_addr}{self.mode}"
        try:
            response: requests.Response = requests.post(
                url, json=self.payload, stream=True
            )
            return response
        except Exception as e:
            print(f"Post到{url}:{e}")
            return None

    def get(self) -> Optional[requests.Response]:
        # 发Get请求到GPT_SoVits
        url = f"{self.api_addr}{self.mode}"
        try:
            response: requests.Response = requests.get(url, params=self.params)
            return response
        except Exception as e:
            print(f"发Get到{url}:{e}")
            return None


class Infer(TTS):
    def __init__(
        self,
        _api_addr: str,  # GPT-SoVITS 服务地址（包含协议与端口）
        _text: str,  # 待合成的文本内容
        _text_lang: str,  # 文本对应的语言代码
        _ref_audio_path: str,  # 参考音频在服务器上的路径
        _prompt_lang: str,  # 参考提示文本的语言代码
        _prompt_text: str = "",  # 参考音频的提示描述文本
        _aux_ref_audio_paths: Optional[
            List[str]
        ] = None,  # 辅助参考音频列表（用于融合音色）
        _top_k: int = 15,  # top-k 采样阈值
        _top_p: float = 1.0,  # top-p（核采样）阈值
        _temperature: float = 1.0,  # 采样温度系数
        _text_split_method: str = "cut5",  # 文本切分策略名称
        _batch_size: int = 1,  # 推理批大小
        _batch_threshold: float = 0.75,  # 批切分阈值
        _split_bucket: bool = True,  # 是否开启分桶处理
        _speed_factor: float = 1.2,  # 输出音频的速度倍率
        _fragment_interval: float = 0.3,  # 音频片段间隔（秒）
        _seed: int = -1,  # 随机种子（-1 表示随机）
        _parallel_infer: bool = True,  # 是否启用并行推理
        _repetition_penalty: float = 1.35,  # 重复惩罚系数
        _sample_steps: int = 32,  # VITS 采样步数
        _super_sampling: bool = False,  # 是否开启超采样
        _streaming_mode: Union[bool, int] = False,  # 流式模式配置（布尔或 0-3）
        _overlap_length: int = 2,  # 流式模式语义 token 重叠长度
        _min_chunk_length: int = 16,  # 流式模式最小语义片段长度
    ) -> None:
        super().__init__(_api_addr)
        self.mode: str = "/tts"

        if _aux_ref_audio_paths is None:
            _aux_ref_audio_paths = []

        self.payload = {
            "text": _text,
            "text_lang": _text_lang,
            "ref_audio_path": _ref_audio_path,
            "aux_ref_audio_paths": _aux_ref_audio_paths,
            "prompt_text": _prompt_text,
            "prompt_lang": _prompt_lang,
            "top_k": _top_k,
            "top_p": _top_p,
            "temperature": _temperature,
            "text_split_method": _text_split_method,
            "batch_size": _batch_size,
            "batch_threshold": _batch_threshold,
            "split_bucket": _split_bucket,
            "speed_factor": _speed_factor,
            "fragment_interval": _fragment_interval,
            "seed": _seed,
            "parallel_infer": _parallel_infer,
            "repetition_penalty": _repetition_penalty,
            "sample_steps": _sample_steps,
            "super_sampling": _super_sampling,
            "streaming_mode": _streaming_mode,
            "overlap_length": _overlap_length,
            "min_chunk_length": _min_chunk_length,
        }

    @classmethod
    def simple(
        cls,
        _api_addr: str,  # GPT-SoVITS 服务地址
        _text: str,  # 待合成的文本内容
        _text_lang: str,  # 文本语言代码
    ) -> "Infer":
        return cls(
            _api_addr=_api_addr,
            _text=_text,
            _text_lang=_text_lang,
            _ref_audio_path="",
            _prompt_lang="",
            _prompt_text="",
            _aux_ref_audio_paths=[],
        )

    def save_audio(self, filename: str) -> Optional[str]:
        save_dir = Path.cwd() / "audio" / "trans"
        save_dir.mkdir(parents=True, exist_ok=True)

        full_path = save_dir / filename

        response = self.post()

        if response and response.status_code == 200:
            with full_path.open("wb") as f:
                f.write(response.content)
            print(f"音频保存至：{full_path}")
            return str(full_path)
        else:
            print(f"保存失败：{response.status_code if response else 'No Response'}")
            return None


class Control(TTS):
    def __init__(
        self,
        _api_addr: str,  # GPT-SoVITS 服务地址
        _command: str,  # 控制指令（restart / exit）
    ) -> None:
        super().__init__(_api_addr)
        self.mode: str = "/control"
        self.params = {"command": _command}


class GPT(TTS):
    def __init__(
        self,
        _api_addr: str,  # GPT-SoVITS 服务地址
        _weights_path: str,  # GPT 权重文件路径
    ) -> None:
        super().__init__(_api_addr)
        self.mode: str = "/set_gpt_weights"
        self.params = {"weights_path": _weights_path}


class Sovits(TTS):
    def __init__(
        self,
        _api_addr: str,  # GPT-SoVITS 服务地址
        _weights_path: str,  # SoVITS 权重文件路径
    ) -> None:
        super().__init__(_api_addr)
        self.mode: str = "/set_sovits_weights"
        self.params = {"weights_path": _weights_path}
