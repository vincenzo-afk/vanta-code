# Engineering Timeline

**Crate:** `autogit-timeline`

## Purpose

A continuously-evolving record of a repository's *engineering* history,
distinct from Git's commit history. Where `git log` tells you what
changed, the Engineering Timeline tells you **why it mattered**.

## What it records

- Introduction of major features
- Security improvements
- Database migrations
- Dependency upgrades (especially major/breaking ones)
- Performance optimizations
- Infrastructure changes
- API evolution (added/changed/removed endpoints or contracts)
- Architectural refactors
- Release milestones
- Technical debt accumulation (and paydown)
- Repository health trends over time

## Relationship to Git history and Repository Memory

- **Git history** is the ground truth of *what changed* (diffs, commits).
- **Repository Memory** is the queryable *knowledge base* of decisions,
  conventions, and context.
- **Engineering Timeline** is the *narrative sequence* — an ordered,
  human-and-agent-readable story of the project's evolution, built from
  Repository Memory records and Decision Engine milestones, cross-linked
  to the actual commits/PRs/releases that realized them.

Think of Repository Memory as the encyclopedia and the Timeline as the
history book written from it.

## Entry shape (conceptual)

```
TimelineEntry {
    id, repository_id, category,     // Feature | Security | Migration |
                                       // Dependency | Performance |
                                       // Infrastructure | API | Refactor |
                                       // Release | TechnicalDebt | Health
    title, narrative,                 // short title + generated narrative
    significance,                      // Minor | Notable | Major
    linked_commits: [Oid],
    linked_memory_records: [MemoryRecordId],
    linked_graph_nodes: [NodeId],
    occurred_at,
}
```

## Repository health trends

The Timeline periodically (via the Scheduler) computes and records
rolling health snapshots: test pass rate trend, dependency freshness,
security advisory exposure, documentation-sync rate, and open
technical-debt volume — so "is this repository getting healthier or
worse?" is answerable with data, not vibes.

## Interfaces

- **Consumes:** `MilestoneReached`, `MemoryRecorded`, `CommitCreated`,
  `ReleaseReady`/release completion events, maintenance findings from
  Repository Maintainer, scheduled health-snapshot ticks
- **Emits:** `TimelineEntryAdded`, `HealthSnapshotRecorded`
- **Queried by:** Documentation Intelligence Engine (changelog and
  release-notes generation), AI Reasoning Layer (long-horizon context for
  future agents), MCP Server (`engineering_timeline` tool for agents/users
  who want the story of the project)

## Why this matters for future AI agents

An agent joining a repository six months from now should be able to
understand *how* the software got to its current state — not just what
the diff between two commits looks like. The Timeline is what makes that
possible without requiring the agent to replay the entire commit log.
