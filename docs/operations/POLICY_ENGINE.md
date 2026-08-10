# Policy Engine

**Crate:** `autogit-policy`

## Purpose

The single arbiter of "is this operation allowed to proceed automatically,
or does it need a human?" Every write-capable engine (Engineering
Decision Engine, Repository Maintainer, Documentation Intelligence,
Project Bootstrap) routes through the Policy Engine before an operation
actually executes.

## Inputs to a policy decision

- The repository's configured Operating Mode (Manual/Assisted/Autonomous)
- Per-category overrides (see below)
- The operation's risk classification (low/medium/high — assigned by the
  requesting engine based on operation type)
- Validation & QA Engine results for the operation
- Any explicit policy rules configured for the repository or
  organization

## Policy rule shape (conceptual)

```
PolicyRule {
    scope: OperationCategory,   // Commit | Branch | Merge | Push | PR
                                  // | Release | DependencyUpdate
                                  // | DocsUpdate | IssueAction
                                  // | RepositoryCleanup | ModeChange
    condition: RuleCondition,    // e.g. "risk <= Low", "path matches
                                  // 'SECURITY.md'", "gate:security passed"
    action: Allow | RequireApproval | Deny,
    priority: u32,                // higher priority rules evaluated first
}
```

Rules are evaluated most-specific-first; if no rule matches, the
repository's base Operating Mode applies as the default.

## Example configuration

```toml
[policy.default]
mode = "assisted"

[[policy.overrides]]
scope = "dependency_update"
condition = "risk <= low && gate:security == passed"
action = "allow"

[[policy.overrides]]
scope = "commit"
paths = ["**/auth/**", "SECURITY.md"]
action = "require_approval"

[[policy.overrides]]
scope = "push"
condition = "force == true"
action = "deny"
```

## Approval routing

When a rule resolves to `RequireApproval`, the Policy Engine emits
`ApprovalRequired` with full context (the proposed operation, why it
needs approval, and the reasoning trail from upstream engines) to
whichever surface the user has configured to receive approvals — the MCP
client session, a CLI prompt, or a notification channel wired through
Provider Integrations (e.g. a PR comment).

## `Deny` vs `RequireApproval`

`Deny` is for operations a repository's policy says should never happen
automatically regardless of who asks — force pushes and destructive
branch deletion are sensible defaults. `RequireApproval` is for anything
that's fine with a human's blessing. Only repository owners (via
configuration, not via an agent's MCP call) can change a `Deny` rule.

## Interfaces

- **Consumes:** operation requests (with risk classification) from any
  write-capable engine, Validation & QA Engine results
- **Emits:** `ApprovalRequired`, `OperationApproved`, `OperationDenied`,
  `OperationBlocked`
- **Configured via:** [`CONFIGURATION.md`](CONFIGURATION.md) — policy
  rules are repository-level config, versionable alongside the repository
  itself (e.g. an `autogit.toml` policy section can itself live in the
  repository, reviewed like any other config change)

## Auditability

Every policy decision (including `Allow` decisions, not just blocks) is
recorded to the Engineering Timeline and platform logging system, so "why
was this allowed to happen automatically?" is always answerable after the
fact.
