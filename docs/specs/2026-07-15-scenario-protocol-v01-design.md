# Scenario Protocol v0.1 — Business-Acceptance Scenarios as Machine-Checkable Contract

**Status:** Draft → pending user review
**Date:** 2026-07-15
**Targets:** plugin v1.6 (`references/scenario-protocol.md` + floor amendment + routing); consumed by the standalone `loop-engine` project (separate repo, separate spec)
**Driver:** The stack's verification chain never traces back to business intent. Every gate checks against the *previous translation* (code vs plan, code vs quality, code vs security) — nothing checks delivered behavior against what the business asked for. Business intent enters once (brainstorming) and then survives 3–4 lossy translations unverified. You can pass every existing gate and ship something businessly wrong. This spec defines the contract that closes that loop: **user-confirmed Given-When-Then scenarios with observable bindings**, written before implementation, mechanically verified against the *running system* by a loop engine.

> **Design provenance:** Co-designed in discussion 2026-07-14/15. User decisions: loop runs in-session first; HTTP/API sensor first (browser second); engine standalone + contract in plugin; two-stage pilot on enterprice_agent (Stage A: retrofit A4a config-reload to validate engine plumbing; Stage B: A4b restart spec-first to validate the discipline). Sensor: hurl + Python thin layer. Strength: conservative-wins (hard floor for projects that adopt the protocol; others unaffected).

## 1. Goal

Ship a **versioned contract document** (`skills/using-engineering-workflow/references/scenario-protocol.md`, protocol version 0.1) that defines:

1. **The scenario schema** — YAML, business-facing Given-When-Then with a machine-executable `when`/`then` and a mandatory observable binding.
2. **The discipline rules** — sign-off (user confirmation makes a scenario an oracle), held-out (anti-Goodhart), tier mounting (which work requires scenarios), and the broken-oracle gate (unbindable `then` = rejected at parse time).
3. **The division of labor** — what the session (loop driver), the engine (stateless verifier), and the contract (this document) each own.

The contract is the *interface*; the engine (separate repo) is the first consumer; the pilot is the acceptance test for both.

## 2. Out of Scope (and Why)

| Item | Why excluded |
|---|---|
| The loop-engine implementation | Separate repo, separate spec. This spec only fixes the interface it must consume. |
| LLM judge for fuzzy assertions ("error message is friendly") | v0.1 is mechanical-assert-only (status/header/JSONPath/retry-until). Deferred until a pilot scenario actually needs it — YAGNI, and it reopens the self-certification problem that needs its own design. |
| Browser/SSE sensors | Sensor #1 is HTTP/API (user decision). Browser is stage 2; SSE streaming assertions are out of hurl's vocabulary and out of pilot scope (admin endpoints only). |
| CI / production probe integration | Loop runs in-session first (user decision). The engine is stateless one-shot precisely so the same scenarios lift to CI later without contract change. |
| Retrofitting scenario requirements onto all projects / all tiers | Conservative-wins: the requirement binds only projects that adopt the protocol, and only T2-with-observable-surface work items. A markdown-only repo (like this plugin) has no HTTP surface — forcing scenarios there is ceremony. |
| Gherkin/Cucumber tooling | The structured format is justified exactly because the engine consumes it — but the consumer is hurl via compilation, not a Gherkin runtime. No step definitions, no glue code. |

## 3. Background — Design Rationale (from discussion)

- **Business correctness has no mechanical oracle.** The only ground truth is the business side's (user's) confirmation. So the protocol's core move is not automation — it is (a) moving user confirmation *before* implementation, and (b) leaving one thread (the scenario) that survives all translation layers and is verified against the running system at the end.
- **Ritual consumed by a machine is an interface, not ceremony.** Earlier we rejected BDD-as-ritual because nothing executed the format. The loop engine is the consumer that legitimizes a structured format. The format follows the sensor: v0.1 scenarios compile to hurl.
- **The floor gets mechanical teeth.** v1.4's known compromise was "enforcement is still prose." For adopted projects, floor #2 (check that can fail) becomes "user-confirmed scenarios with observable bindings," floor #3 (evidence) becomes engine-collected traces, floor #6 (completion checkpoint) becomes the loop's exit gate: not green → not done.
- **Anti-Goodhart is not optional.** An implementer who sees all scenarios will overfit to them. Held-out scenarios (hidden from the implementer, run by the controller at the end) reuse the blind-eval discipline validated in v1.4 (see `docs/learnings/2026-07-06-blind-eval-not-self-graded.md`).

## 4. The Scenario Schema (protocol v0.1)

One YAML file per feature: `scenarios/<feature>.yaml` (held-out variants in `scenarios/held-out/<feature>.yaml`).

```yaml
protocol: scenario/v0.1          # required; engine rejects unknown versions
feature: config-reload           # slug; ties scenarios to the work-item
base_url_env: LOOP_BASE_URL      # env var the engine reads for the target server
scenarios:
  - id: reload-happy-path        # unique within the file, kebab-case
    title: 配置重载成功后返回应用结果   # business language, user-facing
    given: server 正在运行且配置文件合法   # prose precondition (business language)
    setup:                       # optional: machine steps to establish `given`
      - request: { method: GET, path: /api/v1/health }
        expect: [ { status: 200 } ]
    when:                        # exactly one trigger request
      request:
        method: POST
        path: /api/v1/admin/config/reload
        headers: { Authorization: "Bearer ${ADMIN_TOKEN}" }   # ${ENV} interpolation
    then:                        # ≥1 mechanical assertions — the observable binding
      - status: 200
      - header: { name: Content-Type, contains: application/json }
      - jsonpath: { path: "$.applied", equals: true }
      - jsonpath: { path: "$.version", exists: true }
    retry:                       # optional: eventually-semantics (Stage B needs this)
      until_pass: true
      max_attempts: 30
      interval_ms: 1000
```

**Hard rules enforced at parse time (E-3 moved to spec time):**

1. `then` MUST be non-empty and every assertion MUST be one of the mechanical types (`status` / `header` / `jsonpath` / `body_contains`). A scenario whose expectation cannot be expressed in these observables does not belong in the file — it is a broken oracle for this sensor; either rewrite it observably or keep it out (human review path).
2. `when` MUST contain exactly one request. Multi-step business flows = `setup` steps + one trigger. (Keeps a scenario a single verdict; flows needing multi-trigger verdicts are multiple scenarios.)
3. `given` prose is mandatory even when `setup` is present — the business reader must understand the precondition without reading machine steps.
4. Secrets only via `${ENV}` interpolation — literal tokens in scenario files are rejected.

**Scenario boundary rule:** scenarios cover *business rules* (what the feature promises the caller), not technical edge cases (those stay in unit tests). Rough budget: 5–12 scenarios per feature; more is a smell of scenario-explosion.

## 5. Discipline Rules

1. **Sign-off.** The model drafts scenarios from the brainstorm/spec; **the user confirms each one** (edit/veto per scenario). Only confirmed scenarios are oracles. Confirmation is recorded in the feature's spec ("Scenarios confirmed by user on <date>"). Unconfirmed scenario files are advisory, not gating.
2. **Held-out (anti-Goodhart).** At sign-off, the user (or controller) designates ≥1 scenario as held-out → moved to `scenarios/held-out/`, which the implementer (subagent or session under implementation) MUST NOT read. The controller runs held-out scenarios only at completion. A held-out failure after main-suite green = overfitting signal → finding goes back with the *evidence*, not the scenario text.
3. **Tier mounting (conservative-wins).** For projects that have **adopted** this protocol (a line in their CLAUDE.md: "本项目已采纳 scenario-protocol"): any **T2 work-item with an HTTP-observable surface** MUST have confirmed scenarios before implementation begins, and "done" requires the engine's green verdict (main + held-out). T1: recommended, one scenario suffices. T0 / no observable surface: exempt. Non-adopted projects: unaffected (Rule 0.2 conservative-wins — this protocol only ever *adds* gates).
4. **Broken-oracle gate.** Engine parse-rejects any violation of §4's hard rules (empty/non-mechanical `then`, multi-request `when`, missing `given` prose, literal secrets, missing/unknown `protocol` version). Rejection is a spec-time STOP (Rule 0.4 E-3), not a runtime failure.
5. **Loop protocol (session-side, informative).** implement → `loop-verify run` → exit 1 (real red): route per-scenario finding `{id, evidence, diff}` to implementer, retry (cap 2 rounds; same scenario failing twice with different fixes → escalate human: scenario ambiguous or architecture can't satisfy it) → exit 2 (sensor/env failure): fix environment, do NOT count as an implementation round → exit 0 + held-out green: done. This section is informative in the contract (the session/skills own the loop); the exit-code semantics are normative for the engine.

## 6. Integration — File Changes (plugin v1.6)

| File | Change |
|---|---|
| `skills/using-engineering-workflow/references/scenario-protocol.md` | NEW — the versioned contract (schema §4 + rules §5, condensed; this spec is the rationale, the contract is the reference). |
| `skills/using-engineering-workflow/SKILL.md` | Floor #2 gains one sentence: for scenario-protocol-adopted projects, T2 feature work's "check that can fail" = confirmed scenarios + green engine verdict (pointer to the reference doc — keep Rule 0 lean). |
| `README.md` | Short "Scenario Protocol (v1.6)" subsection + adoption line example. |
| `CHANGELOG.md` | v1.6.0 entry. |
| `.claude-plugin/plugin.json` / `marketplace.json` | 1.5.0 → 1.6.0. |

No new skill in v1.6. The loop is driven by session discipline (Rule 0 floor + this contract); a dedicated `loop-verify` orchestration skill is a candidate only after the pilot shows what the orchestration actually needs (YAGNI).

## 7. Test Strategy

The contract is a doc — its oracle is **teachability + parseability**, checked blind (per `blind-eval-not-self-graded`):

1. **Blind authoring check:** a fresh subagent, given ONLY the contract doc + a toy endpoint description (no examples from this spec), must author a valid scenario file. Pass = output parses against §4's hard rules (checked mechanically once the engine exists; until then, checked against the rules by a second blind reviewer).
2. **Blind rejection check:** the same setup, given a deliberately broken scenario (empty `then`, literal secret, fuzzy assertion "response looks right"), must identify all three violations. Pass = all three named.
3. **Empirical (Stage A, after engine v0.1):** author the A4a config-reload scenario file against the real sealed contract; engine parses it and runs green against a live enterprice_agent. This is the contract's real acceptance and is tracked in the engine/pilot specs — v1.6 does not block on it, but the contract carries `protocol: scenario/v0.1` precisely so Stage A findings can bump it to v0.2 without breaking adopters.

## 8. Resolved Decisions

1. In-session loop first; CI later without contract change (stateless engine). ✅ user 2026-07-15
2. HTTP sensor first (hurl + Python thin layer); browser second. ✅ user 2026-07-15
3. Engine standalone repo; contract in plugin. ✅ user 2026-07-15
4. Two-stage pilot: A4a retrofit (plumbing) → A4b spec-first (discipline). ✅ user 2026-07-15
5. Strength: conservative-wins — hard floor only for adopted projects' T2-with-observable-surface work. ✅ user 2026-07-15 ("按推荐执行")
6. v0.1 mechanical asserts only; LLM judge deferred. ✅ (YAGNI, per design discussion)

## 9. Self-Consistency Note

By Rule 0 this work-item is **T2** (new contract, cross-repo interface, oracle must be designed) and was announced as such. The protocol it defines cannot gate itself (this plugin has no HTTP surface — exactly the §5.3 exemption), which is why its oracle is the blind teachability check (§7) rather than scenarios. The first project to adopt the protocol will be enterprice_agent, at Stage B.
