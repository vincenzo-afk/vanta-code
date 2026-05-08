"""Git tools: git_commit, git_status, git_diff."""

from __future__ import annotations

from vanta.tools.registry import tool


@tool("git_commit", "Stage files and commit with an AI-generated message.")
async def git_commit(
    message: str | None = None,
    files: list | None = None,
    config=None,
    state=None,
) -> str:
    """
    Stage all changed files and create a git commit.
    If message is None, the LLM generates one from the diff.

    Args:
        message: Commit message. If None, AI generates one.
        files: Files to stage. If None, stages all changes.

    Returns:
        Commit hash + message, or dry-run notice.
    """
    from git import Repo, InvalidGitRepositoryError

    try:
        repo = Repo(config.project_root if config else ".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise RuntimeError("Not a git repository. Run 'git init' first.")

    if files:
        repo.index.add(files)
    else:
        repo.git.add("-A")

    if not message:
        diff = repo.git.diff("--cached")
        if not diff.strip():
            return "Nothing to commit — working tree clean."
        from vanta.llm.router import route_query

        message = await route_query(
            task=f"Write a concise git commit message (imperative mood, <72 chars) for this diff:\n{diff[:3000]}",
            complexity="low",
            config=config,
        )
        message = message.strip().strip('"').strip("'")

    if config and config.dry_run:
        return f"[DRY RUN] Would commit: {message}"

    commit = repo.index.commit(message)
    return f"Committed {commit.hexsha[:8]}: {message}"


@tool("git_status", "Show the current git status of the project.")
async def git_status(config=None, state=None) -> str:
    """Return git status output."""
    from git import Repo, InvalidGitRepositoryError

    try:
        repo = Repo(config.project_root if config else ".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        return "Not a git repository."
    return repo.git.status()


@tool("git_diff", "Show the current git diff (staged or unstaged).")
async def git_diff(
    staged: bool = False,
    config=None,
    state=None,
) -> str:
    """
    Return git diff output.

    Args:
        staged: If True, show staged diff (--cached). Otherwise unstaged.
    """
    from git import Repo, InvalidGitRepositoryError

    try:
        repo = Repo(config.project_root if config else ".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        return "Not a git repository."
    if staged:
        return repo.git.diff("--cached")
    return repo.git.diff()
