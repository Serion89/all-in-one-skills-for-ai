---
name: reliability-engineering
description: Reliability engineering for software and physical systems - define SLIs and SLOs, run failure mode and effects analysis (FMEA), design for graceful degradation, plan error budgets and alerting, and verify resilience with targeted fault tests. Use when setting reliability targets, reviewing a design for single points of failure, or preparing a system for production or safety-relevant use.
license: MIT
metadata:
  author: sahildark789
  version: "1.0.0"
---

# Reliability Engineering

Reliability is a measured property, not a feeling. Start by defining what "working"
means, then find the ways the system stops working, then decide which ones to design out.

## 1. Define service levels

- **SLI**: a measurable indicator of a user-visible behavior (for example, the fraction
  of requests that return a non-error response in under 300 ms).
- **SLO**: the target for that SLI over a window (for example, 99.9% over 28 days).
- **Error budget**: `1 - SLO`. Spend it deliberately on releases and experiments.
- Choose SLIs from the user's journey, not from internal metrics alone. Good SLIs
  cover availability, latency, correctness, and freshness.

## 2. Run a failure mode analysis

For each component or interface, record:

| Component | Failure mode | Effect on user | Detection | Severity (1-10) | Likelihood (1-10) | Mitigation | Residual risk |
|---|---|---|---|---|---|---|---|
| Payment API | Timeout to provider | Checkout hangs | p99 alert | 8 | 5 | Timeout + retry with idempotency key | Medium |

Rank by Risk Priority Number (severity x likelihood x detectability gap). Fix the top
items first, and record the decision for the rest.

## 3. Find single points of failure

Ask of each dependency:

- What happens if it is slow, not just down? Slow is usually worse.
- Is there a timeout, and is the timeout shorter than the caller's own timeout?
- Are retries bounded, jittered, and applied only to idempotent operations?
- Does a failure in a shared resource (connection pool, queue, cache, DNS, clock) stop
  unrelated features?

## 4. Design the degradation path

- Define what the system does with partial capability: serve stale data, disable a
  non-critical feature, queue work for later, or fail closed for safety-critical actions.
- Choose fail-open or fail-closed per function, and write down why.
- Use bulkheads and load shedding so one overloaded tenant or path cannot starve others.
- For physical systems, define the safe state and how the system reaches it on power loss,
  sensor loss, or communication loss.

## 5. Alert on symptoms and budgets

- Page on user-impacting symptoms and on fast error-budget burn, not on every cause.
- Each alert links to a runbook with: what it means, how to confirm, and the first action.
- Remove alerts that nobody acts on.

## 6. Verify resilience with planned faults

- Test each failure mode from the FMEA: kill a dependency, add latency, drop packets,
  fill a disk, expire a credential, skew a clock.
- Run in staging or a controlled production window with a stop condition written in advance.
- Record the observed behavior next to the expected behavior. Any gap becomes a ticket.

## 7. Review after failure

- Write a blameless review: timeline, impact, contributing factors, what detected it,
  and corrective actions with owners.
- Feed each contributing factor back into the FMEA.

## Checklist before launch

- [ ] SLIs and SLOs are written down and measured.
- [ ] Every external call has a timeout, a bounded retry policy, and an idempotency story.
- [ ] Top FMEA risks have mitigations and tests.
- [ ] Degradation behavior is defined per feature.
- [ ] Alerts map to runbooks; an on-call person can act on them.
- [ ] Rollback is tested, and a rollback plan exists for data migrations.

## Anti-patterns

- Setting a 99.999% target with no measurement behind it.
- Retrying a non-idempotent write and creating duplicates.
- Treating "the dependency is up" as proof that it is healthy.
- Alerting on CPU percentage with no link to user impact.
