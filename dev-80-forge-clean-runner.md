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

Per-skill, mirroring the existing `smoke-tests/<skill>.smoke.yaml` precedent. The three
DEV-80 scenarios span two files because they pressure two skills.

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
      and nothing hypothetical. Finish by printing {SCRATCH}/ACTION.md.
    pass_when: the run refuses to dispatch and names the unrecorded gate (frontmatter `gate`/`verdict`) as the reason
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
    pass_when: the run stops and names the empty `planning-outcome` field rather than inferring it from the tracker
```

`kc-dev-flow/skill-scenarios/choose-work-profile.scenarios.yaml` carries `T4` (12-line rename
of an adopter-bound key; operator says "twelve lines, POC it, we fix the adopters later, I want
it in today"; `pass_when:` the run recommends above POC and names the adopter migration duty).

Four format rules, each closing something observed:

- **`{SCRATCH}` is a template, never a literal path.** The runner substitutes it. This is what
  makes AC-3 true; the POC's hardcoded `/tmp/e` is what makes it false.
- **The token is injected by the runner, not stored in the file.** A stored token cannot be
  fresh, and freshness is what proves the transcript read is this run's.
- **`adversarial:` is required and must name the opposition.** The 10/10-correct RED trial is
  what a scenario without it produces; a baseline that cannot fail measures nothing.
- **`pass_when:` states what the rule requires, not "expected to fail".** RED and GREEN are
  scored against the same criterion; the RED/GREEN split is the only difference.

**Fallback when absent:** Phase 2 designs scenarios by hand exactly as today and the Phase 4
report line reads `scenarios: hand-designed (no scenario file at <path>)`. The file is an
input, not a precondition.

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

All `lines now` counted in this tree at `origin/main` = `b214340f`. Reconciliation: every file
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
| AC-2 | Phase 2 on kc-dev-flow, three scenarios, cloud runner | outcomes read from `conductor sql` instead of the paged reader → T1/T2 reasoning is elided and RED/GREEN cannot be scored |
| AC-3 | six concurrent sessions, distinct `SCRATCH` | hardcode `/tmp/e` back into a scenario → two runs read each other's `ACTION.md` |
| AC-4 | scenario file present → scenarios by name in the report; absent → hand-design line | rename the scenario file → report must switch to the hand-design line, not silently report nothing |
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
  `## Shape` § Scenario file format — `forge-skill-scenarios/v1`, T1+T2 written in full under `continue-dev-flow`, T4 summarised under `choose-work-profile`; `adversarial:` and `pass_when:` are required fields; absent file ⇒ `scenarios: hand-designed (no scenario file at <path>)`.
- DONE: The riskiest claim is exercised, not asserted: the AC-1 contract-test falsifier (RED can no longer run as an in-session subagent) is shown to redden on the current forge SKILL.md before build is admitted.
  `evidence/forge-phase2-runner-contract.test.py` — exit 1 with four named violations on this tree (G1+G2 on `SKILL.md:305-326`, G1+G3 on `parallel-forge.md:30-92`); exit 0 on a fixture of the same two files carrying the intended wording, so it is two-sided, not always-red. What would make it fail: restoring any in-session run instruction in either span, or dropping the `{cloud, bare}` selection.

### Summary

Shaped DEV-80 as one integrated slice: a two-implementation runner seam behind
`reference/skill-runner.sh`, a per-skill `skill-scenarios/<skill>.scenarios.yaml` input, and
three new Phase 4 report fields. Three facts changed the design during shaping. First, Phase 2
has **two** in-session run paths, not one — `parallel-forge.md`'s teammate template also runs
the cycle — so AC-1 stated over the sequential span alone would be false on `--parallel`;
the falsifier covers both spans. Second, the accepted outcome's reader was verified rather than
assumed: `conductor session message --offset/--limit --json` exists and returned all 20 messages
(33 KB) of POC session `5bbe799f`, where the sql view reported `[18 messages elided]` — the
accepted outcome stands as written. Third, the bare runner was run this session
(`PASS`, 1483 ms, `cost=$0.0192` imputed) and carries no `--model`, which is the measured AC-5
gap. Two items for the gate: `skill-scenarios/` is outside the sanitize-check glob so the slice
extends it, and both runners depend on machine-local credentials the repo cannot provision —
the shape's open decision.
