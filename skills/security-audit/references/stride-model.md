# STRIDE Threat Model Reference

STRIDE is a threat classification framework developed by Microsoft. Apply it at each **trust boundary** in the system — where data crosses between components with different trust levels.

## The Six Threats

### S — Spoofing

**Question:** Can an attacker impersonate a legitimate entity?

| Boundary | Spoofing Risk | Mitigation |
|----------|--------------|------------|
| User → Frontend | Stolen credentials, session hijacking | MFA, secure session management, token rotation |
| Frontend → Backend | Forged API requests, token replay | JWT validation, CSRF tokens, origin checking |
| Service → Service | Impersonated internal service | Mutual TLS, service mesh auth, API keys |
| External → System | Fake webhooks, spoofed callbacks | Signature verification, IP allowlisting |

### T — Tampering

**Question:** Can data be modified without detection?

| Boundary | Tampering Risk | Mitigation |
|----------|---------------|------------|
| Client → Server | Modified request parameters, replayed requests | Input validation, request signing, idempotency keys |
| Network transit | Man-in-the-middle modification | TLS, certificate pinning |
| Data at rest | Database modification, config tampering | Integrity checksums, audit logs, immutable storage |
| Build pipeline | Compromised dependencies, modified artifacts | Dependency pinning, signed builds, SBOM |

### R — Repudiation

**Question:** Can someone deny they performed an action?

| Boundary | Repudiation Risk | Mitigation |
|----------|-----------------|------------|
| User actions | "I didn't do that" for critical operations | Audit logging with user identity, timestamps |
| Admin operations | Untracked configuration changes | Change management logs, git history for config |
| API calls | Disputed transactions or data changes | Request logging, non-repudiation tokens |

### I — Information Disclosure

**Question:** Can sensitive data leak through this boundary?

| Boundary | Disclosure Risk | Mitigation |
|----------|----------------|------------|
| Server → Client | PII in error messages, stack traces in responses | Generic error messages, error ID for correlation |
| Logs | Passwords, tokens, PII in log output | Structured logging with sensitive field filtering |
| Database → App | Over-fetching sensitive columns | Column-level access control, projection queries |
| Backup/Export | Unencrypted exports containing sensitive data | Encryption at rest, access controls on exports |

### D — Denial of Service

**Question:** Can this boundary be overwhelmed or blocked?

| Boundary | DoS Risk | Mitigation |
|----------|---------|------------|
| Internet → App | Volume attacks, resource exhaustion | Rate limiting, CDN, autoscaling |
| App → Database | Expensive queries, connection exhaustion | Query timeouts, connection pooling, query complexity limits |
| App → External API | Cascading failures from downstream outages | Circuit breakers, timeouts, fallbacks |
| User → Feature | Abuse of expensive operations (file upload, report generation) | Per-user rate limiting, queue-based processing |

### E — Elevation of Privilege

**Question:** Can a lower-privilege user gain higher access?

| Boundary | EoP Risk | Mitigation |
|----------|---------|------------|
| User role → Admin | Missing role checks on admin endpoints | Role-based access control at every endpoint |
| API scope → Full access | Overly broad OAuth scopes, token permissions | Least privilege, scoped tokens |
| Container → Host | Container escape, privilege escalation | Non-root containers, seccomp profiles, read-only filesystem |
| Application → OS | Code execution through injection | Input sanitization, sandboxing, principle of least privilege |

## How to Apply

### Step 1: Draw the boundaries

Identify all trust boundaries in the system. Common boundaries:

```
User Browser ←→ CDN/Load Balancer ←→ Web Server ←→ App Server ←→ Database
                                                  ←→ Cache
                                                  ←→ External APIs
                                                  ←→ Message Queue ←→ Worker
```

### Step 2: STRIDE each boundary

For each boundary, ask all six STRIDE questions. Mark each as:
- **✓ Mitigated** — protection exists and is verified
- **⚠ Partial** — some protection but gaps remain
- **✗ Unmitigated** — no protection or protection is bypassable

### Step 3: Prioritize

Not all threats are equal. Prioritize by:
1. **Likelihood** — how easy is it to exploit?
2. **Impact** — what's the damage if exploited?
3. **Existing mitigations** — how much work to fix?

### Output Matrix

```markdown
| Boundary | S | T | R | I | D | E | Notes |
|----------|---|---|---|---|---|---|-------|
| User → API | ✓ | ✓ | ⚠ | ✓ | ⚠ | ✓ | Rate limiting needed |
| API → DB | ✓ | ✓ | ✗ | ✓ | ⚠ | ✓ | No audit logging on writes |
```
