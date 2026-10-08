#!/usr/bin/env python3
"""assert-env — validate required environment variables before a command runs.

Usage:
  assert-env DATABASE_URL PORT API_KEY
  assert-env --pattern PORT='[0-9]+' API_KEY='.+'
  assert-env --file .env.required
  assert-env --json DATABASE_URL REDIS_URL

NOTE: This tool may ship under a different name. See NOTES.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


def parse_pattern_arg(s: str) -> tuple[str, str]:
    """Parse VAR=PATTERN into (var_name, pattern). VAR alone means non-empty."""
    if "=" in s:
        var, pattern = s.split("=", 1)
        return var.strip(), pattern
    return s.strip(), None


def load_requirements_file(path: Path) -> list[str]:
    """Read var names (one per line) from a requirements file.

    Lines starting with # are comments. VAR=PATTERN syntax is supported.
    """
    lines = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def check_var(name: str, pattern: str | None) -> dict:
    """Check a single env var. Returns a result dict."""
    value = os.environ.get(name)
    result = {"name": name, "status": None, "detail": None}

    if value is None:
        result["status"] = "missing"
        result["detail"] = "not set"
    elif value == "":
        result["status"] = "empty"
        result["detail"] = "set but empty"
    elif pattern is not None:
        try:
            if re.fullmatch(pattern, value):
                result["status"] = "ok"
            else:
                result["status"] = "invalid"
                result["detail"] = f"value does not match pattern /{pattern}/"
        except re.error as exc:
            result["status"] = "invalid"
            result["detail"] = f"bad pattern: {exc}"
    else:
        result["status"] = "ok"

    return result


def format_table(results: list[dict]) -> str:
    """Render results as a human-readable table."""
    lines = []
    max_name = max(len(r["name"]) for r in results) if results else 10
    for r in results:
        status = r["status"]
        name = r["name"].ljust(max_name)
        if status == "ok":
            marker = "✓"
        else:
            marker = "✗"
        detail = f"  ({r['detail']})" if r["detail"] else ""
        lines.append(f"  {marker}  {name}  {status}{detail}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="assert-env",
        description="Validate required environment variables before a command runs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  assert-env DATABASE_URL PORT API_KEY
  assert-env --pattern PORT='[0-9]+' API_KEY='.+'
  assert-env --file .env.required
  assert-env --json DATABASE_URL REDIS_URL

Exit codes:
  0  All variables are set (and match patterns if given)
  1  One or more variables are missing, empty, or do not match their pattern
  2  Usage error
""",
    )
    parser.add_argument(
        "vars",
        nargs="*",
        metavar="VAR",
        help="Variable names to require (must be non-empty).",
    )
    parser.add_argument(
        "--pattern",
        nargs="+",
        metavar="VAR=PATTERN",
        default=[],
        help="Require VAR to match regex PATTERN. VAR alone means non-empty.",
    )
    parser.add_argument(
        "--file",
        metavar="PATH",
        help="Read required var names (one per line) from PATH.",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output results as JSON.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output; use exit code only.",
    )

    args = parser.parse_args()

    # Collect all checks: (var_name, pattern_or_None)
    checks: list[tuple[str, str | None]] = []

    # Positional vars: just check non-empty
    for v in args.vars:
        checks.append((v, None))

    # --pattern args: VAR or VAR=PATTERN
    for p in args.pattern:
        name, pattern = parse_pattern_arg(p)
        checks.append((name, pattern))

    # --file: each line is VAR or VAR=PATTERN
    if args.file:
        req_path = Path(args.file)
        if not req_path.exists():
            print(f"assert-env: file not found: {args.file}", file=sys.stderr)
            return 2
        try:
            file_entries = load_requirements_file(req_path)
        except OSError as exc:
            print(f"assert-env: cannot read {args.file}: {exc}", file=sys.stderr)
            return 2
        for entry in file_entries:
            name, pattern = parse_pattern_arg(entry)
            checks.append((name, pattern))

    if not checks:
        parser.print_usage(sys.stderr)
        print("assert-env: no variables specified", file=sys.stderr)
        return 2

    results = [check_var(name, pattern) for name, pattern in checks]
    failures = [r for r in results if r["status"] != "ok"]

    if args.as_json:
        if not args.quiet:
            output = {
                "ok": len(failures) == 0,
                "total": len(results),
                "passed": len(results) - len(failures),
                "failed": len(failures),
                "results": results,
            }
            print(json.dumps(output, indent=2))
    else:
        if not args.quiet:
            print(format_table(results))
            if failures:
                names = ", ".join(r["name"] for r in failures)
                print(f"\nassert-env: {len(failures)} variable(s) failed: {names}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
