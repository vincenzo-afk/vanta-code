# Scheduler

**Crate:** `autogit-scheduler`

## Purpose

Drives every time-based (as opposed to purely event-reactive) behavior in
AutoGit: periodic maintenance scans, health-snapshot computation,
scheduled release windows, and cache/state cleanup.

## Two kinds of scheduling

- **Cron-style** (via `tokio-cron-scheduler`) — e.g. "run a maintenance
  scan every 6 hours," "compute a repository health snapshot nightly"
- **Reactive/delayed** — e.g. "re-check this failing build in 10 minutes
  in case it was a transient CI issue," "abandon this objective if no
  related activity occurs for 3 days" (Intent Tracking Engine)

## Why a shared scheduler rather than ad hoc timers per engine

Centralizing scheduling means:

- Global visibility into what's scheduled and when (useful for
  telemetry and debugging "why did AutoGit do something at 3am")
- Coordinated jitter/staggering across many repository workers so, e.g.,
  a fleet of 50 repositories doesn't all kick off maintenance scans in
  the same second
- One place to apply global rate limits (e.g. LLM request budget shared
  across scheduled jobs)

## Job model

```rust
struct ScheduledJob {
    id: JobId,
    repository_id: Option<RepoId>,   // None for global jobs
    schedule: Schedule,               // Cron | Once { at } | Delay { after }
    kind: JobKind,                    // MaintenanceScan | HealthSnapshot |
                                        // ReleaseWindow | CacheCleanup |
                                        // ObjectiveTimeout | Custom(String)
    on_fire: EventEnvelope<JobFired>, // event emitted, consumed by owning engine
}
```

The scheduler itself does no domain work — firing a job just emits an
event onto the relevant worker's (or the global) event bus; the owning
engine (Repository Maintainer, Engineering Timeline, Intent Tracker)
decides what to actually do.

## Persistence

Scheduled job state (next-run time, in-flight status) is persisted via
the Storage Layer so a restart doesn't lose track of pending scheduled
work or double-fire jobs that were mid-flight at shutdown.

## Configuration

Cron expressions and default delays are configurable per repository (see
[`../operations/CONFIGURATION.md`](../operations/CONFIGURATION.md),
`[scheduler]` section); plugins can register additional job kinds via the
Plugin System.

## Interfaces

- **Emits:** `JobFired` (typed per `JobKind`)
- **Consumed by:** Autonomous Repository Maintainer (scan triggers),
  Engineering Timeline (health snapshots), Intent Tracking Engine
  (objective timeouts), Storage Layer (cleanup jobs)
- **Configured via:** Configuration Manager
