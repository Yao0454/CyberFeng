from lib.stt import STT

def main():
    stt1: STT = STT("/Users/feng/Desktop/CyberFeng/audio/raw/Sample1.m4a")
    print(stt1.one_click())

if __name__ == "__main__":
    main()
# end main


