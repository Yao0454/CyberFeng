from lib.stt import STT
from lib.llm import LLM

def main():
    stt1: STT = STT("/Users/feng/Desktop/CyberFeng/audio/raw/Sample2.m4a")
    llm1: LLM = LLM(stt1.one_click())
    
    print(llm1.get_response())

if __name__ == "__main__":
    main()
# end main


