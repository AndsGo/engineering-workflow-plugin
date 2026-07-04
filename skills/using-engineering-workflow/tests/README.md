# using-engineering-workflow — Rule 0 Blind Eval

Rule 0 (plugin v1.4) is validated by a **blind, multi-run, held-out** eval, not
self-graded fixtures (a self-graded walkthrough is circular — it grades itself
with the answer key in hand).

Protocol (run by the controller, see `eval-2026-07-04.md`):
1. **Blind:** each scenario in `eval-scenarios.md` is handed to a FRESH subagent
   with only the scenario + shipped `SKILL.md`. The expected tier is withheld; the
   subagent is instructed NOT to read `tests/`, `docs/plans/`, or `docs/specs/`
   (the answer key + tier rationale live there), and ideally runs with the scenario
   + SKILL.md pasted inline and no repo file tools.
2. **Multi-run:** >=5 independent runs per scenario; a scenario passes only if the
   tier is stable across all runs (flapping => signals underspecified).
3. **Held-out:** scenarios are real git-history work-items, not authored to fit
   the rules.
4. **Calibration:** report the tier distribution — nearly-all-T2 is a failure
   (ceremony-restoration) as much as all-T0 is (unsafe).
5. **Live empirical:** one real task run end-to-end through Rule 0, controller-observed.

Ground truth is held by the controller and recorded in `eval-2026-07-04.md`
AFTER the blind runs — never shown to the classifying subagents.
