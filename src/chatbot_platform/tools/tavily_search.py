from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from .tool_adapter import ToolAdapter, ToolExecutionError
from ..config import settings

_logger = logging.getLogger(__name__)


class TavilySearchTool(ToolAdapter):
    @property
    def name(self) -> str:
        return "tavily_search"

    async def run(self, input_payload: Dict[str, Any]) -> Dict[str, Any]:
        query = input_payload.get("query")
        if not query:
            raise ToolExecutionError("query is required")

        headers = {
            "Authorization": f"Bearer {settings.tavily_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.tavily_endpoint,
                json={"query": query, "max_results": input_payload.get("max_results", 5)},
                headers=headers,
            )
            if response.status_code != 200:
                _logger.error("Tavily search failed: %s", response.text)
                raise ToolExecutionError(f"Search API responded with {response.status_code}")
            result = response.json()
            return {"results": result}
