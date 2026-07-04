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
