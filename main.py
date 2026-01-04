from lib.stt import STT
from lib.llm import LLM
import lib.tts as tts
import src.webAPI as webAPI
import os



def main():
    stt1: STT = STT("/Users/feng/Desktop/CyberFeng/audio/raw/Sample3.m4a")
    prompt, filename = stt1.one_click()
    llm1: LLM = LLM(prompt, filename)
        
    tts_addr: str = "36.103.177.158:9880"
    
    refau: str = "reference_voice/reference.wav"
    refte: str = "就是学习函数可能的输出，在这个例子里"
    #tts_Sovits = tts.Sovits(tts_addr, "SoVITS_weights_v4/CyberFeng_e8_s64_l32.pth")
    #tts_GPT = tts.GPT(tts_addr, "GPT_weights_v4/CyberFeng-e15.ckpt")
    #tts_Sovits.get()
    #tts_GPT.get()
    llm_response_text: str = llm1.get_response()
    
    if os.environ.get('NO_PROXY'):
        os.environ['NO_PROXY'] += ',36.103.177.158'
    else:
        os.environ['NO_PROXY'] = '36.103.177.158'
    tts_infer: tts.Infer = tts.Infer(tts_addr, llm_response_text, "zh", refau, "zh", refte)
    tts_infer.save_audio(f"{filename}.wav")
    
    print(llm1.get_response())
   

def debug_web():
    webAPI.run_server()

if __name__ == "__main__":
    #main()
    debug_web()

# end main