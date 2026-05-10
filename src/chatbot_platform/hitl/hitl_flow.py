from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from ..models import ExecutionStatus, SessionState

_logger = logging.getLogger(__name__)


class HitlCommand(str):
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    CORRECT = "correct"


class HitlFlow:
    def __init__(self, session: SessionState):
        self.session = session
        self.awaiting_since = datetime.utcnow()

    def request_approval(self, reason: str) -> None:
        self.session.status = ExecutionStatus.AWAITING_HITL
        self.session.memory.metadata["approval_reason"] = reason
        self.session.memory.metadata["requested_at"] = datetime.utcnow().isoformat()
        _logger.info("HITL approval requested: %s", reason)

    def apply_command(self, command: str, payload: Optional[Dict[str, Any]] = None) -> None:
        payload = payload or {}
        _logger.info("HITL command received: %s", command)
        if command == HitlCommand.APPROVE:
            self.session.memory.metadata["approved_at"] = datetime.utcnow().isoformat()
            self.session.status = ExecutionStatus.RUNNING
        elif command == HitlCommand.REJECT:
            self.session.status = ExecutionStatus.FAILED
            self.session.memory.metadata["rejection_reason"] = payload.get("reason", "rejected")
        elif command == HitlCommand.ESCALATE:
            self.session.memory.metadata["escalated"] = True
            self.session.status = ExecutionStatus.AWAITING_HITL
        elif command == HitlCommand.CORRECT:
            self.session.memory.metadata["correction"] = payload
            self.session.status = ExecutionStatus.RUNNING
        else:
            raise ValueError(f"Unknown HITL command: {command}")

    def has_timed_out(self, timeout_seconds: int) -> bool:
        return datetime.utcnow() - self.awaiting_since > timedelta(seconds=timeout_seconds)
