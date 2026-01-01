import os
import shutil
import sys
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from lib.llm import LLM
from lib.stt import STT
import lib.tts as tts

app = FastAPI(title="CyberFeng")

UPLOAD_DIR = os.path.join(os.getcwd(), "audio", "raw")
RESPONCE_DIR = os.path.join(os.getcwd(), "audio", "trans")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESPONCE_DIR, exist_ok=True)

TTS_SERVER_ADDR = "http://127.0.0.1:9880"
REF_AUDIO_PATH = "reference_voice/reference.wav"
REF_TEXT = "就是学习函数可能的输出，在这个例子里"



@app.post("/chat")
async def chat_endpoint(file: UploadFile = File(...)):
    try:
        #保存上传到服务器的音频文件
        file_location: str = os.path.join(UPLOAD_DIR, file.filename or "")
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"成功收到音频文件{file_location}")
        
        #STT
        stt_workflow = STT(file_location)
        input_text, filename = stt_workflow.one_click()
        
        #LLM
        llm_workflow = LLM(input_text, filename)
        llm_responce = llm_workflow.get_response()
        
        #TTS
        tts_workflow = tts.Infer(
            _api_addr=TTS_SERVER_ADDR,
            _text=llm_responce,
            _text_lang="zh",
            _ref_audio_path=REF_AUDIO_PATH,
            _prompt_lang="zh",
            _prompt_text=REF_TEXT
        )
        
        output_audio_path = tts_workflow.save_audio(filename)
        
        if output_audio_path and os.path.exists(output_audio_path):
            return FileResponse(output_audio_path, media_type="audio/wav", filename="reply.wav")
        else:
            raise HTTPException(status_code=500, detail="TTS进程失败")
        



    except Exception as e:
        print(f"Error:{e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/control")
async def control_endpoint(command: str):
    
    control_workflow = tts.Control(TTS_SERVER_ADDR, command)
    response = control_workflow.get()
    
    if command == "restart":
        return {"status": "success", "message": "重启指令已发送"}
    
    if response and response.status_code == 200:
        return {"status": "success", "detail": f"指令 {command} 执行成功"}
    else:
        raise HTTPException(status_code=500, detail="指令执行失败或服务端无响应")


  
@app.get("/set_gpt_weights")
async def set_gpt_weights_endpoint(weights_path: str):
    
    set_gpt_weights_workflow = tts.GPT(TTS_SERVER_ADDR, weights_path)
    response = set_gpt_weights_workflow.get()
    
    if response and response.status_code == 200:
        return {"status": "success", "detail": f"已将GPT模型权重文件路径改为{weights_path}"}
    else:
        raise HTTPException(status_code=500, detail="指令执行失败或服务端无响应")
    

@app.get("/set_sovits_weights")
async def set_sovits_weights_endpoint(weights_path: str):
    
    set_sovits_weights_workflow = tts.Sovits(TTS_SERVER_ADDR, weights_path)
    response = set_sovits_weights_workflow.get()
    
    if response and response.status_code == 200:
        return {"status": "success", "detail": f"已将Sovits模型权重文件路径改为{weights_path}"}
    else:
        raise HTTPException(status_code=500, detail="指令执行失败或服务端无响应")



def run_server(host: str = "0.0.0.0", port: int = 1111):
    print(f"CyberFeng后端服务器启动中 监听{host}:{port}")
    
    uvicorn.run(app, host=host, port=port)
    
if __name__ == "__main__":
    run_server()
# end main
