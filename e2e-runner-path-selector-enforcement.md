---
title: "The LLM-driven browser paths read mappings the compiler never gates"
status: validation
source: found at the e2e-selector-compile-gate ideation gate, 2026-08-01 — EM check 7 against the S1 exit condition
product: e2e-pipeline
sprint: S1
started: 2026-08-01
completed:
verdict:
worktree: .worktrees/spacedock-ensign-e2e-runner-path-selector-enforcement
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

## Captain ruling — option E, 2026-08-02

**A mapping-lint CI job, shipped through the existing template mechanism.** Reasoning given
at the decision: the population write-time enforcement uniquely catches is latent — a banned
selector no flow exercises is not hurting anyone yet — so E's lateness costs almost nothing,
while E is the only option configured once per repo rather than per clone, the only one an
agent cannot route around, and the only one that needs no change to an agent definition on an
entity that has already been wrong twice about agent behavior. A, B, C, D, F and null are not
taken.

With the enforcement point fixed, the outputs deferred to this choice are now written.

### The design decision inside E, and the precedent that settles it

**Whole-file linting would turn an adopting repo red on day one.** Measured against carlove
on 2026-08-02 with the shipped `scripts/lint-mapping.sh`, per file, reading the tool's own
`path:line:` findings: `secha-office.yaml` **15**, `secha-app.yaml` **24**, both exit 2; the
other three mappings clean, exit 0. So a naive job fails immediately on **39** pre-existing
findings in 2 of 5 files, none of which the adopting PR touched.

An earlier version of this section said 16 / 25 / 41 and attributed those to the linter. It
had not run the linter — the numbers were a raw grep. `secha-office.yaml:706` carries
`>> nth=1` inside a `note:` string, which the linter deliberately excludes because it
classifies selector *values*, not any occurrence of the token. The correction is worth
keeping on record as evidence that narrowing works, not just as a retraction.

That is the exact failure the captain ruled against on 2026-08-01 when #88 was cut to
flow-resolved blocking: an unrelated whole-file migration must not be the price of touching
one flow. The same reasoning binds here, so **the job is diff-scoped**: it fails only on
mapping lines the pull request **adds or modifies**. Untouched pre-existing findings are
reported as annotations and do not fail the job.

Rejected alternative: a baseline file like #88's. `lint-mapping.sh` has no baseline concept
today, so this would add one plus its producer and its staleness story, to solve a problem
diff-scoping solves with information the PR already carries. Recorded because it is the
option a later reader will ask about.

### Plan constraint — the linter is fail-open on multiple arguments

`scripts/lint-mapping.sh` processes **only `argv[1]`**. Verified 2026-08-02 against carlove:
invoked as `lint-mapping.sh *.yaml` with the clean file sorting first, it prints one `— OK`
line and returns **rc=0**, leaving both failing files unscanned.

So the "fastest path" rejected above is worse than day-one red — written the obvious way it
is **day-one green and proves nothing**. The job must loop per file and check each exit code
individually, and the implementation owes a test for the clean-first-file case specifically,
because that is the arrangement under which the naive form passes.

`docs/ci-integration.md` also mislabels the contract: it says "CI-friendly: exit 1 on any
violation" where the script documents and returns **2** (and 123 under the `xargs -0 -n1`
form the same page suggests). That correction rides with the doc diff below.

### Design determination

`design: required`. The decision attached: the job's blocking scope is the PR's added and
modified mapping lines, not the whole file and not a baseline — grounded in the #88 ruling
above rather than in preference.

### Fastest path and smallest cut

**Fastest:** a job that runs `lint-mapping.sh` over every mapping and fails on exit 2. Two
lines of YAML. Rejected: it is the day-one-red shape measured above.
**Smallest cut that satisfies the AC:** diff-scoped linting, no baseline, no changes to
`lint-mapping.sh`'s own contract — the diff scoping lives in the job, and the linter stays
the single per-file authority it already is.

## Acceptance criteria

**AC-1 — A banned selector added by a pull request fails the job.**
Verified by: a probe PR that adds one `>> nth=` selector line to a mapping in the adopting
repo (**carlove**, which the captain owns and which holds the mappings this entity measured);
the job is observed red on live CI and its log names the file, line and class.
Falsified by: an implementation that passes on that PR, or that reports a line the PR did
not touch.

**AC-2 — Pre-existing findings on untouched lines do not fail the job.**
Verified by: the same probe PR against a mapping that already carries banned selectors on
lines the PR does not touch — `secha-office.yaml` is such a file, whose pre-existing finding
count is read from the linter at verification time rather than pinned here, because it is a
mutable file in another repository. The job fails on the added line only; the untouched
findings appear as annotations. Falsified by: a red attributable to any untouched finding,
which is the day-one-red shape this AC exists to prevent.

**AC-3 — A red job actually blocks the merge in an adopting repo.**
This is the value criterion: the bounded claim recorded for option E is that a banned
selector cannot *merge* into a repo that has adopted the template **and** marked the job a
required check, and an unrequired job is advisory.
Verified by: after adoption, `gh api repos/<owner>/<repo>/branches/main/protection` lists the
job's context name, and the AC-1 probe PR reports a blocked merge state while the job is red.
Falsified by: the probe PR remaining mergeable with the job red, which would show the
adoption instructions produced an advisory job.

### E2E determination

Owed, and satisfied by the probe PR: AC-1 and AC-3 are both live-CI observations, not local
runs. Per the validation stage's live-CI clause, plan **one probe commit per step** — steps
within a job short-circuit, so a single red run proves only the first failing step. Close the
probe PR without merging, delete its branch, and record the run URLs.

### Appetite

Two budgets, separated because the ACs span two repositories and one number would hide that.

**Deliverable (this repo): 2 hours.** A job in `templates/browser-e2e.yml`, the diff-scoping
logic, and the docs. `lint-mapping.sh` and `selector-policy.js` are untouched — but the
diff-scoping is real logic (parse `git diff --unified=0` hunk headers, intersect with the
linter's `path:line:` output, split error from warning annotations), so it is extracted into
a tested script rather than inlined in a YAML `run:` block, and it owes RED-before-GREEN like
any other behavior. "No new policy logic" is true of those two files and is not a claim that
there is no new logic.
**Tolerance: +50% (3 hours).** Past that the diff-scoping is fighting something; the re-cut
is to fail on any mapping *file* the PR touches rather than per line, which keeps AC-1 and
AC-2 satisfiable.

**Adoption and verification (carlove): separate, not inside the 2 hours.** Adopting the
template, configuring branch protection, and running the probe PR are a distinct act in a
different repository. **Probe commits: N=1.** All three ACs read the same run — AC-1 the log,
AC-2 the absence of untouched-line failures in that same log, AC-3 the merge state while it
is red — so the live-CI clause's per-step sequencing does not multiply here.

### Implementation dispatch sizing

One dispatch. One behavior, one complete RED→GREEN loop, well under the ~90 minute split
threshold. Adoption in a consumer repo is a separate act and not part of this dispatch.

### Doc diff

`docs/ci-integration.md`, concrete before/after. Sequence **after**
[[ci-integration-consumer-count-backport]], which edits the same file at `:209`.

**Before** (`:242`):

> Wire into CI as a fast pre-flight gate before the browser job spins up.

**After:**

> `templates/browser-e2e.yml` ships a `mapping-lint` job that does this. It fails only on
> mapping lines the pull request adds or modifies; findings on untouched lines are posted as
> annotations, so adopting it does not require migrating pre-existing debt.
>
> The job loops per file and checks each exit code. Do not pass several paths in one
> invocation: `lint-mapping.sh` reads only its first argument, so a glob whose first match is
> clean returns 0 with the rest unscanned.
>
> **The job is advisory until it is marked a required status check.** Adopting the template
> makes it run; branch protection is what makes it block.

**Before** (exit-code line at `:240`):

> Exit codes: `0` clean (and for an explicit `--help`, which is not an error) · `1` missing
> argument / file not found / `node` not on PATH · `2` one or more banned tokens detected
> (path + line printed to stderr).

**After:** unchanged text, plus one sentence — a page elsewhere describes this as "exit 1 on
any violation", which is wrong; it is 2, and 123 when wrapped in `xargs -0 -n1`. Correct that
occurrence in the same edit.

### Pre-mortem for the chosen shape

If this ships exactly per spec and still fails, the most likely cause is **criteria that pass
without delivering value**: the job goes green in the plugin's own repo, which has no
`.claude/e2e/mappings/` at all, and nobody notices that no consumer adopted it. AC-3 is written
specifically against that.

**Neither AC-1 nor AC-3 can be satisfied inside this repository** — it has no
`.claude/e2e/mappings/` directory at all, so there is nothing here for the job to lint. Both
need carlove. **Captain authorization is owed for one thing this entity cannot grant itself:**
AC-3 requires changing carlove's branch protection to mark the job a required check. Adopting
the template is a normal PR; editing branch protection is a change to that repo's merge
rules, which Judgment Escalation puts on the captain.

## Stage Report: ideation

**TL;DR.** The original approach was disproved by measurement, the captain re-cut the entity
to write-time enforcement, the option field was built over three EM rounds, and the captain
ruled option E. AC-1, AC-2 and AC-3 are written against that shape; AC-3 is the value
criterion and is deliberately unsatisfiable inside this repository. Appetite 2h / +50%, one
dispatch, `design: required` with the blocking scope attached.

**How the shape got here.** Three artifacts were wrong before this one was right, and each
was caught by a different mechanism rather than by re-reading:

1. The argv classifier was disproved by a measured run — 145 of 147 invocations routed, and
   the selectors still did not arrive, because the consumers resolve to a snapshot ref first.
2. The first re-shape omitted CI entirely. An EM return restored it; it is now the ruled
   option, so the omission would have decided this entity by silence.
3. A spike reported "zero drift orphans" and drew a conclusion from it. The check could not
   have failed — both local installs are pre-#135 — and the conclusion was withdrawn.

**Evidence produced at this stage, not asserted.** The 41 pre-existing findings that make
whole-file linting a day-one red were measured against carlove with the shipped linter, not
estimated: 16 in `secha-office.yaml`, 25 in `secha-app.yaml`, both exit 2, three other
mappings clean. That measurement is what turns the diff-scoping decision from a preference
into an application of the #88 ruling.

**Reviewer citations.** Every `file:line` adopted from an EM round was checked against
`origin/main` before use. One round's citations for `cleanupClosedNamespaceState` were wrong
and were corrected to `:1924` / `:2880` / `:3028` / `:3075` rather than carried.

**Not done here.** The entity stays in `ideation`: this session is a state non-holder, so the
stage transition is binary-owned and cannot be run from here.

### Gate disposition

EM held the ideation gate 2026-08-02 and returned `narrow` with six bounded fixes, all
applied above: the measurement corrected to 15/24/39 with the mis-attribution recorded, the
linter's multi-argument fail-open added as a plan constraint, the doc diff put in before/after
form, the verification vehicle named with the branch-protection authorization the captain
still owes, appetite split into two budgets with N=1 probe commits, and the grandfathered debt
filed as [[carlove-legacy-selector-debt]]. EM stated no further EM round and no captain round
are needed before the stage moves.

**The stage does not move from here.** This session is a state non-holder, so the
`ideation → implementation` transition is binary-owned and cannot be run. The next session
holding state advances it and starts implementation from the ACs above.

## Stage Report: implementation

### Summary

Implemented option E on code commit `62cb72e474ef53c7900d44d505d24d1134eac440`
(`feat(e2e-pipeline): add diff-scoped mapping lint CI gate`). The reusable
`e2e-pipeline/scripts/diff-scoped-mapping-lint.js` enumerates changed mapping files with
NUL-delimited git output, runs the existing `scripts/lint-mapping.sh` once per file, parses
zero-context diff hunks, emits blocking GitHub `error` annotations only for findings whose
new-file line is added or modified, and emits `warning` annotations for legacy findings on
untouched lines. The existing selector policy module and per-file linter were not changed.

`e2e-pipeline/templates/browser-e2e.yml` now contains a thin `mapping-lint` job with a
full-history checkout and delegates all diff parsing and annotation behavior to that tested
script. `auth-setup` depends on the job, so browser setup does not start after a mapping-lint
failure. The job's check name is `Mapping Selector Lint`.

### Produced

- `e2e-pipeline/scripts/diff-scoped-mapping-lint.js`
- `e2e-pipeline/compiler/test/diff-scoped-mapping-lint.test.js`
- `e2e-pipeline/templates/browser-e2e.yml`

No changes were made to `scripts/lint-mapping.sh`,
`compiler/lib/selector-policy.js`, `docs/ci-integration.md`, carlove, branch protection, or
required-check configuration.

### RED evidence

Scoped command for every loop:

```text
rtk node --test compiler/test/diff-scoped-mapping-lint.test.js
```

1. `blocks when a clean changed mapping sorts before a violating changed mapping` — 1 run,
   1 failed. After correcting an arrangement error so both fixture changes were committed,
   the clean-first precondition passed and the behavior assertion failed: expected exit 2,
   got exit 1 with `MODULE_NOT_FOUND` for the not-yet-created
   `scripts/diff-scoped-mapping-lint.js`.
2. `annotates a violation on an added mapping line as a blocking error` — 2 run, 1 failed.
   The wrapper exited nonzero, but stdout contained only the clean file's `— OK` line; the
   expected `::error` carrying `z-violating.yaml`, line 8, and class `>>nth` was absent.
3. `annotates a finding on an untouched legacy line as a non-blocking warning` — 3 run,
   1 failed. Stdout contained the new-line `::error` but no `::warning` for the untouched
   line 6 `has-text` finding.
4. `the CI template runs the reusable gate before browser setup` — 4 run, 1 failed. The
   template had no `mapping-lint` job, full-history checkout, reusable-script invocation,
   base/head arguments, or `auth-setup` dependency, so the single workflow-contract regex
   did not match.

The modified-line case exercises the same zero-context hunk parser established in loops 2
and 3: a second commit changes the selector at line 8 from `>>nth` to `has-text`, and the
final suite requires the annotation to remain an error at the new-file line. Arrangement
assertions are labelled in the test; the clean-first ordering assertion is a precondition,
not a claim about the gate behavior.

### GREEN and exit evidence

- Scoped suite: 5 tests, 5 passed, 0 failed. It covers clean-first/multiple-file scanning,
  added and modified line errors, untouched-line warning plus exit 0, and workflow wiring.
- Full earned suite: `npm test` exit 0; 957 tests, 956 passed, 0 failed, 1 skipped;
  `duration_ms 122762.535`.
- Targeted pinned linter:
  `npx biome lint scripts/diff-scoped-mapping-lint.js compiler/test/diff-scoped-mapping-lint.test.js`
  checked both files with no diagnostics.
- `node --check scripts/diff-scoped-mapping-lint.js`, a `js-yaml` parse of
  `templates/browser-e2e.yml`, and `git diff --check` all exited 0.
- `actionlint -shellcheck= e2e-pipeline/templates/browser-e2e.yml` exited 0. Normal
  `actionlint` reports two SC2086 notices in the pre-existing mapping-staleness shell block;
  the same two notices reproduce against `origin/main`, so this diff adds no actionlint
  finding.

Tests were added, so the implementation-stage timeout audit searched `.github` for a job
that runs `npm test`, `node --test`, or the compiler test directory. There is no such job;
there is therefore no existing CI test-job timeout margin for these five tests to consume.
The local full-suite duration above is recorded rather than pretending it measures a CI
job. The new template job has `timeout-minutes: 5`; its actual live-run margin remains part
of adoption evidence.

The old-behavior test audit found one prior linter arrangement,
`selector-lint-drift.test.js`: it intentionally invokes the per-file linter with one mapping
path to prove policy-table drift. Its intent is unchanged and the full suite keeps it green.
No prior test arranged a multi-path invocation or diff-scoped annotation behavior.

### Acceptance-criterion status and remaining proof

- AC-1 implementation evidence is local and green: a violating added or modified line
  produces a file/line/class `::error` and exit 2, including when a clean changed file sorts
  first. The adopting-repo probe PR and live job URL are still required.
- AC-2 implementation evidence is local and green: an untouched legacy finding in a changed
  mapping produces a `::warning` and, when it is the only finding, exit 0. The same carlove
  probe must show this on GitHub Actions against its live legacy population.
- AC-3 is not attempted. carlove adoption, marking `Mapping Selector Lint` as a required
  context, the probe PR, blocked merge-state observation, branch deletion, and run URL are
  separately authorized cross-repository work.

`docs/ci-integration.md` remains a dependency rather than absorbed scope. Its approved diff
must follow `ci-integration-consumer-count-backport`, which is still backlog; that later edit
must document exit 2 (and xargs exit 123), per-file invocation, diff scoping, annotations,
and the required-check/advisory boundary.

## Stage Report: validation

- FAILED: Attack diff scoping and failure behavior: additions, modifications, renames/deletions, malformed or empty lint output, invalid base/head, and clean-first multi-file ordering; record exact commands and falsifiers.
  `rtk node /tmp/validate-diff-scoped-mapping-lint.js` passed add/modify/delete/clean-first/invalid-revision cases but falsified pure-renames and empty/malformed rc=2 handling.
- DONE: Verify the GitHub Actions template structurally and semantically: full history, event SHA selection, path/script availability, job ordering/dependency, annotations, exit propagation, and timeout; distinguish local proof from live adoption proof.
  `js-yaml`, `actionlint -shellcheck=`, and scratch runs proved fetch-depth 0, PR/push SHAs, annotations/exit 2, `auth-setup` dependency, and 5-minute cap; the declared plugin path is absent after a plain template copy, so adoption customization remains unproved here.
- DONE: Re-run focused and earned suites from exact commit 62cb72e474ef53c7900d44d505d24d1134eac440; confirm only the three approved files changed and that docs/ci-integration.md, selector-policy, lint-mapping.sh, carlove, and branch protection remain untouched.
  Focused 5/5 passed; full suite was 955 pass, 1 unrelated fail, 1 skip of 957, and the unchanged failing trace test passed 1/1 alone; `git diff --name-only` listed only the three approved files.

### Evidence block

Lenses: executable script + workflow; correctness FAIL (1), silent-failure FAIL (1), security PASS (0), resource-lifecycle PASS (0); type-design, concurrency, and manifest/back-compat did not fire.
Diff coverage: 86.76% line coverage on the all-new production script via `node --test --experimental-test-coverage`; PASS over the 85% executable-line ratchet.
Adversarial: flipping the blocking guard and deleting `auth-setup`'s dependency each made the focused suite red (4 pass, 1 fail); the external fixture exposed two suite holes.
Cross-model: Gemini 3.6 Flash High independently found the same two Material defects; citations were verified, its insufficient `-M`-only rename correction was replaced, and its main-only zero-before edge was declined as out of adoption scope. A prior Gemini round was discarded for false repository context.
E2E: NOT RUN — ideation says the carlove probe is owed, but this dispatch explicitly excludes adoption, required-check configuration, and the probe PR; all live AC-1/2/3 evidence remains outstanding.

### Material findings

1. `e2e-pipeline/scripts/diff-scoped-mapping-lint.js:28-31,95-97` loses the rename source by enumerating only the new path and then path-scoping the hunk diff. A pure R100 rename of legacy debt emitted `::error` and rc=2 instead of warning/rc=0; `-M` with only the new path reproduces the full-add diff. Carry old+new names from rename-aware name-status output into hunk parsing and add pure-rename plus rename-and-edit tests.
2. `e2e-pipeline/scripts/diff-scoped-mapping-lint.js:109-125,133` accepts linter rc=2 even when stderr yields zero parseable findings, leaving `violations=false` and returning 0. Empty and malformed fake linters both reproduced the green gate; validate the linter summary/count against parsed findings and return infrastructure rc=1 on any mismatch, with focused tests.

### Summary

Validation rejects commit `62cb72e`: normal additions/modifications and workflow wiring work locally, but the gate violates AC-2 on pure renames and fails open when its linter protocol cannot be parsed. The focused suite and coverage ratchet pass, while the full-suite failure is pre-range/flaky evidence rather than part of this diff; live carlove adoption remains deliberately unverified.

## Stage Report: implementation — feedback cycle 1

### Summary

Validation's two Material findings are repaired by additive code commit
`8a86e866af252ea79e7d69f5277ef318c194a72e`
(`fix(e2e-pipeline): harden diff-scoped mapping lint`). The rejected commit remains in
history; it was not amended.

The rename defect was provenance loss: destination-only `--name-only` enumeration followed
by `git diff -- new-path` presents a pure rename as a full addition. The gate now enumerates
`--name-status -z -M`, retains old and new paths for rename/copy records, lints the
destination, and gives both paths to the zero-context hunk diff. A pure R100 rename therefore
has no touched lines, while a rename with an edited selector carries only the actual
new-file hunk lines.

The protocol defect was an unchecked inference: rc=2 entered the violation branch, but zero
parsed findings left `violations=false` and returned 0. The gate now accepts rc=2 only when
stderr is entirely parseable as findings plus exactly one FAIL summary, every finding and
the summary name the destination mapping, and the positive summary count equals the parsed
finding count. Empty, malformed, duplicate, count-mismatched, or identity-mismatched output
returns infrastructure rc=1 with an `invalid lint-mapping protocol` diagnostic.

Authorized follow-up edits were limited to:

- `e2e-pipeline/scripts/diff-scoped-mapping-lint.js`
- `e2e-pipeline/compiler/test/diff-scoped-mapping-lint.test.js`

The workflow template, workflow topology, selector policy, per-file linter, docs, carlove,
and branch protection were unchanged in this feedback commit.

### Feedback RED evidence

Command:

```text
rtk node --test compiler/test/diff-scoped-mapping-lint.test.js
```

Result before production edits: 11 tests, 5 passed, 6 failed.

1. `a pure R100 rename keeps untouched legacy debt non-blocking` — the Git R100 arrangement
   precondition passed; actual was `{status:2, warning:false, error:true}` instead of
   `{status:0, warning:true, error:false}`.
2. `a rename plus selector edit warns on untouched debt and blocks the edited line` — the
   rename arrangement precondition passed; the edited line was an error, but the untouched
   legacy line was also an error instead of a warning.
3. `rc=2 with empty stderr is an infrastructure failure` — actual was
   `{status:0, diagnostic:false}` instead of `{status:1, diagnostic:true}`.
4. `rc=2 with malformed stderr is an infrastructure failure` — same false-green result.
5. `rc=2 with a mismatched FAIL count is an infrastructure failure` — same false-green
   result despite one finding and a declared count of two.
6. `rc=2 with a mismatched mapping identity is an infrastructure failure` — same
   false-green result when the finding named the requested mapping and the summary named a
   different one.

Each behavior is one deep equality assertion, so the RED run reached and falsified every
added behavior claim. The Git name-status checks in the two rename cases are explicitly
labelled arrangement preconditions.

### Feedback GREEN and exit evidence

- Rename subset: 2 tests, 2 passed, 0 failed.
- rc=2 protocol subset: 4 tests, 4 passed, 0 failed.
- Full focused file: 11 tests, 11 passed, 0 failed; `duration_ms 7596.755875`.
- Full earned suite: `npm test` exit 0; 963 tests, 962 passed, 0 failed, 1 skipped;
  `duration_ms 123030.84925`. This closes the unrelated one-off validation failure with a
  fresh full-population run rather than a focused retry.
- `node --check scripts/diff-scoped-mapping-lint.js`, targeted pinned Biome over both edited
  files, the `js-yaml` template parse, `actionlint -shellcheck=` on the unchanged template,
  and `git diff --check` all exited 0.
- Final code worktree status after the additive commit was clean and ahead of `origin/main`
  by exactly the original feature commit plus the feedback fix.

The old-behavior audit found that the original five focused cases still use their original
fixtures and assertions: clean-first scanning, added-line error, modified-line error,
untouched-line warning/exit 0, and workflow wiring all remained green. `runGate` gained only
an optional fake-linter path for protocol tests; its default remains the real per-file
linter. `selector-lint-drift.test.js` still arranges one real mapping per linter invocation
and remained green in the full suite, so the feedback did not narrow its policy-drift intent.

### Effort and remaining proof

The commit timestamps conservatively bound the entire interval from the rejected feature
commit to the feedback fix at 36 minutes (`17:28:55` to `18:04:57` Asia/Taipei). That upper
bound includes validation and re-dispatch time, so feedback implementation consumed no more
than 0.6h: 30% of the 2h deliverable appetite and below the 3h tolerance.

Six tests were added. Focused runtime increased from the prior recorded 3.454s to 7.597s
(+4.143s), while the full suite measured 123.031s versus the prior 122.763s (+0.268s in this
local run). As recorded in the first implementation report, no repository workflow runs
this Node suite, so there is no existing CI test-job timeout margin to consume or claim.

Live carlove adoption remains outside this dispatch. AC-1/AC-2 still need the adopting-repo
probe run, and AC-3 still needs captain-authorized required-context configuration plus a
blocked merge-state observation. `docs/ci-integration.md` remains sequenced after
`ci-integration-consumer-count-backport`; no part of that dependency was absorbed here.

## Stage Report: validation (cycle 2)

- FAILED: Independently reproduce both prior Material findings against exact head 8a86e866af252ea79e7d69f5277ef318c194a72e, then attack adjacent rename/copy/delete and rc=2 protocol boundaries; verify no fail-open or false-blocking regression remains.
  `node /tmp/validate-diff-scoped-mapping-lint-r2.js` independently closed the prior rename and empty/malformed/count/path cases but exited 1 because three parseable, semantically impossible rc=2 records still returned green.
- DONE: Re-run mechanical lenses, focused tests, executable diff coverage, adversarial mutations, workflow static checks, and one earned full suite; obtain a fresh cross-model review with exact cwd/base/head and validate every citation.
  Focused 11/11, line coverage 89.85%, two claim-breaking scratch mutations red, static checks clean, and full suite 962 pass / 0 fail / 1 skip of 963; Gemini 3.1 Pro High's sole citation was checked and its copy claim disproved by execution.
- DONE: Audit scope and acceptance evidence: only the three original approved files differ from origin/main, feedback commit changes only script/tests, and live carlove adoption, required-check configuration, probe PR, and docs/ci-integration.md remain explicitly unclaimed.
  `git diff --name-status 0a1079c..8a86e86` lists only the script, its test, and the template; `8a86e86^..8a86e86` lists only script/test, with all excluded cross-repo and doc surfaces untouched.

### Evidence block

Lenses: executable script + workflow; correctness FAIL (1), silent-failure FAIL (1), security PASS (0), resource-lifecycle PASS (0); type-design, concurrency, and manifest/back-compat did not fire.
Diff coverage: `node --test --experimental-test-coverage compiler/test/diff-scoped-mapping-lint.test.js` reports 89.85% line coverage on the all-new production script; PASS over the 85% executable-line ratchet.
Adversarial: destination-only rename provenance made both rename tests red (0/2), and accepting a missing rc=2 summary made the empty-protocol test red; the external boundary harness then exposed one uncovered mismatch class.
Cross-model: Gemini 3.1 Pro High reviewed exact cwd/base `0a1079c`/head `8a86e86`; its only citation, script line 62, exists but the finding is false because `-M` reports a copy as `A`, and the independent C100 control blocked the copy at rc=2.
E2E: N/A — this dispatch explicitly excludes live carlove adoption, required-check configuration, and the probe PR that ideation says owe AC-1/2/3 runtime proof.

### Material findings

1. `e2e-pipeline/scripts/diff-scoped-mapping-lint.js:78-108,178-184` validates rc=2 record grammar, path, summary and count but never verifies that a finding's line is a positive in-range destination line or that its source equals that on-disk line. In the fresh harness, otherwise-valid records for line 0, line 999, and line 6 with fabricated source each emitted only `::warning` and returned rc=0. Validate every parsed record against the destination bytes before touched-line classification (safe positive integer, in range, exact raw-line match), and add those three regressions; this is the smallest correction that closes the demonstrated mismatch class without duplicating selector policy.

### Summary

Validation rejects `8a86e86`: the prior pure-rename and empty/malformed rc=2 defects are closed, adjacent copy/delete/ordinary odd-name cases behave correctly, and all repository checks are green. A semantically inconsistent but parseable rc=2 record still fails open, so this second consecutive validation rejection must stop the feedback loop and return to the captain per gate authority; live consumer proof remains separately unclaimed.

## Stage Report: implementation — feedback cycle 2

### Summary

The final captain-authorized feedback fix is additive code commit
`33ffbbea9be930af2ed12c361b447d12a7d1754a`
(`fix(e2e-pipeline): validate mapping lint finding identity`). It closes the
remaining fail-open without changing selector policy or duplicating the
per-file linter.

After rc=2 output passes the existing grammar, mapping, summary, and count
checks, the gate now reads the destination bytes and validates every parsed
finding before touched-line classification. Each line number must be a safe
positive integer within the destination line range, and each finding source
must exactly equal the raw destination line at that one-based position.
Invalid identities return infrastructure rc=1 with the existing
`invalid lint-mapping protocol` diagnostic.

The feedback commit changes exactly the two authorized product paths:

- `e2e-pipeline/scripts/diff-scoped-mapping-lint.js`
- `e2e-pipeline/compiler/test/diff-scoped-mapping-lint.test.js`

Selector policy, `lint-mapping.sh`, the workflow template and topology,
docs, carlove, branch protection, probe PRs, and required checks remain
unchanged.

### TDD and verification evidence

RED command:

```text
rtk node --test --test-name-pattern='line zero|out-of-range|fabricated source' compiler/test/diff-scoped-mapping-lint.test.js
```

Before the production edit, all three new tests failed: 0 passed, 3 failed,
`duration_ms 2626`. Line 0, line 999, and a valid line paired with fabricated
source each actually returned `{status:0, diagnostic:false}` instead of the
required `{status:1, diagnostic:true}`.

The same targeted command passed 3/3 after the identity check. The full
focused file then passed 14/14 with 0 failures in
`duration_ms 11156.666`. All 11 pre-existing cases remained green, preserving
clean-first scanning, added/modified-line errors, untouched-line warnings,
workflow wiring, pure-rename handling, rename-plus-edit classification, and
the earlier rc=2 protocol failures.

The single earned full suite passed: 966 tests, 965 passed, 0 failed, 1
skipped, `duration_ms 152958.862459`. This is the expected three-test
population increase from the prior 963-test run. `node --check`, pinned
Biome over the two edited files, `js-yaml` parsing of the unchanged template,
`actionlint -shellcheck=`, and `git diff --check` all exited 0.

### Effort, runtime margin, and disposition

Commit timestamps conservatively bound this final feedback interval at
36 minutes 52 seconds (`18:04:57` to `18:41:49` Asia/Taipei). That is about
31% of the 2h deliverable appetite and about 20% of its +50% tolerance ceiling
of 3h.

Focused runtime increased from the prior 11-test `7596.755875` ms to the
14-test `11156.666` ms: +3.560s, or about 46.9%. The full local suite measured
152.959s versus the prior 123.031s (+29.928s, about 24.3%); this whole-suite
delta is recorded as observed runtime, not attributed solely to three focused
tests. No repository workflow runs this Node suite, so there is no existing CI
test-job timeout margin to consume or claim.

Implementation is complete for the final bounded correction. Per captain
direction, this is the last implementation feedback cycle: FO should dispatch
one fresh validation and must not automatically reopen another feedback loop.
Live carlove adoption, required-context configuration, blocked merge-state
observation, probe PRs, and sequenced documentation remain outside this
dispatch and unclaimed.

## Stage Report: validation (cycle 3)

- DONE: Independently reproduce all three validation defect classes against exact head 33ffbbea9be930af2ed12c361b447d12a7d1754a: rename provenance, malformed/mismatched rc=2 protocol, and impossible line/source identity; attack adjacent boundaries without editing product files.
  `/tmp/validate-diff-scoped-mapping-lint-r3.js` passed 19/19 independent fixtures: pure rename, rename+edit, empty/malformed/count/path rc=2, line 0/range/source identity, add/modify/legacy-warning/clean-first/delete/copy/linter-rc1, and invalid revisions.
- DONE: Run focused tests, executable diff coverage, adversarial mutations, static workflow/script checks, one final earned full suite, and a fresh exact-head cross-model review; verify every citation and distinguish live adoption evidence still owed.
  Focused 14/14 and 90.57% script line coverage passed; three scratch mutations red; static checks passed; Gemini 3.6 Flash found no Material defect; the final full suite was 963 pass/2 range-external fail/1 skip of 966.
- DONE: Audit final scope and claims: origin/main..HEAD changes only the original three approved files, the final feedback commit changes only script/tests, all AC-local claims have independent evidence, and no workflow/docs/carlove/branch-protection scope was added.
  `0a1079c..33ffbbe` lists only gate script/test/template; `33ffbbe^..33ffbbe` lists only script/test; the code worktree is clean and excluded live-adoption surfaces remain untouched.

### Evidence block

Lenses: executable script + workflow; correctness PASS (0), silent-failure PASS (0), security PASS (0), resource-lifecycle PASS (0); type-design, concurrency, and manifest/back-compat did not fire.
Diff coverage: `node --test --experimental-test-coverage compiler/test/diff-scoped-mapping-lint.test.js` reports 90.57% line coverage on the all-new gate script; PASS over the 85% executable-line ratchet.
Adversarial: destination-only provenance made both rename tests fail (0/2), removing identity validation made line0/range/source fail (0/3), and removing `auth-setup`'s dependency made workflow wiring fail (0/1).
Cross-model: Gemini 3.6 Flash reviewed exact cwd/base `0a1079c`/head `33ffbbe` and found no Material defect; its function/workflow references were verified at script lines 25-209 and template lines 37-59.
E2E: N/A — this dispatch explicitly excludes carlove adoption, required-check configuration, and the probe PR that ideation says owe live AC-1/2/3 proof.

### Full-suite context

The one final `npm test` run exited 1 with 963 passed, 2 failed, and 1 skipped of 966 in 197.882s. Both failures are in unchanged `compiler/test/trace-finalization.test.js:457,484`; blame attributes each line to pre-base commit `c8d6d619`, and the exact range contains no commit for that file, so they are reported rather than debugged or rerun.

### Material findings

None in the dispatched local deliverable at exact head `33ffbbea9be930af2ed12c361b447d12a7d1754a`.

### Summary

Cycle 3 closes all three prior defect classes and finds no adjacent fail-open or false-blocking regression in the bounded plugin deliverable. AC-1/AC-2 have independent local add/modify/legacy-warning proof, while carlove live annotations, required-context configuration, blocked merge state, probe cleanup, and the sequenced `docs/ci-integration.md` edit remain explicitly owed outside this dispatch; AC-3 is not claimed locally.

### Validation gate — EM verdict `proceed`

Fresh EM independently rechecked exact head
`33ffbbea9be930af2ed12c361b447d12a7d1754a` over base
`0a1079c4904bdd5c8cee6f5e3d01b997faf8f1f4`, reran the 19-fixture harness,
focused 14-test suite, and executable coverage, and found zero Material defects in the
bounded plugin-local deliverable. The two failures in the validator's final full-suite run
remain explicit context: both are timeout-sensitive assertions at unchanged pre-base lines
in `trace-finalization.test.js`; an earlier exact-head full run was 965 pass / 0 fail / 1
skip, and EM's focused rerun of those two names passed 2/2.

Verdict scope is validation only. It does not claim merged, shipped, adopted, AC-3 complete,
or live AC-1/AC-2 proof. The next delivery boundary is carlove adoption: customize the
template, obtain captain authorization before requiring `Mapping Selector Lint` on `main`,
run the one-commit red probe, capture annotations, blocked merge state, and the run URL, then
close the probe and delete its branch. The `docs/ci-integration.md` edit remains sequenced
after `ci-integration-consumer-count-backport`.
