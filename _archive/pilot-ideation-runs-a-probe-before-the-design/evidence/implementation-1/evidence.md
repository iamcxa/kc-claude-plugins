# Implementation evidence

Base: `88f86f2749dadb6f4ef0cf9aa089c1827096865b`; candidate: `f0e00d30ce00542b2895f13173bd41075cc8bfd4`.

## Acceptance commands

Use the exact environment in `accept-results.json`; all Python helpers ran with bytecode disabled and temporary files under the assigned scratch root. The original acceptance section is unchanged.

- AC-1: `bash /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design/evidence/ideation-1/bin/accept.sh AC-1 /tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1/out/AC-1`; exit 0; saved output `AC-1.log`.
- AC-2: `bash /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design/evidence/ideation-1/bin/accept.sh AC-2 /tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1/out/AC-2`; exit 0; saved output `AC-2.log`.
- AC-3: `bash /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design/evidence/ideation-1/bin/accept.sh AC-3 /tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1/out/AC-3`; exit 1; saved output `AC-3.log`.
- AC-4: `bash /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design/evidence/ideation-1/bin/accept.sh AC-4 /tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1/out/AC-4`; exit 0; saved output `AC-4.log`.
- AC-5: `bash /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design/evidence/ideation-1/bin/accept.sh AC-5 /tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1/out/AC-5`; exit 0; saved output `AC-5.log`.
- AC-6: `bash /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design/evidence/ideation-1/bin/accept.sh AC-6 /tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1/out/AC-6`; exit 0; saved output `AC-6.log`.
- AC-7: `bash /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design/evidence/ideation-1/bin/accept.sh AC-7 /tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1/out/AC-7`; exit 0; saved output `AC-7.log`.

## AC-3 deviation

The original command exited 1 because `grep -c "repeats"` counts lint's success line `no unlisted passage repeats it`. Lint itself exited 0; both removed-ban counts were 0. The task-evidence copy of the harness changes only that pattern to `grep -c "^FAIL:.*repeats"`.

Corrected command, with the same environment: `bash /tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1/bin/accept.sh AC-3 /tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1/out/AC-3-corrected`; exit 0; `AC-3-corrected.log`. The changed line runs `python3 -B "$tmp/kc-dev-flow-2/scripts/lint-skills.py" --root "$tmp/kc-dev-flow-2" | grep -c "^FAIL:.*repeats"`. Original `AC-3.log` and the corrected output are both retained. This is an evidence-harness deviation; the approved criterion has not been amended. FO message 7dd2f933-9586-4d18-8390-a1ac918d9723 directs preserving it for validation and the Captain. The initial corrected invocation had an invalid transcribed ref; `AC-3-corrected-invalid-ref.log` is retained but excluded from candidate evidence.

## Falsifiers

- AC-2-outside-ideation: expected failing exit 1, observed 1; `mutation-AC-2-outside-ideation.log`; exact invocation in `mutation-results.json` or `mutation-AC-1-result.json`.
- AC-3-duplicate-ban: expected failing exit 1, observed 1; `mutation-AC-3-duplicate-ban.log`; exact invocation in `mutation-results.json` or `mutation-AC-1-result.json`.
- AC-4-remove-raise: expected failing exit 1, observed 1; `mutation-AC-4-remove-raise.log`; exact invocation in `mutation-results.json` or `mutation-AC-1-result.json`.
- AC-5-word-6100: expected failing exit 1, observed 1; `mutation-AC-5-word-6100.log`; exact invocation in `mutation-results.json` or `mutation-AC-1-result.json`.
- AC-1-control-as-candidate: expected failing exit 1, observed 1; `mutation-AC-1-control-as-candidate.log`; exact invocation in `mutation-results.json` or `mutation-AC-1-result.json`.

## Checks and boundaries

- Repository lint: exit 0 (`lint.log`), 6099 of 6099 words. `test_lint_skills.py`: exit 0, all 47 tests (`test_lint_skills.log`). The duplicate-ban mutation is refused; removing the raise step fails by 66 words.
- Installed 0.41.0 `adr_lint.py docs/adr --since 88f86f2749dadb6f4ef0cf9aa089c1827096865b --require 0084`: exit 0 (`adr-lint.log`). New ADR 0084 supersedes only the Pilot ban clause in ADR 0005, quoting the ideation gate and amendment. Required code pointer retained.
- Installed 0.41.0 `number_guards.py check --repo <assigned worktree> --workflow-dir <workflow> --task <entity> --base 88f86f2749dadb6f4ef0cf9aa089c1827096865b --head f0e00d30ce00542b2895f13173bd41075cc8bfd4`: exit 0 (`number-guards.log`), including fetched cross-workflow reservations.
- Installed 0.41.0 `comment_ratio.py 88f86f2749dadb6f4ef0cf9aa089c1827096865b HEAD --workflow-dir <workflow>`: exit 0 (`comment-ratio.log`). Four added code lines and one required ADR pointer: 25.0%; the default 5% ceiling is not enforced below the 20-code-line floor. This is the script's exemption, not a measured ratio below 5%.
- Installed 0.41.0 `design_surfaces.py check <entity>`: exit 0 (`design-surfaces.log`). `doc_impact.py 88f86f2749dadb6f4ef0cf9aa089c1827096865b HEAD --json`: exit 0; every returned document has a verdict in `doc-impact-verdicts.md`.
- The dispatch suite runs installed Spacedock binary 0.27.2 with the named 0.27.3 plugin-root fixtures. The native suite passed (`AC-6/test_sd_dispatch.log`); it does not run a model or prove skill reading, live gates, the delivery hook body or remote merge.
- Existing design audit reused: the upstream dispatch worktree would be the delivery branch, so the probe remains separate. Current origin/main equals the approved base. The named local probe diff is carried forward unchanged except for the approved raise and the new ADR. No need for another capability redesign.
- POC derivation equality is checked by AC-2. Only the ideation workflow section changes, so the Prod branch retains the otherwise-write-ban. No design gate, version, POC text, budget grammar or timeline helper change.
- Probe branch deletion verified after candidate commit and FO removal of its clean worktree; `probe-cleanup.log`. Portable diff remains in `evidence/ideation-1/probe.diff`.
- Not run: RoboRev (FO-owned local review), hosted CI, live model replay (AC-8), post-release worker behavior (AC-9), publication, merge and release. No product branch push or PR opened: publication belongs to FO. CI cost per PR was not measured; no workflow trigger changed.

## Word costs

The exact before/after lifecycle counts are in `AC-5/words-by-moment.json`: startup +66, ideation dispatch definition +66, ideation skill reading +135, Pilot implementation profile +15. FO-written probe instructions in the stripped replay inputs are 0 (`AC-5.log`); the accepted trial comparison was 184 words per dispatch. The total Pilot ideation reading rises by 201 words versus released text, or 17 versus the trial with its hand-written instructions. Idle, merge ask, archive and gate text are unchanged. Speed and defect reduction remain unmeasured.
