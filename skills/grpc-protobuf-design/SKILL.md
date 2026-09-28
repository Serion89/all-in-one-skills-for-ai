---
name: grpc-protobuf-design
description: gRPC service design and Protocol Buffers v3 schema evolution. Use when defining high-performance internal microservice RPCs, binary serialization contracts, streaming RPC semantics, deadline propagation, and status codes.
---

# gRPC & Protocol Buffers (proto3) Service Design

## Purpose
Build high-performance, strongly typed, binary-encoded microservice interfaces using gRPC over HTTP/2 and Protocol Buffers v3.

---

## Proto3 Design Conventions

### 1. Field Number Allocation Rules
- Tag numbers `1` through `15` consume 1 byte on the wire: reserve these exclusively for frequently transmitted fields.
- Tag numbers `16` through `2047` consume 2 bytes: use for lower-frequency fields.
- **NEVER re-use tag numbers**: Once a field is deleted, mark its tag number and field name as `reserved` to prevent backward incompatibility bugs:
  ```protobuf
  message User {
    reserved 3, 7 to 9;
    reserved "phone_number", "avatar_url";
    string id = 1;
    string email = 2;
  }
  ```

### 2. Standard gRPC Error Model
Never return HTTP 200 with custom JSON error bodies. Use standard gRPC status codes paired with `google.rpc.Status` rich error details:
- `INVALID_ARGUMENT`: Client provided bad input (field violations).
- `NOT_FOUND`: Target resource does not exist.
- `ALREADY_EXISTS`: Resource collision on creation.
- `PERMISSION_DENIED`: Caller lacks authorization.
- `UNAUTHENTICATED`: Missing or invalid credentials.
- `DEADLINE_EXCEEDED`: Upstream deadline lapsed before operation completed.

### 3. Deadline & Cancellation Propagation
Always propagate incoming context deadlines across outbound downstream gRPC calls:
```go
// Propagate timeout context to downstream dependency
ctx, cancel := context.WithTimeout(parentCtx, 500*time.Millisecond)
defer cancel()
res, err := downstreamClient.Process(ctx, req)
```
