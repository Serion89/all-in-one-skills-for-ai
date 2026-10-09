---
name: flaky-test-triage
description: Find, classify, and fix flaky tests - tests that pass and fail on the same code. Covers measuring failure rates, bisecting order-dependent failures, and fixing the usual causes (timing and sleeps, shared state, time and randomness, external services, async mistakes, port and file collisions). Use when CI is intermittently red, when a test fails only in CI or only in a particular order, or when deciding whether to quarantine a test.
license: MIT
metadata:
  author: Serion89
  version: "1.0.0"
---

# Flaky Test Triage

A flaky test is worse than no test: it trains people to ignore red builds. Treat each
flake as a bug in either the test or the code under test, and fix the cause.

## 1. Measure before reacting

- Gather evidence: CI history for the test, failure messages, the commit, the runner, and the time of day.
- Re-run the test in isolation many times, for example 50 to 100 runs, and record the failure rate:

```bash
# pytest
pytest path/to/test.py::test_name --count=100 -x   # with pytest-repeat
# jest / vitest
npx vitest run path/to/test.ts --repeat 100        # or a loop in CI
```

- If it never fails in isolation, the cause is almost certainly shared state or order. Go to step 3.
- If it fails in isolation, the cause is inside the test or the code under test. Go to step 2.

## 2. Classify the cause

| Signature | Usual cause |
|---|---|
| Fails only on slow or loaded machines | Fixed `sleep` or a short timeout |
| Fails near midnight, month end, or DST | Wall-clock time or time zone |
| Different result each run, no pattern | Unseeded randomness or unordered iteration (set, dict, map order) |
| Fails only in CI | Environment: locale, time zone, CPU count, missing env var, network |
| Connection refused or address in use | Fixed ports or shared external services |
| Passes locally, fails when run with others | Order-dependent shared state |
| Assertion sees old data | Missing `await`, unawaited promise, or eventual consistency |
| File exists or not, sporadically | Shared temp path or cleanup races |

## 3. Bisect order-dependent failures

- Run the suite in random order with a recorded seed (`pytest -p randomly`, `jest --randomize`, `vitest --sequence.shuffle`). Save the seed of each failing run.
- Narrow down the culprit: run the failing test after each earlier test, or bisect the list of preceding tests until one prior test makes it fail.
- The culprit usually mutates a global, a singleton, a database row, a file, an environment variable, or a module-level cache.

## 4. Fix the cause

- **Replace sleeps with conditions**: poll for the state you need with a deadline, or await the event. A sleep is a guess about timing.
- **Inject time**: pass a clock into the code and control it in the test instead of reading the real clock.
- **Seed randomness** and sort collections before comparing them when order is not part of the contract.
- **Isolate state**: give each test its own database schema or transaction, its own temp directory, and free ports (port 0). Restore globals and environment variables in teardown.
- **Fake external services at the boundary** with a local stub or recorded responses. Keep a small number of contract tests against the real service, marked and run separately.
- **Await everything**: enable lint rules for floating promises and missing `await`.
- **Fix the product code** when the test found a real race. A flaky test sometimes reveals a bug in production code, so do not assume the test is at fault.

## 5. Quarantine only with a plan

If a fix cannot land immediately, quarantine the test rather than letting it block the pipeline. Quarantine means:

- Mark it explicitly (for example, a named tag or a dedicated suite) with an owner and a link to a tracking issue.
- Keep it running in a non-blocking job so you still see its failure rate.
- Set a deadline; a quarantined test with no deadline is a deleted test.

Never disable, skip, or delete a test silently to get green, and never retry in CI until it passes without fixing the cause.

## 6. Verify the fix

- Re-run the measurement from step 1 with the same count. The failure rate should be zero over the same number of runs.
- Run the suite in random order several times with different seeds.
- Run the test under CI conditions (same container, same parallelism) before closing the issue.

## Checklist

- [ ] Failure rate measured and recorded with the run count.
- [ ] Cause classified, not guessed.
- [ ] No fixed sleeps or real-clock reads left in the test.
- [ ] Shared state is isolated and restored in teardown.
- [ ] Verified over the same number of runs with random order.

## Anti-patterns

- Retrying the job until it passes and calling the build green.
- Increasing a timeout from 1 s to 30 s without knowing what it waits for.
- Adding `@skip` or `.only` left in the code.
- Fixing the test by weakening its assertion.
