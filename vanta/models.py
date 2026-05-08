"""All Pydantic v2 data models used throughout Vanta Code."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MessageRole(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"


# ---------------------------------------------------------------------------
# Conversation / Session Models
# ---------------------------------------------------------------------------

class AgentMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v


class ToolCall(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool: str  # Must match a key in TOOL_REGISTRY
    params: dict[str, Any] = Field(default_factory=dict)
    step_id: str | None = None  # Links to planner step
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ToolResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_call_id: str | None = None  # Links to the ToolCall
    success: bool
    output: str
    error: str | None = None
    duration_ms: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Memory / Indexing Models
# ---------------------------------------------------------------------------

class CodeChunk(BaseModel):
    id: str  # Unique ID for ChromaDB
    file: str  # Relative file path
    start_line: int
    end_line: int
    content: str
    language: str
    embedding: list[float] | None = None


class CodebaseIndex(BaseModel):
    project_root: str
    total_files: int
    total_chunks: int
    languages: dict[str, int]  # {language: file_count}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Config Models
# ---------------------------------------------------------------------------

class LLMConfig(BaseModel):
    provider: str = "groq"
    fallback_provider: str = "gemini"
    groq_model: str = "llama3-70b-8192"
    gemini_model: str = "gemini-1.5-flash"
    context_budget: int = 6000
    complexity_threshold: float = 0.7
    temperature: float = 0.2
    max_tokens: int = 4096


class MemoryConfig(BaseModel):
    enabled: bool = True
    chroma_path: str = ".vanta/chroma"
    graph_path: str = ".vanta/graph.pkl"
    chunk_size: int = 512
    chunk_overlap: int = 64
    include_extensions: list[str] = Field(
        default_factory=lambda: [".py", ".ts", ".js", ".rs", ".go", ".md", ".toml", ".yaml"]
    )
    exclude_patterns: list[str] = Field(
        default_factory=lambda: [
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/.venv/**",
            "**/dist/**",
            "**/.git/**",
        ]
    )
    embedding_model: str = "all-MiniLM-L6-v2"


class TUIConfig(BaseModel):
    theme: str = "classic"
    panel_widths: list[int] = Field(default_factory=lambda: [20, 55, 25])
    show_file_tree: bool = True
    show_terminal: bool = True
    show_memory_bar: bool = True
    max_chat_history: int = 200


class AgentConfig(BaseModel):
    max_steps: int = 50
    max_retries: int = 3
    dry_run: bool = False
    auto_commit: bool = False
    verbose_tools: bool = False


class VantaConfig(BaseModel):
    project_name: str = "project"
    project_root: str = "."
    language: str = "python"
    conventions: str = ""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    tui: TUIConfig = Field(default_factory=TUIConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    dry_run: bool = False  # Global override


# ---------------------------------------------------------------------------
# Agent Planning Models
# ---------------------------------------------------------------------------

class PlanStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    tool: str
    params: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    estimated_complexity: str = "medium"  # low | medium | high
    can_parallelize: bool = False
    status: str = "pending"  # pending | running | done | failed


class SessionState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    history: list[AgentMessage] = Field(default_factory=list)
    results: list[ToolResult] = Field(default_factory=list)
    current_plan: list[PlanStep] = Field(default_factory=list)
    task: str = ""
    is_complete: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Plot / Debug Models
# ---------------------------------------------------------------------------

class PlotRequest(BaseModel):
    data: list[float] | list[list[float]]
    chart_type: str = "line"  # line | bar | scatter | hist
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    width: int = 80
    height: int = 24


class DebugAttempt(BaseModel):
    attempt_number: int
    error_type: str
    error_message: str
    file: str | None
    line: int | None
    fix_applied: str | None
    tests_passed: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
