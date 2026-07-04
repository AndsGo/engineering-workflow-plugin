# Process Auto-Scaling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tier-based triage front-door to `using-engineering-workflow` so the plugin auto-scales process weight to change size while enforcing a constant correctness floor.

**Architecture:** A new **Rule 0: Triage** is prepended to `skills/using-engineering-workflow/SKILL.md`. It classifies each task T0–T3 from observable signals, applies a tier-appropriate subset of the existing Gates (Rules 1–6), enforces an invariant floor at every tier, honors one-directional tripwires, and announces the tier (T1+) for a cheap user veto. Rules 2–3 become tier-conditional. Behavior is validated by fixture-first classification cases plus a verification report, mirroring document-sync v2.

**Tech Stack:** Markdown skill authoring (no runtime). "Tests" are behavior-level classification fixtures checked by a reasoning walkthrough with literal-token evidence gates (the document-sync v2 pattern). Bash for size/acceptance checks.

## Global Constraints

- Spec: `docs/specs/2026-07-04-process-auto-scaling-design.md` (authoritative; copy content verbatim where steps reference it).
- Target version: **1.4.0** (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` both `metadata.version` and `plugins[0].version`).
- The invariant floor is **stricter-or-equal** to current correctness behavior — never loosen a correctness guarantee; only make *scaffolding* conditional.
- **Backward compatible:** every existing consumer keeps working with no change; old always-full behavior is reachable via the pin-to-T2+ convention.
- Superpowers Iron Laws are re-expressed as the floor, never removed.
- Commits: incremental, manual, Chinese-or-English conventional-commit subject, end body with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Branch: `feat/v1.4-process-auto-scaling` (already created; no worktree, per repo precedent).

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `skills/using-engineering-workflow/tests/fixtures/*.md` | Classification oracle — one scenario per tier + tripwires | 1 |
| `skills/using-engineering-workflow/tests/README.md` | Fixture documentation | 1 |
| `skills/using-engineering-workflow/SKILL.md` | Add Rule 0 Triage (front-door) | 2 |
| `skills/using-engineering-workflow/SKILL.md` | Make Rules 2–3 tier-conditional; Rule 4 → floor cross-ref | 3 |
| `skills/using-engineering-workflow/tests/verification-2026-07-04.md` | Verification report (walkthrough + evidence gates + self-application) | 4 |
| `README.md` | Auto-scaling section + consumer migration note | 5 |
| `CHANGELOG.md` | v1.4.0 entry | 5 |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Version bump 1.3.0 → 1.4.0 | 5 |

---

## Task 1: Classification fixtures (the oracle, written first)

**Files:**
- Create: `skills/using-engineering-workflow/tests/fixtures/t0-version-bump.md`
- Create: `skills/using-engineering-workflow/tests/fixtures/t1-bugfix-with-test.md`
- Create: `skills/using-engineering-workflow/tests/fixtures/t2-multifile-feature.md`
- Create: `skills/using-engineering-workflow/tests/fixtures/t3-auth-change.md`
- Create: `skills/using-engineering-workflow/tests/fixtures/tripwire-scope-creep.md`
- Create: `skills/using-engineering-workflow/tests/fixtures/tripwire-unfailable-test.md`
- Create: `skills/using-engineering-workflow/tests/README.md`

**Interfaces:**
- Produces: fixture files each containing `Scenario`, `Expected tier`, `Expected process`, and `Pass criteria (literal tokens)`. Task 4's verification report consumes these exact tokens.

- [ ] **Step 1: Create fixture `t0-version-bump.md`**

```markdown
# Fixture: t0-version-bump

## Scenario
Bump the plugin manifest version from 1.4.0 to 1.4.1 in `.claude-plugin/plugin.json`. One file, one field, fully reversible, no behavior change.

## Expected tier
T0

## Expected process
Just do it + invariant floor. No brainstorming, no plan, no plan-review, no structured-review gate. **Silent** (T0 does not announce).

## Pass criteria (literal tokens a correct triage MUST contain)
- `T0`
- one of: `reversible`, `single-point`, `one file`
- `floor` (floor still applies)
- MUST NOT invoke: `plan-review-personas`, `subagent-driven-development`
```

- [ ] **Step 2: Create fixture `t1-bugfix-with-test.md`**

```markdown
# Fixture: t1-bugfix-with-test

## Scenario
Fix an off-by-one in `parse_learnings.py` date parsing. 1–2 files, clear repro, existing pytest suite already covers the module (oracle exists / cheap to extend).

## Expected tier
T1

## Expected process
Announce tier. spec-lite (a few sentences) + one failing test as oracle + self-review + ONE structured-review. Skip brainstorming, plan-review-personas, subagent choreography.

## Pass criteria (literal tokens)
- `Tier: T1`
- one of: `oracle exists`, `existing test`, `bounded`
- `structured-review`
- one of: `spec-lite`, `one test`, `failing test`
- MUST NOT invoke: `plan-review-personas`, `brainstorming`
```

- [ ] **Step 3: Create fixture `t2-multifile-feature.md`**

```markdown
# Fixture: t2-multifile-feature

## Scenario
Add a new `engineering-retro` output mode spanning the skill file, a new template, and a docs update — several files, real design choices, the oracle (what "good retro output" is) must be designed.

## Expected tier
T2

## Expected process
Announce tier. Full flow: brainstorming → writing-plans → plan-review-personas → subagent-driven-development → structured-review. Gates 1–4 apply.

## Pass criteria (literal tokens)
- `Tier: T2`
- `brainstorming`
- `plan-review-personas`
- `subagent-driven-development`
- one of: `design choices`, `oracle must be designed`, `multi-file`
```

- [ ] **Step 4: Create fixture `t3-auth-change.md`**

```markdown
# Fixture: t3-auth-change

## Scenario
A change whose diff touches an authentication/token-handling path (e.g., a `verifyToken`/session helper). Even if only 2 files, the security-sensitive path dominates.

## Expected tier
T3 (via tripwire T-1)

## Expected process
Announce tier + announce escalation. T2 flow PLUS mandatory security-audit + adversarial verification + human approval before the irreversible step. Cannot be auto-downgraded.

## Pass criteria (literal tokens)
- `Tier: T3`
- `security-audit`
- one of: `auth`, `token`, `security-sensitive`
- one of: `cannot be auto-downgraded`, `mandatory`, `human approval`
```

- [ ] **Step 5: Create fixture `tripwire-scope-creep.md`**

```markdown
# Fixture: tripwire-scope-creep

## Scenario
A task classified T1 at the start (fix one helper). Mid-implementation it turns out the fix requires editing 7 files across a second subsystem.

## Expected tier
Starts T1 → auto-upgrades to T2 via tripwire T-2. One-directional (does not drop back to T1).

## Expected process
Announce the escalation. Run plan-review before continuing. Upgrade cannot be auto-reversed within the task.

## Pass criteria (literal tokens)
- `T1` and `T2` (both — showing the transition)
- one of: `escalate`, `upgrade`, `tripwire`
- one of: `plan-review`, `Gate 1`
- one of: `one-directional`, `cannot`, `not reversed`
```

- [ ] **Step 6: Create fixture `tripwire-unfailable-test.md`**

```markdown
# Fixture: tripwire-unfailable-test

## Scenario
During a T1 task the implementer writes `assert True` / a test asserting a tautology that passes regardless of the code under test.

## Expected tier
Any tier → STOP (tripwire T-3: oracle broken).

## Expected process
Halt. The check cannot fail, so it is not an oracle. Fix the check before proceeding. Do not claim done.

## Pass criteria (literal tokens)
- `STOP`
- one of: `cannot fail`, `oracle`, `tautology`
- one of: `fix the check`, `broken`
```

- [ ] **Step 7: Create `tests/README.md`**

```markdown
# using-engineering-workflow — Classification Fixtures

Behavior-level fixtures for **Rule 0: Triage** (plugin v1.4). Each fixture is a
task scenario with the expected tier, expected process, and the literal tokens a
correct triage output must contain. Verified by a reasoning walkthrough (see
`../verification-2026-07-04.md`), mirroring document-sync v2's fixture approach.

| Fixture | Exercises |
|---|---|
| `t0-version-bump` | T0 trivial → floor-only, silent |
| `t1-bugfix-with-test` | T1 standard → spec-lite + 1 test + 1 review |
| `t2-multifile-feature` | T2 substantial → full flow |
| `t3-auth-change` | T3 via tripwire T-1 → security-audit mandatory |
| `tripwire-scope-creep` | T-2 mid-task upgrade (one-directional) |
| `tripwire-unfailable-test` | T-3 broken-oracle STOP |

These are the oracle for Rule 0. They are written BEFORE Rule 0 (fixture-first):
against the pre-Rule-0 skill a walkthrough produces no tier line, so the fixtures
fail; after Rule 0 they pass.
```

- [ ] **Step 8: Verify fixtures fail against the current skill (red)**

Run: read `skills/using-engineering-workflow/SKILL.md` and confirm it has **no Rule 0 / no tier / no triage** section.

```bash
grep -c -iE "Rule 0|Tier:|triage" skills/using-engineering-workflow/SKILL.md
```
Expected: `0` (skill cannot yet produce any fixture's required `Tier:` / `T0` tokens → fixtures are red).

- [ ] **Step 9: Commit**

```bash
git add skills/using-engineering-workflow/tests/
git commit -m "test(workflow): add T0-T3 + tripwire classification fixtures (red)"
```

---

## Task 2: Add Rule 0 Triage front-door

**Files:**
- Modify: `skills/using-engineering-workflow/SKILL.md` (insert new section immediately after the `## Flow Control Rules` heading, before `### Rule 1`)

**Interfaces:**
- Consumes: fixture token expectations from Task 1.
- Produces: `### Rule 0: Triage` with sub-sections `0.1` tiers, `0.2` signals, `0.3` floor, `0.4` tripwires, `0.5` announce — referenced by Task 3 (gates) and Task 4 (verification).

- [ ] **Step 1: Insert Rule 0 after the `## Flow Control Rules` line**

Insert this block (verbatim) between `## Flow Control Rules` and `### Rule 1: Skill Routing (MUST follow)`:

````markdown
### Rule 0: Triage — classify BEFORE routing (MUST run first)

Before applying Rules 1–6, classify the task into a tier. The tier decides HOW MUCH of the process below applies. **Auto-scaling scales the scaffolding (HOW); it never scales the invariant floor (0.3) or the tripwires (0.4).** When uncertain, round UP.

#### 0.1 Tiers

| Tier | Profile | Process (beyond the floor) |
|---|---|---|
| **T0 Trivial** | single-point, reversible, target unambiguous, oracle already exists | Just do it. Skip Rules 1–3 gates. |
| **T1 Standard** | bounded feature/bugfix, 1–few files, target mostly clear, oracle exists or cheap | spec-lite (a few sentences) + one failing test as oracle + self-review + ONE `structured-review`. Skip brainstorming, plan-review-personas, subagent choreography. |
| **T2 Substantial** | multi-file, real design choices, intent needs excavation, or oracle must be designed | Full flow: `superpowers:brainstorming` → `superpowers:writing-plans` → `plan-review-personas` → `superpowers:subagent-driven-development` → `structured-review`. Gates 1–4 apply. |
| **T3 High-stakes / irreversible** | touches auth / secrets / user-input / migrations / public API / other consumers of this plugin, or hard to reverse | T2 **plus** mandatory `security-audit` + adversarial verification + human approval before the irreversible step. **Cannot be auto-downgraded.** |

#### 0.2 Classification signals (read each; highest-triggered tier wins; round UP when uncertain)

| Dimension | Pushes tier up when… |
|---|---|
| Reversibility / blast radius | touches `main` directly, outward-facing action, affects other consumers, migration/schema → T2+; secrets/auth/migration/public-API → **T3** |
| Surface area | > ~5 files or > 1 subsystem with integration → T2+ |
| Ambiguity | intent must be excavated → T2+ |
| Verifiability | oracle must be designed (not merely extended) → T2+ |

#### 0.3 Invariant floor — holds at EVERY tier, never scaled away

1. Define "correct" before implementing (≥1 explicit sentence).
2. Have a check that can **actually fail** (test / fixture / evidence-backed manual observation).
3. Verify with evidence before claiming done (`superpowers:verification-before-completion`).
4. Never auto-execute irreversible / outward-facing actions (push, deploy, migration, delete, external send) — confirm first.
5. Learnings discipline (Rule 4) applies.

#### 0.4 Tripwires — one-directional (only ever upgrade; cannot auto-downgrade mid-task)

| Observed fact | Forced action |
|---|---|
| diff touches a security-sensitive path: auth/authn/authz, secrets/credentials/keys/tokens/session, input validation & sanitization, public API surface, crypto, SQL/query construction, file path & upload handling, deserialization, secret-bearing config | escalate to **T3**; `security-audit` mandatory |
| files touched exceed ~5, or a second subsystem gets involved | escalate to at least **T2**; run plan-review (Gate 1) before continuing |
| a test was written that **cannot fail**, or a test was weakened to pass | **STOP** — the oracle is broken; fix the check before proceeding |
| a second valid interpretation of the target appears mid-task | bounce back to spec/clarify (do not guess) |
| actual reversibility turns out worse than assumed | escalate one tier |

Thresholds ("~5 files", the security-path list) are project-tunable — a consumer may override them in its own CLAUDE.md.

#### 0.5 Announce the tier

At the start of any **T1+** task, emit one line before acting:

```
Tier: T<n> — <one-line signal reading> → <process to run>
```

**T0 is silent** (it still obeys the floor; narrating a trivial change is itself ceremony noise). Tripwire escalations are **always** announced (the upgrade is the noteworthy event). Honor manual overrides verbatim ("treat as T2" / "run full").
````

- [ ] **Step 2: Verify Rule 0 present and well-formed**

```bash
grep -c -iE "Rule 0|Tier:|floor|tripwire" skills/using-engineering-workflow/SKILL.md
```
Expected: ≥ 8 (multiple hits across the new section).

- [ ] **Step 3: Commit**

```bash
git add skills/using-engineering-workflow/SKILL.md
git commit -m "feat(workflow): add Rule 0 Triage front-door (T0-T3 + floor + tripwires + announce)"
```

---

## Task 3: Make Rules 2–3 tier-conditional; Rule 4 floor cross-ref

**Files:**
- Modify: `skills/using-engineering-workflow/SKILL.md` (Rule 2 preamble, Rule 3 preamble, Rule 4 note)

**Interfaces:**
- Consumes: Rule 0.1 tier definitions from Task 2.
- Produces: gate application conditioned on tier — Task 4 verification checks this wiring.

- [ ] **Step 1: Add a tier-conditional preamble to Rule 2**

Immediately under `### Rule 2: Flow Sequence Gates` and its existing intro line, insert:

```markdown
**Gates apply per the task's tier (Rule 0.1):**
- **T0** — skip Gates 1–3 entirely (floor still applies).
- **T1** — Gate 2/3 apply in light form (one `structured-review`); Gate 1 (plan-review) is skipped.
- **T2** — Gates 1–4 apply in full.
- **T3** — Gates 1–4 apply, plus `security-audit` is mandatory and a human approval precedes any irreversible step.

The gate descriptions below are the **T2 baseline**; lighter tiers apply the subset above.
```

- [ ] **Step 2: Scope Rule 3 (Anti-Skip) to T1+**

Under `### Rule 3: Anti-Skip Enforcement`, replace the intro sentence
`These thoughts mean STOP — you are about to skip a flow gate:`
with:

```markdown
At **T1+**, these thoughts mean STOP — you are about to skip a flow gate. (At **T0** the gates are intentionally absent by classification, not by rationalization — but the invariant floor in Rule 0.3 still holds, and any tripwire in Rule 0.4 overrides the T0 classification.)
```

- [ ] **Step 3: Add a floor cross-reference to Rule 4**

At the end of `### Rule 4: Learnings Discipline`, append:

```markdown
Rule 4 is an **invariant floor** item (Rule 0.3 #5): it applies at every tier, T0 included.
```

- [ ] **Step 4: Verify wiring**

```bash
grep -c -iE "per the task's tier|T1\+|invariant floor" skills/using-engineering-workflow/SKILL.md
```
Expected: ≥ 3.

- [ ] **Step 5: Commit**

```bash
git add skills/using-engineering-workflow/SKILL.md
git commit -m "feat(workflow): make Gates 2-3 tier-conditional; Rule 4 floor cross-ref"
```

---

## Task 4: Verification report (walkthrough + evidence gates + self-application)

**Files:**
- Create: `skills/using-engineering-workflow/tests/verification-2026-07-04.md`

**Interfaces:**
- Consumes: all six fixtures (Task 1) + Rule 0 (Task 2) + tier-conditional gates (Task 3).
- Produces: a report ending in a literal `Verdict: PASS` line (matched by the Task 6 acceptance gate).

- [ ] **Step 1: For each fixture, predict the triage output and check literal tokens**

For every fixture in `tests/fixtures/`, walk the skill's Rule 0 against the scenario and record: the produced `Tier:` line (or `STOP`), which signals/tripwires fired, and a per-fixture check that **every** literal token in that fixture's `Pass criteria` is present and every `MUST NOT` token is absent. Structure each section like document-sync v2's `verification-2026-04-30.md` (Predicted output → Pass-criteria check → `Verdict: PASS`).

- [ ] **Step 2: Self-application check (spec §11)**

Add a section that runs Rule 0 on **this v1.4 change itself** and confirms it classifies as **T2 bordering T3** (rewrites the plugin's core contract; affects every consumer's routing). Evidence: cite the Reversibility/blast-radius signal ("affects other consumers of this plugin"). This proves the framework classifies itself as heavyweight — the intended demonstration.

- [ ] **Step 3: Write the summary table + final verdict**

Include a summary table (fixture → result) and a final line exactly:
```
Verdict: PASS
```
(only if all six fixtures pass AND the self-application check holds; otherwise record gaps and `Verdict: FAIL`).

- [ ] **Step 4: Verify the report has the pass line**

```bash
grep -c "^Verdict: PASS" skills/using-engineering-workflow/tests/verification-2026-07-04.md
```
Expected: `1`.

- [ ] **Step 5: Commit**

```bash
git add skills/using-engineering-workflow/tests/verification-2026-07-04.md
git commit -m "test(workflow): Rule 0 triage verification report (6 fixtures + self-application)"
```

---

## Task 5: Docs sync + version bump

**Files:**
- Modify: `README.md` (add auto-scaling section + consumer migration note)
- Modify: `CHANGELOG.md` (v1.4.0 entry)
- Modify: `.claude-plugin/plugin.json` (version → 1.4.0)
- Modify: `.claude-plugin/marketplace.json` (`metadata.version` + `plugins[0].version` → 1.4.0)

**Interfaces:**
- Consumes: Rule 0 behavior (Tasks 2–3).
- Produces: consumer-facing description of auto-scaling; the version other users update to.

- [ ] **Step 1: Add an "Auto-Scaling Process" section to README.md**

Add a section documenting: the T0–T3 tiers (one line each), the invariant floor, the announce-the-tier line (T1+ only, T0 silent), and a **Consumer migration note**:

```markdown
> **Migration (v1.4):** Routing now auto-scales by tier (T0–T3). If your project's
> `CLAUDE.md` duplicates the old always-full routing, you can trim it to a pointer at
> `using-engineering-workflow`. To keep the pre-v1.4 always-full behavior, add a line
> pinning tasks to T2+, or say "treat as T2" per task. No config file is required.
```

- [ ] **Step 2: Add the v1.4.0 CHANGELOG entry**

Prepend under the changelog's top, user-facing voice, dated `2026-07-04`:

```markdown
## [1.4.0] - 2026-07-04

### Added
- **Process auto-scaling** in `using-engineering-workflow`: a new Rule 0 Triage classifies each task T0–T3 and applies a matching subset of the workflow gates — trivial changes skip ceremony, substantial/high-stakes changes get the full flow.
- **Invariant floor** applied at every tier (define-correct-first, a check that can fail, evidence-before-done, no auto-irreversible actions, learnings discipline).
- **One-directional tripwires** that auto-escalate mid-task (security paths → T3 + mandatory security-audit; scope creep → T2 + plan-review; an unfailable test → STOP).
- Classification fixtures + verification report for Rule 0.

### Changed
- Flow Sequence Gates (Rule 2) and Anti-Skip Enforcement (Rule 3) are now **tier-conditional** rather than unconditional.

### Compatibility
- Backward-compatible: existing consumers keep working unchanged. Old always-full behavior is reachable via the pin-to-T2+ convention or a per-task "treat as T2" override. No config file added.
```

- [ ] **Step 3: Bump versions**

Set `.claude-plugin/plugin.json` `version` to `1.4.0`. Set `.claude-plugin/marketplace.json` `metadata.version` and `plugins[0].version` to `1.4.0`. Refresh the two descriptions to mention auto-scaling.

- [ ] **Step 4: Verify versions**

```bash
grep -H '"version"' .claude-plugin/plugin.json && grep -H '"version"' .claude-plugin/marketplace.json && grep -c "## \[1.4.0\] - 2026-07-04" CHANGELOG.md
```
Expected: `1.4.0` in plugin.json; two `1.4.0` in marketplace.json; CHANGELOG count `1`.

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(release): document auto-scaling; bump plugin to 1.4.0"
```

---

## Task 6: Final acceptance gate

**Files:** none (verification only)

**Interfaces:**
- Consumes: all prior tasks.
- Produces: a pass/fail gate before merge/tag.

- [ ] **Step 1: Run the acceptance checks**

```bash
echo "[1] Rule 0 present:" && grep -q "Rule 0: Triage" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[2] Tiers T0-T3:" && for t in "T0 Trivial" "T1 Standard" "T2 Substantial" "T3 High-stakes"; do grep -q "$t" skills/using-engineering-workflow/SKILL.md || echo "  MISSING $t"; done; echo "  (blank above = OK)"
echo "[3] Floor present:" && grep -q "Invariant floor" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[4] Tripwires one-directional:" && grep -qi "one-directional" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[5] Announce + T0 silent:" && grep -qi "T0 is silent" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[6] Gates tier-conditional:" && grep -qi "per the task's tier" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[7] 6 fixtures present:" && ls skills/using-engineering-workflow/tests/fixtures/*.md | wc -l
echo "[8] Verification PASS:" && grep -q "^Verdict: PASS" skills/using-engineering-workflow/tests/verification-2026-07-04.md && echo OK || echo FAIL
echo "[9] Manifest 1.4.0:" && grep -q '"version": "1.4.0"' .claude-plugin/plugin.json && grep -q '"version": "1.4.0"' .claude-plugin/marketplace.json && echo OK || echo FAIL
echo "[10] CHANGELOG 1.4.0:" && grep -q "## \[1.4.0\] - 2026-07-04" CHANGELOG.md && echo OK || echo FAIL
```
Expected: `[7]` prints `6`; all others `OK` with no `MISSING`.

- [ ] **Step 2: Report result**

If all checks pass, report the branch state (`git log --oneline` since `v1.3.0`) and hand off to `superpowers:finishing-a-development-branch`. If any check fails, fix in the owning task and re-run.

---

## Self-Review

**1. Spec coverage:**
- §4 tiers → Task 2 Step 1 (0.1) + fixtures t0–t3. ✅
- §4.2 signals → Task 2 Step 1 (0.2). ✅
- §5 floor → Task 2 (0.3) + Task 3 Step 3 (Rule 4 cross-ref) + fixtures assert `floor`. ✅
- §6 tripwires → Task 2 (0.4) + fixtures tripwire-scope-creep / tripwire-unfailable-test. ✅
- §7 announce (T0 silent, T1+ announce, override) → Task 2 (0.5) + t0 asserts silent, t1/t2/t3 assert `Tier:`. ✅
- §8 integration (Rule 2/3 conditional, README, CHANGELOG, version) → Tasks 3 & 5. ✅
- §9 test strategy (6 fixtures + evidence gates) → Tasks 1 & 4. ✅
- §10 decisions (front-door, silent-T0, no config, expanded security list, migration out of scope) → reflected in Tasks 2/3/5. ✅
- §11 self-application → Task 4 Step 2. ✅

**2. Placeholder scan:** No TBD/TODO. All insert text and fixtures are complete verbatim content. Commands have expected output. ✅

**3. Type consistency:** Section anchors are consistent everywhere — `Rule 0.1`–`0.5`, `Gate 1`–`4`, tier tokens `T0`/`T1`/`T2`/`T3`, tripwire references. Fixture pass-criteria tokens match the exact strings in the Rule 0 text (`security-audit`, `plan-review-personas`, `structured-review`, `one-directional`, `STOP`, `Tier: T<n>`). ✅

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-07-04-process-auto-scaling.md`.

Per the workflow, the gate before execution is `plan-review-personas` (this is a T2/T3 change). After plan review passes, execute via `superpowers:subagent-driven-development` (fresh subagent per task + two-stage review).
