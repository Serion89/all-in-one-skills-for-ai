---
name: api-security-testing
description: Defensive API security posture verification against the OWASP API Security Top 10. Use when auditing REST and GraphQL endpoints for authorization boundaries (BOLA/BFLA), token validation, CORS configurations, rate-limiting, and input sanitization.
---

# API Security Posture Verification (OWASP API Top 10)

## Purpose
Systematically inspect, audit, and harden web APIs against the OWASP API Security Top 10 vulnerabilities through automated code inspection, contract auditing, and defensive test assertions.

---

## Defensive Verification Matrix

| Vulnerability | Attack Vector | Defensive Verification Checklist |
| :--- | :--- | :--- |
| **API1: BOLA (Broken Object Level Authorization)** | Accessing `/api/users/456/profile` while authenticated as user `123`. | Verify that database queries filter by both `id` AND the authenticated `user_id` from the session token: `WHERE id = :targetId AND owner_id = :authenticatedUserId`. |
| **API2: Broken Authentication** | Replaying expired JWTs, missing signature verification, weak secret keys. | Ensure asymmetric validation (RS256/ES256), strict token expiration (`exp` claim), and rejection of tokens with `alg: "none"`. |
| **API3: Broken Object Property Level Authorization** | Mass assignment: sending `{ isAdmin: true }` in user profile update payload. | Enforce strict input DTO schemas (Pydantic / Zod / class-validator) with explicitly allowed fields. Strip unknown properties. |
| **API4: Unrestricted Resource Consumption** | Sending massive batch requests or unindexed filters causing OOM crashes. | Enforce pagination ceilings (e.g. `limit` capped at 100), request payload size limits, and per-client rate limiting. |
| **API5: BFLA (Broken Function Level Authorization)** | Standard user calling `/api/admin/system/restart`. | Enforce role checks in middleware before executing controller handlers. Test that non-admin requests receive HTTP 403 Forbidden. |
| **API6: Unrestricted Access to Sensitive Business Flows** | Scalping or automated credential abuse on checkout/login routes. | Implement anti-automation mechanisms: captcha verification on high-value routes, exponential backoff on auth failures. |
| **API7: Server-Side Request Forgery (SSRF)** | Supplying `http://169.254.169.254/latest/meta-data` to an image URL parser. | Parse and validate target URLs against an explicit domain allowlist. Block loopback (`127.0.0.1`), private IP ranges (RFC 1918), and link-local addresses. |
| **API8: Security Misconfiguration** | Verbose error stack traces in production, unhardened CORS headers (`Access-Control-Allow-Origin: *` with credentials). | Return sanitized error codes. Restrict CORS origins to trusted domain lists. Enforce `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`. |
| **API9: Improper Inventory Management** | Exposed unauthenticated `/v1` APIs running alongside `/v2` without updated security patches. | Maintain automated OpenAPI / Swagger documentation pipelines; decommission legacy endpoints with redirect or deprecation notices. |
| **API10: Unsafe Consumption of APIs** | Blindly trusting responses from integrated third-party webhooks without validation. | Validate all incoming webhook payloads using shared HMAC secrets (`X-Hub-Signature`), strict schema validation, and safe XML/JSON parsing. |

---

## Automated Verification Protocol

```bash
# 1. Inspect endpoint route guards
# Verify every mutation route has an explicit authentication and authorization middleware attached.

# 2. Check schema validation
# Verify no route accepts raw unvalidated Request bodies.

# 3. Audit CORS and security headers
curl -I -X OPTIONS http://localhost:8080/api/v1/resource -H "Origin: https://untrusted-site.com"
# Expected: Untrusted origins should NOT receive Access-Control-Allow-Origin reflections.
```
