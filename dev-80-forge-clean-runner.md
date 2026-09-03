---
title: "Forge Phase 2 RED/GREEN runs in a clean runner with a scenario file slot"
status: backlog
source:
product: kc-plugin-forge
planning-window:
planning-outcome:
sprint: S1
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-80
pr:
mod-block:
id: kmt1mgvwqy0g9qmshemqtsn1
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
