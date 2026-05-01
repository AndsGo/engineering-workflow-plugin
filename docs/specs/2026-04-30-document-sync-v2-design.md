# document-sync v2 — Sustainable Doc-Sync for Consumer Projects

**Status:** Draft → pending user review
**Date:** 2026-04-30
**Targets:** plugin v1.3 (document-sync skill upgrade only)
**Driver:** v1.2 review of `D:\work\enterprice_agent` revealed that document-sync is **freshness-only** and **single-direction (additive)**. For consumer projects whose CLAUDE.md is loaded into every Claude Code session, this leads to gradual token-budget bloat with no countervailing pressure. Concrete projection: enterprice_agent's CLAUDE.md (currently 89 lines / ~880 tokens) reaches 2000+ tokens within 1-2 release cycles given current drift patterns and current skill behavior.

## 1. Goal

Make document-sync sustainable for **long-lived consumer CLAUDE.md** by adding two missing capabilities:

1. **Stronger freshness checks** — close the high-value drift gaps identified in v1.2 review (counted lists, path references, diff-driven targeting).
2. **Active hygiene** — make the skill bidirectional (proposes prune + link-out + removal, not just additions), and enforce a soft size budget so CLAUDE.md doesn't accrete forever.

After v1.3, document-sync should produce CLAUDE.md that stays accurate **and** stays small.

## 2. Out of Scope (and Why)

| Item | Why excluded |
|---|---|
| Auto-prune (mutate CLAUDE.md without user confirmation) | Pruning requires human judgment about what context Claude actually needs in-session vs what can be linked. Always ask. |
| Splitting document-sync into multiple skills (`claude-md-hygiene`, etc.) | One skill, one trigger, one PR-time integration point. Hygiene fits inline as a phase. |
| Changing CHANGELOG behavior | CHANGELOG preservation rule (Step 7) stays as-is — it is already correct. |
| Auto-generating link targets | When document-sync proposes link-out, it suggests the target path; user creates the linked file. Auto-creation is a separate concern. |
| Multi-tier CLAUDE.md scanning (workspace + project) | Scope to single-repo. Cross-repo CLAUDE.md handling is a v1.4+ topic; this spec keeps scope tight to the freshness/hygiene core. **Non-functional add:** if Step 4.7 detects an upstream CLAUDE.md (parent dir or `~/.claude/`), it REPORTS the path so the user knows it exists, but does NOT scan or modify it. |
| Backwards-incompatible CLAUDE.md format requirements | All projects' existing CLAUDE.mds remain valid input. v1.3 only changes the skill's audit behavior. |

## 3. Background — Why Now

### 3.1 CLAUDE.md is high-stakes (different from README)

Unlike README (a human reads it once), CLAUDE.md is loaded into every Claude Code session as system instructions. **Drift in CLAUDE.md changes Claude's actual behavior, not just documentation accuracy.** Token cost is paid every session, on every prompt.

### 3.2 Token math (concrete projection)

Current state for enterprice_agent (representative consumer project):

| Source | Tokens |
|---|---|
| `D:\work\enterprice_agent\CLAUDE.md` (89 lines) | ~880 |
| Workspace `CLAUDE.md` (50 lines) | ~450 |
| Plugin skill descriptions (auto-injected via SessionStart hook) | ~2500 |
| Per-skill SKILL.md when triggered | +200-1500 each |
| **Session-start system context baseline** | **~3800** |

Without hygiene pressure, CLAUDE.md grows linearly with releases. enterprice_agent's projected CLAUDE.md after 5 more phases / 2 years of normal velocity: **~200 lines / ~2000 tokens** for that file alone. Total session baseline approaches 5000 tokens before the user types anything.

### 3.3 Six inflation modes observed

Patterns observed in `D:\work\enterprice_agent\CLAUDE.md` and predicted to recur in any long-lived consumer:

| # | Pattern | enterprice_agent example | Why document-sync misses it today |
|---|---|---|---|
| I1 | Unbounded route/skill list growth | line 60-73: `Endpoints (14 total)` + 14 bullets | No count-vs-actual check, no length budget |
| I2 | Phase narrative accretion | line 81: `Phase 2.0 multi-agent mode...` (Phase 1 still earlier) | "Phase X" is just prose; skill doesn't recognize the pattern |
| I3 | Architectural detail sediment | line 79-85: `NewRequestOrchestrator(agentID, scope)`, session crash-safety, message-time annotation | Each detail correct in isolation; aggregate is bloat |
| I4 | Failed-experiment scar tissue | (latent — emerges on deprecations) | "Used to / previously / legacy" prose accumulates |
| I5 | Verbatim code blocks | line 45-53: JSON config example | Acceptable in moderation; balloons when schemas grow |
| I6 | Policy/rule accretion | "Don't commit X", "Always do Y" | Each rule reasonable; aggregate overwhelming |

### 3.4 What document-sync v1 covers (~50%)

Current Step 4 sub-section for CLAUDE.md is 3 bullets (~14 lines):
- Project structure section matches file tree?
- Listed commands accurate?
- Build/test instructions match package.json?

These cover I3 (partial) and the build-command angle. They miss I1, I2, I4, I5, I6 entirely. They are also **vague on HOW to verify** (no concrete grep/diff procedures).

## 4. Design

### 4.1 Freshness Improvements (3 items, ~55 lines SKILL.md addition)

**F1 — Diff-driven section targeting.** Instead of audit-everything, compute which CLAUDE.md sections are at risk based on what changed in the diff:

| Diff touches | Audit these CLAUDE.md sections |
|---|---|
| `api/`, route handlers, framework router files | Endpoint enumerations + counts |
| `Makefile`, `package.json`, `Cargo.toml`, `pyproject.toml` | Build/Test Commands sections |
| Top-level dir add/rename/delete | Project Structure paragraph |
| Public function signatures (compute via diff hunks) | Architecture paragraphs (grep for referenced symbols) |
| Config schema files (`*.json`/`*.yaml` in config/) | JSON/YAML code-block examples |

**F2 — Counted enumerations check.** Detect patterns like `(N total)`, `N skills`, `N endpoints` in CLAUDE.md headings/intro lines. Count actual bullets that follow. Flag count mismatches as auto-fix candidates.

**F3 — Path/package reference validation.** Extract every backtick-quoted path from CLAUDE.md (e.g., `agent/`, `cli/commands/main.go`). For each, verify it exists in the repo via `test -d` / `test -f`. Missing paths are factual drift; auto-fix is rename or remove (ask if uncertain).

### 4.2 Hygiene Additions (new Step 4.7, ~45 lines SKILL.md addition)

**Step 4.7: CLAUDE.md Hygiene Audit** — runs after Step 4 (per-file audit) and before Step 5 (auto-update apply). New responsibilities:

**H1 — Measure size at start.**
```bash
lines=$(wc -l < CLAUDE.md)
chars=$(wc -m < CLAUDE.md)

# Token estimate — chars / 4 for English/code-heavy text;
# chars / 2 for CJK-heavy (Chinese/Japanese/Korean dominate).
# Heuristic for picking divisor: if >30% of chars are non-ASCII, use 2.
non_ascii=$(LC_ALL=C grep -c '[^[:print:][:space:]]' CLAUDE.md || true)
# divisor = 2 if (non_ascii * 100 / chars) > 30, else 4
```

The numeric caps are **token estimates**, not line counts:

- Soft cap: **1500 estimated tokens** (~200 lines English / ~100 lines CJK)
- Hard cap: **3000 estimated tokens** (~400 lines English / ~200 lines CJK)

If over soft cap: warn + treat hygiene candidates as "ask user" (not skip).
If over hard cap: refuse to add ANY new content; only prune and replace are permitted in this run.

**H2 — Inflation pattern detection.** For each of I1-I6, detect candidates and propose action:

| Pattern | Detection rule | Proposed action (always ASK) |
|---|---|---|
| I1: Verbatim list >5 items inline | Count contiguous bullets after `(N total)` or numbered list | Move to dedicated doc (e.g., `docs/api.md`); leave 1-line summary + link |
| I2: Phase narrative with 2+ phases | Find `Phase X.0` patterns, count occurrences | Keep current phase; archive older to spec docs; leave version pointer |
| I3: Architectural-detail accretion (≥3 non-list paragraphs in one H2/H3 section) | Count `\n\n`-separated non-list paragraphs between consecutive H2/H3 boundaries | No automatic action; flag for human review |
| I4: Scar tissue prose | Grep `used to|previously|legacy|formerly|in v\d` | Ask "still load-bearing? or can be removed?" |
| I5: Code blocks >10 lines | `wc -l` between ``` markers | Move to schema/config file; leave reference path |
| I6: Bullet rule lists >10 items | Count `^-` bullets in same list | Ask user to consolidate or link to convention doc |

**H3 — Removal-on-feature-removal.** When the diff DELETES code (function, route, command, config field), document-sync proposes deleting the corresponding CLAUDE.md description. Currently the skill is **additive-only** — this is the gap.

**H4 — Date-stamp staleness flag.** Find paragraphs containing `(Month YYYY)` or similar date markers. If the marker is >6 months old AND the diff doesn't touch nearby code, ask: "still accurate? still relevant for current contributors?"

### 4.3 Behavioral default change

**Step 5 (Apply Auto-Updates)** gets a new pre-edit principle, prepended to the existing rules:

> **Before adding any new content to CLAUDE.md:**
> 1. Is there an existing section this belongs to? (Update inline, don't append a new section unless one is genuinely needed)
> 2. Is the new content actually needed in every Claude Code session? Or could it be linked from a separate doc?
> 3. Will this content be stale in 6 months? (If yes, link to a versioned doc instead of inlining)

This shifts the skill's bias from "patch facts as needed" to "patch facts cheaply, link out when in doubt."

### 4.4 Auto-update gate is TIGHTER for CLAUDE.md

Current Step 4 classification (Auto-update / Ask user / No change). For CLAUDE.md specifically, recalibrate:

| Old classification | New classification for CLAUDE.md |
|---|---|
| Auto-update: count corrections, path renames clearly inferred from diff, command renames clearly inferred from diff | **Same** (mechanical replacements stay auto) |
| Auto-update: missing-path removal | **Ask** (deletion is a prune; always confirm) |
| Auto-update: small table-row edits | **Ask** if the edit removes a row OR changes semantic meaning |
| Ask: section removal | **Same** |
| Ask: large rewrite | **Same** |
| (new) | **Ask:** removal-on-feature-removal (when diff deletes code, doc removal still asks) |
| (new) | **Ask:** any addition that grows file >5% of current size |
| (new) | **Ask:** any addition that pushes file over soft cap |

**Hard rule:** any operation that REMOVES content from CLAUDE.md MUST
ask the user. Pruning requires human judgment about what context Claude
actually needs in-session.

## 5. SKILL.md Changes — Detailed

The current `### CLAUDE.md / AGENTS.md` sub-section (lines 132-136, 14 lines) becomes ~50 lines. New `### Step 4.7: CLAUDE.md Hygiene Audit` H3 added between Step 4 and Step 5.

### 5.1 Replace `### CLAUDE.md / AGENTS.md` sub-section

```markdown
### CLAUDE.md / AGENTS.md (high-stakes — drives Claude Code session behavior)

**Why elevated:** unlike README which a human reads, CLAUDE.md is loaded
into every Claude Code session as system instructions. Drift here changes
Claude's actual behavior, not just documentation accuracy. Token cost is
paid every session, on every prompt.

**Diff-driven section targeting** — choose checks based on what changed:

| Diff touches | Audit these CLAUDE.md sections |
|---|---|
| `api/`, route handlers | Endpoint enumerations + counts |
| `Makefile`, `package.json`, `Cargo.toml`, `pyproject.toml` | Build/Test Commands |
| Top-level dir add/rename/delete | Project Structure paragraph |
| Public function signatures | Architecture paragraphs (grep referenced symbols) |
| Config schema files | JSON/YAML code-block examples |

**Counted enumerations** — find `(N total)` / `N skills` / `N endpoints`
patterns; count actual bullets that follow; flag count mismatches.

**Path/package references** — extract every backtick-quoted path
(`agent/`, `cli/commands/main.go`); verify each exists; flag missing.

**Endpoint route validation** — if HTTP routes enumerated, grep code for
route definitions; flag missing-from-doc or missing-from-code.

**Symbol references** — function/method names mentioned in prose
(e.g., `Foo.NewBar(...)`); grep code for definition; flag if absent or
signature differs.

**Auto-update vs ask gate is TIGHTER for CLAUDE.md** — pruning
ALWAYS asks; only mechanical replacements are auto:
- Auto-update: count-only corrections; rename clearly inferable from
  the diff (path or command renamed); table-row text fix that doesn't
  delete a row
- **Ask** (do not auto-update): missing-path removal, section deletion,
  list-item removal, link-out / move-to-doc, removal-on-feature-removal,
  any addition that grows file >5% or pushes over soft cap (1500 tokens)
```

### 5.2 New Step 4.7

```markdown
## Step 4.7: CLAUDE.md Hygiene Audit (size + inflation pressure)

**Why this step exists:** CLAUDE.md is loaded into every session. Each
line costs tokens forever, on every prompt. Drift goes both ways —
content can become stale (need update) AND content can become irrelevant
(need removal). Step 4 handles the first; this step handles the second.

**Modes:**
- **Auto (default):** runs only if the diff touches `CLAUDE.md` OR file
  size is over soft cap. Otherwise skipped silently to keep PR-time
  audits cheap.
- **Forced full sweep (`--full-sweep` flag, or skill invocation phrase
  "audit CLAUDE.md hygiene"):** runs all hygiene checks regardless of
  diff/size. Used for monthly hygiene reviews, release pre-flights, and
  empirical validation of this skill itself.

### Measure size

```bash
lines=$(wc -l < CLAUDE.md)
chars=$(wc -m < CLAUDE.md)
# Token estimate: chars/4 for English/code-heavy; chars/2 for CJK-heavy.
# If >30% of chars are non-ASCII, use chars/2.
```

Caps are **token estimates**, not line counts:
- Soft cap: 1500 tokens
- Hard cap: 3000 tokens

If over soft cap → warn user, treat all hygiene candidates as "ask".
If over hard cap → refuse to ADD content; only prune/replace permitted.

### Detect upstream CLAUDE.md (report-only, do NOT scan)

```bash
for dir in "$PWD/.." "$PWD/../.." "$HOME/.claude"; do
  [ -f "$dir/CLAUDE.md" ] && echo "Note: upstream CLAUDE.md at $dir/CLAUDE.md (not in v1.3 scope)"
done
```

If found, report the path so the user knows it exists, but DO NOT
scan or modify it. Cross-repo handling is a v1.4+ topic.

### Inflation pattern detection

For each pattern, detect candidates and propose action. Always ASK
before mutating — pruning requires human judgment about what context
Claude actually needs in-session.

| Pattern | Detection | Proposed action |
|---|---|---|
| Verbatim list >5 items inline | Bullets after `(N total)` or numbered list | Move to dedicated doc; leave summary + link |
| Phase narrative with 2+ phases | `Phase X.0` count >1 | Keep current phase; archive older to spec docs |
| Architectural detail accretion (≥3 non-list paragraphs in one H2/H3 section) | Count `\n\n`-separated non-list paragraphs between consecutive H2/H3 boundaries | Flag for human review |
| Scar tissue prose | grep `used to|previously|legacy|formerly|in v[0-9]` | Ask "still load-bearing?" |
| Code blocks >10 lines | Lines between ``` markers | Move to schema file; leave reference |
| Rule list >10 items | `^-` bullets in same list | Ask: consolidate or link to convention doc |

### Removal-on-feature-removal

When the diff DELETES a feature (function/route/command/config field),
also propose deleting its CLAUDE.md description. The current skill is
additive-only — this closes that gap.

### Date-stamp staleness

Find date markers in two **explicit** forms only:
- Parenthesized: `(Month YYYY)` — e.g., `(April 2026)`
- Inline: `as of YYYY-MM` — e.g., `as of 2025-09`

Do NOT match `since YYYY` (too broad — false-positives on license years,
compatibility statements, design history). Do NOT match generic dates
inside JSON examples or commit-message blocks.

If the date is >6 months old AND the diff doesn't touch nearby code in
the same section, ask: "still accurate? still relevant for current
contributors?"

### Output

```
## CLAUDE.md Hygiene Report
- Current size: <N> lines / ~<M> tokens (vs 1500 soft cap)
- Inflation candidates: <list with line refs + proposed action>
- Removal candidates (feature removed in diff): <list>
- Stale-date candidates: <list with date markers>
```

User decides per candidate. Approved actions apply in Step 5.
```

### 5.3 Modify Step 5 preamble

Prepend to Step 5 ("Apply Auto-Updates"):

```markdown
**Before adding new content to CLAUDE.md, check:**

1. Is there an existing section this belongs to? (Update inline,
   don't append new section unless genuinely needed)
2. Is the new content actually needed in every Claude Code session?
   Or could it be linked from a separate doc?
3. Will this content be stale in 6 months? (If yes, link to a
   versioned doc instead of inlining)

Bias toward replacing/linking-out, not appending.
```

## 6. Size Budget Specification (canonical)

```
SOFT CAP:  1500 tokens (~200 lines)
HARD CAP:  3000 tokens (~400 lines)

Inline-vs-link heuristics:
  - Lists ≤5 items:  inline OK
  - Lists 6-10 items: borderline — prefer link if items grow ≥1/release
  - Lists >10 items: MUST link out (audit reports this)

  - Code blocks ≤10 lines: inline OK
  - Code blocks 11-30 lines: borderline
  - Code blocks >30 lines: MUST link to source file

  - Phase narratives: keep CURRENT phase only; older phases linked
  - Scar-tissue prose: link to deprecation note in design docs

Inline-mandatory categories (cannot link out):
  - Skill routing decisions (Claude needs them in-context to act)
  - Coding style essentials (apply to every edit)
  - Build/test command essentials (apply to every change)
  - Critical "DO NOT" rules
```

## 7. Acceptance Criteria

| Check | Pass condition |
|---|---|
| F1 implemented | Skill text contains "Diff-driven section targeting" with at least 4 mapping rows |
| F2 implemented | Skill text mentions "Counted enumerations" check with detection logic |
| F3 implemented | Skill text mentions backtick-quoted path extraction + existence check |
| Step 4.7 exists | New H2 between current Step 4 and Step 5 titled "CLAUDE.md Hygiene Audit" |
| Soft/hard cap stated | Numeric thresholds present in skill body (1500, 3000 tokens) |
| All 6 inflation patterns covered | Detection rules for I1-I6 present in Step 4.7 table |
| Removal-on-removal mentioned | Skill explicitly says "When diff DELETES a feature, propose deletion" |
| Step 5 bias change | "Before adding new content to CLAUDE.md, check:" preamble present |
| Tighter gate for CLAUDE.md | "Ask: addition that pushes over soft cap" or equivalent rule |
| Empirical | Run upgraded document-sync against `D:\work\enterprice_agent` **in forced full-sweep mode** (Step 4.7 must NOT be bypassed despite small diff and under-soft-cap size); verify it flags ≥3 inflation candidates from §3.3 table |
| **Behavior — counted-list mismatch** | Construct a fixture CLAUDE.md saying `Endpoints (5 total):` followed by 4 bullets. Run skill. Output MUST contain a line ref to the count line + a suggested fix (either change "5" to "4" or add the missing bullet) |
| **Behavior — missing path** | Construct a fixture mentioning a non-existent path like `pkg/gone/deleted.go`. Run skill. Output MUST present this as an ASK (not auto-remove) — user confirms before any deletion |
| **Behavior — over-hard-cap rejection** | Construct a CLAUDE.md ≥3000 estimated tokens. Trigger an additive change scenario. Skill MUST reject the addition or convert it to ask/link-out; never silently append |

## 8. Migration / Compatibility

| Concern | Strategy |
|---|---|
| Existing CLAUDE.mds may already exceed soft cap | First run on such projects shows warning + lists trim candidates; user opts in to changes per row |
| Auto-update behavior changes for CLAUDE.md (tighter gate) | Strict superset of current behavior — never silently mutates more than v1; only mutates LESS |
| Other docs (README, ARCHITECTURE, etc.) | Behavior unchanged. Only the CLAUDE.md sub-section + new Step 4.7 are touched. |
| CHANGELOG preservation rule | Unchanged. Step 7 stays as-is. |
| Skills calling document-sync (`ship-and-pr` Step 7 suggestion) | Still works — same trigger surface |

## 9. Risks

| Risk | Mitigation |
|---|---|
| Token-budget thresholds (1500/3000) are arbitrary; some projects legitimately need more | Cap is a SOFT prompt, not enforced. Hard cap is a refusal signal that user can override per-run via "do it anyway". Caps are also revisitable in v1.4. |
| Inflation pattern detection produces false positives | Always ASK; never auto-prune. False positive = user says "skip"; cost = one prompt. |
| Hygiene step adds time to every document-sync run | Step 4.7 default mode is bypassable when diff doesn't touch CLAUDE.md AND file is under soft cap. `--full-sweep` mode (or "audit CLAUDE.md hygiene" trigger) overrides for monthly reviews and pre-release checks. |
| Date-stamp pattern matching produces noise | Restricted to two explicit forms (`(Month YYYY)` parenthesized; `as of YYYY-MM` inline). `since YYYY` deliberately excluded — too broad. |
| Removal-on-feature-removal might miss/misidentify deletions | Always ASK; user verifies before removing CLAUDE.md content. |
| Spec scope grows during implementation | Keep changes confined to `skills/document-sync/SKILL.md`. No new skills, no new files except possibly a `references/inflation-patterns.md` if the pattern table outgrows inline. |

## 10. Sequencing & Plan Structure

This spec maps to one implementation plan with the following phases:

```
Phase 1: F1 — Diff-driven section targeting (~20 line skill addition + verification)
Phase 2: F2 — Counted enumerations check (~10 lines)
Phase 3: F3 — Path reference validation (~15 lines)
Phase 4: New Step 4.7 — Hygiene Audit (~50 lines, includes auto/forced modes + upstream-CLAUDE.md report-only detection)
Phase 5: Step 5 preamble + tighter CLAUDE.md gate (~10 lines)
Phase 6: Empirical validation — manual run on `D:\work\enterprice_agent` CLAUDE.md in forced full-sweep mode; confirm ≥3 inflation candidates surfaced + run 3 behavior-level fixtures (counted-list mismatch / missing path / over-hard-cap) from §7
Phase 7: Docs sync (CHANGELOG v1.3.0 entry, README mention)
Phase 8: Tag v1.3.0
```

Total: ~100-120 lines of `skills/document-sync/SKILL.md` increment. No new files, no new dependencies.

Realistic effort: half day (similar to v1.1 Tier 1).

## 11. Test Strategy

- **Unit-style:** review the modified SKILL.md sections for completeness against acceptance criteria (deterministic).
- **Empirical:** run document-sync against `D:\work\enterprice_agent` (a real consumer CLAUDE.md) **in forced full-sweep mode** (`--full-sweep` or "audit CLAUDE.md hygiene" trigger). The default-mode bypass would skip this run because the file is under soft cap and the diff is empty — empirical validation must explicitly override that. Expected behavior:
  - Reports current size: 89 lines / ~880 estimated tokens (under soft cap; warns NO).
  - Surfaces inflation candidates from §3.3 table: at minimum I1 (14 endpoint list — recommend link-out to `docs/api.md`), I3 (architectural detail accretion lines 79-85 — recommend review), I5 (JSON config block — recommend link to schema).
  - No false positives on stable sections (Coding Style, Commit Guidelines).
  - **Note:** `D:\work\enterprice_agent` is an external dependency; this empirical check is marked as **manual verification** in Phase 6, not a CI-able unit test. A repo-internal fixture (~30 lines) is sufficient for the 3 behavior-level acceptance checks above.
- **Negative:** run on a tiny CLAUDE.md (~30 lines). Expected: passes hygiene audit cleanly with no candidates surfaced. No false signal.
