#!/usr/bin/env python3
"""
smartenup - Deterministic Atomic Code Patcher
Designed for resilience even with low-parameter / small models.

Features:
- Windows CRLF / Unix LF transparent normalization.
- Unambiguous anchor validation with exact line-number diagnostics.
- Pre-flight syntax and structural balance gates (Python AST, JSON, bracket balance).
- File truncation guard (catches accidental line drops).
- Unified diff output on dry-run or commit.
- Atomic file swapping (zero risk of 0-byte corrupted files).
- Auto-backup (.bak).
"""

import argparse
import ast
import difflib
import json
import os
import sys
from pathlib import Path


def detect_crlf(raw_bytes: bytes) -> bool:
    """Check if file primarily uses Windows CRLF."""
    return b"\r\n" in raw_bytes


def normalize_newlines(text: str) -> str:
    """Normalize all newlines to Unix \\n for consistent indexing."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def get_line_numbers(text: str, substring: str) -> list[int]:
    """Return 1-based line numbers where substring starts in text."""
    lines = text.split("\n")
    line_nums = []
    current_idx = 0
    while True:
        idx = text.find(substring, current_idx)
        if idx == -1:
            break
        # Calculate line number
        line_num = text[:idx].count("\n") + 1
        line_nums.append(line_num)
        current_idx = idx + max(1, len(substring))
    return line_nums


def check_bracket_balance(orig: str, patched: str) -> tuple[bool, str]:
    """
    Check if the patch introduced unbalanced delimiters.
    If original was balanced, patched must be balanced.
    """
    delimiters = [("{", "}"), ("(", ")"), ("[", "]")]
    for open_char, close_char in delimiters:
        orig_open = orig.count(open_char)
        orig_close = orig.count(close_char)
        new_open = patched.count(open_char)
        new_close = patched.count(close_char)

        orig_delta = orig_open - orig_close
        new_delta = new_open - new_close

        if orig_delta == 0 and new_delta != 0:
            return False, (
                f"Delimiters '{open_char}{close_char}' became unbalanced.\n"
                f"Original: {orig_open} '{open_char}', {orig_close} '{close_char}' (balanced).\n"
                f"Patched:  {new_open} '{open_char}', {new_close} '{close_char}' (unbalanced: delta {new_delta:+d})."
            )
    return True, ""


def validate_syntax(content: str, suffix: str, mode: str) -> tuple[bool, str]:
    """Run lightweight language syntax gate."""
    ext = suffix.lower()
    
    if mode == "none":
        return True, ""

    if mode == "py" or (mode == "auto" and ext == ".py"):
        try:
            ast.parse(content)
            return True, "Python AST valid."
        except SyntaxError as e:
            return False, f"Python SyntaxError at line {e.lineno}: {e.msg}\n  {e.text or ''}"

    if mode == "json" or (mode == "auto" and ext == ".json"):
        try:
            json.loads(content)
            return True, "JSON parse valid."
        except json.JSONDecodeError as e:
            return False, f"JSONDecodeError at line {e.lineno}, col {e.colno}: {e.msg}"

    return True, ""


def find_anchors_and_replace(
    content: str,
    start_anchor: str,
    end_anchor: str,
    replacement: str,
    mode: str,
) -> tuple[str, str]:
    """
    Locates anchors and performs replacement.
    mode: 'inclusive' replaces start through end.
          'exclusive' replaces strictly between start and end.
    Returns (new_content, diagnostic_info).
    """
    start_matches = get_line_numbers(content, start_anchor)
    if len(start_matches) == 0:
        # Give helpful context: search for first line of start_anchor
        first_line = start_anchor.strip().split("\n")[0]
        first_line_matches = get_line_numbers(content, first_line) if first_line else []
        hint = ""
        if first_line_matches:
            hint = f"\nHint: First line of anchor ('{first_line[:40]}...') was found at line(s): {first_line_matches}. Check remaining lines or whitespace."
        raise ValueError(f"Start anchor not found in target file.{hint}")

    if len(start_matches) > 1:
        raise ValueError(
            f"Start anchor matched {len(start_matches)} times (lines: {start_matches}).\n"
            f"Anchor must be unique. Include 1-2 surrounding lines or comments to make it unambiguous."
        )

    start_idx = content.find(start_anchor)
    search_after = start_idx + len(start_anchor)

    # Validate end_anchor
    # Reject dangerously generic end anchors that cause accidental truncated matches
    generic_end_tokens = {"}", "};", "]", "];", ")", ");", "end"}
    if end_anchor.strip() in generic_end_tokens:
        raise ValueError(
            f"End anchor '{end_anchor.strip()}' is too generic and will match the first inner block boundary.\n"
            f"Include the preceding statement or return line (e.g. '  return result;\\n{end_anchor.strip()}') to make it specific."
        )

    end_rel_idx = content[search_after:].find(end_anchor)
    if end_rel_idx == -1:
        # Check if end_anchor exists anywhere in the file
        global_end_matches = get_line_numbers(content, end_anchor)
        if global_end_matches:
            raise ValueError(
                f"End anchor found at line(s) {global_end_matches}, but appears BEFORE the start anchor (line {start_matches[0]}).\n"
                f"Ensure the end anchor comes after the start anchor."
            )
        raise ValueError(
            f"End anchor not found anywhere after start anchor (line {start_matches[0]}).\n"
            f"Check spelling, indentation, or newline differences."
        )

    end_idx = search_after + end_rel_idx
    end_anchor_end = end_idx + len(end_anchor)

    start_line = content[:start_idx].count("\n") + 1
    end_line = content[:end_anchor_end].count("\n") + 1

    if mode == "inclusive":
        # Replace start_anchor ... end_anchor
        new_content = content[:start_idx] + replacement + content[end_anchor_end:]
        diag = f"Replaced lines {start_line} to {end_line} (inclusive of anchors)."
    else:
        # Replace only between start_anchor and end_anchor
        new_content = content[:search_after] + replacement + content[end_idx:]
        diag = f"Replaced content between line {start_line} and line {end_line} (exclusive of anchors)."

    return new_content, diag


def main():
    parser = argparse.ArgumentParser(
        description="smartenup patcher: Deterministic, safe code replacement engine."
    )
    parser.add_argument("--target", "-t", required=True, help="Path to target file.")
    parser.add_argument("--start", "-s", required=True, help="Exact start anchor string.")
    parser.add_argument("--end", "-e", required=True, help="Exact end anchor string.")
    parser.add_argument(
        "--patch-file", "-p", help="Path to file containing replacement content."
    )
    parser.add_argument(
        "--patch", help="Direct replacement string (alternative to --patch-file)."
    )
    parser.add_argument(
        "--delete", action="store_true", help="Delete the targeted section (empty replacement)."
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["inclusive", "exclusive"],
        default="inclusive",
        help="Replacement mode: 'inclusive' replaces anchors too (default); 'exclusive' replaces only between anchors.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and show unified diff without modifying the target file.",
    )
    parser.add_argument(
        "--no-backup", action="store_true", help="Do not create a .bak backup file."
    )
    parser.add_argument(
        "--allow-shrink",
        action="store_true",
        help="Allow file size reduction greater than --max-shrink threshold.",
    )
    parser.add_argument(
        "--max-shrink",
        type=float,
        default=35.0,
        help="Max allowable file size drop percentage (default: 35.0%%).",
    )
    parser.add_argument(
        "--syntax-check",
        choices=["auto", "py", "json", "brackets", "none"],
        default="auto",
        help="Pre-commit syntax validation mode (default: auto).",
    )

    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    if not target_path.exists():
        print(f"ERROR: Target file does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    # Determine replacement content
    if args.delete:
        replacement = ""
    elif args.patch_file:
        patch_path = Path(args.patch_file).resolve()
        if not patch_path.exists():
            print(f"ERROR: Patch file does not exist: {patch_path}", file=sys.stderr)
            sys.exit(1)
        replacement = patch_path.read_text(encoding="utf-8")
    elif args.patch is not None:
        replacement = args.patch
    else:
        print(
            "ERROR: One of --patch-file, --patch, or --delete must be specified.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Read original file
    raw_bytes = target_path.read_bytes()
    is_crlf = detect_crlf(raw_bytes)
    orig_content = raw_bytes.decode("utf-8", errors="replace")

    # Normalize newlines for deterministic indexing
    norm_content = normalize_newlines(orig_content)
    norm_start = normalize_newlines(args.start)
    norm_end = normalize_newlines(args.end)
    norm_replacement = normalize_newlines(replacement)

    # Perform replacement
    try:
        new_norm_content, diag = find_anchors_and_replace(
            norm_content, norm_start, norm_end, norm_replacement, args.mode
        )
    except ValueError as e:
        print(f"ERROR: Anchor resolution failed:\n{e}", file=sys.stderr)
        sys.exit(1)

    # Check 1: File shrinkage guard
    orig_len = len(norm_content)
    new_len = len(new_norm_content)
    if orig_len > 0 and new_len < orig_len:
        shrink_pct = ((orig_len - new_len) / orig_len) * 100.0
        if shrink_pct > args.max_shrink and not args.allow_shrink:
            print(
                f"ERROR: File size shrank by {shrink_pct:.1f}% ({orig_len} -> {new_len} chars), "
                f"exceeding max allowable drop of {args.max_shrink}%. "
                f"If intentional, pass --allow-shrink.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Check 2: Delimiter balance check
    if args.syntax_check in ("auto", "brackets"):
        balanced, msg = check_bracket_balance(norm_content, new_norm_content)
        if not balanced:
            print(f"ERROR: Syntax safety check failed:\n{msg}", file=sys.stderr)
            sys.exit(1)

    # Check 3: Language-specific AST check
    valid_ast, ast_msg = validate_syntax(
        new_norm_content, target_path.suffix, args.syntax_check
    )
    if not valid_ast:
        print(f"ERROR: Language validation failed:\n{ast_msg}", file=sys.stderr)
        sys.exit(1)

    # Generate unified diff
    diff_lines = list(
        difflib.unified_diff(
            norm_content.splitlines(keepends=True),
            new_norm_content.splitlines(keepends=True),
            fromfile=f"a/{target_path.name}",
            tofile=f"b/{target_path.name}",
            n=3,
        )
    )

    if not diff_lines:
        print("NOTICE: Patch produced identical content. No changes made.")
        sys.exit(0)

    print("=== UNIFIED DIFF ===")
    sys.stdout.write("".join(diff_lines))
    print("====================")
    print(f"Operation: {diag}")

    if args.dry_run:
        print("DRY-RUN COMPLETE: File not modified. All checks passed successfully.")
        sys.exit(0)

    # Restore line endings matching the original file
    if is_crlf:
        final_text = new_norm_content.replace("\n", "\r\n")
    else:
        final_text = new_norm_content

    # Atomic write
    temp_target = target_path.with_name(f"{target_path.name}.tmp")
    bak_target = target_path.with_name(f"{target_path.name}.bak")

    try:
        temp_target.write_text(final_text, encoding="utf-8")

        if not args.no_backup:
            try:
                bak_target.write_bytes(raw_bytes)
            except Exception as e:
                print(f"WARNING: Could not write backup file: {e}", file=sys.stderr)

        os.replace(temp_target, target_path)
        print(
            f"SUCCESS: Atomically updated '{target_path.name}' ({orig_len} -> {new_len} chars)."
        )
    except Exception as e:
        if temp_target.exists():
            temp_target.unlink(missing_ok=True)
        print(f"ERROR: Atomic disk commit failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
