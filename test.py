from lib.llm import LLM
from lib.stt import STT


def pre_work(stt_workflow: STT, llm_workflow: LLM) -> bool:
    stt_workflow.load_model()
    llm_workflow.load_model()
    if not (stt_workflow.get_model_status or llm_workflow.get_model_status):
        return False
    return True


def main() -> None:
    model_path: str = "Qwen/Qwen2.5-1.5B-Instruct"
    audio_path: str = "audio/raw/Sample5.m4a"
    stt_workflow = STT(audio_path)
    llm_workflow = LLM(model_path)
    if not pre_work(stt_workflow, llm_workflow):
        print("模型启动失败")
        return
