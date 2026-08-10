# Operating Modes

AutoGit supports three configurable operating modes, set per repository
(and overridable per operation category). Mode governs **how much human
approval** is required before a repository is actually modified — it
never changes what the engines *analyze* or *decide*, only what they're
allowed to *execute* without confirmation.

## Manual Mode

Every repository modification requires explicit user approval before
execution. AutoGit still runs its full pipeline — Observer, Intent
Tracker, Decision Engine, Validation, Reasoning — and presents a complete
proposed action (e.g. "ready to commit: JWT auth implementation, all
gates passed, here's the message") for the user to approve, edit, or
reject. Nothing reaches Git or a remote provider without a yes.

Best for: sensitive repositories, teams establishing trust in AutoGit for
the first time, compliance-constrained environments.

## Assisted Mode

AutoGit prepares commits, reviews, documentation, branches, and pull
requests autonomously, but requests confirmation before **publishing**
changes — i.e. it will create local commits and local branches on its own
judgment, but pushing to a remote, opening a PR, or creating a release
requires a confirmation step.

Best for: most day-to-day use — removes friction from the mechanical
parts of committing while keeping a human in the loop for anything
externally visible.

## Autonomous Mode

AutoGit independently manages repository maintenance, engineering
workflows, documentation, issue resolution, pull requests, releases, and
repository improvements, within configurable safety policies (see
[`POLICY_ENGINE.md`](POLICY_ENGINE.md)). Even in this mode, high-risk
categories (breaking API changes, force-pushes, destructive branch
deletion, security-sensitive dependency changes without a passing test
suite) can be individually pinned to always require approval.

Best for: mature repositories with strong test coverage and a policy
configuration the team trusts.

## Mode is not all-or-nothing

Operating mode is the *default* for a repository, but the Policy Engine
allows per-category overrides — e.g. "Assisted mode overall, but
Autonomous for dependency patch bumps" or "Autonomous overall, but Manual
for anything touching `SECURITY.md` or auth code." See
[`POLICY_ENGINE.md`](POLICY_ENGINE.md) for how these overrides are
expressed.

## Mode transitions

Changing a repository's mode is itself a policy-relevant action: dropping
from Manual to Autonomous should surface a clear summary of what that
newly permits before taking effect, especially in a team setting where the
person changing the mode may not be the only one affected by it.

## Relationship to Validation & QA

Operating mode never bypasses quality gates. A failing gate in
Autonomous mode still blocks the operation — mode only controls whether a
*passing* operation additionally requires human sign-off before
execution/publication.
