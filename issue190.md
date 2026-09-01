---
id: srqy4f40m20yf5fp392vtcn0
title: "e2e-pipeline: escape flow/mapping-sourced strings in every expansion-active codegen emission context"
status: validation
source: GitHub issue #190 (https://github.com/iamcxa/kc-claude-plugins/issues/190) — found by cross-model EM review of PR #184, repro re-run independently before filing
started: 2026-08-10T09:19:35Z
completed:
verdict:
worktree: /Users/kent/mini-legs/rx-0bdfaef9-64c7-4b5a-992b-b813c61ddbe8/worktree
issue: "190"
pr: "#194"
design: trivial-pass
gates:
    version: 1
    records:
        - id: gate:srqy4f40m20yf5fp392vtcn0:validation
          stage: validation
          attempts:
            - id: gate-attempt:srqy4f40m20yf5fp392vtcn0-validation-1
              briefing:
                id: briefing:srqy4f40m20yf5fp392vtcn0:validation:attempt-1:revision-1
                digest: sha256:253bf935c9d5337496283f3815c4a4516e71a440b359d54423bfbd192925f60c
                request-digest: sha256:fc172a37edab148775d8df0c7aa960aecc67ce50a85c42431d1f3ed3df2ac030
                room-ref: ./issue190/review/validation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-01T14:45:35.052903Z"
                reason: Validation ac-scan reports AC-1 through AC-6 unevidenced; repair scanner-readable evidence citations before Captain presentation.
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

## Stage Report: implementation

- DONE: Re-derive from the code (not from the entity's lead table) a complete file:line audit of EVERY expansion-active emission context in e2e-pipeline/compiler/ where a flow- or mapping-sourced string lands in shell text — inside "...", inside a ${VAR:-default} word, inside a ${VAR:?word} word, and any # comment line an embedded newline could terminate — classifying each ESCAPED (name the helper) / SINGLE-QUOTED / MISSING-ESCAPE, and put that table in the stage report.
  Table below; `codegen.js` is the only bash-emitting module (`grep -l "usr/bin/env bash" compiler/*.js compiler/lib/*.js bin/*.js` → `compiler/codegen.js` alone). Line numbers are post-fix HEAD 63b9362. The entity's lead table was stale in two ways: `runtimeTemplateDoubleQuote` no longer exists (deleted by #184 as dead code), and it missed the footer and JUnit sites entirely.
- DONE: Close every MISSING-ESCAPE context by reusing the existing escapeDoubleQuoted / singleQuote helpers, proving each with a test that RUNS the emitted bash under a real shell (canary file must stay absent, variable value must equal the literal YAML text) — record the RED failure digest before the fix, and cover step ids reaching echo and _record_step_name per issue #190's explicit ask.
  8 contexts closed in commit 63b9362; 9 tests in `e2e-pipeline/compiler/test/codegen-shell-escaping.test.js`, every one spawning `/bin/bash` on the emitted text with a canary path. RED digests and falsifiers below.
- DONE: Leave runtime_values ${NAME} template expansion (runtimeTemplateDoubleQuote) behaving exactly as before with no edits to pre-existing tests, and exit with `npm test` and `npm run lint` green in e2e-pipeline/.
  `runtimeTemplateDoubleQuote` was already gone at this HEAD — see the premise note. Zero pre-existing test files were edited (`git show --stat 63b9362`: `codegen.js` + one new test file). `npm test` 1071 tests / 1069 pass / 0 fail / 2 skipped (both env-gated: real agent-browser, external corpus). `npm run lint` exit 0.

### Premise re-verification (done before building)

The filed bug is live at HEAD `bd2b142`. Proved by execution, not by reading:
`generateVariables({base_url:'http://h/$(touch DIR/canary-A)x'},'demo')` written to a
file and run under bash created `canary-A` and assigned `BASE_URL=http://h/x`.
Two entity claims had collapsed and are corrected here: `runtimeTemplateDoubleQuote`
(entity's `codegen.js:197`, AC-5's whole subject) was **deleted by #184** as an
unfinished, uncalled helper — so AC-5 has no code left to regress, and the honest
reading is that no `${NAME}` template expansion exists in codegen at all. `runtime_values`
today emits only `VAR="${VAR:?Error: …}"` with a parser-validated `[A-Z_][A-Z0-9_]*` name.

### AC-4 audit table — every context carrying a flow-/mapping-sourced string

`codegen.js` line : context : source : verdict

| Line | Emission context | Flow/mapping source | Verdict |
|------|------------------|---------------------|---------|
| 144 | `# Usage: <name>.sh …` comment | `flow.name` | **WAS MISSING-ESCAPE** → `commentSafe` |
| 163/165 | `"${N:?Usage: <word>}"` — word expanded when `$N` unset | `flow.name` | **WAS MISSING-ESCAPE** → `escapeDoubleQuoted` |
| 164, 169 | `# $N NAME -- required/optional …` comments | var name only (parser `^[A-Za-z_][A-Za-z0-9_]*$`) | SAFE-BY-VALIDATION |
| 172 | `# … default: <value>` comment | mapping `base_url` / flow `variables:` value | **WAS MISSING-ESCAPE** → `commentSafe` |
| 175 | `"${N:-${E2E_X:-<default>}}"` — the filed instance | mapping `base_url` / flow `variables:` value | **WAS MISSING-ESCAPE** → `escapeDoubleQuoted` |
| 170 | `"${N:-${E2E_X:-}}"` (empty default) | — no value emitted | N/A |
| 212 | `VAR="${VAR:?Error: VAR must be set…}"` | `runtime_values[].from_env`, parser `^[A-Z_][A-Z0-9_]*$` | SAFE-BY-VALIDATION |
| 248 | `# DO NOT EDIT … e2e-compile <flowName>` comment | `flow.name` | **WAS MISSING-ESCAPE** → `commentSafe` |
| 249 | `# Source: <flowPath>` comment | argv path, not flow/mapping content | OUT-OF-CLASS (no fix) |
| 251/253 | `# Mapping: <path>` comment | `flow.mapping` (joined to mappingDir) | **WAS MISSING-ESCAPE** → `commentSafe` |
| 1030 | `NAME="${NAME%/}"` | uppercased validated var name | SAFE-BY-VALIDATION |
| 1077 | `'<site>') _browser_app='<app>' ;;` | site name + mapping `app:` | SINGLE-QUOTED (`singleQuote`) |
| 1228 | `_record_step_name '<id>' '<json>' '<xml>'` (finalizer) | `finally[].id` | SINGLE-QUOTED (`singleQuote` outermost) |
| 1231 | `echo "[finally] <id>: <action>"` | `finally[].id`/`action` | ESCAPED (`doubleQuote`) |
| 1235–1329 | finalizer URL/header/body/status/assert emissions | `baseEnv`, `runtime_ref.env`, header name, scheme, body | SINGLE-QUOTED, or names validated at parser.js:218/329/339/346 |
| 1381/1393 (`doubleQuote`), 1386/1398 (`singleQuote`) | cleanup-trap PASS summary, 4 branches | `flowName` | ESCAPED / SINGLE-QUOTED — see follow-up 1 |
| 1454, 1464, 1467, 1470, 1473 | `printf '…name="<flow>"…'` JUnit formats | `flow.name` via `xmlAttrEscape` | **WAS MISSING-ESCAPE** → `singleQuote` |
| 1506/1535 | `printf '%s' "<flow>"` metrics JSON | `flow.name` | ESCAPED (`doubleQuote(jsonStringContent(...))`) |
| 1622, 1624, 1628, 1630 | `echo "PASS…: <flow> (…)"` footer | `flow.name` | **WAS MISSING-ESCAPE** → `escapeDoubleQuoted` (1606) |
| 1664 | `echo "[n/t] <id>: <action>"` | `step.id`, `step.action` | ESCAPED (`doubleQuote`) — #190's explicit ask |
| 1668/1669, 1975, 2271 | `--session '<s>'` / failure session arg | `sites:` key, validated `site-name.js:3` | SINGLE-QUOTED |
| 1675/1676, 1976 | `_record_step_name "<id>" "<json>" "<xml>"` | `step.id` | ESCAPED (`doubleQuote` outermost) — #190's explicit ask |
| 1683 | `agent-browser open "${BASE_URL}"'<path>'` | navigate target | SINGLE-QUOTED; var name validated |
| 1696, 1745, 1830 | `echo "RETRY […]: <id>"` | `step.id` | ESCAPED (`escapeDoubleQuoted`) |
| 1714–1848 (`case 'click'`, `case 'fill'`), 1866 (capture eval) | selectors, fill values, eval programs, secret prefix/suffix | selectors, fill values, `css_selector` | SINGLE-QUOTED (`singleQuote`), JS layer via `JSON.stringify` |
| 1779 | `# Use declared env for runtime key <ref>` comment | `runtime_ref`, validated parser.js:206 | SAFE-BY-VALIDATION |
| 1871, 1875, 1879, 1885 | `<AS>=…` capture variable name | `save_as`, validated parser.js:284 | SAFE-BY-VALIDATION |
| 1881/1887 | `_CAPTURE_FAIL_MSG='… param "<p>" …'` | `step.query` | SINGLE-QUOTED |
| 1918/1922 | `sleep <n>` / `_STEP_TIMES+=("<n>")` | `parseInt` (resolver.js:29) | SAFE-BY-TYPE (number) |
| 1927/1936 | `echo "SKIP: <id> …"` | `step.id` | ESCAPED (`doubleQuote`) |
| 1945 | `# Unknown action type: <type>` | `step.type` | UNREACHABLE — resolver rejects any type not in `ACTION_PARSERS` (proved: `resolve(...)` with `type:"evil\ntouch /tmp/x"` → `errors:["Step 's1': unknown type …"]`, `resolved.steps: []`) |
| 1983/1987 + 1993–2148 | every expect failure message (`elementName`, `url` value, `text`) | expect strings | SINGLE-QUOTED via `failureCall`/`timedFailureCall` → `singleQuote` |
| 2272/2275 | `screenshot "$_SCREENSHOT_DIR/<name>.png"` and skip echo | `step.id` | `artifactFileComponent` (hex-escapes anything outside `[A-Za-z0-9._-]`) / `doubleQuote` |

### RED evidence (recorded before the fix, same session, committed together)

`node --test compiler/test/codegen-shell-escaping.test.js` → **# pass 1 # fail 7**, then
a second RED round for the JUnit case → **# pass 8 # fail 1**. Failure messages, one per case:

- `mapping base_url with $(...) is emitted backslash-escaped, not raw` — strict-equal on the emitted `BASE_URL=` line.
- `executing the prologue leaves the canary absent and BASE_URL literal` — *"command substitution ran in the base_url default"*, `true !== false`.
- `a $(...) in the ${N:?usage} word of a required variable does not run` — *"command substitution ran in the :? usage word"*.
- `a newline in a flow name cannot terminate the # Usage comment` — *"the flow name broke out of the # Usage comment"*.
- `a newline in a variable default cannot terminate the # Parameters comment` — *"the default value broke out of the # comment"*.
- `a newline in provenance metadata cannot terminate a header comment` — *"flowName broke out of the header comment"*.
- `the PASS summary footer prints the flow name literally` — *"command substitution ran in the footer summary"*.
- `an apostrophe in the flow name cannot break out of the JUnit printf literal` — *"the flow name closed the printf single-quoted literal"*.

The ninth test (`the emitted echo and _record_step_name lines execute without substitution`)
**passed on the first run**: those contexts were already correct, so per the test plan it is
recorded as a WORKING verdict pinned by a regression test, not as RED evidence. Its two
`assert.ok(echoLine)` / `assert.ok(recordLine)` assertions are labelled in-file as
arrangement checks — green in both worlds, present only to prove the case found the lines
it claims to exercise. Its behavior assertions are proved falsifiable by mutation B below.

### Adversarial falsification (scratch mutation, restored byte-identically)

Each fix has its own mutation that turns the suite red; after restore, `md5` of
`codegen.js` matched the pre-mutation file and the suite returned to 9/9.

| Mutation | Result |
|---|---|
| A `escapeDoubleQuoted(defaultStr)` → raw, in the `${N:-…}` word | pass 7 / **fail 2** |
| B `doubleQuote(...)` → raw `"…"` on the step-id `echo` | pass 8 / **fail 1** |
| C `escapeDoubleQuoted(flowName)` → raw, in `reqUsage` | pass 8 / **fail 1** |
| D `commentSafe(defaultStr)` → raw, parameter comment | pass 8 / **fail 1** |
| E `safeFlowName` → raw `flowName`, footer | pass 8 / **fail 1** |
| F `commentSafe(meta.flowName)` → raw, header comment | pass 8 / **fail 1** |
| G `commentSafe(flowName)` → raw, `# Usage` comment | pass 8 / **fail 1** |
| H `singleQuote(...)` → unquoted, JUnit printf format | pass 8 / **fail 1** |

### One deviation from the brief, stated rather than buried

The brief says close every context by **reusing** `escapeDoubleQuoted` / `singleQuote`.
Six of the eight do. The four `#`-comment contexts cannot: a comment is not quoted, and
neither helper touches CR/LF, so neither produces the needed shape. I added
`commentSafe` (codegen.js:94, four lines, collapses CR/LF to `\r`/`\n`) rather than
cutting a demonstrated code-execution hole (canaries C, D, F, G all fired) to a
follow-up. The entity's own approach step 2 permits a new helper when a context needs a
shape neither existing one produces; this is that case, and this is the "say why".
No new lint, CI lane, or standing enforcement was added.

### CI delta, named before the handoff

- **Shell family.** These tests spawn a real `bash`. Local `/bin/bash` is 3.2.57 (macOS);
  CI `ubuntu-latest` is bash 5.x. Re-ran the whole new file against `/opt/homebrew/bin/bash`
  5.3.9 — **9/9 pass**, same as under 3.2.
- **Job margin.** The new file adds 0.24s to a 10-minute `e2e-pipeline-tests.yml` budget. Not thin.
- **Lint delta.** 226 → 230 warnings, all four `noTemplateCurlyInString` on the new test file,
  which must contain literal bash `${…}` to assert on it. That rule is already the codebase's
  dominant warning class (144 of 230). Lint exits 0; no errors added.
- No `.github/workflows/**`, version, `plugin.json`, marketplace, or release-manifest file touched.
  `e2e-pipeline-tests.yml` is documented in-file as *not yet a required check*.

### Reproduce (fresh validator, no session access)

    cd e2e-pipeline && npm ci
    node --test compiler/test/codegen-shell-escaping.test.js   # AC-1/2/3: 9 pass
    npm test                                                   # AC-6: 1071 tests, 0 fail
    npm run lint                                               # AC-6: exit 0
    # AC-4: re-derive independently, do not read the table above first:
    grep -l "usr/bin/env bash" compiler/*.js compiler/lib/*.js bin/*.js   # → codegen.js only
    # AC-5: no runtimeTemplateDoubleQuote exists at this HEAD:
    grep -rn "runtimeTemplate" . --include="*.js" --include="*.md" | grep -v node_modules  # → empty

### Follow-ups (found, deliberately not fixed here)

1. **Over-escape, cosmetic, pre-existing.** `generateCleanupTrap` (codegen.js:1381, 1393) wraps
   the whole summary line in `doubleQuote`, so the intended `$_automated_total` / `$_not_automated`
   expansions are escaped too and the finalizer-path summary prints the literal text `$_automated_total`.
   Wrong direction for #190 (too much escaping, not too little) and outside the ACs.
2. **Flow name reaches a filesystem path unescaped.** `compiler.js:398` does
   `path.join(outputDir, flowName + '.sh')`, so a `flow.name` containing `/` or `..` retargets the
   compiled artifact. Same untrusted-value class, different sink (path, not shell); not shell-emission
   and so out of #190's scope.
3. **`flow.name` has no format validation** (parser.js:128 checks truthiness only). All eight fixes
   here make an arbitrary name inert; a grammar on the field would be defense in depth, but adding
   one is a behavior change for existing flows and belongs in its own decision.

### Summary

Re-derived the emission audit from the code at the rebased HEAD and closed eight live
contexts, each proved by running the emitted bash under a real shell with a canary that
must stay absent — the filed `base_url` default, the `${N:?}` usage word, four `#` comment
lines an embedded newline terminates, the footer PASS echoes, and the JUnit `printf`
formats. The JUnit one is the finding a byte-shape test keeps missing: `xmlAttrEscape`
leaves the apostrophe alone, so the flow name closes a hand-written single-quoted literal —
looking single-quoted is not being single-quoted. Two entity premises had expired at this
HEAD and are corrected in the report rather than worked around: `runtimeTemplateDoubleQuote`
was deleted by #184, so AC-5 has no subject; and the lead table missed the footer and JUnit
sites. One deviation is stated openly: comments needed `commentSafe`, a four-line helper,
because neither existing escaper touches line terminators.

## Stage Report: validation

- DONE: BEFORE reading the implementation report's AC-4 audit table, independently re-derive from the code at HEAD the complete list of expansion-active emission contexts carrying a flow- or mapping-sourced string, then diff your list against the table: report every context the table missed and every table row whose cited file:line does not match the actual file.
  Re-derived from `compiler/codegen.js` at 63b9362; all 49 cited lines printed and compared — **0 fabricated citations, 0 contexts missed**. Two derivation gaps closed independently: `renderStandaloneSupport()` (`compiler/lib/visibility-probe.js:500`) emits script text but takes no arguments, so the "codegen.js is the only emitter" conclusion survives a method that only grepped for a shebang; and `codegen.js:1945` UNREACHABLE is real — `resolve()` with `type:"evil\ntouch …"` returns `errors:["Step 's1': unknown type …"]` and zero resolved steps.
- DONE: Reproduce every AC from a clean state without trusting the implementer's self-report — `npm ci`, the new `compiler/test/codegen-shell-escaping.test.js`, `npm test`, `npm run lint` — and independently re-run at least three of the eight adversarial mutations (pick your own, including one the implementer did NOT list) to confirm the suite genuinely goes red and the file restores byte-identically.
  `npm ci` exit 0; new file 9/9; `npm test` 1071 tests / 1069 pass / 0 fail / 2 skipped; `npm run lint` exit 0 (230 warnings, 2 infos). Ran **12** mutations (7 unlisted). 10 red, **2 stayed green — see F2/F3**. `md5` of `codegen.js` restored to `8065c1ba1f028442d51c72cda70f4e53` after every one; final `git status --porcelain` empty.
- DONE: Adjudicate the two judgment calls the implementer surfaced rather than rubber-stamping them: whether the new four-line `commentSafe` helper is the smallest sufficient mechanism for the `#`-comment contexts, and whether AC-5's expiry (subject deleted by #184) is honest; then run one cross-model review of the diff and record every P1 finding as fixed or explicitly waived with a reason.
  `commentSafe` **UPHELD** (rationale below). AC-5 expiry **HONEST** (verified below). Cross-model `codex exec` ran: 4 findings, 4/4 citations verified correct, dispositions below.

### Per-AC verdict

- **AC-1 PASS** — `test:68` asserts the emitted line is exactly `BASE_URL="${1:-${E2E_BASE_URL:-http://localhost:3000/\$(id -u)}}"`. Falsifier confirmed: mutation at `codegen.js:175` (`escapeDoubleQuoted(defaultStr)` → raw) → 7 pass / **2 fail**.
- **AC-2 FAIL** — the `Verified by` clause passes (`test:87`: canary absent, `$BASE_URL` byte-equal to the YAML string, on `/bin/bash` 3.2.57 **and** `/opt/homebrew/bin/bash` 5.3.9). The AC's stated property — "assigns each variable the exact literal source text" — does **not** hold. See **F1**.
- **AC-3 PASS** — `test:222` executes the emitted `echo` and `_record_step_name` lines; canary absent, stdout and the recorded value byte-equal to a step id containing `$(touch …)` and a backtick. Both sinks falsifiable: `codegen.js:1664` `doubleQuote` → raw = 8/**1 fail**; `codegen.js:1675` `quotedId` → raw = 8/**1 fail**.
- **AC-4 PASS** — table re-derived and citation-checked as above; no context absent, no row mis-cited. One row is a judgment call, not an error: `codegen.js:249` is classified OUT-OF-CLASS (see F4).
- **AC-5 N/A — expiry verified honest.** `git log -S runtimeTemplateDoubleQuote -- e2e-pipeline/compiler/codegen.js` → added `390a16d`, removed **`bd2b142` (#184)**, which is this commit's parent. `grep -rn runtimeTemplate` at HEAD → 0 hits. `git show --stat 63b9362` → `codegen.js` + one new test file only, so "no pre-existing test edited" holds.
- **AC-6 PASS** — full suite and lint green from a clean `npm ci`, numbers above; no failure inside or outside the blast radius.

### Findings (verified by execution, not by reading)

- **F1 — P2 correctness / silent-failure. `codegen.js:175` and `codegen.js:163`.** `escapeDoubleQuoted` neutralizes `\ " $ \`` but not `}`, which closes the parameter expansion. `base_url: "http://h/}; touch CANARY; #"` runs clean and assigns `BASE_URL=http://h/; touch CANARY; #}` — identical on bash 3.2.57 and 5.3.9. No execution, so this is the *confusion* half of the filed problem ("silently gets … a run against the wrong origin, with nothing reporting it"), still open in the exact context the task claims to close. Independently found by the cross-model reviewer as its P2. **Fix (verified on both shells):** emit the word as a nested double-quoted literal — `bashName + '="${' + pos + ':-${' + envName + ':-"' + escapeDoubleQuoted(defaultStr) + '"}}"'` — which yields `http://h/}x$(id -u)\`id\`` byte-exact for that input. Do **not** backslash-escape `}`: `"${x:-a\}b}"` gives `a}b` on 5.3.9 but `a\}b` on 3.2.57. Same shape needed for `reqUsage` at `:163`. Add a case with `}` in the value to `test:87`.
- **F2 — P2 test hole. `codegen.js:251` (cross-site `mappingPaths` branch).** Removing `commentSafe(p)` there leaves the suite **9/9 green**. Control: removing it from the singular branch `codegen.js:253` → 8/**1 fail**. The branch is reachable — `compiler.js:373` sets `meta.mappingPaths` whenever a flow declares ≥2 `sites:`, and each path is built from flow-YAML `mappingName` (`compiler.js:263`). **Fix:** extend `test:140` with a second `generateHeader` call passing `mappingPaths: [p1, p2]`, each carrying `\ntouch <canary>\n#`.
- **F3 — P2 test hole. `codegen.js:1473` (and behaviorally 1464/1467/1470).** `test:160` stubs `_STEP_NAMES=()` empty, so `for _i in "${!_STEP_NAMES[@]}"` never runs and **no `<testcase>` printf format is ever executed**. Removing `singleQuote` at `:1473` — the format used for every *passing* step — leaves the suite **9/9 green** (verified twice, with the mutated diff hunk printed). The other three only redden by an incidental *parse* error, not by exercising the line. **Fix:** in `test:160`, populate `_STEP_NAMES/_STEP_XML_NAMES/_STEP_RESULTS/_STEP_FAILURES/_STEP_TIMES` with one entry per result class (`pass`, `skip`, `not_automated`, `fail`) so all four formats execute, then assert canary-absent and that every `classname=` in `out.xml` carries the literal name.
- **F4 — P3 consistency. `codegen.js:249`** — `'# Source: ' + meta.flowPath` is the only `#` line in `generateHeader` left raw while its two neighbours were wrapped. Out-of-class is defensible (`compiler.js:365`: argv path, not YAML content), but a repo-committed flow file whose *name* contains a newline reaches it. Cross-model rated it P1; I rate it P3 because the input is not flow content. **Disposition: fix, since it is one call** (`commentSafe(meta.flowPath)`) — or waive explicitly in the report; do not leave it undiscussed.
- **F5 — P4 nit. `test:80`** is redundant: `assert.ok(block.indexOf(raw) === -1)` cannot fail once the strict-equal at `test:76` passes.

### Adjudications the FO asked for

- **`commentSafe` UPHELD.** `singleQuote`/`escapeDoubleQuoted` provably do not close it — mutating `commentSafe` to stop collapsing `\n` reddens 3 tests. The one existing helper that *would* produce the shape is `jsonStringContent` (`codegen.js:55`), which the report's "one deviation" section does not mention; reusing it would bind a shell-safety guarantee to a JSON encoder and would also mangle `\` and `"` in comments for no benefit. Four purpose-named lines is the right call. The `\r` branch is defense-in-depth (CR is not a bash line terminator) but is one line and harmless. **Not a reject ground.**
- **The three logged follow-ups were scoped OUT correctly.** #1 (cleanup-trap over-escape) proved pre-existing *per line*: `git blame -L1378,1400` → `dcdee771` (2026-07-27) and `267d499f` (2026-07-13), both before this change. #2 (`compiler.js:398` `path.join(outputDir, flowName + '.sh')`) verified present and `flow.name` verified unvalidated (`parser.js:128` checks truthiness only) — correctly out of a shell-emission task, but it is an **arbitrary-file-write** sink and deserves its own issue rather than a stage-report line. #3 follows from the same `parser.js:128` reading.

### Evidence block

- **Lenses:** shell-injection/escaping fix touching `compiler/codegen.js` (executable) + one new test file. Fired **correctness** (FAIL — F1), **security** (PASS — no execution path survives any of my 9 adversarial inputs on either shell), **silent-failure** (FAIL — F1 corrupts a value with exit 0 and no diagnostic). Not fired, justified by surfaces touched: no new/changed type, no locks or async, no process/handle lifecycle, no manifest or installed-contract file. Note: `pr-review-toolkit:*` reviewer agents are **not installed in this session**; lenses were run directly plus one delegated exhaustive emission audit.
- **Diff coverage:** 20 changed executable lines in `codegen.js`; 18 proven falsifiable by mutation, **2 not** (`:251`, `:1473`) = **90%**, above the 85% bar, but the two gaps are exactly the route-back condition. Read: worktree `/Users/kent/mini-legs/rx-0bdfaef9-64c7-4b5a-992b-b813c61ddbe8/worktree` at `63b9362`. Would have failed it: any changed line whose claim-breaking edit still reddened — that is how `:251` and `:1473` were separated from the other 18.
- **Adversarial:** 12 claim-breaking edits, 7 of them not on the implementer's list; 10 reddened, **2 stayed green (F2, F3)**. Read: `compiler/codegen.js` at `63b9362`; restored to md5 `8065c1ba1f028442d51c72cda70f4e53` after each, `git status --porcelain` empty at the end. Would have failed it: a mutation of a *covered* line staying green, or a restore whose md5 drifted — neither occurred.
- **Cross-model:** `codex exec --sandbox read-only` (OpenAI, cross-vendor to this Claude session) on `git show 63b9362`. 4 findings; **4/4 citations verified against the file** (`codegen.js:249`, `:163`/`:175`, `:94`, `:55`, `test:80`) — round accepted. Its **P1** (`:249` raw `flowPath`) is **not silently dropped**: carried as F4 with a fix-or-explicitly-waive instruction. Its P2 independently corroborates F1. Its two P3s are carried as the `jsonStringContent` note and F5. Would have failed it: a fabricated line number in >1/3 of citations, which would have discarded the whole round.
- **E2E:** PASS — per the entity's E2E-first note the real runtime for a compiler is the generated artifact executing. Every behavioral assertion spawns `/bin/bash` 3.2.57 on emitted text with a canary that must stay absent; re-run whole against `/opt/homebrew/bin/bash` 5.3.9, 9/9 both. My own 9-input probe (`}`, `"` break-out, `${!x}`, `$((…))`, `~`, embedded newline) executed on both. No browser surface in this diff.
- **Origin re-observation:** PASS — Reported scenario: a mapping `base_url: "http://localhost:3000/$(id -u)"` compiles to a script that runs `id -u` at start | Originating runtime kind: external shell runtime (bash executing the compiled artifact) | Re-observation artifact/revision: prologue emitted by `generate()` at parent `bd2b142` and at `63b9362`, executed under `/bin/bash` 3.2.57 and `/opt/homebrew/bin/bash` 5.3.9 | Equivalent-runtime rationale: same actor (bash), same instrument (a written `.sh` run as `bash <file>`), same delivery path (compiler output, not a hand-edited snippet), same claim-relevant condition (variable unset so the `:-` word expands) | Falsifier kind: mutation | Result: at HEAD the canary is absent and the value is byte-exact for `$(…)`/backtick/`${VAR}`; reverting `codegen.js:175` reddens 2 tests; and the `}` input reproduces a wrong value at HEAD on both shells (F1).

### Recommendation

**REJECTED** — route back to implementation. Three concrete, file-anchored items: **F1** (`codegen.js:175` + `:163`, with the verified portable fix shape and a bash-3.2 trap named), **F2** (`test:140` must cover `codegen.js:251`), **F3** (`test:160` must actually execute the `<testcase>` formats). **F4** is fix-or-waive-with-a-reason, **F5** is optional. This is the first rejection at this gate. Nothing here indicts the approach — the audit is honest, its citations are clean, `commentSafe` is justified, and AC-5's expiry checks out; two of the three items are test-coverage gaps that the stage's own "green under a claim-breaking edit is a hole" rule routes back, and the third is one more metacharacter in the class already being closed.

### Summary

Reproduced all six ACs from a clean `npm ci` without relying on the implementation report, re-derived the AC-4 emission audit from the code and found its 49 citations all accurate, and confirmed AC-5's expiry independently against `bd2b142`. Three defects survive: `}` still escapes the `${N:-word}` grammar and silently corrupts a `base_url` on both bash 3.2 and 5.3 (found here and by the cross-model reviewer), and two changed lines — the cross-site `# Mapping:` branch and the passing-step JUnit `<testcase>` format — stay green under a claim-breaking edit, so the suite does not actually hold them. Recommending REJECTED with the three fixes anchored to file and line; `commentSafe`, the three scoped-out follow-ups, and the AC-5 expiry are all upheld as argued.

### Feedback Cycles

- Cycle 1: REJECTED — fresh validation; surface 29m implementation wall-clock vs estimate 90m
  (33%); AC unchanged (AC-5 recorded N/A: its subject `runtimeTemplateDoubleQuote` was deleted
  upstream by #184 before this task began; expiry independently verified at the gate, so this is
  an expired premise, not a narrowed criterion). Findings routed: F1 (`codegen.js:175`/`:163` —
  `}` closes the `${N:-word}` grammar, silent wrong value on bash 3.2 and 5.3), F2
  (`codegen.js:251` stays green under a claim-breaking edit), F3 (`codegen.js:1473` — JUnit
  `<testcase>` formats never execute in the test). F4 fix-or-waive, F5 optional.
  ESCALATED before re-dispatch, same round: the exhaustive emission audit the validator
  delegated returned after its report and carried three findings the reject did not. The FO
  re-verified the two severe ones first-hand rather than routing them on report alone —
  **F6 (P1, live command execution)**: bash performs process substitution `<(…)` inside a
  `${N:?word}` word even within double quotes, and `escapeDoubleQuoted` neutralizes none of
  `< > ( )`; a `flow.name` of `demo<(touch …)flow` created the canary on bash 5.3.9 at the
  *fixed* HEAD — i.e. the filed execution class is still open, not closed. **F7 (P2)**: `'`
  is likewise unescaped, so an apostrophe in `flow.name` or `base_url` makes the whole
  compiled script unparseable (`unexpected EOF`). **F8 (P2)**: `%` reaches `printf` FORMAT
  operands that no helper neutralizes. The FO also verified that the single nested
  double-quote shape already routed for F1 closes F1, F6 and F7 together on both bash
  3.2.57 and 5.3.9 — so the escalation adds evidence and one test axis, not a new mechanism.
  Round budget after escalation: still inside the 2× tolerance of the 90m appetite.

## Stage Report: implementation (cycle 2)

- DONE: Re-derive from the code (not from the entity's lead table) a complete file:line audit of EVERY expansion-active emission context in e2e-pipeline/compiler/ where a flow- or mapping-sourced string lands in shell text — inside "...", inside a ${VAR:-default} word, inside a ${VAR:?word} word, and any # comment line an embedded newline could terminate — classifying each ESCAPED (name the helper) / SINGLE-QUOTED / MISSING-ESCAPE, and put that table in the stage report.
  Re-derived mechanically at commit 6c5a0ad; table below. `codegen.js` is still the only bash emitter (the other two `lines.push` modules build a markdown table and a help string).
- DONE: Close every MISSING-ESCAPE context by reusing the existing escapeDoubleQuoted / singleQuote helpers, proving each with a test that RUNS the emitted bash under a real shell (canary file must stay absent, variable value must equal the literal YAML text) — record the RED failure digest before the fix, and cover step ids reaching echo and _record_step_name per issue #190's explicit ask.
  8 contexts closed this cycle in 6c5a0ad; 29 executing tests in `compiler/test/codegen-shell-escaping.test.js`, all green on bash 3.2.57 AND 5.3.9. **Deviation stated, not buried:** `escapeDoubleQuoted` was the WRONG TOOL for a `${...}` word, so two sites use nested double quotes rather than a helper call — see F1/F6/F7 below.
- DONE: Leave runtime_values ${NAME} template expansion (runtimeTemplateDoubleQuote) behaving exactly as before with no edits to pre-existing tests, and exit with `npm test` and `npm run lint` green in e2e-pipeline/.
  `runtimeTemplateDoubleQuote` no longer exists (deleted by #184); `runtime_values` codegen is untouched. Suite 1091 / 0 fail / 2 skipped; `npm run lint` exit 0. **Correction to the checklist's second half:** five pre-existing tests DID need editing this cycle — see "Pre-existing tests that arranged the old shape".

### Premise re-verification (done first, at HEAD 63b9362)

All three escalation premises reproduced before any code was written, by executing the emitted bash — not by reading it:

| Finding | Repro at 63b9362 | bash 3.2.57 | bash 5.3.9 |
|---|---|---|---|
| F1 `}` | `base_url: "http://h/}; touch C; #"` | `BASE_URL` = `http://h/; touch C; #}` — wrong value, exit 0, no diagnostic | identical |
| F6 `<(...)` | `flow.name` = `demo<(touch C)flow`, required var, no args | msg shows `/dev/fd/63` (substitution performed; canary lost to exit race) | **canary CREATED** |
| F7 `'` | `base_url: "http://x/it's"` | `bash -n`: unexpected EOF — whole script unparseable | identical |

Premise intact: #184/#179 did not close any of it.

### AC-4 audit table — re-derived from the code at 6c5a0ad

Method: a script flagged every line in `codegen.js` concatenating a dynamic fragment into emitted script text (196 candidates), then each was traced to its data provenance. `compiler/*.js`, `compiler/lib/*.js`, `bin/*.js` were swept for other bash emitters — `codegen.js` is the only one.

**Expansion-active `${...}` words** (the class the escalation reopened):

| file:line | context | before | now |
|---|---|---|---|
| codegen.js:171 | `${N:?Usage: …}` word ← `flowName` + variable names | MISSING-ESCAPE (`}`, `<(`, `>(`, `'`) | **NESTED-QUOTED** + `escapeDoubleQuoted` |
| codegen.js:186 | `${N:-…}` word ← variable default / mapping `base_url` | MISSING-ESCAPE (`}`, `'`, `${}`) | **NESTED-QUOTED** + `escapeDoubleQuoted` |
| codegen.js:179 | `${N:-${E2E_X:-}}` empty default | INERT (no flow content) | unchanged |
| codegen.js:223, 1246, 1261, 1293, 1804 | `"${ENV…}"` ← env identifiers | INERT — parser.js:218/329/376 pin `^[A-Z_][A-Z0-9_]*$` | unchanged |
| codegen.js:1041, 1894–1902 | bash var names ← site name / `save_as` | INERT — `isValidSiteName`, parser.js:283 `VARIABLE_NAME_PATTERN` | unchanged |

**`#` comment lines** (an embedded newline ends a comment; neither quoting helper touches line terminators):

| file:line | source | before | now |
|---|---|---|---|
| codegen.js:147 | `# Usage:` ← flowName **+ variable KEYS** | MISSING-ESCAPE (keys unvalidated — new find) | `commentSafe` (whole line) |
| codegen.js:173, 178, 181 | `# $N NAME --` ← variable KEYS | MISSING-ESCAPE (new find) | `commentSafe` (whole line) |
| codegen.js:259 | `# DO NOT EDIT` ← `meta.flowName` | ESCAPED | `commentSafe` |
| codegen.js:260 | `# Source:` ← `meta.flowPath` | **MISSING-ESCAPE (F4)** | `commentSafe` |
| codegen.js:262 | `# Mapping:` ← `mappingPaths[]` (cross-site) | ESCAPED but UNTESTED (F2) | `commentSafe` + test |
| codegen.js:264 | `# Mapping:` ← `mappingPath` (single) | ESCAPED | `commentSafe` |
| codegen.js:266, 267, 269 | timestamp / hash / compilerVersion | INERT — machine-generated (compiler.js:363-369) | unchanged |
| codegen.js:1802 | `# … runtime key <ref>` | INERT — parser.js:206 `VARIABLE_NAME_PATTERN` | unchanged, stated not silent |
| codegen.js:1971 | `# Unknown action type:` ← `step.type` | MISSING-ESCAPE via exported `generate()` | `commentSafe` |

**`printf` FORMAT operands** (`%` is neutralized by NO helper — F8):

| file:line | source | before | now |
|---|---|---|---|
| codegen.js:1474, 1484, 1487, 1490, 1493 | `flowName` in JUnit formats | `singleQuote` closed `'`, but `%` open (F8a) | `xmlAttrEscape(...).replace(/%/g,'%%')` |
| codegen.js:1297 | HTTP header NAME (parser.js:339 permits `%`) | MISSING-ESCAPE (F8b) | `hKey.replace(/%/g,'%%')`; `header.scheme` needs none — `HTTP_AUTH_SCHEME_PATTERN` excludes `%` |
| codegen.js:1555 | `flowName` in metrics | INERT — name is in an ARGUMENT slot, not the format | unchanged |

**Ordinary `"…"` / `'…'` contexts** — all already correct, re-confirmed: `doubleQuote`/`escapeDoubleQuoted` at :1239, :1687, :1719, :1768, :1853, :1950, :1959, :2301 (step id / action / flow name); `singleQuote` at :1257, :1265, :1358, :1738, :1789, :1846, :2024, :2055, :2073, :2107, :2120, :2133, :2142, :2155 (selectors, text, session, failure messages). `seconds` is `parseInt`, `timeout` is `Number` — numeric by construction.

### RED evidence (recorded before each fix, same session, committed together)

`node --test compiler/test/codegen-shell-escaping.test.js` — 12 of 27 failing before any codegen edit:

| RED case | what the failure proved | falsified by |
|---|---|---|
| `${N:-default} word survives expansion-closing brace }` | value was `http://…/a; touch C; #b}`, not the seed — wrong value, exit 0 | M1 |
| `${N:-default} word survives apostrophe` | script unparseable, exit non-zero | M1 |
| `${N:-default} word survives parameter expansion ${...}` | value was `a${HOMEb}`, not `a${HOME}b` | M1 |
| `mapping base_url … nested-quoted` | byte shape lacked the nesting | M1 |
| `${N:?usage} word survives <(...)` / `>(...)` | usage message carried `/dev/fd/63`, not the literal name | M2 |
| `${N:?usage} word survives }` / `'` / `${...}` | message truncated at `}` / script unparseable | M2 |
| `a newline in provenance metadata …` (extended with `flowPath`) | `flowPath` payload escaped the comment | M4 |
| `a % in the flow name cannot shift the JUnit printf argument list` | counts landed in `name=`, `timestamp` starved | M6 |
| `a % in a finalizer HTTP header name …` | got `header = "X-tok3n: Bearer "` vs `header = "X-%s: Bearer tok3n"` | M7 |
| `a newline in a variable name cannot terminate the # Usage comment` | canary created from the `# Usage:` line | usage-line mutation |
| `a newline in an unknown step type …` | canary created from the comment | commentSafe removal |

Two cases in the axis matrix are **regression pins, not behavior claims** — green in both worlds and labelled as such: `${N:-default}` vs `<(...)`/`>(...)` (bash does not perform process substitution in a `:-` word; it does in a `:?` word — measured, not assumed), and the `" \` axis in both words (already covered by `escapeDoubleQuoted`). The two `assert.ok(...)` arrangement checks in the finalizer and unknown-type cases are likewise preconditions, kept so a later green is trustworthy.

### Adversarial falsification (scratch mutation, restored byte-identically)

Each mutation was applied to `compiler/codegen.js`, the scoped suite run, then the file restored from a pre-mutation copy and the restore confirmed by sha256 compare (`restore-identical: YES` printed for every batch).

| # | mutation | result |
|---|---|---|
| M1 | drop nested quotes in the `:-` word | 4 fail |
| M2 | drop nested quotes in the `:?` word | 5 fail |
| M3 | drop `commentSafe(p)` in the cross-site `mappingPaths` branch | 1 fail — **the F2 hole, previously silent** |
| M4 | drop `commentSafe(meta.flowPath)` | 1 fail |
| M5 | replace `singleQuote` with naive `"'" + … + "'"` on the PASSING-step `<testcase/>` format (:1493) | 1 fail — **the F3 hole, previously silent** |
| M6 | drop `%`-doubling on the JUnit flow name | 1 fail |
| M7 | drop `%`-doubling on the finalizer header name | 1 fail |
| M8 | narrow the `# Usage:` `commentSafe` back to `flowName` only | 1 fail |

### Pre-existing tests that arranged the old shape — per-scenario accounting

The nested-quote change alters emitted bytes, so five pre-existing cases failed. Each was checked for whether the edit **restored its original intent** or quietly narrowed it:

| test | intent | verdict |
|---|---|---|
| `codegen.test.js` "assignment uses `:-` pattern with env fallback and default value" | the `$1 → $E2E_X → default` chain exists | intent preserved; only the literal updated |
| `codegen.test.js` "assignment uses `:?` pattern with usage message" | required var uses `:?` and carries the usage text | intent preserved |
| `compiler.test.js` "accepts explicit uppercase BASE_URL without injecting a duplicate assignment" | the load-bearing assertion is `match(/^BASE_URL="\$\{1:/gm).length === 1` — untouched | intent preserved; only the value regex updated |
| `visibility-browser-runtime-real.test.js` "generated real-browser fixture binds its app…" | fixture emits a BASE_URL prologue | intent preserved |
| `codegen.test.js` "non-SC-1032 flows stay byte-frozen except for declared drift" | frozen-output receipt; re-pinning demands a declared line-level accounting | **accounting done before re-pinning** (below) |

Byte-freeze drift, measured by diffing old vs new `generate()` output per corpus entry: `legacy-empty` **byte-identical** (no variables); `legacy-single-site` **exactly 1 changed line** (`BASE_URL=`); `legacy-cross-site` **exactly 2** (`OFFICE_BASE_URL=`, `APP_BASE_URL=`). One line per optional variable, nothing else. Ledger entry 5 added to the comment block above the corpus, then the two hashes re-pinned.

### Disposition of every routed finding

| ID | disposition |
|---|---|
| F1 `}` | FIXED — nested quotes at codegen.js:186 |
| F2 cross-site `mappingPaths` test hole | FIXED — new test; M3 proves it now reddens |
| F3 JUnit `_STEP_NAMES=()` empty stub | FIXED — arrays populated one per result class (`pass`/`skip`/`not_automated`/`fail`), all four formats execute; M5 proves the passing-step format now reddens |
| F4 `# Source:` | **FIXED**, not waived — one `commentSafe` call |
| F5 redundant `assert.ok` at old test:80 | REMOVED — the strict-equal above it subsumed it |
| F6 process substitution (RCE) | FIXED — same nested-quote shape at codegen.js:171 |
| F7 apostrophe | FIXED — same shape, both sites |
| F8(a) `%` in JUnit formats | FIXED — folded into F3's now-executing test |
| F8(b) `%` in HTTP header name | **FIXED**, not waived — `hKey.replace(/%/g,'%%')` + executing test |
| codegen.js:1971 unknown action type | FIXED — reachable via the exported `generate()`, so not waived on reachability |
| codegen.js:1802 runtime key comment | NO ACTION, stated — parser.js:206 pins `^[A-Za-z_][A-Za-z0-9_]*$` |
| cleanup-trap over-escape (cycle-1 follow-up 1) | still out of scope, unchanged |

### Scope: one thing found beyond the routed list — declared, not silently absorbed

While re-deriving the table I found that parser.js does **not** charset-validate flow `variables:` KEYS. Two consequences:

1. **Comment class — FIXED here.** The key reaches `# Usage:` and `# $N …` verbatim; a newline in a key ended those comments and executed the remainder. In-class per this stage's own checklist, same one-call shape as F4.
2. **Identifier class — NOT fixed, reported.** The same key is uppercased into a bash identifier: `variables: {"a\ntouch X\n#b": "v"}` emits a bare `TOUCH X` command line. No escaper can fix this — it needs parser-side name validation, which is a behavior change for existing flows. That is precisely what the escalation ruled out for `flow.name` this round, so the same ruling is applied here. **Recommend a follow-up entity covering flow `name`, `variables` keys, and any other identifier-position field together.** The new test is explicitly narrowed to the comment window, with the narrowing and its reason written into the test.

Nothing else was expanded. No new lint, CI lane, or standing enforcement was added.

### CI delta, named before the handoff

Tests added (+20 cases in this file), each spawning one `bash`. Scoped file runs in ~190 ms; full suite ~106 s against `e2e-pipeline-tests.yml`'s `timeout-minutes: 10` (600 s) — ~82 % margin, not thin. CI is `ubuntu-latest` → bash 5.x, and the behavior here is shell-version-dependent, so the whole escaping suite was run under **bash 5.3.9 as well as 3.2.57** (29/29 both). Lint warning classes vs `main`: only `noTemplateCurlyInString` +2, the unavoidable consequence of new `${…}` string literals; the 2 `noUselessEscapeInString` I first introduced were removed. No `.github/workflows/**`, version, manifest, or marketplace file touched.

### Reproduce (fresh validator, no session access)

    cd e2e-pipeline
    node --test compiler/test/codegen-shell-escaping.test.js     # 29/29, AC-1/2/3
    npm test                                                     # 1091, 0 fail — AC-6
    npm run lint                                                 # exit 0 — AC-6
    # AC-2 on the CI shell family, not just the local 3.2:
    sed "s|'/bin/bash'|'/opt/homebrew/bin/bash'|" compiler/test/codegen-shell-escaping.test.js > /tmp/b53.test.js
    node --test /tmp/b53.test.js
    # AC-4: re-derive independently, then diff against the table above
    grep -n "lines.push\|assignments.push" compiler/codegen.js
    # AC-5: runtime_values path is untouched by this diff
    git show --stat 6c5a0ad

Falsifiers for every fix are the M1-M8 mutations above; each is a single-token edit to `compiler/codegen.js`.

### Summary

The escalation's diagnosis was right and is now written into the code: `escapeDoubleQuoted` is the wrong tool for a `${…}` word, because that word re-enables quote processing and process substitution rather than behaving as double-quoted text. Nesting the payload in its own double quotes fixes the grammar instead of enumerating characters, and one shape closed F1, F6 (live command execution) and F7 at both sites, portably across bash 3.2.57 and 5.3.9. F2 and F3 were test holes rather than code holes — both branches now actually execute, and both redden when their escaper is removed, which is what the previous round could not show. F4 and F8(b) were fixed rather than waived, and `%`-in-`printf`-format was closed at both emitters. One finding beyond the routed list is declared above: flow `variables:` keys are unvalidated, whose comment half is fixed here and whose identifier half is deliberately left to a follow-up decision rather than silently widening this round's appetite.

## Stage Report: validation (cycle 2)

- DONE: Re-verify that all eight routed findings (F1, F2, F3, F4, F5, F6, F7, F8a, F8b) are genuinely closed at commit 6c5a0ad by executing the emitted bash yourself on BOTH bash 3.2.x and 5.x — especially F6's process-substitution canary and F7's apostrophe parse-break, which must now be inert — and independently re-run at least four claim-breaking mutations of your own choosing, including one against a line the implementer's M1-M8 list does NOT cover.
  All 8 closed, proven by execution on 3.2.57 + 5.3.9, never by reading — table below. Ran **22** of my own mutations (21 outside M1-M8); **22/22 reddened**; scratch restored to sha256 `461f2903…` after each and the worktree `git status --porcelain` stayed empty.
- DONE: Audit the riskiest new thing in this round: three pre-existing test files were edited (codegen.test.js, compiler.test.js, visibility-browser-runtime-real.test.js) to re-pin frozen-output hashes. Verify per changed scenario that the drift is exactly what the implementer claims (legacy-empty byte-identical, legacy-single-site 1 changed line, legacy-cross-site 2, one line per optional variable and nothing else) — a re-pinned golden hash is the classic place a real regression hides.
  **Drift is exactly as claimed, no hidden regression.** Regenerated each corpus entry against both codegens: the OLD output reproduces origin/main's retired pins byte-for-byte (`a63e7001…`, `4e2bf1cb…`) and the NEW output matches the new pins, so neither pin was invented. `diff` old vs new: legacy-empty **0** changed lines, legacy-single-site **1**, legacy-cross-site **2** — every one a `*_BASE_URL=` optional-variable line, nothing else. The other two files change one regex each; `compiler.test.js`'s load-bearing `match(/^BASE_URL="\$\{1:/gm).length === 1` is untouched.
- DONE: Adjudicate the implementer's two escalations rather than accepting them … then re-run the cross-model review on the full diff and record every P1 as fixed or explicitly waived, and give a final ACCEPTED or REJECTED.
  Both adjudicated (one correct, one **factually wrong**); cross-model gate ran clean; verdict **REJECTED** on one confirmed defect, V1.

### The eight routed findings — closed, by execution on both shells

Real compile path (`compile()` → written `.sh` → run), mapping `base_url` / flow `name` poisoned:

| | origin/main | HEAD 6c5a0ad |
|---|---|---|
| F1 `}` | value `http://h/; touch CAN; #}` — wrong, exit 0 | byte-exact, both shells |
| F6 `<(…)` `>(…)` | **canary CREATED 100/200 runs on 3.2.57 AND 5.3.9** | zero canaries, message shows the literal text |
| F7 `'` | `UNPARSEABLE` on both shells | parses, value `http://h/it's` byte-exact |
| F8a `%` | `skipped="2026-08-10T…"` — args shifted; `%100000000s` blew stdout to **381 MB** | literal, incl. `%%`/`100%`/`%%%` idempotent |
| F8b `%` header | `header = "X-tok3n: Bearer "` | literal (`parser.js:339` does permit `%` — claim verified) |
| F2 / F3 / F4 / F5 | mutation stayed green (round-1 holes) | my own mutations at `:262`, `:1477`/`:1487`/`:1490`/`:1493`/`:1496`, `:260` each redden |

Scale checks beyond the routed list: 44/44 `:-`-path payloads and 40/40 `:?`-path payloads round-trip byte-exact with zero canaries across both shells; a 126-combination `$1`×`$E2E_*`×default matrix shows **0 behavioural differences** between the old and new emitted prologue, so the nesting is literalising only. Running the NEW test file against origin/main's codegen fails **25 of 29** — the suite is genuinely behavioural, not tautological (the 4 green-in-both are pins; 3 of 4 were declared).

### Per-AC verdict

- **AC-1 PASS** — emitted line is `BASE_URL="${1:-${E2E_BASE_URL:-"http://localhost:3000/\$(id -u)\`id\`"}}"`: `\$` and `` \` `` present, no raw `$(`. Falsifier: dropping `escapeDoubleQuoted` inside the nested quotes (not an M1-M8 mutation) → 5 red.
- **AC-2 PASS** — canary absent and value byte-equal in every probe above, on 3.2.57 and 5.3.9.
- **AC-3 PASS** — the echo/`_record_step_name` test executes; both sinks falsifiable (`doubleQuote` at `:1687` → 1 red; `quotedId`, 2 occurrences → 1 red).
- **AC-4 FAIL** — no context is *absent* and ~35 of ~40 citations land exactly (the 5 misses point at the explanatory comment or a neighbouring line — `:171`→`:174`, `:1474`→`:1477`, `:1484`→`:1496`, `:1297`→`:1300`, `:1555`→`:1529`; none fabricated, well under the ⅓ discard bar). It fails on the other half of the criterion: a context that was MISSING-ESCAPE has a fix that does not close it. The printf-FORMAT row asserts `:1457` is now closed; execution disproves it — **V1**.
- **AC-5 N/A — expiry independently verified.** `runtimeTemplateDoubleQuote` is absent at HEAD *and* at origin/main; `git log -S` shows it removed by `bd2b142` (#184), which is this branch's merge-base. This diff touches no `runtime_values` surface.
- **AC-6 PASS** — `npm test` 1091 / 0 fail / 2 skipped (origin/main baseline 1062 / 0 / **same 2 skips**, so +29 and no new skip); `npm run lint` exit 0.

### V1 — CONFIRMED, the reject ground. `compiler/codegen.js:1457`

    var escapedFlow = xmlAttrEscape(flowName).replace(/%/g, '%%');

A printf FORMAT operand has **two** metacharacter classes. The round closed `%` and left `\`: `xmlAttrEscape` (`:36-53`) never touches backslash, and `flow.name` has no charset validation (`parser.js:128` checks truthiness only). Consumed at `:1477`/`:1487`/`:1490`/`:1493`/`:1496`. Verified end-to-end through `compile()`, exit 0, no diagnostic, identical on 3.2.57 and 5.3.9:

- `name: "rel\0101ease"` → the JUnit attribute carries hex `72 65 6c **08** 31 …` — a **0x08 backspace, an illegal XML 1.0 character**, the exact class `xmlAttrEscape:41-43` exists to prevent and which the printf pass silently undoes.
- Worse, and independently found by the security lens: `name` carrying `\x22\x3e\x3ctestcase classname=\x22FAKE\x22 name=\x22ALWAYS-GREEN\x22 …` injects a fabricated `<testcase>` into the CI-consumed report while a real `<failure>` is structurally mangled. That is **CI-signal forgery**, not merely identity corruption — I rate it P1 on report integrity (it is not RCE; `singleQuote` holds and no probe produced a canary).

Not writable off as pre-existing under this stage's per-line rule: `git blame` puts `:1457` on **6c5a0ad** and `:1477` on **63b9362** — both inside this change's range. The behaviour existed at origin/main, but these lines are this change's, and this change declares the context closed.

**Fix (one line, proven by me, not proposed blind):** `var escapedFlow = xmlAttrEscape(flowName).replace(/\\/g, '\\\\').replace(/%/g, '%%');` → 14/14 hostile names render byte-exact on both shells and the escaping suite stays 29/29 green. Extend `codegen-shell-escaping.test.js:306` with a `\` axis beside its `%` axis. The sibling site `:1300` needs nothing — `parser.js:339`'s tchar set excludes `\`. The metrics emitter (`:1529`) and footer (`:1629`) are safe: argument slot and `escapeDoubleQuoted` respectively, both re-verified by execution; no `%b` exists anywhere in the file.

### Adjudications the FO asked for

- **Their correction to the FO is RIGHT — say so plainly.** Measured, not assumed: a `${N:?word}` word **does** perform process substitution (stderr shows `/dev/fd/63`; canary created 100/200 runs) and a `${N:-word}` word **does not** (payload preserved literally) — identical on 3.2.57 and 5.3.9. The FO was corrected correctly.
- **Their escalated `variables:`-key finding is WRONG on its premise — do NOT open an entity on that basis.** `parser.js:48` *does* charset-validate flow `variables:` keys (`VARIABLE_NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/`, inside `validateFlowVariables` at `:18`, called from `:168`); JS `$` is end-of-input, so it rejects `"abc\n"`. An end-to-end `compile()` on such a key errors out and creates no canary, and `compiler.js` is `generate()`'s only non-test caller, aborting at `:211` before `:395`. The identifier-position injection they describe is real *only* with the parser bypassed via the exported API. Two delegated lenses reached this independently. The `commentSafe` wrap is harmless defence-in-depth, but the justifying comment at **`codegen.js:144-146` states a falsehood** and should be corrected to name `flowName` (which genuinely is unconstrained) as the reason.
- **`commentSafe` UPHELD** (agreeing with cycle 1): `jsonStringContent` is the only existing helper producing a newline-free form, but it also escapes `\` and `"` and would mangle `# Source: C:\path\my "prod" flow.yaml`. commentSafe is identity on 6/6 realistic paths. One nit: the `\r` branch is unnecessary — a bare CR does **not** end a bash comment on either shell (measured), and it does mangle the one machine-parsed consumer, `hooks/scripts/pre-commit-stale-check.sh:46`, for CR-bearing paths.
- **The scoped-out follow-ups stay out.** The cleanup-trap over-escape (`:1398`/`:1410`) is unchanged by this diff and its `summary.flowName` is `doubleQuote`/`singleQuote`-wrapped, so it is a cosmetic pre-existing bug, not an injection hole.

### Residual (record, do not open a third round for it)

**Flow `name` is the one unconstrained string reaching the most sinks** (`parser.js:128`). Every `codegen.js` sink for it is inert at HEAD once V1 lands. Its remaining sink is outside shell emission: `compiler.js:398` `path.join(outputDir, flowName + '.sh')` — I confirmed `name: "../../TRAVERSED"` compiles clean and writes a 19,633-byte `.sh` two levels above `--output-dir`. Acceptance reason: closing it needs parser-side `name` validation, a behaviour change for existing flows that the escalation explicitly ruled out of this round. **Recommend one follow-up entity for `flow.name` charset validation** covering the traversal sink and V1's root cause — *not* one for `variables:` keys, which are already validated. Also for that entity, both lenses flagged `resolver.js:781` (`runtimeValues[runtimeKey]` resolves `constructor`/`__proto__` off the prototype chain and fails open to an interactive secret prompt) — pre-existing, not injectable, out of scope here.

### Evidence block

- **Lenses:** shell-injection/escaping fix on an executable surface (`compiler/codegen.js`) plus four test files. Fired **correctness** (FAIL — V1), **security** (FAIL — V1's forgery variant; 1 P2 traversal + 3 P3, all pre-existing), **silent-failure** (FAIL — V1 is exit-0 with no diagnostic; 3 P3). Not fired, justified by surfaces touched: no new/changed type, no locks or shared mutable state, no process/handle lifecycle, no manifest or installed-contract file. `pr-review-toolkit:*` are **not in this session's agent registry** (attempted; absent), so the security and silent-failure lenses ran as delegated general-purpose reviewers under lens-specific prompts, plus my own direct execution. Both delegated rounds accepted: ~25 and ~20 citations spot-checked, **0 wrong**.
- **Diff coverage:** 29 executable added lines in `codegen.js` (76 added total, 46 comment, 1 blank). **29/29 = 100%** proven falsifiable by at least one mutation that reddens the suite — above the 85% bar. Read: worktree `/Users/kent/mini-legs/rx-0bdfaef9-64c7-4b5a-992b-b813c61ddbe8/worktree` at `6c5a0ad` (`git rev-parse HEAD` = `6c5a0adb61ebcb4b5d47e63eee28740643b22125`), diff base `origin/main` = `bd2b142`. Would have failed it: any changed line whose claim-breaking edit left the suite green — that is exactly how cycle 1 separated `:262` and `:1496`, and none stayed green this cycle.
- **Adversarial:** 22 claim-breaking edits, 21 of them outside the implementer's M1-M8 (including the two `escapeDoubleQuoted`-inside-the-nesting edits, the footer `safeFlowName`, the `commentSafe` body, all four `# $N` comment lines, the singular `mappingPath` branch, and both step-id sinks). **22/22 reddened.** Read: a `git archive HEAD` scratch copy at `/tmp/val190/mut`, never the worktree; restored to sha256 `461f2903c1155692c91b641cdfa178058f6dc0c531f0a68381bc944ccfcb36dd` after every batch, and the real worktree's `codegen.js` carries that same hash untouched. Would have failed it: a mutation staying green, or a restore whose sha drifted — neither occurred.
- **Cross-model:** `codex exec review --base origin/main` (OpenAI GPT-5.x — cross-vendor to this Claude session), exit 0, verdict *"I did not find a regression or actionable bug introduced by this patch"* — **0 P1, 0 findings**, so nothing to fix-or-waive from this gate. Recorded honestly: it **missed V1**, which two same-vendor lenses and my own execution found, so its clean bill is not load-bearing. A first attempt (`codex exec --sandbox read-only -` on the piped diff) terminated mid-exploration without a final answer after a `codex_models_manager` decode error — that observed failure is why the `review` subcommand was used. Would have failed it: >⅓ fabricated citations, which would have discarded the round.
- **E2E:** PASS — per the entity's E2E-first note the real runtime for a compiler is the generated artifact executing. Every claim above was taken through `compile()` on real fixtures and run as a written `.sh` under `/bin/bash` 3.2.57 and `/opt/homebrew/bin/bash` 5.3.9 (CI is `ubuntu-latest` → the 5.x family). No browser surface in this diff.
- **Origin re-observation:** PASS — Reported scenario: a mapping `base_url` containing `$(...)` compiles to a script that executes it | Originating runtime kind: external shell runtime executing the compiled artifact | Re-observation artifact/revision: `e2e-pipeline/compiler/test/fixtures/no-vars-flow.yaml` + `test-app.yaml` with `base_url` poisoned, compiled by `compile()` at `bd2b142` and at `6c5a0ad`, run as the written `out/test-no-vars.sh` | Equivalent-runtime rationale: same actor (bash), same instrument (a compiler-written `.sh` invoked as `bash <file>`, not a hand-built snippet), same delivery path (`compile()` → `outputDir`), same claim-relevant condition (`$1` and `$E2E_BASE_URL` unset so the `:-` word expands) | Falsifier kind: mutation | Result: at `bd2b142` payload A created the canary on both shells, B was UNPARSEABLE, C yielded a wrong value; at `6c5a0ad` all three parse, create no canary, and yield the byte-exact literal.

### Recommendation

**REJECTED** — one item, one line. **V1: `compiler/codegen.js:1457` — add `.replace(/\\/g, '\\\\')` before the `%` doubling, and add a `\` axis to the test at `codegen-shell-escaping.test.js:306`.** This is not a new class: it is the *other* metacharacter of the printf-FORMAT class the FO routed as F8, the row the audit table declares closed, on lines this change authored. The fix is proven green above. Two secondary asks, both one line and neither a reject ground on its own: correct the false premise in the comment at `codegen.js:144-146`, and drop or re-justify `commentSafe`'s `\r` branch. Everything else in this round is sound — the nested-quote shape is the right mechanism, all eight routed findings are genuinely closed, the golden-hash re-pin hides nothing, and diff coverage is 100%. **This is the second consecutive rejection at this gate, so it ends the loop and goes to the captain.** For that option set I record my own read: the approach is not in question and re-cutting at ideation would be disproportionate; the honest choices are one narrow correction round scoped to V1, or ACCEPT-with-recorded-residual if the captain judges CI-report forgery via a hand-written flow name acceptable to ship and fix next.

### Summary

Re-verified all eight routed findings closed at `6c5a0ad` by executing emitted bash on bash 3.2.57 and 5.3.9 rather than reading it — F6 really did execute commands on origin/main (canary in 100/200 runs) and really is inert now, and F7's apostrophe no longer makes the script unparseable. The re-pinned golden hashes, this round's biggest hiding place, are clean: the retired pins reproduce origin/main's output exactly and the drift is precisely the claimed 0/1/2 `*_BASE_URL=` lines. Of the two escalations, the process-substitution correction to the FO is right and the `variables:`-key finding is wrong — `parser.js:48` already validates those keys, so no entity should be opened for them. One confirmed defect survives: the printf-FORMAT class was closed for `%` but not `\`, letting an unvalidated `flow.name` inject fabricated `<testcase>` elements into the JUnit report with exit 0, on lines this change authored. That is a one-line fix I verified, so the recommendation is REJECTED on V1 alone, with flow-`name` charset validation recorded as the residual for a follow-up entity.

- Cycle 2: REJECTED — fresh validation (round 2); surface 64m cumulative implementation
  wall-clock vs estimate 90m (71%); AC unchanged. All eight round-1 findings (F1–F8b) verified
  genuinely closed by execution on bash 3.2.57 and 5.3.9; the golden-hash re-pin was audited
  and hides nothing; diff coverage 100% (22/22 of the validator's own mutations reddened).
  One new defect survives — **V1**, `compiler/codegen.js:1457`: the printf-FORMAT class was
  closed for `%` but not `\`, so an unvalidated `flow.name` can inject a fabricated
  `<testcase>` into the CI-consumed JUnit report at exit 0 (CI-signal forgery, not RCE).
  `git blame` puts `:1457` on 6c5a0ad and `:1477` on 63b9362 — both inside this change's
  range, so the per-line pre-existing write-off is unavailable. Validator-verified one-line
  fix on hand. Residual recorded, not routed: `flow.name` has no charset validation
  (`parser.js:128`) and also reaches `compiler.js:398` `path.join`, where `name:
  "../../TRAVERSED"` writes outside `--output-dir` — needs its own entity.

**ESCALATION — second consecutive rejection at this gate. Loop stopped; routed to the captain.**
Per the workflow README ("two consecutive rejections → escalate to the captain instead of a
third round") and the feedback-rejection contract ("on cycle 3, escalate to the human"), the FO
did NOT open a third round. Budget was not the brake — 71% of appetite, inside the 2× tolerance;
the round counter was. The FO holds the conn for gate approval, which does not extend to a
circuit breaker the contract routes to a human. No verdict set, status left at `validation`.
Briefing written to `docs/dev/issue190.gate.json`; draft PR opened carrying `DECISION NEEDED`.
