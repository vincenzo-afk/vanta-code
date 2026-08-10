# AI Reasoning Layer

**Crate:** `autogit-reasoning`

## Purpose

The single place where AutoGit talks to language models. Every commit
message, pull request description, issue summary, release note,
documentation update, and changelog entry is produced here — never
generated ad hoc inside another engine.

## Why raw diffs are never sent to the LLM

Raw Git diffs are a poor prompt: they lack the "why," conflate unrelated
hunks, and give the model no grounding in repository history or
convention. Instead, this layer constructs **structured semantic
context**:

```
ReasoningRequest {
    task: CommitMessage | PrDescription | IssueSummary
        | ReleaseNotes | ChangelogEntry | DocSection
        | BootstrapProse | MaintenanceFixExplanation,

    intent: Objective,                      // from Intent Tracker
    affected_components: [GraphNode],       // from Repository Intelligence
    dependency_changes: [DependencyDelta],
    testing_outcomes: TestSummary,
    documentation_changes: [DocDelta],
    relevant_memory: [MemoryRecord],        // from Repository Memory
    relevant_timeline: [TimelineEntry],
    validation_results: ValidationSummary,
}
```

## Structured output, schema-validated

Every response is requested and parsed against a predefined schema for
its task type (e.g. a `CommitMessage` schema with `summary`, `body`,
`breaking_change: bool`, `type: Feat|Fix|Refactor|Docs|Chore|...`). Output
that fails schema validation is retried with the validation error fed
back to the model before it's ever handed to another engine; it is never
passed through as free-form text that downstream engines have to
re-parse.

## LLM interface abstraction

This crate owns the only outbound LLM client in the system. It supports
pluggable providers/models (configurable per deployment — local models,
hosted APIs) behind a single trait, so no other engine has a hard
dependency on a specific model provider.

```rust
#[async_trait]
trait ReasoningProvider {
    async fn complete(&self, request: ReasoningRequest)
        -> Result<ReasoningResponse, ReasoningError>;
}
```

## Responsibilities by task type

| Task | Primary consumer |
|---|---|
| Commit message | Engineering Decision Engine → Git Engine |
| PR description | Provider Integrations |
| Issue summary / triage note | Autonomous Repository Maintainer |
| Release notes | Engineering Decision Engine (release flow) |
| Changelog entry | Documentation Intelligence Engine |
| Documentation section drafts | Documentation Intelligence Engine |
| Bootstrap prose (README, CONTRIBUTING) | Project Bootstrap Engine |
| Maintenance fix explanation | Autonomous Repository Maintainer |
| Repository memory summarization | Repository Memory |

## Interfaces

- **Consumes:** structured `ReasoningRequest`s from any engine listed
  above (never raw diffs, never unstructured free text)
- **Emits:** schema-validated `ReasoningResponse`s; also emits
  `ReasoningFailed` when a request cannot produce a valid response after
  configured retries, which callers must handle explicitly (never silently
  falling back to unvalidated output)
- **Consumed by:** Engineering Decision Engine, Documentation Intelligence
  Engine, Project Bootstrap Engine, Autonomous Repository Maintainer

## Cost & rate awareness

Requests are batched and cached where safe (e.g. identical context
producing identical output within a short window is not re-requested),
and the layer exposes token/cost metrics to the platform Telemetry system
so operators can see reasoning cost per repository.
