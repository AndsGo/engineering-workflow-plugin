# Changelog

All notable changes to this plugin are documented here. Written for users, not contributors.

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
