---
name: data-engineering
description: Data engineering for pipelines, warehouses, and data stores - design idempotent and replayable ingestion, define schemas and data contracts, add data quality checks and lineage, handle late and duplicate data, and plan backfills safely. Use when building or changing ETL/ELT jobs, streaming consumers, batch loads, or analytical tables where wrong data is worse than late data.
license: MIT
metadata:
  author: sahildark789
  version: "1.0.0"
---

# Data Engineering

Data pipelines fail quietly. A job that succeeds with wrong numbers is more dangerous
than one that fails loudly. Design for correctness, replay, and visibility first.

## 1. Define the data product

- Who consumes this data, and what decisions depend on it?
- What is the grain of each table (one row per what?), and what is the freshness requirement?
- What is the acceptable error, and what is the cost of a late or missing record?

## 2. Set data contracts

For each source and each output, write down:

- Schema with types, nullability, units, and time zone for every timestamp.
- Keys: primary key, natural key, and what makes a record unique.
- Expected volume and freshness, with alert thresholds.
- Ownership: who to contact when the contract breaks.
- Compatibility rule: additive changes allowed; renames and type changes require a new version.

## 3. Make ingestion idempotent

- Running a job twice must produce the same result as running it once.
- Use deterministic keys and `MERGE`/upsert semantics rather than blind appends, or
  write to a new partition and swap atomically.
- Store the source offset, watermark, or file manifest with the output so reruns resume correctly.
- Keep raw data immutable so transformations can be rebuilt.

## 4. Handle time correctly

- Store event time and processing time separately.
- Define the lateness window explicitly and decide what happens to records that arrive after it
  (accept and restate, or route to a late-data table).
- Partition by the date the business cares about, and state the time zone.

## 5. Add data quality checks

Run checks at ingestion and before publishing each table:

- **Completeness**: row counts within expected bounds; no empty partitions.
- **Uniqueness**: no duplicate keys in the grain.
- **Validity**: values within domain rules (non-negative amounts, valid enums).
- **Referential integrity**: foreign keys resolve, or orphans are counted and reported.
- **Freshness**: the latest record is within the agreed lag.
- **Reconciliation**: totals match the source system within a stated tolerance.

Failing checks should block publication of the affected table, not just log a warning.

## 6. Plan backfills and schema changes

- Backfill in bounded windows with checkpoints; never one unbounded query.
- Run the new logic side by side with the old, compare outputs, and only then switch.
- For schema migrations, use expand -> migrate -> contract: add the new column, dual-write
  or backfill, switch readers, then remove the old column in a later release.

## 7. Document lineage and ownership

- Record which upstream sources feed each output and what transformations they pass through.
- Mark PII and sensitive fields; apply masking or access control at the table level.
- Keep retention rules explicit, and delete data when its retention period ends.

## Checklist

- [ ] Grain and primary key are documented and tested for uniqueness.
- [ ] Job is idempotent: a rerun on the same input produces identical output.
- [ ] Time zones and event-time semantics are explicit.
- [ ] Quality checks gate publication.
- [ ] Backfill plan exists with checkpoints and a reconciliation step.
- [ ] Lineage, owner, and retention are recorded.

## Anti-patterns

- Appending on every run and then deduplicating in a dashboard query.
- Silent type coercion (strings to numbers with `NULL` on failure) with no count of rejected rows.
- Joining on non-unique keys and inflating totals.
- Changing a metric's definition without versioning it.
