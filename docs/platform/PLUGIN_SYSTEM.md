# Plugin System

**Crate:** `autogit-plugin`

## Purpose

Lets every engine be extended or replaced without modifying core code,
consistent with the architecture-wide rule that engines communicate only
through events (see
[`../architecture/EVENT_BUS.md`](../architecture/EVENT_BUS.md)). Plugins
are how AutoGit stays adaptable to language ecosystems, providers, and
organizational workflows it doesn't ship with by default.

## What can be plugged in

| Extension point | Example |
|---|---|
| Language analyzer | A Tree-sitter grammar + analyzer for a language not in the core set |
| Quality gate | An organization-specific static analysis tool |
| Reasoning provider | An alternative or local LLM backend |
| Remote provider | A self-hosted Git host (e.g. Gitea) beyond GitHub/GitLab/Bitbucket |
| MCP tool | A new semantic tool exposed to agents (e.g. `compliance_review`) |
| Documentation template | Org-specific README/CONTRIBUTING structure |
| Maintenance check | A custom repository-health rule |
| Notification channel | Routing `ApprovalRequired` to a specific chat platform |

## Plugin trait shape (conceptual)

```rust
trait Plugin: Send + Sync {
    fn id(&self) -> &str;
    fn kind(&self) -> PluginKind;
    fn subscribed_events(&self) -> &[EventKind];
    async fn handle(&self, event: EventEnvelope<Value>, ctx: &PluginContext)
        -> Result<Vec<EventEnvelope<Value>>>;
}
```

Plugins subscribe to the same event bus every core engine uses — a
plugin is architecturally indistinguishable from a core engine from the
bus's point of view. This is deliberate: it keeps the plugin API from
becoming a second-class, restricted subset of what core engines can do.

## Loading model

Plugins are compiled Rust crates (via a stable plugin ABI/dynamic
loading) rather than an embedded scripting language, prioritizing
type-safety and performance over runtime flexibility. A plugin manifest
(`plugin.toml`) declares its id, kind, subscribed events, and required
capabilities (filesystem access, network access, credential access),
which the Plugin Manager enforces at load time.

```toml
[plugin]
id = "org-compliance-gate"
kind = "quality_gate"
version = "0.1.0"

[capabilities]
filesystem = "read_repository"
network = false
credentials = []
```

## Sandboxing & trust

Plugins run within the same process (for performance) but are granted
only the capabilities declared in their manifest; the Plugin Manager
denies any operation (network call, credential access, filesystem
access outside the repository) not explicitly declared. Plugins that
attempt undeclared operations are logged and disabled.

## Interfaces

- **Registered with:** Plugin Manager (a shared runtime service)
- **Communicates via:** the same per-worker and runtime-level event buses
  as core engines
- **Configured via:** `[plugins]` section of repository/global config,
  listing enabled plugin ids and any plugin-specific settings
