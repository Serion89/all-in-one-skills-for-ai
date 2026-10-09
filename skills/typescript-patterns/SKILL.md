---
name: typescript-patterns
description: Idiomatic, type-safe TypeScript and Node.js - strict compiler settings, narrowing instead of casting, discriminated unions and exhaustive checks, validation at trust boundaries, async error handling and cancellation, ESM and environment configuration, and graceful shutdown. Use when writing or reviewing TypeScript or Node code outside a specific framework, or when a bug comes from a type hole, an unhandled promise, or a misconfigured runtime.
license: MIT
metadata:
  author: Serion89
  version: "1.0.0"
---

# TypeScript Patterns

The compiler can only protect you from what the types describe. Make the types describe
the real data, validate what crosses into the program, and let unhandled cases fail loudly.

## 1. Compiler configuration

- Enable `strict`. Also consider `noUncheckedIndexedAccess`, `noImplicitOverride`, and `exactOptionalPropertyTypes` for new projects.
- Set `"verbatimModuleSyntax": true` (or `isolatedModules`) and import types with `import type`.
- Keep `tsc --noEmit` in CI so type errors fail the build even when the bundler is lenient.
- Do not disable a rule file-wide to fix one line. Narrow the suppression to the line and explain it.

## 2. Types that describe reality

- Use `unknown` for values you have not checked, never `any`. Narrow `unknown` with type guards or a schema library.
- Prefer discriminated unions over optional fields that only make sense together:

```ts
type Payment =
  | { status: "pending" }
  | { status: "captured"; capturedAt: Date }
  | { status: "failed"; reason: string };
```

- Require exhaustive handling: add a `default` branch that assigns the value to `never` so a new variant is a compile error.
- Use `readonly` for data that should not change, and `as const` for literal tables.
- Prefer string-literal unions or `const` objects over `enum`; they erase cleanly and interoperate better with plain JSON.
- Avoid `as` casts. A cast tells the compiler to trust you; a type guard proves it.

## 3. Validate at trust boundaries

- Every value from HTTP, a queue, a file, `process.env`, or `JSON.parse` starts as `unknown`.
- Parse it with a schema (for example `zod`) and use the parsed output type everywhere else.
- Validate environment variables once at startup and fail fast with a message naming the missing key.
- Never trust a type from another service's generated client without checking that its runtime version matches.

## 4. Async correctness

- Every promise must be awaited, returned, or explicitly handled. A floating promise hides failures.
- In `forEach`, `async` callbacks are not awaited. Use `for...of` with `await`, or `Promise.all(items.map(...))`.
- Choose the combinator on purpose: `Promise.all` fails fast; `Promise.allSettled` reports every outcome.
- Add timeouts and cancellation with `AbortController`, and pass the signal through to `fetch` and other APIs that accept it.
- Limit concurrency for large batches; an unbounded `Promise.all` over 10,000 items can exhaust sockets.
- Do not `await` inside a loop when the iterations are independent; collect the promises and await them together.

## 5. Errors

- Throw `Error` objects (or subclasses), never strings or plain objects.
- Use `new Error("context", { cause: err })` when translating errors so the original stack survives.
- Type caught errors as `unknown` and narrow them: `if (err instanceof Error)`.
- Catch at boundaries that can act (request handler, job runner, process entry point), not in every function.

## 6. Node.js runtime

- Decide ESM or CommonJS per package with `"type"` in `package.json`; do not mix them casually.
- Read configuration in one module that validates and exports typed values.
- Handle `SIGTERM` and `SIGINT`: stop accepting new work, finish in-flight requests within a deadline, close connections, then exit.
- Log unhandled rejections and uncaught exceptions, then exit. Do not continue with unknown state.
- Use `node:`-prefixed built-in imports (`node:fs/promises`) to make them explicit.
- Use `structuredClone` for deep copies instead of `JSON.parse(JSON.stringify(x))`, which drops `Date`, `undefined`, and `Map`.

## 7. Common correctness traps

- Compare with `===`. Only use `== null` deliberately, to match both `null` and `undefined`.
- `Array.prototype.sort` mutates in place; copy first with `[...arr].sort(...)` or `toSorted`.
- Date-only strings like `"2026-10-09"` parse as UTC, but `new Date(y, m, d)` uses local time. Pick one and state it.
- Floating-point money: store integer minor units (cents) and format at the edge.
- `parseInt` needs a radix; prefer `Number()` with a check for `NaN`.

## 8. Testing

- Use the project's runner (Vitest or Jest). Test behavior through public functions, not private helpers.
- Type-test important types with `expectTypeOf` or a `tsd`-style check so refactors cannot silently weaken them.
- Inject time and I/O clients. Use fake timers for debounce and retry logic.

## Anti-patterns

- `as any` or `// @ts-ignore` to make an error disappear.
- Optional properties that are sometimes required, modeled as one interface with `?` everywhere.
- Business logic in a catch-all `try` that swallows the failure.
- Barrel files (`index.ts` re-exporting everything) that pull large dependency trees into small bundles.
