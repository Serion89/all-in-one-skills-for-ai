---
name: engineering-design-review
description: Structured, discipline-neutral review of an engineering design or significant decision before it is locked in - checks the problem statement, options and trade-offs, failure modes, operability, security, cost, reversibility, and open questions, then produces a findings list with severities and a go/no-go recommendation. Use when reviewing a design doc, RFC, ADR, architecture proposal, or hardware/system design before implementation.
license: MIT
metadata:
  author: sahildark789
  version: "1.0.0"
---

# Engineering Design Review

A design review exists to find the expensive mistakes while they are still cheap to fix.
Review the reasoning, not only the diagrams. A good design states what it does not do.

## 1. Check the problem statement

- Is the problem stated without the solution inside it?
- Are the success measures numeric, and do they match the requirements?
- Is the scope explicit, including what is deliberately excluded?

If the problem is not clear, stop the review and send the design back.

## 2. Check the options

- Are at least two real alternatives considered, including "do nothing" or the simplest option?
- Is each rejected option rejected for a stated reason tied to a criterion?
- Are the criteria weighted, or at least ranked, and agreed before the choice was made?

## 3. Check the design itself

- Can a reader trace each requirement to a component or decision?
- Are the interfaces and data formats defined with units, versions, and error behavior?
- Does any component have a hidden dependency (shared database, global state, single host, single vendor)?
- Is complexity justified? Ask what breaks if a proposed element is removed.

## 4. Check failure, operability, and security

- What happens on each important failure: timeout, partial write, duplicate message, lost sensor, full disk?
- How is it deployed, rolled back, monitored, and debugged by someone who did not design it?
- What data flows in and out, what is sensitive, and how is access controlled and audited?
- What are the trust boundaries, and where is input validated?

## 5. Check cost, schedule, and reversibility

- What does it cost to build, run, and maintain? Is the estimate sourced or a guess?
- Which decisions are one-way (public API, schema, vendor contract, physical layout)?
  Those deserve more scrutiny than reversible ones.
- Is there a migration or exit path if the choice turns out to be wrong?

## 6. Record findings with severity

Use these levels:

- **Blocker**: will cause a safety, security, data-loss, or major correctness problem if built as written.
- **Major**: likely to cause significant rework, outage, or cost overrun.
- **Minor**: clarity, naming, or completeness issues that do not change the decision.
- **Question**: information the author must provide before a decision can be made.

Each finding states: the location in the design, what is wrong, why it matters, and a suggested change.

## 7. Give a recommendation

- **Go**: no blockers; majors have owners and plans.
- **Go with conditions**: list the conditions and who verifies them, and by when.
- **Revise and re-review**: blockers or unanswered questions that change the decision.

## Output template

```
Design: <title> (version, date, reviewer)
Summary of the proposal (3 sentences):
Recommendation: Go | Go with conditions | Revise and re-review

Findings:
1. [Blocker|Major|Minor|Question] <location> - <issue>. Why: <impact>. Suggested: <change>.

What is good (keep these):
Open questions for the author:
Decisions that are hard to reverse:
```

## Anti-patterns

- Reviewing only the diagrams and ignoring the stated trade-offs.
- Approving a design whose failure behavior is "it should be fine".
- Blocking on style when the design has an unexamined one-way decision.
- Accepting an option list where every option except the favorite is a straw man.
