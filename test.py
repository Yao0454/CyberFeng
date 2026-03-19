from src.CyberFeng import CyberFeng, CyberFengData


def main() -> None:
    datas: CyberFengData = CyberFengData()

    cyberfeng: CyberFeng = CyberFeng(datas)

    cyberfeng.start_service()


if __name__ == "__main__":
    main()
