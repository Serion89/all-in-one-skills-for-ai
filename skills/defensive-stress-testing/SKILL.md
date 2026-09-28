---
name: defensive-stress-testing
description: Safe developer load, stress, and breakpoint testing using k6, Locust, and autocannon. Use when determining service breaking points, verifying P95/P99 latency SLAs, testing connection pool saturation, and detecting memory leaks under sustained load.
---

# Defensive Load & Stress Testing

## Purpose
Safely evaluate backend service resilience, identify resource ceilings (CPU, memory, database connection pools), and verify P95/P99 latency SLAs under high throughput.

---

## Safety & Governance Rules (MANDATORY)

> [!IMPORTANT]
> - **Authorized Targets Only**: Execute stress tests ONLY against localhost, isolated staging environments, or explicitly designated performance sandbox clusters.
> - **Never Target Third-Party Services**: Strip or mock all third-party external APIs (Stripe, Twilio, SendGrid) before initiating load tests to avoid bill spikes and rate-limit bans.
> - **Automated Abort Thresholds**: Every test script MUST include an automatic kill condition (e.g. abort if HTTP 5xx error rate exceeds 5% or latency exceeds 5000ms).

---

## Core Testing Profiles

### 1. Smoke Test (Sanity Baseline)
- **Profile**: 1 to 5 Virtual Users (VUs) for 1 minute.
- **Goal**: Verify that all endpoints, authentication headers, and database seeds function properly before applying high load.

### 2. Load Test (Expected Production Volume)
- **Profile**: Ramp up to target peak concurrency (e.g. 100 VUs) over 5 minutes, sustain for 15 minutes, ramp down over 2 minutes.
- **Goal**: Measure baseline latency percentiles (P50, P90, P99) and resource consumption under expected traffic.

### 3. Stress & Breakpoint Test
- **Profile**: Continuous step-ramp (e.g. +20 VUs every 2 minutes) until error rates surge or latency degrades catastrophically.
- **Goal**: Identify the exact bottleneck: connection pool starvation, thread exhaustion, garbage collection pause, or CPU throttling.

### 4. Soak Test (Endurance)
- **Profile**: 60% of peak load sustained for 2 to 8 hours.
- **Goal**: Uncover gradual resource degradation: memory leaks, unclosed database cursors, and socket exhaustion (TIME_WAIT proliferation).

---

## Standard k6 Test Harness Pattern

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Warm up
    { duration: '5m', target: 200 },  // Sustained load
    { duration: '1m', target: 0 },    // Cooldown
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],    // Error rate must be under 1%
    http_req_duration: ['p(95)<400'],  // 95% of requests must resolve under 400ms
  },
};

export default function () {
  const url = __ENV.TARGET_URL || 'http://localhost:8080/api/v1/health';
  const res = http.get(url);
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response body valid': (r) => r.body.length > 0,
  });
  
  sleep(1);
}
```

---

## Diagnostic Checklist During Stress Execution
1. **CPU & Memory**: Monitor container metrics (`docker stats` or `kubectl top pod`).
2. **Database Engine**: Inspect active connections and slow query logs (`SELECT count(*) FROM pg_stat_activity;`).
3. **Event Loop Latency**: In Node.js or Python asyncio, track event loop delay lag under heavy I/O.
4. **Graceful Degradation**: Verify that the service returns clean HTTP 429 (Too Many Requests) or 503 rather than dropping TCP connections abruptly.
