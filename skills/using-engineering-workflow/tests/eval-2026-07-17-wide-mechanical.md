# Rule 0 Blind Eval — 2026-07-17 (v1.10 wide-mechanical recalibration)

**What changed:** the surface-area signal (`>~5 files → T2`) was replaced by nature-based signals (design divergence / ambiguity / verifiability / interaction breadth); same-pattern many-file work is now **wide-mechanical T1** with announced breadth; E-2 retargeted to the announcement (absolute >~5 kept for unannounced work). This is a semantic change to a judgment artifact → full blind re-run per protocol (`README.md` in this directory), including regression on the original v1.4 suite.

**Setup:** 8 scenarios (S1–S6 original held-out suite + S7/S8 new-boundary, both drawn from this repo's real 2026-07-17 history) × 5 fresh Sonnet classifiers = 40 runs. Each classifier received ONLY the shipped Rule 0 section (single-file read, no other repo access) + one scenario inline. Expected tiers withheld; this key was recorded after the runs.

## Controller key & results

| Scenario | Expected (key) | Runs | Result |
|---|---|---|---|
| S1 version bump | T0 | 5 | 5/5 T0 |
| S2 single-file bash fix | T1 | 5 | 5/5 T1 (runtime-logic ≥T1 cited) |
| S3 document-sync v2 | T2 | 5 | 5/5 T2 (design + oracle signals, size not needed) |
| S4 learnings-refresh subsystem | T2 | 5 | 5/5 T2 (oracle-must-be-designed) |
| S5 off-by-one w/ pytest | T1 | 5 | 5/5 T1 |
| S6 auth expiry change | ≥T2 via E-1 + security-audit | 5 | 5/5 T2 with E-1 named |
| **S7 count-drift sweep (~8 files)** | **T1 wide-mechanical** | 5 | **5/5 T1**, wide-mechanical cited; breadth (~8 files) declared in 5/5 |
| **S8 spec-fidelity reviewer addition** | **T2** (design + oracle; moderate size must not cap it) | 5 | **5/5 T2** (design divergence + oracle-must-be-designed + interaction breadth cited) |

**Verdict: 40/40 stable — PASS.**

- **Regression:** original 6 scenarios classify identically to the v1.4 eval; removing the size signal did not leak S3/S4 down (their T2 rests on design/oracle signals) and did not disturb T0/T1/E-1 boundaries.
- **New boundary:** wide-mechanical work lands T1 in every run (previously size-forced to T2), and design-heavy moderate-size work stays T2 in every run — the boundary discriminates by nature, not size, as intended.
- **Calibration:** distribution T0×1 / T1×3 / T2×4 across the suite — neither ceremony-restoration (all-T2) nor unsafe flattening (all-T0/T1).
- **Variance note:** S7 signal lines varied in whether the `(wide-mechanical, ~8 files)` tag appeared in the Tier line or the signal line — cosmetic; tier and breadth declaration were present in all runs.
- **Known limitation (spec-fidelity review):** S7's scenario text ("same class per file; no runtime logic") partially echoes the rubric's discriminating vocabulary, softening its held-out property — the 5/5 may partly reflect vocabulary match. A future S7 variant should describe the task in task-level language only.
