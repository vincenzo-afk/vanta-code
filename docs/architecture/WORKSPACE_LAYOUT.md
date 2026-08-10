# Rust Workspace Layout

AutoGit is a single Cargo workspace. Every engine described in
[`docs/engines/`](../engines/) maps to its own crate so it can be
compiled, tested, and versioned independently.

```
autogit/
├── Cargo.toml                      # workspace root
├── crates/
│   ├── autogit-runtime/            # Tokio runtime, worker supervisor, event bus
│   ├── autogit-events/             # shared event envelope + enum definitions
│   ├── autogit-config/             # Configuration Manager
│   ├── autogit-storage/            # SQLite/Sled abstraction, migrations
│   ├── autogit-scheduler/          # cron-like + reactive scheduling
│   ├── autogit-auth/               # credential storage, OAuth flows
│   ├── autogit-telemetry/          # logging + metrics
│   ├── autogit-plugin/             # plugin trait definitions + loader
│   ├── autogit-policy/             # Policy Engine, operating modes
│   │
│   ├── autogit-git-engine/         # git2-based low-level Git operations
│   ├── autogit-intelligence/       # Repository Intelligence Engine (Tree-sitter, knowledge graph)
│   ├── autogit-memory/             # Persistent Repository Memory
│   ├── autogit-observer/           # Development Observer Engine
│   ├── autogit-decision/           # Engineering Decision Engine
│   ├── autogit-timeline/           # Engineering Timeline
│   ├── autogit-intent/             # Intent Tracking Engine
│   ├── autogit-validation/         # Validation & QA Engine
│   ├── autogit-docs-engine/        # Documentation Intelligence Engine
│   ├── autogit-bootstrap/          # Project Bootstrap Engine
│   ├── autogit-maintainer/         # Autonomous Repository Maintainer
│   ├── autogit-reasoning/          # AI Reasoning Layer (LLM interface, prompt schemas)
│   │
│   ├── autogit-providers/          # shared provider trait
│   │   ├── github/
│   │   ├── gitlab/
│   │   └── bitbucket/
│   │
│   ├── autogit-mcp-server/         # MCP tool definitions + transport (stdio/HTTP/SSE)
│   └── autogit-cli/                # optional local CLI / debugging surface
│
├── config/                         # default config templates
├── docs/                           # this documentation set
└── scripts/                        # dev tooling (bootstrap, release, etc.)
```

## Dependency direction

Crates only depend "downward":

```
autogit-cli, autogit-mcp-server
        │
        ▼
autogit-decision, autogit-maintainer, autogit-bootstrap   (orchestration)
        │
        ▼
autogit-intelligence, autogit-memory, autogit-observer,
autogit-intent, autogit-validation, autogit-docs-engine,
autogit-reasoning, autogit-timeline                        (engines)
        │
        ▼
autogit-git-engine, autogit-providers/*                    (low-level I/O)
        │
        ▼
autogit-events, autogit-storage, autogit-config,
autogit-telemetry, autogit-auth, autogit-scheduler,
autogit-policy, autogit-plugin                              (platform)
```

`autogit-runtime` sits outside this stack and wires everything together
at startup; it is the only crate allowed to depend on (nearly) everything.

## Key external crates

| Purpose | Crate |
|---|---|
| Async runtime | `tokio` |
| Git operations | `git2` |
| Code parsing | `tree-sitter` + per-language grammars |
| Embedded storage | `rusqlite` (SQLite) and/or `sled` |
| MCP transport | `rmcp` (or hand-rolled JSON-RPC over stdio/HTTP/SSE) |
| HTTP client (providers, LLM) | `reqwest` |
| Serialization | `serde`, `serde_json` |
| Config parsing | `serde` + `toml` |
| Filesystem watching | `notify` |
| CLI | `clap` |
| Logging/tracing | `tracing`, `tracing-subscriber` |
| Scheduling | `tokio-cron-scheduler` |

## Testing strategy per crate

Every engine crate exposes a pure, event-in/event-out test harness (no
network, no real Git repository required) plus a smaller set of
integration tests in `autogit-runtime` that wire multiple real engines
together against a scratch Git repository created in a temp directory.
