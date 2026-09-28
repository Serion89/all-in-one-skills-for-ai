---
name: supply-chain-security
description: Software supply chain security, dependency vulnerability management, and SBOM generation. Use when auditing third-party libraries, scanning package lockfiles, generating CycloneDX/SPDX manifests, and preventing malicious dependency attacks.
---

# Software Supply Chain Security & Dependency Auditing

## Purpose
Protect software build pipelines, application binaries, and container images against compromised dependencies, typosquatting, malicious scripts, and supply-chain attacks.

---

## 4-Tier Supply Chain Defense

### 1. Lockfile Integrity & Deterministic Builds
- Always commit package lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`, `poetry.lock`).
- In CI/CD pipelines, strictly enforce deterministic installs that fail if the lockfile drifts from manifests:
  ```bash
  npm ci              # Node.js
  cargo build --locked # Rust
  poetry install --no-root --sync # Python
  ```

### 2. Dependency Vulnerability Auditing
Automate vulnerability scans on every pull request:
```bash
# Node.js vulnerability scan
npm audit --audit-level=high

# Python dependency scan
pip-audit --desc on

# Rust dependency scan
cargo audit
```

### 3. Software Bill of Materials (SBOM) Generation
Generate machine-readable SBOM manifests in standardized CycloneDX or SPDX format during release packaging:
```bash
# Generate CycloneDX SBOM for container or workspace
syft dir:. -o cyclonedx-json=sbom.json
```

### 4. Malicious Lifecycle Script Mitigation
Disable arbitrary package installation scripts (`preinstall`, `postinstall`) unless explicitly required:
```bash
npm install --ignore-scripts
```
