from src.CyberFeng import CyberFeng, CyberFengData


def main() -> None:
    datas: CyberFengData = CyberFengData()

    cyberfeng: CyberFeng = CyberFeng(datas)

    cyberfeng.start_service()
    (
        cyberfeng.choose_audio("audio/raw/Sample1.m4a")
        .stt()
        .llm()
        .choose_audio("audio/raw/Sample2.m4a")
        .stt()
        .llm()
        .choose_audio("audio/raw/Sample3.m4a")
        .stt()
        .llm()
    )


if __name__ == "__main__":
    main()
