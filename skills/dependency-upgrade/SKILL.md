---
name: dependency-upgrade
description: Plan and execute library, framework, and runtime upgrades safely - inventory current versions, read every breaking-change note between the current and target version, establish characterization tests, upgrade in small reviewable steps, and verify build, behavior, types, and performance before merging. Use when bumping a major version of a dependency, upgrading a framework or language runtime, or triaging a batch of automated dependency PRs.
license: MIT
metadata:
  author: Serion89
  version: "1.0.0"
---

# Dependency Upgrade

An upgrade is a code change with a version number attached. Treat it as a change to
behavior, not just to a manifest file, and keep each upgrade small enough to revert.

This skill covers upgrading dependencies you consume. For removing your own deprecated APIs or migrating users, use `deprecation-and-migration`.

## 1. Inventory

- Record the current version, the target version, and the reason for the upgrade (security fix, feature, end-of-life, bug).
- Find every use of the dependency: direct imports, plugins, config files, and build integrations. `grep` for the package name and its main exports.
- Check transitive effects: peer dependencies, required runtime versions (Node, Python, JDK), and types packages.
- Check the security advisory database for the current version. A security-driven upgrade has a deadline; plan around it.

## 2. Read the breaking changes

- Read the changelog or migration guide for **every major version** between current and target. Skipping a major without reading its notes is the most common cause of surprises.
- Read the deprecation warnings on the **current** version first; most breaking changes are announced there.
- Mark each breaking change as affecting this codebase or not, with a reason. Check the actual call sites for the ones that do.

## 3. Establish a safety net

- Confirm the existing test suite passes on the current version before changing anything. A red baseline makes the upgrade unverifiable.
- Add characterization tests for the behavior you depend on, especially around the changed APIs. Write them against the current version and make sure they pass.
- Pin the exact version in the lockfile and keep the old lockfile in version control so the change is revertible.

## 4. Upgrade in steps

- One dependency per change for major upgrades. Do not mix a framework upgrade with a feature.
- If the migration guide says to go through intermediate versions, do that, one at a time.
- Apply the codemod the vendor provides, if there is one, then review its diff. Do not accept codemod output blindly.
- Fix type errors first, then runtime test failures, then lint warnings.
- Update related tooling in the same change only when the new version requires it (for example, a plugin that must match the core version).

## 5. Verify

Run each check and record its result:

- [ ] Clean install from the lockfile succeeds (`npm ci`, `uv sync --locked`, or equivalent).
- [ ] Type check passes with no new suppressions.
- [ ] Full test suite passes, including the characterization tests.
- [ ] Build succeeds for every target (production, library exports, container image).
- [ ] Bundle size or binary size change is measured if the dependency is in the client path.
- [ ] A smoke test of the critical path runs against a staging or local environment.
- [ ] For runtime or database-driver upgrades: run a performance check on the hot path, since defaults change.

## 6. Roll out

- Merge behind a normal review with the changelog excerpt and the list of breaking changes in the PR description.
- For services, deploy to a canary or staging first and watch error rates and latency.
- Keep the revert path simple: the previous lockfile and the previous image or artifact.

## 7. Triage automated upgrade PRs

- Group minor and patch updates and merge them once CI is green; they are usually low-risk.
- Review every major update individually, using steps 2 to 5. Do not auto-merge majors.
- Close or defer updates that no code path uses only if the security team agrees; otherwise, keep the dependency current.

## Anti-patterns

- Bumping every dependency in one commit.
- Running `npm audit fix --force` or equivalent without reading what it changes.
- Ignoring peer dependency warnings that predict runtime failures.
- Upgrading a dependency inside an unrelated feature PR.
- Declaring success because the build passed, without running the behavior tests.
