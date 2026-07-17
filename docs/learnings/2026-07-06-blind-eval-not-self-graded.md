---
track: knowledge
status: active
category: pitfall
last-verified: 2026-07-06
---
# Validate LLM-facing artifacts with a blind held-out eval, not self-graded fixtures

**Track:** Knowledge
**Date:** 2026-07-06
**Applies to:** general (validating prompts, skills, rubrics, classifiers — any LLM-facing instruction artifact)

## Context

You've written an LLM-facing artifact (a skill, a routing rubric, a classifier prompt) and want evidence it "works." The tempting move — author fixtures that state their own expected answer, then have the model classify and grade itself against them — feels like testing but is **circular**.

## Guidance

A self-authored, self-graded walkthrough proves almost nothing:
- the fixture embeds its own expected answer, and the **same agent** that wrote the rubric predicts its own output and grades it **with the answer key in hand**;
- it runs in **calm conditions**, exactly the conditions that mask the real failure (a pressured model under-classifying / cutting corners);
- unlike a code test, there's **no mechanical ground truth** — a judgment the author both sets and confirms can't catch a *wrong* judgment.

Do this instead:
1. **Blind:** hand each case to a *fresh* agent with only the artifact + the input; **withhold the expected answer**, and deny access to any file where the key lives (plan/spec/tests). Ideally paste the artifact inline with no repo tools.
2. **Multi-run (≥5):** classify each case several times; it passes only if **stable across all runs**. Flapping is a finding — the signals are underspecified — not noise to average away. (3 runs is too few: a 20–30% error rate — the dangerous band — clears a 3-run check too often.)
3. **Held-out:** draw cases from **real history**, not examples authored to fit the rules.
4. **Calibrate the distribution:** for a "do less when possible" artifact, everything landing in the heavy bucket is as much a failure as everything landing in the light one.
5. **One live run** of the real thing as independent behavioral evidence.

The payoff is a real loop: blind eval → catches a genuine gap → tighten the artifact → re-run → stable.

## When to Apply

- Before shipping any prompt/skill/rubric whose whole job is to make the model *decide* something (classify, route, gate, choose).
- Whenever you catch yourself writing a "verification" the authoring model performs on its own output.

## When NOT to Apply

- Pure deterministic code with a real test harness — use the harness; this is for judgment artifacts with no mechanical oracle.
- Throwaway/one-shot prompts where the cost of a blind eval exceeds the value.

## Examples

- Plugin v1.4 Rule 0 Triage: the initial plan proposed self-graded fixtures; plan-review flagged the circularity (a BLOCKER). The redesigned eval (`skills/using-engineering-workflow/tests/eval-2026-07-04.md`) used 6 held-out scenarios × 5 blind Sonnet runs, key withheld. It caught scenario S5 (a one-line bugfix) *flapping* T0/T1 — a real underspecification — which drove a rubric fix ("any runtime logic change is ≥T1"); the re-run was stable. Self-graded fixtures would have rubber-stamped it.

## Related

- [[2026-07-06-scaffolding-vs-invariant]] — "a check that can actually fail" is the invariant this operationalizes for LLM artifacts.
- [[2026-07-17-oracle-assertions-anchor-to-structure]] — the same theme on the mechanical-assertion side: a substring check satisfied by adjacent text is a check that cannot fail.
- `skills/using-engineering-workflow/tests/README.md` — the reusable blind-eval protocol.
