---
id: srqy4f40m20yf5fp392vtcn0
title: "e2e-pipeline: escape flow/mapping-sourced strings in every expansion-active codegen emission context"
status: backlog
source: GitHub issue #190 (https://github.com/iamcxa/kc-claude-plugins/issues/190) — found by cross-model EM review of PR #184, repro re-run independently before filing
started:
completed:
verdict:
worktree:
issue: "190"
pr:
design: trivial-pass
---

## Problem

`e2e-pipeline`'s compiler emits a mapping-sourced `base_url` straight into a
double-quoted Bash default without escaping `$` or backticks. A mapping with

```yaml
base_url: "http://localhost:3000/$(id -u)"
```

compiles (exit 0, `bash -n` clean) to

```bash
BASE_URL="${1:-${E2E_BASE_URL:-http://localhost:3000/$(id -u)}}"
```

which runs `id -u` at script start. Two distinct failures ride the same line:
**confusion** (an author writing `base_url: "http://host/${APP_ENV}"` silently
gets an empty expansion and a run against the wrong origin, with nothing
reporting it) and **execution** (`$(...)` and `` ` `` run).

The escaper already exists and is used almost everywhere else
(`e2e-pipeline/compiler/codegen.js:72` `escapeDoubleQuoted`, and
`codegen.js:67` `singleQuote`). The `BASE_URL=` header bypasses it. This is
the reverse of #179 (there the runner does not substitute; here the compiler
does) and #180 would not catch it — that gate reads generated source rather
than running it, and this line is well-formed source.

Threat framing, honestly: `base_url` is author-supplied input to `/e2e-map`
(`agents/e2e-mapper.md:30`), not page-derived, so anyone who can write it
already controls the compiled script. This is a footgun with a live edge, not
a privilege boundary. Severity is driven by the failure being **silent** while
the fix is a reuse of an escaper that already ships.

Issue #190 explicitly scopes the fix to the **class**, not the fixture: audit
every codegen emission context for a flow- or mapping-sourced string. The
original sentinel sweep covered flow and mapping free-text fields but did
**not** cover step ids, which reach `echo` lines and `_record_step_name`
arguments.

## Proposed approach

Minimal, seam-scoped repair — reuse the existing escapers at the emission
sites that bypass them. No new abstraction, no new standing check.

1. **Audit every emission context** in `e2e-pipeline/compiler/codegen.js` (and
   any other compiler module that emits script text) where a flow- or
   mapping-sourced string lands in a shell context that is *expansion-active*:
   inside `"..."`, inside a `${VAR:-default}` word, inside a `${VAR:?word}`
   word (the `word` is expanded when the parameter is unset), and any `#`
   comment line where an embedded newline could terminate the comment.
   Record the audit as a file:line table in the stage report with a
   WORKING / MISSING-ESCAPE classification per context.
2. **Fix each MISSING-ESCAPE context** by routing the value through the
   existing `escapeDoubleQuoted` / `singleQuote` helper appropriate to that
   context. Do not invent a new helper unless an audited context genuinely
   needs a shape neither helper produces (and say why in the report).
3. **Prove inertness by executing**, not only by reading emitted bytes.

### Reverse-recovery audit (against `origin/main`)

Layer-traced before proposing any new mechanism — the abstraction already
exists, so this is a repair, not a build:

| Layer | Site | Verdict |
|-------|------|---------|
| Escaper (double-quoted) | `compiler/codegen.js:72` `escapeDoubleQuoted` — escapes `\`, `"`, `$`, `` ` `` | WORKING |
| Escaper (single-quoted) | `compiler/codegen.js:67` `singleQuote` | WORKING |
| Variable-name safety | `compiler/parser.js:46` shell-identifier pattern + reserved-name rejection; `compiler/site-name.js:6` | WORKING (names cannot inject; values are the gap) |
| `BASE_URL` / optional-variable default | `compiler/codegen.js:154` — `defaultStr` interpolated raw into `"${N:-${E2E_X:-<raw>}}"` | **EXISTS_BROKEN** (the filed instance) |
| Required-variable `:?` usage word | `compiler/codegen.js:146` — `reqUsage` embeds unvalidated `flowName` into an expansion-active `${N:?word}` | **Lead — verify and classify** |
| Parameter comment lines | `compiler/codegen.js:153`, `:127` — `defaultStr` / `flowName` emitted into `#` comments | **Lead — newline-break risk; verify and classify** |
| Step id → `echo` | `compiler/codegen.js:1271`, `:1320`, `:1405` — via `escapeDoubleQuoted(step.id)` | WORKING (re-verify by exercise, per #190's explicit ask) |
| Step id → `_record_step_name` | `compiler/codegen.js:877` (`singleQuote`), `:1252` (`quotedId`) | WORKING (re-verify by exercise) |
| Navigate URL path | `compiler/codegen.js:1258` — `singleQuote(urlPath)` | WORKING (inert per #190's sweep) |
| `runtime_values` templates | `compiler/codegen.js:197` `runtimeTemplateDoubleQuote` — escapes, then **deliberately re-enables** `${NAME}` | WORKING BY DESIGN — must not regress |

The leads above are starting points, not the finished audit. The audit is the
deliverable; the table must be re-derived from the code, not copied from here.

### Complementarity with recent interpolation work

#179's fix touches `compiler/resolver.js` (plus its tests and one dead-function
deletion) and concerns the *runner* not substituting. This task touches
emission sites in `codegen.js`. `runtimeTemplateDoubleQuote` (`codegen.js:197`)
intentionally re-enables `${NAME}` expansion for `runtime_values` templates —
that behavior is **load-bearing and must survive**. Implementation re-verifies
this against a fresh `origin/main` before building; if the premise has
collapsed, escalate rather than build.

### Appetite

~90 minutes, ONE implementation worker session (below the ~90-minute split
threshold; the work is one behavior class in one module, so a split would only
buy cold-start cost). If the audit turns up a context that needs a genuinely
new escaping shape, cut it to a follow-up backlog seed rather than extending
the budget.

### Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is
**criteria that pass without delivering value**: tests that assert the emitted
*bytes* look escaped while never executing them, so a syntactically-present but
semantically-wrong escape still goes green. AC-4 exists specifically to close
that hole by running the emitted prologue under a real `bash`.

### Spike

No spike needed. Every mechanism relied on is already proven in this repo:
`escapeDoubleQuoted` / `singleQuote` (in use across `codegen.js`), the
`node --test compiler/test/*.test.js` harness, and executing generated bash
under `bash -c` (the issue's own repro already did this).

## Design determination

`trivial-pass` — no UI, contract, interface, schema, or visual surface changes.
The compiled script's observable contract is unchanged for every input that was
already safe; only inputs containing shell metacharacters change behavior, and
they change from "executed" to "literal", which is the documented intent.

## Acceptance criteria

**AC-1 — A mapping `base_url` containing `$(...)` or `` ` `` compiles to a script that assigns it literally.**
Compiling a flow whose mapping sets `base_url: "http://localhost:3000/$(id -u)"`
emits a `BASE_URL=` line in which the `$` and any backtick are backslash-escaped.
Verified by: a `node --test` case in `e2e-pipeline/compiler/test/` asserting the
emitted line contains the escaped form and NOT the raw `$(id -u)`.
Falsified by: removing the escaper call at `compiler/codegen.js:154` — the test
must go red.

**AC-2 — Executing the emitted script's variable prologue performs no command substitution (the end-value AC).**
The prologue emitted from inputs seeded with `$(...)`, `` `...` `` and `${VAR}`
sentinels, when run under a real `bash`, leaves a canary file uncreated and
assigns each variable the exact literal source text.
Verified by: a test that compiles such a flow, executes the emitted
variable/header prologue under `bash`, and asserts (a) the canary path does not
exist and (b) the variable's runtime value equals the literal YAML string.
Falsified by: reverting any single escaper call fixed under AC-1/AC-3 — the
canary appears or the value differs.

**AC-3 — Step ids reaching `echo` lines and `_record_step_name` are inert against `$(...)` and backticks.**
A flow with a step id containing `$(id -u)` and a backtick compiles to a script
whose `echo` and `_record_step_name` emissions treat the id as literal text.
Verified by: a `node --test` case compiling that flow and executing the
generated `echo` / `_record_step_name` lines under `bash`, asserting the printed
and recorded step name equals the literal id.
Falsified by: dropping `escapeDoubleQuoted` at `compiler/codegen.js:1271`.

**AC-4 — The audit closes the class: every expansion-active emission context for a flow-/mapping-sourced string is enumerated and classified.**
The implementation stage report contains a file:line table covering every such
context in the compiler, each marked ESCAPED (naming the helper) or
SINGLE-QUOTED (inert), with no context left unclassified, and each context that
was MISSING-ESCAPE at the start has both a fix and a test.
Verified by: the table in the stage report, cross-checked by validation
independently re-deriving the context list from the code (not from the table).
Falsified by: validation finding one expansion-active emission context absent
from the table, or a table row whose cited `file:line` does not match the file.

**AC-5 — `runtime_values` `${NAME}` template expansion is not regressed.**
The deliberate re-enabling of `${NAME}` in `runtimeTemplateDoubleQuote`
(`compiler/codegen.js:197`) still expands as before.
Verified by: the pre-existing `runtime_values` template tests pass unchanged
(no test edits to accommodate the fix).
Falsified by: replacing `runtimeTemplateDoubleQuote` with plain
`escapeDoubleQuoted`.

**AC-6 — No regression across the compiler suite and lint.**
`npm test` and `npm run lint` in `e2e-pipeline/` are green on the final commit.
Verified by: full-suite run output at stage exit, re-run independently by
validation.
Falsified by: any newly failing test or lint diagnostic.

## Test plan

TDD, RED before GREEN, both closing in the same session and committed together.

1. **RED** — add the AC-1 failing test (mapping `base_url` with `$(id -u)`);
   run scoped: `npm test -- ` / `node --test compiler/test/codegen.test.js`;
   record the failure output digest in the stage report.
2. **RED** — add the AC-2 executable canary test (compile → run the emitted
   prologue under `bash` → assert canary absent and literal value). Record RED.
3. **RED** — add the AC-3 step-id test. If it passes immediately, that is a
   legitimate WORKING verdict for that context: record it as a
   regression-pin test with an explicit note that no RED was possible, and
   prove the pin can fail via the AC-3 falsification edit run in a scratch copy.
4. **GREEN** — apply the minimal escaping fixes at each MISSING-ESCAPE site.
5. Re-run scoped tests to green.
6. **Adversarial spot-check** — in a scratch copy, revert one escaper call and
   confirm the suite goes red; restore. Record the evidence.
7. **Full suite once at stage exit** — `npm test` and `npm run lint` in
   `e2e-pipeline/`.
8. Validation independently re-derives the AC-4 context table from the code,
   re-runs every AC's check, and runs one cross-model review of the diff.

E2E-first note: the "real flow" for a compiler is *the generated artifact
actually executing*. AC-2 and AC-3 satisfy the E2E-first clause by running
generated bash under a real shell; a browser run is not applicable and is not
required here.

## Doc diff

None — no described behavior changes. `base_url` was never documented as an
interpolation surface (`e2e-pipeline/CLAUDE.md` YAML conventions show it as a
plain URL), so treating it literally is the documented intent, not a change to
it. If the audit turns up published wording that promises `${VAR}` expansion in
a field this task makes literal, implementation flags it at the validation gate
rather than silently editing docs.

## Out of scope

- `.github/workflows/**` — untouched, by captain directive.
- Any version bump, `plugin.json`, `.codex-plugin/plugin.json`, marketplace
  entry, or release manifest edit — release-please owns versioning.
- #179's `resolver.js` runner-substitution semantics — different layer, must
  not be regressed but is not changed here.
- #180's generated-source gate — this task does not build it, and explicitly
  does not add a new standing lint/CI lane. Closing the class here means
  escaping the sites plus regression tests, not standing up an enforcement
  mechanism.
- Contexts the audit classifies as already inert (single-quoted) get a
  classification row, not a rewrite.
- Deletions, deploys, credential handling, and any outbound address — none of
  these are performed.
