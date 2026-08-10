# Intent Tracking Engine

**Crate:** `autogit-intent`

## Purpose

Continuously infers what the developer or AI agent is currently trying to
accomplish, so that commits, reviews, and pull requests reflect completed
**objectives** rather than arbitrary snapshots of file changes.

## Objective inference

Objectives are inferred from a combination of:

- Explicit signals — an agent calling MCP tools like `feature_started` or
  stating intent in a `feature_completed` call's description
- Implicit signals — clusters of related file changes (via Knowledge
  Graph proximity), branch naming patterns, commit message patterns from
  manual Git activity, and recurring terminal/build commands
- Repository Memory — matching current activity against previously
  recorded intentions ("plan to migrate to Postgres next")

Examples of recognized objective types: implementing authentication,
redesigning navigation, migrating databases, integrating payments,
improving caching, writing documentation, fixing production bugs.

## Objective lifecycle

```
Inferred → In Progress → Near Completion → Ready for Commit → Completed
                │
                ├─→ Blocked (missing dependency, failing test, waiting on review)
                └─→ Abandoned (no related activity for a configurable period)
```

## Tracked per objective

- Estimated completion percentage (derived from graph coverage of
  affected areas + test/doc status, not a guess pulled from thin air)
- Blockers (explicit or inferred, e.g. a failing test tied to the
  objective's changed files)
- Pending tests (tests that exist but haven't been run since related
  files changed, or tests the Decision Engine expects but doesn't see)
- Missing documentation (surfaces touched by the objective that have no
  corresponding doc update yet)
- Remaining subtasks (either explicitly declared by an agent, or inferred
  from TODOs / stubbed implementations detected by Repository
  Intelligence)
- Readiness for commit — a boolean+reasons view consumed directly by the
  Engineering Decision Engine

## Multiple concurrent objectives

A repository worker can track several objectives simultaneously (e.g. one
agent implementing a feature while another fixes an unrelated bug).
Objectives are disambiguated primarily by non-overlapping Knowledge Graph
regions; overlapping changes are flagged as a potential conflict rather
than silently merged into one objective.

## Data model (conceptual)

```
Objective {
    id, repository_id, kind, title,
    status: Inferred | InProgress | NearCompletion | ReadyForCommit
          | Completed | Blocked | Abandoned,
    completion_estimate: 0.0..1.0,
    blockers: [Blocker],
    affected_graph_nodes: [NodeId],
    related_agent_sessions: [SessionId],
    created_at, updated_at,
}
```

## Interfaces

- **Consumes:** `FileChanged`, `AgentInteraction`, `TestRunFinished`,
  `BuildFinished` (Observer), `GraphEdgeChanged` (Repository
  Intelligence), historical objectives from Repository Memory
- **Emits:** `ObjectiveInferred`, `ObjectiveProgressUpdated`,
  `ObjectiveBlocked`, `ObjectiveReadyForCommit`, `ObjectiveCompleted`,
  `ObjectiveAbandoned`
- **Queried by:** Engineering Decision Engine (primary consumer),
  Repository Memory (records completed/abandoned objectives), MCP Server
  (`objective_status` tool so an agent can ask "what's left before this
  is commit-ready?")
