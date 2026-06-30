import os
import uuid
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Optional

from google.adk.runners import Runner
from google.adk.cli.utils.service_factory import (
    create_session_service_from_options,
    create_artifact_service_from_options,
    create_memory_service_from_options
)
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

from app.agent import app as adk_app

# Setup logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CustomBridgeServer")

app = FastAPI(title="Research Navigator AI - Premium Bridge Server")

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ADK Services
agents_dir = "app"
session_service = create_session_service_from_options(base_dir=agents_dir)
artifact_service = create_artifact_service_from_options(base_dir=agents_dir)
memory_service = create_memory_service_from_options(base_dir=agents_dir)
credential_service = InMemoryCredentialService()

runner = Runner(
    app=adk_app,
    session_service=session_service,
    artifact_service=artifact_service,
    memory_service=memory_service,
    credential_service=credential_service,
    auto_create_session=True
)

class RunMessagePart(BaseModel):
    text: Optional[str] = None
    function_response: Optional[Any] = None

class RunMessage(BaseModel):
    role: str
    parts: list[RunMessagePart]

class RunAgentRequest(BaseModel):
    app_name: str = "app"
    user_id: str = "user"
    session_id: str
    invocation_id: Optional[str] = None
    new_message: Optional[RunMessage] = None
    streaming: bool = True

@app.post("/apps/app/users/user/sessions")
async def create_session():
    session_id = str(uuid.uuid4())
    session = await session_service.get_session(app_name="app", user_id="user", session_id=session_id)
    if not session:
        session = await session_service.create_session(
            app_name="app",
            user_id="user",
            session_id=session_id
        )
    return {"id": session.id, "session_id": session.id}

@app.post("/run_sse")
async def run_agent_sse(req: RunAgentRequest):
    new_msg_payload = None
    if req.new_message and req.new_message.parts:
        parts_payload = []
        for p in req.new_message.parts:
            if p.function_response:
                fr = p.function_response
                parts_payload.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fr.get("name"),
                            id=fr.get("id"),
                            response=fr.get("response")
                        )
                    )
                )
            elif p.text:
                parts_payload.append(types.Part.from_text(text=p.text))
        new_msg_payload = types.Content(role=req.new_message.role, parts=parts_payload)

    async def sse_event_generator():
        try:
            async for event in runner.run_async(
                user_id=req.user_id,
                session_id=req.session_id,
                invocation_id=req.invocation_id,
                new_message=new_msg_payload,
                run_config=RunConfig(streaming_mode=StreamingMode.SSE)
            ):
                fn_calls = [c.name for c in event.get_function_calls()] if event.get_function_calls() else []
                fn_responses = [r.name for r in event.get_function_responses()] if event.get_function_responses() else []
                
                event_dict = {
                    "node_name": event.node_name,
                    "partial": event.partial,
                    "invocation_id": event.invocation_id,
                    "get_function_calls": fn_calls,
                    "get_function_responses": fn_responses,
                }
                if event.content and event.content.parts:
                    event_dict["content"] = {
                        "parts": [{"text": p.text} for p in event.content.parts if p.text]
                    }
                
                import json
                yield f"data: {json.dumps(event_dict)}\n\n"
        except Exception as e:
            logger.exception("Error in custom server sse_event_generator:")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(sse_event_generator(), media_type="text/event-stream")

# Serve React static assets
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return {"status": "Backend running. Please build the frontend (npm run build) to serve it here."}
