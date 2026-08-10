---
id: n6hhdhm5tyggcs6408ztm45e
title: "e2e-pipeline: anchor the click action grammar so no click action is accepted on a prefix"
status: validation
source: "GitHub issue #189 (iamcxa/kc-claude-plugins) — trusted own-lane intake, dispatched by the captain"
started: 2026-08-10T09:00:16Z
completed:
verdict:
worktree: /Users/kent/mini-legs/rx-d1b173ab-c5c4-4dca-a82f-1dfb272d3040/worktree
issue: "189"
pr: 191
design: required
---

## Problem

`e2e-pipeline/compiler/resolver.js:11` defines `ACTION_PARSERS.click` as an
**unanchored** pattern:

```js
pattern: /Click\s+(\w+)(?:\s+on\s+([\w-]+))?/i,
```

`\w+` cannot match `row(id=7)`, and because the pattern has neither `^` nor `$`
the regex engine is free to match a *prefix* and succeed. Against
`Click row(id=7) on list` it binds `element: 'row'`, leaves `page: null`, and
discards `(id=7)` and ` on list` without a word. `fill` (resolver.js:15) is
anchored (`/^Fill\s+…$/`) and errors loudly on the same shape, so the two
sibling parsers disagree about what "does not match" means.

Two consequences, per issue #189:

1. **Parameters vanish.** `agents/e2e-test-runner.md:137/148/240` documents
   `Click <element(param=val)> on <loc>` as a supported form that substitutes
   params into the mapping selector's `${param}` placeholders. The compiler
   never performs that substitution, so under `/e2e-compile` the form is
   accepted, stripped, and silently reinterpreted as a bare `Click row`.
2. **The page qualifier vanishes, and nothing refuses that.** `page` is left
   `null`, so the element resolves globally instead of on the named page. With a
   name collision this surfaces as "ambiguous"; without one it silently resolves
   the only candidate — which may be the wrong element on a mapping where the
   author wrote the page precisely to express intent rather than to break a tie.
   This second consequence is entirely unguarded.

End value: **the compiler must never silently accept only a prefix of a click
action and discard its page qualifier or parameter syntax.**

## Reverse-recovery audit (against `origin/main` @ 7521546)

Layer trace, flow YAML → compiled `.sh`:

| Layer | Location | Verdict |
|-------|----------|---------|
| Flow YAML ingest | `compiler/parser.js` | WORKING — hands `step.action` through verbatim |
| Action grammar | `compiler/resolver.js:5-42` (`ACTION_PARSERS`) | **EXISTS_BROKEN** — `click` (`:11`) unanchored; `fill` (`:15`) anchored |
| Mismatch diagnostic | `compiler/resolver.js:77-82` (`parseActionString`) | WORKING — already emits `Step '<id>': action string does not match expected format for type '<type>'. Got: <action>`; it is simply never reached for a click prefix match |
| Element/page resolution | `compiler/resolver.js:334-360` | WORKING — consumes `operands.element`; `operands.page` is currently produced but never consulted (separate, out of scope) |
| Codegen | `compiler/codegen.js` | WORKING |
| Selector `${param}` substitution | absent from `compiler/` (`grep substituteSelectorTemplate compiler/` → 0 hits) | MISSING by design — it exists only on the `/e2e-test` agent-runner path |

One broken seam (the `click` pattern). Repair is scoped to that seam; no rebuild.

## Related work — PR #184 (closes #179), OPEN DRAFT, branch `iamcxa/e2e-179-usage-promise`

PR #184 adds `interpolationError()` / `stepInterpolationErrors()` /
`unresolvedActionSelectorError()` to the same file (`resolver.js`, +121/-1) and
explicitly defers #189: *"the click pattern is unanchored, so it also drops the
` on <page>` qualifier. That half is unguarded, is not an interpolation problem,
and wants its own decision."* #184 is **not** in this task's base
(`main` @ 7521546), so its guard cannot be duplicated or undone here — but this
task must not re-introduce it, must not implement `${...}` substitution (the
thing #184 deliberately refuses), and must keep its diff small enough to
rebase cleanly under #184.

## Proposed approach

**Reject, do not implement substitution.** Anchor the click grammar to match
`fill`, and refuse the parameterized form with a diagnostic that names it:

1. Anchor `ACTION_PARSERS.click.pattern` to `/^Click\s+(\w+)(?:\s+on\s+([\w-]+))?$/i`.
   Any click action the grammar cannot **fully consume** now falls through to the
   existing descriptive `parseActionString` error, which already names the step
   id and echoes the full action string.
2. Add a targeted diagnostic for the documented parameterized shape
   (`element(param=value)`) so `Click row(id=7) on list` reports *that specific
   unsupported form* and names `/e2e-test` as the executor that does support it,
   rather than a generic "does not match expected format".
3. Document the executor divergence where a `/e2e-compile` user will see it,
   in the same spirit as #184's `docs/multi-site-testing.md` note.

Why reject rather than support: supporting it end-to-end means implementing
`${...}` selector substitution and emitting the result — a new bash/JS escaping
surface that PR #184 declined on the recorded ground that *"building a new
escaping surface where nothing can see it is the wrong order."* Issue #189's own
measurement says **0 of 45 flows / 355 mapping elements** use a parameterized
click today, so rejection costs nothing live and fully delivers the end value.
Supporting the form remains open and is the question carried to the gate.

## Design determination

`required` — this changes a **compiler input contract**: a form the docs call
supported becomes a compile-time error. The decision recorded above is *reject
with a named diagnostic*; the alternative (*support end-to-end, substitute
before the unresolved-`${...}` guard*) is carried to the validation gate as the
routing question, since it is the captain's call and not reversible for free
once published.

## Spike / blast radius (measured before changing behaviour)

`grep -rhoE "action: [\"']Click [^\"']*[\"']" e2e-pipeline/` → 30 occurrences, 23
distinct. Anchoring changes the outcome of exactly four of them, and **none is
on the resolver path**:

| String | Where | Effect of anchoring |
|--------|-------|---------------------|
| `Click app submit` | `compiler/test/codegen.test.js:188` | none — codegen fixture, bypasses `parseActionString` |
| `Click hostile selector` | `compiler/test/codegen-status-safety.test.js:700` | none — same |
| `Click on the first in_progress work order row` | `compiler/test/migrate.test.js:183` | none — migrate does not parse action grammar |
| `Click <element> on <page>` | doc/template placeholder | none — never compiled |

Every resolver-path click string in the repo is already of the anchored form.
No spike needed beyond this for the regex change itself; the CLI end-to-end
refusal is the remaining unproven mechanism and is AC-1's proof.

## Acceptance criteria

**AC-1 — (end value) The compiler never accepts a click action on a prefix.**
Every click action string the compiler accepts is fully consumed by the grammar;
one it cannot fully consume is a compile-time error that names the step id and
echoes the whole action string, and no `.sh` artifact is written.
Verified by: a `bin/e2e-compile.js` invocation on a fixture flow containing
`Click row(id=7) on list` — non-zero exit, diagnostic on stderr, and `ls` of the
output dir showing no emitted script (CLI end-to-end, satisfying the E2E-first
clause). Falsified by: removing the `^`/`$` anchors from
`ACTION_PARSERS.click.pattern` — the run goes green and emits a script.

**AC-2 — The page qualifier is never silently dropped.**
`Click <element> on <page>` still binds `page`; a click string with any trailing
content beyond the grammar (e.g. `Click login_button on login extra`) errors
instead of binding `login_button` and discarding the tail.
Verified by: two resolver unit tests — one asserting `operands.page === 'login'`
on the valid form, one asserting an error (and no resolved step) on the trailing
-content form. Falsified by: dropping the `$` anchor — the trailing-content test
goes green with `page` bound and the tail gone.

**AC-3 — The documented parameterized form is refused by name, not generically.**
`Click row(id=7) on list` produces a diagnostic that identifies the
`element(param=value)` form specifically and names the executor that does
support it, so a reader is not left guessing which token was wrong.
Verified by: a resolver unit test asserting the error text contains the
parameterized-form guidance (not merely `does not match expected format`).
Falsified by: deleting the parameterized-form branch — the error falls back to
the generic mismatch text and the assertion fails.

**AC-4 — No regression, and PR #184's surface is left alone.**
The full `e2e-pipeline` compiler suite is green, and the diff touches neither
`fill`'s grammar nor any interpolation/unresolved-selector guard.
Verified by: one full-suite run at stage exit with the pass/fail counts recorded,
plus `git diff --stat origin/main...HEAD` in the report showing the touched files.
Falsified by: any failing test in the suite, or a diff hunk inside `fill`'s
pattern.

**AC-5 — The change is delivered as a reviewable DRAFT PR linked to #189.**
A draft PR exists against `main` from the task branch, opened through the GitHub
REST endpoint (not `gh pr create`), whose body links issue #189 and carries the
open support-vs-reject question.
Verified by: the PR URL plus `gh pr view <n> --json isDraft,body` showing
`isDraft: true` and the `#189` link. Falsified by: a non-draft PR, or a body
with no `#189` reference.

## Test plan

RED before GREEN, in `e2e-pipeline/compiler/test/resolver.test.js`:

1. RED: `Click row(id=7) on list` → expect a compile error (currently resolves
   silently to `element: 'row'`, `page: null`). Run, capture the failure digest.
2. RED: `Click login_button on login extra` → expect a compile error (currently
   binds `login_button`, drops the tail).
3. RED: error text for case 1 names the `element(param=value)` form.
4. Control (must stay GREEN throughout): `Click login_button on login` binds
   `element: 'login_button'`, `page: 'login'`; `Click submit_button` binds
   `page: null`; `fill`'s existing behaviour unchanged.
5. GREEN: anchor the pattern + add the parameterized-form diagnostic.
6. Scoped run: `node --test compiler/test/resolver.test.js` (or the package's
   scoped equivalent) green.
7. CLI end-to-end for AC-1: compile a fixture flow with the malformed action,
   assert non-zero exit and no emitted `.sh`.
8. Full suite exactly once at stage exit; record counts.
9. Adversarial spot-check: revert the `$` anchor in a scratch copy and confirm
   the new tests go red. A suite that stays green under that edit is a hole.

## Doc diff

The parameterized click form is documented as supported at
`e2e-pipeline/agents/e2e-test-runner.md:137`, `:148`, `:240`. Those lines describe
the **`/e2e-test` agent runner**, where the form genuinely works, so they stay
accurate and are **not** rewritten. Add instead a short executor-divergence note
on the compile side (`e2e-pipeline/skills/e2e-compile/` reference or the compiler
docs the skill points at), in the shape #184 used for `docs/multi-site-testing.md`:

> Before: (no statement about parameterized element references)
> After: "`Click <element(param=val)> on <loc>` is an `/e2e-test` agent-runner
> form. `/e2e-compile` does not substitute selector parameters and refuses the
> form at compile time rather than silently dropping the parameters — see #189."

PRODUCT.md / ARCHITECTURE.md: no change — neither describes the action grammar.

## Sizing

ONE implementation dispatch. Single behaviour (one regex + one diagnostic + a
doc note), well under the ~90-minute / 3-behaviour split threshold. Appetite:
~90 minutes of worker time; on overrun, cut the doc note to backlog rather than
extending, and never compress validation.

## Pre-mortem

*If this ships exactly per spec and still fails, the most likely cause is
**criteria that pass without delivering value**:* click is anchored, the tests
are green, and the identical prefix-match defect survives in the sibling parsers
(`navigate`, `wait`, `snapshot`, `capture-url-query`, `verify-external`,
`execute-external` — all unanchored today). The fix would be locally correct and
the class would live on. Mitigation: implementation records an anchoring audit
of **every** `ACTION_PARSERS` entry in the stage report — anchored / intentionally
unanchored + why / genuinely at risk — and files a backlog seed for any entry in
the third bucket, without widening this diff.

## Out of scope

- Implementing `${...}` selector substitution on the compile path (that is the
  new escaping surface #184 declined; it is the gate question, not this diff).
- Re-adding or altering PR #184's `unresolvedActionSelectorError` /
  interpolation guards — #184 owns them.
- Anchoring the other `ACTION_PARSERS` entries (audited and reported, filed as a
  seed if real, but not changed here).
- Making the resolver actually *consult* `operands.page` to scope element lookup
  to the named page. Today `page` is bound and then unused; this task stops the
  qualifier being silently discarded by the parser. Page-scoped resolution is a
  separate behaviour change.
- Any `.github/workflows/**` edit, any version bump, any release-please manifest
  edit.

## Stage Report: implementation

- DONE: Anchored click grammar, RED first: a click action string the grammar cannot FULLY consume is a compile-time error naming the step id and echoing the whole action — proven by failing-test-first evidence in the stage report AND end-to-end through `node bin/e2e-compile.js` on a fixture flow (non-zero exit, no `.sh` emitted). Silent prefix-matching must be impossible, not merely unlikely.
  Commit c7f9c3b. RED first, against the unmodified parser: `Click login_button on login extra` → `errors[0] === undefined` (silently accepted, tail discarded); `Click heading(id=1) on login` → **zero errors** and a resolved step, i.e. the dropped ` on login` let a `dashboard` element resolve while the author named `login`. CLI both ways on one fixture: anchored → `exit=1`, stderr diagnostic, output dir empty; anchors reverted → `exit=0`, `t189-param-click.sh` emitted containing `agent-browser click '[data-testid="row"]'`. "Impossible, not unlikely" is pinned by the adversarial matrix (scratch copy, each edit verified applied): drop `$` → 3 fail; drop `^` → 1 fail; drop both → 4 fail; delete the diagnostic branch → 1 fail.
- DONE: `Click row(id=7) on list` is refused by a diagnostic that NAMES the `element(param=value)` form and names `/e2e-test` as the executor that does support it — not the generic "does not match expected format" text.
  `parameterizedClickError` (resolver.js). Test `the parameterized element form is refused by name, not generically` asserts the message matches `/element\(param=value\)/` and `/\/e2e-test/` AND `assert.doesNotMatch(/does not match expected format/)` — deleting the branch makes it fall back to the generic text and the test fails (verified: adversarial case C, 1 fail).
- DONE: Anchoring audit of EVERY `ACTION_PARSERS` entry recorded in the stage report as a three-bucket table (anchored / intentionally unanchored + why / genuinely at risk), with a backlog seed proposed for anything in the third bucket and NO widening of this diff beyond `click`.
  Every row measured by running the parser, not read off the regex. No sibling parser was modified.

| Parser | Bucket | Measured |
|---|---|---|
| `click` | anchored (this diff) | — |
| `fill` | anchored (already) | untouched; diff has no hunk in its pattern |
| `snapshot` | intentionally unanchored | `"snapshot this and that"` → accepted, `operands={}` — detector with no operands; nothing to discard |
| `verify-external` | intentionally unanchored | `"Verify external service and more"` → accepted, `operands={}` — same |
| `execute-external` | intentionally unanchored | `"Please Execute external junk"` → accepted, `operands={}` — same |
| `capture-url-query` | intentionally unanchored | `"Please Capture token from url query and discard the rest"` → accepted, `operands={as:"TOK",state_key:"tok"}` — operands come from the step's `save_as:`; the captured group is never read |
| `navigate` | **genuinely at risk** | `"Please Navigate to /list"` → `target="/list"` (leading text dropped); `"Navigate to /list and then some junk"` → `target="/list and then some junk"`, which `resolveNavigate` accepts as a literal path |
| `wait` | **genuinely at risk** | `"Wait 5 minutes"` → `seconds=5`. A 60× silent misread. `"Please Wait 5 zzz"` → `seconds=5` |

  Backlog seed proposed (NOT fixed here — a second behaviour change needs its own blast-radius measurement): anchor `navigate` and `wait`. `wait` is the sharper one: `Wait 5 minutes` compiling to 5 seconds is latent, not live (no corpus flow uses that phrasing), which is why it is a seed and not a hotfix.

### Summary

Two material re-baselines happened mid-stage and both are in the PR body. First, the worktree was cut from a local `main` ~15 commits behind `origin/main`, whose `e2e-pipeline` differed by +28390/-1167 — I fast-forwarded rather than build against a tree the PR would never merge into. `ACTION_PARSERS` was byte-identical on the real main, so the spec and all five ACs survived unchanged; what did NOT survive is the entity's premise that `substituteSelectorTemplate` is absent from `compiler/` (it exists and runs today on the `expect:` path). Second, **PR #184 merged while I was working**, so I rebased onto it. Its guard and mine overlap on exactly one input, `Click row(id=7)`, which mine now intercepts earlier; I confirmed its guard is not dead (a plain `Click row`/`Fill row` against a templated selector still reaches it), repointed its two tests at the form they actually own, and corrected the comments that described the parser as discarding parameters — which, after this change, it no longer does. That is a deliberate, flagged deviation from the entity's "do not touch #184" scope line, forced by the merge; it is called out in the PR body for the gate.

The support-vs-reject choice was NOT made here. It is in the PR body under the literal heading `DECISION NEEDED`, with both routes and one correction the captain needs: the recorded reason to reject — "supporting it means building a new escaping surface" — is now stale, because the substitution machinery already exists and runs on the `expect:` path. Route B's remaining risk is emission/escaping in codegen, not parsing. Anchoring is required under either route, so none of this diff is wasted work whichever way the captain rules.

Verification: full suite ONCE at stage exit — 1068 tests, 1066 pass, 0 fail, 2 skipped (both pre-existing, env-gated). Lint parity per touched file measured in place against `origin/main`: `resolver.js` 14 vs 14, `resolver.test.js` 13 vs 13. Draft PR **#191** — https://github.com/iamcxa/kc-claude-plugins/pull/191 — `isDraft: true`, base `main`, links #189.

CI on #191 (post-report): all required checks green — `e2e-pipeline suite (portable)` pass, `version parity` pass, `real-browser proofs` pass, GitGuardian pass. `mergeable: MERGEABLE`.

## Stage Report: validation

- DONE: Independently reproduce EVERY AC's `Verified by:` clause from the actual tree — never the implementer's self-report — and report PASS/FAIL per AC with the actual command output. AC-1 requires you to run the CLI end-to-end BOTH ways yourself (anchored → non-zero exit and no `.sh`; anchors reverted in a scratch copy → exit 0 and an emitted script). AC-5 requires `gh pr view 191 --json isDraft,body` showing `isDraft: true`, a `#189` link, and the literal string `DECISION NEEDED`.
  All five PASS, reproduced against `c7f9c3b` (HEAD, `origin/main` = `bd2b142` is a direct ancestor; PR `MERGEABLE`/`CLEAN`). Per-AC table below.
- DONE: Adjudicate the two mid-stage re-baselines the implementer flagged … (a) PR #184 overlap … (b) The stale rejection premise …
  (a) NOT dead, and the repointing was FORCED, not a weakening. (b) The stale-premise claim is TRUE. Both proven by execution, detail below.
- DONE: Adversarial spot-check plus one independent cross-model review … confirm the claimed fail counts … Verify every reviewer `file:line` citation …
  Matrix reproduced EXACTLY (3 / 1 / 4 / 1). Cross-model (codex, GPT-5.x): P1 none, P2 none, 2× P3 — 4/4 citations correct. Silent-failure lens: P1 none, 1× P2 (confirmed, see Findings), 5× P3; 16/17 citations correct.

### Diff under review

`git diff --stat origin/main...HEAD` — 3 files, +163/−17:
`e2e-pipeline/compiler/resolver.js` (+78/−…), `e2e-pipeline/compiler/test/resolver.test.js` (+101/−…), `e2e-pipeline/skills/e2e-compile/SKILL.md` (+1).
Repo-rule gates: commit is `fix(e2e-pipeline): …` (conventional, correctly scoped); staging is exactly the three files that belong; **zero** version hunks in any `plugin.json` / `marketplace.json` / release-please manifest; **zero** hunks under `.github/workflows/**`. Lint parity measured per file HEAD-vs-`origin/main`: `resolver.js` 14 vs 14, `resolver.test.js` 13 vs 13 — no new warnings.

### Per-AC verdicts (all reproduced from the tree)

- **AC-1 PASS** — CLI both ways on my own fixture (`/tmp/i189-ac1`, mapping selector `[data-testid="row"]`, action `Click row(id=7) on list`). Anchored: `exit=1`, named diagnostic on stderr, output dir **empty**. Anchors reverted in a scratch git worktree (edit verified applied via `git diff`): `exit=0`, `t189-param-click.sh` emitted containing `agent-browser click '[data-testid="row"]'`. Also reproduced the defect on unmodified `origin/main`: same fixture, `exit=0`, same wrong click emitted.
- **AC-2 PASS** — `Click login_button on login extra` → 1 error, `resolved.steps.length === 0`; `Click heading on dashboard` → binds `element=heading`, `page=dashboard`. The sharp half re-proved on `origin/main`: `Click heading(id=1) on login` returned **zero errors** with `page: null` and resolved to *dashboard's* `role=heading[name="Dashboard"]` — the page-scoping gate was genuinely defeated, not merely bypassed.
- **AC-3 PASS** — `Click row(id=7) on list` yields a message matching `/element\(param=value\)/` and `/\/e2e-test/` and NOT `/does not match expected format/`. Deleting the dispatch branch turns it back into the generic text (matrix case 4 → 1 fail).
- **AC-4 PASS** — one full-suite run at stage exit in the worktree: **1068 tests, 1066 pass, 0 fail, 2 skipped** (env-gated: real browser, absent external corpus at `/Users/kent/Project/carlove`). No diff hunk in `fill`'s pattern (grep-proven). `unresolvedActionSelectorError`'s body is **comment-only** edits — filtering the diff to non-comment lines leaves exactly three things: the anchored pattern, `parameterizedClickError`, and its 5-line dispatch branch.
- **AC-5 PASS** — `gh pr view 191`: `isDraft: true`, base `main`, body line 1 `Closes #189.`, literal `## DECISION NEEDED` at body line 57. All required checks green (portable suite, version parity, real-browser proofs, GitGuardian). *Unverifiable-by-artifact:* the "opened via GitHub REST, not `gh pr create`" clause leaves no observable trace; the observable half passes.

### Evidence block

`Lenses:` Diff class = executable parser/input-validation change (`resolver.js`) + its unit tests + one markdown table row; no frontmatter, no manifest, no workflow, no shell. **Fired: correctness** (run by me — CLI e2e both ways, 13-shape edge matrix, repo-wide corpus sweep, mutation matrix; verdict PASS, 0 findings) · **silent-failure** (error handling + input validation; ran as a general-purpose agent under the silent-failure brief because `pr-review-toolkit:silent-failure-hunter` is **not registered in this session's agent list** — substitution recorded, not a skip; verdict PASS-with-findings: 0 P1, 1 P2, 5 P3) · **back-compat half of manifest/back-compat** (the action-string grammar is a contract already-written flow YAML reads; verdict PASS — sweep below). **Not fired, with the surfaces named:** security (diff touches a regex, an error string, unit tests, one doc row — no auth/permission/trust boundary, no shell-running hook, no secrets), type-design (no new or changed type; `parameterizedClickError` returns `string|null`, the same shape as the file's existing `unresolvedActionSelectorError` / `interpolationError`), concurrency (resolver is synchronous and pure over its arguments), resource-lifecycle (no processes, handles, or unbounded growth). Read: worktree `c7f9c3b` and `origin/main` `bd2b142`, `e2e-pipeline/compiler/resolver.js` + `compiler/test/resolver.test.js` + `skills/e2e-compile/SKILL.md`. Would have failed it: a click string in the repo that compiled on `bd2b142` and errors on `c7f9c3b` **on the resolver path** — swept all 51 distinct click action strings in the repo through both regexes; 45 unchanged-accept, 3 unchanged-reject, **3 newly rejected** (`Click app submit`, `Click hostile selector`, `Click on the first in_progress work order row`), all three off the resolver path and all three confirmed harmless by the green full suite. The third is an *improvement*: the old pattern bound `element: 'on'` from it.
`Diff coverage:` **100%** of this diff's added/changed executable lines in `resolver.js`. Measured with `node --test --experimental-test-coverage compiler/test/*.test.js`: file-level 97.02% line / 87.59% branch, uncovered = `337-341 457-461 560 593-600 652-656 1036-1040 1044-1047 1123-1124`; the diff's lines (19, 150-166, 177-181) appear in none of those ranges. Above the 85% bar. Read: worktree `c7f9c3b`. Would have failed it: any diff line in the uncovered set.
`Adversarial:` Ran the full four-case matrix MYSELF in a throwaway `git worktree` at `c7f9c3b`, each edit proven applied by `git diff` before running, full suite per case. drop `$` → **3 fail**; drop `^` → **1 fail**; drop both → **4 fail**; delete the diagnostic branch → **1 fail**. Exactly the implementer's claimed counts; no case stayed green. Plus a fifth of my own for checklist 2(a): neuter `unresolvedActionSelectorError` to `return null` → **exactly 2 fail**, and they are exactly the two repointed #184 tests. Read: `c7f9c3b` in `/tmp/i189-scratch` and `/tmp/i189-s2` (both removed). Would have failed it: a green suite under any of the five edits.
`Cross-model:` **PASS** — `codex exec` (codex-cli 0.136.0, GPT-5.x — cross-vendor relative to me, Claude; `agy` attempted and absent from `$PATH`, so codex was the first available other-vendor tool). Verdict: **P1 none, P2 none**, two P3 (both independently confirmed by me: multiline `Click row\non list` is accepted because every separator is `\s+`; and `\w+` vs `[A-Za-z_][A-Za-z0-9_]*` disagree, so `Click 1row(id=7)` gets the generic message). All 4 cited `file:line` verified against the real files — 4/4 correct, round retained. Read: worktree `c7f9c3b`. Would have failed it: a P1 left unfixed and unwaived at this gate — none was raised.
`E2E:` **PASS** — real runtime, `node bin/e2e-compile.js` on a hand-built fixture project, both directions (AC-1 above), plus a `sites:`-block flow driven through `resolveMultiSite`. Read: `c7f9c3b` for the anchored run, a scratch worktree of the same commit for the reverted run, `bd2b142` for the pre-fix baseline. Would have failed it: a `.sh` in the output dir on the anchored run, or exit 0.
`Origin re-observation:` **N/A — no accepted claim originated in consumer or external runtime behavior.** Issue #189 is an own-lane source read of `ACTION_PARSERS.click` in this repo (I read the issue body to confirm), and the behavior it describes was re-observed here directly through this repo's own `bin/e2e-compile.js`, which is the enforcement point rather than an external consumer. Caveat recorded under Findings: the *secondary* claim that `/e2e-test` does support the form rests on `agents/e2e-test-runner.md:261/272/303` as documentation and was never re-observed in the live agent runner.

### Checklist item 2 — adjudication

**(a) #184's guard is NOT dead, and the repointing was forced.** Neutering `unresolvedActionSelectorError` reddens exactly `errorDetails — additive structured channel` and `cross-site traversal carries the same refusals` — the two repointed tests, and nothing else (a first run also showed 3 `trace-contract.test.js` reds; re-run without concurrent load → clean, so those are load-flakes in a file outside this diff, reported as CONTEXT). The repointing was **forced, not cosmetic**: at HEAD `Click row(id=7) on list` now returns the parameterized diagnostic, so the unmodified test would have failed asserting the wrong message. The new input still owns real behaviour — `Click row on list` AND `Fill row with 'x' on list` against a templated selector both still hit the guard. No coverage was lost: the parameterized form is now pinned by the `#189` block instead.
**(b) The stale-premise claim is TRUE, and I proved it by running, not reading.** On `origin/main` `bd2b142`, an `expect:` entry `row(id=7) is visible on list` against `[data-testid="row-${id}"]` resolves to `effectiveSelector`/`cssSelector` = `[data-testid="row-7"]`, zero errors. So `parseElementReference` and `substituteSelectorTemplate` exist AND run on the `expect:` path today. **One precision the captain should have:** the two *leaf helpers* are directly reusable, but the wrapper that calls them (`resolveVisibilityElement`) also enforces the mapped-visibility `css_selector` requirement and returns a visibility-shaped object, so Route B is "call the two existing helpers from `resolvedActionElement`", not "call `resolveVisibilityElement` from the action path". That is still far cheaper than "invent substitution", so the claim is TRUE and not overstated — only the wrapper reuse is. The residual Route-B risk the PR body names (emission/escaping in codegen) is real and is corroborated by `e2e-pipeline/CLAUDE.md`, which records that a click's raw `selector:` is passed to `agent-browser click` literally and `css_selector` goes through a bash-then-JS `eval` IIFE.

### Findings

- **P2 — the new guard has no cross-site (`resolveMultiSite`) test, and the repo's own convention next door demands one.** `compiler/test/resolver.test.js:1543-1545` states it verbatim: *"resolveMultiSite is a second, parallel walk over steps. Every guard added to the single-site walk has to be added there too, and nothing enforces that but a test — 'I patched both call sites' is not evidence anyone can re-check."* All six `#189 anchored click grammar` tests use single-site `resolve()`; zero use `resolveMultiSite`. Independently instrumented: `resolver.js:1044-1047` (the cross-site parse-refusal branch) is **uncovered across the entire 1068-test suite**. **The behaviour is correct today** — I drove `resolveMultiSite` directly and all three shapes refuse, including the named diagnostic — so this is a missing regression guard, not a live bug. **Correction to the reviewer's framing, which I checked:** that branch was *also* uncovered on `origin/main` (there, lines `988-991`), so the diff did not regress branch coverage; what the diff removed is the only cross-site test *input* carrying the parameterized form (`resolver.test.js:1571-1574`, `Click row(id=7) on list` → `Click row on list`). Fix is ~8 lines in a file already in the diff: mirror `resolver.test.js:311` through `resolveMultiSite`.
- **P3 (residuals, all confirmed by running, none blocking).** (1) `Click row\non list` is accepted — `\s+` matches newlines and `$` is not `m`-anchored; not a prefix match (the string is fully consumed), so AC-1 stands, and `fill` has always had the identical property. (2) `Click 1row on list` is accepted by the grammar but `Click 1row(id=7) on list` falls through to the generic message — `\w+` (`resolver.js:19`) vs `[A-Za-z_][A-Za-z0-9_]*` (`resolver.js:153`); the diagnostic class matches the `expect:` path's, so the looser one is the grammar. (3) `Fill row(id=7) with 'x' on list` — same authoring error, one type over — gets only the generic message; `parameterizedClickError` is gated on `type === 'click'`. Same for `Click row (id=7)…` (space) and `Click row(id=7 …` (unclosed). All refuse correctly; only message quality differs. (4) Trailing whitespace now hard-fails with an **invisible** cause: `Click login_button on login ` emits `Got: Click login_button on login ` and the offending character cannot be seen; `JSON.stringify`-ing the `Got:` value (as `resolver.js:546` already does for selectors) would fix it. Correct direction — `fill` has always behaved this way — and I swept the repo: no live flow has it. (5) The parse gate `continue`s, so a step refused at parse time never resolves its `expect:`, masking downstream diagnostics; measured A/B, a tier-1 error carrying `candidates` becomes a tier-2 generic one. Iteration cost, not a false pass, and the `continue` predates the diff. (6) `SKILL.md:148` keys the row on the grammar form, not on the emitted sentence — the string a user would paste into a search ("parameterized element reference is not supported") appears **0 times** in `SKILL.md`, while neighbouring rows key on literal message fragments. (7) `compiler/migrate.js:21-32` still claims to "mirror resolver.js ACTION_PARSERS" and carries a third grammar (`/^Click\s+\w+_\w+/i`); pre-existing drift this diff widens but does not create.
- **CONTEXT (not this diff).** `/e2e-compile` prints every error **twice** — reproduced identically on `origin/main` with an unrelated `element not found` error; already disclosed in the PR body. Three `compiler/test/trace-contract.test.js` tests go red under concurrent full-suite load and green when run alone.
- **Unverified secondary claim.** AC-3 and `SKILL.md:148` assert that `/e2e-test` *does* support the parameterized form. That rests entirely on `agents/e2e-test-runner.md:261/272/303` — an LLM agent's prose instruction, never re-observed in a live agent run. The diff did not create the claim (#189 itself asserts it), but the diagnostic now sends users there, so it is worth the captain knowing it is doc-derived.

### Recommendation (advisory — I set no `verdict:` and did not advance status)

**Accept the ACs, then one narrow correction round for the single P2.** All five ACs PASS on independently reproduced evidence, both flagged re-baselines adjudicate in the implementer's favour, the adversarial matrix reproduces exactly, and no reviewer raised a P1 on either round. The one thing I would not wave through is the P2: this repo wrote the "every guard needs its cross-site twin test" rule into the very file the diff edits, the branch is provably uncovered suite-wide, and the fix is roughly eight lines in a file already open. The P3s are converged residuals — they are the named class "an anchored single-line grammar over a `\s`-separated regex, with a diagnostic narrower than the mistake it describes", which this approach cannot dissolve without widening scope into `fill`, `navigate`, and `wait` that the entity explicitly deferred to a backlog seed. I recorded them rather than opening another round. On the routing question I express no preference; my job was to check that the captain's DECISION NEEDED is stated on true facts, and it is — with the one precision noted in 2(b).

### Summary

Validated PR #191 at `c7f9c3b` from a fresh context, reproducing every AC from the tree rather than the self-report: CLI end-to-end both ways, the pre-fix defect re-observed on `origin/main`, a five-case mutation matrix that reproduced the implementer's counts exactly, a repo-wide sweep of all 51 click action strings, real diff-coverage measurement, and two independent review rounds (cross-model codex plus a silent-failure lens) whose citations I checked one by one. All five ACs PASS; both mid-stage re-baselines adjudicate correctly, and the stale-premise claim underpinning the gate question is TRUE by execution, not by reading. One P2 survives — the anchored grammar has no `resolveMultiSite` test, on a branch the coverage instrument shows is uncovered suite-wide, against a convention this repo states verbatim three lines from the code the diff edits. Seven P3s are recorded as converged residuals.

### Feedback Cycles

- Cycle 1: REJECTED (captain ruling on `briefing:issue189-validation-c2` —
  decision `revise`, `route:approve-route-a-after-cross-site-test`, `to:
  stage:implementation`; the leg's own recommendation) — fresh validation;
  surface implementation wall-clock NOT INSTRUMENTED for either round, so the
  measurable surface is dispatch count: 2 implementation dispatches vs the
  entity's declared estimate of 1 (`## Sizing`, "ONE implementation dispatch";
  200%, exactly AT the default 2× tolerance and not past it, so no design-reset
  decision is owed — a Cycle 2 would be past it). Appetite `~90 minutes of
  worker time` is the entity's other declared number and no round recorded
  minutes against it; that is a gap in the reports, not a zero. AC unchanged —
  the captain kept Route A, so the `## Design determination` recorded at
  ideation stands and no criterion was narrowed or dropped.
  Findings routed: **1 fixed** — the P2, `resolver.js:1044-1047` (the cross-site
  parse-refusal branch) has no `resolveMultiSite` test and is uncovered across
  the whole 1068-test suite, against the convention `resolver.test.js:1543-1545`
  states verbatim three lines from the code the diff edits; the diff removed the
  only cross-site input carrying the parameterized form
  (`resolver.test.js:1571-1574`). **7 declined, each named, none unexamined** —
  the P3 residual class "an anchored single-line grammar over a `\s`-separated
  regex, with a diagnostic narrower than the mistake it describes": (1) multiline
  `Click row\non list` accepted, (2) `\w+` grammar vs
  `[A-Za-z_][A-Za-z0-9_]*` diagnostic disagree, (3) `Fill row(id=7) …` gets no
  named diagnostic (branch gated on `type === 'click'`), (4) trailing whitespace
  fails with an invisible cause, (5) the parse gate `continue`s so a refused
  step never resolves its `expect:`, (6) `SKILL.md:148` keys its row on the
  grammar form not the emitted sentence, (7) `migrate.js:21-32` carries a third
  drifted grammar (pre-existing). Accepted under the validation stage's
  converge-by-naming-residuals clause: Route A cannot dissolve the class without
  widening into `fill`/`navigate`/`wait`, which `## Out of scope` defers to a
  backlog seed. **2 recorded as cantTell, not passed** — AC-5's "opened through
  the REST endpoint" clause leaves no observable artifact, and the `/e2e-test`
  parameterized-support claim is doc-derived from
  `agents/e2e-test-runner.md:261,272,303` and was never re-observed live
  (`route:hold-for-live-e2e-test-runner-probe`, the route the captain did not
  take). **1 CONTEXT** — `/e2e-compile` double-prints errors, reproduced
  identically on `origin/main`; not this diff.

## Stage Report: implementation (cycle 2)

Wall-clock this round: **14 minutes** (06:55–07:10 CST, 2026-08-11), against the
entity's `~90 minutes of worker time` appetite for the whole task.

- DONE: Add the missing `resolveMultiSite` regression test to `e2e-pipeline/compiler/test/resolver.test.js` — mirror `resolver.test.js:311` through `resolveMultiSite` — so `resolver.js:1044-1047` is exercised
  `resolver.test.js:1589`, `the parameterized element form is refused by name on the cross-site walk`, commit `6d9663b` (+28 lines, no other file). Drives `Click row(id=7) on list` through `resolveMultiSite` and asserts exactly one error, named (`element(param=value)` + `/e2e-test`), not the generic mismatch text, with the tier-2 detail forwarded and no step resolved. `resolver.js` unchanged: `git show --stat 6d9663b` lists only the test file.
- DONE: In a THROWAWAY scratch worktree, neuter the cross-site parse gate, prove the edit applied with `git diff`, run the new test, and record the RED digest — then discard the scratch and record the GREEN
  Scratch `git worktree add --detach /tmp/issue189-red-scratch`; unneutered baseline 87/87 green. **Six** one-line neuters of `resolver.js:1043-1047`, each shown by `git diff` before the run, each turning **exactly this one test red (86 pass / 1 fail of 87)**: N1 drop both pushes → `0 !== 1`; N2 hand-roll a generic message → `must name the form the author actually wrote`; N3 strip the step-id prefix → `must name the step the author has to go edit`; N4 hand-roll the tier-2 detail → `deepEqual` fail; N5 drop `/e2e-test` → `must name the executor that does support the form`; N6 append the generic text → `the generic mismatch text leaves the author guessing…`. Scratch discarded (`git worktree remove --force` + `rm -rf`; absent from `git worktree list`). GREEN after: `node --test test/resolver.test.js` 87/87.
  *Assertion honesty (stage-def "count new assertions against the RED output"):* all six behaviour-claiming assertions are individually falsifiable by the neuters above. The seventh, `assert.equal(result.resolved.steps.length, 0)`, is green under every neuter tried — each still `continue`s the step — so it is an arrangement check, not a behaviour claim, and is labelled as such in the test comment.
- DONE: Finish by re-instrumenting `node --test --experimental-test-coverage` and showing `1044-1047` is no longer in the uncovered set
  Two full-suite coverage runs. Before (new test reverted, 1068 tests): `resolver.js | 97.02 | 87.59 | 95.12 | 337-341 457-461 560 593-600 652-656 1036-1040 1044-1047 1123-1124`. After (1069 tests): `97.36 | 87.97 | 95.12 | 337-341 457-461 560 593-600 652-656 1036-1040 1123-1124`. `1044-1047` is gone. `1036-1040` (the cross-site `!step.type` branch) is still uncovered and was not in scope this round.
- DONE: Nothing else moves … Re-anchor on the source requirement before touching code … Full suite ONCE at stage exit with the pass/fail/skip counts recorded
  *Re-anchor against #189:* its asks map — "an action string the parser cannot fully consume should be an error" → AC-1; "the page qualifier vanishes and nothing refuses that" → AC-2; "accept `element(param=value)` … or reject it explicitly" → AC-3 (reject; captain-settled Route A); its conditional fourth ask (substitution must precede the unresolved-`${...}` guard *if* the form becomes supported) is untriggered because the form is rejected. One #189 observation is served by no AC — the element still resolves globally rather than page-scoped — and `## Out of scope` defers it by name as a separate behaviour change. *Diff the other way:* `git diff --stat origin/main...HEAD` = `compiler/resolver.js` (AC-1/2/3), `compiler/test/resolver.test.js` (AC-2/3/4 + this round's guard), `skills/e2e-compile/SKILL.md` +1 (the ideation-approved Doc diff). No changed file lacks an AC. `git diff --name-only origin/main...HEAD | grep -E 'plugin\.json|marketplace\.json|release-please|\.github/workflows'` → empty.
  *Full suite at stage exit:* `npm run test:ci` → **tests 1069, pass 1067, fail 0, skipped 2, todo 0**, 108s wall. The 2 skips are pre-existing (the reverted-test baseline run was 1068/1066/0/2).
- DONE: PR #191 is updated and its CI is re-observed green AT THE NEW HEAD … Report the mergeable state and every required check at the exact new head … say explicitly whether the incoming `happy-path.test.js` change interacts with this diff
  New head **`6d9663b`**, pushed fast-forward (`c7f9c3b..6d9663b`); no force-push, no history rewrite. The branch first merged `origin/main` **a024b25** as `b7144f7` (no conflicts, no file in this diff touched by main), so it is no longer 6 behind. `gh pr view 191` → `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`, `isDraft: true`. `gh pr checks 191` at `6d9663b`, all seven entries, none failing: **e2e-pipeline suite (portable) pass** 1m57s; **version parity (plugin.json / marketplace.json / codex / README) pass** 24s; **decide whether the real browser is needed pass** 7s; **real-browser proofs pass** 3s; **GitGuardian Security Checks pass** 4s; `e2e-pipeline real-browser proofs (#91,…)` skipping; `report-failure` skipping. Bounded claim on "required": branch protection is not readable with this token (`/branches/main/protection` → 404, `rulesets` → empty), so this is the set GitHub attached to the PR, not a read of the protection rule.
  *Interaction with the incoming `happy-path.test.js`: yes, and it exercises this diff rather than merely coexisting with it.* That test compiles `compiler/test/fixtures/happy-path-flow.yaml`, which carries two click steps — `Click submit_button on login` and `Click refresh_button on dashboard` — both canonical `Click <element> on <page>` forms the anchored pattern must still fully consume. Main's rework changed its assertions from "the emitted script contains X" to "the run issues call X" (new `test/fixtures/agent-browser-argv-stub.js`); it did **not** change the flow fixture, so the action strings reaching the resolver are unchanged. Scoped run at the merged head: `node --test compiler/test/happy-path.test.js` → 1/1 pass; green again in the full suite and on CI.
  *CI margin (stage-def "tests added" clause):* portable job 1m57s against `timeout-minutes: 10` — roughly 80% of the cap unused; one test added to 1069. No margin disclosure owed.
- SKIPPED: the RED-before-GREEN loop in its ordinary form
  The round brief and the validator both establish the branch already refuses correctly, so no failing-first run exists to record. Substituted by the six-neuter falsifiability record above, per the checklist's instruction.

### Summary

One test added (`resolver.test.js:1589`); no product code changed. The round's real
work was making a green-on-arrival guard falsifiable — six single-line neuters of
`resolver.js:1043-1047`, each turning only this test red out of 87 — plus a
before/after full-suite coverage measurement showing `1044-1047` leave the
uncovered set. **Two deviations to surface.** (1) The branch was merged with
`origin/main` a024b25 (`b7144f7`, clean) so the exit suite and CI would exercise
this diff against current main instead of a 6-commit-stale base; that is a second
commit beyond the "~8-line correction", taken because the checklist asks for CI at
the exact new head and for a statement about the incoming `happy-path.test.js`,
neither of which is answerable from a stale base. (2) The correction commit is
typed `test(e2e-pipeline)` rather than the `fix(e2e-pipeline)` shown in the round
brief: it adds no behaviour, `CLAUDE.md` lists `test` as a valid type, and the PR
title — the squash message release-please actually reads — is still
`fix(e2e-pipeline): …`. None of the seven accepted P3 residuals were touched.

## Stage Report: validation (cycle 2)

- DONE: The P2 is actually closed, and the new guard can fail. Do NOT take the implementer's neuter record on trust — reproduce it.
  Reproduced, and then strengthened. Ran `resolver.test.js:1589` at `6d9663b`: 87/87 green (control). In my own throwaway worktree I neutered `resolver.js:1044-1047` **by line number** eight ways — the implementer's six (drop both pushes; hand-rolled generic message; strip step-id prefix; hand-rolled tier-2 detail; drop `/e2e-test`; append generic text) plus two of my own (delete the whole branch; replace only the `continue` with a fall-through). Each edit proven applied via `git diff` hunk header showing `@@ -1044 … @@ function resolveMultiSite`. **Every one: 87 tests, 86 pass, 1 fail — and the one leaf failure is always `the parameterized element form is refused by name on the cross-site walk`.** The implementer's claim reproduces exactly.
  **The decisive check they did not run:** I applied the same neuters to a worktree at `c7f9c3b` (pre-correction). Deleting the *entire* cross-site parse-refusal branch left the suite **86/86 GREEN**. So the hole was genuinely open and this test genuinely closes it — the guard is not green-on-arrival decoration.
  Coverage re-instrumented myself at `6d9663b`: `node --test --experimental-test-coverage compiler/test/*.test.js` → `resolver.js | 97.36 | 87.97 | 95.12 | 337-341 457-461 560 593-600 652-656 1036-1040 1123-1124`. **`1044-1047` has left the uncovered set**, matching the reported before/after exactly.
  **The `resolved.steps.length === 0` label is NOT honest — it is a behaviour claim mislabelled as arrangement.** `resolver.test.js:1611-1613` says "Arrangement check, not a behaviour claim". Codex and the silent-failure lens both accepted that. My neuter A2 (replace `resolver.js:1046`'s `continue` with a fall-through supplying empty operands, both pushes intact) fails the test on `expected: 0, actual: 1` — that assertion, alone, and only this test out of 87. The bounded half ("green under every neuter *tried*") is true; the classification is false. See Findings.
- DONE: Re-anchor the five ACs on the NEW bytes; the prior PASS verdicts do not carry.
  Read `6d9663b` in worktree `/Users/kent/mini-legs/rx-d1b173ab-…/worktree`, branch `mini/issue189-click-parser` — verified identical to `gh pr view 191` `headRefOid` and to `git ls-remote origin` (all `6d9663b`), and `origin/main` is now `a024b25` **and is the merge-base**, so the branch is not stale. All five re-anchored on the new bytes.
  **AC-1 PASS** — CLI end-to-end both ways on my own fixture (`/tmp/v189-ac1`, `Click row(id=7) on list`). Anchored at `6d9663b`: `exit=1`, named diagnostic, output dir **empty**. Its stated falsifier applied in a scratch worktree (un-anchor `resolver.js:19`, `git diff` proven): `exit=0`, `v189-param-click.sh` emitted carrying `agent-browser click '[data-testid="row"]'` — parameters and page qualifier silently dropped. **AC-2 PASS / AC-3 PASS** — `node --test --test-name-pattern='#189|parameterized|…'` 15/15; and neuter N2 (a generic message that still starts with `Step 'hit':`) reddens the test, proving the named-diagnostic assertions discriminate rather than merely matching a prefix. **AC-4 PASS** — `node --test compiler/test/*.test.js` (identical to `npm run test:ci`) run **twice**, both **1069 / 1067 pass / 0 fail / 2 skipped**; `git diff --stat origin/main...HEAD` = 3 files +191/-17; no hunk in `fill`'s pattern. Biome lint parity with/without the added test: 226 warnings, 2 infos, both — no new warnings. **AC-5 PASS on its observable half, `cantTell` on REST provenance (unchanged, not upgraded)** — `isDraft: true`, base `main`, body line 1 `Closes #189.`, line 57 `## DECISION NEEDED`. I re-tested the provenance clause rather than inheriting it: `gh api …/pulls/191 -q 'keys[]'` has no creation-source field of any kind, so no artifact can settle it.
  What would have failed me: an emitted `.sh` on the anchored run; a suite red outside the diff's blast radius; a `headRefOid` other than `6d9663b`.
- DONE: Adjudicate the two disclosed deviations and the scope in both directions.
  **(a) The merge `b7144f7` is provably clean, not merely asserted clean.** `git diff-tree --cc b7144f7` is **empty** (zero conflict-resolution edits), and I recomputed the merge independently: `git merge-tree --write-tree c7f9c3b a024b25` → `5530c97…`, **byte-identical to `b7144f7^{tree}`**. So the merge added nothing a machine would not have produced. `git diff c7f9c3b b7144f7` touches 19 files, **none of them the three in this PR's diff**; and the three-dot PR diff against the new `origin/main` is still exactly those three files, so the merge drags nothing into the PR.
  **(b) Release surface: zero movement, and the release-please reading confirmed by API, not by assumption.** `git diff --name-only origin/main...HEAD | grep -E 'plugin\.json|marketplace\.json|release-please|\.github/workflows|CHANGELOG'` → **empty**. The PR has **3** commits and the repo's `squash_merge_commit_title` is `COMMIT_OR_PR_TITLE` (`gh api repos/…`), which resolves to the **PR title** whenever a PR has more than one commit — so release-please reads `fix(e2e-pipeline): anchor the click action grammar…`. The `test(e2e-pipeline)` commit type is therefore harmless. *Bounded:* squash is not enforced — merge-commit and rebase merges are also enabled; under either, release-please would read the individual commits, which still include `c7f9c3b`'s `fix(e2e-pipeline)`, so a patch bump lands either way.
  **(c) Scope in the other direction: nothing quietly fixed, diff grew by exactly the one test.** `git show --stat 6d9663b` = 1 file, +28, 0 deletions; `git diff --stat c7f9c3b 6d9663b -- resolver.js skills/e2e-compile/SKILL.md` is **empty** (product code and doc byte-identical). I re-ran all seven accepted P3 residuals against `6d9663b` and **all seven still reproduce**: multiline `Click row\non list` still accepted (0 errors, 1 step); `Click 1row(id=7)` and `Fill row(id=7) with 'x'` still get only the generic text; trailing whitespace still fails invisibly; the parse gate still `continue`s; `SKILL.md:148` still keys on the grammar form (the emitted sentence appears **0** times in the file); `migrate.js:21-32` still carries `/^Click\s+\w+_\w+/i`. No accepted residual was touched.
  **(d) Live CI re-observed at the exact head.** `gh api …/commits/6d9663b/check-runs` — all seven check-runs carry `head_sha: 6d9663b`: **5 success** (e2e-pipeline suite (portable), version parity, decide whether the real browser is needed, real-browser proofs, GitGuardian), **2 skipped**, **0 failure**. `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`, `isDraft: true`. *Bounded claim, independently reproduced:* `/branches/main/protection` → 404 and `/rulesets` → `[]` with this token (scopes `gist, read:org, repo, user`), so this is the set GitHub attached to the PR, **not** a read of the protection rule. I cannot say "all required checks".

### Evidence block

`Lenses:` Diff class = **test-only**: one `test()` function, +28 lines, in `e2e-pipeline/compiler/test/resolver.test.js`; zero product code, zero markdown, zero manifest, zero frontmatter, zero shell. **Fired: correctness** (exercise-based, run by me — 8 line-anchored mutations at `resolver.js:1044-1047` plus a pre-correction control at `c7f9c3b`, CLI e2e both ways, two full-suite runs, coverage before/after; verdict PASS, 1 finding) · **silent-failure** (the guarded code is error handling and the diff's whole subject is whether a refusal is reported; `pr-review-toolkit:silent-failure-hunter` is **not registered in this session's agent list**, so ran as a `general-purpose` agent under the silent-failure brief — substitution recorded, not a skip; verdict PASS-with-findings: 0 P1, 1 raised P2 which I reproduced and **downgraded to P3**, see Findings; 5/5 citations verified correct). **Not fired, with the surfaces named:** security (no auth/permission/trust boundary, no shell-running hook, no secrets — the diff is assertions in a test file), type-design (no new or changed type), concurrency (`resolveMultiSite` is synchronous and pure over its arguments), resource-lifecycle (no processes, handles, or unbounded growth), manifest/back-compat (no `marketplace.json` / `plugin.json` / skill frontmatter hunk — grep-proven empty, and no already-installed copy reads a test file). Read: `6d9663b` at `/Users/kent/mini-legs/rx-d1b173ab-…/worktree` on `mini/issue189-click-parser`, plus `c7f9c3b` and `a024b25` in throwaway worktrees. Would have failed it: any product-code hunk in `git diff c7f9c3b 6d9663b -- resolver.js` — it is empty.
`Diff coverage:` **N/A as a percentage bar — the diff adds no product lines; measured on the lines it exists to cover instead.** All +28 lines are test code, executed by definition (the test runs and passes). The meaningful measurement is the guarded surface: `node --test --experimental-test-coverage compiler/test/*.test.js` at `6d9663b` → `resolver.js` 97.36% line / 87.97% branch, uncovered `337-341 457-461 560 593-600 652-656 1036-1040 1123-1124`; at `c7f9c3b` the same run additionally listed `1044-1047`. **`1044-1047` left the uncovered set**, which is the ratchet moving the right way. Above the 85% bar. Read: `6d9663b`, `e2e-pipeline/compiler/`. Would have failed it: `1044-1047` still appearing in the uncovered column.
`Adversarial:` **PASS — 8 claim-breaking edits by me, in my own throwaway worktrees, never the implementer's.** At `6d9663b`, `resolver.js:1044-1047` neutered eight ways by line index (N1 drop both pushes · N2 hand-rolled generic message · N3 strip step-id prefix · N4 hand-rolled tier-2 detail · N5 drop `/e2e-test` · N6 append generic text · X7 delete the whole branch · A2 replace only the `continue`). Every edit proven applied by a `git diff` hunk header naming `function resolveMultiSite`; **every one → 87 tests, 86 pass, 1 fail, the single red leaf always `the parameterized element form is refused by name on the cross-site walk`.** Control unmodified: 87/87. The same neuters at **`c7f9c3b`** left the suite **86/86 green even when the whole branch was deleted** — the hole was real. Plus the silent-failure lens's duplicate-`errorDetails.push` mutation, which I reproduced: suite stays **87/87 green** with `errors.length 1` / `errorDetails.length 2`. Read: `6d9663b` in `/tmp/v189-scratch`, `c7f9c3b` in `/tmp/v189-pre`, `6d9663b` in `/tmp/v189-sf` (all three `git worktree remove`d and `rm -rf`ed; `git worktree list` shows zero remaining). Would have failed it: any neuter leaving the suite green, or reddening a scattering of other tests instead of this one. **Two false starts I am recording because they nearly produced a confident wrong verdict:** my first neuter pass anchored on a *textual* match and landed at `resolver.js:790` — the byte-identical single-site branch inside `resolve()`, not the cross-site one; and my first harness had no `node_modules` in the scratch worktree, so all six "REDs" were `Cannot find module 'js-yaml'` load crashes, not assertion failures. Both were caught only by demanding a green control first. That the implementer recorded an unneutered 87/87 baseline is what makes their record credible.
`Cross-model:` **PASS** — `codex exec` (codex-cli **0.136.0**, GPT-5.x; cross-vendor relative to me, Claude). `agy` attempted first per the clause and is **absent from `$PATH`** (`agy: command not found`), an observed failure, not an assumption — so codex was the first available other-vendor tool. Verdict: **P1 none, P2 none, P3 none**; it independently traced the fixture through `resolver.js:1015/1035` to the branch at `1043` and confirmed no neighbouring guard can produce the same pass. **All 15 cited `file:line` verified against the real files — 15/15 correct**, round retained. It did dissent from me on one point, agreeing with the "Arrangement check" label; my A2 execution result overrides its reading. It also observed 4 unrelated failures at 1063 passes when it ran the broad package suite — consistent with the previously recorded `trace-contract.test.js` load-flake CONTEXT; my own two full-suite runs were 1067/0. Read: `6d9663b`, `e2e-pipeline/compiler/`. Would have failed it: a P1 left unfixed and unwaived at this gate — none was raised on either round.
`E2E:` **PASS** — real runtime, `node bin/e2e-compile.js` at `6d9663b` on a fixture project I built myself (`/tmp/v189-ac1`: one mapping, one flow, action `Click row(id=7) on list`), both directions. Anchored: `exit=1`, the named diagnostic on stderr, output dir empty. Falsifier direction in a scratch worktree with `resolver.js:19` un-anchored: `exit=0` and `v189-param-click.sh` emitted containing `agent-browser click '[data-testid="row"]'` at line 558 — the exact silent wrong-click #189 reported. Read: `6d9663b` for the anchored run, a `/tmp/v189-scratch` worktree of the same commit for the reverted one. Would have failed it: a `.sh` in the output dir on the anchored run, or exit 0. *(Reproduced in passing: the double-printed error CONTEXT finding, at the new head too.)*
`Origin re-observation:` **N/A — no accepted claim originated in consumer or external runtime behavior.** #189 is an own-lane source read of `ACTION_PARSERS.click` in this repo, and the behaviour was re-observed here through this repo's own `bin/e2e-compile.js`, which is the enforcement point rather than an external consumer. The one genuinely external-runtime claim — that `/e2e-test` *does* support the parameterized form — remains doc-derived from `agents/e2e-test-runner.md:261,272,303` and was **not** re-observed live; the captain declined `route:hold-for-live-e2e-test-runner-probe`, so it stays a recorded caveat and I did not upgrade it.

### Findings (cycle 2)

- **P3 — the test comment mislabels a falsifiable behaviour claim as an arrangement check.** `resolver.test.js:1611-1613` says of `assert.equal(result.resolved.steps.length, 0)`: "Arrangement check, not a behaviour claim". It is a behaviour claim. Neuter A2 — replace only the `continue` at `resolver.js:1046` with a fall-through that supplies empty operands, leaving both pushes intact — fails the test on `expected: 0, actual: 1`, that assertion alone, and only this test out of 87. The bounded half of the sentence ("green under every neuter *tried in the RED record*") is true and complies with the repo's absolute-claims rule; the classification after it does not. Fix is one line of comment. This is in the implementer's favour: the guard is stronger than advertised, and the comment's own next sentence ("so a later green cannot be read as 'refused AND emitted anyway'") is exactly right.
- **P3 (raised as P2 by the silent-failure lens; I reproduced it and downgraded it, with reasons).** The test pins `errors.length === 1` and `deepEqual(errorDetails[0], {message})` but never bounds `errorDetails.length`, so an errors/errorDetails desync in the very branch under test stays green. Reproduced exactly: duplicating `resolver.js:1045` gives `errors.length 1` / `errorDetails.length 2` and the suite stays **87/87**. The desync is user-visible — `bin/e2e-compile.js:55` reports `resolveErrors: (errorDetails || []).length` and `compiler/compiler.js:238,284` forwards `errorDetails` into `--json` output. One line closes it: `assert.equal(result.errorDetails.length, 1)`. **Downgraded to P3 because** (i) the behaviour is correct today, (ii) the identical gap exists in the single-site twin at `resolver.test.js:311-325`, which predates this round and was accepted at cycle 1, and (iii) the round brief instructed "mirror `resolver.test.js:311` through `resolveMultiSite`" — the implementer mirrored faithfully, and adding an assertion the twin lacks would have been the deviation. Better as a one-line follow-up or a backlog seed than a third round.
- **CONTEXT (not this diff, not new).** `/e2e-compile` still prints every error twice — observed again at `6d9663b` in my AC-1 run; previously reproduced on `origin/main`, so pre-existing. The `trace-contract.test.js` load-flake is independently corroborated: codex saw 4 failures at 1063 passes under full-suite load; my two dedicated full-suite runs were both 1067/0.
- **Process note, not a defect.** The dispatch names my CODE branch as `spacedock-ensign/issue189`; the actual worktree is on `mini/issue189-click-parser`, which is also the PR head branch. Harmless for a validator (I committed no code), but the FO should know the dispatch template's branch field did not match reality.

### Recommendation (advisory — I set no `verdict:` and did not advance `status:`)

**Accept. The correction round did what it was sent to do, and I would not open a third round.** The P2 is closed on the strongest available evidence: the same mutation that leaves the pre-correction suite green when it deletes the entire branch now reddens exactly one test, and `1044-1047` has left the uncovered set on my own instrument. The implementer's six-neuter record reproduces exactly, and I added two neuters of my own that also hold. Both disclosed deviations adjudicate in their favour, and the merge is clean by independent recomputation of the merge tree rather than by assertion. Scope moved in neither direction — no product byte changed, all seven accepted P3 residuals still reproduce. Live CI is green at the exact head, with the honest bounded claim about "required" reproduced independently. The two P3s above are one-line follow-ups on a test file, not gate blockers; my only genuine correction to the implementer's own account is that they under-claimed their `steps.length` assertion.

### Summary

Validated the correction round at `6d9663b` — not `c7f9c3b`, not `origin/main` — with the head verified against `gh pr view` and `git ls-remote` before reading anything. Reproduced the implementer's six-neuter falsifiability record and extended it to eight, then ran the same neuters at `c7f9c3b` to prove the hole was open: deleting the whole cross-site parse-refusal branch left the pre-correction suite 86/86 green, and reddens exactly one test now. Re-anchored all five ACs on the new bytes including the CLI end-to-end both ways; AC-5's REST-provenance clause re-tested against the API's field list and left `cantTell`. The merge `b7144f7` is clean by independent `merge-tree` recomputation matching its tree byte-for-byte. Two P3s: the `steps.length` assertion is mislabelled an arrangement check (it is falsifiable — I broke it), and the test does not bound `errorDetails.length` (a reviewer's P2, reproduced and downgraded with reasons). Recommend accept.
