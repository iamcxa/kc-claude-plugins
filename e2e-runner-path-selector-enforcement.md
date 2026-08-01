---
title: "The LLM-driven browser paths read mappings the compiler never gates"
status: ideation
source: found at the e2e-selector-compile-gate ideation gate, 2026-08-01 — EM check 7 against the S1 exit condition
product: e2e-pipeline
sprint: S1
started: 2026-08-01
completed:
verdict:
worktree:
issue: "126"
pr:
design: required
lane: main
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

## The shape changed once the code was read — there is a real chokepoint

The backlog note assumed the fix was "have each agent run a preflight lint over the
mapping before its first browser call, and refuse on a finding", and named the
load-bearing risk itself: **a hard stop is only worth building if the agent cannot talk
itself past it.** A `STOP if the linter says no` instruction in three markdown files is
prose enforcement — which is the model #88 exists to replace, re-applied to the paths #88
could not reach. It would have been the wrong build.

Reading the code found a chokepoint that is not prose. Every browser operation on all
three paths goes through the **owned browser runtime**, `bin/e2e-browser-runtime.js`:

```
browser_command: node "{{browser_runtime}}" --run-id … --app … --receipt …
```
(`agents/e2e-test-runner.md:57-59`; the same prefix in `e2e-flow-verifier` and the
walkthrough path.) That file carries an explicit `ALLOWED_COMMANDS` allowlist
(`bin/e2e-browser-runtime.js:10-40`) covering `click`, `fill`, `is`, `check`, `uncheck`,
`hover`, `press`, `select`, `type`, `get`, `find` — and the selector arrives as an argv
element on the way through.

And bypassing it is **already prohibited for an unrelated reason the agents need**:
"Bare `agent-browser` commands are prohibited: they can attach to the default daemon or a
different Chrome-based browser. The runtime pins Chrome for Testing, an owned daemon…"
(`agents/e2e-test-runner.md:73-76`). So an agent that routes around the gate also loses
the pinned browser and the owned namespace, and its run stops being trustworthy for
reasons that have nothing to do with selectors.

## Proposed approach — refuse at the point of use, not at a preflight

Classify the selector argument of each selector-taking subcommand inside the runtime,
using the `compiler/lib/selector-policy.js` table #88 landed, and refuse before invoking
`agent-browser`.

**This is a strictly tighter scope than anything the compiled path can do.** The compiled
gate blocks on "selectors this flow resolves", because a compiler must decide ahead of
time. The runtime decides at the moment of use, so it blocks exactly the operation that
would break and nothing else. There is no mapping to look up, no whole-file question, and
— see below — no baseline.

**No baseline on this path, and the reason is evidence rather than preference.** The three
surviving classes do not work here *today*: `>> nth=`, `:has-text(` and a
`find role|text|label|testid …` chain handed literally to `agent-browser` return
false / not-found / timeout, which `CLAUDE.md` § Selector Priority already documents and
PR #123 re-probed live against agent-browser 0.32.0. So refusing them converts a silent
wrong answer into a loud one and grandfathers nothing that works. A baseline here would be
an escape hatch, and an escape hatch is precisely how a gate gets talked past — the thing
this entity exists to prevent.

## What is NOT decided yet, and goes to the gate

1. **`e2e-mapper`.** It both produces selectors and drives a browser. Gating it means a
   mapper that emits a banned form discovers it immediately, which is good — but it may
   also legitimately *probe* one while exploring. Include or exclude, on record.
2. **`eval`.** A selector can reach the DOM inside an `agent-browser eval` string, which
   this gate cannot see without parsing JavaScript. That is a named residual, not a hole to
   close: it is the same class as `scanMappingText` not reading block scalars, and the same
   answer — bound it and say so.
3. **Failure shape.** A non-zero exit with the class and the replacement, versus a
   structured refusal the calling agent is told to surface. The agents are LLMs; the
   message is the enforcement surface's usability.

## Reverse-recovery audit (against `origin/main` `8634d89`)

| layer | verdict | evidence |
|---|---|---|
| Policy table | **WORKING** | `compiler/lib/selector-policy.js`, landed by #88, dependency-free and already read by two consumers |
| Owned runtime as a chokepoint | **WORKING** | `bin/e2e-browser-runtime.js:10-40` allowlist; every agent prefix routes through it; bare `agent-browser` already prohibited |
| Policy invoked on that path | **MISSING** | `grep -n 'selector-policy' bin/e2e-browser-runtime.js` → no hit |
| Agent-side prose | **EXISTS_BROKEN** | `agents/e2e-test-runner.md:808` etc. state the ban and nothing can refuse it — the same defect #88 fixed one layer down |

One missing seam, and the repair is wiring an existing module into an existing chokepoint.
No greenfield.

## Appetite

**Estimate: 3 hours.** Smaller than #88 by construction: the table, its tests and its
diagnostics already exist; this adds a call site and its refusal path.
**Tolerance: +50% (4.5h).** Past that, re-cut to `click`/`fill` only — the two subcommands
where a banned form is unambiguously broken — and defer the rest.

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a **hidden
assumption**: that the three consumers really do route every browser call through the
owned runtime. The prose says they must and the runtime is built for it, but "the agents
are instructed to" is not "the agents do", and an agent that emits a bare `agent-browser`
line would sail past this gate exactly as it sails past the prose today. **The first
implementation task is therefore to verify the routing empirically** — drive one real run
per consumer and confirm every browser invocation carries the runtime prefix — not to
write the classifier.
