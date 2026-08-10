# Project Bootstrap Engine

**Crate:** `autogit-bootstrap`

## Purpose

Makes repository initialization completely autonomous. Given a new or
under-scaffolded repository, this engine analyzes it and generates every
standard asset a production-ready repository needs.

## Analysis phase

Before generating anything, the engine determines:

- Technology stack (languages, frameworks, runtime versions)
- Project goals (inferred from any existing README/description, or asked
  of the initiating agent/user if genuinely ambiguous)
- Deployment targets (containers, serverless, static hosting, etc. —
  inferred from existing infra files or asked)
- Package manager(s) in use
- Testing framework(s) present or conventional for the detected stack
- Existing repository structure (to avoid clobbering anything already
  present — Bootstrap always merges, never overwrites blindly)

This reuses Repository Intelligence's stack-detection rather than
duplicating it.

## Generated assets

| File | Notes |
|---|---|
| `README.md` | Structured from detected stack, goals, and (once available) Documentation Intelligence Engine conventions |
| `LICENSE` | Only when a license choice is known/confirmed — never assumed silently |
| `.gitignore` | Stack-appropriate, merged with any existing entries |
| `.gitattributes` | Line-ending and diff-strategy rules appropriate to detected file types |
| `CONTRIBUTING.md` | Includes detected build/test/lint commands |
| `CODE_OF_CONDUCT.md` | Standard template, configurable |
| `SECURITY.md` | Vulnerability reporting process template |
| `CHANGELOG.md` | Seeded, then owned going forward by Documentation Intelligence Engine |
| `.editorconfig` | Derived from detected formatter/linter config |
| Docker configuration | Only when a containerized deployment target is detected/confirmed |
| CI/CD workflows | Wired to detected build/test/lint commands and target CI provider |
| Issue templates | Bug report / feature request, tailored to detected stack |
| Pull request template | Includes the quality-gate checklist relevant to this repo |
| Release workflow | Tied to the versioning policy configured in the Decision Engine |
| Environment templates (`.env.example`) | Derived from env vars discovered by Repository Intelligence |
| `robots.txt`, `sitemap.xml` | Only for web-facing projects where applicable |
| Dependency configuration | Lockfile conventions, registry config where relevant |
| Formatting/linting configuration | Only generated if none exists; existing config is always respected |
| Testing configuration | Wired to detected test framework |
| Repository metadata | Provider-specific metadata (topics, description) via Provider Integrations |

## Never overwrite silently

Any file that already exists is treated as authoritative. Bootstrap either
leaves it untouched, proposes a diff for approval (Assisted/Manual mode),
or — in Autonomous mode with explicit policy permission — merges
non-conflicting additions only.

## Interfaces

- **Consumes:** `RepositoryRegistered`, stack analysis from Repository
  Intelligence
- **Emits:** `BootstrapAssetGenerated`, `BootstrapCompleted`
- **Delegates to:** AI Reasoning Layer (README/CONTRIBUTING prose),
  Validation & QA Engine (verify generated CI actually runs, generated
  Docker builds), Git Engine (initial commit), Provider Integrations
  (repository metadata, initial webhook setup)

## Re-running Bootstrap on an existing repository

Bootstrap is idempotent and can be re-invoked (e.g. "add a security
policy we don't currently have") — it always re-runs the analysis phase
against current repository state rather than caching stale assumptions
from first initialization.
