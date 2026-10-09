---
name: software-engineering-craft
description: Disciplined end-to-end software engineering workflow for application code, libraries, APIs, and refactors - understand the codebase, define the smallest correct change, implement it with tests, verify with evidence, and hand off clearly. Use for feature work, bug fixes, and refactors where correctness and maintainability matter more than speed of first draft.
license: MIT
metadata:
  author: sahildark789
  version: "1.0.0"
---

# Software Engineering Craft

Write the smallest change that is correct, tested, readable, and reversible. Treat
the codebase as the primary source of truth for conventions.

## 1. Understand before editing

- Read the code path that the change touches, plus its callers and its tests.
- Find existing conventions: naming, error handling, logging, module layout, test style.
  Match them unless they are the problem being fixed.
- Check the git history of the files you will touch (`git log -p -- <file>`) for
  intent behind odd-looking code.
- State your understanding in two or three sentences before changing anything. If you
  cannot, you do not understand the change yet.

## 2. Define the change

- Write the acceptance criteria as observable behavior ("given X, the API returns 409 when Y").
- Identify the smallest diff that satisfies them. Prefer reuse of existing functions,
  modules, and libraries over new abstractions.
- Name the risks: data migrations, public API changes, performance-sensitive paths,
  concurrency, and security-sensitive input.
- If the change is large, split it into slices that each leave the system working and tested.

## 3. Implement

- Keep each commit or edit focused on one reason to change.
- Make invalid states hard to represent: use types, enums, and validation at boundaries.
- Handle errors at the layer that can do something useful with them. Do not swallow errors.
- Do not add configuration, flags, or extension points that no current caller needs.
- Leave the code cleaner in the area you touched, but do not reformat unrelated code.

## 4. Test at the right level

- Write a test that fails before the fix for every bug, then make it pass.
- Cover the boundary conditions: empty input, maximum sizes, concurrent calls, timeouts,
  and partial failure.
- Prefer deterministic tests. Inject clocks, randomness, and network clients.
- Run the project's existing test, lint, and type-check commands. Report the exact output.

## 5. Verify with evidence

Before saying the work is done, confirm each item and record how you confirmed it:

- [ ] Acceptance criteria are each demonstrated (test name or manual step).
- [ ] Existing tests still pass; no tests were skipped or deleted to get green.
- [ ] Public contracts (API shape, CLI flags, config keys, database schema) are unchanged, or the change is documented as breaking.
- [ ] Logs and errors give enough context to debug the failure without leaking secrets.
- [ ] The diff contains no debug code, commented-out code, or unrelated edits.

## 6. Hand off

Write a short summary that a reviewer can act on:

1. **What changed and why** (one paragraph).
2. **How it was verified** (commands run and results).
3. **Risks and rollback** (what could break, how to revert it).
4. **Follow-ups** (deliberately out of scope, with a reason).

## Anti-patterns

- Editing before reading the callers.
- "Fixing" a failing test by weakening its assertion.
- Broad refactors bundled into a bug fix.
- Adding a dependency for a function that is a few lines of standard-library code.
- Claiming success without running the verification commands.
