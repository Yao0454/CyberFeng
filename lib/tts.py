# lib/tts.py

from pathlib import Path
from typing import List, Optional, Union

import requests


class TTS:
    """
    父类：给 GPT-SoVIts 发送请求
    """

    def __init__(self, _gpt_url: str) -> None:
        """
        在这里输入你的 APIKEY, 发送网络请求
        """
        # 规范化地址：确保开头有 http://
        if not _gpt_url.startswith("http://") and not _gpt_url.startswith("https://"):
            _gpt_url = f"http://{_gpt_url}"

        self.api_addr: str = _gpt_url  # 服务器地址
        self.mode: str = ""  # 告诉 API 进行对应操作，在子类中填写，拼接到服务器地址后面
        self.payload: dict = {}  # 存放要发给 API 的数据
        self.params: dict = {}  # 存放链接里的参数
        self.server_addr = "/mnt/data/GPTSoVits"

    def post(self) -> Optional[requests.Response]:
        """
        发POST请求给GPT_SoVits服务器
        """
        # POST 请求：向发送大量数据（这里是 JSON 格式）
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
        """
        发Get请求到GPT_SoVits服务器
        """
        # GET 请求：向服务器索取数据
        url = f"{self.api_addr}{self.mode}"
        try:
            response: requests.Response = requests.get(url, params=self.params)
            return response
        except Exception as e:
            print(f"发Get到{url}:{e}")
            return None


class Infer(TTS):
    """
    子类 Infer: 负责语音推理
    """

    def __init__(
        self,
        _gpt_url: str,  # GPT-SoVITS 服务地址（包含协议与端口）
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
        super().__init__(_gpt_url)
        self.mode: str = "/tts"  # 告诉服务器，我要做语音合成

        if _aux_ref_audio_paths is None:
            _aux_ref_audio_paths = []

        # GPT-SoVITS 需要的参数
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
        _gpt_url: str,
        _text: str,
        _text_lang: str,
    ) -> "Infer":
        """接受少量核心参数，其余复杂的参数按照默认值分配

        Args:
            _gpt_url (str): GPT-SoVITS 服务器地址
            _text: str (str): 待合成的文本内容
            _text_lang (str): 参考提交文本的语言，例如 "zh"

        Returns:
            Infer: 一个实例对象
        """
        return cls(
            _gpt_url=_gpt_url,
            _text=_text,
            _text_lang=_text_lang,
            _ref_audio_path="",
            _prompt_lang="",
            _prompt_text="",
            _aux_ref_audio_paths=[],
        )

    def save_audio(self, filename: str) -> Path | str:
        """保存声音文件

        Args:
            filename (str): 文件名

        Returns:
            Path | str: 文件路径 or 空
        """
        save_dir = Path.cwd() / "audio" / "trans"
        save_dir.mkdir(parents=True, exist_ok=True)

        full_path = save_dir / filename

        response = self.post()

        if response and response.status_code == 200:
            with full_path.open("wb") as f:
                f.write(response.content)
            print(f"音频保存至：{full_path}")
            return full_path
        else:
            print(f"保存失败：{response.status_code if response else 'No Response'}")
            return ""


class Control(TTS):
    def __init__(
        self,
        _gpt_url: str,  # GPT-SoVITS 服务地址
        _command: str,  # 控制指令（restart / exit）
    ) -> None:
        super().__init__(_gpt_url)
        self.mode: str = "/control"  # 服务器进行 control 操作
        self.params = {"command": _command}  # 重启 or 退出


class GPT(TTS):
    """
    改变说话风格
    """

    def __init__(
        self,
        _gpt_url: str,  # GPT-SoVITS 服务地址
        _weights_path: str,  # GPT 权重文件路径
    ) -> None:
        super().__init__(_gpt_url)
        self.mode: str = "/set_gpt_weights"
        self.params = {"weights_path": _weights_path}


class Sovits(TTS):
    """
    改变音色
    """

    def __init__(
        self,
        _gpt_url: str,  # GPT-SoVITS 服务地址
        _weights_path: str,  # SoVITS 权重文件路径
    ) -> None:
        super().__init__(_gpt_url)
        self.mode: str = "/set_sovits_weights"
        self.params = {"weights_path": _weights_path}


def main() -> None:
    addr: str = "http://127.0.0.1:9880"
    infer: Infer = Infer(
        _gpt_url=addr,
        _text="你好啊",
        _text_lang="zh",
        _ref_audio_path="referenc_voice/reference.wav",
        _prompt_lang="zh",
        _prompt_text="就是学习函数可能的输出，在这个例子里",
    )
    infer.post()


if __name__ == "__main__":
    main()
