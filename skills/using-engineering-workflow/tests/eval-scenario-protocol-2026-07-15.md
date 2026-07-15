# Scenario Protocol v0.1 — Blind Teachability Eval

**Date:** 2026-07-15
**Artifact:** `references/scenario-protocol.md` (protocol v0.1)
**Method:** blind — fresh Sonnet subagents, contract text pasted inline, NO repo tools, no expected answers in context. Controller graded mechanically against the 5 hard rules. Mirrors the protocol validated in `eval-2026-07-04.md` and `docs/learnings/2026-07-06-blind-eval-not-self-graded.md`.

## 1. Authoring check (×2 runs)

Input: contract + toy notes API (`POST /api/v1/notes` → 201 `{id,text}`, auth required; `GET /api/v1/notes/{id}` → 200/404). Required: valid scenario file, ≥2 scenarios incl. one 404 case.

| Run | Scenarios | R1 then-mechanical | R2 single-when | R3 given-prose | R4 no-literal-secrets | R5 protocol | 404 case | Verdict |
|---|---|---|---|---|---|---|---|---|
| A1 | 3 | ✅ (status/header/jsonpath; equals/exists/contains) | ✅ | ✅ | ✅ (`${ADMIN_TOKEN}`) | ✅ | ✅ | **PASS** |
| A2 | 3 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **PASS** |

Notable: both authors independently converged on the same valid idioms — `${FIXTURE_NOTE_ID}` env-binding for a known fixture, all-zero UUID for the 404 probe, business-language `title`/`given` in Chinese. Strong teachability signal; no rule was misread in either run.

## 2. Rejection check (×2 runs)

Input: contract + planted-violation file (verbatim in `docs/plans/2026-07-15-scenario-protocol-v01.md` Task 2) with exactly 3 violations: rule 1 (fuzzy `looks: friendly`), rule 2 (two requests under `when`), rule 4 (literal `sk-live-abc123`).

| Run | Rule 1 caught | Rule 2 caught | Rule 4 caught | False positives | Total reported | Verdict |
|---|---|---|---|---|---|---|
| R1 | ✅ exact location | ✅ exact location | ✅ exact location | 0 | 3 | **PASS** |
| R2 | ✅ | ✅ | ✅ | 0 | 3 | **PASS** |

Both runs also correctly prescribed the fix for rule 2 (`setup` + single trigger, or split scenarios) — the remedy is in the contract and was retrieved, not invented.

## 3. Blindness evidence

Each subagent prompt contained ONLY: the contract text (pasted inline) + the task input (API description / file under review) + "Do NOT read any files or use any tools — work purely from this prompt." No expected answers, no plan/spec access, no repo tools were used (0 tool calls in all 4 runs).

## 4. Known Gaps (accepted v0.1 looseness)

Operator vocabulary inside assertion types (`equals` / `exists` / `contains`) is exemplified, not normatively enumerated. Both blind authors stayed within the exemplified set, so the gap did not bite in this eval — but an engine author reading the contract alone cannot derive a closed operator set. Per spec §7.3, this is sealed by Stage A pilot findings (bump to v0.2), not by speculating ahead of the engine's actual capabilities.

## 5. Verdict

4/4 runs pass (2 authoring valid, 2 rejection 3/3 with zero false positives).

EVAL VERDICT: PASS
