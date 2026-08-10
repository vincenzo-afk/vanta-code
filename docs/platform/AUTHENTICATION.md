# Authentication & Credential Management

**Crate:** `autogit-auth`

## Purpose

The single owner of every credential AutoGit holds: provider OAuth
tokens, LLM API keys, webhook secrets, and MCP client scoping. No other
crate stores or transmits raw secrets — they request resolved
credentials from this crate at the point of use.

## What it manages

- **Provider credentials** — OAuth tokens/app installations for GitHub,
  GitLab, Bitbucket (and any provider plugin)
- **Reasoning provider credentials** — API keys for the configured LLM
  backend(s)
- **Webhook secrets** — used to verify inbound provider webhooks
- **MCP client scoping** — which connected agent/session is permitted to
  address which repositories

## Storage

Secrets are encrypted at rest using OS-native secure storage where
available (Keychain on macOS, Credential Manager on Windows, Secret
Service/libsecret on Linux), falling back to an encrypted file store
(key derived from an OS-protected master key) where no OS secret store is
available. Secrets are never written to the same embedded storage used
for the Knowledge Graph/Memory (see
[`STORAGE.md`](STORAGE.md)) — a compromise or backup of that store should
never expose credentials.

## Credential resolution

Configuration files reference credentials indirectly
(`env:AUTOGIT_GH_TOKEN`, or `auth:github.example-org`); the Auth Manager
resolves these references at the moment a provider/reasoning call is
about to be made, and the resolved secret is held in memory only for the
duration of that call.

```rust
trait CredentialResolver {
    async fn resolve(&self, reference: &CredentialRef) -> Result<Secret>;
}
```

## OAuth flows

Provider integrations initiate OAuth (device-code flow where supported,
otherwise a local-loopback browser flow) through this crate; the Auth
Manager owns token refresh so provider crates never handle raw refresh
logic themselves.

## MCP scoping

Every MCP connection is associated with an access scope — which
repositories it may address and which tool categories it may invoke (e.g.
a read-only integration might be scoped to `repository_analysis` and
`objective_status` but not `prepare_release`). Scopes are configured per
connection, not inferred from the tool call itself, so a compromised or
misbehaving agent session cannot escalate its own access.

## Interfaces

- **Consumed by:** Provider Integrations (OAuth tokens), AI Reasoning
  Layer (LLM API keys), MCP Server (connection scoping), Provider
  Integrations' webhook handlers (secret verification)
- **Never consumed by:** Repository Intelligence, Repository Memory,
  Engineering Timeline, or any engine with no legitimate need for
  credentials — access is need-to-know, enforced by which trait each
  engine is given a reference to at construction time
