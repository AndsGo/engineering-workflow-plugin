---
name: using-engineering-workflow
description: "Use when starting any session with engineering work, or when unsure which engineering-workflow skill to invoke for a given task. Also use when flow gate questions arise (should I review before shipping? should I run security audit?)."
---

# Engineering Workflow — Flow Control

This plugin provides 12 specialized skills that extend Superpowers with process and tool capabilities. These rules govern when and how they are invoked.

## Relationship with Superpowers

**Superpowers is the discipline layer. This plugin is the process and tool layer.**

- Superpowers Iron Laws (TDD, systematic debugging, verification) are NEVER overridden
- This plugin adds structured review, knowledge accumulation, security audit, and release workflow ON TOP of Superpowers discipline
- When both plugins could apply, Superpowers discipline applies first, then this plugin's process

## Flow Control Rules

### Rule 0: Triage — classify BEFORE routing (MUST run first)

Classify the **work-item** (the user's current request/deliverable, not a single file edit) before applying Rules 1–6. The tier sets HOW MUCH process applies. **Auto-scaling scales scaffolding (HOW); it never scales the floor (0.3) or the escalation conditions (0.4).**

#### 0.1 Tiers and the process each runs

| Tier | Profile | Process (beyond the floor) |
|---|---|---|
| **T0 Trivial** | single-point, reversible, unambiguous, oracle already exists, **and no runtime logic/behavior change** (version bump, typo, doc one-liner, comment) | Just do it. Skip the Gates 1–3 (route via Rule 1 as normal). **Silent.** |
| **T1 Standard** | bounded, target clear, oracle exists/cheap — 1–few files, OR **wide-mechanical**: many files, ONE repeated pattern, no per-site design choice (rename, sync sweep, mass textual update) | Announce (wide-mechanical: declare expected breadth). spec-lite + one failing test as oracle + self-review + ONE `structured-review`. Skip brainstorming / plan-review / subagent choreography. |
| **T2 Substantial** | real design choices, intent must be excavated, oracle must be designed, or breadth with cross-cutting design risk (interacting subsystems — not the same edit repeated) | Announce. Full flow: `superpowers:brainstorming` → `superpowers:writing-plans` → `plan-review-personas` → `superpowers:subagent-driven-development` → `structured-review`. |

Signals (highest wins; round up ONLY when genuinely uncertain — over-escalating everything defeats the purpose): **design divergence** (real alternatives to choose between → T2), **ambiguity** (intent must be excavated → T2), **verifiability** (oracle must be designed → T2), **interaction breadth** (>1 subsystem whose changes interact — beyond the same edit repeated → T2). **Size alone is not a tier signal:** the same change repeated across many files with no per-site design choice is **wide-mechanical T1** — announce the expected breadth; E-2 escalates if the work outgrows the announcement. **Any change to runtime behavior/logic is ≥T1** (it needs a check that can fail — so a one-line bugfix is T1, not T0). Security/irreversibility is NOT a size signal — it is the floor overlay (0.3 #6 / 0.4 E-1).

#### 0.2 Precedence — conservative wins

If a tier conflicts with the consumer's own `CLAUDE.md` rule or a Superpowers Iron Law, **the stricter / higher-tier / more-review instruction wins.** An unmigrated consumer that says "always review" keeps it — Rule 0 only ever *adds* escalation. (Auto-scaling is thus safe-by-default and opt-in.)

#### 0.3 Invariant floor — every tier, never scaled away

1. Define "correct" before implementing (≥1 sentence). Two valid interpretations → resolve with the user, don't guess.
2. Have a check that can **actually fail** (test / fixture / for docs-only: a concrete independently-checkable assertion or explicit human review). A tautology is a broken oracle → STOP. For scenario-protocol-adopted projects, a T2 work-item with an HTTP-observable surface requires user-confirmed acceptance scenarios + a green loop-engine verdict (see `references/scenario-protocol.md`).
3. Verify with evidence before "done" (`superpowers:verification-before-completion`).
4. Never auto-execute irreversible / outward-facing actions (push, deploy, migration, delete, external send) — confirm first.
5. Learnings discipline (Rule 4) applies.
6. **Completion-time checkpoint (forcing function):** before claiming done, re-scan the **actual diff** against 0.4 — independent of the starting tier. If a condition fires, escalate, **announce it**, and run the required gate before completion. (Catches a diff that turned out to touch a security path, scope that grew mid-task, or a surprise irreversible op — the pre-diff classification sees none.) **Ordering:** this checkpoint runs *before* any floor-#4 irreversible/outward-facing action, so E-1's `security-audit` fires before a push/deploy, never after — closing the silent-T0 seam.

#### 0.4 Escalation conditions (checked at the 0.3 #6 checkpoint; one-directional)

| # | Condition (vs the actual diff) | Forced action | Tunable |
|---|---|---|---|
| E-1 | touches a security path: auth, secrets/credentials/keys/tokens/session, input validation, public API, crypto, SQL/query, file-path/upload, deserialization, secret-bearing config | **≥T2 + mandatory `security-audit`** + human approval before the irreversible step | **No** — consumers may extend the list, not disable it |
| E-2 | scope outgrew the classification: more files/subsystems than the announcement declared; absolute > ~5 files when NO breadth was announced (silent T0 / plain T1); or per-site judgment emerged in work classified wide-mechanical | escalate to **T2**; plan-review before continuing | upward only, hard floor |
| E-3 | a test that cannot fail / was weakened to pass | **STOP** — broken oracle | No |
| E-4 | diff performs a surprise irreversible/destructive op (migration, delete/drop, mass rewrite, force-push) | escalate to **≥T2** + human approval before the irreversible step | No |

#### 0.5 Announce

T1+ emit before acting: `Tier: T<n> — <signals> → <process>`; wide-mechanical T1 additionally declares expected breadth: `Tier: T1 (wide-mechanical, ~N files / <subsystems>) — …` (the announcement is what E-2 measures against). **T0 is silent** (still obeys the floor, including the 0.3 #6 checkpoint). Checkpoint escalations are always announced. Honor overrides verbatim ("treat as T2" / "run full").

### Rule 1: Skill Routing (MUST follow)

Match the user's intent to the correct skill. Check this routing table BEFORE responding:

| User intent | Skill | Priority |
|-------------|-------|----------|
| Product idea, feature exploration | `superpowers:brainstorming` | SP first |
| Write implementation plan | `superpowers:writing-plans` | SP first |
| Review plan before execution | `plan-review-personas` | This plugin |
| Stress-test a plan/design interactively, "grill me" | `grill-me` | This plugin |
| Implement code | `superpowers:subagent-driven-development` | SP first |
| Test page in browser, "does this work" | `e2e-browser-test` | This plugin |
| Review code, check diff, verify diff matches plan/spec | `structured-review` | This plugin |
| Security sensitive changes | `security-audit` | This plugin |
| Acceptance scenarios, "跑验收", "verify scenarios" | `loop-verify` | This plugin |
| Ship, commit, create PR | `ship-and-pr` | This plugin |
| Update docs after shipping | `document-sync` | This plugin |
| Resolve PR review comments | `resolve-pr-feedback` | This plugin |
| Record learnings, compound | `knowledge-compound` | This plugin |
| Weekly retro | `engineering-retro` — **user-invoked**: suggest the user run `/engineering-retro` | This plugin |
| Maintain/refresh learnings | `learnings-refresh` — **user-invoked**: suggest the user run `/learnings-refresh` | This plugin |
| Debug, fix bug | `superpowers:systematic-debugging` | SP first |

### Rule 2: Flow Sequence Gates

These transitions are enforced. Do not skip forward without completing the prior step.

**Gates apply per the work-item's tier (Rule 0.1), subject to conservative-wins precedence (Rule 0.2):**
- **T0** — skip Gates 1–3 (floor still applies, incl. the Rule 0.3 #6 checkpoint).
- **T1** — Gate 2/3 in light form (one `structured-review`); Gate 1 skipped.
- **T2** — Gates 1–4 in full.
- **Security/irreversibility overlay (Rule 0.4 E-1)** — adds mandatory `security-audit` + human approval before the irreversible step, on top of whatever tier applies.

The gate descriptions below are the **T2 baseline**; lighter tiers apply the subset above. A stricter consumer rule always wins.

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

At **T1+**, these thoughts mean STOP — you are about to skip a flow gate. (At **T0** the gates are absent by classification, not rationalization — but the Rule 0.3 floor still holds, including the #6 checkpoint.)

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
- **READ:** domain glossary first if present (L0) → INDEX-first → 📚 synthesis preferred → targeted reads → Grep fallback. Cite sources.
- **WRITE:** suggest `knowledge-compound`, never write directly. Frontmatter required (`track`, `status`).
- **MAINTAIN:** `/learnings-refresh` (user-invoked) — suggest it to the user monthly or when the session-start signal fires; you cannot self-invoke it.

If `docs/learnings/INDEX.md` does not exist and the project has ≥30 learnings, suggest the user run `/learnings-refresh` (fallback name: `/engineering-workflow:learnings-refresh`) to auto-generate it.

**Domain glossary (opt-in):** a project MAY keep a `CONTEXT.md` domain glossary at the repo root. When present, skills read it first and adopt its vocabulary; when a session coins or sharpens a project term, offer to record it there. Convention: `references/domain-glossary.md`. No glossary → nothing changes (conservative-wins).

This is not optional. Prior knowledge lookup prevents repeating mistakes. Knowledge output prevents losing insights.

Rule 4 is an **invariant floor** item (Rule 0.3 #5): it applies at every tier, T0 included.

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

## Available Skills (12)

| Skill | Trigger |
|-------|---------|
| `structured-review` | Code review before merge (quality + spec-fidelity axes) |
| `knowledge-compound` | Document learnings after tasks |
| `plan-review-personas` | Stress-test plans before execution (async) |
| `grill-me` | Stress-test a plan/design interactively (live) |
| `ship-and-pr` | Commit, push, create PR |
| `security-audit` | Security review on sensitive changes |
| `engineering-retro` | Weekly/milestone retrospective — **user-invoked** (`/engineering-retro`) |
| `e2e-browser-test` | Browser testing on affected pages |
| `resolve-pr-feedback` | Batch-process PR review comments |
| `document-sync` | Sync docs to match shipped code |
| `learnings-refresh` | Maintain docs/learnings/ — detect stale, cluster, regenerate INDEX — **user-invoked** (`/learnings-refresh`) |
| `loop-verify` | Drive the scenario-protocol acceptance loop (sign-off → run → green) |

## Workflow State

The SessionStart hook reports:
- `LEARNINGS_COUNT` — number of project learnings in `docs/learnings/`
- `REVIEW_DONE` — whether a review artifact exists from this session
- `PLAN_REVIEWED` — whether a plan review was done

Use this state to enforce gates contextually. If `REVIEW_DONE=true`, Gate 2 is satisfied.
