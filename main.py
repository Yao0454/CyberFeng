import src.webAPI as webAPI
from lib.stt import STT


def main() -> None:
    stt1: STT = STT()
    prompt, filename = stt1.process_audio("")

    """
    tts_addr: str = "36.103.177.158:9880"

    refau: str = "reference_voice/reference.wav"
    refte: str = "就是学习函数可能的输出，在这个例子里"
    # tts_Sovits = tts.Sovits(tts_addr, "SoVITS_weights_v4/CyberFeng_e8_s64_l32.pth")
    # tts_GPT = tts.GPT(tts_addr, "GPT_weights_v4/CyberFeng-e15.ckpt")
    # tts_Sovits.get()
    # tts_GPT.get()
    llm_response_text: str = llm1.get_response()

    if os.environ.get("NO_PROXY"):
        os.environ["NO_PROXY"] += ",36.103.177.158"
    else:
        os.environ["NO_PROXY"] = "36.103.177.158"
    tts_infer: tts.Infer = tts.Infer(
        tts_addr, llm_response_text, "zh", refau, "zh", refte
    )
    tts_infer.save_audio(f"{filename}.wav")
    """


def debug_web() -> None:
    webAPI.run_server()


if __name__ == "__main__":
    # main()
    debug_web()

# end main
