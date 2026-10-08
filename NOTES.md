# assert-env — Build Notes

## Status

Built 2026-09-01 (Week 44). 33 tests, all passing. Stdlib only.

**Name pending Cory's call.** The original `env-check` (Week 1, April 2026) reads `.env.example` and checks against the live env. This tool does the opposite: you name vars explicitly on the CLI or in a requirements file, and it validates them. Different interface, different use case — but same name as originally planned. Cory needs to pick: (a) rename to `require-env`/`assert-env`, (b) ship as `env-check` v2 superseding the old one, or (c) merge the two concepts. Built under `assert-env` as provisional name.

---

## Design Decisions

**Why `re.fullmatch` not `re.search`?**
Pattern intent is always "the whole value matches this shape." Partial matches (`PORT=[0-9]+` passing on `"8080abc"`) would be surprising and wrong for validation. Full match is the safe default.

**Why does empty string fail even for `.*` patterns?**
Empty string is special-cased before pattern matching. An empty var is almost never intentionally set — it's usually a misconfigured env. If you truly want to allow empty, don't list the var. This is the same philosophy as `.env` validators generally.

**Why not run a command directly (like `env-check VAR cmd args`)?**
That scope creep makes this tool harder to compose. Users already have `&&` and script wrappers. The job of this tool is validation, not execution.

**Why no `.env` file reading?**
That's `envrun`'s job. This tool validates what's actually in the live environment. Mixing in file loading conflates two different problems. Users who want to load-then-validate can do: `envrun --file .env -- assert-env DATABASE_URL`.

---

## What went well

- Test-first approach: wrote the interface design, then tests, then code. No surprises.
- The `parse_pattern_arg` helper made the `VAR=PATTERN` syntax clean in all three input paths (positional, `--pattern`, `--file`).
- Column alignment in output landed naturally.

## What might need adjustment

- The `--pattern VAR` form (no `=`) currently means "non-empty" — but it's in `--pattern` which might confuse users who expect a pattern. Could split into two flags. Hold for Cory feedback.
- Could add `--strict` to fail on *any* unset var (including those set to a value that isn't a valid value for the context). Currently "set and non-empty" is the baseline.

---

## 2026-09-01

Built skeleton, tests, README in one Build session. 33 tests, 0 failures. Tool is complete pending name decision.
