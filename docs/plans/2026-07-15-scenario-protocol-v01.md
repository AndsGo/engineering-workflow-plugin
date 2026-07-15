# Scenario Protocol v0.1 Implementation Plan (plugin v1.6)

> **For agentic workers:** Small 3-task plan. Task 2 is controller-orchestrated (blind eval). Steps use checkbox (`- [ ]`) syntax.

**Goal:** Ship the scenario-protocol v0.1 contract into the plugin (reference doc + floor hook + docs + version 1.6.0), validated by a blind teachability eval.

**Architecture:** One new versioned reference doc (`references/scenario-protocol.md`, styled after `learnings-protocol.md`), one sentence added to Rule 0's floor, README/CHANGELOG/manifest updates. The oracle is a two-part blind eval (authoring + rejection) run by the controller, mirroring the validated v1.4 pattern.

**Tech Stack:** Markdown authoring; blind subagent eval; bash acceptance greps.

## Global Constraints

- Spec: `docs/specs/2026-07-15-scenario-protocol-v01-design.md` (authoritative).
- Target version **1.6.0** (plugin.json; marketplace.json ×2 fields).
- Contract doc matches `learnings-protocol.md` conventions: English, normative MUST, versioned header, Failure Modes section.
- Rule 0 stays lean — the floor hook is ONE sentence + pointer, no restatement.
- Branch: `feat/v1.6-scenario-protocol` (current). Commits incremental, `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

## Task 1: Author `references/scenario-protocol.md`

**Files:** Create: `skills/using-engineering-workflow/references/scenario-protocol.md`

- [ ] **Step 1: Write the contract verbatim:**

````markdown
# Scenario Protocol — v0.1

**Versioning:** This is protocol v0.1. Scenario files declare `protocol: scenario/v0.1`; engines MUST reject unknown versions. Breaking changes bump the version and document migration.

Business-acceptance scenarios: **user-confirmed Given-When-Then with observable bindings**, written before implementation, mechanically verified against the *running system*. This closes the gap where every gate checks the previous translation (code vs plan) but nothing checks delivered behavior vs business intent.

## Division of Labor

| Layer | Owns |
|---|---|
| **This contract** | schema, discipline rules, engine exit-code semantics |
| **loop-engine** (standalone repo) | stateless one-shot verify: parse → validate → compile to sensor (hurl) → run → normalized verdict JSON. Mechanical asserts only; no LLM judge, no retry-loop driving. |
| **Session** (loop driver) | implement→verify→retry loop (cap 2 rounds), finding routing, held-out orchestration, human escalation |

## Schema (v0.1)

One YAML file per feature: `scenarios/<feature>.yaml`; held-out variants in `scenarios/held-out/<feature>.yaml`.

```yaml
protocol: scenario/v0.1
feature: config-reload
base_url_env: LOOP_BASE_URL
scenarios:
  - id: reload-happy-path            # unique, kebab-case
    title: 配置重载成功后返回应用结果      # business language
    given: server 正在运行且配置文件合法  # prose precondition, mandatory
    setup:                            # optional machine steps for `given`
      - request: { method: GET, path: /api/v1/health }
        expect: [ { status: 200 } ]
    when:                             # exactly ONE trigger request
      request:
        method: POST
        path: /api/v1/admin/config/reload
        headers: { Authorization: "Bearer ${ADMIN_TOKEN}" }   # secrets via ${ENV} only
    then:                             # ≥1 mechanical assertion = the observable binding
      - status: 200
      - header: { name: Content-Type, contains: application/json }
      - jsonpath: { path: "$.applied", equals: true }
      - jsonpath: { path: "$.version", exists: true }
    retry:                            # optional eventually-semantics
      until_pass: true
      max_attempts: 30
      interval_ms: 1000
```

**Hard rules (engine MUST reject at parse time — broken oracle, Rule 0.4 E-3 at spec time):**

1. `then` non-empty; assertion types limited to `status` / `header` / `jsonpath` / `body_contains`. Expectations not expressible in these observables do not belong in scenario files — rewrite observably or route to human review.
2. `when` contains exactly one request. Multi-step flows = `setup` + one trigger; flows needing multiple verdicts = multiple scenarios.
3. `given` prose is mandatory even when `setup` exists.
4. Secrets only via `${ENV}` interpolation; literal tokens rejected.
5. `protocol` field present and known.

**Scenario boundary:** scenarios cover business rules (what the feature promises callers), not technical edge cases (unit tests own those). Budget 5–12 per feature; more is scenario-explosion.

## Discipline

1. **Sign-off.** Model drafts scenarios from the brainstorm/spec; the **user confirms each one**. Only confirmed scenarios are oracles; confirmation is recorded in the feature spec. Unconfirmed files are advisory, never gating.
2. **Held-out (anti-Goodhart).** At sign-off, ≥1 scenario is designated held-out → `scenarios/held-out/`, which the implementer MUST NOT read. Controller runs it only at completion. Held-out failure after main green = overfitting signal; route back the *evidence*, not the scenario text.
3. **Tier mounting (conservative-wins).** For adopted projects (see Adoption): T2 work-items with an HTTP-observable surface MUST have confirmed scenarios before implementation and a green verdict (main + held-out) before "done". T1: recommended (one scenario). T0 / no observable surface: exempt. Non-adopted projects: unaffected.
4. **Engine exit codes (normative):** `0` all green · `1` scenario failure (real red → one implementation retry round) · `2` sensor/environment failure (fake red → fix environment; does NOT consume a retry round).
5. **Loop protocol (informative).** implement → run engine → exit 1: route per-scenario finding `{id, evidence, diff}` to implementer, retry (cap 2; same scenario failing twice with different fixes → escalate to human: the scenario is ambiguous or the architecture can't satisfy it) → exit 0 + held-out green: done.

## Failure Modes (do not do)

- ❌ Implementer reads `scenarios/held-out/` (breaks anti-Goodhart blindness)
- ❌ Gating on unconfirmed scenarios (no sign-off = no oracle)
- ❌ Fuzzy assertions ("response looks right") — not expressible in v0.1
- ❌ Weakening a scenario to make it pass without user re-confirmation (oracle tamper → STOP, Rule 0.4 E-3)
- ❌ Literal secrets in scenario files
- ❌ Engine driving the retry loop or judging fuzzily (session owns the loop; v0.1 is mechanical only)

## Adoption

A project adopts by adding one line to its `CLAUDE.md`:

> 本项目已采纳 scenario-protocol (v0.1)：T2 且有 HTTP 观察面的工作项，实现前需用户确认验收场景，完成需 loop-engine 绿色裁决（含 held-out）。

Effect: Rule 0.3 floor item #2 hardens as described in Tier mounting. Non-adopted projects are unaffected — this protocol only ever *adds* gates (Rule 0.2 conservative-wins).
````

- [ ] **Step 2: Verify + commit**

```bash
grep -c "scenario/v0.1" skills/using-engineering-workflow/references/scenario-protocol.md   # expect ≥2
git add skills/using-engineering-workflow/references/scenario-protocol.md
git commit -m "feat(workflow): scenario-protocol v0.1 contract (schema + discipline)"
```

---

## Task 2: Blind teachability eval (controller-orchestrated)

**Files:** Create: `skills/using-engineering-workflow/tests/eval-scenario-protocol-2026-07-15.md`

> Controller dispatches blind subagents (contract text pasted inline, NO repo tools, no examples beyond the contract itself); implementer-style delegation would break blindness.

- [ ] **Step 1: Authoring check ×2.** Fresh subagent gets: the contract text + a toy endpoint description (`POST /api/v1/notes` → 201 + `{id, text}`; `GET /api/v1/notes/{id}` → 200 or 404) + instruction to author a scenario file with ≥2 scenarios including one 404 case. Grade mechanically against the 5 hard rules. Both runs must produce valid files.
- [ ] **Step 2: Rejection check ×2.** Fresh subagent gets: the contract text + this planted-violation file VERBATIM (exactly 3 violations: rule 1 fuzzy assertion type, rule 2 two requests, rule 4 literal secret — `protocol`/`given`/non-empty-`then` are deliberately valid so ground truth stays exactly 3). Must name all 3; both runs must catch 3/3.

```yaml
protocol: scenario/v0.1
feature: notes-broken
base_url_env: LOOP_BASE_URL
scenarios:
  - id: create-note-broken
    title: 创建笔记后返回该笔记
    given: server 正在运行
    when:
      - request:
          method: POST
          path: /api/v1/notes
          headers: { Authorization: "Bearer sk-live-abc123" }
      - request:
          method: GET
          path: /api/v1/notes/1
    then:
      - status: 201
      - looks: friendly
```
- [ ] **Step 3: Write the eval report** (ground truth, per-run results, prompt excerpt proving blindness) ending with exactly `EVAL VERDICT: PASS` (only if 4/4 runs pass; otherwise FAIL + fix contract wording in Task 1 and re-run). Include a **Known Gaps** note: operator vocabulary inside assertion types (`equals`/`exists`/`contains`) is exemplified, not normatively enumerated — accepted v0.1 looseness, to be sealed by Stage A findings (per spec §7.3), not by speculating ahead of the engine.
- [ ] **Step 4: Verify + commit**

```bash
grep -c "^EVAL VERDICT: PASS" skills/using-engineering-workflow/tests/eval-scenario-protocol-2026-07-15.md   # expect 1
git add skills/using-engineering-workflow/tests/eval-scenario-protocol-2026-07-15.md
git commit -m "test(workflow): blind teachability eval for scenario-protocol v0.1"
```

---

## Task 3: Integration + version bump + acceptance gate

**Files:** Modify: `skills/using-engineering-workflow/SKILL.md`, `README.md`, `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] **Step 1: Floor hook.** In `SKILL.md` Rule 0.3, append to item 2 (after "A tautology is a broken oracle → STOP."):

```
For scenario-protocol-adopted projects, a T2 work-item with an HTTP-observable surface requires user-confirmed acceptance scenarios + a green loop-engine verdict (see `references/scenario-protocol.md`).
```

- [ ] **Step 2: README.** Add as a SIBLING section (`##`, not nested) after the Process Auto-Scaling section:

```markdown
## Scenario Protocol (v1.6)

Business-acceptance scenarios as a machine-checkable contract: user-confirmed Given-When-Then with observable bindings, compiled and verified against the running system by the standalone loop-engine (forthcoming, separate repo). Opt-in per project (conservative-wins); see `skills/using-engineering-workflow/references/scenario-protocol.md`.
```

- [ ] **Step 3: CHANGELOG** (prepend above 1.5.0, keep all entries):

```markdown
## [1.6.0] - 2026-07-15

### Added
- **Scenario Protocol v0.1** (`references/scenario-protocol.md`): business-acceptance scenarios as a machine-checkable contract — YAML Given-When-Then with mandatory observable bindings, user sign-off, held-out anti-overfitting scenarios, and engine exit-code semantics. Consumed by the standalone loop-engine; adoption is opt-in per project (conservative-wins).
- Rule 0 floor hook: adopted projects' T2 work with an HTTP surface gates "done" on a green scenario verdict.

### Compatibility
- No behavior change for non-adopted projects. No new skill added.
```

- [ ] **Step 4: Version bump** plugin.json + marketplace.json (×2) → `1.6.0`. Verify:

```bash
grep -c '"version": "1.6.0"' .claude-plugin/marketplace.json   # expect exactly 2
python -m json.tool .claude-plugin/plugin.json > /dev/null && python -m json.tool .claude-plugin/marketplace.json > /dev/null && echo "json ok"
```
- [ ] **Step 5: Acceptance gate**

```bash
echo "[1]"; grep -q "Scenario Protocol — v0.1" skills/using-engineering-workflow/references/scenario-protocol.md && echo OK || echo FAIL
echo "[2]"; grep -q "scenario-protocol-adopted" skills/using-engineering-workflow/SKILL.md && echo OK || echo FAIL
echo "[3]"; grep -q "^EVAL VERDICT: PASS" skills/using-engineering-workflow/tests/eval-scenario-protocol-2026-07-15.md && echo OK || echo FAIL
echo "[4]"; grep -q '"version": "1.6.0"' .claude-plugin/plugin.json && grep -q '"version": "1.6.0"' .claude-plugin/marketplace.json && echo OK || echo FAIL
echo "[5]"; grep -q "## \[1.6.0\] - 2026-07-15" CHANGELOG.md && echo OK || echo FAIL
echo "[6] held-out + sign-off + exit codes in contract:"; grep -q "held-out" skills/using-engineering-workflow/references/scenario-protocol.md && grep -q "Sign-off" skills/using-engineering-workflow/references/scenario-protocol.md && grep -q "exit code" skills/using-engineering-workflow/references/scenario-protocol.md && echo OK || echo FAIL
```

- [ ] **Step 6: Commit**

```bash
git add README.md CHANGELOG.md .claude-plugin/plugin.json .claude-plugin/marketplace.json skills/using-engineering-workflow/SKILL.md
git commit -m "docs(release): scenario-protocol integration; bump plugin to 1.6.0"
```

---

## Self-Review

1. **Spec coverage:** §4 schema → Task 1 (verbatim, all 4+1 hard rules present); §5 discipline 1–5 → Task 1 Discipline section (sign-off/held-out/tier/exit-codes/loop); §6 integration table → Task 3 (all 5 files); §7 test strategy → Task 2 (authoring + rejection, blind, controller-run); §8 decisions → embedded (conservative-wins in Tier mounting + Adoption). ✅
2. **Placeholder scan:** none — contract text, eval prompts, planted violations, and all commands are concrete. ✅
3. **Consistency:** hard rules identical between spec §4 and contract text (5 rules incl. protocol version); exit codes 0/1/2 match spec §5.4-5; `learnings-protocol.md` style conventions honored (versioned header, Failure Modes, normative MUST). ✅

## Execution Handoff

T2 work-item → plan-review before execution (standard complexity: feasibility + scope-guardian). After APPROVE: execute inline (3 small tasks, Task 2 controller-run by necessity; dispatching implementers to paste verbatim content is scaffolding without a correctness gain).
