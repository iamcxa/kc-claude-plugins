---
id: n6hhdhm5tyggcs6408ztm45e
title: "e2e-pipeline: anchor the click action grammar so no click action is accepted on a prefix"
status: implementation
source: "GitHub issue #189 (iamcxa/kc-claude-plugins) — trusted own-lane intake, dispatched by the captain"
started: 2026-08-10T09:00:16Z
completed:
verdict:
worktree: /Users/kent/mini-legs/rx-d1b173ab-c5c4-4dca-a82f-1dfb272d3040/worktree
issue: "189"
pr:
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
