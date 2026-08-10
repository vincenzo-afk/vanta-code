# Logging, Telemetry & Metrics

**Crate:** `autogit-telemetry`

## Purpose

Gives operators and developers visibility into what AutoGit is doing and
why — critical for a system whose entire premise is taking autonomous
action on a codebase. If a commit, PR, or maintenance fix appears and a
developer can't quickly answer "why did AutoGit do this?", the platform
has failed at its most basic trust requirement.

## Logging

Built on `tracing` + `tracing-subscriber`. Every event flowing through
the internal event bus carries a `correlation_id` (see
[`../architecture/EVENT_BUS.md`](../architecture/EVENT_BUS.md)); log
lines emitted while handling that event are tagged with the same id, so a
full causal chain — observation → intent → decision → validation → git
operation → memory record — can be reconstructed from logs alone.

Log levels follow standard conventions (`error`, `warn`, `info`, `debug`,
`trace`), configurable globally and per-engine (e.g. run the Repository
Intelligence Engine at `debug` while everything else stays at `info`).

## Metrics

Exposed in a pull-based format (Prometheus-compatible) plus an
in-process aggregate queryable via the CLI/MCP for quick local checks.

Key metrics tracked:

| Metric | Purpose |
|---|---|
| `autogit_events_processed_total{engine, event_kind}` | Bus throughput per engine |
| `autogit_quality_gate_duration_seconds{gate}` | Validation pipeline performance |
| `autogit_quality_gate_result_total{gate, result}` | Pass/fail/autofix rates |
| `autogit_commits_created_total{repository, mode}` | Autonomy activity volume |
| `autogit_approval_required_total{category}` | How often policy requires a human |
| `autogit_reasoning_requests_total{task, provider}` | LLM usage by task type |
| `autogit_reasoning_tokens_total{provider}` | Cost visibility |
| `autogit_worker_active_count` | Live repository workers |
| `autogit_scheduler_job_duration_seconds{kind}` | Scheduled job performance |

## Audit trail

Beyond metrics and logs, every decision that results in a repository
mutation is separately recorded to the Engineering Timeline (see
[`../engines/ENGINEERING_TIMELINE.md`](../engines/ENGINEERING_TIMELINE.md))
as a durable, queryable record — logs and metrics are operational
visibility; the Timeline is the permanent, structured audit record meant
to survive far longer than log retention windows.

## Privacy

Telemetry never includes repository source code content, credential
values, or full LLM prompt/response bodies by default — only structural
metadata (event kinds, durations, counts, repository/engine identifiers).
Verbose debug logging that does include more detail is explicitly opt-in
and scoped to a time window, never left on by default.

## Interfaces

- **Consumes:** every event on every bus (as a passive subscriber — never
  mutates state)
- **Exposes:** `/metrics` HTTP endpoint (local-only by default), CLI
  query commands, structured log output (JSON or human-readable,
  configurable)
