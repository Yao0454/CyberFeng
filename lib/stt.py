'''
这应该是我真正意义上的第一个自己完成的项目文件吧
太他妈爽了
里面包含了一段我自己都绷不住的声音
我受不了了

这个我是调用了通义的qwen3的API做的语音转文字
挺好用的
新人还有5000k tokens能领
'''

#stt.py 即 Speak to Text 将嵌入式端得到的语音文件转换为文本
import os
import dashscope
import subprocess
import json

#给声音处理创建一个类
class STT:
    #构造函数：传入音频文件地址
    def __init__(self, _raw_path: str) -> None:
        
        self.raw_path: str = _raw_path
        #获取环境变量中的API_KEY
        self.api_key: str = str(os.getenv("DASHSCOPE_API_KEY"))
        #给API节点设置地址，位于北京，他还可以选用新加坡的节点
        dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

        #设置我的音频处理输出路径和我的文字输出路径
        self.audio_output_dir = os.path.join(os.getcwd(), "audio", "converted")
        self.json_output_dir = os.path.join(os.getcwd(), "json", "stt_output")

        #万一没有呢？
        if not os.path.exists(self.audio_output_dir):
            os.makedirs(self.audio_output_dir)
        if not os.path.exists(self.json_output_dir):
            os.makedirs(self.json_output_dir)        

    #这个函数用了FFMPEG将输入进来的音频统一转换为API支持的格式
    def convert_audio(self) -> tuple[str, str]:
        #首先获取一下文件名 方便给接下来生成的文件命名
        filename: str = os.path.splitext(os.path.basename(self.raw_path))[0]
        #配置输出文件的路径以及名字
        output_path: str = os.path.join(self.audio_output_dir, f"{filename}_converted.wav")
        #他这个API调用文件必须加一个这个我服了
        front: str = "file://"
        #使用FFMPEG的命令
        command: list = [
            'ffmpeg',
            '-y',
            '-i', self.raw_path,
            '-ac', '1',
            '-ar', '16000',
            '-sample_fmt', 's16',
            output_path
        ]
        #直到开始做项目才发现try except有多重要
        try:
            #调用子进程来处理音频文件
            subprocess.run(command, check=True, capture_output=True)
            #print(f"转换成功: {output_path}")
            return front + output_path, filename
        except subprocess.CalledProcessError as e:
            print(f"转换失败: {e}")
            if e.stderr:
                print(f"错误详情: {e.stderr.decode()}")
            return "", filename
        
    #这个函数用来将音频文件发给API然后转换成文字
    #他们官方文档给的返回值是一个带有固定模版的jsonfile
    def process_audio(self, filepath: str):
        #这里配置模型设置
        messages: list[dict] = [
            {"role" : "system", "content" : [{"text" : ""}]},
            {"role" : "user", "content" : [{"audio" : filepath}]}
        ]
        #诶 我再try一下
        try:
            response = dashscope.MultiModalConversation.call(
                api_key = self.api_key,
                model = "qwen3-asr-flash",
                messages = messages,
                result_format = "message",
                asr_options = {
                    "enable_itn" : False
                }
            )
            
            return response
            
        except Exception as e:
            print(f"[Error]:{e}")
            return
        
    #这个函数把我获取到的responce写入一个json文件里面
    def save_to_json(self, response, filename: str) -> str:
        json_filename: str = f"{filename}_text.json"
        json_path: str = os.path.join(self.json_output_dir, json_filename)
        #讨厌文件处理
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=4)
        
        #print(f"语音文本已保存至{json_path}")
        return json_path

    #从json里面取出精华，即你说的话
    def get_text(self, json_path: str) -> str:
        with open(json_path, 'r' ,encoding='utf-8') as f:
            data = json.load(f)
            text: str = data['output']['choices'][0]['message']['content'][0]['text']
            return text
    
    #傻瓜式 直接返回你说的话 类型为str方便之后的操作
    #其实我可以写个修饰器让他直接变成一个变量
    #再说吧
    #@property
    #算了 反正就一行
    def one_click(self) -> tuple[str, str]:
        converted_path, filename = self.convert_audio()
        return self.get_text(self.save_to_json(self.process_audio(converted_path), filename)), filename
    
    

    
if __name__ == "__main__":
    #debuuuuuuuuuuuuuuug
    filepath: str = "/Users/feng/Desktop/CyberFeng/audio/raw/Sample1.m4a"
    #print(os.getenv("DASHSCOPE_API_KEY"))
    #converted_path, filename = convert_audio(filepath)
    #json_path: str = save_to_json(process_audio(converted_path), filename)
    stt_demo = STT(filepath)
    converted_path, filename = stt_demo.convert_audio()
    stt_demo.save_to_json(stt_demo.process_audio(converted_path), filename)
    
    
    
# end main