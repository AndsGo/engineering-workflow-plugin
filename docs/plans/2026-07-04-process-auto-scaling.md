# Process Auto-Scaling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Revised after plan-review RETHINK round 1** — self-graded fixtures replaced by a blind/held-out eval; T3 removed; tripwires folded into a completion-time floor checkpoint; two SKILL.md tasks merged; acceptance gate folded into the final task.

**Goal:** Add a tier-based triage front-door to `using-engineering-workflow` so the plugin auto-scales process weight to change size, with a constant correctness floor whose completion-time checkpoint gives escalation a real forcing function.

**Architecture:** A lean **Rule 0: Triage** is prepended to `skills/using-engineering-workflow/SKILL.md`. It classifies each *work-item* T0–T2 from observable signals, applies a tier-appropriate subset of Gates (Rules 1–6), enforces an invariant floor (incl. a mandatory completion-time diff re-scan), escalates on non-tunable security / scope / broken-oracle conditions, resolves consumer conflicts by conservative-wins precedence, and announces the tier (T1+). Behavior is validated by a **blind, multi-run, held-out** classification eval + a live empirical session, not self-graded fixtures.

**Tech Stack:** Markdown skill authoring (no runtime). Validation = a blind eval where fresh subagents classify held-out real scenarios given only the scenario + shipped `SKILL.md` (expected tiers withheld), controller diffs against a key it holds. Bash for presence/version checks.

## Global Constraints

- Spec: `docs/specs/2026-07-04-process-auto-scaling-design.md` (authoritative; copy content verbatim where steps reference it).
- Target version: **1.4.0** (`.claude-plugin/plugin.json`; `.claude-plugin/marketplace.json` both `metadata.version` and `plugins[0].version`).
- The floor is **stricter-or-equal** to current correctness behavior; only *scaffolding* becomes conditional. E-1 security escalation is **non-tunable**.
- **Backward compatible via conservative-wins:** an unmigrated consumer's stricter rule always wins; auto-scaling lightening is opt-in.
- Superpowers Iron Laws are re-expressed as the floor, never removed. Rule 0 is kept **lean** (a large Rule 0 would bloat an always-loaded file — self-defeating).
- Commits: incremental, manual, conventional-commit subject, body ends with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Branch: `feat/v1.4-process-auto-scaling` (already created; no worktree, per repo precedent).

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `skills/using-engineering-workflow/tests/eval-scenarios.md` | Held-out scenarios (drawn from real git history), **no expected tier shown** | 1 |
| `skills/using-engineering-workflow/tests/README.md` | Blind-eval protocol documentation | 1 |
| `skills/using-engineering-workflow/SKILL.md` | Add lean Rule 0 Triage + make Rules 2–4 tier-conditional / floor-aware | 2 |
| `skills/using-engineering-workflow/tests/eval-2026-07-04.md` | Blind eval report: per-scenario blind results, ground-truth key, tier distribution, live empirical, verdict | 3 |
| `README.md` | Auto-scaling section + consumer migration note | 4 |
| `CHANGELOG.md` | v1.4.0 entry | 4 |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Version bump 1.3.0 → 1.4.0 | 4 |

---

## Task 1: Held-out eval scenarios + protocol (the oracle, kept blind)

**Files:**
- Create: `skills/using-engineering-workflow/tests/eval-scenarios.md`
- Create: `skills/using-engineering-workflow/tests/README.md`

**Interfaces:**
- Produces: a numbered scenario list (scenario text only — NO expected tier in this file) consumed by the Task 3 blind runs; and a README defining the blind protocol. The ground-truth key is NOT stored here (it lives in the plan below + the Task 3 report), so a classifier that reads the repo cannot see the answers.

- [ ] **Step 1: Create `tests/eval-scenarios.md` (scenarios only, drawn from real history)**

```markdown
# Rule 0 — Held-out Classification Scenarios

Real work-items from this repo's history (plus one security scenario, since the
repo has no auth change in history — flagged S6). A blind classifier is given
ONLY one scenario at a time + the shipped SKILL.md, and must output a tier.
Expected tiers are deliberately NOT in this file.

- **S1:** Bump the plugin manifest version from 1.3.0 to 1.4.0 in `.claude-plugin/plugin.json` and the two fields in `marketplace.json`. No behavior change.
- **S2:** In `skills/document-sync/SKILL.md`, a size-measurement bash block is committed with a commented-out divisor instead of a real computation; make it actually executable. Single skill file, clear target, no test harness.
- **S3:** Build document-sync v2: stronger freshness checks + a hygiene audit with token caps + inflation-pattern detection across the skill, plus behavior fixtures and a verification report. Multi-file, real design choices, the "what is good hygiene" oracle must be designed.
- **S4:** Add the `learnings-refresh` skill: Python scripts to parse learnings, detect stale entries, cluster by category, generate an INDEX, with a pytest suite. New subsystem, several files, oracle (tests) to be designed.
- **S5:** Fix an off-by-one in `parse_learnings.py` date parsing; the existing pytest suite covers the module.
- **S6:** Change how `verifyToken()` validates session expiry in an auth helper (2 files) so tokens 60 min old are still accepted.

Classify each. Output exactly: `Tier: T<n>` + one line of signals + (if any) the escalation condition that fires.
```

- [ ] **Step 2: Create `tests/README.md` (blind protocol)**

```markdown
# using-engineering-workflow — Rule 0 Blind Eval

Rule 0 (plugin v1.4) is validated by a **blind, multi-run, held-out** eval, not
self-graded fixtures (a self-graded walkthrough is circular — it grades itself
with the answer key in hand).

Protocol (run by the controller, see `eval-2026-07-04.md`):
1. **Blind:** each scenario in `eval-scenarios.md` is handed to a FRESH subagent
   with only the scenario + shipped `SKILL.md`. The expected tier is withheld;
   the subagent is instructed NOT to read anything under `tests/`.
2. **Multi-run:** ≥3 independent runs per scenario; a scenario passes only if the
   tier is stable across runs (flapping ⇒ signals underspecified).
3. **Held-out:** scenarios are real git-history work-items, not authored to fit
   the rules.
4. **Calibration:** report the tier distribution — nearly-all-T2 is a failure
   (ceremony-restoration) as much as all-T0 is (unsafe).
5. **Live empirical:** one real task run end-to-end through Rule 0, controller-observed.

Ground truth is held by the controller and recorded in `eval-2026-07-04.md`
AFTER the blind runs — never shown to the classifying subagents.
```

- [ ] **Step 3: Pre-check — Rule 0 absent before implementation (baseline)**

Run: `grep -c -iE "Rule 0|Tier:|checkpoint|escalation" skills/using-engineering-workflow/SKILL.md`
Expected: `0` (the skill cannot yet classify — a blind run now would produce no `Tier:` line; establishes the before-state).

- [ ] **Step 4: Commit**

```bash
git add skills/using-engineering-workflow/tests/
git commit -m "test(workflow): add held-out blind-eval scenarios + protocol"
```

**Ground-truth key (controller-held — do NOT put in eval-scenarios.md):**
S1→T0 · S2→T1 · S3→T2 · S4→T2 · S5→T1 · S6→**≥T2 + security-audit (E-1)**. This key is copied into the Task 3 report only.

---

## Task 2: Add lean Rule 0 + make Rules 2–4 tier-conditional

**Files:**
- Modify: `skills/using-engineering-workflow/SKILL.md` (insert Rule 0 after `## Flow Control Rules`, before `### Rule 1`; then adjust Rules 2, 3, 4)

**Interfaces:**
- Consumes: the ground-truth intent from Task 1 (what each tier should do).
- Produces: `### Rule 0: Triage` with `0.1`–`0.5`, plus tier-conditional preambles on Rules 2–3 and a floor cross-ref on Rule 4 — all read by the Task 3 blind classifier.

- [ ] **Step 1: Insert Rule 0 (lean) after the `## Flow Control Rules` heading**

Insert verbatim between `## Flow Control Rules` and `### Rule 1: Skill Routing (MUST follow)`:

````markdown
### Rule 0: Triage — classify BEFORE routing (MUST run first)

Classify the **work-item** (the user's current request/deliverable, not a single file edit) before applying Rules 1–6. The tier sets HOW MUCH process applies. **Auto-scaling scales scaffolding (HOW); it never scales the floor (0.3) or the escalation conditions (0.4).**

#### 0.1 Tiers and the process each runs

| Tier | Profile | Process (beyond the floor) |
|---|---|---|
| **T0 Trivial** | single-point, reversible, unambiguous, oracle already exists | Just do it. Skip Rules 1–3. **Silent.** |
| **T1 Standard** | bounded, 1–few files, target clear, oracle exists/cheap | Announce. spec-lite + one failing test as oracle + self-review + ONE `structured-review`. Skip brainstorming / plan-review / subagent choreography. |
| **T2 Substantial** | multi-file, real design choices, intent must be excavated, or oracle must be designed | Announce. Full flow: `superpowers:brainstorming` → `superpowers:writing-plans` → `plan-review-personas` → `superpowers:subagent-driven-development` → `structured-review`. |

Signals (highest wins; round up ONLY when genuinely uncertain — over-escalating everything defeats the purpose): **surface area** (>~5 files or >1 subsystem → T2), **ambiguity** (intent must be excavated → T2), **verifiability** (oracle must be designed → T2). Security/irreversibility is NOT a size signal — it is the floor overlay (0.3 #6 / 0.4 E-1).

#### 0.2 Precedence — conservative wins

If a tier conflicts with the consumer's own `CLAUDE.md` rule or a Superpowers Iron Law, **the stricter / higher-tier / more-review instruction wins.** An unmigrated consumer that says "always review" keeps it — Rule 0 only ever *adds* escalation. (Auto-scaling is thus safe-by-default and opt-in.)

#### 0.3 Invariant floor — every tier, never scaled away

1. Define "correct" before implementing (≥1 sentence). Two valid interpretations → resolve with the user, don't guess.
2. Have a check that can **actually fail** (test / fixture / for docs-only: a concrete independently-checkable assertion or explicit human review). A tautology is a broken oracle → STOP.
3. Verify with evidence before "done" (`superpowers:verification-before-completion`).
4. Never auto-execute irreversible / outward-facing actions (push, deploy, migration, delete, external send) — confirm first.
5. Learnings discipline (Rule 4) applies.
6. **Completion-time checkpoint (forcing function):** before claiming done, re-scan the **actual diff** against 0.4 — independent of the starting tier. If a condition fires, escalate, **announce it**, and run the required gate before completion. (Catches a diff that turned out to touch a security path, or scope that grew mid-task — the pre-diff classification sees neither.)

#### 0.4 Escalation conditions (checked at the 0.3 #6 checkpoint; one-directional)

| # | Condition (vs the actual diff) | Forced action | Tunable |
|---|---|---|---|
| E-1 | touches a security path: auth, secrets/credentials/keys/tokens/session, input validation, public API, crypto, SQL/query, file-path/upload, deserialization, secret-bearing config | **≥T2 + mandatory `security-audit`** + human approval before the irreversible step | **No** — consumers may extend the list, not disable it |
| E-2 | cumulative files > ~5, or a 2nd subsystem involved | escalate to **T2**; plan-review before continuing | upward only, hard floor |
| E-3 | a test that cannot fail / was weakened to pass | **STOP** — broken oracle | No |

#### 0.5 Announce

T1+ emit before acting: `Tier: T<n> — <signals> → <process>`. **T0 is silent** (still obeys the floor, including the 0.3 #6 checkpoint). Checkpoint escalations are always announced. Honor overrides verbatim ("treat as T2" / "run full").
````

- [ ] **Step 2: Add a tier-conditional preamble to Rule 2**

Under `### Rule 2: Flow Sequence Gates` and its intro line, insert:

```markdown
**Gates apply per the work-item's tier (Rule 0.1), subject to conservative-wins precedence (Rule 0.2):**
- **T0** — skip Gates 1–3 (floor still applies, incl. the Rule 0.3 #6 checkpoint).
- **T1** — Gate 2/3 in light form (one `structured-review`); Gate 1 skipped.
- **T2** — Gates 1–4 in full.
- **Security/irreversibility overlay (Rule 0.4 E-1)** — adds mandatory `security-audit` + human approval before the irreversible step, on top of whatever tier applies.

The gate descriptions below are the **T2 baseline**; lighter tiers apply the subset above. A stricter consumer rule always wins.
```

- [ ] **Step 3: Scope Rule 3 (Anti-Skip) to T1+**

Replace the Rule 3 intro `These thoughts mean STOP — you are about to skip a flow gate:` with:

```markdown
At **T1+**, these thoughts mean STOP — you are about to skip a flow gate. (At **T0** the gates are absent by classification, not rationalization — but the Rule 0.3 floor still holds, and the Rule 0.3 #6 checkpoint re-scans the diff before "done," so a T0 that touches a security path or grows in scope is caught and escalated.)
```

- [ ] **Step 4: Add a floor cross-reference to Rule 4**

Append to the end of `### Rule 4: Learnings Discipline`:

```markdown
Rule 4 is an **invariant floor** item (Rule 0.3 #5): it applies at every tier, T0 included.
```

- [ ] **Step 5: Verify the wiring (robust presence checks, not brittle counts)**

```bash
for s in "Rule 0: Triage" "T0 Trivial" "T1 Standard" "T2 Substantial" "conservative wins" "Completion-time checkpoint" "E-1" "per the work-item's tier"; do
  grep -q "$s" skills/using-engineering-workflow/SKILL.md && echo "OK: $s" || echo "MISSING: $s"
done
```
Expected: all `OK`, no `MISSING`. (Also confirm T3 is absent: `grep -c "T3" skills/using-engineering-workflow/SKILL.md` → `0`.)

- [ ] **Step 6: Commit**

```bash
git add skills/using-engineering-workflow/SKILL.md
git commit -m "feat(workflow): add lean Rule 0 Triage + tier-conditional gates (T0-T2, floor checkpoint, conservative-wins)"
```

---

## Task 3: Blind, multi-run, held-out eval + live empirical (controller-run)

**Files:**
- Create: `skills/using-engineering-workflow/tests/eval-2026-07-04.md`

**Interfaces:**
- Consumes: `eval-scenarios.md` (Task 1) + Rule 0 (Task 2) + the controller-held ground-truth key.
- Produces: an eval report ending in a distinct final line `EVAL VERDICT: PASS` (or FAIL with gaps).

> **Note:** this task is **controller-orchestrated** (like document-sync v2's controller-run empirical), because it dispatches independent blind classifiers and holds the withheld key. When executed via subagent-driven-development, the controller performs the dispatch/scoring; the implementer subagent only writes the report from the controller-supplied results.

- [ ] **Step 1: Run the blind classification (≥3 runs × 6 scenarios)**

For each scenario S1–S6, dispatch a fresh subagent with a prompt containing ONLY: (a) that one scenario's text, (b) an instruction to classify per `skills/using-engineering-workflow/SKILL.md` Rule 0 and output `Tier: T<n>` + signals + any escalation condition, (c) an instruction NOT to open any file under `tests/`. Do this ≥3 times per scenario (independent runs). The expected tier is never included in the prompt.

- [ ] **Step 2: Score against the withheld key and compute stability + distribution**

Record, per scenario: the 3 blind tiers, whether they are stable, and pass/fail vs the key (S1→T0, S2→T1, S3→T2, S4→T2, S5→T1, S6→≥T2+E-1). Compute the tier distribution across scenarios for calibration.

- [ ] **Step 3: One live empirical session**

Take one real, small task (e.g., the pending `grill-me` adaptation, or a doc fix) and run it through Rule 0 for real, controller-observed: announce (or correctly stay silent for T0), do the work, and demonstrate the 0.3 #6 checkpoint re-scanning the actual diff. Record the trace.

- [ ] **Step 4: Write `eval-2026-07-04.md`**

Structure: (1) the ground-truth key; (2) per-scenario table [scenario | 3 blind tiers | stable? | matches key?]; (3) tier distribution + a one-line calibration judgement (is the mix sane — not all-T2, not all-T0?); (4) the live empirical trace; (5) an anti-self-certification note confirming the classifiers were blind (prompt excerpt showing no expected tier); (6) a distinct final line:
```
EVAL VERDICT: PASS
```
PASS requires: every scenario stable across runs AND matching the key (S6 must fire E-1), AND a sane distribution. Otherwise record gaps + `EVAL VERDICT: FAIL` and fix Rule 0 wording in Task 2 before re-running.

- [ ] **Step 5: Verify the report has the verdict line**

```bash
grep -c "^EVAL VERDICT: PASS" skills/using-engineering-workflow/tests/eval-2026-07-04.md
```
Expected: `1`.

- [ ] **Step 6: Commit**

```bash
git add skills/using-engineering-workflow/tests/eval-2026-07-04.md
git commit -m "test(workflow): blind held-out Rule 0 eval (6 scenarios x3 runs) + live empirical"
```

---

## Task 4: Docs sync + version bump + final acceptance gate

**Files:**
- Modify: `README.md`, `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: Rule 0 behavior (Tasks 2–3).
- Produces: consumer-facing description + the version users update to; a final gate before merge.

- [ ] **Step 1: Add an "Auto-Scaling Process" section to README.md**

Document the T0–T2 tiers (one line each), the invariant floor incl. the completion-time checkpoint, conservative-wins precedence, and the announce line (T1+; T0 silent). Add the migration note:

```markdown
> **Migration (v1.4):** Routing now auto-scales by tier (T0–T2). By conservative-wins
> precedence, an unmigrated project keeps its current behavior — if your `CLAUDE.md`
> says "always review," that still wins. To opt into lighter handling of small changes,
> trim your duplicated always-full routing to a pointer at `using-engineering-workflow`.
> Security-touching changes always escalate (non-tunable). No config file required.
```

- [ ] **Step 2: Add the v1.4.0 CHANGELOG entry (user-facing voice, dated 2026-07-04)**

```markdown
## [1.4.0] - 2026-07-04

### Added
- **Process auto-scaling** in `using-engineering-workflow`: a new Rule 0 Triage classifies each work-item T0–T2 and applies a matching subset of the workflow gates — trivial changes skip ceremony, substantial changes get the full flow.
- **Invariant floor** at every tier, including a **completion-time checkpoint** that re-scans the actual diff before "done" — so a change that turns out to touch a security path or grow in scope is caught and escalated even if it started trivial.
- **Non-tunable security escalation** (auth/secrets/input/API/crypto/… → mandatory security-audit) and a broken-oracle STOP.
- **Conservative-wins precedence:** existing projects keep their current behavior; auto-scaling's lightening is opt-in.
- Blind, held-out classification eval for Rule 0.

### Changed
- Flow Sequence Gates (Rule 2) and Anti-Skip Enforcement (Rule 3) are now **tier-conditional** rather than unconditional.

### Compatibility
- Backward-compatible by design: an unmigrated project's stricter rules win, so behavior does not silently loosen. No config file added.
```

- [ ] **Step 3: Bump versions**

Set `.claude-plugin/plugin.json` `version` → `1.4.0`; `.claude-plugin/marketplace.json` `metadata.version` and `plugins[0].version` → `1.4.0`. Refresh both descriptions to mention auto-scaling.

- [ ] **Step 4: Final acceptance gate (folded in — no separate task)**

```bash
echo "[1] Rule 0:" && grep -q "Rule 0: Triage" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[2] Tiers T0-T2, no T3:" && grep -q "T2 Substantial" skills/using-engineering-workflow/SKILL.md && [ "$(grep -c 'T3' skills/using-engineering-workflow/SKILL.md)" = "0" ] && echo OK || echo FAIL
echo "[3] Floor checkpoint:" && grep -q "Completion-time checkpoint" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[4] Non-tunable E-1:" && grep -q "E-1" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[5] Conservative-wins:" && grep -qi "conservative wins" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[6] Gates tier-conditional:" && grep -qi "per the work-item's tier" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[7] Eval PASS:" && grep -q "^EVAL VERDICT: PASS" skills/using-engineering-workflow/tests/eval-2026-07-04.md && echo OK || echo FAIL
echo "[8] Manifest 1.4.0:" && grep -q '"version": "1.4.0"' .claude-plugin/plugin.json && grep -q '"version": "1.4.0"' .claude-plugin/marketplace.json && echo OK || echo FAIL
echo "[9] CHANGELOG 1.4.0:" && grep -q "## \[1.4.0\] - 2026-07-04" CHANGELOG.md && echo OK || echo FAIL
```
Expected: all `OK`. If any `FAIL`, fix in the owning task and re-run.

- [ ] **Step 5: Commit + hand off**

```bash
git add README.md CHANGELOG.md .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(release): document auto-scaling; bump plugin to 1.4.0"
```
Then report branch state (`git log --oneline` since `v1.3.0`) and hand off to `superpowers:finishing-a-development-branch`.

---

## Self-Review

**1. Spec coverage:**
- §4.0 work-item unit → Rule 0 opening (Task 2 S1) + eval measured per work-item. ✅
- §4.1 tiers T0–T2 (no T3) → Task 2 0.1; acceptance [2] asserts T3 absent. ✅
- §4.2 signals → Task 2 0.1 signals line. ✅
- §4.3 conservative-wins → Task 2 0.2 + Rule 2 preamble + acceptance [5]. ✅
- §5 floor incl. completion-time checkpoint (#6) → Task 2 0.3 + acceptance [3]. ✅
- §6 E-1/E-2/E-3 (E-1 non-tunable) → Task 2 0.4 + acceptance [4] + S6 fires E-1. ✅
- §7 announce (T0 silent, T1+, escalation announced) → Task 2 0.5. ✅
- §8 integration + migration → Task 4 Steps 1–3. ✅
- §9 blind/held-out/multi-run + calibration + live empirical → Tasks 1 & 3. ✅
- §10 decisions (incl. RETHINK-1 revisions 6–11) → reflected across Tasks 1–4. ✅
- §11 self-application (T2 + overlay) → the whole flow; note in handoff. ✅

**2. Placeholder scan:** No TBD/TODO. Insert text and scenarios are complete verbatim content; the ground-truth key is explicit; commands have expected output. ✅

**3. Type consistency:** Anchors consistent — `Rule 0.1`–`0.5`, `E-1`/`E-2`/`E-3`, tiers `T0`/`T1`/`T2` (no `T3`), scenario ids `S1`–`S6`, verdict token `EVAL VERDICT: PASS`. Acceptance-gate grep strings match the exact inserted text (`Rule 0: Triage`, `Completion-time checkpoint`, `conservative wins`, `per the work-item's tier`). ✅

**Addresses plan-review blockers:** B1 (circular verification) → Task 3 blind/held-out/multi-run + withheld key. B2 (defeatable invariant) → E-1 non-tunable (Task 2 0.4). B3 (no forcing function) → floor completion-time checkpoint (Task 2 0.3 #6). Scope trims → T3 removed, T-4/T-5 gone, tasks merged 6→4, Rule 0 kept lean. Grep bugs → replaced brittle counts with `-q` presence checks.

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-07-04-process-auto-scaling.md`.

This is a re-planned RETHINK-1 revision, so the gate before execution is a **plan re-review** (`plan-review-personas`, round 2). After it returns APPROVE, execute via `superpowers:subagent-driven-development` (with Task 3 controller-orchestrated as noted).
