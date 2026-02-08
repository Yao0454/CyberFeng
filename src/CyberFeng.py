from dataclasses import dataclass
from pathlib import Path
from typing import Self

from lib.llm import LLM
from lib.stt import STT
from lib.tts import Infer


@dataclass
class CyberFengData:
    input_audio_path: Path | str = ""
    model_path: Path | str = "Qwen/Qwen2.5-1.5B-Instruct"
    transfered_text: str = ""
    filename: str = ""
    llm_response: str = ""


@dataclass
class CyberFeng:
    datas: CyberFengData = CyberFengData()

    @classmethod
    def get_status(cls) -> bool:
        return cls.stt_service.get_model_status and cls.llm_service.get_model_status

    @classmethod
    def start_service(cls) -> bool:
        cls.stt_service: STT = STT()
        cls.llm_service: LLM = LLM(str(cls.datas.model_path))

        cls.stt_service.load_model()
        cls.llm_service.load_model()
        return cls.get_status()

    @classmethod
    def stop_service(cls) -> bool:
        cls.stt_service.unload_model()
        cls.llm_service.unload_model()
        return (
            not cls.stt_service.get_model_status
            and not cls.llm_service.get_model_status
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
