---
name: grill-me
description: "Interview the user relentlessly about a plan, design, or idea until reaching shared understanding, resolving each branch of the decision tree with a recommended answer per question. The live, synchronous alternative to the async plan-review-personas. Use when the user wants to stress-test a plan/design interactively, or says 'grill me', '质询我的计划', '拷问这个设计', 'poke holes in this'."
---

# Grill Me

Interactive, human-in-the-loop stress-testing of a plan, design, or idea. Complements the other planning skills: `superpowers:brainstorming` *explores* what to build (divergent); `plan-review-personas` runs *async adversarial agents* over a finished plan; **grill-me** is the *synchronous* version — you and the user, one question at a time, until the design's decision tree is resolved.

**Origin:** adapted from Matt Pocock's `grill-me` skill (MIT) — https://github.com/mattpocock/skills.

## When to Use

- The user has a plan/design/idea on the table and wants it challenged before committing.
- Triggers: "grill me", "质询我的计划", "拷问这个设计", "poke holes in this", "stress-test this with me".

## When NOT to Use

- No concrete proposal yet → use `superpowers:brainstorming` (explore first).
- A written plan needs adversarial coverage without a live back-and-forth → use `plan-review-personas` (async agents).
- You just want code reviewed → `structured-review`.

## Floor (before you start)

READ relevant prior knowledge per `using-engineering-workflow/references/learnings-protocol.md` — scan `docs/learnings/` (Decision-track especially) so your questions are informed by past decisions and pitfalls, not naïve.

## The Method

1. **Interview relentlessly, ONE question at a time.** Never batch questions — a single question per turn, then wait for the answer. Walk *down* the decision tree: resolve dependencies between decisions one by one (a later question often depends on an earlier answer).
2. **Recommend an answer for every question.** Don't just ask — state the answer you'd choose and *why* (one line). The user corrects or confirms; either way you converge faster than open-ended interrogation.
3. **Explore the codebase instead of asking, when the answer is discoverable.** If a question can be settled by reading a file, running a grep, or checking git history — do that first and report what you found, rather than spending a question on it.
4. **Surface assumptions and failure modes**, not just preferences: "this assumes X — is that true?", "what happens when Y fails halfway?".

## Exit Criteria

Stop when **shared understanding is reached**: every branch of the decision tree is resolved, no open dependency remains, and the user has no further "but what about…". State explicitly that you've reached the end (don't grill forever) and summarize the resolved decisions in a few lines.

## Hand-off

If the grilling surfaced a non-obvious decision (a real trade-off where reasoning drove the choice), suggest recording it via `knowledge-compound` (Decision track). If it exposed that the underlying idea is under-explored, route back to `superpowers:brainstorming`; if the plan itself has holes, to `superpowers:writing-plans` / `plan-review-personas`.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "Let me ask these five things at once" | One question per turn. Batching breaks the dependency-resolution flow. |
| "I'll just ask the user where X is" | If a file/grep/git answers it, look — don't spend a question. |
| "I'll ask without suggesting an answer" | Every question carries your recommended answer + why. |
| "Keep grilling, there's always more" | Converge. When the tree is resolved, say so and stop. |
