# Git Engine

**Crate:** `autogit-git-engine`

## Purpose

The only place in AutoGit that touches Git directly, implemented on
Rust's `git2` crate (libgit2 bindings). It is deliberately "dumb" —
purely mechanical Git operations with no engineering judgment. Judgment
lives upstream in the Engineering Decision Engine, Repository Maintainer,
and Policy Engine; this engine only executes what it's told, safely.

## Responsibilities

- Object creation (blobs, trees, commits)
- Staging (index manipulation)
- Commit creation
- Branch creation, deletion, switching
- Merging (including conflict detection/reporting — not conflict
  *resolution*, which is an engineering decision)
- Tagging
- Rebasing
- Remote management
- Pushing, fetching, pulling
- Diff generation
- Repository initialization
- Repository cloning
- Object traversal / history access
- Conflict information reporting

## What it explicitly does NOT do

- Decide *whether* to commit, branch, merge, or release (Engineering
  Decision Engine's job)
- Decide *what* a commit message says (AI Reasoning Layer's job)
- Decide whether an operation requires approval (Policy Engine's job)
- Talk to GitHub/GitLab/Bitbucket APIs (Provider Integrations' job — this
  engine only understands the local repository and configured remotes)

## Access control

**No AI agent and no MCP tool ever calls into this engine directly.**
Every operation is invoked exclusively through the higher-level engines
(primarily Engineering Decision Engine and Repository Maintainer), which
themselves have already passed through Validation & QA and Policy
approval. This is a hard architectural boundary, not a convention — the
crate's public API is intentionally not exposed through the MCP server
surface.

## Concurrency discipline

Per repository worker, write operations (commit, branch mutation, merge,
push) are strictly serialized through a single-writer queue to avoid
concurrent `git2::Repository` handle misuse and index corruption.
Read-only operations (log traversal, diff generation, status) may use
short-lived handles concurrently.

## Error surface

Git Engine errors are translated into a typed `GitEngineError` (not raw
`git2::Error`) so upstream engines can reason about failure categories
(conflict, dirty working tree, detached HEAD, auth failure on
push/fetch, object corruption) without depending on libgit2 internals.

## Interfaces

- **Consumes:** validated operation requests from Engineering Decision
  Engine and Repository Maintainer (post-Policy-approval)
- **Emits:** `CommitCreated`, `BranchCreated`, `BranchDeleted`,
  `MergeCompleted`, `MergeConflictDetected`, `TagCreated`,
  `PushCompleted`, `FetchCompleted`, `RebaseCompleted`,
  `RepositoryInitialized`, `RepositoryCloned`
- **Used by:** Development Observer also *reads* from this engine's
  history-access API (not its write API) to detect manual Git activity
  performed outside AutoGit

## Testing

Exercised primarily against real scratch repositories created in temp
directories — this is one of the few crates where mocking is
counterproductive, since correctness here is fundamentally about real
Git object-model behavior.
