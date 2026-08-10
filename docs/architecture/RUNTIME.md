# Runtime & Concurrency Model

## One process, one Tokio runtime, many repositories

AutoGit runs as a single cross-platform background service built on
**Tokio**. It does not spawn a new OS process per repository. Instead, the
runtime owns a pool of **repository workers**, each an isolated async task
(or task group) responsible for exactly one repository.

```
                     AutoGit Runtime (single process)
 ┌────────────────────────────────────────────────────────────────┐
 │  Shared services (singletons, injected into every worker):      │
 │   - LLM Interface        - MCP Server         - Scheduler        │
 │   - Auth Manager         - Storage Layer       - Plugin Manager  │
 │   - Logging / Telemetry  - Configuration Mgr   - Policy Engine   │
 ├────────────────────────────────────────────────────────────────┤
 │  Repository Worker A     Repository Worker B     Worker C  ...   │
 │   - own state             - own state             - own state    │
 │   - own locks              - own locks              - own locks   │
 │   - own cache               - own cache               - own cache  │
 │   - own event queue          - own event queue          - own queue │
 │   - own repo memory ns        - own repo memory ns        - own ns   │
 │   - own config overlay         - own config overlay        - own    │
 └────────────────────────────────────────────────────────────────┘
```

## Why per-repository isolation matters

- A slow or misbehaving analysis job in one repository must never block
  commits or MCP responses for another.
- Repository memory and knowledge-graph state must never leak across
  repositories, even when they share a monorepo host machine.
- Configuration (operating mode, quality gates, provider credentials) is
  frequently repository-specific and must not be globally mutable at
  runtime.

## Worker lifecycle

1. **Registration** — a repository is registered (via MCP tool,
   CLI, or auto-discovery) with a path and initial configuration.
2. **Bootstrap** — the worker loads or builds its knowledge graph and
   repository memory from persistent storage (see
   [`../platform/STORAGE.md`](../platform/STORAGE.md)).
3. **Active** — the worker subscribes to filesystem/Git/build events from
   the Development Observer and begins servicing MCP tool calls scoped to
   its repository.
4. **Idle/suspended** — workers with no recent activity release in-memory
   caches but keep their event queue and persisted state, so they resume
   instantly on the next event.
5. **Deregistration** — explicit removal clears in-memory state; persisted
   memory/knowledge graph is retained unless the user requests a purge.

## Communication model

Workers never call into each other's internals. All cross-cutting
communication — including from shared services back into a worker — goes
through **asynchronous channels and the event bus** (`tokio::sync::mpsc` /
`broadcast` internally). This keeps every engine independently testable:
an engine can be exercised in isolation just by feeding it events and
asserting on the events it emits.

See [`EVENT_BUS.md`](EVENT_BUS.md) for the event taxonomy and
[`WORKSPACE_LAYOUT.md`](WORKSPACE_LAYOUT.md) for how this maps to Rust
crates.

## Concurrency safety within a worker

- All mutable worker state is owned by the worker's task and only
  reachable through message-passing — no shared `Mutex<RepoState>` across
  engines.
- Git Engine operations against a given repository are strictly
  serialized per worker (a single-writer discipline) to avoid concurrent
  `git2::Repository` handle misuse; read-heavy operations (diff, log
  inspection) may use short-lived read handles concurrently.
- Long-running analysis (Tree-sitter parsing, knowledge graph rebuilds) is
  offloaded to a bounded `spawn_blocking` pool shared across workers, so
  CPU-heavy parsing never starves the async scheduler.

## Failure isolation

A panic or unrecoverable error inside one worker is caught at the worker
task boundary, logged with full context, and results in that worker
transitioning to a `Degraded` state (MCP calls for that repository return
a clear error) without affecting other workers or the shared runtime.
