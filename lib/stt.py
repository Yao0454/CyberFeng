# stt.py 即 Speak to Text 将嵌入式端得到的语音文件转换为文本
import gc
import json
import subprocess
from pathlib import Path

import torch
from funasr import AutoModel

project_root = Path(__file__).resolve().parent.parent
models_dir = project_root / "models"
models_dir.mkdir(parents=True, exist_ok=True)


# 给声音处理创建一个类
class STT:
    # 构造函数：传入音频文件地址
    def __init__(
        self,
    ) -> None:
        """
        初始化 STT 服务
        """

        # 设置我的音频处理输出路径和我的文字输出路径
        self.audio_output_dir: Path = Path.cwd() / "audio" / "converted"
        self.json_output_dir: Path = Path.cwd() / "json" / "stt_output"
        # 万一没有呢？
        self.audio_output_dir.mkdir(parents=True, exist_ok=True)
        self.json_output_dir.mkdir(parents=True, exist_ok=True)

        # 预设模型启动状态为空
        self.model = None

    def load_model(self) -> None:
        """
        启动 STT 模型
        """
        if self.model is None:
            print("正在启动 STT 模型")
            try:
                self.model = AutoModel(
                    model="paraformer-zh",
                    vad_model="fsmn-vad",
                    device="cuda",
                )
                print("STT 模型加载完成")
            except Exception as e:
                print(f"STT 模型加载失败：{e}")
        else:
            print("STT 模型已在运行中")

    def unload_model(self) -> None:
        """
        关闭 STT 模型
        """
        if self.model is not None:
            print("正在关闭 STT 模型")
            try:
                del self.model
                self.model = None
                gc.collect()
                torch.cuda.empty_cache()
                print("STT 模型已卸载")

            except Exception as e:
                print(f"模型未成功卸载：{e}")
        else:
            print("STT 模型为加载")

    @property
    def get_model_status(self) -> bool:
        return self.model is not None

    # 这个函数用了FFMPEG将输入进来的音频统一转换为API支持的格式
    def convert_audio(self, raw_path: str) -> tuple[str, str]:
        # 首先获取一下文件名 方便给接下来生成的文件命名

        filename: str = Path(raw_path).stem
        # 配置输出文件的路径以及名字
        output_path = self.audio_output_dir / f"{filename}_converted.wav"
        # 他这个API调用文件必须加一个这个我服了
        # 使用FFMPEG的命令
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(raw_path),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-sample_fmt",
            "s16",
            str(output_path),
        ]
        # 直到开始做项目才发现try except有多重要
        try:
            # 调用子进程来处理音频文件
            subprocess.run(command, check=True, capture_output=True)
            print(f"转换成功: {output_path}")
            return str(output_path), filename
        except subprocess.CalledProcessError as e:
            print(f"转换失败: {e}")
            if e.stderr:
                print(f"错误详情: {e.stderr.decode()}")
            return "", filename

    # 这个函数用来将音频文件发给API然后转换成文字
    # 他们官方文档给的返回值是一个带有固定模版的jsonfile
    def process_audio(self, raw_path: str) -> tuple[str, str]:
        """
        语音转文字

        Returns:
            text: str 转换后的文字
            filename: str 文件名
        """
        if not self.model:
            print("STT 模型未加载，将自动加载模型...")
            self.load_model()
            assert self.model is not None

        converted_path, filename = self.convert_audio(raw_path)

        try:
            response = self.model.generate(input=converted_path)
            text: str = response[0]["text"]
            self.save_to_json(response=response, filename=filename)
            return text, filename
        except Exception as e:
            print(f"识别过程出错：{e}")
            return "", filename

    # 这个函数把我获取到的responce写入一个json文件里面
    def save_to_json(self, response, filename: str) -> str:
        """
        接受stt的response以及写入json文件的文件名
        将转换的文字写入该文件
        """
        json_filename: str = f"{filename}_text.json"

        json_path = self.json_output_dir / json_filename
        # 讨厌文件处理
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=4)

        print(f"语音文本已保存至{json_path}")
        return str(json_path)


if __name__ == "__main__":
    # debuuuuuuuuuuuuuuug
    filepath: str = "/home/xingning/CyberFeng/audio/raw/Sample3.m4a"

# end main
