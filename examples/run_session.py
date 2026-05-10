import asyncio

from chatbot_platform.api.server import app


async def main() -> None:
    print("This example illustrates how to call the FastAPI endpoints for session orchestration.")
    print("Run the service with: uvicorn chatbot_platform.api.server:app --reload")
    print("Then POST /sessions and POST /sessions/{session_id}/run to execute a workflow.")


if __name__ == "__main__":
    asyncio.run(main())
