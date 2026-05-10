from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..graph.state_graph import StateGraph
from ..models import ExecutionStatus, SessionState, StateNode, ToolCall
from ..tools.tool_adapter import ToolAdapter, ToolExecutionError

_logger = logging.getLogger(__name__)


class AgentWorkflow:
    def __init__(self, session: SessionState, tools: List[ToolAdapter]):
        self.state_graph = StateGraph(session=session)
        self.tools = {tool.name: tool for tool in tools}

    async def run(self, prompt: str) -> SessionState:
        node = self.state_graph.add_node(node_id="agent_root", label="agent_root", inputs={"prompt": prompt})
        self.state_graph.set_current_node(node.node_id)
        self.state_graph.start_node(node.node_id)

        try:
            reasoning = self.generate_reasoning(prompt)
            tool_calls = await self.process_tool_calls(reasoning)
            output = {"reasoning": reasoning, "tool_calls": [call.model_dump() for call in tool_calls]}
            self.state_graph.complete_node(node.node_id, output=output)
            self.state_graph.session.status = ExecutionStatus.COMPLETED
        except Exception as exc:
            self.state_graph.fail_node(node.node_id, str(exc))
            raise

        return self.state_graph.session

    def generate_reasoning(self, prompt: str) -> str:
        return f"Analyzing prompt and preparing tool actions for: {prompt[:120]}"

    async def process_tool_calls(self, reasoning: str) -> List[ToolCall]:
        tool_calls: List[ToolCall] = []
        if "search" in reasoning.lower():
            tool_calls.append(ToolCall(tool_name="tavily_search", input_payload={"query": reasoning}))
        else:
            tool_calls.append(ToolCall(tool_name="internal_utils", input_payload={"action": "summarize", "text": reasoning}))

        for tool_call in tool_calls:
            tool_call.status = ExecutionStatus.RUNNING
            try:
                tool = self.tools[tool_call.tool_name]
                result = await tool.run(tool_call.input_payload)
                tool_call.output_payload = result
                tool_call.status = ExecutionStatus.COMPLETED
            except ToolExecutionError as exc:
                tool_call.status = ExecutionStatus.FAILED
                tool_call.output_payload = {"error": str(exc)}
                _logger.error("Tool execution failed for %s: %s", tool_call.tool_name, exc)
            except Exception as exc:
                tool_call.status = ExecutionStatus.FAILED
                tool_call.output_payload = {"error": str(exc)}
                _logger.exception("Unexpected tool execution error")
            finally:
                tool_calls.append(tool_call)

        return tool_calls
