from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_HITL = "awaiting_hitl"


class ToolCall(BaseModel):
    tool_name: str
    input_payload: Dict[str, Any]
    output_payload: Optional[Dict[str, Any]] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ConversationMemory(BaseModel):
    session_id: str
    history: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StateNode(BaseModel):
    node_id: str
    label: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    trace: List[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class SessionState(BaseModel):
    session_id: str
    nodes: List[StateNode] = Field(default_factory=list)
    memory: ConversationMemory
    current_node: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
