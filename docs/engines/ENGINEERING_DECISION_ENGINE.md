# Engineering Decision Engine

**Crate:** `autogit-decision`

## Purpose

The primary intelligence of AutoGit. Every other engine feeds this one
information; this engine decides what, if anything, should actually
happen to the repository.

## What it classifies work as

- Completed feature
- Partial implementation
- Refactor
- Documentation improvement
- Infrastructure modification
- Dependency update
- Security fix
- Performance optimization
- Hotfix
- Experimental work
- Unfinished implementation

Classification draws on: Intent Tracking Engine's current objective and
progress, Repository Intelligence's impact analysis of changed graph
nodes, Development Observer's build/test outcomes, and Repository
Memory's history of similar past changes.

## The core rule: no commits by proxy metrics

Commits **never** happen because N files changed or because a timer
elapsed. A commit happens only when the Decision Engine concludes, from
the evidence above, that:

1. A meaningful engineering milestone has been reached, **and**
2. Tests have passed according to the repository's configured policy,
   **and**
3. Documentation is sufficiently updated (or a documentation-update task
   has been queued as part of the same milestone), **and**
4. Repository quality gates (Validation & QA Engine) are satisfied.

If any condition fails, the Decision Engine either withholds action, asks
the Validation Engine for auto-fixes, or — depending on operating mode —
raises an `ApprovalRequired` event through the Policy Engine.

## Decisions this engine makes

| Decision | Inputs | Output event |
|---|---|---|
| Commit now? | intent progress, quality gates, doc sync | `MilestoneReached` → triggers Git Engine commit |
| Branch creation | objective scope, current branch policy | `BranchRecommended` |
| Merge readiness | validation results, review status, target branch protections | `MergeReadySignal` |
| Release readiness | changelog completeness, version policy, test suite health | `ReleaseReady` |
| Version bump (semver) | change classification (feature/fix/breaking) | `VersionBumpRecommended` |
| Changelog generation trigger | milestone type | delegated to AI Reasoning Layer |
| Documentation regeneration trigger | graph diff touching documented surfaces | `DocsOutOfSync` |
| Issue resolution | fix classification + linked issue reference | `IssueResolutionCandidate` |
| Rollback recommendation | post-merge regression signal (build/test failure trend) | `RollbackRecommended` |
| Repository cleanup | dead code / stale branch findings from Maintainer | `CleanupRecommended` |

## Decision pipeline

```
Observation + Intent + Graph impact
              │
              ▼
     Classify work type
              │
              ▼
   Ask Validation & QA Engine to run gates
              │
        ┌─────┴─────┐
     pass          fail
        │             │
        ▼             ▼
  Ask AI Reasoning   Attempt safe auto-fix
  Layer for commit    (Validation Engine)
  message / doc plan       │
        │              ┌───┴───┐
        ▼            fixed   still failing
  Check Policy Engine   │         │
  for required approval ▼         ▼
        │          re-run gate  ApprovalRequired /
        ▼                        postpone (per mode)
  Emit MilestoneReached
```

## Interfaces

- **Consumes:** `ObjectiveProgressUpdated`, `ObjectiveReadyForCommit`
  (Intent Tracker), `GraphEdgeChanged`/`AnalysisCompleted` (Repository
  Intelligence), `QualityGatePassed`/`QualityGateFailed` (Validation
  Engine), `BuildFinished`/`TestRunFinished` (Observer), maintenance
  findings (Repository Maintainer)
- **Emits:** `MilestoneReached`, `BranchRecommended`, `ReleaseReady`,
  `VersionBumpRecommended`, `DocsOutOfSync`, `IssueResolutionCandidate`,
  `RollbackRecommended`, `CleanupRecommended`
- **Delegates to:** Git Engine (execution), AI Reasoning Layer (content
  generation), Policy Engine (approval gating)

## Configurability

Teams can tune, per repository: minimum test coverage delta, whether
documentation sync is a hard blocker or a follow-up task, semver policy
strictness, and which milestone types are allowed to auto-commit even in
Assisted Mode (e.g. hotfixes might be allowed to fast-track).
