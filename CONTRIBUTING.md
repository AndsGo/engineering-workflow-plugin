# Contributing

## Quick Start

```bash
git clone https://github.com/AndsGo/engineering-workflow-plugin.git
cd engineering-workflow-plugin

# Load the plugin from source for development
claude --plugin-dir .

# Test: start a conversation, the SessionStart hook should fire
# You should see "engineering-workflow plugin active" in the context
```

## Development Setup

**Prerequisites:**
- Claude Code installed
- Superpowers plugin installed
- Git

**No build step required.** Skills are Markdown, hooks are Shell. Edit and reload.

**To test changes:** Start a new Claude Code session with `--plugin-dir .` pointing to your checkout. Changes to SKILL.md files take effect on the next skill invocation. Changes to hooks take effect on the next session start.

## Directory Layout

```
engineering-workflow-plugin/
├── .claude-plugin/plugin.json      # Plugin metadata (name, version)
├── hooks/
│   ├── hooks.json                  # Hook registration (points to run-hook.cmd)
│   ├── run-hook.cmd                # Cross-platform polyglot wrapper (CMD + bash)
│   ├── session-start               # SessionStart: dependency check + flow injection
│   └── pre-commit-gate             # PreToolUse: commit/push advisory gate
├── skills/
│   ├── using-engineering-workflow/  # Meta skill: flow control rules + references/ (protocols, domain-glossary) + tests/
│   ├── structured-review/          # + reviewers/*.md + checklist.md
│   ├── knowledge-compound/         # + references/*.md
│   ├── plan-review-personas/       # + reviewers/*.md
│   ├── grill-me/
│   ├── ship-and-pr/
│   ├── security-audit/             # + references/*.md
│   ├── engineering-retro/          # user-invoked (/engineering-retro)
│   ├── learnings-refresh/          # user-invoked (/learnings-refresh); + scripts/*.py + tests/ + evals/
│   ├── loop-verify/
│   ├── e2e-browser-test/
│   ├── resolve-pr-feedback/
│   └── document-sync/
├── setup                           # Install script
├── CLAUDE.md                       # Maintenance sync invariants (auto-loaded in repo sessions)
├── docs/                           # skill-authoring.md, engineering-workflow-guide.md, learnings/, plans/, specs/
├── README.md                       # User-facing docs
├── ARCHITECTURE.md                 # Design decisions
├── CONTRIBUTING.md                 # This file
└── CHANGELOG.md                    # Release history
```

## Making Changes

### Modifying a skill

1. Edit the SKILL.md (or supporting files in the skill's directory)
2. Test with `claude --plugin-dir .`
3. Verify the skill triggers on the right conditions
4. Verify the flow gates still work (meta skill integration)

### Adding a new skill

1. Decide the invocation mode first (see Skill Writing Standards → Invocation)
2. Create `skills/<skill-name>/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: skill-name
   description: "Use when <triggering conditions>. Also use when <alternative triggers>."
   # user-invoked instead? add disable-model-invocation: true and make the
   # description a human-facing one-liner (no trigger phrasing)
   ---
   ```
3. Follow the established patterns: Iron Law, Process Flow (Graphviz), Red Flags table, Prior Knowledge Lookup, Knowledge Output, Integration with Superpowers
4. Sweep ALL sync surfaces per `CLAUDE.md` 同步不变量 (8 surfaces, version ×3 included — the canonical list lives there)
5. If your skill reads or writes `docs/learnings/`, follow `skills/using-engineering-workflow/references/learnings-protocol.md` (add yourself to its participation table) and cite it in your Step 0.

### Modifying hooks

1. Edit the hook script in `hooks/` (e.g., `session-start`, `pre-commit-gate`)
2. **Do not modify `run-hook.cmd`** unless you are fixing cross-platform execution — it is a polyglot wrapper that routes to the actual hook scripts
3. Test by starting a new Claude Code session
4. Verify JSON output format for all supported platforms (Claude Code, Cursor, Copilot CLI)
5. Test the Superpowers dependency detection with and without Superpowers installed
6. On Windows: verify hooks fire via `run-hook.cmd` → Git Bash path

## Skill Writing Standards

**Methodology** — predictability, leading words, information hierarchy, pruning/no-op hunting, failure modes, and the blind-eval requirement for judgment artifacts — lives in `docs/skill-authoring.md`. This section is the repo-mechanical checklist only.

### Invocation (decide FIRST — canonical criterion)

- **Model-invoked** (default): choose ONLY if the agent must reach the skill autonomously mid-flow, or another skill invokes it. Its `description` is model-facing and is loaded into every session (permanent context cost) — that cost must buy auto-triggering.
- **User-invoked**: everything else — deliberate, human-started rituals (currently: `engineering-retro`, `learnings-refresh`). Add `disable-model-invocation: true`; the model can only *suggest* `/skill-name`, never self-invoke.
- Flipping a skill's invocation is a behavior change: sweep every routing surface per the sync invariants in `CLAUDE.md`.

### Frontmatter Rules
- `name` and `description`; user-invoked skills additionally set `disable-model-invocation: true`. No other fields.
- Model-invoked: `description` starts with "Use when..." — triggering conditions only
- User-invoked: `description` is a human-facing one-liner (what it does, no trigger lists)
- **Never** summarize the workflow in the description (CSO rule)
- Max 500 characters for description

### Structure
- Iron Law (one-line absolute rule)
- Process Flow (Graphviz for non-obvious decisions)
- Prior Knowledge Lookup (search docs/learnings/ before analysis)
- Core workflow steps
- Knowledge Output (suggest knowledge-compound if findings are reusable)
- Red Flags table (anti-rationalization)
- Integration with Superpowers section

### Cross-References
- Reference other skills by name: `structured-review`, `superpowers:test-driven-development`
- Never use `@` links (burns context by force-loading)
- Use `**REQUIRED BACKGROUND:**` for hard dependencies

## Commit Style

```
feat: add new skill for <purpose>
fix: correct <specific issue> in <skill>
docs: update <file> to reflect <change>
refactor: restructure <component> for <reason>
```

One logical change per commit. If you modified a skill AND updated its documentation, that's one commit. If you modified two unrelated skills, that's two commits.

## Pull Request Checklist

- [ ] SKILL.md frontmatter complies with Skill Writing Standards → Frontmatter Rules (invocation mode decided; user-invoked skills set `disable-model-invocation: true`; model-invoked descriptions use "Use when...")
- [ ] No workflow summary in description (CSO rule)
- [ ] New skills added to meta skill routing table
- [ ] README.md updated if skills/hooks changed
- [ ] Tested with `claude --plugin-dir .`
- [ ] Hooks tested on session start (if modified)

## Questions?

Open an issue on GitHub. For design discussions, reference ARCHITECTURE.md to understand why things are built the way they are.
