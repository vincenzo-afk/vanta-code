# Event Bus & Inter-Engine Communication

Every engine in AutoGit communicates exclusively through events. No engine
holds a direct reference to another engine's internal state or calls its
methods synchronously. This is what makes engines independently testable,
replaceable, and pluginizable.

## Event categories

| Category | Examples | Typical producer |
|---|---|---|
| **Observation events** | `FileChanged`, `GitOperationDetected`, `BuildFinished`, `TestRunFinished`, `DependencyInstalled`, `AgentInteraction` | Development Observer |
| **Intent events** | `ObjectiveInferred`, `ObjectiveProgressUpdated`, `ObjectiveReadyForCommit` | Intent Tracking Engine |
| **Knowledge events** | `GraphNodeAdded`, `GraphNodeUpdated`, `GraphEdgeChanged` | Repository Intelligence Engine |
| **Decision events** | `MilestoneReached`, `CommitApproved`, `BranchRecommended`, `ReleaseReady`, `RollbackRecommended` | Engineering Decision Engine |
| **Validation events** | `QualityGateStarted`, `QualityGatePassed`, `QualityGateFailed`, `AutoFixApplied` | Validation & QA Engine |
| **Documentation events** | `DocsOutOfSync`, `DocsRegenerated` | Documentation Intelligence Engine |
| **Git events** | `CommitCreated`, `BranchCreated`, `MergeCompleted`, `TagCreated`, `PushCompleted` | Git Engine |
| **Provider events** | `PullRequestOpened`, `IssueUpdated`, `WebhookReceived` | Provider Integrations |
| **Memory events** | `MemoryRecorded`, `TimelineEntryAdded` | Repository Memory / Engineering Timeline |
| **Policy events** | `ApprovalRequired`, `OperationBlocked` | Policy Engine |

## Transport

Internally, events are typed Rust enums delivered over `tokio::sync`
channels:

- **Per-worker broadcast bus** — most engine-to-engine traffic within a
  single repository worker. Every engine subscribes to the subset of
  event variants it cares about.
- **Point-to-point mpsc channels** — used where back-pressure and
  guaranteed delivery matter more than fan-out, e.g. Validation & QA
  Engine → Engineering Decision Engine gate results.
- **Runtime-level broadcast bus** — cross-worker events that shared
  services need (e.g. Scheduler ticks, global policy changes,
  configuration reloads).

## Event envelope

Every event carries a common envelope regardless of payload:

```rust
struct EventEnvelope<T> {
    id: Uuid,
    repository_id: RepoId,
    timestamp: DateTime<Utc>,
    correlation_id: Option<Uuid>, // ties a chain of events to one workflow
    source_engine: EngineId,
    payload: T,
}
```

`correlation_id` is what lets the Engineering Timeline and logging system
reconstruct "why did AutoGit commit this?" as a causal chain: observation
→ intent → decision → validation → git operation → memory record.

## Backpressure & ordering guarantees

- Observation events are best-effort and may be coalesced (debounced) by
  the Development Observer before entering the bus — engines downstream
  should never assume every raw filesystem event arrives individually.
- Decision-affecting events (validation results, git operation results)
  use bounded mpsc channels with backpressure; a slow consumer will make
  its producer wait rather than silently drop critical results.
- Within one `correlation_id` chain, events are strictly ordered; across
  different chains, no ordering is guaranteed.

## Why not direct calls?

Direct calls would mean the Engineering Decision Engine imports and calls
into the Validation Engine's crate, the Documentation Engine's crate,
etc. — collapsing them into one tightly coupled binary. With events:

- Any engine can be swapped for a plugin implementation without touching
  callers.
- New engines (e.g. a future "Cost Estimation Engine") can subscribe to
  existing events without modifying producers.
- Every workflow is replayable and unit-testable by feeding a recorded
  event sequence back through the bus.
