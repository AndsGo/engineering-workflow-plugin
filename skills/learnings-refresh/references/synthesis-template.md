# Synthesis Doc Template

Use when `learnings-refresh` flags ≥3 same-category learnings worth unifying. Copy the template below; fill the placeholders; place at `docs/learnings/YYYY-MM-DD-<synthesis-slug>.md`.

## Template

```markdown
---
track: knowledge
status: active
category: <category from cluster, e.g., pattern, pitfall>
last-verified: <YYYY-MM-DD>
---

# <Synthesis Title — names the unifying principle>

**Track:** Knowledge (Synthesis)
**Synthesizes:** N prior learnings (list in Related section below)

## Context

Why these N learnings turn out to be the same principle on different surfaces. 1-2 paragraphs.

## The Common Principle

State the unifying rule in 1-3 sentences.

## The N Faces (one paragraph per source learning)

### Face 1 — `<source-learning-1-filename>`

1-paragraph summary of the source's specific surface.

### Face 2 — `<source-learning-2-filename>`

...

## Common Decision Rule

If applicable: a checklist or audit prompt that covers all faces. (e.g., "When you write or review code that consumes external input, ask: 1. Where is the schema defined? 2. Where is the earliest enforcement point? ...")

## When to Apply

- Bullet list of situations where this synthesized principle applies.

## When NOT to Apply

- Bullet list of edge cases or contrarian situations.

## Examples in This Codebase

Cite the strongest example from each face, or one representative example.

## Related — Source Learnings (in chronological order)

- [<Source 1 title>](<source-1-filename.md>) (date)
- [<Source 2 title>](<source-2-filename.md>) (date)
- ... (one per face)

## Related — Adjacent Patterns

- [<Adjacent pattern>](<filename.md>) — how it differs
```

## After Writing the Synthesis

For EACH source learning that the synthesis covers, edit its `Related:` section to add a backlink:

```markdown
- **[<Synthesis Title>](<synthesis-filename.md>)** — synthesis: this learning is one face of the same principle
```

This makes the knowledge graph bidirectional. `learnings-refresh` will offer to do this automatically; user confirms each backlink edit.
