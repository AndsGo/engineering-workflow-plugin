# Engineering Workflow Plugin

Complete engineering workflow for Claude Code. Extends [Superpowers](https://github.com/obra/superpowers) with multi-role code review, knowledge accumulation, security audit, browser testing, PR feedback resolution, and document sync.

**10 process skills + 2 enforcement hooks + 1 meta skill. Zero runtime dependencies.**

## Quick Start

```bash
# 1. Install Superpowers first (required dependency)
/plugin install superpowers@claude-plugins-official

# 2. Add the engineering-workflow marketplace
/plugin marketplace add AndsGo/engineering-workflow-plugin

# 3. Install the plugin
/plugin install engineering-workflow@engineering-workflow-marketplace
```

Done. The plugin loads automatically in every new session.

## Install

### Option A: Via Plugin Marketplace (recommended)

The official Claude Code marketplace install method. Two commands in Claude Code:

```bash
# Step 1: Add the marketplace (one-time)
/plugin marketplace add AndsGo/engineering-workflow-plugin

# Step 2: Install the plugin
/plugin install engineering-workflow@engineering-workflow-marketplace
```

To update later:

```bash
/plugin marketplace update engineering-workflow-marketplace
```

### Option B: For a specific project (team sharing)

Add to your project's `.claude/settings.json` so teammates get it automatically:

```json
{
  "extraKnownMarketplaces": {
    "engineering-workflow-marketplace": {
      "source": {
        "source": "github",
        "repo": "AndsGo/engineering-workflow-plugin"
      }
    }
  },
  "enabledPlugins": {
    "engineering-workflow@engineering-workflow-marketplace": true
  }
}
```

Teammates who trust the project folder are prompted to install automatically.

### Option C: Clone + Setup (manual)

```bash
git clone https://github.com/AndsGo/engineering-workflow-plugin.git ~/.engineering-workflow
cd ~/.engineering-workflow && ./setup --global
```

This copies the plugin to `~/.claude/plugins/engineering-workflow/`.

### Option D: --plugin-dir (development/testing)

```bash
git clone https://github.com/AndsGo/engineering-workflow-plugin.git ~/engineering-workflow-plugin
claude --plugin-dir ~/engineering-workflow-plugin
```

Loads the plugin from source. Edits are reflected immediately.

### Option E: One-liner install prompt

Paste this into Claude Code and let it do the rest:

> Install engineering-workflow: run `/plugin marketplace add AndsGo/engineering-workflow-plugin` then `/plugin install engineering-workflow@engineering-workflow-marketplace`. If Superpowers is not installed, install it first with `/plugin install superpowers@claude-plugins-official`.

## Prerequisites

### Required

| Dependency | Why | Install |
|-----------|-----|---------|
| [Superpowers](https://github.com/obra/superpowers) | Discipline layer (TDD, debugging, verification) | `/plugin install superpowers@claude-plugins-official` |
| git | Used by most skills | Usually pre-installed |

**Superpowers is auto-detected.** If missing, the SessionStart hook displays installation instructions in every session until you install it.

### Optional

| Tool | Used by | Install |
|------|---------|---------|
| `agent-browser` | e2e-browser-test | `npm install -g agent-browser && agent-browser install` |
| `gh` CLI | resolve-pr-feedback, ship-and-pr | [cli.github.com](https://cli.github.com/) |

Optional tools are checked at session start. Missing tools produce a one-line note, not an error.

## What's Inside

### Skills (10)

| Skill | What it does | Triggered by |
|-------|-------------|-------------|
| **using-engineering-workflow** | Flow control rules (auto-injected) | Every session start |
| **structured-review** | Multi-role code review (4 reviewer agents) | "review code", before merge |
| **knowledge-compound** | Document learnings (Bug/Knowledge/Decision) | After tasks, debugging, session end |
| **plan-review-personas** | Stress-test plans (3 adversarial personas) | After writing plans, before execution |
| **ship-and-pr** | Pre-flight, commit, push, create PR | "ship it", "create PR" |
| **security-audit** | OWASP Top 10 + STRIDE threat model | Auth/input/API/secrets changes |
| **engineering-retro** | Git-based engineering retrospective | "retro", weekly review |
| **learnings-refresh** | Maintain docs/learnings/ — detect stale, cluster, regenerate INDEX | Monthly, threshold-triggered, "refresh learnings" |
| **e2e-browser-test** | Browser testing on diff-affected pages | "test the site", "e2e test" |
| **resolve-pr-feedback** | Batch-process PR review comments | "resolve PR comments" |
| **document-sync** | Sync docs to match shipped code | After shipping, "update docs" |

### Hooks (2) + Cross-Platform Wrapper

| Hook | When | What |
|------|------|------|
| **SessionStart** | Every conversation | Injects flow rules, checks Superpowers dependency, reports workflow state |
| **PreToolUse** | Before `git commit`/`git push` | Advisory warning if no review artifact found |
| **run-hook.cmd** | (wrapper) | Polyglot CMD+bash script for Windows/Linux/macOS compatibility |

## How It Works

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│ This Plugin: Process & Tools                             │
│ 10 skills + 2 hooks + flow gates                        │
│ Review → Ship → Document → Knowledge → Retro            │
├─────────────────────────────────────────────────────────┤
│ Superpowers: Discipline (required dependency)            │
│ TDD · Systematic Debugging · Verification · Anti-skip   │
├─────────────────────────────────────────────────────────┤
│ Claude Code: Runtime                                     │
│ Skills · Hooks · Agents · Tools                         │
└─────────────────────────────────────────────────────────┘
```

### The 5 Flow Gates

```
GATE 1: Plan → Plan Review       (non-trivial work must be reviewed)
GATE 2: Implementation → Review  (code must be reviewed before ship)
GATE 3: Review PASS → Ship       (BLOCK verdict = fix first)
GATE 4: Ship → Document Sync     (if docs affected by changes)
GATE 5: Session End → Knowledge   (always offer to capture learnings)
```

### Knowledge Loop

Every analysis skill reads `docs/learnings/INDEX.md` first (when present), prefers 📚 synthesis docs, then targets specific learnings. Falls back to `Grep docs/learnings/` when INDEX is absent. The complete read/write/maintain contract is in `skills/using-engineering-workflow/references/learnings-protocol.md`. (The MAINTAIN-phase implementation `learnings-refresh` is shipped — invoke via "refresh learnings".)

```
                    ┌─── knowledge-compound WRITES ───┐
                    ▼                                  │
              docs/learnings/                          │
                    │                                  │
    ┌───────────────┼───────────────┐                  │
    ▼               ▼               ▼                  │
structured    plan-review     security         engineering
-review       -personas       -audit           -retro
  READS         READS          READS             READS
    │               │               │                │
    └───────────────┴───────────────┘                │
                    │                                  │
                    └──── suggest compound ────────────┘
```

## The Workflow

```
Brainstorm → Plan → Review Plan → Execute (TDD) → Browser Test
                                                        │
                                                        ▼
                                    Code Review → Security Audit
                                                        │
                                                        ▼
                               Ship PR → Document Sync → PR Feedback
                                                        │
                                                        ▼
                                    Knowledge Compound ← Retro
```

## Process Auto-Scaling (v1.4)

`using-engineering-workflow` classifies each work-item into a tier and applies a matching amount of process — trivial changes skip ceremony, substantial ones get the full flow.

- **T0 Trivial** — version bump, typo, doc one-liner (no runtime logic change): just do it, silently.
- **T1 Standard** — bounded bugfix/feature: spec-lite + one test + one `structured-review`.
- **T2 Substantial** — multi-file / real design choices / oracle must be designed: full flow (brainstorming → writing-plans → plan-review-personas → subagent-driven-development → structured-review).

An **invariant floor** holds at every tier (define "correct" first; a check that can actually fail; evidence before "done"; never auto-execute irreversible/outward-facing actions; learnings discipline), plus a **completion-time checkpoint** that re-scans the actual diff before "done": a change that turns out to touch a security path (→ mandatory `security-audit`), grow past ~5 files (→ plan-review), or perform a surprise irreversible op (→ human approval) is caught and escalated even if it started trivial — and the checkpoint runs *before* any push/deploy. T1+ work announces its tier so you can veto a misclassification in one glance.

> **Migration (v1.4):** Routing now auto-scales by tier (T0–T2). By conservative-wins precedence, an unmigrated project keeps its current behavior — if your `CLAUDE.md` says "always review," that still wins. To opt into lighter handling of small changes, trim your duplicated always-full routing to a pointer at `using-engineering-workflow`. Security-touching changes always escalate (non-tunable). No config file required.

## Origin

This plugin extracts and fuses patterns from three open-source projects:

| Source | What we extracted |
|--------|------------------|
| [gstack](https://github.com/garrytan/gstack) (Garry Tan) | Review checklist, security audit (OWASP+STRIDE), ship workflow, document-release, retro, QA methodology |
| [compound-engineering](https://github.com/EveryInc/compound-engineering-plugin) (Every) | Reviewer personas, confidence calibration, knowledge accumulation, PR feedback resolution, plan review |
| [Superpowers](https://github.com/obra/superpowers) (Jesse Vincent) | Iron Laws, Red Flags tables, anti-rationalization patterns, Graphviz flow style |

All skills are independently written (not copied), combining the best patterns from each source into a unified workflow.

## Updating

```bash
cd ~/.engineering-workflow   # or wherever you cloned
git pull
./setup --global             # re-install with updates
```

## Uninstalling

```bash
cd ~/.engineering-workflow
./setup --uninstall
```

Or manually: `rm -rf ~/.claude/plugins/engineering-workflow`

## Contributing

1. Fork the repo
2. Create a branch for your changes
3. Follow `superpowers:writing-skills` for skill creation (TDD for docs)
4. Test with `claude --plugin-dir ./` to load from source
5. Submit a PR

## License

MIT
