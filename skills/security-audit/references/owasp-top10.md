# OWASP Top 10 (2021) Quick Reference

Checklist for code-level security auditing. For each category, list common vulnerability patterns and what to search for.

## A01: Broken Access Control

**What breaks:** Users acting outside their intended permissions.

| Pattern | Search for |
|---------|-----------|
| Missing auth check on endpoint | New routes/controllers without auth middleware |
| IDOR | Database queries using user-supplied ID without ownership check |
| Path traversal | User input in file paths without normalization |
| CORS misconfiguration | `Access-Control-Allow-Origin: *` |
| Missing function-level access | Admin endpoints accessible to regular users |
| Metadata manipulation | JWT claims or hidden form fields used for authorization |

## A02: Cryptographic Failures

**What breaks:** Sensitive data exposed through weak or missing encryption.

| Pattern | Search for |
|---------|-----------|
| Plaintext passwords | `password` stored without hashing |
| Weak hash algorithms | `MD5`, `SHA1` for passwords (HMAC use is acceptable) |
| Missing encryption at rest | PII, credentials in plaintext database columns |
| Hardcoded keys/IVs | Encryption keys in source code |
| Weak random | `Math.random()`, `rand()` for security-critical values |

## A03: Injection

**What breaks:** Untrusted data sent to an interpreter as part of a command/query.

| Pattern | Search for |
|---------|-----------|
| SQL injection | String concatenation/interpolation in SQL queries |
| Command injection | User input in `system()`, `exec()`, `spawn()` |
| NoSQL injection | User input in MongoDB query objects |
| LDAP injection | User input in LDAP filters |
| Expression injection | User input in template engines, `eval()` |

## A04: Insecure Design

**What breaks:** Missing or ineffective security controls at the design level.

| Pattern | Search for |
|---------|-----------|
| Missing rate limiting | Auth endpoints without throttling |
| No account lockout | Unlimited login attempts |
| Missing CAPTCHA | Bot-sensitive operations without verification |
| Trust boundary violations | Client-side validation as only validation |

## A05: Security Misconfiguration

**What breaks:** Insecure default configuration, incomplete setup, open cloud storage.

| Pattern | Search for |
|---------|-----------|
| Debug mode in production | `DEBUG=True`, `NODE_ENV=development` |
| Default credentials | Unchanged admin passwords, default API keys |
| Verbose errors | Stack traces in HTTP responses |
| Unnecessary features | Unused endpoints, admin panels, sample data |
| Missing security headers | No CSP, HSTS, X-Frame-Options |

## A06: Vulnerable and Outdated Components

**What breaks:** Using components with known vulnerabilities.

| Pattern | Search for |
|---------|-----------|
| Outdated dependencies | `npm audit`, `pip audit`, `bundle audit` |
| Unmaintained packages | No updates in 2+ years with known issues |
| Pinned vulnerable versions | Lock files with known CVEs |

## A07: Identification and Authentication Failures

**What breaks:** Attacks related to user identity, authentication, session management.

| Pattern | Search for |
|---------|-----------|
| Weak passwords allowed | No complexity requirements |
| Missing MFA | High-privilege operations without second factor |
| Session fixation | Session ID not rotated after login |
| Token in URL | Session tokens in query parameters |
| Credential stuffing | No detection of automated login attempts |

## A08: Software and Data Integrity Failures

**What breaks:** Code and infrastructure not protected against integrity violations.

| Pattern | Search for |
|---------|-----------|
| Unsigned updates | Auto-update without signature verification |
| Unsafe deserialization | `pickle.loads()`, `JSON.parse()` of untrusted data into typed objects |
| CI/CD tampering | Build pipelines without integrity checks |

## A09: Security Logging and Monitoring Failures

**What breaks:** Breaches not detected, investigated, or responded to.

| Pattern | Search for |
|---------|-----------|
| Missing auth logging | Login attempts not logged |
| No alerting | Failed logins, permission denials without alerts |
| Sensitive data in logs | Passwords, tokens, PII in log output |
| Missing audit trail | Critical operations without who/what/when records |

## A10: Server-Side Request Forgery (SSRF)

**What breaks:** Server makes requests to attacker-controlled destinations.

| Pattern | Search for |
|---------|-----------|
| User-controlled URLs | `fetch(userInput)`, `requests.get(userInput)` |
| Redirect following | HTTP client follows redirects to internal services |
| Cloud metadata | Access to `169.254.169.254` not blocked |
