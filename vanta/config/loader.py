"""Load and validate vanta.toml + .env into a VantaConfig instance."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from vanta.models import (
    AgentConfig,
    LLMConfig,
    MemoryConfig,
    TUIConfig,
    VantaConfig,
)

# Load .env from cwd or parent dirs
load_dotenv()


def load_config(toml_path: str | None = None) -> VantaConfig:
    """
    Load vanta.toml (if present) and merge with env-var overrides.

    Args:
        toml_path: explicit path to a vanta.toml. If None, searches cwd + parents.

    Returns:
        VantaConfig instance with all fields populated.
    """
    raw: dict = {}

    if toml_path:
        path = Path(toml_path)
    else:
        path = _find_toml()

    if path and path.exists():
        if sys.version_info >= (3, 11):
            import tomllib

            with open(path, "rb") as f:
                raw = tomllib.load(f)
        else:
            try:
                import tomli as tomllib  # type: ignore[import]

                with open(path, "rb") as f:
                    raw = tomllib.load(f)
            except ImportError:
                raw = {}

    # Build sub-configs
    proj = raw.get("project", {})
    llm_raw = raw.get("llm", {})
    mem_raw = raw.get("memory", {})
    tui_raw = raw.get("tui", {})
    agent_raw = raw.get("agent", {})

    llm_cfg = LLMConfig(
        provider=llm_raw.get("provider", "groq"),
        fallback_provider=llm_raw.get("fallback_provider", "gemini"),
        groq_model=os.getenv("VANTA_GROQ_MODEL", llm_raw.get("groq_model", "llama3-70b-8192")),
        gemini_model=os.getenv(
            "VANTA_GEMINI_MODEL", llm_raw.get("gemini_model", "gemini-1.5-flash")
        ),
        context_budget=int(llm_raw.get("context_budget", 6000)),
        complexity_threshold=float(llm_raw.get("complexity_threshold", 0.7)),
        temperature=float(llm_raw.get("temperature", 0.2)),
        max_tokens=int(llm_raw.get("max_tokens", 4096)),
    )

    mem_cfg = MemoryConfig(
        enabled=bool(mem_raw.get("enabled", True)),
        chroma_path=mem_raw.get("chroma_path", ".vanta/chroma"),
        graph_path=mem_raw.get("graph_path", ".vanta/graph.pkl"),
        chunk_size=int(mem_raw.get("chunk_size", 512)),
        chunk_overlap=int(mem_raw.get("chunk_overlap", 64)),
        include_extensions=mem_raw.get(
            "include_extensions", [".py", ".ts", ".js", ".md", ".toml", ".yaml"]
        ),
        exclude_patterns=mem_raw.get(
            "exclude_patterns",
            ["**/node_modules/**", "**/__pycache__/**", "**/.venv/**"],
        ),
        embedding_model=mem_raw.get("embedding_model", "all-MiniLM-L6-v2"),
    )

    tui_cfg = TUIConfig(
        theme=tui_raw.get("theme", "classic"),
        panel_widths=tui_raw.get("panel_widths", [20, 55, 25]),
        show_file_tree=bool(tui_raw.get("show_file_tree", True)),
        show_terminal=bool(tui_raw.get("show_terminal", True)),
        show_memory_bar=bool(tui_raw.get("show_memory_bar", True)),
        max_chat_history=int(tui_raw.get("max_chat_history", 200)),
    )

    agent_cfg = AgentConfig(
        max_steps=int(agent_raw.get("max_steps", 50)),
        max_retries=int(agent_raw.get("max_retries", 3)),
        dry_run=bool(agent_raw.get("dry_run", False)),
        auto_commit=bool(agent_raw.get("auto_commit", False)),
        verbose_tools=bool(agent_raw.get("verbose_tools", False)),
    )

    project_root = str(Path(proj.get("root", ".")).resolve())

    return VantaConfig(
        project_name=proj.get("name", "project"),
        project_root=project_root,
        language=proj.get("language", "python"),
        conventions=proj.get("conventions", ""),
        llm=llm_cfg,
        memory=mem_cfg,
        tui=tui_cfg,
        agent=agent_cfg,
        dry_run=bool(agent_raw.get("dry_run", False)),
    )


def _find_toml() -> Path | None:
    """Walk up from cwd to find vanta.toml."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        candidate = parent / "vanta.toml"
        if candidate.exists():
            return candidate
    return None
