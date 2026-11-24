---
name: smartenup
description: Deterministic atomic code patcher for large files (>1,000 lines), nested template literals, complex GLSL/Canvas scripts, and multi-region edits where standard string diffs fail.
---

# Smartenup: Deterministic Atomic Code Patcher

Use this skill when standard string replacement or diff tools fail due to line drift, escaping conflicts (backticks, `${...}`, quotes), or when editing large files (>1,000 lines) where edits must apply atomically without risk of truncation or corruption.

**DO NOT write ad-hoc Python file-slicing scripts.** 
Always use the built-in deterministic patcher engine located at:
`scripts/patcher.py` (or `<skill_dir>/scripts/patcher.py`)

---

## When to Use

1. **Standard `edit_file` failed**: Target string was not found, whitespace mismatched, or partial diff failed.
2. **Heavy template literals & raw strings**: Files with nested backticks (`` ` ``), GLSL shaders, regex, or Canvas scripts where tool escaping mangles characters.
3. **Large files (> 1,000 lines)**: Replacing entire functions, classes, or multi-line blocks safely with pre-commit validation.

---

## The 3-Step Protocol

### Step 1: Pick Unambiguous Anchors
Read the lines around the target code. Identify:
- **`--start` anchor**: The exact first line(s) of the block to replace (e.g. `export function renderScene(` or `// --- SECTION A ---`).
- **`--end` anchor**: The exact last line(s) of the block.
  > **CRITICAL RULE FOR END ANCHORS**: 
  > Never use bare brackets like `}` or `);` as an end anchor. They will match early inner blocks! 
  > Always include the preceding statement (e.g. `  return scene;\n}` or `this.cleanup();\n}`).

### Step 2: Write Replacement to a Scratch File
Do not pass large multi-line code directly via CLI flags. 
Use your file writing tool to write the verbatim new code into a scratch text file:
- Target path: `scratch/patch.txt` (or any temporary `.txt` file)
- The file contains pure replacement code. No Python scripts, no JSON escaping.

### Step 3: Run the Patcher Engine
Execute the command via PowerShell/Bash:

```bash
python "<path_to_smartenup>/scripts/patcher.py" \
  --target "path/to/target_file.ext" \
  --start "exact_start_anchor" \
  --end "exact_end_anchor" \
  --patch-file "scratch/patch.txt"
```

The engine will automatically:
1. Normalize line endings (CRLF/LF) safely.
2. Verify anchors match uniquely (rejects ambiguous multiple matches).
3. Validate syntax (AST check for Python/JSON; delimiter & bracket balance for JS/TS/C/Rust).
4. Guard against accidental truncation (aborts if file shrinks > 35%).
5. Create a `.bak` backup and atomically swap the file (`os.replace`).
6. Print a clean unified `git diff` to stdout.

---

## Command Flags Reference

| Flag | Description | Default |
| :--- | :--- | :--- |
| `--target`, `-t` | Absolute or relative path to file being edited. | **Required** |
| `--start`, `-s` | Exact start anchor string. | **Required** |
| `--end`, `-e` | Exact end anchor string (include 1 line before `}`). | **Required** |
| `--patch-file`, `-p` | Path to scratch file with new replacement code. | Recommended |
| `--mode`, `-m` | `inclusive` (replaces anchors too) or `exclusive` (replaces between). | `inclusive` |
| `--dry-run` | Shows unified diff and validates without writing to disk. | Off |
| `--delete` | Deletes the targeted block (empty replacement). | Off |
| `--allow-shrink` | Overrides the 35% file shrinkage protection. | Off |
| `--syntax-check` | `auto`, `py`, `json`, `brackets`, or `none`. | `auto` |

---

## Error Handling & Self-Correction

If the patcher returns an error, follow these exact fixes:

- **Error: "Start anchor matched X times"**:
  Add 1 preceding line (e.g. a comment, decorator, or parent signature) to make `--start` completely unique.
- **Error: "End anchor is too generic"**:
  Do not use bare `}`. Include the line directly above it (e.g., `  return result;\n}`).
- **Error: "Delimiters became unbalanced"**:
  Your replacement code has an unclosed `{`, `(`, or `[`. Check and balance brackets in `patch.txt`.
- **Error: "File size shrank by X%"**:
  Your end anchor probably matched too far down the file. Verify your anchors. If you genuinely intended to delete a huge chunk of code, add `--allow-shrink`.
