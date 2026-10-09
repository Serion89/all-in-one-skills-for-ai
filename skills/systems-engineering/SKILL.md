---
name: systems-engineering
description: Systems engineering method for work that spans multiple subsystems, teams, or physical and software boundaries - decompose the system, define interfaces and budgets, trace requirements to verification, run trade studies, and manage integration risk. Use for system architecture across hardware and software, platform-level changes, and any project where an interface mismatch would be expensive to discover late.
license: MIT
metadata:
  author: sahildark789
  version: "1.0.0"
---

# Systems Engineering

Systems engineering keeps the whole system coherent while the parts are built by
different people. Its main job is to control interfaces, budgets, and traceability.

## 1. Define the system boundary

- What is inside the system, what is outside, and who or what interacts across the edge?
- List every external actor (users, other services, sensors, operators, regulators).
- Write the mission or purpose in one sentence and the top-level measures of success.

## 2. Capture and allocate requirements

- Separate **stakeholder needs** ("operators must know a fault within 5 seconds") from
  **system requirements** ("the monitor publishes fault events within 2 seconds of detection").
- Every requirement must be: singular, measurable, testable, and traceable to a need.
- Allocate each requirement to exactly one subsystem. If it spans two, split it.
- Maintain a traceability table: need -> requirement -> subsystem -> verification method.

## 3. Define interfaces first

For each interface between subsystems, write a contract:

| Field | Example |
|---|---|
| Name and direction | `TelemetryStream`, producer -> consumer |
| Data or signal, with units | `temperature_c` float, 1 Hz |
| Timing | Max latency 500 ms, jitter < 50 ms |
| Failure behavior | What the consumer does on missing or stale data |
| Versioning | How breaking changes are introduced |

Interfaces are where integration failures hide. Review them with both sides present.

## 4. Budget the critical resources

Pick the resources that can be exhausted and assign each a budget that sums to the total:

- Latency end-to-end, memory, CPU, bandwidth, power, mass, cost, and error budget.
- Record the margin. A budget with no margin is a prediction of failure.

## 5. Run trade studies

When there are two or more viable designs:

1. List the criteria and weight them (agree on weights before scoring).
2. Score each option against each criterion with evidence, not opinion.
3. Record the decision, the rejected options, and what would change the decision.

## 6. Plan verification

- Choose a method per requirement: **test**, **analysis**, **inspection**, or **demonstration**.
- Verify at the lowest level that can prove the requirement (unit before integration before system).
- Plan integration in increasing scope: interface tests with simulators, then hardware or
  service-in-the-loop, then full system.

## 7. Manage risk

- Keep a risk register: description, likelihood, impact, owner, mitigation, and trigger.
- Prioritize risks that touch interfaces, unproven technology, and tight budgets.
- Re-review the register at each integration milestone.

## Deliverables

- System context diagram and boundary statement.
- Requirements table with traceability to verification.
- Interface control documents (one per interface).
- Budget table with margins.
- Trade-study record for each major decision.
- Verification plan and integration sequence.

## Anti-patterns

- Writing subsystem requirements before the system-level behavior is agreed.
- Interfaces described only in code, with no written contract.
- Requirements that say "fast", "robust", or "user-friendly" with no number.
- Budgets that were never summed.
