---
name: chaos-engineering
description: Resilience and fault-injection engineering principles. Use when designing disaster-recovery experiments, testing circuit breaker trip thresholds, injecting synthetic network latency, simulating database dropouts, and proving self-healing behavior.
---

# Chaos Engineering & Resilience Validation

## Purpose
Proactively validate system resilience under unexpected failure conditions. Formulate testable hypotheses, inject controlled faults in non-production environments, and prove that self-healing systems and graceful degradation patterns behave as designed.

---

## The 4 Principles of Chaos Engineering

1. **Define Steady State**: Establish measurable baseline metrics indicating healthy operation (e.g. error rate < 0.1%, P95 latency < 200ms, throughput > 500 RPS).
2. **Formulate Hypothesis**: State expected behavior under failure (e.g. *"If the Redis cache cluster fails, the API service will fallback to read-replica Postgres with degraded P99 latency, but zero HTTP 5xx errors."*).
3. **Introduce Real-World Variables**: Simulate realistic hardware, network, or dependency outages.
4. **Disprove Hypothesis**: Measure deviation from steady state. Any deviation uncovers an architectural vulnerability before it causes a production outage.

---

## Controlled Fault Scenarios

| Failure Domain | Synthetic Fault | Expected System Reaction | Failure Indicator (Bug) |
| :--- | :--- | :--- | :--- |
| **Network Latency** | Add 1500ms delay to downstream payment service. | Circuit breaker opens after 5 failures; fallback response returned in < 250ms. | Thread exhaustion, client timeout cascading across all upstream services. |
| **Service Outage** | Terminate primary authentication worker pod. | Kubernetes restarts pod; ingress re-routes traffic to healthy replicas with zero dropped connections. | End users logged out, 502 Bad Gateway errors returned. |
| **Database Disconnect** | Temporarily block port 5432 via firewall rules. | Connection pool catches socket error; queries queue gracefully or return user-friendly service unavailable code. | Backend process crashes with unhandled fatal exception. |
| **Disk Saturation** | Fill temporary disk partition to 98% capacity. | Application logs warning, discards ephemeral debug artifacts, preserves core read paths. | Hard crash, unhandled I/O panic, corrupted local state files. |

---

## Safe Execution Guardrails

> [!WARNING]
> - **Blast Radius Containment**: Always run experiments in a scoped staging cluster with synthetic mock traffic.
> - **Emergency Abort Switch**: Ensure immediate capability to revert the fault injection (e.g. clear network latency rules, unblock firewall) within 30 seconds.
> - **Observability Synchronization**: Never run a chaos experiment without active, synchronized monitoring (Prometheus, Grafana, or OpenTelemetry traces) recording steady state telemetry.
