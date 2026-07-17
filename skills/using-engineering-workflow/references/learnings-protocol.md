# Learnings Protocol — v1.1

**Versioning:** This is protocol v1.1. Breaking changes will document migration when needed.
**v1.1 (2026-07-17):** added READ step L0 (domain glossary); MAINTAIN trigger rephrased for the user-invoked `/learnings-refresh`; participation table completed (`grill-me`, `loop-verify`, `resolve-pr-feedback`). No breaking changes.

Any skill that reads, writes, or maintains `docs/learnings/` MUST follow this protocol. Skills cite this document and inherit its rules; per-skill semantics (e.g., security-audit's category filter) layer on top.

## READ Phase (analysis skills, before main work)

0. **L0 — Domain glossary:** If `CONTEXT.md` exists at the repo root, read it before L1 and adopt its vocabulary in output (see `domain-glossary.md`). Absent glossary → skip silently.
1. **L1 — INDEX-first:** If `docs/learnings/INDEX.md` exists, read it. Use the Domain section relevant to the changed files / scope to build a candidate list.
2. **L2 — Synthesis-preferred:** When the Domain has a 📚 synthesis doc, read it FIRST. A synthesis summarizes 3+ individual learnings; reading it can replace reading the individuals.
3. **L3 — Targeted reads:** Read individual learning files when the synthesis points to them, OR when the Domain has no synthesis.
4. **L4 — Grep fallback:** Use `Grep docs/learnings/` for keyword-precise matches OR when INDEX is absent / staleness > 60 days.
5. **Cite sources:** Output the list of learnings consulted (paths) so the user can audit. "No prior knowledge applied" is a valid output when nothing matched.

## WRITE Phase (after analysis, when findings are reusable)

1. Suggest `knowledge-compound`; do not write directly. The user opts in.
2. Required frontmatter: `track` (bug/knowledge/decision), `status` (active/superseded/archived). Optional: `category`, `last-verified`, `superseded-by`.
3. Cross-reference: search for ≥1 related existing learning; add bidirectional `Related:` links.
4. Synthesis trigger: if ≥3 active learnings share a category, prompt user to consider a synthesis doc instead of a 4th leaf.

## MAINTAIN Phase (periodic)

The MAINTAIN phase is implemented by the `learnings-refresh` skill (current).

1. Runs when the user invokes `/learnings-refresh` (the skill is user-invoked; the model cannot self-invoke it). Suggest it monthly, when the user asks to refresh/audit learnings, or when the session-start hook signals a threshold crossing.
2. Never auto-mutate. Detection is read-only; user confirms each action.
3. Preserve INDEX-authored sections by heading allowlist (`## Refresh Cycle`, `## How to Use This Index`, `## Notes for Future Refreshes`).
4. Apply curation actions (archive / supersede / synthesize) only after explicit user confirmation per row.

## Failure Modes (do not do)

- ❌ Bake project-specific patterns into skill prompts (keep skills general; project knowledge lives in the project's `docs/learnings/`)
- ❌ Auto-archive or auto-merge without user confirmation
- ❌ Write learnings without `track` and `status` (other fields optional)
- ❌ Skip INDEX check and grep blindly when INDEX exists
- ❌ Read learnings into the reviewer prompt without citing them in the output

## Read-Side Tolerance

Existing learnings without frontmatter remain valid. Parsers default:
- `track` → `knowledge`
- `status` → `active`
- `last-verified` → file's git creation date
- `category`, `superseded-by` → unset

## Skill Participation Reference

| Skill | Phase(s) |
|---|---|
| `using-engineering-workflow` | meta — pins this protocol |
| `knowledge-compound` | WRITE (primary) |
| `learnings-refresh` | MAINTAIN (primary) |
| `structured-review` | READ + suggest WRITE |
| `plan-review-personas` | READ |
| `grill-me` | READ + suggest WRITE |
| `loop-verify` | suggest WRITE (light) |
| `security-audit` | READ + suggest WRITE |
| `e2e-browser-test` | READ + suggest WRITE |
| `ship-and-pr` | READ + suggest WRITE |
| `engineering-retro` | READ + suggest WRITE |
| `resolve-pr-feedback` | suggest WRITE (light) |
| `document-sync` | suggest WRITE (light) |
