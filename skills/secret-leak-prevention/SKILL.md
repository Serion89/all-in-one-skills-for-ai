---
name: secret-leak-prevention
description: Defensive secret detection, git hygiene, and credential protection. Use when scanning repositories for hardcoded API keys, JWT secrets, private keys, database credentials, configuring Gitleaks pre-commit hooks, and executing rotation playbooks.
---

# Secret Leak Prevention & Credential Hygiene

## Purpose
Prevent, detect, and remediate exposed credentials, private keys, authentication tokens, and sensitive secrets within source code repositories and build pipelines.

---

## The 3 Pillars of Credential Protection

### 1. Prevention (Pre-Commit Gates)
Stop secrets from ever entering git history:
- Enforce `.gitignore` templates covering:
  - `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa`, `*.p12`
  - Cloud credentials: `~/.aws/credentials`, `~/.gcp/`, `kubeconfig`
- Install automated pre-commit scanners (e.g. Gitleaks, TruffleHog):
  ```bash
  # Install Gitleaks pre-commit hook
  gitleaks protect --staged --verbose
  ```

### 2. Detection (Static Entropy & Pattern Scans)
Search existing git commit trees for high-entropy strings and known signature patterns:

```bash
# Scan entire git repository history for leaked secrets
gitleaks detect --source . --verbose --report-path gitleaks-report.json

# Scan unstaged and staged files
git diff | gitleaks detect --pipe
```

Common Signatures Monitored:
- AWS Access Key (`AKIA[0-9A-Z]{16}`)
- GitHub Personal Access Token (`ghp_[0-9a-zA-Z]{36}`)
- Stripe API Secret Key (`sk_live_[0-9a-zA-Z]{24}`)
- Private RSA / OpenSSH Header (`-----BEGIN OPENSSH PRIVATE KEY-----`)
- High-entropy base64/hexadecimal strings assigned to variable names like `api_key`, `secret`, `password`, `bearer`.

### 3. Immediate Remediation Protocol (If Secret is Committed)

> [!CAUTION]
> Once a secret is pushed to a remote git repository, it MUST be assumed compromised. Deleting the line in a new commit does NOT secure the secret because it remains in git history.

Execute the 4-step emergency rotation:
1. **Revoke & Rotate**: Immediately revoke the exposed token in the service provider console (AWS IAM, GitHub, Stripe, Supabase) and issue a replacement.
2. **Purge Git History**: If local-only, rebase interactively to remove the commit. If pushed remotely, use `git-filter-repo` or BFG Repo-Cleaner to rewrite history across all branches.
3. **Force-Push with Caution**: Coordinate with team members before running `git push origin --force --all`.
4. **Audit Provider Access Logs**: Inspect the credential's access logs over the exposure window to confirm zero unauthorized API calls were made.
