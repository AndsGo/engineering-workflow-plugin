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
