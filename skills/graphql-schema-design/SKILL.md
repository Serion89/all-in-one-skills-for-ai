---
name: graphql-schema-design
description: Enterprise GraphQL schema design, Apollo Federation, and query performance. Use when authoring GraphQL schemas, solving the N+1 database problem via DataLoader, designing cursor-based pagination, and enforcing field-level authorization.
---

# Enterprise GraphQL Schema Design & Performance

## Purpose
Structure scalable, expressive GraphQL APIs that prevent client-driven performance degradation, solve N+1 database queries, enforce field-level security, and facilitate schema federation.

---

## Schema Architecture Standards

### 1. Strict Typing & Mutation Payloads
Always design mutations with explicit input objects and distinct payload types containing user-facing error unions:

```graphql
input CreateUserInput {
  email: String!
  fullName: String!
}

type CreateUserPayload {
  user: User
  errors: [UserError!]!
}

type UserError {
  field: String
  message: String!
  code: ErrorCode!
}
```

### 2. Solving the N+1 Query Problem (DataLoader)
Never query the database directly inside nested type resolvers.
- **Batching & Caching**: Wrap relational lookups in a request-scoped `DataLoader` instance that coalesces individual primary key lookups into a single batch SQL query:
  ```javascript
  // Translates N individual SELECTs into a single:
  // SELECT * FROM authors WHERE id IN (1, 2, 3...);
  const authorLoader = new DataLoader(keys => myDb.getAuthorsByIds(keys));
  ```

### 3. Cursor-Based Pagination (Relay Connection Spec)
Avoid offset-based pagination (`limit`/`offset`) on large datasets due to row-shift and index-scan degradation:

```graphql
type Query {
  posts(first: Int, after: String): PostConnection!
}

type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
}

type PostEdge {
  cursor: String!
  node: Post!
}
```

### 4. Query Depth & Complexity Limiting
Protect the GraphQL engine against denial-of-service via deeply nested circular queries:
- Enforce maximum query depth limits (e.g. max depth = 6).
- Implement static complexity analysis to reject queries with astronomical field multipliers before execution.
