# assert-env

**Validate required environment variables before a command runs.**

Exit 0 if everything is set. Exit 1 with a clear list if anything is missing, empty, or doesn't match a pattern. Works as a guard at the top of scripts, Makefiles, or CI pipelines.

> **Name note:** This tool may ship under a different name (`env-check` v2, `require-env`, or similar). See NOTES.md.

---

## Install

Single file, no dependencies. Copy to your `$PATH`:

```bash
cp assert-env.py ~/.local/bin/assert-env
chmod +x ~/.local/bin/assert-env
```

---

## Usage

```bash
# Require vars to be set and non-empty
assert-env DATABASE_URL PORT API_KEY

# Require vars to match a regex pattern
assert-env --pattern PORT='[0-9]+' API_KEY='.{20,}'

# Read var names from a file (one per line, # comments ok)
assert-env --file .env.required

# JSON output for CI scripts
assert-env --json DATABASE_URL REDIS_URL

# Exit code only — no output
assert-env --quiet DATABASE_URL && echo "ok"

# Mix positional + file + pattern
assert-env DATABASE_URL --file .env.required --pattern LOG_LEVEL='debug|info|warn|error'
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All variables are set and match patterns |
| 1 | One or more variables are missing, empty, or invalid |
| 2 | Usage error (no vars given, file not found, etc.) |

---

## `.env.required` File Format

One var name per line. Comments start with `#`. Pattern syntax (`VAR=PATTERN`) is supported.

```
# Required for database connectivity
DATABASE_URL
DB_POOL_SIZE=[0-9]+

# Auth
API_KEY
JWT_SECRET
```

---

## Output

```
  ✓  DATABASE_URL  ok
  ✗  PORT          missing  (not set)
  ✗  API_KEY       empty    (set but empty)
  ✗  LOG_LEVEL     invalid  (value does not match pattern /debug|info|warn|error/)

assert-env: 3 variable(s) failed: PORT, API_KEY, LOG_LEVEL
```

---

## JSON Output

```json
{
  "ok": false,
  "total": 4,
  "passed": 1,
  "failed": 3,
  "results": [
    {"name": "DATABASE_URL", "status": "ok", "detail": null},
    {"name": "PORT", "status": "missing", "detail": "not set"},
    {"name": "API_KEY", "status": "empty", "detail": "set but empty"},
    {"name": "LOG_LEVEL", "status": "invalid", "detail": "value does not match pattern /debug|info|warn|error/"}
  ]
}
```

---

## What it doesn't do

- Does not read `.env` files (use `envrun` for that)
- Does not check `.env.example` files (use the original `env-check` for that)
- Does not set or export variables
- Does not run a command (pair with `env-check VAR && your-command`)

---

## Earn model

Free.
