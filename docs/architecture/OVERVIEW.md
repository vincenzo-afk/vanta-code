# Architecture Overview

## Core principle

Git is the **object database and version-history engine**. AutoGit is the
**reasoning layer** above it. AI agents never talk to Git directly and
never talk to raw file operations directly — they talk to AutoGit's MCP
server using engineering intent, and AutoGit's engines translate that
intent into validated, policy-checked Git operations.

```
 AI Coding Agent (Claude Code, Cursor, etc.)
          │  MCP (stdio / HTTP / SSE)
          ▼
   ┌─────────────────────┐
   │      MCP Server      │  ← semantic tools, not git commands
   └─────────┬────────────┘
             ▼
   ┌─────────────────────────────────────────────┐
   │            Engineering Decision Engine        │  ← primary intelligence
   └───┬───────┬────────┬────────┬────────┬───────┘
       │       │        │        │        │
   Intent   Validation  Docs   Repo      AI
   Tracker  & QA        Intel  Maintainer Reasoning
       │       │        │        │        │
       └───────┴────────┴────────┴────────┘
                       │
             ┌─────────▼─────────┐
             │     Git Engine     │  (git2 crate — low level only)
             └─────────┬─────────┘
                       │
                    Git objects
```

## Design tenets

1. **Git-native, not Git-replacing.** AutoGit never invents its own
   history format. All version history lives in real Git objects,
   readable by any standard Git tool.
2. **Intent in, decisions out.** Agents describe *what happened*
   ("authentication implemented"); AutoGit decides *what to do about it*
   (commit now? wait for tests? open a PR?).
3. **Engines, not utilities.** Every capability is an independently
   testable, replaceable engine communicating over an async event bus —
   never a direct function call into another engine's internals.
4. **Memory outlives commits.** Architectural decisions, rationale, and
   unfinished work are first-class, persisted data — not something that
   has to be reverse-engineered from a diff.
5. **Documentation is generated, not maintained by hand.** Docs are a
   projection of the knowledge graph and repository memory, regenerated
   whenever the underlying reality changes.
6. **Safety is configurable, not implicit.** Every write operation passes
   through the Validation & QA Engine and the Policy Engine before it can
   touch a repository, and the operating mode (Manual / Assisted /
   Autonomous) governs how much human approval is required.

## The three layers

| Layer | Responsibility | Key components |
|---|---|---|
| **Interface layer** | Exposes AutoGit to the outside world | MCP Server, Provider Integrations (GitHub/GitLab/Bitbucket), CLI/API |
| **Intelligence layer** | Understands and reasons about software | Repository Intelligence Engine, Repository Memory, Development Observer, Engineering Decision Engine, Intent Tracker, Documentation Intelligence, AI Reasoning Layer |
| **Execution layer** | Performs safe, validated repository operations | Validation & QA Engine, Project Bootstrap Engine, Repository Maintainer, Git Engine, Policy Engine |

Cross-cutting platform services (Storage, Scheduler, Configuration,
Logging/Metrics, Authentication, Plugin System) are shared across every
repository worker — see [`docs/platform/`](../platform/).

## Repository isolation

Each repository AutoGit manages runs inside its own **worker**: independent
state, locks, in-memory caches, event queue, repository memory namespace,
and configuration. Workers never share mutable state directly; they share
*services* (LLM interface, MCP server, scheduler, storage, auth) through
the runtime. See [`RUNTIME.md`](RUNTIME.md) for the concurrency model.

## Data flow for a typical "feature completed" event

1. Agent calls the `feature_completed` MCP tool.
2. Development Observer has already been recording file/test/build events
   for that repository and worker.
3. Intent Tracker matches the signal against the in-progress objective
   ("implementing authentication") and marks it near-complete.
4. Engineering Decision Engine asks Validation & QA Engine to run the
   configured quality gates.
5. If gates pass (or are auto-fixed), Decision Engine asks the AI
   Reasoning Layer to draft a commit message and, if relevant, changelog
   / doc updates, using structured context from Repository Memory and the
   Knowledge Graph.
6. Documentation Intelligence Engine regenerates any docs affected by the
   change.
7. Git Engine performs the actual commit (and branch/PR operations if the
   operating mode allows).
8. Engineering Timeline and Repository Memory are updated with the new
   milestone.

See [`docs/architecture/EVENT_BUS.md`](EVENT_BUS.md) for exactly how these
steps are wired together as async events rather than direct calls.
