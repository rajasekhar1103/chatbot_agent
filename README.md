# Chatbot Platform

A production-grade AI orchestration platform built with Python, LangGraph, LangChain, and FastAPI.

## Architecture

- `StateGraph` manages conversational state, node execution, and transitions.
- `MemorySaver` persists long-term conversational memory and recovery state.
- ReAct-style agent workflows support reasoning, tool calling, and iterative decision-making.
- `ToolNode` adapters allow external search, internal utilities, and MCP tool servers.
- HITL workflows support interrupt, approval, correction, and escalation.
- Streaming observability exposes state updates, streamed values, and execution traces.

## Features

- Stateful multi-agent orchestration
- Persistent session management
- Retrieval-augmented tool use
- Approval workflow and CLI/HITL review path
- Real-time streaming and execution tracing
- Docker-ready backend deployment

## Setup

1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and configure your API keys.

3. Run the API server:
   ```bash
   uvicorn chatbot_platform.api.server:app --reload
   ```

## Development

- `src/chatbot_platform/config.py` for environment-based configuration.
- `src/chatbot_platform/graph/state_graph.py` for the core workflow engine.
- `src/chatbot_platform/persistence.py` for persistent memory and checkpointing.
- `src/chatbot_platform/agents/agent_workflow.py` for agent execution.
- `src/chatbot_platform/tools/` for tool adapters.
- `src/chatbot_platform/mcp/server.py` for MCP tool server scaffolding.
- `src/chatbot_platform/hitl/hitl_flow.py` for human-in-the-loop workflows.
- `src/chatbot_platform/streaming/observability.py` for streaming events.

## Docker

Build and run the service with Docker:

```bash
docker compose up --build
```

## Example Workflows

- Autonomous tool use
- External MCP tool execution
- HITL approval flow
- Streaming state updates
