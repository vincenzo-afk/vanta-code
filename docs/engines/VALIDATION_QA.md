# Validation & Quality Assurance Engine

**Crate:** `autogit-validation`

## Purpose

Runs before every repository write operation. Nothing reaches Git without
passing through this engine's configured quality gates (or being
explicitly approved despite a failure, in modes that allow it).

## Quality gates (modular pipeline)

Each gate is an independent, pluggable step:

- Formatting (language-appropriate formatters)
- Linting (static style/quality rules)
- Static analysis (deeper correctness/security-adjacent analysis)
- Security scanning (code-level vulnerability patterns)
- Dependency auditing (known-vulnerable dependency versions)
- Dead-code detection (via Repository Intelligence's `unreferenced_nodes`)
- Duplicate-code detection
- Broken import detection
- Build verification (does it actually build?)
- Unit tests
- Integration tests
- Documentation validation (does referenced documentation still match
  reality — links, code samples, config keys)
- Configuration verification (schema-valid config files, no missing
  required env vars for the detected deployment target)
- Language-specific quality tools (e.g. `cargo clippy` for Rust, `mypy`
  for Python) as configured per detected stack

## Pipeline execution

```
Trigger (pending write operation from Decision Engine)
        │
        ▼
Select applicable gates (by changed-file language/kind)
        │
        ▼
Run gates concurrently where independent, sequentially where dependent
(e.g. formatting before linting)
        │
        ▼
   ┌───────────────┐
   │ Any failures?  │
   └───┬───────┬────┘
      no       yes
       │         │
       ▼         ▼
   QualityGatePassed   Attempt safe auto-fix (formatting, some lint
                        autofixes, import sorting)
                              │
                        ┌─────┴─────┐
                      fixed      still failing
                        │             │
                        ▼             ▼
                 re-run affected   QualityGateFailed →
                 gates             Policy Engine decides:
                                   request approval / postpone
                                   (per operating mode)
```

## What counts as a "safe" automatic fix

Only deterministic, low-risk transformations are auto-applied without
approval: code formatting, import ordering, trailing whitespace,
straightforward lint autofixes explicitly marked safe by the underlying
tool, and dependency lockfile regeneration when it doesn't change resolved
versions. Anything that changes program behavior is never auto-applied —
it is reported as a failure requiring a real fix or explicit approval.

## Interfaces

- **Consumes:** pending-operation requests from Engineering Decision
  Engine, repository stack info from Repository Intelligence
- **Emits:** `QualityGateStarted`, `QualityGatePassed`,
  `QualityGateFailed`, `AutoFixApplied`
- **Consumed by:** Engineering Decision Engine (gating), Autonomous
  Repository Maintainer (health monitoring), Policy Engine (approval
  routing on failure)

## Configuration

Per repository: which gates are enabled, severity thresholds (e.g. "fail
only on high/critical security findings"), whether auto-fix is allowed at
all, and per-gate tool selection (teams can point AutoGit at their own
existing lint/format configs rather than imposing new ones).
