---
name: contract-testing-pact
description: Consumer-driven contract testing between microservices using Pact. Use when verifying API integrations between independent frontend and backend services without deploying end-to-end integration environments.
---

# Consumer-Driven Contract Testing (Pact)

## Purpose
Verify API integration contracts between consuming clients and producing services independently in CI/CD pipelines, preventing breaking API changes without brittle end-to-end testing environments.

---

## The Contract Testing Lifecycle

```
[Consumer Tests] ---> Generates Pact Contract JSON ---> Uploads to Pact Broker
                                                                 |
[Provider Tests] <--- Pulls Contract JSON <---------------------+
       |
Verifies API matches contract ---> Publishes Verification Results
```

---

## Consumer Test Pattern (Defines the Contract)

```javascript
import { PactV3, MatchersV3 } from '@pact-foundation/pact';

const provider = new PactV3({
  consumer: 'FrontendWebApp',
  provider: 'UserMicroservice',
});

test('get user profile contract', async () => {
  provider
    .given('user 123 exists')
    .uponReceiving('a request for user 123')
    .withRequest({
      method: 'GET',
      path: '/api/v1/users/123',
    })
    .willRespondWith({
      status: 200,
      headers: { 'Content-Type': 'application/json' },
      body: {
        id: MatchersV3.like('123'),
        email: MatchersV3.regex('^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', 'user@domain.com'),
        role: MatchersV3.string('ADMIN'),
      },
    });

  await provider.executeTest(async (mockserver) => {
    const res = await fetch(`${mockserver.url}/api/v1/users/123`);
    expect(res.status).toBe(200);
  });
});
```

---

## Provider Verification Pattern
The backend provider runs automated tests that pull the consumer contract and verify that its actual controllers return schemas matching the expected Pact assertions.
- If a backend change alters an API field required by a consumer, provider tests fail immediately in CI before deployment.
