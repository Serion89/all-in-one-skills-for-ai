---
name: engineering-router
description: Routes an engineering task to the right discipline skill (software, systems, requirements, reliability, data, ML, embedded/hardware, or design review) and sets the order in which they apply. Use at the start of any engineering task whose discipline is unclear, or when a task spans several disciplines (for example, a sensor-to-dashboard product or a model-serving feature with an SLO).
license: MIT
metadata:
  author: sahildark789
  version: "1.0.0"
---

# Engineering Router

Most engineering mistakes come from applying the wrong lens: writing code before the
requirement is clear, designing a system before the interfaces are known, or tuning a
model before the data is trusted. This skill picks the lens first.

## Step 1: Classify the work

Answer these questions in one line each. They decide the discipline.

| Question | If yes, load |
|---|---|
| Is the requirement vague, conflicting, or missing acceptance criteria? | `requirements-engineering` |
| Does the work cross several subsystems, teams, or physical/software boundaries? | `systems-engineering` |
| Is it application or library code, an API, or a refactor? | `software-engineering-craft` |
| Is it about uptime, latency targets, failure modes, or on-call risk? | `reliability-engineering` |
| Does it move, transform, or store data at scale (pipelines, warehouses, schemas)? | `data-engineering` |
| Does it train, evaluate, deploy, or monitor a model? | `ml-engineering` |
| Does it run on a microcontroller, sensor, actuator, or custom board? | `embedded-systems-engineering` |
| Is a decision about to be locked in (architecture, vendor, protocol, process)? | `engineering-design-review` |

Load the matches in this default order when several apply:

1. `requirements-engineering`: fix what "done" means.
2. `systems-engineering`: split the work into subsystems and interfaces.
3. The domain skill(s): data, ML, embedded, or software.
4. `reliability-engineering`: define how it fails and how you will know.
5. `engineering-design-review`: review the decision before it is expensive to undo.

## Step 2: Confirm the goal in one sentence

Write: "We are building X for Y so that Z, and we will know it works when W is measured."
If you cannot fill in W, go back to `requirements-engineering` before doing anything else.

## Step 3: Hand off with explicit inputs

For each selected discipline, record:

- The question that discipline must answer.
- The inputs it needs (constraints, data, prior decisions).
- The output it must hand to the next discipline.

## Anti-patterns to refuse

- Jumping into implementation with no acceptance criteria.
- Loading every discipline at once. Load only what the task needs.
- Treating a cross-disciplinary risk (for example, sensor noise that breaks an ML threshold) as belonging to only one domain.
- Skipping verification because "it's a small change" in a safety-, money-, or data-critical path.
