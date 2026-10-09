---
name: python-patterns
description: Idiomatic, production-grade Python - project layout, precise typing, error handling and exception chaining, resource management, safe async and concurrency, logging, subprocess and path safety, timezone-aware datetimes, and pytest-based testing. Use when writing or reviewing Python code, choosing between Python idioms, or fixing Python bugs caused by language pitfalls (mutable defaults, late binding, blocking the event loop).
license: MIT
metadata:
  author: Serion89
  version: "1.0.0"
---

# Python Patterns

Write Python that a type checker, a linter, and the next maintainer can all trust.
Prefer the standard library, explicit types, and the project's existing tools.

## 1. Project layout and tooling

- Use `pyproject.toml` as the single source of project metadata and tool config.
- Prefer a `src/<package>/` layout so tests import the installed package, not the working directory.
- Pin the Python version the project supports (`requires-python`) and test against it.
- Use the project's own toolchain (for example `uv`, `ruff`, `mypy` or `pyright`). Do not add a second formatter or linter.
- Keep import-time side effects out of modules: no network calls, file writes, or heavy computation at import.

## 2. Typing

- Annotate public functions and class attributes. Let inference handle local variables.
- Use `X | None`, not `Optional[X]`, on Python 3.10+.
- Model data with `dataclasses(frozen=True, slots=True)` for internal values and Pydantic or similar at trust boundaries (HTTP, files, env vars).
- Use `Protocol` for structural dependencies and `Literal` or `Enum` for closed sets of values.
- Do not use `Any` to silence the checker. Use `object` or a narrowed type and check with `isinstance`.
- Run the type checker in strict mode for new modules.

## 3. Pitfalls that cause real bugs

- **Mutable default arguments**: `def f(items=[])` shares one list across calls. Use `items: list[T] | None = None` and create the list inside.
- **Late binding in closures**: `[lambda: i for i in range(3)]` returns the same final `i`. Bind it: `lambda i=i: i`.
- **Truthiness checks on values that can be valid falsy**: use `if x is None` when `0`, `""`, or `[]` are legitimate.
- **Iterating and mutating the same collection**: iterate over a copy or build a new list.
- **`is` for value comparison**: use `==`. `is` is only for `None`, sentinels, and identity.
- **Naive datetimes**: use `datetime.now(timezone.utc)`. Never store a naive datetime for an instant in time.
- **String paths**: use `pathlib.Path` and join with `/`.

## 4. Errors

- Catch the specific exception you can handle. Never write a bare `except:`; `except Exception:` only at a top-level boundary that logs and re-raises or returns a controlled error.
- Chain exceptions when you translate them: `raise DomainError("...") from exc`.
- Define a small exception hierarchy for your package so callers can catch one base class.
- Do not use exceptions for normal control flow in hot paths.
- Keep `try` blocks small so you know which call raised.

## 5. Resources and iteration

- Acquire files, connections, locks, and sockets with `with` statements or `contextlib.contextmanager`.
- Use generators for large sequences; do not build a full list just to iterate once.
- Use `enumerate`, `zip(..., strict=True)`, and `dict` comprehensions instead of index arithmetic.

## 6. Async and concurrency

- Never call blocking I/O (`requests`, `time.sleep`, file-heavy work, CPU-bound loops) inside a coroutine. Use an async client, `asyncio.sleep`, or `asyncio.to_thread` for blocking calls.
- Use `asyncio.TaskGroup` (3.11+) for structured concurrency so one failure cancels siblings and no task is orphaned.
- Keep a reference to every task you create, or it may be garbage-collected mid-run.
- Handle `asyncio.CancelledError` by cleaning up and re-raising it.
- Use threads for blocking I/O and processes for CPU-bound work. The GIL serializes pure-Python CPU work across threads.

## 7. Logging, subprocess, and security

- Use `logger = logging.getLogger(__name__)` per module. Pass arguments lazily: `logger.info("loaded %s rows", n)`, not an f-string.
- Never log secrets, tokens, or full request bodies that contain personal data.
- Run subprocesses with a list of arguments and no `shell=True`. If user input reaches a command, it must never be interpolated into a shell string.
- Use `secrets` (not `random`) for tokens and identifiers that must be unguessable.
- Validate external input at the boundary; treat deserialization of untrusted data with `pickle` as code execution and refuse it.

## 8. Testing

- Use `pytest`. Write small, focused tests with descriptive names and `@pytest.mark.parametrize` for input tables.
- Use fixtures for setup and `tmp_path` for files. Do not write to the repo from tests.
- Inject clocks and random sources rather than patching `datetime` globally.
- Mock at the system boundary (HTTP client, database driver), not internal functions, so tests survive refactors.

## Anti-patterns

- `from module import *` in library code.
- Catching and discarding exceptions with `pass`.
- Nested comprehensions that take longer to read than the equivalent loop.
- Global mutable state used as a cache without a size bound or lock.
- Type comments and `# type: ignore` with no reason attached.
