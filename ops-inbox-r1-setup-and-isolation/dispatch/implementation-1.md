# implementation dispatch 1

Model: sonnet
Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0

## Checklist

1. Apply Captain amendments 1 and 2 to `## Acceptance criteria`: move the AC-3, AC-4 and AC-5 blocks verbatim into amendment 2 under `Superseded text:`, and write AC-13 under a fresh id ("Amended by Captain, amendment 2"): the inbox core imports only node:crypto and its tests pass under the Netlify adapter; then land the axis ADR as docs/adr/0031 (AC-6) as the first commit and contract v1 with validator and fixtures (AC-1) next, reporting the contract's path and commit to the First Officer as soon as it is committed so relay can build its emitter.
2. Build AC-7 to AC-11 and AC-13 in `kc-ops-inbox/**` (aggregation, ADR-aware diagnosis with the citation check, trigger-repository isolation, state-branch gate with the two measures, runbook and read-back script) with tests that can fail, and raise every outward action (any repository, App, ruleset, secret, deployment, Slack post or push outside your worktree branch) to the First Officer as one decision request before taking it.
3. Run AC-12 only after relay's emitter is on a relay deploy preview (FO tells you); stop and hold-report if the estimate passes 3.5 days or any stop condition fires.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (pass it as --workflow-dir on every spacedock command).
ADR: 0031 (reserved by FO for the axis ADR, AC-6). The task holds one ADR number; the trigger-repository and state-branch ruling (D2, D3) is not written as an ADR here, FO files it as a follow-up.
Approved design: the task's ## Design (cycle 2) and the ideation gate resolution of attempt 2 (D1, D4, D6 to D10). Copy and rewrite POC code from branches spacedock-ensign/inbox-exactly-once-delivery-poc (cd079cb8) and spacedock-ensign/hermes-ops-fo-exe-dev-poc (aae7041b) under kc-ops-inbox/; do not carry POC1's hermes-profile/ or rehearsal/.
No .claude-plugin/plugin.json or marketplace entry yet unless the design's packaging needs it; if it does, raise it to FO first (release-please and version-parity rules in the repo CLAUDE.md).
Do not edit relay, qnow or any scratch resource from the POCs. Relay's emitter and the setup PR files in relay go through a relay task; FO coordinates.
Secrets: never read, print or copy a credential; the Captain sets every secret.
Budget 3.5 days (Captain, ideation gate attempt 2).
Captain standing ask, 2026-10-21: 「請持續針對套件的意義做觀察與回饋」 — include one package-value observation in the stage report.

roborev: Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <your stamped worktree path> --base c27e76590c1d2dc910e7fa2d332242a7534df0b0`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
