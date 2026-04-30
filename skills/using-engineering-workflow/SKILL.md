---
name: using-engineering-workflow
description: "Use when starting any session with engineering work, or when unsure which engineering-workflow skill to invoke for a given task. Also use when flow gate questions arise (should I review before shipping? should I run security audit?)."
---

# Engineering Workflow — Flow Control

This plugin provides 9 specialized skills that extend Superpowers with process and tool capabilities. These rules govern when and how they are invoked.

## Relationship with Superpowers

**Superpowers is the discipline layer. This plugin is the process and tool layer.**

- Superpowers Iron Laws (TDD, systematic debugging, verification) are NEVER overridden
- This plugin adds structured review, knowledge accumulation, security audit, and release workflow ON TOP of Superpowers discipline
- When both plugins could apply, Superpowers discipline applies first, then this plugin's process

## Flow Control Rules

### Rule 1: Skill Routing (MUST follow)

Match the user's intent to the correct skill. Check this routing table BEFORE responding:

| User intent | Skill | Priority |
|-------------|-------|----------|
| Product idea, feature exploration | `superpowers:brainstorming` | SP first |
| Write implementation plan | `superpowers:writing-plans` | SP first |
| Review plan before execution | `plan-review-personas` | This plugin |
| Implement code | `superpowers:subagent-driven-development` | SP first |
| Test page in browser, "does this work" | `e2e-browser-test` | This plugin |
| Review code, check diff | `structured-review` | This plugin |
| Security sensitive changes | `security-audit` | This plugin |
| Ship, commit, create PR | `ship-and-pr` | This plugin |
| Update docs after shipping | `document-sync` | This plugin |
| Resolve PR review comments | `resolve-pr-feedback` | This plugin |
| Record learnings, compound | `knowledge-compound` | This plugin |
| Weekly retro | `engineering-retro` | This plugin |
| Debug, fix bug | `superpowers:systematic-debugging` | SP first |

### Rule 2: Flow Sequence Gates

These transitions are enforced. Do not skip forward without completing the prior step.

```
GATE 1: Plan → Plan Review
  After superpowers:writing-plans produces a plan for non-trivial work,
  invoke plan-review-personas BEFORE execution.
  Exception: trivial plans (single task, < 30 min) skip review.

GATE 2: Implementation → Review
  After implementation is complete, invoke structured-review
  BEFORE ship-and-pr.
  Exception: documentation-only or test-only changes.

GATE 3: Review → Ship
  structured-review must produce PASS or PASS WITH NOTES
  before ship-and-pr proceeds.
  If BLOCK: fix issues first, re-review.

GATE 4: Ship → Document Sync
  After ship-and-pr creates a PR, suggest document-sync
  if the diff touches documented behavior.

GATE 5: Session End → Knowledge Capture
  Before ending a session that involved problem-solving,
  debugging, or architectural decisions, offer knowledge-compound.
```

### Rule 3: Anti-Skip Enforcement

These thoughts mean STOP — you are about to skip a flow gate:

| Thought | Required action |
|---------|----------------|
| "Let me just commit this quickly" | GATE 2+3: Run structured-review first |
| "Tests pass, ship it" | GATE 3: Review is not the same as testing |
| "The plan is obvious, start coding" | GATE 1: Even obvious plans benefit from a quick feasibility check |
| "Docs are fine, skip sync" | GATE 4: Check, don't assume. document-sync takes 2 minutes. |
| "Nothing to learn from this session" | GATE 5: Offer knowledge-compound. Let the user decide. |
| "Security isn't relevant here" | Check file patterns: auth, input, API, secrets, config |

### Rule 4: Learnings Discipline

All learning-touching skills MUST follow `references/learnings-protocol.md`.

In short:
- **READ:** INDEX-first → 📚 synthesis preferred → targeted reads → Grep fallback. Cite sources.
- **WRITE:** suggest `knowledge-compound`, never write directly. Frontmatter required (`track`, `status`).
- **MAINTAIN:** `learnings-refresh` skill (ships in v1.2). Until then, manual curation against the protocol is acceptable.

If `docs/learnings/INDEX.md` does not exist and the project has ≥30 learnings, consider hand-writing one (or wait for v1.2 to automate).

This is not optional. Prior knowledge lookup prevents repeating mistakes. Knowledge output prevents losing insights.

### Rule 5: RETHINK Limit

`plan-review-personas` has a hard cap: **2 consecutive RETHINK verdicts**. After the second RETHINK, STOP and require human intervention. Do not loop back to brainstorming a third time.

### Rule 6: Severity Routing

| structured-review verdict | Next step |
|--------------------------|-----------|
| PASS | → ship-and-pr |
| PASS WITH NOTES | → ship-and-pr (notes included in PR description) |
| BLOCK | → fix issues → re-review (do NOT ship) |

| security-audit verdict | Next step |
|-----------------------|-----------|
| PASS | → continue to ship |
| FAIL | → fix P0/P1 issues → re-audit (do NOT ship) |

## Available Skills (9)

| Skill | Trigger |
|-------|---------|
| `structured-review` | Code review before merge |
| `knowledge-compound` | Document learnings after tasks |
| `plan-review-personas` | Stress-test plans before execution |
| `ship-and-pr` | Commit, push, create PR |
| `security-audit` | Security review on sensitive changes |
| `engineering-retro` | Weekly/milestone retrospective |
| `e2e-browser-test` | Browser testing on affected pages |
| `resolve-pr-feedback` | Batch-process PR review comments |
| `document-sync` | Sync docs to match shipped code |

## Workflow State

The SessionStart hook reports:
- `LEARNINGS_COUNT` — number of project learnings in `docs/learnings/`
- `REVIEW_DONE` — whether a review artifact exists from this session
- `PLAN_REVIEWED` — whether a plan review was done

Use this state to enforce gates contextually. If `REVIEW_DONE=true`, Gate 2 is satisfied.
