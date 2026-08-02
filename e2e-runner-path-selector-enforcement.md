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

## Spike result — the pre-mortem fired, on a different hidden assumption

The pre-mortem above named the category correctly and the assumption wrongly. It worried
that an agent would emit a bare `agent-browser` line and sail past the gate. Measured, that
does not happen. What does happen is that the selector never arrives at the gate at all.

### What was measured

A shim was shadow-installed at the resolved `agent-browser` binary path
(`~/.npm-global/bin/agent-browser`) so it records invocations reaching *that* path and the
command line of the spawning process without depending on `PATH`, then execs the real
binary. A caller that resolved a different install would sit outside it; none was observed,
and no second strategy was run to look for one. A call counts as routed only when its
immediate parent process **is**
`node <path>/e2e-browser-runtime.js`, anchored on `node <path>` — matching the runtime path
anywhere in the ancestor chain false-passed a bare control call twice, because a shell whose
command line merely quotes that path matches. Both directions were exercised before the
probe was trusted: a bare call must read BYPASS, a runtime-mediated call must read routed.

One real `e2e-test-runner` run, carlove `gate-smoke-all-pages`, 10 steps, 19 expectations,
all passing:

- 147 `agent-browser` invocations, 145 routed, 2 bypasses.
- Both bypasses are `bin/e2e-trace-contract.js` running `--version` and `trace --help`.
  Capability probes, no selector argument.
- In this run, the LLM runner improvised no bare call. One run is a sample; the claim is
  about these 147 invocations, not about the agent in general.

### The disproof

Routing is not the invariant this entity needs. Of the four calls in that run that consumed
an element:

```
fill e12 admin@bw.tw
fill e14 pwd123
click e9
is visible 'role=heading[name=/每日看板/]'
```

`e9`/`e12`/`e14` are snapshot-assigned refs. `secha-office.yaml` carries 244 `selector:`
entries and none has the form `e<digits>` — they are `role=textbox[name="電子郵件"]` and
similar. Three of the four resolved through a snapshot first; exactly one selector reached
argv, and it matches mapping entry 6 verbatim.

**A runtime argv classifier would have inspected one selector in a ten-step flow and seen
none of the click/fill operations.** This is not an accident of this flow. What makes it
hold is agent-browser's behavior, live-probed against 0.32.0 in PR #123: `role=…` and
`text=…` handed literally to `click|fill` return false, so the agents go through
snapshot→ref to get a working locator. `CLAUDE.md` § Selector Priority records that probe
result; the probe, not the record, is what makes it true. The Proposed approach assumed the
selector rides on the argv of the operation that uses it, and on the action path it does
not.

### Corrections to what is recorded above

- **Reverse-recovery audit, row 2.** "Owned runtime as a chokepoint — WORKING" is accurate
  about *transport* and wrong as a premise for *selector* enforcement. Superseded by this
  section; the allowlist it cites is a command allowlist, not a command grammar, so there is
  no per-command schema saying which argument is a selector. Scanning every argv element
  false-positives on fill values, wait text, URLs and JavaScript (`fill e12 admin@bw.tw` —
  the value is an argument); scanning a fixed position misses `is visible` and `get count`.
- **The consumer inventory is short by one.** `skills/ui-verify/bin/run.js:94` reads a
  mapping, spawns `agent-browser` directly, passes selectors to click/fill, and embeds check
  selectors inside `eval`. It is a second mapping-selector consumer this gate cannot see.
- **`eval` and `@ref` are larger than "a named residual".** The claim this shape can support
  is narrow: known-broken strings are not forwarded to native selector-taking CLI
  operations. It cannot support "these consumers cannot silently use banned selector
  semantics."
- **Open question 1 (`e2e-mapper`) is unchanged by this spike and remains open.** The
  measurement exercised `e2e-test-runner`; `e2e-mapper` was not run, so nothing here bears
  on it. Note for whoever re-cuts: a `--consumer`-style exemption is caller-supplied, and
  the runtime is not given anything that would let it authenticate the caller independently.
  Gating a consumer also says nothing about mapper *output* — a banned selector written into
  a mapping and never exercised is not reached by any runtime check.

### Provenance

The disproof came from an independent cross-model read of this repository (Codex,
read-only), which rejected the approach on the snapshot→ref ground before the argv data was
re-examined. The measurement above is this session's; the reading of it is not.

The negative result reported earlier in this session — "147 invocations, 0 bypasses" — was
a Proof Policy 7 miss on my part: it was an absence claim whose searched population
(invocations that route) was never the population the gate cares about (selectors that
arrive). One search strategy was a sample, not a census.

### Effort against the appetite

Approximately 1.5h of the declared 3h estimate went to this spike — building the probe,
validating it in both directions, one measured consumer run, the cross-model read, and the
argv re-analysis. A further ~1h went to an unplanned blocker outside this entity's scope:
the owned runtime could not open a browser at all for any app name of ten characters or
more, fixed and merged as PR #135, which is why the first measurement attempt produced only
runtime preflight calls.

So roughly 1.5h of the 3h remains, and the tolerance (+50%, 4.5h) is untouched. The
remaining budget was sized for building a classifier that this spike has now shown will not
see what it was meant to gate, so the number is reported for the re-cut rather than
proposed as a plan.

### What this does not decide

Replacing the point-of-use classifier with a different mechanism is a scope re-cut, and
Gate Authority puts scope on the captain alone. This section records the disproof and stops
there. The approach on record is now known-insufficient rather than superseded, and the
entity stays in `ideation` pending that ruling.

## Re-shape — the captain cut this to write-time enforcement

Captain ruling, 2026-08-02: stop defending the moment of use and defend the moment the
selector is **written**. Reason given: it is cheap, reversible, and the only thing that
catches a banned selector written into a mapping and never exercised. Accepted cost: it does
not stop a banned selector already sitting in a mapping from being used.

This section re-shapes against that ruling and **stops at the options**. The captain
reserved the choice of enforcement point (2026-08-02) and this does not make it.

### Reverse-recovery audit (against `origin/main` `0a1079c`)

| layer | verdict | evidence |
|---|---|---|
| Policy table | **WORKING** | `compiler/lib/selector-policy.js` — one table, dependency-free, read by two consumers |
| Per-file linter | **WORKING** | `scripts/lint-mapping.sh` (54 lines) execs the policy module; documented exit codes |
| Compile-path enforcement | **WORKING** | #88: blocks on flow-resolved selectors, warns on the rest of the file |
| Hook infrastructure on `Write` | **WORKING** | `hooks/hooks.json` registers a `PreToolUse` `Write` matcher; ships and installs with the plugin, so it reaches consumer repos |
| A fail-closed point on any write path | **MISSING** | every shipped hook `exit 0`s — see below |
| Mapping files covered by any write hook | **MISSING** | `pre-write-flow-guard.sh` matches `*/.claude/e2e/flows/*.yaml` only; mappings are not matched |

Nothing here is greenfield. The linter exists, the hook channel exists and is already
delivered to consumer repos. What is missing is a call site that refuses.

### The constraint that decides this, and it is already on record here

`hooks/scripts/pre-write-flow-guard.sh` is a `PreToolUse` hook on `Write` that **deliberately
warns instead of blocking**, and its header says why:

> block is trivially bypassed via Bash, creating an adversarial dynamic where agents find
> workarounds instead of understanding why the /e2e-flow path is better.

`pre-commit-e2e-check.sh` likewise ends `exit 0`. **Every hook this plugin ships is
advisory.** So the repo has already made this exact call once, in the same problem shape,
and chose cooperative warning.

That prior reasoning is sound *for a Write-only matcher* — a `cat > file` in Bash does not
fire a `Write` hook. It is not a general argument against blocking: a matcher covering both
`Write` and `Bash` closes that route, at the cost of inspecting arbitrary shell.

### What write-time enforcement actually buys, stated honestly

A banned selector written into a mapping and never exercised by any flow is **already
warned about** at compile time — #88 warns on the whole-file scope. It is visible today and
unenforced, not invisible. The delta this work buys is turning that warning into a refusal,
and reaching selectors on paths that never compile at all.

### The options, with what each can and cannot catch

**A — pre-commit hook, consumer-repo installed.** Banned selectors cannot enter a commit.
Catches hand edits, mapper output and verifier repairs alike, because all three end in git.
Cannot catch anything before commit, so an agent runs a whole browser session against a bad
mapping first. Bypassable with `--no-verify`, which is a human choice rather than an agent
improvisation. Cheapest of the three; nothing about the agents changes.

**B — the two agents write mappings through an owned CLI that validates first.** A real
chokepoint at the moment of writing, and it is the only option that refuses before a browser
ever runs. Requires changing `agents/e2e-mapper.md` and `agents/e2e-flow-verifier.md` — both
currently hold the raw `Write` tool and write the file directly. Its weakness is exactly the
one this entity exists to attack: telling an agent in markdown to use the CLI is prose
enforcement, and an agent that writes with `Write` anyway sails past. Pairing it with a
`Write`-matcher hook that refuses mapping paths converts that into a mechanism, and then the
`Bash` route is the residual.

**C — both.** The CLI refuses at the moment of use, the hook catches what routes around it,
and pre-commit catches hand edits. Highest coverage, three surfaces to build and maintain,
and it contradicts the shipped precedent above in one place: the `Write` hook would have to
block where the existing one warns.

**D — extend the existing warn-only guard to mapping paths.** Smallest possible change: add
a mapping glob to `pre-write-flow-guard.sh`. Consistent with the shipped precedent, one file
touched. But it is a warning, and a warning is what #88 replaced. It would make the class
visible at write time without making it refusable — worth stating because it is the honest
floor, not because it satisfies the original problem.

### What is NOT decided here

Which option. The captain reserved it. Each has a different appetite, and B and C both
change agent definitions, which is the surface this entity has already been wrong about
once.

### Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a **hidden
assumption** again: that the agents' writes are the population. Mappings are also hand-edited
by humans and written by whatever future skill needs one, and only the git-level point sees
all of those. An option chosen for the agent path alone will be measured against a population
it does not cover.
