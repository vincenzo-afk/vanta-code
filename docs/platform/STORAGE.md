# Storage Layer

**Crate:** `autogit-storage`

## Purpose

Provides embedded, persistent storage shared by every engine that needs
state to survive process restarts: the Software Knowledge Graph,
Repository Memory, Engineering Timeline, configuration cache, and
scheduler state.

## Backend choice

Supports both **SQLite** (via `rusqlite`) and **Sled** behind a common
trait, selectable per deployment:

- SQLite — default; mature tooling, easy to inspect/debug, good fit for
  the relational shape of the Knowledge Graph and Timeline
- Sled — optional for deployments prioritizing pure-Rust embedded
  key-value performance over relational query needs

```rust
#[async_trait]
trait StorageBackend {
    async fn get(&self, namespace: &str, key: &str) -> Result<Option<Bytes>>;
    async fn put(&self, namespace: &str, key: &str, value: Bytes) -> Result<()>;
    async fn query(&self, namespace: &str, query: StorageQuery) -> Result<Vec<Record>>;
    async fn transaction<F>(&self, f: F) -> Result<()>
        where F: FnOnce(&mut Transaction) -> Result<()>;
}
```

## Namespacing

Every repository worker gets its own storage namespace
(`repositories/<repo_id>/...`), guaranteeing that no query can
accidentally cross repository boundaries. Shared/global data (scheduler
state, plugin registry, telemetry aggregates) lives in a separate
`global/` namespace.

## What's stored where

| Data | Shape | Notes |
|---|---|---|
| Knowledge Graph | Relational (nodes/edges tables) | Incrementally updated, see `REPOSITORY_INTELLIGENCE.md` |
| Repository Memory | Relational + full-text/vector index | Append-and-supersede |
| Engineering Timeline | Relational, time-ordered | Cross-linked to graph nodes and memory records |
| Configuration cache | Key-value | Derived/resolved config, invalidated on `ConfigurationChanged` |
| Scheduler state | Key-value | Next-run timestamps, in-flight job tracking |
| Auth tokens | Encrypted key-value | Delegated to Auth Manager, never stored in plaintext |

## Migrations

Schema changes ship with versioned migration scripts run automatically at
startup, with a pre-migration backup of the SQLite file (or Sled tree
snapshot) taken before applying, so a bad migration is always
recoverable.

## Backup & portability

Since all durable AutoGit state lives in this layer, "back up AutoGit's
understanding of a repository" is just "copy the namespace's storage
file" — no distributed state to reconcile.

## Interfaces

- **Used directly by:** Repository Intelligence, Repository Memory,
  Engineering Timeline, Configuration Manager, Scheduler
- **Never used directly by:** MCP Server or any engine that should only
  see structured domain objects, not raw storage records — those go
  through the owning engine's query API instead
