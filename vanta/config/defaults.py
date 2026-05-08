"""Default configuration values and vanta.toml template."""

DEFAULT_TOML = """\
[project]
name = "my-project"
language = "python"
conventions = "Use type hints everywhere, docstrings for all public functions."
root = "."

[llm]
provider = "groq"
fallback_provider = "gemini"
groq_model = "llama3-70b-8192"
gemini_model = "gemini-1.5-flash"
context_budget = 6000
complexity_threshold = 0.7
temperature = 0.2
max_tokens = 4096

[memory]
enabled = true
chroma_path = ".vanta/chroma"
graph_path = ".vanta/graph.pkl"
chunk_size = 512
chunk_overlap = 64
include_extensions = [".py", ".ts", ".js", ".md", ".toml", ".yaml"]
exclude_patterns = ["**/node_modules/**", "**/__pycache__/**", "**/.venv/**"]
embedding_model = "all-MiniLM-L6-v2"

[tui]
theme = "{theme}"
panel_widths = [20, 55, 25]
show_file_tree = true
show_terminal = true
show_memory_bar = true
max_chat_history = 200

[agent]
max_steps = 50
max_retries = 3
dry_run = false
auto_commit = false
verbose_tools = false
"""
