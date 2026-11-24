# Smartenup

Deterministic Atomic Code Mutation and Syntactic Safety Engine

Smartenup is a resilient code replacement engine and agent skill designed to eliminate common failure modes encountered by automated coding tools and Large Language Models (LLMs) when modifying complex or large source files.

---

## 1. Overview

Standard diff and string-replacement tools (such as line-by-line diff matchers or simple substring replacers) exhibit high failure rates in specific edge cases:

1. **Delimiter and Escape Collisions**: Files containing nested template literals (e.g. JavaScript/TypeScript backticks, template variables `${...}`), regular expressions, GLSL shaders, or nested shell scripts are prone to parameter-escaping corruption when passed through JSON-RPC or terminal execution layers.
2. **Whitespace and Indentation Drift**: In files exceeding 1,000 lines, subtle differences in indentation or line endings often cause substring matchers to fail with unrecoverable target mismatch errors.
3. **Partial Mutation and Truncation Risk**: If a multi-site refactoring operation fails midway, target files can be left in an inconsistent state or accidentally truncated to zero bytes.
4. **Low-Parameter Model Instability**: Small or local models (7B to 14B parameters) frequently make off-by-one errors when instructed to generate ad-hoc file-slicing scripts.

Smartenup resolves these issues by offloading file manipulation to a pre-built, hardened CLI utility (`patcher.py`). The model or developer provides verbatim replacement text in a scratch file and executes a deterministic command with boundary anchors.

---

## 2. Architectural Safety Gates

Before modifying any file on disk, the engine applies sequential validation stages:

| Safety Gate | Verification Mechanism | Failure Mitigation |
| :--- | :--- | :--- |
| **Line Ending Normalization** | Automatically detects and normalizes Windows CRLF (`\r\n`) and Unix LF (`\n`). | Prevents index mismatch caused by operating system line-ending differences. |
| **Anchor Uniqueness Verification** | Asserts that the start boundary occurs exactly once in the target document. | Rejects ambiguous matches and outputs exact line numbers for disambiguation. |
| **Generic Token Shield** | Flags and rejects short, generic closing tokens (e.g., bare `}`, `);`, `]`). | Prevents premature block termination at nested conditional or loop statements. |
| **Pre-Commit Delimiter Gate** | Calculates balance delta for curly braces `{}`, parentheses `()`, and square brackets `[]`. | Blocks commit if the patch introduces unbalanced syntax delimiters. |
| **In-Memory AST Gate** | Parses candidate content via `ast.parse` (Python) or `json.loads` (JSON). | Ensures syntactically invalid code is never written to disk. |
| **Truncation Guard** | Compares pre-patch and post-patch byte counts against a maximum threshold (default: 35%). | Halts execution if a large portion of the file was unintentionally omitted. |
| **Atomic OS Replacement** | Writes candidate content to a temporary file (`.tmp`) and swaps via `os.replace`. | Guarantees atomic writes; target files cannot be corrupted by mid-write aborts. |
| **Automated Backup** | Creates an exact copy of the pre-operation file (`.bak`). | Provides zero-overhead recovery in local workspaces. |

---

## 3. Repository Structure

```text
smartenup/
|-- README.md               # Technical documentation and specifications
|-- SKILL.md                # Agent skill definition for AI coding environments
|-- scripts/
|   `-- patcher.py          # Deterministic atomic replacement engine
`-- tests/
    `-- test_patcher.py     # Functional test suite
```

---

## 4. Usage Reference

### 4.1 CLI Command Syntax

```bash
python scripts/patcher.py \
  --target "path/to/target_file.ext" \
  --start "exact_start_anchor" \
  --end "exact_end_anchor" \
  --patch-file "path/to/replacement.txt"
```

### 4.2 Parameter Reference

| Parameter | Shorthand | Description | Default |
| :--- | :--- | :--- | :--- |
| `--target` | `-t` | Absolute or relative path to the target file. | Required |
| `--start` | `-s` | Exact start boundary string. | Required |
| `--end` | `-e` | Exact end boundary string (include preceding line context). | Required |
| `--patch-file` | `-p` | Path to file containing replacement text. | Optional |
| `--patch` | None | Direct replacement string passed via argument. | Optional |
| `--delete` | None | Deletes targeted region without replacement. | Flag (False) |
| `--mode` | `-m` | `inclusive` (replaces anchors) or `exclusive` (replaces between). | `inclusive` |
| `--dry-run` | None | Validates boundaries and outputs diff without modifying disk. | Flag (False) |
| `--allow-shrink` | None | Bypasses the 35% file reduction safety threshold. | Flag (False) |
| `--max-shrink` | None | Custom maximum allowable file size reduction percentage. | `35.0` |
| `--syntax-check` | None | Validation mode: `auto`, `py`, `json`, `brackets`, or `none`. | `auto` |
| `--no-backup` | None | Disables generation of `.bak` backup file. | Flag (False) |

### 4.3 Practical Examples

#### Replacing a Function Safely
```bash
python scripts/patcher.py \
  --target "src/rendering/pipeline.ts" \
  --start "export function initializePipeline(" \
  --end "  return pipelineInstance;\n}" \
  --patch-file "scratch/updated_pipeline.txt"
```

#### Executing a Dry Run
```bash
python scripts/patcher.py \
  --target "services/auth.py" \
  --start "class TokenManager:" \
  --end "    return self.session\n" \
  --patch-file "scratch/auth_patch.txt" \
  --dry-run
```

#### Deleting a Deprecated Module Block
```bash
python scripts/patcher.py \
  --target "src/config.json" \
  --start "\"legacySettings\": {" \
  --end "  }," \
  --delete
```

---

## 5. Integration with AI Agent Workflows

When deploying Smartenup as a skill for autonomous agents (e.g. Claude Code, Antigravity, Gemini, or Cursor):

1. **Step 1: Anchor Selection**  
   The agent inspects the target file and selects an unambiguous start boundary (e.g. function declaration) and an end boundary (including the statement immediately preceding the closing bracket).

2. **Step 2: Isolated Patch Authoring**  
   The agent writes replacement code into a plain scratch file (e.g. `scratch/patch.txt`). This avoids string escaping collisions.

3. **Step 3: Execution and Verification**  
   The agent executes `patcher.py`. If execution succeeds, a standard unified diff is returned for verification. If an error is raised (such as an ambiguous anchor or unbalanced braces), the engine provides exact line references for immediate self-correction.

---

## 6. Verification and Testing

Execute the test suite to validate all internal safety gates:

```bash
python tests/test_patcher.py
```

Expected output:
```text
Testing patcher engine (patcher.py)...
[PASS] Test 1: Normal replacement and backup creation.
[PASS] Test 2: Generic anchor rejection.
[PASS] Test 3: Delimiter balance detection.
[PASS] Test 4: Truncation and shrink guard.
[PASS] Test 5: Shrink threshold override.
[PASS] Test 6: AST syntax validation.

Status: All test cases passed successfully.
```

---

## 7. Credits and License

Created by **ciel 441**

[![GitHub](https://img.shields.io/badge/GitHub-Ciel--441-181717?style=flat&logo=github)](https://github.com/Ciel-441)

Released under the MIT License. Free for open-source and commercial use.
