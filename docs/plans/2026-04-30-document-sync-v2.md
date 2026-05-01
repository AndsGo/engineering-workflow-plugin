# document-sync v2 (plugin v1.3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `document-sync` skill from freshness-only to freshness + hygiene, so consumer projects' CLAUDE.md stays accurate AND stays small.

**Architecture:** All v1.3 functional changes are confined to a single file: `skills/document-sync/SKILL.md`. Add diff-driven section targeting (F1), counted-enumeration check (F2), path-reference validation (F3), a new Step 4.7 Hygiene Audit, and a Step 5 preamble that biases toward replacement over append. Plus 3 small fixture CLAUDE.mds for behavior-level acceptance verification, a verification report, and the standard v1.3.0 release housekeeping (CHANGELOG, manifest version bump).

**Tech Stack:** Markdown (skill prose), bash (verification commands inside skill), no Python or new dependencies. Manual subagent-led verification for behavior tests (the skill is interpreted by Claude when triggered, not executable code).

**Spec:** `docs/specs/2026-04-30-document-sync-v2-design.md`

---

## File Structure

**Files to create**

| Path | Responsibility |
|---|---|
| `skills/document-sync/tests/fixtures/counted-list-mismatch/CLAUDE.md` | Fixture: `(N total)` count mismatches actual bullet count |
| `skills/document-sync/tests/fixtures/missing-path/CLAUDE.md` | Fixture: backtick-quoted path that doesn't exist |
| `skills/document-sync/tests/fixtures/over-hard-cap/CLAUDE.md` | Fixture: ≥3000 estimated tokens; trigger an additive scenario |
| `skills/document-sync/tests/fixtures/over-hard-cap/generate.sh` | Reproducible generator for the over-hard-cap fixture |
| `skills/document-sync/tests/fixtures/README.md` | Fixture overview: target check + expected behavior + invocation pattern |
| `skills/document-sync/tests/verification-2026-04-30.md` | Verification report from Phase 5 (subagent-produced + manual empirical appendix) |

**Files to modify**

| Path | Change | Phase |
|---|---|---|
| `skills/document-sync/SKILL.md` | Replace `### CLAUDE.md / AGENTS.md` sub-section (F1+F2+F3+gate) | 1 |
| `skills/document-sync/SKILL.md` | Insert new `## Step 4.7: CLAUDE.md Hygiene Audit` between Step 4 and Step 5 | 2 |
| `skills/document-sync/SKILL.md` | Prepend bias-toward-replacement preamble to Step 5 | 3 |
| `CHANGELOG.md` | New v1.3.0 entry above v1.2.0 | 7 |
| `README.md` | Update document-sync skill description if needed | 7 |
| `.claude-plugin/plugin.json` | Bump version `1.2.0` → `1.3.0`; touch description if needed | 7 |
| `.claude-plugin/marketplace.json` | Bump 2 version fields `1.2.0` → `1.3.0` | 7 |

No new Python, no new shell scripts, no manifest schema changes, no skill-tree restructuring.

---

## Universal Rule for Prose Edits

This plan is mostly prose edits to `skills/document-sync/SKILL.md`. **For every Edit, Read the target section first to capture exact bytes** (CRLF/LF/BOM/whitespace), then Edit with the live `old_string`. Do NOT copy `old_string` from this plan body verbatim — line endings may differ.

If Edit fails byte-match: re-Read, check whitespace/EOL drift, retry with freshly-captured `old_string`.

---

## Task Map

| # | Task | Phase |
|---|---|---|
| 1 | Replace `### CLAUDE.md / AGENTS.md` sub-section (F1+F2+F3 + tighter gate) | 1 |
| 2 | Insert new `## Step 4.7: CLAUDE.md Hygiene Audit` | 2 |
| 3 | Prepend bias-toward-replacement preamble to Step 5 | 3 |
| 4 | Create 3 behavior-test fixtures | 4 |
| 5 | Subagent verification on 3 fixtures (token-evidence gated) + inline gap-fix if FAIL + manual enterprice_agent empirical (controller, optional) | 5 |
| 6 | Docs sync + version bump (CHANGELOG / README / plugin.json / marketplace.json) | 6 |
| 7 | Final verify + commit + tag v1.3.0 | 7 |

**7 tasks across 7 phases.** Realistic estimate: half day.

**Round-1 plan-review fixes integrated:**
- R1: Phase 7 verdict grep → `^Verdict: PASS$` (single-line); subagent must emit that exact line
- R2: Each behavior check has literal token-evidence requirements (line refs, action verbs); subagent can't lazy-PASS
- R3: enterprice_agent walkthrough moved out of subagent dispatch; controller-level manual check (optional, non-blocking)
- R4: former Task 6 (gap-fix loop) folded into Phase 5 Step 2; verification-report Gaps Identified section requires structured `Old text:` / `New text:` blocks for mechanical Edit dispatch

---

## Phase 1 — Freshness Improvements (F1+F2+F3 + tighter CLAUDE.md gate)

### Task 1: Replace `### CLAUDE.md / AGENTS.md` sub-section in SKILL.md

**Files:**
- Modify: `skills/document-sync/SKILL.md` (replaces lines ~132-136 with ~40 lines)

- [ ] **Step 1: Read the current sub-section live to capture exact bytes**

```bash
grep -n "^### CLAUDE.md\|^### Other .md\|^## Step 5" skills/document-sync/SKILL.md
```

Note the line range. Then use the Read tool with offset around the captured start to get the live content, byte-exact.

- [ ] **Step 2: Edit — replace the sub-section**

Use the Edit tool with `old_string` = the live content captured in Step 1. The `new_string`:

```markdown
### CLAUDE.md / AGENTS.md (high-stakes — drives Claude Code session behavior)

**Why elevated:** unlike README which a human reads, CLAUDE.md is loaded into every Claude Code session as system instructions. Drift here changes Claude's actual behavior, not just documentation accuracy. Token cost is paid every session, on every prompt.

**Diff-driven section targeting** — choose checks based on what changed:

| Diff touches | Audit these CLAUDE.md sections |
|---|---|
| `api/`, route handlers | Endpoint enumerations + counts |
| `Makefile`, `package.json`, `Cargo.toml`, `pyproject.toml` | Build/Test Commands |
| Top-level dir add/rename/delete | Project Structure paragraph |
| Public function signatures | Architecture paragraphs (grep referenced symbols) |
| Config schema files | JSON/YAML code-block examples |

**Counted enumerations** — find `(N total)` / `N skills` / `N endpoints` patterns; count actual bullets that follow; flag count mismatches.

**Path/package references** — extract every backtick-quoted path (`agent/`, `cli/commands/main.go`); verify each exists; flag missing.

**Endpoint route validation** — if HTTP routes enumerated, grep code for route definitions; flag missing-from-doc or missing-from-code.

**Symbol references** — function/method names mentioned in prose (e.g., `Foo.NewBar(...)`); grep code for definition; flag if absent or signature differs.

**Auto-update vs ask gate is TIGHTER for CLAUDE.md** — pruning ALWAYS asks; only mechanical replacements are auto:

- Auto-update: count-only corrections; rename clearly inferable from the diff (path or command renamed); table-row text fix that doesn't delete a row
- **Ask** (do not auto-update): missing-path removal, section deletion, list-item removal, link-out / move-to-doc, removal-on-feature-removal, any addition that grows file >5% or pushes over soft cap (1500 estimated tokens)

**Hard rule:** any operation that REMOVES content from CLAUDE.md MUST ask the user. Pruning requires human judgment about what context Claude actually needs in-session.
```

- [ ] **Step 3: Verify the replacement**

```bash
# F1: diff-driven section targeting present
grep -c "Diff-driven section targeting" skills/document-sync/SKILL.md
# Expected: 1

# F2: counted enumerations check present
grep -c "Counted enumerations" skills/document-sync/SKILL.md
# Expected: 1

# F3: path/package references check present
grep -c "Path/package references" skills/document-sync/SKILL.md
# Expected: 1

# Tighter gate hard rule present
grep -c "Hard rule" skills/document-sync/SKILL.md
# Expected: 1

# Removal-always-asks language present
grep -F "any operation that REMOVES content from CLAUDE.md MUST ask" skills/document-sync/SKILL.md
# Expected: 1 match
```

If any check returns 0, the Edit didn't land. Re-Read and retry.

- [ ] **Step 4: Stage gate + commit**

```bash
git add skills/document-sync/SKILL.md
staged=$(git diff --cached --name-only | wc -l | tr -d ' ')
[ "$staged" = "1" ] || { echo "STAGE: $staged"; exit 1; }

git commit -m "feat(document-sync): elevate CLAUDE.md handling — diff-driven targeting + counted/path/symbol checks (F1+F2+F3)

- Replace generic 3-bullet CLAUDE.md sub-section with high-stakes framing
- F1: diff-driven section targeting (which CLAUDE.md sections to audit
  based on what changed)
- F2: counted enumerations check (N total / N skills patterns)
- F3: path/package reference existence validation
- Tighter auto-update gate for CLAUDE.md: removal/deletion always asks;
  only mechanical replacements stay auto. Hard rule: any REMOVE op
  must ask the user.

Spec: docs/specs/2026-04-30-document-sync-v2-design.md §4.1, §5.1"
```

---

## Phase 2 — Step 4.7 Hygiene Audit (size + inflation pressure)

### Task 2: Insert new `## Step 4.7: CLAUDE.md Hygiene Audit` section

**Files:**
- Modify: `skills/document-sync/SKILL.md` (insert ~50 lines between Step 4 and Step 5)

- [ ] **Step 1: Locate insertion point**

```bash
grep -n "^## Step 4\|^## Step 5" skills/document-sync/SKILL.md
```

The new Step 4.7 goes immediately before `## Step 5: Apply Auto-Updates`.

- [ ] **Step 2: Read the existing `## Step 5: Apply Auto-Updates` line live**

This line is the anchor. Capture its exact bytes (Read tool around the located line number).

- [ ] **Step 3: Edit — insert Step 4.7 immediately before Step 5**

Use Edit with `old_string` = live "## Step 5: Apply Auto-Updates" line + the line right after it. `new_string` = the same content PLUS the new Step 4.7 prepended.

The Step 4.7 content to insert:

````markdown
## Step 4.7: CLAUDE.md Hygiene Audit (size + inflation pressure)

**Why this step exists:** CLAUDE.md is loaded into every session. Each line costs tokens forever, on every prompt. Drift goes both ways — content can become stale (need update) AND content can become irrelevant (need removal). Step 4 handles the first; this step handles the second.

**Modes:**
- **Auto (default):** runs only if the diff touches `CLAUDE.md` OR file size is over soft cap. Otherwise skipped silently to keep PR-time audits cheap.
- **Forced full sweep (`--full-sweep` flag, or skill invocation phrase "audit CLAUDE.md hygiene"):** runs all hygiene checks regardless of diff/size. Used for monthly hygiene reviews, release pre-flights, and empirical validation of this skill itself.

### Measure size

```bash
lines=$(wc -l < CLAUDE.md)
chars=$(wc -m < CLAUDE.md)
# Token estimate: chars/4 for English/code-heavy; chars/2 for CJK-heavy.
# Heuristic: if >30% of chars are non-ASCII, use chars/2.
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

If found, report the path so the user knows it exists, but DO NOT scan or modify it. Cross-repo handling is a v1.4+ topic.

### Inflation pattern detection

For each pattern, detect candidates and propose action. **Always ASK before mutating** — pruning requires human judgment about what context Claude actually needs in-session.

| Pattern | Detection | Proposed action |
|---|---|---|
| Verbatim list >5 items inline | Bullets after `(N total)` or numbered list | Move to dedicated doc; leave summary + link |
| Phase narrative with 2+ phases | `Phase X.0` count >1 | Keep current phase; archive older to spec docs |
| Architectural detail accretion (≥3 non-list paragraphs in one H2/H3 section) | Count `\n\n`-separated non-list paragraphs between consecutive H2/H3 boundaries | Flag for human review |
| Scar tissue prose | grep `used to|previously|legacy|formerly|in v[0-9]` | Ask "still load-bearing?" |
| Code blocks >10 lines | Lines between ``` markers | Move to schema file; leave reference |
| Rule list >10 items | `^-` bullets in same list | Ask: consolidate or link to convention doc |

### Removal-on-feature-removal

When the diff DELETES a feature (function/route/command/config field), also propose deleting its CLAUDE.md description. The current skill is additive-only — this closes that gap.

### Date-stamp staleness

Find date markers in two **explicit** forms only:
- Parenthesized: `(Month YYYY)` — e.g., `(April 2026)`
- Inline: `as of YYYY-MM` — e.g., `as of 2025-09`

Do NOT match `since YYYY` (too broad — false-positives on license years, compatibility statements, design history). Do NOT match generic dates inside JSON examples or commit-message blocks.

If the date is >6 months old AND the diff doesn't touch nearby code in the same section, ask: "still accurate? still relevant for current contributors?"

### Output

```
## CLAUDE.md Hygiene Report
- Current size: <N> lines / ~<M> estimated tokens (vs 1500 soft cap)
- Mode: <auto | forced full sweep>
- Upstream CLAUDE.md detected: <path or "none">
- Inflation candidates: <list with line refs + proposed action>
- Removal candidates (feature removed in diff): <list>
- Stale-date candidates: <list with date markers>
```

User decides per candidate. Approved actions apply in Step 5.
````

- [ ] **Step 4: Verify Step 4.7 is in place and sectioned correctly**

```bash
# New section header present
grep -c "^## Step 4.7: CLAUDE.md Hygiene Audit" skills/document-sync/SKILL.md
# Expected: 1

# Two modes documented (auto + forced full sweep)
grep -F "Forced full sweep" skills/document-sync/SKILL.md
# Expected: ≥1

# Token-estimate measurement (not just wc -l)
grep -F "wc -m" skills/document-sync/SKILL.md
# Expected: ≥1

# Upstream-CLAUDE.md detection block
grep -F "Detect upstream CLAUDE.md (report-only" skills/document-sync/SKILL.md
# Expected: 1

# All 6 inflation patterns
grep -c "Verbatim list >5 items\|Phase narrative\|Architectural detail accretion\|Scar tissue prose\|Code blocks >10 lines\|Rule list >10 items" skills/document-sync/SKILL.md
# Expected: 6

# Always-ASK rule
grep -F "Always ASK before mutating" skills/document-sync/SKILL.md
# Expected: 1

# Removal-on-removal
grep -F "Removal-on-feature-removal" skills/document-sync/SKILL.md
# Expected: 1

# Date-stamp staleness with the two explicit forms
grep -F "(Month YYYY)" skills/document-sync/SKILL.md
# Expected: ≥1
grep -F "as of YYYY-MM" skills/document-sync/SKILL.md
# Expected: ≥1
grep -F "Do NOT match \`since YYYY\`" skills/document-sync/SKILL.md
# Expected: 1

# Section ordering — Step 4.7 between Step 4 and Step 5
grep -n "^## Step " skills/document-sync/SKILL.md | head -8
# Expected: order should be Step 0, 1, 2, 3, 4, 4.7, 5, 6, 7, 8 (numerically)
```

- [ ] **Step 5: Stage gate + commit**

```bash
git add skills/document-sync/SKILL.md
staged=$(git diff --cached --name-only | wc -l | tr -d ' ')
[ "$staged" = "1" ] || { echo "STAGE: $staged"; exit 1; }

git commit -m "feat(document-sync): add Step 4.7 CLAUDE.md Hygiene Audit (size + inflation)

- New step between Step 4 and Step 5
- Two modes: Auto (default) and forced full-sweep
- Measure size via wc -m + token estimate (chars/4 English, chars/2 CJK);
  soft cap 1500, hard cap 3000 tokens
- Detect upstream CLAUDE.md report-only (do NOT scan)
- 6 inflation patterns with always-ASK gate (verbatim list, phase
  narrative, architectural accretion, scar tissue, code blocks, rule list)
- Removal-on-feature-removal: when diff deletes a feature, propose CLAUDE.md
  removal too (always asks)
- Date-stamp staleness: only (Month YYYY) and as of YYYY-MM forms

Spec: docs/specs/2026-04-30-document-sync-v2-design.md §4.2, §5.2"
```

---

## Phase 3 — Step 5 preamble (bias toward replacement)

### Task 3: Prepend the 3-question preamble to Step 5

**Files:**
- Modify: `skills/document-sync/SKILL.md` (Step 5 prelude — add ~10 lines)

- [ ] **Step 1: Read the start of Step 5 live**

Use Read on `skills/document-sync/SKILL.md` around the current location of `## Step 5: Apply Auto-Updates`. Capture the heading + first paragraph.

- [ ] **Step 2: Edit — insert preamble after the Step 5 heading**

`old_string` = live "## Step 5: Apply Auto-Updates" + the existing first paragraph.

`new_string` = same content with this preamble inserted between the heading and the first paragraph:

```markdown
**Before adding new content to CLAUDE.md, check:**

1. Is there an existing section this belongs to? (Update inline, don't append a new section unless one is genuinely needed)
2. Is the new content actually needed in every Claude Code session? Or could it be linked from a separate doc?
3. Will this content be stale in 6 months? (If yes, link to a versioned doc instead of inlining)

Bias toward replacing/linking-out, not appending.
```

So the result is:

```markdown
## Step 5: Apply Auto-Updates

**Before adding new content to CLAUDE.md, check:**

1. Is there an existing section this belongs to? ...
2. Is the new content actually needed in every Claude Code session? ...
3. Will this content be stale in 6 months? ...

Bias toward replacing/linking-out, not appending.

Make all factual corrections directly using the Edit tool.
...
```

- [ ] **Step 3: Verify**

```bash
grep -F "Before adding new content to CLAUDE.md, check:" skills/document-sync/SKILL.md
# Expected: 1 match

grep -F "Bias toward replacing/linking-out, not appending" skills/document-sync/SKILL.md
# Expected: 1 match

# Step 5 still present and orderly
grep -n "^## Step 5\|^## Step 6" skills/document-sync/SKILL.md | head -2
# Expected: Step 5 line < Step 6 line (preserved)
```

- [ ] **Step 4: Stage gate + commit**

```bash
git add skills/document-sync/SKILL.md
staged=$(git diff --cached --name-only | wc -l | tr -d ' ')
[ "$staged" = "1" ] || { echo "STAGE: $staged"; exit 1; }

git commit -m "feat(document-sync): bias-toward-replacement preamble for Step 5

Before adding new content to CLAUDE.md, the skill now asks 3 hygiene
questions (existing section to fold into? actually needed in every
session? stale in 6 months?) and explicitly biases toward replacing
or linking out rather than appending.

Spec: docs/specs/2026-04-30-document-sync-v2-design.md §4.3, §5.3"
```

---

## Phase 4 — Behavior Test Fixtures

### Task 4: Create 3 fixture CLAUDE.mds for behavior-level acceptance verification

**Files:**
- Create: `skills/document-sync/tests/fixtures/counted-list-mismatch/CLAUDE.md`
- Create: `skills/document-sync/tests/fixtures/missing-path/CLAUDE.md`
- Create: `skills/document-sync/tests/fixtures/over-hard-cap/CLAUDE.md`
- Create: `skills/document-sync/tests/fixtures/README.md` (describes the fixtures + expected behaviors)

These fixtures are inputs to Phase 5's manual subagent verification. Each fixture targets one of the 3 behavior-level acceptance checks from spec §7.

- [ ] **Step 1: Create fixtures directory**

```bash
mkdir -p skills/document-sync/tests/fixtures/counted-list-mismatch
mkdir -p skills/document-sync/tests/fixtures/missing-path
mkdir -p skills/document-sync/tests/fixtures/over-hard-cap
```

- [ ] **Step 2: Write counted-list-mismatch fixture**

Create `skills/document-sync/tests/fixtures/counted-list-mismatch/CLAUDE.md`:

```markdown
# Test Fixture — Counted-List Mismatch

This fixture tests F2 (counted enumerations check). The heading says "5 total" but only 4 bullets follow.

## API Endpoints (5 total)

- `GET /api/v1/health` — public health
- `GET /api/v1/status` — service status
- `POST /api/v1/echo` — debug echo
- `DELETE /api/v1/cache` — clear cache

(Expected document-sync behavior: surface the count mismatch with line ref + suggested fix — either change "5" to "4" or add a missing bullet.)
```

- [ ] **Step 3: Write missing-path fixture**

Create `skills/document-sync/tests/fixtures/missing-path/CLAUDE.md`:

```markdown
# Test Fixture — Missing Path

This fixture tests F3 (path/package reference validation).
The path `pkg/gone/deleted.go` is mentioned but does NOT exist in this fixture root.

## Project Structure

The main entry point is `pkg/gone/deleted.go`. Adjacent helpers live under `pkg/gone/`.

(Expected document-sync behavior: detect that `pkg/gone/deleted.go` doesn't exist, present this as an ASK candidate — never auto-remove the reference. User must confirm.)
```

- [ ] **Step 4: Write over-hard-cap fixture**

Create `skills/document-sync/tests/fixtures/over-hard-cap/CLAUDE.md`. The fixture must exceed 3000 estimated tokens (≥12000 chars for English-heavy content).

Generate with a script (committed under fixture as well) so the size is reproducible:

```bash
cat > skills/document-sync/tests/fixtures/over-hard-cap/generate.sh <<'EOF'
#!/usr/bin/env bash
# Regenerate the over-hard-cap fixture deterministically.
out="$(dirname "$0")/CLAUDE.md"

{
  echo "# Test Fixture — Over Hard Cap"
  echo
  echo "This fixture deliberately exceeds 3000 estimated tokens (~12000 chars)."
  echo "Used to verify the hard-cap gate refuses additive changes."
  echo
  for i in $(seq 1 60); do
    echo "## Section $i"
    echo
    echo "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod"
    echo "tempor incididunt ut labore et dolore magna aliqua ut enim ad minim"
    echo "veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex"
    echo "ea commodo consequat duis aute irure dolor in reprehenderit in voluptate"
    echo "velit esse cillum dolore eu fugiat nulla pariatur excepteur sint."
    echo
  done
} > "$out"

chars=$(wc -m < "$out")
echo "Generated $out: $chars chars (~$((chars / 4)) tokens English-heavy)"
EOF

chmod +x skills/document-sync/tests/fixtures/over-hard-cap/generate.sh
bash skills/document-sync/tests/fixtures/over-hard-cap/generate.sh
```

Verify the fixture is over hard cap:

```bash
chars=$(wc -m < skills/document-sync/tests/fixtures/over-hard-cap/CLAUDE.md)
estimated_tokens=$((chars / 4))
echo "Chars: $chars; estimated tokens: $estimated_tokens"
# Expected: estimated_tokens >= 3000 (i.e., chars >= 12000)
[ "$estimated_tokens" -ge "3000" ] || { echo "FIXTURE TOO SMALL"; exit 1; }
```

- [ ] **Step 5: Write fixtures README**

Create `skills/document-sync/tests/fixtures/README.md`:

```markdown
# document-sync Test Fixtures

These fixtures support the 3 behavior-level acceptance checks from
`docs/specs/2026-04-30-document-sync-v2-design.md` §7.

| Fixture | Target check | Expected skill behavior |
|---|---|---|
| `counted-list-mismatch/` | F2 — counted enumerations | Output contains line ref + suggested fix |
| `missing-path/` | F3 — path/package validation | Present as ASK; never auto-remove |
| `over-hard-cap/` | Hard-cap gate | Reject additive change OR convert to ask/link-out |

## Verification mode

These fixtures are exercised in **forced full-sweep mode**:

```
"Run document-sync against this fixture in forced full-sweep mode."
```

(The default-mode bypass would skip Step 4.7 because the fixtures have no diff and most are small — explicit override is required.)

## Empirical run record

See `skills/document-sync/tests/verification-2026-04-30.md` for the
v1.3.0 empirical verification report.
```

- [ ] **Step 6: Stage gate + commit**

```bash
git add skills/document-sync/tests/fixtures/

staged=$(git diff --cached --name-only | wc -l | tr -d ' ')
echo "Staged: $staged"
# Expected: ≥5 (3 fixture CLAUDE.md + 1 generate.sh + 1 README)
[ "$staged" -ge "5" ] || { echo "STAGE LOW: $staged"; exit 1; }

git commit -m "test(document-sync): add 3 behavior-level fixtures + README

- counted-list-mismatch: F2 (count says 5, only 4 bullets)
- missing-path: F3 (cites pkg/gone/deleted.go that doesn't exist)
- over-hard-cap: hard-cap gate (≥3000 estimated tokens via generate.sh)
- README documents target check + expected behavior + forced full-sweep
  invocation pattern

Spec: docs/specs/2026-04-30-document-sync-v2-design.md §7 (behavior checks)"
```

---

## Phase 5 — Empirical Verification (subagent-driven walkthrough)

### Task 5: Run upgraded skill against fixtures + enterprice_agent; document results

**Files:**
- Create: `skills/document-sync/tests/verification-2026-04-30.md` (verification report)

The skill is prose interpreted by Claude. To verify behavior, dispatch a subagent that:
1. Reads the upgraded `skills/document-sync/SKILL.md`
2. For each of the 3 fixtures: walks through what document-sync WOULD do per the new instructions; records the predicted output
3. For `D:\work\enterprice_agent\CLAUDE.md`: walks through Step 4.7 in **forced full-sweep mode**; records inflation candidates surfaced
4. Writes results to `skills/document-sync/tests/verification-2026-04-30.md`

The plan controller (you, the controlling skill) must dispatch this verification subagent. The subagent has the same prose-reading capability as a real document-sync invocation would have.

- [ ] **Step 1: Dispatch verification subagent**

Use the Agent tool with these instructions (paste verbatim into the subagent prompt; do not delegate "go figure it out"):

```
You are performing empirical verification of the upgraded document-sync skill at v1.3.

Working directory: H:/code_demo/claude_workspace/engineering-workflow-plugin
Skill to verify: skills/document-sync/SKILL.md (just upgraded)
Spec: docs/specs/2026-04-30-document-sync-v2-design.md (the source of truth for expected behavior)

## Your Task

Read the upgraded skill, then walk through what it WOULD do (predicted output, traces) for each of these inputs. Record results in skills/document-sync/tests/verification-2026-04-30.md.

### Token-evidence requirement (anti-self-validation gate)

For each input below, your "Predicted skill output" block MUST contain the
listed literal tokens before you may emit `Verdict: PASS`. If a required
token is missing, emit `Verdict: FAIL` and describe the gap.

This protects against rationalization — you cannot pass a behavior check
purely by saying "the skill would do the right thing"; you must produce
the trace that proves it.

### Input 1: Fixture counted-list-mismatch

File: skills/document-sync/tests/fixtures/counted-list-mismatch/CLAUDE.md
Mode: forced full-sweep
Spec §7 behavior #1: output contains line ref + suggested fix.

**Required tokens in your predicted output (PASS gate):**
- Literal line number: read the fixture file FIRST, identify which line
  contains `## API Endpoints (5 total)`, and reference that exact line
  number in your predicted output (e.g., `line 5` — but verify against
  the fixture; do NOT trust this prompt's hint).
- Literal mismatch detection: the words `count mismatch` (or `mismatch`)
  must appear in your trace.
- Literal suggested fix: at least ONE of the strings `change "5" to "4"`,
  `change 5 to 4`, or `add the missing bullet` must appear in your
  predicted Hygiene Report.

Walk through the skill's instructions; produce the predicted CLAUDE.md
Hygiene Report output (be concrete — paste the exact predicted lines).

### Input 2: Fixture missing-path

File: skills/document-sync/tests/fixtures/missing-path/CLAUDE.md
Mode: forced full-sweep
Spec §7 behavior #2: missing path presented as ASK, not auto-remove.

**Required tokens in your predicted output (PASS gate):**
- Literal path mention: `pkg/gone/deleted.go` must appear.
- Literal action verb: the predicted output must use `ask` (or `ASK`)
  to classify this as user-confirmation-required. The token
  `auto-remove` MUST NOT appear in connection with this path.
- Literal gate quote: the predicted trace must reference the skill's
  Hard Rule (e.g., `any operation that REMOVES content from CLAUDE.md
  MUST ask`).

Walk through; predict output.

### Input 3: Fixture over-hard-cap

File: skills/document-sync/tests/fixtures/over-hard-cap/CLAUDE.md
Mode: forced full-sweep WITH a simulated additive-change scenario
(e.g., "the diff added a new endpoint, a new bullet would be appended").
Spec §7 behavior #3: hard-cap gate refuses the addition OR converts to
ask/link-out; no silent append.

**Required tokens in your predicted output (PASS gate):**
- Literal size measurement: the predicted output must include a token
  count or char count that you computed for the fixture (state the
  actual number — e.g., `~5250 estimated tokens`). Read the fixture
  with `wc -m` to compute.
- Literal cap reference: the strings `hard cap` and `3000` must appear.
- Literal action: at least ONE of `refuse`, `reject`, or `link-out`
  must appear in connection with the proposed addition. The token
  `silent append` MUST NOT be used as the predicted behavior.

### Optional Input 4 — REMOVED from this dispatch

The original plan included a walkthrough of `D:/work/enterprice_agent/
CLAUDE.md` here. That input is **removed** from the subagent dispatch
because (a) the path is outside the plugin repo and may be inaccessible,
and (b) without read access the subagent has motivation to hallucinate
plausible inflation candidates from the spec text. Spec §11 already
classifies this empirical run as **manual verification** by the
controller, not by the subagent.

The controller will perform the enterprice_agent walkthrough manually
after this subagent verification completes. Do NOT include "Empirical:
enterprice_agent" in your verification report.

## Output Format

Write skills/document-sync/tests/verification-2026-04-30.md with:

```markdown
# document-sync v1.3 Empirical Verification

**Plan date:** 2026-04-30 (when this plan was authored)
**Run date:** <fill with actual execution date — `date +%Y-%m-%d` at run time>
**Skill version:** v1.3 (post-Phase-3 commits)
**Mode:** forced full-sweep

## Summary

| Test | Result |
|---|---|
| Behavior #1: counted-list mismatch | PASS / FAIL |
| Behavior #2: missing path → ask | PASS / FAIL |
| Behavior #3: over-hard-cap rejection | PASS / FAIL |

(Empirical run on enterprice_agent CLAUDE.md is performed by the controller manually, not by this subagent. See Phase 5 Step 4 — Manual Empirical Check.)

## Test Details

### Behavior #1 — counted-list-mismatch

**Predicted skill output:**
<paste predicted output>

**Pass criteria check:** ...

### Behavior #2 — missing-path

...

### Behavior #3 — over-hard-cap

...

## Gaps Identified

(If any test FAILS, fill this section with one or more structured fix
blocks. Use the EXACT format below — implementer relies on it for
mechanical Edit-tool dispatch:)

```
### Gap 1: <one-line description>

**File:** <path relative to plugin repo>

**Old text:**
```
<exact bytes from current SKILL.md that need replacing>
```

**New text:**
```
<exact replacement bytes>
```

**Pass-criteria after fix:** <which behavior check this gap unblocks>
```

If verdict is PASS, leave this section empty (or "(no gaps)").

## Verdict

Emit EXACTLY one of these two single-line verdicts as the final line of the report (Phase 7's acceptance gate uses `grep -q "^Verdict: PASS$"`):

```
Verdict: PASS
```

or

```
Verdict: FAIL
```

If FAIL: also fill the "Gaps Identified" section above (see structured-block requirement).
```

Save the file, then report the verdict back to the controller.
```

Wait for the subagent to return the verdict.

- [ ] **Step 2: Read the verification report and gate on subagent verdict**

Read `skills/document-sync/tests/verification-2026-04-30.md`. The final line MUST be either `Verdict: PASS` or `Verdict: FAIL`.

**If verdict is PASS:** proceed to Step 3 (manual empirical — also gating).

**If verdict is FAIL — fix gaps inline before continuing:**

The "Gaps Identified" section MUST be filled with structured fix blocks (per the prompt template). Each gap contains an exact `Old text:` / `New text:` pair plus a Pass-criteria.

For each gap:
- Read the live target file (per Universal Rule)
- Apply the structured Edit using `Old text` as `old_string` and `New text` as `new_string`
- Run the gap's Pass-criteria check; confirm it now passes

After all gaps applied, re-dispatch the subagent with the SAME prompt as Step 1 (full re-run, not "restricted to failed inputs only" — the fixes may have ripple effects). Append a `## Second Pass (post-fix)` section to the verification report. The second-pass `Verdict:` line must be `PASS` to continue.

If the SECOND pass also FAILS, stop — escalate to user. Do not commit.

- [ ] **Step 3: Manual empirical check on `D:/work/enterprice_agent/CLAUDE.md`** (controller-level; **gating when readable**)

This check runs BEFORE the Phase 5 commit. Per spec §7 acceptance criterion #empirical, when the path is accessible, ≥3 inflation candidates from {I1, I3, I5} must be surfaced AND no false positives on stable sections (Coding Style, Commit Guidelines).

The subagent above only verified 3 in-repo fixtures (R3 fix from plan-review round 1). enterprice_agent stays manual to avoid hallucination on an external path the subagent may not be able to read. But the OUTCOME still gates this phase.

```bash
# Step 3a: confirm path is readable from this session
if ls -la D:/work/enterprice_agent/CLAUDE.md > /dev/null 2>&1; then
  echo "READABLE — perform manual walkthrough (gating)"
else
  echo "UNREADABLE — manual empirical SKIPPED (non-blocking)"
fi
```

**If READABLE — gate strictly:**

The controller (you, the orchestrating agent) performs the walkthrough manually:
- Read `D:/work/enterprice_agent/CLAUDE.md`
- Apply Step 4.7 (forced full-sweep mode) of the upgraded SKILL.md mentally
- Append a new section `## Manual Empirical: enterprice_agent` to `verification-2026-04-30.md` containing:
  - The predicted Hygiene Report (concrete candidates with line refs)
  - Pass criteria check: `≥3 candidates from {I1, I3, I5}`?
  - False-positive check: any flag on Coding Style (~lines 18-22) or Commit Guidelines (~lines 35-39)?
- Append a single-line verdict at the END of that new section: `Manual empirical: PASS` or `Manual empirical: FAIL`.

**If `Manual empirical: FAIL`** — block. Either:
1. Fix gaps in the upgraded SKILL.md so the predicted output would meet the criteria, then re-walk and re-verdict. OR
2. Escalate to user with the failure details — do not proceed to Phase 5 commit.

**If UNREADABLE — SKIP allowed:**

Append `## Manual Empirical: enterprice_agent — SKIPPED (path not accessible from this session)` to the verification report. This is non-blocking only because the path is genuinely unavailable; if access exists, the gate is enforced.

- [ ] **Step 4: Stage gate + commit verification report (and any fixes from Step 2)**

```bash
# verification report always staged (now contains: 3-fixture verdict + manual empirical or SKIPPED note)
git add skills/document-sync/tests/verification-2026-04-30.md

# if any SKILL.md fixes were applied during gap-resolution (Step 2) or manual-empirical fix-up, stage them too
[ -n "$(git diff skills/document-sync/SKILL.md)" ] && git add skills/document-sync/SKILL.md

staged=$(git diff --cached --name-only | wc -l | tr -d ' ')
[ "$staged" -ge "1" ] && [ "$staged" -le "2" ] || { echo "STAGE: $staged"; exit 1; }

git commit -m "test(document-sync): empirical verification report (Phase 5)

Subagent verified 3 in-repo fixtures in forced full-sweep mode with
token-evidence gates. Manual empirical on D:/work/enterprice_agent
performed by controller (or SKIPPED if path unreadable).

Verdict: PASS

(If gaps were found and fixed inline, this commit also contains the
SKILL.md fixes — see git diff for specifics.)

Spec: docs/specs/2026-04-30-document-sync-v2-design.md §7, §11"
```

---

## Phase 6 — Docs Sync + Version Bump

### Task 6: CHANGELOG, README, plugin.json, marketplace.json

**Files:**
- Modify: `CHANGELOG.md` (new v1.3.0 entry)
- Modify: `README.md` (only if document-sync description warrants update)
- Modify: `.claude-plugin/plugin.json` (version 1.2.0 → 1.3.0)
- Modify: `.claude-plugin/marketplace.json` (2 version fields, both 1.2.0 → 1.3.0)

- [ ] **Step 1: Compute today's date dynamically**

```bash
TODAY=$(date +%Y-%m-%d)
echo "Will use date: $TODAY"
```

- [ ] **Step 2: Update CHANGELOG.md — insert v1.3.0 entry above v1.2.0**

Use a bash heredoc with `$TODAY` interpolation; do NOT leak `<TODAY>` placeholder.

```bash
TODAY=$(date +%Y-%m-%d)

ENTRY=$(cat <<EOF
## [1.3.0] - $TODAY

### Added

- \`document-sync\` skill: new \`Step 4.7: CLAUDE.md Hygiene Audit\` —
  size budget (1500/3000 token caps), 6 inflation patterns, removal-on-
  feature-removal proposal, date-stamp staleness flag. Two modes:
  Auto (default, bypassable) and forced full-sweep.
- Diff-driven section targeting (F1): the skill chooses CLAUDE.md
  audit checks based on what changed in the diff.
- Counted enumerations check (F2): detects \`(N total)\` or \`N skills\`
  mismatches against actual bullet count.
- Path/package reference validation (F3): backtick-quoted paths in
  CLAUDE.md must exist in the repo.
- 3 behavior-level fixtures under \`skills/document-sync/tests/fixtures/\`
  for empirical acceptance checks.

### Changed

- \`document-sync\` Step 5 prepended with bias-toward-replacement
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
  AND file under soft cap; \`--full-sweep\` overrides for monthly
  reviews and pre-release checks.
- No new dependencies; pure prose change to one skill.

EOF
)

echo "Will prepend entry (first 3 lines):"
echo "$ENTRY" | head -3
# Expected first line: "## [1.3.0] - 20YY-MM-DD"
```

Use Edit tool to prepend `$ENTRY` content (the materialized text, not the literal `$ENTRY`) immediately before the `## [1.2.0]` heading in CHANGELOG.md.

Verify date is real:

```bash
grep -E "## \[1.3.0\] - 20[0-9]{2}-[0-9]{2}-[0-9]{2}" CHANGELOG.md | wc -l
# Expected: 1

grep -F "<TODAY>" CHANGELOG.md
# Expected: 0 (no leaked placeholder)
```

- [ ] **Step 3: Update README.md document-sync description (if needed)**

Read the README's skills table for the `document-sync` row.

```bash
grep -n "document-sync" README.md
```

If the existing description is acceptable (e.g., "Sync documentation to match shipped code") — no change needed.

If it lacks the new hygiene capability, update the row to:

```markdown
| **document-sync** | Sync documentation to match shipped code; CLAUDE.md hygiene audit (size budget + inflation prune) | After PR creation, "update the docs" |
```

(Use Edit with the live row as `old_string`.)

- [ ] **Step 4: Bump `.claude-plugin/plugin.json` version**

Read the file. Change `"version": "1.2.0"` → `"version": "1.3.0"`.

If the description is shorter than 250 chars, append " Now with CLAUDE.md hygiene audit." to make the v1.3 capability discoverable.

- [ ] **Step 5: Bump `.claude-plugin/marketplace.json` (2 version fields)**

```bash
grep -n '"version":' .claude-plugin/marketplace.json
# Expected: 2 lines (metadata.version + plugins[0].version), both "1.2.0"
```

For each line, change `"1.2.0"` → `"1.3.0"`.

- [ ] **Step 6: Verify all edits**

```bash
# CHANGELOG
grep -E "## \[1.3.0\] - 20[0-9]{2}-[0-9]{2}-[0-9]{2}" CHANGELOG.md
# Expected: 1 hit

# plugin.json
grep -E '"version": "1.3.0"' .claude-plugin/plugin.json
# Expected: 1 hit

# marketplace.json (2 hits)
grep -cE '"version": "1.3.0"' .claude-plugin/marketplace.json
# Expected: 2

# Old version gone from manifest files
grep -E '"version": "1.2.0"' .claude-plugin/plugin.json .claude-plugin/marketplace.json
# Expected: 0 hits
```

- [ ] **Step 7: Stage gate + commit**

```bash
git add CHANGELOG.md .claude-plugin/plugin.json .claude-plugin/marketplace.json
# Add README.md only if it was changed in Step 3:
[ -n "$(git diff README.md)" ] && git add README.md

staged=$(git diff --cached --name-only | wc -l | tr -d ' ')
echo "Staged: $staged"
# Expected: 3 (CHANGELOG + plugin.json + marketplace.json) or 4 (with README)
[ "$staged" -ge "3" ] && [ "$staged" -le "4" ] || { echo "STAGE: $staged"; exit 1; }

git commit -m "chore(release): bump plugin manifest to 1.3.0; CHANGELOG entry

- .claude-plugin/plugin.json: 1.2.0 → 1.3.0
- .claude-plugin/marketplace.json: 1.2.0 → 1.3.0 (both metadata.version
  and plugins[0].version)
- CHANGELOG.md: v1.3.0 entry — document-sync v2 (CLAUDE.md hygiene audit
  + freshness improvements F1+F2+F3 + tighter gate + bias-toward-replacement)

Marketplace consumers will pick up v1.3.0 on next /plugin update or
reinstall."
```

---

## Phase 7 — Final Verify + Tag v1.3.0

### Task 7: Run all acceptance gates + tag

- [ ] **Step 1: Run all spec §7 acceptance checks against current HEAD**

```bash
bash -c '
# F1 — diff-driven section targeting
grep -q "Diff-driven section targeting" skills/document-sync/SKILL.md || { echo FAIL: F1; exit 1; }

# F2 — counted enumerations
grep -q "Counted enumerations" skills/document-sync/SKILL.md || { echo FAIL: F2; exit 1; }

# F3 — path/package references
grep -q "Path/package references" skills/document-sync/SKILL.md || { echo FAIL: F3; exit 1; }

# Step 4.7 — Hygiene Audit
grep -q "^## Step 4.7: CLAUDE.md Hygiene Audit" skills/document-sync/SKILL.md || { echo FAIL: Step 4.7; exit 1; }

# Soft + hard cap stated
grep -q "1500" skills/document-sync/SKILL.md && grep -q "3000" skills/document-sync/SKILL.md || { echo FAIL: caps; exit 1; }

# All 6 inflation patterns
[ "$(grep -c "Verbatim list >5 items\|Phase narrative\|Architectural detail accretion\|Scar tissue prose\|Code blocks >10 lines\|Rule list >10 items" skills/document-sync/SKILL.md)" = "6" ] || { echo FAIL: 6 patterns; exit 1; }

# Removal-on-removal
grep -q "Removal-on-feature-removal" skills/document-sync/SKILL.md || { echo FAIL: removal-on-removal; exit 1; }

# Step 5 preamble
grep -q "Before adding new content to CLAUDE.md, check:" skills/document-sync/SKILL.md || { echo FAIL: Step 5 preamble; exit 1; }

# Tighter gate for CLAUDE.md
grep -q "Hard rule" skills/document-sync/SKILL.md || { echo FAIL: tighter gate hard rule; exit 1; }

# Verification report exists with PASS verdict
[ -f skills/document-sync/tests/verification-2026-04-30.md ] || { echo FAIL: verification report missing; exit 1; }
grep -q "^Verdict: PASS$" skills/document-sync/tests/verification-2026-04-30.md || { echo FAIL: verification verdict not PASS; exit 1; }

# Manifest version
grep -q "\"version\": \"1.3.0\"" .claude-plugin/plugin.json || { echo FAIL: plugin.json version; exit 1; }
[ "$(grep -c "\"version\": \"1.3.0\"" .claude-plugin/marketplace.json)" = "2" ] || { echo FAIL: marketplace.json versions; exit 1; }

# CHANGELOG v1.3.0 with real date
grep -qE "## \[1.3.0\] - 20[0-9]{2}-[0-9]{2}-[0-9]{2}" CHANGELOG.md || { echo FAIL: CHANGELOG date; exit 1; }

# Fixtures exist
[ -f skills/document-sync/tests/fixtures/counted-list-mismatch/CLAUDE.md ] || { echo FAIL: fixture 1 missing; exit 1; }
[ -f skills/document-sync/tests/fixtures/missing-path/CLAUDE.md ] || { echo FAIL: fixture 2 missing; exit 1; }
[ -f skills/document-sync/tests/fixtures/over-hard-cap/CLAUDE.md ] || { echo FAIL: fixture 3 missing; exit 1; }

echo "ALL ACCEPTANCE CHECKS PASSED"
'
```

If any FAIL: do not proceed; investigate and fix.

- [ ] **Step 2: Pre-tag re-validation (W2-style — guard against rebase between phases)**

Re-run Step 1 to ensure HEAD still passes after any intermediate operations.

```bash
git log --oneline -10
# Verify recent log shows phases 1-7 commits (8 commits + spec/plan baseline)
```

- [ ] **Step 3: Tag v1.3.0**

```bash
git tag -a v1.3.0 -m "Engineering Workflow Plugin v1.3.0 — document-sync v2 (CLAUDE.md hygiene)"

# Confirm annotated tag at HEAD
git cat-file -t v1.3.0
# Expected: tag (annotated)

git rev-parse v1.3.0^{commit}
# Expected: SHA of HEAD (the manifest-bump commit from Phase 6)
```

- [ ] **Step 4: Final summary output**

```bash
echo "=== v1.3.0 release ==="
git log --oneline 'v1.2.0..HEAD' | wc -l  # commits in v1.3 release
git diff --shortstat 'v1.2.0..HEAD'
echo "Tag:"; git tag -l v1.3.0
echo "Tag message:"; git tag -n v1.3.0
```

---

## Self-Review (against spec)

This plan was checked against `docs/specs/2026-04-30-document-sync-v2-design.md`:

**1. Spec coverage:**
- §4.1 F1 (diff-driven section targeting) → Task 1
- §4.1 F2 (counted enumerations) → Task 1
- §4.1 F3 (path validation) → Task 1
- §4.2 H1 (size measure with wc -m + token estimate) → Task 2
- §4.2 H2 (6 inflation patterns) → Task 2
- §4.2 H3 (removal-on-removal) → Task 2
- §4.2 H4 (date-stamp staleness, 2 forms only) → Task 2
- §4.3 (Step 5 preamble) → Task 3
- §4.4 (tighter CLAUDE.md gate) → Task 1 (gate text replaced as part of sub-section replacement)
- §6 (size budget canonical) → covered in skill text via Task 2's "Soft cap: 1500" / "Hard cap: 3000" lines
- §7 acceptance — all 13 checks → Task 7 final verify + Task 5 empirical verification + Task 4 fixture creation
- §8 migration — handled via "first run warns + lists prune candidates" wording in Task 2's Step 4.7 content
- §9 risks — none require code; all are mitigated by skill text or existing flow
- §10 sequencing — 7 phases / 8 tasks here; matches spec's phase decomposition

**2. Plan-review fixes integrated** (from spec audit-team round 1):
- H1 (missing-path removal auto→ask conflict) → Task 1's gate text
- H2 (forced full-sweep for empirical) → Task 2's modes block + Task 5's prompt + Task 7's verdict check
- M3 (size measurement wc -m + token estimate) → Task 2 measure block
- M4 (date-stamp drop "since YYYY") → Task 2's date-stamp block
- M5 (3 behavior-level acceptance) → Task 4 fixtures + Task 5 verification
- I3 threshold ≥3 → Task 2's Architectural detail accretion row
- OOS upstream-CLAUDE.md report-only → Task 2's "Detect upstream CLAUDE.md" block

**3. Placeholder scan:** No "TBD" / "TODO" / "implement later". CHANGELOG date dynamically computed (W1-style fix from v1.2 carried forward).

**4. Cross-task consistency:**
- Task 1 establishes the new sub-section; Task 2 inserts Step 4.7 between Step 4 and Step 5 (depends on Task 1 not changing Step 4/5 boundaries — confirmed: Task 1 only replaces a sub-section under Step 4, doesn't move Step 4/5 headers)
- Task 3 modifies Step 5 (depends on Task 2 not changing Step 5 anchor — confirmed: Task 2 inserts BEFORE Step 5)
- Task 5 references the upgraded SKILL.md (depends on Tasks 1-3 committed)
- Task 5 inline gap-fix branch only fires conditionally (FAIL verdict from subagent); structured Old/New blocks required
- Task 7 final-verify covers everything from Tasks 1-6

**5. Scope:** Confined to one SKILL.md + 4 new fixture files + standard release housekeeping. No Python, no new skills, no new dependencies. Realistic ~half-day effort.

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-04-30-document-sync-v2.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review per task. Best for prose discipline (each Edit needs Read-first byte-exact match) + Phase 5 already needs subagent dispatch by design.

**2. Inline Execution** — sequential in one session. Faster but less review rigor.

Which approach?
