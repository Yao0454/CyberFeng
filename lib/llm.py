# 这里是llm.py 即 Large Language Model
# 在这里将处理后的文字发送给LLM处理回答
import json
import os
from pathlib import Path
from typing import Optional

import torch
import vllm
from dotenv import load_dotenv 
from transformers import AutoTokenizer # 分词器：把文字转换成电脑认识的数字

load_dotenv()
proxy_url = "http://127.0.0.1:10808"

os.environ["HTTP_PROXY"] = proxy_url
os.environ["HTTPS_PROXY"] = proxy_url


class LLM:
    def __init__(
        self,
        _modelpath: str,
        _temperature: float = 0.7,
        _top_p: float = 0.8,
        _max_tokens: int = 512,
        _gpu_memory_utilization: float = 0.65,
    ) -> None:
        """
        初始化 LLM 配置
        """
        
        # 人设设定
        self.role_prompt: str = "你是一个AI智能语音助手，你叫枫枫子，你会很热情的回答别人的问题，把你的回答总结为一句话，不超过20个字"
        
        self.model_path: str = _modelpath
        self.temperature: float = _temperature
        self.top_p: float = _top_p
        self.max_tokens: int = _max_tokens # 最大回复长度
        self.gpu_memory_utilization: float = _gpu_memory_utilization # 显存占用率

        self.llm = None
        self.tokenizer = None
        self.sampling_params = None


    def load_model(self) -> None:
        """
        新增接口：启动配置的 LLM 模型
        """
        # 找到模型的存储路径
        project_root = Path(__file__).resolve().parent.parent
        models_dir = project_root / "models"

        if self.llm is None:
            print(f"正在加载模型：{self.model_path}")
            
            # 使用 vLLM 加载模型 
            self.llm = vllm.LLM(
                model=self.model_path,
                gpu_memory_utilization=self.gpu_memory_utilization,
                download_dir=str(models_dir),
            )

            # 加载分词器
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            
            # 模型参数设置：选词方式
            self.sampling_params = vllm.SamplingParams(
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
            )
            print("模型加载完成")
        else:
            print("模型已经在运行中")

    def unload_model(self) -> None:
        """
        新增接口：关闭模型
        """
        if self.llm is not None:
            print("正在关闭模型")
            del self.llm
            self.llm = None

            if self.tokenizer:
                del self.tokenizer
                self.tokenizer = None

            torch.cuda.empty_cache()
            print("模型已关闭")
        else:
            print("模型并未启动")

    @property
    def get_model_status(self) -> bool:
        return self.llm is not None

    def get_response(self, text: str, filename: str) -> Optional[str]:
        """
        用来产出对话

        Args:
            text: 输入文本
            filename: 文件名
        Returns:
            answer_text: llm回复
        """
        if self.tokenizer is None or self.llm is None:
            print("模型未启动")
            return

        assert self.tokenizer is not None
        assert self.llm is not None

        # AI 对话的标准格式：系统指令 + 用户提问
        messages = [
            {"role": "system", "content": self.role_prompt},
            {"role": "user", "content": text},
        ]

        # 把 messages 列表转成模型能看懂的格式
        prompt_text = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )

        # 生成回答
        response = self.llm.generate([prompt_text], self.sampling_params)

        # 提取回答中的文字
        answer_text: str = str(response[0].outputs[0].text)

        
        request_output: vllm.RequestOutput = response[0]
        raw_data_dict: dict = {
            "request_id": request_output.request_id,
            "prompt": request_output.prompt,
            "generated_text": request_output.outputs[0].text,
            "finish_reason": request_output.outputs[0].finish_reason,
            "finished": request_output.finished,
        }
        
        # 需要的结果保存在字典中
        data_to_save = {
            "input": text,
            "output": answer_text,
            "raw_data": raw_data_dict,
        }

        # 和 STT 文件中、的逻辑类似，让 LLM 的输出保留在 json 文件里面
        save_dir = Path.cwd() / "json" / "llm_output"
        save_dir.mkdir(parents=True, exist_ok=True)
        full_path = save_dir / f"{filename}.json"
        with full_path.open("w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        print(f"LLM输出已保存至{full_path}")
        return str(answer_text)

    def set_sampling_params(
        self, _temperature: float, _top_p: float, _max_tokens: int
    ) -> None:
        """
        这个函数用来调整模型采样参数
        """
        self.temperature = _temperature
        self.top_p = _top_p
        self.max_tokens = _max_tokens
        if self.sampling_params:
            self.sampling_params = vllm.SamplingParams(
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
            )

    def set_gpu_memory_utilization(self, gpu_memory_utilization: float) -> None:
        if self.llm is None:
            self.gpu_memory_utilization = gpu_memory_utilization
        else:
            self.unload_model()
            self.gpu_memory_utilization = gpu_memory_utilization
            self.load_model()

    def __del__(self) -> None:
        """
        析构函数: 删除实例对象后清理显存
        """
        if self.llm:
            del self.llm
            torch.cuda.empty_cache()


if __name__ == "__main__":
    extext: str = "你好啊，我很高兴和你对话！"
    model_path: str = "Qwen/Qwen2.5-1.5B-Instruct"

    llm1 = LLM(model_path)
    llm1.load_model()
    response1: Optional[str] = llm1.get_response("你好呀！", "test1")
    response2: Optional[str] = llm1.get_response("你知道物理应该怎么学吗？", "test2")
    print(response1, response2)
    llm1.unload_model()
# end main
