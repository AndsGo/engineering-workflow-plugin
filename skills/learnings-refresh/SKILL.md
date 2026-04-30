---
name: learnings-refresh
description: "Use monthly, at project milestones, or when LEARNINGS_COUNT exceeds threshold (30+). Audits docs/learnings/ for staleness, missing INDEX, duplicate themes (≥3 same-category), and orphaned references to deleted code paths. Produces a per-learning recommendation table for user-confirmed keep/update/replace/archive/synthesize actions. Triggers on: 'refresh learnings', 'review compound knowledge', 'audit our learnings', 'curate learnings'."
---

# Learnings Refresh — Placeholder

Implements the **MAINTAIN phase** of `skills/using-engineering-workflow/references/learnings-protocol.md`.

Requires Python 3.7+. Invocation: `python3 scripts/<name>.py` (Unix) or `py -3 scripts\<name>.py` (Windows). On Windows the bare `python` may be a Store stub or 3.6 — prefer `py` launcher. Workflow detail filled in Phase 6.
