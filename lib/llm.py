#这里是llm.py 即 Large Language Model
#在这里将处理后的文字发送给LLM处理回答

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class LLM:
    def __init__(self, _text: str) -> None:
        self.text: str = _text
        api_key: str = str(os.getenv("GEMINI_API_KEY"))
        self.client = genai.Client(api_key=api_key)
    
    def get_response(self):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.text
        )
        print(response.text)
    

    
if __name__ == "__main__":
    extext: str = "你好啊，我很高兴和你对话！"
    
    llm1: LLM = LLM(extext)
    
    llm1.get_response()
# end main