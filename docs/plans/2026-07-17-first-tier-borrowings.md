# First-Tier Borrowings from mattpocock/skills (plugin v1.8)

> **For agentic workers:** 5-item borrowing set from the 2026-07-17 mattpocock/skills comparison, first tier only. Docs/skill-text changes; no runtime code. Steps use checkbox syntax.
>
> **Plan review:** round 1 — feasibility: FEASIBLE WITH CHANGES; scope-guardian: TRIM RECOMMENDED; merged verdict **REVISE** (no blockers). Revisions below are incorporated (marked ↻). Proceeding without re-review per minor-revision rule.

**Goal:** Land the five first-tier borrowings — ① domain glossary layer (CONTEXT.md), ② invocation dichotomy (user-invoked vs model-invoked), ③ skill-authoring reference, ④ maintenance sync invariants + drift fixes, ⑤ grill-me facts/decisions HITL rule — as plugin v1.8.0.

**Source:** Deep-compare session 2026-07-17 (mattpocock/skills commit 9603c1c; CodeWiki at `D:\git\mattpocock\skills\.codewiki\`). All adopted text is independently written (adapted, attributed), not copied.

**Oracle (floor #2):** consistency check script (scratchpad, temporary scaffolding — not committed) asserting counts sync + flips + no "10 skills" remnants + participation-table completeness + version ×3. Verified RED today (6 failures). ↻ `claude plugin validate . --strict` validates the marketplace manifest only (baseline PASS today) — it does NOT verify the flip; flip verified by the script + a post-change behavior spot-check (`claude plugin details` / manual `/learnings-refresh` in a fresh session, user-side). Plus plan-review (done) and structured-review on the final diff.

## Global Constraints

- **Conservative-wins:** every new convention is opt-in for consumer projects; no behavior change for projects without `CONTEXT.md`.
- Runtime references in English; maintainer-facing docs (repo CLAUDE.md, skill-authoring) in Chinese.
- `learnings-protocol.md` bumps v1.0 → **v1.1** (L0 glossary read + participation-table completion + MAINTAIN phrasing rewrite; ↻ not purely additive — the MAINTAIN trigger sentence is rewritten; one version-header changelog line covers all three, finalized after Task 4).
- Version **1.8.0** in `plugin.json` + `marketplace.json` (×2 fields). CHANGELOG entry in house style.
- No commits until the user says so (repo convention: 手动提交). No push.
- ↻ **Single canonical home rule:** the invocation decision criterion lives in CONTRIBUTING only; plugin CLAUDE.md and skill-authoring.md carry pointers, never restatements.
- ↻ `../CLAUDE.md` (workspace, outside this git repo) gets exactly one route-line edit — executed as an explicitly announced separate step in the final report (out of structured-review's diff scope; separately revertable).

---

## Task 1 — ① Domain glossary layer

**Files:** create `skills/using-engineering-workflow/references/domain-glossary.md`; edit `references/learnings-protocol.md`, `skills/using-engineering-workflow/SKILL.md`, `skills/grill-me/SKILL.md`, `README.md` (one pointer line).

- [ ] `domain-glossary.md` (English, ~60 lines, advisory SHOULD): what CONTEXT.md is (pure glossary — project-specific terms only, 1-2 sentences each, `_Avoid:` banned near-synonyms; NO implementation details, NOT a spec/scratchpad); lazy creation (only when there's something to write, with user consent); inline updates during sessions (not batched); READ discipline (analysis skills read it first when present, adopt its vocabulary); explicit mapping — **ADR-worthy decisions route to `knowledge-compound` Decision track** (no separate ADR system); attribution to Matt Pocock's `domain-modeling`/CONTEXT-FORMAT (MIT).
- [ ] `learnings-protocol.md` → v1.1: add READ step "L0 — Domain glossary" pointing at `domain-glossary.md`.
- [ ] `using-engineering-workflow/SKILL.md` Rule 4: one short pointer paragraph (opt-in, conservative-wins).
- [ ] ↻ `grill-me/SKILL.md`: **no new section** — extend the existing Hand-off section with 1-2 lines: newly coined/sharpened project terms → offer to record in `CONTEXT.md` per `using-engineering-workflow/references/domain-glossary.md`; trade-off decisions continue to Decision track (existing line). No mechanics restated.

## Task 2 — ② Invocation dichotomy

**Files:** edit `skills/engineering-retro/SKILL.md` + `skills/learnings-refresh/SKILL.md` (frontmatter + description ↻+ body "When to Use" freshening), `skills/using-engineering-workflow/SKILL.md` (Rule 1 row + Available Skills rows ↻+ Rule 4 MAINTAIN lines 139/141), `README.md` (table rows ↻+ Knowledge Loop prose sentence line 166), `hooks/session-start` (2 signal strings), `CONTRIBUTING.md` (frontmatter rule + invocation criterion — canonical home), `../CLAUDE.md` (retro route line, announced separately), `docs/engineering-workflow-guide.md` (matching lines).

- [ ] Flip `engineering-retro` + `learnings-refresh` to `disable-model-invocation: true`; descriptions become human-facing one-liners (no trigger lists). Rationale: deliberate maintenance rituals, interactive by design, never invoked mid-flow by another skill (grep-verified); the model **suggests the user run** `/engineering-retro` / `/learnings-refresh` (↻ bare name primary, plugin-qualified `/engineering-workflow:…` as fallback phrasing where suggested).
- [ ] Update every routing surface to suggest-the-user phrasing: Rule 1 table, Available Skills table, ↻ Rule 4 MAINTAIN bullet + INDEX line, README table + ↻ README "invoke via 'refresh learnings'" sentence, guide lines, session-start signal strings (↻ preserve 30+/50+ threshold semantics in the signal strings + meta rule — description no longer carries them).
- [ ] CONTRIBUTING: amend "Only `name` and `description`" rule → `disable-model-invocation: true` allowed for user-invoked skills; add the decision criterion (model-invoked ONLY if the agent must reach it autonomously or another skill invokes it; user-invoked = human-facing one-line description). ↻ This is the single canonical home of the criterion.

## Task 3 — ③ Skill-authoring reference

**Files:** create `docs/skill-authoring.md`; edit `CONTRIBUTING.md`.

- [ ] `docs/skill-authoring.md` (Chinese, maintainer-facing) **owns methodology**: predictability as root virtue; context/cognitive load economics (pointer to CONTRIBUTING for the decision criterion); description rules (front-load leading words, one trigger per branch, CSO); information hierarchy ladder (steps vs reference, progressive disclosure, completion criterion = clarity + demand); leading words; pruning (no-op hunting per sentence, single source of truth, sediment); failure-mode table (premature completion / duplication / sediment / sprawl / no-op / negation / negative space); our layer: Iron Law + Red Flags conventions, blind-eval requirement for judgment artifacts (pointers to `skills/using-engineering-workflow/tests/README.md` + the two 2026-07-06 learnings). Attributed to writing-great-skills (MIT), adapted.
- [ ] ↻ **Ownership split:** CONTRIBUTING "Skill Writing Standards" shrinks to repo-mechanical checklist (frontmatter fields, CSO rule, invocation criterion, cross-reference rules, required sections list) + pointer to `docs/skill-authoring.md` for methodology. skill-authoring.md does not restate the mechanical checklist.

## Task 4 — ④ Maintenance invariants + drift fixes

**Files:** create `CLAUDE.md` (plugin repo root); edit `ARCHITECTURE.md`, `README.md` (line 143), `CONTRIBUTING.md` (layout tree), `learnings-protocol.md` (participation table), `skills/document-sync/SKILL.md` (one bullet).

- [ ] Plugin `CLAUDE.md` (Chinese, ≤ ~1200 tokens, mechanism not documentation): sync invariants — skill add/remove/rename/behavior change ⇒ update Rule 1 routing table + Available Skills table + README table & headline counts + ARCHITECTURE counts/lists + CONTRIBUTING layout + guide + CHANGELOG + version ×3; "router that lies" rule for the meta skill; ↻ invocation policy as one pointer line to CONTRIBUTING; pointers to `docs/skill-authoring.md` + blind-eval protocol; versioned-contract rule (protocol edits bump version).
- [ ] Fix drift: ARCHITECTURE:21 "(10 skills)" → 12+1 with full list; ARCHITECTURE:169 "All 10 learning-touching skills" → uncounted phrasing ↻ and "(v1.0)" → "(v1.1)" on the same line; ↻ README:143 "10 skills + 2 hooks" (third remnant); CONTRIBUTING layout tree gains grill-me / learnings-refresh / loop-verify.
- [ ] Protocol participation table: add `grill-me` ↻ as **READ + suggest WRITE** (Hand-off suggests knowledge-compound) and `loop-verify` ↻ as **suggest WRITE (light)** (matches reality — no READ floor exists; adding one would be new behavior outside first tier).
- [ ] `document-sync` ARCHITECTURE.md checklist gains: counted enumerations (same F2 check as CLAUDE.md).

## Task 5 — ⑤ grill-me HITL rule

**Files:** edit `skills/grill-me/SKILL.md`.

- [ ] Sharpen Method rule 3 into facts/decisions dichotomy: **facts** (discoverable in files/grep/git) → explore, never ask; **decisions** (trade-offs, preferences, scope) → always put to the user and wait, even when a plausible answer exists — an agent that answers its own questions has broken the loop (matters most when grill-me runs inside another flow). Add matching Red Flags row.

## Task 6 — Version, changelog, checks

- [ ] `plugin.json` + `marketplace.json` → 1.8.0.
- [ ] CHANGELOG 1.8.0 entry (Added/Changed/Compatibility; conservative-wins; the invocation flip's UX change called out).
- [ ] Run consistency script (must be GREEN) + `claude plugin validate . --strict` (manifest-level regression only). ↻ Behavior spot-check of the flip is user-side (fresh session): note it in the final report.
- [ ] `structured-review` on the full diff; fix safe_auto findings.
