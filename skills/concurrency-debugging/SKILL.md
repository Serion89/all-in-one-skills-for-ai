---
name: concurrency-debugging
description: Diagnose and fix concurrency bugs - data races, check-then-act and lost updates, deadlocks and lock-ordering cycles, async reentrancy, and event-loop blocking. Use when behavior is intermittent under load, when results depend on timing, when a service hangs with threads or tasks waiting on each other, or when a fix for a race condition is being proposed.
license: MIT
metadata:
  author: Serion89
  version: "1.0.0"
---

# Concurrency Debugging

Concurrency bugs depend on timing, so they do not reproduce on demand and often vanish
when you add logging. Work from evidence, widen the timing window until the bug is
reproducible, and fix the design rather than the symptom.

## 1. Name the bug class

Classify the symptom before touching code:

| Symptom | Likely class |
|---|---|
| Two workers both act on the same item | Check-then-act (TOCTOU) |
| Counter or balance is wrong by a few updates | Lost update (read-modify-write) |
| Crash or corrupted value, rare, no lock involved | Data race on shared memory |
| Process hangs; threads or tasks waiting forever | Deadlock or missing wakeup |
| Hang that clears after a timeout | Lock held across I/O, or livelock |
| Invariant broken between two `await`s | Async reentrancy |
| All requests slow at once, CPU low | Event loop or thread pool blocked |

## 2. Find the shared state

- List every variable, row, file, cache, and singleton touched by more than one thread, task, or process.
- For each, write down who writes it, who reads it, and what lock or ordering protects it. If you cannot name one, that is the bug.
- Check for hidden shared state: module-level caches, default arguments, class attributes, and connection pools used without per-request ownership.

## 3. Reproduce deliberately

- Widen the window: insert a short `sleep` or yield at the suspected point, temporarily, to make the race frequent. Remove it before the fix.
- Stress the path: run the operation in a loop from many workers, with a barrier so they start together.
- Use tooling built for this:
  - Go: `go test -race` and `go run -race`.
  - C and C++: ThreadSanitizer (`-fsanitize=thread`).
  - Rust: `loom` for model checking small lock-free code.
  - Java: jcstress for memory-model tests; thread dumps (`jstack`) for deadlocks.
  - Python: `faulthandler.dump_traceback_later` to see where threads are stuck.
  - Node and browsers: check for unhandled rejections and inspect the event loop lag.
- For hangs, capture a thread or task dump first. It shows who is waiting for whom.

## 4. Build a timeline

- Log with a thread or task ID, a monotonic timestamp, and the operation's key ID.
- Reconstruct the interleaving that produces the bad result. Write it as a numbered sequence of steps for two actors.
- A bug you cannot explain as an interleaving is not yet understood. Keep investigating before you fix.

## 5. Fix the design, not the timing

Prefer, in order:

1. **Remove sharing**: confine state to one owner and pass messages (queue, channel, actor). Immutable data needs no lock.
2. **Make the operation atomic in the datastore**: `UPDATE ... SET x = x + 1 WHERE version = ?`, unique constraints, `SELECT ... FOR UPDATE`, or compare-and-swap.
3. **Make retries safe**: idempotency keys so a duplicate operation is detected, not repeated.
4. **Protect with a lock** only when the others are impossible. Keep it short, never hold it across network or disk I/O, and document what it guards.
5. **Enforce lock order**: if two locks are needed, always acquire them in one global order. Use `tryLock` or acquisition timeouts to detect violations.

For async code: do not hold an invariant across an `await`. Re-read shared state after each `await`, or make the update a single synchronous step.

## 6. Verify the fix

- Run the reproduction loop for enough iterations that the old code failed reliably (for example, 10,000 runs) and the new code passed every time.
- Run with the race detector or sanitizer enabled.
- Add a regression test that forces the bad interleaving deterministically, using a controlled barrier or injected delay, not a sleep.
- Check for deadlock under load with a timeout on the test, so a hang fails the test instead of blocking CI.

## Anti-patterns

- Adding `sleep` to "fix" a race. This only moves the window.
- Wrapping a racy section in `try/catch` and retrying until it works.
- Using `volatile` (Java) or plain flags as synchronization. They give visibility, not atomicity.
- Removing a lock because it "slows things down" without measuring the cost of the bug it prevents.
- Declaring a race fixed after one passing run.
