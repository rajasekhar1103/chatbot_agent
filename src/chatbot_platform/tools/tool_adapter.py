from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class ToolAdapter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def run(self, input_payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class ToolExecutionError(Exception):
    pass
