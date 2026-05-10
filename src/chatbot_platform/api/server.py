from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import EventSourceResponse

from ..agents.agent_workflow import AgentWorkflow
from ..config import settings
from ..hitl.hitl_flow import HitlCommand, HitlFlow
from ..models import ConversationMemory, ExecutionStatus, SessionState
from ..persistence import memory_saver
from ..streaming.observability import ObservabilityStream
from ..tools.internal_utils import InternalUtilsTool
from ..tools.tavily_search import TavilySearchTool
from .schemas import CreateSessionRequest, HitlCommandRequest, SessionResponse

_logger = logging.getLogger(__name__)

app = FastAPI(title="Chatbot Orchestration API")
stream = ObservabilityStream()
sessions: Dict[str, SessionState] = {}


def build_session(session_id: str, prompt: str) -> SessionState:
    memory = ConversationMemory(session_id=session_id, history=[{"role": "system", "content": prompt}])
    return SessionState(session_id=session_id, memory=memory)


def serialize_session(session: SessionState) -> SessionResponse:
    return SessionResponse(
        session_id=session.session_id,
        status=session.status.value,
        current_node=session.current_node,
        memory=session.memory.model_dump(),
        nodes=[node.model_dump() for node in session.nodes],
    )


@app.on_event("startup")
async def startup_event() -> None:
    logging.getLogger().setLevel(settings.log_level.upper())
    _logger.info("Chatbot orchestration API starting in %s mode", settings.environment)


@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest) -> SessionResponse:
    if request.session_id in sessions:
        raise HTTPException(status_code=409, detail="Session already exists")

    session = build_session(request.session_id, request.prompt)
    sessions[session.session_id] = session
    memory_saver.set(session.session_id, session.model_dump())
    await stream.emit("session.created", {"session_id": session.session_id})
    return serialize_session(session)


@app.post("/sessions/{session_id}/run", response_model=SessionResponse)
async def run_session(session_id: str) -> SessionResponse:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    tools = [TavilySearchTool(), InternalUtilsTool()]
    workflow = AgentWorkflow(session=session, tools=tools)
    try:
        await workflow.run(prompt=session.memory.history[0]["content"])
        sessions[session_id] = workflow.state_graph.session
        memory_saver.set(session_id, workflow.state_graph.session.model_dump())
        await stream.emit("session.updated", {"session_id": session_id, "status": session.status.value})
        return serialize_session(workflow.state_graph.session)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/sessions/{session_id}/hitl", response_model=SessionResponse)
async def hitl_command(session_id: str, command_request: HitlCommandRequest) -> SessionResponse:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    flow = HitlFlow(session=session)
    if command_request.command not in (HitlCommand.APPROVE, HitlCommand.REJECT, HitlCommand.ESCALATE, HitlCommand.CORRECT):
        raise HTTPException(status_code=400, detail="Unknown HITL command")

    flow.apply_command(command_request.command, payload=command_request.payload)
    sessions[session_id] = session
    memory_saver.set(session_id, session.model_dump())
    await stream.emit("hitl.command", {"session_id": session_id, "command": command_request.command})
    return serialize_session(session)


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return serialize_session(session)


@app.get("/events")
async def events(request: Request) -> EventSourceResponse:
    async def event_generator() -> asyncio.AsyncIterator[str]:
        async for event in stream.listen():
            if await request.is_disconnected():
                break
            yield f"event: {event['type']}\ndata: {event['payload']}\n\n"

    return EventSourceResponse(event_generator())
