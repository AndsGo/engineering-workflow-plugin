# Domain Glossary Convention — CONTEXT.md

**Status:** advisory convention (SHOULD, not MUST). Adoption is opt-in per project; a project without `CONTEXT.md` behaves exactly as before (conservative-wins). This is a convention document, not a versioned contract.

**Origin:** adapted from Matt Pocock's `domain-modeling` skill and CONTEXT-FORMAT (MIT) — https://github.com/mattpocock/skills.

## What it is

`CONTEXT.md` at the repo root is the project's **domain glossary** — the shared language between the humans and the agent. One term per entry, 1–2 sentences each. Its payoff compounds: consistent naming, fewer tokens spent paraphrasing ("the materialization cascade" instead of a sentence), and an agent that navigates the codebase by the same words the team uses.

```markdown
# <Project> — Domain Glossary

**<Term>**:
<1–2 sentence definition, in this project's sense.>
_Avoid_: <banned near-synonyms, comma-separated>
```

## Rules

- **Pure glossary.** Project-specific terms only — words a newcomer or a fresh agent would misuse. NO implementation details, NO architecture prose, NOT a spec or scratchpad. If a general term is used in its ordinary sense, it does not belong here.
- **`_Avoid:` lists are the teeth.** Each term names its banned near-synonyms so the language stays single-sourced (e.g. **Issue tracker** — _Avoid_: backlog manager, issue host).
- **Lazy creation.** Do not scaffold an empty `CONTEXT.md`. Create it the first time there is a real term to record — and only with the user's consent.
- **Inline updates, not batches.** When a session coins a new term or sharpens a fuzzy one, offer to record it right then. Don't collect a list for later.
- **Definitions are opinionated.** A glossary entry states what the term means *here*, including what it excludes.

## READ discipline

When `CONTEXT.md` exists, analysis skills read it before their main work and adopt its vocabulary in output (this is READ step L0 in `learnings-protocol.md`). Reading the glossary is a one-line habit, not a skill invocation.

## What does NOT go here

**Decisions.** A trade-off with reasoning behind it (an ADR in other methodologies) is a `knowledge-compound` **Decision-track learning** — this plugin does not add a separate ADR system. The glossary holds *words*; `docs/learnings/` holds *decisions and experience*. A decision that introduces a new term produces both: a Decision learning and a glossary entry.

## Failure modes (do not do)

- ❌ Turning CONTEXT.md into an architecture document or feature list
- ❌ Scaffolding an empty glossary "for later"
- ❌ Recording generic industry terms that mean nothing project-specific
- ❌ Adding entries without the user's confirmation
- ❌ Duplicating a Decision learning's rationale into a glossary entry (link by term instead)
