---
id: a2f9wsqt63eac4xe7hzfxa5g
title: Close the last --json escape hatch — Commander's own arg-parse output
status: backlog
source: residual accepted at [[e2e-json-diagnostics]]'s validation gate, 2026-07-26; carries a working prototype and one correction to the record
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

[[e2e-json-diagnostics]] guarantees that `--json` puts exactly one JSON document on stdout. Three
violations were found and fixed. A fourth class survives: Commander's own argument-parse and help
paths, which never reach the action handler where the fix lives.

    --json --bogus-flag                  -> exit 1, 0-byte stdout
    --json <dash-leading-flow-name>      -> exit 1, 0-byte stdout
    --json --help                        -> exit 0, 1192 bytes of prose on STDOUT

**Correcting the record, because this entity was nearly filed on a false premise.** The validation
report states `--json --help` "emits no document (exit 0, help to stderr)". Measured: stdout 1192
bytes, stderr 0 bytes. It is not an absence — it is prose on the contract channel, which is AC-1's
falsification clause verbatim, and it exits 0 so a consumer reads success before parsing help text.
That makes this class strictly worse than recorded, and it is why the deferral needs an owner
rather than quiet acceptance.

## What is already proven, so it is not re-derived

- A `--json`-gated `exitOverride` is roughly 14 lines, leaves non-`--json` behaviour byte-identical
  (verified), and passes 650/650 in a scratch copy.
- **Inference, not a finding** — `exitOverride` alone is likely insufficient for the `--help` case,
  because Commander writes help through its output writer *before* the exit path fires, so
  intercepting the exit does not unwrite stdout; `configureOutput` / `writeOut` redirection is
  probably also needed. **Disproof hook, one command:** run the existing scratch prototype with
  `--json --help` and check whether stdout is empty. If it is, this inference is wrong and the
  entity is simpler than described.

## Why it was deferred rather than fixed

Reachability is a different class from the three that were fixed: those were reachable from a
*correct* skill invocation against a hostile environment, whereas this needs a malformed argv,
which means the caller's own command template is already broken. Symptom identity is not trigger
identity. The fix also crosses into CLI-wide error handling for non-`--json` callers, which the
captain's scope ruling on that entity explicitly excluded.

## The design question this entity must answer first

What should `--json --help` mean? A help document has no natural JSON shape, and "emit nothing"
conflicts with the guarantee. Decide that before writing code — it is the reason the class has an
irreducible tail rather than a mechanical fix.
