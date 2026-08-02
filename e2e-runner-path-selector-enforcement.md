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

## Appetite (superseded — see the re-shape section)

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

The captain also reserved the choice of enforcement point. **This section lays out the field
and does not pick from it.** It is a scope escalation, not an ideation gate: every remaining
mandatory ideation output — appetite, ACs, the `design: required` decision, the E2E
determination, dispatch sizing, the doc diff — is a function of the reserved choice. The
`## Appetite` section above (3h / +50%) was sized for the disproved argv classifier and is
superseded; the correction-round brake should not read those numbers as current.

### 換句話說

**What breaks if this is wrong.** A test author writes a page-locator string that cannot
work. Nothing refuses it. Later a test reports "element not found" and someone debugs the
application for an afternoon before discovering the locator was never valid. The worse
version is a locator that silently satisfies an assertion through a fallback, and a green
test that proves nothing.

**How expensive to reverse.** D and F are one PR each and install nowhere, so reversing them
is one more PR. A and E each need an install in every consumer repo (A per clone, E per
repo), so reversing them means un-installing wherever they were adopted. B and C change how
two agents write files — the surface this entity has already been wrong about once — so
reversing those is an agent change plus whatever consumer repos adapted to it.

**What is actually being chosen.** Not "should bad selectors be refused" — that is settled.
It is **where the refusal lives**, and the places trade coverage against timing. The
git-level points (A, E) see all three populations — agent output, human hand-edits, and
verifier repairs — but only after the file is already written. The write-path points (B, C)
refuse before a browser ever runs, but see only what the agents write. The compile-path
point (F) sees every mapping on disk, but only when someone compiles and only as a warning
unless the #88 severity ruling is reopened.

### Reverse-recovery audit (against `origin/main` `0a1079c`)

| layer | verdict | evidence |
|---|---|---|
| Policy table | **WORKING** | `compiler/lib/selector-policy.js` — one table, dependency-free, read by three consumers: `compiler/compiler.js:11`, `bin/e2e-selector-baseline.js:37`, and `scripts/lint-mapping.sh` via `exec` |
| Per-file linter | **WORKING** | `scripts/lint-mapping.sh`, 54 lines, execs the policy module; exit codes documented at lines 6-9 |
| Compile-path enforcement | **WORKING** | #88 `checkSelectorPolicy`: blocks on elements the flow resolves, warns on the remainder **of the mappings a compiled flow loads** |
| Hook infrastructure on `Write` | **WORKING** | `hooks/hooks.json` registers a `PreToolUse` `Write` matcher. Scope nuance the options turn on: a plugin hook is per-user and per-agent-session, so it reaches any repo this user's Claude touches — and reaches neither a human editor nor CI |
| Agent-side prose on the write path | **EXISTS_BROKEN** | `agents/e2e-mapper.md:224-229` states the ban explicitly and nothing can refuse it. This row was in the pre-disproof audit and the first re-shape dropped it |
| Commit / CI wiring for the linter | **built, unwired** | `docs/ci-integration.md:242` recommends wiring `lint-mapping.sh` as a CI pre-flight; `git grep lint-mapping` over `origin/main` finds zero workflow and zero `.githooks` references |
| A fail-closed point on any write path | **MISSING** | the four scripts under `hooks/scripts/` all end `exit 0` — `pre-write-flow-guard.sh`, `pre-commit-e2e-check.sh:45`, `pre-commit-stale-check.sh:105`, `post-write-plan-e2e-check.sh:68`. Nothing enforces that a fifth would |
| Mapping files covered by any write hook | **MISSING** | `pre-write-flow-guard.sh:17-20` matches `*/.claude/e2e/flows/*.yaml`; `post-write-plan-e2e-check.sh:22-31` matches plan files. No hook matches `.claude/e2e/mappings/` |

Nothing here is greenfield. The linter exists, the hook channel exists and already ships to
consumer repos, and the CI recommendation is already written down. What is missing is a call
site that acts on the linter's verdict.

### One constraint already on record in this repo

`hooks/scripts/pre-write-flow-guard.sh` is a `PreToolUse` hook on `Write` that deliberately
warns instead of blocking, and its header says why:

> block is trivially bypassed via Bash, creating an adversarial dynamic where agents find
> workarounds instead of understanding why the /e2e-flow path is better.

That reasoning is sound **for a `Write`-only matcher** — a `cat > file` in Bash does not fire
a `Write` hook. It is not a general argument against blocking: `hooks.json` already registers
`Bash` matchers for the two pre-commit scripts, so a matcher covering both is existing
infrastructure, at the cost of inspecting arbitrary shell.

### What write-time enforcement buys, bounded

A banned selector on an element no step resolves, **in a mapping that some compiled flow
loads**, is already warned about by #88. For that population the delta is turning a warning
into a refusal, not making an invisible thing visible — and the warning is ephemeral stderr
on a manual compile that no CI runs, so "visible" means visible to whoever happens to compile.

Outside that population the delta is larger: a mapping **no flow loads at all** is never
scanned by the compiler and gets no warning today. That population demonstrably exists —
`pre-commit-e2e-check.sh:31` exists specifically to warn that mappings are present with no
flows.

### The options

**A — pre-commit hook, consumer-repo installed.** Catches agent output, hand edits and
verifier repairs alike, because all three end in git. Cannot refuse anything before commit,
so a whole browser session can run against a bad mapping first. Bounded claim: a banned
selector cannot enter a commit **from a clone that has installed the hook** (`git config
core.hooksPath`, which this repo's own `.githooks/pre-commit:3` documents as per-clone
opt-in) **and does not pass `--no-verify`**. Never runs in CI.
**Cost:** one hook script plus install docs; adoption surface per-clone.

**B — the two agents write mappings through an owned CLI that validates first.** The cheapest
option that refuses before a browser ever runs. Requires changing `agents/e2e-mapper.md` and
`agents/e2e-flow-verifier.md`, both of which hold the raw `Write` tool and write the file
directly (`e2e-flow-verifier.md:240,464` writes mappings back). Its weakness is measured, not
hypothetical: the EXISTS_BROKEN row above is the same instruction-only mechanism failing
today. Pairing it with a `Write`-matcher hook that refuses mapping paths converts it into a
mechanism; the `Bash` route is then the residual.
**Cost:** a new CLI plus edits to two agent definitions, and a hook if it is to be a
mechanism rather than an instruction; adoption surface none (ships with the plugin).

**C — B plus A.** Refusal at the moment of writing, git as the net for what routes around it.
Two surfaces to build and maintain. Contradicts the shipped precedent in one place: the
`Write` hook would block where the existing one warns.
**Cost:** B plus A; adoption surface per-clone for the A half.

**D — extend the shipped warn-only guard to mapping paths.** As stated in the first
re-shape this was mis-specified, and the correction cuts against it: `pre-write-flow-guard.sh`
**never inspects file content**. It checks for a `.flow-write-authorized` sentinel and, absent
one, prints a flow-specific message pointing at `/e2e-flow`. Adding a mapping glob would warn
on every mapping write regardless of selector content, with the wrong message, and would need
a sentinel producer on the `/e2e-map` side. Making it a *selector* warning means calling the
policy module — a different and larger change than "add a glob".
**Cost:** as described it is one glob and produces the wrong warning; as a selector warning
it is a rewrite of the guard; adoption surface none. It warns, it does not refuse.

**E — a mapping-lint CI job, shipped through the existing template mechanism.** The plugin
already ships `templates/browser-e2e.yml` as its CI delivery mechanism and
`docs/ci-integration.md:242` already recommends wiring `lint-mapping.sh` as a pre-flight
gate. Bounded claim: a banned selector cannot **merge** into a repo that has adopted the
template **and marked the job a required check** — `templates/browser-e2e.yml:3` is
`# USAGE: Copy this file to .github/workflows/browser-e2e.yml`, and nothing in it establishes
branch protection, so an unadopted or unrequired job is advisory in the same way #88's
ephemeral stderr is. Residual: the workflow file is repo-writable by the same agent it gates.
It is also the latest point in the field — it refuses after the commit, in the pull request,
so a bad selector can be written, exercised and pushed before anything says no.
**Cost:** one template edit plus a docs change; adoption surface per-repo.

**F — widen the existing compile-time gate to every mapping on disk.** The traversal already
exists and is already wired: `selector-policy.js` exports the file-scope `scanMappingText`,
and `compiler/compiler.js:54` `checkSelectorPolicy(mappingSources, referencedElements,
baseline)` already consumes a source list. Today that list is the mappings a compiled flow
loads, so a mapping no flow references is never scanned. Widening the list to the mappings
directory needs no consumer install, no hook, and no new call site — it changes what is
passed in. It answers the captain's stated reason for the cut directly: a selector written
and never exercised is exactly what a directory-wide scan catches. Its limit is timing —
it fires when someone compiles, and nothing in CI compiles today, which is the same
adoption gap E closes.
**As specified this widens the WARNING channel only.** Blocking severity keys on the
elements a flow resolves — `compiler.js:113-130` builds `blocking` from
`scanElements(referencedElements)` and the warning stream from `scanElements(allRecords)`
minus that set — so an unexercised banned selector would get stderr, not a refusal. Making F
refuse means revisiting the two-severity split the captain ruled on at #88, whose reasoning
is in `compiler.js:41-52`: whole-file blocking reds every flow that loads a mapping carrying
unrelated legacy debt. That is plausibly the largest cost in the field, and it is a decision
already made the other way.
**Cost:** as a warning, smallest in the field — a read-and-parse loop over the mappings
directory plus a failure policy for an unrelated malformed mapping; adoption surface none.
As a refusal, it reopens the #88 severity ruling.

**Null — accept the status quo.** Listed so the field is not five build options and no
alternative. Today a banned selector written and never exercised produces no refusal and, in
an unreferenced mapping, no warning either. The stated harm is an afternoon of debugging the
application instead of the locator. Whether that clears any of the costs above is the
captain's to weigh, not the shaper's to presume.

**The options combine.** C is already A+B. F+E is the other natural pair — F sees every
mapping, E supplies a run that is not "whoever happens to compile" — and each closes the
other's stated limit. Named for completeness; which pairing, if any, is the captain's.

### What is NOT decided here

Which option, and therefore every ideation output that depends on it. The captain reserved
this on 2026-08-02.

### Owed back-port

`docs/ci-integration.md:209` says the policy table has two consumers; it has three. Filed as
its own seed, [[ci-integration-consumer-count-backport]], rather than recorded here — a debt
line inside an entity that will eventually be archived has no owner and no due date.

### Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a **hidden
assumption** again: that the agents' writes are the population. Mappings are also hand-edited
by humans and written by whatever future skill needs one, and only the git-level points — A
and E — see those. An option chosen for the agent path alone will be measured against a
population it does not cover.

### Provenance of this re-shape

The first version of this section omitted option E and dropped two audit rows. An EM review
returned it, and every `file:line` that review cited was checked against `origin/main`
`0a1079c` before being adopted here rather than taken on the reviewer's word: the CI template
exists, `.githooks/pre-commit:3` documents the per-clone opt-in, `ci-integration.md:209` does
undercount the policy consumers, `lint-mapping.sh` appears in zero workflows and zero
`.githooks`, and both verifier write-back sites are real. The policy module's three consumers
were counted directly.

### Residual class, recorded so the field can close

Two things no option in this field reaches, recorded rather than iterated on:

- A human hand-edit that skips both the git hooks and CI is outside A, B, C, D, E and F.
- `eval` and `@ref` remain outside every option, for the reason recorded in the spike above:
  the selector is not a selector by the time it reaches the browser.

These are properties of the chosen frame, not defects in it. The field is presentable.
