---
title: "The LLM-driven browser paths read mappings the compiler never gates"
status: backlog
source: found at the e2e-selector-compile-gate ideation gate, 2026-08-01 — EM check 7 against the S1 exit condition
product: e2e-pipeline
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
design:
lane:
id: nabz0jraexvynv5bnzkms2kj
---

## Problem

`e2e-pipeline/S1`'s exit condition is "invalid selectors fail before browser startup".
[[e2e-selector-compile-gate]] (#88) makes that true on the **compiled** path only:
`bin/e2e-compile.js` → `parser.js` → the shared policy module.

It is not the only path to a browser. `agents/e2e-test-runner.md`,
`agents/e2e-flow-verifier.md`, and the walkthrough path are LLM-driven — they read the
mapping YAML directly and hand `selector:` values to `agent-browser` without ever going
through `compiler/`. A banned form on those paths reaches the browser exactly as it does
today, and the only thing standing in front of it is prose in the agent's own instruction
file, which is the enforcement model #88 exists to replace.

So after #88 lands, the sprint exit condition is met for one of at least three consumers,
and nothing owns the other two: #124 is the chord-narrowing question, #91 is multi-match
visibility semantics, and neither reaches this.

## Notes for ideation

- The obvious shape is for those agents to run the shared policy module as a preflight
  command over the mapping before the first browser call, and refuse on a finding — the
  module lands with #88, so this is wiring rather than new policy. Check whether these
  agents have Bash (the flow-writer deliberately does not, and it also never opens a
  browser, so it is likely out of scope here).
- The load-bearing question is what an LLM agent does with a refusal. A hard stop is only
  useful if the agent cannot talk itself past it; "the linter said no, but I'll try
  anyway" is the failure mode that makes the whole approach worthless, and it is not a
  failure mode the compiled path has.
- Whether the baseline from #88 applies here too, or whether these paths are strict, is a
  real decision — a runner that refuses on a grandfathered finding is more correct and
  less adoptable.
