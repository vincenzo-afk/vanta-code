# Persistent Repository Memory

**Crate:** `autogit-memory`

## Purpose

Gives every repository memory that outlives individual Git commits. When
an AI agent joins a repository — new session, new agent, or an entirely
different tool — it should never have to rediscover the project from
scratch by reading every file. Repository Memory answers "what has
already happened here and why?"

## What is remembered

- Architectural decisions and their rationale
- Implemented features and when/how they landed
- Unfinished work and known blockers
- Developer and AI-agent intentions ("plan to migrate to Postgres next")
- AI conversation summaries and design discussions
- Coding conventions actually observed in the codebase (not just declared
  in a style guide)
- Dependency history (additions, removals, major version jumps and why)
- Migration history (database, framework, API)
- Documentation evolution
- Testing status and coverage trends
- Known technical debt and recurring bugs
- Prior engineering decisions, including ones that were later reversed

## Data model (conceptual)

```
MemoryRecord {
    id, repository_id, kind,       // Decision | Feature | Convention |
                                    // Blocker | DependencyChange |
                                    // Migration | Debt | Bug | Discussion
    summary,                        // short human-readable text
    detail,                         // longer structured detail
    related_graph_nodes: [NodeId],  // links into the Knowledge Graph
    related_commits: [Oid],
    confidence,                      // inferred vs explicitly stated
    created_at, superseded_by,       // memory can be revised, not just appended
}
```

Memory is **append-and-supersede**, not append-only: when new information
contradicts or refines an old record, the old record is marked
`superseded_by` rather than deleted, preserving the history of what
AutoGit believed and when — itself useful engineering context.

## How memory is populated

- Directly from the Engineering Decision Engine when a milestone is
  reached (feature completion, architectural refactor, etc.)
- From the Intent Tracking Engine when an objective is inferred or
  completed
- From the AI Reasoning Layer, which is asked to summarize significant
  agent/developer conversations into structured memory records
- From the Autonomous Repository Maintainer when it identifies recurring
  issues or resolves technical debt

## How memory is surfaced

When an agent connects to a repository (`repository_context` MCP tool),
AutoGit returns a curated **context bundle**:

- Current architecture summary (derived jointly with the Knowledge Graph)
- Recently completed features
- Ongoing work and its progress
- Remaining known tasks / blockers
- Observed coding conventions
- Relevant, non-superseded engineering history

This bundle is size-bounded and relevance-ranked (recency + graph
proximity to files the agent is about to touch), never a full memory dump.

## Interfaces

- **Emits:** `MemoryRecorded`, `MemorySuperseded`
- **Consumes:** `MilestoneReached`, `ObjectiveCompleted`, `CommitCreated`,
  `AgentInteraction`
- **Queried by:** MCP Server (`repository_context` tool), AI Reasoning
  Layer, Documentation Intelligence Engine, Autonomous Repository
  Maintainer

## Storage

Persisted in the same embedded storage layer as the Knowledge Graph (see
[`../platform/STORAGE.md`](../platform/STORAGE.md)), namespaced per
repository worker, with full-text and vector-similarity indexing so
"context bundle" retrieval can be relevance-ranked rather than purely
chronological.
