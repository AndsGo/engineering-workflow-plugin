# structured-review — reviewer eval fixtures

Behavior-level fixtures for the reviewer prompts, following the blind protocol in `skills/using-engineering-workflow/tests/README.md`: a fresh agent gets ONLY the reviewer prompt + the fixture's SPEC/DIFF (and ORCHESTRATOR NOTE, if present) blocks — the `## Expected (key — withhold from the agent)` section must NOT be shown to it. **Paste the blocks inline into the agent prompt; never give the eval agent the fixture path, the tests/ directory, or repo file-read access** — the key lives one screen below the DIFF. Grade detection (did every planted item surface; did any non-item get flagged), not wording. Fixtures A–C are synthetic plants (detection smoke); entry 3 records the held-out real-history generalization check.

## spec-fidelity

| Fixture | Plants | Non-items (must NOT be flagged) |
|---|---|---|
| `fixtures/spec-fidelity-A.md` | 1 missing deliverable (README update), 1 unspecced substantive change (timeout 30→60) | the two implemented spec claims |
| `fixtures/spec-fidelity-B.md` | 1 contradiction of an explicit constraint (return shape vs "行为保持完全一致") | the spec'd version bump (consequential edit) |
| `fixtures/spec-fidelity-C.md` | 1 partial implementation (endpoint done, docs surface missing), 1 silent reinterpretation (ready-log written to file vs console, choice unsurfaced) | the descoped rate-limit claim (orchestrator note: latest agreed revision excludes it) |

### Eval record — 2026-07-17 entry 3 (held-out real-history case)

1 blind run against real history: commit `963a99f` (v1.8, 18 files, +310/−50) as the diff, its committed revision-marked plan as the spec; agent restricted to those two inputs; graded against a controller-prepared claim list (not planted answers). **PASS** — coverage (23 claims: 22 implemented, 1 partial) matched the controller list; the single finding (P3 advisory) is a genuine unsurfaced reinterpretation the controller had pre-identified (plan said ARCHITECTURE "(v1.0)→(v1.1)"; the diff shipped a version-agnostic header pointer — a review-driven improvement the plan never recorded; accepted and now surfaced); non-items honored (out-of-repo carve-out per Global Constraints, review-driven mechanical sweeps as consequential edits, ~-approximations within tolerance); zero hallucinated deviations; no `safe_auto`. Generalization beyond synthetic plants: confirmed.

### Eval record — 2026-07-17 entry 2 (shipped prompt, protocol floor)

15 blind runs (5 per fixture A/B/C, fresh Sonnet agents, all content pasted inline, no file access, shipped keys): **15/15 — every planted item detected in every run; zero false positives on non-items (spec'd version bump, descoped claim); zero `safe_auto` across all 45 findings-slots (the never-safe_auto rule holds in live runs).** Evaluated prompt pinned: prompt-sha256:41e32f6f99037b00. Observed variance, judged cosmetic (detection identical): coverage bookkeeping labels (the two-surface item counted as "partial" in 3 runs, "missing" with partial-substance evidence in 2) and claim-count granularity (3 vs 4 claims in fixture B). Pending: one held-out real-history spec+diff case (generalization check beyond synthetic plants).

### Eval record — 2026-07-17 entry 1 (v1.9.0, reviewer introduced; superseded — see entry 2)

4 blind runs (2 per fixture A/B, fresh Sonnet agents, key withheld): 4/4 against the *pre-tightening* keys — all planted items detected, zero false positives; coverage summaries accurate. Variance observed: autofix_class flapped safe_auto/gated_auto on a missing-doc finding → the "never safe_auto on the Spec axis" rule was added to the prompt **after** these runs. Under the shipped (tightened) keys this record grades ≤3/4 and covers neither the tightened rule nor fixture C — scope-limited to detection smoke at n=2/fixture, below the protocol's ≥5 floor.
