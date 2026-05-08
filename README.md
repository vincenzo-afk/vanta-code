# Vanta Code 🖤

> **The autonomous CLI coding agent with a soul.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is Vanta Code?

Vanta Code is a fully autonomous, terminal-native AI coding agent. It reads your project, understands its structure semantically, plans tasks, executes them with real tools, reflects on outcomes, and retries intelligently — all inside a beautiful Textual TUI.

```
❯ vanta chat
```

---

## Features

| Feature | Description |
|---|---|
| **Autonomous Agent Loop** | Plan → Act → Observe → Reflect with up to 50 steps |
| **Smart LLM Routing** | Auto-routes to Groq (fast) or Gemini (powerful) based on complexity |
| **Memory Brain** | ChromaDB semantic search + NetworkX knowledge graph |
| **8 CLI Commands** | `chat`, `run`, `init`, `plot`, `debug`, `commit`, `search`, `config` |
| **Textual TUI** | 3-panel layout: file tree · chat · terminal |
| **3 Themes** | `classic`, `hacker`, `sakura` — switchable live with `Ctrl+T` |
| **AutoDebug** | Reads tracebacks, generates fixes, applies patches, re-runs tests |
| **AI Commits** | One command to stage, generate a commit message, and push |
| **Inline Charts** | `vanta plot data.csv` renders beautiful terminal charts |

---

## Installation

```bash
# Clone the repo
git clone https://github.com/your-org/vanta-code.git
cd vanta-code

# Install with pip (editable mode)
pip install -e ".[dev]"

# Copy and configure your API keys
cp .env.example .env
# Edit .env — add GROQ_API_KEY and/or GEMINI_API_KEY
```

---

## Quick Start

```bash
# 1. Initialize Vanta Code in your project
cd my-project
vanta init

# 2. Open the interactive TUI
vanta chat

# 3. Run a one-shot task
vanta run "Add docstrings to all public functions in src/"

# 4. Auto-commit with AI message
vanta commit --push

# 5. Debug a traceback
python main.py 2>&1 | vanta debug

# 6. Plot a CSV
vanta plot metrics.csv --type line --title "Accuracy"
```

---

## CLI Commands

```
vanta init        Initialize Vanta Code (index codebase, create vanta.toml)
vanta chat        Launch the full Textual TUI
vanta run <task>  Run a one-shot task non-interactively
vanta plot <file> Render a terminal chart from CSV/JSON
vanta debug       Read a traceback and auto-fix it
vanta commit      Stage + AI commit message + optional push
vanta search <q>  Search docs and summarize
vanta config      View/edit vanta.toml settings
```

---

## TUI Keyboard Shortcuts

| Key | Action |
|---|---|
| `Enter` | Send message / execute task |
| `Ctrl+T` | Cycle through themes |
| `Ctrl+Q` | Quit |
| `Ctrl+F` | Focus file tree |
| `Ctrl+L` | Clear chat |
| `F2` | Toggle terminal panel |
| `↑ / ↓` | Navigate input history |
| `Ctrl+K` | Show shortcuts |

### Slash Commands (in TUI)
```
/help        Show all commands
/clear       Clear chat history
/plan        Show the current execution plan
/theme <n>   Switch theme: classic | hacker | sakura
/exit        Quit
```

---

## Configuration (`vanta.toml`)

```toml
[project]
name = "my-project"
language = "python"
conventions = "Use type hints, docstrings for public APIs."

[llm]
provider = "groq"               # groq | gemini
groq_model = "llama3-70b-8192"
gemini_model = "gemini-1.5-flash"
complexity_threshold = 0.7      # Tasks above this use Gemini

[memory]
enabled = true
chroma_path = ".vanta/chroma"

[tui]
theme = "classic"               # classic | hacker | sakura

[agent]
max_steps = 50
dry_run = false
auto_commit = false
```

---

## Architecture

```
vanta/
├── agent/          # Plan → Act → Observe → Reflect loop
│   ├── loop.py     # AgentLoop (main orchestrator)
│   ├── planner.py  # Task → PlanSteps decomposition
│   ├── executor.py # Tool dispatch (parallel-aware)
│   └── reflector.py # Post-action self-evaluation
├── llm/
│   ├── router.py   # Complexity-based model routing
│   ├── groq_client.py
│   └── gemini_client.py
├── memory/
│   ├── indexer.py  # File walker + chunker + embedder
│   ├── chroma_store.py # ChromaDB wrapper
│   ├── graph.py    # NetworkX knowledge graph
│   └── retriever.py # Unified query interface
├── tools/          # 15+ agent-callable tools
├── tui/            # Textual 3-panel UI + 3 themes
├── cli/            # Typer CLI (8 commands)
└── config/         # vanta.toml loader + Pydantic schema
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key (required for Groq) |
| `GEMINI_API_KEY` | Google Gemini API key (required for Gemini) |
| `VANTA_GROQ_MODEL` | Override Groq model name |
| `VANTA_GEMINI_MODEL` | Override Gemini model name |
| `VANTA_LOG_LEVEL` | Log level: DEBUG / INFO / WARNING |
| `VANTA_LOG_FILE` | Path to log file |
| `VANTA_SEARXNG_URL` | Custom SearXNG instance for web search |

---

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check vanta/

# Type check
mypy vanta/
```

---

## License

MIT — see [LICENSE](LICENSE).
