# Architecture

This document explains **why** the plugin is built the way it is. For installation, see README.md. For contributing, see CONTRIBUTING.md.

## Core Idea

Engineering Workflow is a **pure-Markdown plugin** that turns Claude Code into a process-aware engineering assistant. No compiled binaries, no runtime servers, no dependencies beyond Superpowers — just skills (Markdown instructions) and hooks (Shell scripts).

The key insight: **LLMs follow structured prose instructions reliably when the instructions are injected at the right time, in the right format, with anti-rationalization guards.** This plugin exploits three injection points in Claude Code's architecture:

```
SessionStart hook     → Flow rules injected BEFORE first user message
PreToolUse hook       → Gate checks injected BEFORE git commit/push
SKILL.md load         → Detailed workflow injected WHEN skill is invoked
```

## Three-Layer Architecture

```
┌─────────────────────────────────────────────┐
│ This Plugin: Process & Tools                 │
│ (12 process skills + 1 meta)                 │
│ structured-review, ship-and-pr, security-    │
│ audit, knowledge-compound, plan-review-      │
│ personas, grill-me, engineering-retro,       │
│ e2e-browser-test, resolve-pr-feedback,       │
│ document-sync, learnings-refresh,            │
│ loop-verify + using-engineering-workflow     │
├─────────────────────────────────────────────┤
│ Superpowers: Discipline (required)           │
│ TDD, systematic-debugging, verification-     │
│ before-completion, brainstorming, writing-   │
│ plans, subagent-driven-dev                   │
├─────────────────────────────────────────────┤
│ Claude Code: Runtime                         │
│ Skills, Hooks, Agents, Tools, Context        │
└─────────────────────────────────────────────┘
```

**Why depend on Superpowers?** Superpowers provides the discipline layer — TDD iron laws, systematic debugging, verification before completion. Reimplementing these would be duplication. Our plugin adds the process layer (what order to do things) and the tool layer (how to review, audit, ship). The two layers are complementary, not overlapping.

## Enforcement Model

Skills are prose instructions. The agent can choose to follow or ignore them. We use a graduated enforcement model:

| Level | Mechanism | Reliability | Used for |
|-------|-----------|-------------|----------|
| **Hook injection** | SessionStart / PreToolUse shell scripts | ~95-100% | Flow gates, dependency checks |
| **Context priority** | CLAUDE.md routing rules | ~90% | Skill selection |
| **Skill Iron Laws** | "NO X WITHOUT Y" patterns in SKILL.md | ~70-80% | Step enforcement within a skill |
| **Red Flags tables** | Anti-rationalization lists in SKILL.md | ~60% | Preventing skip behavior |

**Why not 100% hard enforcement?** Claude Code hooks can block tool calls (`exit 1`), but hard-blocking creates friction that makes the plugin unusable. The current `pre-commit-gate` hook uses advisory warnings (`exit 0` with context injection), not hard blocks. This can be upgraded to hard enforcement per-project by changing `exit 0` to `exit 1` in the hook script.

## Meta Skill: using-engineering-workflow

The meta skill is the plugin's "brain". It defines:

1. **Skill routing table** — maps user intent to the correct skill
2. **5 Flow Gates** — enforces ordering (plan→review→execute→review→ship)
3. **Anti-Skip table** — counters common rationalizations for skipping steps
4. **Knowledge Loop rules** — every skill reads prior knowledge and offers to write new
5. **RETHINK limit** — caps plan-review loops at 2 rounds

The meta skill is injected into EVERY conversation via the SessionStart hook, regardless of which skill the user invokes. This ensures the flow rules are always in the agent's context.

## Skill Design Patterns

### Pattern 1: Prior Knowledge Lookup → Analysis → Knowledge Output

Every analysis skill follows the same three-phase knowledge pattern:

```
Phase 1: Read docs/learnings/INDEX.md (if present) → 📚 synthesis docs → targeted learnings; fall back to grep when INDEX absent. Per `learnings-protocol.md` READ phase.
Phase 2: Do the actual work (review, audit, test, etc.)
Phase 3: Offer to write new learnings via knowledge-compound
```

This creates a feedback loop: knowledge accumulates over time, and each skill benefits from prior knowledge.

### Pattern 2: Parallel Reviewer Dispatch

`structured-review` and `plan-review-personas` dispatch multiple independent reviewer agents in parallel, then merge their findings:

```
Main agent → Spawn reviewer agents in parallel
          → Collect structured findings
          → Deduplicate and merge
          → Apply confidence gates
          → Present unified report
```

Each reviewer has its own prompt file (`reviewers/*.md`) with specific focus, confidence calibration, and output format.

### Pattern 3: Iron Law + Red Flags

Every skill that enforces discipline uses two complementary mechanisms:

- **Iron Law**: A one-line absolute rule (`NO MERGE WITHOUT STRUCTURED REVIEW`)
- **Red Flags table**: A list of thoughts that indicate the agent is rationalizing a skip

The Iron Law provides the rule. The Red Flags table provides pattern-matching against the agent's internal reasoning. Together they create a "pre-compiled chain-of-thought guardrail."

## Hook Architecture

### Cross-Platform Execution: run-hook.cmd

All hooks are invoked through `hooks/run-hook.cmd`, a **polyglot file** that works as both a Windows CMD script and a Unix bash script:

```
hooks.json → run-hook.cmd → session-start / pre-commit-gate
```

- **Windows (CMD):** CMD interprets the batch portion, locates Git Bash (`C:\Program Files\Git\bin\bash.exe` or PATH), and delegates to the bash script
- **Unix (bash):** bash sees `:` as a no-op, skips the batch block via heredoc, and runs the script directly with `exec bash`

This pattern (borrowed from [Superpowers](https://github.com/obra/superpowers)) ensures hooks work on Windows 11, Linux, and macOS without platform detection in `hooks.json`.

### SessionStart Hook

```
session-start
├── Check Superpowers dependency (3-level detection)
│   ├── Marketplace cache scan
│   ├── Manual install path check
│   └── Settings.json keyword search
├── Read using-engineering-workflow/SKILL.md
├── Check workflow state (.context/ artifacts)
├── Count learnings (docs/learnings/)
├── Signal LEARNINGS_SIGNAL when count crosses LEARNINGS_THRESHOLD_INDEX (30) or LEARNINGS_THRESHOLD_REFRESH (50)
├── Check optional tools (agent-browser, gh)
└── Inject everything as session context
```

**Platform detection**: The hook outputs different JSON formats for Claude Code (`hookSpecificOutput`), Cursor (`additional_context`), and Copilot CLI (`additionalContext`).

### PreToolUse Hook

```
pre-commit-gate
├── Check if in git repo
├── Check branch (warn if on main/master)
├── Check for review artifacts (.context/engineering-workflow/)
├── Check for test script in package.json
└── Output advisory warnings (never block)
```

**Design choice: advisory, not blocking.** The hook warns but does not prevent `git commit`. Hard blocking would break legitimate workflows (e.g., WIP commits, fixup commits). Per-project escalation to hard blocking is a one-line change.

## Knowledge Storage

```
docs/learnings/                    # Project knowledge (committed to repo)
├── INDEX.md                       # Routing layer — Domain & Track grouping; auto-regenerated by learnings-refresh
├── 2026-MM-DD-<topic>.md          # Individual learnings; frontmatter optional pre-v1.1, required for new docs post-v1.1 (track + status)
└── archive/                       # Superseded/archived learnings (excluded from INDEX)

.context/engineering-workflow/     # Ephemeral workflow state (gitignored)
├── review-*.json                  # Review run artifacts
└── plan-review-*.json             # Plan review artifacts
```

### Learnings Lifecycle

The plugin treats `docs/learnings/` as a managed artifact with three phases, all defined in `skills/using-engineering-workflow/references/learnings-protocol.md`:

1. **READ** — every analysis skill consults INDEX-first → synthesis docs → individual learnings → grep fallback. Sources are cited in skill output.
2. **WRITE** — `knowledge-compound` is the sole writer. Required frontmatter: `track`, `status`. Optional: `category`, `last-verified`, `superseded-by`. Existing learnings without frontmatter remain valid.
3. **MAINTAIN** — implemented by the user-invoked `/learnings-refresh` skill. Suggested monthly, or when the session-start hook signals a threshold crossing. Detection scripts are read-only; user confirms each curation action.

The protocol is versioned (current version in its file header). Every learning-touching skill cites it explicitly (the authoritative list is the protocol's own Skill Participation Reference table); per-skill semantic filtering (e.g., security-audit's category list) layers on top.

**Why two locations?** `docs/learnings/` is durable knowledge shared with the team. `.context/` is session-specific state that gates enforce (e.g., "has a review been run?").

## What's Intentionally Not Here

- **No compiled binaries.** Pure Markdown + Shell. No build step, no `node_modules`.
- **No runtime server.** Unlike gstack's browse daemon, we delegate browser automation to `agent-browser` CLI.
- **No cross-platform converter.** Unlike compound-engineering's CLI, we're Claude Code-native. Cursor support comes from Claude Code's plugin format compatibility.
- **No telemetry.** No usage tracking, no analytics, no phone home.
- **No auto-update.** `git pull && ./setup --global` is the update mechanism.
