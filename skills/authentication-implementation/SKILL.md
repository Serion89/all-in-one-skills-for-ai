---
name: authentication-implementation
description: Implement authentication and session management correctly - choose between delegated OIDC login and first-party accounts, store passwords with Argon2id, set secure session cookies with rotation and revocation, use OAuth 2.0 with PKCE, handle refresh-token rotation and reuse detection, and build password reset and MFA without account enumeration. Use when building or changing login, sessions, tokens, password reset, or MFA. For reviewing an existing system's security, use security-auditor instead.
license: MIT
metadata:
  author: Serion89
  version: "1.0.0"
---

# Authentication Implementation

Authentication is the place where small mistakes become account takeovers. Use proven
libraries and managed providers, and spend your effort on the boundaries: how sessions
start, how they end, and what an attacker learns from each response.

This skill is for building auth. To audit an existing system, use `security-auditor`.

## 1. Decide the architecture first

- **Delegate when you can**: an identity provider (OIDC) handles passwords, MFA, and account recovery. Your app validates the ID token and creates its own session.
- **Build first-party accounts only when required**: then use a maintained library for your framework and do not write hashing, token signing, or session storage yourself.
- **Pick the session model deliberately**:
  - Server-side sessions with an opaque ID in an HttpOnly cookie: easiest to revoke. Default for browser apps.
  - JWT access tokens: stateless, but revocation is delayed until expiry. Keep them short-lived.
- Write down the threat model in one paragraph: who the users are, what an account grants, and what the worst outcome of takeover is.

## 2. Password storage

- Hash with **Argon2id** (memory-hard), using the library's recommended parameters. Use bcrypt only when Argon2 is unavailable, with cost 12 or higher.
- Never store, log, or send passwords in plaintext, including in error messages and analytics.
- Compare hashes with the library's constant-time verification. Do not compare hashes with `==`.
- Check new passwords against a breached-password list (for example, k-anonymity range queries) and enforce length, not composition rules.
- Rehash on login when the stored parameters are weaker than current defaults.

## 3. Session cookies

- Generate session IDs with at least 128 bits from a CSPRNG (`secrets.token_urlsafe(32)` or equivalent).
- Set the cookie attributes:
  - `HttpOnly` so scripts cannot read it.
  - `Secure` so it is sent only over HTTPS.
  - `SameSite=Lax` (or `Strict` where it fits) to reduce CSRF.
  - `Path=/` and a scoped `Domain` only when needed.
- **Rotate the session ID on login and on privilege change** to prevent session fixation.
- Enforce both an idle timeout and an absolute lifetime.
- Store only a hash of the session token server-side, so a database leak does not yield live sessions.
- Make logout delete the server-side session, not only the cookie.
- Protect state-changing requests from CSRF: use `SameSite` plus a synchronizer or double-submit token for forms and non-JSON endpoints.

## 4. OAuth 2.0 and OIDC clients

- Use the **authorization code flow with PKCE** for every client, including server-side apps. Do not use the implicit flow or the resource owner password grant.
- Generate a random `state` for each request and verify it on callback. Generate a `nonce` for OIDC and verify it in the ID token.
- Match redirect URIs exactly against a registered allow-list. Do not use prefix or wildcard matching.
- Validate every ID token: signature against the provider's JWKS, `iss`, `aud`, `exp`, `iat`, and `nonce`. Pin the expected algorithm; reject `none` and algorithm switching.
- Keep client secrets on the server. Public clients (SPA, mobile) use PKCE only.

## 5. Tokens and refresh rotation

- Access tokens: short-lived (minutes), audience-scoped, and validated on every request.
- Refresh tokens: opaque, stored hashed, **rotated on each use**. Keep a family ID per login.
- **Reuse detection**: if an already-rotated refresh token is presented, revoke the whole family and force re-authentication. This signals theft.
- Store tokens in HttpOnly cookies for browser apps. Avoid `localStorage` for refresh tokens.
- Revoke tokens on password change, logout, and account disable.

## 6. Password reset

- Generate a single-use reset token with at least 128 bits of entropy, store its hash, and expire it in 15 to 60 minutes.
- Invalidate the token after use and after a successful password change.
- Respond with the same message and similar timing whether or not the email exists. Do not reveal account existence.
- Send the link to the registered email only. Never reveal the token in the response body.
- Require re-authentication, or notify the user by email, after a password change.

## 7. MFA

- Offer TOTP or, better, WebAuthn/passkeys. SMS is the weakest option; use it only as a fallback.
- Rate-limit MFA attempts and lock the challenge after a small number of failures.
- Generate recovery codes once, show them once, and store them hashed.
- Do not let a password reset bypass MFA.

## 8. Rate limiting and errors

- Rate-limit login, reset, and MFA endpoints per account and per source IP.
- Return one generic error for failed login: "Invalid email or password." Do not distinguish unknown user from wrong password.
- Log authentication events (success, failure, reset, MFA change) with user ID and IP, never the password or token.

## Checklist

- [ ] Architecture chosen and the threat model written down.
- [ ] Passwords hashed with Argon2id; comparison is constant-time.
- [ ] Session ID rotated on login; cookie has HttpOnly, Secure, SameSite.
- [ ] Logout and password change revoke server-side sessions.
- [ ] OAuth uses PKCE, validated `state` and `nonce`, exact redirect URIs.
- [ ] Refresh tokens rotate with reuse detection.
- [ ] Reset tokens are single-use, hashed, short-lived, and do not reveal accounts.
- [ ] Negative tests exist for every row above.

## Anti-patterns

- Rolling your own token format or cipher instead of a maintained library.
- Storing access tokens in `localStorage` where any injected script can read them.
- Trusting a JWT's claims without verifying the signature and algorithm.
- Long-lived access tokens with no revocation path.
- Separate "user not found" and "wrong password" messages.
