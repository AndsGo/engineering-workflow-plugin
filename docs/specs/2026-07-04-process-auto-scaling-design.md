# Process Auto-Scaling — Match Process Weight to Change Size

**Status:** Draft → pending user review
**Date:** 2026-07-04
**Targets:** plugin v1.4 (`using-engineering-workflow` skill restructure; docs; classification fixtures)
**Driver:** The plugin's flow control (`using-engineering-workflow`) is **maximally rigid** — a flat routing table plus 5 unconditional gates. Every non-trivial change pays the full toll (brainstorm → plan → plan-review → subagent-driven → structured-review → …), regardless of blast radius. This session produced a live example: a 4-sentence skill (`grill-me`) was routed through the same heavyweight pipeline that produced document-sync v2's 406-line spec + 1162-line plan. As models get stronger, prescribing *how* to execute (micro-step choreography) adds friction and can anchor the model below its own judgment; the durable value moves to *what must be true* (correct target, an oracle that can fail, adversarial verification of the gap). The plugin should scale its own process weight to the task.

> **Design provenance:** The core model (T0–T3 tiers, invariant floor, one-directional tripwires, announce-the-tier) was co-designed with the user in a strategic discussion prior to this spec. The five open questions in §10 were **resolved by the user on 2026-07-04** ("go with your recommendations"); §10 now records the decisions, and the affected sections (§6, §7, §8) reflect them.

## 1. Goal

Replace "every change pays the full toll" with **"process weight auto-scales to change size, but a set of correctness invariants always holds."**

Concretely, add a **triage front-door** to `using-engineering-workflow` that:

1. Classifies each task into a tier **T0–T3** using observable signals.
2. Applies a tier-appropriate subset of the existing gates (Rules 1–6) — light for small changes, full for large ones.
3. Enforces an **invariant floor** that is constant across all tiers (never scaled away).
4. Honors **one-directional tripwires** that force an upgrade mid-task and cannot be auto-downgraded.
5. **Announces the chosen tier + one-line rationale** at task start, so a wrong classification is vetoable by the user at near-zero cost.

The distinction that makes "auto" safe: **auto-scaling scales the scaffolding (HOW), never the invariants (WHAT-must-be-true).**

## 2. Out of Scope (and Why)

| Item | Why excluded |
|---|---|
| A new standalone `process-triage` skill | "Auto" triage that depends on a separate skill firing reliably is weaker than a front-door that always runs. Fold into `using-engineering-workflow` — one entry point, single source of truth. |
| Editing consumer projects' `CLAUDE.md` routing sections | The plugin skill is the source of truth; consumers can't be auto-edited. v1.4 ships the plugin change + a **migration note** (README) telling consumers their routing now auto-scales and their local duplicated routing can be trimmed to a pointer. Not performed in-repo. |
| Hook-based auto-measurement (SessionStart hook emitting diff-size/file-count signals to feed tripwires) | Valuable but a separable mechanism. v1.4 classifies from signals the model can already observe. Hook-fed signals are a v1.5+ enhancement. |
| Bundling `grill-me` into this release | Different feature, different tier (T0/T1). Keep v1.4 focused on the auto-scaling contract. |
| Overriding Superpowers Iron Laws | TDD/systematic-debugging/verification remain non-negotiable. They are re-expressed here as *invariants* (the floor), not removed. The floor is stricter-or-equal to current behavior, never looser on correctness. |
| Auto-executing irreversible actions at any tier | Push/deploy/migration/delete/external-send always require confirmation regardless of tier. This is a floor item, not a tier dial. |

## 3. Background — Why Now

### 3.1 Two things wear the name "process"

- **Execution choreography (HOW):** "write the failing test, run it, watch it fail, write minimal code, commit"; "dispatch a fresh subagent per task"; "explore before fixing." These are instructions about *how the executor moves*. A strong model already does most of this; prescribing the micro-steps adds token overhead and can anchor it. **Value decays as capability rises.**
- **Invariants / guarantees (WHAT-must-be-true):** "no code merges without an adversarial review it did not write itself"; "success is defined by a check that can actually fail"; "removing content from CLAUDE.md must ask a human." These are not about how the model moves — they constrain which states are allowed. **Value rises as capability rises**, because a stronger model produces more plausible-looking output faster, so an undetected wrong target costs more.

TDD is really both: TDD-as-ritual (micro-steps → scaffolding) and TDD-as-specification (the test is the executable definition of "correct," written first to pin the target before the implementation anchors it → invariant). v1.4 keeps the specification essence at every tier and relaxes the ritual by tier.

### 3.2 Why naive "auto" is the failure mode

A model under delivery pressure, told only "use your judgment on how much process to apply," will systematically under-apply — skipping review/tests is the path of least resistance. So auto-scaling must be bounded by: (a) a constant floor, (b) one-directional tripwires that only ever upgrade, (c) a round-up bias under uncertainty, and (d) an announced tier the user can veto. Without these, "auto" degrades to "confident and wrong, cheaper to hit and harder to notice."

### 3.3 Evidence from this project's own recent work

The value in document-sync v2 concentrated in the **fixtures (executable oracles)** and the **token-evidence gates (adversarial verification that the subagent did not self-certify)** — not in the 7-phase execution choreography. That is a datapoint for keeping oracle + adversarial verification as floor items while relaxing choreography.

## 4. The Tier Model

### 4.1 Tiers

| Tier | Triggering profile | Process applied (beyond the floor in §5) |
|---|---|---|
| **T0 Trivial** | Single-point, reversible, target unambiguous, oracle already exists | Just do it. Skip Rules 1–3 gates. (version bump, typo, one-line doc, `grill-me`-style tiny skill adaptation) |
| **T1 Standard** | Bounded feature/bugfix, 1–few files, target mostly clear, oracle exists or is cheap to make | spec-lite (a few sentences, not a doc) + one failing test as the oracle + self-review + **one** `structured-review`. Skip brainstorming, plan-review-personas, subagent choreography. |
| **T2 Substantial** | Multi-file, real design choices, intent needs excavation, or the oracle must be designed | Full current flow: brainstorming + writing-plans + plan-review-personas + subagent-driven-development + structured-review. Gates 1–4 all apply. (document-sync v2 was this tier.) |
| **T3 High-stakes / irreversible** | Touches auth / secrets / user-input / migrations / public API / **other consumers of this plugin**, or is hard to reverse | T2 **plus** mandatory `security-audit` + adversarial verification + human approval before the irreversible step. **Cannot be auto-downgraded.** |

### 4.2 Classification signals (observable, not vibes)

Four dimensions; the model records a one-line reading of each. **Highest-triggered tier wins; when uncertain, round up.**

| Dimension | Proxy questions | Pushes tier up when… |
|---|---|---|
| Reversibility / blast radius | Touches `main` directly? Outward-facing (push/deploy/PR/external send)? Affects other consumers of the plugin? Migrations/schema? Secrets/auth? | any yes → T2+; secrets/auth/migration/public-API → T3 |
| Surface area | # files, # subsystems, rough LOC | > ~5 files or > 1 subsystem with integration → T2+ |
| Ambiguity | Is the target already crisp (clear repro, explicit spec) or must intent be excavated? | intent needs excavation → T2+ |
| Verifiability | Does an oracle exist, is it cheap (one unit test), or must it be designed (new fixtures/behavior tests)? | oracle must be designed → T2+ |

### 4.3 The invariant floor — constant across ALL tiers (§5 detail)

Even T0 obeys the floor. The floor is where the Superpowers Iron Laws live, re-expressed as guarantees rather than choreography.

## 5. Invariant Floor

These hold at every tier and are never scaled away:

1. **Define "correct" before implementing** — at minimum one explicit sentence of expected behavior/outcome.
2. **Have a check that can actually fail** — a test, a fixture, or a manual observation captured with evidence. A check that cannot fail is treated as a broken oracle (see tripwire T-3).
3. **Verify with evidence before claiming done** — `superpowers:verification-before-completion` applies at every tier. No success claim without observed output.
4. **Never auto-execute irreversible or outward-facing actions** — push, deploy, migration, delete, external send always require explicit confirmation, regardless of tier.
5. **Learnings discipline (Rule 4) still applies** — READ before analytical work; offer WRITE at session end. (INDEX-first per `learnings-protocol.md`.)

## 6. Tripwires — one-directional auto-upgrade

Auto-**downgrade** is allowed only before work starts, from the initial classification. Once any tripwire fires, the tier only moves **up**, and the upgrade cannot be auto-reversed within the task:

| # | Observed fact | Forced action |
|---|---|---|
| T-1 | diff touches security-sensitive paths: auth/authn/authz, secrets/credentials/keys/tokens/session, input validation & sanitization, public API surface (endpoints/handlers), crypto, SQL/query construction, file path & upload handling, deserialization, secret-bearing config (`.env`, etc.) | escalate to **T3**; `security-audit` becomes mandatory |
| T-2 | files touched exceed ~5, or a second subsystem gets involved | escalate to at least **T2**; run plan-review before continuing |
| T-3 | a test was written that cannot fail, or a test was weakened to make it pass | **STOP** — the oracle is broken; fix the check before proceeding |
| T-4 | a second valid interpretation of the target is discovered mid-task | bounce back to spec/clarify (do not guess) |
| T-5 | actual reversibility turns out worse than assumed at classification | escalate one tier |

Thresholds ("~5 files" for T-2, the T-1 security path list) are project-tunable defaults — a consumer may override them in its own CLAUDE.md.

## 7. Announce-the-Tier Contract

At the start of any **T1+** task, emit one line before acting:

```
Tier: T<n> — <one-line signal reading> → <process I will run>
```

Example: `Tier: T1 — reversible, 2 files, oracle exists → spec-lite + 1 test + 1 structured-review.`

**T0 is silent** — a trivial change announcing its triage would itself be ceremony noise, which contradicts the goal. T0 still obeys the invariant floor (§5); it just doesn't narrate. If a tripwire (§6) later escalates a T0/T1 task, the escalation IS announced (the upgrade is the noteworthy event).

The announce line gives the user a near-zero-cost veto: a wrong downgrade is caught in one glance and corrected in one sentence. It recovers most of the control of an explicit `--light/--full` switch without the friction, while keeping the default fully automatic. **Manual override:** the user may pin a task with a phrase like "treat as T2" / "run this full" (upgrade) — honored verbatim.

## 8. Integration — File Changes

| File | Change |
|---|---|
| `skills/using-engineering-workflow/SKILL.md` | Add **Rule 0: Triage** (tiers, signals, floor, tripwires, announce contract) as the new front-door. Rewrite Rule 2 (Flow Sequence Gates) and Rule 3 (Anti-Skip) to be **tier-conditional** — gates apply per the tier's row in §4.1, not unconditionally. Rules 4–6 unchanged in substance; Rule 4 (learnings) becomes a floor item cross-reference. |
| `README.md` (plugin) | Document auto-scaling; add the consumer migration note (local duplicated routing can become a pointer). |
| `CHANGELOG.md` | v1.4.0 entry. |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Bump to 1.4.0; refresh descriptions to mention auto-scaling. |
| `skills/using-engineering-workflow/tests/` (new) | Classification fixtures — see §9. |

**Backward compatibility:** existing consumers keep working. The floor is stricter-or-equal to today's correctness behavior; only the *scaffolding* becomes conditional. A consumer that wants the old always-full behavior can pin every task to T2+ — documented as a convention (a line in their CLAUDE.md, or the per-task "treat as T2" override phrase). **No config file / flag is added in v1.4** (YAGNI); a structured config knob is a v1.5+ option only if demand appears.

## 9. Test Strategy

Behavior-level fixtures, each a short task description + the expected tier + expected process. Mirrors document-sync v2's fixture approach (executable oracle over prose assertion).

| Fixture | Input profile | Expected classification |
|---|---|---|
| `t0-version-bump` | bump manifest version, one file, reversible | T0, floor-only, no gates |
| `t1-bugfix-with-test` | fix a bounded bug, 2 files, existing test suite | T1, spec-lite + 1 test + 1 review |
| `t2-multifile-feature` | new capability across several files, design choices | T2, full flow |
| `t3-auth-change` | edit touches an auth/secret path | T3 via tripwire T-1, security-audit mandatory |
| `tripwire-scope-creep` | starts as T1, grows past ~5 files mid-task | auto-upgrade to T2 (T-2), non-reversible |
| `tripwire-unfailable-test` | a test asserting a tautology | STOP (T-3) |

**Verification gate (anti-self-certification):** each fixture's pass requires the classification output to literally contain the tier token, the triggering signal, and (for tripwire fixtures) the escalation phrase — no prose-only "looks right."

## 10. Resolved Decisions (user approved 2026-07-04)

1. **Placement** — front-door **Rule 0** inside `using-engineering-workflow`. Not a standalone skill, not consumer-CLAUDE.md. ✅
2. **Tripwire thresholds** (§6) — keep "~5 files or >1 subsystem → T2"; T-1 security-path list expanded to cover injection-prone areas (SQL/query, file-path/upload, deserialization) in addition to auth/secrets/API/crypto/config. Both project-tunable. ✅
3. **Escape hatch** — documented **convention** (pin-to-T2+ line in CLAUDE.md) + per-task **override phrase** ("treat as T2" / "run full"). **No config file in v1.4** (YAGNI). ✅
4. **Announce verbosity** — **silent on T0**, announce on **T1+**; tripwire escalations are always announced (§7). ✅
5. **Consumer migration** — **out of v1.4 scope**. v1.4 ships the plugin change + README migration note. The reference migration of this workspace's `CLAUDE.md` is a **separate follow-up** (different repo/parent dir; itself a T0/T1 task). ✅

## 11. Self-Consistency Note

By its own model, this change is **T2 bordering T3**: it rewrites the plugin's core contract and affects every consumer's routing. Accordingly it is going through the full flow (brainstorm → spec → plan → plan-review → subagent-driven → review) — the framework correctly classifies itself as heavyweight. That is the intended demonstration.
