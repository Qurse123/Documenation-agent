import asyncio
import uuid
from typing import Literal

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.agent import DocAgent

app = FastAPI(title="Doc Agent API")

app.add_middleware( ## Middleware is code that runs before and after every request 
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization"],
)

agent = DocAgent(screenshot_interval=5.0) ## new instance of the docagent class
_state: Literal["idle", "recording", "generating", "ready"] = "idle" ## sets the state as these exact strings and sets state as idle
_session_id: str = "" 
_result: dict = {}


# --- Response models ---

class StartSessionResponse(BaseModel): ## BaseModel validates types, converts to JSON if needed and ensures required fields exist. This is a class from pydantic which we can inherit from
    session_id: str

class StopSessionResponse(BaseModel):
    message: str

class StatusResponse(BaseModel):
    state: Literal["idle", "recording", "generating", "ready"]

class ResultResponse(BaseModel):
    notion_url: str
    documentation_markdown: str


# --- Background task ---

async def _run_stop():
    global _state, _result
    try:
        state = await agent.stop()
        _result = {
            "notion_url": state.get("notion_page_url", ""),
            "documentation_markdown": state.get("documentation", ""),
        }
        _state = "ready"
    except Exception:
        _state = "idle"
        raise


# --- Endpoints ---

@app.post("/session/start", response_model=StartSessionResponse) ## the decorator tells FASTAPI that when a post request is sent to session/start run the function start_session 
## the response model tells fastapi how we expect the structure of the response followed StartSessionResponse
async def start_session():
    global _state, _session_id
    if _state == "recording":
        raise HTTPException(status_code=409, detail="Session already recording") ## 409 means a conflict  
    await agent.start() ## calls the Doc Agents start method
    _state = "recording"
    _session_id = str(uuid.uuid4())
    return StartSessionResponse(session_id=_session_id)


@app.post("/session/stop", response_model=StopSessionResponse)
async def stop_session(background_tasks: BackgroundTasks):
    global _state
    if _state != "recording":
        raise HTTPException(status_code=400, detail="No active recording session")
    _state = "generating"
    background_tasks.add_task(_run_stop)
    return StopSessionResponse(message="Stopping session and generating documentation")


@app.get("/session/status", response_model=StatusResponse)
async def get_status():
    return StatusResponse(state=_state)


@app.get("/session/result", response_model=ResultResponse)
async def get_result():
    if _state != "ready":
        raise HTTPException(status_code=404, detail="Result not ready yet")
    return ResultResponse(**_result) ## ** unpacks dictionaries and * unpacks lists and tuples 
