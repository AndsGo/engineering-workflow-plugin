# Decision Rules — Refresh Recommendations

When `learnings-refresh` surfaces a learning with one or more signals, apply these defaults. **The user always confirms** — these are STARTING POINTS, not final answers.

## Signal → Recommendation

| Signal | Default recommendation | Reason |
|---|---|---|
| `ref-missing` (cited code path no longer exists) | candidate `archive` (Knowledge/Bug); candidate `supersede` (Decision) | Code that grounded the learning is gone |
| `old-and-uncited` (180+ days, 0 inbound `Related:`) | candidate `archive` | Probably never reused |
| Cluster ≥3 same category | candidate `synthesize` | Worth rolling into one umbrella doc |
| Decision-track learning, ANY signal | candidate `supersede` (NOT archive) | Decisions retain rationale; supersede preserves history |
| Bug-track learning, last-verified > 90 days, ref-missing | candidate `archive` (user confirms bug class extinct) | Script can't prove fix; user judges |
| `status: superseded` for ≥1 refresh cycle | candidate `archive` | Grace period to surface broken inbound links |

## Threshold Reference

These thresholds are HARDCODED in the scripts (per S2/S3 plan-review). Revisit only if a second project demonstrates a different cadence:

- `STALE_DAYS_BUG = 90` (in `detect_stale.py`) — bug-track staleness
- `ORPHAN_DAYS = 180` (in `detect_stale.py`) — no-refs staleness
- `MIN_CLUSTER_SIZE = 3` (in `cluster_by_category.py`) — synthesis trigger

## Action Semantics

- **Keep:** no change. Update `last-verified` to today.
- **Update:** edit body to fix drifted details; bump `last-verified`.
- **Replace:** new doc, old doc gets `status: superseded` + `superseded-by`.
- **Archive:** `git mv` to `archive/`. Content unchanged. `status: archived`.
- **Synthesize:** new umbrella doc using `synthesis-template.md`; member docs add `Related:` link to umbrella; members are NOT archived.

## Failure Modes (do not do)

- ❌ Auto-mutate any file without explicit user confirmation per row
- ❌ Archive Decision-track learnings (they supersede; never archive)
- ❌ Drop user-authored INDEX sections (heading allowlist + diff prompt enforced by `generate_index.py`)
- ❌ Force-categorize learnings (uncategorized is fine; refresh prompts but doesn't require)
