from __future__ import annotations

import json
import logging
from pathlib import Path
from threading import Lock
from typing import Any, Dict

from pydantic import BaseModel

from .config import settings

_logger = logging.getLogger(__name__)


class MemorySaver(BaseModel):
    file_path: Path = settings.memory_store_path
    lock: Lock = Lock()
    state: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True

    def initialize(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if self.file_path.exists():
            try:
                with self.file_path.open("r", encoding="utf-8") as handle:
                    self.state = json.load(handle)
                _logger.info("Loaded memory state from %s", self.file_path)
            except (json.JSONDecodeError, OSError) as exc:
                _logger.warning("Could not load memory state: %s", exc)
                self.state = {}
        else:
            self.state = {}

    def save(self) -> None:
        with self.lock:
            try:
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                with self.file_path.open("w", encoding="utf-8") as handle:
                    json.dump(self.state, handle, indent=2)
                _logger.debug("Memory state checkpointed to %s", self.file_path)
            except OSError as exc:
                _logger.error("Failed to persist memory state: %s", exc)

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self.lock:
            self.state[key] = value
            self.save()

    def update(self, values: Dict[str, Any]) -> None:
        with self.lock:
            self.state.update(values)
            self.save()


memory_saver = MemorySaver()
memory_saver.initialize()
