# 这里是llm.py 即 Large Language Model
# 在这里将处理后的文字发送给LLM处理回答

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# from google import genai
# from google.genai import types
from fastapi.openapi.models import APIKey
from openai import OpenAI, base_url

load_dotenv()


class LLM:
    def __init__(self, _text: str, _filename: str) -> None:
        self.text: str = _text
        self.role_prompt: str = "你是一个AI智能语音助手，你叫枫枫子，你会很热情的回答别人的问题，把你的回答总结为一句话，不超过20个字"
        # Gemini API 暂时弃用
        # api_key: str = str(os.getenv("GEMINI_API_KEY"))
        # 更换为通义千问
        # api_key: str = str(os.getenv("DASHSCOPE_API_KEY"))

        self.client = OpenAI(
            # api_key=api_key,
            # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            base_url="http://localhost:8000/v1",
            api_key="EMPTY",
        )
        self.model_name: str = "qwen2.5"
        self.filename: str = _filename

    def get_response(self) -> str:
        """
        暂时弃用 Gemini
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.text,
            config=types.GenerateContentConfig(
                system_instruction = self.role_prompt
            )
        )
        换用通义千问
        """
        response = self.client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": self.role_prompt},
                {"role": "user", "content": self.text},
            ],
        )

        # 新增逻辑让LLM输出保留在json文件里面
        save_dir = Path.cwd() / "json" / "llm_output"

        save_dir.mkdir(parents=True, exist_ok=True)

        """
        更换后输出格式为json
        data_to_save: dict = {
            "输入" : self.text,
            "LLM输出" : response.text
        }
        """
        answer_text: str = str(response.choices[0].message.content)

        data_to_save = {
            "input": self.text,
            "output": answer_text,
            "raw_data": response.model_dump(),
        }

        full_path = save_dir / f"{self.filename}.json"
        with full_path.open("w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        print(f"LLM输出已保存至{full_path}")
        return str(answer_text)


if __name__ == "__main__":
    extext: str = "你好啊，我很高兴和你对话！"

    llm1: LLM = LLM(extext, "qwq")

    llm1.get_response()
# end main
