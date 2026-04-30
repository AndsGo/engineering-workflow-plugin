---
name: learnings-refresh
description: "Use monthly, at project milestones, or when LEARNINGS_COUNT exceeds threshold (30+). Audits docs/learnings/ for staleness, missing INDEX, duplicate themes (≥3 same-category), and orphaned references to deleted code paths. Produces a per-learning recommendation table for user-confirmed keep/update/replace/archive/synthesize actions. Triggers on: 'refresh learnings', 'review compound knowledge', 'audit our learnings', 'curate learnings'."
---

# Learnings Refresh

Implements the **MAINTAIN phase** of `skills/using-engineering-workflow/references/learnings-protocol.md`.

## Invocation

Scripts require Python 3.7+. Use:
- **Unix:** `python3 scripts/<name>.py --root <project>`
- **Windows:** `py -3 scripts\<name>.py --root <project>` (the bare `python` may be a Store stub or 3.6 — prefer `py` launcher)

## When to Use

- Monthly cadence (first business day)
- When `LEARNINGS_SIGNAL` appears in session-start state info (count ≥ 30 without INDEX, or ≥ 50)
- When user says "refresh learnings", "audit our learnings", "review compound knowledge"
- After `engineering-retro` flags recurring patterns (≥3 same area)

## Workflow

### Step 1 — Detect

Run all three detection scripts in parallel against the project root:

```bash
python3 scripts/parse_learnings.py --root <project> > /tmp/lr-parse.json
python3 scripts/detect_stale.py --root <project> > /tmp/lr-stale.json
python3 scripts/cluster_by_category.py --root <project> > /tmp/lr-cluster.json
```

Collect outputs (each is JSON to stdout).

### Step 2 — Build the Recommendation Table

For each learning emitted by `parse_learnings.py`, build one row:

| Path | Track | Status | Category | Signals | Recommended Action |
|---|---|---|---|---|---|
| `2026-04-09-x.md` | knowledge | active | (none) | none | keep |
| `2025-01-01-y.md` | knowledge | active | pattern | ref-missing | candidate archive |
| ... | | | | | |

Apply defaults from `references/decision-rules.md`. Group rows where recommendation matches.

### Step 3 — Present to User

Show the table sorted: non-keep rows first (need attention), then keep rows.

If `cluster_by_category.py` returned ≥1 cluster, list each cluster after the table:

> Cluster: 4 learnings in category `pattern` — synthesize? (y/n/skip)
> - 2026-04-14-a.md
> - 2026-04-14-b.md
> - 2026-04-29-c.md
> - 2026-04-29-d.md

### Step 4 — Per-Cluster Synthesis Decision

For each ≥3 cluster, ask user: **synthesize? (y/n/skip)**.

On `y`:
- Read `references/synthesis-template.md`
- Draft a synthesis doc filling Face sections from each member's body
- Show draft to user; iterate until approved
- Write the synthesis doc
- Add backlink to it from each member learning's `Related:` section (user confirms each)

On `n` or `skip`: continue to Step 5.

### Step 5 — Per-Row Action Confirmation

For each non-keep row, show the row + recommended action. Ask: **(k)eep / (u)pdate / (r)eplace / (a)rchive / (s)kip?**

- **(u)pdate:** ask what to update; bump `last-verified` to today
- **(r)eplace:** prompt user to write new doc; mark old as `status: superseded`
- **(a)rchive:** confirm; `git mv` to `archive/`; set `status: archived`
- **(s)kip:** leave as-is (no mutation)

### Step 6 — Apply Actions

Execute confirmed actions (in order):

- **Archive:** `git mv <path> docs/learnings/archive/<basename>`. Edit frontmatter `status: archived`.
- **Update:** open file, apply user's intent, set `last-verified` to today.
- **Replace:** write new doc; old doc gets `status: superseded` + `superseded-by: <new-relative-path>`.
- **Synthesize:** done in Step 4.

### Step 7 — Regenerate INDEX

```bash
python3 scripts/generate_index.py --root <project> --dry-run
```

Show the diff. If user approves:

```bash
python3 scripts/generate_index.py --root <project>
```

The script preserves headings in the allowlist (`## How to Use This Index`, `## Refresh Cycle`, `## Notes for Future Refreshes`) and **refuses to write** if it would drop a non-empty section outside that allowlist. If you see the refusal error, either:
1. Add the heading to `PRESERVED_HEADINGS` in `generate_index.py`, OR
2. Remove the section from `INDEX.md` (preserve content elsewhere first)

### Step 8 — Suggest Commit

Print suggested commit message:

```
docs(learnings): refresh — N archived, M synthesized, K updated; INDEX regenerated
```

**Do NOT auto-commit.** The user commits.

## Failure Modes (do not do)

- ❌ Auto-mutate any file without explicit user confirmation per row
- ❌ Archive Decision-track learnings (they supersede; never archive)
- ❌ Drop user-authored INDEX sections (the script's B3 guard catches this — never bypass)
- ❌ Force-categorize learnings (uncategorized is fine; refresh prompts but doesn't require)
- ❌ Run when `docs/learnings/` is empty (exit cleanly with "no learnings found")

## Empty / No-Op Cases

- Empty `docs/learnings/`: print "No learnings found at <path>"; exit cleanly.
- All learnings keep: print "All N learnings keep — INDEX still in sync? (y/n regenerate)"; exit.

## Decision Rules

See `references/decision-rules.md` for the full signal → action heuristics.

## Synthesis Template

See `references/synthesis-template.md` for the umbrella-doc template + backlink convention.
