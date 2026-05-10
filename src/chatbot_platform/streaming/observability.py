from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncIterator, Dict

_logger = logging.getLogger(__name__)


class StateStreamEvent:
    def __init__(self, event_type: str, payload: Dict[str, Any]) -> None:
        self.event_type = event_type
        self.payload = payload

    def to_json(self) -> Dict[str, Any]:
        return {"type": self.event_type, "payload": self.payload}


class ObservabilityStream:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[StateStreamEvent] = asyncio.Queue()

    async def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        event = StateStreamEvent(event_type=event_type, payload=payload)
        await self.queue.put(event)
        _logger.debug("Emitted observability event: %s", event_type)

    async def listen(self) -> AsyncIterator[Dict[str, Any]]:
        while True:
            event = await self.queue.get()
            yield event.to_json()
            self.queue.task_done()
