from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    environment: str = Field("development", env="ENVIRONMENT")
    log_level: str = Field("info", env="LOG_LEVEL")
    tavily_api_key: Optional[str] = Field(None, env="TAVILY_API_KEY")
    tavily_endpoint: str = Field("https://api.tavily.ai/v1/search", env="TAVILY_ENDPOINT")
    memory_store_path: Path = Field(Path("./data/memory_store.json"), env="MEMORY_STORE_PATH")
    session_store_path: Path = Field(Path("./data/session_store.json"), env="SESSION_STORE_PATH")
    mcp_server_port: int = Field(8081, env="MCP_SERVER_PORT")
    max_tool_retries: int = Field(2, env="MAX_TOOL_RETRIES")
    hitl_timeout_seconds: int = Field(300, env="HITL_TIMEOUT_SECONDS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
