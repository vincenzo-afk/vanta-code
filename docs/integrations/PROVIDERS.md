# Remote Provider Integrations

**Crates:** `autogit-providers` (shared trait) + `autogit-providers::github`,
`::gitlab`, `::bitbucket`

## Purpose

Everything AutoGit needs to do against a *remote* Git host — as opposed to
the local repository, which is the Git Engine's job — lives here, behind
a single abstraction so adding a new provider never requires touching
engine logic.

## Provider trait (conceptual)

```rust
#[async_trait]
trait RemoteProvider {
    async fn authenticate(&self, creds: ProviderCredentials) -> Result<()>;
    async fn create_repository(&self, spec: RepoSpec) -> Result<RemoteRepo>;
    async fn open_pull_request(&self, pr: PullRequestSpec) -> Result<PullRequest>;
    async fn list_issues(&self, filter: IssueFilter) -> Result<Vec<Issue>>;
    async fn update_issue(&self, id: IssueId, update: IssueUpdate) -> Result<()>;
    async fn create_release(&self, release: ReleaseSpec) -> Result<Release>;
    async fn workflow_status(&self, reference: &str) -> Result<Vec<WorkflowRun>>;
    async fn ci_status(&self, reference: &str) -> Result<CiStatus>;
    async fn list_discussions(&self, filter: DiscussionFilter) -> Result<Vec<Discussion>>;
    async fn manage_labels(&self, op: LabelOp) -> Result<()>;
    async fn manage_milestones(&self, op: MilestoneOp) -> Result<()>;
    async fn register_webhook(&self, hook: WebhookSpec) -> Result<()>;
    async fn repository_metadata(&self) -> Result<RepoMetadata>;
}
```

Every provider crate (`github`, `gitlab`, `bitbucket`) implements this
trait against its own API. Engines (Decision Engine, Repository
Maintainer, Documentation Intelligence) depend only on `RemoteProvider`,
never on a specific provider's types.

## Handled per provider

- OAuth authentication (device flow / app-based, per provider convention)
- Repository creation and metadata
- Pull requests (open, update, review status)
- Issues (list, create, update, close)
- Releases
- CI/CD workflow status
- Discussions (where supported, e.g. GitHub Discussions)
- Labels
- Milestones
- Webhooks (inbound events — PR updates, issue comments, CI completion —
  translated into AutoGit's internal event bus as `PullRequestOpened`,
  `IssueUpdated`, `WebhookReceived`, etc.)
- Repository metadata sync

## Webhook handling

Incoming webhooks are verified (signature/secret check per provider),
normalized into AutoGit's internal event types, and injected onto the
relevant repository worker's event bus — so, for example, a CI failure
reported via GitHub Actions webhook flows into the Autonomous Repository
Maintainer exactly like a locally-observed build failure would.

## Adding a new provider

1. Implement `RemoteProvider` in a new `autogit-providers::<name>` module.
2. Implement credential handling via the shared Auth Manager (see
   [`../platform/AUTHENTICATION.md`](../platform/AUTHENTICATION.md)).
3. Register the provider in repository configuration
   (`provider = "gitea"`, etc.) — no engine code changes required.

## Interfaces

- **Consumes:** operation requests from Engineering Decision Engine
  (PR/release creation), Repository Maintainer (issue triage, PR
  creation), Project Bootstrap Engine (initial repo metadata/webhook
  setup)
- **Emits:** `PullRequestOpened`, `PullRequestUpdated`, `IssueUpdated`,
  `WebhookReceived`, `CiStatusChanged`
- **Depends on:** Auth Manager (credentials), Policy Engine (some
  provider write actions may themselves require approval depending on
  operating mode)
