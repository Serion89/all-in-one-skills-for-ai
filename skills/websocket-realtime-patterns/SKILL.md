---
name: websocket-realtime-patterns
description: Full-duplex WebSocket and Server-Sent Events (SSE) engineering. Use when building real-time dashboards, collaborative multiplayer sync, chat messaging, connection heartbeats, reconnect backoff, and distributed Redis Pub/Sub broadcasting.
---

# WebSocket & Real-Time Streaming Architecture

## Purpose
Engineer resilient, low-latency, bidirectional real-time communication layers using WebSockets and Server-Sent Events (SSE) with horizontal clustering.

---

## Core Engineering Directives

### 1. Connection Lifecycle & Heartbeat (Ping/Pong)
Dead TCP connections silently consume memory and file descriptors without sending `FIN`/`RST` packets when clients drop off Wi-Fi.
- **Protocol**: Server initiates a `ping` frame every 30 seconds.
- **Timeout**: If the client fails to return a `pong` frame within 10 seconds, the server terminates the socket and releases associated memory.

### 2. Reconnection with Exponential Backoff & Jitter
Prevent "thundering herd" floods against the backend server during server restarts:
```javascript
function getNextRetryDelay(attempt, base = 1000, max = 30000) {
  const exponential = Math.min(max, base * Math.pow(2, attempt));
  const jitter = Math.random() * 0.5 * exponential; // Add 50% random jitter
  return exponential + jitter;
}
```

### 3. Horizontal Scaling via Redis Pub/Sub
Because WebSocket connections are stateful and pinned to a specific server instance:
- Connect all backend nodes to a shared message broker (Redis / RabbitMQ).
- When User A on Node 1 sends a message to Room X, Node 1 publishes the event to Redis channel `room:X`.
- All backend nodes subscribed to `room:X` receive the event and broadcast it locally to their connected clients.

### 4. SSE vs WebSocket Selection Rule
- Use **Server-Sent Events (SSE)** for unidirectional server-to-client streaming (e.g. LLM token streaming, notifications, real-time charts). SSE works over standard HTTP/2, handles auto-reconnect natively, and traverses corporate proxies easily.
- Use **WebSockets** exclusively when true bidirectional, low-latency client-to-server messaging is required (e.g. collaborative canvases, gaming, trading terminals).
