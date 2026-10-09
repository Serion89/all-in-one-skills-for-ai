---
name: requirements-engineering
description: Turns vague requests into testable requirements and acceptance criteria - elicits the real need, surfaces assumptions and conflicts, writes measurable requirements, defines non-functional targets, and records scope decisions. Use when a request is ambiguous, when stakeholders disagree, or before estimating or building anything whose definition of done is unclear.
license: MIT
metadata:
  author: sahildark789
  version: "1.0.0"
---

# Requirements Engineering

A requirement is good when a tester who did not write it can say pass or fail without
asking a question. This skill exists to reach that state before design begins.

## 1. Elicit the need, not the solution

Ask, or infer from context and state as assumptions:

- **Who** uses or is affected by this, and in what situation?
- **What problem** happens today, and how often, and what does it cost?
- **Why now**, and what happens if we do nothing?
- **What does success look like** in a number that someone will check?

If the request is a solution ("add a Redis cache"), restate the need behind it
("reads of the product page take 900 ms at p95 and we need under 200 ms").

## 2. Write requirements that can fail

Use this form for each requirement:

> **[ID]** The system shall <behavior> <condition> <measure>.

Examples:

- `REQ-101` The checkout API shall return a payment result within 3 s at p95 under 500 requests per second.
- `REQ-102` The importer shall reject rows with a missing `customer_id` and report the row number.

Rules:

- One behavior per requirement. Split "and" clauses.
- Replace adjectives with measures: "fast" -> latency; "secure" -> named threats and controls; "easy" -> a task time or error rate for a stated user.
- State the condition: under what load, input, or state does it apply?
- Mark what is out of scope, explicitly.

## 3. Cover the non-functional requirements

Check each category; write "not applicable" with a reason if it does not apply:

- Performance (latency, throughput, resource limits)
- Reliability and availability (targets, recovery time, recovery point)
- Security and privacy (who may access what; data retention; regulated data)
- Accessibility and localization
- Operability (logging, metrics, alerting, runbooks, deployment)
- Compatibility (platforms, versions, public APIs that must not break)
- Cost and capacity limits

## 4. Surface conflicts and assumptions

- List every assumption with an owner and a date to confirm it.
- When two stakeholders disagree, write both positions and the decision needed, and who decides.
- Identify contradicting requirements ("real-time" plus "batch only") before they reach code.

## 5. Make acceptance criteria executable

For each user-visible requirement, write at least one scenario:

```
Given <precondition>
When <action>
Then <observable outcome>
```

Include one negative scenario (what must not happen) and one boundary scenario.

## 6. Trace and version

- Give every requirement a stable ID and link it to the tests or checks that verify it.
- Record changes with the date, the reason, and who approved them.
- Re-check requirements when scope changes; do not let them drift silently from the build.

## Output template

```
Goal (one sentence):
Users and situations:
Problem and cost today:
Success measures (numbers):
Requirements (IDs, testable):
Non-functional requirements:
Out of scope:
Assumptions (owner, due):
Open decisions (owner, due):
Acceptance scenarios:
```

## Anti-patterns

- Requirements that describe the implementation instead of the behavior.
- Acceptance criteria that only the author can judge.
- Requirements with no owner and no measure.
- Treating a stakeholder's guess as a measured fact.
