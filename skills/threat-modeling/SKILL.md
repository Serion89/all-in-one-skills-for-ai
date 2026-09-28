---
name: threat-modeling
description: STRIDE-A architectural threat modeling and attack surface analysis. Use when evaluating system designs, mapping trust boundaries, identifying privilege escalation risks, and validating defense-in-depth mitigations.
---

# Threat Modeling & Architectural Attack Surface Analysis

## Purpose
Apply structured threat modeling (STRIDE-A) to evaluate system designs, isolate trust boundaries, discover architectural vulnerabilities, and establish defense-in-depth controls before writing implementation code.

---

## The STRIDE-A Methodology

Evaluate every data flow, component interface, and storage tier against the 6 core threat classes:

| Threat Class | Security Property at Risk | Common Architectural Failure | Defensive Countermeasure |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Authenticity | Missing identity verification, trusting client headers | Mutual TLS, signed JWTs with strict algorithm pinning, asymmetric session verification. |
| **Tampering** | Integrity | Unsigned payload modification, SQL/NoSQL parameter injection | Parameterized queries, HMAC/cryptographic signatures, input sanitization at boundaries. |
| **Repudiation** | Non-repudiation | Unlogged sensitive actions, mutable application logs | Immutable audit logs, structured event schemas, append-only storage with tamper-evident hashes. |
| **Information Disclosure** | Confidentiality | PII leaks in stack traces, unencrypted network transit, verbose errors | End-to-end TLS 1.3, field-level encryption, generic client error messages, zero-PII logging policies. |
| **Denial of Service** | Availability | Unbounded resource queries, missing request timeouts, memory exhaustion | Leaky-bucket rate limiting, query pagination ceilings, strict connection pools, timeouts at every hop. |
| **Elevation of Privilege** | Authorization | Broken object-level authorization (BOLA), client-side role checks | Centralized RBAC/ABAC policy engine, contextual token verification, least-privilege service accounts. |

---

## 4-Step Threat Modeling Workflow

### 1. Data Flow & Trust Boundary Mapping
- Identify all actors: End users, internal microservices, third-party webhooks, background workers.
- Draw explicit trust boundaries where data crosses authentication domains (e.g. Public Internet -> Ingress Controller -> Private VPC -> Storage).
- Flag any unauthenticated transport crossing trust boundaries.

### 2. Threat Enumeration per Element
- For every entry point, trace incoming payload validation.
- Audit authentication: Are tokens verified cryptographically at the component boundary, or blindly trusted from upstream?
- Audit authorization: Does the handler verify that the requesting user owns the targeted resource ID (preventing BOLA/IDOR)?

### 3. Risk Scoring (DREAD Heuristic)
Rate identified threats from 1-10 across 5 dimensions:
- **Damage Potential**: What is the impact if exploited?
- **Reproducibility**: How easy is it to repeat the failure?
- **Exploitability**: Does it require authenticated access or elevated privilege?
- **Affected Users**: What percentage of users are impacted?
- **Discoverability**: How visible is the boundary defect in public interfaces?

### 4. Mitigation Specification
- For every High/Critical threat, document an explicit mitigation requirement before approving architectural blueprints.
- Add regression test criteria to `task_plan.md` to prove the defensive guardrail holds under automated tests.
