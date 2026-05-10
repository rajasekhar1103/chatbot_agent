from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    session_id: str
    prompt: str


class HitlCommandRequest(BaseModel):
    command: str
    payload: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    session_id: str
    status: str
    current_node: Optional[str]
    memory: Dict[str, Any]
    nodes: List[Dict[str, Any]]
