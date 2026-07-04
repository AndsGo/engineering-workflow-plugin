# Process Auto-Scaling — Match Process Weight to Change Size

**Status:** Revised (RETHINK-1) + hardened (round-2 REVISE) → execution-ready pending user go
**Date:** 2026-07-04
**Targets:** plugin v1.4 (`using-engineering-workflow` skill restructure; docs; classification eval)
**Driver:** The plugin's flow control (`using-engineering-workflow`) is **maximally rigid** — a flat routing table plus 5 unconditional gates. Every non-trivial change pays the full toll (brainstorm → plan → plan-review → subagent-driven → structured-review → …), regardless of blast radius. This session produced a live example: a 4-sentence skill (`grill-me`) was routed through the same heavyweight pipeline that produced document-sync v2's 406-line spec + 1162-line plan. As models get stronger, prescribing *how* to execute (micro-step choreography) adds friction and can anchor the model below its own judgment; the durable value moves to *what must be true* (correct target, an oracle that can fail, adversarial verification of the gap). The plugin should scale its own process weight to the task.

> **Design provenance:** The core model was co-designed with the user, then the plan built from an earlier draft of this spec was stress-tested by three plan-review personas (feasibility, scope-guardian, adversarial). Their review returned **RETHINK (round 1/2)** with three design-level blockers — circular self-certifying verification, a defeatable "invariant" security escalation, and tripwires with no forcing function. This revision integrates the fix the reviewers converged on, **"fewer, stronger"**: collapse redundant tiers (T3 → T2 + a security/irreversibility overlay), fold the tripwires into a mandatory **completion-time floor checkpoint** that runs against the *actual diff*, make the security escalation a **non-tunable** floor guarantee, add **conservative-wins precedence** (which also makes rollout safe/opt-in), and replace self-graded fixtures with a **blind, multi-run, held-out** eval. §10 records all decisions.

## 1. Goal

Replace "every change pays the full toll" with **"process weight auto-scales to change size, but a set of correctness invariants always holds."**

Concretely, add a **triage front-door** to `using-engineering-workflow` that:

1. Classifies each **work-item** (§4.0) into a tier **T0–T2** using observable signals.
2. Applies a tier-appropriate subset of the existing gates (Rules 1–6) — light for small changes, full for large ones.
3. Enforces an **invariant floor** (§5) that is constant across all tiers and includes a mandatory **completion-time checkpoint** that re-scans the actual diff for escalation conditions (§6) — the forcing function that makes escalation real rather than voluntary.
4. Resolves conflicts with a consumer's own rules by **conservative-wins precedence** (§4.3): the stricter instruction always wins, so an unmigrated consumer keeps its current behavior and auto-scaling is effectively opt-in.
5. **Announces the chosen tier + one-line rationale** for any T1+ work-item, so a wrong classification is vetoable by the user at near-zero cost.

The distinction that makes "auto" safe: **auto-scaling scales the scaffolding (HOW), never the invariants (WHAT-must-be-true).**

## 2. Out of Scope (and Why)

| Item | Why excluded |
|---|---|
| A new standalone `process-triage` skill | "Auto" triage that depends on a separate skill firing reliably is weaker than a front-door that always runs. Fold into `using-engineering-workflow` — one entry point, single source of truth. |
| Editing consumer projects' `CLAUDE.md` routing sections | The plugin skill is the source of truth; consumers can't be auto-edited. v1.4 ships the plugin change + a **migration note** (README). By conservative-wins precedence (§4.3) an unmigrated consumer is unaffected until it opts in. Not performed in-repo. |
| Hook-based auto-measurement (SessionStart hook emitting diff-size/file-count signals) | Valuable, and it would give E-2 a second enforcement layer, but it is a separable mechanism. v1.4's forcing function is the completion-time checkpoint (§5.6) run by the model against the diff; a hook is a v1.5 hardening. **Shadow-logging** (below) is the other recommended v1.5 item. |
| Runtime telemetry / shadow-logging of skipped gates | A skipped review leaves no artifact, so field-detection of under-classification needs a shadow mechanism. Deferred to v1.5; conservative-wins bounds the v1.4 blast radius in the meantime (§9 rollback note). |
| Bundling `grill-me` into this release | Different feature, different tier (T0/T1). Keep v1.4 focused on the auto-scaling contract. |
| Overriding Superpowers Iron Laws | TDD/systematic-debugging/verification remain non-negotiable. They are re-expressed here as *invariants* (the floor), not removed. The floor is stricter-or-equal to current behavior. |

## 3. Background — Why Now

### 3.1 Two things wear the name "process"

- **Execution choreography (HOW):** "write the failing test, run it, watch it fail, write minimal code, commit"; "dispatch a fresh subagent per task"; "explore before fixing." These are instructions about *how the executor moves*. A strong model already does most of this; prescribing the micro-steps adds token overhead and can anchor it. **Value decays as capability rises.**
- **Invariants / guarantees (WHAT-must-be-true):** "no code merges without an adversarial review it did not write itself"; "success is defined by a check that can actually fail"; "removing content from CLAUDE.md must ask a human." These constrain which states are allowed. **Value rises as capability rises** — a stronger model produces more plausible-looking output faster, so an undetected wrong target costs more.

TDD is really both: TDD-as-ritual (micro-steps → scaffolding) and TDD-as-specification (the test is the executable definition of "correct," written first to pin the target → invariant). v1.4 keeps the specification essence at every tier and relaxes the ritual by tier.

### 3.2 Why naive "auto" is the failure mode

A model under delivery pressure, told only "use your judgment on how much process to apply," will systematically under-apply — skipping review/tests is the path of least resistance. Bounding it with prose alone is not enough (prose is administered to the same pressured model). So the floor includes a **forcing function** (§5.6): a mandatory checkpoint that re-scans the real diff before "done," independent of the self-assigned tier. That is the difference between a guarantee and a good intention.

### 3.3 Evidence from this project's own recent work

The value in document-sync v2 concentrated in the **fixtures (executable oracles)** and the **token-evidence gates (adversarial verification that the subagent did not self-certify)** — not in the 7-phase choreography. Note the caution this cuts both ways: that value came from fixtures with *mechanically re-verifiable ground truth* plus a *separate controller-run empirical pass*. A self-authored, self-graded walkthrough has neither — which is why §9 is a blind eval, not a self-graded one.

## 4. The Tier Model

### 4.0 Unit of classification

The unit is the **work-item** — the user's current request / deliverable — not the individual file edit. Surface-area and scope signals (§4.2, §6) are measured against the work-item's *cumulative* diff. A change that is trivial in isolation (a lone version bump) is T0; a docs edit that is one step of a larger feature inherits the feature's tier.

### 4.1 Tiers

| Tier | Triggering profile | Process applied (beyond the floor in §5) |
|---|---|---|
| **T0 Trivial** | Single-point, reversible, target unambiguous, oracle already exists | Just do it. Skip Rules 1–3 gates. (version bump, typo, one-line doc, `grill-me`-style tiny skill adaptation) |
| **T1 Standard** | Bounded feature/bugfix, 1–few files, target mostly clear, oracle exists or is cheap to make | spec-lite (a few sentences, not a doc) + one failing test as the oracle + self-review + **one** `structured-review`. Skip brainstorming, plan-review-personas, subagent choreography. |
| **T2 Substantial** | Multi-file, real design choices, intent needs excavation, or the oracle must be designed | Full flow: brainstorming + writing-plans + plan-review-personas + subagent-driven-development + structured-review. Gates 1–4 all apply. (document-sync v2 was this tier.) |

**Security & irreversibility are handled by the floor (§5) as an overlay, not by a separate tier.** The earlier draft had a T3 tier; plan-review (scope-guardian) found its only distinguishing behaviors — mandatory `security-audit` and human-approval-before-irreversible — were *already* floor-guaranteed. So T3 is removed and expressed as a **security/irreversibility overlay**: whenever the §6 checkpoint detects a security path, the work-item runs at **≥T2 plus mandatory `security-audit` + human approval before the irreversible step**, regardless of its size-based tier. Fewer tiers, and the safety behavior is no longer a tier that can be traded away by a low size score.

### 4.2 Classification signals (observable, not vibes)

Three dimensions; the model records a one-line reading of each. **Highest-triggered tier wins; when genuinely uncertain, round up** — but round-up is a *tie-breaker*, not a license to escalate everything (ceremony-restoration, §9 calibration, is a real failure mode too).

| Dimension | Proxy questions | Pushes to T2 when… |
|---|---|---|
| Surface area | # files, # subsystems, rough LOC (cumulative over the work-item) | > ~5 files or > 1 subsystem with integration |
| Ambiguity | Is the target already crisp (clear repro, explicit spec) or must intent be excavated? | intent needs excavation |
| Verifiability | Does an oracle exist / is it cheap (one unit test) / must it be designed? | oracle must be designed |

Security/irreversibility is deliberately **not** a size signal — it is the §5/§6 overlay, checked against the actual diff, so it cannot be classified away.

### 4.3 Precedence — conservative wins

When Rule 0's tier conflicts with an instruction already in the consumer's `CLAUDE.md` (or a Superpowers Iron Law), **the stricter / higher-tier / more-review instruction wins.**

- An **unmigrated** consumer whose CLAUDE.md says "always review" keeps always-review — Rule 0 can only *add* escalation, never *remove* a stricter existing rule. v1.4 is therefore **safe-by-default and effectively opt-in**: the lightening only takes effect once a consumer *chooses* to trim its always-full override (§8 migration).
- This resolves the "is a behavior-changing default safe?" concern: existing behavior does not silently loosen.

### 4.4 The invariant floor — constant across ALL tiers (§5)

Even T0 obeys the floor, including the completion-time checkpoint (§5.6). The floor is where the Superpowers Iron Laws live, re-expressed as guarantees rather than choreography.

## 5. Invariant Floor

Holds at every tier, never scaled away. Items 1–5 are guarantees; item 6 is the **forcing function** that makes escalation real.

1. **Define "correct" before implementing** — ≥1 explicit sentence of expected behavior/outcome. If two valid interpretations of the target exist, resolve with the user before coding (do not guess).
2. **Have a check that can actually fail.** A test, a fixture, or — for prose/docs-only work-items where no code runs — a concrete, independently-checkable assertion (e.g., "the documented count equals the actual count") or an explicit human review. A tautology that cannot fail is a broken oracle: **STOP** and fix it. Vacuous self-agreement does not satisfy this item.
3. **Verify with evidence before claiming done** — `superpowers:verification-before-completion` at every tier. No success claim without observed output.
4. **Never auto-execute irreversible or outward-facing actions** — push, deploy, migration, delete, external send always require explicit confirmation, regardless of tier. The item-6 checkpoint MUST complete before any such action (see #6 ordering).
5. **Learnings discipline (Rule 4)** — READ before analytical work; offer WRITE at session end (INDEX-first per `learnings-protocol.md`).
6. **Completion-time checkpoint (the forcing function).** Before claiming a work-item done, re-scan the **actual diff** against the escalation conditions in §6 — independent of the tier assigned at the start. This closes gaps the initial (pre-diff) classification cannot see: a diff that turns out to touch a security path (E-1), scope that grew past the threshold mid-task (E-2), or an irreversible/destructive op that only became apparent in the diff (E-4). If a condition is met, the work-item escalates, the escalation is announced, and the corresponding gate runs **before** completion. A mandatory checkpoint — not voluntary mid-task monitoring.
   **Ordering (closes the silent-T0 seam):** the checkpoint runs *before* any floor-#4 irreversible/outward-facing action. So for a work-item that looked trivial but whose diff touches a security path, the E-1 scan and its forced `security-audit` happen **before** the push/commit/deploy — never after. A silent T0 that turns out to touch security is therefore caught and escalated (and thus announced) prior to any irreversible step.

## 6. Escalation Conditions — enforced at the §5.6 checkpoint

Escalation is **one-directional** (only ever raises the tier) and enforced by the mandatory completion-time checkpoint (§5.6) run against the real diff — no reliance on the model voluntarily re-evaluating mid-task.

| # | Condition (checked against the actual diff) | Forced action | Tunable? |
|---|---|---|---|
| E-1 | diff touches a security-sensitive path: auth/authn/authz, secrets/credentials/keys/tokens/session, input validation & sanitization, public API surface, crypto, SQL/query construction, file path & upload handling, deserialization, secret-bearing config | run at **≥T2 + mandatory `security-audit`** + human approval before the irreversible step | **No** — non-tunable floor guarantee. A consumer may *extend* the path list; it may not disable the requirement or shrink below the built-in core set. |
| E-2 | cumulative files touched exceed the threshold (default ~5) or a second subsystem is involved | escalate to **T2**; run plan-review (Gate 1) before continuing | threshold tunable **upward only, with a hard built-in floor** |
| E-3 | a test was written that cannot fail, or was weakened to pass | **STOP** — broken oracle; fix the check before proceeding | No |
| E-4 | the diff performs an irreversible/destructive op that wasn't apparent at classification: schema migration, data delete/drop, mass rewrite, force-push | escalate to **≥T2** + human approval before the irreversible step | No |

Removed from the earlier draft (per plan-review): old T-4 ("second interpretation → clarify") is now floor item 1 (define-correct). Old T-5 ("reversibility worse than assumed") is **not** silently subsumed — it is made explicit as **E-4**, since a small, non-security destructive change would otherwise escalate via neither E-1 (security-only) nor E-2 (size-only). Floor item 4 still guarantees a confirmation for any irreversible op at every tier; E-4 adds the elevated design scrutiny (plan-review) when the irreversibility was a surprise. Four conditions, each with a forcing function at the checkpoint.

## 7. Announce-the-Tier Contract

At the start of any **T1+** work-item, emit one line before acting:

```
Tier: T<n> — <one-line signal reading> → <process I will run>
```

Example: `Tier: T1 — reversible, 2 files, oracle exists → spec-lite + 1 test + 1 structured-review.`

**T0 is silent** — narrating a trivial change is itself ceremony noise. T0 still obeys the floor, **including the completion-time checkpoint (§5.6)**; it just doesn't narrate up front. This matters for the dangerous case: a work-item that looked T0 but whose diff touches a security path (E-1) or grew past the size threshold (E-2) is caught at the checkpoint and the escalation **is announced** — so even a silent T0 surfaces to the user the moment it stops being trivial.

The announce line is a near-zero-cost veto: a wrong classification is caught in a glance and corrected in a sentence. It recovers most of an explicit `--light/--full` switch without the friction. **Manual override:** the user may pin a work-item ("treat as T2" / "run full") — honored verbatim.

## 8. Integration — File Changes

| File | Change |
|---|---|
| `skills/using-engineering-workflow/SKILL.md` | Add **Rule 0: Triage** (unit, tiers T0–T2, signals, precedence, floor incl. completion-time checkpoint, escalation conditions, announce) as the new front-door — kept **lean** to avoid bloating an always-loaded file: state the tier→process map once, cross-reference the existing "Relationship with Superpowers" section instead of restating the Iron Laws. Rewrite Rule 2 (Gates) and Rule 3 (Anti-Skip) to be **tier-conditional** and to defer to conservative-wins precedence. |
| `README.md` (plugin) | Document auto-scaling; add the consumer migration note (trim duplicated always-full routing to a pointer to opt in). |
| `CHANGELOG.md` | v1.4.0 entry. |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Bump to 1.4.0; refresh descriptions to mention auto-scaling. |
| `skills/using-engineering-workflow/tests/` (new) | Blind classification eval assets — see §9. |

**Backward compatibility (guaranteed, not asserted):** by conservative-wins precedence (§4.3) an unmigrated consumer's existing "always review" rule keeps winning, so existing behavior does **not** silently loosen; auto-scaling activates only on opt-in. The floor is stricter-or-equal to today's correctness behavior. **No config file in v1.4** (YAGNI); the one tunable threshold (E-2) lives in the consumer's CLAUDE.md with a hard floor, and E-1's security requirement is non-tunable.

## 9. Test Strategy — blind, not self-graded

Plan-review flagged that a self-authored, self-graded fixture walkthrough is circular: it runs in calm conditions with the answer key in hand and cannot detect the central failure (under-pressure under-classification). Revised strategy:

1. **Blind classification eval.** A *fresh subagent* gets only the scenario text + the shipped `SKILL.md` (Rule 0) — the expected tier is **withheld**. It is instructed not to read `tests/`, `docs/plans/`, or `docs/specs/` (where the answer key and tier rationale live), and ideally is run without repo file tools (scenario + SKILL.md pasted inline). The controller diffs its answer against held-out ground truth. The graded model never sees the answer key.
2. **Multi-run (variance).** Each scenario is classified by **≥5** independent runs; a scenario passes only if classification is stable across all runs. Flapping is itself a finding — the signals are underspecified. (≥5, not 3: a 20–30% misclassification rate — the dangerous under-classification band — clears a 3-run stability check too often.)
3. **Held-out set from real history.** Scenarios are drawn from this repo's actual git history (v1.1–v1.4 work-items), not author-constructed to match the rules — so the eval measures realistic classification, not recognition of the examples the rules were written against.
4. **Tier-distribution calibration.** Report the tier mix over the held-out set. The feature's purpose is *less* ceremony, so nearly-everything-T2 is a **failure** (ceremony-restoration) just as everything-T0 is (unsafe). The measured mix is evidence the feature works in the intended direction.
5. **One live empirical session.** Run one real task end-to-end through Rule 0 (controller-observed) as independent behavioral evidence — mirroring document-sync v2's second, controller-run empirical pass.
6. **Anti-self-certification gate.** Checks require literal token presence/absence (tier token, escalation phrase) applied to the *blind* runs' outputs — the gate now constrains a model that did not write the answer key.

**Rollback / detection note:** v1.4 has no runtime telemetry (a skipped review leaves no artifact). Conservative-wins (§4.3) bounds the blast radius — only opted-in consumers can be affected. Field detection via **shadow-logging** (log what Rule 0 *would* skip while still running the full flow) is a recommended v1.5 follow-up.

**Opt-in tradeoff (acknowledged, per plan-review):** because rollout is conservative-wins/opt-in, existing consumers with an "always review" rule feel **no** lightening until they migrate — so the motivating pain isn't relieved automatically, and until v1.5 shadow-logging lands the field benefit is unmeasurable. This is a deliberate safety-over-speed choice for v1.4. The **activation path for this project** is the already-planned separate follow-up: migrate this workspace's own `CLAUDE.md` to defer to Rule 0 (a T0/T1 task), which both dogfoods the feature and realizes its benefit here first.

## 10. Resolved Decisions

**Approved by the user 2026-07-04 (original open questions):**
1. **Placement** — front-door **Rule 0** inside `using-engineering-workflow`. ✅
2. **Thresholds** — E-2 "~5 files or >1 subsystem" (tunable upward with a floor); E-1 security-path list covers injection-prone areas. ✅
3. **Escape hatch** — convention (pin-to-T2+) + per-task override phrase; **no config file** (YAGNI). ✅
4. **Announce** — silent on T0, announce T1+; escalations always announced. ✅
5. **Consumer migration** — out of v1.4 scope; README note + conservative-wins opt-in. ✅

**Revisions from plan-review RETHINK round 1 (2026-07-04):**
6. **T3 removed** — collapsed into "T2 + security/irreversibility overlay" (scope-guardian: T3's behaviors were already floor-guaranteed). Tiers are now T0/T1/T2.
7. **Tripwires → completion-time floor checkpoint** (§5.6) — escalation now has a mandatory forcing function against the real diff, not voluntary mid-task monitoring (adversarial B3). T-4/T-5 removed as redundant.
8. **Security escalation is non-tunable** (§6 E-1) — moved from a tunable tripwire into the floor; a consumer may extend but not disable it (adversarial B2).
9. **Conservative-wins precedence** (§4.3) — resolves the Rule-0-vs-consumer-CLAUDE.md contradiction and makes rollout safe/opt-in (adversarial: "backward-compatible was false").
10. **Verification redesigned** (§9) — blind, multi-run, held-out + calibration + live empirical (feasibility + adversarial B1: circular self-certification).
11. **Classification unit defined** (§4.0) + **docs-only floor handling** (§5.2) + **Rule 0 kept lean** to avoid token-bloat in an always-loaded file (scope-guardian).

**Round-2 re-review hardening (REVISE, 2026-07-04):**
12. **Checkpoint-before-irreversible ordering** (§5 #4/#6) — closes the silent-T0-touches-security seam (adversarial round-2 blocker): the E-1 scan runs before any push/deploy.
13. **E-4 added** (§6) — a non-security, small irreversible/destructive change now escalates explicitly; the earlier "subsumed by E-1/E-2" claim was inaccurate and is corrected (adversarial round-2 warning).
14. **Blind isolation broadened + runs ≥5** (§9) — classifier must not read `docs/plans/`/`docs/specs/`/`tests/` (the key lived there); n bumped 3→5 for the under-classification band (feasibility + adversarial round-2).
15. **Opt-in tradeoff acknowledged** (§9) — benefit is deferred behind migration and unmeasurable until v1.5 shadow-logging; workspace-CLAUDE.md migration is the activation path.

**Eval-driven refinement (during execution, 2026-07-04):**
16. **T0 excludes runtime logic changes.** The blind eval (§9) caught scenario S5 (a one-line off-by-one fix with an existing test suite) *flapping* T0/T1 across runs — the T0/T1 boundary for a tiny code fix was underspecified. Rule 0's T0 row + signals were tightened to "**any change to runtime behavior/logic is ≥T1**" (a one-line bugfix is T1, not T0); re-running the eval gave a stable, correct classification on all 6 scenarios. This is the intended loop: blind eval → finding → tighten rubric → re-run → stable.

## 11. Self-Consistency Note

By its own model, this change is **T2 with the security/irreversibility overlay engaged** (it rewrites the plugin's core contract and affects every consumer's routing — E-1-class blast radius). Accordingly it went through the full flow — and plan-review actually returned **RETHINK**, forcing this revision. The framework not only classified itself as heavyweight; its own adversarial gate caught real design blockers in the plan to build it, and the fixes made the design materially safer. That is the intended demonstration, and it worked.
