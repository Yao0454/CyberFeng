import os
import uuid
from pathlib import Path

import psutil
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

import lib.tts as tts
from src.CyberFeng import CyberFeng, CyberFengData


class ChatRequest(BaseModel):
    message: str


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
async def chat_endpoint(request: Request):
    count: int = 0
    if os.environ.get("NO_PROXY"):
        os.environ["NO_PROXY"] += ",127.0.0.1"
    else:
        os.environ["NO_PROXY"] = "127.0.0.1"
    try:
        # 保存上传到服务器的音频文件
        audio_data = await request.body()
        count += 1
        file_name = f"upload{count}"

        file_path: Path = UPLOAD_DIR / file_name

        with file_path.open("wb") as buffer:
            buffer.write(audio_data)
        print(f"成功收到音频文件{file_path}")

        cf.choose_audio(file_path).stt().llm().tts()

        if not cfdata.output_audio_path:
            raise RuntimeError("过程错误！")

        output_audio_path = cfdata.output_audio_path

        if output_audio_path and Path(output_audio_path).exists():
            return FileResponse(
                output_audio_path, media_type="audio/mpeg", filename="reply.mp3"
            )
        else:
            raise HTTPException(status_code=500, detail="进程失败")

    except Exception as e:
        print(f"Error:{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/text")
async def text_endpoint(req: ChatRequest):
    if os.environ.get("NO_PROXY"):
        os.environ["NO_PROXY"] += ",127.0.0.1"
    else:
        os.environ["NO_PROXY"] = "127.0.0.1"

    try:
        cfdata.filename = f"text_{uuid.uuid4().hex}"
        cfdata.transfered_text = req.message
        cf.llm().tts()

        filename = Path(cfdata.output_audio_path).name

        file_url = f"{cfdata.base_url}/audio/{filename}"
        return {"reply": cfdata.llm_response, "audio_url": file_url}

    except Exception as e:
        print(f"Error:{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    file_path = RESPONCE_DIR / filename
    if file_path.exists():
        media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
        return FileResponse(file_path, media_type=media_type, filename=filename)
    raise HTTPException(status_code=404, detail="文件不存在")


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
        "model": cf.llm_service.model_path,
        "cpu": psutil.cpu_percent(interval=0.5),
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
