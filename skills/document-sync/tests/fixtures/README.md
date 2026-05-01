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
