---
id: gzh8xe17fgnjpc03qk19n3xx
title: Structured compiler diagnostics an agent can repair from
status: backlog
source: captain note — e2e-pipeline agent-native audit, 2026-07-25 (session analysis + agy cross-model review)
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

The compiler emits nothing a program can consume. There is no `--json`; errors are prose on
stderr (`ERROR: Step 'x': element 'submit_btn' not found in mapping`) and the exit code is
0 or 1 with no per-class distinction. There is also no fuzzy matching anywhere — grepping
`compiler/` for levenshtein, "did you mean", closest, or suggest returns zero hits. So an
agent that hits an unknown-element error has no path to the fix except reading the entire
mapping YAML back into context to discover the real name was `submit_button`. The
information needed to repair is sitting in the symbol table the resolver just built, and is
thrown away with the error.

The cost of that missing structure is visible in the skill layer: roughly 100 of the 202
lines of `skills/e2e-compile/SKILL.md` are prose instructions teaching the agent how to
re-format the compiler's human prose into different human prose — a presentation layer for
a machine talking to a machine.

Shape to decide at ideation: `--json` emitting `{ok, output, stats, errors: [{code,
step_id, field, got, candidates[], message}]}`, with nearest-match candidates drawn from
the symbol table for unknown element/page, and for a rejected expect the list of supported
expect shapes. Then delete the reformatting prose from the compile skill.

## Notes for ideation

- The value AC should be measured, not asserted: repair a flow carrying three seeded errors
  with and without `--json`, and record both the token cost of the repair loop and whether
  the agent had to re-read the mapping file at all. That is a baseline that can move the
  wrong way.
- That measurement is only meaningful after [[e2e-typed-operands]] closes the silent-pass
  hole — otherwise the "before" case can succeed by not failing.
- Error codes should come from [[e2e-schema-contract]]'s vocabulary rather than a private
  enum invented here.
