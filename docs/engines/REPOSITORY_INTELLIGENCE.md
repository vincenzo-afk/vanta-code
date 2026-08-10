# Repository Intelligence Engine

**Crate:** `autogit-intelligence`

## Purpose

The foundation of AutoGit. Continuously builds and maintains a semantic
understanding of the entire software system — not a bag of files, but a
graph of components and their relationships.

## What it understands

- Files, directories, and their roles (source, config, test, generated)
- Functions, classes, methods, modules
- APIs and routes (REST/GraphQL/RPC handlers)
- Database schemas and ORM models
- Environment variables and their usage sites
- Services, packages, imports, and dependency graphs
- Frontend pages/components and backend services
- Infrastructure-as-code and deployment definitions
- Tests (and what they cover)
- Documentation and its relationship to the code it describes
- Build pipelines and CI/CD configuration
- External integrations (third-party APIs, webhooks, SDKs)

## How it works

1. **Parsing** — Tree-sitter parsers per detected language produce ASTs.
   Language-specific analyzers walk these ASTs to extract symbols,
   definitions, references, and framework-specific patterns (e.g. route
   decorators, ORM model classes, env var access).
2. **Graph construction** — extracted entities become nodes; relationships
   (calls, imports, extends, implements, tests, documents, configures,
   deploys) become edges in a **Software Knowledge Graph**.
3. **Persistence** — the graph is persisted in embedded storage (SQLite or
   Sled, see [`../platform/STORAGE.md`](../platform/STORAGE.md)), not held
   only in memory, so workers can resume instantly after restart.
4. **Incremental updates** — on file change events from the Development
   Observer, only the affected subgraph is re-parsed and diffed against
   the persisted graph; the engine never rebuilds the whole graph from
   scratch unless explicitly requested (e.g. after a `.gitignore` or
   language toolchain change invalidates cached assumptions).

## Knowledge graph shape (conceptual)

```
Node kinds:  File, Function, Class, Module, Route, Model, EnvVar,
             Service, Package, Test, DocSection, ConfigKey,
             DeploymentTarget, ExternalIntegration

Edge kinds:  defines, imports, calls, extends, implements, tests,
             documents, configures, depends_on, deploys_to,
             reads_env, exposes_route
```

## Interfaces

- **Emits:** `GraphNodeAdded`, `GraphNodeUpdated`, `GraphNodeRemoved`,
  `GraphEdgeChanged`, `AnalysisCompleted`
- **Consumes:** `FileChanged`, `RepositoryRegistered`,
  `DependencyInstalled` (from Development Observer)
- **Queried by:** Engineering Decision Engine (impact analysis), Intent
  Tracking Engine (mapping edits to objectives), Documentation
  Intelligence Engine (what needs re-documenting), AI Reasoning Layer
  (structured context for prompts)

## Query API (used internally by other engines)

- `find_symbol(name) -> Vec<GraphNode>`
- `impacted_by(node_id) -> Vec<GraphNode>` — reverse-dependency lookup
- `subgraph_for_path(path) -> Subgraph`
- `unreferenced_nodes(kind) -> Vec<GraphNode>` — dead code candidates
- `routes() / models() / env_vars() / services()` — typed views used by
  Bootstrap and Documentation engines

## Language support strategy

Ships with first-class Tree-sitter grammars for the most common
ecosystems (Rust, TypeScript/JavaScript, Python, Go, Java) and falls back
to a generic file/symbol-level model (no deep AST understanding) for
unsupported languages, so no repository is left completely opaque.
