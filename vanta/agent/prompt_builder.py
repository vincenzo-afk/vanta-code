"""Prompt builder — assembles system + user prompts from template files."""

from __future__ import annotations

from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts/ directory."""
    path = _PROMPTS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def build_system_prompt(config=None) -> str:
    """Build the full system prompt for the agent."""
    base = load_prompt("system_base.txt")
    if config:
        project_ctx = (
            f"\n\n## Project Context\n"
            f"- Name: {config.project_name}\n"
            f"- Language: {config.language}\n"
            f"- Root: {config.project_root}\n"
        )
        if config.conventions:
            project_ctx += f"- Conventions: {config.conventions}\n"
        return base + project_ctx
    return base


def build_planner_prompt(task: str, config=None) -> str:
    """Build the task planning prompt."""
    template = load_prompt("planner.txt")
    return template.replace("{{TASK}}", task) if template else (
        f"Break down this task into atomic steps:\n\nTask: {task}\n\n"
        "Return a JSON list of steps, each with: description, tool, params, depends_on, estimated_complexity."
    )


def build_reflector_prompt(task: str, results_summary: str) -> str:
    """Build the reflection prompt after executing steps."""
    template = load_prompt("reflector.txt")
    if template:
        return (
            template
            .replace("{{TASK}}", task)
            .replace("{{RESULTS}}", results_summary)
        )
    return (
        f"Original task: {task}\n\n"
        f"Steps completed:\n{results_summary}\n\n"
        "Is the task complete? If not, what steps remain? "
        "Reply with JSON: {\"complete\": true/false, \"next_steps\": [...]}"
    )


def build_debugger_prompt(error_type: str, error_msg: str, code: str) -> str:
    """Build the AutoDebug fix prompt."""
    template = load_prompt("debugger.txt")
    if template:
        return (
            template
            .replace("{{ERROR_TYPE}}", error_type)
            .replace("{{ERROR_MSG}}", error_msg)
            .replace("{{CODE}}", code)
        )
    return (
        f"Fix this {error_type}: {error_msg}\n\nCode:\n```python\n{code}\n```\n"
        "Return ONLY the fixed code block."
    )
