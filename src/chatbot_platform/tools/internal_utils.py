from __future__ import annotations

from typing import Any, Dict

from .tool_adapter import ToolAdapter


class InternalUtilsTool(ToolAdapter):
    @property
    def name(self) -> str:
        return "internal_utils"

    async def run(self, input_payload: Dict[str, Any]) -> Dict[str, Any]:
        action = input_payload.get("action")
        if action == "summarize":
            text = input_payload.get("text", "")
            return {"summary": text[: min(len(text), 320)]}

        if action == "clean":
            payload = input_payload.get("payload", {})
            return {"cleaned": {k: str(v).strip() for k, v in payload.items()}}

        return {"message": "unsupported internal utility action"}
