import os
import shutil
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

import lib.tts as tts
from src.CyberFeng import CyberFeng, CyberFengData

app = FastAPI(title="CyberFeng")

UPLOAD_DIR = Path.cwd() / "audio" / "raw"
RESPONCE_DIR = Path.cwd() / "audio" / "trans"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESPONCE_DIR.mkdir(parents=True, exist_ok=True)

TTS_SERVER_ADDR = "http://127.0.0.1:9880"
REF_AUDIO_PATH = "reference_voice/reference.wav"
REF_TEXT = "就是学习函数可能的输出，在这个例子里"


cfdata: CyberFengData = CyberFengData()
cf: CyberFeng = CyberFeng(cfdata)


@app.post("/chat")
async def chat_endpoint(file: UploadFile = File(...)):
    if os.environ.get("NO_PROXY"):
        os.environ["NO_PROXY"] += ",127.0.0.1"
    else:
        os.environ["NO_PROXY"] = "127.0.0.1"
    try:
        # 保存上传到服务器的音频文件
        file_location = UPLOAD_DIR / (file.filename or "")

        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"成功收到音频文件{file_location}")

        cf.choose_audio(file).stt().llm().tts()

        if not cfdata.output_audio_path:
            raise RuntimeError("过程错误！")

        output_audio_path = cfdata.output_audio_path

        if output_audio_path and Path(output_audio_path).exists():
            return FileResponse(
                output_audio_path, media_type="audio/wav", filename="reply.wav"
            )
        else:
            raise HTTPException(status_code=500, detail="进程失败")

    except Exception as e:
        print(f"Error:{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/text")
async def text_endpoint(text: str):
    if os.environ.get("NO_PROXY"):
        os.environ["NO_PROXY"] += ",127.0.0.1"
    else:
        os.environ["NO_PROXY"] = "127.0.0.1"

    try:
        cfdata.transfered_text = text
        cf.llm()

        return {"reply": cfdata.llm_response}

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

    print(
        f"DEBUG: response={response}, status={response.status_code if response else 'None'}, body={response.text if response else 'None'}"
    )

    if response and response.status_code == 200:
        return {
            "status": "success",
            "detail": f"已将GPT模型权重文件路径改为{weights_path}",
        }
    else:
        raise HTTPException(status_code=500, detail="指令执行失败或服务端无响应")


@app.get("/set_sovits_weights")
async def set_sovits_weights_endpoint(weights_path: str):
    set_sovits_weights_workflow = tts.Sovits(TTS_SERVER_ADDR, weights_path)
    response = set_sovits_weights_workflow.get()

    if response and response.status_code == 200:
        return {
            "status": "success",
            "detail": f"已将Sovits模型权重文件路径改为{weights_path}",
        }
    else:
        raise HTTPException(status_code=500, detail="指令执行失败或服务端无响应")


@app.get("/status")
async def get_status() -> dict:
    return {
        "status": "online",
        "stt": str(cf.stt_service.get_model_status),
        "llm": str(cf.llm_service.get_model_status),
    }


def run_server(host: str = "0.0.0.0", port: int = 1111):
    cf.start_service()

    if not cf.get_status:
        raise RuntimeError("模型启动失败！")

    print(f"CyberFeng后端服务器启动中 监听{host}:{port}")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
# end main
