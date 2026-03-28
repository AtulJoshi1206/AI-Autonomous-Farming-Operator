from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import shutil

# Importing Multi-Agent Hub
from utils.multi_agent import FarmingMultiAgentSystem
from utils.gemini import generate_what_if
from utils.multilingual import translate_output
from utils.voice import generate_speech_base64

app = FastAPI(title="Autonomous Farming Operator — Multi-Agent Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the multi-agent system
multi_agent = FarmingMultiAgentSystem()

class PipelineInput(BaseModel):
    crop: str
    location: str
    task: Optional[str] = "fertilization"
    soil: Optional[str] = None
    manual_rain: Optional[float] = None
    text_input: Optional[str] = None
    language: Optional[str] = "English"

class WhatIfInput(BaseModel):
    crop: str
    location: str
    task: Optional[str] = "fertilization"
    rain_prob: float
    reason: str
    action: str
    language: Optional[str] = "English"

class TTSInput(BaseModel):
    text: str
    language: str


@app.post("/run")
async def run(data: PipelineInput):
    try:
        result = await multi_agent.run_flow(
            text=data.text_input or "Manual Entry",
            location=data.location,
            crop=data.crop,
            task=data.task,
            soil=data.soil
        )
        
        # Consistent API Response structure for both Full and Awaiting Info flows
        response = {
            "status": result.get("status", "success"),
            "explanation": result["explanation"],
            "weather": result.get("environment", {}).get("current_weather"),
            "forecast": result.get("environment", {}).get("five_day_forecast", []),
            "timeline": result.get("pipeline", {}).get("timeline", []),
            "summary": result.get("pipeline", {}).get("summary", {}),
            "translated_input": result["linguistic"].get("transcription", {})
        }
        
        return response
    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice")
async def voice_input(file: UploadFile = File(...), location: str = Form(None), crop: str = Form(None), soil: str = Form(None)):
    try:
        # Save temp file
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = await multi_agent.run_flow(
            audio_path=temp_path,
            location=location,
            crop=crop,
            soil=soil
        )
        
        os.remove(temp_path)
        
        # Consistent API Response structure
        response = {
            "status": result.get("status", "success"),
            "explanation": result["explanation"],
            "weather": result.get("environment", {}).get("current_weather"),
            "forecast": result.get("environment", {}).get("five_day_forecast", []),
            "timeline": result.get("pipeline", {}).get("timeline", []),
            "summary": result.get("pipeline", {}).get("summary", {}),
            "transcription": result["linguistic"].get("transcription", {})
        }
        
        return response
    except Exception as e:
        print(f"Voice API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts")
async def get_tts(data: TTSInput):
    try:
        audio_b64 = await generate_speech_base64(data.text, data.language)
        return {"audio_base64": audio_b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/what-if")
async def what_if(data: WhatIfInput):
    try:
        result = generate_what_if({
            "crop": data.crop,
            "task": data.task,
            "location": data.location,
            "rain_prob": data.rain_prob,
            "reason": data.reason,
            "action": data.action
        })
        
        if data.language and data.language.lower() != "english":
            result["risk_local"] = translate_output(result.get("risk_en", ""), data.language)
            result["impact_local"] = translate_output(result.get("impact_en", ""), data.language)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
