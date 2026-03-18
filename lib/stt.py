# stt.py 即 Speak to Text 将嵌入式端得到的语音文件转换为文本
import gc  # Garbage Collector："垃圾回收"，手动清理显存/内存
import json
import subprocess
from pathlib import Path  # 现代文件路径处理库

import torch
from funasr import AutoModel

# 环境准备：确保在父目录中创建 models 文件夹
project_root = Path(__file__).resolve().parent.parent
models_dir = project_root / "models"
models_dir.mkdir(parents=True, exist_ok=True)


# 给声音处理创建 STT 类
class STT:
    # 构造函数：传入的音频文件所在地址
    def __init__(self) -> None:
        """
        1. 初始化 STT 服务：设置音频处理输出路径和文字输出路径
        """
        # cwd(): 获取当前文件的路径
        # 在 Path 库中，"/" 被重载为 "进入下一级目录"
        self.audio_output_dir: Path = Path.cwd() / "audio" / "converted"
        self.json_output_dir: Path = Path.cwd() / "json" / "stt_output"
        # 以防万一，确保两个文件夹的创建
        self.audio_output_dir.mkdir(parents=True, exist_ok=True)
        self.json_output_dir.mkdir(parents=True, exist_ok=True)
        # 预设模型启动状态为空，节省显存
        self.model = None

    def load_model(self) -> None:
        """
        2. 启动 STT 模型
        """
        if self.model is None:
            print("正在启动 STT 模型")
            try:
                self.model = AutoModel(
                    model="paraformer-zh",  # 下载和加载中文“语音转文字”模型
                    vad_model="fsmn-vad",  # 辅助模型：选取有声音的片段
                    device="cuda",  # 计算设备：GPU
                )
                print("STT 模型加载完成")
            except Exception as e:
                print(f"STT 模型加载失败：{e}")
        else:
            print("STT 模型已在运行中")

    def unload_model(self) -> None:
        """
        3. 卸载 STT 模型
        """
        # 使用 try-except 结构，防止程序直接崩溃
        if self.model is not None:
            print("正在关闭 STT 模型")
            try:
                del self.model  # "删除"模型
                self.model = None
                gc.collect()  # 清理系统内存
                torch.cuda.empty_cache()  # 利用 Pytorch 强制释放未使用的显存
                print("STT 模型已卸载")

            except Exception as e:
                print(f"模型未成功卸载：{e}")
        else:
            print("STT 模型为加载")

    @property
    def get_model_status(self) -> bool:
        return self.model is not None

    def convert_audio(self, raw_path: str, output_path: str) -> tuple[str, str]:
        """
        4. 使用 FFmpeg 将音频格式转换为 API 支持的格式

        Arg:
            raw_path: str : 原始音频文件路径

        Returns：
            str(output_path), filename | "", filename : 转换格式后的音频文件路径和文件名
        """

        # 首先获取一下文件名 方便给接下来生成的文件命名
        # Path 类中，stem 属性直接对应文件名，无需切割
        filename: str = Path(raw_path).stem
        # 配置输出文件的路径以及名字
        # 使用 FFmpeg 的命令，用 "," 替代命令行中的 " "
        command = [
            "ffmpeg",  # 表明使用 FFmpeg
            "-y",
            "-f",
            "s16le",  # 采样深度
            "-ar",
            "16000",  # 声音频率设置：16000Hz
            "-ac",
            "1",  # 声道设置：单声道
            "-i",
            str(raw_path),  # 输入文件,
            str(output_path),
        ]
        # 直到开始做项目才发现try except有多重要
        try:
            # 调用子进程来处理音频文件
            # 运行上面的命令，相当于在终端里按回车
            subprocess.run(command, check=True, capture_output=True)
            print(f"转换成功: {output_path}")
            return str(output_path), filename
        except subprocess.CalledProcessError as e:
            print(f"转换失败: {e}")
            if e.stderr:
                print(f"错误详情: {e.stderr.decode()}")
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

    def process_audio(self, raw_path: str, output_path: str) -> tuple[str, str]:
        """
        5. 把音频文件发给本地模型进行语音转文字，作为后续的 Prompt

        Returns:
            text: str 转换后的文字
            filename: str 文件名
        """
        if not self.model:
            print("STT 模型未加载，将自动加载模型...")
            self.load_model()
            assert self.model is not None

        converted_path, filename = self.convert_audio(raw_path, output_path)

        try:
            response = self.model.generate(input=converted_path)
            text: str = response[0]["text"]
            # 把文本以及更多信息保存到 json 文件中
            self.save_to_json(response=response, filename=filename)
            return text, filename
        except Exception as e:
            print(f"识别过程出错：{e}")
            return "", filename


if __name__ == "__main__":
    # debuuuuuuuuuuuuuuug
    filepath: str = "/home/xingning/CyberFeng/audio/raw/Sample3.m4a"

# end main
