# Configuration Reference

**Crate:** `autogit-config`

## Configuration layers

Configuration is resolved in layers, each overriding the previous:

1. **Built-in defaults** (compiled into `autogit-config`)
2. **Global user config** — `~/.config/autogit/config.toml` — applies to
   every repository managed by this AutoGit instance
3. **Repository config** — `<repo>/.autogit/config.toml` — checked into
   the repository itself, reviewable like any other file
4. **Runtime overrides** — set via MCP tool calls or CLI for the current
   session only, never persisted unless explicitly saved

## Top-level structure (illustrative)

```toml
[repository]
name = "example-service"
languages = ["rust", "typescript"]

[runtime]
debounce_ms = 3000
max_concurrent_analysis_jobs = 4

[operating_mode]
default = "assisted"           # manual | assisted | autonomous

[policy]
# see docs/operations/POLICY_ENGINE.md for full rule syntax
[[policy.overrides]]
scope = "dependency_update"
condition = "risk <= low"
action = "allow"

[validation]
gates = ["format", "lint", "static_analysis", "security_scan",
         "dependency_audit", "dead_code", "duplicate_code",
         "broken_imports", "build", "unit_tests", "integration_tests",
         "docs_validation", "config_validation"]
auto_fix = true
fail_on = "high"                # minimum severity that blocks

[documentation]
auto_regenerate = true
managed_files = ["README.md", "CHANGELOG.md", "docs/**"]

[reasoning]
provider = "anthropic"
model = "claude-sonnet-5"
max_retries = 2

[providers.github]
enabled = true
webhook_secret_ref = "env:AUTOGIT_GH_WEBHOOK_SECRET"

[scheduler]
maintenance_scan_cron = "0 */6 * * *"   # every 6 hours

[storage]
backend = "sqlite"               # sqlite | sled
path = ".autogit/state.db"

[telemetry]
log_level = "info"
metrics_enabled = true
```

## Secrets

Configuration files never contain raw secrets. Any credential-shaped
value is referenced indirectly (`env:VAR_NAME` or a reference into the
platform Auth Manager's secure store) and resolved at runtime — see
[`../platform/AUTHENTICATION.md`](../platform/AUTHENTICATION.md).

## Hot reload

Global and repository config changes are picked up by the Configuration
Manager without restarting the runtime; affected repository workers are
notified via a `ConfigurationChanged` event and re-derive any cached
settings (e.g. active quality gates) rather than requiring a full worker
restart.

## Validation

The Configuration Manager validates config against a schema at load time
and on every hot-reload; invalid configuration is rejected with a
specific error rather than silently falling back to defaults, so a typo
in `.autogit/config.toml` never results in AutoGit quietly running with
unintended settings.

## Per-repository config lives in the repository

Because `.autogit/config.toml` is checked into the repository itself,
policy and validation configuration changes go through the exact same
review process (PR review, approval) as any other code change — the
configuration governing AutoGit's autonomy is itself subject to the same
scrutiny AutoGit applies to everything else.
