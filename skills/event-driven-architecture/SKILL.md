---
name: event-driven-architecture
description: Event-driven architecture and asynchronous messaging patterns. Use when designing distributed systems with Apache Kafka, RabbitMQ, EventBridge, implementing the Transactional Outbox pattern, idempotency keys, dead-letter queues (DLQs), and CQRS.
---

# Event-Driven Architecture & Asynchronous Messaging

## Purpose
Design resilient, decoupled, high-throughput distributed systems using asynchronous event streams and message brokers. Enforce at-least-once delivery safety, partition ordering, and eventual consistency boundaries.

---

## Core Architectural Patterns

### 1. Transactional Outbox Pattern
Never perform a database write and a message broker publish in the same application transaction without an outbox table.
- **Mechanism**: Write state changes and event payloads into an `outbox` table within the same ACID transaction. A separate relay process (or CDC connector like Debezium) tails the outbox table and publishes events to the broker.
- **Benefit**: Guarantees zero lost events even if the message broker is temporarily offline during transaction commit.

### 2. Idempotent Consumer Pattern
Assume the message broker delivers duplicate messages (at-least-once semantics).
- **Mechanism**: Every event MUST carry a unique, deterministic `event_id` or `idempotency_key`. The consumer checks a dedicated `processed_events` table before applying business logic.
- **SQL Pattern**:
  ```sql
  INSERT INTO processed_events (event_id, consumer_group, processed_at)
  VALUES (:eventId, :consumerGroup, NOW())
  ON CONFLICT (event_id, consumer_group) DO NOTHING;
  ```

### 3. Dead-Letter Queue (DLQ) & Poison Pill Handling
- **Transient Failures** (network timeouts, lock contention): Retry with exponential backoff and jitter.
- **Permanent Failures** (schema mismatch, malformed payload): After $N$ retries (typically 3-5), route the message to a Dead-Letter Queue with error context headers.
- **Never Block the Partition**: Stalled poison pill messages must not halt consumption of subsequent healthy partition messages.

---

## Schema Evolution Rules (Avro / Protobuf / JSON Schema)
1. **Backward Compatibility**: New schema versions can read records written by old schemas. Only add optional fields; never delete required fields without multi-phase deprecation.
2. **Forward Compatibility**: Old schema versions can read records written by new schemas.
3. **Full Compatibility**: Both backward and forward compatibility maintained simultaneously.
