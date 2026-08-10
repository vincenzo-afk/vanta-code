# MCP Server

**Crate:** `autogit-mcp-server`

## Purpose

AutoGit's primary interface for AI coding agents. Implements the **Model
Context Protocol** so any MCP-compatible agent (Claude Code, Cursor, or
any future MCP client) can connect without custom integration work.

## Transports supported

- **stdio** — for agents that spawn AutoGit as a local subprocess-style
  MCP server
- **HTTP** — for agents/tools that connect to AutoGit as a long-running
  local service
- **SSE (Server-Sent Events)** — for streaming tool results and
  long-running operations (e.g. a maintenance scan in progress)

All three transports expose the identical tool surface; transport choice
never changes semantics.

## Core design: semantic tools, not Git commands

Agents never call `git_commit(message)` or `git_branch(name)`. Instead
they express **engineering intent**, and AutoGit's engines determine what
repository operations that intent requires.

## Tool catalog (representative — grouped by purpose)

### Repository lifecycle
- `repository_init` — bootstrap a new/under-scaffolded repository
  (delegates to Project Bootstrap Engine)
- `repository_register` — start managing an existing repository
- `repository_context` — retrieve the curated context bundle from
  Repository Memory + Knowledge Graph for an agent joining a repository

### Engineering intent signals
- `feature_started` / `feature_completed`
- `bug_fixed`
- `refactor_completed`
- `authentication_implemented` (and other domain-specific shorthand
  intents that map to common objective kinds recognized by the Intent
  Tracking Engine)
- `objective_status` — "what's left before this is commit-ready?"

### Review & analysis
- `repository_analysis` — request a fresh Knowledge Graph / health
  summary
- `engineering_review` — request the Decision Engine's assessment of
  current state (ready to commit? ready to release? outstanding
  concerns?)

### Release & documentation
- `prepare_release`
- `generate_changelog`
- `generate_documentation`
- `update_dependencies`

### Maintenance
- `repository_maintenance` — trigger an on-demand maintenance scan
- `issue_resolution` — hand AutoGit a specific issue to investigate/fix

### Deployment
- `prepare_deployment`

## Tool call → engine routing (example)

```
Agent calls: feature_completed(description: "JWT auth implemented,
              tests passing, docs updated")
        │
        ▼
MCP Server validates/normalizes the call, emits AgentInteraction
        │
        ▼
Intent Tracking Engine matches against tracked objective, marks
ready-for-commit
        │
        ▼
Engineering Decision Engine runs its pipeline (validation, reasoning,
policy) — see ENGINEERING_DECISION_ENGINE.md
        │
        ▼
MCP Server returns a structured result to the agent: what happened
(commit created / PR opened / approval pending) and why
```

## Response shape

Every tool response includes not just a result but the **reasoning
trail** relevant to it (which objective this was tied to, which quality
gates ran, what memory/timeline entries were created) so the agent (and
any human reviewing the agent's session) can see AutoGit's reasoning, not
just its output.

## Authentication & scoping

MCP connections are scoped to specific repositories at connection time
(or via `repository_register`); an agent cannot address a repository it
hasn't been granted access to. See
[`../platform/AUTHENTICATION.md`](../platform/AUTHENTICATION.md).

## Extensibility

New semantic tools can be added by plugins without modifying the core MCP
server — see [`../platform/PLUGIN_SYSTEM.md`](../platform/PLUGIN_SYSTEM.md).
