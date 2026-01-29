from lib.llm import LLM


def main() -> None:
    llmex: LLM = LLM("Qwen/Qwen2.5-1.5B-Instruct")
    llmex.load_model()
    i = 1
    while True:
        prompt: str = input("请输入提示词，退出则输入0：")
        if prompt == "0":
            llmex.unload_model()
            break
        print(llmex.get_response(prompt, f"test{i}"))
        i += 1


if __name__ == "__main__":
    main()
