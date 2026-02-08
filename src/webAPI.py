import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

import lib.tts as tts
from lib.llm import LLM
from lib.stt import STT

app = FastAPI(title="CyberFeng")

UPLOAD_DIR = Path.cwd() / "audio" / "raw"
RESPONCE_DIR = Path.cwd() / "audio" / "trans"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESPONCE_DIR.mkdir(parents=True, exist_ok=True)

TTS_SERVER_ADDR = "http://36.103.177.158:9880"
REF_AUDIO_PATH = "reference_voice/reference.wav"
REF_TEXT = "就是学习函数可能的输出，在这个例子里"


@dataclass
class WorkFlows:
    stt: STT
    llm: LLM


def pre_work(
    model_path: str = "Qwen/Qwen2.5-1.5B-Instruct",
) -> bool:
    workflows = WorkFlows(stt=STT(), llm=LLM(model_path))
    workflows.stt.load_model()
    workflows.llm.load_model()

    if not (workflows.stt.get_model_status and workflows.llm.get_model_status):
        return False
    app.state.workflows = workflows
    return True


def get_workflows() -> WorkFlows:
    if not hasattr(app.state, "workflows"):
        raise RuntimeError("workflows 没有被正确初始化")
    return cast(WorkFlows, app.state.workflows)


def stop_service() -> bool:
    workflows = get_workflows()
    workflows.stt.unload_model()
    workflows.llm.unload_model()
    return not workflows.stt.get_model_status and not workflows.llm.get_model_status


@app.post("/chat")
async def chat_endpoint(file: UploadFile = File(...)):
    workflows: WorkFlows = get_workflows()
    llm: LLM = workflows.llm
    stt: STT = workflows.stt

    try:
        # 保存上传到服务器的音频文件
        file_location = UPLOAD_DIR / (file.filename or "")

        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"成功收到音频文件{file_location}")

        convert_text, filename = stt.process_audio(str(file_location))
        output_text: str | None = llm.get_response(convert_text, filename)

        tts_workflow: tts.Infer = tts.Infer(
            _api_addr=TTS_SERVER_ADDR,
            _text=str(output_text),
            _text_lang="zh",
            _ref_audio_path=REF_AUDIO_PATH,
            _prompt_lang="zh",
            _prompt_text=REF_TEXT,
        )
        output_audio_path = tts_workflow.save_audio(filename)

        if output_audio_path and Path(output_audio_path).exists():
            return FileResponse(
                output_audio_path, media_type="audio/wav", filename="reply.wav"
            )
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


def run_server(host: str = "0.0.0.0", port: int = 1111):
    print(f"CyberFeng后端服务器启动中 监听{host}:{port}")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
# end main
