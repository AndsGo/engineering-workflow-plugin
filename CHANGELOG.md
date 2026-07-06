# Changelog

All notable changes to this plugin are documented here. Written for users, not contributors.

## [1.5.0] - 2026-07-06

### Added
- **`grill-me` skill** — interactive, human-in-the-loop stress-testing of a plan/design/idea: it interviews you one question at a time, walking the decision tree with a recommended answer per question, and explores the codebase instead of asking when the answer is discoverable. Complements `plan-review-personas` (async adversarial agents) with a synchronous, live alternative. Adapted from Matt Pocock's `grill-me` (MIT). Triggers: "grill me", "质询我的计划", "拷问这个设计", "poke holes in this".

## [1.4.0] - 2026-07-04

### Added
- **Process auto-scaling** in `using-engineering-workflow`: a new Rule 0 Triage classifies each work-item T0–T2 and applies a matching subset of the workflow gates — trivial changes skip ceremony, substantial changes get the full flow.
- **Invariant floor** at every tier, including a **completion-time checkpoint** that re-scans the actual diff before "done" — so a change that turns out to touch a security path or grow in scope is caught and escalated even if it started trivial.
- **Non-tunable security escalation** (auth/secrets/input/API/crypto/… → mandatory security-audit) and a broken-oracle STOP.
- **Conservative-wins precedence:** existing projects keep their current behavior; auto-scaling's lightening is opt-in.
- Blind, held-out classification eval for Rule 0.

### Changed
- Flow Sequence Gates (Rule 2) and Anti-Skip Enforcement (Rule 3) are now **tier-conditional** rather than unconditional.

### Compatibility
- Backward-compatible by design: an unmigrated project's stricter rules win, so behavior does not silently loosen. No config file added.

## [1.3.0] - 2026-05-01

### Added

- `document-sync` skill: new `Step 4.7: CLAUDE.md Hygiene Audit` —
  size budget (1500/3000 token caps), 6 inflation patterns, removal-on-
  feature-removal proposal, date-stamp staleness flag. Two modes:
  Auto (default, bypassable) and forced full-sweep.
- Diff-driven section targeting (F1): the skill chooses CLAUDE.md
  audit checks based on what changed in the diff.
- Counted enumerations check (F2): detects `(N total)` or `N skills`
  mismatches against actual bullet count.
- Path/package reference validation (F3): backtick-quoted paths in
  CLAUDE.md must exist in the repo.
- 3 behavior-level fixtures under `skills/document-sync/tests/fixtures/`
  for empirical acceptance checks.

### Changed

- `document-sync` Step 5 prepended with bias-toward-replacement
  preamble: 3 hygiene questions before adding new content to CLAUDE.md.
- Auto-update vs ask gate is TIGHTER for CLAUDE.md: removal/deletion
  always asks; only mechanical replacements (count fix, clear rename
  from diff) stay auto.
- Hard rule: any operation that REMOVES content from CLAUDE.md MUST
  ask the user.

### Compatibility

- All other docs (README, ARCHITECTURE, CONTRIBUTING, etc.) audit
  behavior unchanged. Only the CLAUDE.md sub-section + new Step 4.7
  are touched.
- CHANGELOG preservation rule (Step 7) unchanged.
- Existing CLAUDE.mds may already exceed soft cap. First run on such
  projects warns + lists prune candidates; user opts in per row.
- Hygiene Audit defaults to bypass when diff doesn't touch CLAUDE.md
  AND file under soft cap; `--full-sweep` overrides for monthly
  reviews and pre-release checks.
- No new dependencies; pure prose change to one skill.

## [1.2.0] - 2026-04-30

### Added

- `learnings-refresh` skill — implements MAINTAIN phase of `learnings-protocol.md`.
  Detects stale learnings (ref-missing, orphaned), clusters ≥3 same-category for
  synthesis, regenerates INDEX.md. All actions user-confirmed.
- 4 Python scripts (stdlib-only, Python 3.7+): parse_learnings, detect_stale,
  cluster_by_category, generate_index.
- 5 self-contained eval fixtures + evals.json for skill-creator validation.
- 2 reference docs (decision-rules, synthesis-template).

### Changed

- `using-engineering-workflow` meta-skill: drops v1.2 forward-reference;
  cites `learnings-refresh` as the available MAINTAIN tool.
- README skill count: 9 → 10.
- ARCHITECTURE Learnings Lifecycle: v1.2 forward-references replaced with
  current-tense descriptions.
- engineering-workflow-guide: skill table + naming convention + FAQ updated.

### Compatibility

- INDEX.md regeneration is safe: refuses to overwrite if it would drop a
  non-empty section outside the preservation allowlist.
- Existing learnings without frontmatter remain valid.
- Skill is opt-in (triggered monthly or on threshold signal); no behavior
  change for projects that don't use it.
- Python 3.7+ required for the new skill (other plugin components remain
  bash + markdown).

## [1.1.0] - 2026-04-30

### Added

- `learnings-protocol.md` — formal versioned contract for read/write/maintain across all learning-touching skills. Cited by 1 meta-skill + 7 consumer skills + `document-sync` (9 files total).
- `knowledge-compound` now emits frontmatter (`track`, `status`; optional `category` / `last-verified` / `superseded-by`).
- Forward-reference to `learnings-refresh` skill (ships in v1.2 — implements MAINTAIN phase).

### Changed

- `engineering-retro`: explicit baseline mode for first-ever retro (no comparison language); per-contributor section omitted entirely under solo mode.
- session-start hook: signals when LEARNINGS_COUNT exceeds 30 (no INDEX) or 50 (refresh recommended). Both thresholds env-overridable. Signal JSON-escaped to prevent injection.
- All 7 learning-consuming skills + `document-sync` (and the meta-skill) cite `learnings-protocol.md` instead of duplicating prose.

### Compatibility

- Existing learnings without frontmatter continue to load (read-side defaults applied).
- Hook signals are additive (silent below threshold).
- No breaking changes to skill names, paths, or invocation.
- Skill count unchanged (9); v1.2 will add 10th skill (`learnings-refresh`).
- New env vars: `LEARNINGS_THRESHOLD_INDEX` (default 30) and `LEARNINGS_THRESHOLD_REFRESH` (default 50).

## [1.0.0] - 2026-04-03

First release. A complete engineering workflow plugin for Claude Code.

### What You Can Do Now

**Plan with confidence:**
- `/plan-review-personas` — stress-test your implementation plans through three adversarial personas (feasibility, scope guardian, adversarial) before committing to execution. Catches scope creep and infeasible approaches.

**Review code deeply:**
- `/structured-review` — four specialized reviewer agents (correctness, security, testing, maintainability) run in parallel, merge findings, and apply a fix-first heuristic. Two-pass severity model (CRITICAL then INFORMATIONAL) with confidence-gated output.

**Ship with discipline:**
- `/ship-and-pr` — pre-flight checks (branch, tests, conflicts), value-communicating commit messages, and PR descriptions that scale to change complexity. No more "update stuff" PRs.

**Audit security systematically:**
- `/security-audit` — phased audit combining OWASP Top 10 code scanning with STRIDE threat modeling. Confidence-gated findings with attack path tracing. Two modes: focused (diff only) and comprehensive (full codebase).

**Test in real browsers:**
- `/e2e-browser-test` — maps your diff to affected pages, opens them in a real browser via agent-browser CLI, and tests at three depth levels (Quick/Standard/Exhaustive). Screenshots as evidence.

**Handle PR feedback efficiently:**
- `/resolve-pr-feedback` — fetches all unresolved review threads, triages them (new/pending/handled), dispatches parallel agents to fix valid comments, commits, pushes, and replies to threads.

**Keep docs current automatically:**
- `/document-sync` — scans every .md file in your project, cross-references against the diff, auto-fixes factual drift, and asks before subjective changes. CHANGELOG entries are never overwritten.

**Accumulate knowledge that compounds:**
- `/knowledge-compound` — document solved problems as Bug, Knowledge, or Decision tracks. Every analysis skill reads prior learnings before starting and offers to write new ones after finishing. Knowledge compounds across sessions.

**Retro with data:**
- `/engineering-retro` — analyzes git history for quantitative metrics (commit volume, test ratio, bug rate, churn) and qualitative reflections. Compares against prior retros to track improvement.

### How Flow Enforcement Works

Two hooks enforce the engineering process:

- **SessionStart** — injects 5 flow gates and routing rules into every conversation. Also detects if Superpowers is installed and guides you through setup if not.
- **PreToolUse** — warns before `git commit`/`git push` if no review artifact is found in the current session.

### Prerequisites

- [Superpowers](https://github.com/obra/superpowers) plugin (auto-detected, installation guided if missing)
- Optional: `agent-browser` CLI for browser testing, `gh` CLI for PR feedback
