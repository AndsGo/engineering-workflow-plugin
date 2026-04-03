# Review Checklist

Two-pass review model. CRITICAL pass runs first and blocks merge. INFORMATIONAL pass runs second and produces recommendations.

## CRITICAL Pass (Merge Blockers)

### SQL & Data Safety
- Raw SQL with string interpolation or concatenation
- Missing parameterized queries
- DROP/TRUNCATE/DELETE without WHERE
- Migration without rollback strategy
- Bulk updates without batching or limits

### Race Conditions & Concurrency
- Shared mutable state without synchronization
- Check-then-act patterns (TOCTOU)
- Missing database transactions around multi-step mutations
- Optimistic locking assumptions without retry logic
- Async operations with implicit ordering assumptions

### Security & Trust Boundaries
- User input used directly in queries, commands, or file paths
- Missing authentication or authorization checks on new endpoints
- Secrets or credentials in code or config committed to VCS
- LLM output used as trusted input (trust boundary violation)
- CORS, CSP, or security header changes without justification

### Shell / Command Injection
- User input interpolated into shell commands
- `eval()`, `exec()`, `system()` with dynamic arguments
- Template rendering with unsanitized user content

### Enum & Value Completeness
- Switch/case/match without exhaustive handling
- New enum values without updating all consumers
- API response codes added without client handling
- Feature flags without default/fallback behavior

## INFORMATIONAL Pass (Recommendations)

### Async / Sync Consistency
- Mixing sync and async patterns unnecessarily
- Missing `await` on async calls
- Callback-style in async/await codebase

### Field Safety
- Missing nil/null/undefined guards on optional fields
- Accessing nested properties without safe navigation
- Type assertions without runtime validation at system boundaries

### Dead Code & Unused Imports
- Functions/methods defined but never called
- Imports that are no longer referenced
- Commented-out code blocks (should be deleted, not commented)

### Naming & Clarity
- Boolean variables without is/has/should prefix
- Functions that don't describe their side effects
- Ambiguous names (data, info, result, tmp, val)

### Error Message Quality
- Generic error messages ("Something went wrong")
- Missing context in error messages (what failed, what was expected)
- Swallowed exceptions without logging
