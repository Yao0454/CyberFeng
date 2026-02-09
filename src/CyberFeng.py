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

    def get_status(self) -> bool:
        return self.stt_service.get_model_status and self.llm_service.get_model_status

    def start_service(self) -> bool:
        self.stt_service: STT = STT()
        self.llm_service: LLM = LLM(str(self.datas.model_path))

        self.stt_service.load_model()
        self.llm_service.load_model()
        return self.get_status()

    def stop_service(self) -> bool:
        self.stt_service.unload_model()
        self.llm_service.unload_model()
        return (
            not self.stt_service.get_model_status
            and not self.llm_service.get_model_status
        )

    def choose_audio(self, input_audio_path) -> Self:
        self.datas.input_audio_path = input_audio_path
        return self

    def stt(self) -> Self:
        if not self.get_status():
            raise RuntimeError("模型没有被正常初始化！")

        self.datas.transfered_text, self.datas.filename = (
            self.stt_service.process_audio(str(self.datas.input_audio_path))
        )

        return self

    def llm(self) -> Self:
        if not self.get_status():
            raise RuntimeError("模型没有被正常初始化！")
        self.datas.llm_response = str(
            self.llm_service.get_response(
                self.datas.transfered_text, self.datas.filename
            )
        )
        return self

    def tts(self) -> Self:
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
