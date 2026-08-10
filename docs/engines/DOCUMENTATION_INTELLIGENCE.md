# Documentation Intelligence Engine

**Crate:** `autogit-docs-engine`

## Purpose

Ensures repository documentation always reflects the actual project.
Documentation is treated as a **generated projection** of repository
reality (the Knowledge Graph + Repository Memory + Engineering Timeline),
not a static artifact maintained by hand and left to rot.

## Documents it owns

- README.md
- API documentation
- Architecture diagrams
- Deployment instructions
- CHANGELOG.md
- Migration guides
- Environment/configuration documentation
- Usage examples
- Contribution guides
- Release notes
- Security documentation
- Developer onboarding materials

## Trigger conditions

The engine listens for `DocsOutOfSync` from the Engineering Decision
Engine, which fires whenever a Knowledge Graph diff touches a "documented
surface" — a route, public API, environment variable, dependency,
deployment target, or architectural boundary that existing docs reference
or that convention says should be documented.

## Generation pipeline

```
DocsOutOfSync (which graph nodes changed)
        │
        ▼
Identify affected doc sections (doc-to-graph-node index)
        │
        ▼
Gather structured context:
  - current graph state for affected nodes
  - relevant Repository Memory records
  - relevant Engineering Timeline entries
  - prior doc content (to preserve human-authored prose where possible)
        │
        ▼
AI Reasoning Layer drafts updated section(s) against a
schema (see AI_REASONING_LAYER.md)
        │
        ▼
Validation & QA Engine: documentation validation gate
(links resolve, code samples compile/run where feasible,
referenced config keys actually exist)
        │
        ▼
DocsRegenerated → queued as part of the same commit/PR as the
underlying code change (never a separate, lagging "docs commit"
unless the operating mode requires separate review)
```

## Preserving human intent

The engine never blindly overwrites human-authored prose. It maintains a
doc-to-graph-node index and only regenerates the specific sections tied to
changed nodes, using clearly-delimited generated regions where full
regeneration is appropriate (e.g. an API reference table) versus
surgical, minimal edits where a human narrative surrounds a changed
detail (e.g. a "Getting Started" walkthrough).

## Architecture diagrams

Generated as text-based diagrams (Mermaid) derived directly from the
Knowledge Graph's service/module/dependency edges, so they never drift
independently of the graph they represent — regenerating a diagram is a
graph query plus a template, not a separate manually-maintained asset.

## Interfaces

- **Consumes:** `DocsOutOfSync` (Decision Engine), graph queries
  (Repository Intelligence), Repository Memory records, Engineering
  Timeline entries
- **Emits:** `DocsRegenerated`, `DocsValidationFailed`
- **Delegates to:** AI Reasoning Layer (drafting), Validation & QA Engine
  (verification)
- **Used by:** Project Bootstrap Engine (initial doc generation),
  Autonomous Repository Maintainer (detecting stale docs proactively)
