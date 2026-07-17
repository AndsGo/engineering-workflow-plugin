---
track: knowledge
status: active
category: pattern
last-verified: 2026-07-06
---
# Scaffolding vs Invariant — match process weight to change size

**Track:** Knowledge
**Date:** 2026-07-06
**Applies to:** general (engineering process design, agentic workflows, skill/plugin authoring)

## Context

Recurring question: as models get stronger, do rigid, fixed engineering processes (mandatory TDD micro-steps, unconditional review gates, phase choreography) still help — or start to hurt? Applies whenever you design a workflow, a plugin, a review gate, or decide how much ceremony a task deserves.

## Guidance

Don't ask "how much process?" Ask **"is this rule scaffolding, or an invariant?"** — they move in opposite directions as capability rises:

- **Scaffolding (HOW / execution choreography):** "write the failing test, run it, watch it fail, minimal code, commit"; "dispatch a fresh subagent per task"; "explore before fixing." Instructions about *how the executor moves*. A strong model already does most of this; prescribing the micro-steps adds token cost and can anchor it **below** its own judgment. **Value decays as capability rises — retire it.**
- **Invariant (WHAT-must-be-true / guarantees):** "no code merges without an adversarial review it didn't write itself"; "success is a check that can actually fail"; "removing content must ask a human"; "irreversible actions confirm first." These constrain *which states are allowed*. A stronger model produces more plausible-looking output faster, so an undetected wrong target costs more. **Value rises as capability rises — keep and strengthen it.**

Key reframe: **TDD is both** — TDD-as-ritual (micro-steps → scaffolding) vs TDD-as-specification (the test is the executable definition of "correct," written first to pin the target → invariant). Keep the specification essence at every level; relax the ritual.

Making "auto-scale process to change size" safe requires four bounds, because prose alone is administered to the same pressured model that skips it:
1. a **constant floor** of invariants that never scales away;
2. **one-directional escalation** enforced by a mandatory checkpoint (not voluntary mid-task monitoring), ideally against the *actual diff*;
3. **round-up under genuine uncertainty** — but as a tie-breaker only (over-escalating everything re-creates the rigidity you were removing);
4. an **announced decision** the human can veto cheaply.

## When to Apply

- Designing or trimming any workflow/gate/skill and tempted to add (or keep) a mandatory step.
- Deciding whether a task needs the full pipeline or can be done directly ("this feels like over-process").
- Reviewing a process that "worked for weaker models" — ask which rules were capability crutches (drop) vs correctness guarantees (keep).

## When NOT to Apply

- Don't use "scaffolding decays" to justify dropping an **invariant** (review, an oracle that can fail, irreversibility guards). Those are not scaffolding.
- Don't drop process AND under-invest in the target/oracle — that yields "fast, confident, wrong," the worst outcome, which strong models hit more cheaply.

## Examples

- Plugin v1.4 `using-engineering-workflow` Rule 0 Triage operationalizes this: T0–T2 tiers scale scaffolding; a non-scaling invariant floor + completion-time checkpoint hold the guarantees. See `docs/specs/2026-07-04-process-auto-scaling-design.md` (§3.1 makes the distinction explicit).
- The value in `document-sync` v2 concentrated in its fixtures (oracles) + anti-self-certification gates, not its 7-phase choreography — a datapoint that oracle + adversarial verification are the invariants worth keeping.

## Related

- [[2026-07-06-blind-eval-not-self-graded]] — the "check that can fail" invariant, applied to validating LLM-facing artifacts.
- [[2026-07-17-mattpocock-borrowing-tiers]] — this lens applied to a borrowing decision (invariant-strengthening adopted first; orchestration scaffolding gated on real triggers).
- [[2026-07-17-invocation-dichotomy-context-economics]] — the per-standing-instruction cost economics, applied to skill invocation modes.
- `docs/specs/2026-07-04-process-auto-scaling-design.md` — the v1.4 decision this lens drove.
