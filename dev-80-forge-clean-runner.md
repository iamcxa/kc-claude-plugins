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
worktree: .worktrees/spacedock-ensign-dev-80-forge-clean-runner
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
            - id: gate-attempt:kmt1mgvwqy0g9qmshemqtsn1-ideation-2
              briefing:
                id: briefing:kmt1mgvwqy0g9qmshemqtsn1:ideation:attempt-2:revision-1
                digest: sha256:a17b8a8a886f70e651ce4ee8232980cdd84968db5d65f76baf99d25c16bcb6f9
                room-ref: ./dev-80-forge-clean-runner/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:kmt1mgvwqy0g9qmshemqtsn1:ideation:2
                briefing: briefing:kmt1mgvwqy0g9qmshemqtsn1:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-09-03T09:50:43.42895Z"
                decision: approve
                reason: 'Captain approved the corrected shape at attempt 2: assert: list replaces prose pass_when, judge: demoted to judged; T1 gains the frontmatter_field decision: dispatch|hold assertion (one prompt change, designed not observed, AC-2 falsifier names it); credential default is fail loudly and record which runner ran.'
              application:
                target-stage: implementation
                state: consumed
            - id: gate-attempt:kmt1mgvwqy0g9qmshemqtsn1-ideation-3
              briefing:
                id: briefing:kmt1mgvwqy0g9qmshemqtsn1:ideation:attempt-3:revision-1
                digest: sha256:5c41285772219478a8c62590d044fc3a575516a8b3cba776337bb86ac74cfbe7
                room-ref: ./dev-80-forge-clean-runner/review/ideation/briefing-3
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

Forge Phase 2 gets one interface, `python3 reference/skill-runner.py <runner> <scenario-file>
<scenario-id> <variant> <plugin-dir>`, with two implementations behind it. It prints one
line per run — `outcome=<pass|fail|error> runner=<cloud|bare> model=<pin> scratch=<dir>` —
and writes the full transcript to `<scratch>/<id>-<variant>.json`. Phase 2 calls only this
interface; it never dispatches the run itself.

**Cycle 3 correction.** The built tree reached that interface through a 17-line
`reference/skill-runner.sh` whose entire body is `exec python3 "$HERE/skill-runner.py" "$@"`.
Cut. Nothing breaks: this repository already invokes `python3 <script>.py` directly from CI
(`.github/workflows/marketplace-parity.yml` runs `python3 ./kc-plugin-forge/scripts/forge-phase2-runner-contract.test.py .`)
and from the release smoke documented in `CLAUDE.md`. The wrapper's one observed effect was
a mode-644 commit that made every dispatch fail with "permission denied" until `chmod +x`
(`a640a72f`) — a failure class the direct `python3 <path>` call does not have.

| Choice | Trap it closes | Evidence |
|---|---|---|
| Every RED/GREEN run leaves the session (cloud sandbox or `claude --bare`) | **in-session contamination** — the 2026-09-03 kc-dev-flow trial had 10/10 RED answers correct, one emitting the operator's own status block and one citing "the CLAUDE.md guardrail" | brief; `--bare` documented as skipping MEMORY.md, CLAUDE.md discovery, hooks, plugin sync (`reference/clean-profile-test.sh` header) |
| Runner mints a per-run scratch dir and substitutes it for `{SCRATCH}` in the scenario | **shared-scratch collision, observed not hypothetical** — all six POC scenarios wrote the same absolute `/tmp/e/ACTION.md`, and the six sessions shared one workspace (`2bfb186a`), so one filesystem: T2 GREEN (`866bd372`) never ran its own setup heredoc and read the `dev-72-receipt.md` that T2 RED (`c26fd227`) had written. Cycle 1 recorded that the cloud sandboxes hid this; scoring the transcripts disproved it | `grep -cE 'mktemp\|cd \|TMPDIR\|SCRATCH' reference/clean-profile-test.sh` = 0 — the bare runner has no scratch of its own and inherits the caller's `$PWD` |
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
5. **DESIGNED** — For each scenario, `skill-runner.py` mints `SCRATCH=$(mktemp -d
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
| T1 `file_unchanged` on the work item — **cut in cycle 3** | held — RED wrote the `sed 's/^gate: pending/gate: accepted/'` line *into* `ACTION.md` rather than running it (session `5bbe799f`, tool calls: Bash setup, Read, Write `ACTION.md`, Bash cat) | held |
| T1 `frontmatter_field decision: hold` | designed at cycle 2; **observed in the build and it did not discriminate** — live RED session `334a0f15` wrote `decision: hold` with no skill in context (§ Cycle 3: T1) | designed |
| T1 `output_contains: gate` | held — RED's own text says "unrecorded gate acceptance" | held (`227f0f47`: quotes the deterministic-gate rule) |
| T2 `file_unchanged` on the receipt — **cut in cycle 3** | held — RED never edited it (`c26fd227`) | held (`866bd372`) |
| T2 `planning receipt incomplete` | **absent** — RED stopped for an unrelated reason (brief named no code location) and never mentions the receipt | present in `ACTION.md` and in the final output, citing § 4 |
| T4 `selected:\s*production` | **no match** — RED wrote `selected: POC, recommended: Pilot` (`79e089f8`) | match — `selected: production` (`6455fde4`) |

**T1's two prescribed assertions do not discriminate on their own, and that is why the third
exists.** Scored against the recorded POC sessions this cycle — assertion sets evaluated
host-side over the file bodies and terminal result strings recovered through `conductor session
message --offset`, nothing re-run — the pair `file_unchanged` + `output_contains: gate` returns
**pass on RED and pass on GREEN**, so it scores T1 RED as a pass and inverts AC-2. The same
harness returns RED fail / GREEN pass for T2 and for T4, so it is not scoring everything green.
T1's three-assertion set returns fail on both variants, because the POC prompt had no `decision:`
field to read — that assertion is the one build's AC-2 run has to observe. Harness committed at
`docs/dev/.spacedock-state/dev-80-forge-clean-runner/evidence/poc-assert-scoring.py`; it reads the six
sessions and creates none. Its `file_unchanged` is falsifiable, not decorative:
running it with `--mutate-t1-red` injects a rewrite of the T1 fixture and the assertion flips to
`False`. They were kept at cycle 2 because they close a real
failure mode — a run that edits the work item to make the gate look accepted — which simply did
not fire in this POC. The `decision:` frontmatter field carries the discrimination, at the cost of
one prompt change: `ACTION.md` must now open with that field. It does not cue the answer; the
prompt already poses the dispatch-or-message binary.

**Cycle 3 supersedes both halves of that paragraph.** The build ran T1 for real and `decision:`
did not discriminate either — see § Cycle 3: T1 is retired from AC-2's RED-fail claim. And
`file_unchanged` is cut from `forge-skill-scenarios/v1`: across the six POC sessions and the six
live sessions it held twelve times out of twelve, and the one run that came closest to the failure
mode it names (POC `5bbe799f`, which wrote the `sed` rewrite *into* `ACTION.md`) it scores as
unchanged. See § Cycle 3: the runner, block by block, and the Captain decision below.

**How each assertion is evaluated.**

- `file_unchanged: <path>` — **cut in cycle 3.** It required a host-side re-run of `setup:` and a
  `sha256sum` epilogue (33 lines across six blocks) and discriminated nothing in twelve runs.
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

**Enforcement point.** These are refusals in `skill-runner.py`, not prose: it exits non-zero
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
input, not a precondition. **How a hand-designed scenario reaches the runner** — one clause in
`SKILL.md` Phase 2 step 3, added in cycle 3 because AC-1 forbids an in-session run and the runner
reads only scenario files, so without it the next implementer invents a second input path: Phase 2
writes the hand-designed scenarios to a `forge-skill-scenarios/v1` file under its own scratch dir
and calls the runner with that path. They pass the same refusals as a checked-in file; only the
report line distinguishes them.

**Where the model pin lives.** Two places, because AC-4's fallback and AC-5 must both hold: a
`model:` key in the scenario file, and a default pin (`sonnet-4-6`, the POC's model) constant in
`skill-runner.py` used when no scenario file exists. The runner **refuses to start unpinned** —
it neither inherits the host default nor lets `claude`/`conductor` pick. That is what makes
AC-5's falsifier coherent: delete the constant and the scenario key, and the runner has nothing
to report, so the report's runner field is empty and the check fails.

### Persistence, recovery, and data-safety boundaries

- The only durable writes are the two scenario files and the runner/reader/test scripts. Run
  transcripts live under a per-run `mktemp -d` scratch and are not committed.
- Cloud: `workspace create` is not idempotent and has no request token, so the runner creates
  **one** workspace per Phase 2 invocation, records its id in the scratch dir before the first
  session, and reconciles by name on re-entry rather than creating a second. The build's
  reconciler returned a peer's id without waiting for `ready`; corrected in § Cycle 3: residual
  dispositions, residual 1.
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

The runner also parses YAML, so **PyYAML** is a third machine dependency this repository does not
vendor. The built runner names it (`missing machine dependency: PyYAML (pip install pyyaml)`)
rather than raising `ImportError`; that refusal stays.

### Cycle 3: the runner, block by block

The build put the whole runner in `kc-plugin-forge/reference/skill-runner.py` — 390 lines at
`a640a72f`, a file the table below never listed — behind the 17-line `skill-runner.sh` cut above.
Two of this shape's own numbers were inconsistent before the build started and could not both
have held: the table budgeted `skill-runner.sh (new) ~135` lines for the entire runner, while
`### Stop numbers` set a 180-line runaway guard on one area *inside* that same file. A 135-line
file cannot contain a 180-line sub-area, so the guard could not fire until the table's own
estimate was already blown. That estimate was not derived from the work. This section derives it.

Line ranges are measured with `cat -n` on `skill-runner.py` at `a640a72f`. "Keep" means the block
answers what breaks without it and names the run that shows it; "cut" means it cannot.

| Block (lines) | Verdict | What breaks without it — and the run that shows it |
|---|---|---|
| module docstring 1–14 (14) | keep, −8 | usage and the outcome-line format stay; the rest restates `skill-scenarios.md` |
| imports + constants 15–32 (18) | keep | `DEFAULT_MODEL` is AC-5's pin; `ABS_SCRATCH_LITERAL` is AC-3's refusal |
| `outcome_line` + `die` 34–41 (8) | keep | the outcome line is the only thing Phase 2 reads back; every refusal in the implementation report prints it |
| `load_yaml` 44–50 (7) | keep | names PyYAML as a declared machine dependency instead of raising `ImportError` |
| `validate_scenario` 53–66 (14) | keep | the five format refusals; five exercised at `exit 2` in the build (literal `/tmp/e`, both `assert:`+`judge:`, neither, missing `adversarial:`, missing `setup:`). Without it AC-3's strong form — the collision cannot be attempted — is prose |
| `resolve_model` 69–74 (6) | keep | AC-5's falsifier: `DEFAULT_MODEL=""` with no scenario or file pin → `exit 2, no model pin resolved`. Exercised |
| `bare_model_id` 77–82 (6) | keep, −2 | the two CLIs take different model spellings. Its docstring asserts `claude --bare --model sonnet-4-6` 404s — an absolute the implementation report flagged as not re-verified. Rewrite as the dated bounded observation |
| `assertion_paths` 85–95 (11) | keep, −3 | tells the epilogue which paths to print; loses the `hashed` half with `file_unchanged` |
| `build_epilogue` 98–112 (15) | keep, −2 | without an epilogue the host cannot see file state inside a cloud sandbox at all, so `file_matches`/`frontmatter_field` are unimplementable on the primary runner. Its four-line comment stays: an epilogue phrased as "your final action" was observed to swallow the spoken answer, leaving `output_contains` nothing to match |
| `substitute` 115–116 (2) | keep | `{SCRATCH}` templating is what makes AC-3 true |
| `build_prompt` 119–131 (13) | keep, −2 | assembles preamble/setup/prompt/epilogue; the GREEN preamble is the only RED/GREEN difference |
| **`host_side_baseline` 134–151 (18)** | **cut, −19** (block + its blank separator) | exists only to compute `file_unchanged`'s expected hash. See the Captain decision below |
| `extract` 154–174 (21) | keep, −3 | recovers file bodies from `tool_use_result` and the terminal string from the `subtype: success` payload; loses the sha half |
| `score` 177–204 (28) | keep, −3 | the scoring path itself, two-sided on six live sessions (T2/T4 RED fail, three GREEN pass, T1 RED pass); loses the `file_unchanged` branch |
| `run_bare` 207–226 (20) | keep | the fallback named in `## Accepted outcome`. Never completed a run — see residual 3 |
| `resolve_project_id` 229–240 (12) | keep | `conductor session create` needs a project id and nothing else resolves it from the git remote |
| `reconcile_workspace` 243–284 (42) | keep, +2 | `workspace create` is not idempotent and has no request token, so without the lock file six scenario-variant calls create six workspaces. Carries residual 1's cause; the fix is two lines here, not a rewrite |
| `run_cloud` 287–307 (21) | keep | the primary runner; six live sessions |
| `page_until_token` 310–341 (32) | keep, −4 docstring, +3 | the paged reader is the accepted outcome's named mechanism — the sql view elided 18 of 20 messages on `5bbe799f` |
| `main` 344–390 (45) | keep, −1 | argv, scratch and token minting, dispatch, exit code; loses the `baseline =` call |
| scenario-file-absent refusal | **add +2** | the built runner raises a traceback on a missing scenario file; AC-4's absent branch gets a named reason at the script boundary |

Projected: 390 − 33 (`file_unchanged`) − 14 (three docstrings) + 7 (new guards) = **350** — the
per-block deltas in the column above sum to −40, which is the same number.

Cutting `file_unchanged` is the only block-level cut, and it is not free of the Captain's earlier
ruling — see § Open decision for the Captain.

### Cycle 3: T1 is retired from AC-2's RED-fail claim

Evidence, from the build's own run: live session `334a0f15` (T1 RED, cloud, `sonnet-4-6`, no skill
content in context) wrote `decision: hold`, left the fixture unchanged, and its output cites
"gate" — a **pass**. The `frontmatter_field decision: hold` assertion cycle 2 added *to make T1
discriminate* was observed doing the opposite: it recorded that an unskilled run holds. The rule
T1 pressures — do not act on a remembered approval, read the recorded gate — is one the base model
already applies without the skill.

**Decision: T1 is retired from AC-2's RED-fail claim; that claim covers T2 and T4.**
`## Acceptance criteria` is not rewritten — this record is the decision and the falsifier table
below follows it.

Why not the other branch offered (redesign T1 so an unskilled run plausibly fails): a candidate
exists and is worth naming. The fixture's `gate: pending` line is a loud tell a base model reads
straight off; a fixture carrying no gate field at all, whose stage report ends
`recommendation: proceed`, would put the skill's own rule — acceptance is a recorded resolution,
absence is not acceptance — in the discriminating position without leaking the answer, because the
operator's ask and the visible evidence would both still point at dispatch. It is **not** admitted
here, for the reason this return exists: it is designed, not observed, and writing a RED-fail claim
for a run nobody has seen fail is exactly the cycle-2 error being corrected. It belongs in its own
item, executed before anything depends on it.

**T1 stays in the scenario file**, and what it now buys is stated rather than assumed: it is the
only live run in which the scorer returned `pass` on a RED baseline. T2 RED and T4 RED both
failed; without T1, nothing in the six sessions shows the scorer *can* score a baseline as a pass.
That two-sidedness on live data is why T1 is retired from the claim rather than deleted.

**The consequence the gate must rule on.** `## Accepted outcome`'s last sentence reads "RED fails
on T1 and T4, GREEN passes on all three." Retiring T1's RED-fail claim makes the T1 half of that
sentence false; the GREEN half is unaffected (all three GREEN runs passed). This shape does not
edit that sentence — `## Route-back conditions` reserves it. The Captain rules whether this is a
wording correction to the admission snapshot or a planning delta.

### Cycle 3: residual dispositions

**Residual 1 — workspace cold-start race. Fixed inside the trimmed runner, +5 lines.**
Observed: the build session's first dispatch (`38bf53e3`) returned
`outcome=error reason=session went idle without printing the token` after the full 480 s budget
with **zero messages** in the transcript, while `conductor session status` reported `working`
moments later. Cause: `reconcile_workspace`'s lock-file fast path returns a peer's workspace id
without the ready-wait the fresh-create path performs, so a session can be created against a
workspace still waking from `sleeping`; `page_until_token` then reads `status: idle` on a session
that has not started its first turn and treats it as a completed stall.
*Reproduce condition:* `conductor workspace status <id>` reports `sleeping` at `session create`
time — any Phase 2 invocation reusing a workspace idle long enough to have slept.
*Fix:* (a) in `page_until_token`, `idle` counts as a stall only after at least one
non-`userMessage` message has been seen; with zero agent-originated messages it keeps polling to
the budget. (b) in `reconcile_workspace`, the lock-file fast path waits for `status == ready` the
same way the create path does.
*Falsifier at implementation re-entry:* create one session against a workspace confirmed
`sleeping`. Without (a) it returns `outcome=error ... went idle without printing the token` on a
zero-message transcript; with (a) it returns the scenario's real outcome. Cost: one cloud session,
the same unit as each of the six AC-2 sessions.

**Residual 2 — AC-4 and AC-5 have no CI-wired check. The trimmed slice adds one; and AC-5's
report fields are a missing deliverable, not only a missing check.**
Measured on the built tree: the fenced report block under `## Phase 4: Re-validate + Report` in
`kc-plugin-forge/skills/kc-plugin-forge/SKILL.md` is **byte-identical to the delivery base**. It
carries no runner field, no model pin, and no per-scenario outcome, and AC-4's
`scenarios: hand-designed (no scenario file at <path>)` line has no slot in it. AC-5's acceptance
text is therefore not merely unchecked — the thing it accepts does not exist in the tree. The
implementation report's AC-5 evidence (`DEFAULT_MODEL=""` → `exit 2`) tests the runner's pin
refusal, which is AC-5's other half.
*Build obligation (≈5 lines in `SKILL.md`):* the Phase 4 report block gains

```
Phase 2 Runner: <cloud|bare> (<reason, when it fell back>)
                Model pin: <model>
                Scenarios: <scenario-file path> | hand-designed (no scenario file at <path>)
                <ID>: RED <passed|failed|judged|error> / GREEN <passed|failed|judged|error>
```

*CI (≈22 lines added to the existing `forge-phase2-runner-contract.test.py`):* two guards over
that block, in the same shape as G1–G3. **G4** — the block names a runner field carrying both
`cloud` and `bare`, and a model-pin field. **G5** — the block carries per-scenario RED and GREEN
outcome labels drawn from `{passed, failed, judged, error}` and a scenarios line with both the
file branch and the hand-designed branch. Falsifiers: delete the model-pin line → G4 fires and
names it; drop `judged` from the label set → G5 fires, which is the falsifier AC-4's row already
names.
*Cost per PR:* nothing beyond what already runs — the existing `Validate forge Phase 2
clean-runner contract` step invokes this script; no new step, no new job, no new checkout. Not
measured in seconds.
*Known limit, stated:* G4/G5 guard the report template and the instruction, exactly as G1–G3 do.
They prove forge is *told* to record runner, pin, and per-scenario outcome; they do not prove a
given run recorded them. The runtime half of AC-4 — a live Phase 2 behaving differently with the
scenario file present and absent — is evidenced by a live forge run only. The trimmed slice adds
the one script-boundary piece of it that a script can own: a missing scenario file exits with a
named reason instead of a traceback.

**Residual 3 — surfaced by this trim, recorded rather than carried silently: `run_bare` has never
completed a run.** `clean-profile-test.sh` ran standalone during ideation (`PASS`, 1483 ms), but
the built `run_bare` path was exercised only as far as its credential refusal; no scenario has
been scored end to end on `bare`, and `bare_model_id`'s model-spelling claim was not re-verified.
Disposition: a known limit of this slice — `cloud` is primary and carried all six AC-2 sessions —
recorded here so it is not read as tested. One `bare` run of T4 at implementation re-entry would
close it and costs no cloud workspace; it is not admitted into an acceptance criterion.

### Where it touches

Rewritten in cycle 3 against the tree that was actually built. `base` is delivery base
`4bc79749` (`origin/main` = `b214340f` plus the already-merged, unrelated ablation-anchor fix that
landed on this branch first); `built` is `a640a72f`, both counted with `wc -l`; `corrected` is what
this shape now admits.

| Path | base | built | corrected |
|---|---|---|---|
| `kc-plugin-forge/skills/kc-plugin-forge/SKILL.md` | 713 | 715 | 721 |
| `kc-plugin-forge/reference/parallel-forge.md` | 230 | 237 | 237 |
| `kc-plugin-forge/reference/clean-profile-test.sh` | 112 | 147 | 147 |
| `kc-plugin-forge/reference/skill-runner.py` (new) | 0 | 390 | ≈350 |
| `kc-plugin-forge/reference/skill-runner.sh` (built, now cut) | 0 | 17 | **0** |
| `kc-plugin-forge/reference/skill-scenarios.md` (new) | 0 | 84 | 79 |
| `kc-plugin-forge/scripts/forge-phase2-runner-contract.test.py` (new) | 0 | 54 | 76 |
| `kc-plugin-forge/skills/kc-plugin-forge-sanitize-check/SKILL.md` | 164 | 165 | 165 |
| `kc-plugin-forge/docs/architecture.md` | 135 | 143 | 142 |
| `kc-plugin-forge/docs/commands.md` | 220 | 220 | 220 |
| `.github/workflows/marketplace-parity.yml` | 60 | 63 | 63 |
| `kc-dev-flow/skill-scenarios/continue-dev-flow.scenarios.yaml` (new) | 0 | 64 | 62 |
| `kc-dev-flow/skill-scenarios/choose-work-profile.scenarios.yaml` (new) | 0 | 22 | 22 |

**What the cycle-2 table got wrong, in both directions.** It named `skill-runner.sh (new) ~135`
for the whole runner and listed no `.py` at all — the file that took 390 lines. It also
over-budgeted the parts it could see: `SKILL.md` at ~762 where the build spent 715, and
`commands.md` at ~227 where the build spent 220. The overrun is not spread across the slice; it
sits in one unlisted file, which is why the file-level guard below is restated on that file and a
second guard is restated on the area the old 180 was aiming at.

Reconciliation: every file still appears in the journey except the three docs rows, which exist
because journey step 4 changes a command grammar those files describe — the `project_context`
receipt below, not unexplained scope. `skill-runner.py` is journey steps 5–7; the
`forge-phase2-runner-contract.test.py` growth is AC-4/AC-5 (residual 2). No journey step depends
on a file this table omits.

### Stop numbers

Measured as the diff against delivery base `4bc79749`. The built tree at `a640a72f` is
**13 files, 712 insertions, 25 deletions** — over the 700-line number, which is why this stage
exists. The projection below is derived from that measured tree, line by line, not re-estimated.

| Change | insertions |
|---|---|
| built tree at `a640a72f` | 712 |
| cut `file_unchanged` (runner −33, `continue-dev-flow.scenarios.yaml` −2, `skill-scenarios.md` −5) | −40 |
| cut the `skill-runner.sh` wrapper (file −17, `architecture.md` tree row −1) | −18 |
| trim three docstrings in `skill-runner.py` | −14 |
| add residual 1's two race guards | +5 |
| add AC-4's missing-scenario-file refusal | +2 |
| add AC-5's Phase 4 report fields in `SKILL.md` | +5 |
| add the hand-designed-scenario clause to `SKILL.md` Phase 2 step 3 | +1 |
| add G4/G5 to `forge-phase2-runner-contract.test.py` | +22 |
| **projected** | **675** |

- changed files > **14** → stop and report. Projected **12** (13 built, minus the cut wrapper).
- changed lines > **700** → stop and report. Projected **675** — 25 lines of margin, thin by
  design: anything not in the table above stops and reports rather than spending it.
- runaway area, restated on the file that actually holds it:
  `kc-plugin-forge/reference/skill-runner.py` > **370** lines → stop and report. Projected
  **≈350** (390 built − 33 − 14 + 7).
- runaway area, restated on what the old 180 was aiming at — the cloud poller and pager, i.e.
  `resolve_project_id` + `reconcile_workspace` + `run_cloud` + `page_until_token` — > **130**
  lines → stop and report. Measured **107** on the built tree (12 + 42 + 21 + 32), ≈**110** after
  the race guards. That area never breached its own guard. What breached it was the scorer, the
  prompt builder, the extractor and the bare path, which the cycle-2 shape budgeted nowhere; the
  file-level guard above is the one that would have fired.

### Acceptance checks that falsify the slice

| AC | Check | Falsifier |
|---|---|---|
| AC-1 | `forge-phase2-runner-contract.test.py` over both Phase 2 run-execution spans | restore an in-session run instruction in either span → G2/G3 fires and names the line |
| AC-2 | Phase 2 on kc-dev-flow, three scenarios, cloud runner; each scenario's `assert:` list evaluated identically for RED and GREEN. **Cycle 3: the RED-fail claim covers T2 and T4** — see § Cycle 3: T1 | one, and the cycle-2 falsifier is retired by measurement (live session `334a0f15` shows T1 RED passes *with* `frontmatter_field` present): read outcomes from `conductor sql` instead of the paged reader → the file bodies the `file_matches`/`frontmatter_field` assertions need are elided (`T4-green.result.txt` carries no assistant block, while the paged reader returns `selected: production` from the `tool_use_result` at index 16 of session `6455fde4`) and the run reports `error`, not a score |
| AC-3 | six concurrent sessions, distinct `SCRATCH` | hardcode `/tmp/e` back into a scenario → two runs read each other's `ACTION.md` |
| AC-4 | scenario file present → scenarios by name in the report, each carrying `passed`, `failed`, `judged`, or `error`; absent → hand-design line. **Cycle 3: G5 in `forge-phase2-runner-contract.test.py` guards the report template's two branches; the runner refuses a missing scenario file with a named reason** | rename the scenario file → the runner exits with `scenario file not found`, not a traceback, and the report must switch to the hand-design line; drop `judged` from the report template's label set → G5 fires, because `judged` is what keeps a model-scored scenario out of AC-2's RED/GREEN claim. Known limit: G5 guards the template, not a live run |
| AC-5 | report carries runner, model pin, per-scenario outcomes. **Cycle 3: those fields do not exist in the built tree — adding them is a build obligation, and G4 guards them** | two halves: delete the model-pin line from the Phase 4 report block → G4 fires and names it (template half); delete `DEFAULT_MODEL` and every scenario/file `model:` → the runner exits 2 with `no model pin resolved`, exercised in the build (runner half) |

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

**1. Cutting `file_unchanged`, which the Captain named at ideation gate 1.** That resolution said
"T1 `file_unchanged` on the entity file plus `output_contains` gate". Cycle 3 proposes cutting the
assertion type from `forge-skill-scenarios/v1` and from T1 and T2, on measurement: across six POC
sessions and six live sessions it held **twelve out of twelve** and discriminated nothing, and the
single run that came closest to the failure mode it names — POC `5bbe799f`, which wrote the
`sed 's/^gate: pending/gate: accepted/'` rewrite *into* `ACTION.md` rather than running it — it
scores as unchanged. The failure mode it names is the one it did not catch.
Its cost is **33 lines** — `host_side_baseline` entire, plus a branch in five other blocks and the
`sha256sum` half of the epilogue. That is the difference between fitting the 700-line stop number
and breaching it again: cut → **675 insertions**; keep → **708**, over.
Captain's call: cut (the default, and what every number above assumes), or keep and rule on which
33 lines elsewhere pay for it.

**2. `## Accepted outcome`'s last sentence.** Retiring T1 from AC-2's RED-fail claim (§ Cycle 3:
T1) makes "RED fails on T1 and T4" false in its T1 half. This stage did not edit that sentence.
Wording correction to the admission snapshot, or planning delta.

**3. Carried forward from cycle 2, unchanged.** The bare fallback resolves its API key from a path
outside the repo and the cloud runner needs a machine-local `conductor` token; PyYAML is a third
un-vendored dependency. Build proceeds with "fail loudly and record which runner ran"; a different
answer (require cloud, fail hard without it) would change the runner-selection design.

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
trivially. Two things the scoring run turned up that cycle 1 had wrong: the
POC's six sessions shared one workspace filesystem, so the shared-scratch collision AC-3 names
actually happened (T2 GREEN read the fixture T2 RED wrote) rather than being hidden by the
sandboxes — the § runner seam row is corrected; and the first version of the scorer compared a
file against itself, so `file_unchanged` could never return `False`. Both are fixed and the
mutation run proves the second.

### Dispatch Retries

- Retry 1: implementation — no-completion-signal (worker session terminated by API rate limit 429, 2026-09-03 ~20:20 CST); re-dispatched -retry

## Stage Report: implementation

- DONE: AC-1 holds on the built tree and its falsifier is exercised, not asserted.
  `python3 kc-plugin-forge/scripts/forge-phase2-runner-contract.test.py .` → `PASSED: 0 violation(s)`, wired into `.github/workflows/marketplace-parity.yml` beside the release-contract step. Restoring the in-session line (`2. **RED**: Design 3-4 pressure scenarios, run with general-purpose subagents`) into `SKILL.md`'s Sequential-mode span and re-running → `FAIL: G2 ... run executed in-session`, exit 1; reverting restores `PASSED: 0 violation(s)`. Both Phase 2 run-execution spans (`SKILL.md` Sequential mode, `parallel-forge.md` Teammate Template) are covered.
- DONE: AC-2 is observed on the real cloud runner, not designed — with one designed assertion falsified in the direction the shape itself named.
  Six live sessions on workspace `71b06aaa-65ec-4c26-a6ea-351ca161f5be` (now archived), model `sonnet-4-6` / resolved `claude-sonnet-4-6`, read back via `conductor session message --offset/--limit --json`, never `sql`:
  | Scenario | Variant | Outcome | Session | Note |
  |---|---|---|---|---|
  | T1 | RED | **pass** (designed: fail) | `334a0f15` | Held correctly on its own — `decision: hold`, fixture unchanged, output cites "gate" — with no skill content in context. Per the completion checklist this is recorded as the `decision:` assertion's own falsification, not papered over as a pass. |
  | T1 | GREEN | pass | `8897f3dc` | Quotes `SKILL.md` verbatim ("Use required deterministic gates..."). |
  | T2 | RED | fail | `644cd377` | Failed by refusing the whole exercise as suspected prompt injection (the forced `TOKEN:` epilogue), never writing `ACTION.md` — a different path to the same designed outcome, not the POC's "stopped for an unrelated reason." Worth a scenario-design look, not a runner bug. |
  | T2 | GREEN | pass | `a9cdb0c1` | Writes `planning receipt incomplete`, cites skill step 4 by field name. |
  | T4 | RED | fail | `5c1cf12a` | Recommended Pilot, not Production. |
  | T4 | GREEN | pass | `0b3febf0` | Recommends Production, cites two named skill rules. |
  So: T2 and T4 reproduce the designed RED-fail/GREEN-pass split; T1 does not — RED passed. AC-2's literal text ("RED fails on T1 and T4") is therefore not fully met; the gate needs this fact, not a rounded-up summary.
- DONE: AC-3's collision falsifier does not reproduce, and per-run scratch isolation is proven at both the local refusal layer and on the live runs.
  All six sessions used distinct remote scratch dirs (`/tmp/forge-003a9b18`, `-8b80c1cb`, `-5badd6e0`, `-277b9eec`, `-c547dee3`, `-bd6308c4`) and distinct host scratch dirs. Five of six (T1-red/green, T2-red/green, T4-red) started within the same 121 ms window (`13:02:13.862`–`.983Z`) — genuinely concurrent. T4-green started ~2 minutes later, alone: my own dispatch script indexed a zsh array 0-based (`ids=(...); for i in 0 1 2 3 4 5; ids[$i]`) — zsh arrays are 1-indexed by default, so index 0 produced an empty id/variant (one wasted `outcome=error reason=runner must be cloud|bare...` run) and every real index shifted, dropping T4-green from the batch; it was dispatched separately once noticed. This is a harness bug in my run script, not in `skill-runner.sh`/`skill-runner.py`. Hardcoding `/tmp/e` into a scenario's `setup:` is refused before any API call (see below), which is the stronger form of AC-3: the collision cannot be attempted, not merely observed absent.
- DONE: every refusal in checklist item 3 is exercised locally, no API calls spent.
  | Refusal | Command | Result |
  |---|---|---|
  | Literal `/tmp/e` in `setup:` | `skill-runner.sh cloud <copy w/ /tmp/e> T1 red kc-dev-flow` | exit 2, `reason=... carries a literal absolute scratch path ... use {SCRATCH}` |
  | Both `assert:` and `judge:` | (T4 copy with both keys) | exit 2, `reason=... must carry exactly one of assert:/judge:` |
  | Neither `assert:` nor `judge:` | (T4 copy with neither) | exit 2, same reason |
  | Missing `adversarial:` | (T4 copy) | exit 2, `reason=... missing required key 'adversarial:'` |
  | Missing `setup:` | (T4 copy) | exit 2, `reason=... missing required key 'setup:'` |
  | AC-5 falsifier: `DEFAULT_MODEL=""` + scenario/file carry no `model:` | (edited then reverted `skill-runner.py`) | exit 2, `reason=no model pin resolved — scenario, file, and default constant are all empty`; file restored, `git status` clean after |
  | Missing both `CONDUCTOR_API_KEY` and `ANTHROPIC_API_KEY`(+unreachable `forge.yaml` via isolated `$HOME`) | `env -u CONDUCTOR_API_KEY -u ANTHROPIC_API_KEY HOME=$(mktemp -d) skill-runner.sh cloud ...` | exit 2, `runner=bare (cloud unavailable: CONDUCTOR_API_KEY not set)` in the outcome line, `reason=ANTHROPIC_API_KEY not found (env or forge.yaml api_key_file)` on stderr — both runners named, neither silently skipped |
  | Per-run scratch dirs (falsifier run, no cloud) | two consecutive invocations under the credential-missing path | distinct `forge-host-*` dirs each time |
- DONE: `skill-scenarios/` is inside the sanitize-check glob.
  `kc-plugin-forge-sanitize-check/SKILL.md` description line and file-list block both carry `skill-scenarios/*.yaml` (inherited from the WIP, verified present).
- FIXED (0-line): `kc-plugin-forge/reference/skill-runner.sh` was committed at mode 644 by the WIP — every dispatch failed with "permission denied" until `chmod +x`. Committed separately (`a640a72f`), no content change.
- **FALSIFIED, not verified**: the retry context's claim that the prior cloud workspace had "all six done."
  The workspace held exactly one real session (`T4-red`, `4b1727c4`) plus a `Readiness Check`. `T4-red`'s only turn hit `api_error_status: 429` ("You've hit your session limit · resets 9pm (Asia/Taipei)") with zero tool calls — it never ran. The retry context's stated reset time, "20:20 CST," was also stale: the session's own `rate_limit_info.resetsAt` (unix `1788440400`) is `2026-09-03T21:00:00+08:00`. AC-2's six real runs above were dispatched only after that time, confirmed by `conductor workspace status` returning `ready` (it was still `sleeping` at 20:40).
- **RESIDUAL, not fixed**: a workspace-cold-start race in `page_until_token`/`reconcile_workspace`.
  The first real dispatch this session (`T4-red` canary, session `38bf53e3`) returned `outcome=error reason=session went idle without printing the token` after the full 480 s budget — but the session had 0 messages and `conductor session status` showed `working` moments later, i.e. it was still waking from `sleeping`, not finished. `reconcile_workspace`'s lock-file fast path (reusing an id another caller already resolved) skips the ready-wait loop that a fresh `workspace create` goes through, so a session created against a still-sleeping workspace can report `idle` before its first turn starts, and `page_until_token` treats that as a completed stall. Re-running immediately (workspace now `ready`) succeeded (`outcome=fail`, correct). Not fixed here: `skill-runner.py` is already the file the shape's own stop-number table did not budget for at its current size (below), and this is a narrow, already-worked-around race, not a correctness defect in the scoring path.
- **NOT MET: stop numbers.** Measured against delivery base `4bc79749` (equivalent to `origin/main` merge point `b214340f` plus the already-merged, unrelated ablation-anchor fix that happened to land on this worktree branch first): `git diff --stat 4bc79749 HEAD` → **13 files, 712 insertions(+), 25 deletions(-)**. Insertions alone (712) exceed the 700-line stop number under any reading of "changed lines" (insertions-only, or insertions+deletions=737). File count (13) is under the 14-file limit. The named runaway-area guard — "`kc-plugin-forge/reference/skill-runner.sh` ... > 180 lines in that one file → stop and report" — is met *literally* (the `.sh` is a 17-line wrapper) but not in *intent*: the cloud poller/pager/scorer it names lives in `kc-plugin-forge/reference/skill-runner.py` (new, 390 lines — 2.2× the guard), a file the shape's "Where it touches" table never listed. This breach was already present in the inherited WIP before this session touched it (the retry context handed it over as "+712/-25" without comparing to the 700-line stop number); this session added 0 lines to `skill-runner.py` and only the mode-only executable-bit commit. Per the shape's own rule ("stop and report") this is reported, not self-repaired — cutting `skill-runner.py` to fit 180 lines is a redesign, not a trim, and out of scope for this stage.
- Not covered by any script: AC-4 (scenario-file-present-vs-absent fallback) is enforced in prose only, in `SKILL.md` Phase 2 step 3 — no contract test exercises it. AC-5's falsifier was exercised manually this session (above) but is not wired into CI; only AC-1 has a landed, CI-wired test per the completion checklist's own scope.
- Unverified, inherited: `bare_model_id`'s docstring claim ("`claude --bare --model sonnet-4-6` 404s, `--model claude-sonnet-4-6` works") was not re-checked this session — cloud was primary and the bare path was only exercised via the missing-credential refusal, which exits before that flag is used.

### Summary

Landed AC-1 (contract test green + wired into CI, falsifier reddens and un-reddens) and AC-2
(six real cloud sessions on kc-dev-flow, read back via the paged session-message reader, workspace
archived after). AC-2's headline claim is partially met: T2 and T4 reproduce the designed
RED-fail/GREEN-pass split, but T1 RED passed on its own — recorded as the `decision:` assertion's
falsification per the completion checklist, not smoothed over. AC-3's collision falsifier does not
reproduce (six distinct scratch dirs; five of six genuinely concurrent, one dispatched solo after
my own script's zsh 1-indexed-array bug dropped it from the batch). Every checklist-item-3 refusal
(literal scratch path, assert/judge exclusivity, missing adversarial/setup, unpinned model, missing
credentials) fires locally with a named reason, no API cost. Two things this session found and did
not invent: the retry context's "all six done" was false (one session, 429'd, zero tool calls) and
its reset time was stale by 40 minutes; and the shape's own 700-line / 180-line-in-one-file stop
numbers are breached by the inherited WIP (712 insertions; the 390-line poller/pager sits in a new
`skill-runner.py` the shape's file table never named). Both are stated plainly for the gate rather
than resolved unilaterally. One residual left open: a workspace-cold-start race that produced one
false `outcome=error` before the workspace was confirmed awake; it did not reproduce once observed,
and fixing it would add lines to a file already over its guard.
- Retry 1: ideation (cycle 3) — agent-error (API 500 server_error at first action, 2026-09-03 ~21:45 CST); re-dispatched -retry
- Hold: ideation (cycle 3) — second consecutive agent-error (API 529 overloaded on the -retry dispatch, ~21:50 CST); entity held un-dispatched pending Captain instruction
- Resume: ideation (cycle 3) — Captain instructed re-dispatch after Claude status cleared (09:30 CST); fresh -cycle3-r2 dispatch on Opus

## Stage Report: ideation (cycle 3)

- DONE: `kc-plugin-forge/reference/skill-runner.py` (390 lines) is either cut to the shape's own 180-line runaway guard or each remaining block is justified by name against the without-it test; blocks that cannot answer are cut. The `### Where it touches` table and `### Stop numbers` are rewritten to name the actual files and the new guard, and the total insertions fit the stated line number.
  `## Shape` § Cycle 3: the runner, block by block — all 21 blocks measured by `cat -n` line range, each with what breaks without it and the run that shows it. Cut to 180 is unreachable without deleting outcome-bound blocks — the cloud path alone measures 107 and the scorer plus extractor another ~45 before `bare` is counted — so branch 2 was taken: two cuts (`host_side_baseline` + the whole `file_unchanged` path, 33 lines; the `skill-runner.sh` wrapper, 17 lines) and 14 lines of docstring trim. The old 180 guard is shown to have been aimed at the cloud poller/pager, measured at **107** lines on the built tree — that area never breached it; the scorer, prompt builder, extractor and bare path, budgeted nowhere, did. Restated: `skill-runner.py` > 370 (projected ≈350), cloud path > 130 (projected ≈110). Total insertions derived line by line from the built tree: 712 → **675**, under the unchanged 700 stop number with 25 lines of margin; files 13 → 12.
- DONE: The T1 `frontmatter_field decision: hold` assertion is resolved from the build's own evidence (session 334a0f15).
  `## Shape` § Cycle 3: T1 is retired from AC-2's RED-fail claim. Branch 2 of the two offered: the claim now covers T2 and T4; `## Acceptance criteria` untouched; the AC-2 falsifier row follows the decision and the retired cycle-2 falsifier is marked retired by measurement. The redesign branch is named in full (drop the `gate: pending` tell so the skill's recorded-resolution rule does the discriminating) and explicitly not admitted, because admitting a RED-fail claim for a run nobody has seen fail is the cycle-2 error being corrected. T1 stays in the scenario file: it is the only live run where the scorer returned `pass` on a RED, which is the harness's two-sidedness on live data.
- DONE: The two open residuals are dispositioned by name.
  `## Shape` § Cycle 3: residual dispositions. Residual 1 (workspace cold-start race) is **fixed inside the trimmed runner**, +5 lines, both halves named (`page_until_token` requires ≥1 non-`userMessage` message before `idle` counts as a stall; `reconcile_workspace`'s lock-file fast path gains the ready-wait), with the reproduce condition (`workspace status` = `sleeping` at `session create`) and a one-session falsifier. Residual 2 (AC-4/AC-5 not CI-wired) — the trimmed slice **adds** G4/G5 to the existing contract test (no new CI step, no new job; seconds not measured), and the disposition corrects the premise: AC-5's report fields do not exist in the tree at all.
- FINDING, not in the checklist: **AC-5's deliverable is missing, not just its check.** Verified byte-identically — the fenced report block under `## Phase 4: Re-validate + Report` in `kc-plugin-forge/skills/kc-plugin-forge/SKILL.md` has the same md5 (`c5ecfffd…`) at delivery base `4bc79749` and at built HEAD `a640a72f`; `git diff -U0` shows SKILL.md's only hunks are at lines 309 and 319, both inside Phase 2. There is no runner field, no model pin, no per-scenario outcome, and no slot for AC-4's hand-designed line. The build obligation is now in the shape (≈5 lines) and in the AC-4/AC-5 falsifier rows.
- FINDING: **residual 3, surfaced by the trim** — `run_bare` has never completed a run; it was exercised only to its credential refusal, and `bare_model_id`'s "`--model sonnet-4-6` 404s" docstring is an unverified absolute the implementation report already flagged. Recorded as a known limit with the closing run named, not admitted into an AC.

### Summary

Corrected the shape; no code touched (worktree clean at `a640a72f`). Two decisions need the
Captain and both are in `### Open decision for the Captain`. First: cutting `file_unchanged`,
which the Captain himself named at ideation gate 1 — it held 12 of 12 across the six POC and six
live sessions, discriminated nothing, and the one run closest to the failure mode it names (POC
`5bbe799f`, which wrote the `sed` rewrite *into* `ACTION.md`) it scores as unchanged. Its 33 lines
are exactly the difference between 675 insertions and 708, i.e. between fitting the 700-line stop
number and breaching it again. Second: retiring T1 from AC-2's RED-fail claim makes the T1 half of
`## Accepted outcome`'s last sentence false — wording correction to the admission snapshot, or
planning delta. Everything else is derived arithmetic from the measured tree rather than a new
estimate; the cycle-2 numbers were shown to be internally impossible (a ~135-line file budget with
a 180-line guard on an area inside it), which is why they never fired.
