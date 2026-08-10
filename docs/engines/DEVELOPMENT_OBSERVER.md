# Development Observer Engine

**Crate:** `autogit-observer`

## Purpose

Turns raw activity on the developer's machine into **structured
engineering events** that the rest of AutoGit can reason about. This is
the only engine that touches the OS-level filesystem watcher, terminal
hooks, and editor integrations directly.

## What it observes

- Filesystem changes (platform-native watchers via `notify`, debounced)
- Git operations (branch switches, commits made outside AutoGit, merges,
  rebases — detected via a lightweight ref/reflog watcher)
- Terminal commands relevant to engineering (build tools, test runners,
  package managers) — opt-in, shell-hook based
- Build executions and their outcomes
- Test executions and their outcomes
- Editor activity, when an editor integration is available (open files,
  active file, save events) — supplements filesystem events with intent
  signal, never required
- Dependency installations (lockfile changes, package manager invocations)
- Configuration file changes
- Documentation file changes
- Interactions from connected AI agents via the MCP server

## Debouncing philosophy

AutoGit must react to **stable states**, not keystrokes. Filesystem events
are coalesced with a configurable quiet window (default a few seconds of
inactivity in a touched subtree) before being emitted as a single
`FileChanged` batch event. This is a hard architectural requirement — no
downstream engine should ever be triggered per-keystroke.

## Event enrichment

Raw OS events are enriched before leaving the Observer:

- File paths are classified using the Knowledge Graph (source vs. test
  vs. config vs. generated vs. vendored)
- A batch of related file changes is tagged with the graph nodes it
  likely affects
- Build/test outcomes are attached to the commit-range or working-tree
  state they correspond to

## Interfaces

- **Emits:** `FileChanged`, `GitOperationDetected`, `BuildFinished`,
  `TestRunFinished`, `DependencyInstalled`, `ConfigChanged`,
  `DocChanged`, `AgentInteraction`, `TerminalCommandExecuted`
- **Consumes:** none from other engines — this is a source engine that sits
  at the edge of the system, reading the OS and the MCP server's inbound
  traffic
- **Configuration:** debounce window, which paths/globs to ignore
  (`.gitignore`-aware by default), whether terminal-command and editor
  observation are enabled (both opt-in due to sensitivity)

## Privacy & scope boundaries

- Terminal command observation only inspects the command line, never
  captures full terminal output by default, and is opt-in per repository.
- Editor integration observes file focus/save events only — never keylog
  content.
- All observation is scoped strictly to registered repository paths;
  AutoGit never watches arbitrary parts of the filesystem.

## Why this engine matters for the Decision Engine

Every downstream "was this a meaningful milestone?" judgment made by the
Engineering Decision Engine depends on having a *reliable, de-noised*
signal to reason over. A noisy or naive file watcher would make the whole
platform look twitchy and untrustworthy; the Observer's debouncing and
enrichment work is what makes "reason about intent, not diffs" possible
at all.
