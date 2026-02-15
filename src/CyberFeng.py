from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from lib.llm import LLM
from lib.stt import STT
from lib.tts import Infer


@dataclass
class CyberFengData:
    input_audio_path: Path | str = ""
    model_path: Path | str = "Qwen/Qwen2.5-1.5B-Instruct"
    tts_addr: str = "http://36.103.177.158:9880"
    ref_audio_path: str = "reference_voice/reference.wav"
    ref_text: str = "就是学习函数可能的输出，在这个例子里"

    transfered_text: str = ""
    filename: str = ""
    llm_response: str = ""
    output_audio_path: Path | str = ""


@dataclass
class CyberFeng:
    datas: CyberFengData = field(default_factory=CyberFengData)

    @property
    def get_status(self) -> bool:
        """获取服务状态，当 STT 和 LLM 模型均已加载时返回 True。

        Returns:
            bool: 当 STT 和 LLM 模型均已加载时返回 True，否则返回 False。
        """
        return self.stt_service.get_model_status and self.llm_service.get_model_status

    def start_service(self) -> bool:
        """启动服务：初始化并加载 STT 和 LLM 模型，返回是否全部加载成功。

        Returns:
            bool: 当 STT 和 LLM 模型均加载成功时返回 True，否则返回 False。
        """
        self.stt_service: STT = STT()
        self.llm_service: LLM = LLM(str(self.datas.model_path))

        self.stt_service.load_model()
        self.llm_service.load_model()
        return self.get_status

    def stop_service(self) -> bool:
        """停止服务：卸载 STT 和 LLM 模型，返回是否全部卸载成功。

        Returns:
            bool: 当 STT 和 LLM 模型均卸载成功时返回 True，否则返回 False。
        """
        self.stt_service.unload_model()
        self.llm_service.unload_model()
        return (
            not self.stt_service.get_model_status
            and not self.llm_service.get_model_status
        )

    def choose_audio(self, input_audio_path) -> Self:
        """选择输入音频文件路径，支持链式调用。

        Args:
            input_audio_path: 输入音频文件的路径。

        Returns:
            Self: 返回自身实例，支持链式调用。
        """
        self.datas.input_audio_path = input_audio_path
        return self

    def stt(self) -> Self:
        """语音转文字：将输入音频通过 STT 模型转换为文本，结果存储在 datas 中，支持链式调用。

        转写结果保存至 datas.transfered_text，文件名保存至 datas.filename。

        Returns:
            Self: 返回自身实例，支持链式调用。

        Raises:
            RuntimeError: 当 STT 或 LLM 模型未正常初始化时抛出。
        """
        if not self.get_status:
            raise RuntimeError("模型没有被正常初始化！")

        self.datas.transfered_text, self.datas.filename = (
            self.stt_service.process_audio(str(self.datas.input_audio_path))
        )

        return self

    def llm(self) -> Self:
        """大语言模型推理：将 STT 转写的文本送入 LLM 获取回复，结果存储在 datas 中，支持链式调用。

        推理结果保存至 datas.llm_response。

        Returns:
            Self: 返回自身实例，支持链式调用。

        Raises:
            RuntimeError: 当 STT 或 LLM 模型未正常初始化时抛出。
        """
        if not self.get_status:
            raise RuntimeError("模型没有被正常初始化！")
        self.datas.llm_response = str(
            self.llm_service.get_response(
                self.datas.transfered_text, self.datas.filename
            )
        )
        return self

    def tts(self) -> Self:
        """文字转语音：将 LLM 的回复通过 TTS 服务合成为音频文件，输出路径存储在 datas 中，支持链式调用。

        合成音频的保存路径存储至 datas.output_audio_path。

        Returns:
            Self: 返回自身实例，支持链式调用。
        """
        infer: Infer = Infer(
            _api_addr=self.datas.tts_addr,
            _text=str(self.datas.llm_response),
            _text_lang="zh",
            _ref_audio_path=self.datas.ref_audio_path,
            _prompt_lang="zh",
            _prompt_text=self.datas.ref_text,
        )
        self.datas.output_audio_path = infer.save_audio(self.datas.filename)

        return self
