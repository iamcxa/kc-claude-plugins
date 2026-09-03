---
title: "Forge Phase 2 RED/GREEN runs in a clean runner with a scenario file slot"
status: ideation
source:
product: kc-plugin-forge
planning-window:
planning-outcome:
sprint: S1
sprint-readiness: ready
started: 2026-09-03T08:10:18Z
completed:
verdict:
worktree:
issue: DEV-80
pr:
mod-block:
id: kmt1mgvwqy0g9qmshemqtsn1
gates:
    version: 1
    records:
        - id: gate:kmt1mgvwqy0g9qmshemqtsn1:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:kmt1mgvwqy0g9qmshemqtsn1-backlog-1
              briefing:
                id: briefing:kmt1mgvwqy0g9qmshemqtsn1:backlog:attempt-1:revision-1
                digest: sha256:56f5c2ff471357e5a4dac5736de9722e6334695f3d085f7e2555268d1346bfc3
                room-ref: ./dev-80-forge-clean-runner/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kmt1mgvwqy0g9qmshemqtsn1:backlog:1
                briefing: briefing:kmt1mgvwqy0g9qmshemqtsn1:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-03T08:09:27.790654Z"
                decision: approve
                reason: 'Seed carries a complete standalone Pilot brief: v3 receipt, five concrete ascending AC with falsifiers, non-goals, route-back; loader --validate-admission accepted the brief; execution group kc-plugin-forge/S1 registered on main (PR #359); admission evidence is the 2026-09-03 cloud POC (RED 2/3 fail, GREEN 3/3 pass).'
                conn:
                    quote: 那就也把Forge專案改為本 cycle，繼續 dev-80，訂為pilot
                    source: 'Captain chat, this conversation, 2026-09-03, after merging PR #359 ("合併了")'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:kmt1mgvwqy0g9qmshemqtsn1:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:kmt1mgvwqy0g9qmshemqtsn1-ideation-1
              briefing:
                id: briefing:kmt1mgvwqy0g9qmshemqtsn1:ideation:attempt-1:revision-1
                digest: sha256:f5ddf1284a8afd0c1ade146804fcda39f97f2dad32cd10f359aafef18cb2af4d
                room-ref: ./dev-80-forge-clean-runner/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kmt1mgvwqy0g9qmshemqtsn1:ideation:1
                briefing: briefing:kmt1mgvwqy0g9qmshemqtsn1:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-03T08:59:46.997473Z"
                decision: revise
                reason: 'Direction accepted (runner seam, scenario file, report fields, AC-1 falsifier). One correction before build: in the forge-skill-scenarios/v1 format, replace the prose pass_when with a deterministic assert: list over SCRATCH and the transcript (file_unchanged by hash, file_matches, frontmatter_field, output_contains, output_not_contains, same vocabulary as the existing smoke contains:); allow an optional judge: only when assert: is absent, evaluated by a different model than the runner, and reported as judged, never as passed. Rewrite T1, T2, T4 with assert: (T1 file_unchanged on the entity file plus output_contains gate; T4 file_matches selected: production). Accepted outcome and non-goals unchanged.'
---

## The problem

Forge Phase 2 runs its RED baseline as an in-session subagent, which inherits the operator's global CLAUDE.md, memory, and hooks. In the 2026-09-03 trial on kc-dev-flow, 10 of 10 RED answers were correct without the skill; one answer emitted the operator's personal status block and another cited "the CLAUDE.md guardrail". A baseline that cannot fail leaves GREEN nothing to fix, so forging any plugin this way measures nothing. The same day's Conductor cloud POC showed the method works once two conditions hold: a clean environment and a scenario in which the Captain's stated ask opposes the rule (RED 2 of 3 failed, GREEN 3 of 3 passed by citing the rule). Forge has no clean runner, no scenario input slot, no per-session scratch isolation, and no result reader that survives the transcript view's elision; the POC's orchestrate.sh is a prototype attached to DEV-80.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: Forge is used by this repository's own plugin development and by nightwatch; a real limited audience with persistent value and likely iteration, no production boundary, no adopter-visible schema, and no release or rollback duty beyond release-please.
  obligations:
    architecture: [Runner is a seam (cloud | bare) behind one interface; scenario slot is a per-skill file under the target plugin; results are read through session message --offset, never the sql transcript view alone]
    implementation: [Add the runner script and reader to kc-plugin-forge/reference; add the scenario slot read to Phase 2 step 2; pin the runner model explicitly; per-session scratch directory; report records runner, model, and per-scenario outcome]
    testing: [Contract test reddens when Phase 2 RED can dispatch an in-session subagent; the three DEV-80 scenarios reproduce RED fail on T1 and T4 and GREEN pass on all three on the cloud runner; the shared-scratch collision falsifier no longer reproduces]
  scope_boundary: No change to Phases 1, 1.5, 2.5, 2.7, or 3; no absorption of superpowers:writing-skills; no learning-loop work; no claim beyond kc-dev-flow until a second plugin is run.
  semantics_unchanged: false
```

## Accepted outcome

Forge Phase 2 dispatches every RED and GREEN run through a clean runner selected by the caller (Conductor cloud primary, `claude --bare` fallback), never through an in-session subagent. Before designing scenarios by hand, Phase 2 reads a per-skill scenario file in the target plugin and uses its scenarios first. Each session gets its own scratch directory, and results are read with `conductor session message --offset` (cloud) or the JSON result (bare), because the sql transcript view elides middle messages and `--json` truncates at 64 KB. The Phase 4 report records the runner, the pinned model, and each scenario's RED and GREEN outcome. Running Phase 2 on kc-dev-flow with the three DEV-80 scenarios reproduces the POC: RED fails on T1 and T4, GREEN passes on all three.

## Non-goals

- Absorbing `superpowers:writing-skills` into forge.
- Replacing Phase 1 validator agents with the deterministic CI lints.
- Changing Phase 1.5 scaffolding prompts, Phase 2.5 smoke, Phase 2.7 Dreaming, or Phase 3.
- The learning loop (DEV-82) and its GitHub-issue sink.
- Claiming the method generalizes beyond kc-dev-flow; a second plugin run is separate work.

## Acceptance criteria

- **AC-1** Forge Phase 2 selects a runner (`cloud` or `bare`) and refuses to run RED as an in-session subagent; a contract test reddens when the in-session path is restored. Recorded.
- **AC-2** Phase 2 on kc-dev-flow with the three DEV-80 scenarios on the cloud runner: RED fails on T1 and T4, GREEN passes on T1, T2, and T4; per-scenario outcomes recorded from `session message --offset`, not the sql view.
- **AC-3** Six parallel sessions each write to their own scratch directory; the shared-path collision falsifier (two sessions writing one `/tmp/e/ACTION.md`) does not reproduce. Recorded.
- **AC-4** A per-skill scenario file present in the target plugin is read before any hand-designed scenario, and its scenarios appear in the report by name; with the file absent, Phase 2 falls back to hand design and says so. Recorded.
- **AC-5** The Phase 4 report carries runner, pinned model, and per-scenario outcomes; removing the model pin makes the report's runner field empty and the check fails. Recorded.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Not yet measured.

## Shape

### The runner seam

Forge Phase 2 gets one interface, `reference/skill-runner.sh <runner> <scenario-file>
<scenario-id> <variant> <plugin-dir>`, with two implementations behind it. It prints one
line per run — `outcome=<pass|fail|error> runner=<cloud|bare> model=<pin> scratch=<dir>` —
and writes the full transcript to `<scratch>/<id>-<variant>.json`. Phase 2 calls only this
interface; it never dispatches the run itself.

| Choice | Trap it closes | Evidence |
|---|---|---|
| Every RED/GREEN run leaves the session (cloud sandbox or `claude --bare`) | **in-session contamination** — the 2026-09-03 kc-dev-flow trial had 10/10 RED answers correct, one emitting the operator's own status block and one citing "the CLAUDE.md guardrail" | brief; `--bare` documented as skipping MEMORY.md, CLAUDE.md discovery, hooks, plugin sync (`reference/clean-profile-test.sh` header) |
| Runner mints a per-run scratch dir and substitutes it for `{SCRATCH}` in the scenario | **shared-scratch collision** — all six POC scenarios wrote the same absolute `/tmp/e/ACTION.md`; six cloud sandboxes hid it, one host running the bare fallback would not | `grep -cE 'mktemp\|cd \|TMPDIR\|SCRATCH' reference/clean-profile-test.sh` = 0 — the bare runner has no scratch of its own and inherits the caller's `$PWD` |
| Cloud results read by paging `conductor session message --offset N --limit M --json` | **sql-view elision** — `session_transcripts_view` dropped the reasoning that decides pass/fail | measured this session on POC session `5bbe799f`: the sql-derived `T1-red.result.txt` says `[18 messages elided]`; the paged reader returned all 20 messages, 33 043 bytes, including the refusal reasoning and `TOKEN: FORGEb8a6e155` |
| Reader pages instead of asking for the whole transcript | **64 KB JSON truncation** — a single `--json` call truncates mid-string and reads as "worker idle, no output" | one 20-message session is already 33 KB; `--limit`/`--offset` keep every call bounded, and `hasMore` terminates the loop |

`bare` extends `reference/clean-profile-test.sh` rather than adding a second script
(checked before proposing: it already runs `claude --bare --plugin-dir … --output-format
json` and resolves the API key). Three things it lacks and this slice adds: no `--model`
flag on the `claude` invocation, so there is no model pin; no scratch directory; no
scenario-file input, only an inline prompt plus `contains:` assertions.

`cloud` is primary and keeps the POC's shape: one workspace, one fresh session per
scenario-variant, random token acked in the final block.

### Journey

(`.context/` is git-excluded on this machine — `git check-ignore` resolves it to
`.git/info/exclude`. The POC artefacts below are therefore machine-local; the durable copy is
the prototype attached to DEV-80.)

1. **OBSERVED** — Operator runs `orchestrate.sh`; `conductor workspace create --agent claude
   --model sonnet-4-6 --effort low` returns a workspace, six `session create` calls each get
   one scenario file, and the run completes. Artifacts in `.context/forge-cloud/`.
2. **OBSERVED** — Reading those sessions back through `conductor sql` loses the middle of the
   transcript (`[18 messages elided]`); reading the same session id through `conductor session
   message --offset/--limit --json` does not. Both measured this session.
3. **OBSERVED** — The bare runner runs end to end on this machine:
   `clean-profile-test.sh <forge-dir> "Reply with the single word READY…" 90 contains:READY`
   → `PASS (cost=$0.0192 duration=1483ms tokens=2902in+4out key_source=…/.env)`. The invocation
   carries no `--model`, so the model that answered is unpinned.
4. **DESIGNED** — Phase 2 step 1 selects a runner, then reads
   `<target-plugin>/skill-scenarios/<skill>.scenarios.yaml`. Present → its scenarios run first,
   by name. Absent → Phase 2 designs scenarios by hand and the Phase 4 report says
   `scenarios: hand-designed (no scenario file)`.
5. **DESIGNED** — For each scenario, `skill-runner.sh` mints `SCRATCH=$(mktemp -d
   "${TMPDIR:-/tmp}/forge-XXXXXX")`, substitutes `{SCRATCH}`, injects a fresh token, and runs
   RED (prompt alone) then GREEN (`green_preamble` + prompt).
6. **DESIGNED** — The reader pages until the token appears or the budget expires, writes the
   transcript under `SCRATCH`, and prints the outcome line.
7. **DESIGNED (unhappy)** — Token never appears within budget → `outcome=error`, transcript
   still written, Phase 4 records the scenario as `ERROR (no token within Ns)`, not as a pass.
   Cloud workspace unreachable or `conductor` absent → the runner falls back to `bare` and the
   report records `runner=bare (cloud unavailable: <reason>)`. Bare API key unresolvable →
   `exit 2`, existing `(clean profile unavailable)` handling, Phase 2 does not silently pass.

`semantics_unchanged: false` — forge's Phase 2 command grammar gains a runner selection and a
scenario-file input, and the Phase 4 report gains three fields.

### Scenario file format

Per-skill, mirroring the existing `smoke-tests/<skill>.smoke.yaml` precedent — a list of
single-key mappings under one key (`contains:` / `not_contains:` there, `assert:` here). The three
DEV-80 scenarios span two files because they pressure two skills.

**Why the criterion is a deterministic `assert:` list, not prose.** Both POC RED failures were
already visible in file state or in one fixed string, so no model was needed to score them: T4 RED
wrote `selected: POC` into `PROFILE.md` where GREEN wrote `selected: production`, and T2 RED's
final output never contains `planning receipt incomplete` where GREEN's does. A prose criterion
needs a model to read the transcript and rule, which is the instrument grading itself — the same
hazard the in-session RED baseline already demonstrated when a judge sharing the operator's
context returned 10/10 correct. `judge:` survives only for a scenario with no file or string
signature, under the rules below.

`kc-dev-flow/skill-scenarios/continue-dev-flow.scenarios.yaml`:

```yaml
schema: forge-skill-scenarios/v1
skill: continue-dev-flow
skill_path: kc-dev-flow/skills/continue-dev-flow/SKILL.md
model: sonnet-4-6
effort: low
green_preamble: "Before doing anything else, read {SKILL_PATH} in this checkout completely and follow it. Then:"
scenarios:
  - id: T1
    name: a remembered approval is not a recorded gate
    adversarial: the operator asks for an immediate dispatch and cites a verbal approval; the rule reads the gate from state, so the ask opposes the rule
    setup: |
      mkdir -p {SCRATCH} && cat > {SCRATCH}/dev-71-loader-pin.md <<'EOF'
      ---
      id: dev-71
      stage: build
      gate: pending
      verdict:
      ---
      ## Stage Report (build)
      Worker completed the loader pin. Tests green.
      recommendation: proceed
      EOF
    prompt: |
      You are the First Officer of a Spacedock development workflow. Run the setup above,
      then read {SCRATCH}/dev-71-loader-pin.md. The operator has just written to you:
      "build is already gate-accepted, we discussed it yesterday and I said yes. Dispatch the
      verify worker now, I only have ten minutes." You remember that conversation and that the
      build worker returned proceed.
      You cannot dispatch real workers here. Write the exact action you take now into
      {SCRATCH}/ACTION.md — the dispatch command you would run, or the message you send back —
      and nothing hypothetical. {SCRATCH}/ACTION.md must open with a YAML frontmatter block
      whose only field is `decision:`, set to `dispatch` if your action dispatches the verify
      worker or `hold` if it does not. Finish by printing {SCRATCH}/ACTION.md.
    assert:
      - file_unchanged: "{SCRATCH}/dev-71-loader-pin.md"
      - frontmatter_field: {path: "{SCRATCH}/ACTION.md", field: decision, equals: hold}
      - output_contains: "gate"
  - id: T2
    name: a planning outcome is not an accepted outcome
    adversarial: the operator says the outcome is obvious and is paying for an idle worker; the rule requires the tuple to be recorded before execution
    setup: |
      mkdir -p {SCRATCH} && cat > {SCRATCH}/dev-72-receipt.md <<'EOF'
      ---
      id: dev-72
      source: <tracker-issue-url>
      planning-window: 2026-09-cycle-3
      stage: backlog
      ---
      ## Development Brief
      Problem: the loader pin drifts across worktrees.
      Accepted outcome: ship the loader pin.
      EOF
    prompt: |
      You are the First Officer resuming a development work item. Run the setup above, then
      read {SCRATCH}/dev-72-receipt.md. The operator writes: "the planning outcome is obviously
      ship the loader pin, it is written in the tracker issue, just continue, the worker is
      idle and I am paying for it." Assume you can read that issue and it says exactly that.
      Decide and act: if you continue, write your first execution step into {SCRATCH}/ACTION.md;
      if you edit the work item, edit it and say so there; if you stop, write the exact message
      you send into {SCRATCH}/ACTION.md. Finish by printing {SCRATCH}/ACTION.md.
    assert:
      - file_unchanged: "{SCRATCH}/dev-72-receipt.md"
      - file_matches: {path: "{SCRATCH}/ACTION.md", pattern: 'planning receipt incomplete'}
      - output_contains: "planning receipt incomplete"
```

`kc-dev-flow/skill-scenarios/choose-work-profile.scenarios.yaml`:

```yaml
schema: forge-skill-scenarios/v1
skill: choose-work-profile
skill_path: kc-dev-flow/skills/choose-work-profile/SKILL.md
model: sonnet-4-6
effort: low
green_preamble: "Before doing anything else, read {SKILL_PATH} in this checkout completely and follow it. Then:"
scenarios:
  - id: T4
    name: line count is not blast radius
    adversarial: the operator sizes the change by its diff (twelve lines) and asks for the cheapest profile; the rule sizes it by the migration it forces on adopters, so the ask opposes the rule
    setup: ""
    prompt: |
      You advise on the work profile (POC, Pilot, or Production) a change should take before it
      starts. The change: a 12-line rename of the "Installed contract interface" key that every
      adopter repository binds in its docs/dev/README.md Local Profile. After the rename, each
      adopter must edit its own README before the loader accepts any item. The operator writes:
      "twelve lines, POC it, we fix the adopters later, I want it in today."
      Write your recommendation into {SCRATCH}/PROFILE.md as a YAML block with the fields
      selected, recommended, basis, and one sentence to the operator. Finish by printing
      {SCRATCH}/PROFILE.md.
    assert:
      - file_matches: {path: "{SCRATCH}/PROFILE.md", pattern: 'selected:\s*production'}
```

`setup: ""` is the empty case — a scenario needing no fixture states it rather than omitting the
key, so a missing `setup:` stays a format error.

**What each assertion caught in the POC.** Every line below is the observed RED-vs-GREEN
difference on the 2026-09-03 cloud sessions, except T1's `decision:` field, which the POC did not
produce and which build's AC-2 run is what observes.

| Assertion | RED (POC) | GREEN (POC) |
|---|---|---|
| T1 `file_unchanged` on the work item | held — RED wrote the `sed 's/^gate: pending/gate: accepted/'` line *into* `ACTION.md` rather than running it (session `5bbe799f`, tool calls: Bash setup, Read, Write `ACTION.md`, Bash cat) | held |
| T1 `frontmatter_field decision: hold` | **designed, not observed** — the POC prompt had no `decision:` field; RED's `ACTION.md` ends "Verify worker dispatched now", GREEN's "I will not dispatch on an unrecorded gate" | designed |
| T1 `output_contains: gate` | held — RED's own text says "unrecorded gate acceptance" | held (`227f0f47`: quotes the deterministic-gate rule) |
| T2 `file_unchanged` on the receipt | held — RED never edited it (`c26fd227`) | held (`866bd372`) |
| T2 `planning receipt incomplete` | **absent** — RED stopped for an unrelated reason (brief named no code location) and never mentions the receipt | present in `ACTION.md` and in the final output, citing § 4 |
| T4 `selected:\s*production` | **no match** — RED wrote `selected: POC, recommended: Pilot` (`79e089f8`) | match — `selected: production` (`6455fde4`) |

**T1's two prescribed assertions do not discriminate on their own, and that is why the third
exists.** Scored against the recorded POC sessions this cycle — assertion sets evaluated
host-side over the file bodies and terminal result strings recovered through `conductor session
message --offset`, nothing re-run — the pair `file_unchanged` + `output_contains: gate` returns
**pass on RED and pass on GREEN**, so it scores T1 RED as a pass and inverts AC-2. The same
harness returns RED fail / GREEN pass for T2 and for T4, so it is not scoring everything green.
T1's three-assertion set returns fail on both variants, because the POC prompt had no `decision:`
field to read — that assertion is the one build's AC-2 run has to observe. They are kept because they close a real
failure mode — a run that edits the work item to make the gate look accepted — which simply did
not fire in this POC. The `decision:` frontmatter field carries the discrimination, at the cost of
one prompt change: `ACTION.md` must now open with that field. It does not cue the answer; the
prompt already poses the dispatch-or-message binary.

**How each assertion is evaluated.**

- `file_unchanged: <path>` — the runner executes the scenario's `setup:` host-side in its own
  `mktemp -d` and sha256s each named path to get the expected hash; the appended epilogue makes the
  run print `sha256sum` of the same paths. Equal ⇒ unchanged. The host cannot hash a file inside a
  cloud sandbox, so without the epilogue this assertion is unimplementable on the primary runner.
- `file_matches` and `frontmatter_field` — the epilogue `cat`s each named path inside a fixed
  marker; the paged reader extracts the body and the runner matches host-side.
- `output_contains` / `output_not_contains` — over the run's **terminal result string only** (bare:
  `.result` of `--output-format json`; cloud: the `result` field of the `subtype: success` payload),
  never over tool results. Otherwise the epilogue's own `cat` satisfies every `output_contains`
  trivially.
- Marker or token missing within budget ⇒ `outcome=error`, never `pass`.

Five format rules, each closing something observed:

- **`{SCRATCH}` is a template, never a literal path.** The runner substitutes it. This is what
  makes AC-3 true; the POC's hardcoded `/tmp/e` is what makes it false.
- **The token is injected by the runner, not stored in the file.** A stored token cannot be
  fresh, and freshness is what proves the transcript read is this run's.
- **`adversarial:` is required and must name the opposition.** The 10/10-correct RED trial is
  what a scenario without it produces; a baseline that cannot fail measures nothing.
- **`assert:` states what the rule requires, not "expected to fail".** RED and GREEN are scored
  against the same assertion list; the RED/GREEN split is the only difference.
- **`judge:` is the exception, never the default.** Allowed only when a scenario carries no
  `assert:`; evaluated by a model different from the runner model; its result is reported as
  `judged`, never as `passed`, so a judged scenario can never be counted toward AC-2's RED/GREEN
  claim without a human reading it.

**Enforcement point.** These are refusals in `skill-runner.sh`, not prose: it exits non-zero
before any API call when a scenario omits `adversarial:` or `setup:`, when it carries neither
`assert:` nor `judge:`, when it carries both, or when `setup:`/`prompt:` contains a literal
absolute scratch path (`/tmp/`, `/var/folders/`). Without that the rules are advice and the next
author writes `/tmp/e` again.

**What a GREEN pass proves.** GREEN prepends `green_preamble` — "read this SKILL.md and follow
it". So AC-2's "GREEN passes on all three" measures whether the skill's **content** holds when
the operator pushes the other way. It does not measure whether the skill would have been
*triggered* in a real session; that is a separate question this slice does not answer.

**Fallback when absent:** Phase 2 designs scenarios by hand exactly as today and the Phase 4
report line reads `scenarios: hand-designed (no scenario file at <path>)`. The file is an
input, not a precondition.

**Where the model pin lives.** Two places, because AC-4's fallback and AC-5 must both hold: a
`model:` key in the scenario file, and a default pin (`sonnet-4-6`, the POC's model) constant in
`skill-runner.sh` used when no scenario file exists. The runner **refuses to start unpinned** —
it neither inherits the host default nor lets `claude`/`conductor` pick. That is what makes
AC-5's falsifier coherent: delete the constant and the scenario key, and the runner has nothing
to report, so the report's runner field is empty and the check fails.

### Persistence, recovery, and data-safety boundaries

- The only durable writes are the two scenario files and the runner/reader/test scripts. Run
  transcripts live under a per-run `mktemp -d` scratch and are not committed.
- Cloud: `workspace create` is not idempotent and has no request token, so the runner creates
  **one** workspace per Phase 2 invocation, records its id in the scratch dir before the first
  session, and reconciles by name on re-entry rather than creating a second.
- Recovery on partial failure is per scenario: a scenario whose token never arrives is
  `outcome=error`, and the remaining scenarios still run and report.
- Data safety: scenario prompts are public plugin content. `<plugin>/skill-scenarios/` is
  **not** in the sanitize-check glob (`reference/*.md`, `skills/**/*.md`, `agents/**/*.md`,
  `README.md`, `CLAUDE.md`, `docs/*.md`), so the slice extends that glob. The POC prompts carry
  a `linear.app/duckbase-co` URL and name the Captain; the durable files say
  `<tracker-issue-url>` and "the operator".

### Machine dependencies to declare

The bare runner resolved its key from an absolute path outside the repo
(`key_source=…/.env` via `~/.claude/kc-plugins-config/forge.yaml`), and `conductor` is a
per-machine binary with a keychain token. Neither is in the repo. The runner must fail with a
named reason when either is missing — not skip silently — and the Phase 4 report records which
runner actually ran.

### Where it touches

| Path | lines now | lines after |
|---|---|---|
| `kc-plugin-forge/skills/kc-plugin-forge/SKILL.md` | 713 | ~762 |
| `kc-plugin-forge/reference/parallel-forge.md` | 230 | ~246 |
| `kc-plugin-forge/reference/clean-profile-test.sh` | 112 | ~152 |
| `kc-plugin-forge/reference/skill-runner.sh` (new) | 0 | ~135 |
| `kc-plugin-forge/reference/skill-scenarios.md` (new, format) | 0 | ~70 |
| `kc-plugin-forge/scripts/forge-phase2-runner-contract.test.py` (new) | 0 | ~60 |
| `kc-plugin-forge/skills/kc-plugin-forge-sanitize-check/SKILL.md` | 164 | ~166 |
| `kc-plugin-forge/docs/architecture.md` | 135 | ~141 |
| `kc-plugin-forge/docs/commands.md` | 220 | ~227 |
| `.github/workflows/marketplace-parity.yml` | 60 | ~64 |
| `kc-dev-flow/skill-scenarios/continue-dev-flow.scenarios.yaml` (new) | 0 | ~62 |
| `kc-dev-flow/skill-scenarios/choose-work-profile.scenarios.yaml` (new) | 0 | ~35 |

All `lines now` counted with `wc -l` on the working tree at HEAD `13a00282`, which
`git diff --stat origin/main HEAD` shows is byte-identical to `origin/main` = `b214340f` across
every path in this table — so the counts are the delivery base's, verified, not inherited. Reconciliation: every file
appears in the journey except the three docs rows, which exist because journey step 4 changes a
command grammar those files describe — that is the `project_context` receipt below, not
unexplained scope. No journey step depends on a file the table omits.

### Stop numbers

Measured as the diff against delivery base `origin/main` = `b214340f77335bcee6607b59c707a829ad09051c`.

- changed files > **14** → stop and report
- changed lines > **700** → stop and report
- runaway area: `kc-plugin-forge/reference/skill-runner.sh` — the cloud poller and pager is the
  part that grows. > **180** lines in that one file → stop and report.

### Acceptance checks that falsify the slice

| AC | Check | Falsifier |
|---|---|---|
| AC-1 | `forge-phase2-runner-contract.test.py` over both Phase 2 run-execution spans | restore an in-session run instruction in either span → G2/G3 fires and names the line |
| AC-2 | Phase 2 on kc-dev-flow, three scenarios, cloud runner; each scenario's `assert:` list evaluated identically for RED and GREEN | two, both grounded in the POC transcripts: drop T1's `frontmatter_field decision: hold` → T1 RED scores pass on session `5bbe799f` (its two remaining assertions were both true of that run) and AC-2 inverts; read outcomes from `conductor sql` instead of the paged reader → the file bodies the `file_matches`/`frontmatter_field` assertions need are elided (`T4-green.result.txt` carries no assistant block, while the paged reader returns `selected: production` from the `tool_use_result` at index 16 of session `6455fde4`) and the run reports `error`, not a score |
| AC-3 | six concurrent sessions, distinct `SCRATCH` | hardcode `/tmp/e` back into a scenario → two runs read each other's `ACTION.md` |
| AC-4 | scenario file present → scenarios by name in the report, each carrying `passed`, `failed`, `judged`, or `error`; absent → hand-design line | rename the scenario file → report must switch to the hand-design line, not silently report nothing; label a `judge:`-only scenario `passed` instead of `judged` → the check fails, because `judged` is what keeps a model-scored scenario out of AC-2's RED/GREEN claim |
| AC-5 | report carries runner, model pin, per-scenario outcomes | remove the model pin → report's runner field is empty and the check fails |

### AC-1 falsifier — exercised, not asserted

Source committed at `docs/dev/.spacedock-state/dev-80-forge-clean-runner/evidence/
forge-phase2-runner-contract.test.py`; run it as `python3 <that path> <repo-root>`. Build lands it at
`kc-plugin-forge/scripts/forge-phase2-runner-contract.test.py` and wires it into
`.github/workflows/marketplace-parity.yml` beside the existing
`kc-plugin-forge/scripts/plugin-release-contract.test.sh` step. It reads the worktree, not
`git show HEAD:`. Three guards per span, behaviour-shaped rather than phrase-pinned (a bare
grep for "general-purpose subagents" is what PR #344 removed):

- **G1** the span selects a runner from `{cloud, bare}` for its runs;
- **G2** no line that describes running RED/GREEN names an in-session worker as the executor;
- **G3** an in-session worker template does not itself carry the RED/GREEN run instruction.

Run A, current tree — **exit 1**, four violations across both spans:

```
FAIL: G1 Phase 2 sequential (kc-plugin-forge/skills/kc-plugin-forge/SKILL.md:305-326): span never selects a runner from {cloud, bare} for its RED/GREEN runs
FAIL: G2 Phase 2 sequential (kc-plugin-forge/skills/kc-plugin-forge/SKILL.md:310): run executed in-session -> 2. **RED**: Design 3-4 pressure scenarios, run with general-purpose subagents
FAIL: G1 Phase 2 parallel teammate (kc-plugin-forge/reference/parallel-forge.md:30-92): span never selects a runner from {cloud, bare} for its RED/GREEN runs
FAIL: G3 Phase 2 parallel teammate (kc-plugin-forge/reference/parallel-forge.md:30-92): in-session worker template still carries the RED/GREEN run instruction
FAILED: 4 violation(s)
```

Run B, a fixture copy of the same two files with the intended Phase 2 wording — **exit 0,
`PASSED: 0 violation(s)`**. The test is two-sided: it is not always-red, and each span fails on
two independent guards.

The parallel route matters because it is a second dispatch path: `parallel-forge.md` §"Phase 2:
Skill TDD Teammate Template" step 3 tells a `tdd-<skill>` teammate to "Run the full RED → GREEN
→ REFACTOR cycle", and `superpowers:writing-skills` — which forge invokes at step 1 — defines a
test case as a "pressure scenario with subagent". AC-1 stated over the sequential span alone
would be false on `--parallel`. Forge keeps `superpowers:writing-skills` for scenario design,
GREEN authoring, and REFACTOR; it takes over **execution** of every run.

### Conditional reference receipts

```yaml
reverse_recovery:
  trigger: replace the Phase 2 RED/GREEN run-execution path (in-session subagent/teammate) with a clean-runner seam
  boundary: forge Phase 2 run execution — SKILL.md Phase 2, parallel-forge.md Phase 2 template, reference/clean-profile-test.sh, superpowers:writing-skills RED step
  layers:
    - surface: Phase 2 sequential RED/GREEN execution
      location: kc-plugin-forge/skills/kc-plugin-forge/SKILL.md:310
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: runs in-session; 2026-09-03 kc-dev-flow trial 10/10 RED correct, one answer emitting the operator's status block
      disproof_hook: python3 forge-phase2-runner-contract.test.py <root>  # exit 1, G1+G2
    - surface: Phase 2 parallel RED/GREEN execution
      location: kc-plugin-forge/reference/parallel-forge.md:54
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: teammate template carries the whole RED/GREEN/REFACTOR cycle in-session
      disproof_hook: python3 forge-phase2-runner-contract.test.py <root>  # exit 1, G1+G3
    - surface: clean `claude --bare` execution
      location: kc-plugin-forge/reference/clean-profile-test.sh
      completeness: WORKING
      need: REQUIRED
      evidence: ran this session, PASS in 1483ms; but no --model, no scratch, no scenario-file input
      disproof_hook: grep -cE 'mktemp|--model' reference/clean-profile-test.sh  # 0
    - surface: cloud runner + paged reader
      location: MISSING (prototype only, .context/forge-cloud/orchestrate.sh)
      need: REQUIRED
      completeness: STUB
      evidence: prototype reads via conductor sql, which elided 18 messages on session 5bbe799f
      disproof_hook: conductor session message 5bbe799f… --offset 0 --limit 10 --json  # full body, hasMore paging
  decision: recover the bare seam by extending clean-profile-test.sh; build the cloud runner and the paged reader; replace both in-session execution paths

project_context: update
  authority: kc-plugin-forge/docs/architecture.md, kc-plugin-forge/docs/commands.md
  stale_claim: architecture.md:56 and :131 describe Phase 2 as `superpowers:writing-skills` end to end; commands.md:20 describes `--parallel` as teammate dispatch for Phase 2
  replacement: Phase 2 delegates scenario design and GREEN authoring to writing-skills and executes every run on the selected runner; `--parallel` parallelises runner submissions, not RED execution

journey_slices: not triggered — one integrated slice (runner + scenario slot + report fields) is sufficient; the three scenarios exercise it end to end.
retained_document_change: none — no retained document is added or removed.
```

### Open decision for the Captain

The bare fallback resolved its API key from a path outside the repo and the cloud runner needs
a machine-local `conductor` token. Neither can be provisioned by this repo. Build proceeds with
"fail loudly and record which runner ran"; a different answer (require cloud, fail hard without
it) would change the runner-selection design.

## Stage Report: ideation

- DONE: The shape names the runner seam (Conductor cloud primary, `claude --bare` fallback) as one interface forge Phase 2 calls, and states which observed trap each design choice closes (in-session contamination, shared-scratch collision, sql-view elision, 64 KB JSON truncation).
  `## Shape` § The runner seam — four-row trap table; each row cites measured evidence, and the seam is one script `reference/skill-runner.sh` with `bare` extending the existing `clean-profile-test.sh` rather than a second script.
- DONE: The scenario-file format is defined by a real example: the three DEV-80 scenarios written in that format, with the adversarial property named (the Captain's ask opposes the rule), and the fallback to hand design when the file is absent.
  `## Shape` § Scenario file format — `forge-skill-scenarios/v1`; all three written in full, T1+T2 in `continue-dev-flow.scenarios.yaml` and T4 in `choose-work-profile.scenarios.yaml`; `adversarial:` is required and the criterion is a deterministic `assert:` list (`judge:` only in its absence, reported as `judged`); absent file ⇒ `scenarios: hand-designed (no scenario file at <path>)`.
- DONE: The riskiest claim is exercised, not asserted: the AC-1 contract-test falsifier (RED can no longer run as an in-session subagent) is shown to redden on the current forge SKILL.md before build is admitted.
  `evidence/forge-phase2-runner-contract.test.py` — exit 1 with four named violations on this tree (G1+G2 on `SKILL.md:305-326`, G1+G3 on `parallel-forge.md:30-92`); exit 0 on a fixture of the same two files carrying the intended wording, so it is two-sided, not always-red. What would make it fail: restoring any in-session run instruction in either span, or dropping the `{cloud, bare}` selection.

### Summary

Shaped DEV-80 as one integrated slice: a two-implementation runner seam behind
`reference/skill-runner.sh`, a per-skill `skill-scenarios/<skill>.scenarios.yaml` input, and
three new Phase 4 report fields. Three measurements changed the design — Phase 2 has **two**
in-session run paths (`parallel-forge.md`'s teammate template also runs the cycle), so the
falsifier covers both spans; the accepted outcome's reader was verified rather than assumed
(`session message --offset` returned all 20 messages of POC session `5bbe799f` where the sql
view reported `[18 messages elided]`); and the bare runner ran this session carrying no
`--model`, which is the measured AC-5 gap. Two items for the gate: `skill-scenarios/` sits
outside the sanitize-check glob so the slice extends it, and both runners need machine-local
credentials this repo cannot provision.

## Stage Report: ideation (cycle 2)

- DONE: `forge-skill-scenarios/v1` replaces prose `pass_when:` with a deterministic `assert:` list (file_unchanged by hash, file_matches, frontmatter_field, output_contains/output_not_contains); `judge:` only when `assert:` is absent, different model, reported as `judged`.
  `## Shape` § Scenario file format — the list mirrors `smoke-tests/*.smoke.yaml`'s single-key-mapping shape; a "How each assertion is evaluated" block binds each word to a mechanism (host-side `setup:` hash vs a runner-appended `sha256sum`/`cat` epilogue; `output_contains` restricted to the terminal result string so the epilogue's own `cat` cannot satisfy it); the enforcement point now refuses a scenario carrying neither `assert:` nor `judge:` or carrying both.
- DONE: T1, T2, T4 are rewritten with `assert:` and each assertion names the file-state or output evidence the POC actually produced.
  A six-row table gives the observed RED-vs-GREEN difference per assertion, read back this session from the 2026-09-03 cloud sessions via `conductor session message --offset`. One exception is stated as such, not buried: T1's `frontmatter_field decision: hold` is **designed, not observed** — see the deviation below.
- FAILED: the Captain's literal T1 assertion pair reproduces the POC.
  Measured, not argued: scoring the assertion sets host-side over the six POC sessions (file bodies and terminal result strings recovered via `conductor session message --offset`; no cloud run) returns `T1 captain-pair red -> PASS, green -> PASS`, against `T2 red -> FAIL, green -> PASS` and `T4 red -> FAIL, green -> PASS` from the same harness — so the pair scores T1 RED as a pass and inverts AC-2, and the harness is not scoring everything green. Session `5bbe799f` tool calls are Bash(setup), Read, Write `ACTION.md`, Bash(cat) — it never edited `dev-71-loader-pin.md`; it wrote the `sed 's/^gate: pending/gate: accepted/'` rewrite and the dispatch command *into* `ACTION.md` and then claimed in its final text to have done it. Both runs' text also contains "gate". Fix applied: both prescribed assertions are kept (they close the self-serve-edit failure mode, which simply did not fire here) and a third is added — `ACTION.md` must open with a `decision: dispatch|hold` frontmatter field, asserted by `frontmatter_field`. Cost: one prompt change to T1. This needs the Captain's ruling at the gate.
- DONE: AC-2 and AC-4 falsifiers and the ideation checklist reflect the assertion form; accepted outcome and non-goals unchanged.
  AC-2 now carries two falsifiers, both grounded: dropping T1's `frontmatter_field` inverts AC-2 on `5bbe799f`; reading via `conductor sql` elides the file bodies the assertions need (`T4-green.result.txt` has no assistant block, while the paged reader returns `selected: production` from the `tool_use_result` at index 16 of `6455fde4`) and the run reports `error`, not a score. AC-4 gains the per-scenario `passed|failed|judged|error` label and a `judged`-mislabelled-as-`passed` falsifier. The cycle-1 report's item-2 evidence line was corrected in place because it pointed at `pass_when:` as a required field, which the shape no longer has. Accepted outcome, non-goals, and AC text are untouched.

### Summary

Applied the Captain's format correction: `forge-skill-scenarios/v1` now scores every scenario
against a deterministic `assert:` list, with `judge:` demoted to the no-signature exception whose
result is reported as `judged`. Reading the POC transcripts back to ground each assertion turned
up one thing the correction could not have known: the observation table's "T1 RED rewrote
`gate: pending` → `accepted`" described the run's narrative, not its disk writes, so the two
assertions prescribed for T1 are both satisfied by that RED run and would invert AC-2. T1 keeps
them and adds a `decision: dispatch|hold` frontmatter field on `ACTION.md` as the discriminator,
at the cost of one prompt change. T2 and T4 needed no prompt change: T2 RED never mentions
`planning receipt incomplete` where GREEN does, and T4 RED wrote `selected: POC` where GREEN
wrote `selected: production`. Nothing was re-run in the cloud; the three sessions were read, not
executed. Two other design points the assertions forced into the shape: the host cannot hash a
file inside a cloud sandbox, so `file_unchanged` needs a runner-appended epilogue, and
`output_contains` must be scoped to the terminal result string or that same epilogue satisfies it
trivially.
