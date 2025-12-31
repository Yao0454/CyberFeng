from lib.stt import STT
from lib.llm import LLM
import lib.tts as tts

def main():
    stt1: STT = STT("/Users/feng/Desktop/CyberFeng/audio/raw/Sample3.m4a")
    stt1_result = stt1.one_click()
    llm1: LLM = LLM(stt1_result[0])
    
    
    
    
    tts_addr: str = "127.0.0.1:9880"
    
    refau: str = "reference_voice/reference.wav"
    refte: str = "就是学习函数可能的输出，在这个例子里"
    #tts_Sovits = tts.Sovits(tts_addr, "SoVITS_weights_v4/CyberFeng_e8_s64_l32.pth")
    #tts_GPT = tts.GPT(tts_addr, "GPT_weights_v4/CyberFeng-e15.ckpt")
    #tts_Sovits.get()
    #tts_GPT.get()
    tts_infer: tts.Infer = tts.Infer(tts_addr, llm1.get_response(), "zh", refau, "zh", refte)
    tts_infer.save_audio(f"{stt1_result[1]}.wav")
    
   #print(llm1.get_response())

if __name__ == "__main__":
    main()

# end main