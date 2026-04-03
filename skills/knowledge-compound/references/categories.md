# Learning Categories

Use these categories as tags in document filenames or front matter for searchability.

## Bug Track Categories

| Category | Examples |
|----------|---------|
| `race-condition` | Concurrency bugs, TOCTOU, async ordering |
| `data-integrity` | Corruption, lost updates, orphaned records |
| `config-drift` | Environment-specific failures, missing env vars |
| `dependency` | Version conflicts, breaking updates, missing packages |
| `encoding` | Unicode, charset, line endings, serialization |
| `auth` | Authentication/authorization failures, token issues |
| `migration` | Database migration failures, data loss during migration |
| `integration` | Third-party API changes, protocol mismatches |

## Knowledge Track Categories

| Category | Examples |
|----------|---------|
| `pattern` | Reusable code/architecture patterns |
| `pitfall` | Common mistakes in this codebase/framework |
| `performance` | Optimization techniques, caching strategies |
| `testing` | Test patterns, fixture strategies, mocking approaches |
| `tooling` | CLI tricks, IDE config, build system quirks |
| `convention` | Project-specific naming/structure conventions |
| `workaround` | Known framework/library limitations and bypasses |

## Decision Track Categories

| Category | Examples |
|----------|---------|
| `architecture` | System design, service boundaries, data flow |
| `technology` | Language/framework/library selection |
| `api-design` | Endpoint structure, versioning, authentication model |
| `data-model` | Schema design, normalization decisions |
| `trade-off` | Performance vs simplicity, consistency vs availability |
| `process` | Workflow decisions, review policies, release strategy |

## File Naming Convention

```
docs/learnings/YYYY-MM-DD-<category>-<brief-slug>.md
```

Examples:
- `docs/learnings/2026-04-02-race-condition-user-session-conflict.md`
- `docs/learnings/2026-04-02-pattern-retry-with-exponential-backoff.md`
- `docs/learnings/2026-04-02-architecture-event-sourcing-for-audit.md`
