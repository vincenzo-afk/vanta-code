# Autonomous Repository Maintainer

**Crate:** `autogit-maintainer`

## Purpose

Continuously improves repository health over time, independent of any
single feature being actively worked on. Where most engines react to
active development, the Maintainer proactively watches for decay.

## What it monitors

- CI failures (including flaky-test detection over time)
- Dependency updates (including transitive advisories)
- Security advisories (matched against the dependency graph)
- Issue trackers (via Provider Integrations)
- Pull requests (stale, conflicting, abandoned)
- Merge conflicts
- Stale branches
- Outdated documentation (cross-checked with Documentation Intelligence)
- Release schedules (cadence drift against configured policy)
- Failing builds
- Performance regressions (via Engineering Timeline health trends)
- Vulnerability databases (OSV, GitHub Advisory Database, etc.)
- Repository analytics (activity trends, contributor patterns)

## Maintenance loop

```
Scheduled scan (via Scheduler) or event-triggered
      (e.g. new security advisory published)
        │
        ▼
Detect problem + identify probable root cause
        │
        ▼
Generate candidate fix (AI Reasoning Layer, using full
repository context from Memory + Knowledge Graph)
        │
        ▼
Validate locally (checkout in scratch worktree, apply fix)
        │
        ▼
Run configured quality gates (Validation & QA Engine)
        │
        ▼
   ┌──────────────┐
   │ Gates pass?    │
   └───┬──────┬─────┘
      yes      no
       │         │
       ▼         ▼
Prepare commit    Discard candidate, log finding for
+ branch + PR      manual triage; do not force a bad fix
(via Git Engine +
Provider Integrations)
       │
       ▼
Update documentation if affected
       │
       ▼
Notify maintainers according to operating mode
(auto-merge only if Autonomous mode + policy allows
for this class of fix, e.g. patch-level dependency bumps)
```

## Root-cause identification

Rather than pattern-matching purely on error text, the Maintainer
correlates failures against the Knowledge Graph (which recent changes
touch the failing area) and Repository Memory (has this failed before,
and how was it fixed then) before generating a candidate fix — reducing
the chance of proposing a fix that only masks a symptom.

## Escalation, not silent action

Findings the Maintainer cannot safely auto-remediate (ambiguous root
cause, fix requires a design decision, security issue with no available
patched version) are recorded and surfaced, never silently dropped or
silently forced through.

## Interfaces

- **Consumes:** scheduled ticks (Scheduler), `QualityGateFailed`,
  provider webhooks (`PullRequestOpened`/`IssueUpdated` etc.), vulnerability
  feed updates
- **Emits:** `MaintenanceFindingRecorded`, `CleanupRecommended` (to
  Decision Engine), candidate-fix branches/PRs (via Git Engine / Provider
  Integrations)
- **Delegates to:** AI Reasoning Layer, Validation & QA Engine, Git
  Engine, Provider Integrations, Policy Engine (approval routing)

## Configuration

Per repository: scan cadence, which maintenance categories are enabled,
auto-merge eligibility rules (typically limited to low-risk categories
like patch dependency bumps with passing gates), and notification
channels.
